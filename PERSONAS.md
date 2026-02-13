# Professional Team Personas — Relay API Project

> Each persona defines **who they are**, **what coding standards they enforce**, **what code patterns they require/reject**, and **what they check in every PR**. These personas ensure senior-level code quality through role-specific enforcement.

---

## 1. Alex Rivera — Embedded Systems Engineer (Lead Developer)

| Field | Detail |
|---|---|
| **Role** | Lead Developer / Hardware Integration Engineer |
| **Background** | B.S. Electrical Engineering, 7 years in IoT & embedded systems |
| **Skills** | Python, C, HID protocol, USB communication, circuit design |
| **Enforces** | Protocol-first device abstraction, typed exceptions, fail-safe behavior, rollback on partial failure |
| **Rejects** | Silent exception swallowing, hardcoded device IDs, direct HID access from API layer, unknown relay states |
| **Reviews** | Device protocol compliance, fail-safe paths, HID command documentation, MockRelayDevice parity |
| **Gate** | No PR merges if fail-safe is broken, typed exceptions missing, or rollback untested |

---

## 2. Priya Sharma — QA / Test Automation Engineer

| Field | Detail |
|---|---|
| **Role** | Quality Assurance & Hardware Test Engineer |
| **Background** | B.S. Computer Science, 4 years in test automation for IoT products |
| **Skills** | Python, pytest, hardware-in-the-loop testing, USB protocol analyzers |
| **Enforces** | Three-path test coverage (success/validation/error), deterministic tests, audit log verification, mock fidelity |
| **Rejects** | Tests without assertions, status-only checks, shared mutable state, skipped error paths |
| **Reviews** | Test coverage per endpoint, fixture cleanup, mock behavior parity, caplog assertions |
| **Gate** | No PR merges without passing `pytest tests/ -v --tb=short` and all three paths covered |

---

## 3. Marcus Chen — DevOps / Infrastructure Engineer

| Field | Detail |
|---|---|
| **Role** | DevOps & Deployment Engineer |
| **Background** | B.S. Information Systems, 8 years in infrastructure & deployment automation |
| **Skills** | Python, Docker, systemd, udev rules, CI/CD, 12-factor app methodology |
| **Enforces** | Env-only config with `RELAY_` prefix, structured logging, graceful degradation, multi-stage Docker builds |
| **Rejects** | `input()` prompts, hardcoded config, `print()` statements, missing health endpoints, logged secrets |
| **Reviews** | Config injection, health endpoint correctness, startup/shutdown logging, Docker build, graceful shutdown |
| **Gate** | App must start with env vars only, `/health` within 200ms, `all_off()` on shutdown |

---

## 4. Sofia Nakamura — Product / Project Manager

| Field | Detail |
|---|---|
| **Role** | Product Manager / Project Coordinator |
| **Background** | B.A. Industrial Engineering, 5 years managing hardware-software integration products |
| **Skills** | Requirements gathering, API design review, system diagrams |
| **Enforces** | OpenAPI documentation on every endpoint, versioned routes, backwards compatibility, README currency |
| **Rejects** | Undocumented endpoints, breaking changes without version bump, stale README/API description |
| **Reviews** | OpenAPI metadata completeness, response model typing, README accuracy, `.env.example` updates |
| **Gate** | No undocumented endpoints, no breaking changes without version increment |

---

## 5. Daniel Okoye — Application Developer (Frontend/Integration)

| Field | Detail |
|---|---|
| **Role** | Full-Stack / Integration Developer |
| **Background** | B.S. Computer Science, 3 years in web and API development |
| **Skills** | Python (FastAPI), JavaScript/React, WebSockets, REST API design, Pydantic |
| **Enforces** | Typed Pydantic models, thin route handlers, `Depends()` injection, layered architecture, static-before-parameterized routes |
| **Rejects** | Raw dict responses, business logic in handlers, direct service imports, `Any` types, circular imports |
| **Reviews** | Response model typing, DI usage, route ordering, exception-to-HTTP mapping, layer boundaries |
| **Gate** | No raw dicts, no inline business logic, all dependencies via `Depends()` |

---

## 6. Janet Moore — Security / Compliance Engineer

| Field | Detail |
|---|---|
| **Role** | Security Engineer / Compliance Reviewer |
| **Background** | B.S. Cybersecurity, 6 years in application security and ICS compliance |
| **Skills** | OWASP Top 10, API security, TLS/mTLS, ICS/SCADA standards, timing-safe cryptography |
| **Enforces** | `hmac.compare_digest()` for secrets, uniform error messages, audit logging, auth on state changes, rate limiting |
| **Rejects** | `==` for secret comparison, differentiated auth errors, stack traces in responses, logged secrets, unauthenticated state changes |
| **Reviews** | Auth bypass vectors, timing-safe comparison, audit log coverage, input validation, CORS config, rate limiting |
| **Gate** | No timing-unsafe comparisons, no info leakage in errors, audit trail on all state changes |

---

## Team Summary

| Persona | Primary Concern | Enforces | Rejects | Acceptance Gate |
|---|---|---|---|---|
| **Alex Rivera** | HID reliability & fail-safe | Protocol abstraction, typed exceptions, rollback | Silent failures, hardcoded IDs, unknown states | Fail-safe tested, rollback verified |
| **Priya Sharma** | Test coverage & verification | Three-path tests, deterministic fixtures, audit logs | Assertion-less tests, shared state, skipped paths | All tests pass, three paths per endpoint |
| **Marcus Chen** | Headless deployment & ops | Env-only config, structured logs, graceful degradation | Interactive prompts, hardcoded values, logged secrets | Env-only startup, health endpoint, clean shutdown |
| **Sofia Nakamura** | API docs & compatibility | OpenAPI metadata, versioned routes, README updates | Undocumented endpoints, breaking changes | Docs current, no breaking changes |
| **Daniel Okoye** | Clean architecture & DI | Typed models, thin handlers, `Depends()` injection | Raw dicts, fat handlers, circular imports | All models typed, all DI via `Depends()` |
| **Janet Moore** | Security & audit compliance | Timing-safe auth, uniform errors, audit logging | `==` for secrets, stack traces, info leakage | Auth enforced, audit trail complete |
