"""Ad serving routes - render, click, embed."""

from fastapi import APIRouter, Form, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from app.config import get_settings
from app.dependencies import SessionDep
from app.models import Ad, Click, Zone
from app.services.ad_selection import record_impression, select_ad_for_zone

router = APIRouter(tags=['Serving'])
templates = Jinja2Templates(directory='templates')
settings = get_settings()


@router.get('/render', response_class=HTMLResponse)
def render_ad(
    request: Request,
    session: SessionDep,
    response: Response,
    zone: int = Query(1, description='Zone ID (defaults to 1)'),
):
    """Render an ad for the specified zone."""
    # Tell search engines not to index this endpoint
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    # Verify zone exists
    z = session.get(Zone, zone)
    if not z:
        raise HTTPException(
            status_code=404,
            detail=(
                f'Zone {zone} not found. '
                'Create a zone first via /zones/ or /admin/zones'
            ),
        )

    # Query ads for this zone directly
    query = select(Ad).where(Ad.zone_id == zone)
    if hasattr(Ad, 'is_active'):
        query = query.where(Ad.is_active == True)  # noqa: E712
    ads = list(session.exec(query).all())

    if not ads:
        # Check if there are any inactive ads
        all_ads_query = select(Ad).where(Ad.zone_id == zone)
        all_ads = list(session.exec(all_ads_query).all())
        if all_ads:
            raise HTTPException(
                status_code=404,
                detail=(
                    f'Zone {zone} ({z.name}) has {len(all_ads)} ad(s) '
                    'but none are active. Activate ads via /admin/ads'
                ),
            )
        raise HTTPException(
            status_code=404,
            detail=(
                f'Zone {zone} ({z.name}) has no ads. Create ads via /ads/ or /admin/ads'
            ),
        )

    # Select ad using weighted CTR-based selection
    ad = select_ad_for_zone(session, ads)

    if ad.id is None:
        raise HTTPException(status_code=500, detail='Ad ID is missing')

    # Log impression
    record_impression(session, ad.id)

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


@router.get('/click')
def click(id: int, session: SessionDep, response: Response):
    """Handle ad click - log and redirect to Adsterra SmartLink."""
    # Tell search engines not to index this endpoint
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    ad = session.get(Ad, id)
    if not ad:
        raise HTTPException(status_code=404, detail='Ad not found')

    # Log click internally
    session.add(Click(ad_id=ad.id))  # type: ignore
    session.commit()

    # Always redirect to Adsterra SmartLink
    return RedirectResponse(url=settings.adsterra_smartlink, status_code=302)


@router.get('/embed.js', response_class=Response, include_in_schema=False)
def embed_js(
    request: Request,
    zone: int | None = Query(default=None, description='Zone ID'),
):
    """Generate embeddable JavaScript for ad display."""
    return templates.TemplateResponse(
        request=request,
        name='embed.js.jinja2',
        context={'zone': zone},
        media_type='application/javascript',
    )


# -------- Ad Rental Form --------
@router.get('/ads/rent', response_class=HTMLResponse)
def rent_form(request: Request, session: SessionDep):
    """Ad rental form page."""
    zones = session.exec(select(Zone)).all()
    return templates.TemplateResponse(
        request=request, name='ads/rent.html', context={'zones': zones}
    )


@router.post('/ads/rent')
def submit_rental(
    session: SessionDep,
    html: str = Form(...),
    url: str = Form(...),
    zone_id: int = Form(...),
    weight: int = Form(1),
):
    """Submit ad rental form."""
    if not session.get(Zone, zone_id):
        raise HTTPException(status_code=400, detail='Invalid zone ID')

    ad = Ad(html=html, url=url, zone_id=zone_id, weight=weight)
    session.add(ad)
    session.commit()

    # Optionally notify via logging
    print(f'New ad rental submitted for zone {zone_id}')

    return RedirectResponse(url='/ads/rent?success=true', status_code=303)


# Note: /tools route is now handled by public_router
