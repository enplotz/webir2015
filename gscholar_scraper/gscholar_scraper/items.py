# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import urllib2
from scrapy.loader.processors import MapCompose


class GScholarItem(scrapy.Item):
    updated_at = scrapy.Field()

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
