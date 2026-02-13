---
name: security-audit
description: Deep security audit of the codebase (Janet Moore's workflow)
---

Perform a security audit on the Relay API codebase following Janet Moore's standards.

## Audit Checklist

### 1. Authentication & Authorization
- Read `app/api/dependencies.py` — verify `hmac.compare_digest()` is used, not `==`
- Verify health/readiness endpoints bypass auth via `get_relay_service_public()`
- Verify ALL state-changing endpoints require auth when `RELAY_API_KEY` is set
- Check error messages are uniform: "Invalid or missing API key" — no enumeration clues

### 2. Input Validation
- Read `app/models/schemas.py` — verify all fields have type constraints
- Check channel parameters use `ge=1` validation
- Check state parameters use `RelayState` enum — no raw strings
- Verify Pydantic models are used on every endpoint (no raw dict parsing)

### 3. Information Leakage
- Search for `traceback`, `stack`, `__file__`, `__name__` in API responses
- Verify all error responses use `ErrorResponse` schema
- Check no internal paths, class names, or implementation details in 4xx/5xx responses
- Verify logging never outputs API keys or secrets

### 4. Audit Trail
- Verify ALL state-changing operations produce `relay.audit` log entries
- Check audit entries include: action, channel, state, timestamp
- Verify `set_channel`, `set_all_channels`, and `all_off` all audit

### 5. Rate Limiting
- Read `app/middleware.py` — verify per-client IP rate limiting
- Check `429` response includes `Retry-After` header
- Verify rate limit is configurable via `RELAY_RATE_LIMIT`

### 6. CORS & Headers
- Check CORS origins come from config, not hardcoded
- Verify default is configurable via `RELAY_CORS_ORIGINS`

### 7. Dependencies
- Run `pip audit` if available to check for known CVEs
- Review `requirements.txt` for outdated or vulnerable packages

## Output Format
Group findings by severity: **Critical**, **High**, **Medium**, **Low**, **Info**
Include specific file:line references and remediation steps for each finding.
