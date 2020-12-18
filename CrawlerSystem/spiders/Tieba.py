# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import TiebaThreadItem, TiebaPostItem, TiebaCommentItem
from CrawlerSystem.custom_settings import Tieba_custom_settings

from urllib import parse
import json
from datetime import datetime
from math import ceil


class TiebaSpider(CrawlSpider):
    name = 'tieba'
    allowed_domain = ['tieba.baidu.com']
    custom_settings = Tieba_custom_settings

    rules = [
        Rule(LinkExtractor(allow=(r'/p/[\d]+$')),callback='parse_post',process_links='add_pn'),
        Rule(LinkExtractor(restrict_xpaths=('//a[contains(string(.),"下一页>")]')),callback='parse_start_url',follow=True)
        ]

    def start_requests(self):
        url = 'https://tieba.baidu.com/f?kw={}&ie=utf-8'.format(self.settings['TIEBA'])
        yield scrapy.Request(url)

    def add_pn(self,links):         #添加第一页标记，方便判断页数
        for link in links:
            link.url += '?pn=1'
        return links

    def parse_start_url(self, response):        #解析贴吧索引页，获取帖子基本信息
        Threads = response.xpath('//li[contains(@class,"j_thread_list")]')
        if Threads:
            for thread in Threads:
                data = json.loads(thread.xpath('@data-field').get())
                if data['id'] == 1:        # 去掉"本吧吧主火热招募"
                    continue
                item = TiebaThreadItem()
                item['threadId'] = data['id']
                item['title'] = thread.xpath('.//div[contains(@class, "threadlist_title")]/a/@title').get()
                item['author'] = data['author_name']
                item['video'] = thread.xpath('//div[@class="threadlist_video"]/a/@data-video').get()
                item['post_count'] = data['reply_num']
                yield item
        else:
            return None
            
    def parse_post(self, response):                    #解析回帖的内容
        argu = response.request.url.split('/')[-1]     #request评论所需参数
        threadId = argu.split('?')[0]                       #帖子id
        pn = argu.split('?')[-1]                       #当前页数
        Posts = response.xpath("//div[contains(@class, 'l_post')]")
        if Posts:
            for post in Posts:
                item = TiebaPostItem()
                data = json.loads(post.xpath("@data-field").get())
                item['postId'] = data['content']['post_id']
                item['content'] = post.xpath('string(.//cc/div[contains(@class,"d_post_content")])').get()
                item['author'] = data['author']['user_name']
                item['img'] = post.xpath('.//cc//img/@src').getall()
                item['comment_count'] = data['content']['comment_num']
                item['threadId'] = threadId
                if 'date' in data['content'].keys():            #仅旧帖子data-field中有日期
                    item['time'] = data['content']['date']
                else:
                    item['time'] = post.xpath('.//div[@class="post-tail-wrap"]/span[last()]/text()').get()
                item['floor'] = data['content']['post_no']
                yield item
                
                if data['content']['comment_num'] > 0:
                    postId = data['content']['post_id']
                    url = "https://tieba.baidu.com/p/comment?threadId={}&postId={}&pn=1".format(threadId, postId)
                    yield scrapy.Request(url, callback = self.parse_comment, cb_kwargs={'postId': postId})         #帖子翻页

            next_page = response.xpath('//ul[@class="l_posts_num"]//a[string(.)="下一页"]/@href').get()
            if next_page:
                #pass
                yield response.follow(next_page, callback = self.parse_post)            #获取评论
        else:
            return None
  
    def parse_comment(self, response, postId):
        comments_list = response.xpath('//li[contains(@class,"lzl_single_post")]')
        for comment in comments_list:
            data = json.loads(comment.attrib['data-field'])
            item = TiebaCommentItem()
            item['commentId'] = data['spostId']
            item['content'] = comment.xpath('string(.//span[@class="lzl_content_main"])').get()
            item['author'] = data['user_name']
            item['postId'] = postId
            item['time'] = comment.xpath('.//span[@class="lzl_time"]/text()').get()
            yield item

        next_page = response.xpath('//p[@class="j_pager l_pager pager_theme_2"]/a[contains(text(),"下一页")]/@href').get()
        if next_page:
            url = response.url[:-1] + next_page[-1]
            yield scrapy.Request(url,callback=self.parse_comment, cb_kwargs={'postId': postId})
