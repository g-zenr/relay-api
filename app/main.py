from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import init_relay_service
from app.api.v1.relays import router as relays_router
from app.api.v1.system import router as system_router
from app.config import settings
from app.core.device import HIDRelayDevice, MockRelayDevice, RelayDevice
from app.services.relay_service import RelayService

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    device: RelayDevice
    if settings.mock:
        device = MockRelayDevice(channels=settings.relay_channels)
        device.open()
        logger.info("Running in MOCK mode — no real hardware")
    else:
        device = HIDRelayDevice(settings.vendor_id, settings.product_id)
        try:
            device.open()
            logger.info(
                "Device connected — %d channels ready", settings.relay_channels
            )
        except Exception:
            logger.warning(
                "USB relay device not found — starting in disconnected mode. "
                "Relay endpoints will return 503 until the device is available."
            )

    service = RelayService(
        device, channels=settings.relay_channels, pulse_ms=settings.pulse_ms,
    )
    if device.is_open:
        service.all_off()
    init_relay_service(service)

    if settings.api_key:
        logger.info("API key authentication ENABLED")
    else:
        logger.info("API key authentication DISABLED (open access)")
    if settings.rate_limit > 0:
        logger.info("Rate limiting ENABLED (%d req/min)", settings.rate_limit)
    if settings.pulse_ms > 0:
        logger.info("Pulse mode ENABLED (%dms auto-off)", settings.pulse_ms)
    logger.info("Relay API started")
    yield

    logger.info("Shutting down")
    if device.is_open:
        service.all_off()
        device.close()


DESCRIPTION = """\
REST API for controlling DCT Tech USB relay modules via HID.

## Features

- **Single Channel Control** — Turn individual relay channels ON or OFF.
- **Bulk Control** — Set all channels to the same state in a single request.
- **State Tracking** — Query current relay states at any time.
- **Device Info** — Read USB manufacturer and product strings.
- **Fail-Safe** — All relays default to OFF on startup and shutdown.

## Authentication

Set the `RELAY_API_KEY` environment variable to enable API key authentication.
When enabled, all requests must include an `X-API-Key` header with the configured key.
When unset, the API is open — restrict access via network policies.

## Audit Logging

All relay state changes are logged to the `relay.audit` logger with ISO-8601 timestamps,
action type, target channel(s), and resulting state.

## Rate Limiting

Set `RELAY_RATE_LIMIT` to a positive integer to enable per-client IP rate limiting
(requests per minute). Returns `429 Too Many Requests` with a `Retry-After` header
when exceeded. Disabled by default.
"""

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Relays",
            "description": "Control and monitor individual or all relay channels.",
        },
        {
            "name": "System",
            "description": "Health checks and API status.",
        },
    ],
    license_info={"name": "MIT"},
    contact={"name": "Relay API Team"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.rate_limit > 0:
    from app.middleware import RateLimitMiddleware

    app.add_middleware(RateLimitMiddleware)

app.include_router(relays_router, prefix="/api/v1")
app.include_router(system_router)
