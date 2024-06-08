from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
import uuid
from db.redis_db import UrlRedis, ExpRedis
import datetime 

def get_uuid(name):
    namespace = uuid.NAMESPACE_DNS
    return uuid.uuid5(namespace, name).hex

app = FastAPI()

class UrlBody(BaseModel):
    url:str
    exp_date:str|None = None # 만료 기한

@app.post("/shorten")
async def post_shorten(body:UrlBody):
    id = get_uuid(body.url)

    # url_db 저장
    url_db = UrlRedis().get()
    url_db.set(id, body.url)

    # 만료 기한 구현 
    if body.exp_date:
        exp_db = ExpRedis().get()
        try:
            datetime.datetime.fromisoformat(body.exp_date)
        except:
            raise "iso 변환 x"
        exp_db.set(id, body.exp_date)
    
    return JSONResponse({"short_url":id}, status_code=201)

@app.get("/{short_key}")
async def post_shorten(short_key:str):
    # url_db 조회
    url_db = UrlRedis().get()
    url:bytes = url_db.get(short_key)

    if not url: # 조회 불가 시 404
        return Response(status_code=404)
    
    url = url.decode()

    # 만료 기간 확인
    exp_db = ExpRedis().get()
    exp:bytes = exp_db.get(short_key)
    if exp:
        exp = exp.decode()
        now = datetime.datetime.now()
        exp_time = datetime.datetime.fromisoformat(exp)

        if now > exp_time: # 기간 만료
            url_db.delete(short_key)
            exp_db.delete(short_key)
            return JSONResponse({"detail":"url 기간 만료"}, status_code=410)

    # todo - 조회수 구현

    return RedirectResponse(url, status_code=301)