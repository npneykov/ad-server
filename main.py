from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from db import get_session
from models import Ad, Click, Impression, Zone  # add Impression, Click

app = FastAPI()

templates = Jinja2Templates(directory='templates')


# -------- util --------
def weighted_choice(items, weights):
    import random

    total = sum(weights)
    if total <= 0:
        # fallback to first item to avoid errors
        return items[0]
    r = random.uniform(0, total)
    upto = 0
    # remove strict=False for wider Py compat
    for item, weight in zip(items, weights, strict=False):
        if upto + weight >= r:
            return item
        upto += weight
    # safety fallback
    return items[-1]


# -------- Zones CRUD --------
@app.post('/zones/', response_model=Zone)
def create_zone(zone: Zone, session: Session = Depends(get_session)):
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


@app.get('/zones/', response_model=list[Zone])
def list_zones(session: Session = Depends(get_session)):
    return session.exec(select(Zone)).all()


@app.get('/zones/{zone_id}', response_model=Zone)
def get_zone(zone_id: int, session: Session = Depends(get_session)):
    zone = session.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail='Zone not found')
    return zone


@app.put('/zones/{zone_id}', response_model=Zone)
def update_zone(
    zone_id: int,
    updated: Zone,
    session: Session = Depends(get_session),
):
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


@app.delete('/zones/{zone_id}')
def delete_zone(zone_id: int, session: Session = Depends(get_session)):
    zone = session.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail='Zone not found')
    session.delete(zone)
    session.commit()
    return {'ok': True}


# -------- Ads CRUD --------
@app.post('/ads/', response_model=Ad)
def create_ad(ad: Ad, session: Session = Depends(get_session)):
    # ensure zone exists
    if not session.get(Zone, ad.zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone_id')
    session.add(ad)
    session.commit()
    session.refresh(ad)
    return ad


@app.get('/ads/', response_model=list[Ad])
def list_ads(session: Session = Depends(get_session)):
    return session.exec(select(Ad)).all()


@app.get('/ads/{ad_id}', response_model=Ad)
def get_ad(ad_id: int, session: Session = Depends(get_session)):
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    return ad


@app.put('/ads/{ad_id}', response_model=Ad)
def update_ad(
    ad_id: int,
    updated: Ad,
    session: Session = Depends(get_session),
):
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


@app.delete('/ads/{ad_id}')
def delete_ad(ad_id: int, session: Session = Depends(get_session)):
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    session.delete(ad)
    session.commit()
    return {'ok': True}


# -------- Render & Click (iframe, Python-only) --------
@app.get('/render', response_class=HTMLResponse)
def render_ad(
    request: Request,
    zone: int = Query(..., description='Zone ID'),
    session: Session = Depends(get_session),
):
    z = session.get(Zone, zone)
    if not z:
        raise HTTPException(status_code=404, detail='Zone not found')

    ads = session.exec(select(Ad).where(Ad.zone_id == zone)).all()
    if not ads:
        raise HTTPException(status_code=404, detail='No ads for zone')

    ad = weighted_choice(ads, [a.weight for a in ads])  # <-- fixed indent

    # Log impression
    if ad.id is None:
        raise HTTPException(status_code=500, detail='Ad ID is missing')
    session.add(Impression(ad_id=ad.id))
    session.commit()

    # Click URL (through our redirect)
    click_url = f'/click?id={ad.id}'

    # Render full-page HTML for the iframe
    return templates.TemplateResponse(
        'render.html',
        {
            'request': request,
            'html': ad.html,  # creative HTML
            'click_url': click_url,  # our tracking redirect
        },
        status_code=200,
    )


@app.get('/click')
def click(
    id: int = Query(..., description='Ad ID'),
    session: Session = Depends(get_session),
):
    ad = session.get(Ad, id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')

    # Log click
    if ad.id is None:
        raise HTTPException(status_code=500, detail='Ad ID is missing')
    session.add(Click(ad_id=ad.id))
    session.commit()

    return RedirectResponse(url=ad.url, status_code=302)


@app.get('/some-endpoint')
def some_endpoint():
    return {'message': 'Success'}
