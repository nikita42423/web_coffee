from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Genre(models.Model):
    """Жанры фильмов"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    icon = models.CharField('Иконка', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Country(models.Model):
    """Страны производства"""
    name = models.CharField('Название', max_length=100)
    code = models.CharField('Код', max_length=2, blank=True)
    
    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Actor(models.Model):
    """Актеры"""
    name = models.CharField('Имя', max_length=200)
    photo = models.ImageField('Фото', upload_to='films/actors/', blank=True, null=True)
    bio = models.TextField('Биография', blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Актер'
        verbose_name_plural = 'Актеры'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Director(models.Model):
    """Режиссеры"""
    name = models.CharField('Имя', max_length=200)
    photo = models.ImageField('Фото', upload_to='films/directors/', blank=True, null=True)
    bio = models.TextField('Биография', blank=True)
    
    class Meta:
        verbose_name = 'Режиссер'
        verbose_name_plural = 'Режиссеры'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Film(models.Model):
    """Модель фильма/сериала"""
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Фильм'),
        ('series', 'Сериал'),
        ('cartoon', 'Мультфильм'),
        ('anime', 'Аниме'),
    ]
    
    STATUS_CHOICES = [
        ('announced', 'Анонсирован'),
        ('filming', 'Съемки'),
        ('released', 'Вышел'),
        ('ongoing', 'Выходит'),
    ]
    
    title = models.CharField('Название', max_length=300)
    original_title = models.CharField('Оригинальное название', max_length=300, blank=True)
    slug = models.SlugField('URL', unique=True)
    content_type = models.CharField('Тип', max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie')
    
    # Постер и кадры
    poster = models.ImageField('Постер', upload_to='films/posters/', blank=True, null=True)
    backdrop = models.ImageField('Задний фон', upload_to='films/backdrops/', blank=True, null=True)
    
    # Основная информация
    description = models.TextField('Описание')
    short_description = models.CharField('Краткое описание', max_length=500, blank=True)
    year = models.IntegerField('Год', null=True, blank=True)
    countries = models.ManyToManyField(Country, verbose_name='Страны', blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True)
    
    # Люди
    directors = models.ManyToManyField(Director, verbose_name='Режиссеры', blank=True)
    actors = models.ManyToManyField(Actor, verbose_name='Актеры', blank=True)
    
    # Технические детали
    duration = models.IntegerField('Длительность (мин)', null=True, blank=True)
    age_rating = models.CharField('Возрастной рейтинг', max_length=10, blank=True)
    imdb_rating = models.FloatField('Рейтинг IMDB', null=True, blank=True, 
                                   validators=[MinValueValidator(0), MaxValueValidator(10)])
    kinopoisk_rating = models.FloatField('Рейтинг Кинопоиск', null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Для сериалов
    seasons = models.IntegerField('Количество сезонов', default=1)
    episodes = models.IntegerField('Количество серий', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='released')
    
    # Доступность для людей с нарушениями слуха
    has_subtitles = models.BooleanField('Есть субтитры', default=True)
    has_sign_language = models.BooleanField('Есть жестовый перевод', default=False)
    has_audio_description = models.BooleanField('Есть аудиоописание', default=False)
    
    # Статистика
    views_count = models.IntegerField('Просмотры', default=0)
    likes_count = models.IntegerField('Лайки', default=0)
    
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['year']),
            models.Index(fields=['content_type']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('films:detail', args=[self.slug])
    
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

class VideoSource(models.Model):
    """Источники видео (локальные файлы или iframe код)"""
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('vk', 'VK Видео'),
        ('rutube', 'RuTube'),
        ('local', 'Локальный файл'),
        ('iframe', 'Встроенный код'),
        ('other', 'Другое'),
    ]
    
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='videos')
    platform = models.CharField('Платформа', max_length=20, choices=PLATFORM_CHOICES, default='local')
    
    # Для локального видео
    video_file = models.FileField(
        'Видео файл', 
        upload_to='films/videos/%Y/%m/', 
        blank=True, 
        null=True,
        help_text='Загрузите видео файл (mp4, webm, etc.)'
    )
    
    # Для встроенного кода (iframe)
    embed_code = models.TextField(
        'HTML код для вставки', 
        blank=True,
        help_text='Вставьте iframe код с YouTube, VK, RuTube и т.д.'
    )
    
    # Для YouTube/VK (альтернативный способ)
    url = models.URLField('Ссылка на видео', blank=True)
    youtube_id = models.CharField('YouTube ID', max_length=50, blank=True)
    vk_id = models.CharField('VK ID', max_length=100, blank=True)
    vk_owner_id = models.CharField('VK Owner ID', max_length=50, blank=True)
    
    # Метаданные
    title = models.CharField('Название источника', max_length=200, blank=True)
    quality = models.CharField('Качество', max_length=10, default='HD', blank=True)
    language = models.CharField('Язык', max_length=50, default='Русский', blank=True)
    
    # Доступность
    has_subtitles = models.BooleanField('С субтитрами', default=True)
    has_sign_language = models.BooleanField('С жестовым переводом', default=False)
    
    # Приоритет
    is_primary = models.BooleanField('Основной источник', default=False)
    order = models.IntegerField('Порядок', default=0)
    
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Видеоисточник'
        verbose_name_plural = 'Видеоисточники'
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        source = self.title or self.get_platform_display()
        return f"{source} - {self.film.title}"
    
    def get_embed_html(self):
        """Получить HTML для встраивания"""
        if self.embed_code:
            return self.embed_code
        
        if self.platform == 'youtube' and self.youtube_id:
            return f'<iframe width="100%" height="100%" src="https://www.youtube.com/embed/{self.youtube_id}" frameborder="0" allowfullscreen></iframe>'
        
        if self.platform == 'vk' and self.vk_id:
            owner = self.vk_owner_id or ''
            return f'<iframe src="https://vkvideo.ru/video_ext.php?oid={owner}&id={self.vk_id}&hash=3ac5b93799aaa07d" width="100%" height="100%" frameborder="0" allowfullscreen="1" allow="autoplay; encrypted-media; fullscreen; picture-in-picture"></iframe>'
        
        if self.platform == 'local' and self.video_file:
            return f'<video width="100%" height="100%" controls><source src="{self.video_file.url}" type="video/mp4">Ваш браузер не поддерживает видео.</video>'
        
        return '<p>Видео временно недоступно</p>'
    
    def get_thumbnail(self):
        """Получить миниатюру для видео"""
        # Здесь можно добавить логику для получения превью
        if self.platform == 'youtube' and self.youtube_id:
            return f'https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg'
        return None
    
class Episode(models.Model):
    """Серии для сериалов"""
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='episodes_list')
    season = models.IntegerField('Сезон')
    episode = models.IntegerField('Серия')
    title = models.CharField('Название серии', max_length=300, blank=True)
    description = models.TextField('Описание', blank=True)
    
    # Видео для этой серии
    videos = models.ManyToManyField(VideoSource, blank=True, related_name='episodes')
    
    duration = models.IntegerField('Длительность (мин)', null=True, blank=True)
    release_date = models.DateField('Дата выхода', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'
        ordering = ['season', 'episode']
        unique_together = ['film', 'season', 'episode']
    
    def __str__(self):
        return f"{self.film.title} S{self.season:02d}E{self.episode:02d}"

class FilmRating(models.Model):
    """Оценки пользователей"""
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ['film', 'user']

class FilmReview(models.Model):
    """Отзывы на фильмы"""
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

class FilmCollection(models.Model):
    """Подборки фильмов"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='films/collections/', blank=True, null=True)
    films = models.ManyToManyField(Film, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'
    
    def __str__(self):
        return self.title