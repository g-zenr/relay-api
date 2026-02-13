---
name: design-api
description: Design API contracts before implementation — endpoints, models, status codes (Daniel Okoye's workflow)
disable-model-invocation: true
---

Design the API contract for: $ARGUMENTS

Design BEFORE implementing. This produces a specification that /add-endpoint or /add-feature will implement.

## Step 1 — Requirements
- What problem does this API solve?
- Who are the consumers? (frontend, mobile, external integrators, automation)
- What data flows in and out?
- What error conditions exist?

## Step 2 — Endpoint Design
For each endpoint, define:

```markdown
### `METHOD /api/v1/<path>`
**Summary:** <one-line description>
**Auth:** Required / Public
**Request Body:**
```json
{
  "field": "type — description (constraints)"
}
```
**Response 200:**
```json
{
  "field": "type — description"
}
```
**Error Responses:**
| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Missing/invalid API key | `{"detail": "Invalid or missing API key"}` |
| 404 | Resource not found | `{"detail": "..."}` |
| 422 | Validation error | Pydantic validation error |
| 503 | Device disconnected | `{"detail": "Device not connected"}` |
```

## Step 3 — Pydantic Models
Define request/response schemas:
```python
class FeatureRequest(BaseModel):
    field: type = Field(..., description="...", ge=0)

class FeatureResponse(BaseModel):
    field: type
```
- Explicit types on every field — no `Any`
- Constraints via `Field()` — `ge`, `le`, `min_length`, `pattern`
- Enum types for fixed value sets

## Step 4 — Route Organization
- Determine which router file: `relays.py` or `system.py` (or new router?)
- Static routes MUST come before parameterized routes
- Version prefix: `/api/v1/`
- Consider path conflicts with existing routes

## Step 5 — Auth & Security
- Which endpoints modify state? → Require auth (`Depends(get_relay_service)`)
- Which endpoints are read-only monitoring? → Consider public access (`Depends(get_relay_service_public)`)
- What input validation is needed beyond Pydantic?
- Rate limiting implications?

## Step 6 — Backwards Compatibility
- Do any existing response shapes change? → Breaking change, needs versioning
- Do any existing endpoints move? → Redirect or deprecation needed
- Are new required fields added to existing requests? → Breaking change

## Output
Produce a complete API specification document that /add-endpoint or /add-feature can implement directly. Include all endpoints, models, status codes, and auth requirements.
