import pytest
from sqlmodel import Session, SQLModel, create_engine

from models import Ad, Zone


@pytest.fixture(name='session')
def session_fixture(tmp_path):
    db_file = tmp_path / 'test.db'
    engine = create_engine(f'sqlite:///{db_file}')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_zone_crud(session):
    z = Zone(name='Banner', width=728, height=90)
    session.add(z)
    session.commit()
    session.refresh(z)
    assert z.id is not None
    fetched = session.get(Zone, z.id)
    assert fetched.name == 'Banner'


def test_ad_crud(session):
    # first create a zone
    z = Zone(name='Side', width=300, height=250)
    session.add(z)
    session.commit()
    session.refresh(z)
    assert z.id is not None, 'Zone ID should not be None'
    ad = Ad(zone_id=z.id, html='<img/>', url='https://x', weight=2)
    session.add(ad)
    session.commit()
    session.refresh(ad)
    assert ad.id is not None and ad.weight == 2
    fetched = session.get(Ad, ad.id)
    assert fetched.zone_id == z.id
