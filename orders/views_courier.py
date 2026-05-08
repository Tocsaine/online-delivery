from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order


# 1. Панель курьера (список заказов)
@login_required
def courier_dashboard(request):
    # 🔒 Проверка: если это не курьер — выкидываем
    if request.user.profile.role != 'courier':
        messages.error(request, "Доступ запрещен. Это панель для курьеров.")
        return redirect('catalog:menu')

    # Доступные заказы (кухня приготовила, ждет курьера)
    available_orders = Order.objects.filter(status='packing').order_by('created_at')

    # Мои активные заказы (я везу прямо сейчас)
    my_active_orders = Order.objects.filter(courier=request.user, status='delivering').order_by('-created_at')

    # История (я доставил)
    my_history = Order.objects.filter(
        courier=request.user
    ).exclude(
        status__in=['new', 'preparing', 'packing', 'delivering']  # Исключаем неактивные статусы
    ).order_by('-updated_at')[:20]

    return render(request, 'orders/courier_dashboard.html', {
        'available_orders': available_orders,
        'my_active_orders': my_active_orders,
        'my_history': my_history,
    })


# 2. Взять заказ в доставку
@login_required
def accept_order(request, order_id):
    if request.user.profile.role != 'courier':
        return redirect('catalog:menu')

    order = get_object_or_404(Order, id=order_id, status='packing')

    order.courier = request.user
    order.status = 'delivering'
    order.save()

    messages.success(request, f"Заказ #{order.id} принят в доставку!")
    return redirect('orders:courier_dashboard')


# 3. Завершить доставку
@login_required
def complete_delivery(request, order_id):
    if request.user.profile.role != 'courier':
        return redirect('catalog:menu')

    # Проверяем, что заказ принадлежит этому курьеру и в статусе доставки
    order = get_object_or_404(Order, id=order_id, courier=request.user, status='delivering')

    order.status = 'awaiting_confirmation'
    order.save()

    messages.success(request, f"Заказ #{order.id} доставлен. Ожидает подтверждения клиентом.")
    return redirect('orders:courier_dashboard')
