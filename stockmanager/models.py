from django.db import models
from django.contrib.auth.models import User

class StockItem(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, default='BTC')
    price_usd = models.FloatField(default=0.0)
    is_active =  models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class UserHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)

    def total_value(self):
        return self.quantity * self.stock.price_usd
