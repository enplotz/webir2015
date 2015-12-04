import random, os, urllib2, time

from scrapy.conf import settings
from scrapy import log
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent

IP_ENDPOINT = 'http://icanhazip.com/'

ua = UserAgent()
ua.update()

class LoggerMiddleware(object):
    def process_request(self, request, spider):
        spider.logger.debug(u'User-Agent: {0} {1}'.format(request.headers['User-Agent'], request))


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

