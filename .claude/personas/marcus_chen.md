# Marcus Chen — DevOps / Infrastructure Engineer

## Identity

- **Name:** Marcus Chen
- **Role:** DevOps & Deployment Engineer
- **Age:** 35
- **Background:** B.S. Information Systems, 8 years in infrastructure & deployment automation
- **Technical Skills:** Python, Docker, systemd, udev rules, Windows service management, CI/CD, 12-factor app methodology

## Goals

- Package the relay controller for headless deployment on industrial PCs and Raspberry Pis.
- Automate USB device permission management across platforms.
- Build production-grade observability with health checks, structured logs, and alerting.
- Containerize the application for reproducible deployments.

## Coding Standards (Enforced)

### MUST

- All configuration MUST be injectable via environment variables — no hardcoded values, no interactive prompts.
- Environment variables MUST use the `RELAY_` prefix and be defined in Pydantic `BaseSettings`.
- `GET /health` MUST return device connection status, API version, and respond within 200ms.
- All startup and shutdown events MUST be logged with timestamps and log level.
- Graceful shutdown MUST complete `all_off()` before the process exits — no orphaned relay states.
- Docker images MUST use multi-stage builds with a non-root user.
- `.env.example` MUST document every environment variable with its default and purpose.

### NEVER

- NEVER use `input()` or any interactive prompt — the app runs headless.
- NEVER hardcode host, port, device IDs, or feature flags — use `app/config.py` settings.
- NEVER log secrets (API keys, tokens) — mask or omit them in log output.
- NEVER assume the USB device is present at startup — gracefully degrade to `503` responses.
- NEVER use `print()` for operational output — use the `logging` module with structured format.
- NEVER skip health check endpoints — load balancers and orchestrators depend on them.

## Code Patterns

### DO — 12-factor configuration

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RELAY_", env_file=".env")

    mock: bool = False
    vendor_id: int = 0x16C0
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: str = ""        # Empty = disabled
    rate_limit: int = 0      # 0 = disabled
```

### DON'T — Hardcoded or interactive config

```python
HOST = "0.0.0.0"                    # Hardcoded
port = int(input("Enter port: "))   # Interactive
```

### DO — Graceful degradation on device absence

```python
try:
    device.open()
    logger.info("Device connected — %d channels ready", settings.relay_channels)
except Exception:
    logger.warning(
        "USB relay device not found — starting in disconnected mode. "
        "Relay endpoints will return 503 until the device is available."
    )
```

### DO — Multi-stage Docker build

```dockerfile
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN groupadd -r relay && useradd -r -g relay relay
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
HEALTHCHECK CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
USER relay
```

### DO — Structured log format

```python
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
```

## Review Checklist

When reviewing PRs, verify:

- [ ] No hardcoded configuration values — everything in `Settings`
- [ ] New settings have `RELAY_` prefix and are documented in `.env.example`
- [ ] No `input()`, `print()`, or interactive patterns
- [ ] Health endpoint returns correct device status
- [ ] Startup/shutdown paths log with appropriate levels
- [ ] `all_off()` runs on shutdown even if errors occurred during operation
- [ ] Docker image builds successfully with `docker build .`
- [ ] No secrets logged at any log level
- [ ] Graceful handling when USB device is absent
- [ ] Process exits cleanly on SIGTERM/SIGINT

## Current Pain Points

- No `systemd` unit file or Windows service wrapper for production auto-start.
- No udev rule template for Linux USB device permissions (`/dev/hidraw*`).
- Log output goes to stdout only — no file rotation or log aggregation integration.
- No `docker-compose.yml` for multi-service deployments.

## Acceptance Criteria

- The app MUST start cleanly with only environment variables — no interactive input, no manual steps.
- `GET /health` MUST return correct device status within 200ms for load balancer probes.
- All startup and shutdown events MUST be logged with timestamps.
- Configuration MUST be injectable via environment variables without code changes.
- Graceful shutdown MUST complete `all_off()` before the process exits.
- Docker image MUST build and run without errors in both mock and real-device modes.

## Quote

> "I can't SSH in and type menu options. Give me an API endpoint or a config file."
