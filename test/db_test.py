import pytest 
import redis

def test_url_redis(url_db:redis.Redis):
    url_db.set("A", "B")
    assert url_db.get("A") == "B".encode()

def test_exp_redis(exp_db:redis.Redis):
    exp_db.set("A", "B")
    assert exp_db.get("A") == "B".encode()



