from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import Stock, UserHolding, UserProfile, Transaction


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "balance",
            "created_at",
        )
        read_only_fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "created_at",
        )


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = (
            "id",
            "name",
            "symbol",
            "price_inr",
            "sector",
            "isin",
            "is_active",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at")


class UserHoldingSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    profit_loss_pct = serializers.SerializerMethodField()

    class Meta:
        model = UserHolding
        fields = (
            "id",
            "symbol",
            "quantity",
            "average_price",
            "current_price",
            "current_value",
            "profit_loss",
            "profit_loss_pct",
            "updated_at",
        )

    def _price(self, obj) -> float:
        prices = self.context.get("prices", {})
        return float(prices.get(obj.symbol, obj.average_price))

    def get_current_price(self, obj) -> float:
        return round(self._price(obj), 2)

    def get_current_value(self, obj) -> float:
        return round(self._price(obj) * obj.quantity, 2)

    def get_profit_loss(self, obj) -> float:
        cost = float(obj.average_price) * obj.quantity
        return round(self._price(obj) * obj.quantity - cost, 2)

    def get_profit_loss_pct(self, obj) -> float:
        avg = float(obj.average_price)
        if avg == 0:
            return 0.0
        return round((self._price(obj) - avg) / avg * 100, 2)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "symbol",
            "stock_name",
            "action",
            "quantity",
            "price",
            "total_value",
            "timestamp",
        )
        read_only_fields = ("id", "total_value", "timestamp")


class TradeSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20)
    quantity = serializers.IntegerField(min_value=1, max_value=10_000)
    action = serializers.ChoiceField(choices=["BUY", "SELL"])

    def validate_symbol(self, value: str) -> str:
        return value.upper().strip()


class DepositSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
