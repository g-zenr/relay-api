# Relay API — Claude Code Instructions

REST API for controlling DCT Tech USB relay modules via HID. FastAPI + Python 3.12.

## Commands

```bash
# Run tests (use this to verify changes)
python -m pytest tests/ -v --tb=short

# Type checking
python -m mypy app/

# Run the app (mock mode)
RELAY_MOCK=true python run.py
```

## Architecture

```
app/core/device.py    → RelayDevice protocol + HID/Mock implementations (hardware layer)
app/services/         → RelayService: thread-safe business logic + audit logging
app/api/              → FastAPI routes, DI, auth (thin handlers only)
app/models/schemas.py → Pydantic request/response models
app/config.py         → Pydantic BaseSettings with RELAY_ prefix
app/middleware.py     → Rate limiting middleware
tests/                → pytest tests mirroring app/ structure
```

Dependency flow: `API → Services → Core`. Never reverse this direction.

## Coding Standards

These apply to ALL code in this project. Violations block PR merges.

### Types & Safety

- `from __future__ import annotations` in EVERY source file
- All functions MUST have return type annotations
- All Pydantic models MUST use explicit field types — no `Any`
- Run `mypy app/` — must pass clean with zero errors

### Device Layer (`app/core/`)

- All device implementations MUST satisfy the `RelayDevice` Protocol
- Device errors MUST raise typed exceptions: `DeviceNotFoundError`, `DeviceConnectionError`, `InvalidChannelError`
- NEVER catch and swallow exceptions silently — log and re-raise
- `MockRelayDevice` MUST mirror real device behavior (same exceptions, same state transitions)

### Service Layer (`app/services/`)

- Thread safety via `threading.Lock()` — all device access is serialized
- Multi-channel operations MUST rollback completed channels on partial failure
- All state changes MUST produce audit log entries via the `relay.audit` logger
- `all_off()` MUST run on both startup and shutdown — fail-safe is non-negotiable

### API Layer (`app/api/`)

- Route handlers MUST be thin — delegate business logic to `RelayService`
- All service access via `Depends()` injection — never import service instances directly
- All endpoints use typed Pydantic `response_model` — no raw dicts
- Error responses use `ErrorResponse` schema — never expose stack traces or file paths
- Static routes before parameterized routes to avoid path conflicts
- Every endpoint MUST have `summary`, `description`, and `responses` in OpenAPI metadata

### Security

- API key comparison uses `hmac.compare_digest()` — NEVER use `==` for secrets
- Auth error messages are uniform: "Invalid or missing API key" — no differentiation
- Health endpoint bypasses auth (uses `get_relay_service_public`)
- NEVER log API keys or secrets at any log level
- Input validation via Pydantic constraints (`ge=1`, enums) — never trust raw input

### Configuration

- All config via env vars with `RELAY_` prefix in `app/config.py`
- NEVER hardcode host, port, device IDs, or feature flags
- NEVER use `input()` or `print()` — the app runs headless
- `.env.example` MUST document every env var with its default and purpose

### Testing

- Every endpoint needs three test paths: success, validation error, device error
- Test fixtures use DI overrides via `app.dependency_overrides` — proper cleanup in teardown
- Audit log tests use `caplog` on `relay.audit` logger
- Tests MUST be deterministic — no sleep, no execution order dependence
- Run `pytest tests/ -v --tb=short` after every change — all tests must pass

## Team Personas

Detailed coding standards, review checklists, and code patterns for each role:
@.claude/personas/alex_rivera.md (Hardware/Lead)
@.claude/personas/priya_sharma.md (QA/Testing)
@.claude/personas/marcus_chen.md (DevOps)
@.claude/personas/sofia_nakamura.md (Product)
@.claude/personas/daniel_okoye.md (App Developer)
@.claude/personas/janet_moore.md (Security)
