from sqlalchemy import (create_engine, MetaData, Table, Column, String, insert, select,
                        Integer, Numeric, Boolean, insert, delete, text, and_)

import requests
import pandas as pd

# TODO Write as a Package
# Config Passwords
# TODO Schedule with AirFlow
# TODO Deploy to Heroku

TICKER = "DRDR"
db_url = "postgresql://huylpljjnoshbe:b51e90b80991f8e32ed4399a04c6db2a837f803995392e79472d1b92110ac60b@ec2-34-250-16-127.eu-west-1.compute.amazonaws.com:5432/dc7g7o62up02ai"

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

if __name__ == "__main__":
    ts = extract()
    print(ts)
    db = Db("DRDR", db_url)
    db.connect()
    db.create_table()
    db.add_migration(ts)
