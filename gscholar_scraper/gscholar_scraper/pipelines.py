# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import items
from sqlalchemy.orm import sessionmaker
from models import db_connect, create_authors_table

# we set the default values in this pipeline step
class DefaultValuesForItem(object):
    def process_item(self, item, spider):
        # if isinstance(item, items.GScholarItem):
        #     item.setdefault('updated_at', ctime())
        return item

class GscholarScraperPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, items.CategoryItem) or isinstance(item, items.SubCategoryItem):
            spider.logger.info('Got GScholarItem <%s> with name <%s>' % (type(item).__name__, item['name']))
        return item

class DatabaseSavingPipeline(object):
    def __init__(self):
        """
        :return: Init database and sessionmaker. Create tables.
        """
        engine = db_connect()
        create_authors_table(engine)
        self.Session = sessionmaker(bind=engine)

    # TODO batched insert for same items...

    def process_item(self, item, spider):
        """ Save items in the database.
        :param item: item to save
        :param spider: spider that crawled the item
        :return: saved item
        """
        session = self.Session()
        db_item = None
        if hasattr(item, 'Model'):
            db_item = item.Model(**item)

        try:
            session.merge(db_item)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item
