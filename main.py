from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
import uuid
from db.abstract_redis import AbstractRedis

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

    # db 저장
    db = AbstractRedis().get()
    db.set(id, body.url)

    # todo - 만료 기한 구현 
    
    return JSONResponse({"short_url":id}, status_code=201)

@app.get("/{short_key}")
async def post_shorten(short_key:str):
    # db 불러오기

    db = AbstractRedis().get()
    url:bytes = db.get(short_key)
    if not url:
        return Response(status_code=404)
    
    url = url.decode()

    # todo - 조회수 구현

    return RedirectResponse(url, status_code=301)