# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import re
import os
import csv
from datetime import datetime
from datetime import datetime,timedelta

#微博爬虫Pipeline
class WeiboStandardizePipeline():
    def process_item(self,item,spider):
        if item['content']['picsUrl']:         #更换图片的尺寸
            bmiddle = re.compile(r'sinaimg.cn/.+?/')
            item['content']['picsUrl'] = [bmiddle.sub(r'sinaimg.cn/bmiddle/',pic) for pic in item['content']['picsUrl']]

        for key in item['content']:
            if isinstance(item['content'][key], str):           #字符串字段去除首尾空白
                item['content'][key] = item['content'][key].strip()
            elif isinstance(item['content'][key], list):        #列表字段转为一个由','分隔的字符串
                item['content'][key] = ','.join(item['content'][key])

        item['content']['pubTime'] = self.StandardizeTime(item['content']['pubTime'])
        return item

    def StandardizeTime(self,pub_time):     #标准化微博发布时间
        if "刚刚" in pub_time:
            pub_time = datetime.now().strftime("%Y-%m-%d %H:%M:00")
        elif "秒" in pub_time:
            second = pub_time[:pub_time.find("秒")]
            second = timedelta(seconds=int(second))
            pub_time = (datetime.now() - second).strftime("%Y-%m-%d %H:%M:00")
        elif "分钟" in pub_time:
            minute = pub_time[:pub_time.find("分钟")]
            minute = timedelta(minutes=int(minute))
            pub_time = (datetime.now() - minute).strftime("%Y-%m-%d %H:%M:00")
        elif "小时" in pub_time:
            hour = pub_time[:pub_time.find("小时")]
            hour = timedelta(hours=int(hour))
            pub_time = (datetime.now() - hour).strftime("%Y-%m-%d %H:%M:00")
        elif "今天" in pub_time:
            today = datetime.now().strftime('%Y-%m-%d')
            pub_time = today + ' ' + pub_time[2:] + ':00'
        elif '年' not in pub_time:
            year = datetime.now().strftime("%Y")
            month = pub_time[:2]
            day = pub_time[3:5]
            time = pub_time[6:] + ':00'
            pub_time = year + '-' + month + '-' + day + ' ' + time
        else:
            year = pub_time[:4]
            month = pub_time[5:7]
            day = pub_time[8:10]
            time = pub_time[11:] + ':00'
            pub_time = year + '-' + month + '-' + day + ' ' + time
        return pub_time
   
class WeiboCsvPipeline():                #抓取的微博存入CSV文件
    def __init__(self, path):
        self.savePath = path    

    @classmethod
    def from_crawler(cls, crawler):
        return cls(path=crawler.settings.get('SAVE_PATH'))

    def open_spider(self,spider):
        header = ['id', 'authorId', 'bid', 'author', 'text', 'at_user',
            'topics', 'forwards', 'comments', 'likes', 'pubTime', 'from',
            'articleUrl', 'picsUrl', 'videoUrl', 'repostId' ,'soucre','keyword']
        startTime = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
        filename = 'weibo_{}.csv'.format(startTime)
        filePath = os.path.join(self.savePath,filename)
        self.csvFile = open(filePath, 'w', encoding='utf-8-sig',newline='')
        self.writer = csv.writer(self.csvFile)
        self.writer.writerow(header)

    def close_spider(self,spider):
        self.csvFile.close()

    def process_item(self, item, spider):
        row = [item['content']['id'], item['content']['authorId'], item['content']['bid'], item['content']['author'], item['content']['text'], item['content']['at_users'],
            item['content']['topics'], item['content']['forwards'], item['content']['comments'], item['content']['likes'], item['content']['pubTime'], item['content']['_from'],
            item['content']['articleUrl'], item['content']['picsUrl'], item['content']['videoUrl'], item['content']['repostId'], item['content']['source'], item['keyword']]
        self.writer.writerow(row)

'''----------------------------------------------------Pipeline分界线-----------------------------------------------------------------'''

#贴吧爬虫Pipeline
class TiebaCsvPipeline:
    def __init__(self, path):
        self.savePath = path    

    @classmethod
    def from_crawler(cls, crawler):
        return cls(path=crawler.settings.get('SAVE_PATH'))

    def open_spider(self,spider):
        startTime = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
        filename = 'tieba_Posts_{}.csv'.format(startTime)
        filePath = os.path.join(self.savePath,filename)

        self.post_csvFile = open(filePath, 'w', encoding='utf-8-sig',newline='')
        self.post_writer = csv.writer(self.post_csvFile)
        header = ['id','text','authorId','author','comments','belongId','picsUrl','pubTime','floor','source','keyword']
        self.post_writer.writerow(header)

        filename = 'tieba_Comments_{}.csv'.format(startTime)
        filePath = os.path.join(self.savePath,filename)

        self.comment_csvFile = open(filePath, 'w', encoding='utf-8-sig', newline='')
        self.comment_writer = csv.writer(self.comment_csvFile)
        header = ['id','text','author','belongId','pubTime','source']
        self.comment_writer.writerow(header)
        
        self.writer_dict = {
            'Post': self.post_writer,
            'Comment': self.comment_writer
            }

    def close_spider(self,spider):
        self.post_csvFile.close()
        self.comment_csvFile.close()

    def process_item(self, item, spider):
        writer = self.writer_dict[item['type']]
        try:
            row=[item['content']['postId'],item['content']['text'],item['content']['authorId'],item['content']['author'],
                 item['content']['comments'],item['content']['threadId'],item['content']['picsUrl'],item['content']['pubTime'],item['content']['floor'],item['content']['source'],item['keyword']]
        except KeyError:
             row=[item['content']['commentId'],item['content']['text'],item['content']['author'],item['content']['postId'],item['content']['pubTime'],item['content']['source']]
        writer.writerow(row)

class TiebaStandardizePipeline:
    def process_item(self,item,spider):
        for key in item['content']:
            if isinstance(item['content'][key], str):           #字符串字段去除首尾空白
                item['content'][key] = item['content'][key].strip()
            elif isinstance(item['content'][key], list):        #列表字段转为一个由','分隔的字符串
                item['content'][key] = ','.join(item['content'][key])

        if item['type'] == 'Comment':      #处理"回复 username:回复内容"，仅保留回复内容
            pattern = r'^回复[ ].*:'
            item['content']['text'] = re.sub(pattern,'',item['content']['text'])        
        return item

'''----------------------------------------------------Pipeline分界线-----------------------------------------------------------------'''

#新闻爬虫Pipeline
class NewsCsvPipeline:
    def __init__(self, path):
        self.savePath = path    

    @classmethod
    def from_crawler(cls, crawler):
        return cls(path=crawler.settings.get('SAVE_PATH'))

    def open_spider(self,spider):
        startTime = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')

        filename = '{}_{}.csv'.format(spider.name,startTime)
        filePath = os.path.join(self.savePath,filename)
        self.news_csvFile = open(filePath, 'w', encoding='utf-8-sig', newline='')
        self.news_writer = csv.writer(self.news_csvFile)
        header = ['title','text','author','pubTime','newsId','authorId','picsUrl','source']
        self.news_writer.writerow(header)

        filename = '{}_Comments_{}.csv'.format(spider.name,startTime)
        filePath = os.path.join(self.savePath,filename)
        self.comments_csvFile = open(filePath, 'w', encoding='utf-8-sig', newline='')
        self.comments_writer = csv.writer(self.comments_csvFile)
        header = ['text','authorId','author','pubTime','likes','region','picsUrl','belongId','source']
        self.comments_writer.writerow(header)
        
        self.writer_dict = {
            'News': self.news_writer,
            'Comments': self.comments_writer
            }

    def close_spider(self,spider):
        self.news_csvFile.close()
        self.comments_csvFile.close()

    def process_item(self, item, spider):
        writer = self.writer_dict[item['type']]
        try:
            row=[item['content']['title'],item['content']['text'],item['content']['author'],item['content']['pubTime'],
                 item['content']['id'],item['content']['authorId'],item['content']['picsUrl'],item['content']['source']]
        except KeyError:
            row=[item['content']['text'],item['content']['authorId'],item['content']['author'],item['content']['pubTime'],item['content']['likes'],
                 item['content']['location'],item['content']['picsUrl'],item['content']['articleId'],item['content']['source']]
        writer.writerow(row)

class NewsStandardizePipeline:
    def process_item(self,item,spider):
        for key in item['content']:
            if isinstance(item['content'][key], str):           #字符串字段去除首尾空白
                item['content'][key] = item['content'][key].strip()
            elif isinstance(item['content'][key], list):        #列表字段转为一个由','分隔的字符串
                if key == 'text':
                    item['content'][key] = ''.join([sentence.strip() for sentence in item['content'][key]])
                else:
                    item['content'][key] = ','.join(item['content'][key])

        try:
            pubtime=int(item['content']['pubTime'])
        except Exception:
            pass
        else:
            try:
                item['content']['pubTime'] = datetime.fromtimestamp(pubtime).strftime('%Y-%m-%d %H:%M:%S')
            except OSError:     #搜狐评论时间戳是毫秒级
                item['content']['pubTime'] = datetime.fromtimestamp(pubtime//1000).strftime('%Y-%m-%d %H:%M:%S')
        return item