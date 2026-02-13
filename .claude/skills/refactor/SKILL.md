---
name: refactor
description: Safely refactor code while maintaining all tests and type safety (Daniel Okoye's workflow)
disable-model-invocation: true
---

Refactor: $ARGUMENTS

Follow Daniel Okoye's architecture standards:

1. **Baseline**: Run tests and type check BEFORE making any changes
   ```bash
   python -m pytest tests/ -v --tb=short
   python -m mypy app/
   ```
   If either fails, fix existing issues first — never refactor on a broken baseline.

2. **Analyze**: Read the code to be refactored and all its callers
   - Map the dependency graph: who imports/calls this code?
   - Identify the layer: Core → Service → API
   - Check for test coverage of current behavior

3. **Refactor rules**:
   - Preserve the public API — same function signatures, same return types
   - If renaming, update ALL callers and tests in the same commit
   - Maintain layer boundaries: `API → Services → Core` — never reverse
   - Keep route handlers thin — if moving logic, move it INTO service layer, not out
   - All service access still via `Depends()` — no direct imports in API layer
   - Keep `from __future__ import annotations` in every file
   - No new `Any` types — use explicit types

4. **If splitting files**:
   - Update `__init__.py` exports if needed
   - Ensure no circular imports between layers
   - Each new file gets `from __future__ import annotations`

5. **If renaming**:
   - Search entire codebase for old name: source files, tests, config, docs
   - Update `README.md` if it references renamed items
   - Update OpenAPI metadata (summary, description) if endpoints changed

6. **Verify**: Run the same checks as step 1
   ```bash
   python -m pytest tests/ -v --tb=short
   python -m mypy app/
   ```
   All tests MUST still pass. No new type errors. No regressions.
