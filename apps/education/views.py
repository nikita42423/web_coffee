from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from apps.reviews.services import get_average_rating, get_review_count, get_reviews_for, add_review, toggle_favorite, is_favorited


def course_list(request):
    """Список всех курсов с фильтрацией по уровню и доступности"""
    courses = Course.objects.all()

    # Фильтрация по уровню
    level = request.GET.get('level')
    if level in ['beginner', 'intermediate', 'advanced']:
        courses = courses.filter(level=level)

    # Фильтрация по доступности
    if request.GET.get('has_subtitles') == 'on':
        courses = courses.filter(has_subtitles=True)
    if request.GET.get('has_sign_language') == 'on':
        courses = courses.filter(has_sign_language=True)
    if request.GET.get('has_audio_description') == 'on':
        courses = courses.filter(has_audio_description=True)
    if request.GET.get('has_transcript') == 'on':
        courses = courses.filter(has_transcript=True)

    # Пагинация
    paginator = Paginator(courses, 9)  # 9 курсов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'level_filter': level,
        'total_courses': courses.count(),
    }
    return render(request, 'education/list.html', context)


def course_detail(request, course_id):
    """Страница одного курса с возможностью оценки, комментариев и добавления в избранное"""
    course = get_object_or_404(Course, id=course_id)
    recommendations = Course.objects.exclude(id=course_id).filter(tags__icontains=course.tags)[:3]
    reviews = get_reviews_for('course', course.id)
    average_rating = get_average_rating('course', course.id) or 0
    review_count = get_review_count('course', course.id)
    user_review = None
    is_favorite = False

    if request.user.is_authenticated:
        # Получаем отзыв пользователя для этого курса
        user_reviews = reviews.filter(user=request.user)
        if user_reviews.exists():
            user_review = user_reviews.first()
        is_favorite = is_favorited(request.user, course)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        action = request.POST.get('action')
        if action == 'rate':
            rating_value = request.POST.get('rating')
            if rating_value and rating_value.isdigit():
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    add_review(request.user, course, rating_value, '')
                    messages.success(request, 'Ваша оценка сохранена.')
                else:
                    messages.error(request, 'Оценка должна быть от 1 до 5.')
            else:
                messages.error(request, 'Неверная оценка.')
        elif action == 'comment':
            text = request.POST.get('text', '').strip()
            if text:
                add_review(request.user, course, None, text)
                messages.success(request, 'Комментарий добавлен.')
            else:
                messages.error(request, 'Текст комментария не может быть пустым.')
        elif action == 'toggle_favorite':
            toggle_favorite(request.user, course)
            is_favorite = not is_favorite
            if is_favorite:
                messages.success(request, 'Курс добавлен в избранное.')
            else:
                messages.success(request, 'Курс удалён из избранного.')
        return redirect('education:course_detail', course_id=course.id)

    context = {
        'course': course,
        'recommendations': recommendations,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'review_count': review_count,
        'user_review': user_review,
        'is_favorite': is_favorite,
    }
    return render(request, 'education/detail.html', context)


def course_by_level(request, level):
    """Курсы по уровню сложности"""
    if level not in ['beginner', 'intermediate', 'advanced']:
        level = 'beginner'
    courses = Course.objects.filter(level=level)
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'level': level,
        'level_display': dict(Course.LEVEL_CHOICES).get(level, 'Начальный'),
    }
    return render(request, 'education/level.html', context)
