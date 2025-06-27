from django.contrib import admin
from .models import Stock, UserHolding, Transaction, UserProfile  

admin.site.register(Stock)
admin.site.register(UserHolding)
admin.site.register(Transaction)
admin.site.register(UserProfile)
