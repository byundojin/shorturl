from db.abstract_redis import AbstractRedis
from dotenv import load_dotenv
import os

load_dotenv()

class UrlRedis(AbstractRedis):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, database=os.getenv("REDIS_DATABASE_URL"))
        return cls._instance

class ExpRedis(AbstractRedis):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, database=os.getenv("REDIS_DATABASE_Exp"))
        return cls._instance