import scrapy
import re
import random
from gscholar_scraper import items as t
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import stem
import stem.connection
from stem import Signal
from stem.control import Controller

class AuthorLabels(scrapy.Spider):
    name = "authorLabels"
    handle_httpstatus_list = [404, 302]

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        f =open('stops.txt')
        self.container = f.readlines()
        self.container = [i for i in self.container if len(i)>4]

    def start_requests(self):
        if len(self.container) > 0:
            tmp = random.choice(self.container)
            self.container.remove(tmp)
            return [ Request(url = tmp)]

    def spider_closed(self, spider):
        f2 = open('stops.txt','wb')
        f2.write("\n".join(self.container))
        #self.controller.close()

    def parse(self, response):
        # for each author ID on the page,create a new authorItem
        for ids in response.xpath('//*[@id="gsc_ccl"]/div/div/div[@class="gsc_1usr_int"]'):
            full = ids.extract()
            #print tmp
            #full = ids.xpath('a/@href').extract_first()# to-do: simplify to one regex
            #id = re.search('user=(.*)&', tmp).group(1)
            fos = re.findall('=label:([^"]+)"', full)
            if fos:
                item = t.FOSItem()
                item['fos'] = fos
                yield item

        # generate  next url
        new1 = response.xpath('//*[@id="gsc_authors_bottom_pag"]/span/button[2]').extract_first()
        if new1:
            new2 = re.search('mauthors(.*)\'"', new1)
            if new2:
                newUrl = str(new2.group(1)).replace('\\x3d','=').replace('\\x26', '&')
                newUrl = 'https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors' + newUrl
                self.container.append(newUrl)
        yield self.start_requests()[0]


