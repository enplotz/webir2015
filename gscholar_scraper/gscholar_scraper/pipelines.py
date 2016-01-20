# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from items import DeclarativeBase

DB_HOST = 'SCRAPY_DB_HOST'
DB_PORT = 'SCRAPY_DB_PORT'
DB_USERNAME = 'SCRAPY_DB_USERNAME'
DB_PASSWORD = 'SCRAPY_DB_PASSWORD'
DB_DATABASE = 'SCRAPY_DB_DATABASE'

def db_connection(settings):
    """Returns the Postgres database connection. It reads the credentials
    from environment variables or crawler settings (env vars preferred).
    """
    return {
                    'drivername' : 'postgres',
                    'host' : environ.get(DB_HOST, settings.get(DB_HOST, default='localhost')),
                    'port' : environ.get(DB_PORT, settings.get(DB_PORT, default='5432')),
                    'username' : environ.get(DB_USERNAME, settings.get(DB_USERNAME, default='postgres')),
                    'password' : environ.get(DB_PASSWORD, settings.get(DB_PASSWORD, default='postgres')),
                    'database' : environ.get(DB_DATABASE, settings.get(DB_DATABASE, default='postgres')),
    }

class EchoDBSettingsPipeline(object):
    def __init__(self, database_settings):
        self.db_settings = database_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                db_connection(crawler)
            )

    def open_spider(self, spider):
        spider.logger.info('Configured database: %s' % self.db_settings)

    def process_item(self, item, spider):
        return item

class PostgresStoragePipeline(object):
    """A pipeline for storage of items to the database.
    """
    def __init__(self, database_settings):
        self.db_settings = database_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                db_connection(crawler.settings)
            )

    def open_spider(self, spider):
        self.engine = create_engine(URL(**self.db_settings))
        DeclarativeBase.metadata.create_all(self.engine)

        self.sessionmaker = sessionmaker(bind=self.engine)
        spider.logger.info('Created sessionmaker for database %s' % self.db_settings.get('database'))

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):

        session = self.sessionmaker()
        db_item = None
        if hasattr(item, 'Model'):
            db_item = item.Model(**item)

        try:
            session.merge(db_item)
            spider.logger.info('Storing model item %s' % db_item)
            session.commit()
        except Exception as e:
            spider.logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()
        return item

# we set the default values in this pipeline step
class DefaultValuesForItem(object):
    def process_item(self, item, spider):
        # if isinstance(item, items.GScholarItem):
        #     item.setdefault('updated_at', ctime())
        return item


# class DatabaseSavingPipeline(object):
#     def __init__(self):
#         """
#         :return: Init database and sessionmaker. Create tables.
#         """
#         engine = db_connect()
#         create_authors_table(engine)
#         self.Session = sessionmaker(bind=engine)
#
#     # TODO batched insert for same items...
#
#     def process_item(self, item, spider):
#         """ Save items in the database.
#         :param item: item to save
#         :param spider: spider that crawled the item
#         :return: saved item
#         """
#         session = self.Session()
#         db_item = None
#         if hasattr(item, 'Model'):
#             db_item = item.Model(**item)
#
#         try:
#             session.merge(db_item)
#             session.commit()
#         except:
#             session.rollback()
#             raise
#         finally:
#             session.close()
#         return item
