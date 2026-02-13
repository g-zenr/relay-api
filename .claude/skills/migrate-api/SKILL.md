---
name: migrate-api
description: Migrate API from one version to the next (v1 → v2) with backwards compatibility (Sofia + Daniel's workflow)
disable-model-invocation: true
---

Migrate the API: $ARGUMENTS

## Step 1 — Identify Breaking Changes
Read the current API and identify what needs to change:
- Renamed or removed endpoints
- Changed request/response schemas
- Changed authentication flow
- Changed error response format
- Changed URL paths or parameter names

Categorize each change:
- **Breaking**: Clients will fail without code changes
- **Additive**: New fields/endpoints — existing clients unaffected
- **Deprecation**: Old behavior still works but is discouraged

## Step 2 — Design the New Version
Create the new API version structure:
```
app/api/v2/
├── __init__.py
├── relays.py      # Updated endpoints
└── system.py      # Updated system endpoints
```

### Rules:
- v1 endpoints MUST continue working unchanged
- v2 endpoints live in a new router with `/api/v2/` prefix
- Shared logic stays in `app/services/` — NOT duplicated per version
- New Pydantic models can extend or replace v1 models

## Step 3 — Implement v2
1. Create `app/api/v2/` directory with new router files
2. Add new Pydantic models to `app/models/schemas.py` (suffix with `V2` if different)
3. Register the v2 router in `app/main.py`:
   ```python
   from app.api.v2.relays import router as relays_v2_router
   app.include_router(relays_v2_router, prefix="/api/v2")
   ```
4. v1 router remains registered and functional

## Step 4 — Deprecation Headers
Add deprecation headers to v1 endpoints:
```python
from fastapi import Response

@router.get("/relays")
def get_relays(response: Response, ...):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2025-12-31"
    response.headers["Link"] = '</api/v2/relays>; rel="successor-version"'
    ...
```

## Step 5 — Tests
- v1 tests MUST still pass unchanged (backwards compatibility)
- Write new tests for v2 endpoints in `tests/test_api_v2_relays.py`
- Test that v1 responses include deprecation headers

## Step 6 — Documentation
- Update `README.md` with both v1 and v2 endpoint tables
- Update OpenAPI description noting v1 deprecation
- Add migration guide for consumers

## Step 7 — Verify
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
ALL tests pass — both v1 and v2.