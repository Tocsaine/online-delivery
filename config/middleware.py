# config/middleware.py
from django.shortcuts import redirect
from django.contrib import messages


class CourierRestrictionMiddleware:
    """
    Запрещает курьерам доступ к страницам клиента (меню, корзина, профиль).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Проверяем, авторизован ли пользователь
        if request.user.is_authenticated:
            # 2. Проверяем роль (на случай, если профиля еще нет, используем hasattr)
            if hasattr(request.user, 'profile') and request.user.profile.role == 'courier':
                path = request.path

                # 3. СПИСОК РАЗРЕШЕННЫХ ПУТЕЙ ДЛЯ КУРЬЕРА
                # Если URL начинается с этого — доступ разрешен.
                allowed_prefixes = [
                    '/orders/courier',  # Панель курьера
                    '/admin',  # Админка Django
                    '/accounts/logout',  # Возможность выйти из аккаунта
                    '/static',  # CSS/JS файлы
                    '/media',  # Картинки
                    '/favicon.ico',  # Иконка сайта
                ]

                # Проверяем, разрешен ли текущий путь
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)

                # Если путь НЕ в списке разрешенных — делаем редирект
                if not is_allowed:
                    # (Опционально) Можно показать сообщение об ошибке
                    # messages.warning(request, "Курьеры не могут просматривать меню.")

                    # Перенаправляем в панель курьера
                    return redirect('orders:courier_dashboard')

        # 4. Если пользователь не курьер ИЛИ путь разрешен — идем дальше
        response = self.get_response(request)
        return response