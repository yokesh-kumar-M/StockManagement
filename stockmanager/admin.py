from django.contrib import admin
from django.utils.html import format_html

from .models import Stock, UserHolding, Transaction, UserProfile


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "price_inr", "sector", "is_active", "updated_at")
    list_filter = ("is_active", "sector")
    search_fields = ("name", "symbol", "isin")
    list_editable = ("is_active",)
    ordering = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)


@admin.register(UserHolding)
class UserHoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "symbol", "quantity", "average_price", "updated_at")
    list_filter = ("symbol",)
    search_fields = ("user__username", "symbol")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "symbol", "action_badge", "quantity", "price", "total_value", "timestamp")
    list_filter = ("action", "symbol")
    search_fields = ("user__username", "symbol", "stock_name")
    readonly_fields = ("total_value", "timestamp")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)

    def action_badge(self, obj):
        color = "green" if obj.action == "BUY" else "red"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.action)
    action_badge.short_description = "Action"


# Customize admin site
admin.site.site_header = "Stock Manager Admin"
admin.site.site_title = "Stock Manager"
admin.site.index_title = "Dashboard"
