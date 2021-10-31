from abc import abstractmethod, ABC


class TickerLoader(ABC):
    """Loads tick data into a specific data store."""

    @abstractmethod
    def load(self, data, symbol):
        pass