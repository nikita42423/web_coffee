from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Review


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
    """Детальная страница курса с отзывами"""
    course = get_object_or_404(Course, id=course_id)
    recommendations = Course.objects.exclude(id=course_id).filter(tags__icontains=course.tags)[:3]
    reviews = course.reviews.all().select_related('user').order_by('-created_at')

    # Обработка отправки отзыва
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            rating = int(rating)
            # Создать или обновить отзыв
            review, created = Review.objects.update_or_create(
                course=course,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            course.update_rating()
            messages.success(request, 'Ваш отзыв сохранён!' if created else 'Ваш отзыв обновлён!')
            return redirect('education:course_detail', course_id=course.id)
        else:
            messages.error(request, 'Пожалуйста, выберите оценку от 1 до 5.')

    context = {
        'course': course,
        'recommendations': recommendations,
        'reviews': reviews,
        'user_review': reviews.filter(user=request.user).first() if request.user.is_authenticated else None,
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


def free_courses(request):
    """Бесплатные курсы (заглушка, так как поле цены нет)"""
    # Показываем все курсы, но можно добавить поле is_free в будущем
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'title': 'Все курсы (бесплатные)',
    }
    return render(request, 'education/free.html', context)
