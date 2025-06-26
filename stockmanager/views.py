from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import StockItemForm
from .models import StockItem, UserHolding
from .utils import fetch_crypto_prices


def stock_list(request):
    data = fetch_crypto_prices()
    for item in data:
        if isinstance(item, dict) and "symbol" in item:
            obj, created = StockItem.objects.get_or_create(symbol=item["symbol"])
            if obj.is_active:  # Only update if not manually excluded
                obj.name = item.get("name", "")
                obj.price_usd = item.get("current_price", 0.0)
                obj.save()

    items = StockItem.objects.filter(is_active=True).exclude(price_usd=0.0).order_by('-price_usd')
    return render(request, 'stockmanager/stock_list.html', {"items": items})


@login_required
def buy_stock(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    print(f'Buying: {item.name}')
    holding, _ = UserHolding.objects.get_or_create(user=request.user, stock=item)
    holding.quantity += 1
    holding.save()
    return redirect('home')


@login_required
def sell_stock(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    try:
        holding = UserHolding.objects.get(user=request.user, stock=item)
        if holding.quantity > 0:
            holding.quantity -= 1
            holding.save()
            messages.success(request, f"Sold 1 unit of {item.name}. Remaining: {holding.quantity}")
            if holding.quantity == 0:
                holding.delete()
                messages.info(request, f"You no longer hold any {item.name}, so it's removed from your portfolio.")
        else:
            messages.warning(request, f"You don't hold any {item.name} to sell.")
    except UserHolding.DoesNotExist:
        messages.error(request, f"You don't own any {item.name} to sell.")

    return redirect('home')


@login_required
def delete_stock_page(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        if stock_id:
            stock = get_object_or_404(StockItem, pk=stock_id)
            stock.delete()
            return redirect('delete_stock_page')

    items = StockItem.objects.all()
    return render(request, 'stockmanager/delete_stock_page.html', {'items': items})

def add_stock(request):
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StockItemForm()
    return render(request, 'stockmanager/add_stock.html', {'form': form})

@staff_member_required
def delete_stock(request, pk):
    stock = get_object_or_404(StockItem, pk=pk)
    stock.delete()
    return redirect('home')