from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='home'),
    path('add/', views.add_stock, name='add_stock'),
    path("register/", views.register_view, name="register"),
    path('buy/<int:pk>/', views.buy_stock, name='buy_stock'),
    path('sell/<int:pk>/', views.sell_stock, name='sell_stock'),
    path('portfolio/', views.my_portfolio, name='my_portfolio'),
    path('delete-stock/', views.delete_stock_page, name='delete_stock_page'),
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('api/prices/', views.stock_prices_api, name='stock_prices_api'),
    path('transactions/', views.transaction_history, name='transaction_history'),
]
