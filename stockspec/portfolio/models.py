import pytz
from django.db import models

TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class Ticker(models.Model):
    class Meta:
        db_table = "ticker"

    symbol = models.CharField(
        max_length=20, blank=False, null=False, primary_key=True
    )
    timezone = models.CharField(
        max_length=100, choices=TIMEZONES, default="UTC"
    )
    last_updated = models.DateTimeField(auto_now=True)
    logo_url = models.CharField(max_length=300)


class StockPrice(models.Model):
    class Meta:
        db_table = "price"

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    close_price = models.DecimalField(decimal_places=4, max_digits=10)
    volume = models.BigIntegerField()
    datetime = models.DateTimeField()
