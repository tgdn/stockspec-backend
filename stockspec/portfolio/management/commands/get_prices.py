from . import APIBaseCommand
from stockspec.portfolio.models import Ticker


class Command(APIBaseCommand):
    """Get prices from AlphaVantage
    """

    def handle(self, *args, **kwargs):
        symbols = Ticker.objects.values_list("symbol", flat=True)
        self.av.fetch_symbols(symbols)
