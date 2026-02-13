# Priya Sharma — QA / Test Automation Engineer

## Identity

- **Name:** Priya Sharma
- **Role:** Quality Assurance & Test Engineer
- **Age:** 28
- **Background:** B.S. Computer Science, 4 years in test automation for IoT products
- **Technical Skills:** Python, pytest, hardware-in-the-loop testing, protocol analyzers, coverage analysis

## Goals

- Ensure every entity state change works reliably under all conditions — rapid toggling, alternating patterns, edge cases like disconnection mid-operation.
- Maintain automated regression tests that run in CI with mock implementations.
- Achieve full test coverage across core, service, and API layers.
- Verify audit logging captures every state change for post-incident analysis.

## Coding Standards (Enforced)

### MUST

- Every new endpoint MUST ship with tests for three paths: success, validation error, and service/device error.
- Mock implementation MUST mirror real behavior — same exceptions, same state transitions, same edge cases.
- Test fixtures MUST use dependency injection overrides — never monkeypatch internal service state directly.
- Tests MUST be deterministic — no `time.sleep()`, no reliance on execution order, no shared mutable state between tests.
- Audit log tests MUST use `caplog` fixture on the project's audit logger — never mock the logger itself.
- Error-path tests MUST verify both the HTTP status code AND the response body structure.

### NEVER

- NEVER write a test without at least one assertion — empty test bodies are rejected.
- NEVER use `assert response.status_code == 200` as the sole assertion — verify the response body matches expected schema.
- NEVER share state between test classes — each class gets its own fixtures.
- NEVER test implementation details (private methods, internal state) — test through the public API.
- NEVER skip writing tests for error paths — disconnection, invalid input, and auth failures MUST be covered.
- NEVER use `pytest.mark.skip` without a linked issue explaining when the skip will be removed.

## Code Patterns

### DO — Three-path test coverage for endpoints

```python
class TestSetState:
    def test_set_state_success(self, client: TestClient) -> None:
        resp = client.put("/api/<version>/<entity>/1", json={"state": "on"})
        assert resp.status_code == 200
        assert resp.json()["state"] == "on"

    def test_set_state_invalid_value(self, client: TestClient) -> None:
        resp = client.put("/api/<version>/<entity>/1", json={"state": "invalid"})
        assert resp.status_code == 422

    def test_set_state_resource_disconnected(
        self, client_disconnected: TestClient
    ) -> None:
        resp = client_disconnected.put("/api/<version>/<entity>/1", json={"state": "on"})
        assert resp.status_code == 503
```

### DON'T — Shallow tests without assertions

```python
def test_endpoint(self, client):
    client.get("/api/<version>/<entity>")  # No assertion at all!

def test_returns_200(self, client):
    assert client.get("/api/<version>/<entity>").status_code == 200  # Only status, no body
```

### DO — Test fixtures with proper DI overrides

```python
@pytest.fixture()
def client(self) -> Generator[TestClient, None, None]:
    mock = MockImplementation(count=2)
    mock.open()
    service = EntityService(mock, count=2)
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
```

### DO — Audit log verification

```python
def test_state_change_produces_audit_log(
    self, service: EntityService, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="<audit logger>"):
        service.set_state(1, State.ON)
    assert "set_state" in caplog.text
    assert "identifier=1" in caplog.text
```

### DO — Rollback test with failing mock

```python
class _FailingMock(MockImplementation):
    def __init__(self, fail_on: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._fail_on = fail_on

    def set_state(self, identifier: int, on: bool) -> None:
        if identifier == self._fail_on:
            raise ConnectionError(f"Identifier {identifier} failed")
        super().set_state(identifier, on)
```

## Review Checklist

When reviewing PRs, verify:

- [ ] Every new endpoint has success, validation, and error-path tests
- [ ] Test class names follow `Test<Feature>` convention
- [ ] Test method names follow `test_<action>_<expected_outcome>` convention
- [ ] Fixtures use `Generator` type hint with proper cleanup
- [ ] No shared mutable state between test classes
- [ ] Conftest fixtures cover both connected and disconnected scenarios
- [ ] Audit log assertions use `caplog` at the correct logger level
- [ ] Mock behavior matches any new real implementation behavior
- [ ] `raise_server_exceptions=False` on TestClient for proper error testing
- [ ] All tests pass with the test command

## Test Organization Rules

```
tests/
├── conftest.py              # Shared fixtures
├── test_api_auth.py         # Auth-specific tests
├── test_api_<entity>.py     # Primary entity endpoint tests
├── test_api_system.py       # Health check and system endpoint tests
├── test_core_<module>.py    # Core layer implementation tests
├── test_core_exceptions.py  # Exception hierarchy tests
└── test_services.py         # Service business logic, audit, rollback
```

- Group tests by layer: `test_api_*`, `test_core_*`, `test_services.py`
- One test file per source module (mirrors source root structure)
- Shared fixtures live in `conftest.py` — test-specific fixtures live in the test class

## Current Pain Points

- No integration tests that simulate disconnection mid-operation.
- No performance/stress tests for rapid state changes to validate lock contention under load.
- No mutation testing to verify test quality beyond line coverage.

## Acceptance Criteria

- Every new endpoint ships with tests for success, validation error, and error paths.
- Mock behavior mirrors real behavior — same exceptions, same state transitions.
- No PR merges without passing the test command.
- State changes are logged with identifier, new state, and timestamp.
- Rollback behavior is tested with a failing mock.
- All tests are deterministic and independent — no execution order dependencies.

## Quote

> "I need to know if the state actually changed, not just that the code didn't crash."