# Reproducible report and poster exports

**BUILD-01 | Review candidate, 17 November 2026.** Builds are source-only: no application imports, database setup or mutation. The review PDFs incorporate the Track A diagrams and both historical and follow-up test records. Hashes in `docs/report/input-manifest.json` prevent stale or substituted inputs.

## Sources and outputs

| Source | Purpose | Output |
|---|---|---|
| `docs/report/technical-report.md` | Five narrative sections with explicit page breaks | `submission/technical-report.pdf` (12 pages: five A4 narrative/evidence pages and seven native-size vector diagram sheets) |
| `docs/poster/poster.json` | Poster wording, layout, ER node positions and relationships | `submission/poster.pdf` (one 1920 x 1080 pt landscape page) |
| `docs/report/build_documents.py` | Layout, input-hash checks, evidence assertions and image inventory | Both PDFs and ignored build metadata under `output/documents/` |
| `docs/report/input-manifest.json` | Provenance and SHA-256 of every builder input and tested source file | Validates checked-in inputs; no Git object fetch needed |

The poster is a compact presentation view of seven conceptual ER entities and six relationships. The builder checks their IDs and cardinalities against the Draw.io diagram. Supporting reference, ownership and history links are omitted from this view; the report includes the complete conceptual diagram and six schema sheets. The appendix preserves the diagram page sizes so column labels remain legible.

## Build

Prerequisites: Python 3.12 and the pinned document libraries in `docs/report/requirements-docs.txt`. For PDF previews, use Poppler or another renderer. Application requirements remain separate.

```powershell
py -3.12 -m venv .local/docs-venv
.\.local\docs-venv\Scripts\python.exe -m pip install -r docs/report/requirements-docs.txt
.\.local\docs-venv\Scripts\python.exe docs/report/build_documents.py
```

The default input directory is the repository root. To validate another checkout or freshly extracted tree, pass `--input-dir <path-to-tree>`. Output PDFs are written to `submission/`; build checks and the photo inventory go to ignored `output/documents/`. The builder checks 14 historical AI questions, preserves earlier Track A failure totals, verifies the later 173 backend / 22 GUI results and seven assistant/read-only checks, validates source hashes, verifies poster ER relationships and guards report page overflow.

## Recorded build and visual check

Built with Python 3.12.12, ReportLab 4.4.9, pypdf 6.21.4 and Pillow 13.0.0 on Windows 11. The PDFs passed structural/page-count/name checks: report 12 pages, poster 1 page. I rendered all 12 report pages and the poster at 1920 × 1080 and visually inspected them after the final wording/build change. Tables, current-vs-historical labels, diagram appendix, poster relationships and review-status caveat are visible without clipping or overlap. Latest report SHA-256 is recorded in `docs/report/build-validation-followup.json`; the poster hash and manifest are in that same record. Poppler noted missing Symbol/ArialUnicode display fonts but exited successfully; the operators/diagram marks rendered in the inspected pages. `docs/report/input-manifest.json` records source hashes; `docs/report/build-validation-followup.json` records the final PDF hashes and QA result.

The report retains original Track A results (backend 163 Pass / 4 Fail / 1 Info; GUI 21 Pass / 1 Fail) as historical. It separately documents the later follow-up (65 original checks, 173 backend, 22 GUI including restart, 7 assistant/read-only, 3 helper checks and 851 diagram checks). These evidence sets refer to distinct source versions and disposable database instances. See `docs/evidence/FIX_VALIDATION.md`.

The mixed page sizes are intentional: shrinking the detailed relational schema to A4 would reduce label readability. A real projector test, screen-reader/accessibility check and team timed rehearsal remain for the team. The PDF build alone does not establish reviewer acceptance.

## Candidate package

The review-candidate ZIP and its member manifest are created by `scripts/build_candidate.py`. That script uses an explicit include list and excludes local credentials, Git metadata, virtual environments, caches, ignored output, archives and agent skill folders. The ZIP is extracted to an ignored clean directory and then checked for member hashes and required paths. A package check is a review artifact; it is not instructor acceptance or course submission.

## Lab 7 revision — 18 November 2026
Current diagram build and checks: `python docs/diagrams/tools/build_lab7.py`, then `python docs/diagrams/tools/check_lab7.py`, followed by `python docs/report/build_documents.py`. These supersede the earlier diagram layout and 12-page report instructions. Current report: 13 pages (five narrative, five conceptual sheets, three relational sheets); poster: one page. Rendering: `pdftoppm -scale-to 1500 -png submission/technical-report.pdf output/report` and likewise for the poster. No runtime database is used.
