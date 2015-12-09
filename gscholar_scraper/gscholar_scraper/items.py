# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import urllib2
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose
from models import DeclarativeBase
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.dialects import postgresql


class GScholarItem(scrapy.Item):
    pass


def fix_string(input):
    """ Fixes URL-encoded UTF-8 strings which are then again as UTF-8 in the html source
    :param input: input strings to clean
    :return: clean input strings in unicode
    """
    return map(lambda s : urllib2.unquote(s.encode('ASCII')).decode('utf-8'), input)


class FOSItem(GScholarItem):
    """One field-of-study item."""

    class Model(DeclarativeBase):
        __tablename__ = 'labels'
        field_name = Column(String, primary_key=True)

    field_name = scrapy.Field(input_processor=fix_string, output_processor=TakeFirst())


class AuthorItem(GScholarItem):


    class Model(DeclarativeBase):
        """Sqlalchemy authors model"""
        __tablename__ = "authors"

        id = Column(String, primary_key=True)
        name = Column(String)

        fos = Column('fields_of_study', postgresql.ARRAY(String), nullable=True)
        cited = Column(Integer, nullable=True)
        measures = Column(postgresql.ARRAY(Integer), nullable=True)
        org = Column(String, nullable=True)
        hasCo = Column(Boolean, nullable=True)

    # general author info, when searched with label:biology e.g.
    id = scrapy.Field(output_processor=TakeFirst())
    fos = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    cited = scrapy.Field(output_processor=TakeFirst())

    # more detailed author info, scraped from author profiles
    measures = scrapy.Field(input_processor=MapCompose(lambda s: int(s)))
    org = scrapy.Field(output_processor=TakeFirst())
    hasCo = scrapy.Field(output_processor=TakeFirst())


class DocItem(GScholarItem):

    class Model(DeclarativeBase):
        __tablename__ = "documents"
        author_id = Column(String)
        title = Column(String)
        id = Column(String, primary_key=True)
        cite_count = Column(Integer, nullable=True)
        year = Column(Integer)

    author_id = scrapy.Field(
        output_processor = TakeFirst()
    )
    title = scrapy.Field(
        output_processor = TakeFirst()
    )
    id = scrapy.Field(
        input_processor = MapCompose(lambda i: i.split(':')[-1]),
        output_processor = TakeFirst()
    )
    cite_count = scrapy.Field(
        input_processor = MapCompose(lambda i : i.strip()),
        output_processor = TakeFirst())
    year = scrapy.Field(
        output_processor = TakeFirst()
    )


class CategoryItem(GScholarItem):

    # Name of the category
    name = scrapy.Field()
    # Sub-categories (we will use a dict here)
    subs = scrapy.Field()

class SubCategoryItem(GScholarItem):

    # Name of the sub-category
    name = scrapy.Field()
    # parent category name
    parent = scrapy.Field()
    # vq code in request parameter
    code = scrapy.Field()
    # top 20 list of publications listed on google scholar
    # will be a list for now
    publications = scrapy.Field()
