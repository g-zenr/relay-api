---
name: deploy-check
description: Validate deployment readiness — Docker, config, health, logging (Marcus Chen's workflow)
disable-model-invocation: true
---

Validate deployment readiness for the Relay API.

Follow Marcus Chen's infrastructure standards:

## 1. Configuration Validation
- Read `app/config.py` — verify every setting has `RELAY_` prefix
- Read `.env.example` — verify every Settings field is documented
- Verify no hardcoded values in source (search for literal IPs, ports, device IDs)
- Verify no `input()` or `print()` calls anywhere in `app/`

## 2. Health Endpoint
- Read `app/api/v1/system.py` — verify `/health` returns:
  - `status`: "ok" or "degraded"
  - `device_connected`: boolean
  - `version`: string
- Verify health bypasses authentication (`get_relay_service_public`)
- Verify response model is `HealthResponse`

## 3. Startup & Shutdown
- Read `app/main.py` lifespan handler:
  - `all_off()` called on startup (if device connected)
  - `all_off()` called on shutdown (if device connected)
  - Device `close()` called on shutdown
  - All events logged with appropriate levels (INFO/WARNING)
- Verify graceful degradation when device is absent (catches exception, logs warning, continues)

## 4. Docker
- Read `Dockerfile` — verify:
  - Multi-stage build (builder + runtime)
  - Non-root user in runtime stage
  - `HEALTHCHECK` instruction present
  - No secrets baked into image
  - `.dockerignore` excludes venv, .env, __pycache__, .git

## 5. Logging
- Verify structured log format: `%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`
- Verify no `print()` statements in production code
- Verify no secrets (API keys) logged at any level
- Verify audit logger (`relay.audit`) is used for state changes

## 6. Dependencies
- Read `requirements.txt` — verify all deps have minimum versions
- Check for known vulnerabilities: `pip audit` (if available)

## 7. Tests
- Run `python -m pytest tests/ -v --tb=short`
- Run `python -m mypy app/`
- Both MUST pass clean

## Output
Report as: **PASS** / **FAIL** / **WARN** for each section with specific findings.
