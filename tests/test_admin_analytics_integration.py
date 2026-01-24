from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from main import app
from models import Ad, Click, Impression, Zone


@pytest.fixture(autouse=True)
def _set_admin_key(monkeypatch):
    monkeypatch.setenv('ADMIN_KEY', 'testkey')


def test_admin_analytics_renders(session: Session):
    # seed some data
    z = Zone(name='Top', width=728, height=90)
    session.add(z)
    session.commit()
    session.refresh(z)
    assert z.id is not None, 'Zone ID should not be None'
    a = Ad(zone_id=z.id, html='<img>', url='https://example.com', weight=1)
    session.add(a)
    session.commit()
    session.refresh(a)
    assert a.id is not None, 'Ad ID should not be None'
    session.add_all([Impression(ad_id=a.id), Click(ad_id=a.id)])
    session.commit()

    with TestClient(app) as client:
        r = client.get('/admin/analytics?days=7', headers={'X-ADMIN-KEY': 'testkey'})
        assert r.status_code == 200
        text = r.text
        # Just verify the page renders with data
        assert str(a.id) in text
        assert '100.00' in text  # CTR percentage
