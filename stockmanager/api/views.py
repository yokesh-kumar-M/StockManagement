import logging
from decimal import Decimal

import yfinance as yf
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction as db_transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import UserHolding, UserProfile, Transaction
from .serializers import (
    DepositSerializer,
    RegisterSerializer,
    TradeSerializer,
    TransactionSerializer,
    UserHoldingSerializer,
    UserProfileSerializer,
    WithdrawSerializer,
)
from .throttles import StockPriceThrottle, TradeThrottle

logger = logging.getLogger(__name__)

TRACKED_SYMBOLS = [
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT"},
    {"symbol": "INFY.NS", "name": "Infosys", "sector": "IT"},
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
    {"symbol": "ITC.NS", "name": "ITC Ltd", "sector": "FMCG"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "IT"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Finance"},
]


def fetch_live_price(symbol: str) -> dict:
    cache_key = f"live_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        info = yf.Ticker(symbol).info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        change_pct = info.get("regularMarketChangePercent", 0) or 0
        data = {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "price_inr": round(float(price), 2) if price else 0,
            "change_percent": round(float(change_pct), 2),
            "day_high": round(float(info.get("dayHigh") or 0), 2),
            "day_low": round(float(info.get("dayLow") or 0), 2),
            "volume": info.get("volume") or 0,
        }
        if data["price_inr"] > 0:
            cache.set(cache_key, data, timeout=300)
        return data
    except Exception as exc:
        logger.warning("Price fetch failed for %s: %s", symbol, exc)
        return {"symbol": symbol, "name": symbol, "price_inr": 0, "change_percent": 0}


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: {"type": "object"}})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"id": user.id, "username": user.username, "email": user.email},
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Profile ──────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# ─── Stocks ───────────────────────────────────────────────────────────────────

class StockListView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StockPriceThrottle]

    @extend_schema(
        responses={200: {"type": "object"}},
        summary="List live stock prices for tracked Indian equities",
    )
    def get(self, request):
        stocks = []
        for s in TRACKED_SYMBOLS:
            data = fetch_live_price(s["symbol"])
            data.setdefault("sector", s.get("sector", ""))
            stocks.append(data)
        stocks = [s for s in stocks if s["price_inr"] > 0]
        return Response({"stocks": stocks, "count": len(stocks)})


# ─── Trading ──────────────────────────────────────────────────────────────────

class TradeView(APIView):
    throttle_classes = [TradeThrottle]

    @extend_schema(
        request=TradeSerializer,
        responses={200: {"type": "object"}},
        summary="Execute a buy or sell trade",
    )
    @db_transaction.atomic
    def post(self, request):
        serializer = TradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        symbol: str = serializer.validated_data["symbol"]
        quantity: int = serializer.validated_data["quantity"]
        action: str = serializer.validated_data["action"]

        price_data = fetch_live_price(symbol)
        price = Decimal(str(price_data["price_inr"]))

        if price <= 0:
            return Response({"error": "Stock data unavailable. Try again later."}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        total_cost = price * quantity

        if action == Transaction.BUY:
            if profile.balance < total_cost:
                return Response(
                    {"error": f"Insufficient balance. Need ₹{total_cost:.2f}, have ₹{profile.balance:.2f}."},
                    status=400,
                )
            holding, created = UserHolding.objects.get_or_create(
                user=request.user, symbol=symbol,
                defaults={"average_price": price, "quantity": 0},
            )
            new_qty = holding.quantity + quantity
            holding.average_price = (holding.average_price * holding.quantity + price * quantity) / new_qty
            holding.quantity = new_qty
            holding.save()
            profile.balance -= total_cost

        else:  # SELL
            try:
                holding = UserHolding.objects.get(user=request.user, symbol=symbol)
            except UserHolding.DoesNotExist:
                return Response({"error": "You do not own any shares of this stock."}, status=400)

            if holding.quantity < quantity:
                return Response(
                    {"error": f"You only own {holding.quantity} share(s) of {symbol}."},
                    status=400,
                )
            holding.quantity -= quantity
            if holding.quantity == 0:
                holding.delete()
            else:
                holding.save()
            profile.balance += total_cost

        profile.save()

        Transaction.objects.create(
            user=request.user,
            symbol=symbol,
            stock_name=price_data["name"],
            action=action,
            quantity=quantity,
            price=price,
        )

        return Response({
            "message": f"{action} order executed.",
            "symbol": symbol,
            "quantity": quantity,
            "price": float(price),
            "total_value": float(total_cost),
            "new_balance": float(profile.balance),
        })


# ─── Portfolio ────────────────────────────────────────────────────────────────

class PortfolioView(APIView):
    @extend_schema(summary="Get current user portfolio with live P&L")
    def get(self, request):
        holdings = list(UserHolding.objects.filter(user=request.user, quantity__gt=0))

        prices = {s["symbol"]: fetch_live_price(s["symbol"])["price_inr"] for s in TRACKED_SYMBOLS}
        for h in holdings:
            if h.symbol not in prices:
                prices[h.symbol] = fetch_live_price(h.symbol)["price_inr"]

        serializer = UserHoldingSerializer(holdings, many=True, context={"prices": prices})

        total_invested = sum(float(h.average_price) * h.quantity for h in holdings)
        total_current = sum(prices.get(h.symbol, float(h.average_price)) * h.quantity for h in holdings)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        return Response({
            "holdings": serializer.data,
            "summary": {
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_current, 2),
                "total_pnl": round(total_current - total_invested, 2),
                "total_pnl_pct": round(
                    (total_current - total_invested) / total_invested * 100, 2
                ) if total_invested else 0,
                "balance": float(profile.balance),
            },
        })


# ─── Transactions ─────────────────────────────────────────────────────────────

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        action = self.request.query_params.get("action")
        if action in (Transaction.BUY, Transaction.SELL):
            qs = qs.filter(action=action)
        symbol = self.request.query_params.get("symbol")
        if symbol:
            qs = qs.filter(symbol__icontains=symbol.upper())
        return qs


class TransactionClearView(APIView):
    @extend_schema(summary="Delete all transaction history for the current user")
    def delete(self, request):
        count, _ = Transaction.objects.filter(user=request.user).delete()
        return Response({"message": f"Cleared {count} transaction(s)."})


# ─── Admin Actions ────────────────────────────────────────────────────────────

class DepositView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(request=DepositSerializer, summary="Admin: deposit funds to a user account")
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        amount = serializer.validated_data["amount"]
        profile.balance += amount
        profile.save()

        return Response({
            "message": f"₹{amount} deposited to {user.username}.",
            "new_balance": float(profile.balance),
        })


class WithdrawView(APIView):
    @extend_schema(request=WithdrawSerializer, summary="Withdraw funds from authenticated user's account")
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if profile.balance < amount:
            return Response(
                {"error": f"Insufficient balance. You have ₹{profile.balance:.2f}."},
                status=400,
            )

        profile.balance -= amount
        profile.save()

        return Response({"message": f"₹{amount} withdrawn.", "new_balance": float(profile.balance)})


# ─── Charts ───────────────────────────────────────────────────────────────────

class StockChartView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StockPriceThrottle]

    @extend_schema(
        parameters=[
            OpenApiParameter("symbol", str, description="Stock ticker, e.g. TCS.NS"),
            OpenApiParameter("period", str, description="Period: 1d, 5d, 1mo, 3mo, 1y"),
            OpenApiParameter("interval", str, description="Interval: 1m, 5m, 15m, 1h, 1d"),
        ],
        summary="Get OHLCV candlestick data for a stock",
    )
    def get(self, request):
        symbol = request.query_params.get("symbol", "TCS.NS").upper()
        period = request.query_params.get("period", "5d")
        interval = request.query_params.get("interval", "1h")

        cache_key = f"chart_{symbol}_{period}_{interval}"
        if cached := cache.get(cache_key):
            return Response(cached)

        try:
            hist = yf.Ticker(symbol).history(period=period, interval=interval)
            if hist.empty:
                return Response({"error": "No data found for this symbol."}, status=404)

            ohlcv = [
                {
                    "time": idx.isoformat(),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                }
                for idx, row in hist.iterrows()
            ]

            closes = hist["Close"]
            data = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "ohlcv": ohlcv,
                "stats": {
                    "latest": round(float(closes.iloc[-1]), 2),
                    "open": round(float(closes.iloc[0]), 2),
                    "min": round(float(closes.min()), 2),
                    "max": round(float(closes.max()), 2),
                    "avg": round(float(closes.mean()), 2),
                    "change": round(float(closes.iloc[-1] - closes.iloc[0]), 2),
                    "change_pct": round(float((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0] * 100), 2),
                },
            }
            cache.set(cache_key, data, timeout=300)
            return Response(data)
        except Exception as exc:
            logger.error("Chart data error for %s: %s", symbol, exc)
            return Response({"error": "Failed to fetch chart data."}, status=500)


# ─── Health ───────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@extend_schema(summary="Health check", responses={200: {"type": "object"}})
def health_check(request):
    return Response({"status": "ok", "version": "1.0.0"})
