"""Generate the editable Draw.io sources for the Track A database diagrams.

Outputs (overwritten):
  docs/diagrams/conceptual-er.drawio      one-page conceptual ER (Chen notation, (min,max))
  docs/diagrams/relational-schema.drawio  six-page relational schema (overview, 3 detail pages, unit/user FKs, views)

The column/type/constraint data below is transcribed from app/schema.sql; run
check_diagrams_vs_sql.py afterwards to verify the generated schema matches the DDL.
The .drawio files are the editable deliverables. After generation they may be edited
in Draw.io directly; re-running this script would overwrite such manual edits.

Usage (from repository root):
  python docs/diagrams/tools/generate_diagrams.py
"""
import html
import os
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

GREEN = "#2E7D32"
LIGHT = "#E8F5E9"
GREY = "#616161"
DERIVED = "#6A1B9A"
FONT = "fontFamily=Helvetica;"

# ---------------------------------------------------------------------------
# Relational model (from app/schema.sql). Column tuple:
#   (name, sql_type, key_marker, nullability/default, constraint_or_reference)
# ---------------------------------------------------------------------------
TABLES = {
    "emirates": [
        ("emirate_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("emirate_name", "VARCHAR(50)", "UQ", "NOT NULL", "UNIQUE"),
    ],
    "units": [
        ("unit_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("unit_code", "VARCHAR(10)", "UQ", "NOT NULL", "UNIQUE"),
        ("unit_name", "VARCHAR(40)", "", "NOT NULL", ""),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "crops": [
        ("crop_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("crop_name", "VARCHAR(60)", "UQ", "NOT NULL", "UNIQUE"),
        ("category", "VARCHAR(30)", "", "NOT NULL", "DEFAULT 'Vegetable'"),
        ("default_unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "markets": [
        ("market_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("market_name", "VARCHAR(100)", "UQ", "NOT NULL", "UNIQUE"),
        ("emirate_id", "INT", "FK", "NOT NULL", "→ emirates.emirate_id"),
        ("area", "VARCHAR(60)", "", "NULL", ""),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "farms": [
        ("farm_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("farm_name", "VARCHAR(100)", "UQ", "NOT NULL", "UNIQUE"),
        ("emirate_id", "INT", "FK", "NOT NULL", "→ emirates.emirate_id"),
        ("area", "VARCHAR(60)", "", "NULL", ""),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "users": [
        ("user_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("full_name", "VARCHAR(100)", "", "NOT NULL", ""),
        ("email", "VARCHAR(120)", "UQ", "NOT NULL", "UNIQUE"),
        ("role", "ENUM('farmer','market','admin')", "", "NOT NULL", ""),
        ("market_id", "INT", "FK", "NULL", "→ markets.market_id"),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "farm_users": [
        ("farm_id", "INT", "PK,FK", "NOT NULL", "→ farms.farm_id"),
        ("user_id", "INT", "PK,FK", "NOT NULL", "→ users.user_id"),
        ("assigned_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "crop_cycles": [
        ("cycle_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("farm_id", "INT", "FK", "NOT NULL", "→ farms.farm_id"),
        ("crop_id", "INT", "FK", "NOT NULL", "→ crops.crop_id"),
        ("planting_date", "DATE", "", "NOT NULL", ""),
        ("expected_harvest_date", "DATE", "", "NOT NULL", ""),
        ("expected_quantity", "DECIMAL(10,2)", "", "NOT NULL", "forecast only"),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("status", "ENUM('PLANNED','GROWING','HARVESTING','COMPLETED')", "", "NOT NULL", "DEFAULT 'GROWING'"),
        ("created_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("created_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "harvest_lots": [
        ("lot_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("cycle_id", "INT", "FK", "NOT NULL", "→ crop_cycles.cycle_id"),
        ("quantity_harvested", "DECIMAL(10,2)", "", "NOT NULL", ""),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("harvest_date", "DATE", "", "NOT NULL", ""),
        ("sell_by_date", "DATE", "", "NULL", ""),
        ("created_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("created_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
        ("is_active", "BOOLEAN", "", "NOT NULL", "DEFAULT TRUE"),
    ],
    "harvest_lot_images": [
        ("image_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("lot_id", "INT", "FK", "NOT NULL", "→ harvest_lots.lot_id"),
        ("file_name", "VARCHAR(150)", "", "NOT NULL", ""),
        ("mime_type", "VARCHAR(20)", "", "NOT NULL", ""),
        ("image_data", "MEDIUMBLOB", "", "NOT NULL", "binary photo"),
        ("uploaded_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("uploaded_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "market_requests": [
        ("request_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("market_id", "INT", "FK", "NOT NULL", "→ markets.market_id"),
        ("crop_id", "INT", "FK", "NOT NULL", "→ crops.crop_id"),
        ("requested_quantity", "DECIMAL(10,2)", "", "NOT NULL", ""),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("needed_by_date", "DATE", "", "NOT NULL", ""),
        ("status", "ENUM(6 values, see note)", "", "NOT NULL", "DEFAULT 'OPEN'"),
        ("notes", "VARCHAR(255)", "", "NULL", ""),
        ("created_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("created_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "request_status_history": [
        ("history_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("request_id", "INT", "FK", "NOT NULL", "→ market_requests.request_id"),
        ("old_status", "VARCHAR(25)", "", "NULL", "not an ENUM"),
        ("new_status", "VARCHAR(25)", "", "NOT NULL", "not an ENUM"),
        ("changed_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("changed_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
        ("reason", "VARCHAR(255)", "", "NULL", ""),
    ],
    "allocations": [
        ("allocation_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("request_id", "INT", "FK", "NOT NULL", "→ market_requests.request_id"),
        ("lot_id", "INT", "FK", "NOT NULL", "→ harvest_lots.lot_id"),
        ("allocated_quantity", "DECIMAL(10,2)", "", "NOT NULL", ""),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("status", "ENUM('RESERVED','DELIVERED','RELEASED')", "", "NOT NULL", "DEFAULT 'RESERVED'"),
        ("allocated_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("allocated_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "delivery_receipts": [
        ("receipt_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("allocation_id", "INT", "FK,UQ", "NOT NULL", "→ allocations.allocation_id; UNIQUE"),
        ("allocated_quantity", "DECIMAL(10,2)", "", "NOT NULL", "copy at receipt time"),
        ("received_quantity", "DECIMAL(10,2)", "", "NOT NULL", ""),
        ("discrepancy_quantity", "DECIMAL(10,2)", "", "NOT NULL", ""),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("discrepancy_reason", "VARCHAR(255)", "", "NULL", ""),
        ("received_date", "DATE", "", "NOT NULL", ""),
        ("confirmed_by", "INT", "FK", "NOT NULL", "→ users.user_id"),
        ("confirmed_at", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
    ],
    "stock_movements": [
        ("movement_id", "INT AUTO_INCREMENT", "PK", "NOT NULL", ""),
        ("lot_id", "INT", "FK", "NOT NULL", "→ harvest_lots.lot_id"),
        ("movement_type", "ENUM(8 values, see note)", "", "NOT NULL", ""),
        ("quantity", "DECIMAL(10,2)", "", "NOT NULL", "signed only for CORRECTION"),
        ("unit_id", "INT", "FK", "NOT NULL", "→ units.unit_id"),
        ("movement_date", "DATETIME", "", "NOT NULL", "DEFAULT CURRENT_TIMESTAMP"),
        ("user_id", "INT", "FK", "NOT NULL", "→ users.user_id (responsible user)"),
        ("reason", "VARCHAR(255)", "", "NULL", ""),
        ("allocation_id", "INT", "FK", "NULL", "→ allocations.allocation_id"),
    ],
}

# Table-level CHECK constraints and secondary indexes (exact SQL names)
TABLE_NOTES = {
    "users": ["chk_user_market: (role='market' AND market_id IS NOT NULL)",
              "   OR (role<>'market' AND market_id IS NULL)"],
    "farm_users": ["PRIMARY KEY (farm_id, user_id)"],
    "crop_cycles": ["chk_cycle_qty: expected_quantity >= 0",
                    "chk_cycle_dates: expected_harvest_date >= planting_date"],
    "harvest_lots": ["chk_lot_qty: quantity_harvested > 0",
                     "chk_lot_sell_by: sell_by_date IS NULL OR >= harvest_date",
                     "INDEX idx_lot_cycle (cycle_id)"],
    "harvest_lot_images": ["chk_img_type: mime_type IN ('image/jpeg','image/png')"],
    "market_requests": ["chk_req_qty: requested_quantity > 0",
                        "status ∈ OPEN, PARTIALLY_ALLOCATED, FULLY_ALLOCATED,",
                        "   PARTIALLY_DELIVERED, DELIVERED, CANCELLED"],
    "allocations": ["chk_alloc_qty: allocated_quantity > 0",
                    "INDEX idx_alloc_req (request_id)"],
    "delivery_receipts": ["chk_rcpt_nonneg: received_quantity >= 0",
                          "chk_rcpt_max: received_quantity <= allocated_quantity",
                          "chk_rcpt_diff: discrepancy = allocated − received"],
    "stock_movements": ["chk_mov_nonzero: quantity <> 0",
                        "chk_mov_sign: movement_type='CORRECTION' OR quantity > 0",
                        "type ∈ HARVEST_ADDED, RESERVED, RESERVATION_RELEASED,",
                        "   DELIVERED, LOSS, CORRECTION, DONATED, DISPOSED",
                        "INDEX idx_mov_lot (lot_id)"],
}


def fks():
    """Yield (child_table, column, parent_table, nullable, unique) for every FK."""
    for t, cols in TABLES.items():
        for name, _typ, key, null, ref in cols:
            if "FK" in key:
                parent = ref.split("→ ")[1].split(".")[0]
                yield t, name, parent, null == "NULL", "UQ" in key


# ---------------------------------------------------------------------------
# Minimal mxGraph XML writer
# ---------------------------------------------------------------------------
class Page:
    def __init__(self, name, page_id):
        self.name, self.page_id = name, page_id
        self.cells = []
        self.n = 0

    def nid(self, prefix):
        self.n += 1
        return f"{self.page_id}-{prefix}{self.n}"

    def vertex(self, value, x, y, w, h, style, parent="1", cid=None):
        cid = cid or self.nid("v")
        self.cells.append(
            f'<mxCell id="{cid}" value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def edge(self, src, tgt, style, value="", label_x=None, points=None):
        cid = self.nid("e")
        geo_inner = ""
        if points:
            geo_inner = "<Array as=\"points\">" + "".join(
                f'<mxPoint x="{px}" y="{py}"/>' for px, py in points) + "</Array>"
        xattr = f' x="{label_x}"' if label_x is not None else ""
        self.cells.append(
            f'<mxCell id="{cid}" value={quoteattr(value)} style={quoteattr(style)} edge="1" parent="1" '
            f'source="{src}" target="{tgt}"><mxGeometry{xattr} relative="1" as="geometry">{geo_inner}'
            f'</mxGeometry></mxCell>')
        return cid

    def xml(self):
        body = '<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(self.cells)
        return (f'<diagram id="{self.page_id}" name={quoteattr(self.name)}>'
                f'<mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" '
                f'connect="1" arrows="1" fold="1" page="0" pageScale="1" math="0" shadow="0">'
                f'<root>{body}</root></mxGraphModel></diagram>')


def write_file(path, pages):
    xml = ('<mxfile host="Electron" agent="generate_diagrams.py" type="device">'
           + "".join(p.xml() for p in pages) + "</mxfile>\n")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(xml)


def esc(s):
    return html.escape(s, quote=False)


TEXT = FONT + "text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacing=6;"
PANEL = FONT + "rounded=1;arcSize=4;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=10;"


# ---------------------------------------------------------------------------
# Relational schema
# ---------------------------------------------------------------------------
ROW_H = 22
HEAD_H = 30


def table(page, name, x, y, cols, widths, detail, stub=False):
    """Draw a draw.io ER table. Returns its id. Column count = len(widths)."""
    rows = cols if not stub else []
    h = HEAD_H + ROW_H * len(rows)
    fill = "#F5F5F5" if stub else LIGHT
    stroke = "#9E9E9E" if stub else GREEN
    title = name if not stub else f"{name}  (detailed on another page)"
    style = (FONT + f"shape=table;startSize={HEAD_H};container=1;collapsible=0;childLayout=tableLayout;"
             "fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;fontSize=13;"
             f"fillColor={fill};strokeColor={stroke};swimlaneFillColor=#FFFFFF;"
             + ("dashed=1;fontColor=#616161;fontStyle=2;" if stub else ""))
    tid = page.vertex(esc(title), x, y, sum(widths), h, style)
    for i, col in enumerate(rows):
        name_, typ, key, null, ref = col
        rid = page.vertex("", 0, HEAD_H + i * ROW_H, sum(widths), ROW_H,
                          "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;"
                          "fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];"
                          "portConstraint=eastwest;top=0;left=0;right=0;bottom=0;html=1;", parent=tid)
        bold = "PK" in key
        under = "fontStyle=5;" if bold else ("fontStyle=0;" if not key else "fontStyle=2;")
        if detail:
            values = [key, name_, typ, null, ref]
        else:
            values = [key, name_]
        xo = 0
        for j, (val, w) in enumerate(zip(values, widths)):
            st = (FONT + "shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;"
                  "overflow=hidden;whiteSpace=nowrap;html=1;fontSize=12;align=left;spacingLeft=6;")
            if j == 0:
                st += "fontStyle=1;fontColor=#1B5E20;"
            elif j == 1:
                st += under
            else:
                st += "fontColor=#424242;"
            page.vertex(esc(val), xo, 0, w, ROW_H, st, parent=rid)
            xo += w
    return tid, h


def fk_edge(page, child_id, parent_id, nullable, unique, label="", points=None, dashed=False, color=GREY):
    start = "ERzeroToOne" if unique else "ERzeroToMany"   # child side: how many children per parent
    end = "ERzeroToOne" if nullable else "ERmandOne"       # parent side: FK optional or mandatory
    style = (FONT + f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow={start};endArrow={end};"
             f"startFill=0;endFill=0;endSize=12;startSize=12;strokeColor={color};strokeWidth=1.3;"
             "fontSize=11;labelBackgroundColor=#FFFFFF;fontColor=#37474F;"
             + ("dashed=1;" if dashed else ""))
    return page.edge(child_id, parent_id, style, esc(label), points=points)


def legend_relational(page, x, y, w=560):
    txt = ("<b>Notation</b><br>"
           "<b>PK</b> primary key (underlined) · <b>FK</b> foreign key (italic) · <b>UQ</b> UNIQUE<br>"
           "Crow's foot at the FK (child) table: <i>zero-or-many</i>, or <i>zero-or-one</i> when the FK is UNIQUE.<br>"
           "Double bar at the referenced (parent) table: <i>exactly one</i> when the FK is NOT NULL; "
           "circle+bar: <i>zero-or-one</i> when the FK is nullable.<br>"
           "No ON DELETE/ON UPDATE actions are declared (MySQL default: RESTRICT/NO ACTION). "
           "No engine is named in the DDL (MySQL 8 default: InnoDB); charset utf8mb4.<br>"
           "Source of truth: <b>app/schema.sql</b>. Cross-row rules (unit equality, stock ≥ 0, "
           "farmer-only assignment) are enforced in app/db.py, not by SQL.")
    page.vertex(txt, x, y, w, 165, PANEL + "fillColor=#FFFDE7;strokeColor=#F9A825;fontSize=12;")


def build_relational():
    pages = []
    fkinfo = {(c, col): (par, nul, uq) for c, col, par, nul, uq in fks()}

    def draw_fk(pg, ids, child, col, points=None, dashed=False):
        par, nul, uq = fkinfo[(child, col)]
        return fk_edge(pg, ids[child], ids[par], nul, uq, col, points=points, dashed=dashed)

    # ---------- Page 1: overview ----------
    p = Page("1 Overview (all 15 tables)", "rs1")
    W = [52, 190]
    pos = {
        "users": (40, 60), "farm_users": (40, 300),
        "farms": (380, 60), "crop_cycles": (380, 260), "harvest_lots": (380, 570), "harvest_lot_images": (380, 860),
        "emirates": (720, 60), "units": (720, 170), "crops": (720, 330), "allocations": (720, 530),
        "stock_movements": (720, 790),
        "markets": (1060, 60), "market_requests": (1060, 260), "delivery_receipts": (1060, 570),
        "request_status_history": (1400, 260),
    }
    ids = {t: table(p, t, x, y, TABLES[t], W, detail=False)[0] for t, (x, y) in pos.items()}
    for child, col, pts in [
        ("markets", "emirate_id", None), ("farms", "emirate_id", None),
        ("users", "market_id", [(161, 25), (1181, 25)]),
        ("farm_users", "farm_id", [(330, 350), (330, 160)]), ("farm_users", "user_id", None),
        ("crop_cycles", "farm_id", None), ("crop_cycles", "crop_id", None), ("crops", "default_unit_id", None),
        ("harvest_lots", "cycle_id", None), ("harvest_lot_images", "lot_id", None),
        ("market_requests", "market_id", None), ("market_requests", "crop_id", None),
        ("request_status_history", "request_id", None),
        ("allocations", "request_id", [(1010, 600), (1010, 470)]),
        ("allocations", "lot_id", [(680, 640)]),
        ("delivery_receipts", "allocation_id", None),
        ("stock_movements", "lot_id", [(670, 900), (670, 760)]),
        ("stock_movements", "allocation_id", None),
    ]:
        draw_fk(p, ids, child, col, pts)
    p.vertex("<b>Relational schema — page 1: overview of all 15 base tables</b><br>"
             "Column names with key markers. Exact types, nullability, defaults and CHECK constraints: pages 2–4. "
             "The 15 FKs to <i>units</i>/<i>users</i> not drawn here (unit_id columns and the responsible-user "
             "columns created_by, uploaded_by, changed_by, allocated_by, confirmed_by, user_id) are marked FK "
             "in each table and drawn on page 5. Views: page 6.",
             1400, 560, 560, 130, PANEL + "fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;")
    legend_relational(p, 1400, 710)
    pages.append(p)

    WD = [52, 170, 360, 84, 250]
    TW = sum(WD)
    L, R = 40, 40 + TW + 90

    def place(pg, layout, stubs):
        tids = {}
        for t, (x, y) in layout.items():
            tid, h = table(pg, t, x, y, TABLES[t], WD, detail=True)
            notes = TABLE_NOTES.get(t)
            if notes:
                nh = 10 + 17 * len(notes)
                pg.vertex("<br>".join(esc(n) for n in notes), x, y + h, TW, nh,
                          FONT + "text;html=1;align=left;verticalAlign=top;spacingLeft=8;spacingTop=2;"
                          "fontSize=11;fontColor=#4E342E;fillColor=#FFF8E1;strokeColor=#FFE082;")
            tids[t] = tid
        for s, (x, y, w) in stubs.items():
            tids[s], _ = table(pg, s, x, y, [], [w], detail=False, stub=True)
        return tids

    # Page 2: reference data and users (all FKs among these tables drawn)
    p2 = Page("2 Reference data and users", "rs2")
    p2.vertex("<b>Relational schema — page 2: reference data, users and farm assignment</b> "
              "(exact SQL types, nullability, defaults and constraints)", 40, 10, 1400, 40, TEXT + "fontSize=14;")
    t2 = place(p2, {"emirates": (L, 70), "markets": (L, 210), "farms": (L, 410),
                    "units": (R, 70), "crops": (R, 250), "users": (R, 450), "farm_users": (R, 720)}, {})
    for child, col, pts in [
        ("markets", "emirate_id", None),
        ("farms", "emirate_id", [(20, 488), (20, 117)]),
        ("crops", "default_unit_id", None),
        ("users", "market_id", [(L + TW + 30, 557), (L + TW + 30, 300)]),
        ("farm_users", "farm_id", [(L + TW + 60, 785), (L + TW + 60, 500)]),
        ("farm_users", "user_id", None),
    ]:
        draw_fk(p2, t2, child, col, pts)
    legend_relational(p2, L, 620, TW)
    pages.append(p2)

    # Page 3: production, lots, images, ledger
    p3 = Page("3 Production, lots, images, stock ledger", "rs3")
    p3.vertex("<b>Relational schema — page 3: crop cycles (forecast), harvest lots (stock), BLOB images and the "
              "stock-movement ledger.</b> Grey dashed boxes are tables detailed on other pages. "
              "FKs to units/users are labelled in the rows and drawn on page 5.",
              40, 10, 1900, 40, TEXT + "fontSize=14;")
    t3 = place(p3, {"crop_cycles": (L, 140), "harvest_lots": (R, 140),
                    "harvest_lot_images": (L, 560), "stock_movements": (R, 520)},
               {"farms": (L, 70, 260), "crops": (L + 340, 70, 260), "allocations": (R + TW + 150, 640, 220)})
    for child, col, pts in [
        ("crop_cycles", "farm_id", [(L + 130, 110)]), ("crop_cycles", "crop_id", [(L + 470, 110)]),
        ("harvest_lots", "cycle_id", None),
        ("harvest_lot_images", "lot_id", [(L + TW + 45, 650), (L + TW + 45, 330)]),
        ("stock_movements", "lot_id", None),
        ("stock_movements", "allocation_id", None),
    ]:
        draw_fk(p3, t3, child, col, pts)
    pages.append(p3)

    # Page 4: demand and fulfilment
    p4 = Page("4 Requests, allocations, receipts", "rs4")
    p4.vertex("<b>Relational schema — page 4: market requests, status history, allocations and delivery "
              "receipts.</b> Grey dashed boxes are tables detailed on other pages. "
              "FKs to units/users are labelled in the rows and drawn on page 5.",
              40, 10, 1900, 40, TEXT + "fontSize=14;")
    t4 = place(p4, {"market_requests": (L, 140), "request_status_history": (L, 580),
                    "allocations": (R, 140), "delivery_receipts": (R, 500)},
               {"markets": (L, 70, 260), "crops": (L + 340, 70, 260), "harvest_lots": (R + 380, 70, 260)})
    for child, col, pts in [
        ("market_requests", "market_id", [(L + 130, 110)]), ("market_requests", "crop_id", [(L + 470, 110)]),
        ("request_status_history", "request_id", None),
        ("allocations", "request_id", None), ("allocations", "lot_id", [(R + 510, 110)]),
        ("delivery_receipts", "allocation_id", None),
    ]:
        draw_fk(p4, t4, child, col, pts)
    pages.append(p4)

    # Page 5: shared FKs to units and users
    p5 = Page("5 Unit and responsible-user FKs", "rs5")
    p5.vertex("<b>Relational schema — page 5: the 15 foreign keys to the shared tables <i>units</i> and "
              "<i>users</i>.</b> Every quantity carries an explicit unit (BR-06); every operational record keeps "
              "its responsible user (BR-08). Middle boxes list only each table's FK columns.",
              40, 10, 1500, 40, TEXT + "fontSize=14;")
    t5 = {}
    t5["units"], _ = table(p5, "units", 40, 400, TABLES["units"], [52, 150], detail=False)
    t5["users"], _ = table(p5, "users", 1300, 380, TABLES["users"], [52, 150], detail=False)
    mids = ["crops", "crop_cycles", "harvest_lots", "harvest_lot_images", "market_requests",
            "request_status_history", "allocations", "delivery_receipts", "stock_movements"]
    y = 70
    for t in mids:
        cols = [c for c in TABLES[t] if "FK" in c[2] and c[4].split("→ ")[1].split(".")[0] in ("units", "users")]
        t5[t], h = table(p5, t, 640, y, cols, [52, 230], detail=False)
        for c in cols:
            par = c[4].split("→ ")[1].split(".")[0]
            st = (FONT + "rounded=0;html=1;startArrow=ERzeroToMany;endArrow=ERmandOne;startFill=0;endFill=0;"
                  "endSize=12;startSize=12;strokeColor=" + ("#1565C0" if par == "units" else "#6D4C41") +
                  ";strokeWidth=1.2;fontSize=11;labelBackgroundColor=#FFFFFF;fontColor=#37474F;")
            side = "exitX=0;exitY=0.5;exitDx=0;exitDy=0;" if par == "units" else "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
            p5.edge(t5[t], t5[par], st + side, esc(c[0]), label_x=-0.45)
        y += h + 34
    p5.vertex("<font color=\"#1565C0\"><b>Blue</b></font>: 7 FKs → units.unit_id (all NOT NULL). "
              "<font color=\"#6D4C41\"><b>Brown</b></font>: 8 FKs → users.user_id (all NOT NULL; responsible "
              "user). Unit equality between a lot and its allocations, receipts and movements, and with the "
              "request it supplies, is checked in app/db.py; SQL only checks that each unit exists.",
              1300, 640, 420, 120, PANEL + "fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;")
    pages.append(p5)

    # ---------- Page 6: views ----------
    p6 = Page("6 Derived views (not stored)", "rs6")
    p6.vertex("<b>Relational schema — page 6: the two SQL views.</b> Views store no rows; they are recomputed "
              "from base tables on every query. The GUI and the read-only assistant read them.",
              40, 10, 1200, 40, TEXT + "fontSize=14;")
    vstyle = PANEL + "fillColor=#F3E5F5;strokeColor=#6A1B9A;dashed=1;fontSize=12;"
    v1 = p6.vertex(
        "<b>VIEW v_lot_stock</b> — one row per harvest lot<br><br>"
        "<b>Columns:</b> lot_id, cycle_id, farm_id, farm_name, emirate_name, crop_id, crop_name, unit_id, "
        "unit_code, quantity_harvested, harvest_date, sell_by_date, is_active, <i>on_hand</i>, <i>reserved</i>, "
        "<i>available</i><br><br>"
        "<b>Reads:</b> harvest_lots ⋈ crop_cycles ⋈ farms ⋈ emirates ⋈ crops ⋈ units, "
        "LEFT JOIN stock_movements, GROUP BY lot<br><br>"
        "<b>on_hand</b> = Σ HARVEST_ADDED + Σ CORRECTION (signed) − Σ DELIVERED − Σ LOSS − Σ DONATED − Σ DISPOSED<br>"
        "<b>reserved</b> = Σ RESERVED − Σ RESERVATION_RELEASED − Σ DELIVERED<br>"
        "<b>available</b> = on_hand − reserved<br><br>"
        "Unit = the lot's unit (units are never mixed). A lot with no movements shows 0/0/0. "
        "Expected harvest (crop_cycles.expected_quantity) is <u>not</u> an input: forecast stays separate from stock.",
        40, 70, 620, 300, vstyle)
    v2 = p6.vertex(
        "<b>VIEW v_request_status</b> — one row per market request<br><br>"
        "<b>Columns:</b> request_id, market_id, market_name, emirate_name, crop_id, crop_name, "
        "requested_quantity, unit_code, needed_by_date, status, created_at, <i>allocated_quantity</i>, "
        "<i>received_quantity</i><br><br>"
        "<b>Reads:</b> market_requests ⋈ markets ⋈ emirates ⋈ crops ⋈ units, with correlated sub-queries on "
        "allocations and delivery_receipts<br><br>"
        "<b>allocated_quantity</b> = Σ allocations.allocated_quantity WHERE status ≠ 'RELEASED' "
        "(includes already-delivered allocations)<br>"
        "<b>received_quantity</b> = Σ delivery_receipts.received_quantity over the request's allocations<br><br>"
        "<b>status</b> is the stored market_requests.status, maintained by app/db.py "
        "(_refresh_request_status); the view does not recompute it.",
        700, 70, 620, 300, vstyle)
    src = PANEL + "fillColor=" + LIGHT + ";strokeColor=" + GREEN + ";fontSize=12;align=center;verticalAlign=middle;"
    s1 = p6.vertex("<b>stock_movements</b><br>+ harvest_lots, crop_cycles, farms, emirates, crops, units",
                   40, 430, 620, 60, src)
    s2 = p6.vertex("<b>allocations, delivery_receipts</b><br>+ market_requests, markets, emirates, crops, units",
                   700, 430, 620, 60, src)
    dstyle = FONT + "endArrow=block;endFill=1;dashed=1;html=1;strokeColor=#6A1B9A;fontSize=11;labelBackgroundColor=#FFFFFF;"
    p6.edge(s1, v1, dstyle, "computed from")
    p6.edge(s2, v2, dstyle, "computed from")
    pages.append(p6)
    return pages


# ---------------------------------------------------------------------------
# Conceptual ER (Chen notation with (min,max))
# ---------------------------------------------------------------------------
ENT_W = 240


def entity(page, name, attrs, x, y):
    lines = []
    for a in attrs:
        if a.startswith("_"):
            lines.append(f"<u>{esc(a[1:])}</u>")
        elif a.startswith("/"):
            lines.append(f"<font color=\"{DERIVED}\"><i>{esc(a)}</i></font>")
        else:
            lines.append(esc(a))
    per_line = max(1, int((ENT_W - 16) / 6.6))
    n_lines = sum(-(-len(a.lstrip('_')) // per_line) for a in attrs)
    h = 34 + 17 * n_lines + 8
    style = (FONT + "swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=30;html=1;"
             f"fillColor={GREEN};fontColor=#FFFFFF;strokeColor={GREEN};swimlaneFillColor=#FFFFFF;"
             "collapsible=0;fontSize=14;rounded=0;")
    eid = page.vertex(esc(name), x, y, ENT_W, h, style)
    page.vertex("<br>".join(lines), 0, 30, ENT_W, h - 30,
                FONT + "text;html=1;align=left;verticalAlign=top;spacingLeft=8;spacingTop=3;fontSize=12;"
                "whiteSpace=wrap;", parent=eid)
    return eid, (x, y, ENT_W, h)


def build_conceptual():
    p = Page("Conceptual ER", "er1")
    E = {}
    spec = {
        "EMIRATE": (["_emirate_id", "emirate_name (unique)"], 900, 40),
        "FARM": (["_farm_id", "farm_name (unique)", "area", "is_active"], 340, 190),
        "MARKET": (["_market_id", "market_name (unique)", "area", "is_active"], 1460, 190),
        "USER": (["_user_id", "full_name", "email (unique)", "role {farmer | market | admin}", "is_active"], 900, 300),
        "CROP_CYCLE": (["_cycle_id", "planting_date", "expected_harvest_date", "expected_quantity (forecast)",
                        "status {PLANNED…COMPLETED}", "/remaining_expected"], 340, 560),
        "CROP": (["_crop_id", "crop_name (unique)", "category", "is_active"], 900, 580),
        "MARKET_REQUEST": (["_request_id", "requested_quantity", "needed_by_date", "status (6 values)", "notes",
                            "/allocated_quantity", "/received_quantity"], 1460, 560),
        "REQUEST_STATUS_CHANGE": (["_history_id", "old_status", "new_status", "changed_at", "reason"], 1980, 560),
        "UNIT": (["_unit_id", "unit_code (unique)", "unit_name", "is_active"], 900, 860),
        "HARVEST_LOT": (["_lot_id", "quantity_harvested", "harvest_date", "sell_by_date [optional]", "is_active",
                         "/on_hand", "/reserved", "/available"], 340, 980),
        "LOT_IMAGE": (["_image_id", "file_name", "mime_type {jpeg | png}", "image_data (BLOB)", "uploaded_at"],
                      40, 1330),
        "STOCK_MOVEMENT": (["_movement_id", "movement_type (8 values)", "quantity", "movement_date", "reason"],
                           560, 1360),
        "ALLOCATION": (["_allocation_id", "allocated_quantity", "status {RESERVED|DELIVERED|RELEASED}",
                        "allocated_at"], 1080, 1180),
        "DELIVERY_RECEIPT": (["_receipt_id", "allocated_quantity (copy)", "received_quantity",
                              "/discrepancy = allocated − received", "discrepancy_reason", "received_date"],
                             1640, 1180),
    }
    for n, (attrs, x, y) in spec.items():
        E[n] = entity(p, n, attrs, x, y)

    def center(n):
        x, y, w, h = E[n][1]
        return x + w / 2, y + h / 2

    dia = (FONT + "shape=rhombus;perimeter=rhombusPerimeter;whiteSpace=wrap;html=1;fillColor=#FFF8E1;"
           "strokeColor=#F57F17;fontSize=11;fontStyle=1;")
    line = (FONT + "endArrow=none;html=1;strokeColor=#455A64;strokeWidth=1.3;fontSize=12;fontStyle=1;"
            "labelBackgroundColor=#FFFFFF;fontColor=#BF360C;")

    def rel(name, a, ca, b, cb, at=None, dw=124, dh=58, la=-0.55, lb=-0.55, attr=None, total_a=False):
        ax, ay = center(a)
        bx, by = center(b)
        mx, my = at if at else ((ax + bx) / 2, (ay + by) / 2)
        did = p.vertex(esc(name), mx - dw / 2, my - dh / 2, dw, dh, dia)
        p.edge(E[a][0], did, line, ca, label_x=la)
        p.edge(E[b][0], did, line, cb, label_x=lb)
        if attr:
            aid = p.vertex(esc(attr), mx - 50, my + dh / 2 + 18, 100, 30,
                           FONT + "ellipse;whiteSpace=wrap;html=1;fontSize=11;fillColor=#FFFFFF;strokeColor=#F57F17;")
            p.edge(did, aid, FONT + "endArrow=none;html=1;strokeColor=#F57F17;", "")
        return did

    rel("LOCATED IN", "FARM", "(1,1)", "EMIRATE", "(0,N)", at=(700, 120))
    rel("LOCATED IN", "MARKET", "(1,1)", "EMIRATE", "(0,N)", at=(1310, 120))
    rel("ASSIGNED TO", "USER", "(0,N)", "FARM", "(0,N)", at=(700, 330), attr="assigned_at")
    rel("BUYS FOR", "USER", "(0,1)", "MARKET", "(0,N)", at=(1310, 330))
    rel("RUNS", "FARM", "(0,N)", "CROP_CYCLE", "(1,1)", at=(445, 450))
    rel("OF CROP", "CROP_CYCLE", "(1,1)", "CROP", "(0,N)", at=(735, 640))
    rel("REQUESTS", "MARKET_REQUEST", "(1,1)", "CROP", "(0,N)", at=(1300, 640))
    rel("PLACES", "MARKET", "(0,N)", "MARKET_REQUEST", "(1,1)", at=(1565, 450))
    rel("RECORDS", "MARKET_REQUEST", "(1,N)*", "REQUEST_STATUS_CHANGE", "(1,1)", at=(1820, 640), dw=110)
    rel("DEFAULT UNIT", "CROP", "(1,1)", "UNIT", "(0,N)", at=(1005, 800), dw=118)
    rel("FORECAST IN", "CROP_CYCLE", "(1,1)", "UNIT", "(0,N)", at=(700, 860), dw=118)
    rel("REQUESTED IN", "MARKET_REQUEST", "(1,1)", "UNIT", "(0,N)", at=(1300, 860), dw=124)
    rel("YIELDS", "CROP_CYCLE", "(0,N)", "HARVEST_LOT", "(1,1)", at=(445, 900))
    rel("MEASURED IN", "HARVEST_LOT", "(1,1)", "UNIT", "(0,N)", at=(735, 1010), dw=118)
    rel("PICTURED BY", "HARVEST_LOT", "(0,N)", "LOT_IMAGE", "(1,1)", at=(210, 1220), dw=118)
    rel("CHANGED BY", "HARVEST_LOT", "(1,N)*", "STOCK_MOVEMENT", "(1,1)", at=(560, 1270), dw=118)
    rel("SUPPLIES", "HARVEST_LOT", "(0,N)", "ALLOCATION", "(1,1)", at=(860, 1170))
    rel("FULFILLED BY", "MARKET_REQUEST", "(0,N)", "ALLOCATION", "(1,1)", at=(1460, 1000), dw=124)
    rel("CONFIRMED BY", "ALLOCATION", "(0,1)", "DELIVERY_RECEIPT", "(1,1)", at=(1505, 1250), dw=124)
    rel("CAUSES", "ALLOCATION", "(1,N)*", "STOCK_MOVEMENT", "(0,1)", at=(990, 1430))

    title = ("<b style=\"font-size:20px\">Farm-to-Market — Conceptual ER diagram</b><br>"
             "COSC444 Database Systems · Khalifa University · Lab B1 · Chen notation with (min,max) participation")
    p.vertex(title, 40, 20, 780, 60, TEXT + "fontSize=13;")

    legend = ("<b>How to read</b><br>"
              "Rectangle = entity; diamond = relationship; ellipse = relationship attribute.<br>"
              "<b>(min,max)</b> beside an entity = how many times one instance of that entity takes part in the "
              "relationship. Example: FARM (1,1) LOCATED IN EMIRATE (0,N) — every farm is in exactly one emirate; "
              "an emirate may have none or many farms.<br>"
              "<u>underlined</u> = identifier; <font color=\"#6A1B9A\"><i>/name</i></font> = derived (computed, "
              "not entered).<br><b>*</b> minimum guaranteed by the application, not by SQL: every lot gets a "
              "HARVEST_ADDED movement, every allocation a RESERVED movement and every request a "
              "'Request created' status row in the same transaction.")
    p.vertex(legend, 2020, 40, 440, 150, PANEL + "fillColor=#FFFDE7;strokeColor=#F9A825;fontSize=12;")

    rules = (
        "<b>Key business rules shown by the model</b><br>"
        "<b>R1</b> A farm runs many crop cycles; each lot comes from exactly one cycle, so a lot's crop and farm "
        "are derived through its cycle (BR-01).<br>"
        "<b>R2</b> expected_quantity is a <i>forecast</i> on CROP_CYCLE. Stock exists only on HARVEST_LOT and is "
        "never mixed with the forecast (BR-02).<br>"
        "<b>R3</b> /on_hand, /reserved, /available are <i>derived</i> from the dated STOCK_MOVEMENT ledger, never "
        "stored (BR-03).<br>"
        "<b>R4</b> ALLOCATION links one request to one lot. A request can be split across many lots (partial "
        "fulfilment) and a lot can supply many requests. An allocation can never exceed the lot's available "
        "quantity (BR-04, application-enforced under a lot row lock).<br>"
        "<b>R5</b> At most one DELIVERY_RECEIPT per allocation (UNIQUE). It records the received quantity; the "
        "shortfall is stored as the discrepancy, released from the reservation and recorded as LOSS (BR-05).<br>"
        "<b>R6</b> Every quantity is in an explicit UNIT. Allocations, receipts and movements carry the lot's "
        "unit; equality with the lot/request unit is application-enforced. There is no conversion (BR-06).<br>"
        "<b>R7</b> Only farmers are ASSIGNED TO farms; only market buyers BUY FOR exactly one market "
        "(SQL CHECK chk_user_market). Administrators have neither link (BR-07).<br>"
        "<b>R8</b> Each STOCK_MOVEMENT, REQUEST_STATUS_CHANGE, CROP_CYCLE, HARVEST_LOT, LOT_IMAGE, "
        "MARKET_REQUEST, ALLOCATION and DELIVERY_RECEIPT records exactly one responsible USER: USER (0,N) — "
        "record (1,1). These eight accountability links are drawn on relational schema page 5 (BR-08).<br>"
        "<b>R9</b> Every LOT_IMAGE belongs to exactly one lot and stores JPEG/PNG bytes (BLOB) (BR-09).<br>"
        "<b>R10</b> Reference entities and users are deactivated (is_active), not deleted, so history is kept.")
    p.vertex(rules, 2020, 900, 440, 470, PANEL + "fillColor=#FFFFFF;strokeColor=#2E7D32;fontSize=12;")
    return [p]


def main():
    write_file(os.path.join(OUT, "relational-schema.drawio"), build_relational())
    write_file(os.path.join(OUT, "conceptual-er.drawio"), build_conceptual())
    print("Wrote conceptual-er.drawio and relational-schema.drawio")


if __name__ == "__main__":
    main()
