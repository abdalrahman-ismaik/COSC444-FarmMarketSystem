# Track A review note — database diagrams, design and remaining validation

**Owner:** Ali Alshamsi (100062530), working with a Claude Code agent · **Date:** 2026-11-17 · **Branch:** `ali/database-diagrams-validation` · **PR:** https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2 · **Reviewer:** Abd Alrahman Ismaik (`abdalrahman-ismaik`)
**Tasks:** DB-01, DB-02, DB-03, TEST-01 → **Ready for review** (not Accepted; only the reviewer records acceptance)

## What changed and why

The rubric's 10-point *ER diagram and relational schema* category had no artifacts. The test plan also still had open rollback, concurrency, GUI-flow, boundary and image cases. This PR adds:

- the two diagrams as editable Draw.io sources with PDF/SVG exports;
- a database-design explanation;
- new executed test evidence with a list of findings.

**No application code, schema, seed data or business policy was changed.** The defects found are reported below with proposed fixes for your decision.

| Area | Files |
|---|---|
| DB-01 conceptual ER | `docs/diagrams/conceptual-er.drawio`, `.pdf`, `.svg` |
| DB-02 relational schema (6 pages) | `docs/diagrams/relational-schema.drawio`, `.pdf`, `relational-schema.svg`, `relational-schema-p2…p6.svg` |
| Diagram tooling | `docs/diagrams/tools/generate_diagrams.py`, `docs/diagrams/tools/check_diagrams_vs_sql.py`, `docs/diagrams/README.md` (build/export/verify) |
| DB-03 design explanation | `docs/DATABASE_DESIGN.md` |
| TEST-01 evidence | `docs/evidence/REMAINING_TEST_RESULTS.md`; `docs/evidence/track-a/remaining-checks.json`, `remaining-checks-run1.json`, `gui-flow.json`, 9 `gui-*.png` screenshots |
| Guarded reproduction scripts | `app/tests/track_a_remaining_checks.py` (backend, 168 checks), `app/tests/track_a_gui_flow.py` (Tk GUI flow + restart phase) |
| Coordination | `PROGRESS.md` (Track A rows and activity log), `docs/TESTING.md` (one pointer line), this note |

## Requirements addressed

| Requirement | Rubric category | Evidence |
|---|---|---|
| P1-01 conceptual ER in Draw.io with justified entities, relationships, cardinalities and key rules (farms, cycles, lots, requests, allocations, deliveries) | ER/schema (10) | conceptual-er.*; DATABASE_DESIGN §1 |
| P1-02 separate schema: tables, PK/FK, types, important constraints | ER/schema (10) | relational-schema.* pages 1–6; checker 851/0 |
| P1-03/P1-04 constraints and sample coverage | Implementation (15) | DB-01a/b, DB-02a–q, DB-03a–c |
| BR-01…BR-09 business rules; P4 error handling | Errors/rules (5), Backend (10) | REMAINING_TEST_RESULTS groups HAR, FARM, REQ, STK, ALC, DEL, UNIT, ADM, SRCH, ERR |
| P5-01 valid, invalid, boundary, repeated and concurrent cases | Technical doc/test (15) | TX-01a–f rollback, TX-02/03 concurrency, boundaries |
| P5-02 stock after harvest, reservation, release, delivery, loss, correction and disposition; forecast separation | Technical doc/test (15) | STK-01…04, DEL-01…03, LS-04 |
| P2-03 GUI search → request → allocation → partial delivery; P2-05 image upload and retrieval after restart | GUI (10) | GUI-SRCH-01 … GUI-DEL-05, GUI-IMG-02 |
| Phase 3 Loss & Surplus thresholds, boundaries and two dispositions | Advanced feature (10) | LS-01…06, GUI-LS-01/02 |

## Build and verification commands

Export (draw.io desktop 32.4.1) and the read-only diagram check: see [docs/diagrams/README.md](../diagrams/README.md).

```powershell
python docs\diagrams\tools\generate_diagrams.py
& "$env:LOCALAPPDATA\Programs\draw.io\draw.io.exe" -x -f pdf --crop -a -o docs\diagrams\relational-schema.pdf docs\diagrams\relational-schema.drawio
.\.venv\Scripts\python.exe docs\diagrams\tools\check_diagrams_vs_sql.py
```

The tests below run **only on a disposable MySQL instance**. Both scripts refuse to run otherwise:

```powershell
.\.venv\Scripts\python.exe app\setup_database.py
$env:FARM_DISPOSABLE_DB_CONFIRM = "127.0.0.1:3317/farm_market_db"   # your own disposable host:port/db
.\.venv\Scripts\python.exe app\tests\track_a_remaining_checks.py
.\.venv\Scripts\python.exe app\setup_database.py
.\.venv\Scripts\python.exe app\tests\track_a_gui_flow.py; .\.venv\Scripts\python.exe app\tests\track_a_gui_flow.py --restart
```

## Actual validation results (this PC, 2026-11-17)

Environment: Windows 11, Python 3.12.1, a **separate disposable** MySQL 8.0.46 instance on 127.0.0.1:3317 (REPEATABLE-READ, strict mode). The normal MySQL80 service was not touched. Details are in [REMAINING_TEST_RESULTS.md](../evidence/REMAINING_TEST_RESULTS.md).

| Check | Result |
|---|---|
| Existing `test_business_rules.py`, rerun on fresh seed | **65/65 passed** |
| Diagram vs `information_schema` cross-check (parses the .drawio XML) | **851 passed / 0 failed**; 32/32 FKs drawn with correct optionality; 13/13 CHECK names; mutation test detected 3/3 injected errors |
| Visual QA | All 7 PDF pages rendered (PyMuPDF) and inspected; SVGs rendered in headless Edge. Clipping, line crossings, crowding and wrapping were fixed; final pages clean |
| `track_a_remaining_checks.py` run 1 | 162 Pass · 5 Fail · 1 Info (SRCH-02a was a test-oracle error, corrected and documented; run 1 JSON kept) |
| `track_a_remaining_checks.py` run 2 | **163 Pass · 4 Fail · 1 Info**. All 4 failures are finding F-01 |
| GUI flow (final clean run, incl. new-process restart) | **21 Pass · 1 Fail** (F-05) |
| Live LangChain/Gemini | **Not run by Track A** (no key on this PC). Existing evidence: AI_VALIDATION.md |

What now has new evidence:

- intermediate-failure rollback for 6 operations;
- 4 concurrency pairs that serialize correctly, and 1 class that does not (F-01);
- the GUI flow search → request (keyboard) → blocked over-allocation → two allocations → shortfall without reason refused → partial receipt → status, plus upload and photo retrieval in a new process;
- threshold bounds 0/60 and 0/365 with invalid values;
- sell-by today, N, N+1, age M−1/M, null sell-by, fully reserved and released lots;
- donation and disposal of 0.01 and exactly the available quantity, with excess, zero, negative, missing reason, other farmer and admin refused;
- images: missing, empty, wrong type, fake bytes, GIF, exactly 5 MiB accepted, 5 MiB + 1 refused, byte-identical BLOB round trip, no-photo/corrupt/truncated fallbacks;
- unit mismatch both ways;
- the 17 SQL constraint violations, with checksums unchanged afterwards.

## Findings

### F-01 Concurrent oversell

**Severity: High (BR-04).**

- **Reproduction:** `track_a_remaining_checks.py`, TX-02a/b/c. Two threads, released by a barrier, allocate 80 kg each from one 100 kg lot to two *different* requests. Run 2 oversold in **19/20 trials**, leaving the lot at `100/160/−60`. Allocation vs donation of 80 oversold in **10/10** trials. TX-02b reproduces it deterministically by pausing thread A after its ownership query.
- **Root cause:** `allocate`, `dispose_lot` and `record_adjustment` run `_check_lot_owner` (a plain SELECT) before `lot_available` locks the lot row. Under InnoDB's default REPEATABLE READ, that plain SELECT fixes the transaction's read snapshot. After waiting for the lot lock, the following `SELECT … FROM v_lot_stock` still reads the old snapshot, so the other transaction's committed RESERVED or DONATED movement is invisible. The existing suite's race uses a single request, whose row lock serializes the threads before any snapshot is taken, so it passes.
- **Impact:** available and reserved quantities become inconsistent (reserved > on_hand). Delivering both allocations would drive on_hand negative. This contradicts “never allocate more than available”. It probably won't appear in a single-presenter demo, but it is a correctness defect.
- **Smallest proposed fix (needs your authorization; code only, no schema or policy change):** add `init_command="SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"` to `pymysql.connect` in `db.get_connection`. Each statement then reads the latest committed data, so the post-lock availability read sees the competing movement.
  - Simulated in-process (TX-02d): **0/20** oversells.
  - Alternative: move `lot_available(...)` before `_check_lot_owner(...)` in the three functions. This is more local but fragile if code is reordered later.
- **Required validation after the fix:** TX-02a/b/c and TX-03z pass on fresh seed; the 65-check suite, `track_a_remaining_checks.py` and the GUI flow still pass; assistant read-only check (`START TRANSACTION READ ONLY` unaffected).

### F-02 DELIVERED is based on allocated totals

**Policy.** Current behaviour (seed #6, DEL-05a, GUI-DEL-05): a request becomes DELIVERED once allocations reach the requested quantity and none is still reserved, even when less was received (60/52, 30/25, 150/140). Options:

- (a) keep it and justify it: “every allocated quantity was settled; the shortfall is recorded as discrepancy and loss”;
- (b) require received ≥ requested for DELIVERED and keep PARTIALLY_DELIVERED otherwise. This changes `_refresh_request_status`, alters seed request #6's displayed status and needs the business-rule and AI evidence rechecked.

### F-03 One receipt finalises an allocation

**Policy.** The shortfall is released and recorded as LOSS; no later top-up receipt exists (DEL-04). Recommend keeping and documenting it (BR-05 is satisfied: the difference is recorded clearly).

### F-04 “Approved correction”

**Policy.** This is a farmer action with a mandatory reason and no administrator approval step. Recommend documenting it as “reason-justified farmer correction”. A separate approval workflow would be new scope.

### F-05 Allocate pre-fill with thousands separator

**Low (GUI).**

- **Reproduction:** GUI-ALC-03. A 1,500 kg request pre-fills `1,500`; clicking Allocate shows “Allocation quantity must be a number.”
- **Fix:** in `app/app.py` `AllocateTab.on_request`, insert `fmt(remaining).replace(",", "")`, as `DeliveriesTab.on_select` already does.
- **Validation:** GUI-ALC-03 passes; GUI flow otherwise unchanged.

### F-06 Truncated JPEG accepted

**Low (images).**

- **Reproduction:** IMG-04b/IMG-04e. A JPEG cut to half its bytes passes `validate_image` (Pillow `verify()` does not decode pixel data). It is stored, and buyers then see “⚠ Image unavailable”. The app does not crash.
- **Fix:** in `validate_image`, after `verify()`, reopen the bytes and call `.load()` inside the same try block.
- **Validation:** IMG-04b becomes a rejection; IMG-03*/04* and GUI-HAR-01 still pass.

### F-07 Display scaling

**Observation.** At 150 % Windows scaling on 1920×1080, the window is 1280×701 logical. The Deliveries “receipts” table shows no rows without scrolling (screenshot `gui-deliveries-partial.png`). Check the demo PC's scaling. No code change is proposed.

### F-08 Surplus eligibility

**Policy.** “Unallocated” means no non-RELEASED allocation, so previously released lots qualify (LS-06). Recommend documenting the wording as “currently unallocated”.

Also documented (not new defects): cross-record unit equality and farmer-only assignment are application-enforced; `request_status_history` statuses are VARCHAR; the assistant's regex validation and 50-of-200-row summary limit (AI_VALIDATION.md).

## Decisions requested

1. **F-01:** authorize the one-line READ COMMITTED fix (recommended) or the reorder alternative. Fix it in this PR (I add the commit and rerun the validation above) or in a separate PR?
2. **F-02:** keep the allocation-based DELIVERED policy (and justify it in the report/poster) or change it to received-based?
3. **F-03, F-04, F-08:** confirm “keep and document” wording.
4. **F-05 and F-06:** authorize the two small fixes, or leave them documented as known issues.
5. **Diagrams:** is Chen notation with (min,max) acceptable for the conceptual ER, and the multi-page crow's-foot schema for the relational one? For the poster, Track B could use the conceptual ER plus schema page 1.
6. **Packaging:** should `app/tests/track_a_*.py` be included in the submission ZIP as test sources, or kept repository-only? This is a Track B / PACKAGE-01 input.

## Inputs ready for Track B (report and poster)

- Diagrams: use the **PDFs** (vector). `conceptual-er.pdf` is one page, about 1,744 × 1,058 pt. `relational-schema.pdf` has six pages: page 1 is the overview, pages 2–4 the detail pages, page 5 the unit/user FKs and page 6 the views. Scale to a landscape page; SVGs are about 1–2 MB because of PNG fallbacks.
- Text: DATABASE_DESIGN §1 (entity and cardinality justification), §5 (ledger table with a worked example), §8 (transactions), §9 (SQL vs application rules), §10 (policies).
- Results summary: 65/65 existing suite rerun; 851/0 diagram check; 163 Pass / 4 Fail (F-01) / 1 Info backend; 21 Pass / 1 Fail (F-05) GUI. Cite the findings honestly; do not present F-01/F-05 as passing.
- Existing live-AI evidence is unchanged and remains the team's AI evidence (AI_VALIDATION.md).

## Limitations

- **Environment:** one PC, one MySQL version, 150 % scaling only. Concurrency was tested with Python threads on one machine.
- **GUI method:** GUI checks invoke Tk widgets and callbacks programmatically (with Win32 `PrintWindow` screenshots). They are not a human usability or accessibility study.
- **AI:** no Gemini checks were run here.
- **Reproduction script code:** `track_a_remaining_checks.py` patches `db.get_connection` and `db._check_lot_owner` **inside its own process** for fault injection, the READ COMMITTED simulation and the deterministic interleaving. Application files are unchanged.
- **Scope:** administrative items (registration, booking, attendance) and DEMO-01 are outside Track A and were not touched.
