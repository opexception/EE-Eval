# Roles and Permissions

## Purpose
This document defines the role model and visibility boundaries for EE-Eval.

Because EE-Eval may contain highly sensitive HR data, permissions should be explicit, conservative, and role-based.

This document begins as a working draft and should be refined as product decisions are made.

---

## Principles
- default to least privilege
- separate authentication from authorization
- separate view permissions from edit permissions where appropriate
- sensitive records should not be broadly visible by default
- access rules should be explainable and auditable
- permission behavior should be enforced server-side

---

## Initial candidate roles

### 1. HR Administrator
Likely responsibilities:
- manage evaluation cycles
- manage users or access assignments if delegated
- review evaluation records across the organization
- oversee calibration or review workflows
- access sensitive supporting content where policy allows

Likely default access:
- broad read access
- broad edit access for administrative workflows
- access to reporting across the organization
- access to audit data if required

Open questions:
- should HR have full unrestricted visibility?
- should some especially sensitive cases require narrower access even from HR?

### 2. Executive / Senior Leadership
Likely responsibilities:
- review organization-wide or division-wide talent distributions
- review 9-box outcomes
- review promotion or performance trends
- participate in calibration processes

Likely default access:
- read access to broader organizational data
- limited edit rights unless explicitly part of a workflow
- reporting and dashboard access

Open questions:
- should executives see all employees, or only within their org tree?
- should they see full narrative detail, or summarized data only?

### 3. People Manager
Likely responsibilities:
- complete evaluations for direct reports
- add supporting rationale
- participate in review or calibration steps
- review prior periods for employees they manage if allowed

Likely default access:
- read and edit access for their direct reports
- possible read-only access for skip-level reporting structure depending on policy
- no broad access outside their area

Open questions:
- should managers see only direct reports?
- should managers see historical evaluations before drafting a new one?
- should managers see PIP-related information?

### 4. Upper Manager / Second-Line Manager
Likely responsibilities:
- review evaluations submitted by subordinate managers
- support calibration within their reporting line
- view summarized team or org data

Likely default access:
- broader read access than line managers
- edit or approval authority depending on workflow design

Open questions:
- should upper managers be able to edit records directly, or only approve/comment?

### 5. System Administrator
Likely responsibilities:
- infrastructure and application administration
- operational support

Likely default access:
- operational access to the system
- should not automatically receive unrestricted access to HR content unless explicitly required

Important note:
Administrative system access should not automatically imply permission to view sensitive HR content in the application itself.

---

## Permission categories

### Authentication permissions
- login
- logout
- password reset or account recovery
- session management

### User administration permissions
- create user
- deactivate user
- assign role
- reset password
- map user to org scope

### Evaluation permissions
- create evaluation
- edit draft evaluation
- submit evaluation
- reopen evaluation
- view prior evaluations
- attach supporting notes or documents

### Sensitive-content permissions
- view manager notes
- edit manager notes
- view promotion recommendations
- edit promotion recommendations
- view PIP-related content
- edit PIP-related content
- mark content as confidential

### Reporting permissions
- view team dashboard
- view org dashboard
- view 9-box matrix
- drill down into employee detail
- export reports

### Audit permissions
- view change history
- view access history
- view system audit logs

---

## Scope rules to define
The following scope boundaries should be explicitly decided:

- self only
- direct reports only
- full reporting chain below user
- assigned business unit or department
- organization-wide
- explicit exception-based access

---

## Important unresolved policy questions
#Q1. Should HR be able to see everything by default?
Answer:
- Yes.

#Q2. Should executives see full employee-level detail or only certain categories?
Answer:
- Only the following details:
- Latest 3 year rolling average performance score
- Current review score
- 9-boxes for the previous 3 years
- Current 9-box position
- Overall/summary comment from manager for this review.

#Q3. Should managers only see direct reports?
Answer:
- Managers should be able to see all reports below them.

#Q4. Should skip-level leadership see detailed records or summaries first?
Answer:
- Summaries.

#Q5. Should view and edit rights be separated for sensitive fields?
Answer:
- Yes

#Q6. Should especially sensitive cases require a confidentiality flag and narrower visibility?
Answer:
- yes

#Q7. Should audit logs include read access, write access, or both?
Answer:
- audit logs should be read-only.

---

## Recommended implementation approach for v1
For v1, keep authorization simple and explicit.

Suggested approach:
- role-based access control first
- org-scope checks second
- field-level restrictions only where clearly necessary
- sensitive actions logged
- all authorization enforced in backend services and API layer

Avoid overly abstract permission engines in v1 unless requirements clearly justify them.