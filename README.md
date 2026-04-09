# EE-Eval

EE-Eval is an internal web application for sensitive employee evaluation workflows, including 9-box-related processes and year-round performance tracking.

The repository currently includes:

- monorepo project skeleton
- FastAPI backend
- React + TypeScript + Vite frontend
- PostgreSQL service in Docker Compose
- backend configuration and database foundation
- Alembic migration tooling
- backend health and readiness endpoints
- frontend landing page

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

4. Open the frontend landing page.

```text
http://localhost:5173
```

5. Check the backend liveness endpoint.

```text
http://localhost:8000/api/health
```

6. Check the backend readiness endpoint.

```text
http://localhost:8000/api/health/ready
```

7. Stop the stack when you are done.

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
- PostgreSQL: `localhost:5432`

## Environment files

- Root `.env.example` contains Docker Compose defaults for ports and local service settings.
- [`backend/.env.example`](./backend/.env.example) contains backend application placeholders.
- [`frontend/.env.example`](./frontend/.env.example) contains frontend application placeholders.

Only placeholder values are committed. Do not commit real secrets or real employee data.

## Current scope

This scaffold intentionally keeps the implementation simple:

- The backend now includes typed configuration, SQLAlchemy session management, and Alembic migration tooling.
- The initial migration creates a `demo_records` table as a scaffold-only placeholder so database and migration wiring can be verified without introducing real HR data models yet.
- Authentication, authorization, and business workflows are still deferred to later roadmap phases.
- The liveness endpoint stays minimal, while the readiness endpoint only reports database availability.

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](./LICENSE) for the full license text.

## Contributions

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution terms and project expectations.

## Contact

For questions about licensing, contributions, or commercial arrangements:

- Robert Maracle
- robert.maracle@proton.me
