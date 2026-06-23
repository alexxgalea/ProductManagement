# Progress Log & Cheatsheet — ProductManagement

Jurnal de învățare: fiecare greșeală devine o **regulă**. Plus un cheatsheet de concepte.
Actualizat la fiecare pas și oglindit în Pinecone (recall semantic).

**Status:** M1 — Modele Etapa 1 ✅ + seed ✅ + Top produse (queryset/manager) ✅ + API DRF (Top produse) ✅ · **Ultima actualizare:** 2026-06-23

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
| 15 | Am pus `Postgres` în `requirements.in` (pachet greșit); a mers doar fiindcă depindea tranzitiv de `psycopg2-binary` | **Declară direct** dependența de care ai nevoie (`psycopg[binary]` = psycopg 3, preferat de Django 6). Nu te baza pe dependențe tranzitive accidentale. „Merge" ≠ „corect". `pip-sync` curăță pachetele care nu sunt în lockfile. |
| 16 | A doua oară muncă direct pe `main`, fără branch | **Creează branch-ul ÎNAINTE de a scrie cod** pentru un tichet (`git switch -c feature/PM-X-...` ca prim pas), nu după. |
| 17 | Typo-uri în modele: `ReceipeIngredient`, câmpuri `receipe`/`incredient`; iar `__str__` accesa `self.recipe`/`self.ingredient` (nume care nu există) | Numele de câmp = **numele coloanelor DB + API-ul folosit peste tot**; typo migrat = dureros de schimbat. Nepotrivirea nume câmp ↔ nume folosit în `__str__` → `AttributeError` la runtime (ex. în admin). Verifică numele înainte de `makemigrations`. |
| 18 | `on_delete=PROTECT` pe FK-ul `recipe` al liniei de rețetă (contrazice propriul raționament „child → CASCADE") | `on_delete` reflectă **înțelesul datelor**: child-of → `CASCADE`; resursă partajată/referită → `PROTECT`. O linie de rețetă e child al rețetei → CASCADE; ingredientul e resursă partajată → PROTECT. |
| 19 | `from models import ...` în `admin.py` → `ModuleNotFoundError: No module named 'models'` | Folosește **import relativ** `from .models import ...` (leading dot = pachetul curent, `core`) sau absolut `from core.models import ...`. Modelele trăiesc în pachetul app-ului, nu la rădăcină. |

---

## 1.1 Greșeli → reguli (M1 — domeniul de bază: `accounts`)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 20 | Am introdus custom `User` DUPĂ ce PM-7 migrase deja (cu User-ul default) | Custom `User(AbstractUser)` se definește **din prima zi**, chiar gol. `AUTH_USER_MODEL` schimbat după prima migrare = calvar (Django îl tratează ca schimbare **fundamentală**, nu ca extindere). În dev: reset DB. |
| 21 | `on_delete=SET_NULL` doar cu `blank=True` → `fields.E320` | `null` (nivel **DB**: coloana acceptă NULL) ≠ `blank` (nivel **formular/validare**). `SET_NULL` cere `null=True` ca să aibă unde scrie NULL. |
| 22 | `TextChoices` cu 3 valori (`"PATRON", "Patron", "patron"`) | Membru `TextChoices` = `NUME = "VALOARE_DB", "Etichetă"` — **exact 2**. Al treilea sparge maparea value/label și `default`. |
| 23 | Am încercat `manage.py flush` ca să „resetez baza" (+ n-aveam `psql` local) | `flush` golește doar **datele**, păstrează schema + migrările. Pentru schemă nouă pe Postgres-în-Docker: `docker compose down -v` (șterge volumul) → `up -d`. `dbshell` cere psql **local** → folosește `docker compose exec db psql`. |
| 24 | Era tentant `CASCADE` pe FK-urile din `AuditLog` | `on_delete` urmează **scopul datelor**: un audit log trebuie să **supraviețuiască** ștergerii actorului/locației (altfel pierzi exact dovada „ce s-a raportat") → `SET_NULL`. Extinde regula #18 la loguri de audit. |

---

## 1.2 Greșeli → reguli (M1 — catalog + inventory)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 25 | Ezitare `default=0` vs `null=True` pe `unitary_cost` | **0 ≠ NULL.** `0` = măsurătoare („e gratis"); `NULL` = „nu știu încă". Pe un câmp care **hrănește o metrică**, `default=0` ascunde datele lipsă (fail-silent: ingredient nepreț­uit → pierdere valorizată la 0 lei). `null=True` le face găsibile (`filter(unitary_cost__isnull=True)`) → fail-loud. |
| 26 | Voiam alertă la stoc negativ în `save()` / signals | `save()` și `post_save` **NU** se declanșează pe `QuerySet.update()`, `bulk_update()`, update cu `F()` — iar stocul se mută cu `F()` atomic, deci s-ar rata fix momentul. Side-effects de business (alerte) stau în **service layer**, nu în model. Property doar pentru afișare în UI. |
| 27 | FK către model din alt app | Folosește **string reference** `ForeignKey("app.Model", ...)`, nu importul clasei → eviți importurile circulare între app-uri; Django rezolvă referința lazy. |
| 28 | Era să pushez fără fișierele de migrare + app-ul nou (netracked) | Migrările **sunt cod** → `git add` explicit la `*/migrations/0xxx_*.py` și la app-ul nou. Fără ele, schema **nu se reconstruiește** la colegi/CI. |

---

## 1.3 Greșeli → reguli (M1 — sales)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 29 | `external_id = BigAutoField()` pentru id-ul bonului din SoftOK | `AutoField`/`BigAutoField` = cheie surogat **generată de Django**, nu pentru valori externe. Un id dintr-un sistem extern se stochează ca **`CharField`** (e identificator, nu număr; îl setezi tu la import). Cu el + `UniqueConstraint(location, external_id)` ai **import idempotent**. |
| 30 | `total` via `aggregate` — `["total"]` pus pe `Coalesce`, `output_field=DecimalField` (clasa) | `aggregate()` întoarce un **dict** → indexezi `["total"]` pe **rezultatul aggregate** (în afara apelului), nu pe expresia interioară. `output_field` cere o **instanță** `DecimalField()`, nu clasa. `F * F` cu zecimale poate cere `output_field` explicit (mixed types). |
| 31 | Am vrut să las `unit_price` fără constrângere „ca să permit promoții la 0 lei" | `>= 0` **permite 0** (`0 >= 0` e adevărat) → promo la 0 lei trece oricum; constrângerea blochează doar **negativul**. Distinge „0 e valoare validă" de „negativ interzis". Corolar: **nu constrânge ce nu înțelegi încă** (storno/voiduri din SoftOK necunoscute → revizuiești la importul real). |
| 32 | Confuzie `unique=True` vs `UniqueConstraint` | `unique=True` = unicitate pe **un** câmp (field-level); `UniqueConstraint` în `Meta` = pe **unul sau mai multe** câmpuri (modul modern; `unique_together` e soft-deprecated). Multi-câmp ⇒ **obligatoriu** Meta. |
| 33 | (concept) De ce stocăm prețul pe linia de bon | **Snapshot price:** stochează prețul **vândut** pe `ReceiptLine.unit_price`, nu te baza pe prețul curent din catalog (`MenuItem`) — ăla migrează în timp (promoții, schimbări) → pentru venit/profit **istoric** corect ai nevoie de prețul de la momentul vânzării. |

---

## 1.4 Greșeli → reguli (M1 — seed / management command)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 34 | Comandă invizibilă / `args["receipts"]` → TypeError | Management command: **ambele** `__init__.py` (`management/` + `commands/`) sunt obligatorii. Argumentele parsate sunt în `**opts`, NU în `*args`. Argumentele **poziționale ignoră `default`** (sunt obligatorii) → fă-le `--flag` dacă le vrei opționale. |
| 35 | `recipe = [get_or_create(...)[0]]` → „must be a Recipe instance" | `get_or_create` întoarce `(obj, created)` — **despachetează** (`[0]` sau `obj, _ =`). Nu-l pasa ca FK și **nu-l wrappa în `[]`** (altfel pasezi o listă acolo unde se așteaptă o instanță). |
| 36 | `bulk_create` hrănit cu `get_or_create(...)` (tupluri, deja salvate) | Pentru `bulk_create` construiești instanțe **NESALVATE** cu `Model(...)`, nu cu `get_or_create` (ăla deja salvează + întoarce tuplu — nu le amesteca). `ignore_conflicts=True` = idempotență pe `UniqueConstraint`. Părinții trebuie să aibă **PK** înainte de copii. Nu cheamă `save()`/signals/validatori (vezi #26). Și: stochează **valoarea** choice-ului (`Enum.MEMBER`), nu label-ul. |
| 37 | `datetime.now()` naiv; `flush` la final cu `.delete` fără `()` și ordine greșită | `timezone.now()`, nu `datetime.now()` (cu `USE_TZ`). Flush la **ÎNCEPUT** (cureți înainte de seed), ordine **dependenți-întâi** (respectă `PROTECT`: Stock/ReceiptLine/RecipeIngredient înainte de Ingredient), `.delete()` **cu paranteze**. `get_or_create` idempotent cere lookup **stabil** (nu `randint`). |

---

## 1.5 Greșeli → reguli (M1 — query / manager: Top produse)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 38 | Confuzii `values`/`annotate`/`output_field` | `values().annotate()` = **GROUP BY**: `values()` înainte de annotate = cheia de grupare **ȘI** coloanele de ieșire. `filter` pe câmp brut = WHERE; pe o anotare/agregat = HAVING. `output_field` se pune **înăuntrul** agregatului (`Sum(..., output_field=DecimalField())`), NU ca arg al `annotate()` (altfel „received non-expression"). |
| 39 | Neclar de ce `qs = self` în metoda de QuerySet | Custom `QuerySet` + `as_manager()`: metoda pornește din **`self`** (queryset-ul pe care a fost apelată) → **înlănțuibilă** (`.filter(...).top_products()` respectă filtrul). Hardcodarea `.objects.all()` ar arunca contextul. Principiu: „fat model, thin view". |
| 40 | A 3-a chemare întorcea `[]` din cauza `location=None` | `filter(camp=None)` = „WHERE camp **IS NULL**", NU „fără filtru". Ca să sari un filtru, aplică-l **condiționat** (`if x is not None: qs = qs.filter(...)`), construind `qs` pas cu pas. |
| 41 | „Nu se actualizează" după ce schimb codul în shell | Shell-ul Python importă modulele **o dată per proces** (fără hot reload). Pentru iterație: fișier scratch + `manage.py shell < scratch.py` (proces nou = cod proaspăt). Locul „oficial" devine apoi testele (`TestCase`). |

---

## 1.6 Greșeli → reguli (M1 — API / DRF: endpoint Top produse)

| # | Ce s-a întâmplat | Regula de reținut |
|---|---|---|
| 42 | `query_params.get(location, ...)` (variabilă) + `limit` string în `[:limit]` | Cheile din `.get()` sunt **string-uri** (`get("location")`). Query params vin mereu ca **string** (ca env vars — regula #6) → convertește (`int(limit)`). |
| 43 | Validarea rula **după** ce chemam `top_products` | **Early return:** întoarce `400` ÎNAINTE de query-ul costisitor, nu după. Întâi citește → convertește → validează → (dacă errors) return → abia apoi query. |
| 44 | `return Response(response)` în loc de `serializer.data` | Întoarce `serializer.data`, nu obiectul brut — altfel sari peste serializer (redenumiri/format). Pentru date **agregate** (GROUP BY) folosești `serializers.Serializer` simplu, NU `ModelSerializer` (n-ai un model în spate). |
| 45 | `qty`/`revenue` apar ca string în JSON | DRF redă `Decimal` ca **string** (default `COERCE_DECIMAL_TO_STRING`) ca să păstreze precizia — bun pentru bani/cantități. `decimal_places` din câmp controlează zecimalele afișate. |

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
7. **Custom User din start** — `AUTH_USER_MODEL` nu se schimbă ușor după prima migrare; `null` (DB) ≠ `blank` (formular).
8. **0 ≠ NULL** (măsurătoare vs „nu știu"); **side-effects de business în service layer**, nu în `save()`/signals (nu prind `.update()`/`F()`).
