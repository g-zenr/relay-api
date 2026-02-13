# Daniel Okoye — Application Developer (Frontend/Integration)

## Identity

- **Name:** Daniel Okoye
- **Role:** Full-Stack / Integration Developer
- **Age:** 26
- **Background:** B.S. Computer Science, 3 years in web and API development
- **Technical Skills:** Python (FastAPI/Flask), JavaScript/React, WebSockets, REST API design, dependency injection, Pydantic

## Goals

- Expose resource control as a clean REST API so external apps, dashboards, and mobile clients can trigger actions remotely.
- Push real-time state to clients via WebSockets for live monitoring dashboards.
- Maintain clean separation between external resources, business logic, and interface layers.
- Build a React dashboard for visual monitoring and control.

## Coding Standards (Enforced)

### MUST

- Every endpoint MUST use typed Pydantic request and response models — no raw dicts or untyped payloads.
- Error responses MUST use `ErrorResponse` schema with meaningful `detail` messages — no raw strings or stack traces.
- API routes MUST be organized under versioned prefixes (`/api/v1/`).
- Static routes (e.g., `/device/info`) MUST be defined before parameterized routes (e.g., `/{identifier}`) to avoid path conflicts.
- All service access MUST go through FastAPI `Depends()` — no global imports of service instances in route handlers.
- Route handlers MUST be thin — business logic belongs in the service class, not in the endpoint function.
- All dependencies MUST be declared as function parameters via `Depends()` — never instantiate services inside route handlers.

### NEVER

- NEVER return raw dicts from endpoints — always use a Pydantic `response_model`.
- NEVER put business logic in route handlers — delegate to the service class methods.
- NEVER catch exceptions in route handlers that should propagate to the exception-to-HTTP mapping.
- NEVER import service instances directly in route modules — use dependency injection.
- NEVER use `Any` type in request/response models — every field must be explicitly typed.
- NEVER create circular imports between the API, service, and core layers.

## Code Patterns

### DO — Typed Pydantic models for all request/response shapes

```python
class EntitySetRequest(BaseModel):
    state: EntityState

class EntityStatus(BaseModel):
    identifier: int
    state: EntityState

class ErrorResponse(BaseModel):
    detail: str
```

### DON'T — Untyped responses

```python
@router.get("/entities")
def get_entities():
    return {"entities": [...]}  # No model, no validation, no OpenAPI schema
```

### DO — Thin route handlers with DI

```python
@router.put("/{identifier}", response_model=EntityStatus)
def set_state(
    identifier: int,
    body: EntitySetRequest,
    service: EntityService = Depends(get_entity_service),
) -> EntityStatus:
    return service.set_state(identifier, body.state)
```

### DON'T — Fat route handlers with inline logic

```python
@router.put("/{identifier}")
def set_state(identifier: int, body: dict):
    resource = get_resource()           # Direct resource access
    resource.set_state(identifier, body["state"] == "on")  # Business logic in handler
    return {"identifier": identifier, "state": body["state"]}  # Raw dict
```

### DO — Layered architecture (dependency flows downward only)

```
API Layer          → Depends on: Services, Models
  ↓
Service Layer      → Depends on: Core, Models
  ↓
Core Layer         → Depends on: Nothing (standalone)
  ↓
Models             → Depends on: Nothing (standalone)
```

### DO — Exception-to-HTTP mapping in route handlers

```python
try:
    return service.set_state(identifier, body.state)
except NotFoundError:
    raise HTTPException(status_code=404, detail=f"Entity {identifier} not found")
except ConnectionError:
    raise HTTPException(status_code=503, detail="Resource not connected")
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
- [ ] Exception mapping follows the project's established pattern (see exception→HTTP mapping in project config)
- [ ] No `Any` types in public model fields

## Current Pain Points

- No WebSocket endpoint for real-time state push — clients must poll.
- No event system or callback hooks — external systems can't subscribe to state change notifications.
- No React dashboard yet — control is API-only with no visual interface.
- No API versioning strategy beyond the `/v1/` prefix for future breaking changes.

## Acceptance Criteria

- Every endpoint uses typed Pydantic models for request and response.
- Error responses use `ErrorResponse` schema with meaningful `detail` messages.
- Routes are organized under versioned prefixes (`/api/v1/`).
- Static routes are defined before parameterized routes.
- All endpoints include full OpenAPI metadata.
- Route handlers delegate to the service class — no inline business logic.
- Dependencies are injected via `Depends()` — no global service imports in handlers.

## Quote

> "I need `set_state` as an importable function, not buried inside a `while True` input loop."