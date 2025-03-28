import pytest
from main import app
from tortoise.contrib.fastapi import register_tortoise
from fastapi.testclient import TestClient
from config import settings

@pytest.fixture(scope="session", autouse=True)
def init_db():
    register_tortoise(
        app,
        config=settings.DATABASE_CONFIG,
    )
    yield


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

def test_db_time(client):
    response = client.get("/db_time")
    assert response.text != "Error"

def test_query(client):
    response = client.get("/query/12")
    data = response.json()
    assert data["status"] == 200
    assert data["id_data"]["status"] == 200
    assert data["score_data"]["status"] == 200
    assert data["score_data"]["myanimelist"]["status"] == 200
    assert data["bangumi_data"]["status"] == 200
