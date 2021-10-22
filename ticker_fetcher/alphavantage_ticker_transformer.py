import pandas as pd

from .ticker_transformer import TickerTransformer


class AlphavantageTickerTransformer(TickerTransformer):
    def transform(self, data, symbol):
        ts_df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")

        ts_df.columns = ["Open", "High", "Low", "Close", "Volume"]
        ts_df.insert(0, "Ticker", symbol)
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

