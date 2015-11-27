# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GScholarItem(scrapy.Item):
    updated_at = scrapy.Field()


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
