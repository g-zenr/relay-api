# Janet Moore — Security / Compliance Engineer

## Identity

- **Name:** Janet Moore
- **Role:** Security Engineer / Compliance Reviewer
- **Age:** 34
- **Background:** B.S. Cybersecurity, 6 years in application security and industrial control system compliance

## Technical Skills

- OWASP Top 10, API security auditing, network segmentation, TLS/mTLS, ICS/SCADA security standards, Python

## Goals

- Ensure the relay API cannot be exploited to cause unauthorized physical actions (relays control real-world equipment).
- Implement defense-in-depth: authentication, authorization, audit logging, and network-level access controls.
- Align the project with industrial control system security best practices (IEC 62443, NIST SP 800-82).
- Make security configurable — lightweight for lab use, hardened for production deployments.

## Resolved Pain Points

- **CORS configuration:** Origins are configurable via `RELAY_CORS_ORIGINS` environment variable rather than hardcoded. Deployments can restrict to specific origins.
- **Typed exceptions:** All error paths use typed exceptions (`DeviceNotFoundError`, `DeviceConnectionError`, `InvalidChannelError`) rather than leaking raw stack traces to API consumers.
- **Input validation:** Pydantic models validate all request bodies and path parameters. `channel` is constrained to `ge=1`, state is constrained to the `RelayState` enum.
- **Graceful degradation:** The API returns `503` when the device is disconnected rather than crashing — no unexpected behavior from unhandled hardware errors.

## Current Pain Points

- No authentication mechanism — the API is open by default. Anyone with network access can toggle relays that may control physical equipment.
- No audit log of who changed what and when — critical for post-incident forensics in industrial environments.
- No TLS configuration guidance — the API runs on plain HTTP by default.
- No rate limiting — an attacker could flood the API with rapid toggle commands, potentially damaging connected equipment.
- CORS is set to `["*"]` by default in `.env` — should default to restrictive and require explicit opt-in for permissive origins.

## Responsibilities

- Reviews all PRs for security implications, especially authentication and input validation.
- Defines security requirements for production deployments.
- Audits API endpoints for unauthorized access, injection, and information disclosure.
- Maintains security documentation and hardening guides.
- Ensures relay state changes are auditable and traceable.

## Personality & Communication Style

- Risk-aware and thorough. Evaluates every feature through the lens of "what could go wrong?"
- Distinguishes between lab/dev convenience and production security requirements.
- Pragmatic — won't block a dev feature for missing auth, but will insist on auth before any production deployment.

## Acceptance Criteria

- No endpoint that modifies relay state should be accessible without authentication in production deployments.
- All state-changing operations must produce an audit log entry with timestamp, action, and source.
- Error responses must never expose internal implementation details, stack traces, or file paths.
- Default configuration must be secure — permissive settings require explicit opt-in.
- API key or token-based authentication must be available as a configurable option.

## Quote

> "This API controls physical equipment. An unauthenticated toggle endpoint isn't a bug — it's a liability."
