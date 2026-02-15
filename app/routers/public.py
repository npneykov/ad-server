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

HOME_CRUMB = {'name': 'Home', 'url': '/'}
TOOLS_CRUMB = {'name': 'Tools', 'url': '/tools'}
BLOG_CRUMB = {'name': 'Blog', 'url': '/blog'}


@router.get('/', response_class=HTMLResponse)
def home(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        request=request, name='index.html', context={'year': datetime.now(UTC).year}
    )


@router.get('/tools', response_class=HTMLResponse)
def tools_page(request: Request):
    """Ad testing tools page."""
    return templates.TemplateResponse(
        request=request,
        name='tools.html',
        context={'breadcrumb_items': [HOME_CRUMB, {'name': 'Tools', 'url': '/tools'}]},
    )


# Banner Preview Pages
BANNER_SIZES = {
    '728x90': {
        'size': '728×90',
        'name': 'Leaderboard',
        'width': 728,
        'height': 90,
        'zone_id': 1,
        'placement': 'Header, above-the-fold',
    },
    '300x250': {
        'size': '300×250',
        'name': 'Medium Rectangle',
        'width': 300,
        'height': 250,
        'zone_id': 2,
        'placement': 'Sidebar, in-content',
    },
    '468x60': {
        'size': '468×60',
        'name': 'Full Banner',
        'width': 468,
        'height': 60,
        'zone_id': 3,
        'placement': 'Mid-page, footer',
    },
    '160x600': {
        'size': '160×600',
        'name': 'Skyscraper',
        'width': 160,
        'height': 600,
        'zone_id': 4,
        'placement': 'Sidebar (vertical)',
    },
    '160x300': {
        'size': '160×300',
        'name': 'Large Banner',
        'width': 160,
        'height': 300,
        'zone_id': 5,
        'placement': 'Sidebar (vertical)',
    },
    '320x50': {
        'size': '320×50',
        'name': 'Mobile Banner',
        'width': 320,
        'height': 50,
        'zone_id': 6,
        'placement': 'Mobile screens',
    },
}


@router.get('/tools/banner-preview-{size_slug}.html', response_class=HTMLResponse)
def banner_preview_page(request: Request, size_slug: str):
    """Individual banner preview pages."""
    if size_slug not in BANNER_SIZES:
        raise HTTPException(status_code=404, detail='Banner size not found')

    banner_info = BANNER_SIZES[size_slug]
    context = {
        'size_slug': size_slug,
        'breadcrumb_items': [
            HOME_CRUMB,
            TOOLS_CRUMB,
            {
                'name': f'{banner_info["size"]} {banner_info["name"]}',
                'url': f'/tools/banner-preview-{size_slug}.html',
            },
        ],
        **banner_info,
    }
    return templates.TemplateResponse(
        request=request, name='tools/banner-preview.html', context=context
    )


@router.get('/tools/test-html5-banner-preview.html', response_class=HTMLResponse)
def html5_test_page(request: Request):
    """HTML5 banner testing page."""
    return templates.TemplateResponse(
        request=request,
        name='tools/html5-test.html',
        context={
            'breadcrumb_items': [
                HOME_CRUMB,
                TOOLS_CRUMB,
                {
                    'name': 'HTML5 Test Hub',
                    'url': '/tools/test-html5-banner-preview.html',
                },
            ]
        },
    )


@router.get('/tools/html5-banner-preview-collection.html', response_class=HTMLResponse)
def html5_collection_page(request: Request):
    """HTML5 banner multi-size preview page."""
    return templates.TemplateResponse(
        request=request,
        name='tools/html5-collection.html',
        context={
            'breadcrumb_items': [
                HOME_CRUMB,
                TOOLS_CRUMB,
                {
                    'name': 'Banner Collection',
                    'url': '/tools/html5-banner-preview-collection.html',
                },
            ]
        },
    )


@router.get('/tools/html5-banner-validator.html', response_class=HTMLResponse)
def html5_validator_page(request: Request):
    """HTML5 banner validator page."""
    return templates.TemplateResponse(
        request=request,
        name='tools/html5-validator.html',
        context={
            'breadcrumb_items': [
                HOME_CRUMB,
                TOOLS_CRUMB,
                {
                    'name': 'Banner Validator',
                    'url': '/tools/html5-banner-validator.html',
                },
            ]
        },
    )


@router.get('/stats', response_class=HTMLResponse)
def public_stats_ui(request: Request):
    """Public stats page."""
    return templates.TemplateResponse(
        request=request,
        name='stats.html',
        context={
            'breadcrumb_items': [
                HOME_CRUMB,
                {'name': 'Statistics', 'url': '/stats'},
            ]
        },
    )


@router.get('/publisher', response_class=HTMLResponse)
def publisher_page(request: Request):
    """Publisher information page."""
    return templates.TemplateResponse(
        request=request,
        name='publisher.html',
        context={
            'breadcrumb_items': [
                HOME_CRUMB,
                {'name': 'Publishers', 'url': '/publisher'},
            ]
        },
    )


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
        request=request,
        name='blog.html',
        context={
            'posts': posts,
            'breadcrumb_items': [HOME_CRUMB, {'name': 'Blog', 'url': '/blog'}],
        },
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
    title = slug.replace('_', ' ').title()
    return templates.TemplateResponse(
        request=request,
        name=f'public/{filename}',
        context={
            'published': published,
            'year': year,
            'breadcrumb_items': [
                HOME_CRUMB,
                BLOG_CRUMB,
                {'name': title, 'url': f'/blog/{slug}'},
            ],
        },
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
