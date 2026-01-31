"""Public-facing pages and static file routes."""

from datetime import UTC, date, datetime
import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

router = APIRouter(tags=['Public'])
templates = Jinja2Templates(directory='templates')
settings = get_settings()


@router.get('/', response_class=HTMLResponse)
def home(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        request=request, name='index.html', context={'year': datetime.now(UTC).year}
    )


@router.get('/stats', response_class=HTMLResponse)
def public_stats_ui(request: Request):
    """Public stats page."""
    return templates.TemplateResponse(request=request, name='public/stats.html')


@router.get('/publisher', response_class=HTMLResponse)
def publisher_page(request: Request):
    """Publisher information page."""
    return templates.TemplateResponse(request=request, name='public/publisher.html')


@router.get('/publisher-test', response_class=HTMLResponse)
def publisher_test(request: Request):
    """Publisher test page."""
    return templates.TemplateResponse(request=request, name='publisher-test.html')


# -------- Blog --------
@router.get('/blog', response_class=HTMLResponse)
def blog_index(request: Request):
    """Blog index page."""
    posts = [
        f.replace('blog_', '').replace('.html', '')
        for f in os.listdir(settings.blog_dir)
        if f.startswith('blog_')
        and f.endswith('.html')
        and f not in ('blog_index.html', 'blog_base.html')
    ]
    return templates.TemplateResponse(
        request=request, name='public/blog_index.html', context={'posts': posts}
    )


@router.get('/blog/{slug}', response_class=HTMLResponse)
def blog_page(request: Request, slug: str):
    """Individual blog post page."""
    filename = f'blog_{slug}.html'
    filepath = os.path.join(settings.blog_dir, filename)
    published = date.today().isoformat()

    # Check if the file exists
    if not os.path.exists(filepath):
        # Show available posts instead of plain 404
        available = [
            f.replace('blog_', '').replace('.html', '')
            for f in os.listdir(settings.blog_dir)
            if f.startswith('blog_') and f.endswith('.html')
        ]
        raise HTTPException(
            status_code=404,
            detail={
                'error': f"Blog post '{slug}' not found",
                'available_posts': available,
            },
        )

    year = date.today().year
    return templates.TemplateResponse(
        request=request,
        name=f'public/{filename}',
        context={'published': published, 'year': year},
    )


# -------- Static Files --------
@router.get('/ads.txt', response_class=PlainTextResponse, include_in_schema=False)
def ads_txt():
    """Serve ads.txt file."""
    with open('ads.txt') as f:
        return f.read()


@router.get('/robots.txt', response_class=PlainTextResponse, include_in_schema=False)
def robots_txt():
    """Serve robots.txt file."""
    with open('robots.txt') as f:
        return f.read()


@router.get('/sitemap.xml', response_class=PlainTextResponse, include_in_schema=False)
def sitemap_xml():
    """Serve sitemap.xml file."""
    with open('sitemap.xml') as f:
        return f.read()


@router.get(
    '/yandex_6079f30d3b2abdbc.html',
    response_class=PlainTextResponse,
    include_in_schema=False,
)
def yandex_verification():
    """Yandex verification file."""
    return 'yandex-verification: 6079f30d3b2abdbc'
