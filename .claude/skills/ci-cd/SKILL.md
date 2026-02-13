---
name: ci-cd
description: Set up or update GitHub Actions CI/CD pipeline (Marcus Chen's workflow)
disable-model-invocation: true
---

Set up CI/CD: $ARGUMENTS

## Step 1 — Create Workflow Directory
```bash
mkdir -p .github/workflows
```

## Step 2 — CI Workflow (tests + type check on every push/PR)
Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: python -m pytest tests/ -v --tb=short
        env:
          RELAY_MOCK: "true"

      - name: Type checking
        run: python -m mypy app/
```

## Step 3 — Docker Build Workflow (verify Dockerfile on every PR)
Create `.github/workflows/docker.yml`:

```yaml
name: Docker Build

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t relay-api:test .

      - name: Test Docker image
        run: |
          docker run -d --name test-relay -e RELAY_MOCK=true -p 8000:8000 relay-api:test
          sleep 5
          curl -f http://localhost:8000/health || exit 1
          docker stop test-relay
```

## Step 4 — Release Workflow (on tag push)
Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

## Step 5 — Add CI Badge to README
```markdown
[![CI](https://github.com/<owner>/relay-api/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/relay-api/actions/workflows/ci.yml)
```

## Step 6 — Verify
```bash
git add .github/
git commit -m "ci: add GitHub Actions workflows"
git push
```
Check the Actions tab on GitHub to verify the workflow runs.

## Rules
- Always test with `RELAY_MOCK=true` in CI (no hardware)
- Test on multiple Python versions (3.11, 3.12)
- Docker build test ensures Dockerfile stays valid
- Never store secrets in workflow files — use GitHub Secrets