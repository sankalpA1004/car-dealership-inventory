# AI-Assisted Development Log — Car Dealership Inventory System

## 1. Architecture and Technology Selection

**Prompt 1 — Define a maintainable architecture**

I want to build a Car Dealership Inventory System with a clear separation of concerns. I am considering FastAPI for the REST API, SQLAlchemy for persistence, SQLite for local development, and React with Tailwind CSS for the frontend. Propose a minimal architecture that is easy to test and maintain. Explain the responsibilities of each layer, how data flows from the UI to the database, and which abstractions are worth introducing at this project's scale. Avoid unnecessary microservices and overengineering.

## 2. Database Design and Data Integrity

**Prompt 2 — Model the inventory domain**

Design a relational data model for a vehicle inventory system. Identify the essential vehicle attributes, data types, uniqueness constraints, and validation rules. Consider how price, model year, and available quantity should be represented. Explain which integrity rules belong in the database and which belong in application-level validation. Keep the model extensible without introducing speculative features.

**Prompt 3 — Design API schemas independently of database models**

Help me define Pydantic schemas for creating, updating, and returning vehicle records. The API should accept only intended client-editable fields and should not expose internal database details unnecessarily. Explain how partial updates should behave, how invalid values should be rejected, and how the schemas should remain consistent with the SQLAlchemy models.

## 3. REST API Design

**Prompt 4 — Establish consistent endpoint semantics**

Review the REST API design for vehicle creation, listing, retrieval, updating, and deletion. Recommend appropriate HTTP methods, status codes, validation behavior, and error response conventions. Account for nonexistent resources and malformed requests. Keep the API predictable for frontend developers and avoid returning successful responses when an operation has failed.

**Prompt 5 — Implement vehicle CRUD operations**

Help implement the vehicle CRUD endpoints using FastAPI and SQLAlchemy. Keep request validation, database persistence, and HTTP response handling clearly separated. Ensure that failed database operations do not leave inconsistent state. Explain the important implementation decisions and provide focused tests for successful operations and common failure cases.

**Prompt 6 — Add efficient search and filtering**

Design a search interface for the vehicle listing endpoint that supports filtering by relevant attributes such as make, model, year, and stock availability. Multiple filters should combine predictably, and user-provided values must be handled safely through ORM queries. Consider empty results, invalid filter values, and pagination if justified by the current requirements.

## 4. Authentication and Authorization

**Prompt 7 — Implement secure authentication**

Help implement authentication in FastAPI using password hashing and JWT access tokens. Passwords must never be stored in plaintext, signing secrets must come from environment variables, and token validation should be centralized in a reusable dependency. Explain the authentication flow, relevant token claims, expiration handling, and expected behavior for missing or invalid credentials.

**Prompt 8 — Enforce role-based access control**

The system has regular users and administrators. Define a reusable authorization mechanism so that administrative operations cannot be accessed by ordinary users. Enforce permissions on the backend, not just through frontend visibility. Apply the policy consistently to protected endpoints and write negative tests demonstrating that unauthorized requests are rejected.

**Prompt 9 — Review authentication failure modes**

Review the login and authorization flows for common failure modes, including incorrect credentials, malformed tokens, expired tokens, missing authorization headers, and insufficient privileges. Explain the expected HTTP response for each case and identify tests that distinguish authentication failures from authorization failures. Avoid exposing sensitive implementation details in error messages.

## 5. Inventory Business Logic

**Prompt 10 — Make purchase operations safe**

Implement the vehicle purchase operation with explicit business rules. Reject zero or negative quantities and purchases that exceed available stock. Ensure that stock cannot become negative and that the database update remains consistent if an operation fails. Consider transaction boundaries and concurrent requests, and explain which protections are appropriate for SQLite and this project's expected scale.

**Prompt 11 — Restrict and validate restocking**

Design an administrative restock operation that validates the requested quantity and updates inventory safely. Unauthorized users must be denied access, and invalid requests must not modify the database. Add tests for successful restocking, invalid quantities, nonexistent vehicles, and insufficient permissions.

**Prompt 12 — Protect destructive operations**

Review the vehicle deletion workflow. Ensure that deletion is restricted to authorized administrators, that nonexistent records are handled correctly, and that database failures are not reported as successful deletions. Identify any data-integrity implications of deleting vehicles that may have existing inventory or transaction references.

## 6. Test-Driven Development

**Prompt 13 — Apply Red-Green-Refactor to a specific requirement**

Use a test-driven workflow to implement one inventory business rule. Begin by writing a focused test that describes the expected behavior, then run it and confirm that it fails for the intended reason. Implement the smallest change that makes the test pass, rerun the relevant tests, and refactor without changing behavior. Keep each stage independently reviewable so the Git history reflects genuine development progress.

**Prompt 14 — Build isolated API tests**

Help structure pytest tests for the FastAPI application using a separate test database and reusable fixtures. Tests should be deterministic, should not modify development data, and should cover both successful requests and failure conditions. Explain how to override application dependencies for testing and how to ensure test data is cleaned up reliably.

**Prompt 15 — Test security boundaries**

Create a focused test matrix for authentication and role-based permissions. Include unauthenticated requests, authenticated regular users attempting administrative actions, authorized administrators, and invalid credentials. Verify status codes and relevant state changes, not merely that requests return a response. Identify any gaps in the current tests before proposing additional implementation.

**Prompt 16 — Use coverage to guide testing**

Help me interpret the actual pytest and coverage output from this repository. Identify important untested branches in authentication, validation, and inventory operations. Prioritize tests by risk and business impact instead of chasing a coverage percentage alone. Do not invent results or claim that a test passed without execution evidence.

## 7. React Frontend

**Prompt 17 — Structure the frontend around user workflows**

Design a maintainable React interface for browsing and managing dealership inventory. Include authentication, vehicle listing, search and filtering, and forms for permitted inventory operations. Use reusable components where they provide real value, and define clear loading, empty, validation, and error states. Keep the UI aligned with the existing API contract.

**Prompt 18 — Integrate the frontend with the API**

Help organize API calls in a reusable frontend service layer. Connect login, vehicle listing, search, and inventory operations to the FastAPI endpoints. Handle network failures and unsuccessful HTTP responses explicitly. Keep configuration environment-based, avoid hardcoded secrets, and ensure the UI refreshes or updates state after successful mutations.

**Prompt 19 — Improve usability and responsive behavior**

Review the inventory interface for usability, accessibility, and responsive layout. Improve semantic HTML, form labels, keyboard navigation, validation feedback, spacing, and mobile behavior using Tailwind CSS. Preserve existing business logic and API behavior. Explain which changes improve accessibility and which are purely visual.

## 8. Debugging and Security Review

**Prompt 20 — Diagnose errors from evidence**

When the application fails locally, analyze the exact traceback, terminal output, relevant source code, and configuration I provide. Distinguish environment problems from application bugs, identify the most likely root cause, and recommend the smallest safe fix. After the change, specify the command or test that should verify the diagnosis rather than assuming the issue is resolved.

**Prompt 21 — Perform a focused application security review**

Review the current implementation for common web application risks, focusing on password storage, JWT handling, authorization checks, input validation, database operations, secret management, and exception handling. For each credible finding, describe the potential impact, provide a reproducible verification approach, and recommend a proportionate remediation. Clearly distinguish confirmed vulnerabilities from issues that still require testing.

## 9. Documentation and Delivery

**Prompt 22 — Write reproducible setup documentation**

Help prepare a README that allows another developer to run the project from a clean checkout. Document prerequisites, environment configuration, backend setup, frontend setup, test commands, API documentation, key features, screenshots, and known limitations. Verify every command against the actual folder structure and avoid documenting unimplemented features as completed.

**Prompt 23 — Document AI assistance accurately**

Help organize a concise AI usage disclosure describing the assistance used during development, such as architecture discussion, code scaffolding, debugging guidance, test design, and documentation. Distinguish generated suggestions from changes reviewed or tested by the project author. Keep the disclosure specific and accurate rather than using generic claims about productivity.

**Prompt 24 — Conduct a release-readiness review**

Compare the implementation against the assignment requirements. Evaluate API behavior, persistence, authentication, authorization, stock validation, frontend integration, automated tests, documentation, screenshots, and Git history. Produce a checklist that separates verified requirements from unverified ones and identifies the highest-priority remaining work. Base conclusions on repository contents and actual test output, not assumptions.

---

## Development Principles

- Prefer small, reviewable changes over large rewrites.
- Validate behavior through tests and observable API responses.
- Enforce security-sensitive rules on the backend.
- Keep configuration and secrets out of source control.
- Use Red-Green-Refactor where it can be followed genuinely.
- Treat AI-generated suggestions as proposals that require review.
- Record test results and implementation claims only when supported by evidence.
