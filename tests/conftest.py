# tests/conftest.py
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture(scope='function')
def session():
    """
    Provide a SQLModel Session for tests that need direct database access.
    Each test gets its own in-memory SQLite database.
    """
    engine = create_engine(
        'sqlite://',  # in-memory
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as test_session:
        # Override FastAPI's get_session dependency
        def _get_session():
            yield test_session

        app.dependency_overrides[get_session] = _get_session
        yield test_session
        app.dependency_overrides.pop(get_session, None)
