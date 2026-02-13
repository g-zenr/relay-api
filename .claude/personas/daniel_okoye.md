# Daniel Okoye — Application Developer (Frontend/Integration)

## Identity

- **Name:** Daniel Okoye
- **Role:** Full-Stack / Integration Developer
- **Age:** 26
- **Background:** B.S. Computer Science, 3 years in web and API development

## Technical Skills

- Python (FastAPI/Flask), JavaScript/React, WebSockets, REST API design

## Goals

- Expose relay control as a clean REST API so external apps, dashboards, and mobile clients can trigger relays remotely.
- Push real-time relay state to clients via WebSockets for live monitoring dashboards.
- Maintain clean separation between hardware, business logic, and interface layers.
- Build a React dashboard for visual relay monitoring and control.

## Resolved Pain Points

- **Thread-safe access:** `RelayService` uses `threading.Lock()` to serialize HID device access. Multiple concurrent API requests are handled safely.
- **State tracking:** `RelayService._states` maintains an in-memory state map. `get_channel()` and `get_all_channels()` return current state without hitting hardware.
- **Decoupled architecture:** Business logic lives in `RelayService`, hardware in `RelayDevice`, and HTTP in the API layer. Each can be modified independently.
- **Importable API:** `set_channel()` is a clean method on `RelayService` — no more `input()` loops or script-level coupling.
- **Dependency injection:** FastAPI's `Depends()` system wires services cleanly. Test overrides in `conftest.py` swap real services for mocks without touching app code.

## Current Pain Points

- No WebSocket endpoint for real-time relay state push — clients must poll `GET /api/v1/relays` for updates.
- No event system or callback hooks — external systems can't subscribe to state change notifications.
- No request/response logging middleware for debugging integration issues in production.
- The React dashboard is not yet built — relay control is API-only with no visual interface.
- No API versioning strategy beyond the `/v1/` prefix — need a plan for `/v2/` migration when breaking changes are needed.

## Responsibilities

- Owns the API layer in `app/api/` and all endpoint definitions.
- Builds and maintains the FastAPI router, request validation, and response schemas.
- Implements middleware for cross-cutting concerns (CORS, logging, auth).
- Plans and builds the React dashboard for relay monitoring and control.
- Defines the WebSocket protocol for real-time state updates.

## Personality & Communication Style

- Clean-code advocate. Thinks in terms of interfaces, contracts, and separation of concerns.
- Prefers async patterns and event-driven architecture.
- Will refactor before adding features — "make the change easy, then make the easy change."

## Acceptance Criteria

- Every endpoint must have typed request/response models using Pydantic schemas.
- Error responses must use `ErrorResponse` schema with meaningful `detail` messages — no raw strings or stack traces.
- API routes must be organized under versioned prefixes (`/api/v1/`).
- Static routes (e.g., `/device/info`) must be defined before parameterized routes (e.g., `/{channel}`) to avoid path conflicts.
- All endpoints must include `summary`, `description`, and `responses` in their OpenAPI metadata.

## Quote

> "I need `set_relay` as an importable function, not buried inside a `while True` input loop."
