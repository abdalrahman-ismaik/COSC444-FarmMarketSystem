"""Cross-check the Draw.io diagram sources against the live MySQL schema.

Read-only. Parses docs/diagrams/relational-schema.drawio and conceptual-er.drawio
(the actual XML, not the generator's data) and compares them with information_schema
of the database configured in app/.env (DB_NAME, normally farm_market_db).

Checks:
  1. Every base table and view in the database appears in the schema diagram, and no extra tables.
  2. Detailed rows (pages 2-4): column order, SQL type, NULL/NOT NULL, PK/UQ/FK markers,
     defaults and FK targets match information_schema.
  3. Every FK in the database is drawn as an edge labelled with the FK column between the
     correct tables on at least one page, with the correct optionality end marker; no edge
     claims an FK that does not exist.
  4. Every CHECK constraint name in the database is shown in the diagram.
  5. The conceptual diagram contains the proposal's core entities.

Usage (repository root, runtime venv):
  .venv\\Scripts\\python.exe docs\\diagrams\\tools\\check_diagrams_vs_sql.py [diagram_dir]
Exit code 0 when every check passes. diagram_dir defaults to docs/diagrams (useful for
mutation-testing a modified copy).
"""
import html
import os
import re
import sys
import xml.etree.ElementTree as ET

import pymysql
from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DIAG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "diagrams")
load_dotenv(os.path.join(ROOT, "app", ".env"))

failures = []
passes = 0


def ok(cond, msg):
    global passes
    if cond:
        passes += 1
    else:
        failures.append(msg)


def text(v):
    v = re.sub(r"<[^>]+>", "", v or "")
    return html.unescape(v).replace("\xa0", " ").strip()


def load_pages(path):
    root = ET.parse(path).getroot()
    pages = []
    for d in root.findall("diagram"):
        cells = {c.get("id"): c for c in d.iter("mxCell")}
        pages.append((d.get("name"), cells))
    return pages


def tables_on_page(cells):
    """Return {table_name: {"id": id, "rows": [[cell values]], "stub": bool}}."""
    out = {}
    for cid, c in cells.items():
        st = c.get("style") or ""
        if "shape=table;" in st:
            name = text(c.get("value")).split("  (")[0]
            rows = []
            row_ids = [r for r in cells.values() if r.get("parent") == cid and "shape=tableRow" in (r.get("style") or "")]
            row_ids.sort(key=lambda r: float(r.find("mxGeometry").get("y")))
            for r in row_ids:
                vals = [x for x in cells.values() if x.get("parent") == r.get("id")]
                vals.sort(key=lambda x: float(x.find("mxGeometry").get("x")))
                rows.append([text(x.get("value")) for x in vals])
            out[name] = {"id": cid, "rows": rows, "stub": "dashed=1" in st}
    return out


def norm_type(diagram_type, col):
    """Map diagram notation to information_schema COLUMN_TYPE/EXTRA."""
    t = diagram_type.upper()
    db = col["COLUMN_TYPE"].upper()
    if t == "INT AUTO_INCREMENT":
        return db == "INT" and "auto_increment" in col["EXTRA"]
    if t == "BOOLEAN":
        return db == "TINYINT(1)"
    m = re.match(r"ENUM\((\d+) VALUES", t)
    if m:
        return db.startswith("ENUM(") and db.count("'") // 2 == int(m.group(1))
    return t == db


def main():
    conn = pymysql.connect(host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
                           user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""),
                           database=os.getenv("DB_NAME", "farm_market_db"),
                           cursorclass=pymysql.cursors.DictCursor)
    schema = os.getenv("DB_NAME", "farm_market_db")
    with conn.cursor() as cur:
        cur.execute("SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s", (schema,))
        kinds = {r["TABLE_NAME"]: r["TABLE_TYPE"] for r in cur.fetchall()}
        cur.execute("""SELECT TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY,
                              COLUMN_DEFAULT, EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s
                       ORDER BY TABLE_NAME, ORDINAL_POSITION""", (schema,))
        cols = {}
        for r in cur.fetchall():
            cols.setdefault(r["TABLE_NAME"], []).append(r)
        cur.execute("""SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                       FROM information_schema.KEY_COLUMN_USAGE
                       WHERE TABLE_SCHEMA=%s AND REFERENCED_TABLE_NAME IS NOT NULL""", (schema,))
        db_fks = {(r["TABLE_NAME"], r["COLUMN_NAME"]): r["REFERENCED_TABLE_NAME"] for r in cur.fetchall()}
        cur.execute("""SELECT k.TABLE_NAME, k.COLUMN_NAME FROM information_schema.TABLE_CONSTRAINTS t
                       JOIN information_schema.KEY_COLUMN_USAGE k ON k.CONSTRAINT_NAME=t.CONSTRAINT_NAME
                        AND k.TABLE_NAME=t.TABLE_NAME AND k.TABLE_SCHEMA=t.TABLE_SCHEMA
                       WHERE t.TABLE_SCHEMA=%s AND t.CONSTRAINT_TYPE='UNIQUE'""", (schema,))
        uniques = {(r["TABLE_NAME"], r["COLUMN_NAME"]) for r in cur.fetchall()}
        cur.execute("""SELECT k.TABLE_NAME, k.COLUMN_NAME FROM information_schema.TABLE_CONSTRAINTS t
                       JOIN information_schema.KEY_COLUMN_USAGE k ON k.CONSTRAINT_NAME=t.CONSTRAINT_NAME
                        AND k.TABLE_NAME=t.TABLE_NAME AND k.TABLE_SCHEMA=t.TABLE_SCHEMA
                       WHERE t.TABLE_SCHEMA=%s AND t.CONSTRAINT_TYPE='PRIMARY KEY'""", (schema,))
        pks = {(r["TABLE_NAME"], r["COLUMN_NAME"]) for r in cur.fetchall()}
        cur.execute("""SELECT TABLE_NAME, CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS
                       WHERE TABLE_SCHEMA=%s AND CONSTRAINT_TYPE='CHECK'""", (schema,))
        checks = [(r["TABLE_NAME"], r["CONSTRAINT_NAME"]) for r in cur.fetchall()]
        cur.execute("""SELECT TABLE_NAME, INDEX_NAME FROM information_schema.STATISTICS
                       WHERE TABLE_SCHEMA=%s AND INDEX_NAME LIKE 'idx\\_%%'""", (schema,))
        indexes = {(r["TABLE_NAME"], r["INDEX_NAME"]) for r in cur.fetchall()}
    conn.close()

    base = sorted(t for t, k in kinds.items() if k == "BASE TABLE")
    views = sorted(t for t, k in kinds.items() if k == "VIEW")
    print(f"Database {schema}: {len(base)} base tables, {len(views)} views, {len(db_fks)} FKs, "
          f"{len(checks)} CHECK constraints")

    pages = load_pages(os.path.join(DIAG, "relational-schema.drawio"))
    all_text = " ".join(text(c.get("value")) for _, cells in pages for c in cells.values())

    # 1. table coverage
    overview = tables_on_page(pages[0][1])
    ok(sorted(overview) == base, f"overview tables {sorted(overview)} != DB {base}")
    for v in views:
        ok(f"VIEW {v}" in all_text, f"view {v} not described")

    # 2. detailed rows
    detailed = {}
    for name, cells in pages[1:4]:
        for t, info in tables_on_page(cells).items():
            if not info["stub"]:
                detailed[t] = info
    ok(sorted(detailed) == base, f"detailed tables {sorted(detailed)} != DB {base}")
    for t, info in detailed.items():
        dbc = cols.get(t, [])
        ok(len(info["rows"]) == len(dbc), f"{t}: {len(info['rows'])} rows drawn vs {len(dbc)} columns")
        for row, c in zip(info["rows"], dbc):
            key, name, typ, null, ref = (row + [""] * 5)[:5]
            where = f"{t}.{c['COLUMN_NAME']}"
            ok(name == c["COLUMN_NAME"], f"{where}: drawn as {name} (column order/name)")
            ok(norm_type(typ, c), f"{where}: type {typ} vs {c['COLUMN_TYPE']} {c['EXTRA']}")
            ok((null == "NULL") == (c["IS_NULLABLE"] == "YES"), f"{where}: nullability {null} vs {c['IS_NULLABLE']}")
            ok(("PK" in key) == ((t, c["COLUMN_NAME"]) in pks), f"{where}: PK marker {key!r}")
            ok(("FK" in key) == ((t, c["COLUMN_NAME"]) in db_fks), f"{where}: FK marker {key!r}")
            ok(("UQ" in key) == ((t, c["COLUMN_NAME"]) in uniques), f"{where}: UQ marker {key!r}")
            if (t, c["COLUMN_NAME"]) in db_fks:
                ok(f"→ {db_fks[(t, c['COLUMN_NAME'])]}." in ref, f"{where}: FK target {ref!r}")
            dflt = c["COLUMN_DEFAULT"]
            if dflt is not None and "auto_increment" not in c["EXTRA"]:
                exp = {"1": "TRUE", "CURRENT_TIMESTAMP": "CURRENT_TIMESTAMP"}.get(dflt, f"'{dflt}'")
                ok(f"DEFAULT {exp}" in ref, f"{where}: default {dflt!r} not shown ({ref!r})")
            elif "DEFAULT" in ref:
                failures.append(f"{where}: diagram shows a default that the DB lacks ({ref!r})")

    # 3. FK edges
    drawn = set()
    for pname, cells in pages:
        tables = tables_on_page(cells)
        by_id = {v["id"]: k for k, v in tables.items()}
        for c in cells.values():
            if c.get("edge") != "1":
                continue
            src, tgt = by_id.get(c.get("source")), by_id.get(c.get("target"))
            if not src or not tgt:
                continue
            col = text(c.get("value"))
            st = c.get("style") or ""
            claimed = (src, col)
            ok(db_fks.get(claimed) == tgt, f"page '{pname}': edge {src}.{col} -> {tgt} is not a DB FK")
            nullable = next((r["IS_NULLABLE"] == "YES" for r in cols.get(src, []) if r["COLUMN_NAME"] == col), None)
            want_end = "endArrow=ERzeroToOne" if nullable else "endArrow=ERmandOne"
            ok(want_end in st, f"page '{pname}': edge {src}.{col} optionality marker")
            want_start = "startArrow=ERzeroToOne" if claimed in uniques else "startArrow=ERzeroToMany"
            ok(want_start in st, f"page '{pname}': edge {src}.{col} child-side marker")
            drawn.add(claimed)
    missing = sorted(set(db_fks) - drawn)
    ok(not missing, f"FKs never drawn as edges: {missing}")

    # 4. CHECK constraint names and secondary indexes
    for t, name in checks:
        ok(name in all_text, f"CHECK {t}.{name} not shown")
    for t, name in indexes:
        ok(name in all_text, f"INDEX {t}.{name} not shown")

    # 5. conceptual entities
    er = load_pages(os.path.join(DIAG, "conceptual-er.drawio"))[0][1]
    er_text = {text(c.get("value")) for c in er.values()}
    for ent in ["FARM", "USER", "CROP", "CROP_CYCLE", "HARVEST_LOT", "LOT_IMAGE", "STOCK_MOVEMENT", "MARKET",
                "MARKET_REQUEST", "ALLOCATION", "DELIVERY_RECEIPT"]:
        ok(ent in er_text, f"conceptual ER lacks entity {ent}")

    print(f"{passes} checks passed, {len(failures)} failed; FK edges drawn {len(drawn)}/{len(db_fks)}")
    for f in failures:
        print("FAIL", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
