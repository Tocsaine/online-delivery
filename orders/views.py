from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart import utils as cart_utils
from .models import Order, OrderItem
from decimal import Decimal
from accounts.models import Profile, Address
from cart import utils


@login_required
def checkout(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    saved_addresses = Address.objects.filter(user=request.user)

    # Получаем последний адрес из истории заказов
    last_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    last_address = last_order.address if last_order else None

    cart = utils.get_cart(request)
    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('catalog:menu')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()

        address_id = request.POST.get('address_id')
        new_address_text = request.POST.get('address', '').strip()
        save_address_check = request.POST.get('save_address') == 'on'

        final_address = ""

        if address_id == 'new':
            final_address = new_address_text
            if save_address_check and final_address:
                Address.objects.create(user=request.user, text=final_address)
        elif address_id == 'last':
            # Если выбрали последний адрес, берем его из переменной
            final_address = last_address if last_address else new_address_text
        else:
            # Выбрали из сохраненных
            addr_obj = get_object_or_404(Address, pk=address_id, user=request.user)
            final_address = addr_obj.text

        if not all([name, phone, final_address]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'orders/checkout.html', {
                'total': utils.get_cart_total(cart),
                'profile': profile,
                'saved_addresses': saved_addresses,
                'last_address': last_address
            })

        profile.phone = phone
        profile.save()

        order = Order.objects.create(
            user=request.user,
            customer_name=name,
            phone=phone,
            address=final_address,
            total=utils.get_cart_total(cart)
        )

        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=int(pid),
                quantity=int(item['quantity']),
                price=Decimal(str(item['price']))
            )

        cart_utils.clear_cart(request)
        return redirect('orders:success', order_id=order.pk)

    return render(request, 'orders/checkout.html', {
        'total': utils.get_cart_total(cart),
        'profile': profile,
        'saved_addresses': saved_addresses,
        'last_address': last_address
    })


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
