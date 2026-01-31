from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

# Create a test database in memory
test_engine = create_engine('sqlite:///:memory:')
SQLModel.metadata.create_all(test_engine)


# Dependency override for the test session
def override_get_session():
    with Session(test_engine) as session:
        yield session


# Apply the dependency override
app.dependency_overrides[get_session] = override_get_session

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield


def test_example_render_click():
    response = client.get('/some-endpoint')  # Replace with your actual endpoint
    assert response.status_code == 200
    assert response.json() == {'message': 'Success'}  # Replace with expected response
