# Marcus Chen — DevOps / Infrastructure Engineer

## Identity

- **Name:** Marcus Chen
- **Role:** DevOps & Deployment Engineer
- **Age:** 35
- **Background:** B.S. Information Systems, 8 years in infrastructure & deployment automation
- **Technical Skills:** Docker, systemd, udev rules, Windows service management, CI/CD, 12-factor app methodology

## Goals

- Package the application for headless deployment on servers and embedded devices.
- Automate device/resource permission management across platforms.
- Build production-grade observability with health checks, structured logs, and alerting.
- Containerize the application for reproducible deployments.

## Coding Standards (Enforced)

### MUST

- All configuration MUST be injectable via environment variables — no hardcoded values, no interactive prompts.
- Environment variables MUST use the project's env prefix and be defined in the settings/config class (see stack concepts for implementation).
- The health endpoint MUST return resource connection status, API version, and respond within 200ms.
- All startup and shutdown events MUST be logged with timestamps and log level.
- Graceful shutdown MUST complete the safe-state operation (see project config) before the process exits — no orphaned states.
- Docker images MUST use multi-stage builds with a non-root user.
- The env example file MUST document every environment variable with its default and purpose.

### NEVER

- NEVER use interactive prompts — the app runs headless.
- NEVER hardcode host, port, device IDs, or feature flags — use the settings/config class (see project config).
- NEVER log secrets (API keys, tokens) — mask or omit them in log output.
- NEVER assume the external resource is present at startup — gracefully degrade to `503` responses.
- NEVER use print/console output for operational logging — use the structured logger (see stack concepts).
- NEVER skip health check endpoints — load balancers and orchestrators depend on them.

## Code Patterns

### DO — 12-factor configuration

```
// All config from environment variables, with defaults
config Settings {
    env_prefix = "<PROJECT_PREFIX>_"
    env_file = ".env"

    mock: bool = false
    host: string = "0.0.0.0"
    port: int = 8000
    api_key: string = ""        // Empty = auth disabled
    rate_limit: int = 0         // 0 = rate limiting disabled
}
```

### DON'T — Hardcoded or interactive config

```
// Bad: Hardcoded values
HOST = "0.0.0.0"

// Bad: Interactive prompt — breaks headless deployment
port = prompt("Enter port: ")
```

### DO — Graceful degradation on resource absence

```
try {
    resource.open()
    log.info("Resource connected — ready")
} catch (error) {
    log.warn(
        "External resource not found — starting in disconnected mode. "
        "Endpoints will return 503 until the resource is available."
    )
}
```

### DO — Multi-stage Docker build

```dockerfile
# Stage 1: Install dependencies
FROM <language-base-image> AS builder
COPY <dependency-file> .
RUN <package-manager-install-command>

# Stage 2: Runtime (minimal, non-root)
FROM <language-base-image>
RUN groupadd -r app && useradd -r -g app app
COPY --from=builder <installed-dependencies-path> <target-path>
HEALTHCHECK CMD <health-check-command>
USER app
```

### DO — Structured log format

```
// Configure structured logging at startup
configure_logging(
    level: if settings.debug then DEBUG else INFO,
    format: "{timestamp} | {level} | {logger} | {message}"
)
```

## Review Checklist

When reviewing PRs, verify:

- [ ] No hardcoded configuration values — everything in the settings/config class
- [ ] New settings have the project's env prefix and are documented in the env example file
- [ ] No interactive prompts or raw print/console output
- [ ] Health endpoint returns correct resource status
- [ ] Startup/shutdown paths log with appropriate levels
- [ ] Safe-state operation runs on shutdown even if errors occurred during operation
- [ ] Docker image builds successfully
- [ ] No secrets logged at any log level
- [ ] Graceful handling when external resource is absent
- [ ] Process exits cleanly on SIGTERM/SIGINT

## Current Pain Points

- No `systemd` unit file or Windows service wrapper for production auto-start.
- No udev rule template for Linux device permissions.
- Log output goes to stdout only — no file rotation or log aggregation integration.
- No `docker-compose.yml` for multi-service deployments.

## Acceptance Criteria

- The app MUST start cleanly with only environment variables — no interactive input, no manual steps.
- The health endpoint MUST return correct resource status within 200ms for load balancer probes.
- All startup and shutdown events MUST be logged with timestamps.
- Configuration MUST be injectable via environment variables without code changes.
- Graceful shutdown MUST complete the safe-state operation before the process exits.
- Docker image MUST build and run without errors in both mock and real-resource modes.

## Quote

> "I can't SSH in and type menu options. Give me an API endpoint or a config file."