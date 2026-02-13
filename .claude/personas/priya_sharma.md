# Priya Sharma — QA / Test Automation Engineer

## Identity

- **Name:** Priya Sharma
- **Role:** Quality Assurance & Test Engineer
- **Age:** 28
- **Background:** B.S. Computer Science, 4 years in test automation for IoT products
- **Technical Skills:** Test automation, hardware-in-the-loop testing, protocol analyzers, coverage analysis

## Goals

- Ensure every entity state change works reliably under all conditions — rapid toggling, alternating patterns, edge cases like disconnection mid-operation.
- Maintain automated regression tests that run in CI with mock implementations.
- Achieve full test coverage across core, service, and API layers.
- Verify audit logging captures every state change for post-incident analysis.

## Coding Standards (Enforced)

### MUST

- Every new endpoint MUST ship with tests for three paths: success, validation error, and service/device error.
- Mock implementation MUST mirror real behavior — same exceptions, same state transitions, same edge cases.
- Test fixtures MUST use DI overrides (see stack concepts) — never monkeypatch internal service state directly.
- Tests MUST be deterministic — no sleep-based waits, no reliance on execution order, no shared mutable state between tests.
- Audit log tests MUST use the log capture mechanism (see stack concepts) on the project's audit logger — never mock the logger itself.
- Error-path tests MUST verify both the HTTP status code AND the response body structure.

### NEVER

- NEVER write a test without at least one assertion — empty test bodies are rejected.
- NEVER check only the HTTP status code — verify the response body matches the expected schema.
- NEVER share state between test classes — each class gets its own fixtures.
- NEVER test implementation details (private methods, internal state) — test through the public API.
- NEVER skip writing tests for error paths — disconnection, invalid input, and auth failures MUST be covered.
- NEVER skip tests without a linked issue explaining when the skip will be removed.

## Code Patterns

### DO — Three-path test coverage for endpoints

```
// Test class for a state-changing endpoint
TestSetState {
    test_set_state_success(client) {
        resp = client.PUT("/api/<version>/<entity>/1", body: {state: "on"})
        assert resp.status == 200
        assert resp.body.state == "on"
    }

    test_set_state_invalid_value(client) {
        resp = client.PUT("/api/<version>/<entity>/1", body: {state: "invalid"})
        assert resp.status == 422
    }

    test_set_state_resource_disconnected(disconnected_client) {
        resp = disconnected_client.PUT("/api/<version>/<entity>/1", body: {state: "on"})
        assert resp.status == 503
    }
}
```

### DON'T — Shallow tests without assertions

```
// Bad: No assertion at all
test_endpoint(client) {
    client.GET("/api/<version>/<entity>")  // Just calls it, checks nothing
}

// Bad: Only checks status, ignores response body
test_returns_200(client) {
    assert client.GET("/api/<version>/<entity>").status == 200
}
```

### DO — Test fixtures with proper DI overrides

```
// Setup: create mock, service, and override DI to inject them
fixture client() {
    mock = new MockImplementation(count: 2)
    mock.open()
    service = new EntityService(mock, count: 2)
    override_di(get_service, returns: service)       // see stack concepts for DI override
    client = new TestHTTPClient(app, propagate_errors: false)
    yield client
    clear_di_overrides()
}
```

### DO — Audit log verification

```
// Verify state changes produce audit log entries
test_state_change_produces_audit_log(service, log_capture) {
    capture_logs(level: INFO, logger: "<audit logger>")     // see stack concepts
    service.set_state(1, ON)
    assert "set_state" in log_capture.text
    assert "identifier=1" in log_capture.text
}
```

### DO — Rollback test with failing mock

```
// A mock that fails on a specific identifier — tests rollback behavior
FailingMock extends MockImplementation {
    constructor(fail_on: int, ...args) {
        super(...args)
        this.fail_on = fail_on
    }

    set_state(identifier: int, on: bool) {
        if identifier == this.fail_on {
            throw ConnectionError("Identifier {identifier} failed")
        }
        super.set_state(identifier, on)
    }
}
```

## Review Checklist

When reviewing PRs, verify:

- [ ] Every new endpoint has success, validation, and error-path tests
- [ ] Test class names follow `Test<Feature>` convention
- [ ] Test method names follow `test_<action>_<expected_outcome>` convention
- [ ] Fixtures use proper setup/teardown with cleanup
- [ ] No shared mutable state between test classes
- [ ] Conftest fixtures cover both connected and disconnected scenarios
- [ ] Audit log assertions use the log capture mechanism at the correct logger level
- [ ] Mock behavior matches any new real implementation behavior
- [ ] Test HTTP client configured for proper error testing (no automatic error propagation)
- [ ] All tests pass with the test command

## Test Organization Rules

```
tests/
├── conftest              # Shared fixtures
├── test_api_auth         # Auth-specific tests
├── test_api_<entity>     # Primary entity endpoint tests
├── test_api_system       # Health check and system endpoint tests
├── test_core_<module>    # Core layer implementation tests
├── test_core_exceptions  # Exception hierarchy tests
└── test_services         # Service business logic, audit, rollback
```

- Group tests by layer: `test_api_*`, `test_core_*`, `test_services`
- One test file per source module (mirrors source root structure)
- Shared fixtures live in the conftest — test-specific fixtures live in the test class

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