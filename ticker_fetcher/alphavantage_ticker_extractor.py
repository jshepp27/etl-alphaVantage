import requests

from .ticker_extractor import TickerExtractor


class AlphavantageTickerExtractor(TickerExtractor):
    def _api_url(self, symbol):
        return f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.LON&apikey=OMS1DTGJT1MEO1I9"

    def extract(self, symbol):
        response = requests.get(self._api_url(symbol))
        data = response.json()
        response.raise_for_status() # NEVER MISS THIS OUT!!!
        return data

