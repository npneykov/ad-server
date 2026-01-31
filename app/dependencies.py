"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from app.config import get_settings
from app.database import get_session

# Type alias for database session dependency
SessionDep = Annotated[Session, Depends(get_session)]


def verify_admin_key(x_admin_key: str | None = Header(default=None)) -> bool:
    """Verify the admin API key from request header."""
    settings = get_settings()
    expected = settings.admin_key

    if not expected:
        # For local dev: allow if no key set
        return True
    if x_admin_key == expected:
        return True
    raise HTTPException(status_code=401, detail='Unauthorized: invalid X-ADMIN-KEY')
