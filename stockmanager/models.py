from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Stock model (already updated earlier)
class Stock(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    price_inr = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    isin = models.CharField(max_length=12, blank=True, null=True)
    sector = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

# Extend user with balance
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=10000.0)  # Default balance

    def __str__(self):
        return f"{self.user.username} Profile"

# Track holdings
class UserHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)

    def total_value(self):
        return self.quantity * self.stock.price_inr

# Track every buy/sell
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    action = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    quantity = models.IntegerField()
    price = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} {self.action} {self.quantity} of {self.stock.symbol} at ₹{self.price}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)