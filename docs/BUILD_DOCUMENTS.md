# Build the final report and submission package

The final report source is [report/latex/farm-to-market-report.tex](report/latex/farm-to-market-report.tex). It uses the KU navy/gold theme, eight GUI screenshots, original five conceptual ER sheets, three relational schema sheets and the approved poster as fitted figures on A4 pages.

## Final LaTeX report

Install MiKTeX or TeX Live with the packages listed in the preamble. From the repository root:

```powershell
Set-Location docs/report/latex
pdflatex -interaction=nonstopmode -halt-on-error farm-to-market-report.tex
pdflatex -interaction=nonstopmode -halt-on-error farm-to-market-report.tex
Copy-Item farm-to-market-report.pdf ../../../submission/FarmMarketSystem_B1_Technical_Report.pdf
Set-Location ../../..
python scripts/build_report_bundle.py
```

Run pdfLaTeX again if references request it. Overleaf users can upload the complete source ZIP and select `farm-to-market-report.tex`. The bundle builder packages the source, README, used assets and final PDF and verifies CRC and payload equality. It does not compile LaTeX or connect to MySQL.

Install Poppler for visual review:

```powershell
pdftoppm -scale-to 1500 -png submission/FarmMarketSystem_B1_Technical_Report.pdf .local/report-review
```

Inspect every page after content or layout changes. Latest layout/provenance checks are recorded in [report/latex/validation.json](report/latex/validation.json); these are document checks, not fresh application tests.

## Application package

```powershell
python scripts/build_candidate.py --verify-dir .local/fresh-submission-extraction
```

Choose a new extraction directory each time. This builds `submission/FarmMarketSystem_B1_Submission.zip`, writes `submission/MANIFEST.md`, and verifies member hashes and exclusions after extraction. Its 25 members contain the maintained app, SQL, sample images, setup/run scripts, README and approved poster. The technical report and its source ZIP remain separate deliverables. No database reset or runtime suite is performed.

## Preserved sources

- Approved poster: `submission/COSC444_Farm-to-market_Poster.pdf`; editable supplied PowerPoint: `docs/poster/approved-poster.pptx`. The old JSON poster layout is a historical preview.
- Diagram sources/exports: `docs/diagrams/`. The report embeds unchanged copies of the original PDF sheets.
- Previous 13-page report: `docs/report/history/technical-report-2026-11-19.pdf`.
- Legacy Markdown/report builder and historical hash manifests remain under `docs/report/`. They do not generate the final LaTeX report. Their historical output name `submission/technical-report.pdf` must not be confused with the final named PDF.
- Original dated application/assistant verification remains under `docs/evidence/`. Building documents does not rerun those checks or turn historical outcomes into current results.
