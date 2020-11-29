import csv
import logging
import requests
import itertools
from random import randrange
from time import sleep
from urllib.parse import urlencode
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date

from stockspec.exceptions import APIRateLimited
from stockspec.portfolio.models import Ticker, StockPrice

logger = logging.getLogger(__name__)


class AlphaVantage:
    """A simple threaded interface to the AlphaVantage api."""

    API_URL = "https://www.alphavantage.co/query?"
    REQUEST_TIMEOUT = 5  # in seconds
    MAX_RETRIES = 3

    def __init__(self, api_key_pool: List[str]):
        self.api_key_pool = api_key_pool
        self.session = requests.Session()
        # setup adaptor with retries
        adapter = requests.adapters.HTTPAdapter(max_retries=self.MAX_RETRIES)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def parse(self, content):
        """Decode and parse CSV content from request"""
        decoded = content.decode("utf-8")
        return csv.DictReader(decoded.splitlines(), delimiter=",")

    def insert_prices(self, symbol: str, prices: List):
        """Insert new prices in the db"""
        # get or create ticker and get company info if new
        ticker, created = Ticker.objects.get_or_create(symbol=symbol)
        if created:
            self.get_company_info(ticker)

        # build list of price instances
        objs = []
        latest_date = (
            StockPrice.objects.filter(ticker=symbol)
            .order_by("-date")
            .values_list("date", flat=True)
            .first()
        )

        for row in prices:
            # no need to continue if the data is malformed
            if row.get("close") is None:
                raise APIRateLimited(symbol)

            # filter duplicates
            date = parse_date(row.get("timestamp"))
            if latest_date is not None and date <= latest_date:
                continue

            objs.append(
                StockPrice(
                    ticker=ticker,
                    close_price=row.get("close"),
                    volume=row.get("volume"),
                    date=date,
                )
            )

        # insert all prices
        StockPrice.objects.bulk_create(objs)
        # we dont want to update ticker
        # unless we inserted some rows
        if len(objs) > 0:
            # get last 2 rows and update last_price and performance
            start, end = StockPrice.get_series(symbol, 2)
            ticker.last_price = end.close_price
            ticker.delta = end.close_price - start.close_price
            ticker.percentage_change = ticker.delta / start.close_price
            ticker.last_updated = timezone.now()
            ticker.save()

        # number of actually inserted prices
        return len(objs)

    def fetch(self, **params):
        """encode url and make request"""

        symbol = params.get("symbol")
        params["datatype"] = "csv"
        encoded_params = urlencode(params)
        url = f"{self.API_URL}{encoded_params}"
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

    def fetch_symbol(self, symbol: str, api_key: str) -> Tuple[int, int]:
        """Fetch prices for a symbol.
        At the moment we fetch the last 100 daily close prices.
        """

        logger.info(f"Fetching prices for: {symbol} with key: {api_key}")
        function = "TIME_SERIES_DAILY_ADJUSTED"
        # make request
        res = self.fetch(apikey=api_key, function=function, symbol=symbol,)
        reader = self.parse(res.content)  # parse CSV
        res.close()  # avoid running out of request pools
        rows = list(reader)

        total_rows = len(rows)
        total_inserted = 0
        if total_rows > 0:
            total_inserted = self.insert_prices(symbol, rows)
        else:
            logger.info(f"Could not find any prices for symbol: {symbol}")

        return total_rows, total_inserted

    # def fetch_symbols(self, symbols: List[str]):
    #     """A helper method to fetch symbols concurrently"""

    #     # api key generator
    #     # each key can be used 5 times/minute.
    #     # so we pause every key count to avoid being rate limited
    #     api_keygen = itertools.cycle(self.api_key_pool)
    #     threshold = 2  # max(1, len(self.api_key_pool))

    #     with ThreadPoolExecutor() as executor:
    #         fn = self.fetch_symbol
    #         futures_symbol = {}

    #         for i, symbol in enumerate(symbols, 1):
    #             futures_symbol[
    #                 executor.submit(fn, symbol, next(api_keygen))
    #             ] = symbol
    #             if i % threshold == 0:
    #                 sleep(5)  # sleep a little

    #         for future in as_completed(futures_symbol):
    #             symbol = futures_symbol[future]
    #             try:
    #                 total, inserted = future.result()
    #             except Exception as ex:
    #                 logger.error(f"{symbol} generated an exception:\n{ex}")
    #             else:
    #                 logger.info(f"{symbol}: found {total}, inserted {inserted}")

    def import_symbols(self, symbols: List[str]):
        """
        A non threaded method that imports
        news symbols into the system.
        It executes 3 requests every 30 seconds to avoid
        being locked out of the api. (prices, timezone, company_info)
        This means symbols are imported at a rate of 2 per minute (slow).
        """

        symbols_left = symbols[:]  # clone list
        api_keygen = itertools.cycle(self.api_key_pool)
        while len(symbols_left) != 0:
            logger.info(f"Attempting to fetch {len(symbols)} symbols...")
            for i, symbol in enumerate(symbols_left):
                try:
                    total, inserted = self.fetch_symbol(
                        symbol, next(api_keygen)
                    )
                except Exception as ex:
                    logger.error(f"{symbol} generated an exception:\n{ex}")
                else:
                    logger.info(f"{symbol}: found {total}, inserted {inserted}")
                if i != 0 and i % len(self.api_key_pool) == 0:
                    sleep(10)
                else:
                    symbols_left.remove(symbol)
                    sleep(5)

    def get_company_info(self, ticker: Ticker):
        """Get company info from symbol"""

        function = "OVERVIEW"
        symbol = ticker.symbol

        def fetch():
            return self.fetch(function=function, symbol=symbol)

        success = False
        company = None
        # sleep before request to avoid lock
        sleep(randrange(0, 30, 15))
        res = fetch()

        while not success:
            try:
                company = res.json()
                # avoid getting rate limited
                if company.get("Note") is not None:
                    sleep_time = 60  # randrange(30, 90, 15)
                    logger.info(
                        f"{symbol}: Got rate limited, retrying in {sleep_time:.2f}s"
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

