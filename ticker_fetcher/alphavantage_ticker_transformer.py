import pandas as pd

from model import Tick
from .ticker_transformer import TickerTransformer


class AlphavantageTickerTransformer(TickerTransformer):
    def _ticker_list(self, data):
        return [Tick(date=date, ticker=row['Ticker'], open=row['Open'], high=row['High'], low=row['Low'],
                     close=row['Close'], volume=row['Volume']) for date, row in data.iterrows()]

    def transform(self, data, symbol):
        ts_df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")

        ts_df.columns = ["Open", "High", "Low", "Close", "Volume"]
        ts_df.insert(0, "Ticker", symbol)
        ts_df = ts_df.iloc[::-1]

        # storing fixed decimal values as floats is very wasteful.

        # ts_df["Open"] = ts_df["Open"].astype("float")
        # ts_df["High"] = ts_df["High"].astype("float")
        # ts_df["Low"] = ts_df["Low"].astype("float")
        # ts_df["Close"] = ts_df["Close"].astype("float")
        # ts_df["Volume"] = ts_df["Volume"].astype("float")

        # as these are fixed at 4 decimal digits, if we multiply by 10000
        # we can store as an integer

        ts_df["Open"] = ts_df["Open"].str.replace('.', '', regex=False).astype("int")
        ts_df["High"] = ts_df["High"].str.replace('.', '', regex=False).astype("int")
        ts_df["Low"] = ts_df["Low"].str.replace('.', '', regex=False).astype("int")
        ts_df["Close"] = ts_df["Close"].str.replace('.', '', regex=False).astype("int")

        # volume was never a float
        ts_df["Volume"] = ts_df["Volume"].astype("int")

        # converting the date to a string is a display concern
        # date_copy = ts_df.index.copy()
        # ts_df.insert(0, "Date", date_copy)
        # ts_df["Date"] = ts_df["Date"].astype(str)

        # using a pandas dataframe as a transfer format forces the data layer to know about pandas, so
        # let's not do that.

        return self._ticker_list(ts_df)
