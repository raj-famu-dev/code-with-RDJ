# 15 · Spring Boot

**Priority: LATER, but it feeds `project-07`.** You noted Spring Boot as a strength, and this repo currently has no evidence of it. This folder is where that gets evidence.

Convention: one `_N_Name.md` per topic plus a small runnable Maven project per topic where code is needed.

| # | Topic | Status |
|---|---|:---:|
| 1 | `_1_IocAndDependencyInjection` (explain beans and the container without the framework first) | ⬜ |
| 2 | `_2_RestControllers` (DTOs, status codes, validation with `@Valid`) | ⬜ |
| 3 | `_3_SpringDataJpa` (entities, relationships, and reproduce the N+1 problem) | ⬜ |
| 4 | `_4_ExceptionHandling` (`@ControllerAdvice`, consistent error responses) | ⬜ |
| 5 | `_5_ProfilesAndConfig` (no secrets in the repo, `.env.example` only) | ⬜ |
| 6 | `_6_SecurityAndJwt` | ⬜ |
| 7 | `_7_TestingSpringApps` (`@WebMvcTest`, `@DataJpaTest`, Testcontainers) | ⬜ |
| 8 | `_8_OpenApiAndActuator` | ⬜ |
| 9 | `_9_DockerizeIt` (Dockerfile and `docker-compose.yml` with a database) | ⬜ |

**Exit test:** `docker compose up` brings the whole system up from a fresh clone.
