import os
from dotenv import load_dotenv
import redis

load_dotenv()

class AbstractRedis():
    def __new__(cls, *args, **kwargs):
        REDIS_HOST = os.getenv("REDIS_HOST")
        REDIS_PORT = os.getenv("REDIS_PORT")
        REDIS_DATABASE = kwargs["database"]
        cls._instance = super().__new__(cls)
        cls._instance._db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)
        return cls._instance
    
    def __init__(self) -> None:
        self._db:redis.Redis

    def get(self):
        return self._db


