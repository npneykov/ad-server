"""FastAPI application factory and configuration."""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from sqlmodel import SQLModel
from starlette.middleware.gzip import GZipMiddleware
from starlette.staticfiles import StaticFiles

from app.database import engine
from app.routers import admin_router, api_router, public_router, serving_router

logging.basicConfig(level=logging.DEBUG)


class CachedStaticFiles(StaticFiles):
    """Static files with caching headers."""

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers.setdefault('Cache-Control', 'public, max-age=2592000, immutable')
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
    app.include_router(api_router)
    app.include_router(admin_router)
    app.include_router(public_router)
    app.include_router(serving_router)

    # Mount static files
    if os.path.isdir('tools'):
        app.mount('/tools', CachedStaticFiles(directory='tools'), name='tools')

    if os.path.isdir('static'):
        app.mount('/static', CachedStaticFiles(directory='static'), name='static')

    return app


# Create the app instance
app = create_app()
