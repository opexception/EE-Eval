# Roadmap

## Goal
Build EE-Eval in small, reviewable stages while preserving clarity, security, and maintainability.

---

## Phase 0 - Repository and project skeleton
Deliverables:
- monorepo structure
- `backend/`
- `frontend/`
- `docs/`
- Docker Compose setup
- environment examples
- basic README
- backend health endpoint
- frontend landing page

Exit criteria:
- app starts locally with Docker Compose
- backend and frontend are reachable
- README instructions work

---

## Phase 1 - Database and backend foundation
Deliverables:
- PostgreSQL integration
- migration tooling
- basic backend config structure
- initial models or placeholders for users and roles
- backend test baseline

Exit criteria:
- database starts cleanly
- migrations apply successfully
- health checks include DB readiness where appropriate

---

## Phase 2 - Authentication and role model
Deliverables:
- local account model
- password handling
- login/logout flow
- initial role-based authorization model
- protected backend routes
- auth-aware frontend shell

Exit criteria:
- users can authenticate locally
- role-restricted routes are enforced server-side
- basic auth documentation exists

---

## Phase 3 - Core evaluation workflow
Deliverables:
- employee record model
- evaluation cycle model
- evaluation form model
- basic create/edit/view workflow
- manager-visible scoped records

Exit criteria:
- a manager can complete a basic evaluation flow for an authorized employee
- unauthorized access is blocked
- tests cover core workflow paths

---

## Phase 4 - 9-box support
Deliverables:
- rating dimensions or inputs
- 9-box placement logic or storage model
- 9-box matrix view
- drill-down to employee detail

Exit criteria:
- authorized users can view a 9-box representation
- placement logic is documented and testable

---

## Phase 5 - Sensitive workflow features
Deliverables:
- promotion recommendation fields
- manager rationale fields
- optional PIP-related references or notes, depending on scope decisions
- confidentiality handling as required
- initial audit trail for changes

Exit criteria:
- sensitive fields are permission-aware
- important changes are attributable

---

## Phase 6 - Reporting and exports
Deliverables:
- summary dashboards
- org/team views
- selected exports such as CSV and/or PDF if required

Exit criteria:
- reports match confirmed v1 needs
- export permissions are enforced

---

## Phase 7 - LDAP-ready architecture
Deliverables:
- auth interfaces or abstractions refined as needed
- documentation for adding LDAP later
- cleanup of auth boundaries to reduce future rework

Exit criteria:
- local auth still works
- design for LDAP expansion is documented