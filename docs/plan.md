# Plan Master — Fifty's: aplicație de control al pierderilor (peste SoftOK)

**Status:** Activ · **Owner:** Alex · **Ultima actualizare:** 2026-06-20

Acesta e planul-sursă-de-adevăr al produsului. Detaliile tehnice profunde stau în
[architecture.md](architecture.md); vehiculul de învățare în [learning-roadmap.md](learning-roadmap.md);
jurnalul de greșeli→reguli în [progress-log.md](progress-log.md).

---

## 1. Context & integrare

Clientul (restaurantul **Fifty's**, fast-food: burgeri, lipii, strips) folosește **Aristarch / SoftOK**
pentru gestiune. Concluzii din recunoaștere:

- SoftOK rulează pe un **XAMPP (Apache + MariaDB + PHP)** pe un server Windows, expus public pe
  `http://82.78.126.249` (HTTP simplu — vulnerabilitate, dar și argument de vânzare pentru noi).
- Există o aplicație web custom **„Report System SoftOK"** (`/Rapoarte/index.php`) care stă **peste
  baza MariaDB** și expune deja: bonuri, vânzări, stoc + predicție, rețete, NIR/facturi, furnizori,
  top produse. Modulele mobile operaționale sunt marcate „curând".
- **Suprafața de integrare = MariaDB.** Noi *citim* de acolo (read-only), nu primim webhook-uri.
- phpMyAdmin e blocat din exterior (403) → accesul la DB se obține **prin client**, nu prin probing.

**Ce citim din SoftOK (există deja):** bonuri/vânzări, produse, rețete, stoc, NIR/facturi, furnizori.
**Ce construim noi (strat nou peste aceleași date):** UX mobil, alerte/push, **motorul de pierderi**,
Plăți/P&L, OCR facturi, Advisor, integrare delivery.

> Aplicația nu aduce date noi — aduce un **strat nou peste aceleași date**. Acolo e tot rostul ei.

**Întrebări deschise către client / Aristarch:**
- Cine deține „Report System" (Aristarch sau dev anterior) și avem cod + acces DB read-only?
- (Delivery) API-ul de listare comenzi e per platformă (Glovo/Bolt/Wolt separat) sau o sursă unică?

---

## 2. Produsul

Aplicație **mobilă (Android + iOS)** orientată pe **patron/manager**, pentru **control de costuri și
profitabilitate**, cu accent puternic pe **pierderi**. Figma-ul clientului e un **concept/wishlist**,
nu o specificație — noi conducem prioritizarea.

**Module (din Figma):** Dashboard, Facturi, Stoc, Produse & Rețetar, Pierderi, Plăți, Advisor, Rapoarte,
Delivery (Glovo/Bolt/Wolt).

**Diferențiatorii reali** (NU există în Report System):
1. UX mobil + alerte proactive
2. **Motorul de pierderi / reconciliere** (vezi §4) — inima produsului
3. **OCR facturi** (scanare → date) — feature AI vizibil
4. Plăți / P&L complet (chirie, salarii, utilități)
5. Delivery consolidat
6. Securitate (HTTPS + auth real vs XAMPP deschis)

**De ce e nevoie de produs — validat de client:** „mergem pe încredere, aruncă de capul lor, **fură și
zic că-s stricate, le ascund la gunoi**". Nu există proceduri. Reconcilierea prinde exact ce nu se
raportează.

---

## 3. Roadmap pe faze

Ordinea de priorități (stabilită cu clientul): **Fundație → Etapa 1 → 2 → 3 → 4.**

| Fază | Conținut | Dependențe / note |
|---|---|---|
| **Fundație** | Auth (token/JWT) + utilizatori + roluri/drepturi + **multi-locație** + audit log | prerechizită pentru tot |
| **Etapa 1** | Dashboard KPI + Stoc (zile rămase) + Top produse | doar date existente, 100% în controlul nostru |
| **Etapa 2** | Plăți/P&L + Facturi + **Pierderi** + **OCR facturi** | tabele noi simple + motor pierderi |
| **Etapa 3** | **Delivery** (Glovo/Bolt/Wolt) | aplicație/serviciu **decuplat**; dependență externă **neconfirmată** |
| **Etapa 4** | **AI Advisor** | neprioritar; se construiește ușor peste datele agregate |

Note:
- **Multi-locație: DA** (SoftOK are deja „Schimbă Gestiunea"). O locație acum, model pregătit pentru extindere; fără UI de comutare încă.
- **OCR facturi** urcat la importanță mare (lângă Advisor), dar trăiește în Etapa 2.
- **Delivery** = practic a treia aplicație; nu blocăm Etapele 1–2 pe ea până accesul nu e confirmat.

---

## 4. Modelul de pierderi (inima produsului)

**Scop:** gestiune atentă a resurselor încât orice pierdere peste prelucrarea normală să fie
**explicabilă**; ce rămâne neexplicat = semnal de fraudă.

**Formula** — per ingredient, per locație, **săptămânal** (inventar săptămânal):

```
Consum teoretic = Σ vândute(produs) × cantitate_brută(produs, ingredient)
                  unde cantitate_brută = cantitate_netă × (1 + factor_pierdere)
Consum real     = stoc_inițial + intrări(NIR) − stoc_final(inventar)
Pierdere totală = Consum real − Consum teoretic
   − consum propriu / protocol   (BUGET lunar, vezi mai jos)
   − stricare ingredient          (raportat per eveniment)
   = Pierdere NEATRIBUITĂ
Dacă Pierdere neatribuită > prag_fraudă → ALARMĂ
```

**Decizii cheie:**
- **Pierderea de prelucrare se bagă în rețetar pe CANTITATE** (`factor_pierdere` pe linia de rețetă),
  NU pe cost. Costul iese **derivat** din cantitatea brută → rămâne loss-inclusive, iar reconcilierea
  fizică (kg) se închide. (A pune doar pe cost ar da alarme false la fiecare porție.)
- `factor_pierdere` e **per ingredient** (ambalate ~0%, carne gătită mai mult) — nu un 30% global.
- **Prag de fraudă MIC** (~5–10%, modificabil), nu 30% — pierderea normală e deja în baseline.
- Cele două praguri (marjă vs fraudă) au venit ambele „30%" de la client — **de reclarificat**;
  în model rămân două butoane separate, configurabile.

**Două tipuri de pierdere atribuită:**
- `stricare_ingredient` → **raportare per eveniment** (marfă crudă aruncată/expirată).
- `consum_propriu_protocol` → **buget lunar în lei** (`BugetConsumPropriu`), nu raportare per consum
  (sucuri/ape consumate „pe sub mână" de patroni + angajați nu se vor raporta niciodată). Consumul
  până la plafon = acceptat; **ce trece peste plafon = semnal**. Atenție: buget realist/strâns, ca
  să nu mascheze furtul.

**OCR facturi:** poză factură → model vision (Claude) → JSON (furnizor, CIF, dată, linii) → draft NIR
de confirmat. **Prima intrare de la un furnizor = manuală** ca să se construiască maparea
`FurnizorArticolMapping` (produs furnizor → articol intern + conversie UM); de la a doua, OCR
auto-mapează. Nu tot ce se cumpără e ingredient → distincție **Ingredient vs Consumabil** (mănuși,
pungi); reconcilierea rulează doar pe ingrediente.

---

## 5. Decizii tehnice

- **Multi-locație:** FK `Gestiune` peste aproape tot; useri scopaţi pe una/mai multe gestiuni.
- **Mobil Android + iOS → API-first:** Django devine **backend/API** (Django REST Framework);
  aplicația de telefon e frontend separat (React Native sau Flutter — **nedecis**, nu blochează backend-ul).
- **Auth token/JWT** (telefonul nu ține sesiune de browser).
- **OCR = task AI vision** (backend/Celery).
- **Reconciliere = job programat** (Celery beat, săptămânal) — este **DAG-ul central** al sistemului.
- **Securitate** ca diferențiator: HTTPS, auth, drepturi reale.

---

## 6. Harta de date

**Reutilizăm din `core` (PM-7):** `Ingredient`, `MenuItem`, `Recipe`, `RecipeIngredient` (rețetarul).

**Modificăm:**
- `Ingredient`: scoatem `quantity_on_hand` (stocul e per-locație), adăugăm `cost_unitar` + `tip` (ingredient/consumabil).
- `RecipeIngredient`: adăugăm `factor_pierdere`; `quantity` devine cantitate_netă.

**Adăugăm (nou):**
- *Fundație:* `Gestiune`, `User`(AbstractUser) + `Membership(user, gestiune, rol)`, roluri (Patron/Manager/Personal/Contabil), `AuditLog`.
- *Stoc & mișcări:* `Stoc(gestiune, ingredient, cantitate)`, `NIR(gestiune, furnizor, dată)`+linii, `Inventar(gestiune, dată)`+linii, `Furnizor`.
- *Vânzări (din SoftOK):* `Bon(gestiune, dată, external_id)` + `BonLinie(bon, menu_item, cantitate, preț)`.
- *Pierderi:* `TolerantaPrelucrare`, `PierdereRaportata`, `BugetConsumPropriu`, `Reconciliere`.
- *Facturi/OCR:* `FurnizorArticolMapping`.

**`pos` (PM-8):** modelele actuale `POSProvider/POSLocation/POSItemMapping/POSModifierMapping`
(webhook + signing secret + mapare item extern) **NU** se potrivesc cu SoftOK (pull), ci cu
**Delivery (Etapa 3)** — Glovo/Bolt/Wolt chiar trimit webhooks. Acolo le re-folosim.

---

## 7. Legătura cu învățarea

Proiectul rămâne **vehicul de creștere** (țintă: mid dev Adobe). Conceptele se atârnă de nevoi reale:
reconciliere → **DAG**; alerte + OCR → **Celery**; OCR/Advisor → **AI/MCP**; mobil → **API/JWT**;
delivery → **webhooks/idempotență** (designul din architecture.md). Detalii și milestones în
[learning-roadmap.md](learning-roadmap.md).
