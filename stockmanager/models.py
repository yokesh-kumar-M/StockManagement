from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    price_inr = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    isin = models.CharField(max_length=12, blank=True, default="")
    sector = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("10000.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} — ₹{self.balance}"


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)


class UserHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="holdings")
    symbol = models.CharField(max_length=20, db_index=True)
    quantity = models.PositiveIntegerField(default=0)
    average_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "symbol")
        ordering = ["symbol"]

    def __str__(self) -> str:
        return f"{self.user.username} — {self.symbol} × {self.quantity}"


class Transaction(models.Model):
    BUY = "BUY"
    SELL = "SELL"
    ACTION_CHOICES = [(BUY, "Buy"), (SELL, "Sell")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    symbol = models.CharField(max_length=20, db_index=True)
    stock_name = models.CharField(max_length=100)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["symbol"]),
        ]

    def save(self, *args, **kwargs):
        self.total_value = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.username} {self.action} {self.quantity}× {self.symbol} @ ₹{self.price}"
