import logging
import time

from config import Config, ConfigItem, ConfigurationError
from ticker_fetcher import AlphavantageTickerExtractor, PostgresqlTickerLoader, AlphavantageTickerTransformer
from ticker_fetcher.ticker_etl_runner import TickerETLRunner

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_config():
    config = Config(
        ConfigItem("ticker", "TICKER", "ticker", "DRDR"),
        ConfigItem("db_url", "DATABASE_URL", "db_url"),
        ConfigItem("api_key", "ALPHAVANTAGE_API_KEY", "api_key")
    )
    try:
        config.load_config()
    except ConfigurationError as e:
        # We don't mind if the config doesn't load as there's no config.json on heroku
        # We will log it though, so that we know what happened.
        logger.exception(e)
        pass

    return config


def main():
    config = setup_config()
    ticker = config["ticker"]
    db_url = config["db_url"]
    api_key = config["api_key"]

    # this is called dependency injection
    extractor = AlphavantageTickerExtractor(api_key=api_key)
    transformer = AlphavantageTickerTransformer()
    loader = PostgresqlTickerLoader(db_url)
    runner = TickerETLRunner(ticker, extractor, transformer, loader)

    run = 1
    while True:
        runner.run()
        time.sleep(15)
        print(f"Run number: {run}")
        run = run + 1


if __name__ == "__main__":
    main()
