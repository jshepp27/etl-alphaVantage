import logging
import sqlalchemy
import sqlalchemy.orm

from model import Tick, Base

logger = logging.getLogger(__name__)


class PostgresqlTickerLoader:
    def __init__(self, db_url):
        self._db_url = db_url
        if self._db_url.startswith("postgres://"):
            self._db_url = self._db_url.replace("postgres://", "postgresql://", 1)
        self._engine = sqlalchemy.create_engine(self._db_url, future=True)

    # Let the ORM manage the database table
    # def _table_name(self, symbol):
    #     return f"{symbol}-tx-daily"
    #
    # def _has_table(self, table_name):
    #     sqlalchemy.inspect(self._engine).has_table(table_name)
    #
    # # TODO pass Schema as input var
    # # TODO why is CreateTable function required for incremental tx == reliant on the table object
    # def _create_table(self, symbol):
    #     if symbol not in self._tables:
    #         table_name = self._table_name(symbol)
    #         table = sqlalchemy.Table(table_name, self._metadata,
    #                                  # sqlalchemy.Column('Date', sqlalchemy.String, primary_key=True),
    #                                  sqlalchemy.Column('Ticker', sqlalchemy.String, primary_key=True),
    #                                  sqlalchemy.Column('Open', sqlalchemy.Integer),
    #                                  sqlalchemy.Column('High', sqlalchemy.Integer),
    #                                  sqlalchemy.Column('Low', sqlalchemy.Integer),
    #                                  sqlalchemy.Column('Close', sqlalchemy.Integer),
    #                                  sqlalchemy.Column('Volume', sqlalchemy.Integer))
    #         if not self._has_table(table_name):
    #             self._metadata.create_all(self._engine)
    #             print("DB Tables: \n", self._engine.table_names())
    #         self._tables[symbol] = table
    #     return self._tables[symbol]

    def load(self, ticks, symbol):
        # This is the old code from when we were being given a data table
        # table = self._create_table(symbol)
        # table_name = self._table_name(symbol)
        # ts.to_sql(name=table_name, con=self._connection, if_exists="replace", index=False)

        # now we're being given a list of objects

        Base.metadata.create_all(self._engine)

        session = sqlalchemy.orm.Session(self._engine, future=True)
        for tick in ticks:
            session.merge(tick, load=True)
        session.commit()
        session.close()

        # results = self._connection.execute(sqlalchemy.select([table])).fetchall()

        session = sqlalchemy.orm.Session(self._engine, future=True)
        results = session.execute(
            sqlalchemy.select(Tick).where(Tick.ticker == symbol).order_by(Tick.ticker, Tick.date)).scalars().all()
        session.flush()
        session.close()

        logger.info(f"Received {len(results)} Daily Transactions for symbol {symbol}.")
        for i in results:
            logger.debug(f"{i.date}: {i.close / 10000}")
