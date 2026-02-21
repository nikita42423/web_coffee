from django.db import models

class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    author = models.CharField('Автор', max_length=100)
    description = models.TextField('Описание книги', blank=True)
    content = models.TextField('Текст книги')  # Здесь будет обычный текст
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    # Поля доступности
    has_subtitles = models.BooleanField('Есть субтитры', default=False)
    has_sign_language = models.BooleanField('Есть жестовый перевод', default=False)
    has_audio_description = models.BooleanField('Есть аудиоописание', default=False)

    # Теги для рекомендаций
    tags = models.CharField('Теги (через запятую)', max_length=300, blank=True)

    # Рейтинг
    rating = models.FloatField('Рейтинг', default=0.0)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []


class Rating(models.Model):
    """Оценка книги пользователем от 1 до 5"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    value = models.IntegerField('Оценка', choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField('Дата оценки', auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    def __str__(self):
        return f'{self.user.username} - {self.book.title}: {self.value}'


class Comment(models.Model):
    """Комментарий к книге"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'


class Favorite(models.Model):
    """Избранное (лайк) книги пользователем"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
