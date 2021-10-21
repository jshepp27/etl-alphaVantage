from sqlalchemy import (create_engine, MetaData, Table, Column, String, select,
                        Numeric)

from flask import Flask
import requests
import pandas as pd
import config
import logging
import time

# TODO Schedule with AirFlow
# TODO Observability

app = Flask(__name__)

# Send Logs to Gunicorn
gunicorn_logger = logging.getLogger('gunicorn.error')
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

# Globals
TICKER = "DRDR"
DB_URL = config.ProductionConfig.PROD_URI
TABLE_NAME = f"{TICKER}-tx-daily"
API_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={TICKER}.LON&apikey=OMS1DTGJT1MEO1I9"

# Extract (API)
def extract(url=API_URL):
    r = requests.get(url)
    data = r.json()

    return data

# Transform
def transform(ts):
    ts_df = pd.DataFrame.from_dict(ts["Time Series (Daily)"], orient="index")

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

# Load
# Init ORM
metadata = MetaData()

class Db():

    def __init__(self, tableName=TABLE_NAME, db_url=DB_URL):
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

# Init Db
db = Db("DRDR", DB_URL)
db.connect()
db.create_table()

def main():
    while True:
        time.sleep(15)
        ts = extract()
        ts = transform(ts)
        logging.info(ts)
        db.add_migration(ts)

# Gunicorn Entry Object
main()