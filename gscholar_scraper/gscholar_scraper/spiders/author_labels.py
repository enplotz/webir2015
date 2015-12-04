import scrapy
import re
import random
from gscholar_scraper.items import FOSItem
from scrapy.http import Request
from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
import gscholar_scraper.utils as utils

class AuthorLabels(scrapy.Spider):
    name = "authorLabels"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        with open('stops.txt', mode='r') as f:
            self.container = [i for i in f.readlines() if len(i) > 4]
        # select a random url to start at
        start = utils.pop_random(self.container)
        if start:
            self.start_urls = [start]
            # pass
        # self.start_urls = [ 'http://ozuma.sakura.ne.jp/httpstatus/302' ]

    def spider_closed(self, spider):
        f2 = open('stops.txt','wb')
        f2.write("\n".join(self.container))

    def parse(self, response):
        # for each author ID on the page,create a new authorItem
        for ids in response.xpath('//*[@id="gsc_ccl"]/div/div/div[@class="gsc_1usr_int"]'):
            full = ids.extract()
            #print tmp
            #full = ids.xpath('a/@href').extract_first()# to-do: simplify to one regex
            #id = re.search('user=(.*)&', tmp).group(1)
            fos = re.findall('=label:([^"]+)"', full)
            if fos:
                for f in fos:
                    it = ItemLoader(item=FOSItem(), response=response)
                    self.logger.debug(f)
                    it.add_value('field_name', f)
                    yield it.load_item()

        # generate  next url
        new1 = response.xpath('//*[@id="gsc_authors_bottom_pag"]/span/button[2]').extract_first()
        if new1:
            new2 = re.search('mauthors(.*)\'"', new1)
            if new2:
                newUrl = str(new2.group(1)).replace('\\x3d','=').replace('\\x26', '&')
                newUrl = 'https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors' + newUrl
                self.container.append(newUrl)
        # proceed with another random url to randomize access pattern to gscholar
        next = utils.pop_random(self.container)
        if next:
            yield Request(url=next)


