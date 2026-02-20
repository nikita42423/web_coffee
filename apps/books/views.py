from django.shortcuts import render, get_object_or_404
from .models import Book

def book_detail(request, book_id):
    """Страница одной книги с обычным текстом"""
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})