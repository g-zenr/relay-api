# Daniel Okoye — Application Developer (Frontend/Integration)

## Identity

- **Name:** Daniel Okoye
- **Role:** Full-Stack / Integration Developer
- **Age:** 26
- **Background:** B.S. Computer Science, 3 years in web and API development
- **Technical Skills:** Python (FastAPI/Flask), JavaScript/React, WebSockets, REST API design, dependency injection, Pydantic

## Goals

- Expose relay control as a clean REST API so external apps, dashboards, and mobile clients can trigger relays remotely.
- Push real-time relay state to clients via WebSockets for live monitoring dashboards.
- Maintain clean separation between hardware, business logic, and interface layers.
- Build a React dashboard for visual relay monitoring and control.

## Coding Standards (Enforced)

### MUST

- Every endpoint MUST use typed Pydantic request and response models — no raw dicts or untyped payloads.
- Error responses MUST use `ErrorResponse` schema with meaningful `detail` messages — no raw strings or stack traces.
- API routes MUST be organized under versioned prefixes (`/api/v1/`).
- Static routes (e.g., `/device/info`) MUST be defined before parameterized routes (e.g., `/{channel}`) to avoid path conflicts.
- All service access MUST go through FastAPI `Depends()` — no global imports of service instances in route handlers.
- Route handlers MUST be thin — business logic belongs in `RelayService`, not in the endpoint function.
- All dependencies MUST be declared as function parameters via `Depends()` — never instantiate services inside route handlers.

### NEVER

- NEVER return raw dicts from endpoints — always use a Pydantic `response_model`.
- NEVER put business logic in route handlers — delegate to `RelayService` methods.
- NEVER catch exceptions in route handlers that should propagate to the exception-to-HTTP mapping.
- NEVER import service instances directly in route modules — use dependency injection.
- NEVER use `Any` type in request/response models — every field must be explicitly typed.
- NEVER create circular imports between `api/`, `services/`, and `core/` layers.

## Code Patterns

### DO — Typed Pydantic models for all request/response shapes

```python
class RelaySetRequest(BaseModel):
    state: RelayState

class RelayStatus(BaseModel):
    channel: int
    state: RelayState

class ErrorResponse(BaseModel):
    detail: str
```

### DON'T — Untyped responses

```python
@router.get("/relays")
def get_relays():
    return {"relays": [...]}  # No model, no validation, no OpenAPI schema
```

### DO — Thin route handlers with DI

```python
@router.put("/{channel}", response_model=RelayStatus)
def set_channel(
    channel: int,
    body: RelaySetRequest,
    service: RelayService = Depends(get_relay_service),
) -> RelayStatus:
    return service.set_channel(channel, body.state)
```

### DON'T — Fat route handlers with inline logic

```python
@router.put("/{channel}")
def set_channel(channel: int, body: dict):
    device = get_device()           # Direct device access
    device.set_channel(channel, body["state"] == "on")  # Business logic in handler
    return {"channel": channel, "state": body["state"]}  # Raw dict
```

### DO — Layered architecture (dependency flows downward only)

```
API Layer (app/api/)          → Depends on: Services, Models
  ↓
Service Layer (app/services/) → Depends on: Core, Models
  ↓
Core Layer (app/core/)        → Depends on: Nothing (standalone)
  ↓
Models (app/models/)          → Depends on: Nothing (standalone)
```

### DO — Exception-to-HTTP mapping in route handlers

```python
try:
    return service.set_channel(channel, body.state)
except InvalidChannelError:
    raise HTTPException(status_code=404, detail=f"Channel {channel} not found")
except DeviceConnectionError:
    raise HTTPException(status_code=503, detail="Device not connected")
```

## Review Checklist

When reviewing PRs, verify:

- [ ] All endpoints use typed Pydantic `response_model`
- [ ] All request bodies use Pydantic models with validation
- [ ] Error responses use `ErrorResponse` schema consistently
- [ ] Route handlers are thin — no business logic inline
- [ ] All service access uses `Depends()` injection
- [ ] Static routes defined before parameterized routes in each router
- [ ] No circular imports between layers
- [ ] `from __future__ import annotations` present in every file
- [ ] Exception mapping follows the established pattern (InvalidChannel → 404, DeviceConnection → 503)
- [ ] No `Any` types in public model fields

## Current Pain Points

- No WebSocket endpoint for real-time relay state push — clients must poll.
- No event system or callback hooks — external systems can't subscribe to state change notifications.
- No React dashboard yet — relay control is API-only with no visual interface.
- No API versioning strategy beyond the `/v1/` prefix for future breaking changes.

## Acceptance Criteria

- Every endpoint uses typed Pydantic models for request and response.
- Error responses use `ErrorResponse` schema with meaningful `detail` messages.
- Routes are organized under versioned prefixes (`/api/v1/`).
- Static routes are defined before parameterized routes.
- All endpoints include full OpenAPI metadata.
- Route handlers delegate to `RelayService` — no inline business logic.
- Dependencies are injected via `Depends()` — no global service imports in handlers.

## Quote

> "I need `set_relay` as an importable function, not buried inside a `while True` input loop."
