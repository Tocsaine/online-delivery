from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = EncryptedCharField("Телефон", max_length=20, blank=True)

    # В будущем сюда добавим сохранённые адреса, предпочтения и т.д.

    def __str__(self):
        return f"Профиль {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField("Название (напр. Дом)", max_length=50, default="Мой адрес")
    text = EncryptedTextField("Адрес")
    is_default = models.BooleanField("По умолчанию", default=False)

    def __str__(self):
        return f"{self.label}: {self.text[:30]}"

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

        indexes = [

            models.Index(fields=['user', 'is_default'], name='idx_address_user_default'),

            models.Index(fields=['text'], name='idx_address_text'),
        ]
