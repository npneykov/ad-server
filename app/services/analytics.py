"""Analytics and statistics services."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Ad, Click, Impression


def range_counts(
    session: Session, days: int = 7
) -> tuple[dict[int, int], dict[int, int]]:
    """
    Get impression and click counts for the last N days.

    Returns:
        Tuple of (impressions_dict, clicks_dict) mapping ad_id to count.
    """
    since = datetime.now(UTC) - timedelta(days=days)

    imps_rows = session.exec(
        select(Impression.ad_id, func.count(Impression.id))  # type: ignore
        .where(Impression.timestamp >= since)
        .group_by(Impression.ad_id)  # type: ignore
    ).all()

    clicks_rows = session.exec(
        select(Click.ad_id, func.count(Click.id))  # type: ignore
        .where(Click.timestamp >= since)
        .group_by(Click.ad_id)  # type: ignore
    ).all()

    imps = {ad_id: n for ad_id, n in imps_rows}
    clks = {ad_id: n for ad_id, n in clicks_rows}
    return imps, clks


def calculate_ctr_data(
    session: Session, days: int = 7
) -> dict[int, dict[str, int | float]]:
    """
    Calculate CTR data for all active ads.

    Returns:
        Dictionary mapping ad_id to {impressions, clicks, ctr}.
    """
    imps, clks = range_counts(session, days=days)

    # Get active ads only if field exists
    query = select(Ad)
    if hasattr(Ad, 'is_active'):
        query = query.where(Ad.is_active)

    ads = session.exec(query).all() or []

    ctr_data: dict[int, dict[str, int | float]] = {}
    for ad in ads:
        i = imps.get(ad.id, 0)  # type: ignore
        c = clks.get(ad.id, 0)  # type: ignore
        ctr_data[ad.id] = {  # type: ignore
            'impressions': i,
            'clicks': c,
            'ctr': (c / i) if i else 0.0,
        }

    return ctr_data
