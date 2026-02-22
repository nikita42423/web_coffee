from django.db import models
from django.contrib.contenttypes.fields import GenericRelation


class Film(models.Model):
    title = models.CharField('Название фильма', max_length=200)
    director = models.CharField('Режиссер', max_length=100)
    year = models.IntegerField('Год выпуска')
    description = models.TextField('Описание фильма', blank=True)
    duration = models.IntegerField('Продолжительность (минуты)')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    # Поля доступности
    has_subtitles = models.BooleanField('Есть субтитры', default=True)
    has_sign_language = models.BooleanField('Есть жестовый перевод', default=False)
    has_audio_description = models.BooleanField('Есть аудиоописание', default=False)

    # Теги для рекомендаций
    tags = models.CharField('Теги (через запятую)', max_length=300, blank=True)

    # Рейтинг (кэшированное значение из общей системы)
    rating = models.FloatField('Рейтинг', default=0.0)

    # Ссылка на видео или платформу
    video_url = models.URLField('Ссылка на видео', blank=True)
    platform = models.CharField('Платформа', max_length=100, blank=True)

    # Связь с общей системой отзывов
    reviews = GenericRelation('reviews.Review', content_type_field='content_type', object_id_field='object_id')
    favorites = GenericRelation('reviews.Favorite', content_type_field='content_type', object_id_field='object_id')

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.year})'

    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    @property
    def average_rating(self):
        """Средний рейтинг из общей системы"""
        from apps.reviews.services import get_average_rating
        return get_average_rating('film', self.id)

    @property
    def review_count(self):
        """Количество отзывов из общей системы"""
        from apps.reviews.services import get_review_count
        return get_review_count('film', self.id)

    def get_reviews(self):
        """Получить все отзывы для этого фильма"""
        from apps.reviews.services import get_reviews_for
        return get_reviews_for('film', self.id)

    def add_review(self, user, rating, comment='', **accessibility_fields):
        """Добавить отзыв для этого фильма"""
        from apps.reviews.services import add_review
        return add_review(user, self, rating, comment, **accessibility_fields)

    def is_favorited_by(self, user):
        """Проверить, находится ли фильм в избранном у пользователя"""
        from apps.reviews.services import is_favorited
        return is_favorited(user, self) if user.is_authenticated else False
