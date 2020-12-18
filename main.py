#from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

import json
import subprocess

class Item(BaseModel):
    op_type: int
    id: int
    name: str
    sourceSite: list
    sourceUrl: str
    searchKeyword: list
    userId: int
    valid: int
    visible: int
    engineStatus: int

app = FastAPI()

@app.post('/sendMission')
def root(item: Item):
    keyword=','.join(item.searchKeyword)
    for site in item.sourceSite:
        if site == '微博':
            subprocess.Popen(['python','runSpider.py','-id',str(item.id),'-name','weiboSearch','-keyword',keyword])
        elif site == '贴吧':
            subprocess.Popen(['python','runSpider.py','-id',str(item.id),'-name','tiebaSearch','-keyword',keyword])
        elif site == '新闻':
            subprocess.Popen(['python','runSpider.py','-id',str(item.id),'-name','qq'])
            subprocess.Popen(['python','runSpider.py','-id',str(item.id),'-name','163'])
            subprocess.Popen(['python','runSpider.py','-id',str(item.id),'-name','sohu'])
    resp = json.dumps({"code ": 0,"message": "成功"},ensure_ascii=False)
    return item

