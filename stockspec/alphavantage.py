import logging
import requests
from urllib.parse import urlencode
from typing import List
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AlphaVantage:
    API_URL = "https://www.alphavantage.co/query?"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def _fetch(self, **params):
        """encode url and make request
        """
        params["apikey"] = self.api_key
        encoded_params = urlencode(params)
        url = f"{self.API_URL}{encoded_params}"

        return self.session.get(url).json()

    def fetch_symbol(self, symbol: str):
        print(symbol)
        resp = self._fetch(
            function="TIME_SERIES_INTRADAY", symbol=symbol, interval="5min"
        )
        print(len(resp))
        return resp

    def fetch_symbols(self, symbols: List[str]):
        with ThreadPoolExecutor() as executor:
            [executor.submit(self.fetch_symbol, symbol) for symbol in symbols]
