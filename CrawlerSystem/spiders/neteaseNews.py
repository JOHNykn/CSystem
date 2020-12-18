import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import NewsArticleItem, NewsCommentItem
from CrawlerSystem.custom_settings import News_custom_settings
 
import re
import os
import json
from urllib.parse import urlparse

class Netease_News(CrawlSpider):
    name = '163'
    allowed_domains = ['163.com']

    custom_settings = News_custom_settings

    post_id = {}
    denyDomains=['product.auto.163.com','v.163.com','sports.163.com','home.163.com']
    rules = [
        Rule(LinkExtractor(allow = r'/[\d]{2}/[\d]{4}/[\d]{2}/[\w]+',deny_domains = denyDomains), callback = 'parse_content'),
        Rule(LinkExtractor(allow = r'/article/[\w]+', deny_domains = denyDomains), callback='parse_content'),
        Rule(LinkExtractor(allow = r'/photoview/[\w]+/[\d]+',deny_domains = denyDomains), callback = 'parse_content')]

    def start_requests(self):
        filepath = os.path.join('start_urls','163_start.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            for url in urls:
                yield scrapy.Request(url)
        
        filepath = os.path.join('start_urls','163_ajax.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            for url in urls:
                yield scrapy.Request(url,callback=self.parse_ajax)

    def parse_ajax(self,response):              #解析由js加载的数据,获取新闻链接
        if response.text.startswith('data_callback('):
            text = response.text.replace('data_callback(','')[:-1]
        try:
            articles = json.loads(text)
        except Exception as e:
            self.logger.warning(e,'无法解析的页面：{}'.format(response.url))
        else:
            for arti in articles:
                if(urlparse(arti['docurl']).netloc) not in self.denyDomains:
                    yield scrapy.Request(arti['docurl'],callback=self.parse_content)

    def parse_content(self,response):           #解析新闻详细内容
            item = NewsArticleItem()
            if re.search(r'/[\d]{2}/[\d]{4}/[\d]{2}/[\w]+',response.url):       #LinkExtractor(r'/[\d]{2}/[\d]{4}/[\d]{2}/[\w]+')
                item['title'] = response.xpath('//h1/text()').get()
                item['text'] = response.xpath('//div[@id="endText"]//p//text()[not(parent::style)]').getall()
                item['author'] = response.xpath('//a[@id="ne_article_source"]/text()').get()
                item['pubTime'] = response.xpath('//html[@id="ne_wrap"]/@data-publishtime').get()
                item['picsUrl'] = response.xpath('//div[@id="endText"]//img/@src').getall()

            elif re.search(r'/article/[\w]+',response.url):                      #LinkExtractor(r'/article/[\w]+')
                item['title'] = response.xpath('//h1[@class="post_title"]/text()').get()
                item['text'] = response.xpath('//div[@class="post_body"]//p//text()[not(parent::style)]').getall()
                item['author'] = response.xpath('//div[@class="post_wemedia_name"]/a/text()').get()
                item['pubTime'] = response.xpath('//html[@id="ne_wrap"]/@data-publishtime').get()
                item['picsUrl'] = response.xpath('//div[@id="content"]//img/@src').getall()

            elif re.search(r'/photoview/[\w]+/[\d]+',response.url):              #LinkExtractor(r'/photoview/[\w]+/[\d]+')
                info = response.xpath('//textarea[@name="gallery-data"]/text()').get()
                try:
                    info = json.loads(info)
                except Exception as e:
                    self.logger.warning(e)
                text = [pic['note'] for pic in info['list']]
                imgs = [pic['img'] for pic in info['list']]

                item['title'] = info['info']['setname']
                item['text'] = text
                item['author'] = info['info']['source']
                item['pubTime'] = info['info']['lmodify']
                item['picsUrl'] = imgs

            if item['title'] and item['author']:
                item['authorId'] = ''
                item['id'] = response.selector.re_first(r'"docId".+"([\w]+)"')
                item['source'] = self.name
                item['url'] = response.url      #测试用
                yield {'type':'News','content':item}        #返回新闻数据

                base_url = 'https://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'
                if item.get('id'):
                    new = base_url + '{}/comments/newList?ibc=newspc&limit=40&offset=0'.format(item['id'])
                    hot = base_url + '{}/comments/hotList?ibc=newspc&limit=40&offset=0'.format(item['id'])
                    self.post_id[item['id']] = set()            #key-value = 新闻id-评论id，用于评论去重
                    self.post_id[item['id'] + '_flag'] = 2      #表明新闻是否还有评论的标志位,为0时删相应的键

                    yield scrapy.Request(hot,callback=self.parse_comments,      #获取热门评论
                                            cb_kwargs={
                                                'threads': item['id'],
                                                'offset': 0
                                                })                
                    yield scrapy.Request(new,callback=self.parse_comments,      #获取最新评论
                                            cb_kwargs={
                                                'threads': item['id'],
                                                'offset': 0
                                                })                
                else:
                    self.logger.info('跟帖已关闭：{}'.format(response.url))
            else:
                self.logger.info('无法解析的页面：{}'.format(response.url))

    def parse_comments(self, response, threads, offset):
        item = NewsCommentItem()
        comments_id = response.json()['commentIds']
        comments = response.json()['comments']
        if comments:
            for id in comments_id:
                id = id.split(',')[-1]
                post_id = comments[id]['commentId']
                if post_id not in self.post_id[threads]:
                    self.post_id[threads].add(post_id)
                    item['text'] = comments[id]['content']
                    item['authorId'] = comments[id]['user']['userId']
                    item['author'] = comments[id]['user'].get('nickname','火星网友')
                    item['likes'] = comments[id]['vote']
                    item['location'] = comments[id]['user']['location']
                    item['pubTime'] = comments[id]['createTime']
                    item['picsUrl'] = None
                    item['articleId'] = threads
                    item['source'] = self.name
                    yield {'type':'Comments','content':item}        #返回评论数据

            offset += 40
            url = response.url.split('?')[0] + '?ibc=newspc&limit=40&offset={}'.format(offset)
            yield scrapy.Request(url,callback=self.parse_comments,
                                 cb_kwargs={
                                     'threads': threads,
                                     'offset': offset
                                     })

        elif self.post_id[threads + '_flag'] > 0:
            self.post_id[threads + '_flag'] -= 1
        elif self.post_id[threads + '_flag'] == 0:
            del self.post_id[threads]
