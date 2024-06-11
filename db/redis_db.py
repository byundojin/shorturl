from db.models.url_model import UrlCreator, UrlModel
from dotenv import load_dotenv
import os
import datetime
import redis

load_dotenv()

import uuid
def get_uuid():
    return uuid.uuid4().hex

class UrlRedis():
    def __init__(self) -> None:
        self._db:redis.Redis = redis.Redis(host=os.getenv("REDIS_HOST"), 
                                           port=os.getenv("REDIS_PORT"), 
                                           db=os.getenv("REDIS_DATABASE_URL"))

    def get_db(self) -> redis.Redis:
        return self._db
    
    def save(self, url:UrlModel, id:str|None = None) -> str:
        if not id:
            id = get_uuid()
        self.get_db().set(id, bytes(url.b))
        return id
    
    def get(self, key:str) -> UrlModel|None:
        url_bytes = self.get_db().get(key)
        if url_bytes:
            return UrlCreator().create_byte(url_bytes)
        else:
            return None
    
    def delete(self, key:str) -> None:
        return self.get_db().delete(key)
    
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(deamon=True)

@sched.scheduled_job('interval', minutes=5, id='delete-exp-date') # 5분 마다 만료기간 확인 후 삭제
def delete_exp_date():
    print("만료키 정리 시작")
    try:
        for key in UrlRedis().get_db().keys():
            url = UrlRedis().get(key)
            if not url.is_exp:
                continue
            if url.datetime > datetime.datetime.now():
                UrlRedis().delete(key)
    except:
        print("Redis 연결 불가")
        return
    print("만료키 정리 끝")

sched.start()
