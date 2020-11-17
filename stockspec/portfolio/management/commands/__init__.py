from django.conf import settings
from django.core.management.base import BaseCommand

from stockspec.alphavantage import AlphaVantage


class APIBaseCommand(BaseCommand):
    """An BaseCommand abstract class to use with AlphaVantage
    """

    def __init__(self):
        self.av = AlphaVantage(settings.ALPHAVANTAGE_KEY_POOL)
