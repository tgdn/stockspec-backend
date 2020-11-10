from django.db import models


class Ticker(models.Model):
    class Meta:
        db_table = "ticker"

    ticker = models.CharField(
        max_length=20, blank=False, null=False, primary_key=True
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
