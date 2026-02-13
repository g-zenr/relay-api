from __future__ import annotations

from typing import Generator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_relay_service_public
from app.core.device import MockRelayDevice
from app.middleware import RateLimitMiddleware
from app.models.schemas import HealthResponse
from app.services.relay_service import RelayService


class TestApiKeyAuthEnabled:
    """Tests when RELAY_API_KEY is configured (auth required)."""

    def test_missing_key_returns_401(self, client_auth: TestClient) -> None:
        resp = client_auth.get("/api/v1/relays")
        assert resp.status_code == 401
        assert "Invalid or missing" in resp.json()["detail"]

    def test_wrong_key_returns_401(self, client_auth: TestClient) -> None:
        resp = client_auth.get(
            "/api/v1/relays", headers={"X-API-Key": "wrong-key"}
        )
        assert resp.status_code == 401

    def test_correct_key_returns_200(self, client_auth: TestClient) -> None:
        resp = client_auth.get(
            "/api/v1/relays", headers={"X-API-Key": "test-key"}
        )
        assert resp.status_code == 200

    def test_write_endpoint_requires_key(self, client_auth: TestClient) -> None:
        resp = client_auth.put(
            "/api/v1/relays/1", json={"state": "on"}
        )
        assert resp.status_code == 401

    def test_write_endpoint_with_key_succeeds(
        self, client_auth: TestClient
    ) -> None:
        resp = client_auth.put(
            "/api/v1/relays/1",
            json={"state": "on"},
            headers={"X-API-Key": "test-key"},
        )
        assert resp.status_code == 200

    def test_health_bypasses_auth(self, client_auth: TestClient) -> None:
        """Health endpoint must be accessible without an API key."""
        resp = client_auth.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] in ("ok", "degraded")

    def test_device_info_requires_key(self, client_auth: TestClient) -> None:
        resp = client_auth.get("/api/v1/relays/device/info")
        assert resp.status_code == 401


class TestApiKeyAuthDisabled:
    """Tests when RELAY_API_KEY is empty (open access)."""

    def test_open_access_no_key_needed(self, client: TestClient) -> None:
        resp = client.get("/api/v1/relays")
        assert resp.status_code == 200

    def test_open_access_extra_key_ignored(self, client: TestClient) -> None:
        resp = client.get(
            "/api/v1/relays", headers={"X-API-Key": "anything"}
        )
        assert resp.status_code == 200


class TestRateLimiting:
    """Tests for rate limiting middleware."""

    @pytest.fixture()
    def client_rate_limited(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> Generator[TestClient, None, None]:
        """Create a standalone FastAPI app with rate limiting enabled."""
        device = MockRelayDevice(channels=2)
        device.open()
        service = RelayService(device, channels=2)

        monkeypatch.setattr("app.config.settings.rate_limit", 3)

        # Build a minimal app with the rate limiter baked in
        test_app = FastAPI()
        test_app.add_middleware(RateLimitMiddleware)

        def _get_service() -> RelayService:
            return service

        @test_app.get("/health", response_model=HealthResponse)
        def health(
            svc: RelayService = Depends(_get_service),
        ) -> HealthResponse:
            return HealthResponse(
                status="ok", device_connected=True, version="test"
            )

        yield TestClient(test_app, raise_server_exceptions=False)
        monkeypatch.setattr("app.config.settings.rate_limit", 0)

    def test_requests_within_limit_succeed(
        self, client_rate_limited: TestClient
    ) -> None:
        for _ in range(3):
            resp = client_rate_limited.get("/health")
            assert resp.status_code == 200

    def test_exceeding_limit_returns_429(
        self, client_rate_limited: TestClient
    ) -> None:
        for _ in range(3):
            client_rate_limited.get("/health")

        resp = client_rate_limited.get("/health")
        assert resp.status_code == 429
        assert "Rate limit exceeded" in resp.json()["detail"]
        assert "Retry-After" in resp.headers
