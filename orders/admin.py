from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'get_total')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer_name', 'phone', 'address', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone', 'address')
    inlines = [OrderItemInline]
    readonly_fields = ('total', 'created_at', 'updated_at')
    actions = ['mark_preparing', 'mark_delivering', 'mark_completed']

    def mark_preparing(self, request, queryset):
        queryset.update(status='preparing')
    def mark_delivering(self, request, queryset):
        queryset.update(status='delivering')
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    mark_preparing.short_description = "🔥 Готовится"
    mark_delivering.short_description = "🚗 В доставке"
    mark_completed.short_description = "✅ Выполнен"