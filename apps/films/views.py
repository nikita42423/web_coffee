from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Film, Genre, Country, FilmCollection

def film_list(request):
    """Главная страница с фильмами"""
    content_type = request.GET.get('type', 'all')
    genre_slug = request.GET.get('genre')
    year = request.GET.get('year')
    sort = request.GET.get('sort', '-created_at')
    query = request.GET.get('q', '')
    
    films = Film.objects.all()
    
    # Поиск
    if query:
        films = films.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(original_title__icontains=query)
        )
    
    # Фильтр по типу
    if content_type != 'all':
        films = films.filter(content_type=content_type)
    
    # Фильтр по жанру
    if genre_slug:
        films = films.filter(genres__slug=genre_slug)
    
    # Фильтр по году
    if year:
        films = films.filter(year=year)
    
    # Сортировка
    films = films.order_by(sort)
    
    # Пагинация
    paginator = Paginator(films, 24)  # 24 фильма на страницу
    page = request.GET.get('page')
    films_page = paginator.get_page(page)
    
    # Для фильтров
    genres = Genre.objects.annotate(films_count=Count('film')).order_by('name')
    years = Film.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    # Подборки для главной
    collections = FilmCollection.objects.all()[:5]
    
    # Популярные фильмы
    popular_films = Film.objects.order_by('-views_count')[:10]
    
    # Новинки
    new_films = Film.objects.order_by('-created_at')[:12]
    
    context = {
        'films': films_page,
        'genres': genres,
        'years': years,
        'collections': collections,
        'popular_films': popular_films,
        'new_films': new_films,
        'current_type': content_type,
        'current_genre': genre_slug,
        'current_sort': sort,
        'query': query,
    }
    return render(request, 'films/list.html', context)

def film_detail(request, slug):
    """Страница фильма"""
    film = get_object_or_404(Film, slug=slug)
    
    # Увеличиваем счетчик просмотров
    film.views_count += 1
    film.save(update_fields=['views_count'])
    
    videos = film.videos.all().order_by('-is_primary', 'order')
    
    # Похожие фильмы
    similar_films = Film.objects.filter(
        genres__in=film.genres.all()
    ).exclude(id=film.id).distinct().order_by('-views_count')[:6]
    
    context = {
        'film': film,
        'videos': videos,
        'similar_films': similar_films,
    }
    return render(request, 'films/detail.html', context)

def collection_detail(request, slug):
    """Страница подборки"""
    collection = get_object_or_404(FilmCollection, slug=slug)
    films = collection.films.all()
    
    paginator = Paginator(films, 24)
    page = request.GET.get('page')
    films_page = paginator.get_page(page)
    
    context = {
        'collection': collection,
        'films': films_page,
    }
    return render(request, 'films/collection.html', context)

def search(request):
    """Поиск фильмов"""
    query = request.GET.get('q', '')
    
    if query:
        films = Film.objects.filter(
            Q(title__icontains=query) | 
            Q(original_title__icontains=query) |
            Q(description__icontains=query) |
            Q(actors__name__icontains=query) |
            Q(directors__name__icontains=query)
        ).distinct().order_by('-views_count')
    else:
        films = Film.objects.none()
    
    paginator = Paginator(films, 24)
    page = request.GET.get('page')
    films_page = paginator.get_page(page)
    
    context = {
        'films': films_page,
        'query': query,
    }
    return render(request, 'films/search.html', context)