# Progress Log & Cheatsheet — ProductManagement

Jurnal de învățare: fiecare greșeală devine o **regulă**. Plus un cheatsheet de concepte.
Actualizat la fiecare pas și oglindit în Pinecone (recall semantic).

**Status:** M0 — Foundation & workflow (în curs) · **Ultima actualizare:** 2026-06-19

---

## 1. Greșeli → reguli (M0)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 1 | Am crezut că `pip-tools` e „o variantă de venv" | `venv` izolează **mediul**; `pip-tools`/`poetry` **îngheață dependențele**. Probleme diferite, folosite împreună. Conceptul real: **reproductibilitate (lockfile)**. |
| 2 | Răspuns incomplet la `.in` vs `.txt` | `.in` = intenție lejeră (ce ceri), `.txt` = lockfile pinned reproductibil (ce se instalează). Upgrade = `pip-compile --upgrade` **deliberat**, nu drift accidental. |
| 3 | Rulam pe Python 3.9 (system, EOL) | **Niciodată** Python-ul de sistem. Instalează versiune modernă (`brew install python@3.12`). Versiunea de Python **cascadează** în ce pachete poți avea (3.9 → Django 4.2; 3.12 → Django 6). |
| 4 | Typo `requrements.in/.txt` | Verifică numele fișierelor; un nume greșit committat rămâne în istoric. |
| 5 | Definiții duplicate în `settings.py` (vechiul cod hardcodat rămas sub citirile din env) | În Python **ultima atribuire câștigă**. După ce externalizezi o valoare, **șterge** varianta veche, altfel o anulezi. |
| 6 | `ALLOWED_HOSTS = env("...")` → string în loc de listă | Variabilele de mediu sunt **mereu string-uri**. Folosește caster: `env.list`, `env.bool`, `env.int`, `env.db`. |
| 7 | Lipsea `.env.example` | `.env` în `.gitignore`, dar `.env.example` **se commit-ează** — documentează ce chei cere proiectul. |
| 8 | Am uitat `manage.py` când am schimbat `DJANGO_SETTINGS_MODULE` (am făcut doar wsgi/asgi) | Când schimbi ceva în mai multe locuri, schimbă-le pe **toate** — caută cu `grep` ca să fii sigur. |
| 9 | Lipsea `config/settings/__init__.py` | Pachet **explicit** cu `__init__.py`; nu te baza pe namespace packages — e fragil și neevident. |
| 10 | Am crezut că „`check` verde = corect" | Un check verde înseamnă doar că **ce a verificat el** a trecut. Află CE validează: `check` rula pe settings **gol** (default). |
| 11 | Am descris `.parent` invers („mai adânc") | Fiecare `.parent` **urcă** spre rădăcină. Mutarea unui fișier mai adânc cere **+1 `.parent`** ca să compensezi. |
| 12 | Commit direct pe `main`, ad-hoc | `main` protejat & deployable. Feature branch per tichet Jira → PR → merge. |
| 13 | `db.sqlite3` a ajuns în istoric și a fost „șters" mai târziu | Ștergerea într-un commit ulterior **NU** scoate din istoric. Pentru un secret real: **(1) rotește cheia, (2) rescrie istoricul** (`git filter-repo`/BFG). |
| 14 | Commit pe main cu mesaj vag fără cheie (`Actualizing the project`); asociat PM-3 în loc de PM-4 | Mesaj de commit = **cheia tichetului + descriere imperativă clară** a ce s-a schimbat. Fără cheie în mesaj, Jira **nu** leagă munca de tichet (development panel gol). Cheia din branch/commit trebuie să fie a tichetului **real**. |

---

## 2. Cheatsheet — concepte de învățat (roadmap)

- **Backend / Django:** ORM, migrări, constraints, tranzacții (`select_for_update`, `F()`), DRF, settings split, 12-factor config.
- **Securitate:** HMAC + `compare_digest`, replay window, secrete în env/secrets manager, secret scanning.
- **Async / messaging:** Celery (`acks_late`, retries, DLQ), idempotență (3 guards), Kafka (topics, partitions, consumer groups), BullMQ.
- **Infra:** Docker (multi-stage, compose), Kubernetes (pods, deployments, services, probes, HPA), k9s, scalare, multi-regiune.
- **Observability:** metrics vs logs vs traces, Prometheus/Grafana, Datadog agent (sidecar/DaemonSet), Splunk, alerting.
- **Data / pipelines:** Postgres replication, DAGs (Airflow/Dagster), reconciliere/backfill.
- **Workflow:** git trunk-based, PR-uri, Jira (Epic→Story→Task→Bug), smart commits, MCP.

---

## 3. Reguli de aur (condensate)

1. **Mediu ≠ dependențe ≠ lock** — trei lucruri separate.
2. **Config în environment, secrete niciodată în cod sau istoric.**
3. **Fail-fast pe secrete** (fără default), **fail-safe pe siguranță** (`DEBUG` default `False`).
4. **Un check verde nu e o dovadă** — știi ce validează.
5. **Versiunea runtime-ului cascadează** în tot ce poți instala.
6. **main protejat; muncă pe feature branch legat de un tichet.**
