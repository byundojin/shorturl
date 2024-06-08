import pytest
from db.redis_db import UrlRedis, ExpRedis

@pytest.fixture
def exp_db():
    db = UrlRedis().get()
    db.flushdb() # test 전 db 초기화
    yield db
    db.flushdb() # test 후 db 초기화

@pytest.fixture
def exp_db():
    db = ExpRedis().get()
    db.flushdb() # test 전 db 초기화
    yield db
    db.flushdb() # test 후 db 초기화
