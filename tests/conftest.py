# tests/conftest.py
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from db import get_session
from main import app


@pytest.fixture(autouse=True)
def override_db():
    """
    Give every test its own in-memory SQLite database and override the app's
    get_session() dependency to use it. Ensures tables exist before requests.
    """
    engine = create_engine(
        'sqlite://',  # in-memory
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,  # keep one in-memory DB per test function
    )
    SQLModel.metadata.create_all(engine)

    def _get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_session, None)
