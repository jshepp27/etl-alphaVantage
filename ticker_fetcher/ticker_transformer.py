from abc import ABC, abstractmethod


class TickerTransformer(ABC):
    """Transforms data from specific Ticker providers to a generic format."""

    @abstractmethod
    def transform(self, data, symbol):
        pass