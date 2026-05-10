from django.urls import path
from . import views, stats_views
from . import views_courier

app_name = 'orders'
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.success, name='success'),
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('courier/', views_courier.courier_dashboard, name='courier_dashboard'),
    path('courier/accept/<int:order_id>/', views_courier.accept_order, name='accept_order'),
    path('courier/complete/<int:order_id>/', views_courier.complete_delivery, name='complete_delivery'),
    path('confirm/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),
    path('stats/', stats_views.stats_dashboard, name='stats_dashboard'),
]
