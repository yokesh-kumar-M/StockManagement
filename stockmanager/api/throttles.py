from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class StockPriceThrottle(AnonRateThrottle):
    """60 stock-price requests per minute for anonymous users."""
    rate = "60/minute"


class TradeThrottle(UserRateThrottle):
    """Throttle trading actions to prevent abuse."""
    scope = "trade"
