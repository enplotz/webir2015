import random, os, urllib2, time

from scrapy.conf import settings
from scrapy import log
from stem import Signal
from stem.control import Controller

IP_ENDPOINT = 'http://icanhazip.com/'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent' : user_agent}

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

            oldIP = RenewTorConnectionMiddleware.request(IP_ENDPOINT)
            RenewTorConnectionMiddleware.renew_connection()
            newIP = RenewTorConnectionMiddleware.request(IP_ENDPOINT)
            seconds = 0

            while oldIP == newIP:
                sleep = 2
                time.sleep(sleep)
                seconds += sleep
                newIP = RenewTorConnectionMiddleware.request(IP_ENDPOINT)
                spider.logger.info('%d seconds waiting for new IP address' % seconds)
            spider.logger.info('Got new IP: %s' % newIP)


    @classmethod
    def request(cls, url):
        def _set_urlproxy():
            proxy_support = urllib2.ProxyHandler(
                {'http':'{0}:{1}'.format(settings.get("HTTP_PROXY_HOST"), settings.get("HTTP_PROXY_PORT"))})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
        _set_urlproxy()
        request = urllib2.Request(url, None, headers)
        return urllib2.urlopen(request).read()


    @classmethod
    def renew_connection(cls):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password = os.getenviron.get("TOR_CONTROL_PASSWORD"))
            controller.signal(Signal.NEWNYM)

