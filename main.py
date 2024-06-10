from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from db.redis_db import UrlRedis
from db.models.url_model import UrlCreator, DateValueError, UrlModel
import datetime 
import redis


app = FastAPI()

# test용
from tests.main_test import router
app.include_router(router)

class UrlBody(BaseModel):
    url:str
    exp_date:str|None = None # 만료 기한

def check_exp(url:UrlModel) -> bool:
    """만료 기간 확인 | 만료시 -> False"""
    if url.is_exp:
        time = datetime.datetime.now()
        if url.datetime < time:
            return False
    return True    
    
@app.post("/shorten")
async def post_shorten(body:UrlBody):
    # url 생성
    url_creator = UrlCreator()
    if body.exp_date:
        try:
            url_creator.set_date(body.exp_date)
        except DateValueError:
            return # 잘못된 exp date 형식
    url = url_creator.create(body.url)

    # 기간 확인
    if not check_exp(url):
        return Response(status_code=410)

    # url 저장
    try:
        url_id = UrlRedis().save(url)
    except redis.ConnectionError:
        return # redis 연결 불가
    
    return JSONResponse({"short_url" : url_id}, 201)

@app.get("/{short_key}")
async def get_url(short_key:str):
    # url 조회
    try:
        url = UrlRedis().get(short_key)
    except redis.ConnectionError:
        return # redis 연결 불가
    
    if not url:
        return Response(status_code=404)
    
    # 기간 확인
    if not check_exp(url):
        UrlRedis().delete(short_key)
        return Response(status_code=410)
        
    # 조회수 증가
    url.view += 1

    # 저장
    UrlRedis().save(url, short_key)

    return RedirectResponse(url.url, 301)


@app.get("/stats/{short_key}")
async def get_stat(short_key:str):
    # url 조회
    try:
        url = UrlRedis().get(short_key)
    except redis.ConnectionError:
        return # redis 연결 불가
    
    if not url:
        return Response(status_code=404)
    
    # 기간 확인
    if not check_exp(url):
        UrlRedis().delete(short_key)
        return Response(status_code=410)
        
    return JSONResponse({"views": url.view}, status_code=200)