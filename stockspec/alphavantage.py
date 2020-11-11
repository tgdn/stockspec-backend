import csv
import logging
import requests
from urllib.parse import urlencode
from typing import List
from concurrent.futures import ThreadPoolExecutor

import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from stockspec.portfolio.models import Ticker, StockPrice

logger = logging.getLogger(__name__)

OFFSET_TIMEZONE_MAP = {
    "UTC-05": "US/Eastern",
}


class AlphaVantage:
    """A simple threaded interface to the AlphaVantage api.
    """

    API_URL = "https://www.alphavantage.co/query?"
    # price intervals
    INTERVAL = "30min"
    # in seconds
    REQUEST_TIMEOUT = 5
    MAX_RETRIES = 3

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        # setup adaptor with retries
        adapter = requests.adapters.HTTPAdapter(max_retries=self.MAX_RETRIES)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _parse(self, content):
        """Decode and parse CSV content from request
        """
        decoded = content.decode("utf-8")
        return csv.DictReader(decoded.splitlines(), delimiter=",")

    def _insert_prices(self, symbol: str, prices: List):
        # get or create ticker row
        ticker, created = Ticker.objects.get_or_create(symbol=symbol)
        tz = pytz.timezone(ticker.timezone)
        # set timezone if this is a new ticker
        if created:
            tz = self.get_timezone(symbol)
            if tz is not None:
                ticker.timezone = tz.zone
                ticker.save()
            else:
                logger.warn(
                    f"{symbol}: timezone not found, using default: {settings.TIME_ZONE}"
                )

        # build list of price instances
        objs = []
        latest_time = (
            StockPrice.objects.filter(ticker=symbol)
            .order_by("-datetime")
            .values("datetime")
            .first()
            or {}
        ).get("datetime")

        for row in prices:
            # make time aware
            time = timezone.make_aware(parse_datetime(row.get("time")), tz)
            # filter duplicates
            if latest_time is not None and time <= latest_time:
                continue

            objs.append(
                StockPrice(
                    ticker=ticker,
                    close_price=row.get("close"),
                    volume=row.get("volume"),
                    datetime=time,
                )
            )

        # insert all prices
        StockPrice.objects.bulk_create(objs)
        ticker.last_updated = timezone.now()
        ticker.save()

    def _fetch(self, **params):
        """encode url and make request
        """
        params["apikey"] = self.api_key
        params["interval"] = self.INTERVAL
        params["datatype"] = "csv"
        encoded_params = urlencode(params)
        url = f"{self.API_URL}{encoded_params}"
        symbol = params.get("symbol")
        res = None

        try:
            res = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            res.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
        except requests.exceptions.HTTPError as ex:
            status_code = ex.response.status_code
            logger.error(f"Received code {status_code} while fetching {url}")
        except Exception as e:
            logger.exception("Unknown error", stack_info=True)

        return res

    def fetch_symbol(self, symbol: str):
        """Fetch prices for a symbol.

        Let's default to fetching the past month of trade data.
        This should probably depend on whether we need it or not.
        For example, if we have scheduler fetching every trade day,
        then we can use the full version of the TIME_SERIES_INTRADAY function.
        """
        function = "TIME_SERIES_INTRADAY_EXTENDED"

        logger.info(f"Gettting prices for: {symbol}")
        res = self._fetch(function=function, symbol=symbol, slice="year1month1")
        reader = self._parse(res.content)
        rows = list(reader)
        if len(rows) > 0:
            self._insert_prices(symbol, rows)
        else:
            logger.info(f"Could not find any prices for symbol: {symbol}")

        return res

    def fetch_symbols(self, symbols: List[str]):
        """A helper method to fetch symbols concurrently
        """
        with ThreadPoolExecutor() as executor:
            [
                executor.submit(self.fetch_symbol, symbol).result()
                for symbol in symbols
            ]

    def get_timezone(self, symbol: str):
        """Search symbol in AV to get timezone
        """
        function = "SYMBOL_SEARCH"

        res = self._fetch(function=function, keywords=symbol)
        rows = list(self._parse(res.content))
        if len(rows) == 0:
            logger.info(f"No results trying to fetch timezone for {symbol}")
            return

        # Let's use the first match
        result = rows[0]
        timezone = OFFSET_TIMEZONE_MAP.get(result.get("timezone"))

        tz = None
        try:
            tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            pass

        # return none if timezone not found
        return tz
