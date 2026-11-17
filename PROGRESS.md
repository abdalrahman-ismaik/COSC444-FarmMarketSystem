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
| Final diagrams, technical PDF, poster PDF and new candidate ZIP | Not present at handoff creation |

## Remaining tasks

Assignments below are suggestions until a teammate claims them. **Owner is Unclaimed until confirmed**; suggested names do not imply work was performed.

| ID | Task / completion evidence | Suggested lead | Owner | Status | Dependency / review note |
|---|---|---|---|---|---|
| ADMIN-01 | Confirm three-member registration, booked slot, location and attendance | Abd Alrahman / all | Unclaimed | Not started | Human external confirmation; November 16 deadline passed; no agent booking |
| GIT-01 | Publish initial project snapshot to supplied GitHub remote | Abd Alrahman / Codex | Codex (authorized by Abd Alrahman) | Ready for review | Initial commit e67b94a pushed to origin/main; real credentials/runtime excluded; publication is not acceptance of unfinished course deliverables |
| DB-01 | Conceptual ER `.drawio` + SVG/PDF with justified cardinalities/rules | Ali / Track A | Unclaimed | Not started | Source: proposal + actual DDL; reviewer must inspect |
| DB-02 | Separate relational schema `.drawio` + SVG/PDF with all columns/types/keys/constraints | Ali / Track A | Unclaimed | Not started | Actual 15-table/two-view model; no schema invention |
| DB-03 | Database-design explanation and policy/findings decision list | Ali / Track A | Unclaimed | Not started | Document existing semantics; reviewer decides behavior changes |
| TEST-01 | Complete uncovered acceptance cases and expected/actual results | Ali / Track A | Unclaimed | Not started | Disposable runtime; cite prior evidence without claiming personal reruns |
| DOC-01 | Editable concise technical report + final rendered PDF | Mohammad / Track B | Mohammad Arwani / Codex | Ready for review | Review draft PDF/source complete; 12 pages incl. seven pinned Track A diagram sheets. Final depends on PR #2 and policy/fix decisions; see docs/reviews/TRACK_B_REVIEW.md |
| POSTER-01 | Editable poster + projector-readable PDF, ER included | Mohammad / Track B | Mohammad Arwani / Codex | Ready for review | Review draft PDF + editable JSON; 16:9, core ER checked against Track A. Final/projector rehearsal pending reviewer decisions |
| BUILD-01 | Document reproducible exports and per-page PDF visual QA | Mohammad / Track B | Mohammad Arwani / Codex | Ready for review | Reproducible builder + exact commands/versions; all 13 PDF pages inspected; two builds identical; docs/BUILD_DOCUMENTS.md |
| ATTR-01 | Verify exact sample-image source/attribution/license mapping | Mohammad / Track B | Mohammad Arwani / Codex | Ready for review | Audit and 16-asset hashes complete; dataset/license verified; exact source/version/transformation mapping unresolved; reviewer decision required |
| REVIEW-01 | Review A/B outputs, resolve reported policy issues, record acceptance/revisions | Abd Alrahman | Unclaimed | Not started | A/B review notes and actual artifacts |
| DEMO-01 | Full three-person timed rehearsal and cross-topic Q&A | All three | Unclaimed | Not started | Final diagrams/poster, configured demo PC, actual booked slot |
| PACKAGE-01 | Candidate ZIP + manifest, fresh-extraction install/run/document checks | Mohammad / Track B | Mohammad Arwani / Codex | Blocked | Awaiting artifact review, Track A decisions and attribution resolution; no ZIP/manifest/fresh-extraction run yet |

## Contribution and activity log

Append dated factual entries. Include member/agent, task IDs, artifact paths, actual checks and next action. Record individual database contributions explicitly. Do not attribute imported implementation or prior agent testing to a student without evidence.

| Date | Member / agent | Task | Work and evidence | Next action |
|---|---|---|---|---|
| 2026-11-17 | Codex preparation session | Handoff | Added teammate/Claude instructions, task ledger and current evidence links; no student contribution inferred | Teammates claim tasks; Abd Alrahman reviews later outputs |
| 2026-11-17 | Codex, user-authorized publication | GIT-01 | Scanned 184 staged files and archived ZIP for local credentials; published initial commit e67b94a to supplied public remote/main; ignored runtime stayed local | Teammates can clone and claim tracks; reviewer acceptance remains pending |

## Reviewer decisions

No acceptance decisions recorded yet.

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

## Track B claim on 2026-11-17

Mohammad Arwani, working with Codex, claims DOC-01, POSTER-01, BUILD-01, ATTR-01 and PACKAGE-01 on `mohammad/report-poster`. Fetch completed; branch and working tree were clean at `c8fd6cd`. PR #1 remains open/unmerged; the session explicitly authorizes scoped commits, pushes and PR creation. Track A ownership and Ready-for-review outputs are recorded on PR #2 (`80529fb`); the old unclaimed Track A rows above are this branch's baseline, not a new claim. Preserve that owner's artifacts. Draft report/poster will use pinned real Track A inputs and cite its failures. PACKAGE-01 is blocked until artifact review dependencies are satisfied. No application tests or resets run for this claim.

## Track B delivery observations on 2026-11-17

| Member / agent | Task IDs | Files and actual observations | Remaining work |
|---|---|---|---|
| Mohammad Arwani / Codex | DOC-01, POSTER-01, BUILD-01 | docs/report/technical-report.md; docs/poster/poster.json; docs/report/build_documents.py and requirements-docs.txt; submission/technical-report.pdf (12 pages) and poster.pdf (1 page); docs/BUILD_DOCUMENTS.md; build-validation.json. Bundled Python 3.12.14/ReportLab 4.4.9/pypdf 6.21.4/Pillow 13.0.0 on Windows 11; Poppler 26.07.0 rendered all pages. All 13 pages viewed; initial label defects fixed and affected pages rechecked. Two builds have identical hashes. Fourteen actual AI questions and Track A result totals retained; 7 ER nodes/6 relationships checked; application snapshot unchanged. No application/DB/Gemini tests rerun. | Review draft outputs; PR #2 unmerged; final decisions and demo-machine rehearsal pending |
| Mohammad Arwani / Codex | ATTR-01 | docs/IMAGE_ATTRIBUTION.md: 4/4 external JPEGs and 12/12 SQL BLOB tuples match archive; dimensions/SHA-256s/empty EXIF observed. Verified upstream dataset-level credit/license, not exact source mappings. | Recover version/source-file/transformations or reviewer-authorized replacement plan |
| Mohammad Arwani / Codex | PACKAGE-01 | submission/README.md records gate. No candidate ZIP or MANIFEST produced; no fresh-extraction/runtime check claimed. | Artifact review, bug/policy/attribution decisions and disposable runtime |

Database contribution in this pass: documented movement formulas, transaction/constraint boundaries and the receipt-normalization qualification; checked poster cardinalities against Ali's actual Draw.io source. No authorship of imported SQL/application implementation is inferred.

Branch: `mohammad/report-poster`. PR: https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/3 (draft, targets main). GitHub confirmed `abdalrahman-ismaik` as requested reviewer. Review note: [TRACK_B_REVIEW.md](docs/reviews/TRACK_B_REVIEW.md). Only Abd Alrahman records Accepted.

2026-11-17 publication evidence: scoped commit `686b297` pushed to `origin/mohammad/report-poster`; draft PR #3 opened with TRACK_B_REVIEW as its body, and reviewer request succeeded. First connector attempt returned 403 (integration access); existing Git authentication completed the authorized API operation. Staged checks passed after a scoped PDF binary attribute prevented text/CRLF handling; both staged PDF byte sequences equal the visually checked exports. No main push, force-push, merge, acceptance or course submission.
