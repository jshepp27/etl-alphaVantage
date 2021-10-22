class TickerETLRunner:
    """Orchestrates the ETL Process"""
    def __init__(self, symbol, extractor, transformer, loader):
        self._symbol = symbol
        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader

    def run(self):
        data = self._extractor.extract(self._symbol)
        transformer_data = self._transformer.transform(data, self._symbol)
        self._loader.load(transformer_data, self._symbol)


