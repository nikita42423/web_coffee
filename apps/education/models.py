from django.db import models

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

    # Рейтинг
    rating = models.FloatField('Рейтинг', default=0.0)

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
