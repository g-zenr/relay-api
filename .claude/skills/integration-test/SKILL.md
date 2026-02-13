---
name: integration-test
description: Write end-to-end integration tests that exercise full request-to-device flows (Priya Sharma's workflow)
disable-model-invocation: true
---

Write integration tests for: $ARGUMENTS

Integration tests differ from unit tests — they exercise the FULL path from HTTP request through auth, service, device, and back.

## Step 1 — Identify Integration Scenarios
Map complete user workflows:
- Full request lifecycle: HTTP → Auth → Service → Device → Response
- Multi-step workflows: Set channel → verify state → set all → verify all
- Error recovery: Device disconnect mid-operation → reconnect → verify state
- Auth flows: No key → rejected, wrong key → rejected, correct key → success
- Rate limiting: Within limit → success, exceed limit → 429 → wait → success

## Step 2 — Write Integration Test Fixtures
```python
@pytest.fixture()
def integration_client() -> Generator[TestClient, None, None]:
    """Full integration client with real service chain — no dependency overrides."""
    device = MockRelayDevice(channels=2)
    device.open()
    service = RelayService(device, channels=2)
    init_relay_service(service)
    # NO dependency overrides — tests the real DI chain
    yield TestClient(app, raise_server_exceptions=False)
```

## Step 3 — Write Integration Tests

### Workflow tests (multi-step):
```python
class TestRelayWorkflow:
    def test_full_relay_lifecycle(self, integration_client):
        # Set channel ON
        resp = integration_client.put("/api/v1/relays/1", json={"state": "on"})
        assert resp.status_code == 200
        assert resp.json()["state"] == "on"

        # Verify state persists
        resp = integration_client.get("/api/v1/relays/1")
        assert resp.json()["state"] == "on"

        # Set all OFF
        resp = integration_client.put("/api/v1/relays", json={"state": "off"})
        assert resp.status_code == 200

        # Verify all channels OFF
        resp = integration_client.get("/api/v1/relays")
        for relay in resp.json():
            assert relay["state"] == "off"
```

### Error recovery tests:
```python
class TestErrorRecovery:
    def test_device_error_returns_503_and_state_unchanged(self, ...):
        # Set initial state
        # Simulate device failure
        # Verify 503 response
        # Verify state rolled back
```

### Cross-cutting tests:
```python
class TestCrossCutting:
    def test_health_returns_ok_while_device_connected(self, ...):
    def test_health_returns_degraded_when_disconnected(self, ...):
    def test_audit_log_produced_for_every_state_change(self, ...):
```

## Step 4 — Organize
Place integration tests in `tests/test_integration.py` (separate from unit tests).

## Step 5 — Verify
```bash
python -m pytest tests/test_integration.py -v --tb=short
python -m pytest tests/ -v --tb=short  # Full suite still passes
```

## Rules
- Integration tests use the REAL DI chain — minimal or no dependency overrides
- Test multi-step workflows, not individual operations
- Verify side effects (audit logs, state persistence) across steps
- Keep integration tests independent — each test resets state
