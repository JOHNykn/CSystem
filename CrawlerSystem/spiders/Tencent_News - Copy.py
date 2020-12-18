import scrapy
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from CrawlerSystem.items import NewsArticleItem, NewsCommentItem

import logging
import json
from urllib.parse import urlparse
from pprint import pprint

class TencentNews(RedisCrawlSpider):
    name = 'qq_s'
    allowed_domains = ['qq.com']
    redis_key = 'qq:start_urls'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES' : {
            'News.middlewares.TencentNewsRedirectDownloaderMiddleware': 600,      #处理js生成location的302跳转
            }
    }

    rules = [
        Rule(LinkExtractor(allow=(r'https://new.qq.com/omn/[\w]+/[\w]+'),deny=(r'https://new.qq.com/omn/author')),
                           callback='parse_content'),
        Rule(LinkExtractor(allow=(r'https://new.qq.com/rain/a/[\w]+')),callback='parse_content')
        ]

    def pop_list_queue(self, redis_key, batch_size):
        with self.server.pipeline() as pipe:
            pipe.lrange(redis_key, 0, batch_size - 1)
            pipe.ltrim(redis_key, batch_size, -1)
            datas, _ = pipe.execute()
        return datas

    def start_requests(self):
        datas = self.pop_list_queue(self.redis_key, self.settings['CONCURRENT_REQUESTS'])
        for data in datas:
            url=data.decode('utf-8')
            if len(url.split('?')) > 1:   #根据url选择合适的回调函数
                yield scrapy.Request(url,callback=self.parse_ajax)
            else:
                yield scrapy.Request(url)

    #    #测试用
    #    #yield scrapy.Request('https://new.qq.com/omn/20201019/20201019A0DXJZ00.html',callback=self.parse_content)

    def parse_ajax(self,response):              #解析由js加载的数据,获取新闻链接
        try:
            articles = response.json()['data']['list']
        except Exception:
            articles = response.json()['data']
        for arti in articles:
            yield scrapy.Request(arti['url'],callback=self.parse_content)

    def parse_content(self,response):           #解析新闻详细内容
        try:
            pics_info = response.xpath('string(//script[contains(string(.),"IMGDATA")])').get()        #处理图片新闻
            if pics_info:
                pics_info = json.loads(pics_info.split('=')[-1])
                text = [pic['desc'] for pic in pics_info if pic['type'] == 2]
                imgs = [pic['value'] for pic in pics_info if pic['type'] == 2]
            else:
                article = response.xpath('//div[@class="content-article"]')             #处理常规新闻
                text = article.xpath('.//p[@class="one-p"]//text()').getall()
                imgs = article.xpath('.//img/@src').getall()
            info = response.xpath('string(//script[contains(string(.),"window.DATA")])').get()
            info = json.loads(info.split('=')[-1])

            item = NewsItem()
            item['title'] = info['title']
            item['content'] = text
            item['author'] = info['media']
            item['imgs'] = imgs
            item['pubtime'] = info['pubtime']
            item['id'] = info['comment_id']
            item['source'] = 'qq'
            yield item

            url = 'https://coral.qq.com/article/{}/comment/v2?oriorder=t&cursor=0'.format(info['comment_id'])
            #yield scrapy.Request(url,callback=self.parse_comments)              #获取评论

        except Exception as e:
            print('异常：',e,'无法解析的页面：',response.url)

    def parse_comments(self,response):
        item = CommentsItem()
        child_comments = set()
        userlist = response.json()['data']['userList']                 
        comments = response.json()['data']['oriCommList']
        if comments:           #为空说明已无更多评论
            for comm in comments:
                item['comment'] = comm['content']
                item['likes'] = comm['up']
                item['nickname'] = userlist[comm['userid']]['nick']
                item['location'] = userlist[comm['userid']]['region']
                try:
                    item['imgs'] = [pic.url for pic in comm['picture']]
                except Exception:
                    pass
                item['article_id'] = comm['targetid']
                item['source'] = self.name

                if int(comm['orireplynum']) > 0:
                    child_comments.add(comm['id'])
                yield item

            targetid = response.json()['data']['targetid']
            cursor = response.json()['data']['last']
            url = 'https://coral.qq.com/article/{targetid}/comment/v2?oriorder=t&cursor={cursor}'.format(targetid=targetid,cursor=cursor)
            yield scrapy.Request(url,callback=self.parse_comments)     #获取更多评论

            for id in child_comments:
                url = 'https://coral.qq.com/comment/{id}/reply/v2?targetid={targetid}&pageflag=2&cursor=0'.format(id=id,targetid=targetid)
                yield scrapy.Request(url,callback=self.parse_replys)    #获取二级评论

    def parse_replys(self,response):
        item = CommentsItem()
        userlist = response.json()['data']['userList']
        replys = response.json()['data']['repCommList']
        if replys:
            for rep in replys:
                item['comment'] = rep['content']
                item['likes'] = rep['up']
                item['nickname'] = userlist[rep['userid']]['nick']
                item['location'] = userlist[rep['userid']]['region']
                item['article_id'] = rep['targetid']
                item['source'] = self.name
                yield item

            id = response.json()['data']['oriComment']['id']
            targetid = response.json()['data']['targetid']
            cursor = response.json()['data']['first']
            url = 'https://coral.qq.com/comment/{id}/reply/v2?targetid={targetid}&pageflag=2&cursor={cursor}'.format(id=id,targetid=targetid,cursor=cursor)
            yield scrapy.Request(url,callback=self.parse_replys)
                


