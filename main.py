from datetime import datetime, timedelta
import logging
import os

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from db import engine, get_session
from models import Ad, Click, Impression, Zone  # add Impression, Click

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
app = FastAPI()

templates = Jinja2Templates(directory='templates')
ADSTERRA_SMARTLINK = (
    'https://www.revenuecpmgate.com/kh3axptg1?key=1685a081c46f9b5d7aaa7abf4d050eb3'
)
BLOG_DIR = os.path.join('templates', 'public')


@app.on_event('startup')
def on_startup():
    SQLModel.metadata.create_all(engine)


def verify_admin_key(x_admin_key: str | None = Header(default=None)):
    expected = os.getenv('ADMIN_KEY')
    if not expected:
        # For local dev: allow if no key set
        return True
    if x_admin_key == expected:
        return True
    raise HTTPException(status_code=401, detail='Unauthorized: invalid X-ADMIN-KEY')


if os.path.isdir('tools'):
    app.mount('/tools', StaticFiles(directory='tools'), name='tools')


def range_counts(session: Session, days: int = 7):
    since = datetime.utcnow() - timedelta(days=days)

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


@app.get(
    '/admin/analytics',
    response_class=HTMLResponse,
    dependencies=[Depends(verify_admin_key)],
)
def admin_analytics(
    request: Request,
    days: int = Query(7, ge=1, le=90),
    session: Session = Depends(get_session),
):
    try:
        imps, clks = range_counts(session, days=days)

        # get active ads only if field exists
        query = select(Ad)
        if hasattr(Ad, 'is_active'):
            query = query.where(Ad.is_active == True)

        ads = session.exec(query).all() or []

        # ✅ Build dict in the structure template expects
        ctr = {}
        for a in ads:
            i = imps.get(a.id, 0)  # type: ignore
            c = clks.get(a.id, 0)  # type: ignore
            ctr[a.id] = {
                'impressions': i,
                'clicks': c,
                'ctr': (c / i) if i else 0.0,
            }

        return templates.TemplateResponse(
            'admin/analytics.html',
            {'request': request, 'ctr': ctr},
        )

    except Exception as e:
        logging.exception('Error in /admin/analytics')
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get('/ads/rent', response_class=HTMLResponse)
def rent_form(request: Request, session: Session = Depends(get_session)):
    zones = session.exec(select(Zone)).all()
    return templates.TemplateResponse(
        'ads/rent.html', {'request': request, 'zones': zones}
    )


@app.post('/ads/rent')
def submit_rental(
    html: str = Form(...),
    url: str = Form(...),
    zone_id: int = Form(...),
    weight: int = Form(1),
    session: Session = Depends(get_session),
):
    if not session.get(Zone, zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone ID')

    ad = Ad(html=html, url=url, zone_id=zone_id, weight=weight)
    session.add(ad)
    session.commit()

    # Optionally notify you via email or logging
    print(f'New ad rental submitted for zone {zone_id}')

    return RedirectResponse(url='/ads/rent?success=true', status_code=303)


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
from fastapi import Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from db import get_session
from models import Ad, Zone


@app.get('/render', response_class=HTMLResponse)
def render_ad(
    request: Request,
    zone: int = Query(1, description='Zone ID (defaults to 1)'),  # ✅ default value
    session: Session = Depends(get_session),
):
    # Get the zone
    z = session.get(Zone, zone)
    if not z:
        raise HTTPException(status_code=404, detail='Zone not found')

    # ✅ Fix: correctly load ads from the zone
    ads = z.ads if hasattr(z, 'ads') else []
    ads = [a for a in ads if getattr(a, 'is_active', True)]

    if not ads:
        raise HTTPException(status_code=404, detail='No ads for this zone')

    # Calculate CTR weights
    imps, clks = range_counts(session, days=7)
    ctr_weights = []
    for a in ads:
        try:
            i = imps.get(a.id, 0)  # type: ignore
            c = clks.get(a.id, 0)  # type: ignore
            ctr = (c / i) if i > 0 else 0
            boost = 1.0 + min(ctr * 10, 2.0)
            if i < 100:
                boost *= 1.5
            weight = a.weight * boost
        except ZeroDivisionError:
            weight = a.weight
        ctr_weights.append(weight)

    # Pick weighted ad
    ad = weighted_choice(ads, ctr_weights)

    if ad.id is None:
        raise HTTPException(status_code=500, detail='Ad ID is missing')

    # Log impression
    session.add(Impression(ad_id=ad.id))
    session.commit()

    # Build click URL
    click_url = f'/click?id={ad.id}'

    # Render ad HTML
    return f"""
    <div class="ad">
        <a href="{click_url}" target="_blank">
            {ad.html}
        </a>
    </div>
    """


@app.get('/click')
def click(id: int, session: Session = Depends(get_session)):
    ad = session.get(Ad, id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')

    # Log click internally
    session.add(Click(ad_id=ad.id))  # type: ignore
    session.commit()

    # Always redirect to Adsterra SmartLink
    return RedirectResponse(url=ADSTERRA_SMARTLINK, status_code=302)


@app.get('/healthz')
def healthz():
    return {'ok': True}


@app.get('/some-endpoint')
def some_endpoint():
    return {'message': 'Success'}


# ---------- Admin UI ----------
@app.get(
    '/admin', response_class=HTMLResponse, dependencies=[Depends(verify_admin_key)]
)
def admin_home(request: Request):
    return templates.TemplateResponse(
        'admin/base.html', {'request': request, 'page': 'home'}
    )


@app.get(
    '/admin/zones',
    response_class=HTMLResponse,
    dependencies=[Depends(verify_admin_key)],
)
def admin_zones(request: Request, session: Session = Depends(get_session)):
    zones = session.exec(select(Zone)).all()
    return templates.TemplateResponse(
        'admin/zones.html', {'request': request, 'zones': zones}
    )


@app.post('/admin/zones', dependencies=[Depends(verify_admin_key)])
def admin_zones_create(
    name: str = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    session: Session = Depends(get_session),
):
    z = Zone(name=name, width=width, height=height)
    session.add(z)
    session.commit()
    return RedirectResponse(url='/admin/zones', status_code=303)


@app.post('/admin/zones/{zone_id}/delete', dependencies=[Depends(verify_admin_key)])
def admin_zones_delete(zone_id: int, session: Session = Depends(get_session)):
    z = session.get(Zone, zone_id)
    if not z:
        raise HTTPException(status_code=404, detail='Zone not found')
    session.delete(z)
    session.commit()
    return RedirectResponse(url='/admin/zones', status_code=303)


@app.get(
    '/admin/ads', response_class=HTMLResponse, dependencies=[Depends(verify_admin_key)]
)
def admin_ads(
    request: Request,
    zone: int | None = Query(default=None),
    session: Session = Depends(get_session),
):
    try:
        # fetch all zones
        zones = session.exec(select(Zone)).all() or []

        # fetch ads (filter by active + optional zone)
        query = select(Ad)
        if hasattr(Ad, 'is_active'):
            query = query.where(Ad.is_active == True)
        if zone:
            query = query.where(Ad.zone_id == zone)

        ads = session.exec(query).all() or []

        return templates.TemplateResponse(
            'admin/ads.html',
            {
                'request': request,
                'zones': zones,
                'ads': ads,
                'zone_filter': zone,
            },
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return HTMLResponse(f'Error: {e}', status_code=500)


@app.post('/admin/ads', dependencies=[Depends(verify_admin_key)])
def admin_ads_create(
    zone_id: int = Form(...),
    html: str = Form(...),
    url: str = Form(...),
    weight: int = Form(1),
    session: Session = Depends(get_session),
):
    if not session.get(Zone, zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone_id')
    a = Ad(zone_id=zone_id, html=html, url=url, weight=weight)
    session.add(a)
    session.commit()
    return RedirectResponse(url='/admin/ads', status_code=303)


@app.post('/admin/ads/{ad_id}/delete', dependencies=[Depends(verify_admin_key)])
def admin_ads_delete(ad_id: int, session: Session = Depends(get_session)):
    a = session.get(Ad, ad_id)
    if not a:
        raise HTTPException(status_code=404, detail='Ad not found')
    session.delete(a)
    session.commit()
    return RedirectResponse(url='/admin/ads', status_code=303)


@app.get('/embed.js', response_class=Response, include_in_schema=False)
def embed_js(
    request: Request, zone: int | None = Query(default=None, description='Zone ID')
):
    return templates.TemplateResponse(
        'embed.js.jinja2',
        {'request': request, 'zone': zone},
        media_type='application/javascript',
    )


@app.get('/api/stats.json')
def stats_api(session: Session = Depends(get_session)):
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


@app.get('/stats.json', response_class=JSONResponse)
def public_stats(session: Session = Depends(get_session)):
    # Optional: support filtering per zone later
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


@app.get('/stats', response_class=HTMLResponse)
def public_stats_ui(request: Request):
    return templates.TemplateResponse('public/stats.html', {'request': request})


@app.get('/ads.txt', response_class=PlainTextResponse, include_in_schema=False)
def ads_txt():
    with open('ads.txt') as f:
        return f.read()


@app.get('/robots.txt', response_class=PlainTextResponse, include_in_schema=False)
def robots_txt():
    with open('robots.txt') as f:
        return f.read()


@app.get('/sitemap.xml', response_class=PlainTextResponse, include_in_schema=False)
def sitemap_xml():
    with open('sitemap.xml') as f:
        return f.read()


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        'index.html', {'request': request, 'year': datetime.utcnow().year}
    )


@app.get('/publisher', response_class=HTMLResponse)
def publisher_page(request: Request):
    return templates.TemplateResponse('public/publisher.html', {'request': request})


@app.get('/publisher-test', response_class=HTMLResponse)
def publisher_test(request: Request):
    return templates.TemplateResponse('publisher-test.html', {'request': request})


@app.get(
    '/yandex_6079f30d3b2abdbc.html',
    response_class=PlainTextResponse,
    include_in_schema=False,
)
def yandex_verification():
    return 'yandex-verification: 6079f30d3b2abdbc'


@app.get('/blog', response_class=HTMLResponse)
def blog_index(request: Request):
    posts = [
        f.replace('blog_', '').replace('.html', '')
        for f in os.listdir(BLOG_DIR)
        if f.startswith('blog_')
        and f.endswith('.html')
        and f not in ('blog_index.html', 'blog_base.html')
    ]
    return templates.TemplateResponse(
        'public/blog_index.html', {'request': request, 'posts': posts}
    )


@app.get('/blog/{slug}', response_class=HTMLResponse)
def blog_page(request: Request, slug: str):
    filename = f'blog_{slug}.html'
    filepath = os.path.join(BLOG_DIR, filename)

    # Check if the file exists
    if not os.path.exists(filepath):
        # Instead of plain 404 → show available posts
        available = [
            f.replace('blog_', '').replace('.html', '')
            for f in os.listdir(BLOG_DIR)
            if f.startswith('blog_') and f.endswith('.html')
        ]
        raise HTTPException(
            status_code=404,
            detail={
                'error': f"Blog post '{slug}' not found",
                'available_posts': available,
            },
        )

    return templates.TemplateResponse(f'public/{filename}', {'request': request})


@app.post('/admin/ads/{ad_id}/disable', dependencies=[Depends(verify_admin_key)])
def admin_ads_disable(ad_id: int, session: Session = Depends(get_session)):
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    ad.is_active = False
    session.add(ad)
    session.commit()
    return RedirectResponse(url='/admin/analytics', status_code=303)


@app.post('/admin/ads/{ad_id}/enable', dependencies=[Depends(verify_admin_key)])
def admin_ads_enable(ad_id: int, session: Session = Depends(get_session)):
    ad = session.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')
    ad.is_active = True
    session.add(ad)
    session.commit()
    return RedirectResponse(url='/admin/analytics', status_code=303)
