import pytz
from django.db import models
from django.conf import settings

from stockspec.users.models import User

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class Ticker(models.Model):
    """A table that represents a ticker (a publicly listed stock/company)
    """

    class Meta:
        db_table = "ticker"

    symbol = models.CharField(
        max_length=20, blank=False, null=False, primary_key=True
    )
    timezone = models.CharField(
        max_length=100, choices=TIMEZONES, default=settings.TIME_ZONE
    )
    last_updated = models.DateTimeField(auto_now=True)

    company = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    exchange = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    beta = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    logo_url = models.CharField(max_length=300, null=True, blank=True)


class StockPrice(models.Model):
    """A table representing stock price
    timeseries for specific tickers
    """

    class Meta:
        db_table = "price"

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    close_price = models.DecimalField(decimal_places=4, max_digits=10)
    volume = models.BigIntegerField()
    datetime = models.DateTimeField()


class Portfolio(models.Model):
    """A table that represents a user's portfolio
    including the M2M relationship to tickers.
    """

    class Meta:
        db_table = "portfolio"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tickers = models.ManyToManyField(Ticker)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
