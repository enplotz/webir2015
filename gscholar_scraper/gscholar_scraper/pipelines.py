# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import items

class GscholarScraperPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, items.GScholarItem):
            spider.logger.info('Got GScholarItem <%s> with name <%s>' % (type(item).__name__, item['name']))
        return item
