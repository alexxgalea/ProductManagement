# Design Doc: Restaurant Inventory ↔ External POS Integration

**Status:** Draft
**Last updated:** 2026-06-14
**Owner:** Product Management

---

## 1. Overview

This system manages restaurant inventory (ingredients, recipes, stock levels). It does
**not** handle customer-facing ordering. Orders are placed in an **external POS system**
(e.g. Square, Toast, Clover) which notifies us in real time via **webhooks**. On each
order, we map the POS line items to our internal recipes and **deduct the consumed
ingredients** from inventory.

The two hard problems are:

1. **Resilience** — peak-hour traffic can produce a flood of webhooks; the inventory
   deduction logic must not be overwhelmed and must not lose events.
2. **Idempotency** — if the POS drops a connection and retries, we must never deduct the
   same order's ingredients twice.

### Design principle: persist-then-enqueue

The web request does almost nothing. It verifies the signature, writes **one** row, enqueues
**one** background task, and returns `202 Accepted`. All mapping and deduction happen
asynchronously in Celery workers. This is what lets the HTTP endpoint survive a flood — it
never blocks on inventory business logic. The durable record of truth is **Postgres** (the
event table + the inventory ledger), not the message broker.

---

## 2. High-level flow

```
External POS ──HTTP POST (HMAC-signed)──▶ Django Webhook Endpoint (DRF)
                                              │  fast path:
                                              │  verify → persist raw → enqueue → 202
                                              ▼
                                       POSWebhookEvent   (durable buffer, unique event id)
                                              │
                                              ▼ .delay()
                                    Celery broker (RabbitMQ recommended / Redis)
                                              │
                                              ▼ worker (acks_late, idempotent)
                            map items → atomic inventory deduction → ledger
```

---

## 3. Component 1 — POS Webhook Receiver

A dedicated DRF endpoint, CSRF-exempt (machine-to-machine), performing its own HMAC
authentication over the **raw** request body.

### 3.1 Security requirements

| Control | Rationale |
|---|---|
| HMAC-SHA256 over `timestamp + "." + raw_body`, per-location secret | Authenticates the sender; per-location secret limits blast radius of a leaked key |
| `hmac.compare_digest` for comparison | Constant-time; no timing side-channel |
| Sign **raw bytes**, never re-serialized JSON | Key ordering / whitespace would otherwise break verification |
| Timestamp + replay window (reject > 5 min old) | Prevents replay of a captured request |
| Return `202` fast; only auth failures return `401` | Any non-2xx from *our* logic would make the POS retry an event we already stored |
| TLS-only, optional IP allowlist / WAF rate-limit | Defense in depth |

### 3.2 Reference implementation

```python
# pos/views.py
import hmac, hashlib, time, json
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class POSWebhookView(APIView):
    authentication_classes = []          # we do our own HMAC auth
    permission_classes = []

    def post(self, request, provider_slug):
        location = get_object_or_404(
            POSLocation, provider__slug=provider_slug, webhook_active=True)

        raw = request.body                       # bytes, BEFORE DRF parsing
        sig = request.headers.get("X-POS-Signature", "")
        ts  = request.headers.get("X-POS-Timestamp", "")

        # 1. Replay window
        if not ts or abs(time.time() - int(ts)) > 300:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # 2. Constant-time HMAC check
        expected = hmac.new(
            location.signing_secret.encode(),
            ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        payload = json.loads(raw)
        external_event_id = payload["event_id"]   # provider-guaranteed unique

        # 3. Idempotent persist (see §6) — unique constraint dedupes retries
        event, created = POSWebhookEvent.objects.get_or_create(
            location=location,
            external_event_id=external_event_id,
            defaults={"raw_payload": payload, "status": "RECEIVED"},
        )
        if created:
            process_pos_event.delay(event.id)     # enqueue, don't process inline

        # Always 2xx for known/duplicate events so the POS stops retrying
        return Response(status=status.HTTP_202_ACCEPTED)
```

---

## 4. Component 2 — Item mapping (external IDs → internal recipes)

POS "items" rarely map 1:1 to internal recipes. There are **variants** (size) and
**modifiers** (extra cheese, no onion) that each change ingredient consumption. The mapping
is an explicit, auditable table — not a code lookup.

### 4.1 Data model

```python
# core/models.py
class POSProvider(models.Model):           # Square, Toast, Clover...
    slug = models.SlugField(unique=True)

class POSLocation(models.Model):           # one physical restaurant / tenant
    provider        = models.ForeignKey(POSProvider, on_delete=models.PROTECT)
    name            = models.CharField(max_length=120)
    signing_secret  = models.CharField(max_length=128)   # encrypt at rest
    webhook_active  = models.BooleanField(default=True)

class Ingredient(models.Model):            # tracked stock
    name             = models.CharField(max_length=120)
    unit             = models.CharField(max_length=20)    # g, ml, each
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=3)

class MenuItem(models.Model):              # internal sellable item
    name = models.CharField(max_length=120)

class Recipe(models.Model):
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE)

class RecipeIngredient(models.Model):
    recipe     = models.ForeignKey(Recipe, related_name="lines", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity   = models.DecimalField(max_digits=12, decimal_places=3)

# The mapping table — the heart of the integration
class POSItemMapping(models.Model):
    location            = models.ForeignKey(POSLocation, on_delete=models.CASCADE)
    external_item_id    = models.CharField(max_length=128)
    external_variant_id = models.CharField(max_length=128, blank=True, default="")
    menu_item           = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    is_active           = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["location", "external_item_id", "external_variant_id"],
                name="uq_pos_item_mapping"),
        ]

# Modifiers that add/remove ingredients (extra shot, no cheese)
class POSModifierMapping(models.Model):
    location             = models.ForeignKey(POSLocation, on_delete=models.CASCADE)
    external_modifier_id = models.CharField(max_length=128)
    ingredient           = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity_delta       = models.DecimalField(max_digits=12, decimal_places=3)  # +/-

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["location", "external_modifier_id"], name="uq_pos_modifier"),
        ]
```

### 4.2 Mapping rules

- **Scoped per `location`.** The same `external_item_id` means different things at different
  restaurants/providers.
- **Variant + modifier dimensions** are modeled explicitly, so "Large Latte, extra shot"
  deducts correctly.
- **Unmapped items are never silently dropped.** When the worker can't resolve a mapping it
  writes a `POSUnmappedItem` row, fires an alert, and marks the event `NEEDS_MAPPING` (not
  `FAILED`). An operator creates the mapping, then the event is reprocessed. Silent drops
  produce inventory drift discovered weeks later.
- `on_delete=PROTECT` on ingredients/menu items prevents deleting something still referenced
  by a mapping or ledger entry.

---

## 5. Component 3 — Asynchronous processing & resilience

The webhook endpoint has already decoupled ingestion from processing. Celery absorbs the
peak-hour flood; the `POSWebhookEvent` table is the durable backstop if the broker is lost.

### 5.1 Broker choice

**Recommendation: RabbitMQ as the broker, Redis as result backend / cache.**

RabbitMQ provides true message acknowledgements, publisher confirms, and dead-letter
exchanges — appropriate when losing or double-running a message has inventory consequences.
Redis-as-broker is acceptable for operational simplicity **because the real durability
guarantee lives in Postgres** (the event table + ledger), not in the broker. Either way, the
broker is treated as a transient queue, not the system of record.

### 5.2 Celery configuration

```python
# celery_app.py
from celery import Celery

app = Celery("inventory")
app.conf.update(
    task_acks_late=True,             # ack only after success → survive worker crash
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,    # spread a burst across workers, don't hoard
    task_default_queue="ingest",
)
```

```python
# pos/tasks.py
from django.db import OperationalError

@app.task(bind=True, acks_late=True, max_retries=5,
          autoretry_for=(OperationalError,), retry_backoff=True, retry_jitter=True)
def process_pos_event(self, event_id):
    deduct_inventory_for_event(event_id)   # idempotent, atomic — see §6
```

### 5.3 Resilience controls

- **Separate queues** (`ingest` vs `deduct`) so a slow path can't starve the other; scale
  workers independently.
- **`acks_late=True` + idempotent task** is the combination that makes retries safe: a worker
  that dies mid-deduction gets the message redelivered, and idempotency (§6) ensures the
  redelivery does not double-deduct.
- **`prefetch_multiplier=1`** spreads a burst across workers instead of buffering in one.
- **Exponential backoff + jitter** for transient DB/lock contention.
- **Dead-letter queue** for poison messages after `max_retries` → event marked `FAILED`,
  alert fired, queued for human review.
- **Backpressure is automatic:** the HTTP layer never blocks, queue depth grows, workers
  drain it. Monitor queue depth (Flower / Prometheus) and autoscale workers on it.

---

## 6. Component 4 — Idempotency (never deduct twice)

Three independent guards stop a duplicate at whichever layer it reaches.

### Guard 1 — Ingestion dedupe (DB unique constraint)

`get_or_create(location, external_event_id=...)` in the webhook. A POS retry of the same
order hits the unique constraint, returns `created=False`, and **no task is enqueued**. This
catches the common case: POS drops connection and resends.

### Guard 2 — Event state machine with row lock

The worker locks the event row and refuses to process one that is already terminal.

```python
from django.db import transaction

def deduct_inventory_for_event(event_id):
    with transaction.atomic():
        event = POSWebhookEvent.objects.select_for_update().get(id=event_id)
        if event.status in ("PROCESSED", "NEEDS_MAPPING"):
            return                       # already handled — idempotent no-op
        # ... resolve mappings, deduct, write ledger ...
        event.status = "PROCESSED"
        event.save(update_fields=["status"])
```

`select_for_update()` serializes two concurrent workers that both received the same event;
the second sees `PROCESSED` and exits.

### Guard 3 — Ledger with unique constraint (the database-enforced invariant)

Every deduction writes an immutable `InventoryTransaction` keyed by the event. A unique
constraint makes a second deduction physically impossible even if Guards 1 & 2 were bypassed.

```python
class InventoryTransaction(models.Model):
    event          = models.ForeignKey(POSWebhookEvent, on_delete=models.PROTECT)
    ingredient     = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity_delta = models.DecimalField(max_digits=12, decimal_places=3)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "ingredient"], name="uq_ledger_event_ingredient"),
        ]
```

Deduction updates stock with an atomic `F()` expression and inserts the ledger row in the
**same transaction**:

```python
from django.db.models import F

Ingredient.objects.filter(pk=ing.pk).update(
    quantity_on_hand=F("quantity_on_hand") - amount)
InventoryTransaction.objects.create(event=event, ingredient=ing, quantity_delta=-amount)
```

If the task is retried after the transaction already committed, the
`uq_ledger_event_ingredient` insert raises `IntegrityError`, which is caught and treated as
"already done." **Inventory levels are reconciled against the ledger, never adjusted
blindly**, so the ledger is the source of truth and double-counting is impossible by
construction.

**Why three layers:** Guard 1 handles the normal retry cheaply; Guard 2 handles concurrent
in-flight duplicates; Guard 3 is the database-enforced invariant that holds even under code
bugs or out-of-order redelivery. `acks_late` is only safe *because* Guard 3 exists.

---

## 7. Event lifecycle (status state machine)

```
RECEIVED ──▶ PROCESSING ──▶ PROCESSED
                  │
                  ├──▶ NEEDS_MAPPING ──(operator maps + reprocess)──▶ PROCESSED
                  │
                  └──▶ FAILED ──(after max_retries; DLQ + alert + human review)
```

---

## 8. Summary

| Concern | Mechanism |
|---|---|
| Secure receipt | Per-location HMAC-SHA256 over `ts+raw`, `compare_digest`, replay window, fast `202` |
| Mapping | `POSItemMapping` (item+variant) + `POSModifierMapping`, scoped per location, unmapped → review queue |
| Async load | Persist-then-enqueue; RabbitMQ broker (recommended) / Redis; separate queues; `acks_late`; backoff; DLQ |
| Idempotency | Unique event id (ingest) + locked state machine (worker) + unique ledger constraint (DB invariant) |

---

## 9. Open questions / future work

- **Order edits & voids:** how does the POS represent a modified or cancelled order, and do we
  need compensating ledger entries (positive `quantity_delta`) to restock?
- **Backfill / replay:** a tool to replay `POSWebhookEvent` rows after fixing a mapping bug.
- **Negative stock:** allow it (and flag) vs. block — likely allow, since the physical sale
  already happened.
- **Multi-tenancy isolation:** row-level scoping vs. separate schemas per restaurant group.
- **Secret storage:** move `signing_secret` to a secrets manager / encrypted field.
- **Observability:** metrics for queue depth, deduction latency, unmapped-item rate.
```

