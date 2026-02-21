from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('search/', views.book_search, name='book_search'),
    path('accessibility/', views.book_by_accessibility, name='book_by_accessibility'),
    path('<int:book_id>/', views.book_detail, name='book_detail'),
]