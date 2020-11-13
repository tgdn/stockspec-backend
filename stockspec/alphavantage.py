import csv
import logging
import requests
from random import randrange
from time import sleep
from urllib.parse import urlencode
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            # fetch timezone and company info
            tz = self.get_timezone(symbol)
            self.get_company_info(ticker)
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
            .values_list("datetime", flat=True)
            .first()
        )

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

        # number of actually inserted prices
        return len(objs)

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

    def fetch_symbol(self, symbol: str) -> Tuple[int, int]:
        """Fetch prices for a symbol.

        Let's default to fetching the past month of trade data.
        This should probably depend on whether we need it or not.
        For example, if we have scheduler fetching every trade day,
        then we can use the full version of the TIME_SERIES_INTRADAY function.
        """
        function = "TIME_SERIES_INTRADAY_EXTENDED"

        logger.info(f"Fetching prices for: {symbol}")
        res = self._fetch(function=function, symbol=symbol, slice="year1month1")
        reader = self._parse(res.content)
        rows = list(reader)

        total_inserted = 0
        if len(rows) > 0:
            total_inserted = self._insert_prices(symbol, rows)
        else:
            logger.info(f"Could not find any prices for symbol: {symbol}")

        # rows found, rows inserted
        return len(rows), total_inserted

    def fetch_symbols(self, symbols: List[str]):
        """A helper method to fetch symbols concurrently
        """
        with ThreadPoolExecutor() as executor:
            fn = self.fetch_symbol
            futures_symbol = {
                executor.submit(fn, symbol): symbol for symbol in symbols
            }

            for future in as_completed(futures_symbol):
                symbol = futures_symbol[future]
                try:
                    total, inserted = future.result()
                except Exception as ex:
                    logger.exception(f"{symbol} generated an exception:\n{ex}")
                else:
                    logger.info(f"{symbol}: found {total}, inserted {inserted}")

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

    def get_company_info(self, ticker: Ticker):
        """Get company info from symbol
        """
        function = "OVERVIEW"
        symbol = ticker.symbol

        def fetch():
            return self._fetch(function=function, symbol=symbol)

        success = False
        company = None
        res = fetch()
        sleep(randrange(0, 30, 15))

        while not success:
            try:
                company = res.json()
                # avoid getting locked out of api
                if company.get("Note") is not None:
                    sleep_time = randrange(30, 90, 15)
                    logger.info(
                        f"{symbol}: Got locked out, retrying in {sleep_time:.2f}s"
                    )
                    sleep(sleep_time)
                    continue
            except ValueError as ex:
                logger.exception(
                    f"Could not parse JSON when getting company info for {symbol}"
                )
                break
            except Exception as ex:
                logger.exception(
                    f"{symbol}: exception trying to fetch company info:\n{ex}"
                )
                break
            else:
                success = True

        if company is not None:
            ticker.company = company.get("Name")
            ticker.description = company.get("Description")
            ticker.exchange = company.get("Exchange")
            ticker.country = company.get("Country")
            ticker.sector = company.get("Sector")
            ticker.industry = company.get("Industry")
            beta = company.get("Beta")
            if beta == "None":
                beta = None
            ticker.beta = beta
            ticker.save()

