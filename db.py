import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'development')

if APP_ENV == 'development':
    # Local dev DB (SQLite)
    DATABASE_URL = os.getenv('LOCAL_DATABASE_URL', 'sqlite:///./adserver.db')
    connect_agrs = {'check_same_thread': False}
else:
    # Production DB (PostgreSQL)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError('DATABASE_URL environment variable is not set.')
    connect_agrs = {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_agrs)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
