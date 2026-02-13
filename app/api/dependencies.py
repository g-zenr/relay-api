from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.services.relay_service import RelayService

_relay_service: RelayService | None = None

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def init_relay_service(service: RelayService) -> None:
    global _relay_service
    _relay_service = service


def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Verify API key if authentication is enabled.

    When ``RELAY_API_KEY`` is set, every request must include
    a matching ``X-API-Key`` header.  When the setting is empty
    (the default) authentication is disabled.

    Uses constant-time comparison to prevent timing side-channel attacks.
    """
    if not settings.api_key:
        return
    if not api_key or not hmac.compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_relay_service(
    _auth: None = Depends(verify_api_key),
) -> RelayService:
    if _relay_service is None:
        raise RuntimeError("RelayService not initialized")
    return _relay_service


def get_relay_service_public() -> RelayService:
    """Public access — no authentication required.

    Use only for endpoints that must be accessible without credentials,
    such as health checks and readiness probes.
    """
    if _relay_service is None:
        raise RuntimeError("RelayService not initialized")
    return _relay_service


def require_device(
    service: RelayService = Depends(get_relay_service),
) -> RelayService:
    """Dependency that ensures the USB device is connected.

    Returns the service if connected, raises 503 otherwise.
    Use this for endpoints that need to talk to hardware.
    """
    if not service.is_device_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="USB relay device is not connected",
        )
    return service
