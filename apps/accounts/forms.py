# apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Дополнительные поля для доступности
    prefers_subtitles = forms.BooleanField(
        required=False,
        initial=True,
        label='Предпочитаю контент с субтитрами',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    prefers_sign_language = forms.BooleanField(
        required=False,
        label='Предпочитаю контент с жестовым переводом',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    prefers_audio_description = forms.BooleanField(
        required=False,
        label='Предпочитаю контент с аудиоописанием',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы Bootstrap для полей
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = 'Только буквы, цифры и символы @/./+/-/_'
        self.fields['password1'].help_text = 'Пароль должен содержать не менее 8 символов'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Здесь можно сохранить дополнительные поля в профиль
            # когда создадите модель Profile
        return user
