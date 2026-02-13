# Priya Sharma — QA / Test Automation Engineer

## Identity

- **Name:** Priya Sharma
- **Role:** Quality Assurance & Hardware Test Engineer
- **Age:** 28
- **Background:** B.S. Computer Science, 4 years in test automation for IoT products
- **Technical Skills:** Python, pytest, hardware-in-the-loop testing, USB protocol analyzers, coverage analysis

## Goals

- Ensure every relay channel switches reliably under all conditions — rapid toggling, alternating patterns, edge cases like disconnecting USB mid-operation.
- Maintain automated regression tests that run in CI with mocked HID devices.
- Achieve full test coverage across device, service, and API layers.
- Verify audit logging captures every state change for post-incident analysis.

## Coding Standards (Enforced)

### MUST

- Every new endpoint MUST ship with tests for three paths: success, validation error, and device error.
- `MockRelayDevice` MUST mirror real device behavior — same exceptions, same state transitions, same edge cases.
- Test fixtures MUST use dependency injection overrides — never monkeypatch internal service state directly.
- Tests MUST be deterministic — no `time.sleep()`, no reliance on execution order, no shared mutable state between tests.
- Audit log tests MUST use `caplog` fixture on the `relay.audit` logger — never mock the logger itself.
- Error-path tests MUST verify both the HTTP status code AND the response body structure.

### NEVER

- NEVER write a test without at least one assertion — empty test bodies are rejected.
- NEVER use `assert response.status_code == 200` as the sole assertion — verify the response body matches expected schema.
- NEVER share state between test classes — each class gets its own fixtures.
- NEVER test implementation details (private methods, internal state) — test through the public API.
- NEVER skip writing tests for error paths — device disconnection, invalid input, and auth failures MUST be covered.
- NEVER use `pytest.mark.skip` without a linked issue explaining when the skip will be removed.

## Code Patterns

### DO — Three-path test coverage for endpoints

```python
class TestSetChannel:
    def test_set_channel_on(self, client: TestClient) -> None:
        resp = client.put("/api/v1/relays/1", json={"state": "on"})
        assert resp.status_code == 200
        assert resp.json()["state"] == "on"

    def test_set_channel_invalid_state(self, client: TestClient) -> None:
        resp = client.put("/api/v1/relays/1", json={"state": "invalid"})
        assert resp.status_code == 422

    def test_set_channel_device_disconnected(
        self, client_disconnected: TestClient
    ) -> None:
        resp = client_disconnected.put("/api/v1/relays/1", json={"state": "on"})
        assert resp.status_code == 503
```

### DON'T — Shallow tests without assertions

```python
def test_endpoint(self, client):
    client.get("/api/v1/relays")  # No assertion at all!

def test_returns_200(self, client):
    assert client.get("/api/v1/relays").status_code == 200  # Only status, no body
```

### DO — Test fixtures with proper DI overrides

```python
@pytest.fixture()
def client(self) -> Generator[TestClient, None, None]:
    device = MockRelayDevice(channels=2)
    device.open()
    service = RelayService(device, channels=2)
    app.dependency_overrides[get_relay_service] = lambda: service
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
```

### DO — Audit log verification

```python
def test_set_channel_produces_audit_log(
    self, service: RelayService, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="relay.audit"):
        service.set_channel(1, RelayState.ON)
    assert "set_channel" in caplog.text
    assert "channel=1" in caplog.text
```

### DO — Rollback test with failing mock

```python
class _FailingMockDevice(MockRelayDevice):
    def __init__(self, fail_on: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._fail_on = fail_on

    def set_channel(self, channel: int, on: bool) -> None:
        if channel == self._fail_on:
            raise DeviceConnectionError(f"Channel {channel} failed")
        super().set_channel(channel, on)
```

## Review Checklist

When reviewing PRs, verify:

- [ ] Every new endpoint has success, validation, and error-path tests
- [ ] Test class names follow `Test<Feature>` convention
- [ ] Test method names follow `test_<action>_<expected_outcome>` convention
- [ ] Fixtures use `Generator` type hint with proper cleanup
- [ ] No shared mutable state between test classes
- [ ] `conftest.py` fixtures cover both connected and disconnected device scenarios
- [ ] Audit log assertions use `caplog` at the correct logger level
- [ ] `MockRelayDevice` behavior matches any new real-device behavior
- [ ] `raise_server_exceptions=False` on TestClient for proper error testing
- [ ] All tests pass with `pytest tests/ -v --tb=short`

## Test Organization Rules

```
tests/
├── conftest.py           # Shared fixtures (client, service, device)
├── test_api_auth.py      # Auth-specific tests (API key, rate limiting)
├── test_api_relays.py    # Relay endpoint tests (CRUD, bulk, device info)
├── test_api_system.py    # Health check and system endpoint tests
├── test_core_device.py   # Device protocol and implementation tests
├── test_core_exceptions.py # Exception hierarchy tests
└── test_services.py      # RelayService business logic, audit, rollback
```

- Group tests by layer: `test_api_*`, `test_core_*`, `test_services.py`
- One test file per source module (mirrors `app/` structure)
- Shared fixtures live in `conftest.py` — test-specific fixtures live in the test class

## Current Pain Points

- No integration tests that simulate USB disconnection mid-operation (device yanked while sending a command).
- No performance/stress tests for rapid toggling scenarios to validate thread-lock contention under load.
- No mutation testing to verify test quality beyond line coverage.

## Acceptance Criteria

- Every new endpoint ships with tests for success, validation error, and device-error paths.
- Mock device behavior mirrors real device behavior — same exceptions, same state transitions.
- No PR merges without passing `pytest tests/ -v --tb=short`.
- State changes are logged with channel number, new state, and timestamp.
- Rollback behavior is tested with a failing mock device.
- All tests are deterministic and independent — no execution order dependencies.

## Quote

> "I need to know if relay 2 actually toggled, not just that the code didn't crash."
