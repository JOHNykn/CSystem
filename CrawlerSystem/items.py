# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#微博爬虫Items
class WeiboItem(scrapy.Item):
    id = scrapy.Field()                 #单条微博标识id
    authorId = scrapy.Field()           #发布人标识id
    bid = scrapy.Field()                #//weibo.com/id/bid为该微博对应url
    author = scrapy.Field()             #发布人
    text = scrapy.Field()               #正文
    at_users = scrapy.Field()           #正文中@的人
    topics = scrapy.Field()             #正文中的话题
    forwards = scrapy.Field()           #转发数
    comments = scrapy.Field()           #评论数
    likes = scrapy.Field()              #点赞数
    pubTime = scrapy.Field()            #发布时间
    _from = scrapy.Field()             #发布工具
    articleUrl = scrapy.Field()         #头条文章url
    picsUrl = scrapy.Field()            #图片url
    videoUrl = scrapy.Field()           #视频url
    repostId = scrapy.Field()           #被转发的微博id 
    source = scrapy.Field()             #数据来源


class WeiboCommentItem(scrapy.Item):
    id = scrapy.Field()                 #评论标识id
    authorId = scrapy.Field()           #发布人标识id
    author = scrapy.Field()             #发布人
    text = scrapy.Field()               #正文
    likes = scrapy.Field()              #点赞数
    pubTime = scrapy.Field()            #发布时间
    picsUrl = scrapy.Field()            #图片url
    weiboId = scrapy.Field()            #所属微博id
    source = scrapy.Field()             #数据来源

'''----------------------------------------------------Items分界线-----------------------------------------------------------------'''

#贴吧爬虫Items
class TiebaThreadItem(scrapy.Item):
    threadId = scrapy.Field()           #帖子标识id
    title = scrapy.Field()              #帖子标题
    author = scrapy.Field()             #发帖人
    video = scrapy.Field()              #帖子视频
    posts = scrapy.Field()              #回帖数
    
class TiebaPostItem(scrapy.Item):
    postId = scrapy.Field()             #回贴id
    text = scrapy.Field()               #回复内容
    author = scrapy.Field()             #发布人
    authorId = scrapy.Field()           #发布人标识id
    picsUrl = scrapy.Field()            #回复图片
    comments = scrapy.Field()           #回帖的评论数
    threadId = scrapy.Field()           #所属帖子id
    pubTime = scrapy.Field()            #发布时间
    floor = scrapy.Field()              #楼层数
    source = scrapy.Field()             #数据来源


class TiebaCommentItem(scrapy.Item):
    commentId = scrapy.Field()          #评论id
    text = scrapy.Field()               #评论内容
    author = scrapy.Field()             #发布人
    #authorId = scrapy.Field()           #发布人标识id
    postId = scrapy.Field()             #所属回帖id
    pubTime = scrapy.Field()            #发布时间
    source = scrapy.Field()             #数据来源

'''----------------------------------------------------Items分界线-----------------------------------------------------------------'''

#新闻爬虫Items
class NewsArticleItem(scrapy.Item):
    id = scrapy.Field()                 #标识id
    title = scrapy.Field()              #标题
    text = scrapy.Field()               #内容
    author = scrapy.Field()             #作者
    authorId = scrapy.Field()           #发布人标识id
    picsUrl = scrapy.Field()            #图片
    #videos = scrapy.Field()            #视频
    pubTime = scrapy.Field()            #发布时间
    source = scrapy.Field()             #数据来源
    url = scrapy.Field()

class NewsCommentItem(scrapy.Item):
    text = scrapy.Field()               #评论
    likes = scrapy.Field()              #获赞数
    author = scrapy.Field()             #发布人
    authorId = scrapy.Field()           #发布人标识id
    location = scrapy.Field()           #位置
    pubTime = scrapy.Field()            #发布时间
    picsUrl = scrapy.Field()            #图片
    articleId = scrapy.Field()          #所属新闻id
    source = scrapy.Field()             #数据来源