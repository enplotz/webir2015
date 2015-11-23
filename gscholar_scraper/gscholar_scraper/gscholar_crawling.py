from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from spiders.categories import CategoriesSpider

configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
runner = CrawlerRunner()

# add spiders here
runner.crawl(CategoriesSpider)


d = runner.join()
d.addBoth(lambda _ : reactor.stop())

reactor.run() # block here until all jobs are finished
