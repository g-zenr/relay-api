---
name: changelog
description: Generate a changelog from git history for release notes
disable-model-invocation: true
---

Generate a changelog: $ARGUMENTS

If no version/range is specified, generate from the last tag (or all history if no tags exist).

## Step 1 — Gather Commits
```bash
git log --oneline --no-merges <range>
```
If no range given:
```bash
git tag --sort=-v:refname | head -1   # Find latest tag
git log <latest-tag>..HEAD --oneline --no-merges
```
If no tags exist:
```bash
git log --oneline --no-merges
```

## Step 2 — Categorize Changes

Group commits by type using conventional commit prefixes:

### Added
- `feat` commits — new features, endpoints, capabilities

### Changed
- `refactor` commits — restructuring, improvements
- `chore` commits — dependency updates, config changes

### Fixed
- `fix` commits — bug fixes

### Security
- `security` commits — security improvements

### Documentation
- `docs` commits — documentation updates

### Testing
- `test` commits — new or updated tests

## Step 3 — Format Output

```markdown
# Changelog

## [<version>] - <date>

### Added
- <description> (<commit hash>)

### Changed
- <description> (<commit hash>)

### Fixed
- <description> (<commit hash>)

### Security
- <description> (<commit hash>)
```

## Step 4 — Include Summary Stats
- Total commits
- Files changed
- Lines added/removed
- Test count change (if applicable)

## Rules
- Write descriptions from the USER's perspective, not developer's
- "Add rate limiting" not "Add RateLimitMiddleware class"
- Skip merge commits and version bumps
- Include commit hash as reference
- Order by importance within each category
