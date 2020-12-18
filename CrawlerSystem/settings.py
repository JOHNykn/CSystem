BOT_NAME = 'CrawlerSystem'

SPIDER_MODULES = ['CrawlerSystem.spiders']
NEWSPIDER_MODULE = 'CrawlerSystem.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'CrawlerSystem (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

KEYWORD_LIST = ["中山陵","玄武湖","长江大桥","金陵饭店","紫峰大厦","吴政隆","杨岳","李小敏","孟中康","南京条约","商改住","南大碎尸","南京邮政分拨中心","南京理工大学","南京女大学生"]
MISSION_ID = '351'

import os
SAVE_PATH = os.path.join('results', MISSION_ID)
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

#CLOSESPIDER_TIMEOUT = 60

#爬虫速度控制
CONCURRENT_REQUESTS = 48
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False
TELNETCONSOLE_USERNAME = 'qwe'
TELNETCONSOLE_PASSWORD = '123456'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'CrawlerSystem.middlewares.CrawlersystemSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'CrawlerSystem.middlewares.CrawlersystemDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.closespider.CloseSpider' : 100
#}

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
