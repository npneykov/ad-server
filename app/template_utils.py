"""Template utilities with global context."""

from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import get_settings


def create_templates(directory: str = 'templates') -> Jinja2Templates:
    """Create Jinja2Templates instance with settings injected into all contexts."""
    settings = get_settings()
    tmpl = Jinja2Templates(directory=directory)

    # Store original TemplateResponse method
    original_response = tmpl.TemplateResponse

    # Override to inject settings into all template contexts
    def custom_response(
        request: Request, name: str, context: dict[str, Any] | None = None, **kwargs
    ):
        if context is None:
            context = {}
        # Add settings to context if not already present
        if 'settings' not in context:
            context['settings'] = settings
        return original_response(request=request, name=name, context=context, **kwargs)

    tmpl.TemplateResponse = custom_response  # type: ignore
    return tmpl
