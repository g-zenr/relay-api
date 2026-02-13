---
name: pr
description: Create a pull request with proper title, description, and test plan
disable-model-invocation: true
---

Create a pull request for the current branch: $ARGUMENTS

## Step 1 — Pre-PR Validation
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
Both MUST pass. Never create a PR with failing tests or type errors.

## Step 2 — Analyze Changes
```bash
git log main..HEAD --oneline
git diff main...HEAD --stat
```
Understand the full scope of changes since branching from main.

## Step 3 — Generate PR Title
- Under 70 characters
- Use imperative mood: "Add...", "Fix...", "Update..."
- Be specific: "Add rate limiting middleware" not "Update code"

## Step 4 — Generate PR Body
Use this structure:
```markdown
## Summary
- Bullet point 1: what changed and why
- Bullet point 2: what changed and why
- (1-3 bullets max)

## Changes
- List every file modified/created/deleted with brief reason

## Test Plan
- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] Type checking passes (`mypy app/`)
- [ ] New tests added for: <list new test coverage>
- [ ] Manual verification: <curl command or steps>

## Checklist
- [ ] `from __future__ import annotations` in all new files
- [ ] Typed exceptions (no generic `Exception`)
- [ ] Pydantic models for all request/response shapes
- [ ] OpenAPI metadata on all new endpoints
- [ ] README.md updated (if new endpoints/config)
- [ ] .env.example updated (if new settings)
```

## Step 5 — Push and Create PR
```bash
git push -u origin <branch-name>
gh pr create --title "<title>" --body "<body>"
```

## Step 6 — Confirm
Output the PR URL so it can be reviewed.
