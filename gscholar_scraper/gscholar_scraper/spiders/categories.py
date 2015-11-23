# -*- coding: utf-8 -*-
import scrapy
from gscholar_scraper.items import CategoryItem
from urlparse import urlparse, parse_qs

class CategoriesSpider(scrapy.Spider):
    name = "categories"
    allowed_domains = ["scholar.google.com"]
    pat = 'https://scholar.google.com/citations?view_op=top_venues&hl=de&vq={0}'
    # The main categories on Google Scholar
    cat_codes = ('bus','bio','chm', 'hum', 'med', 'eng', 'phy', 'soc')

    start_urls = [pat.format(cat) for cat in cat_codes]

    def parse(self, response):
        """ This function parses the categories and its subcategories on a gscholar web page.

        @url https://scholar.google.com/citations?view_op=top_venues&hl=de&vq=bus
        @returns items 1 1
        @returns requests 0 0
        @scrapes name subs
        """
        # We need the div that is 'selected' i.e. contains gs_sel as a css class
        title_xp = '//*[@id="gs_m_broad"]/div[contains(@class,\'gs_sel\')]/a/span/text()'
        # We simply get all urls that are listed
        subs_xp = '//*[@id="gs_m_rbs"]/ul/li/a'
        item = CategoryItem()
        item['name'] = response.xpath(title_xp).extract_first()
        subs = []
        for sub in response.xpath(subs_xp):
            s = {'name' : sub.xpath('text()').extract_first()}
            text = sub.xpath('@href').extract_first()
            s['vb'] = parse_qs(urlparse(text).query)[u'vq'][0]
            subs.append(s)
        item['subs'] = subs
        yield item
