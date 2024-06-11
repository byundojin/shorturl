from fastapi.testclient import TestClient

import pytest

from fastapi import APIRouter, Response
from db.redis_db import UrlRedis
import redis

router = APIRouter(
    prefix="/example"
)

@router.get("/{number}")
async def get_example(number):
    """test 코드 redirect 되는 곳"""
    return Response(status_code=200)

from main import app

client = TestClient(app)

redis_connect = True
try:
    UrlRedis()
except redis.ConnectionError:
    redis_connect = False

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
@pytest.mark.parametrize(
        "body, status_code",
        [
            pytest.param({
                "url":"https://velog.io/@byundojin/posts"
            }, 201, id="기간 x"),
            pytest.param({
                "url":"https://velog.io/@byundojin/posts",
                "exp_date":"2030-06-10T12:30:50"
            }, 201, id="기간 o, 만료 x"),
            pytest.param({
                "url":"https://velog.io/@byundojin/posts",
                "exp_date":"2010-06-10T12:30:50"
            }, 410, id="기간 o, 만료 o")
        ]
)
def test_post_shorten(body, status_code):
    response = client.post("/shorten", json=body)
    assert response.status_code == status_code



@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_url_1(url1_id): # 기간 x
    response = client.get(f"/{url1_id}")
    assert response.status_code == 200

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_url_2(url2_id): # 기간 o, 만료 x
    response = client.get(f"/{url2_id}")
    assert response.status_code == 200

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_url_3(url3_id): # 기간 x, 만료 o
    response = client.get(f"/{url3_id}")
    assert response.status_code == 410

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_url_4(): # 존재 x
    response = client.get(f"/nothing")
    assert response.status_code == 404

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_stat_1(url1_id): # 조회수 확인 및 조회수 증가 확인
    response = client.get(f"/stats/{url1_id}")
    assert response.status_code == 200
    assert response.json()['views'] == 0

    # 조회
    response = client.get(f"/{url1_id}")
    assert response.status_code == 200
    
    # 조회수 증가
    response = client.get(f"/stats/{url1_id}")
    assert response.status_code == 200
    assert response.json()['views'] == 1

@pytest.mark.skipif(redis_connect, reason="redis 연결 안됨")
def test_get_stat_2(url3_id): # 만료
    response = client.get(f"/stats/{url3_id}")
    assert response.status_code == 410