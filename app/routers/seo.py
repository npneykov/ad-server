"""SEO-related routes: IndexNow verification key."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=['SEO'])

INDEXNOW_KEY = 'b1c4e8f2a3d7e9f0b5c6d8a1e4f7c3b2'


@router.get(f'/{INDEXNOW_KEY}.txt', include_in_schema=False)
def indexnow_key_file():
    """Serve the IndexNow verification key file."""
    return PlainTextResponse(INDEXNOW_KEY)
