from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel

from db import engine
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # Drop and recreate all tables before each test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


def test_create_and_get_zone():
    resp = client.post('/zones/', json={'name': 'Z1', 'width': 100, 'height': 100})
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] and data['name'] == 'Z1'

    get_resp = client.get(f"/zones/{data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()['width'] == 100


def test_list_zones_empty():
    resp = client.get('/zones/')
    assert resp.status_code == 200
    assert resp.json() == []
