"""REST API endpoints for zones and ads."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlmodel import select

from app.dependencies import SessionDep
from app.models import Ad, Click, Impression, Zone
from app.services.analytics import range_counts

router = APIRouter(tags=['API'])


# -------- Zones CRUD --------
@router.post('/zones/', response_model=Zone)
def create_zone(zone: Zone, session: SessionDep):
    """Create a new zone."""
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@router.get('/zones/', response_model=list[Zone])
def list_zones(session: SessionDep):
    """List all zones."""
    return session.exec(select(Zone)).all()


@router.get('/zones/{zone_id}', response_model=Zone)
def get_zone(zone_id: int, session: SessionDep):
    """Get a zone by ID."""
    zone = session.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail='Zone not found')
    return zone


@router.put('/zones/{zone_id}', response_model=Zone)
def update_zone(zone_id: int, updated: Zone, session: SessionDep):
    """Update a zone."""
    zone = session.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail='Zone not found')
    zone.name = updated.name
    zone.width = updated.width
    zone.height = updated.height
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@router.delete('/zones/{zone_id}')
def delete_zone(zone_id: int, session: SessionDep):
    """Delete a zone."""
    zone = session.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail='Zone not found')
    session.delete(zone)
    session.commit()
    return {'ok': True}


# -------- Ads CRUD --------
@router.post('/ads/', response_model=Ad)
def create_ad(ad: Ad, session: SessionDep):
    """Create a new ad."""
    # Ensure zone exists
    if not session.get(Zone, ad.zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone_id')
    session.add(ad)
    session.commit()
    session.refresh(ad)
    return ad


@router.get('/ads/', response_model=list[Ad])
def list_ads(session: SessionDep):
    """List all ads."""
    return session.exec(select(Ad)).all()


@router.get('/ads/{ad_id}', response_model=Ad)
def get_ad(ad_id: int, session: SessionDep):
    """Get an ad by ID."""
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    return ad


@router.put('/ads/{ad_id}', response_model=Ad)
def update_ad(ad_id: int, updated: Ad, session: SessionDep):
    """Update an ad."""
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    ad.html = updated.html
    ad.url = updated.url
    ad.weight = updated.weight
    ad.zone_id = updated.zone_id
    session.add(ad)
    session.commit()
    session.refresh(ad)
    return ad


@router.delete('/ads/{ad_id}')
def delete_ad(ad_id: int, session: SessionDep):
    """Delete an ad."""
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    session.delete(ad)
    session.commit()
    return {'ok': True}


# -------- Stats API --------
@router.get('/api/stats.json')
def stats_api(session: SessionDep):
    """Get stats for all ads (compact format)."""
    imps, clks = range_counts(session, days=7)
    ads = session.exec(select(Ad)).all()

    return [
        {
            'id': ad.id,
            'zone_id': ad.zone_id,
            'html_snippet': ad.html[:100] + '...' if len(ad.html) > 100 else ad.html,
            'impressions': imps.get(ad.id, 0),  # type: ignore
            'clicks': clks.get(ad.id, 0),  # type: ignore
            'ctr': round((clks.get(ad.id, 0) / imps.get(ad.id, 1)) * 100, 2)  # type: ignore
            if imps.get(ad.id)  # type: ignore
            else 0.0,
        }
        for ad in ads
    ]


@router.get('/stats.json', response_class=JSONResponse)
def public_stats(session: SessionDep):
    """Get public stats for all ads (detailed format)."""
    ads = session.exec(select(Ad)).all()

    data = []
    for ad in ads:
        impressions = (
            session.exec(
                select(func.count(Impression.id)).where(Impression.ad_id == ad.id)  # type: ignore
            ).first()
            or 0
        )

        clicks = (
            session.exec(
                select(func.count(Click.id)).where(Click.ad_id == ad.id)  # type: ignore
            ).first()
            or 0
        )

        ctr = round((clicks / impressions * 100.0), 2) if impressions else 0.0

        data.append(
            {
                'ad_id': ad.id,
                'zone_id': ad.zone_id,
                'impressions': impressions,
                'clicks': clicks,
                'ctr': ctr,
                'url': ad.url,
            }
        )

    return {'ads': data}


# -------- Health Check --------
@router.get('/healthz')
def healthz():
    """Health check endpoint."""
    return {'ok': True}


@router.get('/some-endpoint')
def some_endpoint():
    """Test endpoint."""
    return {'message': 'Success'}
