from django.urls import path
from . import views

app_name = 'films'

urlpatterns = [
    path('', views.film_list, name='list'),
    path('search/', views.search, name='search'),
    path('collection/<slug:slug>/', views.collection_detail, name='collection'),
    path('<slug:slug>/', views.film_detail, name='detail'),
]