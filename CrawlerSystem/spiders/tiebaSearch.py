import scrapy 
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import TiebaThreadItem, TiebaPostItem, TiebaCommentItem
from CrawlerSystem.custom_settings import Tieba_custom_settings

from urllib import parse
import json
from datetime import datetime
from math import ceil

class Tieba_Search(scrapy.Spider):
    name = 'tiebaSearch'
    allowed_damains = ['tieba.baidu.com']
    custom_settings = Tieba_custom_settings

    by_time =  'https://tieba.baidu.com/f/search/res?ie=utf-8&qw={}&pn=0&sm=1'      
    by_relevance = 'https://tieba.baidu.com/f/search/res?ie=utf-8&qw={}&pn=0&sm=2'
    only_thread = 'https://tieba.baidu.com/f/search/res?ie=utf-8&qw={}&pn=0&sm=1&only_thread=1'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        spider.keyword_list = crawler.settings.get('KEYWORD_LIST')
        return spider

    def start_requests(self):
        for keyword in self.keyword_list:
            yield scrapy.Request(self.by_time.format(keyword), callback=self.parse, cb_kwargs={'keyword': keyword})          #按时间倒序  
            yield scrapy.Request(self.by_relevance.format(keyword), callback=self.parse, cb_kwargs={'keyword': keyword})     #按相关性顺序
            yield scrapy.Request(self.only_thread.format(keyword), callback=self.parse, cb_kwargs={'keyword': keyword})      #只看主题贴
     
    def parse(self, response, keyword):
        threads = response.xpath('//div[@class="s_post"]//a[@class="bluelink"]/@href').getall()
        for thread in threads:
            url = 'https://tieba.baidu.com{}?pn=1'.format(thread.split('?')[0])
            yield scrapy.Request(url, callback=self.parse_post, cb_kwargs={'keyword': keyword})

    def parse_post(self, response, keyword):            #解析回帖的内容
        argu = response.request.url.split('/')[-1]      #request评论所需参数
        threadId = argu.split('?')[0]                   #帖子id
        pn = argu.split('?')[-1]                        #当前页数     
        Posts = response.xpath('//div[contains(@class, "l_post")]')
        if Posts:
            for post in Posts:
                item = TiebaPostItem()
                data = json.loads(post.xpath("@data-field").get())
                item['postId'] = data['content']['post_id']
                item['text'] = post.xpath('string(.//cc/div[contains(@class,"d_post_content")])').get()
                try:
                    item['authorId'] = data['author']['user_id']
                except KeyError:
                    item['authorId'] = json.loads(post.xpath('.//li[@class="d_name"]/@data-field').get())['user_id']
                item['author'] = data['author']['user_name']
                item['comments'] = data['content']['comment_num']
                item['threadId'] = threadId
                item['picsUrl'] = post.xpath('.//cc//img/@src').getall()
                if 'date' in data['content'].keys():            #仅旧帖子data-field中有日期
                    item['pubTime'] = data['content']['date']
                else:
                    item['pubTime'] = post.xpath('.//div[@class="post-tail-wrap"]/span[last()]/text()').get()
                item['floor'] = data['content']['post_no']
                item['source'] = '贴吧搜索'
                yield {'content':item,'type': 'Post','keyword':keyword}
                
                if data['content']['comment_num'] > 0:
                    postId = data['content']['post_id']
                    url = 'https://tieba.baidu.com/p/comment?tid={}&pid={}&pn=1'.format(threadId, postId)
                    yield scrapy.Request(url, callback = self.parse_comment, cb_kwargs={'postId': postId})         

            next_page = response.xpath('//ul[@class="l_posts_num"]//a[string(.)="下一页"]/@href').get()
            if next_page:
                yield response.follow(next_page, callback = self.parse_post, cb_kwargs={'keyword': keyword})        #帖子翻页


    def parse_comment(self, response, postId):
        comments_list = response.xpath('//li[contains(@class,"lzl_single_post")]')
        for comment in comments_list:
            data = json.loads(comment.attrib['data-field'])
            item = TiebaCommentItem()
            item['commentId'] = data['spid']
            item['text'] = comment.xpath('string(.//span[@class="lzl_content_main"])').get()
            item['author'] = data['user_name']
            item['postId'] = postId
            item['pubTime'] = comment.xpath('.//span[@class="lzl_time"]/text()').get()
            item['source'] = '贴吧搜索'
            yield {'content':item,'type': 'Comment'}

        next_page = response.xpath('//p[@class="j_pager l_pager pager_theme_2"]/a[contains(text(),"下一页")]/@href').get()
        if next_page:
            url = response.url[:-1] + next_page[-1]
            yield scrapy.Request(url, callback=self.parse_comment, cb_kwargs={'postId': postId})
