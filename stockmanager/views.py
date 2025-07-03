from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib import messages
from .forms import StockForm, RegisterForm
from .models import Stock, UserHolding, Transaction, UserProfile

import yfinance as yf
import matplotlib.pyplot as plt
import io
import urllib, base64
import random

YAHOO_STOCK_SYMBOLS = [
    {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
    {'symbol': 'INFY.NS', 'name': 'Infosys'},
    {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
    {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
    {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
    {'symbol': 'ITC.NS', 'name': 'ITC Ltd'},
    {'symbol': 'WIPRO.NS', 'name': 'Wipro'},
    {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies'},
    {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
    {'symbol': 'LT.NS', 'name': 'Larsen & Toubro'},
]

def stock_list(request):
    symbols = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'ITC.NS',
    'WIPRO.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'HCLTECH.NS']
    stocks = []

    for symbol in symbols:
        cached = cache.get(symbol)

        if not cached:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get("currentPrice", 0)

                cached = {
                    "symbol": symbol,
                    "name": info.get("shortName", symbol),
                    "price_inr": round(price, 2) if price else 0
                }

                # Cache only valid prices
                if cached["price_inr"] > 0:
                    cache.set(symbol, cached, timeout=300)  # 5 min cache
            except Exception as e:
                cached = {"symbol": symbol, "name": symbol, "price_inr": 0}

        stocks.append(cached)

    holdings = {}
    balance = None

    if request.user.is_authenticated:
        user_holdings = UserHolding.objects.filter(user=request.user)
        holdings = {h.symbol.upper(): h.quantity for h in user_holdings}

        try:
            balance = request.user.userprofile.balance
        except:
            balance = 0  

    return render(request, 'stockmanager/stock_list.html', {
        "items": stocks,
        "user_balance": balance,
        "holdings": holdings
    })

@login_required
def buy_stock(request):
    symbol = request.GET.get('symbol')
    stock = yf.Ticker(symbol)
    info = stock.info
    price = info.get('currentPrice')

    if not price:
        messages.error(request, "Stock data unavailable.")
        return redirect('home')

    profile = request.user.userprofile
    if profile.balance >= price:
        holding, _ = UserHolding.objects.get_or_create(user=request.user, symbol=symbol)
        holding.quantity += 1
        holding.save()
        profile.balance -= price
        profile.save()

        Transaction.objects.create(user=request.user, stock_name=symbol, action='BUY', quantity=1, price=price)
        messages.success(request, f"Bought 1 share of {symbol} at ₹{price}")
    else:
        messages.error(request, "Insufficient balance.")

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
def sell_stock(request):
    symbol = request.GET.get('symbol')
    stock = yf.Ticker(symbol)
    info = stock.info
    price = info.get('currentPrice')

    holding = UserHolding.objects.filter(user=request.user, symbol=symbol).first()
    if holding and holding.quantity > 0:
        holding.quantity -= 1
        holding.save()
        if holding.quantity == 0:
            holding.delete()

        profile = request.user.userprofile
        profile.balance += price
        profile.save()

        Transaction.objects.create(user=request.user, stock_name=symbol, action='SELL', quantity=1, price=price)
        messages.success(request, f"Sold 1 share of {symbol} at ₹{price}")
    else:
        messages.error(request, "You don't own this stock.")

    return redirect('home')

def stock_graph(request):
    symbol = request.GET.get('symbol', 'AAPL')  # Default: Apple
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d", interval="1h")

    if hist.empty:
        return render(request, 'stockmanager/stock_chart.html', {
            'symbol': symbol,
            'chart': None,
            'error': "Stock symbol not found or data unavailable."
        })

    latest_price = round(hist['Close'].iloc[-1], 2)
    min_price = round(hist['Close'].min(), 2)
    max_price = round(hist['Close'].max(), 2)
    avg_price = round(hist['Close'].mean(), 2)

    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(hist.index, hist['Close'], marker='o', color='cyan')
    plt.title(f"{symbol.upper()} - Last 5 Days (Hourly)")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_uri = 'data:image/png;base64,' + urllib.parse.quote(base64.b64encode(buf.read()))
    plt.close()

    return render(request, 'stockmanager/stock_chart.html', {
        'symbol': symbol,
        'chart': image_uri,
        'latest_price': latest_price,
        'min_price': min_price,
        'max_price': max_price,
        'avg_price': avg_price,
        'error': None
    })

@login_required
def my_portfolio(request):
    holdings = UserHolding.objects.filter(user=request.user)
    total_value = sum(h.quantity * h.stock.price_inr for h in holdings)

    for holding in holdings:
        holding.total_value = holding.quantity * holding.stock.price_inr

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
def clear_transaction_history(request):
    Transaction.objects.filter(user=request.user).delete()
    messages.success(request, "Transaction history cleared.")
    return redirect('transaction_history')

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

@login_required
def withdraw_money(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            if amount <= 0:
                messages.error(request, "Enter a positive amount.")
            elif amount > profile.balance:
                messages.error(request, "Insufficient balance.")
            else:
                profile.balance -= amount
                profile.save()
                messages.success(request, f"₹{amount} withdrawn successfully.")
                return redirect('home')
        except ValueError:
            messages.error(request, "Invalid amount entered.")

    return render(request, 'stockmanager/withdraw_money.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return login(request)  # Optional: log them in after registering
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class Custom_Logout(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)