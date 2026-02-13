---
name: troubleshoot
description: Investigate runtime or production issues from logs, errors, or unexpected behavior (Marcus + Alex workflow)
disable-model-invocation: true
---

Troubleshoot: $ARGUMENTS

Unlike `/debug` (code-level bugs) or `/fix-issue` (known issues), `/troubleshoot` investigates runtime/production problems from symptoms.

## Step 1 — Gather Symptoms
Identify what's happening:
- What errors are users seeing? (status codes, error messages)
- When did it start? (after a deploy, config change, or spontaneously?)
- Is it affecting all requests or specific endpoints?
- Is the health endpoint responding? What status?

## Step 2 — Check Infrastructure
```bash
# Is the process running?
curl http://localhost:8000/health

# Check device connectivity
curl http://localhost:8000/api/v1/relays/device/info

# Check recent logs (if accessible)
# Look for ERROR and WARNING entries
```

### Common infrastructure issues:
| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| All endpoints return 503 | USB device disconnected | `/health` → `device_connected: false` |
| Endpoints return 401 | API key misconfigured | Check `RELAY_API_KEY` env var |
| Endpoints return 429 | Rate limit exceeded | Check `RELAY_RATE_LIMIT` setting |
| Startup fails | Missing env vars or port conflict | Check `.env` and port availability |
| Slow responses | Lock contention or device I/O | Check concurrent request count |

## Step 3 — Check Configuration
Read `app/config.py` and verify env vars are set correctly:
- `RELAY_MOCK` — is it accidentally `true` in production?
- `RELAY_VENDOR_ID` / `RELAY_PRODUCT_ID` — do they match the hardware?
- `RELAY_CHANNELS` — does it match the physical board?
- `RELAY_API_KEY` — is it set when it should be (or unset when it shouldn't)?
- `RELAY_RATE_LIMIT` — is it too restrictive?

## Step 4 — Check Application Logs
Look for patterns in log output:
- `relay.audit` entries — are state changes being logged?
- `WARNING` level — device disconnection, degraded mode
- `ERROR` level — device communication failures, unhandled exceptions
- Startup messages — did all components initialize?

## Step 5 — Reproduce Locally
```bash
# Start in mock mode to isolate hardware vs software issues
RELAY_MOCK=true python run.py

# Hit the failing endpoint
curl -X PUT http://localhost:8000/api/v1/relays/1 \
  -H "Content-Type: application/json" \
  -d '{"state": "on"}'
```
- If it works in mock mode → hardware/driver issue
- If it fails in mock mode → software bug → switch to `/debug`

## Step 6 — Resolution
- If config issue → fix env vars, restart
- If hardware issue → check USB connection, permissions, drivers
- If software bug → use `/debug` or `/fix-issue` to fix the code
- If performance issue → use `/optimize` to profile and fix

## Step 7 — Document
Log the incident:
- What happened, when, how long it lasted
- Root cause identified
- Fix applied
- Prevention steps (monitoring, alerting, tests)