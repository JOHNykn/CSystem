import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import NewsArticleItem, NewsCommentItem
from CrawlerSystem.custom_settings import News_custom_settings

import re
import os
import logging
from time import time

class Sohu_News(CrawlSpider):
    name = 'sohu'
    allowed_domains = ['sohu.com']
    #启用新闻pipeline
    custom_settings = News_custom_settings

    rules = [
        Rule(LinkExtractor(r'https://www.sohu.com/a/[\d_]+[?]?'), callback='parse_content'),
        Rule(LinkExtractor(r'https://www.sohu.com/picture/[\d_]+[?]?'), callback='parse_picture')
        ]

    def start_requests(self):
        filepath=os.path.join('start_urls','sohu_start.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            for url in urls:
                yield scrapy.Request(url)       #腾讯新闻首页所有内容
        
        filepath=os.path.join('start_urls','sohu_ajax.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            timestamp = str(time())
            for url in urls:
                url = url.replace('TIMESTAMP',timestamp)
                yield scrapy.Request(url,callback=self.parse_ajax)

    def parse_ajax(self,response):
        ajax_data = response.json()
        if isinstance(ajax_data,dict):
            _,value = ajax_data.popitem()
            resourceData = value['data']
            for news in resourceData:
                try:
                    url = news['resourceData']['contentData']['url']
                except KeyError:
                    url = news['backupContent']['resourceData']['contentData']['url']
                if not url.startswith('http'):
                    url += 'https://www.sohu.com'
                yield scrapy.Request(url,callback = self.parse_content)
        elif isinstance(ajax_data,list):
            urlFormat = 'https://www.sohu.com/a/{id}_{authorId}'
            for news in ajax_data:
                url = urlFormat.format(id = news['id'],authorId = news['authorId'])
                yield scrapy.Request(url,callback = self.parse_content)

    def parse_content(self,response):           #解析新闻详细内容
        item = NewsArticleItem()
        item['title'] = response.xpath('string(//h1)').get()
        item['text'] = response.xpath('//article[@id="mp-editor"]//p//text()').getall()
        item['author'] = response.xpath('//span[@data-role="original-link"]/a/text()').get()
        item['pubTime'] = response.xpath('//span[@id="news-time"]/text()').get()
        id = response.url.split('/')[-1]
        item['id'] = id.split('_')[0]
        item['authorId'] = re.findall(r'media_id: "([\d]+)"',response.text)
        item['picsUrl'] = response.xpath('//article[@id="mp-editor"]//img/@src').getall()
        item['source'] = self.name
        item['url'] = response.url

        if item['title'] and item['text']:
            yield {'type':'News','content':item}        #返回新闻数据
            url = 'https://apiv2.sohu.com/api/comment/list?page_size=30&page_no=1&source_id=mp_{}'.format(item['id'])
            yield scrapy.Request(url,callback=self.parse_comments,
                                    cb_kwargs={
                                        'page_no':1 + 1,
                                        'source_id':item['id']
                                        })
        else:       #标题和正文不能为空
            logging.info('无法解析的页面：{}'.format(response.url))

    def parse_picture(self,response):           #解析图集新闻详细内容
        item = NewsArticleItem()
        item['title'] = response.xpath('//h1/text()').get()
        item['text'] = response.xpath('//div[@class="txt"]/p/text()').getall()
        item['author'] = response.xpath('//div[@class="info"]/a/text()').get()
        item['pubTime'] = response.xpath('//div[@class="info"]/span/text()').get()
        id = response.url.split('/')[-1]
        item['id'] = id.split('_')[0]
        item['authorId'] = re.findall(r'media_id: "([\d]+)"',response.text)
        item['picsUrl'] = response.xpath('//div[@class="pic-area"]//img/@src').getall()
        item['source'] = self.name
        item['url'] = response.url

        if item['title'] and item['text']:
            yield {'type':'News','content':item}        #返回新闻数据
            url = 'https://api.interaction.sohu.com/api/comments/pages?source_id=mp_{}&page_no=1&page_size=30'.format(item['id'])
            yield scrapy.Request(url, callback=self.parse_pic_comments, 
                                    cb_kwargs={
                                        'page_no':1 + 1,
                                        'source_id':item['id']
                                        })
        else:
            logging.info('无法解析的页面：{}'.format(response.url))

    def parse_comments(self, response, page_no, source_id):
        item = NewsCommentItem()
        #hots = response.json()['jsonObject']['hots']
        try:
            comments = response.json()['jsonObject']['comments']
        except TypeError:
            pass
        else:
            if comments:
                for comm in comments:
                    #id = comm['comment_id'] 测试去重用
                    item['text'] = comm['content']
                    item['likes'] = comm['support_count']
                    item['authorId'] = comm['user_id']
                    item['author'] = comm['passport']['nickname']
                    item['location'] = comm['ip_location']
                    item['pubTime'] = comm['create_time']
                    item['picsUrl'] = None
                    item['articleId'] = source_id
                    item['source'] = self.name
                    yield {'type':'Comments','content':item}

                url = 'https://apiv2.sohu.com/api/comment/list?page_size=30&page_no={}&source_id=mp_{}'.format(str(page_no),source_id)
                yield scrapy.Request(url,callback=self.parse_comments,
                                     cb_kwargs={
                                         'page_no':page_no + 1,
                                         'source_id': source_id
                                         })
    
    def parse_pic_comments(self, response, page_no, source_id):
        item = NewsCommentItem()
        try:
            userlist = response.json()['data']['users']
            comments = response.json()['data']['comments']
        except Exception:
            pass
        else:
            if comments:           #为空说明已无更多评论
                for comm in comments:
                    item['text'] = comm['content']
                    item['likes'] = comm['likeCount']
                    item['authorId'] = comm['userId']
                    item['author'] = userlist[str(comm['userId'])]['userName']
                    item['location'] = comm['location']
                    item['pubTime'] = comm['date']
                    item['articleId'] = source_id
                    item['source'] = self.name
                    yield {'type':'Comments','content':item}        #返回评论数据

                url = 'https://api.interaction.sohu.com/api/comments/pages?source_id=mp_{}&page_no={}&page_size=30'.format(source_id,str(page_no))
                yield scrapy.Request(url,callback=self.parse_pic_comments,
                                     cb_kwargs={
                                         'page_no':page_no + 1,
                                         'source_id': source_id
                                         })