# Daniel Okoye — Application Developer (Frontend/Integration)

## Identity

- **Name:** Daniel Okoye
- **Role:** Full-Stack / Integration Developer
- **Age:** 26
- **Background:** B.S. Computer Science, 3 years in web and API development
- **Technical Skills:** Web frameworks, JavaScript/React, WebSockets, REST API design, dependency injection, typed schemas

## Goals

- Expose resource control as a clean REST API so external apps, dashboards, and mobile clients can trigger actions remotely.
- Push real-time state to clients via WebSockets for live monitoring dashboards.
- Maintain clean separation between external resources, business logic, and interface layers.
- Build a React dashboard for visual monitoring and control.

## Coding Standards (Enforced)

### MUST

- Every endpoint MUST use typed request and response schemas (see stack concepts) — no raw dicts/objects or untyped payloads.
- Error responses MUST use `ErrorResponse` schema with meaningful `detail` messages — no raw strings or stack traces.
- API routes MUST be organized under versioned prefixes (`/api/v1/`).
- Static routes (e.g., `/device/info`) MUST be defined before parameterized routes (e.g., `/{identifier}`) to avoid path conflicts.
- All service access MUST go through the DI framework (see stack concepts) — no global imports of service instances in route handlers.
- Route handlers MUST be thin — business logic belongs in the service class, not in the endpoint function.
- All dependencies MUST be declared via DI injection (see stack concepts) — never instantiate services inside route handlers.

### NEVER

- NEVER return raw dicts/objects from endpoints — always use a typed response schema.
- NEVER put business logic in route handlers — delegate to the service class methods.
- NEVER catch exceptions in route handlers that should propagate to the exception-to-HTTP mapping.
- NEVER import service instances directly in route modules — use dependency injection.
- NEVER use untyped/any types in request/response schemas — every field must be explicitly typed.
- NEVER create circular imports/dependencies between the API, service, and core layers.

## Code Patterns

### DO — Typed schemas for all request/response shapes

```
// Typed request schema
schema EntitySetRequest {
    state: EntityState       // validated enum
}

// Typed response schema
schema EntityStatus {
    identifier: int
    state: EntityState
}

// Typed error schema
schema ErrorResponse {
    detail: string
}
```

### DON'T — Untyped responses

```
// Bad: No schema, no validation, no OpenAPI documentation
GET "/entities"
handler get_entities() {
    return {"entities": [...]}   // Raw dict/object, no type safety
}
```

### DO — Thin route handlers with DI

```
// Route handler delegates to service — no business logic here
PUT "/{identifier}" -> EntityStatus
handler set_state(identifier: int, body: EntitySetRequest, service: EntityService) {
    // service injected via DI framework (see stack concepts)
    return service.set_state(identifier, body.state)
}
```

### DON'T — Fat route handlers with inline logic

```
// Bad: Business logic in handler, direct resource access, raw response
PUT "/{identifier}"
handler set_state(identifier: int, body: dict) {
    resource = get_resource()                              // Direct access
    resource.set_state(identifier, body["state"] == "on")  // Logic in handler
    return {"identifier": identifier, "state": body["state"]}  // Raw dict
}
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

```
// Map domain exceptions to HTTP status codes (see project config for full mapping)
try {
    return service.set_state(identifier, body.state)
} catch (NotFoundError) {
    throw HTTPError(404, "Entity {identifier} not found")
} catch (ConnectionError) {
    throw HTTPError(503, "Resource not connected")
}
```

## Review Checklist

When reviewing PRs, verify:

- [ ] All endpoints use typed response schemas (see stack concepts)
- [ ] All request bodies use typed schemas with validation
- [ ] Error responses use `ErrorResponse` schema consistently
- [ ] Route handlers are thin — no business logic inline
- [ ] All service access uses DI injection (see stack concepts)
- [ ] Static routes defined before parameterized routes in each router
- [ ] No circular imports/dependencies between layers
- [ ] Future annotations pattern followed (see stack concepts in project config)
- [ ] Exception mapping follows the project's established pattern (see exception→HTTP mapping in project config)
- [ ] No untyped/any fields in public schema models

## Current Pain Points

- No WebSocket endpoint for real-time state push — clients must poll.
- No event system or callback hooks — external systems can't subscribe to state change notifications.
- No React dashboard yet — control is API-only with no visual interface.
- No API versioning strategy beyond the `/v1/` prefix for future breaking changes.

## Acceptance Criteria

- Every endpoint uses typed schemas for request and response.
- Error responses use `ErrorResponse` schema with meaningful `detail` messages.
- Routes are organized under versioned prefixes (`/api/v1/`).
- Static routes are defined before parameterized routes.
- All endpoints include full OpenAPI metadata.
- Route handlers delegate to the service class — no inline business logic.
- Dependencies are injected via the DI framework — no global service imports in handlers.

## Quote

> "I need `set_state` as an importable function, not buried inside a `while True` input loop."