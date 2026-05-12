import io
import logging
import urllib.parse
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yfinance as yf

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .forms import StockForm, RegisterForm
from .models import Stock, UserHolding, Transaction, UserProfile

logger = logging.getLogger(__name__)

TRACKED_SYMBOLS = [
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
    {"symbol": "INFY.NS", "name": "Infosys"},
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
    {"symbol": "ITC.NS", "name": "ITC Ltd"},
    {"symbol": "WIPRO.NS", "name": "Wipro"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
    {"symbol": "SBIN.NS", "name": "State Bank of India"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro"},
]


def _fetch_price(symbol: str) -> dict:
    cached = cache.get(f"price_{symbol}")
    if cached:
        return cached
    try:
        info = yf.Ticker(symbol).info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        data = {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "price_inr": round(float(price), 2) if price else 0,
        }
        if data["price_inr"] > 0:
            cache.set(f"price_{symbol}", data, timeout=300)
        return data
    except Exception as exc:
        logger.warning("Price fetch failed for %s: %s", symbol, exc)
        return {"symbol": symbol, "name": symbol, "price_inr": 0}


def stock_list(request):
    stocks = [_fetch_price(s["symbol"]) for s in TRACKED_SYMBOLS]
    stocks = [s for s in stocks if s["price_inr"] > 0]

    holdings, balance = {}, None
    if request.user.is_authenticated:
        for h in UserHolding.objects.filter(user=request.user):
            holdings[h.symbol.upper()] = h.quantity
        try:
            balance = request.user.profile.balance
        except Exception:
            balance = 0

    return render(request, "stockmanager/stock_list.html", {
        "items": stocks,
        "user_balance": balance,
        "holdings": holdings,
    })


@login_required
def buy_stock(request):
    symbol = request.GET.get("symbol", "").upper()
    data = _fetch_price(symbol)
    price = data["price_inr"]

    if not price:
        messages.error(request, "Stock data unavailable.")
        return redirect("home")

    from decimal import Decimal
    price_d = Decimal(str(price))
    profile = request.user.profile

    if profile.balance < price_d:
        messages.error(request, "Insufficient balance.")
        return redirect("home")

    holding, created = UserHolding.objects.get_or_create(
        user=request.user, symbol=symbol,
        defaults={"average_price": price_d},
    )
    if not created:
        total_qty = holding.quantity + 1
        holding.average_price = (holding.average_price * holding.quantity + price_d) / total_qty
        holding.quantity = total_qty
    else:
        holding.quantity = 1
    holding.save()

    profile.balance -= price_d
    profile.save()

    Transaction.objects.create(
        user=request.user, symbol=symbol, stock_name=data["name"],
        action=Transaction.BUY, quantity=1, price=price_d,
    )
    messages.success(request, f"Bought 1 share of {symbol} at ₹{price:.2f}")
    return redirect("home")


@login_required
def sell_stock(request):
    symbol = request.GET.get("symbol", "").upper()
    data = _fetch_price(symbol)
    price = data["price_inr"]

    if not price:
        messages.error(request, "Stock data unavailable.")
        return redirect("home")

    from decimal import Decimal
    price_d = Decimal(str(price))

    try:
        holding = UserHolding.objects.get(user=request.user, symbol=symbol)
    except UserHolding.DoesNotExist:
        messages.error(request, "You don't own this stock.")
        return redirect("home")

    if holding.quantity < 1:
        messages.error(request, "Insufficient shares.")
        return redirect("home")

    holding.quantity -= 1
    if holding.quantity == 0:
        holding.delete()
    else:
        holding.save()

    profile = request.user.profile
    profile.balance += price_d
    profile.save()

    Transaction.objects.create(
        user=request.user, symbol=symbol, stock_name=data["name"],
        action=Transaction.SELL, quantity=1, price=price_d,
    )
    messages.success(request, f"Sold 1 share of {symbol} at ₹{price:.2f}")
    return redirect("home")


@login_required
def my_portfolio(request):
    holdings = list(UserHolding.objects.filter(user=request.user, quantity__gt=0))
    for h in holdings:
        live = _fetch_price(h.symbol)
        h.current_price = live["price_inr"]
        h.current_value = h.current_price * h.quantity
        h.pnl = round((h.current_price - float(h.average_price)) * h.quantity, 2)

    total_value = sum(h.current_value for h in holdings)
    return render(request, "stockmanager/portfolio.html", {
        "holdings": holdings,
        "total_value": total_value,
        "balance": request.user.profile.balance,
    })


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "stockmanager/transaction_history.html", {"transactions": transactions})


@login_required
def clear_transaction_history(request):
    Transaction.objects.filter(user=request.user).delete()
    messages.success(request, "Transaction history cleared.")
    return redirect("transaction_history")


def stock_graph(request):
    symbol = request.GET.get("symbol", "TCS.NS")
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5d", interval="1h")

    if hist.empty:
        return render(request, "stockmanager/stock_chart.html", {
            "symbol": symbol, "chart": None,
            "error": "Stock symbol not found or data unavailable.",
        })

    plt.figure(figsize=(10, 4))
    plt.plot(hist.index, hist["Close"], marker="o", color="cyan")
    plt.title(f"{symbol.upper()} — Last 5 Days (Hourly)")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_uri = "data:image/png;base64," + urllib.parse.quote(base64.b64encode(buf.read()))
    plt.close()

    return render(request, "stockmanager/stock_chart.html", {
        "symbol": symbol,
        "chart": image_uri,
        "latest_price": round(float(hist["Close"].iloc[-1]), 2),
        "min_price": round(float(hist["Close"].min()), 2),
        "max_price": round(float(hist["Close"].max()), 2),
        "avg_price": round(float(hist["Close"].mean()), 2),
        "error": None,
    })


def stock_prices_api(request):
    """Legacy JSON endpoint — kept for backward compatibility."""
    data = [_fetch_price(s["symbol"]) for s in TRACKED_SYMBOLS]
    return JsonResponse({"stocks": data})


def add_stock(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = StockForm()
    return render(request, "stockmanager/add_stock.html", {"form": form})


@login_required
def delete_stock_page(request):
    if request.method == "POST":
        stock_id = request.POST.get("stock_id")
        if stock_id:
            get_object_or_404(Stock, pk=stock_id).delete()
            return redirect("delete_stock_page")
    items = Stock.objects.all()
    return render(request, "stockmanager/delete_stock_page.html", {"items": items})


@user_passes_test(lambda u: u.is_superuser)
def deposit_money(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        amount = float(request.POST.get("amount", 0))
        user = get_object_or_404(User, id=user_id)
        from decimal import Decimal
        user.profile.balance += Decimal(str(amount))
        user.profile.save()
        messages.success(request, f"₹{amount} deposited to {user.username}")
        return redirect("home")
    users = User.objects.all()
    return render(request, "stockmanager/deposit.html", {"users": users})


@login_required
def withdraw_money(request):
    profile = request.user.profile
    if request.method == "POST":
        try:
            from decimal import Decimal
            amount = Decimal(str(request.POST.get("amount")))
            if amount <= 0:
                messages.error(request, "Enter a positive amount.")
            elif amount > profile.balance:
                messages.error(request, "Insufficient balance.")
            else:
                profile.balance -= amount
                profile.save()
                messages.success(request, f"₹{amount} withdrawn successfully.")
                return redirect("home")
        except Exception:
            messages.error(request, "Invalid amount entered.")
    return render(request, "stockmanager/withdraw_money.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


class Custom_Logout(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
