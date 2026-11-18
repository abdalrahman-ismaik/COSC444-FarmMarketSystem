# Build and verify the report, poster, and review package

**BUILD-01 · COSC444 Database Systems · Lab B1**

These commands rebuild the diagrams, technical report, poster, and ZIP from checked-in sources. Document builds do not import the application or connect to a database. Application test results below are dated evidence; rebuilding documents does not rerun them.

## Sources and outputs

| Source | Output |
|---|---|
| `docs/diagrams/tools/build_lab7.py` | Five-sheet conceptual ER and three-sheet relational schema, each as Draw.io, PDF, and SVG. |
| `docs/report/technical-report.md` | Five narrative pages in the 13-page report. |
| `docs/poster/poster.json` | One-page 1920 × 1080 poster with an ER presentation view. |
| `docs/report/build_documents.py` | `submission/technical-report.pdf`, `submission/poster.pdf`, and ignored build checks under `output/documents/`. |
| `scripts/build_candidate.py` | `submission/FarmMarketSystem_B1_review_candidate.zip` and its external SHA-256 manifest. |

The poster shows seven central entities and six relationships. The report appendix carries the full conceptual model and all 15 relational tables. The diagrams preserve their native landscape page size so labels remain readable when zoomed; printing them on A4/Letter requires scaling.

## Build on Windows

Use Python 3.12 and the pinned document-only dependencies. Keep these separate from the application's requirements.

```powershell
py -3.12 -m venv .local/docs-venv
.\.local\docs-venv\Scripts\python.exe -m pip install -r docs/report/requirements-docs.txt
.\.local\docs-venv\Scripts\python.exe docs/diagrams/tools/build_lab7.py
.\.local\docs-venv\Scripts\python.exe docs/diagrams/tools/check_lab7.py
.\.local\docs-venv\Scripts\python.exe docs/report/build_documents.py
python scripts/build_candidate.py --verify-dir .local/candidate-extraction-YYYYMMDD
```

Use a new verification directory inside `.local` each time. The package builder refuses an existing path, extracts the ZIP, and verifies required paths, member hashes, manifest, and excluded-path rules. It does not install or run the application.

To render the PDFs for visual review, install Poppler and run:

```powershell
pdftoppm -scale-to 1500 -png submission/technical-report.pdf output/report
pdftoppm -scale-to 1920 -png -singlefile submission/poster.pdf output/poster
```

## Recorded verification (18 November 2026)

- Independent Lab 7 SQL/XML check: **15 tables, 100 columns, 32 foreign keys, 13 named CHECK constraints; pass**.
- Rebuilt diagrams, report, and poster twice; outputs were byte-identical. The report has 13 pages (five narrative and eight diagram sheets); the poster has one page.
- Every report page and the poster were rendered and visually inspected. No clipping, overlap, or missing diagram labels were observed. Poppler emitted Symbol/ArialUnicode font warnings, but the rendered marks were visible.
- Current PDF hashes and input/source hashes are recorded in `docs/report/build-validation-final.json`; the report builder's structural and evidence assertions are in ignored `output/documents/build-checks.json`.
- Fresh package extraction checked required paths, member hashes, and exclusions. No `.env`, credentials, local environments, or agent skills were included.
- No new database, GUI, or Gemini run was made for this document pass. Dated application evidence is in `docs/evidence/FIX_VALIDATION.md` and `docs/evidence/fixes-2026-11-17/`.

The remaining human tasks are a projector check, confirmation of the demo venue, the three-member timed rehearsal, and the course upload. The exact upstream mapping for the 16 sample images also remains unresolved; see [image attribution](IMAGE_ATTRIBUTION.md).
