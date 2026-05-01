import os
import sys
import django

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Дальше идёт твой код...
from accounts.models import Profile, Address
from orders.models import Order
# ...
print("Шифрование существующих данных...")

# Профили
for profile in Profile.objects.all():
    if profile.phone:
        profile.save(update_fields=['phone'])
        print(f"  ✓ Profile #{profile.id}")

# Адреса
for addr in Address.objects.all():
    if addr.text:
        addr.save(update_fields=['text'])
        print(f"  ✓ Address #{addr.id}")

# Заказы
for order in Order.objects.all():
    if order.phone or order.address:
        order.save(update_fields=['phone', 'address'])
        print(f"  ✓ Order #{order.id}")

print("Готово! Все чувствительные данные зашифрованы.")