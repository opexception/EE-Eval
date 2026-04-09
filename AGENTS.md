# AGENTS.md

## Project identity
EE-Eval is an internal web application for HR and management to support employee evaluation workflows, including a 9-box framework and related performance review processes.

This project handles sensitive HR information. Priorities are:

- clarity
- fairness
- auditability
- privacy
- maintainability
- simple, readable implementation

This repository should be developed in a beginner-friendly way that can still evolve toward enterprise-standard practices later.

---

## Primary technology defaults
Unless explicitly directed otherwise, prefer the following stack:

- Backend: FastAPI
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL
- Containerization: Docker + Docker Compose
- Backend tests: pytest
- Frontend tests: Vitest + React Testing Library

If proposing changes to this stack, explain why clearly before making them.

---

## Architecture guidance
Use a simple monorepo layout with separate backend and frontend applications.

Expected top-level structure:

- `backend/`
- `frontend/`
- `docs/`

General rules:

- Keep business logic in backend service layers, not inside route handlers.
- Keep API handlers thin and readable.
- Prefer REST APIs unless explicitly asked to do otherwise.
- Validate important inputs server-side even if the frontend also validates them.
- Prefer simple, explicit code over abstraction-heavy patterns.
- Use clear module boundaries and predictable file names.
- Do not introduce unnecessary architectural complexity early.

Avoid unless explicitly requested:

- Kubernetes
- microservices
- GraphQL
- overly complex frontend state libraries
- premature optimization
- enterprise-only patterns that significantly reduce beginner readability

---

## Product context
Expected users include, at minimum:

- HR administrators
- executives or senior leadership
- people managers
- other authorized management roles

The permissions model must reflect role-based access to sensitive employee information.

This project may eventually be adapted into a SaaS product, but that is not required for v1. Do not add major multi-tenant complexity unless requested. It is acceptable to keep future SaaS expansion in mind when making naming and layering decisions.

---

## Authentication and authorization guidance
Authentication is highly desired.

Initial auth direction:

- start with locally managed users
- design the auth layer so LDAP can be added later without major rework
- future SSO may be added later

Rules:

- treat authentication and authorization as separate concerns
- prefer a clear role-based authorization model
- default to least privilege
- do not assume broad data visibility unless documentation explicitly says so

---

## Security and privacy rules
Because this application may contain highly sensitive HR data, use conservative defaults.

Required practices:

- never hardcode secrets
- use environment variables for secrets and configuration
- do not commit real employee data
- use only fake or clearly synthetic seed/test/demo data
- avoid logging sensitive review content, PIP content, promotion rationale, or manager notes unless explicitly required
- minimize exposure of stack traces and internal implementation details in user-facing error responses
- prefer secure defaults for session handling, auth flows, and data access
- maintain auditability where practical
- keep access to sensitive records narrowly scoped

If a proposed change may affect confidentiality, integrity, auditability, or authorization boundaries, call that out clearly.

---

## Database and migrations
Use PostgreSQL as the default database.

Rules:

- use a migration tool for schema changes
- do not change schema without updating migrations
- keep schema readable and well named
- avoid stuffing too much business logic into the database early
- seed only fake data for development

---

## Containers and local development
The project must run locally using Docker Compose.

Preferred baseline local setup:

- backend service
- frontend service
- postgres service

Goals for local setup:

- predictable
- beginner-friendly
- copy-pasteable startup instructions
- easy to reset and rebuild

README instructions should remain accurate.

---

## Code quality expectations
When making changes:

- keep code readable and explicit
- prefer small, reviewable changes
- avoid large unrelated refactors
- keep naming consistent
- add comments where they genuinely improve understanding
- do not add cleverness at the expense of maintainability

Use formatting and linting tools if configured.

---

## Testing expectations
For meaningful changes:

- add or update relevant tests
- run relevant backend tests if backend changes were made
- run relevant frontend tests if frontend changes were made
- run linting/formatting checks if configured
- make a best effort to verify the app starts successfully

If you could not run a check, say so explicitly.

Do not claim code is working unless it was actually verified.

---

## Documentation expectations
Keep documentation aligned with implementation.

Rules:

- update `README.md` when setup or run instructions change
- update docs in `docs/` when requirements, auth, roles, security assumptions, or workflows change
- do not overload `AGENTS.md` with full product requirements
- keep product requirements in dedicated documents under `docs/`

Important docs include:

- `docs/requirements.md`
- `docs/roles-and-permissions.md`
- `docs/security-and-privacy.md`
- `docs/roadmap.md`

---

## Change management expectations
Prefer staged delivery.

Default implementation order:

1. scaffold backend, frontend, and docker-compose
2. add health checks and a basic landing page
3. add database models and migrations
4. add local authentication and role model
5. add initial employee evaluation workflow
6. add 9-box visualization and reporting
7. prepare architecture for LDAP integration

For each major step:

- explain what will be changed
- keep the change focused
- update docs if behavior or setup changes
- note assumptions when requirements are incomplete

---

## Working style for Codex
Before implementing a major feature:

1. read `AGENTS.md`
2. read the relevant docs under `docs/`
3. summarize assumptions if requirements are still ambiguous
4. implement only the requested slice
5. keep output aligned with this file

If requirements are missing, prefer a minimal, conservative implementation that preserves future flexibility without adding unnecessary complexity.