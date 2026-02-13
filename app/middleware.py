from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple fixed-window rate limiter per client IP.

    Limits each client to ``settings.rate_limit`` requests per minute.
    Disabled when ``rate_limit`` is ``0`` (the default).

    Returns 429 Too Many Requests with a ``Retry-After`` header when
    the limit is exceeded.
    """

    def __init__(self, app: object) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._window: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        limit = settings.rate_limit
        if limit <= 0:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - 60.0

        # Prune expired timestamps
        timestamps = self._window[client_ip]
        self._window[client_ip] = [t for t in timestamps if t > window_start]
        timestamps = self._window[client_ip]

        if len(timestamps) >= limit:
            retry_after = int(60.0 - (now - timestamps[0])) + 1
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)
        return await call_next(request)
