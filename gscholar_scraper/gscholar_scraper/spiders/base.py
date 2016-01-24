import scrapy
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from gscholar_scraper.database import db_settings


class DBConnectedSpider(scrapy.Spider):

    def __init__(self, *a, **kw):
        super(DBConnectedSpider, self).__init__(*a, **kw)

    def create_session(self):
        settings = get_project_settings()
        self.engine = create_engine(URL(**db_settings(settings)))
        self.sessionmaker = sessionmaker(bind=self.engine)
        return self.sessionmaker()

# self.engine = create_engine(URL(**self.db_settings))
# self.sessionmaker = sessionmaker(bind=self.engine)
#
# @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#                 db_connection(crawler)
#             )
#
#     def open_spider(self, spider):
#         self.engine = create_engine(URL(**self.db_settings))
#         DeclarativeBase.metadata.create_all(self.engine)
#
#         self.sessionmaker = sessionmaker(bind=self.engine)
#         spider.logger.info('Created sessionmaker for database %s' % self.db_settings.get('database'))
#
#     def close_spider(self, spider):
#         self.engine.dispose()
