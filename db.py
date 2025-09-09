import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

os.makedirs('data', exist_ok=True)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/adserver.db')
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
