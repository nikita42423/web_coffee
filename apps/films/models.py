from django.db import models

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

    # Рейтинг
    rating = models.FloatField('Рейтинг', default=0.0)

    # Ссылка на видео или платформу
    video_url = models.URLField('Ссылка на видео', blank=True)
    platform = models.CharField('Платформа', max_length=100, blank=True)

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
