---
name: rollback
description: Roll back a bad release to the previous known-good version (Marcus workflow)
disable-model-invocation: true
---

Roll back: $ARGUMENTS

When a release causes production issues and a hotfix isn't feasible, roll back to the last known-good state.

## Step 1 — Identify What to Roll Back To
```bash
# List recent tags (releases)
git tag --sort=-v:refname | head -10

# List recent commits on main
git log --oneline -10

# Find the last known-good version
# Usually the tag BEFORE the current one
```

## Step 2 — Verify the Target is Good
```bash
# Check out the target version (read-only)
git checkout v<known-good-version>

# Run tests to confirm it's stable
python -m pytest tests/ -v --tb=short
python -m mypy app/
```

## Step 3 — Choose Rollback Strategy

### Option A: Revert Commit (preferred — preserves history)
```bash
git checkout main

# Revert the bad commit(s)
git revert <bad-commit-hash>
# Or revert a range:
git revert <oldest-bad>^..<newest-bad>
```

### Option B: Reset to Tag (if revert is too complex)
```bash
git checkout main

# Create a backup branch first
git branch backup/pre-rollback

# Reset to the known-good tag
git reset --hard v<known-good-version>

# Force push (DANGEROUS — confirm with team)
git push origin main --force-with-lease
```

## Step 4 — Verify Rollback
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/

# Verify the app starts correctly
RELAY_MOCK=true python run.py &
curl http://localhost:8000/health
```

## Step 5 — Tag the Rollback
```bash
# If using revert strategy:
git tag -a v<rollback-version> -m "Rollback: reverted to v<known-good>"
git push origin main
git push origin v<rollback-version>
```

## Step 6 — Post-Rollback
- Document what went wrong and why
- Create an issue for the proper fix
- Schedule the fix using `/fix-issue` or `/hotfix`
- Consider adding tests that would have caught the issue

## Rules
- ALWAYS verify the target version with tests before rolling back
- ALWAYS create a backup branch before destructive operations
- PREFER `git revert` over `git reset --hard` (preserves history)
- NEVER force-push without team confirmation
- ALWAYS document the rollback reason
- After rollback, use `/fix-issue` to properly address the root cause