---
name: onboard
description: Generate a developer onboarding guide for new team members (Sofia Nakamura's workflow)
disable-model-invocation: true
---

Generate an onboarding guide for: $ARGUMENTS

If no specific audience, create a general developer onboarding guide.

## Step 1 — Read the Codebase
Understand the current state by reading:
- `README.md` — project overview
- `CLAUDE.md` — coding standards
- `app/main.py` — app structure and lifespan
- `app/config.py` — all configuration options
- `.env.example` — environment setup
- `PERSONAS.md` — team roles and responsibilities
- `tests/conftest.py` — test infrastructure

## Step 2 — Generate Onboarding Guide

### Quick Start (5 minutes)
```bash
# 1. Clone and set up
git clone <repo-url> && cd relay-api
python -m venv venv && venv\Scripts\activate   # Windows
# source venv/bin/activate                     # Linux/macOS
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — set RELAY_MOCK=true for development

# 3. Run
RELAY_MOCK=true python run.py
# API docs: http://localhost:8000/docs

# 4. Test
python -m pytest tests/ -v --tb=short
python -m mypy app/
```

### Architecture Overview
Explain the layered architecture:
```
HTTP Request → API Layer (routes, auth, DI) → Service Layer (business logic, thread safety) → Core Layer (device protocol, HID)
```
- Layer boundaries: `API → Services → Core` (never reverse)
- Dependency injection via FastAPI `Depends()`
- Device abstraction via `RelayDevice` Protocol

### Key Files to Read First
1. `app/core/device.py` — understand the device protocol
2. `app/services/relay_service.py` — understand business logic
3. `app/api/v1/relays.py` — understand API endpoints
4. `app/api/dependencies.py` — understand auth and DI chain
5. `tests/conftest.py` — understand test infrastructure

### Coding Standards Summary
- `from __future__ import annotations` in every file
- Typed exceptions from `app/core/exceptions.py`
- Pydantic models for all API shapes
- Thin route handlers — logic in `RelayService`
- Three-path test coverage (success, validation, device error)
- `hmac.compare_digest()` for secrets
- Audit logging on all state changes

### Available Skills
List all `/skill` commands available in Claude Code for this project.

### Team Personas
Brief summary of each persona and their area of ownership:
- **Alex Rivera** — Hardware/device layer
- **Priya Sharma** — Testing and QA
- **Marcus Chen** — DevOps and deployment
- **Sofia Nakamura** — Product and documentation
- **Daniel Okoye** — API layer and architecture
- **Janet Moore** — Security and compliance

### Common Tasks
- "Add a new endpoint" → `/add-endpoint`
- "Add a full feature" → `/add-feature`
- "Write tests" → `/test`
- "Fix a bug" → `/fix-issue`
- "Review code" → `/review`
- "Deploy check" → `/deploy-check`

## Step 3 — Output
Write the guide as clear, concise markdown. Target audience: a developer joining the team who has Python and FastAPI experience but has never seen this codebase.