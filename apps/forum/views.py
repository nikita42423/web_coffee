from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.urls import reverse
from .models import ForumCategory, ForumTopic, ForumPost

def forum_index(request):
    """Главная страница форума"""
    categories = ForumCategory.objects.filter(parent__isnull=True, is_active=True)
    
    # Статистика
    total_topics = ForumTopic.objects.filter(is_active=True).count()
    total_posts = ForumPost.objects.count()
    total_users = User.objects.count()
    
    # Последние темы
    recent_topics = ForumTopic.objects.filter(is_active=True)\
                     .select_related('author', 'category')\
                     .order_by('-updated_at')[:10]
    
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
    }
    return render(request, 'forum/index.html', context)

def category_topics(request, slug):
    """Список тем в категории"""
    category = get_object_or_404(ForumCategory, slug=slug, is_active=True)
    topics = ForumTopic.objects.filter(category=category, is_active=True)\
              .select_related('author')
    
    # Поиск
    query = request.GET.get('q')
    if query:
        topics = topics.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    # Пагинация
    paginator = Paginator(topics, 20)
    page = request.GET.get('page')
    topics_page = paginator.get_page(page)
    
    context = {
        'category': category,
        'topics': topics_page,
        'query': query,
    }
    return render(request, 'forum/category.html', context)

def topic_detail(request, topic_id):
    """Просмотр темы"""
    topic = get_object_or_404(ForumTopic, id=topic_id, is_active=True)
    
    # Увеличиваем просмотры
    topic.views += 1
    topic.save(update_fields=['views'])
    
    # Получаем сообщения
    posts = topic.posts.select_related('author').all()
    
    # Пагинация сообщений
    paginator = Paginator(posts, 15)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    
    context = {
        'topic': topic,
        'posts': posts_page,
    }
    return render(request, 'forum/topic.html', context)

@login_required
def create_topic(request):
    """Создание новой темы"""
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content = request.POST.get('content')
        
        if title and category_id and content:
            category = get_object_or_404(ForumCategory, id=category_id)
            topic = ForumTopic.objects.create(
                title=title,
                category=category,
                author=request.user,
                content=content
            )
            messages.success(request, 'Тема успешно создана!')
            return redirect('forum:topic', topic_id=topic.id)
        else:
            messages.error(request, 'Заполните все поля')
    
    categories = ForumCategory.objects.filter(is_active=True)
    return render(request, 'forum/create_topic.html', {'categories': categories})

@login_required
def create_post(request, topic_id):
    """Добавление ответа в тему"""
    topic = get_object_or_404(ForumTopic, id=topic_id, is_active=True)
    
    if topic.is_closed:
        messages.error(request, 'Тема закрыта для ответов')
        return redirect('forum:topic', topic_id=topic.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            post = ForumPost.objects.create(
                topic=topic,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            
            # Обновляем количество ответов в теме
            topic.posts_count = topic.posts.count()
            topic.save(update_fields=['posts_count'])
            
            messages.success(request, 'Ответ добавлен!')
            return redirect(f"{topic.get_absolute_url()}?page=last#post-{post.id}")
    
    return redirect('forum:topic', topic_id=topic.id)

@login_required
def edit_post(request, post_id):
    """Редактирование сообщения"""
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Проверка прав
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование этого сообщения')
        return redirect(post.get_absolute_url())
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            post.content = content
            post.save()
            messages.success(request, 'Сообщение обновлено')
            return redirect(post.get_absolute_url())
    
    return render(request, 'forum/edit_post.html', {'post': post})

def search(request):
    """Поиск по форуму"""
    query = request.GET.get('q', '')
    
    if query:
        topics = ForumTopic.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(posts__content__icontains=query)
        ).filter(is_active=True).distinct()[:30]
    else:
        topics = []
    
    context = {
        'query': query,
        'topics': topics,
    }
    return render(request, 'forum/search.html', context)
