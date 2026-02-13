---
name: fix-issue
description: Investigate and fix a bug following project standards
disable-model-invocation: true
---

Investigate and fix: $ARGUMENTS

1. **Reproduce**: Understand the issue. Read relevant source files and tests.
   - If a test already covers this case, run it to confirm it fails
   - If no test exists, write a failing test first

2. **Diagnose**: Find the root cause
   - Search the codebase for related code using Grep/Glob
   - Check the exception hierarchy in `app/core/exceptions.py`
   - Check service logic in `app/services/relay_service.py`
   - Check API layer in `app/api/v1/`

3. **Fix**: Implement the fix
   - Fix in the correct layer (device → service → API)
   - Use typed exceptions, not generic `Exception`
   - Maintain thread safety if touching service layer
   - Rollback semantics if touching multi-channel operations

4. **Test**: Verify the fix
   - Ensure the failing test now passes
   - Run full suite: `python -m pytest tests/ -v --tb=short`
   - Run type check: `python -m mypy app/`

5. **Audit**: Check for related issues
   - Are there similar patterns elsewhere that have the same bug?
   - Does the fix maintain backwards compatibility?
