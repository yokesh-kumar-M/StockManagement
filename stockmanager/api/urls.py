from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

urlpatterns = [
    # Health
    path("health/", views.health_check, name="api_health"),
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="api_register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="api_verify"),
    # Profile
    path("profile/", views.ProfileView.as_view(), name="api_profile"),
    # Stocks
    path("stocks/", views.StockListView.as_view(), name="api_stocks"),
    path("stocks/chart/", views.StockChartView.as_view(), name="api_chart"),
    # Trading
    path("trade/", views.TradeView.as_view(), name="api_trade"),
    path("portfolio/", views.PortfolioView.as_view(), name="api_portfolio"),
    # Transactions
    path("transactions/", views.TransactionListView.as_view(), name="api_transactions"),
    path(
        "transactions/clear/",
        views.TransactionClearView.as_view(),
        name="api_transactions_clear",
    ),
    # Admin
    path("admin/deposit/", views.DepositView.as_view(), name="api_deposit"),
    path("withdraw/", views.WithdrawView.as_view(), name="api_withdraw"),
]
