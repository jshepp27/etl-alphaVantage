from sqlalchemy import (create_engine, MetaData, Table, Column, String, select,
                        Numeric)

from flask import Flask
import requests
import pandas as pd
import config
import logging
import threading
import time

# TODO Logging (Python Logger) to Heroku, Observe logs
# TODO How to roll back Heroku
# TODO Assert Gunicorn Config
# TODO Complete Local Migration, Assert what Alembic can changes
# TODO Deploy to Heroku
# TODO Write as a Package
# TODO Schedule with AirFlow
# TODO Add a Front-end
# TODO Understand Config in Package context
# Implement Observability

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)


TICKER = "DRDR"

db_url = config.ProductionConfig.PROD_URI

# Extract (API)
def extract():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={TICKER}.LON&apikey=OMS1DTGJT1MEO1I9"

    r = requests.get(url)
    data = r.json()

    ts_df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")

    ts_df.columns = ["Open", "High", "Low", "Close", "Volume"]
    ts_df.insert(0, "Ticker", TICKER)
    ts_df = ts_df.iloc[::-1]

    ts_df["Open"] = ts_df["Open"].astype("float")
    ts_df["High"] = ts_df["High"].astype("float")
    ts_df["Low"] = ts_df["Low"].astype("float")
    ts_df["Close"] = ts_df["Close"].astype("float")
    ts_df["Volume"] = ts_df["Volume"].astype("float")

    date_copy = ts_df.index.copy()
    ts_df.insert(0, "Date", date_copy)
    ts_df["Date"] = ts_df["Date"].astype(str)

    return ts_df

# Transform

# Load
metadata = MetaData()
_tableName = f"{TICKER}-tx-daily"

class Db():

    def __init__(self, tableName, db_url):
        self.db_url = db_url
        self.connection = ""
        self.tableName = tableName
        self.table = ""
        self.engine = ""

    def connect(self):
        self.engine = create_engine(self.db_url)
        self.connection = self.engine.connect()

    # TODO pass Schema as input var
    # TODO why is CreateTable function required for incremental tx == reliant on the table object
    def create_table(self):
        self.table = Table(self.tableName, metadata,
                      Column('Date', String, primary_key=True),
                      Column('Ticker', String, primary_key=True),
                      Column('Open', Numeric),
                      Column('High', Numeric),
                      Column('Low', Numeric),
                      Column('Close', Numeric),
                      Column('Volume', Numeric))

        metadata.create_all(self.engine)
        print("DB Tables: \n", self.engine.table_names())

    def add_migration(self, ts):

        ts.to_sql(name=self.tableName, con=self.connection, if_exists="replace", index=False)

        results = self.connection.execute(select([self.table])).fetchall()

        print(f"Migrated Set of Daily Transactions: \n")

        count = 0
        for i in results:
            print(f"{i.Date}, {i.Close}")
            count += 1
        print("# Transactions:", count)

db = Db("DRDR", db_url)
db.connect()
db.create_table()
#app.logger.info("\n Db created ...")

def main():
    while True:
        time.sleep(10)
        ts = extract()
        logging.info(ts)
        db.add_migration(ts)

main()