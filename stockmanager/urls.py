from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('add/', views.add_stock, name='add_stock'),
    path('buy/<int:stock_id>/', views.buy_stock, name='buy_stock'),
    path('delete/<int:stock_id>/', views.delete_stock, name='delete_stock'),
]