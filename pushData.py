import requests
import json
import csv
import os
from collections import namedtuple
from pprint import pprint

headers = {
    "Content-type":"application/json",
    "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2Mzk3MjA1NTcsInVzZXJJZCI6IjI3IiwidmVyc2lvbiI6IjEuMCIsInVzZXJuYW1lIjoiMSJ9.w_9YwvT0LtX1MbjkpLsysGRVO8y98cN18bj0nyj3vY4",
    }

jsondata = {
        "data": None,
        "insert_time": None
          }

data = {
    "source_site": "",
    "source_url": "",
    "source_area": "",
    "impact_level": 3,
    "info_type": "源发",
    "abstract1": "",
    "content": "",
    "public_time": "",
    "account_name": "",
    "account_url": "",
    "title": "",
    "keyword": "",
    "mark_type": -1,
    "mark_user": 0,
    "user_id": "",
    "scheme_id": 0,
    "valid": 1,
    "visible": 1,
    "figure_print": "",
    "priority": 1000,
    "originnal_pic": "",
    "thumbnail_pic": "",
    "bmiddle_pic": "",
    "video_url": "",
    "nfans": 0,
    "nfriend": 0,
    "briefintrod": "",
    "nreply": 0,
    "nlike": 0,
    "m_id": "",
    "client_remark": "",
    "at_users": "",
    "subject_info": ""
}

comment_data={
    'id': 0,
    'content': "",
    'public_time': '',
    'account_name': "",
    'user_id': "",
    'nlike': 0,
    'originnal_pic': '',
    'm_id': ""
    }

datalist = []

def pushComment(file, Row, post_url, id=None):
    for line in file:
        row = Row(*line)
        rowGet = lambda key:row._asdict().get(key,'')       #用rowGet代替namedtuple._asdict().get()

        comment_data['id'] = rowGet('id')                   #评论id
        comment_data['content'] = rowGet('text')            #评论内容
        comment_data['account_name'] = rowGet('author')     #作者
        comment_data['originnal_pic'] = rowGet('picsUrl')   #图片url
        comment_data['m_id'] = rowGet('belongId')           #所属正文id
        comment_data['public_time'] = rowGet('pubTime').replace(' ','T')    #发布时间
        try:
            data['user_id'] = int(row._asdict().get('authorId'))     #作者标识id
        except Exception:
            data['user_id'] = -1
        try:
            comment_data['nlike'] = int(row._asdict().get('likes', 0))      #获赞数
        except ValueError:
            if row._asdict().get('likes')=='赞':
                comment_data['nlike'] = 0

        datalist.append(comment_data.copy())
        if len(datalist) % 500== 0:
            jsondata['data'] = datalist
            req = requests.post(post_url,json=jsondata,headers=headers)
            print(req.text)
            datalist.clear()

    if datalist:
        jsondata['data'] = datalist
        req = requests.post(post_url,json=jsondata,headers=headers)
        print(req.text)
        datalist.clear()

def pushContent(file, Row, post_url, id):
    for line in file:
        row = Row(*line)
        rowGet = lambda key:row._asdict().get(key,'')       #用rowGet代替namedtuple._asdict().get()

        data['m_id'] = rowGet('id')                       #数据标识id
        data['content'] = rowGet('text')                  #正文
        data['account_name'] = rowGet('author')           #作者
        data['originnal_pic'] = rowGet('picsUrl')         #图片url
        data['video_url'] = rowGet('videoUrl')            #视频url
        data['source_site'] = rowGet('source')            #数据来源
        data['client_remark'] = rowGet('from')            #微博发布工具
        data['keyword'] = rowGet('keyword')               #关键词
        data['at_users'] = rowGet('at_users')             #@用户
        data['subject_info'] = rowGet('topics')           #"#"话题
        data['title'] = rowGet('title')                   #新闻标题
        data['public_time'] = rowGet('pubTime').replace(' ','T')   #发布时间

        try:
            data['user_id'] = int(row._asdict().get('authorId'))     #作者标识id
        except  ValueError:     #无法转为数值，标记为-1
            data['user_id'] = -1
        try:
            data['nreply'] = int(row._asdict().get('comments', 0))   #评论数
        except ValueError:      #无法转为数值
            data['nreply'] = 0
        try:
            data['nlike'] = int(row._asdict().get('likes', 0))       #获赞数
        except ValueError:      #无法转为数值    
            data['nlike'] = 0

        datalist.append(data.copy())
        if len(datalist) % 500 == 0:
            jsondata['data'] = datalist
            #req = requests.post(post_url,json=jsondata,headers=headers)
            #print(req.text)
            datalist.clear()

    if datalist:
        jsondata['data'] = datalist
        #req = requests.post(post_url, json=jsondata,headers=headers)
        #print(req.text)
        datalist.clear()

def push(missionId):
    for relpath, dirs, files in os.walk('results'):
        if missionId == os.path.basename(relpath):
            for file in files:
                filePath=os.path.join(relpath,file)
                with open(filePath, 'r', encoding='utf-8-sig') as csvfile:
                    reader = csv.reader(csvfile)
                    Row = namedtuple('Row',next(reader))
                    if 'Comment' not in file:
                        pushContent(reader,Row,'http://10.10.28.199:9098/dataPush/saveInfos',missionId)
                    else:
                        pushComment(reader,Row,'http://10.10.28.199:9098/dataPush/saveComments')

#仅测试推送数据时使用
if __name__ ==  '__main__':
    push('EVGRQ')
    #import argparse
    #parser = argparse.ArgumentParser(description='推送该任务ID目录下的数据')
    #parser.add_argument('-i','-id',dest='id')

    #args = parser.parse_args()

    #print('开始推送ID为{}的任务'.format(args.id))
    #push(args.id)