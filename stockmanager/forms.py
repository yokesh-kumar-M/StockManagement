from django import forms
from .models import StockItem

class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['symbol', 'name', 'price_usd']
