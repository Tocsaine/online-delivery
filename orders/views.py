from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart import utils as cart_utils
from .models import Order, OrderItem
from decimal import Decimal

def checkout(request):
    cart = cart_utils.get_cart(request)
    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('catalog:menu')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, phone, address]):
            messages.error(request, 'Заполните все поля')
            return render(request, 'orders/checkout.html', {'total': cart_utils.get_cart_total(cart)})

        order = Order.objects.create(
            customer_name=name,
            phone=phone,
            address=address,
            total=cart_utils.get_cart_total(cart),
            user=request.user if request.user.is_authenticated else None,
        )

        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=int(pid),
                quantity=item['quantity'],
                price=Decimal(str(item['price']))
            )

        cart_utils.clear_cart(request)
        return redirect('orders:success', order_id=order.pk)

    return render(request, 'orders/checkout.html', {'total': cart_utils.get_cart_total(cart)})

def success(request, order_id):
    order = Order.objects.get(pk=order_id)
    return render(request, 'orders/success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    """Страница деталей заказа — доступна только владельцу"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    # Если заказ не принадлежит пользователю — редирект в профиль
    if order.user != request.user:
        return redirect('accounts:account')

    return render(request, 'orders/order_detail.html', {'order': order})