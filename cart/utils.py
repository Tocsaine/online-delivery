from catalog.models import MenuItem


def get_cart(request):
    cart = request.session.get('cart', {})
    return cart


def add_to_cart(request, product_id, quantity=1):
    cart = request.session.get('cart', {})
    product = MenuItem.objects.get(pk=product_id, is_available=True)
    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += quantity
    else:
        cart[pid] = {
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else '',
            'quantity': quantity
        }
    request.session['cart'] = cart
    request.session.modified = True


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if cart[pid]['quantity'] > 1:
            cart[pid]['quantity'] -= 1
        else:
            del cart[pid]
    request.session['cart'] = cart
    request.session.modified = True


def delete_from_cart(request, product_id):
    """Полностью удаляет товар из корзины"""
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    request.session['cart'] = cart
    request.session.modified = True


def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True


def get_cart_count(cart):
    """Безопасный подсчёт: обрабатываем и строковые, и числовые ключи"""
    total = 0
    for item in cart.values():
        qty = item.get('quantity', 0)
        if isinstance(qty, str):
            qty = int(qty)
        total += qty
    return total


def get_cart_total(cart):
    """Безопасный подсчёт суммы"""
    total = 0
    for item in cart.values():
        price = item.get('price', 0)
        qty = item.get('quantity', 0)
        if isinstance(price, str):
            price = float(price)
        if isinstance(qty, str):
            qty = int(qty)
        total += price * qty
    return total
