import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import NewsArticleItem, NewsCommentItem
from CrawlerSystem.custom_settings import Tencent_custom_settings

import sys
import os
import json
import logging

class TencentNews(CrawlSpider):
    name = 'qq'
    allowed_domains = ['qq.com']
    #启用新闻pipeline
    custom_settings = Tencent_custom_settings

    denyUrls=['https://new.qq.com/omn/author','https://www.qq.com/babygohome']
    rules = [
        Rule(LinkExtractor(allow=(r'https://new.qq.com/omn/[\w]+/[\w]+'), deny=denyUrls),
             callback='parse_content'),
        Rule(LinkExtractor(allow=(r'https://new.qq.com/rain/a/[\w]+')), 
             callback='parse_content')]

    def start_requests(self):
        filepath=os.path.join('start_urls','qq_start.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            for url in urls:
                yield scrapy.Request(url)       #腾讯新闻首页所有内容
        
        filepath=os.path.join('start_urls','qq_ajax.txt')
        with open(filepath,'r',encoding='utf-8') as urls:
            for url in urls:
                yield scrapy.Request(url,callback=self.parse_ajax)

    def parse_ajax(self,response):              #解析由js加载的数据,获取新闻链接
        try:
            articles = response.json()['data']['list']
        except Exception:
            articles = response.json()['data']
        for arti in articles:
            yield scrapy.Request(arti['url'],callback=self.parse_content)

    def parse_content(self,response):       #解析新闻详细内容
        try:
            pics_info = response.xpath('string(//script[contains(string(.),"IMGDATA")])').get()        
            if pics_info:       #获取图集新闻图片与正文
                pics_info = json.loads(pics_info.split('=')[-1])
                text = [pic['desc'] for pic in pics_info if pic['type'] == 2]
                imgs = [pic['value'] for pic in pics_info if pic['type'] == 2]
            else:               #获取常规新闻图片与正文
                article = response.xpath('//div[@class="content-article"]')             
                text = article.xpath('.//p[@class="one-p"]//text()').getall()
                imgs = article.xpath('.//img/@src').getall()
            info = response.xpath('string(//script[contains(string(.),"window.DATA")])').get()
            info = json.loads(info.split('=')[-1])
        except Exception:
            logging.info('页面无法解析或返回错误：{}'.format(response.url))
        else:
            item = NewsArticleItem()
            item['title'] = info['title']
            item['text'] = text
            item['author'] = info['media']
            item['pubTime'] = info['pubtime']
            item['picsUrl'] = imgs
            item['id'] = info['comment_id']
            item['authorId'] = info['media_id']
            item['source'] = 'qq'
            item['url'] = response.url

            if item['title'] and item['text']:
                yield {'type':'News','content':item}        #返回新闻数据
            else:       #标题和正文不能为空
                logging.info('无法解析的页面：{}'.format(response.url))
            url = 'https://coral.qq.com/article/{}/comment/v2?oriorder=t&cursor=0'.format(info['comment_id'])
            yield scrapy.Request(url,callback=self.parse_comments)              #获取评论

    def parse_comments(self,response):
        jsonResponse = response.json()
        child_comments = set()
        userList = jsonResponse['data']['userList']                 
        oriCommList = jsonResponse['data']['oriCommList']
        repCommList = jsonResponse['data']['repCommList']
        if oriCommList:           #为空说明已无更多评论
            for oriComment in oriCommList:
                item = self.getComment(oriComment, userList)
                yield {'type':'Comments','content':item}    #返回评论数据

                if int(oriComment['orireplynum']) > 0:    #如果该评论有回复
                    if repCommList:
                        for comment in repCommList[oriComment['id']]:
                            item = self.getComment(comment, userList)
                            yield {'type':'Comments','content':item}    #返回评论数据

                        if int(oriComment['orireplynum']) > len(repCommList[oriComment['id']]):
                            child_comments.add(oriComment['id'])      #获取全部回复
                    else:
                        child_comments.add(oriComment['id'])
                        
            targetid = jsonResponse['data']['targetid']
            cursor = jsonResponse['data']['last']
            url = 'https://coral.qq.com/article/{targetid}/comment/v2?oriorder=t&cursor={cursor}'.format(targetid=targetid,cursor=cursor)
            yield scrapy.Request(url,callback=self.parse_comments)     #获取更多评论

            for id in child_comments:
                url = 'https://coral.qq.com/comment/{id}/reply/v2?targetid={targetid}&pageflag=2&cursor=0'.format(id=id,targetid=targetid)
                yield scrapy.Request(url,callback=self.parse_replys)    #获取二级评论
    
    def getComment(self,comment, userlist):
        item = NewsCommentItem()
        item['text'] = comment['content']
        item['authorId'] = comment['userid']
        item['author'] = userlist[comment['userid']]['nick']
        item['likes'] = comment['up']
        item['location'] = userlist[comment['userid']]['region']
        item['pubTime'] = comment['time']
        try:
            item['picsUrl'] = [pic['url'] for pic in comment['picture']]
        except KeyError:
            item['picsUrl'] = None
        item['articleId'] = comment['targetid']
        item['source'] = self.name
        return item

    def parse_replys(self,response):
        jsonResponse = response.json()
        userList = jsonResponse['data']['userList']
        repCommList = jsonResponse['data']['repCommList']
        if repCommList:
            for repComment in repCommList:
                item = self.getComment(repComment, userList)
                yield {'type':'Comments','content':item}        #返回评论数据

            id = jsonResponse['data']['oriComment']['id']
            targetid = jsonResponse['data']['targetid']
            cursor = jsonResponse['data']['first']
            url = 'https://coral.qq.com/comment/{id}/reply/v2?targetid={targetid}&pageflag=2&cursor={cursor}'.format(id=id,targetid=targetid,cursor=cursor)
            yield scrapy.Request(url,callback=self.parse_replys)
                


