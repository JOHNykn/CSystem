import scrapy
from scrapy.selector import Selector
from CrawlerSystem.items import WeiboCommentItem

class CommentSpider(scrapy.Spider):
    name = 'comment'

    #custom_settings = {
    #    'ITEM_PIPELINES' : {
    #        'weibo.pipelines.CommentCsvPipeline': 301      #微博存入CSV文件
    #        }
    #}
    
    commenthreadId = set()

    def start_requests(self):
        url = 'https://weibo.com/aj/v6/comment/big?id={}&from=singleWeiBo'.format(4573868255611273)
        yield scrapy.Request(url,callback=self.parseComment)

    def parseComment(self,response):
        with open('r.html','w',encoding='utf-8') as f:
            f.write(response.json()['data']['html'])
        select = Selector(text=response.json()['data']['html'],type='html')
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        with open('comment.txt','a',encoding='utf-8-sig') as output:
            for comm in select.xpath('//div[@comment_id]'):
                item = CommentItem()
                item['id'] = comm.xpath('@comment_id').get()
                if item['id'] in self.commenthreadId:
                    continue
                else:
                    self.commenthreadId.add(item['id'])
                    item['user_id'] = comm.xpath('.//div[@class="WB_text"]/a/@usercard').get()
                    item['screen_name'] = comm.xpath('.//div[@class="WB_text"]/a[@usercard]/text()').get()
                    item['text'] = comm.xpath('string(.//div[@class="WB_text"])').get()
                    item['likes_count'] = comm.xpath('string(.//span[@node-type="like_status"])').get()
                    item['pub_time'] = comm.xpath('.//div[@class="WB_from S_txt2"]/text()').get()
                    item['pic'] = comm.xpath('.//li[@class="WB_pic S_bg2 bigcursor"]/img/@src').get()
                    childCommentImg = comm.xpath('.//div[@class="WB_text"]/a[@imagecard]/@action-data').get()
                    if childCommentImg:            #获取二级评论中图片的url
                        src = childCommentImg.split('&')[0]
                        item['pic'] = 'https://photo.weibo.com/h5/comment/compic_id/' + src.split('=')[-1]
                    item['weibo_id'] = ''
                    output.write(item['text'])
                    #yield {'content':item}
                more_child_comment = comm.xpath('.//a[@action-type="click_more_child_comment_big"]/@action-data').get()
                if more_child_comment:
                    url = 'https://weibo.com/aj/v6/comment/big?{}&from=singleWeiBo'.format(more_child_comment)
                    yield scrapy.Request(url, callback=self.parseMoreChildComment)

        action_data_from_a = select.xpath('//a[@action-type="click_more_comment"]/@action-data').get()      #查看更多
        action_data_from_div = select.xpath('//div[@node-type="comment_loading"]/@action-data').get()       #正在加载中
        more_comment = action_data = action_data_from_a if action_data_from_a else action_data_from_div
        if more_comment:
            url = 'https://weibo.com/aj/v6/comment/big?{}&from=singleWeiBo'.format(more_comment)
            yield scrapy.Request(url, callback=self.parseComment)

    def parseMoreChildComment(self,response):
        with open('t.html','w',encoding='utf-8') as f:
            f.write(response.json()['data']['html'])
        select = Selector(text=response.json()['data']['html'],type='html')
        with open('childComment.txt','a',encoding='utf-8-sig') as output:
            for comm in select.xpath('//div[@comment_id]'):
                item = CommentItem()
                item['id'] = comm.xpath('@comment_id').get()
                if item['id'] in self.commenthreadId:
                    continue
                else:
                    item['user_id'] = comm.xpath('.//div[@class="WB_text"]/a/@usercard').get()
                    item['screen_name'] = comm.xpath('.//div[@class="WB_text"]/a[@usercard]/text()').get()
                    item['text'] = comm.xpath('string(.//div[@class="WB_text"])').get()
                    item['likes_count'] = comm.xpath('string(.//span[@node-type="like_status"])').get()
                    item['pub_time'] = comm.xpath('.//div[@class="WB_from S_txt2"]/text()').get()
                    item['pic'] = comm.xpath('.//div[@class="WB_text"]/a[@imagecard]/@action-data').get()
                    if item['pic']:
                        src = item['pic'].split('&')[0]
                        item['pic'] = 'https://photo.weibo.com/h5/comment/compic_id/' + src.split('=')[-1]
                    item['weibo_id'] = ''
                    output.write(item['text'])
                    #yield {'content':item}

        more_child_comment = select.xpath('//a[@action-type="click_more_child_comment_big"]/@action-data').get()
        if more_child_comment:
            url = 'https://weibo.com/aj/v6/comment/big?{}&from=singleweibo'.format(more_child_comment)
            yield scrapy.Request(url, callback=self.parseMoreChildComment)
