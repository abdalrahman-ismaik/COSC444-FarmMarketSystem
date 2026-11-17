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
| DB-01 | Conceptual ER `.drawio` + SVG/PDF with justified cardinalities/rules | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | Branch `ali/database-diagrams-validation`, PR https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2 (ready for review, reviewer requested). `docs/diagrams/conceptual-er.{drawio,pdf,svg}`; Chen (min,max) notation; rendered and inspected; reviewer decision on notation requested |
| DB-02 | Separate relational schema `.drawio` + SVG/PDF with all columns/types/keys/constraints | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | `docs/diagrams/relational-schema.{drawio,pdf}` + 6 SVGs; machine-checked against information_schema: 851 passed/0 failed, 32/32 FKs drawn |
| DB-03 | Database-design explanation and policy/findings decision list | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | `docs/DATABASE_DESIGN.md`; findings F-01…F-08 and decisions in `docs/reviews/TRACK_A_REVIEW.md`; no code/schema/policy changed |
| TEST-01 | Complete uncovered acceptance cases and expected/actual results | Ali / Track A | Ali Alshamsi (Claude Code agent) | Ready for review | `docs/evidence/REMAINING_TEST_RESULTS.md`: backend 163 Pass/4 Fail (F-01 concurrent oversell)/1 Info; GUI 21 Pass/1 Fail (F-05); AI checks Blocked here (no key) |
| DOC-01 | Editable concise technical report + final rendered PDF | Mohammad / Track B | Unclaimed | Not started | Draft now; final requires DB-01/02/03 and TEST-01 |
| POSTER-01 | Editable poster + projector-readable PDF, ER included | Mohammad / Track B | Unclaimed | Not started | Draft now; final requires DB-01 and current feature truth |
| BUILD-01 | Document reproducible exports and per-page PDF visual QA | Mohammad / Track B | Unclaimed | Not started | DOC-01 and POSTER-01 outputs; keep doc dependencies separate |
| ATTR-01 | Verify exact sample-image source/attribution/license mapping | Mohammad / Track B | Unclaimed | Not started | Existing Fruits-360/CC BY-SA claim incomplete; do not invent source URLs |
| REVIEW-01 | Review A/B outputs, resolve reported policy issues, record acceptance/revisions | Abd Alrahman | Unclaimed | Not started | A/B review notes and actual artifacts |
| DEMO-01 | Full three-person timed rehearsal and cross-topic Q&A | All three | Unclaimed | Not started | Final diagrams/poster, configured demo PC, actual booked slot |
| PACKAGE-01 | Candidate ZIP + manifest, fresh-extraction install/run/document checks | Mohammad / Track B | Unclaimed | Not started | Reviewed report/poster/diagrams/evidence; never label submitted |

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
