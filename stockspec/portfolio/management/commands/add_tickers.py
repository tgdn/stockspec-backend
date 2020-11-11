from . import APIBaseCommand


class Command(APIBaseCommand):
    """Import new tickers into the system
    """

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("filename", type=argparse.FileType("r"))

    def handle(self, *args, **kwargs):
        pass
