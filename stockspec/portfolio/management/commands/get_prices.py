from django.conf import settings
from django.core.management.base import BaseCommand

from stockspec.alphavantage import AlphaVantage


class Command(BaseCommand):
    """Get prices from AlphaVantage
    """

    def __init__(self):
        self.av = AlphaVantage(settings.ALPHAVANTAGE_KEY)

    def handle(self, *args, **kwargs):
        self.av.fetch_symbols(["AAPL", "GOOGL"])
