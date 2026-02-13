---
name: harden
description: Apply production security hardening to the codebase (Janet Moore's workflow)
disable-model-invocation: true
---

Harden the Relay API for production deployment: $ARGUMENTS

Unlike `/security-audit` (which finds issues), `/harden` actively fixes them.

## 1. Authentication Hardening
- [ ] Verify `RELAY_API_KEY` is required in production (not empty)
- [ ] Verify `hmac.compare_digest()` for all secret comparisons
- [ ] Verify uniform error messages (no auth enumeration)
- [ ] Add API key length validation (minimum 16 characters recommended)
- [ ] Verify health endpoint bypasses auth correctly

## 2. Input Validation Hardening
- [ ] All path parameters have constraints (`ge=1`, `le=max_channels`)
- [ ] All request bodies use Pydantic models with strict validation
- [ ] Verify no raw `dict` or `Any` types in request handling
- [ ] Add request body size limits if not present

## 3. Error Response Hardening
- [ ] All error responses use `ErrorResponse` schema
- [ ] No stack traces in any error response (test with `DEBUG=false`)
- [ ] No internal file paths or class names in responses
- [ ] Verify 500 errors return generic message, not exception details

## 4. CORS Hardening
- [ ] Change default CORS from `["*"]` to restrictive origins
- [ ] Document that `["*"]` requires explicit opt-in
- [ ] Add CORS configuration guidance in `.env.example`

## 5. Rate Limiting Hardening
- [ ] Verify rate limiting is enabled in production config
- [ ] Recommend rate limit value in `.env.example` (e.g., 60 req/min)
- [ ] Verify `429` response includes `Retry-After` header
- [ ] Verify rate limiter is per-client IP, not global

## 6. Logging Hardening
- [ ] Verify no secrets logged at any level (search for `api_key`, `key`, `secret`, `token`)
- [ ] Verify audit log captures all state changes
- [ ] Verify log level defaults to INFO in production (not DEBUG)

## 7. Docker Hardening
- [ ] Non-root user in Dockerfile
- [ ] No secrets baked into image (no `.env` in image)
- [ ] HEALTHCHECK instruction present
- [ ] Minimal base image (slim variant)
- [ ] Read-only filesystem where possible

## 8. Dependency Hardening
- [ ] Run `pip audit` — zero known vulnerabilities
- [ ] Pin exact versions in `requirements.txt` for reproducibility
- [ ] Remove unused dependencies

## Output
For each section, report:
- **HARDENED**: Already secure, no changes needed
- **FIXED**: Issue found and remediated (describe what changed)
- **MANUAL**: Requires manual action (describe what to do)

Apply all fixes that can be automated. List manual steps for the rest.