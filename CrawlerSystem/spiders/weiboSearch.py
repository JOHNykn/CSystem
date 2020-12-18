# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.response import open_in_browser

import re
from datetime import datetime, timedelta
from urllib.parse import unquote,urlparse

from CrawlerSystem.custom_settings import Weibo_custom_settings
from CrawlerSystem.items import WeiboItem
from CrawlerSystem.region import regionCodeDict

def setTimescope():
    date = datetime.today()
    end = date.strftime('%Y-%m-%d')
    start = (date - timedelta(days = 7)).strftime('%Y-%m-%d')
    return start, end

def get_a_day(start,end):
    startDateTime = datetime.strptime(start, '%Y-%m-%d')
    endDateTime = datetime.strptime(end, '%Y-%m-%d') + timedelta(days = 1)
    while startDateTime < endDateTime:
        start = startDateTime.strftime('%Y-%m-%d')
        startDateTime = startDateTime + timedelta(days = 1)
        end = startDateTime.strftime('%Y-%m-%d')
        yield(start + '-0',end + '-0')

class SearchSpider(scrapy.Spider):
    name = 'weiboSearch'
    allowed_domains = ['weibo.com']

    custom_settings = Weibo_custom_settings

    urlFormat='https://s.weibo.com/weibo?q={KEYWORD}&typeall=1&suball=1&timescope=custom:{START_DATE}:{END_DATE}'
    weiboId = set()
    region = regionCodeDict      #获取地区代码字典
    startDate, endDate = setTimescope()    #设置时间范围

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        spider.keyword_list = crawler.settings.get('KEYWORD_LIST')      #初始化关键词列表
        return spider

    def start_requests(self):
        #self.keyword_list = ['xz']      #测试用
        for keyword in self.keyword_list:
            url = self.urlFormat.format(KEYWORD = keyword, START_DATE = self.startDate, END_DATE = self.endDate)    #生成搜索URL
            yield scrapy.Request(url, callback=self.parse,
                                 cb_kwargs={
                                     'keyword': keyword,
                                     'search_range' : 'time'
                                     })

    def parse(self, response, keyword, search_range):
        is_empty = response.xpath('//div[@class="card card-no-result s-pt20b40"]')
        if is_empty:
            #open_in_browser(response)      #测试用
            self.logger.info('当前页面搜索结果为空,关键词：{},URL：{}'.format(keyword,response.url))
        else:
            for weibo in self.parse_weibo(response, keyword):
                yield {'content':weibo,'keyword':keyword}
            page_count = len(response.xpath('//ul[@class="s-scroll"]/li'))
            if page_count < 50:
                next_url = response.xpath('//a[@class="next"]/@href').get()
                if next_url:
                    yield response.follow(next_url, callback=self.parse,
                                          cb_kwargs={
                                              'keyword': keyword,
                                              'search_range' : search_range
                                              })
            else:
                yield from self.getMorePage(search_range, response.url, keyword)

    def getMorePage(self, search_range, ori_url, keyword):
        if search_range == 'time':      #以天为单位缩小搜索范围
            re_timescope = re.compile(r'timescope=custom:(.+):(.+)')
            try:
                startDate, endDate = re_timescope.findall(ori_url)[0]
            except IndexError:
                pass
            else:
                for start,end in get_a_day(startDate, endDate):
                    url = re_timescope.sub(r'timescope=custom:{}:{}'.format(start,end), ori_url)
                    yield scrapy.Request(url, callback=self.parse,
                                         cb_kwargs={
                                             'keyword': keyword,
                                             'search_range' : 'region'
                                             })

        elif search_range == 'region':      #以城市/地区为单位缩小搜索范围
            re_region = re.compile(r'region=custom:([\d]+):([\d]+)&')
            try:
                province, city = re_region.findall(ori_url)[0]
            except IndexError:
                re_keyword = re.compile(r'q=(.+)&')
                for provcode in self.region:
                    url = ori_url.replace('&typeall=1&suball=1','&region=custom:{}:1000'.format(provcode)+'&typeall=1&suball=1')
                    yield scrapy.Request(url, callback=self.parse,
                                         cb_kwargs={
                                             'keyword': keyword,
                                             'search_range' : 'region'
                                             })
            else:
                if city == '1000' and province != '100':
                    for citycode in self.region[province]:
                        url = re_region.sub(r'region=custom:{}:{}&'.format(province,citycode), ori_url)
                        yield scrapy.Request(url, callback=self.parse,
                                             cb_kwargs={
                                                 'keyword': keyword,
                                                 'search_range' : 'stop'
                                                 })


    def split_content(self,content):
        content_dict = {
            'text': None,
            'at_users': None,
            'topics': None,
            }
        content_dict['text'] = content
        at_users = re.compile(r'(?<!//)(@.*?)[\s]')
        topics = re.compile(r'#.*?#')
        content_dict['at_users'] = [ i for i in set(at_users.findall(content))]
        content_dict['topics'] = [ i for i in set(topics.findall(content))]
        return content_dict

    def split_footInfo(self,foot_Info):
        returned_value = []
        for i in foot_Info:
            if i.strip().startswith('转发'):
                returned_value.append(i.lstrip('转发 '))
            elif i.strip().startswith('评论'):
                returned_value.append(i.lstrip('评论 '))
        return returned_value

    def parse_weibo(self, response, keyword):        #解析网页中的微博信息
        #open_in_browser(response)
        for sel in response.xpath('//div[@mid]'):
            weibo = WeiboItem()
            weibo['id'] = sel.xpath('@mid').get()
            if weibo['id'] in self.weiboId:
                continue
            else:
                self.weiboId.add(weibo['id'])
                user = urlparse(sel.xpath('.//div[@class="content"]/p[@class="from"]/a/@href').get()).path.strip('/')
                weibo['authorId'],weibo['bid'] = user.split('/')
                weibo['author'] = sel.xpath('.//div[@class="content"]/div[@class="info"]//a[@class="name"]/@nick-name').get()

                feed_list_content_full = sel.xpath('string(.//p[@nick-name][@node-type="feed_list_content_full"])').get()
                if feed_list_content_full:
                    weibo_content = feed_list_content_full
                else:
                    weibo_content = sel.xpath('string(.//p[@nick-name][@node-type="feed_list_content"])').get()
                content_info = self.split_content(weibo_content)
                weibo['text'] = content_info['text']
                weibo['at_users'] = content_info['at_users']
                weibo['topics'] = content_info['topics']
            
                footInfo = sel.xpath('.//div[@class="card-act"]/ul//a/text()').getall()
                weibo['forwards'], weibo['comments'] = self.split_footInfo(footInfo)
                weibo['likes'] = sel.xpath('.//div[@class="card-act"]/ul//em/text()').get()
                weibo['pubTime'], *weibo['_from'] = sel.xpath('.//div[@class="content"]/p[@class="from"]/a/text()').getall()

                weibo['articleUrl'] = sel.xpath('.//div[@class="media media-article-a"]//h4/a/@href').get()
                weibo['picsUrl'] = sel.xpath('.//div[@class="media media-piclist"]/ul//img/@src').getall()
                weibo['videoUrl'] = sel.xpath('.//div[@class="thumbnail"]/a/@action-data').get()
                if weibo['videoUrl']:
                    weibo['videoUrl'] = unquote(weibo['videoUrl'].split('video_src=')[-1])

                weibo['repostId'] = '0'       #标记，该微博没有转发别的微博
                weibo['source'] = '微博搜索'

                retweet_sel = sel.xpath('.//div[@class="card-comment"]')        #获取被转发的微博
                if retweet_sel:
                    retweet = WeiboItem()
                    retweet['id'] = retweet_sel.xpath('.//a[@action-type="feed_list_like"]/@action-data').get()[4:]
                    if retweet['id'] in self.weiboId:       #微博去重
                        continue
                    else:
                        self.weiboId.add(retweet['id'])
                        user = urlparse(retweet_sel.xpath('.//p[@class="from"]/a/@href').get()).path.strip('/')
                        try:
                            retweet['authorId'], retweet['bid'] = user.split('/')
                        except ValueError:
                            yield weibo         #被转发的微博已删除，直接返回原微博
                        retweet['author'] = retweet_sel.xpath('.//div[@node-type="feed_list_forwardContent"]/a/@nick-name').get()

                        feed_list_content_full = retweet_sel.xpath('string(.//p[@node-type="feed_list_content"])').get()
                        if feed_list_content_full:
                            weibo_content = feed_list_content_full
                        else:
                            weibo_content = retweet_sel.xpath('string(.//p[@node-type="feed_list_content_full"])').get()
                        content_info = self.split_content(weibo_content)
                        retweet['text'] = content_info['text']
                        retweet['at_users'] = content_info['at_users']
                        retweet['topics'] = content_info['topics']

                        footInfo = retweet_sel.xpath('.//div[@class="func"]/ul//a/text()').getall()
                        retweet['forwards'], retweet['comments'] = self.split_footInfo(footInfo)
                        retweet['likes'] = retweet_sel.xpath('.//div[@class="func"]/ul//em/text()').get()
                        retweet['pubTime'], *retweet['_from'] = retweet_sel.xpath('.//p[@class="from"]/a/text()').getall()

                        retweet['articleUrl'] = retweet_sel.xpath('.//div[@class="media media-article-a"]//h4/a/@href').get()
                        retweet['picsUrl'] = retweet_sel.xpath('.//div[@class="media media-piclist"]/ul//img/@src').getall()
                        retweet['videoUrl'] = retweet_sel.xpath('.//div[@class="thumbnail"]/a/@action-data').get()
                        if retweet['videoUrl']:
                            retweet['videoUrl'] = unquote(retweet['videoUrl'].split('video_src=')[-1])

                        retweet['repostId'] = '1'     #标记，被转发微博
                        retweet['source'] = '微博搜索'
                        weibo['repostId'] = retweet['id']
                        yield retweet
            yield weibo
