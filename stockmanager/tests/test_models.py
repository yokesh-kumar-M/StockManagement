"""Unit tests for stockmanager models."""
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from stockmanager.models import Stock, Transaction, UserHolding, UserProfile


@pytest.mark.django_db
class TestUserProfile:
    def test_profile_auto_created_on_user_creation(self):
        user = User.objects.create_user(username="test_profile", password="pass12345")
        assert UserProfile.objects.filter(user=user).exists()

    def test_default_balance_is_10000(self):
        user = User.objects.create_user(username="test_balance", password="pass12345")
        assert user.profile.balance == Decimal("10000.00")

    def test_str_representation(self):
        user = User.objects.create_user(username="test_str", password="pass12345")
        assert "test_str" in str(user.profile)


@pytest.mark.django_db
class TestStock:
    def test_stock_creation(self):
        stock = Stock.objects.create(name="TCS", symbol="TCS.NS", price_inr=Decimal("3500.00"))
        assert str(stock) == "TCS (TCS.NS)"

    def test_symbol_unique_constraint(self):
        Stock.objects.create(name="TCS", symbol="TCS.NS", price_inr=Decimal("3500.00"))
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Stock.objects.create(name="TCS Duplicate", symbol="TCS.NS", price_inr=Decimal("3600.00"))


@pytest.mark.django_db
class TestTransaction:
    def setup_method(self):
        self.user = User.objects.create_user(username="trader", password="pass12345")

    def test_total_value_computed_on_save(self):
        t = Transaction.objects.create(
            user=self.user,
            symbol="TCS.NS",
            stock_name="Tata Consultancy Services",
            action=Transaction.BUY,
            quantity=2,
            price=Decimal("3500.00"),
        )
        assert t.total_value == Decimal("7000.00")

    def test_action_choices_are_valid(self):
        assert Transaction.BUY == "BUY"
        assert Transaction.SELL == "SELL"

    def test_str_representation(self):
        t = Transaction.objects.create(
            user=self.user,
            symbol="INFY.NS",
            stock_name="Infosys",
            action=Transaction.SELL,
            quantity=1,
            price=Decimal("1500.00"),
        )
        assert "trader" in str(t)
        assert "SELL" in str(t)


@pytest.mark.django_db
class TestUserHolding:
    def test_unique_together_constraint(self):
        user = User.objects.create_user(username="holder", password="pass12345")
        UserHolding.objects.create(user=user, symbol="TCS.NS", quantity=5)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            UserHolding.objects.create(user=user, symbol="TCS.NS", quantity=3)
