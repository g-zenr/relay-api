---
name: architect
description: Review and evolve the codebase architecture — evaluate patterns, layers, and design decisions (Alex + Daniel workflow)
---

Evaluate the architecture: $ARGUMENTS

## Step 1 — Read Current Architecture
Read every layer of the codebase:
- `app/core/device.py` — Device protocol and implementations
- `app/services/relay_service.py` — Business logic layer
- `app/api/v1/relays.py` — API endpoints
- `app/api/dependencies.py` — DI and auth chain
- `app/models/schemas.py` — Data models
- `app/config.py` — Configuration
- `app/middleware.py` — Middleware
- `app/main.py` — App initialization and lifespan

## Step 2 — Evaluate Layer Boundaries
Check the dependency graph:
```
API Layer (app/api/)
  ↓ depends on
Service Layer (app/services/)
  ↓ depends on
Core Layer (app/core/)

Models (app/models/) ← shared across layers
Config (app/config.py) ← shared across layers
```

### Check for violations:
- Does any lower layer import from a higher layer?
- Are there circular imports?
- Is business logic leaking into route handlers?
- Is device logic leaking into the service layer?
- Are there god objects (classes doing too much)?

## Step 3 — Evaluate Design Patterns
Review patterns in use and their appropriateness:

| Pattern | Where Used | Evaluate |
|---------|-----------|----------|
| Protocol (interface) | `RelayDevice` | Is it sufficient? Does it need extending? |
| Dependency injection | FastAPI `Depends()` | Is the DI chain clean? Any circular deps? |
| Repository pattern | `RelayService._states` | Is in-memory state sufficient? Need persistence? |
| Middleware | Rate limiting | Is middleware the right layer? Any alternatives? |
| Factory pattern | Device creation in lifespan | Is it extensible for new device types? |
| Observer pattern | Audit logging | Should state changes notify external systems? |

## Step 4 — Evaluate Scalability Concerns
- **Multi-device**: Can the architecture support multiple USB boards?
- **Multi-user**: Can it handle concurrent users with different permissions?
- **Multi-instance**: Can multiple API instances share device state?
- **Event-driven**: Can it push state changes (WebSocket, SSE)?
- **Persistence**: Should relay state survive restarts?

## Step 5 — Identify Technical Debt
- Code that works but is in the wrong layer
- Abstractions that are too tight or too loose
- Missing abstractions (repeated patterns not extracted)
- Configuration that should be dynamic but is static
- Tests that test implementation instead of behavior

## Step 6 — Propose Improvements
For each improvement, evaluate:
- **Impact**: How much does this improve the codebase?
- **Effort**: How much work is required?
- **Risk**: What could break?
- **Priority**: Must-do / Should-do / Nice-to-have

Format:
```markdown
### Proposal: <title>
**Impact:** High/Medium/Low
**Effort:** Small/Medium/Large
**Risk:** Low/Medium/High
**Priority:** Must/Should/Nice

**Current state:** <what exists now>
**Proposed state:** <what it should become>
**Migration path:** <how to get there safely>
**Files affected:** <list>
```

## Step 7 — Architecture Decision Record
If a significant change is proposed, document it:
```markdown
# ADR-<number>: <title>

## Status: Proposed / Accepted / Rejected

## Context
<why this decision is needed>

## Decision
<what we decided>

## Consequences
<positive and negative effects>
```

## Rules
- Architecture changes MUST maintain backwards compatibility
- Never propose changes without migration paths
- Evaluate trade-offs explicitly — no "this is just better"
- Consider the team's current capacity and skill level
- Prefer incremental evolution over big-bang rewrites