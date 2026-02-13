---
name: release
description: Cut a release — version bump, changelog, git tag, and push (Marcus Chen's workflow)
disable-model-invocation: true
---

Create a release: $ARGUMENTS

If no version specified, determine the next version using semantic versioning.

## Step 1 — Pre-release Validation
Run the full quality gate:
```bash
python -m pytest tests/ -v --tb=short
python -m mypy app/
```
Both MUST pass. Never release with failing tests or type errors.

## Step 2 — Determine Version
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, no new features, no breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to the API

Check current version:
```bash
grep 'app_version' app/config.py
git tag --sort=-v:refname | head -5
```

## Step 3 — Update Version
Update version in these files:
1. `app/config.py` — `app_version: str = "<new version>"`
2. `.env.example` — `RELAY_APP_VERSION=<new version>`

## Step 4 — Generate Changelog
Run `/changelog` or manually create entry:
```markdown
## [<version>] - <date>

### Added
- <new features>

### Changed
- <modifications>

### Fixed
- <bug fixes>
```

## Step 5 — Commit Release
```bash
git add app/config.py .env.example CHANGELOG.md
git commit -m "chore: release v<version>"
```

## Step 6 — Tag
```bash
git tag -a v<version> -m "Release v<version>"
```

## Step 7 — Push
```bash
git push origin main
git push origin v<version>
```

## Step 8 — GitHub Release (optional)
```bash
gh release create v<version> \
  --title "v<version>" \
  --notes-file CHANGELOG.md
```

## Step 9 — Verify
```bash
git log --oneline -3
git tag --sort=-v:refname | head -3
```
Confirm the tag and commit exist.

## Rules
- NEVER release without passing tests and type checks
- NEVER skip the changelog
- NEVER use force-push on release tags
- Version in `app/config.py` MUST match the git tag