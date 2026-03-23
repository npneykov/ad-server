"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from sqlmodel import SQLModel
from starlette.middleware.gzip import GZipMiddleware
from starlette.staticfiles import StaticFiles

from app.database import engine
from app.routers import (
    admin_router,
    api_router,
    public_router,
    seo_router,
    serving_router,
)

logging.basicConfig(level=logging.DEBUG)


class CachedStaticFiles(StaticFiles):
    """Static files with Cache-Control tuned for unhashed CSS/JS vs images/fonts."""

    _CACHE_CSS_JS = 'public, max-age=86400'  # 1d — main.css updates apply within a day
    _CACHE_FONT = 'public, max-age=604800'  # 7d
    # 7d; no immutable — same path may be replaced after deploy
    _CACHE_IMAGE = 'public, max-age=604800'

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        if resp.status_code != 200:
            return resp
        ext = path.rsplit('.', 1)[-1].lower() if '.' in path else ''
        if ext in ('css', 'js', 'mjs'):
            resp.headers['Cache-Control'] = self._CACHE_CSS_JS
        elif ext in ('woff', 'woff2', 'ttf', 'otf', 'eot'):
            resp.headers['Cache-Control'] = self._CACHE_FONT
        elif ext in ('png', 'jpg', 'jpeg', 'webp', 'gif', 'ico', 'svg'):
            resp.headers['Cache-Control'] = self._CACHE_IMAGE
        else:
            resp.headers['Cache-Control'] = self._CACHE_CSS_JS
        return resp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown (if needed in future)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(lifespan=lifespan)

    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # Include routers
    app.include_router(seo_router)
    app.include_router(api_router)
    app.include_router(admin_router)
    app.include_router(public_router)
    app.include_router(serving_router)

    # Mount static files
    # Note: /tools routes are now handled by dynamic templates in public_router
    # if os.path.isdir('tools'):
    #     app.mount('/tools', CachedStaticFiles(directory='tools'), name='tools')

    if os.path.isdir('static'):
        app.mount('/static', CachedStaticFiles(directory='static'), name='static')

    return app


# Create the app instance
app = create_app()
