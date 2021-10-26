import sqlalchemy
import sqlalchemy.orm

from model import Tick


class TickerGetter:
    """Responsible for retrieving ticks for a certain symbol from the datastore."""

    def __init__(self, db_url):
        self._db_url = db_url
        if self._db_url.startswith("postgres://"):
            self._db_url = self._db_url.replace("postgres://", "postgresql://", 1)
        self._engine = sqlalchemy.create_engine(self._db_url, future=True)

    def get_ticker(self, ticker):
        with sqlalchemy.orm.Session(bind=self._engine, future=True) as session:
            return session.execute(sqlalchemy.select(Tick).where(Tick.ticker == ticker).order_by(Tick.date.desc())).scalars().all()