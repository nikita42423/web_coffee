from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Country, Actor, Director, Film, VideoSource, Episode, FilmRating, FilmReview, FilmCollection

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name']

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_date', 'photo_preview']
    search_fields = ['name']
    list_filter = ['birth_date']
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'photo', 'bio')
        }),
        ('Дополнительно', {
            'fields': ('birth_date',),
            'classes': ('collapse',)
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Фото'

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'photo_preview']
    search_fields = ['name']
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Фото'

# Inline для видеоисточников (чтобы добавлять видео прямо при редактировании фильма)
class VideoSourceInline(admin.TabularInline):
    model = VideoSource
    extra = 1
    fields = ['platform', 'title', 'video_file', 'embed_code', 'is_primary', 'order', 'has_subtitles', 'has_sign_language', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.id:
            if obj.embed_code:
                return format_html(
                    '<div style="width: 100px; height: 60px; background: #1a1a1a; color: white; display: flex; align-items: center; justify-content: center; border-radius: 4px;">{}</div>',
                    '📺 Код'
                )
        elif obj.video_file:
            return format_html(
                '<video width="100" height="60" style="object-fit: cover; border-radius: 4px;">'
                '<source src="{}" type="video/mp4">'
                '</video>',
                obj.video_file.url
            )
        else:
            return format_html(
                '<div style="width: 100px; height: 60px; background: #2a2a2a; color: #666; display: flex; align-items: center; justify-content: center; border-radius: 4px;">{}</div>',
                '📁'
            )
        return format_html('<span style="color: #999;">—</span>')
    preview.short_description = 'Предпросмотр'

# Inline для эпизодов (для сериалов)
class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ['season', 'episode', 'title', 'duration', 'release_date']
    ordering = ['season', 'episode']

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'year', 'views_count', 'poster_preview', 'has_subtitles', 'has_sign_language']
    list_filter = ['content_type', 'genres', 'countries', 'year', 'has_subtitles', 'has_sign_language']
    search_fields = ['title', 'original_title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['genres', 'countries', 'directors', 'actors']
    readonly_fields = ['views_count', 'poster_preview', 'backdrop_preview']
    inlines = [VideoSourceInline, EpisodeInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'original_title', 'slug', 'content_type', 'description', 'short_description')
        }),
        ('Изображения', {
            'fields': ('poster', 'poster_preview', 'backdrop', 'backdrop_preview'),
        }),
        ('Детали', {
            'fields': ('year', 'countries', 'genres', 'directors', 'actors', 'duration', 'age_rating')
        }),
        ('Рейтинги', {
            'fields': ('imdb_rating', 'kinopoisk_rating', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Доступность', {
            'fields': ('has_subtitles', 'has_sign_language', 'has_audio_description'),
            'classes': ('wide',)
        }),
        ('Для сериалов', {
            'fields': ('seasons', 'episodes', 'status'),
            'classes': ('collapse',)
        }),
    )
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="width: 50px; height: 75px; object-fit: cover; border-radius: 4px;" />', obj.poster.url)
        return "Нет постера"
    poster_preview.short_description = 'Постер'
    
    def backdrop_preview(self, obj):
        if obj.backdrop:
            return format_html('<img src="{}" style="width: 100px; height: 56px; object-fit: cover; border-radius: 4px;" />', obj.backdrop.url)
        return "Нет фона"
    backdrop_preview.short_description = 'Фон'

@admin.register(VideoSource)
class VideoSourceAdmin(admin.ModelAdmin):
    list_display = ['film', 'platform', 'title', 'is_primary', 'order', 'has_subtitles', 'has_sign_language', 'created_at']
    list_filter = ['platform', 'is_primary', 'has_subtitles', 'has_sign_language']
    search_fields = ['film__title', 'title']
    list_editable = ['is_primary', 'order']
    
    fieldsets = (
        ('Основное', {
            'fields': ('film', 'platform', 'title')
        }),
        ('Локальное видео', {
            'fields': ('video_file',),
            'classes': ('wide',),
            'description': '📁 Загрузите видео файл с компьютера (mp4, webm, etc.)'
        }),
        ('Встроенный код (iframe)', {
            'fields': ('embed_code',),
            'classes': ('wide',),
            'description': '🔗 Вставьте iframe код с YouTube, VK, RuTube и т.д.\nПример для VK: <iframe src="https://vkvideo.ru/video_ext.php?oid=-176294899&id=456247458&hash=3ac5b93799aaa07d" width="640" height="360" frameborder="0" allowfullscreen="1"></iframe>'
        }),
        ('Прямые ссылки', {
            'fields': ('url', 'youtube_id', 'vk_id', 'vk_owner_id'),
            'classes': ('collapse',),
            'description': 'Или укажите параметры для автоматической генерации кода'
        }),
        ('Настройки', {
            'fields': ('quality', 'language', 'has_subtitles', 'has_sign_language', 'is_primary', 'order')
        }),
    )
    
    def get_embed_preview(self, obj):
        if obj.embed_code:
            return format_html('<div style="max-width: 200px; max-height: 100px; overflow: hidden; background: #000; color: #fff; padding: 5px;">Код вставлен</div>')
        elif obj.video_file:
            return format_html('<video width="100" height="60"><source src="{}" type="video/mp4"></video>', obj.video_file.url)
        return "—"
    get_embed_preview.short_description = 'Предпросмотр'

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['film', 'season', 'episode', 'title', 'duration', 'release_date']
    list_filter = ['film', 'season']
    search_fields = ['film__title', 'title']
    list_editable = ['title', 'duration']
    
    fieldsets = (
        ('Основное', {
            'fields': ('film', 'season', 'episode', 'title')
        }),
        ('Детали', {
            'fields': ('description', 'duration', 'release_date')
        }),
        ('Видео', {
            'fields': ('videos',),
            'description': 'Выберите видео для этой серии'
        }),
    )
    filter_horizontal = ['videos']

@admin.register(FilmRating)
class FilmRatingAdmin(admin.ModelAdmin):
    list_display = ['film', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['film__title', 'user__username']

@admin.register(FilmReview)
class FilmReviewAdmin(admin.ModelAdmin):
    list_display = ['film', 'user', 'rating', 'created_at', 'short_text']
    list_filter = ['rating', 'created_at']
    search_fields = ['film__title', 'user__username', 'text']
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Отзыв'

@admin.register(FilmCollection)
class FilmCollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'films_count', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['films']
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'description', 'image')
        }),
        ('Фильмы', {
            'fields': ('films',),
            'classes': ('wide',)
        }),
    )
    
    def films_count(self, obj):
        return obj.films.count()
    films_count.short_description = 'Количество фильмов'