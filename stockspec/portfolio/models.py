import pytz
from typing import List
from django.db import models
from django.db.models import Count, Subquery
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

    def __str__(self):
        return self.symbol

    @staticmethod
    def top_tickers():
        """Get tickers that have been used the most in portfolios"""
        # cant do all of this in one query with the orm...
        # be aware there is an extra column returned `price`
        # which is the latest stock price found.
        sql = """
        SELECT
        COUNT(portfolio_tickers.ticker_id) as ticker_count,
        ticker.*,
        T.close_price AS price
        FROM portfolio_tickers
        INNER JOIN ticker ON ticker.symbol=portfolio_tickers.ticker_id
        LEFT JOIN (
            SELECT ticker_id, close_price, max(date)
            FROM price
            GROUP BY ticker_id
        ) T ON T.ticker_id=ticker.symbol
        GROUP BY portfolio_tickers.ticker_id
        ORDER BY ticker_count DESC
        LIMIT 10
        """
        return Ticker.objects.raw(sql)


class StockPrice(models.Model):
    """A table representing stock price
    timeseries for specific tickers
    """

    class Meta:
        db_table = "price"
        ordering = ["date"]

    ticker = models.ForeignKey(
        Ticker, on_delete=models.CASCADE, related_name="prices"
    )
    close_price = models.DecimalField(decimal_places=4, max_digits=10)
    volume = models.BigIntegerField()
    date = models.DateField(null=True)


class Portfolio(models.Model):
    """A table that represents a user's portfolio
    including the M2M relationship to tickers.
    """

    class Meta:
        db_table = "portfolio"
        ordering = ["-updated_at", "name"]

    name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tickers = models.ManyToManyField(Ticker)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}#{self.id}"

    @classmethod
    def exact_tickers(cls, tickers: List[Ticker]):
        """A method that returns portfolios with exactly given tickers.

        It dynamically filters to match exact symbols, which unfortunately
        joins the ticker table n-times (once for each comparison).
        SQLite has a hard limit of 64 joins, our portfolios should not have more.
        ref: https://www.sqlite.org/limits.html
        """
        # avoid database error
        tickers = tickers[:63]
        queryset = cls.objects.annotate(count=Count("tickers")).filter(
            count=len(tickers)
        )

        # dynamically chain filters
        for ticker in tickers:
            queryset = queryset.filter(tickers__symbol=ticker.symbol)
        return queryset
