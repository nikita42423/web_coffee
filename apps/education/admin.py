from django.contrib import admin
from .models import Course, Review


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'instructor',
        'level',
        'duration_hours',
        'has_subtitles',
        'has_sign_language',
        'has_audio_description',
        'has_transcript',
        'rating',
        'created_at',
    )
    list_filter = (
        'level',
        'has_subtitles',
        'has_sign_language',
        'has_audio_description',
        'has_transcript',
        'platform',
    )
    search_fields = (
        'title',
        'instructor',
        'description',
        'tags',
    )
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'instructor', 'description', 'duration_hours', 'level')
        }),
        ('Доступность', {
            'fields': ('has_subtitles', 'has_sign_language', 'has_audio_description', 'has_transcript')
        }),
        ('Метаданные', {
            'fields': ('tags', 'rating', 'course_url', 'platform')
        }),
    )
    ordering = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('course__title', 'user__username', 'comment')
    ordering = ('-created_at',)
