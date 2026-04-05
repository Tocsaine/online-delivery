from django.shortcuts import render
from .models import MenuItem, Category

def menu(request):
    categories = Category.objects.filter(is_active=True)
    items = MenuItem.objects.filter(is_available=True).select_related('category')
    return render(request, 'catalog/index.html', {
        'categories': categories,
        'items': items,
    })