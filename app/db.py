"""Database layer: connections, business rules and transactions.

Every query uses parameters (%s). Every change runs inside one transaction:
if any step fails, everything is rolled back (no partial updates).
"""
import os
import io
import datetime as dt
from decimal import Decimal, InvalidOperation
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MAX_IMAGE_BYTES = 5 * 1024 * 1024          # 5 MB
ALLOWED_IMAGE_EXT = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
MAX_QTY = Decimal("1000000")


class BusinessError(Exception):
    """A rule was broken. The message is shown to the user as-is."""


# ----------------------------------------------------------------------
# Connection helpers
# ----------------------------------------------------------------------
def db_settings():
    return dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "farm_market_db"),
    )


def get_connection():
    return pymysql.connect(
        **db_settings(), charset="utf8mb4", autocommit=False,
        cursorclass=pymysql.cursors.DictCursor, connect_timeout=5,
        init_command="SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")


@contextmanager
def transaction():
    """Open a connection, give a cursor, COMMIT on success, ROLLBACK on any error."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query(sql, params=()):
    with transaction() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def query_one(sql, params=()):
    rows = query(sql, params)
    return rows[0] if rows else None


def friendly_error(exc):
    """Turn any exception into a short message for the GUI (no raw SQL / passwords)."""
    if isinstance(exc, BusinessError):
        return str(exc)
    if isinstance(exc, pymysql.err.MySQLError):
        code = exc.args[0] if exc.args else None
        messages = {
            1045: "Database login failed. Check DB_USER and DB_PASSWORD in the .env file.",
            1049: "The database was not found. Run setup.bat first.",
            2003: "Cannot reach the MySQL server. Make sure MySQL is running.",
            2006: "The database connection was lost. Please try again.",
            2013: "The database connection was lost. Please try again.",
            1062: "This record already exists (duplicate name or email).",
            1452: "A linked record does not exist. Please refresh and try again.",
            1451: "This record is used by other records and cannot be removed.",
            3819: "A value is outside the allowed range.",
            4025: "A value is outside the allowed range.",
            1048: "A required field is missing.",
            1292: "A date or number has an invalid format.",
            1205: "The record is busy (another user is changing it). Please try again.",
            1213: "The record is busy (another user is changing it). Please try again.",
        }
        return messages.get(code, "A database error occurred. Please try again.")
    return "Something went wrong. Please try again."


# ----------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------
def parse_date(text, field, required=True):
    text = (text or "").strip()
    if not text:
        if required:
            raise BusinessError(f"{field} is required.")
        return None
    try:
        return dt.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise BusinessError(f"{field} must be a real date in the format YYYY-MM-DD.")


def parse_qty(text, field, allow_zero=False, allow_negative=False):
    text = str(text or "").strip()
    if not text:
        raise BusinessError(f"{field} is required.")
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise BusinessError(f"{field} must be a number.")
    if not value.is_finite():
        raise BusinessError(f"{field} must be a number.")
    if value.as_tuple().exponent < -2:
        raise BusinessError(f"{field} can have at most 2 decimal places.")
    if abs(value) > MAX_QTY:
        raise BusinessError(f"{field} is too large.")
    if allow_negative:
        if value == 0:
            raise BusinessError(f"{field} cannot be zero.")
    elif value < 0:
        raise BusinessError(f"{field} cannot be negative.")
    elif value == 0 and not allow_zero:
        raise BusinessError(f"{field} must be greater than zero.")
    return value


def require_text(text, field, max_len=255):
    text = (text or "").strip()
    if not text:
        raise BusinessError(f"{field} is required.")
    if len(text) > max_len:
        raise BusinessError(f"{field} is too long (max {max_len} characters).")
    return text


def fmt_qty(value):
    value = Decimal(value or 0)
    return f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"


def validate_image(path):
    """Return (file_name, mime, bytes) or raise BusinessError."""
    from PIL import Image
    if not path or not os.path.isfile(path):
        raise BusinessError("The selected image file was not found.")
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise BusinessError("Only JPG and PNG images are allowed.")
    size = os.path.getsize(path)
    if size == 0:
        raise BusinessError("The image file is empty.")
    if size > MAX_IMAGE_BYTES:
        raise BusinessError("The image is larger than 5 MB. Please choose a smaller image.")
    with open(path, "rb") as fh:
        data = fh.read()
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        if img.format not in ("JPEG", "PNG"):
            raise ValueError
        with Image.open(io.BytesIO(data)) as decoded:
            decoded.load()
    except Exception:
        raise BusinessError("This file is not a valid JPG or PNG image.")
    return os.path.basename(path)[:150], ALLOWED_IMAGE_EXT[ext], data


# ----------------------------------------------------------------------
# Users & permissions
# ----------------------------------------------------------------------
def list_demo_users():
    return query("""
        SELECT u.user_id, u.full_name, u.role, u.market_id, m.market_name,
               (SELECT GROUP_CONCAT(f.farm_name ORDER BY f.farm_name SEPARATOR ', ')
                  FROM farm_users fu JOIN farms f ON f.farm_id = fu.farm_id
                 WHERE fu.user_id = u.user_id) AS farms
        FROM users u LEFT JOIN markets m ON m.market_id = u.market_id
        WHERE u.is_active = TRUE
        ORDER BY FIELD(u.role,'farmer','market','admin'), u.full_name""")


def get_user(user_id):
    return query_one("SELECT * FROM users WHERE user_id=%s AND is_active=TRUE", (user_id,))


def farm_ids_for(cur, user_id):
    cur.execute("""SELECT fu.farm_id FROM farm_users fu JOIN farms f ON f.farm_id=fu.farm_id
                   WHERE fu.user_id=%s AND f.is_active=TRUE""", (user_id,))
    return {r["farm_id"] for r in cur.fetchall()}


def my_farm_ids(user_id):
    with transaction() as cur:
        return farm_ids_for(cur, user_id)


def _require_role(user, role):
    if user["role"] != role:
        names = {"farmer": "farmers", "market": "market buyers", "admin": "administrators"}
        raise BusinessError(f"Only {names[role]} can do this.")


# ----------------------------------------------------------------------
# Reference data (lists)
# ----------------------------------------------------------------------
def list_emirates():
    return query("SELECT emirate_id, emirate_name FROM emirates ORDER BY emirate_name")


def list_units(active_only=True):
    return query("SELECT * FROM units" + (" WHERE is_active=TRUE" if active_only else "") + " ORDER BY unit_code")


def list_crops(active_only=True):
    return query("""SELECT c.*, u.unit_code AS default_unit FROM crops c
                    JOIN units u ON u.unit_id=c.default_unit_id"""
                 + (" WHERE c.is_active=TRUE" if active_only else "") + " ORDER BY c.crop_name")


def list_markets(active_only=True):
    return query("""SELECT m.*, e.emirate_name FROM markets m JOIN emirates e ON e.emirate_id=m.emirate_id"""
                 + (" WHERE m.is_active=TRUE" if active_only else "") + " ORDER BY m.market_name")


def list_farms(active_only=True, farm_ids=None):
    sql = """SELECT f.*, e.emirate_name,
                    (SELECT GROUP_CONCAT(u.full_name SEPARATOR ', ') FROM farm_users fu
                       JOIN users u ON u.user_id=fu.user_id WHERE fu.farm_id=f.farm_id) AS farmers
             FROM farms f JOIN emirates e ON e.emirate_id=f.emirate_id WHERE 1=1"""
    params = []
    if active_only:
        sql += " AND f.is_active=TRUE"
    if farm_ids is not None:
        if not farm_ids:
            return []
        sql += " AND f.farm_id IN (" + ",".join(["%s"] * len(farm_ids)) + ")"
        params += list(farm_ids)
    return query(sql + " ORDER BY f.farm_name", params)


def _check_active(cur, table, key, value, label):
    cur.execute(f"SELECT is_active FROM {table} WHERE {key}=%s", (value,))
    row = cur.fetchone()
    if not row:
        raise BusinessError(f"Unknown {label}. Please pick one from the list.")
    if not row["is_active"]:
        raise BusinessError(f"This {label} is inactive and cannot be used.")


# ----------------------------------------------------------------------
# Farmer: farms and crop cycles
# ----------------------------------------------------------------------
def add_farm(user, name, emirate_id, area):
    _require_role(user, "farmer")
    name = require_text(name, "Farm name", 100)
    if not emirate_id:
        raise BusinessError("Please choose an emirate.")
    with transaction() as cur:
        cur.execute("INSERT INTO farms (farm_name, emirate_id, area) VALUES (%s,%s,%s)",
                    (name, emirate_id, (area or "").strip()[:60] or None))
        farm_id = cur.lastrowid
        cur.execute("INSERT INTO farm_users (farm_id, user_id) VALUES (%s,%s)", (farm_id, user["user_id"]))
    return farm_id


def list_cycles(farm_ids):
    if not farm_ids:
        return []
    marks = ",".join(["%s"] * len(farm_ids))
    return query(f"""
        SELECT cc.*, f.farm_name, c.crop_name, u.unit_code,
               COALESCE((SELECT SUM(l.quantity_harvested) FROM harvest_lots l
                          WHERE l.cycle_id=cc.cycle_id), 0) AS harvested
        FROM crop_cycles cc JOIN farms f ON f.farm_id=cc.farm_id
        JOIN crops c ON c.crop_id=cc.crop_id JOIN units u ON u.unit_id=cc.unit_id
        WHERE cc.farm_id IN ({marks})
        ORDER BY FIELD(cc.status,'HARVESTING','GROWING','PLANNED','COMPLETED'), cc.expected_harvest_date""",
                 list(farm_ids))


def add_cycle(user, farm_id, crop_id, planting, expected_date, expected_qty, unit_id):
    _require_role(user, "farmer")
    if not farm_id or not crop_id or not unit_id:
        raise BusinessError("Please choose a farm, crop and unit.")
    planting = parse_date(planting, "Planting date")
    expected_date = parse_date(expected_date, "Expected harvest date")
    qty = parse_qty(expected_qty, "Expected quantity", allow_zero=True)
    if expected_date < planting:
        raise BusinessError("Expected harvest date cannot be before the planting date.")
    with transaction() as cur:
        if farm_id not in farm_ids_for(cur, user["user_id"]):
            raise BusinessError("You can only change farms assigned to you.")
        _check_active(cur, "crops", "crop_id", crop_id, "crop")
        _check_active(cur, "units", "unit_id", unit_id, "unit")
        status = "PLANNED" if planting > dt.date.today() else "GROWING"
        cur.execute("""INSERT INTO crop_cycles (farm_id, crop_id, planting_date, expected_harvest_date,
                       expected_quantity, unit_id, status, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (farm_id, crop_id, planting, expected_date, qty, unit_id, status, user["user_id"]))
        return cur.lastrowid


def complete_cycle(user, cycle_id):
    _require_role(user, "farmer")
    with transaction() as cur:
        cur.execute("SELECT farm_id, status FROM crop_cycles WHERE cycle_id=%s FOR UPDATE", (cycle_id,))
        cyc = cur.fetchone()
        if not cyc:
            raise BusinessError("Crop cycle not found.")
        if cyc["farm_id"] not in farm_ids_for(cur, user["user_id"]):
            raise BusinessError("You can only change farms assigned to you.")
        if cyc["status"] == "COMPLETED":
            raise BusinessError("This crop cycle is already completed.")
        cur.execute("UPDATE crop_cycles SET status='COMPLETED' WHERE cycle_id=%s", (cycle_id,))


def stock_summary(farm_ids):
    """Expected (forecast), on hand, reserved, available — grouped per crop AND unit (never mixed)."""
    if not farm_ids:
        return []
    marks = ",".join(["%s"] * len(farm_ids))
    ids = list(farm_ids)
    return query(f"""
        SELECT k.crop_name, k.unit_code,
               COALESCE(s.on_hand,0) AS on_hand, COALESCE(s.reserved,0) AS reserved,
               COALESCE(s.available,0) AS available, COALESCE(x.expected,0) AS expected
        FROM (
            SELECT DISTINCT c.crop_name, u.unit_code FROM crop_cycles cc
            JOIN crops c ON c.crop_id=cc.crop_id JOIN units u ON u.unit_id=cc.unit_id
            WHERE cc.farm_id IN ({marks})
        ) k
        LEFT JOIN (
            SELECT crop_name, unit_code, SUM(on_hand) on_hand, SUM(reserved) reserved, SUM(available) available
            FROM v_lot_stock WHERE farm_id IN ({marks}) AND is_active=TRUE GROUP BY crop_name, unit_code
        ) s ON s.crop_name=k.crop_name AND s.unit_code=k.unit_code
        LEFT JOIN (
            SELECT c.crop_name, u.unit_code,
                   SUM(GREATEST(cc.expected_quantity - COALESCE(h.harvested,0), 0)) expected
            FROM crop_cycles cc JOIN crops c ON c.crop_id=cc.crop_id JOIN units u ON u.unit_id=cc.unit_id
            LEFT JOIN (SELECT cycle_id, SUM(quantity_harvested) harvested FROM harvest_lots GROUP BY cycle_id) h
                   ON h.cycle_id=cc.cycle_id
            WHERE cc.farm_id IN ({marks}) AND cc.status <> 'COMPLETED'
            GROUP BY c.crop_name, u.unit_code
        ) x ON x.crop_name=k.crop_name AND x.unit_code=k.unit_code
        ORDER BY k.crop_name""", ids + ids + ids)


# ----------------------------------------------------------------------
# Harvest lots, stock movements, images
# ----------------------------------------------------------------------
def lot_available(cur, lot_id, lock=True):
    """Lock the lot row (prevents two users overselling at the same time) and return its stock."""
    cur.execute("SELECT * FROM harvest_lots WHERE lot_id=%s" + (" FOR UPDATE" if lock else ""), (lot_id,))
    lot = cur.fetchone()
    if not lot:
        raise BusinessError("Harvest lot not found.")
    cur.execute("SELECT * FROM v_lot_stock WHERE lot_id=%s", (lot_id,))
    return lot, cur.fetchone()


def _check_lot_owner(cur, user, lot_id):
    cur.execute("""SELECT cc.farm_id FROM harvest_lots l JOIN crop_cycles cc ON cc.cycle_id=l.cycle_id
                   WHERE l.lot_id=%s""", (lot_id,))
    row = cur.fetchone()
    if not row:
        raise BusinessError("Harvest lot not found.")
    if row["farm_id"] not in farm_ids_for(cur, user["user_id"]):
        raise BusinessError("You can only change lots from farms assigned to you.")


def list_lots(farm_ids=None):
    sql = """SELECT s.*, (SELECT COUNT(*) FROM harvest_lot_images i WHERE i.lot_id=s.lot_id) AS photos
             FROM v_lot_stock s WHERE s.is_active=TRUE"""
    params = []
    if farm_ids is not None:
        if not farm_ids:
            return []
        sql += " AND s.farm_id IN (" + ",".join(["%s"] * len(farm_ids)) + ")"
        params = list(farm_ids)
    return query(sql + " ORDER BY s.harvest_date DESC, s.lot_id DESC", params)


def record_harvest(user, cycle_id, qty, harvest_date, sell_by, image_path=None):
    _require_role(user, "farmer")
    if not cycle_id:
        raise BusinessError("Please choose a crop cycle.")
    qty = parse_qty(qty, "Harvested quantity")
    harvest_date = parse_date(harvest_date, "Harvest date")
    sell_by = parse_date(sell_by, "Sell-by date", required=False)
    if harvest_date > dt.date.today():
        raise BusinessError("Harvest date cannot be in the future.")
    if sell_by and sell_by < harvest_date:
        raise BusinessError("Sell-by date cannot be before the harvest date.")
    image = validate_image(image_path) if image_path else None
    with transaction() as cur:
        cur.execute("SELECT * FROM crop_cycles WHERE cycle_id=%s FOR UPDATE", (cycle_id,))
        cyc = cur.fetchone()
        if not cyc:
            raise BusinessError("Crop cycle not found.")
        if cyc["farm_id"] not in farm_ids_for(cur, user["user_id"]):
            raise BusinessError("You can only record harvests for farms assigned to you.")
        if cyc["status"] == "COMPLETED":
            raise BusinessError("This crop cycle is completed. Choose an active cycle.")
        if harvest_date < cyc["planting_date"]:
            raise BusinessError("Harvest date cannot be before the planting date.")
        cur.execute("""INSERT INTO harvest_lots (cycle_id, quantity_harvested, unit_id, harvest_date,
                       sell_by_date, created_by) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (cycle_id, qty, cyc["unit_id"], harvest_date, sell_by, user["user_id"]))
        lot_id = cur.lastrowid
        cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason)
                       VALUES (%s,'HARVEST_ADDED',%s,%s,%s,'Harvest recorded')""",
                    (lot_id, qty, cyc["unit_id"], user["user_id"]))
        if cyc["status"] in ("PLANNED", "GROWING"):
            cur.execute("UPDATE crop_cycles SET status='HARVESTING' WHERE cycle_id=%s", (cycle_id,))
        if image:
            cur.execute("""INSERT INTO harvest_lot_images (lot_id, file_name, mime_type, image_data, uploaded_by)
                           VALUES (%s,%s,%s,%s,%s)""", (lot_id, image[0], image[1], image[2], user["user_id"]))
    return lot_id


def add_lot_image(user, lot_id, path):
    _require_role(user, "farmer")
    name, mime, data = validate_image(path)
    with transaction() as cur:
        _check_lot_owner(cur, user, lot_id)
        cur.execute("""INSERT INTO harvest_lot_images (lot_id, file_name, mime_type, image_data, uploaded_by)
                       VALUES (%s,%s,%s,%s,%s)""", (lot_id, name, mime, data, user["user_id"]))


def lot_images(lot_id):
    return query("""SELECT image_id, file_name, image_data, uploaded_at FROM harvest_lot_images
                    WHERE lot_id=%s ORDER BY image_id DESC""", (lot_id,))


def lot_movements(lot_id):
    return query("""SELECT m.movement_date, m.movement_type, m.quantity, u.unit_code, us.full_name, m.reason
                    FROM stock_movements m JOIN units u ON u.unit_id=m.unit_id
                    JOIN users us ON us.user_id=m.user_id
                    WHERE m.lot_id=%s ORDER BY m.movement_date, m.movement_id""", (lot_id,))


def record_adjustment(user, lot_id, kind, qty, reason):
    """kind = 'LOSS' (positive qty) or 'CORRECTION' (+/- qty). Reason is mandatory."""
    _require_role(user, "farmer")
    if kind not in ("LOSS", "CORRECTION"):
        raise BusinessError("Choose Loss or Correction.")
    qty = parse_qty(qty, "Quantity", allow_negative=(kind == "CORRECTION"))
    reason = require_text(reason, "Reason")
    with transaction() as cur:
        _check_lot_owner(cur, user, lot_id)
        lot, stock = lot_available(cur, lot_id)
        removing = qty if kind == "LOSS" else -qty
        if removing > 0 and removing > stock["available"]:
            raise BusinessError(f"Only {fmt_qty(stock['available'])} {stock['unit_code']} is available in lot "
                                f"#{lot_id}. Reserved stock cannot be removed.")
        cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (lot_id, kind, qty, lot["unit_id"], user["user_id"],
                     ("Approved correction: " if kind == "CORRECTION" else "") + reason))


# ----------------------------------------------------------------------
# Market requests
# ----------------------------------------------------------------------
def _refresh_request_status(cur, request_id, user_id, reason):
    cur.execute("SELECT status, requested_quantity FROM market_requests WHERE request_id=%s FOR UPDATE", (request_id,))
    req = cur.fetchone()
    if req["status"] == "CANCELLED":
        return
    cur.execute("""SELECT COALESCE(SUM(CASE WHEN status<>'RELEASED' THEN allocated_quantity END),0) AS alloc,
                          COALESCE(SUM(status='DELIVERED'),0) AS delivered,
                          COALESCE(SUM(status='RESERVED'),0) AS reserved
                   FROM allocations WHERE request_id=%s""", (request_id,))
    a = cur.fetchone()
    if a["alloc"] == 0:
        new = "OPEN"
    elif a["delivered"] > 0:
        new = "DELIVERED" if (a["reserved"] == 0 and a["alloc"] >= req["requested_quantity"]) else "PARTIALLY_DELIVERED"
    elif a["alloc"] < req["requested_quantity"]:
        new = "PARTIALLY_ALLOCATED"
    else:
        new = "FULLY_ALLOCATED"
    if new != req["status"]:
        cur.execute("UPDATE market_requests SET status=%s WHERE request_id=%s", (new, request_id))
        cur.execute("""INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
                       VALUES (%s,%s,%s,%s,%s)""", (request_id, req["status"], new, user_id, reason))


def list_requests(market_id=None, open_only=False):
    sql = "SELECT * FROM v_request_status WHERE 1=1"
    params = []
    if market_id:
        sql += " AND market_id=%s"
        params.append(market_id)
    if open_only:
        sql += " AND status IN ('OPEN','PARTIALLY_ALLOCATED')"
    return query(sql + " ORDER BY FIELD(status,'OPEN','PARTIALLY_ALLOCATED','FULLY_ALLOCATED',"
                       "'PARTIALLY_DELIVERED','DELIVERED','CANCELLED'), needed_by_date", params)


def request_history(request_id):
    return query("""SELECT h.changed_at, h.old_status, h.new_status, u.full_name, h.reason
                    FROM request_status_history h JOIN users u ON u.user_id=h.changed_by
                    WHERE h.request_id=%s ORDER BY h.changed_at, h.history_id""", (request_id,))


def create_request(user, crop_id, qty, unit_id, needed_by, notes):
    _require_role(user, "market")
    if not crop_id or not unit_id:
        raise BusinessError("Please choose a crop and a unit.")
    qty = parse_qty(qty, "Requested quantity")
    needed_by = parse_date(needed_by, "Needed-by date")
    if needed_by < dt.date.today():
        raise BusinessError("Needed-by date cannot be in the past.")
    with transaction() as cur:
        _check_active(cur, "crops", "crop_id", crop_id, "crop")
        _check_active(cur, "units", "unit_id", unit_id, "unit")
        cur.execute("""INSERT INTO market_requests (market_id, crop_id, requested_quantity, unit_id,
                       needed_by_date, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (user["market_id"], crop_id, qty, unit_id, needed_by,
                     (notes or "").strip()[:255] or None, user["user_id"]))
        rid = cur.lastrowid
        cur.execute("""INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
                       VALUES (%s,NULL,'OPEN',%s,'Request created')""", (rid, user["user_id"]))
    return rid


def _lock_own_request(cur, user, request_id):
    cur.execute("SELECT * FROM market_requests WHERE request_id=%s FOR UPDATE", (request_id,))
    req = cur.fetchone()
    if not req:
        raise BusinessError("Request not found.")
    if req["market_id"] != user["market_id"]:
        raise BusinessError("You can only manage your own market's requests.")
    return req


def update_request(user, request_id, qty, needed_by, notes):
    _require_role(user, "market")
    qty = parse_qty(qty, "Requested quantity")
    needed_by = parse_date(needed_by, "Needed-by date")
    if needed_by < dt.date.today():
        raise BusinessError("Needed-by date cannot be in the past.")
    with transaction() as cur:
        req = _lock_own_request(cur, user, request_id)
        if req["status"] in ("DELIVERED", "CANCELLED"):
            raise BusinessError("Delivered or cancelled requests cannot be changed.")
        cur.execute("""SELECT COALESCE(SUM(allocated_quantity),0) a FROM allocations
                       WHERE request_id=%s AND status<>'RELEASED'""", (request_id,))
        allocated = cur.fetchone()["a"]
        if qty < allocated:
            raise BusinessError(f"Quantity cannot be less than what is already allocated ({fmt_qty(allocated)}).")
        cur.execute("""UPDATE market_requests SET requested_quantity=%s, needed_by_date=%s, notes=%s
                       WHERE request_id=%s""", (qty, needed_by, (notes or "").strip()[:255] or None, request_id))
        _refresh_request_status(cur, request_id, user["user_id"], "Request quantity updated")


def cancel_request(user, request_id, reason):
    _require_role(user, "market")
    reason = require_text(reason, "Reason")
    with transaction() as cur:
        req = _lock_own_request(cur, user, request_id)
        if req["status"] in ("DELIVERED", "CANCELLED"):
            raise BusinessError("This request is already closed.")
        cur.execute("SELECT * FROM allocations WHERE request_id=%s ORDER BY allocation_id FOR UPDATE", (request_id,))
        allocs = cur.fetchall()
        if any(a["status"] == "DELIVERED" for a in allocs):
            raise BusinessError("This request already has deliveries and cannot be cancelled.")
        for lot_id in sorted({a["lot_id"] for a in allocs if a["status"] == "RESERVED"}):
            lot_available(cur, lot_id)
        for a in allocs:
            if a["status"] == "RESERVED":
                cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id,
                               reason, allocation_id) VALUES (%s,'RESERVATION_RELEASED',%s,%s,%s,%s,%s)""",
                            (a["lot_id"], a["allocated_quantity"], a["unit_id"], user["user_id"],
                             f"Request #{request_id} cancelled", a["allocation_id"]))
                cur.execute("UPDATE allocations SET status='RELEASED' WHERE allocation_id=%s", (a["allocation_id"],))
        cur.execute("UPDATE market_requests SET status='CANCELLED' WHERE request_id=%s", (request_id,))
        cur.execute("""INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
                       VALUES (%s,%s,'CANCELLED',%s,%s)""", (request_id, req["status"], user["user_id"], reason))


# ----------------------------------------------------------------------
# Farmer: allocations
# ----------------------------------------------------------------------
def allocatable_lots(user, request_id):
    req = query_one("SELECT crop_id, unit_id FROM market_requests WHERE request_id=%s", (request_id,))
    ids = my_farm_ids(user["user_id"])
    if not req or not ids:
        return []
    marks = ",".join(["%s"] * len(ids))
    return query(f"""SELECT * FROM v_lot_stock WHERE crop_id=%s AND unit_id=%s AND available>0
                     AND is_active=TRUE AND farm_id IN ({marks})
                     ORDER BY sell_by_date IS NULL, sell_by_date, harvest_date""",
                 [req["crop_id"], req["unit_id"]] + list(ids))


def allocate(user, request_id, lot_id, qty):
    _require_role(user, "farmer")
    if not request_id or not lot_id:
        raise BusinessError("Select a request and a harvest lot first.")
    qty = parse_qty(qty, "Allocation quantity")
    with transaction() as cur:
        cur.execute("SELECT * FROM market_requests WHERE request_id=%s FOR UPDATE", (request_id,))
        req = cur.fetchone()
        if not req:
            raise BusinessError("Request not found.")
        if req["status"] not in ("OPEN", "PARTIALLY_ALLOCATED"):
            raise BusinessError("This request is not open for allocation.")
        _check_lot_owner(cur, user, lot_id)
        lot, stock = lot_available(cur, lot_id)
        if stock["crop_id"] != req["crop_id"]:
            raise BusinessError("This lot is a different crop from the request.")
        if lot["unit_id"] != req["unit_id"]:
            raise BusinessError("The lot and the request use different units. "
                                "Quantities in different units cannot be mixed.")
        if qty > stock["available"]:
            raise BusinessError(f"Not enough stock. Lot #{lot_id} has only {fmt_qty(stock['available'])} "
                                f"{stock['unit_code']} available.")
        cur.execute("""SELECT COALESCE(SUM(allocated_quantity),0) a FROM allocations
                       WHERE request_id=%s AND status<>'RELEASED'""", (request_id,))
        remaining = req["requested_quantity"] - cur.fetchone()["a"]
        if qty > remaining:
            raise BusinessError(f"The request only needs {fmt_qty(remaining)} {stock['unit_code']} more.")
        cur.execute("""INSERT INTO allocations (request_id, lot_id, allocated_quantity, unit_id, allocated_by)
                       VALUES (%s,%s,%s,%s,%s)""", (request_id, lot_id, qty, lot["unit_id"], user["user_id"]))
        alloc_id = cur.lastrowid
        cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason,
                       allocation_id) VALUES (%s,'RESERVED',%s,%s,%s,%s,%s)""",
                    (lot_id, qty, lot["unit_id"], user["user_id"], f"Allocated to request #{request_id}", alloc_id))
        _refresh_request_status(cur, request_id, user["user_id"],
                                f"Allocated {fmt_qty(qty)} {stock['unit_code']} from lot #{lot_id}")
    return alloc_id


def list_allocations(request_id=None, farm_ids=None, market_id=None, status=None):
    sql = """SELECT a.*, u.unit_code, s.farm_name, s.crop_name, r.market_id, mk.market_name,
                    d.received_quantity, d.discrepancy_quantity, d.discrepancy_reason
             FROM allocations a JOIN units u ON u.unit_id=a.unit_id
             JOIN v_lot_stock s ON s.lot_id=a.lot_id
             JOIN market_requests r ON r.request_id=a.request_id
             JOIN markets mk ON mk.market_id=r.market_id
             LEFT JOIN delivery_receipts d ON d.allocation_id=a.allocation_id WHERE 1=1"""
    params = []
    if request_id:
        sql += " AND a.request_id=%s"
        params.append(request_id)
    if farm_ids is not None:
        if not farm_ids:
            return []
        sql += " AND s.farm_id IN (" + ",".join(["%s"] * len(farm_ids)) + ")"
        params += list(farm_ids)
    if market_id:
        sql += " AND r.market_id=%s"
        params.append(market_id)
    if status:
        sql += " AND a.status=%s"
        params.append(status)
    return query(sql + " ORDER BY a.allocated_at DESC", params)


def _lock_allocation(cur, allocation_id):
    """Lock parent request before allocation; all request changes use the same order."""
    cur.execute("SELECT request_id FROM allocations WHERE allocation_id=%s", (allocation_id,))
    link = cur.fetchone()
    if not link:
        raise BusinessError("Allocation not found.")
    cur.execute("SELECT request_id FROM market_requests WHERE request_id=%s FOR UPDATE",
                (link["request_id"],))
    cur.execute("""SELECT a.*, r.market_id FROM allocations a
                   JOIN market_requests r ON r.request_id=a.request_id
                   WHERE a.allocation_id=%s FOR UPDATE""", (allocation_id,))
    allocation = cur.fetchone()
    if not allocation:
        raise BusinessError("Allocation not found.")
    return allocation


def release_allocation(user, allocation_id, reason):
    _require_role(user, "farmer")
    reason = require_text(reason, "Reason")
    with transaction() as cur:
        a = _lock_allocation(cur, allocation_id)
        _check_lot_owner(cur, user, a["lot_id"])
        if a["status"] != "RESERVED":
            raise BusinessError("Only reserved (not yet delivered) allocations can be released.")
        lot_available(cur, a["lot_id"])
        cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason,
                       allocation_id) VALUES (%s,'RESERVATION_RELEASED',%s,%s,%s,%s,%s)""",
                    (a["lot_id"], a["allocated_quantity"], a["unit_id"], user["user_id"], reason, allocation_id))
        cur.execute("UPDATE allocations SET status='RELEASED' WHERE allocation_id=%s", (allocation_id,))
        _refresh_request_status(cur, a["request_id"], user["user_id"], "Allocation released: " + reason)


# ----------------------------------------------------------------------
# Market: delivery confirmation
# ----------------------------------------------------------------------
def confirm_delivery(user, allocation_id, received, reason):
    _require_role(user, "market")
    if not allocation_id:
        raise BusinessError("Select a pending delivery first.")
    received = parse_qty(received, "Received quantity", allow_zero=True)
    with transaction() as cur:
        a = _lock_allocation(cur, allocation_id)
        if a["market_id"] != user["market_id"]:
            raise BusinessError("You can only confirm deliveries for your own market.")
        if a["status"] != "RESERVED":
            raise BusinessError("This delivery was already confirmed or released.")
        if received > a["allocated_quantity"]:
            raise BusinessError(f"Received quantity cannot be more than the allocated "
                                f"{fmt_qty(a['allocated_quantity'])}.")
        diff = a["allocated_quantity"] - received
        reason = (reason or "").strip()
        if diff > 0 and not reason:
            raise BusinessError("Please enter a reason for the difference (discrepancy).")
        lot_available(cur, a["lot_id"])
        uid, lot, unit = user["user_id"], a["lot_id"], a["unit_id"]
        cur.execute("""INSERT INTO delivery_receipts (allocation_id, allocated_quantity, received_quantity,
                       discrepancy_quantity, unit_id, discrepancy_reason, received_date, confirmed_by)
                       VALUES (%s,%s,%s,%s,%s,%s,CURDATE(),%s)""",
                    (allocation_id, a["allocated_quantity"], received, diff, unit, reason[:255] or None, uid))
        receipt = cur.lastrowid
        if received > 0:
            cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason,
                           allocation_id) VALUES (%s,'DELIVERED',%s,%s,%s,%s,%s)""",
                        (lot, received, unit, uid, f"Delivery receipt #{receipt}", allocation_id))
        if diff > 0:
            cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason,
                           allocation_id) VALUES (%s,'RESERVATION_RELEASED',%s,%s,%s,%s,%s)""",
                        (lot, diff, unit, uid, f"Delivery discrepancy (receipt #{receipt})", allocation_id))
            cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason,
                           allocation_id) VALUES (%s,'LOSS',%s,%s,%s,%s,%s)""",
                        (lot, diff, unit, uid, ("Delivery discrepancy: " + reason)[:255], allocation_id))
        cur.execute("UPDATE allocations SET status='DELIVERED' WHERE allocation_id=%s", (allocation_id,))
        _refresh_request_status(cur, a["request_id"], uid,
                                f"Received {fmt_qty(received)} of {fmt_qty(a['allocated_quantity'])}")
    return receipt


def list_receipts(market_id=None):
    sql = """SELECT d.*, u.unit_code, a.request_id, a.lot_id, s.crop_name, s.farm_name, mk.market_name
             FROM delivery_receipts d JOIN allocations a ON a.allocation_id=d.allocation_id
             JOIN units u ON u.unit_id=d.unit_id JOIN v_lot_stock s ON s.lot_id=a.lot_id
             JOIN market_requests r ON r.request_id=a.request_id
             JOIN markets mk ON mk.market_id=r.market_id"""
    params = []
    if market_id:
        sql += " WHERE r.market_id=%s"
        params.append(market_id)
    return query(sql + " ORDER BY d.confirmed_at DESC", params)


# ----------------------------------------------------------------------
# Search & status views (all roles)
# ----------------------------------------------------------------------
def search_lots(crop_id=None, emirate=None, farm_id=None, min_available=None,
                date_from=None, date_to=None, availability="Any", sellable_on=None):
    sql = """SELECT s.*, (SELECT COUNT(*) FROM harvest_lot_images i WHERE i.lot_id=s.lot_id) AS photos
             FROM v_lot_stock s WHERE s.is_active=TRUE"""
    p = []
    if crop_id:
        sql += " AND s.crop_id=%s"; p.append(crop_id)
    if emirate:
        sql += " AND s.emirate_name=%s"; p.append(emirate)
    if farm_id:
        sql += " AND s.farm_id=%s"; p.append(farm_id)
    if min_available not in (None, ""):
        sql += " AND s.available >= %s"; p.append(parse_qty(min_available, "Minimum quantity", allow_zero=True))
    d1 = parse_date(date_from, "From date", required=False)
    d2 = parse_date(date_to, "To date", required=False)
    if d1 and d2 and d2 < d1:
        raise BusinessError("'To date' cannot be before 'From date'.")
    if d1:
        sql += " AND s.harvest_date >= %s"; p.append(d1)
    if d2:
        sql += " AND s.harvest_date <= %s"; p.append(d2)
    d3 = parse_date(sellable_on, "Available on", required=False)
    if d3:
        sql += " AND s.harvest_date <= %s AND (s.sell_by_date IS NULL OR s.sell_by_date >= %s)"; p += [d3, d3]
    if availability == "Available":
        sql += " AND s.available > 0"
    elif availability == "Fully reserved":
        sql += " AND s.available <= 0 AND s.reserved > 0"
    elif availability == "Sold out":
        sql += " AND s.on_hand <= 0"
    return query(sql + " ORDER BY s.crop_name, s.available DESC", p)


def search_requests(crop_id=None, emirate=None, market_id=None, status=None, date_from=None, date_to=None):
    sql = "SELECT * FROM v_request_status WHERE 1=1"
    p = []
    if crop_id:
        sql += " AND crop_id=%s"; p.append(crop_id)
    if emirate:
        sql += " AND emirate_name=%s"; p.append(emirate)
    if market_id:
        sql += " AND market_id=%s"; p.append(market_id)
    if status:
        sql += " AND status=%s"; p.append(status)
    d1 = parse_date(date_from, "From date", required=False)
    d2 = parse_date(date_to, "To date", required=False)
    if d1 and d2 and d2 < d1:
        raise BusinessError("'To date' cannot be before 'From date'.")
    if d1:
        sql += " AND needed_by_date >= %s"; p.append(d1)
    if d2:
        sql += " AND needed_by_date <= %s"; p.append(d2)
    return query(sql + " ORDER BY needed_by_date", p)


# ----------------------------------------------------------------------
# ADVANCED FEATURE: Loss & surplus management
#   Rule 1 EXPIRED      : available > 0 AND sell_by_date <  today
#   Rule 2 NEAR EXPIRY  : available > 0 AND sell_by_date <= today + N days
#   Rule 3 SURPLUS      : available > 0 AND never allocated AND harvested >= M days ago
#   Priority: Expired (1) > Near expiry (2) > Surplus (3); then fewest days left, then most stock.
# ----------------------------------------------------------------------
def flagged_lots(near_days, surplus_days, farm_ids=None):
    try:
        near_days, surplus_days = int(near_days), int(surplus_days)
    except (TypeError, ValueError):
        raise BusinessError("Thresholds must be whole numbers of days.")
    if not (0 <= near_days <= 60 and 0 <= surplus_days <= 365):
        raise BusinessError("Use 0-60 days for expiry and 0-365 days for surplus.")
    sql = """
        SELECT * FROM (
          SELECT s.*, DATEDIFF(s.sell_by_date, CURDATE()) AS days_left,
                 DATEDIFF(CURDATE(), s.harvest_date) AS age_days,
                 (SELECT COUNT(*) FROM allocations a WHERE a.lot_id=s.lot_id AND a.status<>'RELEASED') AS alloc_count
          FROM v_lot_stock s WHERE s.is_active=TRUE AND s.available > 0
        ) t
        WHERE ((t.sell_by_date IS NOT NULL AND t.sell_by_date <= CURDATE() + INTERVAL %s DAY)
           OR (t.alloc_count = 0 AND t.age_days >= %s))"""
    p = [near_days, surplus_days]
    if farm_ids is not None:
        if not farm_ids:
            return []
        sql += " AND t.farm_id IN (" + ",".join(["%s"] * len(farm_ids)) + ")"
        p += list(farm_ids)
    rows = query(sql, p)
    for r in rows:
        if r["sell_by_date"] and r["days_left"] < 0:
            r["flag"], r["priority"] = "EXPIRED", 1
        elif r["sell_by_date"] and r["days_left"] <= near_days:
            r["flag"], r["priority"] = "NEAR EXPIRY", 2
        else:
            r["flag"], r["priority"] = "UNALLOCATED SURPLUS", 3
    rows.sort(key=lambda r: (r["priority"], r["days_left"] if r["days_left"] is not None else 9999,
                             -r["available"]))
    return rows


def dispose_lot(user, lot_id, action, qty, note):
    """action = 'DONATED' or 'DISPOSED'. Only from available (unreserved) stock."""
    _require_role(user, "farmer")
    if action not in ("DONATED", "DISPOSED"):
        raise BusinessError("Choose Donate or Dispose.")
    qty = parse_qty(qty, "Quantity")
    note = require_text(note, "Recipient / reason")
    with transaction() as cur:
        _check_lot_owner(cur, user, lot_id)
        lot, stock = lot_available(cur, lot_id)
        if qty > stock["available"]:
            raise BusinessError(f"Only {fmt_qty(stock['available'])} {stock['unit_code']} is available in lot "
                                f"#{lot_id}. Reserved stock cannot be donated or disposed.")
        label = "Donated to: " if action == "DONATED" else "Disposed: "
        cur.execute("""INSERT INTO stock_movements (lot_id, movement_type, quantity, unit_id, user_id, reason)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (lot_id, action, qty, lot["unit_id"], user["user_id"], (label + note)[:255]))


def disposition_history(farm_ids=None):
    sql = """SELECT m.movement_date, m.movement_type, m.lot_id, s.crop_name, s.farm_name, m.quantity,
                    u.unit_code, us.full_name, m.reason
             FROM stock_movements m JOIN v_lot_stock s ON s.lot_id=m.lot_id
             JOIN units u ON u.unit_id=m.unit_id JOIN users us ON us.user_id=m.user_id
             WHERE m.movement_type IN ('DONATED','DISPOSED')"""
    p = []
    if farm_ids is not None:
        if not farm_ids:
            return []
        sql += " AND s.farm_id IN (" + ",".join(["%s"] * len(farm_ids)) + ")"
        p = list(farm_ids)
    return query(sql + " ORDER BY m.movement_date DESC", p)


# ----------------------------------------------------------------------
# Administrator: users and reference data (no transaction editing)
# ----------------------------------------------------------------------
def list_users():
    return query("""SELECT u.*, m.market_name,
                       (SELECT GROUP_CONCAT(f.farm_name SEPARATOR ', ') FROM farm_users fu
                          JOIN farms f ON f.farm_id=fu.farm_id WHERE fu.user_id=u.user_id) AS farms
                    FROM users u LEFT JOIN markets m ON m.market_id=u.market_id
                    ORDER BY u.role, u.full_name""")


def add_user(admin, name, email, role, market_id):
    _require_role(admin, "admin")
    name = require_text(name, "Full name", 100)
    email = require_text(email, "Email", 120).lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise BusinessError("Please enter a valid email address.")
    if role not in ("farmer", "market", "admin"):
        raise BusinessError("Please choose a role.")
    if role == "market" and not market_id:
        raise BusinessError("Market buyers must be linked to a market.")
    with transaction() as cur:
        cur.execute("INSERT INTO users (full_name, email, role, market_id) VALUES (%s,%s,%s,%s)",
                    (name, email, role, market_id if role == "market" else None))
        return cur.lastrowid


def assign_farm(admin, user_id, farm_id):
    _require_role(admin, "admin")
    if not user_id or not farm_id:
        raise BusinessError("Select a farmer and a farm.")
    with transaction() as cur:
        cur.execute("SELECT role FROM users WHERE user_id=%s", (user_id,))
        u = cur.fetchone()
        if not u or u["role"] != "farmer":
            raise BusinessError("Farms can only be assigned to farmers.")
        cur.execute("SELECT 1 FROM farm_users WHERE user_id=%s AND farm_id=%s", (user_id, farm_id))
        if cur.fetchone():
            raise BusinessError("This farmer is already assigned to that farm.")
        cur.execute("INSERT INTO farm_users (farm_id, user_id) VALUES (%s,%s)", (farm_id, user_id))


ACTIVE_TABLES = {"users": "user_id", "crops": "crop_id", "units": "unit_id",
                 "markets": "market_id", "farms": "farm_id"}


def set_active(admin, table, record_id, active):
    """Records are deactivated (not deleted) so history is kept."""
    _require_role(admin, "admin")
    key = ACTIVE_TABLES[table]
    if table == "users" and record_id == admin["user_id"] and not active:
        raise BusinessError("You cannot deactivate your own account.")
    with transaction() as cur:
        cur.execute(f"UPDATE {table} SET is_active=%s WHERE {key}=%s", (bool(active), record_id))


def add_crop(admin, name, category, unit_id):
    _require_role(admin, "admin")
    name = require_text(name, "Crop name", 60)
    if not unit_id:
        raise BusinessError("Please choose a default unit.")
    with transaction() as cur:
        cur.execute("INSERT INTO crops (crop_name, category, default_unit_id) VALUES (%s,%s,%s)",
                    (name, (category or "Vegetable").strip()[:30], unit_id))


def add_unit(admin, code, name):
    _require_role(admin, "admin")
    code = require_text(code, "Unit code", 10)
    name = require_text(name, "Unit name", 40)
    with transaction() as cur:
        cur.execute("INSERT INTO units (unit_code, unit_name) VALUES (%s,%s)", (code, name))


def add_market(admin, name, emirate_id, area):
    _require_role(admin, "admin")
    name = require_text(name, "Market name", 100)
    if not emirate_id:
        raise BusinessError("Please choose an emirate.")
    with transaction() as cur:
        cur.execute("INSERT INTO markets (market_name, emirate_id, area) VALUES (%s,%s,%s)",
                    (name, emirate_id, (area or "").strip()[:60] or None))
