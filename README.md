# EE-Eval

EE-Eval is an internal web application for sensitive employee evaluation workflows, including 9-box-related processes and year-round performance tracking.

The repository currently includes:

- monorepo project skeleton
- FastAPI backend
- React + TypeScript + Vite frontend
- PostgreSQL service in Docker Compose
- backend configuration, database foundation, and local authentication
- Alembic migration tooling
- backend health, readiness, login, and current-user endpoints
- frontend login page and authenticated shell

No business features are implemented yet.

Copyright (C) 2026 Robert Maracle

## Repository layout

```text
backend/   FastAPI application and backend tests
frontend/  React + TypeScript + Vite application
docs/      product, security, and roadmap documentation
```

## Prerequisites

- Docker
- Docker Compose
- Python 3

## Backend Local Development

This repository supports a simple local backend workflow using a repo-local virtual environment.

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install backend runtime dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

Install backend development and test dependencies:

```bash
python -m pip install -r backend/requirements-dev.txt
```

Run backend tests:

```bash
pytest backend/tests -q
```

If you prefer Make targets from the repository root:

```bash
make backend-venv
make backend-dev-install
make backend-test
```

`backend/requirements-dev.txt` already includes `backend/requirements.txt`, so for day-to-day development you can usually install just the dev requirements file after the venv exists.

## Quick start

1. Optional: copy the root environment example if you want to change ports or local defaults.

```bash
cp .env.example .env
```

2. Build and start the project.

```bash
docker compose up --build
```

3. Apply the backend migrations.

```bash
docker compose exec backend alembic upgrade head
```

4. Seed the fake demo users and fake review data for development.

```bash
docker compose exec backend python -m app.scripts.seed_demo_users
```

5. Open the frontend login page.

```text
http://localhost:5173
```

6. Sign in with one of the seeded demo users listed below.

7. Check the backend liveness endpoint.

```text
http://localhost:8000/api/health
```

8. Check the backend readiness endpoint.

```text
http://localhost:8000/api/health/ready
```

9. Stop the stack when you are done.

```bash
docker compose down
```

If you want to remove the local PostgreSQL data volume too:

```bash
docker compose down -v
```

## Local services

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Backend liveness endpoint: `http://localhost:8000/api/health`
- Backend readiness endpoint: `http://localhost:8000/api/health/ready`
- Backend login endpoint: `http://localhost:8000/api/auth/login`
- Backend current-user endpoint: `http://localhost:8000/api/auth/me`
- Backend employees endpoint: `http://localhost:8000/api/employees`
- Backend review cycles endpoint: `http://localhost:8000/api/review-cycles`
- Backend evaluations endpoint: `http://localhost:8000/api/evaluations`
- PostgreSQL: `localhost:5432`

## Environment files

- Root `.env.example` contains Docker Compose defaults for ports and local service settings.
- [`backend/.env.example`](./backend/.env.example) contains backend application placeholders.
- [`frontend/.env.example`](./frontend/.env.example) contains frontend application placeholders.

Only placeholder values are committed. Do not commit real secrets or real employee data.

## Auth-related environment variables

The main auth settings are:

- `EE_EVAL_CORS_ORIGINS`: allowed frontend origins for browser access to the backend
- `EE_EVAL_JWT_SECRET`: signing key for backend access tokens
- `EE_EVAL_ACCESS_TOKEN_EXPIRE_MINUTES`: access token lifetime in minutes
- `EE_EVAL_MAX_FAILED_LOGIN_ATTEMPTS`: failed local login attempts before lockout
- `EE_EVAL_LOCKOUT_MINUTES`: temporary lockout length after repeated failed logins
- `EE_EVAL_SEED_DEMO_USERS`: enables the development-only demo seed command
- `EE_EVAL_DEMO_PASSWORD`: shared password assigned to the seeded fake users
- `VITE_API_BASE_URL`: frontend API base URL used by the browser

## Seeded demo credentials

The seed command creates fake users plus fake employees, review cycles, and evaluations.
These records are for local development and demos only.

Shared demo password:

```text
DemoPass123!ChangeMe
```

Seeded users:

| Username | Role |
| --- | --- |
| `employee.taylor` | `employee` |
| `manager.avery` | `people_manager` |
| `upper.lee` | `upper_manager` |
| `executive.morgan` | `executive` |
| `hr.harper` | `hr_admin` |
| `it.rowan` | `system_admin` |

## Current scope

This scaffold intentionally keeps the implementation simple:

- The backend now includes typed configuration, SQLAlchemy session management, Alembic migration tooling, local users, role assignments, employee profiles, review cycles, evaluations, and role-check dependencies.
- Passwords are stored as Argon2 hashes, and local login attempts lock temporarily after repeated failures.
- Employee profiles and review-cycle records use simple, summary-safe fields only in this first pass.
- Each employee currently has one evaluation record per review cycle, which is updated over time instead of versioned.
- Demo users and review data are seeded only in development and use fake names and a documented fake password.
- `DELETE` endpoints archive employees, review cycles, and evaluations instead of hard-deleting database rows.
- The frontend keeps the access token in memory only for this first pass, so refreshing the page signs you out.
- HR administrators can manage employees and review cycles, people managers can manage evaluations for their reporting line, upper managers are read-only for their reporting line, and executives are read-only at the summary level.
- Employee access to evaluation records is intentionally deferred until published/shared visibility rules are designed more fully.
- Business workflows, LDAP integration, password reset, attachments, and broader authorization rules are still deferred to later phases.

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](./LICENSE) for the full license text.

## Contributions

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution terms and project expectations.

## Contact

For questions about licensing, contributions, or commercial arrangements:

- Robert Maracle
- robert.maracle@proton.me
