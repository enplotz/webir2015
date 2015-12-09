import scrapy
import re
from gscholar_scraper.items import AuthorDetItem, DocItem
from scrapy.http import Request
from scrapy import signals
from scrapy.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
import gscholar_scraper.utils as utils

class AuthorDetails(scrapy.Spider):
    name = "authorsDetail"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        # with open('labels.txt', mode='r') as f:
        #    self.container = [i for i in f.readlines() if len(i) > 4]

        # author profiles with cstart and pagesize parameters
        self.container = ['https://scholar.google.de/citations?hl=de&user=TaJMF0EAAAAJ&cstart=0&pagesize=100']
        # select a random url to start at
        start = utils.pop_random(self.container)
        if start:
            self.start_urls = [start]
            # pass

    def spider_closed(self, spider):
        f2 = open('stops_detailed.txt','wb')
        f2.write("\n".join(self.container))

    def parse(self, response):

        # find 'cstart' in the given url
        oldStartTmp = re.search('&cstart=(\d+)&',response.url)
        oldStart = int(oldStartTmp.group(1))

        #crawl 'organisation id' and 'measurements' only at the first time, we look at that author profile
        if oldStart == 0:
                # measures has values for citetotal, cite2010, htotal, h2010, i10total, i2010
                measures = response.xpath('//td[@class="gsc_rsb_std"]/text()').extract()

                hasCoTmp = response.xpath('//div[@id="gsc_rsb_co"]').extract()

                hasCo = str(len(hasCoTmp)>0)
                # with another spider:
                #  crawl https://scholar.google.de/citations?view_op=list_colleagues&hl=de&user=F4P3ghEAAAAJ
                # for the users having hasCo true.

                orgtmp = response.xpath('//div[@class="gsc_prf_il"]').extract_first()
                orgtmp2 = re.search('org=(\d+)"', orgtmp)
                org = orgtmp2.group(1) if orgtmp2 else None
                #build detailed author item
                item = ItemLoader(item=AuthorDetItem(), response=response)
                item.add_value('measures', measures)
                item.add_value('org', org)
                item.add_value('hasCo', hasCo )
                yield item.load_item()


        # crawl the author's documents
        # return documents as quadruples (docid, docname, citecounts, years)
        # docid is the part in the following
        # /citations?view_op=view_citation&;hl=de&user=F4P3ghEAAAAJ&pagesize=100&citation_for_view=F4P3ghEAAAAJ:u5HHmVD_uO8C
        # to-do: id unique? same id, when document requested from another author's profile?

        authorID = re.search('&user=([^&]+)',response.url).group(1)

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
        next = utils.pop_random(self.container)
        if next:
            yield Request(url=next,dont_filter=True)


