from django.urls import path
from . import views

app_name = 'catalog'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('api/item/<int:pk>/', views.menu_item_detail, name='item_detail'),
]
