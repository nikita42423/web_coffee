from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

class ForumCategory(MPTTModel):
    """Категории форума"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)
    icon = models.CharField('Иконка', max_length=50, default='📌')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                           related_name='children')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    
    # Статистика
    topics_count = models.IntegerField('Количество тем', default=0)
    posts_count = models.IntegerField('Количество сообщений', default=0)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория форума'
        verbose_name_plural = 'Категории форума'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('forum:category', args=[self.slug])

class ForumTopic(models.Model):
    """Темы форума"""
    title = models.CharField('Заголовок', max_length=200)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    content = models.TextField('Содержание')
    
    views = models.IntegerField('Просмотры', default=0)
    posts_count = models.IntegerField('Количество ответов', default=0)
    
    is_pinned = models.BooleanField('Закреплено', default=False)
    is_closed = models.BooleanField('Закрыто', default=False)
    is_active = models.BooleanField('Активно', default=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Тема форума'
        verbose_name_plural = 'Темы форума'
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum:topic', args=[self.id])

class ForumPost(models.Model):
    """Сообщения в темах"""
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField('Сообщение')
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='replies')
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Сообщение форума'
        verbose_name_plural = 'Сообщения форума'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Сообщение #{self.id} от {self.author.username}"
    
    def get_absolute_url(self):
        return f"{self.topic.get_absolute_url()}#post-{self.id}"