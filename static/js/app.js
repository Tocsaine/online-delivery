document.addEventListener('DOMContentLoaded', () => {
    console.log('🟢 app.js инициализирован');

    // 🚀 Применяем начальное состояние корзины сразу при загрузке страницы
    if (window.INITIAL_CART && document.querySelector('.menu-grid')) {
        renderMenuWidgets(window.INITIAL_CART);
    }

    // 🔹 Безопасное получение CSRF-токена
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    // 🔹 Единый слушатель кликов
    document.addEventListener('click', (e) => {
        const addBtn = e.target.closest('.add-to-cart-btn');
        if (addBtn) {
            e.preventDefault();
            updateCart('add', addBtn.dataset.id);
            return;
        }

        const qtyBtn = e.target.closest('.qty-btn');
        if (qtyBtn) {
            e.preventDefault();
            updateCart(qtyBtn.dataset.action, qtyBtn.dataset.id);
            return;
        }

        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            e.preventDefault();
            updateCart('delete', removeBtn.dataset.id);
            return;
        }

        const menuQtyBtn = e.target.closest('.menu-qty-btn');
        if (menuQtyBtn) {
            e.preventDefault();
            const control = menuQtyBtn.closest('.menu-qty-control');
            if (control) updateCart(menuQtyBtn.dataset.action, control.dataset.id);
            return;
        }
    });

    // 🔹 Отправка запроса
    function updateCart(action, id) {
        const csrfToken = getCSRFToken();
        if (!csrfToken) {
            console.error('🔴 CSRF-токен отсутствует');
            return;
        }

        const btn = document.querySelector(`[data-id="${id}"].add-to-cart-btn, [data-id="${id}"].qty-btn, [data-id="${id}"].remove-btn, [data-id="${id}"].menu-qty-btn`);
        const originalHTML = btn?.innerHTML;
        if (btn) {
            btn.style.opacity = '0.6';
            btn.disabled = true;
        }

        fetch('/cart/update/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({action, id})
        })
            .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
            .then(data => {
                if (data.success) {
                    const countEl = document.getElementById('cart-count');
                    if (countEl) {
                        countEl.style.transform = 'scale(1.3)';
                        setTimeout(() => {
                            countEl.textContent = data.count;
                            countEl.style.transform = 'scale(1)';
                        }, 150);
                    }

                    // Обновляем только нужные компоненты
                    if (document.querySelector('.cart-page')) updateCartPage(data.cart);
                    if (document.querySelector('.menu-grid')) renderMenuWidgets(data.cart, id); // ← передаём ID изменённого товара
                } else {
                    console.error('🔴 Ответ сервера:', data);
                }
            })
            .catch(err => console.error('🔴 Ошибка:', err))
            .finally(() => {
                if (btn && originalHTML) {
                    btn.innerHTML = originalHTML;
                    btn.style.opacity = '1';
                    btn.disabled = false;
                }
            });
    }

    // 🔹 Обновление таблицы корзины
    function updateCartPage(cart) {
        const totalEl = document.getElementById('cart-total');
        let totalSum = 0;

        for (const item of Object.values(cart)) {
            totalSum += parseFloat(item.price) * item.quantity;
        }
        if (totalEl) totalEl.textContent = `${Math.round(totalSum)} ₽`;

        if (Object.keys(cart).length === 0) {
            const cartLayout = document.querySelector('.cart-layout');
            if (cartLayout && !document.querySelector('.empty-cart')) {
                cartLayout.innerHTML = `
          <div class="empty-cart" style="grid-column:1/-1;text-align:center;padding:60px;">
            <div style="font-size:64px;margin-bottom:20px;">🛒</div>
            <h3>Корзина пуста</h3>
            <a href="/catalog/menu/" class="btn-primary" style="display:inline-block;width:auto;padding:12px 28px;">Перейти в меню</a>
          </div>`;
            }
            return;
        }

        // Удаляем строки, которых нет в новой корзине
        document.querySelectorAll('.cart-table tbody tr[data-id]').forEach(row => {
            if (!cart[row.dataset.id]) row.remove();
        });

        // Обновляем или создаём строки
        for (const [pid, item] of Object.entries(cart)) {
            let row = document.querySelector(`.cart-table tbody tr[data-id="${pid}"]`);
            const lineTotal = (parseFloat(item.price) * item.quantity).toFixed(0);

            if (row) {
                row.querySelector('.qty').textContent = item.quantity;
                row.querySelector('.line-total').textContent = `${lineTotal} ₽`;
            } else {
                row = document.createElement('tr');
                row.dataset.id = pid;
                row.innerHTML = `
          <td><div class="cart-item-info">
            ${item.image ? `<img src="${item.image}" class="cart-item-img">` : `<div class="cart-item-img placeholder-cart">🍔</div>`}
            <span class="cart-item-name">${item.name}</span>
          </div></td>
          <td class="price-col">${Math.round(parseFloat(item.price))} ₽</td>
          <td><div class="qty-control">
            <button class="qty-btn" data-action="remove" data-id="${pid}">−</button>
            <span class="qty">${item.quantity}</span>
            <button class="qty-btn" data-action="add" data-id="${pid}">+</button>
          </div></td>
          <td class="line-total">${lineTotal} ₽</td>
          <td><button class="remove-btn" data-id="${pid}">✕</button></td>`;
                document.querySelector('.cart-table tbody').appendChild(row);
            }
        }
    }
    
    // 🔹 Обновление виджетов в меню (ИСПРАВЛЕНО)
    function renderMenuWidgets(cart, changedId = null) {
        // 1️⃣ Обновляем или создаём виджеты для товаров, которые ЕСТЬ в корзине
        for (const [pid, item] of Object.entries(cart)) {
            const control = document.querySelector(`.menu-qty-control[data-id="${pid}"]`);
            const addBtn = document.querySelector(`.add-to-cart-btn[data-id="${pid}"]`);
            const qty = parseInt(item.quantity) || 0;

            if (qty > 0) {
                if (addBtn && !control) {
                    // Создаём новый виджет
                    const wrapper = document.createElement('div');
                    wrapper.className = 'menu-qty-control';
                    wrapper.dataset.id = pid;
                    wrapper.innerHTML = `
            <button class="menu-qty-btn" data-action="remove">−</button>
            <span class="menu-qty-val">${qty}</span>
            <button class="menu-qty-btn" data-action="add">+</button>`;
                    addBtn.replaceWith(wrapper);
                } else if (control) {
                    const valEl = control.querySelector('.menu-qty-val');
                    if (valEl) {
                        valEl.textContent = qty;
                        // 🎯 Анимация ТОЛЬКО для изменённого элемента
                        if (pid === changedId) {
                            valEl.style.transform = 'scale(1.2)';
                            valEl.style.transition = 'transform 0.15s ease';
                            setTimeout(() => {
                                valEl.style.transform = 'scale(1)';
                            }, 150);
                        }
                    }
                }
            }
        }

        // 2️⃣ 🔥 Убираем виджеты у товаров, которых НЕТ в корзине (количество стало 0)
        document.querySelectorAll('.menu-qty-control').forEach(control => {
            const pid = control.dataset.id;
            // Если товара больше нет в ответе сервера
            if (!cart[pid] || (cart[pid] && parseInt(cart[pid].quantity) === 0)) {
                const btn = document.createElement('button');
                btn.className = 'add-to-cart-btn';
                btn.dataset.id = pid;
                btn.textContent = 'В корзину';
                control.replaceWith(btn);
            }
        });
    }
});