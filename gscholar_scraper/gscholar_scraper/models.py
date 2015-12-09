from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.engine.url import URL
from sqlalchemy import func

import settings


class TimestampedBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


DeclarativeBase = declarative_base(cls=TimestampedBase)


def db_connect():
    """ Performs database connection using database settings from settings.py.
    :return: sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_authors_table(engine):
    DeclarativeBase.metadata.create_all(engine)




