from django.urls import path
from . import views

app_name = 'films'

urlpatterns = [
    path('', views.film_list, name='film_list'),
]
