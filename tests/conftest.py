from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_relay_service,
    get_relay_service_public,
    init_relay_service,
    require_device,
)
from app.core.device import MockRelayDevice
from app.services.relay_service import RelayService


@pytest.fixture()
def mock_device() -> MockRelayDevice:
    device = MockRelayDevice(channels=2)
    device.open()
    return device


@pytest.fixture()
def mock_device_closed() -> MockRelayDevice:
    return MockRelayDevice(channels=2)


@pytest.fixture()
def service(mock_device: MockRelayDevice) -> RelayService:
    return RelayService(mock_device, channels=2)


@pytest.fixture()
def service_disconnected(mock_device_closed: MockRelayDevice) -> RelayService:
    return RelayService(mock_device_closed, channels=2)


@pytest.fixture()
def client(service: RelayService) -> Generator[TestClient, None, None]:
    from app.main import app

    app.dependency_overrides[get_relay_service] = lambda: service
    app.dependency_overrides[get_relay_service_public] = lambda: service
    app.dependency_overrides[require_device] = lambda: service
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_disconnected(
    service_disconnected: RelayService,
) -> Generator[TestClient, None, None]:
    from app.main import app

    app.dependency_overrides[get_relay_service] = lambda: service_disconnected
    app.dependency_overrides[get_relay_service_public] = (
        lambda: service_disconnected
    )

    def _require_device_fail() -> RelayService:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="USB relay device is not connected",
        )

    app.dependency_overrides[require_device] = _require_device_fail
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_auth(
    service: RelayService, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    """Client with API key authentication enabled.

    Uses real dependency chain (no overrides) so the auth
    middleware is exercised.  The API key is set to "test-key".
    """
    from app.main import app

    monkeypatch.setattr("app.config.settings.api_key", "test-key")
    init_relay_service(service)
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    init_relay_service(None)  # type: ignore[arg-type]
    monkeypatch.setattr("app.config.settings.api_key", "")
