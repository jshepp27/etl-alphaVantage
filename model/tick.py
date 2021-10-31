from sqlalchemy import Column, Integer, Date, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Tick(Base):
    __tablename__ = "Ticks"
    date = Column(Date, primary_key=True)
    ticker: str = Column(String, primary_key=True)
    open: int = Column(Integer)
    high: int = Column(Integer)
    low: int = Column(Integer)
    close: int = Column(Integer)
    volume: int = Column(Integer)
