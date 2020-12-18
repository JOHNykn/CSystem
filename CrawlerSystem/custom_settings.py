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
        'Cookie': 'SINAGLOBAL=1541501523588.6199.1599624237866; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhI3UUx8ZgN8SSxrvKLTLh55JpX5KMhUgL.FoqEehq7S0nfSKn2dJLoI7Heqg9Jdntt; UM_distinctid=17627d2a1f3263-02177706cb27e8-c791e37-144000-17627d2a1f4791; UOR=login.sina.com.cn,weibo.com,www.google.com; wvr=6; ALF=1639798758; SSOLoginState=1608262760; SCF=An-bZsX3H2J7nJyoPCcUCw9rd9aX0BLSsD-s__UwRnuzrmbEKEoGnHBIloWgx_ZueAz3R-hsP6mlTgrT_ovpeh0.; SUB=_2A25y2FQ4DeRhGeBM61QR9ybJzjSIHXVRrMLwrDV8PUNbmtAfLUbykW9NRQRfYVadSfwV_m6XD7Rx5p7yrUps1iS_; _s_tentry=login.sina.com.cn; Apache=9803555046935.953.1608262765593; ULV=1608262765730:80:14:5:9803555046935.953.1608262765593:1608180155556; WBStorage=8daec78e6a891122|undefined; webim_unReadCount=%7B%22time%22%3A1608283904992%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A2%7D'
        }
}