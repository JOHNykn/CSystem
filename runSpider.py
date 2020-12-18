from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import os
from datetime import datetime
import logging
import argparse

from pushData import push

def runSpider(spider,settings=None):
    process = CrawlerProcess(get_project_settings())
    process.settings.update(settings)
    process.crawl(spider)
    process.start()

parser = argparse.ArgumentParser(description='根据命令行参数运行爬虫')
parser.add_argument('-i','-id',dest='id')
parser.add_argument('-n','-name',dest='spiderName')
parser.add_argument('-k','-keyword',nargs='*',dest='keyword')

args = parser.parse_args()
spider = args.spiderName
savePath = os.path.join('results', args.id)
if not os.path.exists(savePath):
    os.makedirs(savePath)

#记录INFO级以上的日志到文件里
startTime = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
filename='{}_{}.log'.format(spider, startTime)
filepath = os.path.join('logs', filename)
fh = logging.FileHandler(filepath)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logger.addHandler(fh)

try:
    keywordList=args.keyword[0].split(',')
except TypeError:
    keywordList = None

settings = {
    'MISSION_ID' : args.id,
    'KEYWORD_LIST' : keywordList,
    'SAVE_PATH' : savePath
    }

#运行名为Spider的爬虫，根据settings更新爬虫设置
runSpider(spider,settings)
#推送目录名为id下的所有数据
push(args.id)


