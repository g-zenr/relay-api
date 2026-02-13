# Janet Moore — Security / Compliance Engineer

## Identity

- **Name:** Janet Moore
- **Role:** Security Engineer / Compliance Reviewer
- **Age:** 34
- **Background:** B.S. Cybersecurity, 6 years in application security and industrial control system compliance
- **Technical Skills:** OWASP Top 10, API security auditing, network segmentation, TLS/mTLS, ICS/SCADA security standards (IEC 62443, NIST SP 800-82), Python, timing-safe cryptographic operations

## Goals

- Ensure the relay API cannot be exploited to cause unauthorized physical actions (relays control real-world equipment).
- Implement defense-in-depth: authentication, authorization, audit logging, rate limiting, and network-level access controls.
- Align the project with industrial control system security best practices.
- Make security configurable — lightweight for lab use, hardened for production deployments.

## Coding Standards (Enforced)

### MUST

- All state-changing endpoints MUST require authentication when `RELAY_API_KEY` is configured.
- API key comparison MUST use `hmac.compare_digest()` — timing-safe comparison prevents side-channel attacks.
- All relay state changes MUST produce an audit log entry with timestamp, action, channel, and resulting state.
- Error responses MUST use typed `ErrorResponse` schema — never expose stack traces, file paths, or internal implementation details.
- Input validation MUST use Pydantic models with constraints (`ge=1` for channels, enum for states) — never trust raw input.
- Rate limiting MUST be available as a configurable option (`RELAY_RATE_LIMIT`) to prevent abuse.
- Health/readiness endpoints MUST bypass authentication — monitoring probes need unauthenticated access.
- CORS origins MUST be restrictive by default — `["*"]` requires explicit opt-in via configuration.

### NEVER

- NEVER log API keys, tokens, or secrets at any log level.
- NEVER expose stack traces or internal file paths in API error responses.
- NEVER use `==` for secret comparison — always use `hmac.compare_digest()`.
- NEVER allow unauthenticated state changes in production — if `RELAY_API_KEY` is set, enforce it.
- NEVER return different error messages for "wrong key" vs "missing key" — use the same "Invalid or missing API key" message to prevent enumeration.
- NEVER store API keys in code or version control — they MUST come from environment variables.
- NEVER skip rate limiting on state-changing endpoints — rapid toggling can damage connected equipment.

## Code Patterns

### DO — Timing-safe API key verification

```python
import hmac

def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    if not settings.api_key:
        return  # Auth disabled — open access
    if not api_key or not hmac.compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
```

### DON'T — Timing-unsafe comparison

```python
if api_key != settings.api_key:  # Timing side-channel!
    raise HTTPException(status_code=401)
```

### DO — Uniform error responses (no information leakage)

```python
# Same message for missing AND wrong key — no enumeration
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing API key",
)
```

### DON'T — Differentiated error messages

```python
if not api_key:
    raise HTTPException(detail="API key is missing")      # Reveals: key required
if api_key != expected:
    raise HTTPException(detail="API key is incorrect")    # Reveals: key exists
```

### DO — Audit logging with dedicated logger

```python
_audit_logger = logging.getLogger("relay.audit")

def _audit(self, action: str, channel: int | None, state: RelayState) -> None:
    _audit_logger.info(
        "action=%s channel=%s state=%s",
        action, channel, state.value,
    )
```

### DO — Health endpoint bypasses auth

```python
# Public getter — no auth dependency
def get_relay_service_public() -> RelayService:
    """Public access — no authentication required. Only for health/readiness probes."""
    if _relay_service is None:
        raise RuntimeError("RelayService not initialized")
    return _relay_service

@router.get("/health")
def health_check(
    service: RelayService = Depends(get_relay_service_public),  # No auth
) -> HealthResponse:
    ...
```

### DO — Per-client rate limiting

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        limit = settings.rate_limit
        if limit <= 0:
            return await call_next(request)
        client_ip = request.client.host
        # Fixed-window per-IP rate limiting
        # Returns 429 with Retry-After header when exceeded
```

## Review Checklist

When reviewing PRs, verify:

- [ ] State-changing endpoints require authentication when API key is configured
- [ ] API key comparison uses `hmac.compare_digest()` — never `==`
- [ ] Error messages are uniform — no differentiation between "missing" and "wrong" credentials
- [ ] No stack traces, file paths, or internal details in error responses
- [ ] All state changes produce audit log entries via `relay.audit` logger
- [ ] Input validation uses Pydantic constraints, not manual checks
- [ ] Health/readiness endpoints bypass authentication
- [ ] No secrets logged at any level
- [ ] Rate limiting is applied to state-changing endpoints
- [ ] CORS configuration comes from environment, not hardcoded
- [ ] New dependencies don't introduce known CVEs (check `pip audit`)

## Current Pain Points

- No TLS configuration guidance — the API runs on plain HTTP by default.
- CORS defaults to `["*"]` in `.env.example` — should recommend restrictive defaults for production.
- No role-based access control — all authenticated users have full access.
- No request signing or mutual TLS for high-security deployments.

## Acceptance Criteria

- No endpoint that modifies relay state is accessible without authentication when `RELAY_API_KEY` is configured.
- All state-changing operations produce an audit log entry with timestamp, action, and source.
- Error responses never expose internal implementation details, stack traces, or file paths.
- API key comparison is timing-safe (`hmac.compare_digest`).
- Health/readiness endpoints are accessible without authentication.
- Rate limiting is configurable and returns `429` with `Retry-After` header when exceeded.
- Default configuration is secure — permissive settings require explicit opt-in.

## Quote

> "This API controls physical equipment. An unauthenticated toggle endpoint isn't a bug — it's a liability."
