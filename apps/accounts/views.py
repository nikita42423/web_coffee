# apps/accounts/views.py
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Регистрация
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Добавляем сообщение об успешной регистрации
        messages.success(self.request, 'Регистрация прошла успешно! Теперь вы можете войти.')
        return response

    def form_invalid(self, form):
        # Вместо общего сообщения, ошибки будут отображаться в форме
        return self.render_to_response(self.get_context_data(form=form))

# Вход
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

# Выход
class CustomLogoutView(LogoutView):
    template_name = 'accounts/logged_out.html'

# Профиль
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.contenttypes.models import ContentType
        from apps.reviews.models import Favorite
        from apps.books.models import Book
        from apps.education.models import Course
        from apps.films.models import Film

        # Получаем все избранные записи пользователя
        favorites = Favorite.objects.filter(user=self.request.user)

        # Группируем по типам контента
        book_ids = []
        course_ids = []
        film_ids = []

        for fav in favorites:
            if fav.content_type.model == 'book':
                book_ids.append(fav.object_id)
            elif fav.content_type.model == 'course':
                course_ids.append(fav.object_id)
            elif fav.content_type.model == 'film':
                film_ids.append(fav.object_id)

        # Получаем объекты
        favorite_books = Book.objects.filter(id__in=book_ids) if book_ids else []
        favorite_courses = Course.objects.filter(id__in=course_ids) if course_ids else []
        favorite_films = Film.objects.filter(id__in=film_ids) if film_ids else []

        # Создаем словарь для быстрого сопоставления объекта с датой добавления в избранное
        fav_dates = {}
        for fav in favorites:
            key = (fav.content_type.model, fav.object_id)
            fav_dates[key] = fav.created_at

        # Передаем в контекст
        context['favorite_books'] = [
            {'book': book, 'created_at': fav_dates.get(('book', book.id))}
            for book in favorite_books
        ]
        context['favorite_courses'] = [
            {'course': course, 'created_at': fav_dates.get(('course', course.id))}
            for course in favorite_courses
        ]
        context['favorite_films'] = [
            {'film': film, 'created_at': fav_dates.get(('film', film.id))}
            for film in favorite_films
        ]

        # Статистика для боковой панели
        context['books_count'] = len(favorite_books)
        context['films_count'] = len(favorite_films)
        context['courses_count'] = len(favorite_courses)

        return context
