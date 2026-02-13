---
name: verify
description: Run the full verification pipeline — tests, types, and quality checks
---

Run the complete verification pipeline for the Relay API.

## Step 1: Tests
```bash
python -m pytest tests/ -v --tb=short
```
- ALL tests must pass
- Report total count and any failures with full error output

## Step 2: Type Checking
```bash
python -m mypy app/
```
- Must pass with zero errors
- Report any type violations with file:line references

## Step 3: Quick Sanity Checks
Verify these project invariants:
- `from __future__ import annotations` present in every `.py` file under `app/`
- No `print()` statements in `app/` (use `logging` instead)
- No `Any` type in `app/models/schemas.py`
- `all_off()` called in both startup and shutdown paths in `app/main.py`

## Output
```
Tests:      PASS (X passed) / FAIL (X passed, Y failed)
Types:      PASS (X files) / FAIL (list errors)
Invariants: PASS / FAIL (list violations)
```

If everything passes: "Ready to commit."
If anything fails: list each failure with file:line and suggested fix.
