from django.shortcuts import render, get_object_or_404
from .models import Film

def film_list(request):
    films = Film.objects.all()
    return render(request, 'films/list.html', {'films': films})

def film_detail(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    return render(request, 'films/detail.html', {'film': film})

def film_search(request):
    query = request.GET.get('q', '')
    films = Film.objects.filter(title__icontains=query) if query else []
    return render(request, 'films/search.html', {'films': films, 'query': query})
