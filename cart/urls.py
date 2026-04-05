from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart_view, name='view'),
    path('update/', views.update_cart, name='update'),
]