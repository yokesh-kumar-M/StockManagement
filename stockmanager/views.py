from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from .forms import StockForm, RegisterForm
from .models import Stock, UserHolding, Transaction, UserProfile
# from .utils import fetch_stock_prices  # Optional: implement later for real data


#  Optional: Uncomment & implement if using API to update stock prices
# def stock_list(request):
#     data = fetch_stock_prices()  # e.g., [{'symbol': 'TCS', 'price': 3770.0}, ...]
#     for item in data:
#         obj, created = Stock.objects.get_or_create(symbol=item["symbol"])
#         if obj.is_active:
#             obj.name = item.get("name", obj.name)
#             obj.price_inr = item.get("price", obj.price_inr)
#             obj.save()

#     items = Stock.objects.filter(is_active=True).exclude(price_inr=0.0).order_by('-price_inr')
#     return render(request, 'stockmanager/stock_list.html', {"items": items})


#  Use this version if you're manually managing stocks (initial version)
import random

def stock_list(request):
    items = Stock.objects.filter(is_active=True)
    for stock in items:
        delta = stock.price_inr * random.uniform(-0.05, 0.05)
        stock.price_inr = max(stock.price_inr + delta, 1)
        stock.save()

    user_balance = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_balance = profile.balance

    return render(request, 'stockmanager/stock_list.html', {
        "items": items,
        "user_balance": user_balance
    })



@login_required
def buy_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    user_profile = request.user.userprofile
    price = stock.price_inr

    if user_profile.balance >= price:
        holding, _ = UserHolding.objects.get_or_create(user=request.user, stock=stock)
        holding.quantity += 1
        holding.save()
        user_profile.balance -= price
        user_profile.save()
        Transaction.objects.create(user=request.user, stock=stock, action='BUY', quantity=1, price=price)
        messages.success(request, f"Bought 1 {stock.name} at ₹{price}")
    else:
        messages.error(request, f"Insufficient balance to buy {stock.name}")

    return redirect('home')

def stock_prices_api(request):
    items = Stock.objects.filter(is_active=True)
    data = []

    for stock in items:
        delta = stock.price_inr * random.uniform(-0.05, 0.05)
        new_price = max(stock.price_inr + delta, 1)
        stock.price_inr = round(new_price, 2)
        stock.save()
        data.append({
            'id': stock.id,
            'name': stock.name,
            'symbol': stock.symbol,
            'price_inr': stock.price_inr,
        })

    return JsonResponse({'stocks': data})

@login_required
def sell_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    user_profile = request.user.userprofile
    try:
        holding = UserHolding.objects.get(user=request.user, stock=stock)
        if holding.quantity > 0:
            holding.quantity -= 1
            holding.save()

            user_profile.balance += stock.price_inr
            user_profile.save()

            Transaction.objects.create(user=request.user, stock=stock, action='SELL', quantity=1, price=stock.price_inr)

            messages.success(request, f"Sold 1 unit of {stock.name} at ₹{stock.price_inr}. New balance: ₹{user_profile.balance:.2f}")

            if holding.quantity == 0:
                holding.delete()
                messages.info(request, f"You no longer hold any {stock.name}.")
        else:
            messages.warning(request, f"You don't hold any {stock.name} to sell.")
    except UserHolding.DoesNotExist:
        messages.error(request, f"You don't own any {stock.name} to sell.")
    return redirect('home')

@login_required
def my_portfolio(request):
    holdings = UserHolding.objects.filter(user=request.user).select_related('stock')
    total_value = sum(h.quantity * h.stock.price_inr for h in holdings)

    return render(request, 'stockmanager/portfolio.html', {
        'holdings': holdings,
        'total_value': total_value,
        'balance': request.user.userprofile.balance
    })

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'stockmanager/transaction_history.html', {'transactions': transactions})

@login_required
def delete_stock_page(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        if stock_id:
            stock = get_object_or_404(Stock, pk=stock_id)
            stock.delete()
            return redirect('delete_stock_page')

    items = Stock.objects.all()
    return render(request, 'stockmanager/delete_stock_page.html', {'items': items})


def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StockForm()
    return render(request, 'stockmanager/add_stock.html', {'form': form})


@staff_member_required
def delete_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('home')

@user_passes_test(lambda u: u.is_superuser)
def deposit_money(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = float(request.POST.get('amount', 0))
        user = User.objects.get(id=user_id)
        user.userprofile.balance += amount
        user.userprofile.save()
        messages.success(request, f"₹{amount} deposited to {user.username}")
        return redirect('home')

    users = User.objects.all()
    return render(request, 'stockmanager/deposit.html', {'users': users})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})