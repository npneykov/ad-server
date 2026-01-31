"""Database engine and session management."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()

# Configure connection arguments based on database type
if settings.effective_database_url.startswith('sqlite'):
    connect_args = {'check_same_thread': False}
else:
    connect_args = {}

engine = create_engine(
    settings.effective_database_url,
    echo=False,
    connect_args=connect_args,
)


def init_db() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session for dependency injection."""
    with Session(engine) as session:
        yield session
