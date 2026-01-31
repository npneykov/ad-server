"""Ad selection and weighted choice services."""

from collections.abc import Sequence
import random
from typing import TypeVar

from sqlmodel import Session

from app.models import Ad, Impression
from app.services.analytics import range_counts

T = TypeVar('T')


def weighted_choice(items: Sequence[T], weights: Sequence[int | float]) -> T:
    """
    Select an item based on weighted probability.

    Args:
        items: Sequence of items to choose from.
        weights: Corresponding weights for each item.

    Returns:
        Selected item based on weighted random choice.
    """
    total = sum(weights)
    if total <= 0:
        # Fallback: equal chance if weights invalid
        return items[0]
    r = random.uniform(0, total)
    upto = 0.0
    for item, weight in zip(items, weights, strict=False):
        upto += weight
        if r <= upto:
            return item
    return items[-1]  # Safety fallback


def calculate_ad_weights(
    ads: Sequence[Ad],
    imps: dict[int, int],
    clks: dict[int, int],
) -> list[float]:
    """
    Calculate CTR-boosted weights for ads.

    Args:
        ads: List of ads to calculate weights for.
        imps: Dictionary of ad_id -> impression count.
        clks: Dictionary of ad_id -> click count.

    Returns:
        List of calculated weights corresponding to each ad.
    """
    weights = []
    for ad in ads:
        try:
            i = imps.get(ad.id, 0)  # type: ignore
            c = clks.get(ad.id, 0)  # type: ignore
            ctr = (c / i) if i > 0 else 0
            boost = 1.0 + min(ctr * 10, 2.0)
            # Exploration bonus for new ads
            if i < 100:
                boost *= 1.5
            weight = ad.weight * boost
        except ZeroDivisionError:
            weight = ad.weight
        weights.append(weight)
    return weights


def select_ad_for_zone(session: Session, ads: list[Ad]) -> Ad:
    """
    Select an ad from the given list using weighted CTR-based selection.

    Args:
        session: Database session.
        ads: List of active ads for the zone.

    Returns:
        Selected ad.
    """
    imps, clks = range_counts(session, days=7)
    weights = calculate_ad_weights(ads, imps, clks)
    return weighted_choice(ads, weights)


def record_impression(session: Session, ad_id: int) -> None:
    """Record an impression for the given ad."""
    session.add(Impression(ad_id=ad_id))
    session.commit()
