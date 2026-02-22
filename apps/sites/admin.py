from django.contrib import admin
from django.utils.html import format_html
from .models import SiteCategory, Site

@admin.register(SiteCategory)
class SiteCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order', 'sites_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def sites_count(self, obj):
        return obj.sites.count()
    sites_count.short_description = 'Количество сайтов'

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'is_published', 'visits_count', 'logo_preview']
    list_filter = ['category', 'is_featured', 'is_published']
    search_fields = ['title', 'description', 'url']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['visits_count', 'logo_preview']
    list_editable = ['is_featured', 'is_published']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'url', 'category', 'description', 'short_description')
        }),
        ('Логотип', {
            'fields': ('logo', 'logo_preview'),
            'classes': ('wide',)
        }),
        ('Контакты', {
            'fields': ('contact_info', 'phone', 'email'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_published', 'is_featured', 'visits_count')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: contain;" />', obj.logo.url)
        return "Нет лого"
    logo_preview.short_description = 'Лого'
