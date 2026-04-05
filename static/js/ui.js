document.addEventListener('DOMContentLoaded', () => {
    // 1. Кнопка "Наверх"
    const scrollBtn = document.getElementById('scroll-to-top');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollBtn.style.display = 'flex';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // 2. Скрытие шапки при скролле вниз и показ при скролле вверх
    let lastScrollTop = 0;
    const header = document.getElementById('header');
    window.addEventListener('scroll', () => {
        let scrollTop = window.scrollY;
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    });

    // 3. Анимация кнопки "В корзину" при клике
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.add-to-cart-btn');
        if (btn) {
            // Эффект нажатия
            btn.innerHTML = '✅ Добавлено';
            btn.style.background = '#27AE60';
            setTimeout(() => {
                btn.innerHTML = 'В корзину';
                btn.style.background = ''; // Возврат к стилю из CSS
            }, 1000);
        }
    });
});