import scrapy
import re
from gscholar_scraper.items import AuthorItem, DocItem
from scrapy.http import Request
from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
import gscholar_scraper.utils as utils
import urllib2
from models import db_connect, windowed_query, column_windows
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy import or_
import random

def missing_authors():
    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        q = session.query(AuthorItem.Model).filter(or_(AuthorItem.Model.measures == None, AuthorItem.Model.org == None, AuthorItem.Model.hasCo == None))
        for window in windowed_query(q, AuthorItem.Model.id, 1000):
            yield window
    finally:
        session.close()

class AuthorDetails(scrapy.Spider):
    name = "author_detail"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    pattern = 'https://scholar.google.de/citations?hl=de&user={0}&cstart=0&pagesize=100'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.missing_authors = missing_authors()
        # author profiles with cstart and pagesize parameters
        self.container = []
        # select a random url to start at

        if self.missing_authors:
            start_author = self.missing_authors.next()
            print 'starting with author %s' % start_author.name
            self.start_urls = [self.pattern.format(start_author.id)]

    def next_author_from_db(self):
        next_author = next(self.missing_authors, None)
        if not next_author:
            return None
        self.logger.debug('Choosing existing label %s.' % next_author.name)
        return self.pattern.format(next_author.id)

    def choose_next(self):
        if random.random() > 0.5:
            if len(self.container) == 0:
                l = self.next_author_from_db()
                return l
            else:
                u = utils.pop_random(self.container)
                self.logger.debug('Choosing existing url %s.' % u)
                return u
        else:
            next_author = self.next_author_from_db()
            if next_author:
                return next_author

            next_author = utils.pop_random(self.container)
            self.logger.debug('Choosing existing url %s.' % next_author)
            return next_author

    def parse(self, response):

        # Pagination parameters
        oldStart = int(re.search('&cstart=(\d+)&', response.url).group(1))

        authorID = re.search('&user=([^&]+)',response.url).group(1)

        authorItem = AuthorItem()
        authorItem['id'] = authorID

        #crawl 'organisation id' and 'measurements' only at the first time, we look at that author profile
        if oldStart == 0:
            # measures has values for citetotal, cite2010, htotal, h2010, i10total, i2010

            # check if the author has any coauthors listed
            hasCo = str(len(response.xpath('//div[@id="gsc_rsb_co"]').extract()) > 0)
            # can be crawled with another spider:
            #  crawl https://scholar.google.de/citations?view_op=list_colleagues&hl=de&user=F4P3ghEAAAAJ
            # for the users having hasCo true.

            orgMatch = re.search('org=(\d+)"', response.xpath('//div[@class="gsc_prf_il"]').extract_first())
            org = orgMatch.group(1) if orgMatch else None

            # build detailed author item
            item = ItemLoader(item=authorItem, response=response)
            # name required
            item.add_xpath('name', '//*[@id="gsc_prf_in"]/text()')
            item.add_xpath('measures', '//td[@class="gsc_rsb_std"]/text()')
            item.add_value('org', org)
            item.add_value('hasCo', hasCo)
            yield item.load_item()


        # crawl the author's documents
        # return documents as quadruples (docid, docname, citecounts, years)
        # docid is the part in the following
        # /citations?view_op=view_citation&;hl=de&user=F4P3ghEAAAAJ&pagesize=100&citation_for_view=F4P3ghEAAAAJ:u5HHmVD_uO8C
        # to-do: id unique? same id, when document requested from another author's profile?

        # Prepare document item with authors id for reuse
        doc_item = DocItem()
        doc_item['author_id'] = authorID

        # Publication items for the author
        for doc in response.xpath('//*[@class="gsc_a_tr"]'):
            il = ItemLoader(item=doc_item, selector=doc, response=response)
            il.add_xpath('title', './td[@class="gsc_a_t"]/a/text()')
            il.add_xpath('id', './td[@class="gsc_a_t"]/a/@href')
            il.add_xpath('cite_count', './td[@class="gsc_a_c"]/a/text()')
            il.add_xpath('year', './td[@class="gsc_a_y"]//text()')
            yield il.load_item()

        # btn for next documents:
        btnEnabled = response.xpath('//button[@id="gsc_bpf_next" and not(contains(@class ,"gs_dis"))]').extract_first()
        if btnEnabled:
            # there are more documents to crawl for this author!
            # build the next url on our own, as Google solves it in its JS and does not explicitly
            # include the url in the html code

            # generate next url
            newStartTmp = oldStart + 100
            newStart2 = 'cstart='+str(newStartTmp)
            newUrl = response.url.replace('cstart='+str(oldStart), newStart2 )


            self.container.append(newUrl)

        # proceed with another random url to randomize access pattern to gscholar
        next_url = self.choose_next()

        if next_url:
            yield Request(url=next_url)#, dont_filter=True)


