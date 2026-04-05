from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from . import utils
from catalog.models import MenuItem


def cart_view(request):
    cart = utils.get_cart(request)
    total = utils.get_cart_total(cart)
    return render(request, 'cart/cart.html', {'cart': cart, 'total': total})


@require_POST
def update_cart(request):
    import json
    data = json.loads(request.body)
    action = data.get('action')
    product_id = data.get('id')

    if action == 'add':
        utils.add_to_cart(request, product_id)
    elif action == 'remove':
        utils.remove_from_cart(request, product_id)
    elif action == 'clear':
        utils.clear_cart(request)
    elif action == 'delete':
        utils.delete_from_cart(request, product_id)

    cart = utils.get_cart(request)
    return JsonResponse({
        'success': True,
        'count': utils.get_cart_count(cart),
        'total': utils.get_cart_total(cart),
        'cart': cart
    })


def cart_count(request):
    """Контекст-процессор для отображения счётчика в шапке"""
    cart = utils.get_cart(request)
    count = utils.get_cart_count(cart)
    print(f"DEBUG CART COUNT: {count}, session: {request.session.get('cart')}")
    return {'cart_count': utils.get_cart_count(cart)}
