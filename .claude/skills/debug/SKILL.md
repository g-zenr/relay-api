---
name: debug
description: Systematically investigate an error from a traceback, log, or unexpected behavior
disable-model-invocation: true
---

Debug the following issue: $ARGUMENTS

## Step 1 — Gather Evidence
- Read the full error traceback or log output
- Identify the exception type and message
- Identify the file and line number where the error originates
- Note any relevant request data, state, or configuration

## Step 2 — Reproduce
- Write a minimal test that triggers the error:
  ```python
  def test_reproduces_issue(self, client: TestClient) -> None:
      resp = client.<method>("<path>", ...)
      # This should reproduce the error
  ```
- Run it to confirm it fails:
  ```bash
  python -m pytest tests/<file>.py::<TestClass>::<test_method> -v --tb=long
  ```

## Step 3 — Trace the Call Path
Follow the error through the architecture layers:
1. **API layer** (`app/api/v1/`) — Route handler, request parsing, DI
2. **Dependencies** (`app/api/dependencies.py`) — Auth, service injection
3. **Service layer** (`app/services/relay_service.py`) — Business logic, thread safety
4. **Core layer** (`app/core/device.py`) — Device communication, HID protocol
5. **Config** (`app/config.py`) — Settings, environment variables

For each layer, ask:
- Is the input valid at this point?
- Is the exception being caught or propagated correctly?
- Is thread safety maintained?
- Is the device state consistent?

## Step 4 — Isolate the Root Cause
- Narrow down to the specific line/condition that causes the failure
- Check for common issues:
  - **Device errors**: Is the device open? Is the channel valid?
  - **Auth errors**: Is the API key configured? Is `hmac.compare_digest` being used?
  - **State errors**: Is `_states` dict in sync with actual device state?
  - **Thread errors**: Is `_lock` being held during device access?
  - **Config errors**: Is the env var set? Is the type correct?

## Step 5 — Fix
- Implement the fix in the correct layer
- Use typed exceptions — no generic `Exception`
- Maintain thread safety if touching service layer
- Maintain rollback semantics if touching multi-channel operations

## Step 6 — Verify
- The reproduction test MUST now pass
- Run full suite:
  ```bash
  python -m pytest tests/ -v --tb=short
  python -m mypy app/
  ```
- Check for similar patterns elsewhere in the codebase that might have the same issue

## Step 7 — Document
- If the root cause was non-obvious, add a code comment explaining why the fix works
- If the issue could recur, suggest a preventive measure (test, validation, assertion)
