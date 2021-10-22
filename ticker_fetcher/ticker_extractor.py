from abc import ABC, abstractmethod


class TickerExtractor(ABC):
    """Extracts tick data from a specific provider."""

    @abstractmethod
    def extract(self, symbol):
        pass
