import scrapy
import re
from author import items as t
from scrapy.http import Request

class AuthorSpider(scrapy.Spider):
    name = "authorSpider"
    start_urls = ['https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors=Mathias']

    def parse(self, response):
        # for each author ID on the page,create a new authorItem
        for ids in response.xpath('//*[@id="gsc_ccl"]/div/div/h3/a'):
            full = ids.xpath('@href').extract_first()# to-do: simplify to one regex
            tmp = re.search('user=(.*)&hl', full).group(1)
            if tmp:
                item = t.AuthorItem()
                item['authorID'] = tmp
                yield item

        # generate  next url
        new1 = response.xpath('//*[@id="gsc_authors_bottom_pag"]/span/button[2]').extract_first()
        new2 = re.search('mauthors(.*)\'"', new1)
        if new2:
            newUrl = str(new2.group(1)).replace('\\x3d','=').replace('\\x26', '&')
            newUrl = 'https://scholar.google.de/citations?view_op=search_authors&hl=de&mauthors' + newUrl
            yield Request(newUrl, self.parse)




