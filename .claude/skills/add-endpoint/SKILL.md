---
name: add-endpoint
description: Add a new API endpoint following all project standards
---

Add a new API endpoint: $ARGUMENTS

Follow this workflow:

1. **Plan**: Identify which router file the endpoint belongs in (`app/api/v1/relays.py` or `app/api/v1/system.py`)

2. **Schema**: Add Pydantic request/response models to `app/models/schemas.py` if needed
   - All fields explicitly typed — no `Any`
   - Use validators and constraints (`ge=1`, enums)

3. **Service**: Add business logic to `app/services/relay_service.py` if needed
   - Thread-safe with `self._lock`
   - Audit log via `self._audit()` for state changes
   - Typed exceptions for error cases

4. **Route**: Add the endpoint to the router
   - Thin handler — delegate to service
   - Use `Depends(get_relay_service)` for auth-protected or `Depends(get_relay_service_public)` for public
   - Include `response_model`, `summary`, `description`, `responses` in decorator
   - Static routes before parameterized routes
   - Map exceptions: `InvalidChannelError` → 404, `DeviceConnectionError` → 503

5. **Tests**: Add tests in the appropriate `tests/test_api_*.py` file
   - Success path test
   - Validation error test (422)
   - Device error test (503 with `client_disconnected`)

6. **Verify**: Run `python -m pytest tests/ -v --tb=short` and `python -m mypy app/`

7. **Docs**: Update `README.md` API endpoints table if a new endpoint was added
