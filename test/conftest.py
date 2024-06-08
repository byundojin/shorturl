import pytest
from db import DB_Redis

@pytest.fixture
def db():
    db = DB_Redis().get()
    yield db
    db.flushdb()
