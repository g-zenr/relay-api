from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_ok_when_connected(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["device_connected"] is True
        assert "version" in data

    def test_health_degraded_when_disconnected(
        self, client_disconnected: TestClient
    ):
        resp = client_disconnected.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["device_connected"] is False

    def test_health_includes_version(self, client: TestClient):
        resp = client.get("/health")
        assert resp.json()["version"] == "1.0.0"


class TestSwaggerDocs:
    def test_docs_endpoint_available(self, client: TestClient):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_endpoint_available(self, client: TestClient):
        resp = client.get("/redoc")
        assert resp.status_code == 200

    def test_openapi_json_available(self, client: TestClient):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "Relay API"
        assert "/api/v1/relays" in schema["paths"]
        assert "/health" in schema["paths"]
