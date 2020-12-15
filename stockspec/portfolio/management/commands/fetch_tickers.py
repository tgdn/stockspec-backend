import argparse

from . import APIBaseCommand


class Command(APIBaseCommand):
    """Import new tickers into the system"""

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-t", "--tickers", nargs="+", required=True, help="<Required>"
        )

    def handle(self, *args, **kwargs):
        symbols = kwargs.get("tickers")
        try:
            self.av.import_symbols(symbols)
        except KeyboardInterrupt:
            print("Exiting early...")
