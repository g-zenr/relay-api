---
name: test
description: Write comprehensive tests for a module or feature (Priya Sharma's workflow)
---

Write tests for: $ARGUMENTS

Follow Priya Sharma's testing standards:

1. **Identify scope**: Read the source code being tested. Understand every public method, edge case, and error path.

2. **Choose test file**: Match the `app/` structure:
   - `app/api/v1/relays.py` → `tests/test_api_relays.py`
   - `app/api/v1/system.py` → `tests/test_api_system.py`
   - `app/services/relay_service.py` → `tests/test_services.py`
   - `app/core/device.py` → `tests/test_core_device.py`

3. **Write three-path tests** for every endpoint or method:
   - **Success path**: Valid input → expected output, verify response body not just status code
   - **Validation error path**: Invalid input → 422 or `InvalidChannelError`
   - **Device error path**: Device disconnected → 503 or `DeviceConnectionError`

4. **Test conventions**:
   - Class names: `Test<Feature>` (e.g., `TestSetChannel`)
   - Method names: `test_<action>_<expected_outcome>` (e.g., `test_set_channel_returns_updated_state`)
   - Use `Generator[TestClient, None, None]` type hints on fixtures
   - Use `raise_server_exceptions=False` on TestClient
   - DI overrides via `app.dependency_overrides` with cleanup in teardown
   - Audit log assertions via `caplog.at_level(logging.INFO, logger="relay.audit")`
   - No `time.sleep()`, no shared mutable state, no execution order dependence

5. **Edge cases to always consider**:
   - Channel 0 (below minimum)
   - Channel > max channels (above maximum)
   - Invalid state values
   - Device disconnected mid-operation
   - Concurrent access patterns
   - Empty/null request bodies

6. **Verify**: Run `python -m pytest tests/ -v --tb=short` — all tests must pass
