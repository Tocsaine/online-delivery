from django.db import models
from catalog.models import MenuItem


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('preparing', 'Готовится'),
        ('delivering', 'В доставке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    customer_name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    address = models.TextField("Адрес доставки")
    total = models.DecimalField("Итого", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.pk} от {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField("Количество")
    price = models.DecimalField("Цена за шт.", max_digits=8, decimal_places=2)

    def get_total(self):
        """Безопасный расчёт: обрабатываем None и строки"""
        qty = self.quantity or 0
        price = self.price
        if price is None:
            return 0
        if isinstance(price, str):
            from decimal import Decimal
            price = Decimal(price)
        return qty * price

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
