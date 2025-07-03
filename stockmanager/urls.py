from django.urls import path
from .views import Custom_Logout, register
from . import views

urlpatterns = [
    path('', views.stock_list, name='home'),
    path('add/', views.add_stock, name='add_stock'),
    path('register/', register, name='register'),
    path('accounts/logout/', Custom_Logout.as_view(), name='logout'),
    path('buy/', views.buy_stock, name='buy_stock'),
    path('sell/', views.sell_stock, name='sell_stock'),
    path('portfolio/', views.my_portfolio, name='my_portfolio'),
    path('delete-stock/', views.delete_stock_page, name='delete_stock_page'),
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
    path('api/prices/', views.stock_prices_api, name='stock_prices_api'),
    path('realtime-graph/', views.stock_graph, name='stock_graph'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transactions/clear/', views.clear_transaction_history, name='clear_transaction_history'),

]
