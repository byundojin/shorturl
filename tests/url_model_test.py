import pytest 
from db.models.url_model import UrlModel
from db.redis_db import UrlRedis
import redis
from tests.conftest import _url1, _url2, _url3

date = [6,10,12,30,50]

@pytest.mark.parametrize(
    "url_model, url, is_exp, year, month, day, hour, minute, second",
    [
        (_url1, "example/1", False, *([None]*6)),
        (_url2, "example/2", True, 2030, *date),
        (_url3, "example/3", True, 2010, *date),
    ]
)
def test_url_model(url_model:UrlModel, url, is_exp, year, month, day, hour, minute, second):
    assert url_model.url == url
    assert url_model.is_exp == is_exp
    assert url_model.year == year
    assert url_model.month == month
    assert url_model.day == day
    assert url_model.hour == hour
    assert url_model.minute == minute
    assert url_model.second == second

redis_connect = True
try:
    UrlRedis()
except redis.ConnectionError:
    redis_connect = False

@pytest.mark.skipif(not redis_connect, reason="redis 연결 안됨")
@pytest.mark.parametrize(
    "url",
    [(_url1),(_url2),(_url3)]
)
def test_url_redis(url:UrlModel):
    id = UrlRedis().save(url)
    load_url = UrlRedis().get(id)
    assert url.b == load_url.b

