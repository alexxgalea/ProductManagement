# Learning Roadmap — ProductManagement

**Scop dublu:** construim sistemul real din [architecture.md](architecture.md) **și** îl folosim ca
vehicul de învățare pentru un post de **mid dev la Adobe**.

**Status:** Draft · **Owner:** Alex · **Ultima actualizare:** 2026-06-17

---

## 0. Cum lucrăm (contractul de învățare)

Regula de aur: **tu scrii codul.** Eu (Claude) fac:

- **Explic conceptul** înainte să atingi tastatura — ce e, de ce există, ce problemă rezolvă.
- **Fac design-ul / îți dau pașii** sub formă de întrebări și constrângeri, nu de cod gata scris.
- **Review** după ce scrii: ce e bine, ce e greșit, *de ce*, ce ai face în producție.
- **Leg conceptul de interviu**: la fiecare modul, formulăm cum ai explica decizia într-un interviu Adobe.

Ce NU fac: nu-ți scriu funcțiile întregi „ca să meargă". Dacă te blochezi, îți dau un indiciu, apoi
încă unul — nu soluția direct. Vrei ownership 100%; asta înseamnă să simți și frecarea.

**Ritm:** un modul = un branch + (eventual) un tichet Jira. Nu trecem mai departe până nu poți
explica cu cuvintele tale ce ai construit și de ce.

---

## 1. Coloana vertebrală

Sistemul: **inventar restaurant ↔ POS extern**. POS-ul trimite webhook-uri semnate HMAC; noi mapăm
produsele la rețete interne și **scădem ingredientele** din stoc. Trei probleme grele: reziliență la
flood, idempotență (niciodată să nu scădem de două ori), mapping auditabil. Detalii complete în
[architecture.md](architecture.md).

Fiecare concept nou pe care vrei să-l înveți se **atârnă de o nevoie reală** a acestui sistem — nu
facem demo-uri rupte.

---

## 2. Hartă concept → unde trăiește în sistem

| Concept | Unde se atârnă |
|---|---|
| Docker / compose | Stack local: web + worker + Postgres + Redis/broker |
| Postgres + tranzacții | Idempotența: `select_for_update`, ledger cu constraint unic, `F()` |
| Celery | Procesarea async a webhook-urilor (persist-then-enqueue) |
| Kafka | Webhook-urile ca *event stream* — producer → topic → consumer |
| BullMQ (Node) | Microserviciu separat de notificări, cozi în alt ecosistem |
| DAGs (Airflow/Dagster) | Job nocturn de reconciliere stoc din ledger + raport de drift |
| Kubernetes + k9s | Deploy containere, scalare worker-i independent de API |
| Sidecar loguri → Datadog | Datadog Agent (DaemonSet/sidecar) care trimite loguri + traces |
| Datadog / Grafana / Splunk | Metrici: queue depth, latență deducere, rată unmapped |
| Multi-regiune / scalare | Rulare în 2 regiuni; Postgres replication; idempotență cross-region |
| Jira | `POSUnmappedItem`/`FAILED` → creează automat tichet de bug |
| MCP | Server MCP care expune starea inventarului/cozilor ca tool |

---

## 3. Milestones

Fiecare modul are: **Scop · Concepte noi · Ce construiești · De ce așa · Definition of Done · Unghi de interviu.**

### M0 — Fundația & workflow
- **Scop:** schelet de proiect + mod de lucru (git + Jira).
- **Concepte:** structură proiect Django, management dependențe, `.env`/settings split, branch & commit workflow, board Jira.
- **Construiești:** repo Django gol dar rulabil, primul commit, board Jira cu coloane, convenție de branch-uri.
- **De ce așa:** disciplina de workflow e jumătate din ce evaluează un senior la tine.
- **DoD:** `python manage.py runserver` pornește; există un tichet Jira pentru M1.
- **Interviu:** „cum îți organizezi munca / cum arată un commit bun".

### M1 — Domeniul de bază (modele, DB, tranzacții)
- **Concepte:** Django ORM, Postgres, constraints, migrări, tranzacții, `select_for_update`, `F()`.
- **Construiești:** modelele din §4 ale doc-ului (Provider, Location, Ingredient, MenuItem, Recipe, mappings, Event, Ledger).
- **De ce așa:** baza de date e *sistemul de adevăr*, nu broker-ul.
- **DoD:** migrări aplicate; poți inspecta datele în Django admin; constraint-ul unic pe ledger există.
- **Interviu:** „de ce constraint la nivel de DB și nu validare în cod".

### M2 — Webhook receiver (fast path)
- **Concepte:** DRF, securitate HMAC, `compare_digest`, replay window, idempotency Guard 1, 202 vs 401.
- **Construiești:** endpoint-ul din §3, cu autentificare HMAC pe raw body și `get_or_create`.
- **DoD:** teste pentru semnătură validă/invalidă, replay expirat, dedupe pe `external_event_id`.
- **Interviu:** „de ce semnezi raw bytes și de ce întotdeauna 2xx pentru evenimente cunoscute".

### M3 — Procesare async cu Celery
- **Concepte:** workeri, broker (Redis la început), `acks_late`, retries + backoff, DLQ, Guards 2 & 3.
- **Construiești:** `process_pos_event`, rezolvarea mapping-ului, deducerea atomică + ledger, state machine-ul.
- **DoD:** flux end-to-end: webhook → task → stoc scăzut o singură dată chiar la retry.
- **Interviu:** „de ce `acks_late` e sigur DOAR pentru că există Guard 3".

### M4 — Docker / docker-compose
- **Concepte:** Dockerfile, multi-stage build, compose, network, volume, env.
- **Construiești:** containere pentru web, worker, Postgres, Redis; `docker compose up` pornește tot.
- **Interviu:** „de ce multi-stage; cum separi config-ul de imagine".

### M5 — Observability locală
- **Concepte:** metrics vs logs vs traces, Prometheus, Grafana, structured logging, Flower.
- **Construiești:** dashboard cu queue depth, latență deducere, rată unmapped.
- **Interviu:** „ce alertezi și de ce; care metrică prinde un flood".

### M6 — Kafka ca event bus
- **Concepte:** streaming vs queue, topic/partition, consumer groups, ordering, consumer idempotent.
- **Construiești:** webhook produce într-un topic; un consumer deduce. Compari cu varianta Celery.
- **Interviu:** „când Kafka și când o coadă clasică".

### M7 — Microserviciu Node + BullMQ
- **Concepte:** serviciu Node, BullMQ, retries/backoff în alt ecosistem, comunicare între servicii.
- **Construiești:** „notification service" — la `FAILED`/`NEEDS_MAPPING` trimite notificări prin job-uri BullMQ.
- **Interviu:** „de ce un serviciu separat și nu încă un task Celery".

### M8 — Integrare Jira (bug tracking real)
- **Concepte:** integrare API extern, secrete, webhook invers, închidere ciclu.
- **Construiești:** `POSUnmappedItem`/`FAILED` creează automat un tichet Jira; rezolvarea reprocesează evenimentul.
- **Interviu:** „cum eviți spam-ul de tichete (dedupe pe mapping)".

### M9 — DAG de reconciliere (Airflow/Dagster)
- **Concepte:** DAG, scheduling, batch idempotent, backfill/replay.
- **Construiești:** job nocturn care recalculează stocul din ledger și raportează drift.
- **Interviu:** „de ce reconciliezi din ledger și nu ajustezi stocul orbește".

### M10 — Kubernetes + k9s
- **Concepte:** pod, deployment, service, configmap/secret, probes, HPA, scalare.
- **Construiești:** manifeste pentru web/worker; scalezi worker-ii pe queue depth; inspectezi cu k9s.
- **Interviu:** „cum scalezi independent ingestia de procesare".

### M11 — Datadog: loguri + agent sidecar („pod emo")
- **Concepte:** log shipping, Datadog Agent ca DaemonSet/sidecar, APM/traces, monitors.
- **Construiești:** agentul colectează logurile podurilor și le trimite în Datadog; un monitor pe rata de erori.
- **Interviu:** „sidecar vs DaemonSet pentru loguri; ce e un trace".

### M12 — Scalare & multi-regiune
- **Concepte:** regiuni, Postgres primary/replica, data locality, failover, idempotență cross-region.
- **Construiești:** plan + config pentru rulare în 2 regiuni; ce se întâmplă cu unicitatea evenimentelor.
- **Interviu:** „cum garantezi idempotența când ai două regiuni active".

### M13 — Server MCP
- **Concepte:** Model Context Protocol, expunerea de tools către un agent.
- **Construiești:** server MCP care expune starea inventarului/cozilor (read-only la început).
- **Interviu:** „ce e MCP și ce problemă rezolvă pentru integrarea cu agenți".

---

## 4. Fir continuu: pregătire interviu

După fiecare modul scrii 3–5 rânduri în `docs/interview-notes.md`: ce ai construit, ce trade-off ai
făcut, ce ai schimba la scară mare. La final ai un dosar de povești tehnice — exact ce întreabă Adobe.

---

## 5. Ordine recomandată

M0 → M1 → M2 → M3 → M4 → M5 sunt **secvențiale** (construiesc sistemul de bază).
M6–M13 sunt **module care se pot reordona** după pofta de învățare, dar fiecare presupune că M0–M4 există.
