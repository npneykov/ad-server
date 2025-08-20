from sqlmodel import Session, SQLModel, create_engine

# SQLite file in project root
engine = create_engine('sqlite:///./adserver.db', echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
