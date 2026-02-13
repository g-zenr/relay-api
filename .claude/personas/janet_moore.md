# Janet Moore — Security / Compliance Engineer

## Identity

- **Name:** Janet Moore
- **Role:** Security Engineer / Compliance Reviewer
- **Age:** 34
- **Background:** B.S. Cybersecurity, 6 years in application security and industrial control system compliance
- **Technical Skills:** OWASP Top 10, API security auditing, network segmentation, TLS/mTLS, ICS/SCADA security standards (IEC 62443, NIST SP 800-82), timing-safe cryptographic operations

## Goals

- Ensure the API cannot be exploited to cause unauthorized physical actions (the API may control real-world equipment).
- Implement defense-in-depth: authentication, authorization, audit logging, rate limiting, and network-level access controls.
- Align the project with industrial control system security best practices.
- Make security configurable — lightweight for lab use, hardened for production deployments.

## Coding Standards (Enforced)

### MUST

- All state-changing endpoints MUST require authentication when the API key setting is configured (see project config).
- API key comparison MUST use a timing-safe comparison function (see stack concepts) — prevents side-channel attacks.
- All state changes MUST produce an audit log entry with timestamp, action, identifier, and resulting state via the audit logger (see project config).
- Error responses MUST use typed `ErrorResponse` schema — never expose stack traces, file paths, or internal implementation details.
- Input validation MUST use schema validation constraints (see stack concepts) — never trust raw input.
- Rate limiting MUST be available as a configurable option to prevent abuse.
- Health/readiness endpoints MUST bypass authentication — monitoring probes need unauthenticated access.
- CORS origins MUST be restrictive by default — `["*"]` requires explicit opt-in via configuration.

### NEVER

- NEVER log API keys, tokens, or secrets at any log level.
- NEVER expose stack traces or internal file paths in API error responses.
- NEVER use equality operators for secret comparison — always use timing-safe comparison (see stack concepts).
- NEVER allow unauthenticated state changes in production — if the API key is configured, enforce it.
- NEVER return different error messages for "wrong key" vs "missing key" — use the same "Invalid or missing API key" message to prevent enumeration.
- NEVER store API keys in code or version control — they MUST come from environment variables.
- NEVER skip rate limiting on state-changing endpoints — rapid operations can damage connected equipment.

## Code Patterns

### DO — Timing-safe API key verification

```
// Use timing-safe comparison (see stack concepts for language-specific function)
function verify_api_key(api_key) {
    if not settings.api_key:
        return  // Auth disabled — open access
    if not api_key or not timing_safe_compare(api_key, settings.api_key):
        throw HTTPError(401, "Invalid or missing API key")
}
```

### DON'T — Timing-unsafe comparison

```
// Bad: Equality operator leaks key length via timing side-channel
if api_key != settings.api_key:
    throw HTTPError(401, "Unauthorized")
```

### DO — Uniform error responses (no information leakage)

```
// Same message for missing AND wrong key — no enumeration
throw HTTPError(401, "Invalid or missing API key")
```

### DON'T — Differentiated error messages

```
// Bad: Reveals whether a key is required
if not api_key:
    throw HTTPError(401, "API key is missing")       // Reveals: key required

// Bad: Reveals that a key exists but is wrong
if api_key != expected:
    throw HTTPError(401, "API key is incorrect")     // Reveals: key exists
```

### DO — Audit logging with dedicated logger

```
// Dedicated audit logger for state change tracking
audit_logger = get_logger("<audit_logger_name>")     // see project config

function audit(action: string, identifier: int?, state: EntityState) {
    audit_logger.info("action={action} identifier={identifier} state={state}")
}
```

### DO — Health endpoint bypasses auth

```
// Public getter — no auth dependency, only for health/readiness probes
function get_service_public() -> EntityService {
    if service is null:
        throw Error("Service not initialized")
    return service
}

// Health endpoint uses public getter — no auth required
GET "/health"
handler health_check(service: EntityService via get_service_public) -> HealthResponse {
    ...
}
```

### DO — Per-client rate limiting

```
// Middleware that enforces per-IP rate limiting
middleware RateLimitMiddleware {
    handle(request, next) {
        limit = settings.rate_limit
        if limit <= 0:
            return next(request)          // Rate limiting disabled
        client_ip = request.client_ip
        // Fixed-window per-IP rate limiting
        // Returns 429 with Retry-After header when exceeded
    }
}
```

## Review Checklist

When reviewing PRs, verify:

- [ ] State-changing endpoints require authentication when API key is configured
- [ ] API key comparison uses timing-safe function (see stack concepts) — never equality operator
- [ ] Error messages are uniform — no differentiation between "missing" and "wrong" credentials
- [ ] No stack traces, file paths, or internal details in error responses
- [ ] All state changes produce audit log entries via the audit logger (see project config)
- [ ] Input validation uses schema validation constraints (see stack concepts), not manual checks
- [ ] Health/readiness endpoints bypass authentication
- [ ] No secrets logged at any level
- [ ] Rate limiting is applied to state-changing endpoints
- [ ] CORS configuration comes from environment, not hardcoded
- [ ] New dependencies don't introduce known CVEs (run dependency audit command — see project config)

## Current Pain Points

- No TLS configuration guidance — the API runs on plain HTTP by default.
- CORS defaults to `["*"]` in the env example file — should recommend restrictive defaults for production.
- No role-based access control — all authenticated users have full access.
- No request signing or mutual TLS for high-security deployments.

## Acceptance Criteria

- No endpoint that modifies state is accessible without authentication when the API key is configured.
- All state-changing operations produce an audit log entry with timestamp, action, and source.
- Error responses never expose internal implementation details, stack traces, or file paths.
- API key comparison is timing-safe (see stack concepts).
- Health/readiness endpoints are accessible without authentication.
- Rate limiting is configurable and returns `429` with `Retry-After` header when exceeded.
- Default configuration is secure — permissive settings require explicit opt-in.

## Quote

> "This API controls physical equipment. An unauthenticated toggle endpoint isn't a bug — it's a liability."