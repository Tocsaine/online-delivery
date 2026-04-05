from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile  # ← Импортируем профиль напрямую!

class CustomRegistrationForm(UserCreationForm):
    phone = forms.CharField(label="Телефон", max_length=20, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Обновляем телефон в связанном профиле
            # Сигнал post_save уже создал пустой профиль при сохранении пользователя
            Profile.objects.filter(user=user).update(phone=self.cleaned_data["phone"])
        return user