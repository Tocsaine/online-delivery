from django.shortcuts import render
from django.db.models import Q
from .models import MenuItem, Category


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
