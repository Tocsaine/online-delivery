from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile  # Убедись, что импорт есть


class CustomRegistrationForm(UserCreationForm):
    phone = forms.CharField(label="Телефон", max_length=20, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        phone = self.cleaned_data.get("phone")

        if commit:
            user.save()
            # Гарантированно создаём или получаем профиль и сохраняем телефон
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()

        return user
