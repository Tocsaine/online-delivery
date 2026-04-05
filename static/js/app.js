// static/js/app.js
document.addEventListener('DOMContentLoaded', () => {
  console.log('🟢 app.js инициализирован');

  // 🔹 Безопасное получение CSRF-токена (стандарт Django)
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

  // 🔹 Единый слушатель на ВСЮ страницу (работает даже после подмены DOM)
  document.addEventListener('click', (e) => {
    // 1. Кнопка "В корзину"
    const addBtn = e.target.closest('.add-to-cart-btn');
    if (addBtn) {
      e.preventDefault();
      updateCart('add', addBtn.dataset.id);
      return;
    }

    // 2. Кнопки +/- в корзине
    const qtyBtn = e.target.closest('.qty-btn');
    if (qtyBtn) {
      e.preventDefault();
      updateCart(qtyBtn.dataset.action, qtyBtn.dataset.id);
      return;
    }

    // 3. Крестик удаления позиции
    const removeBtn = e.target.closest('.remove-btn');
    if (removeBtn) {
      e.preventDefault();
      const id = removeBtn.dataset.id;

      // 🔍 Отладка: проверяем, что id существует
      console.log('🗑️ Delete clicked:', {
        id: id,
        type: typeof id,
        html: removeBtn.outerHTML
      });

      if (!id) {
        console.error('🔴 Ошибка: data-id атрибут пуст или отсутствует!');
        return;
      }

      updateCart('delete', id);
      return;
    }
  });

  // 🔹 Отправка запроса на сервер
  function updateCart(action, id) {
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
      console.error('🔴 CSRF-токен отсутствует');
      return;
    }

    fetch('/cart/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ action, id })
    })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      if (data.success) {
        const countEl = document.getElementById('cart-count');
        if (countEl) countEl.textContent = data.count;

        // Перезагружаем страницу для синхронизации состояния корзины
        location.reload();
      } else {
        console.error('🔴 Ответ сервера:', data);
      }
    })
    .catch(err => console.error('🔴 Ошибка сети:', err));
  }
});