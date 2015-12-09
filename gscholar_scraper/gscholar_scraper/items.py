# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import urllib2
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose
from models import DeclarativeBase
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class GScholarItem(scrapy.Item):
    # updated_at = scrapy.Field()
    pass

def fix_string(input):
    """ Fixes URL-encoded UTF-8 strings which are then again as UTF-8 in the html source
    :param input: input strings to clean
    :return: clean input strings in unicode
    """
    return map(lambda s : urllib2.unquote(s.encode('ASCII')).decode('utf-8'), input)


class FOSItem(GScholarItem):
    """ One field-of-study item.
    """
    field_name = scrapy.Field(input_processor=fix_string)

class AuthorGenItem(GScholarItem):
    # general author info, when searched with label:biology e.g.

    class Model(DeclarativeBase):
        """Sqlalchemy authors model"""
        __tablename__ = "authors"

        id = Column(String, primary_key=True)
        fos = Column('fields_of_study', postgresql.ARRAY(String), nullable=True)
        name = Column(String)
        cited = Column(Integer, nullable=True)

    model_class = Model

    id = scrapy.Field(output_processor=TakeFirst())
    fos = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    cited = scrapy.Field(output_processor=TakeFirst())


class AuthorDetItem(GScholarItem):
    #more detailed author info, scraped from author profiles

    # TODO how to integrate these fields into the above authors model...
    measures = scrapy.Field()
    org = scrapy.Field()
    hasCo = scrapy.Field()


class DocItem(GScholarItem):

    class Model(DeclarativeBase):
        __tablename__ = "documents"
        author_id = Column(String)
        title = Column(String)
        id = Column(String, primary_key=True)
        cite_count = Column(Integer, nullable=True)
        year = Column(Integer)

    model_class = Model

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
    sqlite_keys = [["name"]]
    # Name of the category
    name = scrapy.Field()
    # Sub-categories (we will use a dict here)
    subs = scrapy.Field()

class SubCategoryItem(GScholarItem):
    sqlite_keys = [["name"]]
    # Name of the sub-category
    name = scrapy.Field()
    # parent category name
    parent = scrapy.Field()
    # vq code in request parameter
    code = scrapy.Field()
    # top 20 list of publications listed on google scholar
    # will be a list for now
    publications = scrapy.Field()
