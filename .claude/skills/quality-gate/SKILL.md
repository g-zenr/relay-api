---
name: quality-gate
description: Pre-merge quality gate — chains verify, review, and security audit into a pass/fail verdict
disable-model-invocation: true
---

Run the full quality gate before merging. This orchestrates multiple checks into a single pass/fail verdict.

## Gate 1 — Verification (automated)
Run the full test and type-check pipeline:
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
- **PASS**: All tests green, zero type errors
- **FAIL**: Any test failure or type error → stop here, fix first

## Gate 2 — Code Quality Audit
Check the codebase for structural issues:

### Layer Violations
- Search for imports that violate `API → Services → Core` direction
- No `app/core/` importing from `app/api/` or `app/services/`
- No `app/services/` importing from `app/api/`

### Dead Code
- Search for unused imports across `app/`
- Search for functions/methods with zero callers
- Check for commented-out code blocks (remove or restore)

### Concurrency
- Verify all device access is wrapped in `self._lock` in `RelayService`
- Verify no race conditions in middleware state (rate limiter counters)

### Observability
- Verify all state changes produce `relay.audit` log entries
- Verify startup/shutdown events are logged
- Verify structured log format is consistent

## Gate 3 — Security Review
Quick security pass:
- [ ] `hmac.compare_digest()` used for all secret comparisons
- [ ] No secrets in error responses (grep for stack trace patterns)
- [ ] No secrets logged at any level (grep for `api_key` in log statements)
- [ ] Auth enforced on all state-changing endpoints when API key is configured
- [ ] Input validation via Pydantic on all endpoints
- [ ] Rate limiting functional when configured

## Gate 4 — Documentation Currency
- [ ] `README.md` API table matches actual routes
- [ ] `.env.example` matches all `Settings` fields
- [ ] OpenAPI metadata present on every endpoint
- [ ] `from __future__ import annotations` in every `app/` source file

## Verdict

```
Gate 1 (Verify):    PASS / FAIL
Gate 2 (Quality):   PASS / FAIL (list violations)
Gate 3 (Security):  PASS / FAIL (list findings)
Gate 4 (Docs):      PASS / FAIL (list gaps)
─────────────────────────────────
OVERALL:            PASS / FAIL
```

**PASS** = Safe to merge. All gates green.
**FAIL** = List every failing item with file:line and remediation. Do not merge.
