# Remaining acceptance test results — Track A (TEST-01)

**Date:** 2026-11-17 · **Tester:** Ali Alshamsi, with a Claude Code agent, on Ali's Windows PC · **Status:** Ready for review. Abd Alrahman Ismaik decides acceptance.

This report adds **new, separately executed** evidence to the existing team evidence. It does not replace it:

- [VALIDATION.md](VALIDATION.md): 65/65 business-rule checks, 18 role tabs, GUI harvest and image restart, observed on the original test PC on 2026-11-16.
- [AI_VALIDATION.md](AI_VALIDATION.md): fourteen live Gemini questions and two Ask AI GUI checks on 2026-11-17, including the initial 12/13 result, model and filter fixes, and segmented reruns.

Those results were **not** rerun by Track A, except the 65-check suite listed below. Track A ran no Gemini/LangChain checks because no API key is configured on this PC (see Blocked).

## Environment

| Item | Value |
|---|---|
| OS / Python | Windows 11 Home 10.0.26300 · Python 3.12.1 (project `.venv`) |
| Database | **Separate disposable** MySQL 8.0.46 instance created for this work: own data directory under ignored `.local/`, `127.0.0.1:3317`, root on loopback only, no other databases. The PC's normal `MySQL80` service was not used or reset |
| MySQL settings | REPEATABLE-READ (default) · `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION` |
| Packages | PyMySQL 1.2.4, cryptography 50.0.2, python-dotenv 1.2.4, Pillow 13.0.0, langchain-core 1.8.1, langchain-google-genai 4.5.0 (from `app/requirements.txt`) |
| Display | 1920×1080 at 150 % Windows scaling; GUI window 1280×701 logical |
| Seed state | Each script was run immediately after `app\setup_database.py` (fresh seed; the scripts verify exact row counts and refuse otherwise). Seed dates are relative to 2026-11-17 |

## Scripts and commands

Both new scripts **mutate data**. They do nothing on import and refuse to run unless `FARM_DISPOSABLE_DB_CONFIRM` names the exact `host:port/database` from `app/.env` and the database is untouched seed data.

```powershell
.\.venv\Scripts\python.exe app\setup_database.py                       # disposable instance only
.\.venv\Scripts\python.exe app\tests\test_business_rules.py            # existing 65-check suite
.\.venv\Scripts\python.exe app\setup_database.py
$env:FARM_DISPOSABLE_DB_CONFIRM = "127.0.0.1:3317/farm_market_db"
.\.venv\Scripts\python.exe app\tests\track_a_remaining_checks.py       # backend: 168 checks
.\.venv\Scripts\python.exe app\setup_database.py
.\.venv\Scripts\python.exe app\tests\track_a_gui_flow.py               # GUI phase 1 (Tk widgets)
.\.venv\Scripts\python.exe app\tests\track_a_gui_flow.py --restart     # GUI phase 2, new process
```

Machine-readable results: [track-a/remaining-checks.json](track-a/remaining-checks.json) (final run), [track-a/remaining-checks-run1.json](track-a/remaining-checks-run1.json) (first run, kept unchanged) and [track-a/gui-flow.json](track-a/gui-flow.json). The tables below are generated from those JSON files.

## Summary of runs (in order)

| # | Run | Result |
|---|---|---|
| 1 | Existing `test_business_rules.py`, fresh seed | **65/65 passed** on this PC (independent rerun of the existing suite) |
| 2 | `check_diagrams_vs_sql.py` (diagrams vs `information_schema`) | **851 passed, 0 failed**; 32/32 FKs drawn. Mutation test: 3 injected errors → 3 failures |
| 3 | `track_a_remaining_checks.py`, run 1 | 162 Pass · 5 Fail · 1 Info. Failures: TX-02a, TX-02b, TX-02c, TX-03z (finding F-01) and **SRCH-02a (test-oracle error, see below)** |
| 4 | `track_a_remaining_checks.py`, run 2 (after the oracle fix) | **163 Pass · 4 Fail · 1 Info.** Remaining failures are all F-01: TX-02a (19/20 trials oversold), TX-02b (deterministic), TX-02c (10/10), TX-03z (invariant check reports the oversold lots) |
| 5 | GUI flow, final clean run | **21 Pass · 1 Fail** (GUI-ALC-03, finding F-05) · 0 Blocked, including the restart phase |

**Oracle correction (SRCH-02a).** Run 1 compared the search result with `rows == []`. PyMySQL returns an empty **tuple**, so the correct empty result (“0 rows”, no error) was reported as Fail. The expectation was not changed; only the comparison was changed (`len(rows) == 0`). Run 1's JSON is preserved unedited.

**GUI run history.** The GUI script was run seven times while it was being stabilised:

- Run 1: same functional results as the final run, but its screen-grab screenshots were black.
- Run 2: same functional results; screenshots cropped by 150 % DPI virtualisation.
- Runs 3–6: disturbed by the live desktop. Windows withheld keyboard focus, minimised the window or returned blank grabs, which produced cascading or Blocked results.
- Run 6: GUI-02c failed because the harness itself moved focus onto the dialog window. This was a test artifact.

None of runs 1–6 is used as evidence, and their screenshots were deleted (console logs remain in ignored `output/test-runs/`). The fixes were all to the test harness, never the app:

- capture with Win32 `PrintWindow`, DPI-correct;
- restore the window before each capture;
- focus the main window before opening a dialog;
- record keyboard checks as Blocked when the OS grants no focus.

Every run that reached the same steps gave the same functional outcomes for allocation, delivery, status and the 1,500 pre-fill. The JSON and screenshots in `track-a/` come from the final run (run 7) only.

## Findings

Full analysis, smallest proposed fixes and required validation: [Track A review](../reviews/TRACK_A_REVIEW.md#findings). No application code, schema or seed data was changed by Track A.

| ID | Severity | Finding | Evidence |
|---|---|---|---|
| F-01 | **High** | Concurrent allocations to different requests, or an allocation racing a donation, can oversell one lot (lot ends 100/160/−60) | TX-02a 19/20, TX-02b, TX-02c 10/10; TX-02d: READ COMMITTED simulation 0/20 |
| F-02 | Policy | A request becomes DELIVERED when allocations reach the requested quantity, even if less was received | DEL-05a (30 allocated/25 received), GUI-DEL-05 (150/140), seed #6 |
| F-03 | Policy | One receipt finalises an allocation; the shortfall becomes LOSS; no later receipt | DEL-02, DEL-04 |
| F-04 | Policy | “Approved correction” = farmer + reason, with no admin approval | STK-02 |
| F-05 | Low | Allocate tab pre-fills `1,500` (thousands separator); clicking Allocate gives “must be a number” | GUI-ALC-03 |
| F-06 | Low | A JPEG truncated to half its bytes passes upload validation; buyers then see “Image unavailable” | IMG-04b (Info), IMG-04e |
| F-07 | Observation | At 150 % scaling the window is 1280×701; the Deliveries receipt table shows no rows without scrolling | [gui-deliveries-partial.png](track-a/gui-deliveries-partial.png) |
| F-08 | Policy | Lots whose allocations were all released count as “unallocated surplus” | LS-06 |

## Blocked or not covered here

| Case | Status | Reason / what is needed |
|---|---|---|
| Live LangChain/Gemini questions (AI-01…AI-15), GUI-04 (user switch while AI pending), AI service-failure variants | **Blocked** on this PC | No Gemini key configured here; existing live evidence is in AI_VALIDATION.md. Needs a key holder on the demo PC |
| GUI-03 display scaling at 100 % / 125 % and minimum window size | Not tested | Only 150 % available here; F-07 observed. Check on the demo PC |
| Full keyboard Tab-order / screen-reader accessibility | Not tested | GUI-02a–d cover only Escape, Return and initial focus in the request form |
| ERR-01 wrong password | Covered by the existing suite rerun (65/65), not repeated |  |
| ERR-01 connection dropped mid-transaction | Simulated | TX-01 injects MySQL error 2013 (connection lost) after the first write: friendly message and full rollback |
| Manual (human) end-to-end demo rehearsal | Not done | Requires the team (DEMO-01) |

## Results

### DB-01 seed

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| DB-01a | Fresh seed: exact row count of every table | {"emirates": 7, "units": 3, "crops": 6, "markets": 4, "farms": 4, "users": 8, "farm_users": 4, "crop_cycles": 10, "harvest_lots": 13, "harvest_lot_images": 12, "market_requests": 9, "request_status_history": 25, "allocations": 10, "delivery_receipts": 6, "stock_movements": 38} | {"emirates": 7, "units": 3, "crops": 6, "markets": 4, "farms": 4, "users": 8, "farm_users": 4, "crop_cycles": 10, "harvest_lots": 13, "harvest_lot_images": 12, "market_requests": 9, "request_status_history": 25, "allocations": 10, "delivery_receipts": 6, "s… | **Pass** |
| DB-01b | Seed meets every proposal minimum | {"farms": 3, "markets": 4, "crops": 5, "crop_cycles": 8, "harvest_lots": 12, "stock_movements": 15, "market_requests": 8, "delivery_receipts": 6} | farms=4, markets=4, crops=6, crop_cycles=10, harvest_lots=13, stock_movements=38, market_requests=9, delivery_receipts=6 | **Pass** |

### DB-03 seed scenarios

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| DB-03a | Seed represents available, reserved, partial, lost, discrepancy and image scenarios | every scenario count > 0 | {"available": 11, "reserved": 3, "partially_delivered": 2, "lost": 4, "discrepancy": 3, "images": 12} | **Pass** |
| DB-03b | Seed ledger invariants: no negative balance; reserved = open RESERVED allocations; one receipt per allocation | no violations | ok | **Pass** |
| DB-03c | Seed unit consistency across lot/cycle/allocation/request/receipt/movement | 0 mismatches | 0 mismatches () | **Pass** |

### DB-02 SQL constraints

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| DB-02a | Duplicate crop_name (UNIQUE) | rejected with MySQL error 1062 | MySQL 1062: Duplicate entry 'Tomato' for key 'crops.crop_name' | **Pass** |
| DB-02b | Duplicate user email (UNIQUE) | rejected with MySQL error 1062 | MySQL 1062: Duplicate entry 'omar@greenoasis.example' for key 'users.email' | **Pass** |
| DB-02c | Invalid role ENUM value (strict mode) | rejected with MySQL error 1265 | MySQL 1265: Data truncated for column 'role' at row 1 | **Pass** |
| DB-02d | Market buyer without market (chk_user_market) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_user_market' is violated. | **Pass** |
| DB-02e | Farmer with a market (chk_user_market) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_user_market' is violated. | **Pass** |
| DB-02f | Unknown FK (farm emirate 99) | rejected with MySQL error 1452 | MySQL 1452: Cannot add or update a child row: a foreign key constraint fails (`farm_market_db`.`farms` | **Pass** |
| DB-02g | Request quantity 0 (chk_req_qty) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_req_qty' is violated. | **Pass** |
| DB-02h | Lot sell-by before harvest (chk_lot_sell_by) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_lot_sell_by' is violated. | **Pass** |
| DB-02i | Cycle expected date before planting (chk_cycle_dates) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_cycle_dates' is violated. | **Pass** |
| DB-02j | Negative LOSS movement (chk_mov_sign) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_mov_sign' is violated. | **Pass** |
| DB-02k | Zero CORRECTION movement (chk_mov_nonzero) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_mov_nonzero' is violated. | **Pass** |
| DB-02l | Receipt received > allocated (chk_rcpt_max) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_rcpt_max' is violated. | **Pass** |
| DB-02m | Receipt discrepancy not equal to allocated-received (chk_rcpt_diff) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_rcpt_diff' is violated. | **Pass** |
| DB-02n | Second receipt for an allocation (UNIQUE allocation_id) | rejected with MySQL error 1062 | MySQL 1062: Duplicate entry '1' for key 'delivery_receipts.allocation_id' | **Pass** |
| DB-02o | GIF MIME type on image (chk_img_type) | rejected with MySQL error 3819 | MySQL 3819: Check constraint 'chk_img_type' is violated. | **Pass** |
| DB-02p | Duplicate farm assignment (composite PK) | rejected with MySQL error 1062 | MySQL 1062: Duplicate entry '1-2' for key 'farm_users.PRIMARY' | **Pass** |
| DB-02q | Invalid allocation status ENUM | rejected with MySQL error 1265 | MySQL 1265: Data truncated for column 'status' at row 1 | **Pass** |
| DB-02z | No table changed after the 17 rejected statements (CHECKSUM TABLE) | identical checksums | identical | **Pass** |

### HAR/FARM/REQ input validation

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| HAR-02a | Harvest quantity '0' rejected | error containing 'greater than zero' | Harvested quantity must be greater than zero. | **Pass** |
| HAR-02b | Harvest quantity '-5' rejected | error containing 'cannot be negative' | Harvested quantity cannot be negative. | **Pass** |
| HAR-02c | Harvest quantity 'NaN' rejected | error containing 'must be a number' | Harvested quantity must be a number. | **Pass** |
| HAR-02d | Harvest quantity 'Infinity' rejected | error containing 'must be a number' | Harvested quantity must be a number. | **Pass** |
| HAR-02e | Harvest quantity '1000000.01' rejected | error containing 'too large' | Harvested quantity is too large. | **Pass** |
| HAR-02f | Harvest quantity '1.234' rejected | error containing '2 decimal places' | Harvested quantity can have at most 2 decimal places. | **Pass** |
| HAR-02g | Harvest quantity 'abc' rejected | error containing 'must be a number' | Harvested quantity must be a number. | **Pass** |
| HAR-02h | Harvest quantity '' rejected | error containing 'is required' | Harvested quantity is required. | **Pass** |
| HAR-02z | No lot created by rejected quantities | 13 lots | 13 | **Pass** |
| HAR-04a | Minimum positive quantity 0.01 with blank sell-by and no photo accepted | lot created; balances 0.01/0/0.01; sell_by NULL; 0 photos | lot 14: 0.01/0/0.01; sell_by=None; photos=0 | **Pass** |
| HAR-04b | Upper boundary 1,000,000 accepted | lot created with on_hand 1000000 | 1,000,000/0/1,000,000 | **Pass** |
| HAR-03a | Harvest date one day before cycle planting date rejected | error 'before the planting date' | Harvest date cannot be before the planting date. | **Pass** |
| HAR-03b | Harvest date tomorrow rejected | error 'future' | Harvest date cannot be in the future. | **Pass** |
| HAR-03c | Impossible date 2027-02-29 rejected | error 'real date' | Harvest date must be a real date in the format YYYY-MM-DD. | **Pass** |
| HAR-03d | Sell-by equal to harvest date accepted (boundary) | lot created | lot 16 | **Pass** |
| FARM-01 | Farmer adds farm; farm and self-assignment committed together | farm row + 1 assignment | farm 6, assignments=1, visible=True | **Pass** |
| FARM-01b | Duplicate farm name rejected without orphan assignment | duplicate error; farm count unchanged | This record already exists (duplicate name or email).; farms=5 | **Pass** |
| FARM-02a | Zero-forecast cycle accepted; forecast stays separate from stock | expected 0, on_hand/reserved/available 0 | {"Tomato": {"expected": "0.00", "on_hand": "0.00", "available": "0.00"}} | **Pass** |
| FARM-02b | Harvest on a COMPLETED cycle rejected | error 'completed' | This crop cycle is completed. Choose an active cycle. | **Pass** |
| FARM-02c | Completing a cycle twice rejected | error 'already completed' | This crop cycle is already completed. | **Pass** |
| FARM-03a | Cycle expected date before planting rejected | error | Expected harvest date cannot be before the planting date. | **Pass** |
| FARM-03b | Farmer cannot add cycle to another farmer's farm | error 'assigned to you' | You can only change farms assigned to you. | **Pass** |
| FARM-03c | Inactive unit rejected for new cycle | error 'inactive' | This unit is inactive and cannot be used. | **Pass** |
| FARM-03d | Unknown crop rejected for new cycle | error 'Unknown crop' | Unknown crop. Please pick one from the list. | **Pass** |
| REQ-02a | Needed-by today accepted (boundary) | request created | request 10 | **Pass** |
| REQ-02b | Needed-by yesterday rejected | error 'past' | Needed-by date cannot be in the past. | **Pass** |
| REQ-02c | Request quantity 0 rejected | error 'greater than zero' | Requested quantity must be greater than zero. | **Pass** |
| REQ-02d | Request quantity -3 rejected | error 'negative' | Requested quantity cannot be negative. | **Pass** |
| REQ-02e | Unknown unit rejected | error 'Unknown unit' | Unknown unit. Please pick one from the list. | **Pass** |
| REQ-02f | Farmer cannot create a market request | error 'Only market buyers' | Only market buyers can do this. | **Pass** |
| REQ-01a | New request records initial status history with actor and reason | 1 row NULL->OPEN by Noura (7), reason 'Request created' | [{"old_status": "None", "new_status": "OPEN", "changed_by": "7", "reason": "Request created"}] | **Pass** |

### STK stock ledger

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| STK-04 | Large forecast (999,999 kg) changes expected only, never stock | expected +999999; on_hand/reserved/available unchanged | expected 220.00->1000219.00; stock 0/0/0->0/0/0 | **Pass** |
| STK-01 | Harvest 100 -> reserve 30 -> release 30 | 100/0/100 -> 100/30/70 -> 100/0/100 | 100/0/100 -> 100/30/70 -> 100/0/100 | **Pass** |
| STK-02 | Loss 10, correction +2, correction -1 on unreserved 100 | available 90 -> 92 -> 91; each movement has actor and reason | 90 -> 92 -> 91; LOSS 10.00 by 2 'Spoiled'; CORRECTION 2.00 by 2 'Approved correction: Recount +2'; CORRECTION -1.00 by 2 'Approved correction: Recount -1' | **Pass** |
| STK-03 | Loss/negative correction/dispose/donate of 12 when available=11 but on_hand=91 | all four rejected (reserved stock protected); balances unchanged | ['Only 11 kg is available in lot #17. Reserved stock cannot be removed.', 'Only 11 kg is available in lot #17. Reserved stock cannot be removed.', 'Only 11 kg is available in lot #17. Reserved stock cannot be donated or disposed.', 'Only 11 kg is available … | **Pass** |
| STK-03b | Loss without reason rejected | error 'Reason is required' | Reason is required. | **Pass** |
| STK-03c | Another farmer cannot record loss on this lot | error 'assigned to you' | You can only change lots from farms assigned to you. | **Pass** |

### ALC allocation

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| ALC-04 | Releasing the same allocation twice | second release rejected; exactly 1 release movement | Only reserved (not yet delivered) allocations can be released.; release movements=1 | **Pass** |
| ALC-02a | Allocate available + 0.01 (50.01 of 50) | rejected 'Not enough stock'; no allocation | Not enough stock. Lot #18 has only 50 kg available.; allocations=0 | **Pass** |
| ALC-01a | Allocate exactly the available quantity (50) | accepted; lot 50/50/0; request PARTIALLY_ALLOCATED | 50/50/0; PARTIALLY_ALLOCATED | **Pass** |
| ALC-02b | Allocate request remainder + 0.01 (20.01 when 20 remain) | rejected 'only needs 20' | The request only needs 20 kg more. | **Pass** |
| ALC-01b | Allocate exactly the remainder (20) | FULLY_ALLOCATED with one new history row | FULLY_ALLOCATED; history rows 2->3 | **Pass** |
| ALC-03a | Allocate to a FULLY_ALLOCATED request | rejected 'not open' | This request is not open for allocation. | **Pass** |
| ALC-03b | Administrator cannot allocate | rejected 'Only farmers' | Only farmers can do this. | **Pass** |
| ALC-03c | Farmer cannot allocate another farm's lot | rejected 'assigned to you' | You can only change lots from farms assigned to you. | **Pass** |

### UNIT units

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| UNIT-01a | Dates request in boxes vs Dates lot in kg | rejected 'different units' | The lot and the request use different units. Quantities in different units cannot be mixed. | **Pass** |
| UNIT-01b | Dates request in kg vs Dates lot #12 in boxes | rejected 'different units' | The lot and the request use different units. Quantities in different units cannot be mixed. | **Pass** |
| UNIT-01c | Fatima's stock summary keeps Dates (box) separate from kg crops; no duplicate crop/unit rows | one row per (crop, unit); Dates row unit = box | [["Dates", "box", "40.00"], ["Eggplant", "kg", "100.00"], ["Tomato", "kg", "220.00"]] | **Pass** |

### DEL delivery

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| DEL-02 | Allocate 30 of 100, receive 25 with 5 shortfall | receipt 30/25/5; movements RESERVED 30, DELIVERED 25, RESERVATION_RELEASED 5, LOSS 5; lot 100/30/70 -> 70/0/70 | receipt 30.00/25.00/5.00; [('RESERVED', '30.00'), ('DELIVERED', '25.00'), ('RESERVATION_RELEASED', '5.00'), ('LOSS', '5.00')]; 100/30/70 -> 70/0/70 | **Pass** |
| DEL-05a | Request fully allocated (30) but only 25 received | documents current policy: status DELIVERED | status=DELIVERED, allocated=30.00, received=25.00 | **Pass** |
| DEL-04 | Confirm the same allocation again | rejected; still exactly 1 receipt and 4 movements | This delivery was already confirmed or released.; receipts=1; movements=4 | **Pass** |
| DEL-03b | Receipt quantity '-1' reason 'x' rejected | error containing 'negative' | Received quantity cannot be negative. | **Pass** |
| DEL-03c | Receipt quantity '20.01' reason 'x' rejected | error containing 'cannot be more' | Received quantity cannot be more than the allocated 20. | **Pass** |
| DEL-03d | Receipt quantity '10' reason '' rejected | error containing 'reason' | Please enter a reason for the difference (discrepancy). | **Pass** |
| DEL-03e | Receipt quantity 'abc' reason 'x' rejected | error containing 'number' | Received quantity must be a number. | **Pass** |
| DEL-03a | Receive zero with a reason | accepted; discrepancy 20; no DELIVERED movement; release 20 + loss 20; on_hand -20 | received 0.00 discrepancy 20.00; movements ['RESERVED', 'RESERVATION_RELEASED', 'LOSS']; 70/20/50 -> 50/0/50 | **Pass** |
| DEL-01 | Full receipt of 40 | one receipt 40/0, reason NULL; one DELIVERED movement; lot 20/0/20 | 40.00/0.00 reason=None; 20/0/20 | **Pass** |

### REQ ownership

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| REQ-03a | Other market confirms this delivery | rejected 'own market' | You can only confirm deliveries for your own market. | **Pass** |
| REQ-04a | Lower request quantity below its allocation (29.99 < 30) | rejected 'less than what is already allocated' | Quantity cannot be less than what is already allocated (30). | **Pass** |
| REQ-01b | Update request quantity down to exactly the allocated amount | accepted; status FULLY_ALLOCATED | FULLY_ALLOCATED | **Pass** |
| REQ-03b | Other market edits this request | rejected 'own market' | You can only manage your own market's requests. | **Pass** |
| REQ-03c | Other market cancels this request | rejected 'own market' | You can only manage your own market's requests. | **Pass** |
| REQ-01c | Cancel request with a reserved allocation | allocation RELEASED; reservation returned; status CANCELLED | allocation RELEASED; lot 100/30/70 -> 100/0/100; request CANCELLED | **Pass** |
| REQ-04b | Edit a cancelled request | rejected | Delivered or cancelled requests cannot be changed. | **Pass** |
| REQ-04c | Cancel a request that already has a delivery | rejected | This request is already closed. | **Pass** |

### ADM admin

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| ADM-02a | Duplicate farm assignment | rejected 'already assigned' | This farmer is already assigned to that farm. | **Pass** |
| ADM-02b | Assign a market buyer to a farm | rejected 'only be assigned to farmers' | Farms can only be assigned to farmers. | **Pass** |
| ADM-02c | Invalid email | rejected 'valid email' | Please enter a valid email address. | **Pass** |
| ADM-01a | Admin deactivates own account | rejected | You cannot deactivate your own account. | **Pass** |
| ADM-01b | Deactivate then reactivate a user (history kept, row not deleted) | hidden from user selector while inactive; visible again after reactivation | hidden=True, shown=True | **Pass** |
| ADM-01c | Farmer cannot add reference data | rejected 'Only administrators' | Only administrators can do this. | **Pass** |

### SRCH search

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| SRCH-01a | Crop filter Tomato | only Tomato lots | 13 rows, crops=['Tomato'] | **Pass** |
| SRCH-01b | Emirate filter Dubai | only Hatta Valley Farm lots | farms=['Hatta Valley Farm'] | **Pass** |
| SRCH-01c | Availability 'Sold out' | only lots with on_hand <= 0 (seed lots #1, #5) | lots=[1, 5] | **Pass** |
| SRCH-01d | Availability 'Fully reserved' | only lots with available <= 0 and reserved > 0 | lots=[18] | **Pass** |
| SRCH-01e | Minimum available 100 | every row available >= 100 | 5 rows, min=100.00 | **Pass** |
| SRCH-01f | Available on a date 61 days ahead | only lots with sell_by NULL or >= that date | lots=[12, 14, 15] | **Pass** |
| SRCH-01g | Request status filter PARTIALLY_DELIVERED | seed requests #1 and #3 only | requests=[1, 3] | **Pass** |
| SRCH-02a | Empty result (unknown crop id) | 0 rows, no error | 0 rows | **Pass** |
| SRCH-02b | Invalid search input {'min_available': 'abc'} | error 'must be a number' | Minimum quantity must be a number. | **Pass** |
| SRCH-02c | Invalid search input {'min_available': '-1'} | error 'negative' | Minimum quantity cannot be negative. | **Pass** |
| SRCH-02d | Invalid search input {'date_from': '2026-11-22', 'date_to': '2026-11-18'} | error 'cannot be before' | 'To date' cannot be before 'From date'. | **Pass** |
| SRCH-02e | Invalid search input {'date_from': '2026-13-01'} | error 'real date' | From date must be a real date in the format YYYY-MM-DD. | **Pass** |

### LS Loss & Surplus

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| LS-02a | Thresholds near='0' surplus='0' | accepted | accepted | **Pass** |
| LS-02b | Thresholds near='60' surplus='365' | accepted | accepted | **Pass** |
| LS-02c | Thresholds near='-1' surplus='7' | rejected with friendly message | Use 0-60 days for expiry and 0-365 days for surplus. | **Pass** |
| LS-02d | Thresholds near='61' surplus='7' | rejected with friendly message | Use 0-60 days for expiry and 0-365 days for surplus. | **Pass** |
| LS-02e | Thresholds near='3' surplus='366' | rejected with friendly message | Use 0-60 days for expiry and 0-365 days for surplus. | **Pass** |
| LS-02f | Thresholds near='3' surplus='-1' | rejected with friendly message | Use 0-60 days for expiry and 0-365 days for surplus. | **Pass** |
| LS-02g | Thresholds near='abc' surplus='7' | rejected with friendly message | Thresholds must be whole numbers of days. | **Pass** |
| LS-02h | Thresholds near='1.5' surplus='7' | rejected with friendly message | Thresholds must be whole numbers of days. | **Pass** |
| LS-02i | Thresholds near='' surplus='7' | rejected with friendly message | Thresholds must be whole numbers of days. | **Pass** |
| LS-03a | Defaults 3/7: lot 23 sell-by today (days_left 0) | NEAR EXPIRY | NEAR EXPIRY | **Pass** |
| LS-03b | Defaults 3/7: lot 24 sell-by today+3 (=N) | NEAR EXPIRY | NEAR EXPIRY | **Pass** |
| LS-03c | Defaults 3/7: lot 25 sell-by today+4 (N+1), age 0 | not flagged | not flagged | **Pass** |
| LS-03d | Defaults 3/7: lot 26 no sell-by, age 7 (=M) | UNALLOCATED SURPLUS | UNALLOCATED SURPLUS | **Pass** |
| LS-03e | Defaults 3/7: lot 27 no sell-by, age 6 (M-1) | not flagged | not flagged | **Pass** |
| LS-01b | Defaults 3/7: lot 28 expired but fully reserved (available 0) | not flagged | not flagged | **Pass** |
| LS-06 | Defaults 3/7: lot 29 age 9, only allocation RELEASED | UNALLOCATED SURPLUS | UNALLOCATED SURPLUS | **Pass** |
| LS-03f | Near-expiry threshold 0: sell-by today is NEAR EXPIRY, not EXPIRED; today+3 not flagged | NEAR EXPIRY / not flagged | NEAR EXPIRY / not flagged | **Pass** |
| LS-01a | Seed: lot #3 EXPIRED priority 1; lot #12 surplus; ordering by priority | lot 3 EXPIRED/1, lot 12 UNALLOCATED SURPLUS/3; first row priority 1 | lot3=('EXPIRED', 1), lot12=('UNALLOCATED SURPLUS', 3), first=1 | **Pass** |
| LS-01c | Result sorted by priority (non-decreasing) | sorted | [1, 2, 2, 2, 2, 2, 2, 3, 3, 3] | **Pass** |
| LS-04a | Donate 0.01 then dispose exactly the remaining 9.99 | 9.99/0/9.99 then 0/0/0 | 9.99/0/9.99 then 0/0/0 | **Pass** |
| LS-04b | Disposition history persists actor, date, type and reason | 2 rows by Fatima Rashid with reasons | [('DISPOSED', '9.99', 'Fatima Rashid', 'Disposed: Bruised'), ('DONATED', '0.01', 'Fatima Rashid', 'Donated to: Sharjah Charity')] | **Pass** |
| LS-04c | Donate qty '0.01' note 'x' | rejected 'only 0' | Only 0 kg is available in lot #30. Reserved stock cannot be donated or disposed. | **Pass** |
| LS-04d | Donate qty '0' note 'x' | rejected 'greater than zero' | Quantity must be greater than zero. | **Pass** |
| LS-04e | Donate qty '-1' note 'x' | rejected 'negative' | Quantity cannot be negative. | **Pass** |
| LS-04f | Donate qty '1' note ' ' | rejected 'required' | Recipient / reason is required. | **Pass** |
| LS-05a | Another farmer disposes Fatima's lot | rejected 'assigned to you' | You can only change lots from farms assigned to you. | **Pass** |
| LS-05b | Administrator attempts donation | rejected 'Only farmers' | Only farmers can do this. | **Pass** |
| LS-05c | Administrator (no farm filter) sees flags across all farms | > 1 farm in result | ['Al Dhaid Fresh Farm', 'Desert Bloom Farm', 'Green Oasis Farm', 'Hatta Valley Farm'] | **Pass** |
| LS-04g | Unknown disposition action | rejected | Choose Donate or Dispose. | **Pass** |

### IMG images

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| IMG-03a | Upload missing.jpg | rejected 'not found' | The selected image file was not found. | **Pass** |
| IMG-03b | Upload empty.jpg | rejected 'empty' | The image file is empty. | **Pass** |
| IMG-03c | Upload notes.txt | rejected 'only jpg and png' | Only JPG and PNG images are allowed. | **Pass** |
| IMG-03d | Upload fake.jpg | rejected 'not a valid' | This file is not a valid JPG or PNG image. | **Pass** |
| IMG-03e | Upload over.png | rejected 'larger than 5 mb' | The image is larger than 5 MB. Please choose a smaller image. | **Pass** |
| IMG-03f | Upload anim.gif | rejected 'only jpg and png' | Only JPG and PNG images are allowed. | **Pass** |
| IMG-03g | Upload gif_named.png | rejected 'not a valid' | This file is not a valid JPG or PNG image. | **Pass** |
| IMG-04a | PNG of exactly 5 MiB (5,242,880 bytes) | accepted (limit is inclusive) | accepted | **Pass** |
| IMG-04b | JPEG truncated to half its bytes | observe: validate_image uses Pillow verify() | accepted by validate_image | **Info** |
| IMG-03z | No image row inserted by rejected uploads | 12 rows | 12 | **Pass** |
| IMG-04c | 5 MiB PNG stored as MEDIUMBLOB and read back byte-identical | SHA-256 equal | stored 5242880 bytes sha256 1d5674673aae3084… orig 1d5674673aae3084… | **Pass** |
| IMG-03h | Farmer uploads photo to another farm's lot | rejected 'assigned to you' | You can only change lots from farms assigned to you. | **Pass** |
| IMG-03i | Market buyer uploads a photo | rejected 'Only farmers' | Only farmers can do this. | **Pass** |

### TX-01 rollback

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| TX-01a | Harvest with photo: fail on image INSERT after lot + movement + cycle-status UPDATE | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01a2 | Cycle #9 status not changed by the rolled-back harvest | GROWING | GROWING | **Pass** |
| TX-01b | Allocate: fail on status-history INSERT after allocation + RESERVED movement + status UPDATE | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01c | Partial delivery: fail on LOSS movement after receipt, DELIVERED and release rows | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01d | Release: fail on status-history INSERT after release movement + allocation UPDATE | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01e | Cancel with reservation: fail on final history INSERT after release + status UPDATE | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01f | Add farm: fail on farm_users INSERT after farms INSERT | operation fails with friendly message; every table's checksum unchanged | The database connection was lost. Please try again.; tables unchanged=True | **Pass** |
| TX-01z | Ledger invariants after all injected failures | no violations | ok | **Pass** |

### TX-02/03 concurrency

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| TX-02a | 20 trials: two farmers' threads allocate 80 each from one 100 kg lot to DIFFERENT requests | at most one allocation per trial; available never negative | both succeeded in 19/20 trials; negative availability in 19/20 (e.g. ['100/160/-60', '100/160/-60', '100/160/-60']) | **Fail** |
| TX-02b | Deterministic interleaving: A reads ownership (snapshot), B allocates 80 and commits, A continues | A rejected 'Not enough stock'; lot available 20 | A=ok, B=ok; lot 100/160/-60 | **Fail** |
| TX-02c | 10 trials: allocation of 80 races a donation of 80 on one 100 kg lot | never both; available never negative | negative availability in 10/10 trials | **Fail** |
| TX-02d | Proposed-fix simulation: same 20 trials with READ COMMITTED sessions | no oversell | both succeeded 0/20; negative availability 0/20 | **Pass** |
| TX-03a | Two concurrent confirmations of one allocation | exactly one succeeds; 1 receipt; no duplicate movements | outcomes=['ok', 'This delivery was already confirmed or released.']; receipts=1; post-reservation movements=1 | **Pass** |
| TX-03b | Release races confirmation on one allocation | exactly one succeeds; allocation status matches ledger | outcomes=['Only reserved (not yet delivered) allocations can be released.', 'ok']; allocation=DELIVERED; lot 0/0/0 | **Pass** |
| TX-03c | Cancellation races allocation on one request | request CANCELLED; no RESERVED allocation left; lot 50/0/50 | outcomes=['ok', 'ok']; request=CANCELLED; reserved allocations=0; lot 50/0/50 | **Pass** |
| TX-03d | Cancellation races delivery confirmation | exactly one succeeds; consistent request/allocation/ledger | outcomes=['This request is already closed.', 'ok']; request=DELIVERED; allocation=DELIVERED; lot 0/0/0 | **Pass** |
| TX-03z | Ledger invariants after all concurrency scenarios | no lot with reserved != open RESERVED allocations; no duplicate receipt | lot problems=[(34, '100/160/-60', Decimal('160.00')), (35, '100/160/-60', Decimal('160.00')), (36, '100/160/-60', Decimal('160.00')), (37, '100/160/-60', Decimal('160.00')), (38, '100/160/-60', Decimal('160.00')), (39, '100/160/-60', Decimal('160.00')), (40… | **Fail** |

### ERR connection

| ID | Check | Expected | Actual | Outcome |
|---|---|---|---|---|
| ERR-01a | Missing database name | friendly 'database was not found' (MySQL 1049) | The database was not found. Run setup.bat first. | **Pass** |
| ERR-01b | Unreachable host (TEST-NET address) | friendly 'Cannot reach the MySQL server' within the 5 s connect timeout | Cannot reach the MySQL server. Make sure MySQL is running. after 5.1s | **Pass** |
| ERR-01c | Friendly messages contain no traceback, driver name or password | no leakage | none | **Pass** |

### GUI end-to-end (Tk widgets)

| ID | Check | Expected | Actual | Outcome | Screenshot |
|---|---|---|---|---|---|
| GUI-HAR-01 | Farmer records 12.5 kg Zucchini harvest with JPG through the form | toast 'Harvest lot #N recorded'; lot 12.5/0/12.5; one BLOB; photo shown | toast='✔ Harvest lot #14 recorded.'; stock=(12.5, 0, 12.5); photos=1; rendered=True | **Pass** | [gui-farmer-harvest.png](track-a/gui-farmer-harvest.png) |
| GUI-HAR-02 | Negative harvest quantity in the form | inline error; dialog stays open; no new lot | error='⚠ Harvested quantity cannot be negative.'; open=1; max lot=14 | **Pass** | — |
| GUI-SRCH-01 | Buyer filters Tomato with minimum 50 and selects lot #8 | only Tomato lots with available >= 50; lot #8 photo tomato_3.jpg rendered | lots=[2, 8, 13]; caption='1 / 1   tomato_3.jpg' | **Pass** | [gui-buyer-search-photo.png](track-a/gui-buyer-search-photo.png) |
| IMG-04d | Buyer selects lot #13 (seed lot without a photo) | 'No photo for this lot yet', no crash | No photo for this lot yet | **Pass** | — |
| GUI-SRCH-02 | Buyer enters minimum quantity 'abc' | friendly error dialog, no crash | ('error', 'Search', 'Minimum quantity must be a number.') | **Pass** | — |
| GUI-02a | Escape in the New request form | dialog closes; no request created | dialog open=0; requests 9->9 | **Pass** | — |
| GUI-02b | New request form opened from a selected lot pre-selects its crop and unit | crop Tomato, unit kg | crop=Tomato; unit=kg | **Pass** | — |
| GUI-02c | First text entry (Quantity) receives keyboard focus | focus on Quantity entry | focus is qty=True | **Pass** | — |
| GUI-02d | Return submits the form | dialog submits | submitted by Return | **Pass** | — |
| GUI-REQ-01 | Buyer creates 150 kg Tomato request from the selected lot (Return key) | request OPEN, 150 kg, market 3, by user 7 | #10 OPEN 150.00 market=3 by=7; toast='✔ Request #10 created.' | **Pass** | — |
| GUI-ALC-00 | Selecting the request lists only Fatima's matching Tomato kg lots and pre-fills the remainder | lots [8, 13]; quantity 150 | lots=[8, 13]; qty='150' | **Pass** | — |
| GUI-ALC-02 | Allocate 150 from lot #13 (120 available) | error 'Not enough stock… only 120'; nothing reserved | ('error', 'Action not completed', 'Not enough stock. Lot #13 has only 120 kg available.'); lot13=(120, 0, 120) | **Pass** | [gui-allocate-blocked.png](track-a/gui-allocate-blocked.png) |
| GUI-ALC-01 | Allocate 120 from lot #13, then the pre-filled remainder from lot #8 | remainder pre-filled 30; request FULLY_ALLOCATED; lot13 120/120/0; lot8 150/80/70 | remainder='30'; FULLY_ALLOCATED; lot13=(120, 120, 0); lot8=(150, 80, 70) | **Pass** | [gui-allocate-done.png](track-a/gui-allocate-done.png) |
| GUI-DEL-03 | Confirm 110 of 120 without a reason | error asking for a discrepancy reason; no receipt | ('error', 'Action not completed', 'Please enter a reason for the difference (discrepancy).'); receipts for request=0 | **Pass** | — |
| GUI-DEL-02 | Partial receipt 110/120 with reason, then full receipt 30/30 (pre-filled) | pending listed [(8,30),(13,120)]; receipts lot8 30/30/0, lot13 120/110/10 with reason; lot13 0/0/0; lot8 120/50/70 | pending=[(8, 30), (13, 120)]; prefill='30'; receipts=[(8, '30.00', '30.00', '0.00', None), (13, '120.00', '110.00', '10.00', '10 kg bruised in transit')]; lot13=(0, 0, 0); lot8=(120, 50, 70) | **Pass** | [gui-deliveries-partial.png](track-a/gui-deliveries-partial.png) |
| GUI-DEL-05 | My Requests shows the request after delivery | allocated 150, received 140; status shown per current policy (DELIVERED) | status=DELIVERED, allocated=150.00, received=140.00; allocations listed=2 | **Pass** | [gui-requests-status.png](track-a/gui-requests-status.png) |
| GUI-ALC-03 | Request of 1,500 kg: allocate using the pre-filled quantity unchanged | observe pre-fill format and result (Deliveries tab strips thousands separators; Allocate tab?) | prefill='1,500'; ('error', 'Action not completed', 'Allocation quantity must be a number.'); lot8=(120, 50, 70) | **Fail** | — |
| GUI-LS-02a | Near-expiry spinbox 'abc' then Apply | friendly 'Invalid threshold' dialog | ('error', 'Invalid threshold', 'Thresholds must be whole numbers of days.') | **Pass** | — |
| GUI-LS-02b | Near-expiry spinbox '61' then Apply | friendly 'Invalid threshold' dialog | ('error', 'Invalid threshold', 'Use 0-60 days for expiry and 0-365 days for surplus.') | **Pass** | — |
| GUI-LS-01 | Valid thresholds 3/7 for Fatima | only Fatima's farm; rows sorted by priority | 2 rows, farms=['Al Dhaid Fresh Farm'], priorities=[2, 3] | **Pass** | [gui-loss-surplus.png](track-a/gui-loss-surplus.png) |
| IMG-04e | Lot #10 with a truncated JPEG (accepted by upload validation) and a corrupt BLOB | upload of truncated file: observe; both unreadable photos show '⚠ Image unavailable' without crashing | upload=accepted; newest=('1 / 3   truncated_eggplant.jpg', '⚠ Image unavailable'); next=('2 / 3   corrupt.jpg', '⚠ Image unavailable') | **Pass** | [gui-image-unavailable.png](track-a/gui-image-unavailable.png) |
| GUI-IMG-02 | New process: buyer finds the GUI-uploaded lot and its photo renders | lot 14 listed; photo rendered; caption 'zucchini.jpg'; stored bytes unchanged | listed=True; rendered=True; caption='1 / 1   zucchini.jpg'; sha256 equal=True | **Pass** | [gui-restart-photo.png](track-a/gui-restart-photo.png) |
