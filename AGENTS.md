# EE-Eval Agent Instructions

## Project purpose
EE-Eval is an internal web application for HR and management to support employee evaluation workflows using a 9-box framework and related performance-review processes.

The application should prioritize:
- clarity
- fairness
- auditability
- privacy
- maintainability
- simple, readable implementation

## Primary tech stack
Use these defaults unless the user explicitly instructs otherwise:
- Backend: Python + FastAPI
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL
- Containerization: Docker + Docker Compose
- Backend testing: pytest
- Frontend testing: Vitest + React Testing Library

## General coding principles
- Favor simple, readable code over clever code.
- Keep functions, modules, and components small and understandable.
- Prefer explicit names over abbreviations.
- Make incremental, low-risk changes.
- Do not introduce unnecessary frameworks or abstractions.
- Do not rewrite working code without a clear reason.

## Architecture guidance
- Keep backend and frontend in separate top-level directories: `backend/` and `frontend/`.
- Keep business rules in backend services, not frontend components.
- Keep API route handlers thin.
- Keep database access organized and separate from request handlers where practical.
- Use REST APIs unless explicitly asked otherwise.
- Validate important inputs server-side.

## Product context
This is an internal HR and management tool.
Expected users may include:
- HR administrators
- executives or senior leadership
- people managers
- other authorized management roles

The permissions model must reflect role-based access to sensitive employee information.

## Authentication and authorization
- Build with support for locally managed users first.
- Design the auth layer so LDAP integration can be added later without major rework.
- Future SSO support may be added later; avoid decisions that would make that difficult.
- Authentication and authorization are separate concerns; implement both.

## Security and privacy
This project handles highly sensitive employee data, potentially including:
- historical performance data
- performance improvement plan documentation
- promotion recommendations
- manager notes and rationale

Therefore:
- do not hardcode secrets
- use environment variables for credentials and configuration
- do not use real employee data in development or tests
- avoid logging sensitive performance content unless explicitly required
- minimize exposure of stack traces and internal errors
- apply least-privilege defaults
- maintain auditability for sensitive actions where practical
- flag privacy or security concerns in responses when relevant

## Database and migrations
- Use PostgreSQL.
- Use a migration tool appropriate for the backend stack.
- Do not change schema without updating migrations.
- Seed data must be clearly fake and safe for development.

## Containers and local development
- The project must run locally with Docker Compose.
- Prefer one service for backend, one for frontend, and one for postgres.
- Keep local setup beginner-friendly and predictable.
- Document copy-pasteable startup commands in README.
- Avoid requiring local dependencies when Docker can provide them.

## Testing and validation
When making code changes:
- run relevant tests
- run linting/formatting if configured
- make a best effort to verify the app starts successfully
- clearly state when checks could not be run

## Documentation expectations
- Keep README accurate.
- Update docs when behavior, setup, auth, env vars, or workflows change.
- Use markdown docs under `docs/` for product requirements, permissions, security, and roadmap details.
- Do not overload this file with full product requirements.

## Change management
- Before large changes, propose a short plan.
- For multi-step work, implement in small verifiable increments.
- Keep changes focused and cohesive.
- Do not mix unrelated refactors with feature work.

## What to avoid unless explicitly requested
- Kubernetes
- microservices
- GraphQL
- overly complex frontend state libraries
- premature optimization
- enterprise-only patterns that significantly reduce beginner readability

## Preferred first milestones
1. Scaffold backend, frontend, and docker-compose
2. Add health checks and basic landing page
3. Add database models and migrations
4. Add local authentication and role model
5. Add initial employee evaluation workflow
6. Add 9-box visualization/reporting
7. Prepare architecture for LDAP integration
