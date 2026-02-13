---
name: monitor
description: Set up observability — structured logging, health probes, metrics, and alerting (Marcus Chen's workflow)
disable-model-invocation: true
---

Set up monitoring and observability: $ARGUMENTS

## 1. Structured Logging Audit
Verify the current logging setup:
- [ ] Format: `%(asctime)s | %(levelname)-8s | %(name)s | %(message)s`
- [ ] Level: `INFO` by default, `DEBUG` when `RELAY_DEBUG=true`
- [ ] No `print()` statements in `app/`
- [ ] All loggers use `logging.getLogger(__name__)`
- [ ] Audit logger: `relay.audit` for state changes

### Log levels used correctly:
| Level | Used For |
|-------|----------|
| DEBUG | Verbose troubleshooting (HID commands, request details) |
| INFO | Normal operations (startup, shutdown, state changes) |
| WARNING | Recoverable issues (device not found, degraded mode) |
| ERROR | Failures that need attention (device communication errors) |

## 2. Health Endpoint Verification
Verify `/health` returns:
```json
{
  "status": "ok|degraded",
  "device_connected": true|false,
  "version": "1.0.0"
}
```
- [ ] Responds within 200ms (load balancer requirement)
- [ ] Bypasses authentication
- [ ] Returns `"degraded"` when device is disconnected
- [ ] Returns correct version from `settings.app_version`

## 3. Readiness Probe (if missing)
Consider adding a `/ready` endpoint that checks:
- Service is initialized
- Device is connected and responsive
- Rate limiter is functional

```python
@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(
    service: RelayService = Depends(get_relay_service_public),
) -> ReadinessResponse:
    return ReadinessResponse(
        ready=service.device_connected,
        checks={
            "service_initialized": True,
            "device_connected": service.device_connected,
        },
    )
```

## 4. Request Logging Middleware (if missing)
Consider adding request/response logging for production debugging:
- Log method, path, status code, and response time for every request
- Don't log request/response bodies (may contain sensitive data)
- Use a dedicated logger: `relay.access`

## 5. Metrics Endpoint (optional)
If Prometheus/metrics are needed:
- Request count by endpoint and status code
- Request latency histogram
- Device connection state gauge
- Active relay states gauge

## 6. Docker Health Integration
Verify `Dockerfile` HEALTHCHECK matches `/health` endpoint:
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

## Output
For each section, report:
- **CONFIGURED**: Already in place and working
- **ADDED**: New monitoring capability implemented
- **RECOMMENDED**: Optional improvement (describe what and why)