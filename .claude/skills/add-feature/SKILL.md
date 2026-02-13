---
name: add-feature
description: Plan and implement a complete feature end-to-end across all layers
disable-model-invocation: true
---

Implement the following feature: $ARGUMENTS

This is a full-feature workflow that touches every layer. Follow the team's standards at each step.

## Phase 1 — Plan (Sofia Nakamura)
1. Define the user story: who needs this, what it does, why it matters
2. Read existing code to understand where the feature fits in the architecture
3. Identify every file that needs to change or be created
4. List acceptance criteria — what "done" looks like
5. Present the plan before writing any code

## Phase 2 — Schema & Config (Daniel Okoye + Marcus Chen)
1. Add any new Pydantic models to `app/models/schemas.py`
   - Explicit types on every field — no `Any`
   - Validators and constraints where applicable
2. Add any new settings to `app/config.py` with `RELAY_` prefix
3. Document new settings in `.env.example` with description and default

## Phase 3 — Core / Device (Alex Rivera)
*Skip if the feature doesn't touch hardware.*
1. If new device behavior is needed, extend `RelayDevice` Protocol
2. Implement in `HIDRelayDevice` and `MockRelayDevice` — both must stay in sync
3. Use typed exceptions: `DeviceNotFoundError`, `DeviceConnectionError`
4. Document any new HID commands with hex values in comments

## Phase 4 — Service Logic (Alex Rivera + Janet Moore)
1. Add business logic to `app/services/relay_service.py`
   - Thread-safe: wrap device access in `self._lock`
   - Rollback on partial failure for multi-channel operations
   - Audit log via `self._audit()` for any state changes
   - Typed exceptions for error conditions

## Phase 5 — API Endpoints (Daniel Okoye)
1. Add routes to the appropriate router in `app/api/v1/`
   - Thin handlers — delegate to `RelayService`
   - `Depends(get_relay_service)` for auth-protected endpoints
   - `Depends(get_relay_service_public)` for unauthenticated endpoints
   - Full OpenAPI metadata: `response_model`, `summary`, `description`, `responses`
   - Static routes before parameterized routes
   - Exception mapping: `InvalidChannelError` → 404, `DeviceConnectionError` → 503

## Phase 6 — Security (Janet Moore)
1. Verify new endpoints respect auth when `RELAY_API_KEY` is configured
2. Verify error responses use `ErrorResponse` — no stack traces or internals
3. Verify input validation via Pydantic — no raw input trusted
4. If handling secrets: use `hmac.compare_digest()`, never `==`

## Phase 7 — Tests (Priya Sharma)
1. Write tests for each new endpoint: success, validation error, device error
2. Write tests for new service methods: happy path, edge cases, error conditions
3. If state changes: test audit log output via `caplog`
4. If multi-channel: test rollback on partial failure
5. Add to appropriate test file matching `app/` structure

## Phase 8 — Verify (All)
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
Both MUST pass with zero errors.

## Phase 9 — Documentation (Sofia Nakamura)
1. Update `README.md` — API endpoints table, configuration table, examples
2. Update `app/main.py` DESCRIPTION if the feature changes API capabilities
3. Verify OpenAPI docs at `/docs` reflect all new endpoints
