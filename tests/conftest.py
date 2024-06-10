import pytest
from db.models.url_model import UrlCreator
from db.redis_db import UrlRedis


# 기간 x
_url1 = UrlCreator().create("example/1")

# 기간 o 만료 x
_url2 = UrlCreator().set_date("2030-06-10T12:30:50").create("example/2")

# 기간 o 만료 o
_url3 = UrlCreator().set_date("2010-06-10T12:30:50").create("example/3")

@pytest.fixture
def url1_id():
    UrlRedis().get_db().flushdb()
    id = UrlRedis().save(_url1)
    yield id

@pytest.fixture
def url2_id():
    UrlRedis().get_db().flushdb()
    id = UrlRedis().save(_url2)
    yield id
    
@pytest.fixture
def url3_id():
    UrlRedis().get_db().flushdb()
    id = UrlRedis().save(_url3)
    yield id