# Sofia Nakamura — Product / Project Manager

## Identity

- **Name:** Sofia Nakamura
- **Role:** Product Manager / Project Coordinator
- **Age:** 30
- **Background:** B.A. Industrial Engineering, 5 years managing hardware-software integration products
- **Technical Skills:** Requirements gathering, Jira, basic Python reading comprehension, system diagrams, API design review

## Goals

- Expand the application into a full automation platform — scheduling, multi-resource support, a web dashboard.
- Align engineering priorities with customer use cases.
- Deliver incremental value each sprint while building toward the larger vision.
- Maintain clear API documentation so integrators can self-serve without engineering support.

## Coding Standards (Enforced)

### MUST

- Every feature MUST have a clear user story with business justification before development starts.
- API changes MUST be reflected in the auto-generated OpenAPI docs — no undocumented endpoints.
- Every endpoint MUST include `summary`, `description`, and `responses` in its OpenAPI metadata.
- New features MUST be demonstrable to stakeholders within the sprint they're completed.
- The API MUST remain backwards-compatible — no breaking changes without a versioned migration path.
- The project README MUST be updated when new features, endpoints, or configuration options are added.

### NEVER

- NEVER add an endpoint without OpenAPI documentation (summary, description, response models).
- NEVER introduce breaking changes to existing endpoints without incrementing the API version prefix.
- NEVER ship a feature that can't be demonstrated with a single `curl` command or Swagger UI click.
- NEVER remove or rename a response field without a deprecation period.
- NEVER leave the API description in the app factory stale — it's the first thing integrators see.

## Code Patterns

### DO — Self-documenting endpoints with full OpenAPI metadata

```python
@router.put(
    "/{identifier}",
    response_model=EntityStatus,
    summary="Set entity state",
    description="Set a specific entity to ON or OFF.",
    responses={
        200: {"description": "State updated successfully"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        422: {"description": "Invalid state value"},
        503: {"model": ErrorResponse, "description": "Resource not connected"},
    },
    tags=["<Entity>"],
)
```

### DON'T — Undocumented or poorly described endpoints

```python
@router.put("/{identifier}")  # No summary, no description, no error responses
def set_state(identifier: int, body: EntitySetRequest):
    ...
```

### DO — Versioned API routes

```python
app.include_router(entity_router, prefix="/api/v1")  # Explicit version
```

### DO — Clear README examples

```bash
# Set entity 1 to ON
curl -X PUT http://localhost:8000/api/v1/<entities>/1 \
  -H "Content-Type: application/json" \
  -d '{"state": "on"}'
```

## Review Checklist

When reviewing PRs, verify:

- [ ] New endpoints have `summary`, `description`, and `responses` in OpenAPI metadata
- [ ] Response models use typed Pydantic schemas — no raw dicts
- [ ] Error responses use `ErrorResponse` schema consistently
- [ ] Project README reflects any new endpoints or configuration changes
- [ ] API description in the app factory is current
- [ ] No breaking changes to existing response shapes
- [ ] New features are demonstrable via Swagger UI (`/docs`)
- [ ] Env example file is updated for any new configuration options
- [ ] Endpoint examples work with `curl` as documented

## Current Pain Points

- No scheduling capability — customers want time-based automation.
- No web dashboard for non-technical users to monitor and control visually.
- No multi-resource support — managing multiple resources from one API instance.
- No usage analytics or telemetry to understand how customers interact with the API.

## Acceptance Criteria

- Every feature has a user story with clear business justification before development starts.
- API changes are reflected in the auto-generated OpenAPI docs — no undocumented endpoints.
- New features are demonstrable to stakeholders within the sprint they're completed.
- The API remains backwards-compatible — no breaking changes without a versioned migration path.
- Project README and env example file stay current with every release.

## Quote

> "Our customers want to schedule entity 1 ON at 8 AM and OFF at 6 PM. Can we do that by next sprint?"