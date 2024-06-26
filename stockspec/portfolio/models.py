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

    # store last price and delta change
    # to avoid the extra join when querying.
    last_price = models.DecimalField(
        decimal_places=4, max_digits=10, null=True, blank=True
    )
    delta = models.DecimalField(
        decimal_places=4, max_digits=10, null=True, blank=True
    )
    percentage_change = models.DecimalField(
        decimal_places=4, max_digits=6, null=True, blank=True
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

    def price_at_date(self, date):
        """returns the price just before given date (latest price)"""
        return (
            self.prices.filter(date__lte=date)
            .values_list("close_price", flat=True)
            .order_by("-date")
            .first()
        )

    def return_for_period(self, start_date, end_date):
        """calculates performance of an asset within period time"""
        price_start = self.price_at_date(start_date)
        price_end = self.price_at_date(end_date)
        # check whether we have prices for period
        if not all([price_start, price_end]):
            raise Exception("No prices for given period")

        return (price_end - price_start) / price_start

    @staticmethod
    def top_tickers():
        """Get tickers that have been used the most in portfolios"""
        # cant do all of this in one query with the orm...
        sql = """
        SELECT
        COUNT(portfolio_tickers.ticker_id) as ticker_count,
        ticker.*
        FROM portfolio_tickers
        INNER JOIN ticker ON ticker.symbol=portfolio_tickers.ticker_id
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

    @staticmethod
    def get_series(symbol: str, length: int):
        """Efficient limit-offset method for getting last n-rows"""
        return StockPrice.objects.raw(
            """
            SELECT * FROM price
            WHERE ticker_id = %s
            ORDER BY date ASC
            LIMIT %s
            OFFSET (
                SELECT count(*)
                FROM price WHERE ticker_id = %s
            ) - %s
            """,
            [symbol, length, symbol, length],
        )


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

    def return_for_period(self, start_date, end_date):
        """return the performance of a portfolio over a period of time"""
        returns = [
            ticker.return_for_period(start_date, end_date)
            for ticker in self.tickers.all()
        ]
        # for now all assets have the same weight (1/len(assets))
        return sum(returns) / len(returns)

    @classmethod
    def get_or_create_from_tickers(cls, user: User, tickers: List[Ticker]):
        """
        Check whether a portfolio with given tickers exists and returns it,
        otherwise it creates one and returns it.
        """
        portfolio = cls.exact_tickers(tickers).filter(user=user).first()
        if portfolio is None:
            portfolio = cls.objects.create(user=user)
            portfolio.tickers.set(tickers)
        return portfolio

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
