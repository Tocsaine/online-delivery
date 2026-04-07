from django.db import models


class Category(models.Model):
    name = models.CharField("Название категории", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True)
    is_active = models.BooleanField("Активна", default=True)

    order = models.PositiveIntegerField("Порядок", default=0, help_text="Меньшее число = выше в списке")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

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

    def __str__(self):
        return self.name
