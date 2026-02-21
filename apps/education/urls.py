from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('level/<str:level>/', views.course_by_level, name='course_by_level'),
    path('free/', views.free_courses, name='free_courses'),
]
