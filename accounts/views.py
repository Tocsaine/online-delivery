from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomRegistrationForm


def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 🔥 ЖЕСТКОЕ СОХРАНЕНИЕ ТЕЛЕФОНА В ПРОФИЛЬ
            # Обращаемся к связанному профилю и обновляем поле
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.save()

            login(request, user)
            messages.success(request, "Аккаунт успешно создан!")
            return redirect('catalog:menu')
    else:
        form = CustomRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # ← Получаем пользователя из формы
            if user:
                login(request, user)  # ← Авторизуем (функция ничего не возвращает)
                username = form.cleaned_data.get('username')
                messages.info(request, f"Добро пожаловать, {username}!")
                # Редирект: приоритет — ?next=, иначе — главная меню
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('catalog:menu')  # ← Имя URL, как в catalog/urls.py
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect('catalog:menu')


@login_required
def account(request):
    profile = request.user.profile
    orders = request.user.orders.all().order_by('-created_at')[:10]

    # Обработка обновления профиля
    if request.method == 'POST':
        user = request.user

        # 1. Сохраняем Email (это поле встроенной модели User)
        new_email = request.POST.get('email', '').strip()
        if new_email:
            user.email = new_email
            user.save()

        # 2. Сохраняем Телефон (это поле нашей модели Profile)
        new_phone = request.POST.get('phone', '').strip()
        if new_phone:
            profile.phone = new_phone
            profile.save()

        messages.success(request, "Данные профиля обновлены!")
        return redirect('accounts:account')  # Перезагружаем страницу, чтобы увидеть новые данные

    return render(request, 'accounts/account.html', {'orders': orders, 'profile': profile})
