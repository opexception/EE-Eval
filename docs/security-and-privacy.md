# Security and Privacy

## Purpose
EE-Eval stores and processes highly sensitive HR information. This document defines the baseline security and privacy posture for the application.

This is a working security requirements document, not a completed security certification artifact.

---

## Data sensitivity
EE-Eval may contain data such as:

- historical performance data
- promotion recommendations
- PIP-related notes or documentation
- manager notes and rationale
- organizational review and calibration data

This data should be treated as highly sensitive.

---

## Core security principles
- least privilege by default
- deny by default where practical
- secure-by-default configuration
- strong separation of authentication and authorization
- minimal data exposure
- explicit handling of sensitive operations
- maintain auditability for important actions
- avoid collecting or exposing more information than needed

---

## Baseline application requirements

### Secrets and configuration
- never hardcode secrets in code or committed files
- use environment variables or secret injection mechanisms
- provide `.env.example` files with placeholders only
- do not commit production credentials

### Development and test data
- never use real employee data in development, testing, demos, or seed data
- use synthetic data only
- avoid realistic identifiers that could be confused with actual personnel data

### Logging
- do not log sensitive review narratives, manager notes, PIP content, promotion rationale, or similar confidential text unless there is an explicit approved reason
- prefer structured operational logging with minimal sensitive context
- avoid logging secrets, tokens, password material, or raw authorization headers

### Error handling
- user-facing errors should be clear but should not leak stack traces or internal implementation details
- detailed exceptions should be handled in a way appropriate for development versus production environments

### Access control
- all access control decisions must be enforced server-side
- frontend visibility controls are not sufficient by themselves
- users should not receive data they are not authorized to access
- field-level restrictions may be required for especially sensitive data

### Auditability
- important data changes should be attributable to a user and timestamp
- security-sensitive or workflow-significant actions should be auditable
- future decisions are needed on whether read access auditing is required

---

## Authentication direction
Initial expectation:
- locally managed accounts for v1

Future expectation:
- LDAP integration later
- possible SSO later
- possible MFA later

Security note:
Authentication design should avoid coupling the app too tightly to only one identity source.

---

## Authorization direction
The authorization model should:
- be role-based
- support org-scope limits
- distinguish between broad administrators and limited managers
- support future refinement for sensitive field visibility

---

## Current first-pass auth implementation
The current local-authentication slice includes:

- locally managed user accounts stored in PostgreSQL
- Argon2 password hashing for stored local passwords
- signed bearer access tokens using an environment-provided secret
- a protected current-user endpoint resolved server-side from the token
- role-check dependencies in the backend for future protected routes
- temporary local-account lockout after repeated failed login attempts
- development-only fake user seeding with synthetic names and demo-safe credentials

Current frontend behavior:

- the access token is kept in memory only for the current page session
- refreshing the browser signs the user out
- no token is written to local storage in this first pass

---

## Database and storage considerations
- use PostgreSQL
- use migrations for schema evolution
- design tables with clear ownership and history in mind
- avoid storing data that is not required
- decide explicitly how attachments, if any, will be stored and protected

Open questions:
- will attachments be allowed in v1?
- if yes, where will they be stored?
- what retention rules apply?

---

## API and backend considerations
- validate all important inputs server-side
- avoid overly permissive CORS settings
- require authentication for non-public endpoints
- keep health endpoints minimal and safe
- sanitize and validate identifiers and request bodies

---

## Frontend considerations
- do not rely on the frontend for security decisions
- avoid exposing sensitive values unnecessarily in client state
- avoid persisting sensitive data in browser storage unless there is a strong reason and clear design

---

## Container and deployment considerations
For local development:
- use Docker Compose
- keep configuration explicit and understandable
- separate development defaults from future production expectations

For future deployment planning:
- run behind TLS
- isolate database access
- control secret distribution
- define backup and restore processes
- define audit log handling
- define retention and deletion policies

---

## Recommended v1 security baseline
At a minimum, v1 should include:

- authenticated access
- role-based authorization
- protected backend endpoints
- migration-managed database schema
- synthetic seed data only
- environment-based secrets
- minimal sensitive logging
- user-attributed change history for important records

---

## Open security and privacy questions
#Q1. Are there data retention requirements for evaluation records?
Answer:
- 10 years

#Q2. Are there deletion or legal hold requirements?
Answer:
- yes. Indefinitely if on legal hold.

#Q3. Do especially sensitive records need extra confidentiality controls?
Answer:
- yes. High level management needs special attention.

#Q4. Is auditing read access required, or only changes?
Answer:
- 

#Q5. Will attachments be allowed in v1?
Answer:
- yes.

#Q6. Are exports restricted for certain roles or data types?
Answer:
- yes. private/sensitive comments should not be exported. 

#Q7. Will MFA be required later?
Answer:
- Yes.

#Q8. Are there internal policy requirements for password rules and lockouts?
Answer:
- 16 charaters
- 1 uppercase, 1 lowercase, 1 number, one special.
- No repeat for 20 previous passwords
- Password change required every 12 months.
- Lockout after 5 failed attempts.

#Q9. Are there compliance expectations that should shape design early?
Answer:
- The organization adheres to GDPR and NIST SP-800-171 compliance.

#Q10. Should some records require additional approval before visibility expands?
Answer:
- yes.


---

## Guidance for implementation
When requirements are incomplete, choose the safer and more conservative default.

Prefer:
- smaller access scope
- less sensitive logging
- less retained data
- more explicit permission checks
- simpler, auditable behavior
