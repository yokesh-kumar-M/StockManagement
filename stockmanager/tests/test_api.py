"""Integration tests for the REST API."""
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from stockmanager.models import Transaction, UserHolding, UserProfile


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    u = User.objects.create_user(username="apiuser", password="pass12345", email="api@test.com")
    UserProfile.objects.filter(user=u).update(balance=Decimal("100000.00"))
    return u


@pytest.fixture
def auth_client(client, user):
    resp = client.post("/api/v1/auth/login/", {"username": "apiuser", "password": "pass12345"})
    assert resp.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return client


# ─── Auth ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register/", {
            "username": "newuser", "email": "new@example.com",
            "password": "strongpass99", "password2": "strongpass99",
        })
        assert resp.status_code == 201
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_register_password_mismatch(self, client):
        resp = client.post("/api/v1/auth/register/", {
            "username": "baduser", "email": "bad@example.com",
            "password": "pass1234", "password2": "nomatch",
        })
        assert resp.status_code == 400

    def test_register_duplicate_email(self, client, user):
        resp = client.post("/api/v1/auth/register/", {
            "username": "other", "email": "api@test.com",
            "password": "pass1234", "password2": "pass1234",
        })
        assert resp.status_code == 400

    def test_register_weak_password(self, client):
        resp = client.post("/api/v1/auth/register/", {
            "username": "weakpass", "email": "w@test.com",
            "password": "1234", "password2": "1234",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, user):
        resp = client.post("/api/v1/auth/login/", {"username": "apiuser", "password": "pass12345"})
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_login_wrong_password(self, client, user):
        resp = client.post("/api/v1/auth/login/", {"username": "apiuser", "password": "wrong"})
        assert resp.status_code == 401


# ─── Profile ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProfile:
    def test_profile_requires_auth(self, client):
        resp = client.get("/api/v1/profile/")
        assert resp.status_code == 401

    def test_profile_returns_balance(self, auth_client, user):
        resp = auth_client.get("/api/v1/profile/")
        assert resp.status_code == 200
        assert "balance" in resp.data
        assert "username" in resp.data


# ─── Stocks ───────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStockList:
    @patch("stockmanager.api.views.fetch_live_price")
    def test_stock_list_public(self, mock_price, client):
        mock_price.return_value = {
            "symbol": "TCS.NS", "name": "TCS", "price_inr": 3500.0, "change_percent": 1.2,
        }
        resp = client.get("/api/v1/stocks/")
        assert resp.status_code == 200
        assert "stocks" in resp.data


# ─── Portfolio ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPortfolio:
    def test_portfolio_empty_for_new_user(self, auth_client):
        resp = auth_client.get("/api/v1/portfolio/")
        assert resp.status_code == 200
        assert resp.data["holdings"] == []
        assert "summary" in resp.data

    def test_portfolio_requires_auth(self, client):
        resp = client.get("/api/v1/portfolio/")
        assert resp.status_code == 401


# ─── Trading ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTrade:
    @patch("stockmanager.api.views.fetch_live_price")
    def test_buy_stock(self, mock_price, auth_client, user):
        mock_price.return_value = {
            "symbol": "TCS.NS", "name": "TCS", "price_inr": 100.0, "change_percent": 0,
        }
        resp = auth_client.post("/api/v1/trade/", {"symbol": "TCS.NS", "quantity": 1, "action": "BUY"})
        assert resp.status_code == 200
        assert UserHolding.objects.filter(user=user, symbol="TCS.NS").exists()

    @patch("stockmanager.api.views.fetch_live_price")
    def test_sell_without_holding_fails(self, mock_price, auth_client, user):
        mock_price.return_value = {
            "symbol": "TCS.NS", "name": "TCS", "price_inr": 100.0, "change_percent": 0,
        }
        resp = auth_client.post("/api/v1/trade/", {"symbol": "TCS.NS", "quantity": 1, "action": "SELL"})
        assert resp.status_code == 400

    @patch("stockmanager.api.views.fetch_live_price")
    def test_buy_insufficient_balance(self, mock_price, auth_client, user):
        mock_price.return_value = {
            "symbol": "TCS.NS", "name": "TCS", "price_inr": 9_999_999.0, "change_percent": 0,
        }
        resp = auth_client.post("/api/v1/trade/", {"symbol": "TCS.NS", "quantity": 1, "action": "BUY"})
        assert resp.status_code == 400


# ─── Transactions ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTransactions:
    def test_empty_transactions(self, auth_client):
        resp = auth_client.get("/api/v1/transactions/")
        assert resp.status_code == 200

    def test_clear_transactions(self, auth_client, user):
        Transaction.objects.create(
            user=user, symbol="TCS.NS", stock_name="TCS",
            action="BUY", quantity=1, price=Decimal("100"),
        )
        resp = auth_client.delete("/api/v1/transactions/clear/")
        assert resp.status_code == 200
        assert Transaction.objects.filter(user=user).count() == 0


# ─── Health ───────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/api/v1/health/")
        assert resp.status_code == 200
        assert resp.data["status"] == "ok"
