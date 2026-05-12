"""Management command to seed initial stock data."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from stockmanager.models import Stock

STOCKS = [
    {
        "name": "Tata Consultancy Services",
        "symbol": "TCS.NS",
        "sector": "IT",
        "price_inr": Decimal("3500.00"),
    },
    {
        "name": "Infosys",
        "symbol": "INFY.NS",
        "sector": "IT",
        "price_inr": Decimal("1450.00"),
    },
    {
        "name": "Reliance Industries",
        "symbol": "RELIANCE.NS",
        "sector": "Energy",
        "price_inr": Decimal("2900.00"),
    },
    {
        "name": "HDFC Bank",
        "symbol": "HDFCBANK.NS",
        "sector": "Banking",
        "price_inr": Decimal("1700.00"),
    },
    {
        "name": "ICICI Bank",
        "symbol": "ICICIBANK.NS",
        "sector": "Banking",
        "price_inr": Decimal("1200.00"),
    },
    {
        "name": "ITC Ltd",
        "symbol": "ITC.NS",
        "sector": "FMCG",
        "price_inr": Decimal("460.00"),
    },
    {
        "name": "Wipro",
        "symbol": "WIPRO.NS",
        "sector": "IT",
        "price_inr": Decimal("510.00"),
    },
    {
        "name": "HCL Technologies",
        "symbol": "HCLTECH.NS",
        "sector": "IT",
        "price_inr": Decimal("1600.00"),
    },
    {
        "name": "State Bank of India",
        "symbol": "SBIN.NS",
        "sector": "Banking",
        "price_inr": Decimal("820.00"),
    },
    {
        "name": "Larsen & Toubro",
        "symbol": "LT.NS",
        "sector": "Infrastructure",
        "price_inr": Decimal("3800.00"),
    },
    {
        "name": "Kotak Mahindra Bank",
        "symbol": "KOTAKBANK.NS",
        "sector": "Banking",
        "price_inr": Decimal("1900.00"),
    },
    {
        "name": "Bajaj Finance",
        "symbol": "BAJFINANCE.NS",
        "sector": "Finance",
        "price_inr": Decimal("7200.00"),
    },
]


class Command(BaseCommand):
    help = "Seed initial stock data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing stocks before seeding"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Stock.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing stocks."))

        created_count = 0
        for data in STOCKS:
            _, created = Stock.objects.get_or_create(
                symbol=data["symbol"], defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {data['name']}"))
            else:
                self.stdout.write(f"  Exists:  {data['name']}")

        exists_count = len(STOCKS) - created_count
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count} new stocks created, {exists_count} already existed."
            )
        )
