from datetime import timedelta

from django.utils import timezone

from . import APIBaseCommand
from stockspec.portfolio.models import Ticker


class Command(APIBaseCommand):
    """Get prices from AlphaVantage
    """

    def handle(self, *args, **kwargs):
        # Our prices are at 30mins intervals
        thirtyminsago = timezone.now() - timedelta(minutes=30)
        symbols = Ticker.objects.filter(
            last_updated__lte=thirtyminsago
        ).values_list("symbol", flat=True)
        self.av.fetch_symbols(symbols)
