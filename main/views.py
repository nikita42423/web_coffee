from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db.models import Q
from apps.books.models import Book
from apps.films.models import Film
from apps.education.models import Course

def index(request):
    """Главная страница с поиском"""
    # Получаем несколько последних записей для отображения на главной
    recent_books = Book.objects.all()[:3]
    recent_films = Film.objects.all()[:3]
    recent_courses = Course.objects.all()[:3]

    return render(request, 'main/index.html', {
        'recent_books': recent_books,
        'recent_films': recent_films,
        'recent_courses': recent_courses,
    })

def search(request):
    """Глобальный поиск по всем типам контента"""
    query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')

    results = {
        'books': [],
        'films': [],
        'courses': [],
        'total': 0
    }

    if query:
        if content_type in ['all', 'books']:
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            results['books'] = books
            results['total'] += books.count()

        if content_type in ['all', 'films']:
            films = Film.objects.filter(
                Q(title__icontains=query) |
                Q(director__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            results['films'] = films
            results['total'] += films.count()

        if content_type in ['all', 'courses']:
            courses = Course.objects.filter(
                Q(title__icontains=query) |
                Q(instructor__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            results['courses'] = courses
            results['total'] += courses.count()

    return render(request, 'main/search_results.html', {
        'query': query,
        'results': results,
        'content_type': content_type
    })
