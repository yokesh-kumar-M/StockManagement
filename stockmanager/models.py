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
    balance = models.FloatField(default=1000.0)  # Default balance

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

    def __str__(self):
        return f"{self.user.username} Profile"
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

# Track holdings
class UserHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)  # e.g., 'TCS.NS'
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.symbol} ({self.quantity})"

# Track every buy/sell
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=50)
    action = models.CharField(max_length=10)  # BUY/SELL
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} {self.action} {self.quantity} of {self.stock.symbol} at ₹{self.price}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)