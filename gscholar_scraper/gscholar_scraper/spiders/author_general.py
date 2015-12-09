import scrapy
import re
import random
from gscholar_scraper.items import AuthorGenItem
from scrapy.http import Request
from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
import gscholar_scraper.utils as utils

class AuthorLabels(scrapy.Spider):
    name = "authorsGeneral"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        # with open('labels.txt', mode='r') as f:
        #    self.container = [i for i in f.readlines() if len(i) > 4]

        # use &hl=de parameter for appropiate citecount pattern
        self.container = ['https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors=label:biology']
        # select a random url to start at
        start = utils.pop_random(self.container)
        if start:
            self.start_urls = [start]
            # pass
        # self.start_urls = [ 'http://ozuma.sakura.ne.jp/httpstatus/302' ]

    def spider_closed(self, spider):
        f2 = open('stops_general.txt','wb')
        f2.write("\n".join(self.container))

    def parse(self, response):
        # determine current search label
        tmp = re.search('(.)+mauthors=label:([^&]+)(&|)', response.url)
        currFOS = tmp.group(2)

        # get 10 author divs
        for divs in response.xpath('//*[@id="gsc_ccl"]/div')[0:9]:
            user = divs.extract()

            # Content in the img's alt tag is the actual name, shown on the profile
            # However, the name in the actual link differs sometimes slightly
            # EH Roberts (link) instead of E H Roberts (on profile + alt)

            id = re.search('citations\?user=([^&]+)(&|)',user)
            name = re.search('alt="([^"]+)"', user)
            citecount = re.search('<div class="gsc_1usr_cby">Zitiert von: ([0-9]+)</div>', user)
            if id and name:
                item = ItemLoader(item=AuthorGenItem(), response=response)
                item.add_value('fos', currFOS)
                item.add_value('id', id.group(1))
                item.add_value('name', name.group(1))

                # unknown citation count:
                cited = citecount.group(1) if citecount else None
                item.add_value('cited', cited)
                yield item.load_item()

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


