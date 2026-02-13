# Sofia Nakamura — Product / Project Manager

## Identity

- **Name:** Sofia Nakamura
- **Role:** Product Manager / Project Coordinator
- **Age:** 30
- **Background:** B.A. Industrial Engineering, 5 years managing hardware-software integration products

## Technical Skills

- Requirements gathering, Jira, basic Python reading comprehension, system diagrams

## Goals

- Expand the relay controller into a full automation platform — scheduling, multi-device support, a web dashboard.
- Align engineering priorities with customer use cases (lab automation, smart home, industrial switching).
- Deliver incremental value each sprint while building toward the larger vision.
- Maintain clear API documentation so integrators can self-serve without engineering support.

## Resolved Pain Points

- **Modular architecture:** The layered design (device → service → API) allows independent feature scoping. New features can target one layer without touching others.
- **N-channel scaling:** `RELAY_CHANNELS` configuration parameter supports 2, 4, 8, or any N-channel board without code changes.
- **API documentation:** FastAPI auto-generates OpenAPI/Swagger docs at `/docs` and `/redoc` with examples, descriptions, and error schemas.
- **REST API:** External apps, dashboards, and mobile clients can integrate via standard HTTP endpoints.

## Current Pain Points

- No scheduling capability — customers want time-based relay automation (e.g., "relay 1 ON at 8 AM, OFF at 6 PM") and it's the most requested feature.
- No web dashboard for non-technical users to monitor and control relays visually.
- No multi-device support — managing multiple USB relay boards from one API instance isn't possible yet.
- No usage analytics or telemetry to understand how customers interact with the API.
- No user-facing quick-start guide for onboarding new customers or team members.

## Responsibilities

- Writes user stories and defines acceptance criteria with Priya.
- Prioritizes the product backlog based on customer feedback and business value.
- Coordinates between hardware procurement and software development.
- Demos the product to stakeholders and collects feedback.
- Ensures API documentation stays current with each release.

## Personality & Communication Style

- Big-picture thinker who translates business needs into technical requirements.
- Asks "what does the customer need?" before "what's technically elegant?"
- Keeps the team focused on deliverables and deadlines without micromanaging.

## Acceptance Criteria

- Every feature must have a user story with clear business justification before development starts.
- API changes must be reflected in the auto-generated OpenAPI docs — no undocumented endpoints.
- New features must be demonstrable to stakeholders within the sprint they're completed.
- The API must remain backwards-compatible — no breaking changes to existing endpoints without a versioned migration path (hence `/api/v1/`).

## Quote

> "Our customers want to schedule relay 1 ON at 8 AM and OFF at 6 PM. Can we do that by next sprint?"
