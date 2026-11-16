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
| Git sharing | Remote `origin` configured for https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem.git; initial snapshot prepared for publication on `main`. Check Git for live synchronization state |
| Final diagrams, technical PDF, poster PDF and new candidate ZIP | Not present at handoff creation |

## Remaining tasks

Assignments below are suggestions until a teammate claims them. **Owner is Unclaimed until confirmed**; suggested names do not imply work was performed.

| ID | Task / completion evidence | Suggested lead | Owner | Status | Dependency / review note |
|---|---|---|---|---|---|
| ADMIN-01 | Confirm three-member registration, booked slot, location and attendance | Abd Alrahman / all | Unclaimed | Not started | Human external confirmation; November 16 deadline passed; no agent booking |
| GIT-01 | Publish initial project snapshot to supplied GitHub remote | Abd Alrahman / Codex | Codex (authorized by Abd Alrahman) | In progress | Remote configured and empty; credential scan passed; verify origin/main after push |
| DB-01 | Conceptual ER `.drawio` + SVG/PDF with justified cardinalities/rules | Ali / Track A | Unclaimed | Not started | Source: proposal + actual DDL; reviewer must inspect |
| DB-02 | Separate relational schema `.drawio` + SVG/PDF with all columns/types/keys/constraints | Ali / Track A | Unclaimed | Not started | Actual 15-table/two-view model; no schema invention |
| DB-03 | Database-design explanation and policy/findings decision list | Ali / Track A | Unclaimed | Not started | Document existing semantics; reviewer decides behavior changes |
| TEST-01 | Complete uncovered acceptance cases and expected/actual results | Ali / Track A | Unclaimed | Not started | Disposable runtime; cite prior evidence without claiming personal reruns |
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
