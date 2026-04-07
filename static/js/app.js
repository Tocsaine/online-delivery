document.addEventListener('DOMContentLoaded', () => {
    console.log('🟢 app.js инициализирован');

    // 🔑 ЕДИНЫЙ ИСТОЧНИК ПРАВДЫ
    let currentCart = window.INITIAL_CART || {};
    renderMenuWidgets(currentCart);

    // ⏱️ Debounce утилита
    function debounce(func, delay) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func(...args), delay);
        };
    }

    const phoneInputs = document.querySelectorAll('.phone-mask');

    phoneInputs.forEach(input => {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, ''); // Убираем все не-цифры
            let formattedValue = '';

            // Если пусто, ставим +7
            if (!value) {
                e.target.value = '';
                return;
            }

            // Всегда начинаем с 7 (если пользователь ввел 8, меняем на 7)
            if (['7', '8', '9'].indexOf(value[0]) > -1) {
                if (value[0] === '9') value = '7' + value; // Если начали с 9
                value = '7' + value.substring(1); // Гарантируем, что первая цифра 7
            }

            // Форматирование: +7 (XXX) XXX-XX-XX
            if (value.length > 0) formattedValue = '+7';
            if (value.length > 1) formattedValue += ' (' + value.substring(1, 4);
            if (value.length >= 5) formattedValue += ') ' + value.substring(4, 7);
            if (value.length >= 8) formattedValue += '-' + value.substring(7, 9);
            if (value.length >= 10) formattedValue += '-' + value.substring(9, 11);

            e.target.value = formattedValue;
        });

        // Очистка при фокусе (если там только "+7")
        input.addEventListener('focus', function (e) {
            if (e.target.value === '+7') e.target.value = '';
        });

        // Восстановление префикса при уходе (blur)
        input.addEventListener('blur', function (e) {
            if (e.target.value === '') e.target.value = '+7';
        });

        // Устанавливаем начальное значение
        if (!input.value) input.value = '+7';
    });

    // ========================================
    // 🔥 ФУНКЦИИ МОДАЛЬНОГО ОКНА (внутри DOMContentLoaded)
    // ========================================

    let currentModalItemId = null;

    async function openItemModal(itemId) {
        currentModalItemId = itemId;
        const modal = document.getElementById('item-modal');
        if (!modal) return;

        // 🔥 1. СБРОС СОСТОЯНИЯ: возвращаем кнопку по умолчанию перед загрузкой
        const actionsContainer = document.getElementById('modal-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = `
        <button class="modal-add-to-cart" id="modal-add-btn" data-modal-action="add">
          🛒 Добавить в корзину
        </button>
      `;
        }

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        try {
            const res = await fetch(`/api/item/${itemId}/`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            // 🔥 2. Безопасная функция обновления (не крашится, если элемента нет)
            const setText = (id, text) => {
                const el = document.getElementById(id);
                if (el) el.textContent = text;
            };

            // Заполняем основные данные
            setText('modal-title', data.name);
            setText('modal-price', `${data.price.toFixed(0)} ₽`);
            setText('modal-description', data.description);
            setText('modal-category', data.category);

            const fullDescSection = document.getElementById('modal-full-desc-section');
            if (fullDescSection) {
                if (data.full_description) {
                    setText('modal-full-description', data.full_description);
                    fullDescSection.style.display = 'block';
                } else {
                    fullDescSection.style.display = 'none';
                }
            }

            // КБЖУ
            const nutritionSection = document.getElementById('modal-nutrition-section');
            if (nutritionSection) {
                if (data.calories > 0 || data.proteins > 0 || data.fats > 0 || data.carbs > 0) {
                    setText('modal-calories', data.calories);
                    setText('modal-proteins', data.proteins);
                    setText('modal-fats', data.fats);
                    setText('modal-carbs', data.carbs);
                    nutritionSection.style.display = 'block';
                } else {
                    nutritionSection.style.display = 'none';
                }
            }

            // Вес
            const weightSection = document.getElementById('modal-weight-section');
            if (weightSection) {
                if (data.weight && data.weight > 0) {
                    setText('modal-weight', `${data.weight} г`);
                    weightSection.style.display = 'block';
                } else {
                    weightSection.style.display = 'none';
                }
            }

            // Изображение
            const img = document.getElementById('modal-img');
            const placeholder = document.getElementById('modal-img-placeholder');
            if (data.image) {
                if (img) {
                    img.src = data.image;
                    img.style.display = 'block';
                }
                if (placeholder) placeholder.style.display = 'none';
            } else {
                if (img) img.style.display = 'none';
                if (placeholder) placeholder.style.display = 'flex';
            }

            // 🔥 3. Проверяем корзину и рисуем нужный интерфейс (+/- или кнопку)
            const itemInCart = currentCart[itemId];
            const currentQty = itemInCart ? parseInt(itemInCart.quantity) : 0;
            updateModalCartUI(currentQty);

        } catch (err) {
            console.error('❌ Ошибка модалки:', err);
            closeItemModal();
            alert('Не удалось загрузить информацию о товаре');
        }
    }

    function closeItemModal() {
        const modal = document.getElementById('item-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Разблокируем скролл
        }
        currentModalItemId = null;
    }

    async function addToCartFromModal() {
        if (!currentModalItemId) return;
        const btn = document.getElementById('modal-add-btn');
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Добавляем...';
        }
        // Просто вызываем общую функцию. Модалка останется открытой.
        updateCart('add', currentModalItemId);
    }

    // 🔥 ПРОБРАСЫВАЕМ ФУНКЦИИ В ГЛОБАЛЬНУЮ ОБЛАСТЬ (для inline-обработчиков и после AJAX)
    window.openItemModal = openItemModal;
    window.closeItemModal = closeItemModal;
    window.addToCartFromModal = addToCartFromModal;

    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeItemModal();
    });

    // ========================================
    // 🔹 CSRF Token
    // ========================================
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) return decodeURIComponent(cookie.substring(name.length + 1));
        }
        return null;
    }

    // ========================================
    // 🔹 Единый делегированный обработчик кликов
    // ========================================
    document.addEventListener('click', (e) => {

        // 1. Кнопки +/- в меню (виджет количества)
        const menuQtyBtn = e.target.closest('.menu-qty-btn');
        if (menuQtyBtn) {
            e.preventDefault();
            const control = menuQtyBtn.closest('.menu-qty-control');
            if (control) updateCart(menuQtyBtn.dataset.action, control.dataset.id);
            return;
        }

        // 2. Кнопка "В корзину" (в меню и в модалке)
        const addBtn = e.target.closest('.add-to-cart-btn, #modal-add-btn');
        if (addBtn) {
            e.preventDefault();
            // Если это кнопка в модалке
            if (addBtn.id === 'modal-add-btn') {
                addToCartFromModal();
            } else {
                updateCart('add', addBtn.dataset.id);
            }
            return;
        }

        // 3. Крестик удаления в корзине
        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            e.preventDefault();
            updateCart('delete', removeBtn.dataset.id);
            return;
        }

        // 4. Кнопки +/- в таблице корзины
        const cartQtyBtn = e.target.closest('.qty-btn');
        if (cartQtyBtn) {
            e.preventDefault();
            updateCart(cartQtyBtn.dataset.action, cartQtyBtn.dataset.id);
            return;
        }

        // 5. 🔥 Клик по кликабельной зоне карточки → открываем модалку
        const clickableZone = e.target.closest('.card-clickable');
        if (clickableZone) {
            e.preventDefault();
            const card = clickableZone.closest('.menu-card');
            if (card && card.dataset.itemId) {
                openItemModal(card.dataset.itemId);
            }
            return;
        }

        // 6. 🔥 Обработчики модального окна (закрытие по крестику или фону)
        const modalClose = e.target.closest('[data-modal-action="close"]');
        if (modalClose) {
            e.preventDefault();
            closeItemModal();
            return;
        }

        const modalOverlay = e.target.closest('#item-modal');
        if (modalOverlay && e.target === modalOverlay) {
            e.preventDefault();
            closeItemModal();
            return;
        }
    });

    // 🔥 Обновление интерфейса корзины внутри модалки
    function updateModalCartUI(qty) {
        const container = document.getElementById('modal-actions');
        if (!container) return;

        if (qty > 0) {
            container.innerHTML = `
        <div class="modal-qty-control">
          <button class="modal-qty-btn" onclick="handleModalQty('remove')">−</button>
          <span class="modal-qty-val">${qty}</span>
          <button class="modal-qty-btn" onclick="handleModalQty('add')">+</button>
        </div>
      `;
        } else {
            container.innerHTML = `
        <button class="modal-add-to-cart" id="modal-add-btn" data-modal-action="add">
          Добавить в корзину
        </button>
      `;
        }
    }

    // 🔥 Глобальный обработчик кликов по +/- в модалке
    window.handleModalQty = function (action) {
        if (currentModalItemId) {
            updateCart(action, currentModalItemId);
        }
    };

    // ========================================
    // 🔹 Отправка запроса в корзину (без изменений)
    // ========================================
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
                    currentCart = data.cart;

                    // Обновляем счётчик в шапке
                    const countEl = document.getElementById('cart-count');
                    if (countEl) {
                        countEl.style.transform = 'scale(1.3)';
                        setTimeout(() => {
                            countEl.textContent = data.count;
                            countEl.style.transform = 'scale(1)';
                        }, 150);
                    }

                    // Обновляем страницу корзины и виджеты меню
                    if (document.querySelector('.cart-page')) updateCartPage(currentCart);
                    if (document.querySelector('.menu-grid')) renderMenuWidgets(currentCart, id);

                    // 🔥 ОБНОВЛЯЕМ МОДАЛКУ, ЕСЛИ ОНА ОТКРЫТА ДЛЯ ЭТОГО ТОВАРА
                    if (currentModalItemId && String(currentModalItemId) === String(id)) {
                        const qty = currentCart[id] ? parseInt(currentCart[id].quantity) : 0;
                        updateModalCartUI(qty);
                    }
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

    // ========================================
    // 🔹 Обновление таблицы корзины (без изменений)
    // ========================================
    function updateCartPage(cart) {
        const totalEl = document.getElementById('cart-total');
        let totalSum = Object.values(cart).reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
        if (totalEl) totalEl.textContent = `${Math.round(totalSum)} ₽`;

        if (Object.keys(cart).length === 0) {
            const cartLayout = document.querySelector('.cart-layout');
            if (cartLayout && !document.querySelector('.empty-cart')) {
                cartLayout.innerHTML = `<div class="empty-cart" style="grid-column:1/-1;text-align:center;padding:60px;"><div style="font-size:64px;margin-bottom:20px;">🛒</div><h3>Корзина пуста</h3><a href="/" class="btn-primary" style="display:inline-block;width:auto;padding:12px 28px;">Перейти в меню</a></div>`;
            }
            return;
        }

        document.querySelectorAll('.cart-table tbody tr[data-id]').forEach(row => {
            if (!cart[row.dataset.id]) row.remove();
        });

        for (const [pid, item] of Object.entries(cart)) {
            let row = document.querySelector(`.cart-table tbody tr[data-id="${pid}"]`);
            const lineTotal = (parseFloat(item.price) * item.quantity).toFixed(0);
            if (row) {
                row.querySelector('.qty').textContent = item.quantity;
                row.querySelector('.line-total').textContent = `${lineTotal} ₽`;
            } else {
                row = document.createElement('tr');
                row.dataset.id = pid;
                row.innerHTML = `<td><div class="cart-item-info">${item.image ? `<img src="${item.image}" class="cart-item-img">` : `<div class="cart-item-img placeholder-cart">🍔</div>`}<span class="cart-item-name">${item.name}</span></div></td><td class="price-col">${Math.round(parseFloat(item.price))} ₽</td><td><div class="qty-control"><button class="qty-btn" data-action="remove" data-id="${pid}">−</button><span class="qty">${item.quantity}</span><button class="qty-btn" data-action="add" data-id="${pid}">+</button></div></td><td class="line-total">${lineTotal} ₽</td><td><button class="remove-btn" data-id="${pid}">✕</button></td>`;
                document.querySelector('.cart-table tbody')?.appendChild(row);
            }
        }
    }

    // ========================================
    // 🔹 Обновление виджетов в меню (без изменений)
    // ========================================
    function renderMenuWidgets(cart, changedId = null) {
        for (const [pid, item] of Object.entries(cart)) {
            const control = document.querySelector(`.menu-qty-control[data-id="${pid}"]`);
            const addBtn = document.querySelector(`.card-footer .add-to-cart-btn[data-id="${pid}"]`);
            const qty = parseInt(item.quantity) || 0;

            if (qty > 0) {
                if (addBtn && !control) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'menu-qty-control';
                    wrapper.dataset.id = pid;
                    wrapper.innerHTML = `<button class="menu-qty-btn" data-action="remove">−</button><span class="menu-qty-val">${qty}</span><button class="menu-qty-btn" data-action="add">+</button>`;
                    addBtn.replaceWith(wrapper);
                } else if (control) {
                    const valEl = control.querySelector('.menu-qty-val');
                    if (valEl) {
                        valEl.textContent = qty;
                        if (pid === changedId) {
                            valEl.style.transform = 'scale(1.2)';
                            valEl.style.transition = 'transform 0.15s ease';
                            setTimeout(() => {
                                valEl.style.transform = 'scale(1)';
                            }, 150);
                        }
                    }
                }
            } else {
                if (control) {
                    const btn = document.createElement('button');
                    btn.className = 'add-to-cart-btn';
                    btn.dataset.id = pid;
                    btn.textContent = 'В корзину';
                    control.replaceWith(btn);
                }
            }
        }

        document.querySelectorAll('.menu-qty-control').forEach(control => {
            const pid = control?.dataset?.id;
            if (!pid || !cart[pid] || parseInt(cart[pid]?.quantity) === 0) {
                const footer = control?.closest('.menu-card')?.querySelector('.card-footer');
                if (footer) {
                    const btn = document.createElement('button');
                    btn.className = 'add-to-cart-btn';
                    btn.dataset.id = pid;
                    btn.textContent = 'В корзину';
                    control.replaceWith(btn);
                }
            }
        });
    }

    // ========================================
    // 🔹 Фильтрация и поиск (без изменений)
    // ========================================
    async function fetchAndRenderMenu(url) {
        const grid = document.querySelector('.menu-grid');
        if (!grid) return;
        const scrollY = window.scrollY;
        grid.style.pointerEvents = 'none';
        grid.style.opacity = '0.7';
        try {
            const res = await fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
            const html = await res.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            const newGrid = doc.querySelector('.menu-grid');
            if (newGrid) {
                grid.innerHTML = newGrid.innerHTML;
                void grid.offsetHeight;
                grid.style.opacity = '1';
                renderMenuWidgets(currentCart);
            }
        } catch (err) {
            console.error('❌ Ошибка фильтрации:', err);
        } finally {
            window.scrollTo({top: scrollY, behavior: 'auto'});
            grid.style.pointerEvents = '';
            grid.style.opacity = '';
        }
    }

    function initCategoryFilter() {
        document.querySelectorAll('.filter-btn').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                link.classList.add('active');
                await fetchAndRenderMenu(link.href);
                history.pushState({}, '', link.href);
            });
        });
    }

    function initSearch() {
        const input = document.getElementById('search-input');
        if (!input) return;
        const handleInput = debounce(async (e) => {
            const query = e.target.value.trim();
            const activeFilter = document.querySelector('.filter-btn.active');
            const catHref = activeFilter ? activeFilter.getAttribute('href') : '';
            const catMatch = catHref?.match(/category=([^&]+)/);
            const category = catMatch ? catMatch[1] : '';
            let url = '/';
            const params = new URLSearchParams();
            if (query) params.set('search', query);
            if (category) params.set('category', category);
            if (params.toString()) url += '?' + params.toString();
            if (!query) {
                const resetUrl = category ? `/?category=${category}` : '/';
                await fetchAndRenderMenu(resetUrl);
                history.replaceState({}, '', resetUrl);
            } else {
                await fetchAndRenderMenu(url);
                history.replaceState({}, '', url);
            }
        }, 400);
        input.addEventListener('input', handleInput);
    }

    // Запуск
    initCategoryFilter();
    initSearch();
    window.addEventListener('popstate', () => location.reload());

}); // ← Закрывающая скобка DOMContentLoaded