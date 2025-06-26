from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='home'),
    path('add/', views.add_stock, name='add_stock'),
    path('buy/<int:pk>/', views.buy_stock, name='buy_stock'),
    path('sell/<int:pk>/', views.sell_stock, name='sell_stock'),
    path('delete-stock/', views.delete_stock_page, name='delete_stock_page'),

]