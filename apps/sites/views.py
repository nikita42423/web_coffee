from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Site, SiteCategory

def site_list(request):
    """Главная страница со списком государственных сайтов"""
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')

    sites = Site.objects.filter(is_published=True)

    # Поиск
    if query:
        sites = sites.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(url__icontains=query)
        )

    # Фильтр по категории
    if category_slug:
        sites = sites.filter(category__slug=category_slug)

    # Категории для фильтра
    categories = SiteCategory.objects.annotate(sites_count=Count('sites'))

    # Рекомендуемые сайты
    featured_sites = Site.objects.filter(is_featured=True, is_published=True)[:5]

    # Пагинация
    paginator = Paginator(sites, 12)
    page = request.GET.get('page')
    sites_page = paginator.get_page(page)

    context = {
        'sites': sites_page,
        'categories': categories,
        'featured_sites': featured_sites,
        'current_category': category_slug,
        'query': query,
    }
    return render(request, 'sites/list.html', context)

def site_detail(request, slug):
    """Детальная страница сайта"""
    site = get_object_or_404(Site, slug=slug, is_published=True)

    # Увеличиваем счетчик
    site.visits_count += 1
    site.save(update_fields=['visits_count'])

    # Похожие сайты
    similar_sites = Site.objects.filter(
        category=site.category,
        is_published=True
    ).exclude(id=site.id)[:4]
    
    context = {
        'site': site,
        'similar_sites': similar_sites,
    }
    return render(request, 'sites/detail.html', context)

def redirect_to_site(request, slug):
    site = get_object_or_404(Site, slug=slug)
    site.visits_count += 1
    site.save(update_fields=['visits_count'])
    return redirect(site.url)
