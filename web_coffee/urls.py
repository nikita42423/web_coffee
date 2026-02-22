from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),                         # Главная страница
    path('books/', include('apps.books.urls')),             # Книги
    path('films/', include('apps.films.urls')),             # Фильмы
    path('education/', include('apps.education.urls')),     # Образование
    path('forum/', include('apps.forum.urls')),             # Форум
    path('sites/', include('apps.sites.urls')),             # Интернет-ресурсы

    # Аутентификация
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
