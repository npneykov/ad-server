from datetime import datetime, timedelta

from sqlmodel import Session

from main import (
    range_counts,
)
from models import Ad, Click, Impression, Zone


def test_range_counts(session: Session):
    # Seed a zone + ad
    z = Zone(name='Z', width=1, height=1)
    session.add(z)
    session.commit()
    session.refresh(z)
    assert z.id is not None, 'Zone ID should not be None'
    a = Ad(zone_id=z.id, html='<img>', url='https://x', weight=1)
    session.add(a)
    session.commit()
    session.refresh(a)
    assert a.id is not None, 'Ad ID should not be None'

    # recent impressions & clicks
    now = datetime.utcnow()
    session.add_all(
        [
            Impression(ad_id=a.id, timestamp=now - timedelta(days=1)),
            Impression(ad_id=a.id, timestamp=now - timedelta(days=2)),
            Click(ad_id=a.id, timestamp=now - timedelta(days=1)),
        ]
    )
    # old impression (outside window)
    session.add(Impression(ad_id=a.id, timestamp=now - timedelta(days=30)))
    session.commit()

    imps, clks = range_counts(session, days=7)
    assert imps.get(a.id) == 2
    assert clks.get(a.id) == 1

    imps_2, clks_2 = range_counts(session, days=1)
    # Only the impression/click at now-1 day qualifies; the one at -2 days drops
    assert imps_2.get(a.id) == 1
    assert clks_2.get(a.id) == 1
