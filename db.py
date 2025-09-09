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


def ensure_is_active_column():
    """Add is_active column to ad table if missing (SQLite only)."""
    if DATABASE_URL.startswith('sqlite'):
        with engine.connect() as conn:
            # Get existing column names
            result = conn.exec_driver_sql('PRAGMA table_info(ad)').all()
            cols = [row[1] for row in result]  # row[1] = column name
            if 'is_active' not in cols:
                conn.exec_driver_sql(
                    'ALTER TABLE ad ADD COLUMN is_active BOOLEAN DEFAULT 1'
                )
                conn.exec_driver_sql(
                    'UPDATE ad SET is_active = 1 WHERE is_active IS NULL'
                )
