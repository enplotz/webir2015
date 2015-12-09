import scrapy
import re
from gscholar_scraper.items import FOSItem, AuthorItem
from scrapy.http import Request
from scrapy.loader import ItemLoader
import gscholar_scraper.utils as utils
from models import db_connect, windowed_query, column_windows
from sqlalchemy.orm import sessionmaker
import random
import urllib2


def all_fields():
    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        for window in windowed_query(session.query(FOSItem.Model), FOSItem.Model.field_name, 1000):
            yield window
    finally:
        session.close()

class AuthorLabels(scrapy.Spider):
    name = "author_general"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    # use &hl=de parameter for appropiate citecount pattern
    pattern = 'https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors=label:{0}'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # fields from the database
        self.fields = all_fields()
        # appended urls from pagination
        self.container = []

        # select a field to start at
        if self.fields:
            start_label = self.fields.next().field_name
            print 'starting with label %s ' % start_label
            enc = urllib2.quote(start_label.encode('utf-8')).encode('ASCII')
            self.start_urls = [self.pattern.format(enc)]

    def next_label_from_db(self):
        next_label = next(self.fields, None)
        if not next_label:
            return None
        enc = urllib2.quote(next_label.field_name.encode('utf-8')).encode('ASCII')
        self.logger.debug('Choosing existing label %s.' % enc)
        return self.pattern.format(enc)

    def choose_next(self):
        if random.random() > 0.5:
            if len(self.container) == 0:
                l = self.next_label_from_db()
                return l
            else:
                u = utils.pop_random(self.container)
                self.logger.debug('Choosing existing url %s.' % u)
                return u
        else:
            next_url = self.next_label_from_db()
            if next_url:
                return next_url

            next_url = utils.pop_random(self.container)
            self.logger.debug('Choosing existing url %s.' % next_url)
            return next_url

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
                item = ItemLoader(item=AuthorItem(), response=response)
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

        # proceed with another random url or label to randomize access pattern to gscholar
        next_url = self.choose_next()

        if next_url:
            yield Request(url=next_url)


