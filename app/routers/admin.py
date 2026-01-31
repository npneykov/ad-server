"""Admin HTML UI routes."""

import logging
import os

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from app.dependencies import SessionDep, verify_admin_key
from app.models import Ad, Zone
from app.services.analytics import calculate_ctr_data

router = APIRouter(prefix='/admin', tags=['Admin'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse, dependencies=[Depends(verify_admin_key)])
def admin_home(request: Request):
    """Admin home page."""
    return templates.TemplateResponse(
        request=request, name='admin/base.html', context={'page': 'home'}
    )


@router.get(
    '/analytics',
    response_class=HTMLResponse,
    dependencies=[Depends(verify_admin_key)],
)
def admin_analytics(
    request: Request,
    session: SessionDep,
    days: int = Query(7, ge=1, le=90),
):
    """Admin analytics page."""
    try:
        ctr = calculate_ctr_data(session, days=days)
        return templates.TemplateResponse(
            request=request,
            name='admin/analytics.html',
            context={'ctr': ctr},
        )
    except Exception as e:
        logging.exception('Error in /admin/analytics')
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    '/zones',
    response_class=HTMLResponse,
    dependencies=[Depends(verify_admin_key)],
)
def admin_zones(request: Request, session: SessionDep):
    """Admin zones list page."""
    zones = session.exec(select(Zone)).all()
    return templates.TemplateResponse(
        request=request, name='admin/zones.html', context={'zones': zones}
    )


@router.post('/zones', dependencies=[Depends(verify_admin_key)])
def admin_zones_create(
    session: SessionDep,
    name: str = Form(...),
    width: int = Form(...),
    height: int = Form(...),
):
    """Create a new zone via form."""
    z = Zone(name=name, width=width, height=height)
    session.add(z)
    session.commit()
    return RedirectResponse(url='/admin/zones', status_code=303)


@router.post('/zones/{zone_id}/delete', dependencies=[Depends(verify_admin_key)])
def admin_zones_delete(zone_id: int, session: SessionDep):
    """Delete a zone."""
    z = session.get(Zone, zone_id)
    if not z:
        raise HTTPException(status_code=404, detail='Zone not found')
    session.delete(z)
    session.commit()
    return RedirectResponse(url='/admin/zones', status_code=303)


@router.get(
    '/ads', response_class=HTMLResponse, dependencies=[Depends(verify_admin_key)]
)
def admin_ads(
    request: Request,
    session: SessionDep,
    zone: int | None = Query(default=None),
):
    """Admin ads list page."""
    try:
        # Fetch all zones
        zones = session.exec(select(Zone)).all() or []

        # Fetch ads (filter by active + optional zone)
        query = select(Ad)
        if hasattr(Ad, 'is_active'):
            query = query.where(Ad.is_active)
        if zone:
            query = query.where(Ad.zone_id == zone)

        ads = session.exec(query).all() or []

        return templates.TemplateResponse(
            request=request,
            name='admin/ads.html',
            context={
                'zones': zones,
                'ads': ads,
                'zone_filter': zone,
            },
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return HTMLResponse(f'Error: {e}', status_code=500)


@router.post('/ads', dependencies=[Depends(verify_admin_key)])
def admin_ads_create(
    session: SessionDep,
    zone_id: int = Form(...),
    html: str = Form(...),
    url: str = Form(...),
    weight: int = Form(1),
):
    """Create a new ad via form."""
    if not session.get(Zone, zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone_id')
    a = Ad(zone_id=zone_id, html=html, url=url, weight=weight)
    session.add(a)
    session.commit()
    return RedirectResponse(url='/admin/ads', status_code=303)


@router.post('/ads/{ad_id}/delete', dependencies=[Depends(verify_admin_key)])
def admin_ads_delete(ad_id: int, session: SessionDep):
    """Delete an ad."""
    a = session.get(Ad, ad_id)
    if not a:
        raise HTTPException(status_code=404, detail='Ad not found')
    session.delete(a)
    session.commit()
    return RedirectResponse(url='/admin/ads', status_code=303)


@router.post('/ads/{ad_id}/disable', dependencies=[Depends(verify_admin_key)])
def admin_ads_disable(ad_id: int, session: SessionDep):
    """Disable an ad."""
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    ad.is_active = False
    session.add(ad)
    session.commit()
    return RedirectResponse(url='/admin/analytics', status_code=303)


@router.post('/ads/{ad_id}/enable', dependencies=[Depends(verify_admin_key)])
def admin_ads_enable(ad_id: int, session: SessionDep):
    """Enable an ad."""
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    ad.is_active = True
    session.add(ad)
    session.commit()
    return RedirectResponse(url='/admin/analytics', status_code=303)


@router.get('/debug/region')
def get_region(request: Request):
    """Debug endpoint to show server region."""
    # Fly.io provides region info via env var FLY_REGION
    region = os.getenv('FLY_REGION', 'unknown')
    client_ip = request.client.host if request.client else 'unknown'

    return {
        'region': region,
        'client_ip': client_ip,
        'message': f'Served from {region.upper()} region',
    }


@router.get('/debug/db')
def debug_db():
    """Debug endpoint to check database configuration."""
    url = os.getenv('DATABASE_URL', '')
    return {
        'DATABASE_URL': url,
        'data_exists': os.path.exists('/data/adserver.db'),
        'app_exists': os.path.exists('/app/adserver.db'),
    }
