---
name: fix-issue
description: Investigate and fix a bug from a report, traceback, log, or unexpected behavior
disable-model-invocation: true
---

Investigate and fix: $ARGUMENTS

## Step 1 — Gather Evidence
- Read the full error traceback, log output, or bug report
- Identify the exception type, message, file, and line number
- Note any relevant request data, state, or configuration
- Check if a test already covers this case

## Step 2 — Reproduce
Write a minimal test that triggers the error:
```python
def test_reproduces_issue(self, client: TestClient) -> None:
    resp = client.<method>("<path>", ...)
    # This should reproduce the error
```
Run it to confirm it fails:
```bash
python -m pytest tests/<file>.py::<TestClass>::<test_method> -v --tb=long
```

## Step 3 — Diagnose
Trace the error through the architecture layers:
1. **API layer** (`app/api/v1/`) — Route handler, request parsing, DI
2. **Dependencies** (`app/api/dependencies.py`) — Auth, service injection
3. **Service layer** (`app/services/relay_service.py`) — Business logic, thread safety
4. **Core layer** (`app/core/device.py`) — Device communication, HID protocol
5. **Config** (`app/config.py`) — Settings, environment variables

For each layer, ask:
- Is the input valid at this point?
- Is the exception caught or propagated correctly?
- Is thread safety maintained?
- Is the device state consistent?

### Common root causes:
- **Device errors**: Device not open, invalid channel
- **Auth errors**: API key misconfigured, missing `hmac.compare_digest`
- **State errors**: `_states` dict out of sync with actual device state
- **Thread errors**: `_lock` not held during device access
- **Config errors**: Env var not set or wrong type

## Step 4 — Fix
- Fix in the correct layer (device → service → API)
- Use typed exceptions, not generic `Exception`
- Maintain thread safety if touching service layer
- Rollback semantics if touching multi-channel operations

## Step 5 — Verify
- The reproduction test MUST now pass
- Run full suite:
  ```bash
  python -m pytest tests/ -v --tb=short
  python -m mypy app/
  ```

## Step 6 — Audit
- Are there similar patterns elsewhere that have the same bug?
- Does the fix maintain backwards compatibility?
- If the root cause was non-obvious, add a code comment explaining why
- If the issue could recur, suggest a preventive measure