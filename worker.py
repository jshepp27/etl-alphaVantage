import os
import logging
import time

from ticker_fetcher import AlphavantageTickerExtractor, PostgresqlTickerLoader, AlphavantageTickerTransformer
from ticker_fetcher.ticker_etl_runner import TickerETLRunner


# TODO Schedule with AirFlow
# TODO Observability


def main():
    print("Starting the amazing ticker app of awesomes.")
    TICKER = "DRDR"
    db_url = os.environ.get("DATABASE_URL")

    # this is called dependency injection
    extractor = AlphavantageTickerExtractor()
    transformer = AlphavantageTickerTransformer()
    loader = PostgresqlTickerLoader(db_url)
    runner = TickerETLRunner(TICKER, extractor, transformer, loader)

    run = 1
    while True:
        runner.run()
        time.sleep(15)
        print(f"Run number: {run}")
        run = run + 1


if __name__ == "__main__":
    main()
