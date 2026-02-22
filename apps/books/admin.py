from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'has_subtitles', 'has_sign_language', 'has_audio_description', 'created_at']
    list_filter = ['has_subtitles', 'has_sign_language', 'has_audio_description']
    search_fields = ['title', 'author']
