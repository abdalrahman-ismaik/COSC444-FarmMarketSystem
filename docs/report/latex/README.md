# Farm-to-Market LaTeX report

Edit `farm-to-market-report.tex` and keep the `figures` folder alongside it. This version retains the fuller report and original five conceptual ER sheets plus three relational schema sheets. All eight sheets are now captioned vector figures on standard A4 report pages, matching the poster's embedded presentation. The supplied instructor/title information, fitted TikZ drawings, operational-overview PNG and poster remain included.

## Compile

Use MiKTeX, TeX Live or Overleaf with pdfLaTeX and the packages in the preamble, including TikZ. Run from this folder:

```text
pdflatex -interaction=nonstopmode -halt-on-error farm-to-market-report.tex
pdflatex -interaction=nonstopmode -halt-on-error farm-to-market-report.tex
```

Run again if contents or references request it. On Overleaf upload the entire source bundle and select `farm-to-market-report.tex` as the main document. No Python or database access is required.

## Assets and editorial decisions

- `figures/conceptual-er.pdf`: five original sheets, unchanged from the repository export.
- `figures/relational-schema.pdf`: three original sheets, unchanged from the repository export.
- `figures/operational-overview.png`: user-supplied image, embedded unchanged. Its receipt link is simplified; the surrounding text clarifies zero-or-one receipt per allocation.
- `figures/poster.pdf`: approved poster, embedded as an ordinary captioned figure. Its five-day example is configurable; the application default is three days.

Workflow and architecture drawings are editable TikZ in the main `.tex`. The full schema tables, rules, stock example, transactions and dated test outcomes are restored. Assistant validation is summarized as requested in the supplied revision; complete question logs remain in project evidence. The report contains no tool-authorship mentions. Report metadata and instructor details follow the user-supplied title page.

The latest layout removes long dashes, lists only lab instructor names as bullets, and routes the supply arrow and label above the Figure 1.1 boxes. Original vector diagram content remains intact and supports zooming. All pages use the same A4 portrait dimensions.

The GUI chapter contains eight captioned screenshots across five pages, covering user selection, harvest/stock, allocation, produce search, delivery receipts, Loss & Surplus, the assistant and administrator Users. Preserved operational captures are dated November 16-17; the administrator view was captured November 19 using read-only MySQL sessions. `figures/gui/sources.json` records their provenance. Screenshot values describe their capture date. Asset files are included unchanged in the source ZIP.

Chapter 1 also documents every one of the 25 members in `submission/FarmMarketSystem_B1_Submission.zip`, the six third-party packages, Tkinter/MySQL requirements, cooperation between GUI/database/image/assistant layers and setup on another machine. The application archive contains dependency declarations, not bundled Python packages or MySQL. This PDF and its source bundle remain separate from that application archive.

At the user's request, the course report presents current system behavior and selected expected/actual evidence without development chronology, old defect descriptions or an internal open-work checklist. The user confirmed the donation policy is approved. That approval is recorded as policy status; no new donation test result is asserted. Original dated verification records remain preserved separately.

Final delivery names: `submission/FarmMarketSystem_B1_Technical_Report.pdf` and `submission/FarmMarketSystem_B1_Technical_Report_Source.zip`. The previous report is preserved under `docs/report/history/`. Run `python scripts/build_report_bundle.py` from the repository root after copying the compiled PDF to the final path. The application ZIP remains a separate deliverable. See `docs/BUILD_DOCUMENTS.md` for the complete workflow. Application/database/model regression suites were not rerun for this document build.
