# Professional Team Personas — Relay API Project

## 1. Alex Rivera — Embedded Systems Engineer (Lead Developer)

| Field | Detail |
|---|---|
| **Role** | Lead Developer / Hardware Integration Engineer |
| **Age** | 32 |
| **Background** | B.S. Electrical Engineering, 7 years in IoT & embedded systems |
| **Technical Skills** | Python, C, HID protocol, USB communication, circuit design |
| **Goals** | Build a reliable, extensible relay control layer with clean abstractions over raw HID commands. Ensure fail-safe behavior and extend device support beyond DCT Tech modules. |
| **Resolved** | `RelayDevice` protocol abstracts hardware. `all_off()` runs on startup/shutdown with per-channel exception handling. `set_channel()` replaces the old `set_relay()` with a clean, testable interface. |
| **Current Pain Points** | Cross-platform HID driver inconsistencies. No hardware read-back to verify actual relay contact position. Sparse vendor documentation. No multi-device registry for multiple USB boards. |
| **Acceptance Criteria** | Every device must satisfy `RelayDevice` protocol. `all_off()` on startup and shutdown. Device errors use typed exceptions. No PR merges if fail-safe is broken. |
| **Quote** | *"If the relay state is unknown after a crash, we have a problem. Fail-safe means OFF."* |

---

## 2. Priya Sharma — QA / Test Automation Engineer

| Field | Detail |
|---|---|
| **Role** | Quality Assurance & Hardware Test Engineer |
| **Age** | 28 |
| **Background** | B.S. Computer Science, 4 years in test automation for IoT products |
| **Technical Skills** | Python, pytest, hardware-in-the-loop testing, USB protocol analyzers |
| **Goals** | Ensure reliable relay switching under all conditions. Maintain automated CI regression tests. Establish an audit trail for post-incident analysis. Achieve full test coverage. |
| **Resolved** | `MockRelayDevice` enables CI without hardware. `RelayService._states` tracks channel states. Structured logging with timestamps. `conftest.py` provides connected and disconnected fixtures. |
| **Current Pain Points** | No state change history/audit log. No integration tests for mid-operation USB disconnection. Error path coverage could be more exhaustive. No stress tests for thread-lock contention. |
| **Acceptance Criteria** | Every endpoint ships with success, validation, and error-path tests. Mock mirrors real device behavior. No PR merges without passing tests. State changes logged with channel, state, and timestamp. |
| **Quote** | *"I need to know if relay 2 actually toggled, not just that the code didn't crash."* |

---

## 3. Marcus Chen — DevOps / Infrastructure Engineer

| Field | Detail |
|---|---|
| **Role** | DevOps & Deployment Engineer |
| **Age** | 35 |
| **Background** | B.S. Information Systems, 8 years in infrastructure & deployment automation |
| **Technical Skills** | Python, Docker, systemd, udev rules, Windows service management, CI/CD |
| **Goals** | Package for headless deployment on industrial PCs and Raspberry Pis. Automate USB permissions. Build production-grade observability. Containerize the application. |
| **Resolved** | FastAPI replaced interactive CLI. `requirements.txt` manages dependencies. Pydantic `BaseSettings` reads `.env` files. `/health` endpoint supports uptime probes. `RELAY_MOCK=true` for hardware-free CI. |
| **Current Pain Points** | No Dockerfile or docker-compose. No systemd unit file or Windows service wrapper. No udev rule template. Stdout-only logging with no rotation. No rate limiting. |
| **Acceptance Criteria** | App starts with only env vars. `/health` responds within 200ms. Startup/shutdown events logged. Config injectable via environment. Graceful shutdown completes `all_off()`. |
| **Quote** | *"I can't SSH in and type menu options. Give me an API endpoint or a config file."* |

---

## 4. Sofia Nakamura — Product / Project Manager

| Field | Detail |
|---|---|
| **Role** | Product Manager / Project Coordinator |
| **Age** | 30 |
| **Background** | B.A. Industrial Engineering, 5 years managing hardware-software integration products |
| **Technical Skills** | Requirements gathering, Jira, basic Python reading comprehension, system diagrams |
| **Goals** | Expand into a full automation platform with scheduling, multi-device support, and a web dashboard. Align engineering with customer use cases. Maintain clear API docs for integrators. |
| **Resolved** | Layered architecture enables independent feature scoping. `RELAY_CHANNELS` supports N-channel boards. FastAPI auto-generates OpenAPI docs at `/docs` and `/redoc`. REST API enables external integration. |
| **Current Pain Points** | No scheduling capability (most requested feature). No web dashboard for non-technical users. No multi-device support. No usage analytics. No quick-start guide for onboarding. |
| **Acceptance Criteria** | Every feature has a user story with business justification. API changes reflected in OpenAPI docs. New features demonstrable within sprint. No breaking changes without versioned migration. |
| **Quote** | *"Our customers want to schedule relay 1 ON at 8 AM and OFF at 6 PM. Can we do that by next sprint?"* |

---

## 5. Daniel Okoye — Application Developer (Frontend/Integration)

| Field | Detail |
|---|---|
| **Role** | Full-Stack / Integration Developer |
| **Age** | 26 |
| **Background** | B.S. Computer Science, 3 years in web and API development |
| **Technical Skills** | Python (FastAPI/Flask), JavaScript/React, WebSockets, REST API design |
| **Goals** | Expose relay control via REST API. Push real-time state via WebSockets. Maintain clean layer separation. Build a React dashboard. |
| **Resolved** | `threading.Lock()` serializes HID access. `_states` dict tracks state without hardware reads. Layered architecture decouples concerns. `set_channel()` is importable. FastAPI `Depends()` enables clean DI. |
| **Current Pain Points** | No WebSocket endpoint (clients must poll). No event system or callback hooks. No request/response logging middleware. No React dashboard yet. No `/v2/` migration strategy. |
| **Acceptance Criteria** | All endpoints use typed Pydantic models. Errors use `ErrorResponse` schema. Routes under versioned prefixes. Static routes before parameterized routes. Full OpenAPI metadata on all endpoints. |
| **Quote** | *"I need `set_relay` as an importable function, not buried inside a `while True` input loop."* |

---

## 6. Janet Moore — Security / Compliance Engineer

| Field | Detail |
|---|---|
| **Role** | Security Engineer / Compliance Reviewer |
| **Age** | 34 |
| **Background** | B.S. Cybersecurity, 6 years in application security and industrial control system compliance |
| **Technical Skills** | OWASP Top 10, API security auditing, network segmentation, TLS/mTLS, ICS/SCADA standards, Python |
| **Goals** | Prevent unauthorized physical actions via the API. Implement defense-in-depth: auth, audit logging, network controls. Align with ICS security best practices. Make security configurable per environment. |
| **Resolved** | CORS origins configurable via env var. Typed exceptions prevent stack trace leaks. Pydantic validates all inputs. Graceful `503` on device disconnect instead of crashes. |
| **Current Pain Points** | No authentication — API is open by default. No audit log for forensics. No TLS configuration guidance. No rate limiting. CORS defaults to `["*"]`. |
| **Acceptance Criteria** | State-changing endpoints require auth in production. All state changes produce audit log entries. Errors never expose internals. Defaults must be secure. API key auth available as config option. |
| **Quote** | *"This API controls physical equipment. An unauthenticated toggle endpoint isn't a bug — it's a liability."* |

---

## Team Summary

| Persona | Role | Primary Concern | Key Acceptance Gate |
|---|---|---|---|
| **Alex Rivera** | Lead / Hardware Engineer | Reliable HID communication & fail-safe behavior | Fail-safe tested, typed device exceptions |
| **Priya Sharma** | QA / Test Engineer | Verifiable relay state & automated testing | Tests pass, state changes logged |
| **Marcus Chen** | DevOps Engineer | Headless deployment & observability | Env-only config, health endpoint, graceful shutdown |
| **Sofia Nakamura** | Product Manager | Feature roadmap & customer use cases | User story exists, API docs updated |
| **Daniel Okoye** | App Developer | API layer & modular architecture | Typed models, versioned routes, OpenAPI metadata |
| **Janet Moore** | Security Engineer | Authentication, audit logging & access control | Auth enabled, audit trail, no info leaks |
