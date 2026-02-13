---
name: optimize
description: Profile and optimize code for performance — identify bottlenecks and fix them
disable-model-invocation: true
---

Optimize: $ARGUMENTS

## Step 1 — Baseline Measurement
Before optimizing, measure current performance:
```bash
python -m pytest tests/ -v --tb=short  # Ensure tests pass first
```

Identify what to measure:
- **Endpoint latency**: Time from request to response
- **Throughput**: Requests per second under load
- **Memory**: Per-request memory allocation
- **Lock contention**: Time spent waiting on `threading.Lock`

## Step 2 — Profile
Read the code and identify potential bottlenecks:

### Common bottlenecks in this codebase:
- **Lock contention** in `RelayService` — are locks held too long?
- **HID communication** — is `set_channel` blocking other requests?
- **Middleware overhead** — rate limiter checking on every request
- **Pydantic serialization** — model validation on large response lists
- **Logging** — synchronous logging in hot paths

### Static analysis checklist:
- [ ] Lock scope is minimal (acquire late, release early)
- [ ] No I/O operations inside lock
- [ ] No unnecessary object creation in hot paths
- [ ] Middleware short-circuits early for exempt paths
- [ ] List comprehensions instead of loops where applicable

## Step 3 — Optimize (targeted fixes only)
For each bottleneck identified:
1. Write a benchmark test that demonstrates the issue
2. Implement the fix
3. Re-run the benchmark to verify improvement
4. Run full test suite to verify no regressions

### Optimization principles:
- Measure before and after — no blind optimization
- Optimize the bottleneck, not everything
- Prefer algorithmic improvements over micro-optimizations
- Never sacrifice readability for negligible performance gains
- Never sacrifice thread safety for performance

## Step 4 — Verify
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
All tests MUST still pass. No type errors. No regressions.

## Step 5 — Document
- Comment any non-obvious optimization with rationale
- Update performance-sensitive code with complexity notes if applicable