# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    sqlite_keys = [["name"]]
    # Name of the category
    name = scrapy.Field()
    # Sub-categories (we will use a dict here)
    subs = scrapy.Field()
    last_updated = scrapy.Field()
