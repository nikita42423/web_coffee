from django.db import models
from django.contrib.contenttypes.fields import GenericRelation


class Course(models.Model):
    title = models.CharField('Название курса', max_length=200)
    instructor = models.CharField('Преподаватель', max_length=100)
    description = models.TextField('Описание курса')
    duration_hours = models.IntegerField('Продолжительность (часы)')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    # Поля доступности
    has_subtitles = models.BooleanField('Есть субтитры', default=True)
    has_sign_language = models.BooleanField('Есть жестовый перевод', default=False)
    has_audio_description = models.BooleanField('Есть аудиоописание', default=False)
    has_transcript = models.BooleanField('Есть текстовая расшифровка', default=True)

    # Теги для рекомендаций
    tags = models.CharField('Теги (через запятую)', max_length=300, blank=True)

    # Ссылка на курс
    course_url = models.URLField('Ссылка на курс', blank=True)
    platform = models.CharField('Платформа', max_length=100, blank=True)

    # Уровень сложности
    LEVEL_CHOICES = [
        ('beginner', 'Начальный'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]
    level = models.CharField('Уровень', max_length=20, choices=LEVEL_CHOICES, default='beginner')

    # Связь с общей системой отзывов
    reviews = GenericRelation('reviews.Review', content_type_field='content_type', object_id_field='object_id')
    favorites = GenericRelation('reviews.Favorite', content_type_field='content_type', object_id_field='object_id')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    @property
    def average_rating(self):
        """Средний рейтинг из общей системы"""
        from apps.reviews.services import get_average_rating
        return get_average_rating('course', self.id)

    @property
    def review_count(self):
        """Количество отзывов из общей системы"""
        from apps.reviews.services import get_review_count
        return get_review_count('course', self.id)

    def get_reviews(self):
        """Получить все отзывы для этого курса"""
        from apps.reviews.services import get_reviews_for
        return get_reviews_for('course', self.id)

    def add_review(self, user, rating, comment='', **accessibility_fields):
        """Добавить отзыв для этого курса"""
        from apps.reviews.services import add_review
        return add_review(user, self, rating, comment, **accessibility_fields)

    def is_favorited_by(self, user):
        """Проверить, находится ли курс в избранном у пользователя"""
        from apps.reviews.services import is_favorited
        return is_favorited(user, self) if user.is_authenticated else False

    def update_rating(self):
        """Пересчитать средний рейтинг на основе отзывов (устаревший метод)"""
        # Этот метод оставлен для обратной совместимости
        # В новой системе рейтинг кэшируется автоматически
        from django.contrib.contenttypes.models import ContentType
        from apps.reviews.services import get_cached_rating
        content_type = ContentType.objects.get_for_model(self)
        cached = get_cached_rating(content_type, self.id)
        self.rating = cached.average_rating
        self.save(update_fields=['rating'])
