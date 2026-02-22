from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from apps.reviews.services import get_average_rating, get_review_count, get_reviews_for, add_review, delete_review, toggle_favorite, is_favorited

def book_list(request):
    """Список всех книг с пагинацией"""
    book_list = Book.objects.all()
    paginator = Paginator(book_list, 6)  # 6 книг на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {'page_obj': page_obj})

def book_detail(request, book_id):
    """Страница одной книги с возможностью оценки, комментариев и добавления в избранное"""
    book = get_object_or_404(Book, id=book_id)
    reviews = get_reviews_for('book', book.id)
    average_rating = get_average_rating('book', book.id) or 0
    review_count = get_review_count('book', book.id)
    user_review = None
    is_favorite = False

    if request.user.is_authenticated:
        # Получаем отзыв пользователя для этой книги
        user_reviews = reviews.filter(user=request.user)
        if user_reviews.exists():
            user_review = user_reviews.first()
        is_favorite = is_favorited(request.user, book)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        action = request.POST.get('action')
        if action == 'rate':
            rating_value = request.POST.get('rating')
            if rating_value and rating_value.isdigit():
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    add_review(request.user, book, rating_value, '')
                    messages.success(request, 'Ваша оценка сохранена.')
                else:
                    messages.error(request, 'Оценка должна быть от 1 до 5.')
            else:
                messages.error(request, 'Неверная оценка.')
        elif action == 'comment':
            text = request.POST.get('text', '').strip()
            if text:
                add_review(request.user, book, None, text)
                messages.success(request, 'Комментарий добавлен.')
            else:
                messages.error(request, 'Текст комментария не может быть пустым.')
        elif action == 'toggle_favorite':
            toggle_favorite(request.user, book)
            is_favorite = not is_favorite
            if is_favorite:
                messages.success(request, 'Книга добавлена в избранное.')
            else:
                messages.success(request, 'Книга удалена из избранного.')
        return redirect('books:book_detail', book_id=book.id)

    context = {
        'book': book,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'review_count': review_count,
        'user_review': user_review,
        'is_favorite': is_favorite,
    }
    return render(request, 'books/book_detail.html', context)

def book_search(request):
    """Поиск книг по различным критериям"""
    query = request.GET.get('q', '')
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(tags__icontains=query)
        )

    # Фильтрация по доступности
    has_subtitles = request.GET.get('has_subtitles')
    if has_subtitles == 'true':
        books = books.filter(has_subtitles=True)
    elif has_subtitles == 'false':
        books = books.filter(has_subtitles=False)

    has_sign_language = request.GET.get('has_sign_language')
    if has_sign_language == 'true':
        books = books.filter(has_sign_language=True)
    elif has_sign_language == 'false':
        books = books.filter(has_sign_language=False)

    has_audio_description = request.GET.get('has_audio_description')
    if has_audio_description == 'true':
        books = books.filter(has_audio_description=True)
    elif has_audio_description == 'false':
        books = books.filter(has_audio_description=False)

    paginator = Paginator(books, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'query': query,
        'has_subtitles': has_subtitles,
        'has_sign_language': has_sign_language,
        'has_audio_description': has_audio_description,
    })

def book_by_accessibility(request):
    """Фильтрация книг по типам доступности"""
    books = Book.objects.all()

    # Фильтрация по доступности
    has_subtitles = request.GET.get('has_subtitles')
    if has_subtitles == 'true':
        books = books.filter(has_subtitles=True)
    elif has_subtitles == 'false':
        books = books.filter(has_subtitles=False)

    has_sign_language = request.GET.get('has_sign_language')
    if has_sign_language == 'true':
        books = books.filter(has_sign_language=True)
    elif has_sign_language == 'false':
        books = books.filter(has_sign_language=False)

    has_audio_description = request.GET.get('has_audio_description')
    if has_audio_description == 'true':
        books = books.filter(has_audio_description=True)
    elif has_audio_description == 'false':
        books = books.filter(has_audio_description=False)

    paginator = Paginator(books, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'has_subtitles': has_subtitles,
        'has_sign_language': has_sign_language,
        'has_audio_description': has_audio_description,
    })
