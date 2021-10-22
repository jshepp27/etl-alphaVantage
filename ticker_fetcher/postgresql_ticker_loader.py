import sqlalchemy


class PostgresqlTickerLoader:
    def __init__(self, db_url):
        self._db_url = db_url
        if self._db_url.startswith("postgres://"):
            self._db_url = self.db_url.replace("postgres://", "postgresql://", 1)
        self._engine = sqlalchemy.create_engine(db_url)
        self._metadata = sqlalchemy.MetaData()
        self._connection = self._engine.connect()
        self._tables = {}

    def _table_name(self, symbol):
        return f"{symbol}-tx-daily"

    def _has_table(self, tableName):
        sqlalchemy.inspect(self._engine).has_table(tableName)

    # TODO pass Schema as input var
    # TODO why is CreateTable function required for incremental tx == reliant on the table object
    def _create_table(self, symbol):
        if symbol not in self._tables:
            table_name = self._table_name(symbol)
            table = sqlalchemy.Table(table_name, self._metadata,
                                     sqlalchemy.Column('Date', sqlalchemy.String, primary_key=True),
                                     sqlalchemy.Column('Ticker', sqlalchemy.String, primary_key=True),
                                     sqlalchemy.Column('Open', sqlalchemy.Numeric),
                                     sqlalchemy.Column('High', sqlalchemy.Numeric),
                                     sqlalchemy.Column('Low', sqlalchemy.Numeric),
                                     sqlalchemy.Column('Close', sqlalchemy.Numeric),
                                     sqlalchemy.Column('Volume', sqlalchemy.Numeric))
            if not self._has_table(table_name):
                self._metadata.create_all(self._engine)
                print("DB Tables: \n", self._engine.table_names())
            self._tables[symbol] = table
        return self._tables[symbol]

    def load(self, ts, symbol):
        table = self._create_table(symbol)
        table_name = self._table_name(symbol)
        ts.to_sql(name=table_name, con=self._connection, if_exists="replace", index=False)
        results = self._connection.execute(sqlalchemy.select([table])).fetchall()

        print(f"Migrated Set of Daily Transactions: \n")
        count = 0
        for i in results:
            print(f"{i.Date}, {i.Close}")
            count += 1
        print("# Transactions:", count)
