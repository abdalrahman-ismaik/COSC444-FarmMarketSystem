"""Automated tests for the business rules (run AFTER setup_database.py).

Run:  python tests/test_business_rules.py
WARNING: changes data. Re-run setup_database.py afterwards for a clean demo.
"""
import os
import sys
import threading
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db  # noqa: E402
import assistant  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []


def check(name, fn, expect_error=None):
    try:
        out = fn()
        ok = expect_error is None
        detail = "ok" if ok else "expected an error but it succeeded"
    except Exception as e:
        msg = db.friendly_error(e)
        ok = expect_error is not None and expect_error.lower() in msg.lower()
        detail = msg
        out = None
    results.append((ok, name, detail))
    print(("PASS " if ok else "FAIL ") + name + ("" if ok and expect_error is None else f"  ->  {detail}"))
    return out


def stock(lot_id):
    return db.query_one("SELECT on_hand, reserved, available FROM v_lot_stock WHERE lot_id=%s", (lot_id,))


omar, fatima = db.get_user(2), db.get_user(3)
noura, aisha = db.get_user(7), db.get_user(5)
admin = db.get_user(1)
img = os.path.join(ROOT, "sample_images", "cucumber.jpg")

print("\n== Harvest & images ==")
lot = check("Farmer records harvest with photo", lambda: db.record_harvest(omar, 2, "50", db.dt.date.today().isoformat(), "", img))
check("Harvest adds stock movement", lambda: stock(lot)["on_hand"] == 50 or (_ for _ in ()).throw(AssertionError()))
check("Photo stored as BLOB", lambda: len(db.lot_images(lot)) == 1 or (_ for _ in ()).throw(AssertionError()))
check("Negative harvest rejected", lambda: db.record_harvest(omar, 2, "-5", "2026-01-01", "", None), "cannot be negative")
check("Invalid date rejected", lambda: db.record_harvest(omar, 2, "5", "2026-02-30", "", None), "real date")
check("Future harvest rejected", lambda: db.record_harvest(omar, 2, "5", "2099-01-01", "", None), "future")
check("Sell-by before harvest rejected", lambda: db.record_harvest(omar, 2, "5", db.dt.date.today().isoformat(), "2000-01-01", None), "before the harvest")
check("Farmer cannot use another farm's cycle", lambda: db.record_harvest(omar, 5, "5", db.dt.date.today().isoformat(), "", None), "assigned to you")
check("Non-image upload rejected", lambda: db.add_lot_image(omar, lot, os.path.join(ROOT, "requirements.txt")), "jpg and png")
check("Market buyer cannot record harvest", lambda: db.record_harvest(noura, 2, "5", "2026-01-01", "", None), "only farmers")

print("\n== Expected vs stock ==")
before = db.stock_summary(db.my_farm_ids(4))
check("Crop cycle forecast created", lambda: db.add_cycle(db.get_user(4), 4, 6, db.dt.date.today().isoformat(), "2099-01-01", "500", 1))
after = db.stock_summary(db.my_farm_ids(4))
zb = [r for r in before if r["crop_name"] == "Zucchini"][0]
za = [r for r in after if r["crop_name"] == "Zucchini"][0]
check("Expected harvest never counted as available stock",
      lambda: (za["available"] == zb["available"] and za["expected"] == zb["expected"] + 500) or (_ for _ in ()).throw(AssertionError()))

print("\n== Allocation rules ==")
check("Allocation larger than lot is rejected", lambda: db.allocate(omar, 7, 2, "100"), "not enough stock")
check("Farmer cannot allocate from another farm", lambda: db.allocate(omar, 7, 13, "10"), "assigned to you")
check("Wrong crop rejected", lambda: db.allocate(omar, 7, 4, "10"), "different crop")
a1 = check("Valid allocation 78 kg from lot 2", lambda: db.allocate(omar, 7, 2, "78"))
check("Lot 2 now fully reserved", lambda: stock(2)["available"] == 0 or (_ for _ in ()).throw(AssertionError()))
check("Over-allocating the request is rejected", lambda: db.allocate(fatima, 7, 13, "50"), "only needs 42")
a2 = check("Second farmer allocates remaining 42 kg", lambda: db.allocate(fatima, 7, 13, "42"))
check("Request becomes FULLY_ALLOCATED",
      lambda: db.query_one("SELECT status FROM market_requests WHERE request_id=7")["status"] == "FULLY_ALLOCATED" or (_ for _ in ()).throw(AssertionError()))
check("Allocating a closed request rejected", lambda: db.allocate(fatima, 7, 13, "1"), "not open")

print("\n== Delivery ==")
check("Other market cannot confirm", lambda: db.confirm_delivery(aisha, a1, "78", ""), "own market")
check("Received > allocated rejected", lambda: db.confirm_delivery(noura, a1, "90", ""), "cannot be more")
check("Shortfall without reason rejected", lambda: db.confirm_delivery(noura, a1, "70", ""), "reason")
check("Partial delivery confirmed (70 of 78)", lambda: db.confirm_delivery(noura, a1, "70", "8 kg bruised"))
s2 = stock(2)
check("Lot 2: on hand 0, reserved 0 after delivery+discrepancy",
      lambda: (s2["on_hand"] == 0 and s2["reserved"] == 0) or (_ for _ in ()).throw(AssertionError(str(s2))))
check("Receipt records difference 8",
      lambda: db.query_one("SELECT discrepancy_quantity d FROM delivery_receipts WHERE allocation_id=%s", (a1,))["d"] == 8 or (_ for _ in ()).throw(AssertionError()))
check("Request becomes PARTIALLY_DELIVERED",
      lambda: db.query_one("SELECT status FROM market_requests WHERE request_id=7")["status"] == "PARTIALLY_DELIVERED" or (_ for _ in ()).throw(AssertionError()))
check("Confirming twice rejected", lambda: db.confirm_delivery(noura, a1, "70", "x"), "already confirmed")
check("Cancel after delivery rejected", lambda: db.cancel_request(noura, 7, "test"), "already has deliveries")

print("\n== Release & requests ==")
r = check("Market creates request", lambda: db.create_request(aisha, 5, "30", 1, "2099-01-01", "test"))
check("Unit mismatch rejected (box lot vs kg request)",
      lambda: db.allocate(fatima, db.create_request(aisha, 3, "5", 1, "2099-01-01", ""), 12, "5"), "different units")
a3 = check("Allocate 20 kg eggplant", lambda: db.allocate(fatima, r, 10, "20"))
before = stock(10)["available"]
check("Release allocation", lambda: db.release_allocation(fatima, a3, "Buyer changed plan"))
check("Released stock is available again", lambda: stock(10)["available"] == before + 20 or (_ for _ in ()).throw(AssertionError()))
check("Past needed-by date rejected", lambda: db.create_request(aisha, 1, "5", 1, "2000-01-01", ""), "past")
check("Other market cannot edit request", lambda: db.update_request(noura, r, "40", "2099-01-01", ""), "own market")
check("Cancel request", lambda: db.cancel_request(aisha, r, "No longer needed"))

print("\n== Loss & surplus (advanced feature) ==")
flags = check("Flagged lots query", lambda: db.flagged_lots(3, 7))
check("Expired lot 3 flagged priority 1",
      lambda: any(f["lot_id"] == 3 and f["flag"] == "EXPIRED" for f in flags) or (_ for _ in ()).throw(AssertionError()))
check("Surplus box lot 12 flagged",
      lambda: any(f["lot_id"] == 12 and f["flag"] == "UNALLOCATED SURPLUS" for f in flags) or (_ for _ in ()).throw(AssertionError()))
check("Bad threshold rejected", lambda: db.flagged_lots("abc", 7), "whole numbers")
check("Donation from past-sell-by lot rejected", lambda: db.dispose_lot(omar, 3, "DONATED", "1", "Food bank"), "past its sell-by")
check("Donate 30 kg from in-date lot", lambda: db.dispose_lot(omar, 6, "DONATED", "30", "UAE Food Bank"))
check("Dispose past-sell-by lot", lambda: db.dispose_lot(omar, 3, "DISPOSED", "40", "Past sell-by date"))
check("Lot 3 now empty", lambda: stock(3)["on_hand"] == 0 or (_ for _ in ()).throw(AssertionError()))
check("Reserved stock cannot be donated", lambda: db.dispose_lot(fatima, 8, "DONATED", "120", "x"), "only 100")

print("\n== Admin & errors ==")
check("Admin cannot allocate (no transaction editing)", lambda: db.allocate(admin, 7, 2, "1"), "only farmers")
check("Duplicate crop rejected", lambda: db.add_crop(admin, "Tomato", "Veg", 1), "already exists")
check("Duplicate email rejected", lambda: db.add_user(admin, "X", "omar@greenoasis.example", "farmer", None), "already exists")
check("Market buyer needs a market", lambda: db.add_user(admin, "X", "x@y.example", "market", None), "linked to a market")
check("Deactivate crop", lambda: db.set_active(admin, "crops", 6, False))
check("Inactive crop cannot be requested", lambda: db.create_request(aisha, 6, "5", 1, "2099-01-01", ""), "inactive")
db.set_active(admin, "crops", 6, True)
check("Unknown crop rejected", lambda: db.create_request(aisha, 999, "5", 1, "2099-01-01", ""), "unknown crop")

print("\n== Concurrency: two farmers race for the same lot ==")
rid = db.create_request(noura, 1, "120", 1, "2099-01-01", "race")
outcomes = []
def race():
    try:
        db.allocate(fatima, rid, 13, "60"); outcomes.append("ok")
    except Exception as e:
        outcomes.append(db.friendly_error(e))
threads = [threading.Thread(target=race) for _ in range(3)]
[t.start() for t in threads]; [t.join() for t in threads]
check("No overselling under concurrent requests (lot 13 had 78 available)",
      lambda: (outcomes.count("ok") == 1 and stock(13)["available"] >= 0) or (_ for _ in ()).throw(AssertionError(str(outcomes))))

print("\n== Bad connection ==")
os.environ["DB_PASSWORD"] = "wrong"
check("Wrong DB password -> friendly message", lambda: db.list_crops(), "login failed")
os.environ["DB_PORT"] = "3999"
check("MySQL down -> friendly message", lambda: db.list_crops(), "cannot reach")

print("\n== Assistant SQL guard ==")
for bad in ["DELETE FROM farms", "SELECT * FROM farms; DROP TABLE farms", "UPDATE units SET unit_code='x'",
            "SELECT image_data FROM harvest_lot_images", "SELECT * FROM mysql.user",
            "SELECT * FROM farms -- comment", "SELECT * INTO OUTFILE '/tmp/x' FROM farms"]:
    check(f"Blocked: {bad[:45]}", lambda b=bad: assistant.validate_sql(b), "")
check("Allowed: SELECT on view", lambda: assistant.validate_sql("SELECT crop_name, SUM(available) FROM v_lot_stock GROUP BY crop_name"))

passed = sum(1 for r in results if r[0])
print(f"\n{passed}/{len(results)} tests passed")
sys.exit(0 if passed == len(results) else 1)
