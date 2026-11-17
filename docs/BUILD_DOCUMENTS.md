# Reproducible report and poster exports

**BUILD-01 | Mohammad Arwani with Codex | 17 November 2026.** These outputs are review drafts. Track A PR #2 is open/unmerged; PACKAGE-01 awaits review dependencies. No database setup, application import or mutating test is part of this build.

## Editable sources and outputs

| Source | Purpose | Output |
|---|---|---|
| `docs/report/technical-report.md` | Five report sections, with explicit page-break comments | `submission/technical-report.pdf` (12 pages: five A4 text pages and seven native-size diagram sheets) |
| `docs/poster/poster.json` | Poster wording, node positions, entity IDs and relationships | `submission/poster.pdf` (one 1920 x 1080 pt, 16:9 page) |
| `docs/report/build_documents.py` | Layout, PDF assembly, input/evidence checks and image inventory | Both PDFs; ignored `output/documents/build-checks.json` and `image-inventory.json` |
| Track A conceptual ER and six schema PDF sheets | Original vector diagrams, unchanged | Report appendix pages 6-12 |

The poster is a presentation view of seven actual Track A entities and six actual relationships, not a replacement conceptual/schema deliverable. The builder checks entity IDs, relation names and cardinalities against the real `.drawio` XML. Supporting references/ownership/history are intentionally omitted from that view and explicitly labeled. Full diagrams and all exact SQL details remain in the report. The report preserves the source diagram page sizes instead of shrinking detailed labels onto A4. In the diagram captions, schema page numbers 1-6 refer to their original sheets (report pages 7-12).

## Pinned inputs

- Application evidence/source snapshot: `c8fd6cd0ec398ad5966df407abb9199d3343f196`.
- Track A: `80529fbfddf58b58735963f6a35847e22dedeadc`, [PR #2](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2), branch `ali/database-diagrams-validation`.
- The builder reads six named inputs from that Git commit into ignored `output/track-a/`. It does not checkout, merge, modify or duplicate Track A's tracked artifacts.
- `docs/report/build-validation.json` records PDF and input SHA-256s plus the local build/QA observations. It is an export evidence record, not a candidate-package manifest.

When reviewed Track A/app changes arrive, deliberately update the pin, evidence wording and expectations, then rebuild and reinspect all affected pages. A change to the application snapshot fails the builder rather than silently producing stale claims. Do not use a floating branch tip for final evidence. A source ZIP without Git objects needs the separate reviewed packaging workflow; this draft builder expects a Git clone with the pinned commit available.

## Portable build commands

Prerequisites: Git; Python 3.12; three document packages below; Poppler for previews. A fresh clone must fetch Track A's branch first. Use a separate docs environment; do not add these libraries to `app/requirements.txt`.

```powershell
git fetch origin ali/database-diagrams-validation
py -3.12 -m venv .local/docs-venv
.\.local\docs-venv\Scripts\python.exe -m pip install -r docs/report/requirements-docs.txt
.\.local\docs-venv\Scripts\python.exe docs/report/build_documents.py
pdftoppm -r 110 -png submission/technical-report.pdf output/documents/report
pdftoppm -scale-to 1920 -png -singlefile submission/poster.pdf output/documents/poster
```

`pdftoppm` must be on PATH or replaced by its installed absolute path. All build output is fixed to this repository's `submission/` and ignored `output/`; it does not write credentials or application data. A new virtual-environment install was not tested here; the recorded run used the bundled packages below.

## Actual environment and commands

Observed on Mohammad's PC, Windows 11 build 10.0.26200, 17 November 2026. Bundled Python **3.12.14**, ReportLab **4.4.9**, pypdf **6.21.4**, Pillow **13.0.0**, Poppler **26.07.0**. No application runtime was configured or started for this document task.

```powershell
$taskRuntime = 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-611-0_26.1112.611.0_x64__3k8sg7r9htsxt/dependencies'
& "$taskRuntime/python/python.exe" docs/report/build_documents.py
& "$taskRuntime/native/poppler/Library/bin/pdftoppm.exe" -r 110 -png submission/technical-report.pdf output/documents/report
& "$taskRuntime/native/poppler/Library/bin/pdftoppm.exe" -scale-to 1920 -png -singlefile submission/poster.pdf output/documents/poster
```

The initial document-library probe found no PyMuPDF; the build uses installed pypdf and Poppler instead. One early read-only inspection hit Windows cp1252 Unicode output; rerunning with UTF-8 stdout succeeded. Poppler emitted `No display font for 'Symbol'` and `No display font for 'ArialUnicode'` warnings, returned exit 0 and produced all pages; inspected mathematical operators, relationship marks and text rendered correctly. These warnings are retained here rather than relabeled as a warning-free run.

## Checks and visual QA

The builder checks all fourteen actual AI questions against saved JSON, backend totals 163/4/1 and GUI totals 21/1 against Track A JSON, seven entity identities/six relationship cardinalities, application snapshot consistency, required names/page counts and report overflow. It is deliberately a small renderer for the Markdown constructs in this source, not a general Markdown engine.

All twelve report PNGs were individually viewed at full render size, and the poster was viewed at 1920 x 1080. Final-page observations:

| Page | Content | Observed layout |
|---|---|---|
| 1 | Context, team, schema rationale, stock formulas/example | Clear text and table; no overlap or missing glyphs |
| 2 | Transactions, constraints, images, Loss & Surplus, policies | Wrapped table/paragraphs fit; footer clear |
| 3 | Expected/actual tests, failures and proposed fixes | Corrected long slash-separated row label; final words wrap cleanly |
| 4 | Fourteen exact AI questions and run history | All 14 rows present, readable, within margins |
| 5 | Limits, source references and review dependencies | No clipped paths; source links visible; footer clear |
| 6 | Full conceptual ER | Original vector labels/cardinalities/rules retained; header/footer separate |
| 7 | Schema overview | All tables/relationships visible; no cropping |
| 8 | Reference/user schema | Keys, types, constraints and connectors readable |
| 9 | Production/stock schema | Status ENUM and BLOB/movement details visible |
| 10 | Request/receipt schema | Receipt checks and history columns readable |
| 11 | Unit/actor FK sheet | Connector endpoints/labels clear |
| 12 | View formulas | Sigma/join/comparison symbols and formulas visible |
| Poster | 16:9 overview and core ER | Initial connector labels were clipped by node boxes; widened gaps and corrected label placement. Final review has readable core labels, visible draft/failure note, no clipping/overlap |

This is visual export QA, not a projector-room trial or an accessibility certification. Review the diagram abbreviation and 12-page format with Abd Alrahman. The team still needs a three-minute poster rehearsal plus twelve-minute live demo/questions, with request before allocation before delivery. See the existing demo runbook.

## Package gate

Do not build a candidate ZIP yet. Required inputs: reviewed report/poster and Track A artifacts; decisions on F-01/F-05/F-06 and status/correction/surplus policies; resolution of image attribution; decision on including Track A test sources; configured disposable environment for fresh-extraction runtime checks. No manifest or ZIP is claimed complete. Final packaging must exclude `.env`, `.git`, `.venv`, `.local`, logs/caches, archives, skills, previews and the ZIP itself, include runnable root/app paths, and record SHA-256 for every member. Only Abd Alrahman records acceptance; no course submission is performed here.

Git export preservation: this PC has an `astextplain` PDF diff attribute, and the first staged check treated PDF content as text and warned about CRLF conversion. `submission/.gitattributes` now marks only submission PDFs binary; staged bytes were compared directly with the verified output files before committing. Do not normalize line endings inside PDFs.
