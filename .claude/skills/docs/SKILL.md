---
name: docs
description: Update all project documentation to match current codebase (Sofia Nakamura's workflow)
disable-model-invocation: true
---

Update project documentation: $ARGUMENTS

Follow Sofia Nakamura's documentation standards:

1. **Audit current state**: Read all documentation files and compare against actual codebase
   - `README.md` — API endpoints table, configuration table, examples
   - `.env.example` — every setting with description and default
   - `app/main.py` DESCRIPTION block — feature list and usage info
   - OpenAPI metadata on every endpoint (summary, description, responses)

2. **README.md updates**:
   - API Endpoints table MUST match actual routes in `app/api/v1/`
   - Configuration table MUST match all fields in `app/config.py` Settings
   - Examples MUST work with current API (test with `curl` commands)
   - Architecture diagram MUST match actual file structure
   - Docker section MUST match current `Dockerfile`

3. **`.env.example` updates**:
   - Every field in `app/config.py` Settings MUST have a corresponding line
   - Each variable has a comment explaining purpose, options, and default
   - Group by category: App, Device, Server, CORS, Auth, Rate Limiting

4. **OpenAPI metadata**:
   - Every endpoint in `app/api/v1/` MUST have `summary` and `description`
   - Every endpoint MUST declare `responses` with status codes and models
   - Check by visiting `/docs` or reading route decorators

5. **API description** in `app/main.py`:
   - DESCRIPTION string MUST list all current features
   - Authentication section matches actual auth behavior
   - Rate limiting section matches actual middleware behavior

6. **Output**: List every change made and every discrepancy found
