---
name: tdd
description: Test-driven development — write failing test first, then implement (red-green-refactor)
disable-model-invocation: true
---

Implement using TDD: $ARGUMENTS

Follow the red-green-refactor cycle strictly.

## Phase 1 — RED: Write Failing Tests

1. **Understand the requirement**: What should the feature/fix do?
2. **Choose test file**: Match `app/` structure
3. **Write tests BEFORE any implementation code**:
   - Success path test — what should happen with valid input
   - Validation error test — what should happen with invalid input
   - Device error test — what should happen when device is disconnected
4. **Run tests** — they MUST fail:
   ```bash
   python -m pytest tests/<test_file>.py -v --tb=short
   ```
   If tests pass without implementation, they're testing nothing. Rewrite them.

### Test Conventions
- Class: `Test<Feature>`
- Method: `test_<action>_<expected_outcome>`
- Fixtures with `Generator` type hints and proper cleanup
- `raise_server_exceptions=False` on TestClient
- Audit log tests with `caplog.at_level(logging.INFO, logger="relay.audit")`

## Phase 2 — GREEN: Minimal Implementation

1. **Write the minimum code to make tests pass** — nothing more
2. Follow project standards:
   - `from __future__ import annotations`
   - Typed exceptions from `app/core/exceptions.py`
   - Thread safety in service layer
   - Pydantic models for API shapes
   - Thin route handlers with `Depends()` injection
3. **Run tests** — they MUST now pass:
   ```bash
   python -m pytest tests/<test_file>.py -v --tb=short
   ```

## Phase 3 — REFACTOR: Clean Up

1. Remove duplication
2. Improve naming
3. Extract helpers if three or more similar patterns exist
4. Ensure layer boundaries are respected
5. **Run full suite** — nothing must break:
   ```bash
   python -m pytest tests/ -v --tb=short
   python -m mypy app/
   ```

## Phase 4 — Complete

1. Verify audit logging if state changes were added
2. Update OpenAPI metadata (summary, description, responses)
3. Update `README.md` if new endpoints or config were added
4. Run final verification:
   ```bash
   python -m pytest tests/ -v --tb=short
   python -m mypy app/
   ```
