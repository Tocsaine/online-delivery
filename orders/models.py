from django.db import models
from catalog.models import MenuItem
from django.db.models import Q, CheckConstraint
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField

class Order(models.Model):
    user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('preparing', 'Готовится'),
        ('packing', 'Упаковываем'),
        ('delivering', 'В доставке'),
        ('awaiting_confirmation', 'Ожидает подтверждения'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    customer_name = models.CharField("Имя", max_length=100)
    phone = EncryptedCharField("Телефон", max_length=20)
    address = EncryptedTextField("Адрес доставки")
    total = models.DecimalField("Итого", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=25, choices=STATUS_CHOICES, default='new')
    courier_delivered_at = models.DateTimeField("Курьер доставил", null=True, blank=True)
    customer_confirmed_at = models.DateTimeField("Клиент подтвердил", null=True, blank=True)

    courier = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courier_order',
        verbose_name="Курьер"
    )

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
        constraints = [
            CheckConstraint(condition=Q(total__gte=0), name='order_total_non_negative'),
            CheckConstraint(condition=Q(status__in=['new', 'preparing', 'packing', 'delivering', 'awaiting_confirmation', 'completed', 'cancelled']),
                            name='order_status_valid_choice'),
        ]

        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_order_user_created'),
            models.Index(fields=['status', 'created_at'], name='idx_order_status_created'),
            models.Index(fields=['phone'], name='idx_order_phone'),
        ]

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
        constraints = [
            CheckConstraint(condition=Q(price__gte=0), name='orderitem_price_non_negative'),
            CheckConstraint(condition=Q(quantity__gte=1), name='orderitem_quantity_min_1'),
        ]

        indexes = [
            models.Index(fields=['order'], name='idx_orderitem_order'),
            models.Index(fields=['order', 'price'], name='idx_orderitem_order_price'),
        ]
