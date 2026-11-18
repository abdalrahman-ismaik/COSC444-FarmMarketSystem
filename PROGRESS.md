# Farm-to-Market progress and review ledger

**Current snapshot: November 17, 2026 · Lab B1.** Start with [teammate handoff](docs/TEAMMATE_HANDOFF.md) and [Claude task prompts](docs/CLAUDE_TASK_PROMPTS.md). This file tracks work/review status; the [rubric](docs/RUBRIC_AND_COVERAGE.md) tracks requirements and dated reports track evidence.

## Status rules

Use **Not started**, **In progress**, **Blocked**, **Ready for review**, **Accepted**, or **Needs revision**. An agent can prepare a deliverable and mark Ready for review; only Abd Alrahman Ismaik marks Accepted. Record the blocker/dependency for Blocked and the reason for Needs revision. Do not report an unfinished test as passed or a proposed responsibility as a completed contribution.

## Existing baseline

| Item | Current evidence/status |
|---|---|
| Organized app, requirements, announcements/full rubric, README, architecture, test plan, theme and demo runbook | Present; see README links. Formal reviewer acceptance not recorded |
| SQL schema and sample population | Implemented: 15 tables, two views; fresh isolated MySQL load observed |
| Existing business-rule suite | 65/65 local pass; [runtime evidence](docs/evidence/VALIDATION.md); not exhaustive |
| Windows GUI/photo persistence | 18 tabs and harvest/image restart checks observed; broader manual flow pending |
| Live Gemini | 14 questions + two GUI checks observed; [AI evidence](docs/evidence/AI_VALIDATION.md) retains initial failures/fixes/limits |
| Git sharing | Initial snapshot published to https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem on `main` (initial commit `e67b94a`). Check Git for subsequent synchronization |
| ER/schema diagrams, technical report, poster and review-candidate ZIP | Present and linked below; awaiting Abd Alrahman’s review |

## Remaining tasks

Assignments below show their current owner and review status. Unclaimed means nobody has confirmed responsibility; a Ready-for-review item is not accepted until Abd Alrahman records that decision.

| ID | Task / completion evidence | Suggested lead | Owner | Status | Dependency / review note |
|---|---|---|---|---|---|
| ADMIN-01 | Confirm three-member registration, booked slot, location and attendance | Abd Alrahman / all | Abd Alrahman / all members | In progress | User confirms all three registered and slot booked for Nov 19, 2026 at 1:30 PM; record venue, confirm sheet entries/attendance, and check whether the Nov 16 deadline affects the group |
| GIT-01 | Publish initial project snapshot to supplied GitHub remote | Abd Alrahman / Codex | Codex (authorized by Abd Alrahman) | Ready for review | Initial commit e67b94a pushed to origin/main; real credentials/runtime excluded; publication is not acceptance of unfinished course deliverables |
| DB-01 | Conceptual ER `.drawio` + SVG/PDF with justified cardinalities/rules | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | Branch `ali/database-diagrams-validation`, PR https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2 (ready for review, reviewer requested). `docs/diagrams/conceptual-er.{drawio,pdf,svg}`; Chen (min,max) notation; rendered and inspected; reviewer decision on notation requested |
| DB-02 | Separate relational schema `.drawio` + SVG/PDF with all columns/types/keys/constraints | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | `docs/diagrams/relational-schema.{drawio,pdf}` + 6 SVGs; machine-checked against information_schema: 851 passed/0 failed, 32/32 FKs drawn |
| DB-03 | Database-design explanation and policy/findings decision list | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | `docs/DATABASE_DESIGN.md`; findings F-01…F-08 and decisions in `docs/reviews/TRACK_A_REVIEW.md`; no code/schema/policy changed |
| TEST-01 | Complete uncovered acceptance cases and expected/actual results | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | Original results retained in `docs/evidence/REMAINING_TEST_RESULTS.md`; follow-up on tested fix source: 173 backend, 22 GUI, 7 assistant/read-only; see `docs/evidence/FIX_VALIDATION.md` |
| DOC-01 | Editable concise technical report + rendered PDF | Mohammad / Track B | Mohammad Arwani / Codex follow-up | Ready for review | `submission/technical-report.pdf`; 12 pages, visually rendered and inspected; historical failures and later fixes separated |
| POSTER-01 | Editable poster + projector-readable PDF, ER included | Mohammad / Track B | Mohammad Arwani / Codex follow-up | Ready for review | `submission/poster.pdf`; 16:9, current tested counts and core ER; room projector rehearsal remains |
| BUILD-01 | Reproducible exports and per-page PDF visual QA | Mohammad / Track B | Mohammad Arwani / Codex follow-up | Ready for review | Hash-verified inputs; rebuilt in fresh extraction; all 12 report pages and poster rendered and inspected; see `docs/BUILD_DOCUMENTS.md` |
| ATTR-01 | Verify exact sample-image source/attribution/license mapping | Mohammad / Track B | Mohammad Arwani | Blocked | Dataset-level attribution/license found; exact original file/version/transform mapping remains unknown; see `docs/IMAGE_ATTRIBUTION.md` |
| REVIEW-01 | Review A/B outputs, resolve reported policy issues, record acceptance/revisions | Abd Alrahman | Abd Alrahman Ismaik | Not started | A/B review notes and actual artifacts |
| DEMO-01 | Full three-person timed rehearsal and cross-topic Q&A | All three | All three members | Not started | Final diagrams/poster, configured demo PC, actual booked slot |
| PACKAGE-01 | Candidate ZIP + manifest, fresh-extraction install/run/document checks | Mohammad / Track B | Codex follow-up (authorized) | Ready for review | `submission/FarmMarketSystem_B1_review_candidate.zip` + `submission/MANIFEST.md`; extracted, dependencies installed, documents rebuilt, 65/65 app suite and 21+22 GUI checks passed on isolated port 3318; not accepted/submitted |

## Contribution and activity log

Append dated factual entries. Include member/agent, task IDs, artifact paths, actual checks and next action. Record individual database contributions explicitly. Do not attribute imported implementation or prior agent testing to a student without evidence.

| Date | Member / agent | Task | Work and evidence | Next action |
|---|---|---|---|---|
| 2026-11-17 | Codex preparation session | Handoff | Added teammate/Claude instructions, task ledger and current evidence links; no student contribution inferred | Teammates claim tasks; Abd Alrahman reviews later outputs |
| 2026-11-17 | Codex, user-authorized publication | GIT-01 | Scanned 184 staged files and archived ZIP for local credentials; published initial commit e67b94a to supplied public remote/main; ignored runtime stayed local | Teammates can clone and claim tracks; reviewer acceptance remains pending |
| 2026-11-17 | Ali Alshamsi with Claude Code agent | DB-01/02/03, TEST-01 | Claimed tasks on branch `ali/database-diagrams-validation` (from origin/main c8fd6cd; PR #1 still open and unmerged). Set up this PC: project `.venv` (Python 3.12.1) and a **separate disposable MySQL 8.0.46** instance (own datadir under ignored `.local/`, 127.0.0.1:3317); the normal MySQL80 service was not used. Ignored `app/.env` points to it; no secrets committed | Build diagrams and evidence |
| 2026-11-17 | Ali Alshamsi with Claude Code agent | DB-01/02 | Generated editable `docs/diagrams/conceptual-er.drawio` and 6-page `relational-schema.drawio`; exported PDF/SVG with draw.io 32.4.1; rendered every PDF page (PyMuPDF) and SVG (headless Edge) and fixed clipping/crossings; `check_diagrams_vs_sql.py` 851 passed / 0 failed, 32/32 FKs, mutation test 3/3 detected | Reviewer inspects diagrams |
| 2026-11-17 | Ali Alshamsi with Claude Code agent | TEST-01 | Reran existing suite on fresh seed: **65/65**. New guarded scripts `app/tests/track_a_remaining_checks.py` (run 1: 162 Pass/5 Fail/1 Info incl. SRCH-02a oracle error, preserved; run 2: **163 Pass/4 Fail/1 Info**) and `app/tests/track_a_gui_flow.py` (final run **21 Pass/1 Fail**, incl. new-process photo restart). Findings: **F-01 High** concurrent oversell (19/20 trials; READ COMMITTED simulation 0/20), F-05 allocate pre-fill `1,500`, F-06 truncated JPEG accepted, F-02/03/04/08 policies, F-07 scaling. No app code/schema/seed changed | Reviewer decisions in TRACK_A_REVIEW.md |
| 2026-11-17 | Ali Alshamsi with Claude Code agent | DB-01/02/03, TEST-01 | Committed c30a18c and pushed `ali/database-diagrams-validation`; opened https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2 targeting `main` (not draft) and requested review from `abdalrahman-ismaik`. PR #1 remains open/unmerged; its PR-register table should record this PR once merged. Nothing merged or accepted by Track A | Await review comments; address via new commits on the same branch |

## Track B claim on 2026-11-17

Mohammad Arwani, working with Codex, claims DOC-01, POSTER-01, BUILD-01, ATTR-01 and PACKAGE-01 on `mohammad/report-poster`. Fetch completed; branch and working tree were clean at `c8fd6cd`. PR #1 remains open/unmerged; the session explicitly authorizes scoped commits, pushes and PR creation. Track A ownership and Ready-for-review outputs are recorded on PR #2 (`80529fb`); the old unclaimed Track A rows above are this branch's baseline, not a new claim. Preserve that owner's artifacts. Draft report/poster will use pinned real Track A inputs and cite its failures. PACKAGE-01 is blocked until artifact review dependencies are satisfied. No application tests or resets run for this claim.

## Initial Track B delivery observations on 2026-11-17 (at PR #3 submission)

| Member / agent | Task IDs | Files and actual observations | Remaining work |
|---|---|---|---|
| Mohammad Arwani / Codex | DOC-01, POSTER-01, BUILD-01 | docs/report/technical-report.md; docs/poster/poster.json; docs/report/build_documents.py and requirements-docs.txt; submission/technical-report.pdf (12 pages) and poster.pdf (1 page); docs/BUILD_DOCUMENTS.md; build-validation.json. Bundled Python 3.12.14/ReportLab 4.4.9/pypdf 6.21.4/Pillow 13.0.0 on Windows 11; Poppler 26.07.0 rendered all pages. All 13 pages viewed; initial label defects fixed and affected pages rechecked. Two builds have identical hashes. Fourteen actual AI questions and Track A result totals retained; 7 ER nodes/6 relationships checked; application snapshot unchanged. No application/DB/Gemini tests rerun. | Review draft outputs; PR #2 unmerged; final decisions and demo-machine rehearsal pending |
| Mohammad Arwani / Codex | ATTR-01 | docs/IMAGE_ATTRIBUTION.md: 4/4 external JPEGs and 12/12 SQL BLOB tuples match archive; dimensions/SHA-256s/empty EXIF observed. Verified upstream dataset-level credit/license, not exact source mappings. | Recover version/source-file/transformations or reviewer-authorized replacement plan |
| Mohammad Arwani / Codex | PACKAGE-01 | submission/README.md records gate. No candidate ZIP or MANIFEST produced; no fresh-extraction/runtime check claimed. | Artifact review, bug/policy/attribution decisions and disposable runtime |

Database contribution in this pass: documented movement formulas, transaction/constraint boundaries and the receipt-normalization qualification; checked poster cardinalities against Ali's actual Draw.io source. No authorship of imported SQL/application implementation is inferred.

Branch: `mohammad/report-poster`. PR: https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/3 (draft, targets main). GitHub confirmed `abdalrahman-ismaik` as requested reviewer. Review note: [TRACK_B_REVIEW.md](docs/reviews/TRACK_B_REVIEW.md). Only Abd Alrahman records Accepted.

2026-11-17 publication evidence: scoped commit `686b297` pushed to `origin/mohammad/report-poster`; draft PR #3 opened with TRACK_B_REVIEW as its body, and reviewer request succeeded. First connector attempt returned 403 (integration access); existing Git authentication completed the authorized API operation. Staged checks passed after a scoped PDF binary attribute prevented text/CRLF handling; both staged PDF byte sequences equal the visually checked exports. No main push, force-push, merge, acceptance or course submission.

## Reviewer decisions

No acceptance decisions recorded yet. Reviewer-only approval remains Abd Alrahman’s responsibility.

| Date | Reviewer | Task / artifact version | Decision and reason |
|---|---|---|---|
| — | — | — | Pending |

## Session handoff template

```text
Date / member / agent:
Assigned task IDs and status:
Files created/changed:
Actual commands/tests/visual checks and results:
Database environment/reset target (no credentials):
Requirements covered and evidence links:
Blocked dependencies / exact reviewer decisions needed:
Remaining work and next action:
Ready-for-review artifact paths:
```

## Correctness follow-up (user-approved plan, November 17)

- Branch: `fix/stock-integrity-validation`, based on Ali's PR #2; PR [#4](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/4) (base: Ali's branch).
- Owner: Codex, authorized by Abd Alrahman; status **Ready for review**, not Accepted.
- Implemented F-01 isolation/lock ordering, F-05 numeric prefill, F-06 decode validation; failure-sensitive test exits/output and bounded concurrency; qualified normalization.
- Policy decision: preserve allocation-settlement DELIVERED and one-receipt/shortfall-as-loss, with GUI explanation.
- Observed: 65/65 original, 173/173 expanded backend, 22/22 GUI, 3 validation-support, 7 assistant/read-only and 851 diagram checks. See [FIX_VALIDATION](docs/evidence/FIX_VALIDATION.md).
- Teammate baseline evidence and contributions remain intact. No PR merge or final artifact acceptance is claimed.


## Integrated review-candidate follow-up (2026-11-17)

- Branch `docs/reviewed-submission`; [PR #5](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/5), based on `mohammad/report-poster`; Ready for review, not merged. PRs #2–#4 and `main` remain unchanged.

- Local branch `docs/reviewed-submission` integrates the Track B report/poster with Ali’s diagrams and Codex’s integrity fixes while preserving the original teammate branches and evidence. The single `PROGRESS.md` merge conflict was resolved by retaining both contribution histories and adding the later follow-up.
- Report builder now consumes checked-in, SHA-256-verified inputs and works from a fresh extraction without fetching unmerged Git objects. Latest exports: 12-page report (`38b99e1d…`) and one-page poster (`7927f1f3…`); all rendered pages and the 1920×1080 poster were visually inspected.
- Candidate archive: `submission/FarmMarketSystem_B1_review_candidate.zip` (116 members); external and embedded manifests list member hashes; ZIP SHA-256 is recorded in `submission/MANIFEST.md`. Fresh extraction verified paths/hashes, installed current app/document dependencies, loaded seed only into isolated MySQL 8.0.46 port 3318, passed 65/65 original tests and GUI flow 21/21 + restart 22/22, and rebuilt both PDFs identically. Existing demo ports were not targeted.
- Status is Ready for review, not Accepted. Exact image provenance, human review, projector test, timed three-person rehearsal, registration/slot confirmation, and final course upload remain. No merge or course submission is claimed.
