from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Stock, UserProfile

'''
@receiver(post_migrate)
def create_default_stocks(sender, **kwargs):
    default_stocks = [
        {"name": "Tata Consultancy Services", "symbol": "TCS", "price_inr": 3750},
        {"name": "Reliance Industries", "symbol": "RELIANCE", "price_inr": 2900},
        {"name": "Infosys", "symbol": "INFY", "price_inr": 1450},
        {"name": "Wipro", "symbol": "WIPRO", "price_inr": 510},
        {"name": "HDFC Bank", "symbol": "HDFC", "price_inr": 1600},
    ]

    for stock in default_stocks:
        Stock.objects.get_or_create(symbol=stock["symbol"], defaults=stock)
'''
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)