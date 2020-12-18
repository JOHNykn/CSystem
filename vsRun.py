from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def runSpider(Spider,settings=None):
    process = CrawlerProcess(get_project_settings())
    process.settings.update(settings)
    process.crawl(Spider)
    process.start()

runSpider('weiboSearch')
#runSpider('qq')



