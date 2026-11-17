# Database diagrams: sources, exports and checks

Track A deliverables DB-01 and DB-02. The `.drawio` files are the editable sources: open them in Draw.io (diagrams.net) desktop or web. The PDF and SVG files are exports of those sources.

| File | Content |
|---|---|
| `conceptual-er.drawio` | One-page conceptual ER: Chen notation, (min,max) participation, derived attributes, key business rules R1–R10 |
| `conceptual-er.pdf`, `conceptual-er.svg` | Exports (vector) |
| `relational-schema.drawio` | Six pages: 1 overview of all 15 tables · 2 reference data and users · 3 cycles, lots, images, stock ledger · 4 requests, history, allocations, receipts · 5 the 15 FKs to `units`/`users` · 6 the two views |
| `relational-schema.pdf` | All six pages (vector, one PDF page per diagram page) |
| `relational-schema.svg`, `relational-schema-p2.svg` … `-p6.svg` | One SVG per page (`relational-schema.svg` = page 1) |
| `tools/generate_diagrams.py` | Regenerates both `.drawio` files from a column/type/constraint table transcribed from `app/schema.sql` |
| `tools/check_diagrams_vs_sql.py` | Read-only checker: parses the `.drawio` XML and compares it with `information_schema` of a loaded database |

## Tool versions used (2026-11-17, Windows 11)

- draw.io desktop **32.4.1** (`winget install JGraph.Draw`), used for export.
- Python 3.12.1; checker uses the app runtime venv (PyMySQL 1.2.4, python-dotenv 1.2.4).
- Preview rendering for visual QA: PyMuPDF 2.1, installed in a separate ignored venv (`.local/docs-venv`). It is not an app dependency.
- MySQL 8.0.46 (separate disposable instance) for the cross-check.

## Rebuild and export (PowerShell, repository root)

```powershell
python docs\diagrams\tools\generate_diagrams.py     # overwrites both .drawio files
$drawio = "$env:LOCALAPPDATA\Programs\draw.io\draw.io.exe"
& $drawio -x -f pdf --crop -o docs\diagrams\conceptual-er.pdf docs\diagrams\conceptual-er.drawio
& $drawio -x -f svg -o docs\diagrams\conceptual-er.svg docs\diagrams\conceptual-er.drawio
& $drawio -x -f pdf --crop -a -o docs\diagrams\relational-schema.pdf docs\diagrams\relational-schema.drawio
& $drawio -x -f svg -p 1 -o docs\diagrams\relational-schema.svg docs\diagrams\relational-schema.drawio
2..6 | ForEach-Object { & $drawio -x -f svg -p $_ -o "docs\diagrams\relational-schema-p$_.svg" docs\diagrams\relational-schema.drawio }
```

If you edit a `.drawio` file by hand in Draw.io, do not run the generator afterwards: it would overwrite your edits. Re-export, then re-run the checker.

`--crop` sizes each PDF page to its diagram, not to A4/Letter. The PDFs are vector files, so they zoom without loss. To print or place them in the report, scale each page to a landscape page; the relational detail pages are about 1,550 × 700 pt. draw.io's SVGs use HTML labels with an embedded PNG fallback, which is why each file is about 1–2 MB. Browsers render the HTML text; tools without `foreignObject` support show the fallback image. **For the technical report and poster, the PDFs are the recommended input.**

## Verify against the database (read-only)

Requires a database loaded from `app/schema.sql` and configured in `app/.env`:

```powershell
.\.venv\Scripts\python.exe docs\diagrams\tools\check_diagrams_vs_sql.py
```

Result on 2026-11-17 (disposable MySQL 8.0.46, fresh seed): **851 checks passed, 0 failed; FK edges drawn 32/32** (15 tables, 2 views, 13 CHECK constraints).

The checker was also mutation-tested. It ran against a copy with three injected errors: a wrong VARCHAR length, a wrong optionality marker and a renamed CHECK. It reported exactly those 3 failures.

## Visual QA performed

Every PDF page was rendered to PNG with PyMuPDF and inspected: 1 conceptual page and 6 schema pages. SVGs were also rendered in headless Microsoft Edge. Defects found and fixed:

- page-1 FK lines crossing tables;
- long dashed loops on the detail pages;
- the crop-cycle status ENUM clipped;
- an FK label colliding with a stub box;
- fan-line crowding on page 5;
- ALLOCATION attribute wrapping outside its box;
- legend and rule panels too small or too large.

Final state: no clipped labels, no lines through tables, and every crow's-foot end matches the column's nullability and uniqueness (also machine-checked). Fonts embedded: Arial family; Cambria Math supplies glyphs such as ⋈ and Σ.
