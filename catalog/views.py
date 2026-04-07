from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import MenuItem, Category
from django.http import JsonResponse


def menu(request):
    # Получаем все активные категории для фильтра
    categories = Category.objects.filter(is_active=True)

    # Получаем выбранный фильтр из query-параметра
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    # Базовый запрос: только доступные блюда
    items = MenuItem.objects.filter(is_available=True).select_related('category')

    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Применяем фильтр, если категория выбрана
    if category_slug:
        items = items.filter(category__slug=category_slug)

    context = {
        'categories': categories,
        'items': items,
        'active_category': category_slug,  # Для подсветки активной кнопки
        'search_query': search_query,
    }

    # 🔥 Если запрос AJAX — возвращаем только фрагмент сетки
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'catalog/_menu_grid.html', context)

    return render(request, 'catalog/index.html', context)


def menu_item_detail(request, pk):
    """Возвращает данные товара в формате JSON"""
    item = get_object_or_404(MenuItem, pk=pk, is_available=True)
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'price': float(item.price),
        'description': item.description,
        'full_description': item.full_description or "",
        'weight': item.weight or 0,
        'image': item.image.url if item.image else None,
        'category': item.category.name if item.category else "",
        'calories': item.calories or 0,
        'proteins': float(item.proteins) if item.proteins else 0,
        'fats': float(item.fats) if item.fats else 0,
        'carbs': float(item.carbs) if item.carbs else 0,

    })
