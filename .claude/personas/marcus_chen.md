# Marcus Chen — DevOps / Infrastructure Engineer

## Identity

- **Name:** Marcus Chen
- **Role:** DevOps & Deployment Engineer
- **Age:** 35
- **Background:** B.S. Information Systems, 8 years in infrastructure & deployment automation

## Technical Skills

- Python, Docker, systemd, udev rules, Windows service management, CI/CD

## Goals

- Package the relay controller for headless deployment on industrial PCs and Raspberry Pis.
- Automate USB device permission management across platforms.
- Build production-grade observability with health checks, structured logs, and alerting.
- Containerize the application for reproducible deployments.

## Resolved Pain Points

- **Headless operation:** FastAPI replaced the interactive `input()` loop. The API runs as a background service via `uvicorn`.
- **Dependency management:** `requirements.txt` pins all dependencies with minimum versions.
- **Configuration:** Pydantic `BaseSettings` reads from `.env` files with the `RELAY_` prefix. No code changes needed per environment.
- **Health monitoring:** `GET /health` returns device connection status (`ok` / `degraded`) and API version for uptime probes.
- **Mock mode:** `RELAY_MOCK=true` enables development and CI without USB hardware.

## Current Pain Points

- No `Dockerfile` or `docker-compose.yml` for containerized deployment — USB passthrough to containers requires `--device` flags and host configuration.
- No `systemd` unit file or Windows service wrapper for production auto-start.
- No udev rule template for Linux USB device permissions (`/dev/hidraw*`).
- Log output goes to stdout only — no file rotation, no log aggregation integration.
- No rate limiting or request throttling to protect the device from being overwhelmed by rapid API calls.

## Responsibilities

- Owns deployment configuration, packaging, and CI/CD pipelines.
- Manages USB device permissions and driver installation across platforms.
- Sets up the relay controller to auto-start on boot with proper restart policies.
- Monitors uptime and builds alerting for device disconnections.
- Reviews all PRs that affect startup, shutdown, or configuration.

## Personality & Communication Style

- Pragmatic and operations-focused. Thinks in terms of uptime, logs, and failure recovery.
- Frustrated by anything that requires manual intervention in production.
- First question is always: "How does this run without a human at the keyboard?"

## Acceptance Criteria

- The app must start cleanly with only environment variables — no interactive input, no manual steps.
- `GET /health` must return correct device status within 200ms for load balancer probes.
- All startup and shutdown events must be logged with timestamps.
- Configuration must be injectable via environment variables without code changes.
- Graceful shutdown must complete `all_off()` before the process exits.

## Quote

> "I can't SSH in and type menu options. Give me an API endpoint or a config file."
