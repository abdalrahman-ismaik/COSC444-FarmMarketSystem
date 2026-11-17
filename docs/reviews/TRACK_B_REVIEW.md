# Track B review - report, poster and reproducible exports

**Owner:** Mohammad Arwani (100064908), with Codex. **Date:** 17 November 2026. **Branch:** `mohammad/report-poster`. **Reviewer:** @abdalrahman-ismaik.

**PR:** https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/3. **Status:** draft PR; produced artifacts are Ready for review, not Accepted. Final exports/package remain dependent on Track A review and decisions below.

The assessed technical/poster PDFs were missing. This change supplies a 12-page technical report, a one-page 16:9 poster, editable sources, reproducible exports and an attribution audit. The report incorporates the real Track A diagrams and expected/actual findings, including failures, with provenance pinned to `80529fbfddf58b58735963f6a35847e22dedeadc` from [PR #2](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2). Earlier test observations are cited as team evidence, not rerun by Mohammad.

No application, SQL, business-policy or Track A file is changed. PR #1 was checked and remains open/unmerged; the user's explicit session instruction authorizes this feature-branch workflow. Neither PR was merged.

## Artifacts and editable sources

| Task | Artifact | State |
|---|---|---|
| DOC-01 | [Technical report PDF](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/submission/technical-report.pdf); [Markdown source](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/report/technical-report.md) | Ready for review as draft; five narrative/evidence pages plus seven full-size vector diagram sheets |
| POSTER-01 | [Poster PDF](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/submission/poster.pdf); [editable JSON](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/poster/poster.json) | Ready for review as draft; green/white 1920 x 1080 landscape |
| BUILD-01 | [Build guide and page QA](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/BUILD_DOCUMENTS.md); [builder](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/report/build_documents.py); [versions](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/report/requirements-docs.txt); [observed build record](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/report/build-validation.json) | Ready for review; two consecutive builds produced identical PDF SHA-256s |
| ATTR-01 | [Image audit and 16-asset hash register](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/docs/IMAGE_ATTRIBUTION.md) | Audit Ready for review; exact upstream mapping remains blocked |
| PACKAGE-01 | [Submission status](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/blob/mohammad/report-poster/submission/README.md) | Blocked: no candidate ZIP/manifest created before review dependencies |

The poster is a labeled presentation view derived from Track A's real conceptual ER: seven core entities, six relationships, and cardinalities mechanically checked against the `.drawio` XML. The full conceptual ER and all six schema sheets remain in the technical report. Track A's tracked sources are not copied or overwritten; the builder extracts pinned inputs to ignored output. Please confirm this abbreviated poster view is suitable for the three-minute overview.

## Requirements and rubric addressed

| Scope | Requirements | Evidence in this change |
|---|---|---|
| Technical documentation/test evidence (15 points) | P5-01/02/03/04/05 | Report rules, transaction table, expected/actual tests and all fourteen actual AI questions; preserved initial failures, corrected oracle and segmented reruns; setup README retained |
| Group poster/demo (5 points) | P5-07 and supplied poster requirements | Context, roles, system/workflow, key rules, core GUI/BLOB/AI, Loss & Surplus and real-model ER; all names/IDs/B1 |
| Database design (10), implementation (15) | P1-01/02/03/04 | Full pinned diagrams, design rationale, counts and constraint evidence cited from Track A; no marks claimed |
| GUI (10), backend (10), assistant (10), feature (10), errors (5) | P2, Phase 3 Loss & Surplus, P4, BR-01 through BR-09 | Accurate behavior and evidence descriptions with unresolved defects, not new implementation or blanket acceptance |
| Individual demo/Q&A (10) | Every member understands and attends | Still requires real participation/rehearsal; no completion or contribution invented |
| Candidate package | P5-06 | Explicit gate documented; package absent until required review |

The ten rubric categories total 100. This mapping describes documentation coverage, not earned marks.

## Rebuild and actual verification

From a Git clone with Python 3.12 and document-only dependencies:

```powershell
git fetch origin ali/database-diagrams-validation
python -m pip install -r docs/report/requirements-docs.txt
python docs/report/build_documents.py
pdftoppm -r 110 -png submission/technical-report.pdf output/documents/report
pdftoppm -scale-to 1920 -png -singlefile submission/poster.pdf output/documents/poster
```

Use a separate docs environment as shown in BUILD_DOCUMENTS; do not alter application requirements. Actual host: Windows 11 10.0.26200, bundled Python 3.12.14, ReportLab 4.4.9, pypdf 6.21.4, Pillow 13.0.0, Poppler 26.07.0. A fresh dependency installation was not tested; installed bundled packages were used.

Observed locally on 17 November:

- Build succeeded: **12 report pages, 1 poster page**; both PDFs reopened and contain team identities. Two consecutive builds have identical SHA-256s.
- **All 12 report pages and the poster were rendered and individually inspected.** Fixed the poster's clipped connector labels and the report's awkward long row label, rebuilt and reinspected affected pages. Final no clipping/overlap/missing glyphs observed. Poppler's Symbol/ArialUnicode font warnings are documented; the relevant rendered symbols were checked.
- Static checks preserve **14 exact AI questions**, Track A backend **163 Pass / 4 Fail / 1 Info**, GUI **21 Pass / 1 Fail**, seven core ER entities/six relationships, and the original application snapshot. Python AST parse and working-tree `git diff --check` passed. The first staged check exposed a PDF text-diff/CRLF setting; a scoped `submission/.gitattributes` binary rule fixes it, and the staged whitespace check passed with PDF bytes identical to the outputs.
- Local image audit: **4/4 external JPEGs and 12/12 SQL BLOB tuples match the original archive**; SHA-256/dimensions recorded, no EXIF keys. Upstream dataset-level attribution/license verified; exact local source version/file mapping unknown.
- No database setup, mutating tests, live GUI or Gemini runs were executed by Track B. No `.env` was read/overwritten. No new application-runtime or fresh-extraction claim is made.

Earlier results cited: original 65/65, 18 tabs and photo restart; fourteen live Gemini cases/two GUI AI checks; Track A's 65-check rerun, diagram check and newer backend/GUI results. See report references R4-R6 for environments and limits.

## Dependencies and decisions for Abd Alrahman

1. Review Track A PR #2 and authorize resolution of **F-01 concurrent overselling**; decide on the small F-05 quantity-prefill and F-06 JPEG-decode fixes and require their stated retests. Track B did not change implementation.
2. Decide whether to retain allocation-based DELIVERED, one-receipt/shortfall-as-loss, reason-based farmer correction and currently-unallocated surplus wording. Donation of expired lots is also current behavior without a defined suitability policy.
3. Review the report's normalization qualification: storing discrepancy = allocated - received means the blanket “all tables BCNF” claim in Track A needs qualification. This is a documentation finding, not a schema-change request.
4. Confirm the **12-page mixed-size report** (five narrative pages plus seven unshrunk diagram sheets) and the poster's checked **core ER presentation view**. The 6-10-page target was guidance, not an instructor limit. Actual projector readability and timed rehearsal remain untested.
5. Supply/recover exact upstream image mappings and transformations, or authorize a documented replacement plan. Do not treat dataset-level license verification as a per-file provenance match.
6. After artifact review, decide whether Track A's guarded test sources belong in the candidate ZIP. Then perform fresh-extraction checks with a confirmed disposable DB and demo-PC AI credentials. PACKAGE-01 stays Blocked until then.
7. Human team members confirm registration, actual booking/location and attendance, and rehearse the existing request-before-allocation-before-delivery sequence within 3 + 12 minutes. No newer eLearn announcements, registration or bookings were checked or performed here.

Only Abd Alrahman records acceptance and decides merging. No course submission, merge, force-push or direct main push is part of this work.

PR delivery: draft PR #3 is open against main; GitHub confirmed `abdalrahman-ismaik` in requested reviewers. Commit `686b297` contains the artifacts. The connector returned 403 for PR creation; the authorized request succeeded using the existing Git authentication without exposing credentials. This note is the PR description source.
