from flask import Flask, render_template
from flask.logging import default_handler
import logging

from config import Config, ConfigItem, ConfigurationError

from .ticker_getter import TickerGetter

app = Flask(__name__)

# route all logs to app
root = logging.getLogger()
root.addHandler(default_handler)

# if we're not in standalone mode
if __name__ != "__main__":
    # route the app logs to gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # set the log levels to the same as gunicorn
    app.logger.setLevel(gunicorn_logger.level)
    root.setLevel(gunicorn_logger.level)


@app.before_first_request
def configure_config():
    config = Config(
        ConfigItem("ticker", "TICKER", "ticker", "DRDR"),
        ConfigItem("db_url", "DATABASE_URL", "db_url"),
    )
    try:
        config.load_config()
    except ConfigurationError as e:
        # We don't mind if the config doesn't load as there's no config.json on heroku
        # We will log it though, so that we know what happened.
        app.logger.exception(e)
        pass
    app.config["ticker"] = config["ticker"]
    app.config["db_url"] = config["db_url"]


@app.route("/")
def index():
    ticker_getter = TickerGetter(app.config["db_url"])
    ticks = ticker_getter.get_ticker(app.config["ticker"])
    return render_template('ticks.html.j2', ticks=ticks)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
