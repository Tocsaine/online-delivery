document.addEventListener('DOMContentLoaded', () => {
    // CSRF токен для fetch
    const getCookie = name => {
        let v = null;
        document.cookie.split(';').forEach(c => {
            const [k, val] = c.trim().split('=');
            if (k === name) v = decodeURIComponent(val);
        });
        return v;
    };

    const sendCartUpdate = async (action, id) => {
        try {
            const res = await fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({action, id})
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('cart-count').textContent = data.count;
                const cartTotalEl = document.getElementById('cart-total');
                if (cartTotalEl) {
                    cartTotalEl.textContent = `${data.total.toFixed(2)} ₽`;
                }
                location.reload(); // Для простоты демо. Можно сделать частичное обновление DOM.
            }
        } catch (e) {
            console.error('Cart error:', e);
        }
    };

    // Кнопки в меню
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => sendCartUpdate('add', btn.dataset.id));
    });

    // Кнопки +/- в корзине
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', () => sendCartUpdate(btn.dataset.action, btn.dataset.id));
    });

    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', () => sendCartUpdate('delete', btn.dataset.id));
    });
});