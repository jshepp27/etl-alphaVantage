import requests

from .ticker_extractor import TickerExtractor


class AlphavantageTickerExtractor(TickerExtractor):

    def __init__(self, api_key):
        self._api_key = api_key
        super().__init__()

    def _api_url(self, symbol):
        return f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.LON&apikey={self._api_key}"

    def extract(self, symbol):
        response = requests.get(self._api_url(symbol))
        data = response.json()
        response.raise_for_status() # NEVER MISS THIS OUT!!!
        return data

