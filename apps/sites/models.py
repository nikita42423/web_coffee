from django.db import models
from django.urls import reverse

class SiteCategory(models.Model):
    """Категории сайтов (например: Госуслуги, Образование, Здравоохранение)"""
    name = models.CharField('Название категории', max_length=100)
    slug = models.SlugField('URL', unique=True)
    icon = models.CharField('Иконка', max_length=50, default='🏛️')
    description = models.TextField('Описание', blank=True)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория сайтов'
        verbose_name_plural = 'Категории сайтов'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Site(models.Model):
    """Государственные и официальные сайты"""
    title = models.CharField('Название сайта', max_length=200)
    slug = models.SlugField('URL', unique=True)
    url = models.URLField('Ссылка на сайт')
    category = models.ForeignKey(
        SiteCategory,
        on_delete=models.CASCADE,
        related_name='sites',
        verbose_name='Категория'
    )

    # Описание
    description = models.TextField('Описание')
    short_description = models.CharField('Краткое описание', max_length=200, blank=True)

    # Логотип или иконка
    logo = models.ImageField('Логотип', upload_to='sites/logos/%Y/%m/', blank=True, null=True)

    # Контактная информация
    contact_info = models.TextField('Контактная информация', blank=True)
    phone = models.CharField('Телефон', max_length=100, blank=True)
    email = models.EmailField('Email', blank=True)

    # Статистика
    visits_count = models.IntegerField('Переходы', default=0)

    # Статус
    is_published = models.BooleanField('Опубликовано', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)

    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'
        ordering = ['-is_featured', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sites:detail', args=[self.slug])
