"""Track A GUI end-to-end flow driven through the real Tkinter widgets.

!!! MUTATES DATA. Run ONLY on a disposable MySQL instance loaded with fresh seed data. !!!

Same guards as track_a_remaining_checks.py: nothing runs on import, env
FARM_DISPOSABLE_DB_CONFIRM must equal "<DB_HOST>:<DB_PORT>/<DB_NAME>", and phase 1 requires
untouched seed data. Message boxes are intercepted and recorded instead of blocking.
Widgets and callbacks are invoked programmatically (no physical mouse); this is GUI
automation evidence, not a manual usability study.

  .\\.venv\\Scripts\\python.exe app\\setup_database.py
  $env:FARM_DISPOSABLE_DB_CONFIRM = "127.0.0.1:3317/farm_market_db"
  .\\.venv\\Scripts\\python.exe app\\tests\\track_a_gui_flow.py            # phase 1
  .\\.venv\\Scripts\\python.exe app\\tests\\track_a_gui_flow.py --restart  # phase 2, new process

Writes docs/evidence/track-a/gui-flow.json (merged across phases) and gui-*.png screenshots.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
ROOT = os.path.dirname(APP)
OUT = os.path.join(ROOT, "docs", "evidence", "track-a")
JSON_PATH = os.path.join(OUT, "gui-flow.json")
STATE = os.path.join(ROOT, "output", "gui-flow-state.json")   # ignored hand-off between phases


def main():
    sys.path.insert(0, APP)
    import db
    s = db.db_settings()
    target = f"{s['host']}:{s['port']}/{s['database']}"
    if os.environ.get("FARM_DISPOSABLE_DB_CONFIRM") != target:
        sys.exit(f"Refusing to run: set FARM_DISPOSABLE_DB_CONFIRM={target} only if that database is disposable.")
    import app as gui
    from PIL import ImageGrab

    restart = "--restart" in sys.argv
    results, dialogs = [], []
    if restart and os.path.exists(JSON_PATH):
        results = [r for r in json.load(open(JSON_PATH, encoding="utf-8"))["results"] if r["id"] != "GUI-IMG-02"]
    elif not restart:
        n = db.query_one("SELECT COUNT(*) n FROM harvest_lots")["n"]
        if n != 13 or db.query_one("SELECT available FROM v_lot_stock WHERE lot_id=13")["available"] != 120:
            sys.exit("Refusing to run phase 1: database is not fresh seed data.")

    def rec(cid, title, expected, actual, ok, shot=None):
        outcome = "Blocked" if ok is None else ("Pass" if ok else "Fail")
        results.append(dict(id=cid, title=title, expected=expected, actual=str(actual),
                            outcome=outcome, screenshot=shot))
        print(f"{outcome:<7} {cid:<8} {title}" + ("" if outcome == "Pass" else f"  ->  {actual}"))

    def capture(kind):
        def f(title, message, **_):
            dialogs.append((kind, title, message))
            return True
        return f
    gui.messagebox.showerror = capture("error")
    gui.messagebox.showinfo = capture("info")
    gui.messagebox.askyesno = capture("yesno")

    A = gui.App()
    A.attributes("-topmost", True)

    def pump(n=6):
        for _ in range(n):
            A.update()
            time.sleep(0.04)

    def print_window():
        """Capture the app window via Win32 PrintWindow (works while covered / not foreground)."""
        import ctypes
        from ctypes import wintypes
        from PIL import Image
        user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
        hwnd = int(A.wm_frame(), 16)
        r = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        w, h = r.right - r.left, r.bottom - r.top
        hdc = user32.GetWindowDC(hwnd)
        mdc = gdi32.CreateCompatibleDC(hdc)
        bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
        gdi32.SelectObject(mdc, bmp)
        user32.PrintWindow(hwnd, mdc, 2)  # PW_RENDERFULLCONTENT

        class BIH(ctypes.Structure):
            _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                        ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]
        bih = BIH(ctypes.sizeof(BIH), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
        buf = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bih), 0)
        gdi32.DeleteObject(bmp)
        gdi32.DeleteDC(mdc)
        user32.ReleaseDC(hwnd, hdc)
        return Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1)

    def shot(name):
        if A.state() != "normal":          # restore if the desktop minimised the window
            A.deiconify()
        A.lift()
        pump()
        try:
            img = print_window()
            if max(img.convert("L").getextrema()) >= 20:
                path = os.path.join(OUT, f"gui-{name}.png")
                img.save(path)
                return os.path.relpath(path, ROOT).replace("\\", "/")
        except Exception as e:  # noqa: BLE001
            print(f"PrintWindow failed for {name}: {e}; falling back to screen grab")
        x, y, w, h = A.winfo_rootx(), A.winfo_rooty(), A.winfo_width(), A.winfo_height()
        path = os.path.join(OUT, f"gui-{name}.png")
        # Tk reports logical (DPI-virtualised) pixels; ImageGrab captures physical pixels.
        k = ImageGrab.grab().width / max(1, A.winfo_screenwidth())
        img = ImageGrab.grab(bbox=tuple(int(v * k) for v in (x, y, x + w, y + h)))
        if max(img.convert("L").getextrema()) < 20:      # blank/black capture (display off or locked)
            print(f"WARNING: screenshot {name} is blank; display not capturable. Not saved.")
            return "blank capture (not saved)"
        img.save(path)
        return os.path.relpath(path, ROOT).replace("\\", "/")

    def login(uid):
        A.show_login()
        pump()
        A.screen.enter(uid)
        pump()
        return A.screen

    def open_tab(screen, key):
        tab = screen.tabs[key]
        screen.nb.select(tab)
        pump()
        tab.refresh()
        pump()
        return tab

    def select(table, pred):
        for iid, row in table._rows.items():
            if pred(row):
                table.tree.selection_set(iid)
                table.tree.see(iid)
                pump()
                return row
        return None

    def dialog():
        ds = [w for w in A.winfo_children() if isinstance(w, gui.FormDialog) and w.winfo_exists()]
        return ds[-1] if ds else None

    def last_dialog():
        return dialogs[-1][2] if dialogs else None

    def lot_stock(lot):
        r = db.query_one("SELECT on_hand, reserved, available FROM v_lot_stock WHERE lot_id=%s", (lot,))
        return tuple(int(r[k]) if r[k] == int(r[k]) else float(r[k]) for k in ("on_hand", "reserved", "available"))

    os.makedirs(OUT, exist_ok=True)

    if restart:
        st = json.load(open(STATE, encoding="utf-8"))
        scr = login(7)
        find = open_tab(scr, "find")
        find.crop.set_value(6)
        find.refresh()
        pump()
        row = select(find.table, lambda r: r["lot_id"] == st["lot"])
        img = db.lot_images(st["lot"])
        same = img and hashlib.sha256(img[0]["image_data"]).hexdigest() == st["sha256"]
        p = shot("restart-photo")
        rec("GUI-IMG-02", "New process: buyer finds the GUI-uploaded lot and its photo renders",
            f"lot {st['lot']} listed; photo rendered; caption '{st['file']}'; stored bytes unchanged",
            f"listed={bool(row)}; rendered={find.photo._tk is not None}; caption='{find.photo.caption.cget('text')}'; "
            f"sha256 equal={same}", bool(row) and find.photo._tk is not None and st["file"] in find.photo.caption.cget("text")
            and same, p)
        A.destroy()
    else:
        # ---- Farmer records a harvest with photo through the form (for the restart phase)
        scr = login(4)  # Khalid Nasser, Hatta Valley Farm
        har = open_tab(scr, "harvest")
        har.record()
        pump()
        d = dialog()
        d.widgets["cycle"][1].set_value(7)
        d.widgets["qty"][1].insert(0, "12.5")
        photo = os.path.join(APP, "sample_images", "zucchini.jpg")
        d.widgets["photo"][1].insert(0, photo)
        d._submit()
        pump()
        lot = db.query_one("SELECT MAX(lot_id) l FROM harvest_lots")["l"]
        img = db.lot_images(lot)
        select(har.table, lambda r: r["lot_id"] == lot)
        p = shot("farmer-harvest")
        rec("GUI-HAR-01", "Farmer records 12.5 kg Zucchini harvest with JPG through the form",
            "toast 'Harvest lot #N recorded'; lot 12.5/0/12.5; one BLOB; photo shown",
            f"toast='{A.status.cget('text')}'; stock={lot_stock(lot)}; photos={len(img)}; rendered={har.photo._tk is not None}",
            "recorded" in A.status.cget("text") and lot_stock(lot) == (12.5, 0, 12.5) and len(img) == 1
            and har.photo._tk is not None, p)
        with open(photo, "rb") as fh:
            orig = fh.read()
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump({"lot": lot, "sha256": hashlib.sha256(orig).hexdigest(), "file": "zucchini.jpg"},
                  open(STATE, "w", encoding="utf-8"))
        har.record()
        pump()
        d = dialog()
        d.widgets["cycle"][1].set_value(7)
        d.widgets["qty"][1].insert(0, "-3")
        d._submit()
        pump()
        rec("GUI-HAR-02", "Negative harvest quantity in the form", "inline error; dialog stays open; no new lot",
            f"error='{d.error.cget('text')}'; open={d.winfo_exists()}; max lot={db.query_one('SELECT MAX(lot_id) l FROM harvest_lots')['l']}",
            "negative" in d.error.cget("text") and d.winfo_exists() and
            db.query_one("SELECT MAX(lot_id) l FROM harvest_lots")["l"] == lot)
        d.destroy()

        # ---- Market buyer searches and sees photos / no-photo fallback
        scr = login(7)  # Noura Ahmed, Sharjah Souq Market
        find = open_tab(scr, "find")
        find.crop.set_value(1)
        find.minq.insert(0, "50")
        find.refresh()
        pump()
        rows = list(find.table._rows.values())
        select(find.table, lambda r: r["lot_id"] == 8)
        p = shot("buyer-search-photo")
        rec("GUI-SRCH-01", "Buyer filters Tomato with minimum 50 and selects lot #8",
            "only Tomato lots with available >= 50; lot #8 photo tomato_3.jpg rendered",
            f"lots={sorted(r['lot_id'] for r in rows)}; caption='{find.photo.caption.cget('text')}'",
            rows and all(r["crop_name"] == "Tomato" and r["available"] >= 50 for r in rows)
            and "tomato_3.jpg" in find.photo.caption.cget("text") and find.photo._tk is not None, p)
        select(find.table, lambda r: r["lot_id"] == 13)
        rec("IMG-04d", "Buyer selects lot #13 (seed lot without a photo)", "'No photo for this lot yet', no crash",
            find.photo.canvas.cget("text"), "No photo" in find.photo.canvas.cget("text"))
        find.minq.delete(0, "end")
        find.minq.insert(0, "abc")
        n = len(dialogs)
        find.refresh()
        pump()
        rec("GUI-SRCH-02", "Buyer enters minimum quantity 'abc'", "friendly error dialog, no crash",
            dialogs[-1] if len(dialogs) > n else "no dialog", len(dialogs) > n and "number" in last_dialog())
        find.minq.delete(0, "end")
        find.refresh()
        pump()

        # ---- Request via keyboard: Escape cancels, Return submits.
        # Keyboard events reach Tk only when Windows grants the test window foreground focus; when it
        # does not (e.g. the user is typing in another application) these checks are recorded as Blocked
        # and the flow continues through the dialog's Save button instead.
        select(find.table, lambda r: r["lot_id"] == 8)
        before = db.query_one("SELECT COUNT(*) n FROM market_requests")["n"]
        A.deiconify()
        A.focus_force()
        pump()
        find.request()
        pump()
        d = dialog()
        has_focus = d.focus_get() is not None
        if has_focus:
            d.focus_get().event_generate("<Escape>")
            pump()
            rec("GUI-02a", "Escape in the New request form", "dialog closes; no request created",
                f"dialog open={d.winfo_exists()}; requests {before}->{db.query_one('SELECT COUNT(*) n FROM market_requests')['n']}",
                not d.winfo_exists() and db.query_one("SELECT COUNT(*) n FROM market_requests")["n"] == before)
        else:
            rec("GUI-02a", "Escape in the New request form", "dialog closes; no request created",
                "OS did not grant keyboard focus to the test window", None)
            d.destroy()
        A.focus_force()
        pump()
        find.request()
        pump()
        d = dialog()
        rec("GUI-02b", "New request form opened from a selected lot pre-selects its crop and unit",
            "crop Tomato, unit kg", f"crop={d.widgets['crop'][1].get()}; unit={d.widgets['unit'][1].get()}",
            d.widgets["crop"][1].get() == "Tomato" and d.widgets["unit"][1].get() == "kg")
        if d.focus_get() is not None:
            rec("GUI-02c", "First text entry (Quantity) receives keyboard focus", "focus on Quantity entry",
                f"focus is qty={d.focus_get() is d.widgets['qty'][1]}", d.focus_get() is d.widgets["qty"][1])
        else:
            rec("GUI-02c", "First text entry (Quantity) receives keyboard focus", "focus on Quantity entry",
                "OS did not grant keyboard focus to the test window", None)
        d.widgets["qty"][1].insert(0, "150")
        d.widgets["notes"][1].insert(0, "Track A GUI flow")
        via = "Return key"
        if d.focus_get() is not None:
            d.widgets["qty"][1].focus_set()
            pump()
            d.widgets["qty"][1].event_generate("<Return>")
            pump()
        if d.winfo_exists():
            if has_focus:
                rec("GUI-02d", "Return submits the form", "dialog submits", "dialog still open after Return", False)
            else:
                rec("GUI-02d", "Return submits the form", "dialog submits",
                    "OS did not grant keyboard focus to the test window", None)
            via = "Save button (_submit)"
            d._submit()
            pump()
        elif has_focus:
            rec("GUI-02d", "Return submits the form", "dialog submits", "submitted by Return", True)
        rid = db.query_one("SELECT MAX(request_id) r FROM market_requests")["r"]
        req = db.query_one("SELECT * FROM market_requests WHERE request_id=%s", (rid,))
        rec("GUI-REQ-01", f"Buyer creates 150 kg Tomato request from the selected lot ({via})",
            "request OPEN, 150 kg, market 3, by user 7",
            f"#{rid} {req['status']} {req['requested_quantity']} market={req['market_id']} by={req['created_by']}; toast='{A.status.cget('text')}'",
            req["status"] == "OPEN" and req["requested_quantity"] == 150 and req["market_id"] == 3 and req["created_by"] == 7)

        # ---- Farmer allocates; over-allocation blocked
        scr = login(3)  # Fatima Rashid, Al Dhaid Fresh Farm (lots 8, 13)
        alc = open_tab(scr, "allocate")
        select(alc.requests, lambda r: r["request_id"] == rid)
        lots = sorted(r["lot_id"] for r in alc.lots._rows.values())
        prefill = alc.qty.get()
        rec("GUI-ALC-00", "Selecting the request lists only Fatima's matching Tomato kg lots and pre-fills the remainder",
            "lots [8, 13]; quantity 150", f"lots={lots}; qty='{prefill}'", lots == [8, 13] and prefill == "150")
        select(alc.lots, lambda r: r["lot_id"] == 13)
        n = len(dialogs)
        alc.allocate()
        pump()
        p = shot("allocate-blocked")
        rec("GUI-ALC-02", "Allocate 150 from lot #13 (120 available)", "error 'Not enough stock… only 120'; nothing reserved",
            f"{dialogs[-1] if len(dialogs) > n else 'no dialog'}; lot13={lot_stock(13)}",
            len(dialogs) > n and "only 120" in last_dialog() and lot_stock(13) == (120, 0, 120), p)
        select(alc.requests, lambda r: r["request_id"] == rid)
        select(alc.lots, lambda r: r["lot_id"] == 13)
        alc.qty.delete(0, "end")
        alc.qty.insert(0, "120")
        alc.allocate()
        pump()
        select(alc.requests, lambda r: r["request_id"] == rid)
        select(alc.lots, lambda r: r["lot_id"] == 8)
        rem = alc.qty.get()
        alc.allocate()
        pump()
        p = shot("allocate-done")
        st = db.query_one("SELECT status FROM market_requests WHERE request_id=%s", (rid,))["status"]
        rec("GUI-ALC-01", "Allocate 120 from lot #13, then the pre-filled remainder from lot #8",
            "remainder pre-filled 30; request FULLY_ALLOCATED; lot13 120/120/0; lot8 150/80/70",
            f"remainder='{rem}'; {st}; lot13={lot_stock(13)}; lot8={lot_stock(8)}",
            rem == "30" and st == "FULLY_ALLOCATED" and lot_stock(13) == (120, 120, 0) and lot_stock(8) == (150, 80, 70), p)

        # ---- Buyer confirms a partial delivery
        scr = login(7)
        dlv = open_tab(scr, "deliveries")
        pend = sorted((r["lot_id"], int(r["allocated_quantity"])) for r in dlv.pending._rows.values())
        select(dlv.pending, lambda r: r["lot_id"] == 13 and r["request_id"] == rid)
        dlv.received.delete(0, "end")
        dlv.received.insert(0, "110")
        n = len(dialogs)
        dlv.confirm()
        pump()
        rec("GUI-DEL-03", "Confirm 110 of 120 without a reason", "error asking for a discrepancy reason; no receipt",
            f"{dialogs[-1] if len(dialogs) > n else 'no dialog'}; receipts for request="
            f"{db.query_one('SELECT COUNT(*) n FROM delivery_receipts d JOIN allocations a ON a.allocation_id=d.allocation_id WHERE a.request_id=%s', (rid,))['n']}",
            len(dialogs) > n and "reason" in last_dialog())
        dlv.reason.insert(0, "10 kg bruised in transit")
        dlv.confirm()
        pump()
        select(dlv.pending, lambda r: r["lot_id"] == 8 and r["request_id"] == rid)
        full = dlv.received.get()
        dlv.confirm()
        pump()
        p = shot("deliveries-partial")
        rc = db.query("""SELECT a.lot_id, d.allocated_quantity, d.received_quantity, d.discrepancy_quantity, d.discrepancy_reason
                         FROM delivery_receipts d JOIN allocations a ON a.allocation_id=d.allocation_id
                         WHERE a.request_id=%s ORDER BY a.lot_id""", (rid,))
        rec("GUI-DEL-02", "Partial receipt 110/120 with reason, then full receipt 30/30 (pre-filled)",
            "pending listed [(8,30),(13,120)]; receipts lot8 30/30/0, lot13 120/110/10 with reason; lot13 0/0/0; lot8 120/50/70",
            f"pending={pend}; prefill='{full}'; receipts={[(r['lot_id'], str(r['allocated_quantity']), str(r['received_quantity']), str(r['discrepancy_quantity']), r['discrepancy_reason']) for r in rc]}; "
            f"lot13={lot_stock(13)}; lot8={lot_stock(8)}",
            pend == [(8, 30), (13, 120)] and len(rc) == 2 and rc[1]["discrepancy_quantity"] == 10
            and lot_stock(13) == (0, 0, 0) and lot_stock(8) == (120, 50, 70), p)
        reqs = open_tab(scr, "requests")
        row = select(reqs.table, lambda r: r["request_id"] == rid)
        p = shot("requests-status")
        rec("GUI-DEL-05", "My Requests shows the request after delivery",
            "allocated 150, received 140; status shown per current policy (DELIVERED)",
            f"status={row['status']}, allocated={row['allocated_quantity']}, received={row['received_quantity']}; "
            f"allocations listed={len(reqs.allocs._rows)}",
            row["status"] == "DELIVERED" and row["allocated_quantity"] == 150 and row["received_quantity"] == 140, p)

        # ---- Pre-filled allocation quantity of 1,000 or more
        big = db.create_request(db.get_user(7), 1, "1500", 1, time.strftime("%Y-%m-%d"), "large order")
        scr = login(3)
        alc = open_tab(scr, "allocate")
        select(alc.requests, lambda r: r["request_id"] == big)
        select(alc.lots, lambda r: r["lot_id"] == 8)
        pre = alc.qty.get()
        n = len(dialogs)
        alc.allocate()
        pump()
        rec("GUI-ALC-03", "Request of 1,500 kg: allocate using the pre-filled quantity unchanged",
            "observe pre-fill format and result (Deliveries tab strips thousands separators; Allocate tab?)",
            f"prefill='{pre}'; {dialogs[-1] if len(dialogs) > n else 'no dialog'}; lot8={lot_stock(8)}",
            "," not in pre)

        # ---- Loss & Surplus thresholds through the GUI
        scr = login(3)
        ls = open_tab(scr, "loss")
        for val, cid in (("abc", "GUI-LS-02a"), ("61", "GUI-LS-02b")):
            ls.near.set(val)
            n = len(dialogs)
            ls.refresh()
            pump()
            rec(cid, f"Near-expiry spinbox '{val}' then Apply", "friendly 'Invalid threshold' dialog",
                dialogs[-1] if len(dialogs) > n else "no dialog", len(dialogs) > n and dialogs[-1][1] == "Invalid threshold")
        ls.near.set("3")
        ls.refresh()
        pump()
        flags = list(ls.table._rows.values())
        p = shot("loss-surplus")
        rec("GUI-LS-01", "Valid thresholds 3/7 for Fatima", "only Fatima's farm; rows sorted by priority",
            f"{len(flags)} rows, farms={sorted({r['farm_name'] for r in flags})}, priorities={[r['priority'] for r in flags]}",
            flags and {r["farm_name"] for r in flags} == {"Al Dhaid Fresh Farm"}
            and [r["priority"] for r in flags] == sorted(r["priority"] for r in flags), p)

        # ---- Unreadable stored images
        with db.transaction() as cur:
            cur.execute("""INSERT INTO harvest_lot_images (lot_id, file_name, mime_type, image_data, uploaded_by)
                           VALUES (10, 'corrupt.jpg', 'image/jpeg', %s, 3)""", (b"\xff\xd8garbage" * 50,))
        jpg = open(os.path.join(APP, "sample_images", "eggplant.jpg"), "rb").read()
        trunc = os.path.join(ROOT, "output", "truncated_eggplant.jpg")
        open(trunc, "wb").write(jpg[: len(jpg) // 2])
        up_err = None
        try:
            db.add_lot_image(db.get_user(3), 10, trunc)
        except Exception as e:  # noqa: BLE001
            up_err = db.friendly_error(e)
        scr = login(7)
        find = open_tab(scr, "find")
        select(find.table, lambda r: r["lot_id"] == 10)
        first = (find.photo.caption.cget("text"), find.photo.canvas.cget("text"))
        find.photo._step(1)
        pump()
        second = (find.photo.caption.cget("text"), find.photo.canvas.cget("text"))
        p = shot("image-unavailable")
        rec("IMG-04e", "Lot #10 with a truncated JPEG (accepted by upload validation) and a corrupt BLOB",
            "upload of truncated file: observe; both unreadable photos show '⚠ Image unavailable' without crashing",
            f"upload={'accepted' if up_err is None else up_err}; newest={first}; next={second}",
            "Image unavailable" in first[1] and "Image unavailable" in second[1], p)
        A.destroy()

    data = {"date": time.strftime("%Y-%m-%d"), "dialogs_recorded": len(dialogs), "results": results}
    json.dump(data, open(JSON_PATH, "w", encoding="utf-8"), indent=1, default=str)
    print("Summary:", {k: sum(1 for r in results if r["outcome"] == k) for k in ("Pass", "Fail", "Blocked")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
