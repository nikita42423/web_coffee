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
        from apps.books.models import Favorite
        favorite_books = Favorite.objects.filter(user=self.request.user).select_related('book')
        context['favorite_books'] = favorite_books
        return context
