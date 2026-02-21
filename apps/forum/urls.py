from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_index, name='index'),
    path('category/<slug:slug>/', views.category_topics, name='category'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic'),
    path('create/', views.create_topic, name='create_topic'),
    path('topic/<int:topic_id>/post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('search/', views.search, name='search'),
]