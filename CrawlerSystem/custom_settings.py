News_custom_settings = {
    'DOWNLOAD_DELAY' : 0.5,
    'AUTOTHROTTLE_TARGET_CONCURRENCY' : 2.0,
    'ITEM_PIPELINES' : {
        'CrawlerSystem.pipelines.NewsStandardizePipeline': 300,
        'CrawlerSystem.pipelines.NewsCsvPipeline': 400
        }
}

#腾讯新闻爬虫
Tencent_custom_settings = {
    'DOWNLOADER_MIDDLEWARES' : {
        'CrawlerSystem.middlewares.QQNewsRedirectDownloaderMiddleware': 600,      #处理js生成location的302跳转
        }
}
Tencent_custom_settings.update(News_custom_settings)

#贴吧爬虫
Tieba_custom_settings = {
    'DOWNLOAD_DELAY' : 1,
    'AUTOTHROTTLE_TARGET_CONCURRENCY' : 2.0,
    'ITEM_PIPELINES' : {
        'CrawlerSystem.pipelines.TiebaStandardizePipeline': 300,
        'CrawlerSystem.pipelines.TiebaCsvPipeline': 400
        }
}

#微博爬虫
Weibo_custom_settings = {
    'DOWNLOAD_DELAY' : 3,
    'AUTOTHROTTLE_TARGET_CONCURRENCY' : 1.0,
    'ITEM_PIPELINES' : {
        'CrawlerSystem.pipelines.WeiboStandardizePipeline': 300,
        'CrawlerSystem.pipelines.WeiboCsvPipeline': 400
        },
    'DEFAULT_REQUEST_HEADERS' : {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        'Cookie': ''
        }
}
