"""
Enterprise upgrade migration — adds new fields, fixes types, adds indexes.
Safe to run on a fresh Supabase PostgreSQL database (runs after 0007).
"""

from decimal import Decimal

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def populate_transaction_symbol(apps, schema_editor):
    """Copy stock_name into the new symbol field for existing rows."""
    Transaction = apps.get_model("stockmanager", "Transaction")
    for t in Transaction.objects.filter(symbol=""):
        t.symbol = t.stock_name.upper()[:20]
        t.save(update_fields=["symbol"])


def populate_transaction_total_value(apps, schema_editor):
    """Compute total_value = price * quantity for existing rows."""
    Transaction = apps.get_model("stockmanager", "Transaction")
    for t in Transaction.objects.filter(total_value=0):
        try:
            t.total_value = Decimal(str(t.price)) * t.quantity
            t.save(update_fields=["total_value"])
        except Exception:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ("stockmanager", "0007_alter_userholding_quantity_alter_userprofile_balance"),
    ]

    operations = [
        # ── Stock ─────────────────────────────────────────────────────────────
        migrations.AlterField(
            model_name="stock",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="stock",
            name="symbol",
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name="stock",
            name="sector",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="stock",
            name="price_inr",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=12
            ),
        ),
        migrations.AddField(
            model_name="stock",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="stock",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # ── UserProfile ───────────────────────────────────────────────────────
        migrations.AlterField(
            model_name="userprofile",
            name="balance",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("10000.00"), max_digits=14
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        # ── UserHolding ───────────────────────────────────────────────────────
        migrations.AlterField(
            model_name="userholding",
            name="symbol",
            field=models.CharField(max_length=20),
        ),
        migrations.AddField(
            model_name="userholding",
            name="average_price",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=12
            ),
        ),
        migrations.AddField(
            model_name="userholding",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name="userholding",
            unique_together={("user", "symbol")},
        ),
        # ── Transaction ───────────────────────────────────────────────────────
        migrations.AlterField(
            model_name="transaction",
            name="stock_name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="action",
            field=models.CharField(
                choices=[("BUY", "Buy"), ("SELL", "Sell")], max_length=4
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AddField(
            model_name="transaction",
            name="symbol",
            field=models.CharField(default="", max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="transaction",
            name="total_value",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=14
            ),
        ),
        # Data migrations
        migrations.RunPython(populate_transaction_symbol, migrations.RunPython.noop),
        migrations.RunPython(
            populate_transaction_total_value, migrations.RunPython.noop
        ),
        # ── Indexes ───────────────────────────────────────────────────────────
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["user", "-timestamp"], name="trans_user_ts_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["symbol"], name="trans_symbol_idx"),
        ),
        migrations.AddIndex(
            model_name="userholding",
            index=models.Index(fields=["symbol"], name="holding_symbol_idx"),
        ),
    ]
