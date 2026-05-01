# ADR-002: SQLite for development, PostgreSQL for production

**Status:** Accepted  
**Date:** 2025-01-01  
**Author:** Alan Maizon / Copilot

## Context

Boombox needs persistent storage for income, expense, and mileage records.
The system must be easy to inspect locally and production-grade at scale.

## Decision

- **Development:** SQLite (`boombox.db`) via `DATABASE_URL=sqlite:///./boombox.db`
- **Production:** PostgreSQL via Cloud SQL, injected as `DATABASE_URL`

`storage.py` uses SQLAlchemy Core (not ORM) with the same schema for both.
`docker-compose.yml` uses SQLite with a volume mount.

## Rationale

- SQLite requires no additional services for local development
- The SQLAlchemy abstraction makes production migration trivial (change URL)
- SQLAlchemy Core (not ORM) keeps the persistence layer explicit and testable

## Consequences

- Tests use a per-test temp SQLite file (see `conftest.py`)
- Production requires a Cloud SQL instance and a `DATABASE_URL` secret in
  Cloud Run
