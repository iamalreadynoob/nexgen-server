"""# Health.

The health endpoints.
"""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """# Health."""
    """Liveness probe (public)."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(request: Request) -> dict:
    """Readiness probe: checks Mongo is reachable (public)."""
    await request.app.state.db.command("ping")
    return {"status": "ready"}
