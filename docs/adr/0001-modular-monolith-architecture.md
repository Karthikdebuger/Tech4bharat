# ADR 0001: Modular Monolith Architecture

## Status
Accepted

## Context
Gold Trust AI must be operable on a single laptop in a jewellery shop without external internet connectivity, while supporting clean separation of concerns, high maintainability, and strict testability. Microservices would add network overhead, distributed transaction complexity, and fragile runtime dependencies.

## Decision
We implement a Modular Monolith inside a single codebase with strictly enforced boundaries:
- `core/`: Pure primitives (configuration, security, canonical JSON, hashing, clock, IDs). No domain knowledge.
- `domain/`: Pure domain library (units, valuation, rule engine, state machine, receipt canonicalization, ledger planning). Zero I/O, zero network, zero ORM.
- `models/`: SQLAlchemy 2.0 ORM definitions and Alembic database migrations.
- `repos/`: Tenant-scoped database repositories ensuring all queries enforce tenant isolation.
- `services/`: Business workflow orchestration.
- `api/`: FastAPI HTTP routers, Pydantic v2 schemas, and dependency injection.
- `worker/`: Background job processors using transactional database job queues.

Layer boundaries are verified automatically in CI via `import-linter`.

## Consequences
- Testing pure domain logic requires zero database or network dependencies.
- Simpler single-node deployments and local operations.
- Clean architectural boundaries prevent codebase rot.
