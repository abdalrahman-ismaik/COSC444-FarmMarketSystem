"""Track A remaining acceptance checks (backend, embedded SQL, transactions, concurrency).

!!! MUTATES DATA. Run ONLY on a disposable MySQL instance loaded with fresh seed data. !!!

Safety guards (the script refuses to run otherwise):
  * nothing runs on import; only `python app/tests/track_a_remaining_checks.py` executes;
  * env FARM_DISPOSABLE_DB_CONFIRM must equal "<DB_HOST>:<DB_PORT>/<DB_NAME>" from app/.env;
  * the database must still hold the untouched seed (exact row counts and lot balances).

Typical run (PowerShell, repository root, disposable server already configured in app/.env):
  .\\.venv\\Scripts\\python.exe app\\setup_database.py
  $env:FARM_DISPOSABLE_DB_CONFIRM = "127.0.0.1:3317/farm_market_db"
  .\\.venv\\Scripts\\python.exe app\\tests\\track_a_remaining_checks.py

Writes docs/evidence/track-a/remaining-checks.json and prints one line per check.
This script does not modify application code. A few checks simulate a proposed fix by
patching the connection inside this process only; they are labelled "proposed-fix simulation".
"""
import datetime as dt
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import re
import sys
import tempfile
import threading
import time
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
ROOT = os.path.dirname(APP)
OUT_DIR = os.path.join(ROOT, "docs", "evidence", "track-a")

RESULTS = []
TODAY = dt.date.today()


def iso(days=0):
    return (TODAY + dt.timedelta(days=days)).isoformat()


def record(cid, title, expected, actual, outcome, group, notes=""):
    RESULTS.append(dict(id=cid, group=group, title=title, expected=expected, actual=str(actual),
                        outcome=outcome, notes=notes))
    print(f"{outcome:<7} {cid:<9} {title}" + ("" if outcome == "Pass" else f"  ->  {actual}"))


def guard():
    sys.path.insert(0, APP)
    import db  # noqa: E402  (loads app/.env)
    s = db.db_settings()
    target = f"{s['host']}:{s['port']}/{s['database']}"
    if os.environ.get("FARM_DISPOSABLE_DB_CONFIRM") != target:
        sys.exit(f"Refusing to run: set FARM_DISPOSABLE_DB_CONFIRM={target} only if that database is disposable.")
    return db


def main():
    db = guard()
    import pymysql
    q, q1 = db.query, db.query_one

    def stock(lot):
        r = q1("SELECT on_hand, reserved, available FROM v_lot_stock WHERE lot_id=%s", (lot,))
        return (r["on_hand"], r["reserved"], r["available"])

    def fmt3(t):
        return "/".join(db.fmt_qty(x) for x in t)

    def err(fn, *a):
        try:
            fn(*a)
        except Exception as e:  # noqa: BLE001
            return db.friendly_error(e)
        return None

    TABLES = ["emirates", "units", "crops", "markets", "farms", "users", "farm_users", "crop_cycles",
              "harvest_lots", "harvest_lot_images", "market_requests", "request_status_history",
              "allocations", "delivery_receipts", "stock_movements"]

    def fingerprint():
        rows = q("CHECKSUM TABLE " + ", ".join(TABLES))
        return {r["Table"].split(".")[-1]: r["Checksum"] for r in rows}

    def counts():
        return {t: q1(f"SELECT COUNT(*) n FROM {t}")["n"] for t in TABLES}

    def invariants():
        """Ledger invariants that must hold after every operation."""
        bad = q("""SELECT s.lot_id, s.on_hand, s.reserved, s.available,
                          COALESCE((SELECT SUM(a.allocated_quantity) FROM allocations a
                                    WHERE a.lot_id=s.lot_id AND a.status='RESERVED'),0) AS open_alloc
                   FROM v_lot_stock s""")
        problems = [r for r in bad if r["on_hand"] < 0 or r["reserved"] < 0 or r["available"] < 0
                    or r["reserved"] != r["open_alloc"]]
        dup = q("SELECT allocation_id FROM delivery_receipts GROUP BY allocation_id HAVING COUNT(*)>1")
        deliv_no_rcpt = q("""SELECT a.allocation_id FROM allocations a LEFT JOIN delivery_receipts d
                             ON d.allocation_id=a.allocation_id WHERE a.status='DELIVERED' AND d.receipt_id IS NULL""")
        return problems, dup, deliv_no_rcpt

    def inv_ok():
        p, d, n = invariants()
        return (not p and not d and not n), f"lot problems={[(r['lot_id'], fmt3((r['on_hand'], r['reserved'], r['available'])), r['open_alloc']) for r in p]} dup_receipts={d} delivered_without_receipt={n}"

    U = {i: db.get_user(i) for i in range(1, 9)}
    admin, omar, fatima, khalid = U[1], U[2], U[3], U[4]
    aisha, yousef, noura, hamad = U[5], U[6], U[7], U[8]

    # ---------------------------------------------------------------- environment
    env = {
        "date": TODAY.isoformat(),
        "python": platform.python_version(), "os": platform.platform(),
        "mysql": q1("SELECT VERSION() v")["v"],
        "isolation": q1("SELECT @@transaction_isolation i")["i"],
        "sql_mode": q1("SELECT @@sql_mode m")["m"],
        "pymysql": importlib.metadata.version("PyMySQL"),
        "target": f"{db.db_settings()['host']}:{db.db_settings()['port']}/{db.db_settings()['database']}",
    }
    print("Environment:", json.dumps(env))

    # ---------------------------------------------------------------- DB-01 fresh seed
    G = "DB-01 seed"
    expected_counts = {"emirates": 7, "units": 3, "crops": 6, "markets": 4, "farms": 4, "users": 8,
                       "farm_users": 4, "crop_cycles": 10, "harvest_lots": 13, "harvest_lot_images": 12,
                       "market_requests": 9, "request_status_history": 25, "allocations": 10,
                       "delivery_receipts": 6, "stock_movements": 38}
    c = counts()
    if c != expected_counts or stock(2) != (78, 0, 78):
        sys.exit(f"Refusing to run: database is not fresh seed data. counts={c}")
    record("DB-01a", "Fresh seed: exact row count of every table", json.dumps(expected_counts), json.dumps(c),
           "Pass", G)
    mins = {"farms": 3, "markets": 4, "crops": 5, "crop_cycles": 8, "harvest_lots": 12, "stock_movements": 15,
            "market_requests": 8, "delivery_receipts": 6}
    record("DB-01b", "Seed meets every proposal minimum", json.dumps(mins),
           ", ".join(f"{k}={c[k]}" for k in mins), "Pass" if all(c[k] >= v for k, v in mins.items()) else "Fail", G)
    scen = {
        "available": q1("SELECT COUNT(*) n FROM v_lot_stock WHERE available>0")["n"],
        "reserved": q1("SELECT COUNT(*) n FROM v_lot_stock WHERE reserved>0")["n"],
        "partially_delivered": q1("SELECT COUNT(*) n FROM market_requests WHERE status='PARTIALLY_DELIVERED'")["n"],
        "lost": q1("SELECT COUNT(*) n FROM stock_movements WHERE movement_type='LOSS'")["n"],
        "discrepancy": q1("SELECT COUNT(*) n FROM delivery_receipts WHERE discrepancy_quantity>0")["n"],
        "images": q1("SELECT COUNT(*) n FROM harvest_lot_images")["n"],
    }
    record("DB-03a", "Seed represents available, reserved, partial, lost, discrepancy and image scenarios",
           "every scenario count > 0", json.dumps(scen), "Pass" if all(scen.values()) else "Fail", "DB-03 seed scenarios")
    ok, detail = inv_ok()
    record("DB-03b", "Seed ledger invariants: no negative balance; reserved = open RESERVED allocations; "
           "one receipt per allocation", "no violations", "ok" if ok else detail, "Pass" if ok else "Fail",
           "DB-03 seed scenarios")
    unit_mix = q("""SELECT 'movement' k, m.movement_id id FROM stock_movements m JOIN harvest_lots l ON l.lot_id=m.lot_id
                    WHERE m.unit_id<>l.unit_id
                    UNION ALL SELECT 'allocation-lot', a.allocation_id FROM allocations a JOIN harvest_lots l
                    ON l.lot_id=a.lot_id WHERE a.unit_id<>l.unit_id
                    UNION ALL SELECT 'allocation-request', a.allocation_id FROM allocations a JOIN market_requests r
                    ON r.request_id=a.request_id WHERE a.unit_id<>r.unit_id
                    UNION ALL SELECT 'receipt', d.receipt_id FROM delivery_receipts d JOIN allocations a
                    ON a.allocation_id=d.allocation_id WHERE d.unit_id<>a.unit_id
                    UNION ALL SELECT 'lot-cycle', l.lot_id FROM harvest_lots l JOIN crop_cycles cc
                    ON cc.cycle_id=l.cycle_id WHERE l.unit_id<>cc.unit_id""")
    record("DB-03c", "Seed unit consistency across lot/cycle/allocation/request/receipt/movement",
           "0 mismatches", f"{len(unit_mix)} mismatches {unit_mix}", "Pass" if not unit_mix else "Fail",
           "DB-03 seed scenarios")

    # ---------------------------------------------------------------- DB-02 SQL constraints
    G = "DB-02 SQL constraints"
    before = fingerprint()
    sql_cases = [
        ("DB-02a", "Duplicate crop_name (UNIQUE)", "INSERT INTO crops (crop_name, default_unit_id) VALUES ('Tomato',1)", 1062),
        ("DB-02b", "Duplicate user email (UNIQUE)",
         "INSERT INTO users (full_name,email,role) VALUES ('X','omar@greenoasis.example','farmer')", 1062),
        ("DB-02c", "Invalid role ENUM value (strict mode)",
         "INSERT INTO users (full_name,email,role) VALUES ('X','x1@t.example','owner')", 1265),
        ("DB-02d", "Market buyer without market (chk_user_market)",
         "INSERT INTO users (full_name,email,role) VALUES ('X','x2@t.example','market')", 3819),
        ("DB-02e", "Farmer with a market (chk_user_market)",
         "INSERT INTO users (full_name,email,role,market_id) VALUES ('X','x3@t.example','farmer',1)", 3819),
        ("DB-02f", "Unknown FK (farm emirate 99)", "INSERT INTO farms (farm_name, emirate_id) VALUES ('Ghost',99)", 1452),
        ("DB-02g", "Request quantity 0 (chk_req_qty)",
         f"INSERT INTO market_requests (market_id,crop_id,requested_quantity,unit_id,needed_by_date,created_by) "
         f"VALUES (1,1,0,1,'{iso(3)}',5)", 3819),
        ("DB-02h", "Lot sell-by before harvest (chk_lot_sell_by)",
         "INSERT INTO harvest_lots (cycle_id,quantity_harvested,unit_id,harvest_date,sell_by_date,created_by) "
         "VALUES (1,5,1,'2026-11-10','2026-11-01',2)", 3819),
        ("DB-02i", "Cycle expected date before planting (chk_cycle_dates)",
         "INSERT INTO crop_cycles (farm_id,crop_id,planting_date,expected_harvest_date,expected_quantity,unit_id,created_by) "
         "VALUES (1,1,'2026-11-10','2026-11-01',5,1,2)", 3819),
        ("DB-02j", "Negative LOSS movement (chk_mov_sign)",
         "INSERT INTO stock_movements (lot_id,movement_type,quantity,unit_id,user_id) VALUES (2,'LOSS',-1,1,2)", 3819),
        ("DB-02k", "Zero CORRECTION movement (chk_mov_nonzero)",
         "INSERT INTO stock_movements (lot_id,movement_type,quantity,unit_id,user_id) VALUES (2,'CORRECTION',0,1,2)", 3819),
        ("DB-02l", "Receipt received > allocated (chk_rcpt_max)",
         f"INSERT INTO delivery_receipts (allocation_id,allocated_quantity,received_quantity,discrepancy_quantity,unit_id,"
         f"received_date,confirmed_by) VALUES (2,50,60,-10,1,'{iso()}',5)", 3819),
        ("DB-02m", "Receipt discrepancy not equal to allocated-received (chk_rcpt_diff)",
         f"INSERT INTO delivery_receipts (allocation_id,allocated_quantity,received_quantity,discrepancy_quantity,unit_id,"
         f"received_date,confirmed_by) VALUES (2,50,40,5,1,'{iso()}',5)", 3819),
        ("DB-02n", "Second receipt for an allocation (UNIQUE allocation_id)",
         f"INSERT INTO delivery_receipts (allocation_id,allocated_quantity,received_quantity,discrepancy_quantity,unit_id,"
         f"received_date,confirmed_by) VALUES (1,100,100,0,1,'{iso()}',5)", 1062),
        ("DB-02o", "GIF MIME type on image (chk_img_type)",
         "INSERT INTO harvest_lot_images (lot_id,file_name,mime_type,image_data,uploaded_by) VALUES (13,'a.gif','image/gif',x'00',2)", 3819),
        ("DB-02p", "Duplicate farm assignment (composite PK)", "INSERT INTO farm_users (farm_id,user_id) VALUES (1,2)", 1062),
        ("DB-02q", "Invalid allocation status ENUM",
         "INSERT INTO allocations (request_id,lot_id,allocated_quantity,unit_id,status,allocated_by) VALUES (7,2,1,1,'PENDING',2)", 1265),
    ]
    conn = db.get_connection()
    try:
        for cid, title, sql, code in sql_cases:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                got = "accepted (no error)"
            except pymysql.err.MySQLError as e:
                got = f"MySQL {e.args[0]}: {e.args[1][:90]}"
            finally:
                conn.rollback()
            record(cid, title, f"rejected with MySQL error {code}", got,
                   "Pass" if got.startswith(f"MySQL {code}:") else "Fail", G)
    finally:
        conn.close()
    after = fingerprint()
    record("DB-02z", "No table changed after the 17 rejected statements (CHECKSUM TABLE)", "identical checksums",
           "identical" if before == after else f"changed: {[t for t in before if before[t] != after[t]]}",
           "Pass" if before == after else "Fail", G)

    # ---------------------------------------------------------------- input validation (HAR, FARM, REQ)
    G = "HAR/FARM/REQ input validation"
    n_lots = c["harvest_lots"]
    for cid, val, want in [("HAR-02a", "0", "greater than zero"), ("HAR-02b", "-5", "cannot be negative"),
                           ("HAR-02c", "NaN", "must be a number"), ("HAR-02d", "Infinity", "must be a number"),
                           ("HAR-02e", "1000000.01", "too large"), ("HAR-02f", "1.234", "2 decimal places"),
                           ("HAR-02g", "abc", "must be a number"), ("HAR-02h", "", "is required")]:
        got = err(db.record_harvest, omar, 1, val, iso(), "", None)
        record(cid, f"Harvest quantity {val!r} rejected", f"error containing '{want}'", got,
               "Pass" if got and want in got.lower() else "Fail", G)
    record("HAR-02z", "No lot created by rejected quantities", f"{n_lots} lots",
           q1("SELECT COUNT(*) n FROM harvest_lots")["n"],
           "Pass" if q1("SELECT COUNT(*) n FROM harvest_lots")["n"] == n_lots else "Fail", G)
    lot_min = db.record_harvest(omar, 1, "0.01", iso(), "", None)
    record("HAR-04a", "Minimum positive quantity 0.01 with blank sell-by and no photo accepted",
           "lot created; balances 0.01/0/0.01; sell_by NULL; 0 photos",
           f"lot {lot_min}: {fmt3(stock(lot_min))}; sell_by={q1('SELECT sell_by_date s FROM harvest_lots WHERE lot_id=%s', (lot_min,))['s']}; "
           f"photos={len(db.lot_images(lot_min))}",
           "Pass" if stock(lot_min) == (Decimal('0.01'), 0, Decimal('0.01')) and not db.lot_images(lot_min) else "Fail", G)
    lot_max = db.record_harvest(omar, 1, "1000000", iso(), "", None)
    record("HAR-04b", "Upper boundary 1,000,000 accepted", "lot created with on_hand 1000000",
           fmt3(stock(lot_max)), "Pass" if stock(lot_max)[0] == 1000000 else "Fail", G)
    cyc1 = q1("SELECT planting_date p FROM crop_cycles WHERE cycle_id=1")["p"]
    got = err(db.record_harvest, omar, 1, "5", (cyc1 - dt.timedelta(days=1)).isoformat(), "", None)
    record("HAR-03a", "Harvest date one day before cycle planting date rejected", "error 'before the planting date'",
           got, "Pass" if got and "before the planting" in got else "Fail", G)
    got = err(db.record_harvest, omar, 1, "5", iso(1), "", None)
    record("HAR-03b", "Harvest date tomorrow rejected", "error 'future'", got,
           "Pass" if got and "future" in got else "Fail", G)
    got = err(db.record_harvest, omar, 1, "5", "2027-02-29", "", None)
    record("HAR-03c", "Impossible date 2027-02-29 rejected", "error 'real date'", got,
           "Pass" if got and "real date" in got else "Fail", G)
    lot_same = db.record_harvest(omar, 1, "5", iso(), iso(), None)
    record("HAR-03d", "Sell-by equal to harvest date accepted (boundary)", "lot created", f"lot {lot_same}",
           "Pass" if lot_same else "Fail", G)

    fid = db.add_farm(omar, "Track A Test Farm", 1, "Al Ain")
    assigned = q1("SELECT COUNT(*) n FROM farm_users WHERE farm_id=%s AND user_id=2", (fid,))["n"]
    record("FARM-01", "Farmer adds farm; farm and self-assignment committed together", "farm row + 1 assignment",
           f"farm {fid}, assignments={assigned}, visible={fid in db.my_farm_ids(2)}",
           "Pass" if assigned == 1 and fid in db.my_farm_ids(2) else "Fail", G)
    got = err(db.add_farm, omar, "Green Oasis Farm", 1, "")
    record("FARM-01b", "Duplicate farm name rejected without orphan assignment", "duplicate error; farm count unchanged",
           f"{got}; farms={q1('SELECT COUNT(*) n FROM farms')['n']}",
           "Pass" if got and "already exists" in got and q1("SELECT COUNT(*) n FROM farms")["n"] == 5 else "Fail", G)
    cyc0 = db.add_cycle(omar, fid, 1, iso(), iso(30), "0", 1)
    summ = {(r["crop_name"], r["unit_code"]): r for r in db.stock_summary({fid})}
    record("FARM-02a", "Zero-forecast cycle accepted; forecast stays separate from stock",
           "expected 0, on_hand/reserved/available 0", json.dumps({k[0]: {x: str(v[x]) for x in ('expected', 'on_hand', 'available')} for k, v in summ.items()}),
           "Pass" if summ[("Tomato", "kg")]["expected"] == 0 and summ[("Tomato", "kg")]["on_hand"] == 0 else "Fail", G)
    db.complete_cycle(omar, cyc0)
    got = err(db.record_harvest, omar, cyc0, "5", iso(), "", None)
    record("FARM-02b", "Harvest on a COMPLETED cycle rejected", "error 'completed'", got,
           "Pass" if got and "completed" in got else "Fail", G)
    got = err(db.complete_cycle, omar, cyc0)
    record("FARM-02c", "Completing a cycle twice rejected", "error 'already completed'", got,
           "Pass" if got and "already completed" in got else "Fail", G)
    got = err(db.add_cycle, omar, fid, 1, iso(), iso(-1), "10", 1)
    record("FARM-03a", "Cycle expected date before planting rejected", "error", got,
           "Pass" if got and "before the planting" in got else "Fail", G)
    got = err(db.add_cycle, fatima, fid, 1, iso(), iso(5), "10", 1)
    record("FARM-03b", "Farmer cannot add cycle to another farmer's farm", "error 'assigned to you'", got,
           "Pass" if got and "assigned to you" in got else "Fail", G)
    db.set_active(admin, "units", 3, False)
    got = err(db.add_cycle, omar, fid, 1, iso(), iso(5), "10", 3)
    db.set_active(admin, "units", 3, True)
    record("FARM-03c", "Inactive unit rejected for new cycle", "error 'inactive'", got,
           "Pass" if got and "inactive" in got else "Fail", G)
    got = err(db.add_cycle, omar, fid, 999, iso(), iso(5), "10", 1)
    record("FARM-03d", "Unknown crop rejected for new cycle", "error 'Unknown crop'", got,
           "Pass" if got and "unknown crop" in got.lower() else "Fail", G)
    before_exp = {(r["crop_name"], r["unit_code"]): r for r in db.stock_summary({1})}[("Bell Pepper", "kg")]
    db.add_cycle(omar, 1, 4, iso(), iso(60), "999999", 1)
    after_exp = {(r["crop_name"], r["unit_code"]): r for r in db.stock_summary({1})}[("Bell Pepper", "kg")]
    record("STK-04", "Large forecast (999,999 kg) changes expected only, never stock",
           "expected +999999; on_hand/reserved/available unchanged",
           f"expected {before_exp['expected']}->{after_exp['expected']}; stock "
           f"{fmt3((before_exp['on_hand'], before_exp['reserved'], before_exp['available']))}->"
           f"{fmt3((after_exp['on_hand'], after_exp['reserved'], after_exp['available']))}",
           "Pass" if after_exp["expected"] - before_exp["expected"] == 999999 and
           (after_exp["on_hand"], after_exp["available"]) == (before_exp["on_hand"], before_exp["available"]) else "Fail",
           "STK stock ledger")

    rq_today = db.create_request(noura, 1, "10", 1, iso(), "today")
    record("REQ-02a", "Needed-by today accepted (boundary)", "request created", f"request {rq_today}", "Pass", G)
    got = err(db.create_request, noura, 1, "10", 1, iso(-1), "")
    record("REQ-02b", "Needed-by yesterday rejected", "error 'past'", got, "Pass" if got and "past" in got else "Fail", G)
    for cid, val, want in [("REQ-02c", "0", "greater than zero"), ("REQ-02d", "-3", "negative")]:
        got = err(db.create_request, noura, 1, val, 1, iso(3), "")
        record(cid, f"Request quantity {val} rejected", f"error '{want}'", got,
               "Pass" if got and want in got else "Fail", G)
    got = err(db.create_request, noura, 1, "5", 99, iso(3), "")
    record("REQ-02e", "Unknown unit rejected", "error 'Unknown unit'", got,
           "Pass" if got and "unknown unit" in got.lower() else "Fail", G)
    got = err(db.create_request, omar, 1, "5", 1, iso(3), "")
    record("REQ-02f", "Farmer cannot create a market request", "error 'Only market buyers'", got,
           "Pass" if got and "only market buyers" in got.lower() else "Fail", G)
    hist = q("SELECT old_status, new_status, changed_by, reason FROM request_status_history WHERE request_id=%s", (rq_today,))
    record("REQ-01a", "New request records initial status history with actor and reason",
           "1 row NULL->OPEN by Noura (7), reason 'Request created'", json.dumps([{k: str(v) for k, v in h.items()} for h in hist]),
           "Pass" if len(hist) == 1 and hist[0]["new_status"] == "OPEN" and hist[0]["changed_by"] == 7 else "Fail", G)

    # ---------------------------------------------------------------- stock ledger sequences
    G = "STK stock ledger"
    L = db.record_harvest(omar, 1, "100", iso(), iso(10), None)
    r1 = db.create_request(aisha, 1, "30", 1, iso(5), "STK-01")
    seq = [stock(L)]
    a1 = db.allocate(omar, r1, L, "30")
    seq.append(stock(L))
    db.release_allocation(omar, a1, "STK-01 release")
    seq.append(stock(L))
    record("STK-01", "Harvest 100 -> reserve 30 -> release 30", "100/0/100 -> 100/30/70 -> 100/0/100",
           " -> ".join(fmt3(s) for s in seq),
           "Pass" if seq == [(100, 0, 100), (100, 30, 70), (100, 0, 100)] else "Fail", G)
    got = err(db.release_allocation, omar, a1, "again")
    n_rel = q1("SELECT COUNT(*) n FROM stock_movements WHERE allocation_id=%s AND movement_type='RESERVATION_RELEASED'", (a1,))["n"]
    record("ALC-04", "Releasing the same allocation twice", "second release rejected; exactly 1 release movement",
           f"{got}; release movements={n_rel}", "Pass" if got and "only reserved" in got.lower() and n_rel == 1 else "Fail",
           "ALC allocation")
    seq = []
    db.record_adjustment(omar, L, "LOSS", "10", "Spoiled")
    seq.append(stock(L))
    db.record_adjustment(omar, L, "CORRECTION", "2", "Recount +2")
    seq.append(stock(L))
    db.record_adjustment(omar, L, "CORRECTION", "-1", "Recount -1")
    seq.append(stock(L))
    movs = q("SELECT movement_type, quantity, user_id, reason FROM stock_movements WHERE lot_id=%s AND movement_type IN ('LOSS','CORRECTION') ORDER BY movement_id", (L,))
    record("STK-02", "Loss 10, correction +2, correction -1 on unreserved 100",
           "available 90 -> 92 -> 91; each movement has actor and reason",
           " -> ".join(db.fmt_qty(s[2]) for s in seq) + "; " + "; ".join(f"{m['movement_type']} {m['quantity']} by {m['user_id']} '{m['reason']}'" for m in movs),
           "Pass" if [s[2] for s in seq] == [90, 92, 91] and all(m["user_id"] == 2 and m["reason"] for m in movs) else "Fail", G)
    r2 = db.create_request(aisha, 1, "80", 1, iso(5), "STK-03")
    a2 = db.allocate(omar, r2, L, "80")   # L: on_hand 91, reserved 80, available 11
    s_before = stock(L)
    outs = [err(db.record_adjustment, omar, L, "LOSS", "12", "too much"),
            err(db.record_adjustment, omar, L, "CORRECTION", "-12", "too much"),
            err(db.dispose_lot, omar, L, "DISPOSED", "12", "too much"),
            err(db.dispose_lot, omar, L, "DONATED", "12", "too much")]
    record("STK-03", "Loss/negative correction/dispose/donate of 12 when available=11 but on_hand=91",
           "all four rejected (reserved stock protected); balances unchanged",
           f"{outs}; {fmt3(s_before)} -> {fmt3(stock(L))}",
           "Pass" if all(o and "reserved stock" in o.lower() for o in outs) and stock(L) == s_before else "Fail", G)
    got = err(db.record_adjustment, omar, L, "LOSS", "5", "  ")
    record("STK-03b", "Loss without reason rejected", "error 'Reason is required'", got,
           "Pass" if got and "reason is required" in got.lower() else "Fail", G)
    got = err(db.record_adjustment, fatima, L, "LOSS", "1", "x")
    record("STK-03c", "Another farmer cannot record loss on this lot", "error 'assigned to you'", got,
           "Pass" if got and "assigned to you" in got else "Fail", G)
    db.release_allocation(omar, a2, "cleanup")

    # ---------------------------------------------------------------- allocation boundaries
    G = "ALC allocation"
    L2 = db.record_harvest(omar, 1, "50", iso(), iso(10), None)
    rq = db.create_request(hamad, 1, "70", 1, iso(5), "ALC")
    got = err(db.allocate, omar, rq, L2, "50.01")
    record("ALC-02a", "Allocate available + 0.01 (50.01 of 50)", "rejected 'Not enough stock'; no allocation",
           f"{got}; allocations={q1('SELECT COUNT(*) n FROM allocations WHERE request_id=%s', (rq,))['n']}",
           "Pass" if got and "not enough stock" in got.lower() else "Fail", G)
    a_exact = db.allocate(omar, rq, L2, "50")
    record("ALC-01a", "Allocate exactly the available quantity (50)", "accepted; lot 50/50/0; request PARTIALLY_ALLOCATED",
           f"{fmt3(stock(L2))}; {q1('SELECT status FROM market_requests WHERE request_id=%s', (rq,))['status']}",
           "Pass" if stock(L2) == (50, 50, 0) and q1('SELECT status FROM market_requests WHERE request_id=%s', (rq,))['status'] == "PARTIALLY_ALLOCATED" else "Fail", G)
    L3 = db.record_harvest(omar, 1, "40", iso(), iso(10), None)
    got = err(db.allocate, omar, rq, L3, "20.01")
    record("ALC-02b", "Allocate request remainder + 0.01 (20.01 when 20 remain)", "rejected 'only needs 20'", got,
           "Pass" if got and "only needs 20" in got else "Fail", G)
    hist_n = q1("SELECT COUNT(*) n FROM request_status_history WHERE request_id=%s", (rq,))["n"]
    db.allocate(omar, rq, L3, "20")
    st = q1("SELECT status FROM market_requests WHERE request_id=%s", (rq,))["status"]
    hist_n2 = q1("SELECT COUNT(*) n FROM request_status_history WHERE request_id=%s", (rq,))["n"]
    record("ALC-01b", "Allocate exactly the remainder (20)", "FULLY_ALLOCATED with one new history row",
           f"{st}; history rows {hist_n}->{hist_n2}", "Pass" if st == "FULLY_ALLOCATED" and hist_n2 == hist_n + 1 else "Fail", G)
    got = err(db.allocate, omar, rq, L3, "1")
    record("ALC-03a", "Allocate to a FULLY_ALLOCATED request", "rejected 'not open'", got,
           "Pass" if got and "not open" in got else "Fail", G)
    rq_box = db.create_request(aisha, 3, "5", 2, iso(5), "Dates in boxes")
    got = err(db.allocate, omar, rq_box, 6, "5")
    record("UNIT-01a", "Dates request in boxes vs Dates lot in kg", "rejected 'different units'", got,
           "Pass" if got and "different units" in got else "Fail", "UNIT units")
    rq_dkg = db.create_request(aisha, 3, "5", 1, iso(5), "Dates kg")
    got = err(db.allocate, fatima, rq_dkg, 12, "5")
    record("UNIT-01b", "Dates request in kg vs Dates lot #12 in boxes", "rejected 'different units'", got,
           "Pass" if got and "different units" in got else "Fail", "UNIT units")
    summ3 = db.stock_summary({3})
    keys = [(r["crop_name"], r["unit_code"]) for r in summ3]
    record("UNIT-01c", "Fatima's stock summary keeps Dates (box) separate from kg crops; no duplicate crop/unit rows",
           "one row per (crop, unit); Dates row unit = box",
           json.dumps([(r['crop_name'], r['unit_code'], str(r['available'])) for r in summ3]),
           "Pass" if len(keys) == len(set(keys)) and ("Dates", "box") in keys else "Fail", "UNIT units")
    got = err(db.allocate, admin, rq_dkg, 6, "1")
    record("ALC-03b", "Administrator cannot allocate", "rejected 'Only farmers'", got,
           "Pass" if got and "only farmers" in got.lower() else "Fail", G)
    got = err(db.allocate, khalid, rq_dkg, 6, "1")
    record("ALC-03c", "Farmer cannot allocate another farm's lot", "rejected 'assigned to you'", got,
           "Pass" if got and "assigned to you" in got else "Fail", G)

    # ---------------------------------------------------------------- deliveries
    G = "DEL delivery"
    L4 = db.record_harvest(omar, 1, "100", iso(), iso(10), None)
    rq4 = db.create_request(yousef, 1, "30", 1, iso(5), "DEL-02")
    a4 = db.allocate(omar, rq4, L4, "30")
    s_mid = stock(L4)
    db.confirm_delivery(yousef, a4, "25", "5 kg crushed")
    rc = q1("SELECT allocated_quantity a, received_quantity r, discrepancy_quantity d FROM delivery_receipts WHERE allocation_id=%s", (a4,))
    mv = q("SELECT movement_type t, quantity qty FROM stock_movements WHERE allocation_id=%s ORDER BY movement_id", (a4,))
    record("DEL-02", "Allocate 30 of 100, receive 25 with 5 shortfall",
           "receipt 30/25/5; movements RESERVED 30, DELIVERED 25, RESERVATION_RELEASED 5, LOSS 5; lot 100/30/70 -> 70/0/70",
           f"receipt {rc['a']}/{rc['r']}/{rc['d']}; {[(m['t'], str(m['qty'])) for m in mv]}; {fmt3(s_mid)} -> {fmt3(stock(L4))}",
           "Pass" if (rc["a"], rc["r"], rc["d"]) == (30, 25, 5) and stock(L4) == (70, 0, 70) and s_mid == (100, 30, 70)
           and [m["t"] for m in mv] == ["RESERVED", "DELIVERED", "RESERVATION_RELEASED", "LOSS"] else "Fail", G)
    rs = q1("SELECT status, allocated_quantity, received_quantity FROM v_request_status WHERE request_id=%s", (rq4,))
    record("DEL-05a", "Request fully allocated (30) but only 25 received", "documents current policy: status DELIVERED",
           f"status={rs['status']}, allocated={rs['allocated_quantity']}, received={rs['received_quantity']}",
           "Pass" if rs["status"] == "DELIVERED" else "Fail", G,
           "Observation of existing allocation-based policy (finding F-02), not an endorsement.")
    got = err(db.confirm_delivery, yousef, a4, "25", "again")
    n_rcpt = q1("SELECT COUNT(*) n FROM delivery_receipts WHERE allocation_id=%s", (a4,))["n"]
    record("DEL-04", "Confirm the same allocation again", "rejected; still exactly 1 receipt and 4 movements",
           f"{got}; receipts={n_rcpt}; movements={len(q('SELECT 1 FROM stock_movements WHERE allocation_id=%s', (a4,)))}",
           "Pass" if got and "already confirmed" in got and n_rcpt == 1 else "Fail", G)
    rq5 = db.create_request(yousef, 1, "20", 1, iso(5), "DEL-03")
    a5 = db.allocate(omar, rq5, L4, "20")
    for cid, val, rsn, want in [("DEL-03b", "-1", "x", "negative"), ("DEL-03c", "20.01", "x", "cannot be more"),
                                ("DEL-03d", "10", "", "reason"), ("DEL-03e", "abc", "x", "number")]:
        got = err(db.confirm_delivery, yousef, a5, val, rsn)
        record(cid, f"Receipt quantity {val!r} reason {rsn!r} rejected", f"error containing '{want}'", got,
               "Pass" if got and want in got.lower() else "Fail", G)
    got = err(db.confirm_delivery, aisha, a5, "20", "")
    record("REQ-03a", "Other market confirms this delivery", "rejected 'own market'", got,
           "Pass" if got and "own market" in got else "Fail", "REQ ownership")
    s0 = stock(L4)
    db.confirm_delivery(yousef, a5, "0", "Whole consignment rejected")
    rc = q1("SELECT received_quantity r, discrepancy_quantity d FROM delivery_receipts WHERE allocation_id=%s", (a5,))
    mv = [m["t"] for m in q("SELECT movement_type t FROM stock_movements WHERE allocation_id=%s ORDER BY movement_id", (a5,))]
    record("DEL-03a", "Receive zero with a reason", "accepted; discrepancy 20; no DELIVERED movement; release 20 + loss 20; on_hand -20",
           f"received {rc['r']} discrepancy {rc['d']}; movements {mv}; {fmt3(s0)} -> {fmt3(stock(L4))}",
           "Pass" if rc["d"] == 20 and "DELIVERED" not in mv and stock(L4) == (s0[0] - 20, 0, s0[2]) else "Fail", G)
    L5 = db.record_harvest(omar, 1, "60", iso(), iso(10), None)
    rq6 = db.create_request(yousef, 1, "40", 1, iso(5), "DEL-01")
    a6 = db.allocate(omar, rq6, L5, "40")
    db.confirm_delivery(yousef, a6, "40", "")
    rc = q1("SELECT received_quantity r, discrepancy_quantity d, discrepancy_reason x FROM delivery_receipts WHERE allocation_id=%s", (a6,))
    record("DEL-01", "Full receipt of 40", "one receipt 40/0, reason NULL; one DELIVERED movement; lot 20/0/20",
           f"{rc['r']}/{rc['d']} reason={rc['x']}; {fmt3(stock(L5))}",
           "Pass" if rc["d"] == 0 and rc["x"] is None and stock(L5) == (20, 0, 20) else "Fail", G)

    # ---------------------------------------------------------------- request update/cancel rules
    G = "REQ ownership"
    rq7 = db.create_request(noura, 1, "50", 1, iso(5), "REQ")
    L6 = db.record_harvest(fatima, 5, "100", iso(), iso(10), None)
    a7 = db.allocate(fatima, rq7, L6, "30")
    got = err(db.update_request, noura, rq7, "29.99", iso(5), "")
    record("REQ-04a", "Lower request quantity below its allocation (29.99 < 30)", "rejected 'less than what is already allocated'",
           got, "Pass" if got and "already allocated" in got else "Fail", G)
    db.update_request(noura, rq7, "30", iso(6), "exact")
    st = q1("SELECT status FROM market_requests WHERE request_id=%s", (rq7,))["status"]
    record("REQ-01b", "Update request quantity down to exactly the allocated amount", "accepted; status FULLY_ALLOCATED",
           st, "Pass" if st == "FULLY_ALLOCATED" else "Fail", G)
    got = err(db.update_request, aisha, rq7, "40", iso(5), "")
    record("REQ-03b", "Other market edits this request", "rejected 'own market'", got,
           "Pass" if got and "own market" in got else "Fail", G)
    got = err(db.cancel_request, aisha, rq7, "not mine")
    record("REQ-03c", "Other market cancels this request", "rejected 'own market'", got,
           "Pass" if got and "own market" in got else "Fail", G)
    s_b = stock(L6)
    db.cancel_request(noura, rq7, "Plan changed")
    a_st = q1("SELECT status FROM allocations WHERE allocation_id=%s", (a7,))["status"]
    record("REQ-01c", "Cancel request with a reserved allocation", "allocation RELEASED; reservation returned; status CANCELLED",
           f"allocation {a_st}; lot {fmt3(s_b)} -> {fmt3(stock(L6))}; request {q1('SELECT status FROM market_requests WHERE request_id=%s', (rq7,))['status']}",
           "Pass" if a_st == "RELEASED" and stock(L6) == (100, 0, 100) else "Fail", G)
    got = err(db.update_request, noura, rq7, "60", iso(5), "")
    record("REQ-04b", "Edit a cancelled request", "rejected", got, "Pass" if got and "cannot be changed" in got else "Fail", G)
    got = err(db.cancel_request, yousef, rq4, "after delivery")
    record("REQ-04c", "Cancel a request that already has a delivery", "rejected", got,
           "Pass" if got and ("already closed" in got or "already has deliveries" in got) else "Fail", G)

    # ---------------------------------------------------------------- admin
    G = "ADM admin"
    got = err(db.assign_farm, admin, 2, 1)
    record("ADM-02a", "Duplicate farm assignment", "rejected 'already assigned'", got,
           "Pass" if got and "already assigned" in got else "Fail", G)
    got = err(db.assign_farm, admin, 5, 1)
    record("ADM-02b", "Assign a market buyer to a farm", "rejected 'only be assigned to farmers'", got,
           "Pass" if got and "farmers" in got else "Fail", G)
    got = err(db.add_user, admin, "X", "not-an-email", "farmer", None)
    record("ADM-02c", "Invalid email", "rejected 'valid email'", got, "Pass" if got and "valid email" in got else "Fail", G)
    got = err(db.set_active, admin, "users", 1, False)
    record("ADM-01a", "Admin deactivates own account", "rejected", got,
           "Pass" if got and "your own account" in got else "Fail", G)
    uid = db.add_user(admin, "Test Farmer", "test.farmer@example.test", "farmer", None)
    db.set_active(admin, "users", uid, False)
    hidden = uid not in [u["user_id"] for u in db.list_demo_users()]
    db.set_active(admin, "users", uid, True)
    shown = uid in [u["user_id"] for u in db.list_demo_users()]
    record("ADM-01b", "Deactivate then reactivate a user (history kept, row not deleted)",
           "hidden from user selector while inactive; visible again after reactivation", f"hidden={hidden}, shown={shown}",
           "Pass" if hidden and shown else "Fail", G)
    got = err(db.add_crop, omar, "Mango", "Fruit", 1)
    record("ADM-01c", "Farmer cannot add reference data", "rejected 'Only administrators'", got,
           "Pass" if got and "administrators" in got else "Fail", G)

    # ---------------------------------------------------------------- search
    G = "SRCH search"
    rows = db.search_lots(crop_id=1)
    record("SRCH-01a", "Crop filter Tomato", "only Tomato lots", f"{len(rows)} rows, crops={sorted({r['crop_name'] for r in rows})}",
           "Pass" if rows and {r["crop_name"] for r in rows} == {"Tomato"} else "Fail", G)
    rows = db.search_lots(emirate="Dubai")
    record("SRCH-01b", "Emirate filter Dubai", "only Hatta Valley Farm lots", f"farms={sorted({r['farm_name'] for r in rows})}",
           "Pass" if {r["farm_name"] for r in rows} == {"Hatta Valley Farm"} else "Fail", G)
    rows = db.search_lots(availability="Sold out")
    record("SRCH-01c", "Availability 'Sold out'", "only lots with on_hand <= 0 (seed lots #1, #5)",
           f"lots={sorted(r['lot_id'] for r in rows)}", "Pass" if rows and all(r["on_hand"] <= 0 for r in rows) else "Fail", G)
    rows = db.search_lots(availability="Fully reserved")
    record("SRCH-01d", "Availability 'Fully reserved'", "only lots with available <= 0 and reserved > 0",
           f"lots={sorted(r['lot_id'] for r in rows)}", "Pass" if all(r["available"] <= 0 < r["reserved"] for r in rows) else "Fail", G)
    rows = db.search_lots(min_available="100")
    record("SRCH-01e", "Minimum available 100", "every row available >= 100", f"{len(rows)} rows, min={min(r['available'] for r in rows) if rows else '-'}",
           "Pass" if rows and all(r["available"] >= 100 for r in rows) else "Fail", G)
    rows = db.search_lots(sellable_on=iso(61))
    record("SRCH-01f", "Available on a date 61 days ahead", "only lots with sell_by NULL or >= that date",
           f"lots={sorted(r['lot_id'] for r in rows)}",
           "Pass" if all(r["sell_by_date"] is None or r["sell_by_date"] >= TODAY + dt.timedelta(days=61) for r in rows) else "Fail", G)
    rows = db.search_requests(status="PARTIALLY_DELIVERED")
    record("SRCH-01g", "Request status filter PARTIALLY_DELIVERED", "seed requests #1 and #3 only",
           f"requests={sorted(r['request_id'] for r in rows)}", "Pass" if sorted(r["request_id"] for r in rows) == [1, 3] else "Fail", G)
    rows = db.search_lots(crop_id=999)
    # Oracle note: the first run compared `rows == []`; PyMySQL returns an empty tuple, so a correct
    # empty result was reported as Fail. Expectation unchanged (0 rows, no error); comparison fixed.
    record("SRCH-02a", "Empty result (unknown crop id)", "0 rows, no error", f"{len(rows)} rows",
           "Pass" if len(rows) == 0 else "Fail", G, "Oracle corrected after 2026-11-17 first run (tuple vs list).")
    for cid, kw, want in [("SRCH-02b", dict(min_available="abc"), "must be a number"),
                          ("SRCH-02c", dict(min_available="-1"), "negative"),
                          ("SRCH-02d", dict(date_from=iso(5), date_to=iso(1)), "cannot be before"),
                          ("SRCH-02e", dict(date_from="2026-13-01"), "real date")]:
        got = err(lambda: db.search_lots(**kw))
        record(cid, f"Invalid search input {kw}", f"error '{want}'", got, "Pass" if got and want in got else "Fail", G)

    # ---------------------------------------------------------------- Loss & Surplus
    G = "LS Loss & Surplus"
    for cid, a, b, ok_ in [("LS-02a", "0", "0", True), ("LS-02b", "60", "365", True), ("LS-02c", "-1", "7", False),
                           ("LS-02d", "61", "7", False), ("LS-02e", "3", "366", False), ("LS-02f", "3", "-1", False),
                           ("LS-02g", "abc", "7", False), ("LS-02h", "1.5", "7", False), ("LS-02i", "", "7", False)]:
        got = err(db.flagged_lots, a, b)
        record(cid, f"Thresholds near={a!r} surplus={b!r}", "accepted" if ok_ else "rejected with friendly message",
               got or "accepted", "Pass" if (got is None) == ok_ else "Fail", G)
    # controlled boundary lots on a fresh Fatima cycle (tomato, farm 3)
    def mk(h_days, sb_days, qty="10"):
        return db.record_harvest(fatima, 5, qty, iso(h_days), iso(sb_days) if sb_days is not None else "", None)
    b_today = mk(-1, 0)
    b_n = mk(0, 3)
    b_n1 = mk(0, 4)
    b_old = mk(-7, None)
    b_young = mk(-6, None)
    b_exp_reserved = mk(-5, -1)
    rq_res = db.create_request(noura, 1, "10", 1, iso(3), "reserve all")
    db.allocate(fatima, rq_res, b_exp_reserved, "10")
    b_released = mk(-9, None)
    rq_rel = db.create_request(noura, 1, "5", 1, iso(3), "release later")
    a_rel = db.allocate(fatima, rq_rel, b_released, "5")
    db.release_allocation(fatima, a_rel, "buyer withdrew")
    flags = {r["lot_id"]: r for r in db.flagged_lots("3", "7", {3})}
    expect = {b_today: "NEAR EXPIRY", b_n: "NEAR EXPIRY", b_n1: None, b_old: "UNALLOCATED SURPLUS", b_young: None,
              b_exp_reserved: None, b_released: "UNALLOCATED SURPLUS"}
    labels = {b_today: "sell-by today (days_left 0)", b_n: "sell-by today+3 (=N)", b_n1: "sell-by today+4 (N+1), age 0",
              b_old: "no sell-by, age 7 (=M)", b_young: "no sell-by, age 6 (M-1)",
              b_exp_reserved: "expired but fully reserved (available 0)",
              b_released: "age 9, only allocation RELEASED"}
    ids_ = {b_today: "LS-03a", b_n: "LS-03b", b_n1: "LS-03c", b_old: "LS-03d", b_young: "LS-03e",
            b_exp_reserved: "LS-01b", b_released: "LS-06"}
    for lot, want in expect.items():
        have = flags.get(lot, {}).get("flag")
        record(ids_[lot], f"Defaults 3/7: lot {lot} {labels[lot]}", want or "not flagged", have or "not flagged",
               "Pass" if have == want else "Fail", G)
    f0 = {r["lot_id"]: r["flag"] for r in db.flagged_lots("0", "365", {3})}
    record("LS-03f", "Near-expiry threshold 0: sell-by today is NEAR EXPIRY, not EXPIRED; today+3 not flagged",
           "NEAR EXPIRY / not flagged", f"{f0.get(b_today)} / {f0.get(b_n) or 'not flagged'}",
           "Pass" if f0.get(b_today) == "NEAR EXPIRY" and b_n not in f0 else "Fail", G)
    seed_flags = {r["lot_id"]: (r["flag"], r["priority"]) for r in db.flagged_lots("3", "7")}
    record("LS-01a", "Seed: lot #3 EXPIRED priority 1; lot #12 surplus; ordering by priority",
           "lot 3 EXPIRED/1, lot 12 UNALLOCATED SURPLUS/3; first row priority 1",
           f"lot3={seed_flags.get(3)}, lot12={seed_flags.get(12)}, first={db.flagged_lots('3', '7')[0]['priority']}",
           "Pass" if seed_flags.get(3) == ("EXPIRED", 1) and seed_flags.get(12, ("",))[0] == "UNALLOCATED SURPLUS"
           and db.flagged_lots("3", "7")[0]["priority"] == 1 else "Fail", G)
    pri = [r["priority"] for r in db.flagged_lots("3", "7")]
    record("LS-01c", "Result sorted by priority (non-decreasing)", "sorted", pri, "Pass" if pri == sorted(pri) else "Fail", G)
    D = mk(-1, 5, "10")
    db.dispose_lot(fatima, D, "DONATED", "0.01", "Sharjah Charity")
    s1 = stock(D)
    db.dispose_lot(fatima, D, "DISPOSED", "9.99", "Bruised")
    s2 = stock(D)
    record("LS-04a", "Donate 0.01 then dispose exactly the remaining 9.99", "9.99/0/9.99 then 0/0/0",
           f"{fmt3(s1)} then {fmt3(s2)}", "Pass" if s1 == (Decimal("9.99"), 0, Decimal("9.99")) and s2 == (0, 0, 0) else "Fail", G)
    hist = [h for h in db.disposition_history({3}) if h["lot_id"] == D]
    record("LS-04b", "Disposition history persists actor, date, type and reason", "2 rows by Fatima Rashid with reasons",
           [(h["movement_type"], str(h["quantity"]), h["full_name"], h["reason"]) for h in hist],
           "Pass" if len(hist) == 2 and all(h["full_name"] == "Fatima Rashid" and h["reason"] and h["movement_date"] for h in hist) else "Fail", G)
    for cid, qty, note, want in [("LS-04c", "0.01", "x", "only 0"), ("LS-04d", "0", "x", "greater than zero"),
                                 ("LS-04e", "-1", "x", "negative"), ("LS-04f", "1", " ", "required")]:
        got = err(db.dispose_lot, fatima, D if cid == "LS-04c" else b_old, "DONATED", qty, note)
        record(cid, f"Donate qty {qty!r} note {note!r}", f"rejected '{want}'", got, "Pass" if got and want in got.lower() else "Fail", G)
    got = err(db.dispose_lot, omar, b_old, "DISPOSED", "1", "not mine")
    record("LS-05a", "Another farmer disposes Fatima's lot", "rejected 'assigned to you'", got,
           "Pass" if got and "assigned to you" in got else "Fail", G)
    got = err(db.dispose_lot, admin, b_old, "DONATED", "1", "admin")
    record("LS-05b", "Administrator attempts donation", "rejected 'Only farmers'", got,
           "Pass" if got and "only farmers" in got.lower() else "Fail", G)
    all_flags = db.flagged_lots("3", "7", None)
    record("LS-05c", "Administrator (no farm filter) sees flags across all farms", "> 1 farm in result",
           sorted({r["farm_name"] for r in all_flags}), "Pass" if len({r["farm_id"] for r in all_flags}) > 1 else "Fail", G)
    got = err(db.dispose_lot, fatima, b_old, "SOLD", "1", "x")
    record("LS-04g", "Unknown disposition action", "rejected", got, "Pass" if got and "donate or dispose" in got.lower() else "Fail", G)

    # ---------------------------------------------------------------- images
    G = "IMG images"
    tmp = tempfile.mkdtemp(prefix="farm_img_")
    from PIL import Image

    def png_of_size(path, size):
        buf = io.BytesIO()
        Image.new("RGB", (32, 32), (20, 160, 60)).save(buf, "PNG")
        data = buf.getvalue()
        with open(path, "wb") as fh:
            fh.write(data + b"\0" * (size - len(data)))   # trailing bytes after IEND
    p_exact = os.path.join(tmp, "exact.png"); png_of_size(p_exact, 5 * 1024 * 1024)
    p_over = os.path.join(tmp, "over.png"); png_of_size(p_over, 5 * 1024 * 1024 + 1)
    p_empty = os.path.join(tmp, "empty.jpg"); open(p_empty, "wb").close()
    p_txt = os.path.join(tmp, "notes.txt"); open(p_txt, "w").write("hello")
    p_fake = os.path.join(tmp, "fake.jpg"); open(p_fake, "wb").write(b"not really a jpeg" * 10)
    p_gif = os.path.join(tmp, "anim.gif"); Image.new("RGB", (8, 8)).save(p_gif, "GIF")
    p_gif_as_png = os.path.join(tmp, "gif_named.png"); Image.new("RGB", (8, 8)).save(p_gif_as_png, "GIF")
    with open(os.path.join(APP, "sample_images", "cucumber.jpg"), "rb") as fh:
        jpg = fh.read()
    p_trunc = os.path.join(tmp, "truncated.jpg"); open(p_trunc, "wb").write(jpg[: len(jpg) // 2])
    for cid, path, want in [("IMG-03a", os.path.join(tmp, "missing.jpg"), "not found"), ("IMG-03b", p_empty, "empty"),
                            ("IMG-03c", p_txt, "only jpg and png"), ("IMG-03d", p_fake, "not a valid"),
                            ("IMG-03e", p_over, "larger than 5 mb"), ("IMG-03f", p_gif, "only jpg and png"),
                            ("IMG-03g", p_gif_as_png, "not a valid")]:
        got = err(db.validate_image, path)
        record(cid, f"Upload {os.path.basename(path)}", f"rejected '{want}'", got,
               "Pass" if got and want in got.lower() else "Fail", G)
    got = err(db.validate_image, p_exact)
    record("IMG-04a", "PNG of exactly 5 MiB (5,242,880 bytes)", "accepted (limit is inclusive)", got or "accepted",
           "Pass" if got is None else "Fail", G)
    got = err(db.validate_image, p_trunc)
    record("IMG-04b", "JPEG truncated to half its bytes", "observe: validate_image uses Pillow verify()",
           got or "accepted by validate_image", "Info", G,
           "Informational: records actual behaviour of the existing validator for truncated JPEGs.")
    n_img = q1("SELECT COUNT(*) n FROM harvest_lot_images")["n"]
    for path in (p_over, p_fake, p_empty):
        err(db.add_lot_image, omar, L, path)
    record("IMG-03z", "No image row inserted by rejected uploads", f"{n_img} rows", q1("SELECT COUNT(*) n FROM harvest_lot_images")["n"],
           "Pass" if q1("SELECT COUNT(*) n FROM harvest_lot_images")["n"] == n_img else "Fail", G)
    lot_png = db.record_harvest(omar, 1, "3", iso(), "", p_exact)
    stored = db.lot_images(lot_png)[0]["image_data"]
    with open(p_exact, "rb") as fh:
        orig = fh.read()
    record("IMG-04c", "5 MiB PNG stored as MEDIUMBLOB and read back byte-identical",
           "SHA-256 equal", f"stored {len(stored)} bytes sha256 {hashlib.sha256(stored).hexdigest()[:16]}… "
           f"orig {hashlib.sha256(orig).hexdigest()[:16]}…", "Pass" if stored == orig else "Fail", G)
    got = err(db.add_lot_image, fatima, lot_png, os.path.join(APP, "sample_images", "zucchini.jpg"))
    record("IMG-03h", "Farmer uploads photo to another farm's lot", "rejected 'assigned to you'", got,
           "Pass" if got and "assigned to you" in got else "Fail", G)
    got = err(db.add_lot_image, noura, 2, os.path.join(APP, "sample_images", "zucchini.jpg"))
    record("IMG-03i", "Market buyer uploads a photo", "rejected 'Only farmers'", got,
           "Pass" if got and "only farmers" in got.lower() else "Fail", G)

    # ---------------------------------------------------------------- TX-01 rollback injection
    G = "TX-01 rollback"
    orig_get = db.get_connection

    def failing(pattern):
        def get():
            conn = orig_get()
            real_cursor = conn.cursor

            def cursor(*a, **k):
                c = real_cursor(*a, **k)
                real_exec = c.execute

                def execute(sql, params=None):
                    if re.search(pattern, sql):
                        raise pymysql.err.OperationalError(2013, "Injected failure (test)")
                    return real_exec(sql, params)
                c.execute = execute
                return c
            conn.cursor = cursor
            return conn
        return get

    def inject(cid, title, pattern, fn, *args):
        fp = fingerprint()
        db.get_connection = failing(pattern)
        try:
            got = err(fn, *args)
        finally:
            db.get_connection = orig_get
        same = fp == fingerprint()
        record(cid, title, "operation fails with friendly message; every table's checksum unchanged",
               f"{got}; tables unchanged={same}" + ("" if same else f" changed={[t for t in fp if fp[t] != fingerprint()[t]]}"),
               "Pass" if got and same else "Fail", G)

    cyc_g = 9  # Omar's GROWING Bell Pepper cycle
    inject("TX-01a", "Harvest with photo: fail on image INSERT after lot + movement + cycle-status UPDATE",
           r"INSERT INTO harvest_lot_images", db.record_harvest, omar, cyc_g, "12", iso(), "",
           os.path.join(APP, "sample_images", "bell_pepper.jpg"))
    record("TX-01a2", "Cycle #9 status not changed by the rolled-back harvest", "GROWING",
           q1("SELECT status FROM crop_cycles WHERE cycle_id=9")["status"],
           "Pass" if q1("SELECT status FROM crop_cycles WHERE cycle_id=9")["status"] == "GROWING" else "Fail", G)
    Lr = db.record_harvest(omar, 1, "40", iso(), iso(9), None)
    rqr = db.create_request(hamad, 1, "40", 1, iso(4), "TX")
    inject("TX-01b", "Allocate: fail on status-history INSERT after allocation + RESERVED movement + status UPDATE",
           r"INSERT INTO request_status_history", db.allocate, omar, rqr, Lr, "25")
    ar = db.allocate(omar, rqr, Lr, "25")
    inject("TX-01c", "Partial delivery: fail on LOSS movement after receipt, DELIVERED and release rows",
           r"VALUES \(%s,'LOSS'", db.confirm_delivery, hamad, ar, "20", "5 short")
    inject("TX-01d", "Release: fail on status-history INSERT after release movement + allocation UPDATE",
           r"INSERT INTO request_status_history", db.release_allocation, omar, ar, "test")
    inject("TX-01e", "Cancel with reservation: fail on final history INSERT after release + status UPDATE",
           r"INSERT INTO request_status_history", db.cancel_request, hamad, rqr, "test")
    inject("TX-01f", "Add farm: fail on farm_users INSERT after farms INSERT", r"INSERT INTO farm_users",
           db.add_farm, omar, "Rollback Farm", 1, "")
    ok, detail = inv_ok()
    record("TX-01z", "Ledger invariants after all injected failures", "no violations", "ok" if ok else detail,
           "Pass" if ok else "Fail", G)

    # ---------------------------------------------------------------- TX-02/03 concurrency
    G = "TX-02/03 concurrency"

    def race(fns):
        """Run callables in parallel threads released by one barrier; return outcomes in order."""
        out = [None] * len(fns)
        bar = threading.Barrier(len(fns))

        def run(i, f):
            bar.wait()
            try:
                f()
                out[i] = "ok"
            except Exception as e:  # noqa: BLE001
                out[i] = db.friendly_error(e)
        th = [threading.Thread(target=run, args=(i, f)) for i, f in enumerate(fns)]
        [t.start() for t in th]
        [t.join() for t in th]
        return out

    def oversell_trials(n, label):
        overs, both, detail = 0, 0, []
        for _ in range(n):
            lot = db.record_harvest(omar, 1, "100", iso(), iso(10), None)
            ra = db.create_request(aisha, 1, "80", 1, iso(5), label)
            rb = db.create_request(noura, 1, "80", 1, iso(5), label)
            out = race([lambda: db.allocate(omar, ra, lot, "80"), lambda: db.allocate(omar, rb, lot, "80")])
            s = stock(lot)
            if out.count("ok") == 2:
                both += 1
            if s[2] < 0:
                overs += 1
                detail.append(fmt3(s))
        return overs, both, detail

    overs, both, detail = oversell_trials(20, "race")
    record("TX-02a", "20 trials: two farmers' threads allocate 80 each from one 100 kg lot to DIFFERENT requests",
           "at most one allocation per trial; available never negative",
           f"both succeeded in {both}/20 trials; negative availability in {overs}/20 (e.g. {detail[:3]})",
           "Pass" if overs == 0 and both == 0 else "Fail", G,
           "Finding F-01 if failing: the availability read uses a REPEATABLE READ snapshot taken before the lot lock.")

    # deterministic interleaving: pause thread A after its first plain SELECT (snapshot) and before the lot lock
    lot = db.record_harvest(omar, 1, "100", iso(), iso(10), None)
    ra = db.create_request(aisha, 1, "80", 1, iso(5), "det")
    rb = db.create_request(noura, 1, "80", 1, iso(5), "det")
    orig_owner = db._check_lot_owner
    gate, entered = threading.Event(), threading.Event()

    def paused_owner(cur, user, lot_id):
        orig_owner(cur, user, lot_id)
        if threading.current_thread().name == "A":
            entered.set()
            gate.wait(10)
    db._check_lot_owner = paused_owner
    res = {}

    def A():
        try:
            db.allocate(omar, ra, lot, "80")
            res["A"] = "ok"
        except Exception as e:  # noqa: BLE001
            res["A"] = db.friendly_error(e)
    ta = threading.Thread(target=A, name="A")
    ta.start()
    entered.wait(10)
    try:
        db.allocate(omar, rb, lot, "80")
        res["B"] = "ok"
    except Exception as e:  # noqa: BLE001
        res["B"] = db.friendly_error(e)
    gate.set()
    ta.join()
    db._check_lot_owner = orig_owner
    s = stock(lot)
    record("TX-02b", "Deterministic interleaving: A reads ownership (snapshot), B allocates 80 and commits, A continues",
           "A rejected 'Not enough stock'; lot available 20",
           f"A={res.get('A')}, B={res.get('B')}; lot {fmt3(s)}",
           "Pass" if res.get("A") != "ok" and s[2] >= 0 else "Fail", G,
           "The pause only widens a timing window that exists in normal scheduling; no SQL is changed.")

    # donation vs allocation race on the same lot
    overs2 = 0
    for _ in range(10):
        lot = db.record_harvest(omar, 1, "100", iso(), iso(10), None)
        ra = db.create_request(aisha, 1, "80", 1, iso(5), "don")
        out = race([lambda: db.allocate(omar, ra, lot, "80"), lambda: db.dispose_lot(omar, lot, "DONATED", "80", "bank")])
        if stock(lot)[2] < 0:
            overs2 += 1
    record("TX-02c", "10 trials: allocation of 80 races a donation of 80 on one 100 kg lot",
           "never both; available never negative", f"negative availability in {overs2}/10 trials",
           "Pass" if overs2 == 0 else "Fail", G)

    # proposed-fix simulation: READ COMMITTED for every connection in this process
    def rc_get():
        conn = orig_get()
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        return conn
    db.get_connection = rc_get
    try:
        overs_fix, both_fix, _ = oversell_trials(20, "rc")
    finally:
        db.get_connection = orig_get
    record("TX-02d", "Proposed-fix simulation: same 20 trials with READ COMMITTED sessions",
           "no oversell", f"both succeeded {both_fix}/20; negative availability {overs_fix}/20",
           "Pass" if overs_fix == 0 and both_fix == 0 else "Fail", G,
           "Simulation inside this test process only; application code unchanged. Not a reviewed fix.")

    # two confirmations of the same allocation
    lot = db.record_harvest(omar, 1, "50", iso(), iso(10), None)
    rq = db.create_request(yousef, 1, "50", 1, iso(5), "dup")
    al = db.allocate(omar, rq, lot, "50")
    out = race([lambda: db.confirm_delivery(yousef, al, "50", ""), lambda: db.confirm_delivery(yousef, al, "45", "short")])
    n_r = q1("SELECT COUNT(*) n FROM delivery_receipts WHERE allocation_id=%s", (al,))["n"]
    n_m = q1("SELECT COUNT(*) n FROM stock_movements WHERE allocation_id=%s AND movement_type<>'RESERVED'", (al,))["n"]
    record("TX-03a", "Two concurrent confirmations of one allocation", "exactly one succeeds; 1 receipt; no duplicate movements",
           f"outcomes={out}; receipts={n_r}; post-reservation movements={n_m}",
           "Pass" if out.count("ok") == 1 and n_r == 1 and n_m in (1, 3) else "Fail", G)
    # release vs confirm
    lot = db.record_harvest(omar, 1, "50", iso(), iso(10), None)
    rq = db.create_request(yousef, 1, "50", 1, iso(5), "rel-conf")
    al = db.allocate(omar, rq, lot, "50")
    out = race([lambda: db.release_allocation(omar, al, "farmer releases"), lambda: db.confirm_delivery(yousef, al, "50", "")])
    a_st = q1("SELECT status FROM allocations WHERE allocation_id=%s", (al,))["status"]
    record("TX-03b", "Release races confirmation on one allocation", "exactly one succeeds; allocation status matches ledger",
           f"outcomes={out}; allocation={a_st}; lot {fmt3(stock(lot))}",
           "Pass" if out.count("ok") == 1 and stock(lot) in ((50, 0, 50), (0, 0, 0)) else "Fail", G)
    # cancel vs allocate
    lot = db.record_harvest(omar, 1, "50", iso(), iso(10), None)
    rq = db.create_request(yousef, 1, "50", 1, iso(5), "cancel-alloc")
    out = race([lambda: db.cancel_request(yousef, rq, "cancel"), lambda: db.allocate(omar, rq, lot, "50")])
    st = q1("SELECT status FROM market_requests WHERE request_id=%s", (rq,))["status"]
    open_res = q1("SELECT COUNT(*) n FROM allocations WHERE request_id=%s AND status='RESERVED'", (rq,))["n"]
    record("TX-03c", "Cancellation races allocation on one request", "request CANCELLED; no RESERVED allocation left; lot 50/0/50",
           f"outcomes={out}; request={st}; reserved allocations={open_res}; lot {fmt3(stock(lot))}",
           "Pass" if st == "CANCELLED" and open_res == 0 and stock(lot) == (50, 0, 50) else "Fail", G)
    # cancel vs confirm
    lot = db.record_harvest(omar, 1, "50", iso(), iso(10), None)
    rq = db.create_request(yousef, 1, "50", 1, iso(5), "cancel-confirm")
    al = db.allocate(omar, rq, lot, "50")
    out = race([lambda: db.cancel_request(yousef, rq, "cancel"), lambda: db.confirm_delivery(yousef, al, "50", "")])
    st = q1("SELECT status FROM market_requests WHERE request_id=%s", (rq,))["status"]
    a_st = q1("SELECT status FROM allocations WHERE allocation_id=%s", (al,))["status"]
    record("TX-03d", "Cancellation races delivery confirmation", "exactly one succeeds; consistent request/allocation/ledger",
           f"outcomes={out}; request={st}; allocation={a_st}; lot {fmt3(stock(lot))}",
           "Pass" if out.count("ok") == 1 and ((st, a_st, stock(lot)) in (("CANCELLED", "RELEASED", (50, 0, 50)),
                                                                            ("DELIVERED", "DELIVERED", (0, 0, 0)))) else "Fail", G)
    ok, detail = inv_ok()
    record("TX-03z", "Ledger invariants after all concurrency scenarios",
           "no lot with reserved != open RESERVED allocations; no duplicate receipt",
           "ok" if ok else detail, "Pass" if ok else "Fail", G,
           "Lots oversold in TX-02a/02c (if any) appear here as negative availability.")

    # ---------------------------------------------------------------- connection errors
    G = "ERR connection"
    saved = {k: os.environ.get(k) for k in ("DB_NAME", "DB_HOST")}
    os.environ["DB_NAME"] = "farm_market_db_missing"
    got = err(db.list_crops)
    record("ERR-01a", "Missing database name", "friendly 'database was not found' (MySQL 1049)", got,
           "Pass" if got and "not found" in got else "Fail", G)
    os.environ["DB_NAME"] = saved["DB_NAME"] or "farm_market_db"
    os.environ["DB_HOST"] = "203.0.113.1"   # TEST-NET-3, unroutable
    t0 = time.time()
    got = err(db.list_crops)
    record("ERR-01b", "Unreachable host (TEST-NET address)", "friendly 'Cannot reach the MySQL server' within the 5 s connect timeout",
           f"{got} after {time.time() - t0:.1f}s", "Pass" if got and "cannot reach" in got.lower() else "Fail", G)
    os.environ["DB_HOST"] = saved["DB_HOST"] or "localhost"
    leak = any(s in (got or "") for s in ("Traceback", "pymysql", os.environ.get("DB_PASSWORD") or "\0"))
    record("ERR-01c", "Friendly messages contain no traceback, driver name or password", "no leakage",
           "none" if not leak else "leak", "Pass" if not leak else "Fail", G)

    # ---------------------------------------------------------------- write evidence
    os.makedirs(OUT_DIR, exist_ok=True)
    summary = {}
    for r in RESULTS:
        summary[r["outcome"]] = summary.get(r["outcome"], 0) + 1
    with open(os.path.join(OUT_DIR, "remaining-checks.json"), "w", encoding="utf-8") as fh:
        json.dump({"environment": env, "summary": summary, "results": RESULTS}, fh, indent=1, default=str)
    print("\nSummary:", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
