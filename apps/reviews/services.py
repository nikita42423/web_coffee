# apps/reviews/services.py
from django.db.models import Avg, Count
from django.contrib.contenttypes.models import ContentType
from .models import Review, CachedRating

def update_cached_rating(content_type, object_id):
    """
    Обновляет кэшированный рейтинг для объекта

    Args:
        content_type: ContentType object or (app_label, model) tuple
        object_id: ID объекта
    """
    # Если content_type передан как строка (app_label, model), получаем ContentType
    if isinstance(content_type, tuple):
        app_label, model = content_type
        content_type = ContentType.objects.get(app_label=app_label, model=model)

    # Вычисляем статистику
    stats = Review.objects.filter(
        content_type=content_type,
        object_id=object_id,
        rating__gt=0  # Только оценки, не комментарии
    ).aggregate(
        avg_rating=Avg('rating'),
        count=Count('id')
    )

    # Создаем или обновляем кэшированный рейтинг
    cached_rating, created = CachedRating.objects.update_or_create(
        content_type=content_type,
        object_id=object_id,
        defaults={
            'average_rating': stats['avg_rating'] or 0,
            'review_count': stats['count'] or 0,
        }
    )

    return cached_rating


def get_cached_rating(content_type, object_id):
    """
    Получает кэшированный рейтинг для объекта
    """
    try:
        return CachedRating.objects.get(
            content_type=content_type,
            object_id=object_id
        )
    except CachedRating.DoesNotExist:
        return update_cached_rating(content_type, object_id)


def delete_cached_rating(content_type, object_id):
    """
    Удаляет кэшированный рейтинг для объекта
    """
    CachedRating.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).delete()


def get_reviews_for_object(content_type, object_id):
    """
    Получает все отзывы для объекта
    """
    return Review.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).select_related('user').order_by('-created_at')


def get_user_review_for_object(user, content_type, object_id):
    """
    Получает отзыв пользователя для конкретного объекта
    """
    try:
        return Review.objects.get(
            user=user,
            content_type=content_type,
            object_id=object_id
        )
    except Review.DoesNotExist:
        return None


def is_favorite(user, content_type, object_id):
    """
    Проверяет, есть ли объект в избранном у пользователя
    """
    from .models import Favorite
    return Favorite.objects.filter(
        user=user,
        content_type=content_type,
        object_id=object_id
    ).exists()


# Утилиты для удобного вызова с объектом или строковым идентификатором

def get_average_rating(content_type_str, object_id):
    """
    Возвращает средний рейтинг для объекта по app_label и model
    content_type_str: строка 'book', 'course', 'film'
    """
    from django.contrib.contenttypes.models import ContentType
    # Преобразуем строку в ContentType
    if content_type_str == 'book':
        ct = ContentType.objects.get(app_label='books', model='book')
    elif content_type_str == 'course':
        ct = ContentType.objects.get(app_label='education', model='course')
    elif content_type_str == 'film':
        ct = ContentType.objects.get(app_label='films', model='film')
    else:
        raise ValueError(f"Unknown content type string: {content_type_str}")
    cached = get_cached_rating(ct, object_id)
    return cached.average_rating


def get_review_count(content_type_str, object_id):
    """
    Возвращает количество отзывов для объекта по app_label и model
    """
    from django.contrib.contenttypes.models import ContentType
    if content_type_str == 'book':
        ct = ContentType.objects.get(app_label='books', model='book')
    elif content_type_str == 'course':
        ct = ContentType.objects.get(app_label='education', model='course')
    elif content_type_str == 'film':
        ct = ContentType.objects.get(app_label='films', model='film')
    else:
        raise ValueError(f"Unknown content type string: {content_type_str}")
    cached = get_cached_rating(ct, object_id)
    return cached.review_count


def get_reviews_for(content_type_str, object_id):
    """
    Возвращает список отзывов для объекта по app_label и model
    """
    from django.contrib.contenttypes.models import ContentType
    if content_type_str == 'book':
        ct = ContentType.objects.get(app_label='books', model='book')
    elif content_type_str == 'course':
        ct = ContentType.objects.get(app_label='education', model='course')
    elif content_type_str == 'film':
        ct = ContentType.objects.get(app_label='films', model='film')
    else:
        raise ValueError(f"Unknown content type string: {content_type_str}")
    return get_reviews_for_object(ct, object_id)


def add_review(user, obj, rating, comment='', **accessibility_fields):
    """
    Создает или обновляет отзыв для объекта.
    obj: экземпляр модели (Book, Course, Film)
    Если rating = None, оценка не обновляется.
    Если comment = '', комментарий не обновляется (кроме случая, когда нужно удалить комментарий).
    Для частичного обновления нужно передавать только изменяемые поля.
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import Review
    content_type = ContentType.objects.get_for_model(obj)

    # Получаем существующий отзыв, если есть
    try:
        review = Review.objects.get(
            user=user,
            content_type=content_type,
            object_id=obj.id
        )
        created = False
    except Review.DoesNotExist:
        review = None
        created = True

    # Подготовка данных для обновления
    update_data = {}

    # Обработка rating
    if rating is not None:
        # rating может быть 0 (без оценки) или числом от 1 до 5
        update_data['rating'] = rating
    # Если rating None, не обновляем

    # Обработка comment
    # Если comment передан как пустая строка, мы не обновляем комментарий (сохраняем старый)
    # Но если нужно удалить комментарий, передать comment='' не удалит, нужно явно передать None?
    # Пока оставляем логику: comment='' не обновляет поле (т.е. комментарий остается прежним)
    # Однако в вызовах из views передается '' при оценке, что не должно удалять комментарий.
    # Для этого нужно отличать случай "не передано" от "передана пустая строка".
    # Изменяем подход: если comment is None, не обновляем; если comment == '' (пустая строка), обновляем на пустую строку (удаляем).
    # Но чтобы не ломать текущие вызовы, оставим как есть: comment='' по умолчанию, и это означает "не обновлять".
    # Для этого добавим флаг: если comment == '' и created = False, то не обновляем.
    if comment is not None:
        if created or comment != '':
            # Если отзыв новый, то comment='' допустим (пустой комментарий)
            # Если отзыв существует и comment не пустая строка, обновляем
            update_data['comment'] = comment
        # иначе (comment == '' и отзыв существует) - не обновляем комментарий

    # Добавляем поля доступности, если они переданы и соответствуют модели
    allowed_accessibility_fields = {
        'accessibility_subtitles',
        'accessibility_sign_language',
        'accessibility_audio_description',
        'accessibility_transcript',
    }
    for field_name, value in accessibility_fields.items():
        if field_name in allowed_accessibility_fields:
            update_data[field_name] = value

    if created:
        # Создаем новый отзыв со всеми полями (не переданные поля получат значения по умолчанию)
        review = Review.objects.create(
            user=user,
            content_type=content_type,
            object_id=obj.id,
            **update_data
        )
    else:
        # Обновляем существующий отзыв только переданными полями
        for field, value in update_data.items():
            setattr(review, field, value)
        review.save()

    # Обновить кэшированный рейтинг
    update_cached_rating(content_type, obj.id)
    return review, created


def toggle_favorite(user, obj):
    """
    Добавляет или удаляет объект из избранного пользователя.
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import Favorite
    content_type = ContentType.objects.get_for_model(obj)
    favorite, created = Favorite.objects.get_or_create(
        user=user,
        content_type=content_type,
        object_id=obj.id
    )
    if not created:
        favorite.delete()
        return False  # Удален
    return True  # Добавлен


def is_favorited(user, obj):
    """
    Проверяет, находится ли объект в избранном у пользователя.
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import Favorite
    if not user.is_authenticated:
        return False
    content_type = ContentType.objects.get_for_model(obj)
    return Favorite.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id
    ).exists()


def delete_review(user, obj):
    """
    Удаляет отзыв пользователя для объекта.
    Возвращает True, если отзыв был удалён, False если отзыва не было.
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import Review
    content_type = ContentType.objects.get_for_model(obj)
    deleted, _ = Review.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id
    ).delete()
    if deleted:
        update_cached_rating(content_type, obj.id)
        return True
    return False
