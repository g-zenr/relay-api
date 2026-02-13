# Relay API — Claude Code Instructions

@.claude/PROJECT.md

REST API for controlling DCT Tech USB relay modules via HID.

## Commands

See `@.claude/PROJECT.md` for test, type-check, run, and audit commands.

## Architecture

Dependency flow: `API → Services → Core`. Never reverse this direction.
See `@.claude/PROJECT.md` for full layer mapping, key abstractions, stack details, and file paths.

## Coding Standards

These apply to ALL code in this project. Violations block PR merges.

### Types & Safety

- Future annotations pattern MUST be followed in every source file (see stack concepts in project config)
- All functions MUST have return type annotations
- All typed schemas MUST use explicit field types — no untyped/any fields (see stack concepts)
- Run type checker — must pass clean with zero errors

### Core Layer

- All implementations MUST satisfy the primary protocol/interface
- Errors MUST raise typed exceptions from the exception hierarchy (see project config)
- NEVER catch and swallow exceptions silently — log and re-raise
- Mock implementation MUST mirror real behavior (same exceptions, same state transitions)

### Service Layer

- Thread safety via mutex/lock (see stack concepts) — all device access is serialized
- Multi-channel operations MUST rollback completed channels on partial failure
- All state changes MUST produce audit log entries via the audit logger
- Fail-safe operation MUST run on both startup and shutdown — non-negotiable

### API Layer

- Route handlers MUST be thin — delegate business logic to the service class
- All service access via DI injection (see stack concepts) — never import service instances directly
- All endpoints use typed response schemas (see stack concepts) — no raw dicts/objects
- Error responses use the error response model — never expose stack traces or file paths
- Static routes before parameterized routes to avoid path conflicts
- Every endpoint MUST have summary, description, and responses in OpenAPI metadata (see stack concepts for route handler metadata)

### Security

- API key comparison uses timing-safe comparison (see stack concepts) — NEVER use equality operator for secrets
- Auth error messages are uniform: "Invalid or missing API key" — no differentiation
- Health endpoint bypasses auth (uses public DI dependency)
- NEVER log API keys or secrets at any log level
- Input validation via schema validation constraints (see stack concepts) — never trust raw input

### Configuration

- All config via env vars with the project's env prefix in the config file
- NEVER hardcode host, port, device IDs, or feature flags
- NEVER use interactive prompts or raw print/console output — the app runs headless
- Env example file MUST document every env var with its default and purpose

### Testing

- Every endpoint needs three test paths: success, validation error, device error
- Test fixtures use DI overrides (see stack concepts) — proper cleanup in teardown
- Audit log tests use log capture mechanism (see stack concepts) on the audit logger
- Tests MUST be deterministic — no sleep, no execution order dependence
- Run test command after every change — all tests must pass

## Team Personas

Detailed coding standards, review checklists, and code patterns for each role:
@.claude/personas/alex_rivera.md (Hardware/Lead)
@.claude/personas/priya_sharma.md (QA/Testing)
@.claude/personas/marcus_chen.md (DevOps)
@.claude/personas/sofia_nakamura.md (Product)
@.claude/personas/daniel_okoye.md (App Developer)
@.claude/personas/janet_moore.md (Security)
