# Define here the models for your Spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/Spider-middleware.html


from scrapy import signals,Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from urllib.parse import urlparse

class CrawlersystemSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the Spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your Spiders.
        s = cls()
        crawler.signals.connect(s.Spider_opened, signal=signals.Spider_opened)
        return s

    def process_Spider_input(self, response, Spider):
        # Called for each response that goes through the Spider
        # middleware and into the Spider.

        # Should return None or raise an exception.
        return None

    def process_Spider_output(self, response, result, Spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_Spider_exception(self, response, exception, Spider):
        # Called when a Spider or process_Spider_input() method
        # (from other Spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, Spider):
        # Called with the start requests of the Spider, and works
        # similarly to the process_Spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def Spider_opened(self, Spider):
        Spider.logger.info('Spider opened: %s' % Spider.name)


class CrawlersystemDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your Spiders.
        s = cls()
        crawler.signals.connect(s.Spider_opened, signal=signals.Spider_opened)
        return s

    def process_request(self, request, Spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, Spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, Spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def Spider_opened(self, Spider):
        Spider.logger.info('Spider opened: %s' % Spider.name)

class QQNewsRedirectDownloaderMiddleware:
    def process_request(self, request, spider):
        url=urlparse(request.url)
        if url.path=='/notfound.htm':
            req=url.query.split('=')[1]
            req=req.split('?')[0]
            req=req.split('/')[-1]
            req_url='https://new.qq.com/rain/a/'+req
            return Request(req_url,callback=spider.parse_content)
