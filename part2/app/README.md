# 🏠 HBnB Part 2 — Application Core

In-memory persistence layer with REST API facade.

## Structure

| Directory | Description |
|-----------|-------------|
| `api/` | REST API endpoints (Flask-RESTX) |
| `models/` | Business logic entities |
| `persistence/` | In-memory repository |
| `services/` | Business logic facade |
| `tests/` | Unit tests |

## Key Features

- In-memory storage (no database)
- RESTful API with namespaces
- Factory pattern (`create_app()`)
- Unit test coverage

---

*Part of [HBnB Part 2](../../README.md)*
