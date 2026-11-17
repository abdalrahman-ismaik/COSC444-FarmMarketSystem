"""Farm-to-Market: Local Farm and Market Food Availability System (Tkinter GUI).

Run:  python app.py
"""
import gc
import io
import queue
import threading
import datetime as dt
import tkinter as tk
from decimal import Decimal
from tkinter import ttk, messagebox, filedialog, font as tkfont

from PIL import Image, ImageTk, ImageDraw

import db
from assistant import Assistant

# ----------------------------------------------------------------------
# Look & feel
# ----------------------------------------------------------------------
GREEN, DARK, LIGHT, BG = "#2E7D32", "#1B5E20", "#E8F5E9", "#F4F6F4"
RED, AMBER, BLUE, GREY, TEXT = "#C62828", "#EF6C00", "#1565C0", "#6B7280", "#1F2933"

ROLE_INFO = {
    "farmer": ("☘", "Farmer", GREEN),
    "market": ("⚖", "Market Buyer", BLUE),
    "admin": ("⚙", "Administrator", "#6A1B9A"),
}
STATUS_LABEL = {
    "OPEN": "○ Open", "PARTIALLY_ALLOCATED": "◐ Partly allocated", "FULLY_ALLOCATED": "● Allocated",
    "PARTIALLY_DELIVERED": "◑ Partly delivered", "DELIVERED": "✔ Delivered", "CANCELLED": "✖ Cancelled",
    "RESERVED": "● Reserved", "RELEASED": "↺ Released",
    "PLANNED": "○ Planned", "GROWING": "☘ Growing", "HARVESTING": "▣ Harvesting", "COMPLETED": "✔ Completed",
}
MOVEMENT_LABEL = {
    "HARVEST_ADDED": "✚ Harvest added", "RESERVED": "● Reserved", "RESERVATION_RELEASED": "↺ Released",
    "DELIVERED": "⇨ Delivered", "LOSS": "✖ Loss", "CORRECTION": "✎ Correction",
    "DONATED": "♥ Donated", "DISPOSED": "✖ Disposed",
}
FLAG_LABEL = {"EXPIRED": "⚠ Expired", "NEAR EXPIRY": "⏱ Near expiry", "UNALLOCATED SURPLUS": "▣ Surplus"}


def today():
    return dt.date.today().isoformat()


def fmt(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, Decimal):
        return db.fmt_qty(value)
    if isinstance(value, float):
        return db.fmt_qty(Decimal(str(value)))
    if isinstance(value, dt.datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def active_fmt(v):
    return "✔ Active" if v else "✖ Inactive"


def setup_style(root):
    families = set(tkfont.families(root))
    base = next((f for f in ("Segoe UI", "Helvetica Neue", "DejaVu Sans", "Arial") if f in families), "TkDefaultFont")
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(name).configure(family=base, size=10)
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=TEXT, font=(base, 10))
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
    s.configure("TLabel", background=BG)
    s.configure("Card.TLabel", background="white")
    s.configure("Title.TLabel", font=(base, 15, "bold"), foreground=DARK)
    s.configure("Section.TLabel", font=(base, 11, "bold"), foreground=DARK)
    s.configure("Muted.TLabel", foreground=GREY)
    s.configure("Error.TLabel", foreground=RED, background="white", font=(base, 10, "bold"))
    s.configure("TButton", padding=(12, 6), background="white", bordercolor="#C9D1C9")
    s.map("TButton", background=[("active", LIGHT), ("disabled", "#EEEEEE")])
    s.configure("Primary.TButton", background=GREEN, foreground="white", bordercolor=GREEN,
                font=(base, 10, "bold"))
    s.map("Primary.TButton", background=[("active", DARK), ("disabled", "#9DBF9F")])
    s.configure("Danger.TButton", background="white", foreground=RED, bordercolor=RED)
    s.map("Danger.TButton", background=[("active", "#FDECEA")])
    s.configure("Header.TButton", background=DARK, foreground="white", bordercolor="white")
    s.map("Header.TButton", background=[("active", GREEN)])
    s.configure("Role.TButton", background="white", anchor="w", padding=(14, 10), font=(base, 11))
    s.map("Role.TButton", background=[("active", LIGHT)])
    s.configure("TNotebook", background=BG, borderwidth=0)
    s.configure("TNotebook.Tab", padding=(16, 8), font=(base, 10, "bold"))
    s.map("TNotebook.Tab", background=[("selected", "white"), ("!selected", "#DDE5DD")],
          foreground=[("selected", DARK)])
    s.configure("Treeview", rowheight=28, fieldbackground="white", background="white")
    s.configure("Treeview.Heading", font=(base, 10, "bold"), background="#DDE8DD", padding=(6, 6))
    s.map("Treeview", background=[("selected", "#A5D6A7")], foreground=[("selected", TEXT)])
    s.configure("TEntry", padding=5)
    s.configure("TCombobox", padding=4)
    s.configure("TLabelframe", background=BG)
    s.configure("TLabelframe.Label", background=BG, foreground=DARK, font=(base, 10, "bold"))
    return base


# ----------------------------------------------------------------------
# Reusable widgets
# ----------------------------------------------------------------------
class LookupCombo(ttk.Combobox):
    """Read-only dropdown that shows labels but returns ids."""

    def __init__(self, parent, options=(), all_label=None, width=24):
        super().__init__(parent, state="readonly", width=width)
        self.set_options(options, all_label)

    def set_options(self, options, all_label=None):
        self._items = ([(all_label, None)] if all_label else []) + list(options)
        self["values"] = [label for label, _ in self._items]
        if self._items:
            self.current(0)
        else:
            self.set("")

    def value(self):
        i = self.current()
        return self._items[i][1] if i >= 0 else None

    def set_value(self, v):
        for i, (_, val) in enumerate(self._items):
            if val == v:
                self.current(i)
                return


class Table(ttk.Frame):
    """Treeview + scrollbar + record count. columns = [(key, heading, width, anchor[, formatter])]."""

    def __init__(self, parent, columns, height=8, on_select=None, tag_fn=None):
        super().__init__(parent)
        self.columns, self.tag_fn, self._rows = columns, tag_fn, {}
        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns], show="headings",
                                 height=height, selectmode="browse")
        for c in columns:
            self.tree.heading(c[0], text=c[1])
            self.tree.column(c[0], width=c[2], anchor=c[3], minwidth=40)
        ys = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.count = ttk.Label(self, style="Muted.TLabel")
        self.count.grid(row=2, column=0, sticky="w", pady=(2, 0))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        for tag, color in (("red", "#FDECEA"), ("amber", "#FFF3E0"), ("blue", "#E3F2FD"),
                           ("green", "#E8F5E9"), ("odd", "#FAFBFA")):
            self.tree.tag_configure(tag, background=color)
        self.tree.tag_configure("grey", foreground="#9AA3A0")
        if on_select:
            self.tree.bind("<<TreeviewSelect>>", lambda e: on_select(self.selected()))

    def load(self, rows):
        self.tree.delete(*self.tree.get_children())
        self._rows = {}
        for i, row in enumerate(rows):
            values = []
            for c in self.columns:
                v = row.get(c[0])
                values.append(c[4](v) if len(c) > 4 else fmt(v))
            tag = self.tag_fn(row) if self.tag_fn else None
            iid = self.tree.insert("", "end", values=values, tags=(tag or ("odd" if i % 2 else ""),))
            self._rows[iid] = row
        self.count.configure(text=f"{len(rows)} record(s)" if rows else "No records found.")

    def selected(self):
        sel = self.tree.selection()
        return self._rows.get(sel[0]) if sel else None


class PhotoPanel(ttk.Frame):
    """Shows the photos stored (as BLOBs) for one harvest lot."""

    def __init__(self, parent, size=(260, 210)):
        super().__init__(parent, style="Card.TFrame", padding=10)
        self.size, self.images, self.index, self._tk = size, [], 0, None
        ttk.Label(self, text="▣ Product photo", style="Section.TLabel", background="white").pack(anchor="w")
        self.canvas = tk.Label(self, bg="#F7F7F7", width=size[0], height=size[1], relief="flat")
        self.canvas.pack(pady=6)
        nav = ttk.Frame(self, style="Card.TFrame")
        nav.configure(relief="flat", borderwidth=0)
        nav.pack(fill="x")
        self.prev_btn = ttk.Button(nav, text="◀", width=3, command=lambda: self._step(-1))
        self.prev_btn.pack(side="left")
        self.caption = ttk.Label(nav, text="", style="Card.TLabel", anchor="center")
        self.caption.pack(side="left", fill="x", expand=True)
        self.next_btn = ttk.Button(nav, text="▶", width=3, command=lambda: self._step(1))
        self.next_btn.pack(side="right")
        self.clear()

    def clear(self, message="Select a lot to see its photo"):
        self.images, self._tk = [], None
        self.canvas.configure(image="", text=message, fg=GREY, width=34, height=11)
        self.caption.configure(text="")
        self._nav_state()

    def show_lot(self, lot_id):
        if not lot_id:
            return self.clear()
        try:
            self.images = db.lot_images(lot_id)
        except Exception as e:
            return self.clear("⚠ " + db.friendly_error(e))
        self.index = 0
        if not self.images:
            return self.clear("No photo for this lot yet")
        self._render()

    def _render(self):
        rec = self.images[self.index]
        try:
            img = Image.open(io.BytesIO(rec["image_data"]))
            img.load()
            img = img.convert("RGB")
            img.thumbnail(self.size)
            canvas = Image.new("RGB", self.size, "white")
            canvas.paste(img, ((self.size[0] - img.width) // 2, (self.size[1] - img.height) // 2))
            self._tk = ImageTk.PhotoImage(canvas)
            self.canvas.configure(image=self._tk, text="", width=self.size[0], height=self.size[1])
        except Exception:
            self._tk = None
            self.canvas.configure(image="", text="⚠ Image unavailable", fg=RED, width=34, height=11)
        self.caption.configure(text=f"{self.index + 1} / {len(self.images)}   {rec['file_name']}")
        self._nav_state()

    def _step(self, d):
        if self.images:
            self.index = (self.index + d) % len(self.images)
            self._render()

    def _nav_state(self):
        state = "normal" if len(self.images) > 1 else "disabled"
        self.prev_btn.configure(state=state)
        self.next_btn.configure(state=state)


class FormDialog(tk.Toplevel):
    """Simple modal form. fields: dicts with key, label, kind (entry/date/combo/file/info), options, default."""

    def __init__(self, app, title, fields, on_submit, submit_text="Save", icon="✎"):
        super().__init__(app)
        self.app, self.on_submit, self.widgets = app, on_submit, {}
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(app)
        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(card, text=f"{icon}  {title}", style="Title.TLabel", background="white").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))
        r = 1
        for f in fields:
            kind = f.get("kind", "entry")
            ttk.Label(card, text=f["label"], style="Card.TLabel").grid(row=r, column=0, sticky="w", padx=(0, 12), pady=6)
            if kind == "combo":
                w = LookupCombo(card, f.get("options", []), width=34)
                if f.get("default") is not None:
                    w.set_value(f["default"])
            elif kind == "info":
                w = ttk.Label(card, text=f.get("default", ""), style="Card.TLabel", font=("", 10, "bold"))
            else:
                w = ttk.Entry(card, width=36)
                if f.get("default") not in (None, ""):
                    w.insert(0, str(f["default"]))
            w.grid(row=r, column=1, sticky="we", pady=6)
            if kind == "date":
                ttk.Label(card, text="YYYY-MM-DD", style="Muted.TLabel", background="white").grid(row=r, column=2, padx=6)
            if kind == "file":
                ttk.Button(card, text="⬆ Browse…", command=lambda e=w: self._browse(e)).grid(row=r, column=2, padx=6)
            self.widgets[f["key"]] = (kind, w)
            r += 1
        self.error = ttk.Label(card, text="", style="Error.TLabel", wraplength=420)
        self.error.grid(row=r, column=0, columnspan=3, sticky="w", pady=(10, 0))
        btns = ttk.Frame(card, style="Card.TFrame")
        btns.configure(borderwidth=0)
        btns.grid(row=r + 1, column=0, columnspan=3, sticky="e", pady=(14, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(btns, text=submit_text, style="Primary.TButton", command=self._submit).pack(side="left")
        self.bind("<Return>", lambda e: self._submit())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        x = app.winfo_rootx() + (app.winfo_width() - self.winfo_width()) // 2
        y = app.winfo_rooty() + (app.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        try:
            self.grab_set()
        except tk.TclError:
            self.after(100, lambda: self.winfo_exists() and self.grab_set())
        first = next((w for k, w in self.widgets.values() if k in ("entry", "date", "file")), None)
        if first:
            first.focus_set()

    def _browse(self, entry):
        path = filedialog.askopenfilename(parent=self, title="Choose a product photo",
                                          filetypes=[("Images", "*.jpg *.jpeg *.png"), ("All files", "*.*")])
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def _submit(self):
        values = {}
        for key, (kind, w) in self.widgets.items():
            if kind == "combo":
                values[key] = w.value()
            elif kind != "info":
                values[key] = w.get().strip()
        try:
            msg = self.on_submit(values)
        except Exception as e:
            self.error.configure(text="⚠ " + db.friendly_error(e))
            return
        self.destroy()
        self.app.toast(msg or "✔ Saved.")


# ----------------------------------------------------------------------
# Base tab
# ----------------------------------------------------------------------
class Tab(ttk.Frame):
    icon, title = "", ""

    def __init__(self, main):
        super().__init__(main.nb, padding=14)
        self.main, self.app, self.user = main, main.app, main.user
        self.build()

    def header(self, actions=()):
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 10))
        ttk.Label(bar, text=f"{self.icon}  {self.title}", style="Title.TLabel").pack(side="left")
        for text, cmd, style in reversed(actions):
            ttk.Button(bar, text=text, command=cmd, style=style or "TButton").pack(side="right", padx=(6, 0))
        return bar

    def need(self, row, what="a row in the table"):
        if not row:
            messagebox.showinfo("Select first", f"Please select {what} first.", parent=self.app)
            return False
        return True

    def build(self):
        pass

    def refresh(self):
        pass


def options(rows, label_key, id_key):
    return [(r[label_key], r[id_key]) for r in rows]


def lot_tag(row):
    if row.get("available", 0) <= 0:
        return "grey"
    sb = row.get("sell_by_date")
    if sb and sb < dt.date.today():
        return "red"
    if sb and (sb - dt.date.today()).days <= 3:
        return "amber"
    return None


LOT_COLUMNS = [
    ("lot_id", "Lot #", 60, "center"), ("farm_name", "Farm", 160, "w"), ("crop_name", "Crop", 100, "w"),
    ("on_hand", "On hand", 80, "e"), ("reserved", "Reserved", 80, "e"), ("available", "Available", 85, "e"),
    ("unit_code", "Unit", 55, "center"), ("harvest_date", "Harvested", 95, "center"),
    ("sell_by_date", "Sell by", 95, "center"), ("photos", "Photos", 60, "center"),
]


# ----------------------------------------------------------------------
# Farmer tabs
# ----------------------------------------------------------------------
class FarmsTab(Tab):
    icon, title = "⌂", "My Farms"

    def build(self):
        self.header([("✚ Add farm", self.add, "Primary.TButton")])
        self.table = Table(self, [("farm_name", "Farm", 220, "w"), ("emirate_name", "Emirate", 140, "w"),
                                  ("area", "Area", 140, "w"), ("farmers", "Assigned farmers", 260, "w")], height=12)
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        self.table.load(db.list_farms(farm_ids=db.my_farm_ids(self.user["user_id"])))

    def add(self):
        def save(v):
            db.add_farm(self.user, v["name"], v["emirate"], v["area"])
            self.refresh()
            return "✔ Farm added and assigned to you."
        FormDialog(self.app, "Add farm", [
            {"key": "name", "label": "Farm name"},
            {"key": "emirate", "label": "Emirate", "kind": "combo",
             "options": options(db.list_emirates(), "emirate_name", "emirate_id")},
            {"key": "area", "label": "Area / city"},
        ], save, "✚ Add farm", "⌂")


class CyclesTab(Tab):
    icon, title = "☘", "Crop Cycles"

    def build(self):
        self.header([("✚ New crop cycle", self.add, "Primary.TButton"), ("✔ Mark completed", self.complete, None)])
        self.table = Table(self, [
            ("cycle_id", "Cycle #", 70, "center"), ("farm_name", "Farm", 170, "w"), ("crop_name", "Crop", 110, "w"),
            ("planting_date", "Planted", 100, "center"), ("expected_harvest_date", "Expected harvest", 130, "center"),
            ("expected_quantity", "Expected qty (forecast)", 160, "e"), ("harvested", "Harvested so far", 130, "e"),
            ("unit_code", "Unit", 60, "center"), ("status", "Status", 130, "w", lambda s: STATUS_LABEL.get(s, s)),
        ], height=14, tag_fn=lambda r: "grey" if r["status"] == "COMPLETED" else None)
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        self.table.load(db.list_cycles(db.my_farm_ids(self.user["user_id"])))

    def add(self):
        farms = db.list_farms(farm_ids=db.my_farm_ids(self.user["user_id"]))
        if not farms:
            return messagebox.showinfo("No farm", "Add a farm first.", parent=self.app)

        def save(v):
            db.add_cycle(self.user, v["farm"], v["crop"], v["planting"], v["expected_date"], v["qty"], v["unit"])
            self.refresh()
            return "✔ Crop cycle created."
        FormDialog(self.app, "New crop cycle", [
            {"key": "farm", "label": "Farm", "kind": "combo", "options": options(farms, "farm_name", "farm_id")},
            {"key": "crop", "label": "Crop", "kind": "combo", "options": options(db.list_crops(), "crop_name", "crop_id")},
            {"key": "planting", "label": "Planting date", "kind": "date", "default": today()},
            {"key": "expected_date", "label": "Expected harvest date", "kind": "date"},
            {"key": "qty", "label": "Expected quantity"},
            {"key": "unit", "label": "Unit", "kind": "combo", "options": options(db.list_units(), "unit_code", "unit_id")},
        ], save, "✚ Create", "☘")

    def complete(self):
        row = self.table.selected()
        if self.need(row, "a crop cycle") and messagebox.askyesno(
                "Mark completed", f"Mark cycle #{row['cycle_id']} ({row['crop_name']}) as completed?", parent=self.app):
            self.app.run(db.complete_cycle, self.user, row["cycle_id"], ok="✔ Crop cycle completed.")
            self.refresh()


class HarvestTab(Tab):
    icon, title = "▣", "Harvest & Stock"

    def build(self):
        self.header([("✚ Record harvest", self.record, "Primary.TButton"), ("⬆ Upload photo", self.upload, None),
                     ("⚠ Loss / correction", self.adjust, None), ("☰ Movement history", self.history, None)])
        ttk.Label(self, text="Stock summary per crop  (expected = forecast, not stock)", style="Section.TLabel").pack(anchor="w")
        self.summary = Table(self, [
            ("crop_name", "Crop", 140, "w"), ("unit_code", "Unit", 60, "center"),
            ("expected", "⏱ Expected (forecast)", 170, "e"), ("on_hand", "▣ On hand", 120, "e"),
            ("reserved", "● Reserved", 120, "e"), ("available", "✔ Available", 120, "e")], height=4)
        self.summary.pack(fill="x", pady=(4, 12))
        ttk.Label(self, text="Harvest lots", style="Section.TLabel").pack(anchor="w")
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(4, 0))
        self.table = Table(body, LOT_COLUMNS, height=9, tag_fn=lot_tag,
                           on_select=lambda r: self.photo.show_lot(r and r["lot_id"]))
        self.table.pack(side="left", fill="both", expand=True)
        self.photo = PhotoPanel(body)
        self.photo.pack(side="right", fill="y", padx=(12, 0))

    def refresh(self):
        ids = db.my_farm_ids(self.user["user_id"])
        self.summary.load(db.stock_summary(ids))
        self.table.load(db.list_lots(ids))
        self.photo.clear()

    def record(self):
        cycles = [c for c in db.list_cycles(db.my_farm_ids(self.user["user_id"])) if c["status"] != "COMPLETED"]
        if not cycles:
            return messagebox.showinfo("No crop cycle", "Create a crop cycle first.", parent=self.app)
        opts = [(f"#{c['cycle_id']}  {c['farm_name']} – {c['crop_name']} ({c['unit_code']})", c["cycle_id"]) for c in cycles]

        def save(v):
            lot = db.record_harvest(self.user, v["cycle"], v["qty"], v["date"], v["sell_by"], v["photo"] or None)
            self.refresh()
            return f"✔ Harvest lot #{lot} recorded."
        FormDialog(self.app, "Record harvest", [
            {"key": "cycle", "label": "Crop cycle", "kind": "combo", "options": opts},
            {"key": "qty", "label": "Harvested quantity"},
            {"key": "date", "label": "Harvest date", "kind": "date", "default": today()},
            {"key": "sell_by", "label": "Sell-by date (optional)", "kind": "date",
             "default": (dt.date.today() + dt.timedelta(days=7)).isoformat()},
            {"key": "photo", "label": "Photo (JPG/PNG, optional)", "kind": "file"},
        ], save, "✚ Record harvest", "▣")

    def upload(self):
        row = self.table.selected()
        if not self.need(row, "a harvest lot"):
            return
        path = filedialog.askopenfilename(parent=self.app, title="Choose a product photo",
                                          filetypes=[("Images", "*.jpg *.jpeg *.png"), ("All files", "*.*")])
        if path and self.app.run(db.add_lot_image, self.user, row["lot_id"], path,
                                 ok=f"✔ Photo saved for lot #{row['lot_id']}.") is not False:
            lot_id = row["lot_id"]
            self.refresh()
            self.photo.show_lot(lot_id)

    def adjust(self):
        row = self.table.selected()
        if not self.need(row, "a harvest lot"):
            return

        def save(v):
            db.record_adjustment(self.user, row["lot_id"], v["kind"], v["qty"], v["reason"])
            self.refresh()
            return f"✔ Stock movement recorded for lot #{row['lot_id']}."
        FormDialog(self.app, f"Loss / correction – lot #{row['lot_id']}", [
            {"key": "info", "label": "Available now", "kind": "info",
             "default": f"{fmt(row['available'])} {row['unit_code']}"},
            {"key": "kind", "label": "Type", "kind": "combo",
             "options": [("✖ Loss (spoiled, damaged…)", "LOSS"), ("✎ Approved correction (+ / −)", "CORRECTION")]},
            {"key": "qty", "label": "Quantity"},
            {"key": "reason", "label": "Reason"},
        ], save, "✔ Record", "⚠")

    def history(self):
        row = self.table.selected()
        if self.need(row, "a harvest lot"):
            show_list(self.app, f"Movement history – lot #{row['lot_id']} ({row['crop_name']})", [
                ("movement_date", "Date", 140, "center"),
                ("movement_type", "Movement", 150, "w", lambda s: MOVEMENT_LABEL.get(s, s)),
                ("quantity", "Qty", 70, "e"), ("unit_code", "Unit", 55, "center"),
                ("full_name", "By", 130, "w"), ("reason", "Reason", 280, "w")], db.lot_movements(row["lot_id"]))


def show_list(app, title, columns, rows):
    win = tk.Toplevel(app)
    win.title(title)
    win.configure(bg=BG)
    win.transient(app)
    frame = ttk.Frame(win, padding=14)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="☰  " + title, style="Title.TLabel").pack(anchor="w", pady=(0, 8))
    t = Table(frame, columns, height=12)
    t.pack(fill="both", expand=True)
    t.load(rows)
    ttk.Button(frame, text="Close", command=win.destroy).pack(anchor="e", pady=(10, 0))
    win.bind("<Escape>", lambda e: win.destroy())


class AllocateTab(Tab):
    icon, title = "⇄", "Allocate to Markets"

    def build(self):
        self.header([("⟳ Refresh", self.refresh, None)])
        top = ttk.Frame(self)
        top.pack(fill="both", expand=True)
        left = ttk.Frame(top)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="① Open market requests", style="Section.TLabel").pack(anchor="w")
        self.requests = Table(left, [
            ("request_id", "Req #", 55, "center"), ("market_name", "Market", 150, "w"),
            ("crop_name", "Crop", 90, "w"), ("requested_quantity", "Requested", 92, "e"),
            ("allocated_quantity", "Allocated", 90, "e"), ("unit_code", "Unit", 50, "center"),
            ("needed_by_date", "Needed by", 95, "center")], height=7, on_select=self.on_request)
        self.requests.pack(fill="both", expand=True, pady=(4, 0))
        right = ttk.Frame(top)
        right.pack(side="left", fill="both", expand=True, padx=(14, 0))
        ttk.Label(right, text="② Your matching lots (same crop & unit)", style="Section.TLabel").pack(anchor="w")
        self.lots = Table(right, [
            ("lot_id", "Lot #", 55, "center"), ("farm_name", "Farm", 150, "w"),
            ("available", "Available", 80, "e"), ("unit_code", "Unit", 50, "center"),
            ("harvest_date", "Harvested", 95, "center"), ("sell_by_date", "Sell by", 95, "center")],
            height=7, tag_fn=lot_tag)
        self.lots.pack(fill="both", expand=True, pady=(4, 0))
        act = ttk.Frame(right)
        act.pack(fill="x", pady=8)
        ttk.Label(act, text="③ Quantity:").pack(side="left")
        self.qty = ttk.Entry(act, width=12)
        self.qty.pack(side="left", padx=6)
        ttk.Button(act, text="⇄ Allocate", style="Primary.TButton", command=self.allocate).pack(side="left")
        ttk.Label(self, text="Your allocations", style="Section.TLabel").pack(anchor="w", pady=(10, 0))
        bottom = ttk.Frame(self)
        bottom.pack(fill="both", expand=True, pady=(4, 0))
        self.allocs = Table(bottom, [
            ("allocation_id", "Alloc #", 65, "center"), ("request_id", "Req #", 55, "center"),
            ("market_name", "Market", 170, "w"), ("lot_id", "Lot #", 55, "center"), ("crop_name", "Crop", 100, "w"),
            ("allocated_quantity", "Qty", 70, "e"), ("unit_code", "Unit", 50, "center"),
            ("status", "Status", 120, "w", lambda s: STATUS_LABEL.get(s, s)),
            ("received_quantity", "Received", 80, "e")], height=6,
            tag_fn=lambda r: "grey" if r["status"] == "RELEASED" else None)
        self.allocs.pack(side="left", fill="both", expand=True)
        ttk.Button(bottom, text="↺ Release", style="Danger.TButton", command=self.release).pack(side="left", padx=10, anchor="n")

    def refresh(self):
        self.requests.load(db.list_requests(open_only=True))
        self.lots.load([])
        self.allocs.load(db.list_allocations(farm_ids=db.my_farm_ids(self.user["user_id"])))

    def on_request(self, req):
        self.lots.load(db.allocatable_lots(self.user, req["request_id"]) if req else [])
        if req:
            remaining = req["requested_quantity"] - req["allocated_quantity"]
            self.qty.delete(0, "end")
            self.qty.insert(0, fmt(remaining).replace(",", ""))

    def allocate(self):
        req, lot = self.requests.selected(), self.lots.selected()
        if not self.need(req, "a market request (①)") or not self.need(lot, "one of your lots (②)"):
            return
        if self.app.run(db.allocate, self.user, req["request_id"], lot["lot_id"], self.qty.get(),
                        ok=f"✔ Allocated from lot #{lot['lot_id']} to request #{req['request_id']}.") is not False:
            self.refresh()

    def release(self):
        row = self.allocs.selected()
        if not self.need(row, "an allocation"):
            return

        def save(v):
            db.release_allocation(self.user, row["allocation_id"], v["reason"])
            self.refresh()
            return "✔ Reservation released. The stock is available again."
        FormDialog(self.app, f"Release allocation #{row['allocation_id']}", [
            {"key": "reason", "label": "Reason"}], save, "↺ Release", "↺")


class LossTab(Tab):
    icon, title = "⚠", "Loss & Surplus"

    def build(self):
        actions = [("♥ Donate", lambda: self.act("DONATED"), "Primary.TButton"),
                   ("✖ Dispose", lambda: self.act("DISPOSED"), "Danger.TButton")]
        self.header(actions if self.user["role"] == "farmer" else [])
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Label(bar, text="⏱ Near expiry within").pack(side="left")
        self.near = ttk.Spinbox(bar, from_=0, to=60, width=5)
        self.near.set(3)
        self.near.pack(side="left", padx=4)
        ttk.Label(bar, text="days      ▣ Unallocated for at least").pack(side="left")
        self.surplus = ttk.Spinbox(bar, from_=0, to=365, width=5)
        self.surplus.set(7)
        self.surplus.pack(side="left", padx=4)
        ttk.Label(bar, text="days").pack(side="left")
        ttk.Button(bar, text="⟳ Apply", command=self.refresh).pack(side="left", padx=10)
        legend = ttk.Frame(bar)
        legend.pack(side="right")
        for text, color in (("Expired", "#FDECEA"), ("Near expiry", "#FFF3E0"), ("Surplus", "#E3F2FD")):
            tk.Label(legend, text=f"  {text}  ", bg=color, fg=TEXT).pack(side="left", padx=3)
        self.table = Table(self, [
            ("priority", "Priority", 70, "center"), ("flag", "Flag", 130, "w", lambda f: FLAG_LABEL.get(f, f)),
            ("lot_id", "Lot #", 55, "center"), ("farm_name", "Farm", 160, "w"), ("crop_name", "Crop", 100, "w"),
            ("available", "Available", 85, "e"), ("unit_code", "Unit", 50, "center"),
            ("sell_by_date", "Sell by", 95, "center"), ("days_left", "Days left", 75, "center"),
            ("age_days", "Age (days)", 80, "center")], height=9,
            tag_fn=lambda r: {"EXPIRED": "red", "NEAR EXPIRY": "amber"}.get(r["flag"], "blue"))
        self.table.pack(fill="both", expand=True)
        ttk.Label(self, text="Donation & disposal history", style="Section.TLabel").pack(anchor="w", pady=(10, 4))
        self.hist = Table(self, [
            ("movement_date", "Date", 140, "center"),
            ("movement_type", "Action", 110, "w", lambda s: MOVEMENT_LABEL.get(s, s)),
            ("lot_id", "Lot #", 55, "center"), ("crop_name", "Crop", 100, "w"), ("farm_name", "Farm", 150, "w"),
            ("quantity", "Qty", 70, "e"), ("unit_code", "Unit", 50, "center"),
            ("full_name", "By", 120, "w"), ("reason", "Details", 220, "w")], height=5)
        self.hist.pack(fill="both", expand=True)

    def _ids(self):
        return db.my_farm_ids(self.user["user_id"]) if self.user["role"] == "farmer" else None

    def refresh(self):
        try:
            self.table.load(db.flagged_lots(self.near.get(), self.surplus.get(), self._ids()))
        except Exception as e:
            messagebox.showerror("Invalid threshold", db.friendly_error(e), parent=self.app)
        self.hist.load(db.disposition_history(self._ids()))

    def act(self, action):
        row = self.table.selected()
        if not self.need(row, "a flagged lot"):
            return
        donate = action == "DONATED"

        def save(v):
            db.dispose_lot(self.user, row["lot_id"], action, v["qty"], v["note"])
            self.refresh()
            return f"✔ {fmt(Decimal(v['qty']))} {row['unit_code']} {'donated' if donate else 'disposed'} from lot #{row['lot_id']}."
        FormDialog(self.app, f"{'Donate' if donate else 'Dispose'} – lot #{row['lot_id']} ({row['crop_name']})", [
            {"key": "info", "label": "Available", "kind": "info", "default": f"{fmt(row['available'])} {row['unit_code']}"},
            {"key": "qty", "label": "Quantity", "default": fmt(row["available"]).replace(",", "")},
            {"key": "note", "label": "Recipient" if donate else "Reason",
             "default": "UAE Food Bank" if donate else ""},
        ], save, "♥ Donate" if donate else "✖ Dispose", "♥" if donate else "✖")


# ----------------------------------------------------------------------
# Market buyer tabs
# ----------------------------------------------------------------------
class FindProduceTab(Tab):
    icon, title = "⌕", "Find Produce"

    def build(self):
        self.header([("✎ Request this crop", self.request, "Primary.TButton")])
        f = ttk.Frame(self)
        f.pack(fill="x", pady=(0, 10))
        ttk.Label(f, text="Crop").grid(row=0, column=0, sticky="w")
        self.crop = LookupCombo(f, options(db.list_crops(), "crop_name", "crop_id"), "All crops", 16)
        self.crop.grid(row=1, column=0, padx=(0, 10))
        ttk.Label(f, text="Emirate").grid(row=0, column=1, sticky="w")
        self.emirate = LookupCombo(f, [(e["emirate_name"], e["emirate_name"]) for e in db.list_emirates()],
                                   "All emirates", 16)
        self.emirate.grid(row=1, column=1, padx=(0, 10))
        ttk.Label(f, text="Min. quantity").grid(row=0, column=2, sticky="w")
        self.minq = ttk.Entry(f, width=10)
        self.minq.grid(row=1, column=2, padx=(0, 10))
        ttk.Label(f, text="Available on (YYYY-MM-DD)").grid(row=0, column=3, sticky="w")
        self.on = ttk.Entry(f, width=14)
        self.on.grid(row=1, column=3, padx=(0, 10))
        ttk.Button(f, text="⌕ Search", style="Primary.TButton", command=self.refresh).grid(row=1, column=4)
        ttk.Button(f, text="Clear", command=self.clear).grid(row=1, column=5, padx=6)
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        cols = [c for c in LOT_COLUMNS if c[0] not in ("on_hand", "reserved")]
        cols.insert(2, ("emirate_name", "Emirate", 100, "w"))
        self.table = Table(body, cols, height=14, tag_fn=lot_tag,
                           on_select=lambda r: self.photo.show_lot(r and r["lot_id"]))
        self.table.pack(side="left", fill="both", expand=True)
        self.photo = PhotoPanel(body)
        self.photo.pack(side="right", fill="y", padx=(12, 0))

    def clear(self):
        self.crop.current(0)
        self.emirate.current(0)
        self.minq.delete(0, "end")
        self.on.delete(0, "end")
        self.refresh()

    def refresh(self):
        try:
            rows = db.search_lots(crop_id=self.crop.value(), emirate=self.emirate.value(),
                                  min_available=self.minq.get().strip() or None, sellable_on=self.on.get(),
                                  availability="Available")
        except Exception as e:
            return messagebox.showerror("Search", db.friendly_error(e), parent=self.app)
        self.table.load(rows)
        self.photo.clear()

    def request(self):
        row = self.table.selected()
        self.main.tabs["requests"].new_request(row["crop_id"] if row else None, row["unit_id"] if row else None)


class MyRequestsTab(Tab):
    icon, title = "✎", "My Requests"

    def build(self):
        self.header([("✚ New request", lambda: self.new_request(), "Primary.TButton"), ("✎ Edit", self.edit, None),
                     ("☰ Status history", self.history, None), ("✖ Cancel request", self.cancel, "Danger.TButton")])
        ttk.Label(self, text="Delivered means all allocations are settled. Check Received and Difference for shortfalls.",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 6))
        self.table = Table(self, [
            ("request_id", "Req #", 60, "center"), ("crop_name", "Crop", 110, "w"),
            ("requested_quantity", "Requested", 90, "e"), ("allocated_quantity", "Allocated", 90, "e"),
            ("received_quantity", "Received", 90, "e"), ("unit_code", "Unit", 55, "center"),
            ("needed_by_date", "Needed by", 100, "center"),
            ("status", "Status", 150, "w", lambda s: STATUS_LABEL.get(s, s))], height=10,
            on_select=self.on_select,
            tag_fn=lambda r: {"DELIVERED": "green", "CANCELLED": "grey"}.get(r["status"]))
        self.table.pack(fill="both", expand=True)
        ttk.Label(self, text="Allocations for the selected request", style="Section.TLabel").pack(anchor="w", pady=(10, 4))
        self.allocs = Table(self, [
            ("allocation_id", "Alloc #", 65, "center"), ("farm_name", "Farm", 170, "w"), ("lot_id", "Lot #", 55, "center"),
            ("allocated_quantity", "Allocated", 85, "e"), ("received_quantity", "Received", 85, "e"),
            ("discrepancy_quantity", "Difference", 85, "e"), ("unit_code", "Unit", 55, "center"),
            ("status", "Status", 120, "w", lambda s: STATUS_LABEL.get(s, s))], height=5)
        self.allocs.pack(fill="both", expand=True)

    def refresh(self):
        self.table.load(db.list_requests(market_id=self.user["market_id"]))
        self.allocs.load([])

    def on_select(self, row):
        self.allocs.load(db.list_allocations(request_id=row["request_id"]) if row else [])

    def new_request(self, crop_id=None, unit_id=None):
        def save(v):
            rid = db.create_request(self.user, v["crop"], v["qty"], v["unit"], v["needed"], v["notes"])
            self.refresh()
            return f"✔ Request #{rid} created."
        FormDialog(self.app, "New market request", [
            {"key": "crop", "label": "Crop", "kind": "combo", "default": crop_id,
             "options": options(db.list_crops(), "crop_name", "crop_id")},
            {"key": "qty", "label": "Quantity"},
            {"key": "unit", "label": "Unit", "kind": "combo", "default": unit_id,
             "options": options(db.list_units(), "unit_code", "unit_id")},
            {"key": "needed", "label": "Needed by", "kind": "date",
             "default": (dt.date.today() + dt.timedelta(days=3)).isoformat()},
            {"key": "notes", "label": "Notes (optional)"},
        ], save, "✚ Create request", "✎")

    def edit(self):
        row = self.table.selected()
        if not self.need(row, "a request"):
            return

        def save(v):
            db.update_request(self.user, row["request_id"], v["qty"], v["needed"], v["notes"])
            self.refresh()
            return f"✔ Request #{row['request_id']} updated."
        notes = db.query_one("SELECT notes FROM market_requests WHERE request_id=%s", (row["request_id"],))["notes"]
        FormDialog(self.app, f"Edit request #{row['request_id']}", [
            {"key": "info", "label": "Crop", "kind": "info", "default": f"{row['crop_name']} ({row['unit_code']})"},
            {"key": "qty", "label": "Quantity", "default": fmt(row["requested_quantity"]).replace(",", "")},
            {"key": "needed", "label": "Needed by", "kind": "date", "default": fmt(row["needed_by_date"])},
            {"key": "notes", "label": "Notes", "default": notes or ""},
        ], save, "✔ Save changes", "✎")

    def cancel(self):
        row = self.table.selected()
        if not self.need(row, "a request"):
            return

        def save(v):
            db.cancel_request(self.user, row["request_id"], v["reason"])
            self.refresh()
            return f"✔ Request #{row['request_id']} cancelled. Reserved stock was released."
        FormDialog(self.app, f"Cancel request #{row['request_id']}", [
            {"key": "reason", "label": "Reason"}], save, "✖ Cancel request", "✖")

    def history(self):
        row = self.table.selected()
        if self.need(row, "a request"):
            show_list(self.app, f"Status history – request #{row['request_id']}", [
                ("changed_at", "Date", 140, "center"),
                ("old_status", "From", 150, "w", lambda s: STATUS_LABEL.get(s, "—") if s else "—"),
                ("new_status", "To", 150, "w", lambda s: STATUS_LABEL.get(s, s)),
                ("full_name", "By", 130, "w"), ("reason", "Reason", 260, "w")], db.request_history(row["request_id"]))


class DeliveriesTab(Tab):
    icon, title = "✔", "Deliveries"

    def build(self):
        self.header([("⟳ Refresh", self.refresh, None)])
        ttk.Label(self, text="① Pending deliveries", style="Section.TLabel").pack(anchor="w")
        self.pending = Table(self, [
            ("allocation_id", "Alloc #", 65, "center"), ("request_id", "Req #", 55, "center"),
            ("crop_name", "Crop", 110, "w"), ("farm_name", "From farm", 180, "w"), ("lot_id", "Lot #", 55, "center"),
            ("allocated_quantity", "Allocated", 90, "e"), ("unit_code", "Unit", 55, "center"),
            ("allocated_at", "Allocated on", 140, "center")], height=6, on_select=self.on_select)
        self.pending.pack(fill="both", expand=True, pady=(4, 0))
        form = ttk.Frame(self)
        form.pack(fill="x", pady=10)
        ttk.Label(form, text="② Received quantity:").pack(side="left")
        self.received = ttk.Entry(form, width=10)
        self.received.pack(side="left", padx=6)
        ttk.Label(form, text="Reason if different:").pack(side="left", padx=(10, 0))
        self.reason = ttk.Entry(form, width=40)
        self.reason.pack(side="left", padx=6)
        ttk.Button(form, text="✔ Confirm delivery", style="Primary.TButton", command=self.confirm).pack(side="left", padx=6)
        ttk.Label(self, text="Delivery receipts", style="Section.TLabel").pack(anchor="w", pady=(6, 4))
        self.receipts = Table(self, [
            ("receipt_id", "Receipt #", 75, "center"), ("request_id", "Req #", 55, "center"),
            ("crop_name", "Crop", 100, "w"), ("farm_name", "From farm", 160, "w"),
            ("allocated_quantity", "Allocated", 85, "e"), ("received_quantity", "Received", 85, "e"),
            ("discrepancy_quantity", "Difference", 85, "e"), ("unit_code", "Unit", 55, "center"),
            ("discrepancy_reason", "Reason", 200, "w"), ("received_date", "Date", 95, "center")], height=6,
            tag_fn=lambda r: "amber" if r["discrepancy_quantity"] > 0 else None)
        self.receipts.pack(fill="both", expand=True)

    def refresh(self):
        self.pending.load(db.list_allocations(market_id=self.user["market_id"], status="RESERVED"))
        self.receipts.load(db.list_receipts(self.user["market_id"]))
        self.received.delete(0, "end")
        self.reason.delete(0, "end")

    def on_select(self, row):
        self.received.delete(0, "end")
        if row:
            self.received.insert(0, fmt(row["allocated_quantity"]).replace(",", ""))

    def confirm(self):
        row = self.pending.selected()
        if not self.need(row, "a pending delivery (①)"):
            return
        if self.app.run(db.confirm_delivery, self.user, row["allocation_id"], self.received.get(), self.reason.get(),
                        ok="✔ Delivery confirmed and receipt saved.") is not False:
            self.refresh()


# ----------------------------------------------------------------------
# Shared tabs
# ----------------------------------------------------------------------
class SearchTab(Tab):
    icon, title = "⌕", "Search & Status"

    def build(self):
        self.header()
        f = ttk.Frame(self)
        f.pack(fill="x", pady=(0, 10))
        self.kind = tk.StringVar(value="lots")
        kinds = ttk.Frame(f)
        kinds.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 6))
        ttk.Radiobutton(kinds, text="▣ Stock (harvest lots)", variable=self.kind, value="lots",
                        command=self.switch).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(kinds, text="✎ Market requests", variable=self.kind, value="requests",
                        command=self.switch).pack(side="left")
        labels = ["Crop", "Emirate", "Farm", "Market", "Request status", "Availability", "From date", "To date"]
        for i, text in enumerate(labels):
            ttk.Label(f, text=text).grid(row=1, column=i, sticky="w")
        self.crop = LookupCombo(f, options(db.list_crops(False), "crop_name", "crop_id"), "All", 12)
        self.emirate = LookupCombo(f, [(e["emirate_name"], e["emirate_name"]) for e in db.list_emirates()], "All", 13)
        self.farm = LookupCombo(f, options(db.list_farms(False), "farm_name", "farm_id"), "All", 16)
        self.market = LookupCombo(f, options(db.list_markets(False), "market_name", "market_id"), "All", 17)
        self.status = LookupCombo(f, [(STATUS_LABEL[s], s) for s in (
            "OPEN", "PARTIALLY_ALLOCATED", "FULLY_ALLOCATED", "PARTIALLY_DELIVERED", "DELIVERED", "CANCELLED")], "All", 15)
        self.avail = LookupCombo(f, [(a, a) for a in ("Any", "Available", "Fully reserved", "Sold out")], None, 12)
        self.d1, self.d2 = ttk.Entry(f, width=11), ttk.Entry(f, width=11)
        for i, w in enumerate((self.crop, self.emirate, self.farm, self.market, self.status, self.avail, self.d1, self.d2)):
            w.grid(row=2, column=i, padx=(0, 8), sticky="w")
        btns = ttk.Frame(f)
        btns.grid(row=3, column=0, columnspan=8, sticky="w", pady=(8, 0))
        ttk.Button(btns, text="⌕ Search", style="Primary.TButton", command=self.refresh).pack(side="left")
        ttk.Button(btns, text="Clear filters", command=self.clear).pack(side="left", padx=6)
        self.hint = ttk.Label(btns, style="Muted.TLabel")
        self.hint.pack(side="left", padx=10)
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        cols = list(LOT_COLUMNS)
        cols.insert(2, ("emirate_name", "Emirate", 100, "w"))
        self.lot_table = Table(self.body, cols, height=14, tag_fn=lot_tag,
                               on_select=lambda r: self.photo.show_lot(r and r["lot_id"]))
        self.photo = PhotoPanel(self.body)
        self.req_table = Table(self.body, [
            ("request_id", "Req #", 60, "center"), ("market_name", "Market", 180, "w"),
            ("emirate_name", "Emirate", 110, "w"), ("crop_name", "Crop", 100, "w"),
            ("requested_quantity", "Requested", 90, "e"), ("allocated_quantity", "Allocated", 90, "e"),
            ("received_quantity", "Received", 90, "e"), ("unit_code", "Unit", 55, "center"),
            ("needed_by_date", "Needed by", 100, "center"),
            ("status", "Status", 150, "w", lambda s: STATUS_LABEL.get(s, s))], height=14,
            tag_fn=lambda r: {"DELIVERED": "green", "CANCELLED": "grey"}.get(r["status"]))
        self.switch()

    def switch(self):
        lots = self.kind.get() == "lots"
        for w in (self.lot_table, self.photo, self.req_table):
            w.pack_forget()
        if lots:
            self.lot_table.pack(side="left", fill="both", expand=True)
            self.photo.pack(side="right", fill="y", padx=(12, 0))
            self.hint.configure(text="Dates filter the harvest date.  Market and status apply to requests only.")
        else:
            self.req_table.pack(fill="both", expand=True)
            self.hint.configure(text="Dates filter the needed-by date.  Farm and availability apply to stock only.")
        for w in (self.farm, self.avail):
            w.configure(state="readonly" if lots else "disabled")
        for w in (self.market, self.status):
            w.configure(state="disabled" if lots else "readonly")
        self.refresh()

    def clear(self):
        for w in (self.crop, self.emirate, self.farm, self.market, self.status, self.avail):
            w.current(0)
        self.d1.delete(0, "end")
        self.d2.delete(0, "end")
        self.refresh()

    def refresh(self):
        try:
            if self.kind.get() == "lots":
                self.lot_table.load(db.search_lots(self.crop.value(), self.emirate.value(), self.farm.value(),
                                                   None, self.d1.get(), self.d2.get(), self.avail.value()))
                self.photo.clear()
            else:
                self.req_table.load(db.search_requests(self.crop.value(), self.emirate.value(), self.market.value(),
                                                       self.status.value(), self.d1.get(), self.d2.get()))
        except Exception as e:
            messagebox.showerror("Search", db.friendly_error(e), parent=self.app)


class AssistantTab(Tab):
    icon, title = "✦", "Ask AI"
    EXAMPLES = ["Which farms have tomatoes available?",
                "Which requests are partially delivered?",
                "Which deliveries had a shortfall?"]

    def build(self):
        self.header()
        self.ai = Assistant()
        self.results = queue.Queue()
        ask = ttk.Frame(self)
        ask.pack(fill="x")
        self.question = ttk.Entry(ask, font=("", 12))
        self.question.pack(side="left", fill="x", expand=True, ipady=4)
        self.question.bind("<Return>", lambda e: self.ask())
        self.ask_btn = ttk.Button(ask, text="✦ Ask", style="Primary.TButton", command=self.ask)
        self.ask_btn.pack(side="left", padx=(8, 0))
        chips = ttk.Frame(self)
        chips.pack(fill="x", pady=8)
        ttk.Label(chips, text="Try:", style="Muted.TLabel").pack(side="left")
        for q in self.EXAMPLES:
            ttk.Button(chips, text=q, command=lambda q=q: self.use(q)).pack(side="left", padx=3)
        card = ttk.Frame(self, style="Card.TFrame", padding=12)
        card.pack(fill="x", pady=(4, 8))
        self.answer = tk.Label(card, text="", bg="white", fg=TEXT, justify="left", anchor="w",
                               wraplength=1100, font=("", 12))
        self.answer.pack(fill="x")
        self.sql = tk.Label(card, text="", bg="white", fg=GREY, justify="left", anchor="w",
                            wraplength=1100, font=("Courier", 9))
        self.sql.pack(fill="x", pady=(6, 0))
        ttk.Label(self, text="Supporting records", style="Section.TLabel").pack(anchor="w")
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, pady=(4, 0))
        self.table = None
        if not Assistant.has_key():
            self.answer.configure(text="⚠ Add your GEMINI_API_KEY to the .env file to use the assistant.", fg=AMBER)

    def use(self, q):
        self.question.delete(0, "end")
        self.question.insert(0, q)
        self.ask()

    def ask(self):
        q = self.question.get().strip()
        if not q:
            return self.answer.configure(text="Please type a question.", fg=AMBER)
        self.ask_btn.configure(state="disabled", text="⏳ Thinking…")
        self.answer.configure(text="⏳ Thinking…", fg=GREY)
        self.sql.configure(text="")
        # Tk objects must only be cleaned up by the main thread: collect now, pause automatic GC
        # while the worker thread talks to the AI service, and resume it in poll().
        gc.collect()
        gc.disable()
        threading.Thread(target=self._work, args=(q,), daemon=True).start()
        self.app.after(200, self.poll)

    def _work(self, q):
        try:
            res = self.ai.ask(q)
        except Exception:
            res = {"kind": "error", "text": "The assistant could not answer. Please try again."}
        self.results.put(res)

    def poll(self):
        try:
            res = self.results.get_nowait()
        except queue.Empty:
            return self.app.after(200, self.poll)
        gc.enable()
        if not self.winfo_exists():
            return
        self.ask_btn.configure(state="normal", text="✦ Ask")
        colors = {"answer": TEXT, "clarify": BLUE, "not_answerable": AMBER, "error": RED}
        icons = {"answer": "✔ ", "clarify": "? ", "not_answerable": "⚠ ", "error": "⚠ "}
        self.answer.configure(text=icons[res["kind"]] + res["text"], fg=colors[res["kind"]])
        self.sql.configure(text=("SQL (read-only):  " + " ".join(res["sql"].split())) if res.get("sql") else "")
        if self.table:
            self.table.destroy()
            self.table = None
        if res.get("columns"):
            cols = [(c, c.replace("_", " ").title(), 120, "w") for c in res["columns"]]
            self.table = Table(self.table_frame, cols, height=8)
            self.table.pack(fill="both", expand=True)
            self.table.load(res["rows"])


# ----------------------------------------------------------------------
# Administrator tabs (reference data only — no transaction editing)
# ----------------------------------------------------------------------
class UsersTab(Tab):
    icon, title = "☺", "Users"

    def build(self):
        self.header([("✚ Add user", self.add, "Primary.TButton"), ("⌂ Assign farm", self.assign, None),
                     ("◐ Activate / deactivate", self.toggle, None)])
        self.table = Table(self, [
            ("user_id", "ID", 50, "center"), ("full_name", "Name", 160, "w"), ("email", "Email", 240, "w"),
            ("role", "Role", 120, "w", lambda r: ROLE_INFO[r][0] + " " + ROLE_INFO[r][1]),
            ("market_name", "Market", 170, "w"), ("farms", "Farms", 220, "w"),
            ("is_active", "Status", 90, "w", active_fmt)], height=15,
            tag_fn=lambda r: None if r["is_active"] else "grey")
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        self.table.load(db.list_users())

    def add(self):
        def save(v):
            db.add_user(self.user, v["name"], v["email"], v["role"], v["market"])
            self.refresh()
            return "✔ User added."
        FormDialog(self.app, "Add user", [
            {"key": "name", "label": "Full name"}, {"key": "email", "label": "Email"},
            {"key": "role", "label": "Role", "kind": "combo",
             "options": [("☘ Farmer", "farmer"), ("⚖ Market buyer", "market"), ("⚙ Administrator", "admin")]},
            {"key": "market", "label": "Market (buyers only)", "kind": "combo",
             "options": [("— none —", None)] + options(db.list_markets(), "market_name", "market_id")},
        ], save, "✚ Add user", "☺")

    def assign(self):
        row = self.table.selected()
        if not self.need(row, "a farmer"):
            return

        def save(v):
            db.assign_farm(self.user, row["user_id"], v["farm"])
            self.refresh()
            return "✔ Farm assigned."
        FormDialog(self.app, f"Assign farm to {row['full_name']}", [
            {"key": "farm", "label": "Farm", "kind": "combo", "options": options(db.list_farms(), "farm_name", "farm_id")},
        ], save, "⌂ Assign", "⌂")

    def toggle(self):
        row = self.table.selected()
        if self.need(row, "a user"):
            self.app.run(db.set_active, self.user, "users", row["user_id"], not row["is_active"],
                         ok="✔ User status changed.")
            self.refresh()


class ReferenceTab(Tab):
    icon, title = "⚙", "Reference Data"

    def build(self):
        self.header()
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.parts = {}
        specs = {
            "crops": ("☘ Crops", [("crop_id", "ID", 50, "center"), ("crop_name", "Crop", 180, "w"),
                                 ("category", "Category", 130, "w"), ("default_unit", "Default unit", 110, "center"),
                                 ("is_active", "Status", 100, "w", active_fmt)], db.list_crops, self.add_crop),
            "units": ("⚖ Units", [("unit_id", "ID", 50, "center"), ("unit_code", "Code", 100, "w"),
                                 ("unit_name", "Name", 200, "w"), ("is_active", "Status", 100, "w", active_fmt)],
                      db.list_units, self.add_unit),
            "markets": ("⌂ Markets", [("market_id", "ID", 50, "center"), ("market_name", "Market", 220, "w"),
                                     ("emirate_name", "Emirate", 140, "w"), ("area", "Area", 140, "w"),
                                     ("is_active", "Status", 100, "w", active_fmt)], db.list_markets, self.add_market),
            "farms": ("☘ Farms", [("farm_id", "ID", 50, "center"), ("farm_name", "Farm", 220, "w"),
                                 ("emirate_name", "Emirate", 140, "w"), ("area", "Area", 140, "w"),
                                 ("farmers", "Farmers", 200, "w"), ("is_active", "Status", 100, "w", active_fmt)],
                      db.list_farms, None),
        }
        for key, (label, cols, loader, adder) in specs.items():
            frame = ttk.Frame(nb, padding=10)
            nb.add(frame, text=label)
            bar = ttk.Frame(frame)
            bar.pack(fill="x", pady=(0, 8))
            if adder:
                ttk.Button(bar, text="✚ Add", style="Primary.TButton", command=adder).pack(side="left")
            ttk.Button(bar, text="◐ Activate / deactivate",
                       command=lambda k=key: self.toggle(k)).pack(side="left", padx=6)
            t = Table(frame, cols, height=12, tag_fn=lambda r: None if r["is_active"] else "grey")
            t.pack(fill="both", expand=True)
            self.parts[key] = (t, loader)

    def refresh(self):
        for t, loader in self.parts.values():
            t.load(loader(False) if loader is not db.list_farms else loader(active_only=False))

    def toggle(self, key):
        t = self.parts[key][0]
        row = t.selected()
        if self.need(row, "a record"):
            rid = row[db.ACTIVE_TABLES[key]]
            self.app.run(db.set_active, self.user, key, rid, not row["is_active"], ok="✔ Status changed.")
            self.refresh()

    def _form(self, title, fields, fn):
        def save(v):
            fn(v)
            self.refresh()
            return f"✔ {title.split(' ', 1)[1]} added."
        FormDialog(self.app, title, fields, save, "✚ Add", "⚙")

    def add_crop(self):
        self._form("Add crop", [{"key": "name", "label": "Crop name"}, {"key": "cat", "label": "Category", "default": "Vegetable"},
                                {"key": "unit", "label": "Default unit", "kind": "combo",
                                 "options": options(db.list_units(), "unit_code", "unit_id")}],
                   lambda v: db.add_crop(self.user, v["name"], v["cat"], v["unit"]))

    def add_unit(self):
        self._form("Add unit", [{"key": "code", "label": "Code (e.g. kg)"}, {"key": "name", "label": "Name"}],
                   lambda v: db.add_unit(self.user, v["code"], v["name"]))

    def add_market(self):
        self._form("Add market", [{"key": "name", "label": "Market name"},
                                  {"key": "em", "label": "Emirate", "kind": "combo",
                                   "options": options(db.list_emirates(), "emirate_name", "emirate_id")},
                                  {"key": "area", "label": "Area"}],
                   lambda v: db.add_market(self.user, v["name"], v["em"], v["area"]))


class ActivityTab(Tab):
    icon, title = "☰", "Activity Log"

    def build(self):
        self.header([("⟳ Refresh", self.refresh, None)])
        ttk.Label(self, text="Stock movements (newest first)", style="Section.TLabel").pack(anchor="w")
        self.moves = Table(self, [
            ("movement_date", "Date", 140, "center"), ("lot_id", "Lot #", 55, "center"),
            ("crop_name", "Crop", 100, "w"), ("farm_name", "Farm", 160, "w"),
            ("movement_type", "Movement", 150, "w", lambda s: MOVEMENT_LABEL.get(s, s)),
            ("quantity", "Qty", 70, "e"), ("unit_code", "Unit", 50, "center"),
            ("full_name", "By", 120, "w"), ("reason", "Reason", 260, "w")], height=9)
        self.moves.pack(fill="both", expand=True, pady=(4, 10))
        ttk.Label(self, text="Request status changes", style="Section.TLabel").pack(anchor="w")
        self.changes = Table(self, [
            ("changed_at", "Date", 140, "center"), ("request_id", "Req #", 55, "center"),
            ("old_status", "From", 150, "w", lambda s: STATUS_LABEL.get(s, "—") if s else "—"),
            ("new_status", "To", 150, "w", lambda s: STATUS_LABEL.get(s, s)),
            ("full_name", "By", 130, "w"), ("reason", "Reason", 260, "w")], height=7)
        self.changes.pack(fill="both", expand=True, pady=(4, 0))

    def refresh(self):
        self.moves.load(db.query("""
            SELECT m.movement_date, m.lot_id, s.crop_name, s.farm_name, m.movement_type, m.quantity,
                   s.unit_code, u.full_name, m.reason
            FROM stock_movements m JOIN v_lot_stock s ON s.lot_id=m.lot_id JOIN users u ON u.user_id=m.user_id
            ORDER BY m.movement_date DESC, m.movement_id DESC LIMIT 300"""))
        self.changes.load(db.query("""
            SELECT h.changed_at, h.request_id, h.old_status, h.new_status, u.full_name, h.reason
            FROM request_status_history h JOIN users u ON u.user_id=h.changed_by
            ORDER BY h.changed_at DESC, h.history_id DESC LIMIT 300"""))


# ----------------------------------------------------------------------
# Screens
# ----------------------------------------------------------------------
TABS_BY_ROLE = {
    "farmer": [("farms", FarmsTab), ("cycles", CyclesTab), ("harvest", HarvestTab), ("allocate", AllocateTab),
               ("loss", LossTab), ("search", SearchTab), ("ai", AssistantTab)],
    "market": [("find", FindProduceTab), ("requests", MyRequestsTab), ("deliveries", DeliveriesTab),
               ("search", SearchTab), ("ai", AssistantTab)],
    "admin": [("users", UsersTab), ("reference", ReferenceTab), ("activity", ActivityTab),
              ("loss", LossTab), ("search", SearchTab), ("ai", AssistantTab)],
}


class LoginScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=30)
        self.app = app
        self.pack(fill="both", expand=True)
        ttk.Label(self, text="☘", font=("", 40), foreground=GREEN).pack(pady=(20, 0))
        ttk.Label(self, text="Farm-to-Market", style="Title.TLabel", font=("", 24, "bold")).pack()
        ttk.Label(self, text="Local farm & market food availability", style="Muted.TLabel",
                  font=("", 12)).pack(pady=(2, 26))
        try:
            users = db.list_demo_users()
        except Exception as e:
            return self.error(db.friendly_error(e))
        ttk.Label(self, text="Choose a demo user to continue", style="Section.TLabel").pack(pady=(0, 12))
        row = ttk.Frame(self)
        row.pack()
        for role in ("farmer", "market", "admin"):
            icon, label, color = ROLE_INFO[role]
            card = ttk.Frame(row, style="Card.TFrame", padding=16)
            card.pack(side="left", padx=12, anchor="n")
            tk.Label(card, text=icon, font=("", 26), fg=color, bg="white").pack()
            tk.Label(card, text=label, font=("", 13, "bold"), fg=color, bg="white").pack(pady=(0, 10))
            for u in [u for u in users if u["role"] == role]:
                sub = u["farms"] if role == "farmer" else u["market_name"] if role == "market" else "System admin"
                ttk.Button(card, text=f"☺  {u['full_name']}\n     {sub or '—'}", style="Role.TButton", width=34,
                           command=lambda uid=u["user_id"]: self.enter(uid)).pack(fill="x", pady=4)

    def error(self, message):
        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.pack(pady=10)
        tk.Label(card, text="⚠", font=("", 30), fg=RED, bg="white").pack()
        tk.Label(card, text=message, font=("", 12), bg="white", fg=TEXT, wraplength=520).pack(pady=10)
        ttk.Button(card, text="⟳ Try again", style="Primary.TButton", command=self.app.show_login).pack()

    def enter(self, user_id):
        try:
            user = db.get_user(user_id)
        except Exception as e:
            return messagebox.showerror("Cannot sign in", db.friendly_error(e), parent=self.app)
        if user:
            self.app.show_main(user)


class MainScreen(ttk.Frame):
    def __init__(self, app, user):
        super().__init__(app)
        self.app, self.user = app, user
        self.pack(fill="both", expand=True)
        icon, label, color = ROLE_INFO[user["role"]]
        head = tk.Frame(self, bg=DARK, height=56)
        head.pack(fill="x")
        tk.Label(head, text="☘  Farm-to-Market", bg=DARK, fg="white", font=("", 15, "bold")).pack(side="left", padx=16, pady=10)
        ttk.Button(head, text="⇦ Switch user", style="Header.TButton", command=app.show_login).pack(side="right", padx=14)
        tk.Label(head, text=f" {icon} {label} ", bg=color, fg="white", font=("", 10, "bold")).pack(side="right", padx=6)
        ctx = ""
        if user["role"] == "market":
            ctx = "  ·  " + db.query_one("SELECT market_name FROM markets WHERE market_id=%s", (user["market_id"],))["market_name"]
        tk.Label(head, text=f"☺ {user['full_name']}{ctx}", bg=DARK, fg="white", font=("", 11)).pack(side="right", padx=6)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.tabs = {}
        for key, cls in TABS_BY_ROLE[user["role"]]:
            try:
                tab = cls(self)
            except Exception as e:
                messagebox.showerror("Cannot open screen", db.friendly_error(e), parent=app)
                continue
            self.tabs[key] = tab
            self.nb.add(tab, text=f"{cls.icon}  {cls.title}")
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_current())

    def refresh_current(self):
        tab = self.nametowidget(self.nb.select()) if self.nb.select() else None
        if tab:
            try:
                tab.refresh()
            except Exception as e:
                self.app.toast("⚠ " + db.friendly_error(e), error=True)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Farm-to-Market – Local Farm & Market Food Availability")
        self.geometry("1280x800")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        setup_style(self)
        icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(icon).ellipse((4, 4, 60, 60), fill=GREEN)
        ImageDraw.Draw(icon).ellipse((20, 14, 44, 50), fill=LIGHT)
        self._icon = ImageTk.PhotoImage(icon)
        self.iconphoto(True, self._icon)
        self.status = tk.Label(self, text="", anchor="w", bg="white", fg=GREEN, font=("", 10, "bold"), padx=14, pady=6)
        self.status.pack(side="bottom", fill="x")
        self.screen = None
        self._toast_job = None
        self.show_login()

    def _swap(self, factory):
        if self.screen:
            self.screen.destroy()
            gc.collect()          # free old screen's Tk objects in the main thread
        self.screen = factory()

    def show_login(self):
        self._swap(lambda: LoginScreen(self))
        self.status.configure(text="")

    def show_main(self, user):
        self._swap(lambda: MainScreen(self, user))
        self.screen.refresh_current()
        self.toast(f"✔ Signed in as {user['full_name']}.")

    def toast(self, text, error=False):
        self.status.configure(text=text, fg=RED if error else GREEN)
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(6000, lambda: self.status.configure(text=""))

    def destroy(self):
        if self._toast_job:
            self.after_cancel(self._toast_job)
        super().destroy()

    def run(self, fn, *args, ok=None):
        """Run a database action; show a friendly message instead of raw errors. Returns False on failure."""
        try:
            result = fn(*args)
        except Exception as e:
            messagebox.showerror("Action not completed", db.friendly_error(e), parent=self)
            return False
        if ok:
            self.toast(ok)
        return result


if __name__ == "__main__":
    App().mainloop()
