# Restaurant Inventory Platform

Event-driven inventory management for restaurants selling on delivery platforms
(Glovo, Bolt, Wolt). Incoming orders are ingested via signed webhooks, mapped to
internal recipes, and deducted from stock in an immutable transaction ledger.

## Architecture

**Persist-then-enqueue ingestion** — the webhook endpoint does minimal work
(verify HMAC signature → persist one event row → enqueue one Celery task → `202
Accepted`), decoupling ingestion from business logic and surviving traffic bursts.

**Three-layer idempotency** — duplicate deliveries can never double-deduct stock:
1. unique constraint on `(location, external_event_id)` blocks duplicate ingestion;
2. an event state machine with `select_for_update()` row locks prevents concurrent
   re-processing;
3. a unique `(event, ingredient)` constraint enforces the invariant at ledger level.

**Signed webhooks** — HMAC-SHA256 with per-location secrets, a 5-minute replay
window, and constant-time comparison.

**Asynchronous workers** — Celery over RabbitMQ with `acks_late`, exponential
backoff, dead-letter queue, and separate queues for load isolation.

## Apps

| App | Responsibility |
|---|---|
| `core` | ingredients, recipes, menu items, external-ID mappings |
| `inventory` | immutable ledger and stock transactions |
| `procurement` / `sales` / `delivery` / `losses` | stock inflows and outflows per business flow |
| `accounts` | users and per-location access |

## Stack

Django · Celery · RabbitMQ · PostgreSQL · Redis · Docker Compose

## Setup

```bash
cp .env.example .env        # fill in secrets
docker compose up -d        # postgres + broker
pip install -r requirements.txt
python manage.py migrate && python manage.py runserver
```

## License

[MIT](LICENSE) © 2026 Alexandru-Marian Galea
