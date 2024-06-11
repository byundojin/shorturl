from fastapi import FastAPI, Body, Path
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, Field
from db.redis_db import UrlRedis
from db.models.url_model import UrlCreator, DateValueError, UrlModel
import datetime 
import redis
from typing import Annotated

app = FastAPI()

# test용
from tests.main_test import router
app.include_router(router)

class UrlBody(BaseModel):
    url:str = Field(examples=["https://velog.io/@byundojin/posts"], title="원본 url")
    exp_date:str|None = Field(default=None, examples=["2024-07-08T15:58:01"], title="만료 기한", description="ISO 8601 표기법으로 보내야합니다.")
    
def check_exp(url:UrlModel) -> bool:
    """만료 기간 확인 | 만료시 -> False"""
    if url.is_exp:
        time = datetime.datetime.now()
        if url.datetime < time:
            return False
    return True    

url_body_example={
    "기간 x": {
        "summary": "기간 x",
        "description": "만료 기간 없음",
        "value": {
            "url":"https://velog.io/@byundojin/posts"
        },
    },
    "기간 o, 만료 x": {
        "summary": "기간 o, 만료 x",
        "description": "만료 기간이 지정되었지만, 만료되지 않음",
        "value": {
            "url":"https://velog.io/@byundojin/posts",
            "exp_date":"2024-07-08T15:58:01"
        },
    },
    "기간 o, 만료 o": {
        "summary": "기간 o, 만료 o",
        "description": "만료 기간이 지정되었고, 기간이 만료됨",
        "value": {
            "url":"https://velog.io/@byundojin/posts",
            "exp_date":"2024-06-10T17:31:00"
        },
    },
}
    
@app.post("/shorten")
async def post_shorten(body:Annotated[UrlBody, Body(openapi_examples=url_body_example)]):
    """short url 생성"""
    # url 생성
    url_creator = UrlCreator()
    if body.exp_date:
        try:
            url_creator.set_date(body.exp_date)
        except DateValueError:
            return JSONResponse({"detail":"exp_date가 ISO 8601 표기법을 따르지 않음"}, status_code=400)
    url = url_creator.create(body.url)

    # 기간 확인
    if not check_exp(url):
        return JSONResponse({"detail":"기간 만료"},status_code=410)

    # url 저장
    try:
        url_id = UrlRedis().save(url)
    except redis.ConnectionError:
        return JSONResponse({"detail":"redis 연결 불가"}, status_code=503)
    
    return JSONResponse({"short_url" : url_id}, 201)

@app.get("/{short_key}")
async def get_url(short_key:str = Path(title="짧은 url")):
    """원본 url redirect"""
    # url 조회
    try:
        url = UrlRedis().get(short_key)
    except redis.ConnectionError:
        return JSONResponse({"detail":"redis 연결 불가"}, status_code=503)
    
    if not url:
        return JSONResponse({"detail":"url을 찾을 수 없음"},status_code=404)
    
    # 기간 확인
    if not check_exp(url):
        UrlRedis().delete(short_key)
        return JSONResponse({"detail":"기간 만료"},status_code=410)
        
    # 조회수 증가
    url.view += 1

    # 저장
    UrlRedis().save(url, short_key)

    return RedirectResponse(url.url, 301)


@app.get("/stats/{short_key}")
async def get_stat(short_key:str = Path(title="짧은 url")):
    "url 조회수 조회"
    # url 조회
    try:
        url = UrlRedis().get(short_key)
    except redis.ConnectionError:
        return JSONResponse({"detail":"redis 연결 불가"}, status_code=503)
    
    if not url:
        return Response(status_code=404)
    
    # 기간 확인
    if not check_exp(url):
        UrlRedis().delete(short_key)
        return Response(status_code=410)
        
    return JSONResponse({"views": url.view}, status_code=200)