# Project Configuration

> **This is the only file you need to edit when porting skills/personas to a new project.**
> Skills and personas reference generic terms that resolve against this config.

## Project

- **Name:** Relay API
- **Description:** REST API for controlling DCT Tech USB relay modules via HID
- **Stack:** Python 3.12, FastAPI, Pydantic v2, pytest, mypy
- **Domain:** Hardware relay control (USB/HID)

## Commands

| Action | Command |
|--------|---------|
| Run tests | `python -m pytest tests/ -v --tb=short` |
| Type check | `python -m mypy app/` |
| Run app (dev) | `RELAY_MOCK=true python run.py` |
| Run app (prod) | `python run.py` |
| Dependency audit | `pip audit` |
| List outdated | `pip list --outdated --format=columns` |
| Syntax check | `python -c "import ast; ast.parse(open('FILE').read())"` |
| Docker build | `docker build -t relay-api:test .` |

## Architecture

| Concept | Path |
|---------|------|
| Source root | `app/` |
| Test root | `tests/` |
| Config file | `app/config.py` |
| Config class | `Settings` (Pydantic `BaseSettings`) |
| Config env prefix | `RELAY_` |
| Env file | `.env` |
| Env example | `.env.example` |
| Entry point | `run.py` |
| App factory | `app/main.py` |
| Dockerfile | `Dockerfile` |
| CI workflows | `.github/workflows/` |
| Requirements | `requirements.txt` |
| Changelog | `CHANGELOG.md` |

### Layers (dependency flows top → bottom only)

| Layer | Path | Purpose |
|-------|------|---------|
| API | `app/api/v1/` | Route handlers — thin, delegates to service |
| Dependencies | `app/api/dependencies.py` | Auth chain, service injection via `Depends()` |
| Service | `app/services/relay_service.py` | Business logic, thread safety, audit logging |
| Core | `app/core/device.py` | Device protocol + implementations |
| Exceptions | `app/core/exceptions.py` | Typed exception hierarchy |
| Models | `app/models/schemas.py` | Pydantic request/response models |
| Middleware | `app/middleware.py` | Rate limiting |

### Routers

| Router | File | Purpose |
|--------|------|---------|
| relays | `app/api/v1/relays.py` | Primary entity CRUD |
| system | `app/api/v1/system.py` | Health, readiness, info |

## Key Abstractions

| Generic Concept | This Project | File |
|----------------|-------------|------|
| Primary protocol/interface | `RelayDevice` (`typing.Protocol`) | `app/core/device.py` |
| Real implementation | `HIDRelayDevice` | `app/core/device.py` |
| Mock implementation | `MockRelayDevice` | `app/core/device.py` |
| Main service class | `RelayService` | `app/services/relay_service.py` |
| State enum | `RelayState` (`on` / `off`) | `app/models/schemas.py` |
| Error response model | `ErrorResponse` | `app/models/schemas.py` |
| Auth-protected DI | `get_relay_service` | `app/api/dependencies.py` |
| Public DI (no auth) | `get_relay_service_public` | `app/api/dependencies.py` |
| Audit logger | `relay.audit` | Used in service layer |
| Fail-safe operation | `all_off()` | Runs on startup + shutdown |

### Exception → HTTP Mapping

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `InvalidChannelError` | 404 | Entity not found |
| `DeviceConnectionError` | 503 | Hardware/connection failure |
| `DeviceNotFoundError` | 503 | Device absent on startup |

### Protocol Methods

```python
class RelayDevice(Protocol):
    def open(self) -> None: ...
    def close(self) -> None: ...
    def set_channel(self, channel: int, on: bool) -> None: ...
    def get_info(self) -> dict[str, str]: ...
    @property
    def is_open(self) -> bool: ...
```

## Test File Mapping

| Source | Test File |
|--------|-----------|
| `app/api/v1/relays.py` | `tests/test_api_relays.py` |
| `app/api/v1/system.py` | `tests/test_api_system.py` |
| `app/services/relay_service.py` | `tests/test_services.py` |
| `app/core/device.py` | `tests/test_core_device.py` |
| Auth chain | `tests/test_api_auth.py` |
| Integration | `tests/test_integration.py` |
| Performance | `tests/test_performance.py` |
| Conftest | `tests/conftest.py` |

## API Routes

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/health` | Health check | Public |
| GET | `/api/v1/relays` | List all entity states | Protected |
| GET | `/api/v1/relays/{channel}` | Get single entity state | Protected |
| PUT | `/api/v1/relays/{channel}` | Set single entity state | Protected |
| PUT | `/api/v1/relays` | Set all entity states | Protected |
| GET | `/api/v1/relays/device/info` | Device information | Protected |

### URLs

| Purpose | URL |
|---------|-----|
| Local dev | `http://localhost:8000` |
| Health | `http://localhost:8000/health` |
| API docs | `http://localhost:8000/docs` |

## Domain

### Vocabulary

| Term | Meaning |
|------|---------|
| relay | A physical switching device controlled via USB |
| channel | A numbered output on the relay board (1-based indexing) |
| device | The USB relay module hardware |
| HID | Human Interface Device protocol (USB communication method) |
| fail-safe | All outputs default to OFF on crash/shutdown |
| mock mode | Running without physical hardware (`RELAY_MOCK=true`) |
| toggle | Switching a relay between on and off states |

### Domain-Specific Behaviors

- Thread safety via `threading.Lock()` — all device access serialized
- Multi-channel operations rollback completed channels on partial failure
- `all_off()` executes on both startup and shutdown (fail-safe non-negotiable)
- Device state tracked in software (no hardware read-back)
- Device selection happens in lifespan based on config

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `RELAY_MOCK` | Enable mock device | `false` |
| `RELAY_CHANNELS` | Number of channels | `2` |
| `RELAY_VENDOR_ID` | USB vendor ID | `0x16C0` |
| `RELAY_PRODUCT_ID` | USB product ID | `0x05DF` |
| `RELAY_API_KEY` | Auth key (empty = open) | `""` |
| `RELAY_RATE_LIMIT` | Requests/minute (0 = off) | `0` |
| `RELAY_HOST` | Bind host | `0.0.0.0` |
| `RELAY_PORT` | Bind port | `8000` |
| `RELAY_DEBUG` | Debug mode | `false` |

## Design Patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| Protocol (interface) | Core layer | Hardware abstraction |
| Dependency injection | `Depends()` in API layer | Decoupled service access |
| Repository pattern | `_states` dict in service | In-memory state tracking |
| Middleware | Rate limiting | Cross-cutting concerns |
| Factory pattern | Device creation in lifespan | Extensible device types |
| Observer pattern | Audit logging | State change notification |

## Troubleshooting

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| All endpoints 503 | Device disconnected | `/health` → `device_connected: false` |
| Endpoints 401 | API key misconfigured | Check `RELAY_API_KEY` env var |
| Endpoints 429 | Rate limit exceeded | Check `RELAY_RATE_LIMIT` setting |
| Startup fails | Missing env vars or port conflict | Check `.env` and port availability |
| Slow responses | Lock contention or device I/O | Check concurrent request count |

## Personas

| Name | Role | Focus |
|------|------|-------|
| Alex Rivera | Lead / Hardware | Protocol design, fail-safe, rollback, typed exceptions |
| Priya Sharma | QA / Testing | Three-path tests, deterministic fixtures, audit log verification |
| Marcus Chen | DevOps | Env-only config, structured logging, Docker, health endpoints |
| Sofia Nakamura | Product | OpenAPI docs, versioned routes, backwards compatibility |
| Daniel Okoye | App Developer | Typed models, thin handlers, DI, layer boundaries |
| Janet Moore | Security | Timing-safe auth, uniform errors, audit logging, rate limiting |