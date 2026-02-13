from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_relay_service_public
from app.config import settings
from app.models.schemas import HealthResponse
from app.services.relay_service import RelayService

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API status, USB device connection state, and version. "
    "Use this endpoint for uptime monitoring and readiness probes. "
    "This endpoint does not require authentication.",
)
def health_check(
    service: RelayService = Depends(get_relay_service_public),
) -> HealthResponse:
    connected = service.is_device_connected
    return HealthResponse(
        status="ok" if connected else "degraded",
        device_connected=connected,
        version=settings.app_version,
    )
