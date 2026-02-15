"""Router modules."""

from app.routers.admin import router as admin_router
from app.routers.api import router as api_router
from app.routers.public import router as public_router
from app.routers.seo import router as seo_router
from app.routers.serving import router as serving_router

__all__ = [
    'admin_router',
    'api_router',
    'public_router',
    'seo_router',
    'serving_router',
]
