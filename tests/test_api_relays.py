from fastapi.testclient import TestClient


# ─── GET /api/v1/relays ───


class TestGetAllRelays:
    def test_returns_all_channels(self, client: TestClient):
        resp = client.get("/api/v1/relays")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["channels"]) == 2
        assert data["channels"][0]["channel"] == 1
        assert data["channels"][1]["channel"] == 2

    def test_default_state_is_off(self, client: TestClient):
        resp = client.get("/api/v1/relays")
        for ch in resp.json()["channels"]:
            assert ch["state"] == "off"

    def test_reflects_state_changes(self, client: TestClient):
        client.put("/api/v1/relays/1", json={"state": "on"})
        resp = client.get("/api/v1/relays")
        channels = resp.json()["channels"]
        assert channels[0]["state"] == "on"
        assert channels[1]["state"] == "off"


# ─── PUT /api/v1/relays ───


class TestSetAllRelays:
    def test_set_all_on(self, client: TestClient):
        resp = client.put("/api/v1/relays", json={"state": "on"})
        assert resp.status_code == 200
        for ch in resp.json()["channels"]:
            assert ch["state"] == "on"

    def test_set_all_off(self, client: TestClient):
        client.put("/api/v1/relays", json={"state": "on"})
        resp = client.put("/api/v1/relays", json={"state": "off"})
        assert resp.status_code == 200
        for ch in resp.json()["channels"]:
            assert ch["state"] == "off"

    def test_invalid_state_returns_422(self, client: TestClient):
        resp = client.put("/api/v1/relays", json={"state": "invalid"})
        assert resp.status_code == 422

    def test_missing_body_returns_422(self, client: TestClient):
        resp = client.put("/api/v1/relays")
        assert resp.status_code == 422

    def test_disconnected_returns_503(self, client_disconnected: TestClient):
        resp = client_disconnected.put("/api/v1/relays", json={"state": "on"})
        assert resp.status_code == 503
        assert "not connected" in resp.json()["detail"]


# ─── GET /api/v1/relays/{channel} ───


class TestGetRelay:
    def test_get_channel_1(self, client: TestClient):
        resp = client.get("/api/v1/relays/1")
        assert resp.status_code == 200
        assert resp.json() == {"channel": 1, "state": "off"}

    def test_get_channel_2(self, client: TestClient):
        resp = client.get("/api/v1/relays/2")
        assert resp.status_code == 200
        assert resp.json()["channel"] == 2

    def test_channel_out_of_range_returns_404(self, client: TestClient):
        resp = client.get("/api/v1/relays/99")
        assert resp.status_code == 404

    def test_channel_zero_returns_422(self, client: TestClient):
        resp = client.get("/api/v1/relays/0")
        assert resp.status_code == 422

    def test_channel_negative_returns_422(self, client: TestClient):
        resp = client.get("/api/v1/relays/-1")
        assert resp.status_code == 422

    def test_channel_non_integer_returns_422(self, client: TestClient):
        resp = client.get("/api/v1/relays/abc")
        assert resp.status_code == 422


# ─── PUT /api/v1/relays/{channel} ───


class TestSetRelay:
    def test_set_on(self, client: TestClient):
        resp = client.put("/api/v1/relays/1", json={"state": "on"})
        assert resp.status_code == 200
        assert resp.json() == {"channel": 1, "state": "on"}

    def test_set_off(self, client: TestClient):
        client.put("/api/v1/relays/1", json={"state": "on"})
        resp = client.put("/api/v1/relays/1", json={"state": "off"})
        assert resp.status_code == 200
        assert resp.json()["state"] == "off"

    def test_set_persists_state(self, client: TestClient):
        client.put("/api/v1/relays/2", json={"state": "on"})
        resp = client.get("/api/v1/relays/2")
        assert resp.json()["state"] == "on"

    def test_set_channel_out_of_range_returns_404(self, client: TestClient):
        resp = client.put("/api/v1/relays/99", json={"state": "on"})
        assert resp.status_code == 404

    def test_set_invalid_state_returns_422(self, client: TestClient):
        resp = client.put("/api/v1/relays/1", json={"state": "maybe"})
        assert resp.status_code == 422

    def test_set_missing_body_returns_422(self, client: TestClient):
        resp = client.put("/api/v1/relays/1")
        assert resp.status_code == 422

    def test_disconnected_returns_503(self, client_disconnected: TestClient):
        resp = client_disconnected.put("/api/v1/relays/1", json={"state": "on"})
        assert resp.status_code == 503

    def test_set_does_not_affect_other_channels(self, client: TestClient):
        client.put("/api/v1/relays/1", json={"state": "on"})
        resp = client.get("/api/v1/relays/2")
        assert resp.json()["state"] == "off"


# ─── GET /api/v1/relays/device/info ───


class TestDeviceInfo:
    def test_returns_device_info(self, client: TestClient):
        resp = client.get("/api/v1/relays/device/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["manufacturer"] == "MockManufacturer"
        assert data["product"] == "MockRelay"
        assert data["channels"] == 2
        assert data["connected"] is True

    def test_disconnected_device_info(self, client_disconnected: TestClient):
        resp = client_disconnected.get("/api/v1/relays/device/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["connected"] is False
        assert data["manufacturer"] == "Unknown"
