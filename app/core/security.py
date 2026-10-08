"""# Security.

It handles the security for the API.
"""

import secrets

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings

# auto_error=False so we can decide ourselves whether a missing key matters.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Enforce API key auth. If no key is configured in .env, the API is open."""
    if not settings.auth_enabled:
        return

    if api_key:
        # constant-time comparison to avoid timing attacks
        for valid in settings.api_keys:
            if secrets.compare_digest(api_key.encode(), valid.encode()):
                return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )
