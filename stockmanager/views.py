from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StockItem, UserHolding
from .utils import fetch_crypto_prices


from django.shortcuts import render
from .models import StockItem
from .utils import fetch_crypto_prices

def stock_list(request):
    data = fetch_crypto_prices()

    for item in data:
        StockItem.objects.update_or_create(
            symbol=item["symbol"],
            defaults={
                "name": item["name"],
                "price_usd": item["current_price"]
            }
        )

    # Get only meaningful items to display
    items = StockItem.objects.exclude(price_usd=0.0).order_by('-price_usd')
    return render(request, 'stockmanager/stock_list.html', {"items": items})



def add_stock(request):
    if request.method == 'POST':
        form = StockItem(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StockItem()
    return render(request, 'stockmanager/add_stock.html', {'form': form})

@login_required
def delete_stock(request, stock_id):
    stock = get_object_or_404(StockItem, id=stock_id)
    stock.delete()
    return redirect('stock_list')

@login_required
def buy_stock(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    holding, _ = UserHolding.objects.get_or_create(user=request.user, stock=item)
    holding.quantity += 1  # Simulated purchase (can replace with form input)
    holding.save()
    return redirect('home')

