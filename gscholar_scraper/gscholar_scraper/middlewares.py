import random
from scrapy.conf import settings
from scrapy import log

from stem import Signal
from stem.control import Controller

class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)
            #this is just to check which user agent is being used for request
            # spider.log(
            #     u'User-Agent: {} {}'.format(request.headers.get('User-Agent'), request),
            #     level=log.DEBUG
            # )


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')


class RenewTorConnectionMiddleware(object):
    def process_spider_input(self, response, spider):
        if response.status != 200:
            spider.logger.error("Got response status %s " % response.status)

            # TODO request new identity from tor

    @classmethod
    def renew_connection(cls):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password = '')
