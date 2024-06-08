import pytest 
import redis

def test_redis(db:redis.Redis):
    db.set("A", "B")
    assert db.get("A") == "B".encode()



