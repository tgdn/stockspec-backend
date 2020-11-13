import argparse

from . import APIBaseCommand


class Command(APIBaseCommand):
    """Import new tickers into the system
    """

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-t", "--tickers", nargs="+", required=True, help="<Required>"
        )

    def handle(self, *args, **kwargs):
        tickers = kwargs.get("tickers")
        self.av.fetch_symbols(tickers)
