# Project 07 — Task Manager REST API (Spring Boot)

**Status:** ⬜ Not started · **Needs:** `10-jdbc-sql`, `11-testing`, `12-build-tools`, `15-spring-boot`

## 📌 Project Description

A deployed REST API for managing tasks, with authentication, a real database, tests, and Docker. This is the first Java project meant to be pinned on your GitHub profile as a **standalone repository**, with a link from this folder.

## 📋 Requirements

### Functional Requirements
1. Register and log in; JWT authentication
2. CRUD for tasks, owned by a user (users cannot see each other's tasks)
3. Pagination, sorting, and filtering on the list endpoint
4. Input validation with consistent JSON error responses
5. OpenAPI documentation reachable at a documented URL

### Non-Functional Requirements
- PostgreSQL with schema migrations (Flyway or Liquibase)
- Tests: controller tests, repository tests, at least one integration test with Testcontainers
- `docker compose up` starts the API and database from a fresh clone
- No secrets in the repository (`.env.example` only)
- Deployed somewhere public, with the URL in the README

## ✅ Definition of Done
- [ ] Standalone repo with README: what it does, architecture diagram, how to run, API examples
- [ ] Test coverage reported and linked
- [ ] Live URL or recorded demo
- [ ] "What I learned / what I would improve" section
