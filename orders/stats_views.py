# orders/stats_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.db.models import Sum, F, Q, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDay
from datetime import timedelta, datetime
from catalog.models import Category
from .models import Order, OrderItem
from django.conf import settings


def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def stats_dashboard(request):
    today = timezone.now().date()

    # === Получаем параметры ===
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Сравнение
    compare_enabled = request.GET.get('compare', '0') == '1'
    compare_type = request.GET.get('compare_type', 'week')  # day, week, month
    compare_value = int(request.GET.get('compare_value', 1))

    # Фильтр категории
    category_filter = request.GET.get('category')

    # === 1. Расчет дат ===
    # Период 1 (Текущий)
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            filter1 = Q(created_at__gte=start_dt, created_at__lt=end_dt)
            period1_label = f"{start_date} — {end_date}"
        except ValueError:
            filter1 = Q()
            period1_label = "Все время"
    else:
        # По умолчанию сегодня
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        filter1 = Q(created_at__date=today)
        period1_label = f"Сегодня ({today})"

    # Период 2 (Для сравнения) — УЛУЧШЕННАЯ ЛОГИКА
    filter2 = None
    period2_label = None

    if compare_enabled:
        preset = request.GET.get('compare_preset', 'yesterday')  # yesterday, last_week, last_month

        if preset == 'yesterday':
            # Вчера
            start_dt_2 = start_dt - timedelta(days=1)
            end_dt_2 = end_dt - timedelta(days=1)
            period2_label = f"Вчера ({start_dt_2.date()})"

        elif preset == 'last_week':
            # Прошлая неделя (7 дней назад)
            start_dt_2 = start_dt - timedelta(days=7)
            end_dt_2 = end_dt - timedelta(days=7)
            period2_label = f"Неделю назад ({start_dt_2.date()} — {end_dt_2.date() - timedelta(days=1)})"

        elif preset == 'last_month':
            # Прошлый месяц (~30 дней)
            start_dt_2 = start_dt - timedelta(days=30)
            end_dt_2 = end_dt - timedelta(days=30)
            period2_label = f"Месяц назад ({start_dt_2.date()} — {end_dt_2.date() - timedelta(days=1)})"

        filter2 = Q(created_at__gte=start_dt_2, created_at__lt=end_dt_2)

    # === 2. Выручка (Orders) ===
    base_order_filter = Q(status='completed')

    # Если выбрана категория, нужно фильтровать через товары в заказе
    # Но для простоты агрегации по заказам используем базовый фильтр
    revenue1 = Order.objects.filter(base_order_filter & filter1).aggregate(total=Sum('total'))['total'] or 0
    orders1 = Order.objects.filter(base_order_filter & filter1).count()

    revenue2 = orders2 = diff_revenue = diff_orders = None
    if compare_enabled and filter2:
        revenue2 = Order.objects.filter(base_order_filter & filter2).aggregate(total=Sum('total'))['total'] or 0
        orders2 = Order.objects.filter(base_order_filter & filter2).count()
        diff_revenue = revenue1 - revenue2
        diff_orders = orders1 - orders2

    # === 3. Детализация по товарам (OrderItems) ===
    from django.db.models import CharField, TextField  # <-- Добавьте этот импорт в начало файла

    items_qs = OrderItem.objects.filter(order__status='completed', product__isnull=False)

    if category_filter:
        items_qs = items_qs.filter(product__category_id=category_filter)

    items_qs1 = items_qs.filter(order__created_at__gte=start_dt, order__created_at__lt=end_dt)

    # Агрегация 1 - ИСПРАВЛЕНО: используем CharField() для output_field
    product_stats = items_qs1.values(
        prod_id=F('product__id'),
        product_name=Coalesce('product__name', Value('Удаленный товар'), output_field=CharField(max_length=255)),
        product_image=Coalesce('product__image', Value(''), output_field=CharField(max_length=255)),
        category_name=Coalesce('product__category__name', Value('Прочее'), output_field=CharField(max_length=100))
    ).annotate(
        qty=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'), output_field=DecimalField(max_digits=10, decimal_places=2))
    ).order_by('-revenue')

    # Сравнение (если нужно)
    stats2_map = {}
    if compare_enabled and filter2:
        items_qs2 = items_qs.filter(order__created_at__gte=start_dt_2, order__created_at__lt=end_dt_2)
        stats2 = items_qs2.values(prod_id=F('product__id')).annotate(
            qty=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'), output_field=DecimalField(max_digits=10, decimal_places=2))
        )
        stats2_map = {item['prod_id']: item for item in stats2}

    # Объединение данных
    products_list = []
    for item in product_stats:
        row = dict(item)
        if compare_enabled:
            p2 = stats2_map.get(item['prod_id'], {'qty': 0, 'revenue': 0})
            row['qty2'] = p2['qty']
            row['revenue2'] = p2['revenue'] or 0
            row['diff_qty'] = item['qty'] - p2['qty']
            row['diff_rev'] = item['revenue'] - (p2['revenue'] or 0)
        products_list.append(row)

    context = {
        'revenue1': revenue1,
        'orders1': orders1,
        'revenue2': revenue2,
        'orders2': orders2,
        'diff_revenue': diff_revenue,
        'diff_orders': diff_orders,
        'products': products_list,
        'compare_enabled': compare_enabled,
        'categories': Category.objects.filter(is_active=True).order_by('order'),
        'category_filter': category_filter,
        'start_date': start_date,
        'end_date': end_date,
        'compare_value': compare_value,
        'compare_type': compare_type,
        'media_url': settings.MEDIA_URL,
    }

    return render(request, 'orders/stats_dashboard.html', context)
