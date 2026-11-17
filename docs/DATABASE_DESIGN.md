# Database design

**COSC444 Database Systems · Lab B1 · Track A (DB-03).** Prepared 2026-11-17 by Ali Alshamsi with a Claude Code agent. Status: **Ready for review**. Abd Alrahman Ismaik decides acceptance.

This document explains the design of the existing database: entities, relationships, mapping, normalization, units, forecasts, the stock ledger, history, ownership and transactions. It describes what `app/schema.sql` and `app/db.py` actually do. It does not record any instructor approval of the policies described. Where current behaviour is a team choice rather than a proposal requirement, it is labelled **Policy** and listed for a reviewer decision in [Track A review](reviews/TRACK_A_REVIEW.md#decisions-requested).

| Artifact | Path |
|---|---|
| Conceptual ER (editable / exports) | [conceptual-er.drawio](diagrams/conceptual-er.drawio) · [PDF](diagrams/conceptual-er.pdf) · [SVG](diagrams/conceptual-er.svg) |
| Relational schema, 6 pages (editable / exports) | [relational-schema.drawio](diagrams/relational-schema.drawio) · [PDF](diagrams/relational-schema.pdf) · SVG per page: [p1](diagrams/relational-schema.svg) [p2](diagrams/relational-schema-p2.svg) [p3](diagrams/relational-schema-p3.svg) [p4](diagrams/relational-schema-p4.svg) [p5](diagrams/relational-schema-p5.svg) [p6](diagrams/relational-schema-p6.svg) |
| Build/verify instructions | [docs/diagrams/README.md](diagrams/README.md) |
| Source of truth | [app/schema.sql](../app/schema.sql) (15 tables, 2 views, 32 FKs, 13 named CHECKs) |
| Test evidence | [REMAINING_TEST_RESULTS.md](evidence/REMAINING_TEST_RESULTS.md) |

The schema diagram was checked mechanically against the live MySQL `information_schema` with `docs/diagrams/tools/check_diagrams_vs_sql.py`. That run passed 851 checks with 0 failures, and all 32 FKs are drawn. The checker parses the `.drawio` XML itself, and a mutation test confirmed that it detects injected errors.

## 1. Conceptual model

### Entities and why they exist

| Entity | Identifier | Why it is a separate entity |
|---|---|---|
| EMIRATE | emirate_id | Location reference shared by farms and markets; supports emirate search filters without free-text spelling variants |
| FARM | farm_id | Proposal core entity; owner of crop cycles; unit of farmer ownership |
| MARKET | market_id | Proposal core entity; owner of requests and receipts; unit of buyer ownership |
| USER | user_id | Proposal core entity; every operational record names a responsible user (BR-08); role decides permitted actions |
| CROP | crop_id | Reference list so requests and cycles compare the same crop; default unit for data entry |
| UNIT | unit_id | Every quantity needs an explicit unit (BR-06); a reference entity prevents “kg”/“KG”/“kilos” variants. No conversion factor is stored, so none can be applied silently |
| CROP_CYCLE | cycle_id | One growing period of one crop on one farm (proposal terminology). Holds the **forecast** (expected date and quantity), keeping it apart from stock (BR-02) |
| HARVEST_LOT | lot_id | One harvested batch with its own quantity, date and optional sell-by date (BR-01). It is the unit of stock, allocation, images and disposition |
| LOT_IMAGE | image_id | A lot can have zero or more photos. A separate entity keeps the large BLOB out of lot queries (BR-09) |
| STOCK_MOVEMENT | movement_id | The dated ledger from which stock is derived (BR-03): harvest, reservation, release, delivery, loss, correction, donation and disposal |
| MARKET_REQUEST | request_id | A buyer's demand for a crop and quantity by a date. It may be fulfilled from several lots (BR-04) |
| REQUEST_STATUS_CHANGE | history_id | Keeps date, user and reason for every request status change (BR-08). It is not overwritten when the status changes |
| ALLOCATION | allocation_id | Associative entity resolving the many-to-many “request supplied from lot”. It carries its own quantity, status and actor, and is the reservation that receipts confirm |
| DELIVERY_RECEIPT | receipt_id | What actually arrived for one allocation: the received quantity and a clearly recorded discrepancy (BR-05) |

Not modelled as entities: the views `v_lot_stock` and `v_request_status` (derived data, §6), and assistant questions (not stored).

### Relationships and cardinalities

(min,max) is the number of relationship instances one entity instance takes part in. “App” means that the minimum is guaranteed by `db.py` in the same transaction and not by SQL.

| Relationship | Cardinality | Justification / enforcement |
|---|---|---|
| FARM LOCATED IN EMIRATE | FARM (1,1) — EMIRATE (0,N) | `farms.emirate_id NOT NULL`; an emirate need not have farms |
| MARKET LOCATED IN EMIRATE | MARKET (1,1) — EMIRATE (0,N) | as above |
| USER ASSIGNED TO FARM {assigned_at} | USER (0,N) — FARM (0,N) | M:N: a farmer may run several farms (Omar runs two) and a farm may have several farmers. Only farmers may be assigned (App: `assign_farm`). `add_farm` assigns the creator in the same transaction |
| USER BUYS FOR MARKET | USER (0,1) — MARKET (0,N) | A market buyer belongs to exactly one market and other roles to none. SQL `CHECK chk_user_market` |
| FARM RUNS CROP_CYCLE | FARM (0,N) — CROP_CYCLE (1,1) | `crop_cycles.farm_id NOT NULL` |
| CROP_CYCLE OF CROP | CROP_CYCLE (1,1) — CROP (0,N) | one crop per cycle |
| CROP_CYCLE YIELDS HARVEST_LOT | CROP_CYCLE (0,N) — HARVEST_LOT (1,1) | Proposal: a lot belongs to one cycle. The lot's crop and farm are **derived through the cycle**, not repeated on the lot |
| HARVEST_LOT PICTURED BY LOT_IMAGE | LOT_IMAGE (1,1) — HARVEST_LOT (0,N) | Every image belongs to a lot (BR-09); photos are optional |
| HARVEST_LOT CHANGED BY STOCK_MOVEMENT | STOCK_MOVEMENT (1,1) — HARVEST_LOT (1,N) App | Every lot gets a `HARVEST_ADDED` movement in the same transaction that creates it |
| MARKET PLACES MARKET_REQUEST | MARKET_REQUEST (1,1) — MARKET (0,N) | A request is owned by one market |
| MARKET_REQUEST REQUESTS CROP | MARKET_REQUEST (1,1) — CROP (0,N) | one crop per request |
| MARKET_REQUEST RECORDS REQUEST_STATUS_CHANGE | REQUEST_STATUS_CHANGE (1,1) — MARKET_REQUEST (1,N) App | A “Request created” row is inserted with the request |
| MARKET_REQUEST FULFILLED BY ALLOCATION | ALLOCATION (1,1) — MARKET_REQUEST (0,N) | Partial fulfilment: a request may draw on many lots |
| HARVEST_LOT SUPPLIES ALLOCATION | ALLOCATION (1,1) — HARVEST_LOT (0,N) | A lot may supply many requests until its availability is exhausted |
| ALLOCATION CONFIRMED BY DELIVERY_RECEIPT | DELIVERY_RECEIPT (1,1) — ALLOCATION (0,1) | At most one receipt per allocation (`UNIQUE allocation_id`); a reserved allocation has none yet |
| ALLOCATION CAUSES STOCK_MOVEMENT | STOCK_MOVEMENT (0,1) — ALLOCATION (1,N) App | Allocation-related movements carry `allocation_id`; harvest, loss, correction, donation and disposal movements do not (nullable FK). Every allocation has its `RESERVED` movement |
| CROP DEFAULT UNIT, CROP_CYCLE FORECAST IN UNIT, HARVEST_LOT MEASURED IN UNIT, MARKET_REQUEST REQUESTED IN UNIT | record (1,1) — UNIT (0,N) | Explicit units (BR-06). Allocations, receipts and movements carry the lot's unit (see §3) |
| Responsible user on cycles, lots, images, requests, status changes, allocations, receipts, movements | record (1,1) — USER (0,N) | BR-08 accountability. Shown as rule R8 on the ER diagram and drawn as 8 FKs on relational page 5 to keep the ER readable |

## 2. Mapping to relational tables

| Conceptual construct | Relational mapping |
|---|---|
| Strong entities | One table each, surrogate `INT AUTO_INCREMENT` PK. Natural identifiers kept as `UNIQUE` (emirate_name, unit_code, crop_name, market_name, farm_name, email) |
| 1:N relationships | FK on the N side. NOT NULL where participation is (1,1); `users.market_id` and `stock_movements.allocation_id` are nullable because participation is optional |
| M:N USER–FARM with attribute | Junction table `farm_users(farm_id, user_id, assigned_at)` with composite PK |
| 1:0..1 ALLOCATION–RECEIPT | FK `delivery_receipts.allocation_id` declared `UNIQUE` |
| ALLOCATION (associative) | Own table with own PK (an allocation has its own status and actor, and is referenced by receipts and movements), FKs to request and lot |
| Role-dependent link USER–MARKET | Nullable FK + table CHECK `chk_user_market` |
| Multivalued / composite attributes | None |
| Derived attributes (/on_hand, /reserved, /available, /allocated_quantity, /received_quantity) | Not stored; computed by views `v_lot_stock` and `v_request_status` |
| Enumerated domains | `ENUM` for role, cycle/request/allocation status and movement type; `CHECK` for image MIME type |

No `ON DELETE`/`ON UPDATE` actions are declared, so MySQL's default (RESTRICT) blocks deleting a referenced row. The application never deletes reference data; it deactivates rows with `is_active` (§7).

## 3. Normalization and deliberate redundancy

Every table has a single-column surrogate key, or the composite key `(farm_id, user_id)`. Non-key attributes describe only that key. There are no repeating groups and no attribute depends on part of a composite key. The base design is in 3NF/BCNF with respect to the declared keys and natural UNIQUE keys. The crop and farm of a lot are not stored on the lot (no transitive copy); they come through `crop_cycles`.

The following redundancies are intentional. Each is controlled as stated:

| Redundant data | Reason | How consistency is kept |
|---|---|---|
| `unit_id` on `harvest_lots`, `allocations`, `delivery_receipts`, `stock_movements` (equal to the cycle/lot unit) | Every quantity row states its unit explicitly (BR-06). Ledger rows are self-describing for audit and the assistant | **App**: `record_harvest` copies the cycle's unit; `allocate` requires lot unit = request unit and copies it; receipts and movements copy it. SQL only checks that the unit exists. DB-03c found 0 mismatches in the seed |
| `delivery_receipts.allocated_quantity` | Snapshot of what was promised when the receipt was confirmed | Copied from the locked allocation in the same transaction |
| `delivery_receipts.discrepancy_quantity` | Makes the difference explicit (BR-05) and easy to query | **SQL** `chk_rcpt_diff`: must equal allocated − received; `chk_rcpt_max`, `chk_rcpt_nonneg` |
| `harvest_lots.quantity_harvested` and the lot's `HARVEST_ADDED` movement | The lot records what was picked; the ledger records stock | Written together by `record_harvest`. Stock is always computed from the ledger, so a later correction changes stock but not `quantity_harvested` |
| `market_requests.status` | Fast filtering and a stable value for status history | Recomputed by `_refresh_request_status` inside every allocation/release/delivery/update transaction; not recomputed by `v_request_status` |
| `request_status_history.old_status/new_status` are `VARCHAR(25)` | History text is kept even if enumerations change | Not constrained to the ENUM values. Only `db.py` writes them |

## 4. Units and forecast separation

- **Units.** Each cycle, lot, request, allocation, receipt and movement has `unit_id NOT NULL`. There is no conversion table. Allocation between a kg request and a box lot is rejected (UNIT-01a/b). Stock summaries group by crop **and** unit (UNIT-01c). The unit name “Box (5 kg)” is only a label; nothing converts it.
- **Forecast.** `crop_cycles.expected_quantity` (≥ 0) and `expected_harvest_date` are the forecast. No stock formula reads them. `stock_summary` reports *remaining expected* = max(expected − Σ lots harvested, 0) for non-completed cycles, in its own column. Adding a 999,999 kg forecast left on-hand, reserved and available unchanged (STK-04).

## 5. Stock ledger

Stock is never stored as a running balance. `v_lot_stock` derives it per lot from `stock_movements`:

```text
on_hand   = Σ HARVEST_ADDED + Σ CORRECTION(signed) − Σ DELIVERED − Σ LOSS − Σ DONATED − Σ DISPOSED
reserved  = Σ RESERVED − Σ RESERVATION_RELEASED − Σ DELIVERED
available = on_hand − reserved
```

All movement quantities are positive except `CORRECTION`, which may be signed. SQL enforces this with `chk_mov_nonzero` and `chk_mov_sign`.

| Event | Movements written | on_hand / reserved / available (worked example, lot of 100 kg) |
|---|---|---|
| Harvest 100 | HARVEST_ADDED 100 | 100 / 0 / 100 |
| Allocate 30 | RESERVED 30 | 100 / 30 / 70 |
| Release 30 | RESERVATION_RELEASED 30 | 100 / 0 / 100 (STK-01) |
| Loss 10, correction +2, −1 | LOSS 10, CORRECTION +2, CORRECTION −1 | 91 / 0 / 91 (STK-02) |
| Allocate 30, receive 25 | RESERVED 30; DELIVERED 25; RESERVATION_RELEASED 5; LOSS 5 | 100/30/70 → 70/0/70 (DEL-02) |
| Receive 0 of 20 | RESERVATION_RELEASED 20; LOSS 20 (no DELIVERED) | on_hand −20, available unchanged (DEL-03a) |
| Donate / dispose | DONATED or DISPOSED | on_hand and available fall equally; reserved untouched (LS-04a) |

Removal actions (loss, negative correction, donation, disposal) may use only *available* stock, so reserved stock is protected (STK-03).

## 6. Views

`v_lot_stock` gives one row per lot with farm, emirate, crop and unit joined, plus the three balances. `v_request_status` gives one row per request with `allocated_quantity` (all non-released allocations, including delivered ones) and `received_quantity` (sum of receipts). Both are recomputed on every query. The GUI and the read-only assistant read them. Relational schema page 6 documents their columns and inputs.

## 7. History, deactivation and ownership

- **History.** Movements and status changes are append-only in the application, with date, user and reason. Movement reasons are required for loss, correction, release, donation and disposal. A delivery reason is required only when there is a shortfall. Allocations are marked `RELEASED`/`DELIVERED` rather than deleted.
- **Deactivation.** Users, crops, units, markets and farms have `is_active`. Administrators toggle it (`set_active`); inactive crops and units are refused for new records (FARM-03c, existing suite). Inactive users disappear from the selector (ADM-01b). An administrator cannot deactivate their own account.
- **Ownership (data layer, not only the GUI).** Farmers change only cycles, lots, images, allocations, losses and dispositions of farms assigned to them (`farm_users`). Buyers create, update, cancel and confirm only their own market's requests and receipts. Administrators maintain users and reference data and are refused operational actions (ALC-03b, LS-05b). The user selector is a demonstration mechanism, not authentication. Read and search screens are shared across roles.

## 8. Transactions and concurrency

Each operation in `db.py` runs inside `transaction()`: one connection, commit on success, rollback on any exception. Values are always `%s` parameters. Locks use `SELECT … FOR UPDATE`.

| Operation | Locks | Writes in one transaction |
|---|---|---|
| Record harvest | cycle row | lot, HARVEST_ADDED movement, cycle → HARVESTING, optional image |
| Allocate | request row, then lot row | allocation, RESERVED movement, request status + history |
| Release | allocation row, lot row | RESERVATION_RELEASED, allocation → RELEASED, request status + history |
| Cancel request | request row, lot rows of reserved allocations | releases, allocations → RELEASED, request → CANCELLED + history |
| Confirm delivery | allocation + request rows, lot row | receipt, DELIVERED, (release + LOSS if short), allocation → DELIVERED, request status + history |
| Loss / correction / donate / dispose | lot row | one movement |

**Observed (this pass):**

- Injected failures after the first write rolled back every table. CHECKSUM TABLE was identical before and after for harvest + image, allocation, partial delivery, release, cancellation and add farm (TX-01a–f).
- Duplicate confirmations, release vs confirm, cancel vs allocate and cancel vs confirm were serialized correctly (TX-03a–d).
- **Finding F-01:** two allocations to *different* requests, or an allocation racing a donation, on the same lot can oversell it (TX-02a/b/c). The availability read in `allocate`, `dispose_lot` and `record_adjustment` is a non-locking read of `v_lot_stock`. Under MySQL's default REPEATABLE READ, it uses the snapshot created by the earlier plain SELECT in `_check_lot_owner`, taken *before* the lot lock was granted. It therefore misses the movement that the lock holder committed. The existing suite's race test uses one request, whose row lock serializes the threads first, so it does not exercise this path. The proposed fix and validation are in the [Track A review](reviews/TRACK_A_REVIEW.md#f-01-concurrent-oversell).

## 9. SQL-enforced vs application-enforced rules

| Rule | SQL | Application (`db.py`) |
|---|---|---|
| Unique names, codes and emails; one receipt per allocation; unique farm assignment | UNIQUE / PK | friendly duplicate message |
| Quantities: request > 0, lot > 0, allocation > 0, forecast ≥ 0, receipt 0…allocated, discrepancy = allocated − received, movement ≠ 0 and positive unless CORRECTION | CHECK | also parsed: max 2 decimals, ≤ 1,000,000, finite |
| Valid statuses, roles and movement types | ENUM (strict mode) | — |
| Market buyer ↔ market link | CHECK chk_user_market | role-specific forms |
| Dates: expected ≥ planting; sell-by ≥ harvest | CHECK | also harvest ≤ today, harvest ≥ planting, needed-by ≥ today |
| Image type JPEG/PNG | CHECK on MIME | extension, ≤ 5 MiB, non-empty, Pillow verify |
| Referential integrity | 32 FKs | — |
| Allocation ≤ lot available; allocation ≤ request remainder; removals ≤ available | — | row locks + checks (see F-01) |
| Lot unit = request unit = allocation/receipt/movement unit | — | checks and copying |
| Only farmers assigned to farms; ownership of every change | — | role and ownership checks |
| Status derivation and history rows | — | `_refresh_request_status` |
| Assistant is read-only | `START TRANSACTION READ ONLY` | regex validation, table allowlist, 200-row cap |

## 10. Current policies (documented, not endorsed)

These match the code and seed data. None was stated by the proposal, and none has recorded reviewer approval:

1. **DELIVERED uses allocated totals.** When no reservation remains and allocated ≥ requested, the request is DELIVERED even if less was received. Examples: seed request #6 (60 allocated / 52 received), DEL-05a and GUI-DEL-05 (150 / 140).
2. **One receipt finalises an allocation.** The shortfall is released from the reservation and recorded as LOSS. There is no second, later receipt for the remainder (DEL-04).
3. **“Approved correction”** is a farmer action with a required reason, stored with the prefix “Approved correction:”. There is no separate administrator approval step.
4. **Unallocated surplus** means “no non-RELEASED allocation”. A lot whose earlier allocations were all released qualifies (LS-06). This is not the same as “never allocated”.
5. **Donation of expired lots** is allowed; no food-safety rule is defined.
6. Loss & Surplus thresholds are adjustable per query (0–60 and 0–365, inclusive whole days) and not persisted.
