from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class Review(models.Model):
    """Единая модель отзыва для всех типов контента"""

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reviews')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ['book', 'course', 'film']})
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    rating = models.IntegerField('Оценка', choices=[(0, 'Без оценки'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField('Комментарий', blank=True)

    accessibility_subtitles = models.BooleanField('Субтитры доступны', default=False)
    accessibility_sign_language = models.BooleanField('Жестовый перевод доступен', default=False)
    accessibility_audio_description = models.BooleanField('Аудиоописание доступно', default=False)
    accessibility_transcript = models.BooleanField('Текстовая расшифровка доступна', default=False)

    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.content_type} #{self.object_id}: {self.rating}'

    def clean(self):
        """Валидация оценки"""
        if self.rating is not None:
            if self.rating < 0 or self.rating > 5:
                raise ValidationError('Оценка должна быть от 0 до 5')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        from .services import update_cached_rating
        update_cached_rating(self.content_type, self.object_id)


class CachedRating(models.Model):
    """Кэшированный рейтинг для быстрого доступа"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                    limit_choices_to={'model__in': ['book', 'course', 'film']})
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    average_rating = models.FloatField('Средний рейтинг', default=0.0)
    review_count = models.PositiveIntegerField('Количество отзывов', default=0)
    last_updated = models.DateTimeField('Последнее обновление', auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id')
        verbose_name = 'Кэшированный рейтинг'
        verbose_name_plural = 'Кэшированные рейтинги'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['average_rating']),
        ]

    def __str__(self):
        return f'{self.content_type} #{self.object_id}: {self.average_rating:.1f} ({self.review_count})'


class Favorite(models.Model):
    """Избранное (лайк) для любого типа контента"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='favorites')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                    limit_choices_to={'model__in': ['book', 'course', 'film']})
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.content_type} #{self.object_id}'
