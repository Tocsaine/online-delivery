from django.db import models
from django.db.models import Q, CheckConstraint


class Category(models.Model):
    name = models.CharField("Название категории", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True)
    is_active = models.BooleanField("Активна", default=True)

    order = models.PositiveIntegerField("Порядок", default=0, help_text="Меньшее число = выше в списке")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

        constraints = [
            CheckConstraint(condition=Q(order__gte=0), name='category_order_non_negative'),
        ]

        indexes = [
            models.Index(fields=['is_active', 'order'], name='idx_category_active_order'),
        ]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items", verbose_name="Категория"
    )
    name = models.CharField("Название", max_length=150)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    image = models.ImageField("Изображение", upload_to="menu/", blank=True, null=True)
    is_available = models.BooleanField("В наличии", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    full_description = models.TextField("Полное описание", blank=True, default="")
    weight = models.IntegerField("Вес (грамм)", default=0, blank=True)
    calories = models.IntegerField("Калории (ккал)", default=0, blank=True)
    proteins = models.DecimalField("Белки (г)", max_digits=5, decimal_places=1, default=0, blank=True)
    fats = models.DecimalField("Жиры (г)", max_digits=5, decimal_places=1, default=0, blank=True)
    carbs = models.DecimalField("Углеводы (г)", max_digits=5, decimal_places=1, default=0, blank=True)

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ["category", "name"]

        constraints = [
            CheckConstraint(condition=Q(price__gte=0), name='menuitem_price_non_negative'),
            CheckConstraint(condition=Q(weight__gte=0), name='menuitem_weight_non_negative'),
            CheckConstraint(condition=Q(calories__gte=0), name='menuitem_calories_non_negative'),
            CheckConstraint(condition=Q(proteins__gte=0), name='menuitem_proteins_non_negative'),
            CheckConstraint(condition=Q(fats__gte=0), name='menuitem_fats_non_negative'),
            CheckConstraint(condition=Q(carbs__gte=0), name='menuitem_carbs_non_negative'),
        ]

        indexes = [
            models.Index(fields=['category', 'is_available'], name='idx_menuitem_cat_available'),

            models.Index(fields=['is_available', 'price'], name='idx_menuitem_available_price'),

            models.Index(fields=['name'], name='idx_menuitem_name'),

            models.Index(fields=['category', 'is_available', '-created_at'], name='idx_menuitem_cat_avail_created'),
        ]

    def __str__(self):
        return self.name
