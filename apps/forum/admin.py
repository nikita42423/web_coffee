from django.contrib import admin
from .models import ForumCategory, ForumTopic, ForumPost

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'parent', 'order', 'is_active', 'topics_count', 'posts_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Иерархия', {
            'fields': ('parent', 'order')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Статистика (только чтение)', {
            'fields': ('topics_count', 'posts_count'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['topics_count', 'posts_count']
