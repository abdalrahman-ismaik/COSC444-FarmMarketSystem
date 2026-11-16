# Detailed rubric and coverage

Source: the user-supplied **Project demo rubrics** announcement, reproduced in [announcements](ANNOUNCEMENTS.md). The categories total **100 points**. This matrix records evidence, not predicted marks or a completion guarantee.

**Current as of November 17, 2026:** [local validation](evidence/VALIDATION.md) records 65/65 checks on MySQL 8.0.46, 18 Windows role tabs, harvest-form validation and image restart persistence. [Live AI validation](evidence/AI_VALIDATION.md) records fourteen questions with reference SQL, expected/actual results, ambiguity/refusal cases, database-integrity checks and two live GUI checks, including initial failures/fixes and segmented retests. The matrix below incorporates this evidence; it is not an initial untested snapshot. Use [PROGRESS.md](../PROGRESS.md) for ownership/review status and the [handoff](TEAMMATE_HANDOFF.md) for artifact contracts.

## Evidence labels

- **Implemented:** relevant source/SQL exists.
- **Statically reviewed:** implementation or seed statements were inspected without executing the live workflow.
- **Historically reported:** the original guide or supplied development narrative reports an outcome; not a fresh local test.
- **Locally tested:** a check was actually executed in this workspace; see [repository review](REPOSITORY_REVIEW.md) for exact results and limits.
- **Missing / pending:** required artifact or current verification is not present.

## Assessment matrix

| Criterion | Points | Full-grade expectations | Existing implementation/evidence | Remaining acceptance work |
|---|---:|---|---|---|
| ER diagram and relational schema | 10 | Justified entities, relationships, cardinalities, and farm/cycle/lot/request/allocation/delivery rules; separate relational schema with PK/FK, types, and constraints | SQL and narrative architecture statically reviewed | **Missing:** Draw.io conceptual ER source/export and separate schema diagram; validate against actual SQL |
| Implementation and population | 15 | Executable creation/population SQL; at least 3 farms, 4 markets, 5 crops, 8 cycles, 12 lots, 15 movements, 8 requests, 6 receipts; available/reserved/partial/lost/discrepant examples and images; suitable constraints | SQL statically has 4/4/6/10/13/38/9/6 respectively and 12 image records; clean isolated MySQL 8.0.46 load observed; stock scenarios exercised by passing suite | Consolidate exact per-table count/constraint evidence, close uncovered boundary cases and verify final submission setup on a fresh machine/extraction |
| Python GUI | 10 | Friendly role workflows for setup, stock, search/requests, allocations, partial delivery/discrepancies; photo upload/retrieval after restart | 18 role tabs, valid/invalid harvest form, buyer photo and uploaded BLOB retrieval in a separate GUI process verified; actual screenshots saved | Full GUI request/allocation/partial-delivery path, remaining image/error boundaries, keyboard/focus/display-scaling and manual usability checks |
| Back-end programming and embedded SQL | 10 | Reliable parameterized SQL, sound transactions, integrity, stock/allocation/delivery/discrepancy persistence and ownership | Parameterized values, transactions and locks implemented; 65-check suite passed, including stock/ownership/repeated delivery and one racing-allocation case | Intermediate-failure rollback and broader release/cancel/delivery concurrency; document or resolve status/shortfall/correction policies |
| LangChain assistant | 10 | Accurate validated read-only answers in GUI with supporting records/summaries; clear ambiguity and unsupported handling; no data changes | 14 live questions checked against SQL/expected handling, two live GUI cases, no-write fingerprints and read-only DB rejection evidence; initial filter/model issues corrected with retained evidence | Incorporate existing evidence into technical PDF; verify on demo PC; remaining paraphrase/injection/large-result robustness and validation limitations, not a wholesale repeat of completed questions |
| Advanced feature: at least one | 10 | One Phase 3 option database-backed, in GUI, tested, demonstrated; Loss & Surplus needs thresholds, priority, two disposition actions, valid movements and checks | SQL-backed flags/GUI, adjustable thresholds, donation/disposal/history implemented; suite verifies flags/actions/excess/reserved-stock checks | Complete threshold and priority boundaries, unauthorized/fully reserved cases and GUI disposition evidence not already exercised |
| Error handling and business rules | 5 | Friendly connection/constraint/duplicate/date/crop/unit/empty-result/assistant/image failures; no negative stock or over-allocation; atomic changes, status/movement history, ownership | Validation and friendly mappings implemented; business-rule script covers many cases | Execute remaining boundary/rollback/image/GUI tests; capture actual results without exposing secrets |
| Demo and poster: group | 5 | Fifteen minutes: ~3-minute poster and ~12-minute demo; restart/photo, buyer search/request/partial delivery, over-allocation block, supported and ambiguous/unsupported assistant, advanced feature, friendly invalid input; explain decisions | Corrected Markdown runbook and poster content checklist prepared | **Missing:** poster PDF; fresh timed rehearsal and all scenarios on demo machine |
| Member demo and Q&A: individual | 10 | Strong understanding; on time; within time; clear, confident answers | Three B1 members identified; proposed leads and shared preparation documented | Confirm contributions, all-member attendance, presentation allocation, and cross-topic rehearsal; no individual performance claim yet |
| Technical documentation and test evidence | 15 | Concise technical PDF with diagrams/rules/transactions and expected/actual evidence; major-function valid/invalid/boundary/repeated/concurrent testing, stock/forecast checks, ten assistant questions, images/GUI/feature tests; README setup/run | README/architecture/test plan plus dated local/AI observed results, JSON comparisons and screenshots exist; original guide is supplementary | **Missing:** concise technical PDF, final diagrams and completion of remaining acceptance cases; consolidate existing live/local evidence accurately rather than call it absent |
| **Total** | **100** | | | |

## Relationship to proposal weights

The proposal groups database design/implementation as 25%, GUI/backend/LangChain as 30%, advanced feature as 10%, error handling as 5%, demo/poster as 15%, and technical documentation/test evidence as 15%. The detailed announcement divides the demo category into **5 group + 10 individual** and the 30-point application category into **10 GUI + 10 backend + 10 assistant**. These totals agree.

## Completion priorities

1. Confirm registration and booking immediately; the later notice specifies a November 16, 2026 deadline and 5% group penalty. That deadline has passed; actual completion is unconfirmed here.
2. Produce and validate the conceptual and relational diagrams.
3. Reuse dated completed database/GUI/image/live-AI evidence and execute the remaining acceptance gaps on a disposable instance; record fresh observations on the final demo machine where needed.
4. Resolve or explicitly justify the implementation findings in the repository review before claiming full compliance.
5. Produce technical/poster PDFs, rehearse the corrected runbook, and assemble one verified ZIP.

No optional second advanced feature is required. Password login, analytics charts/exports, matching criteria, and forecast accuracy analyses are not obligations of the selected Loss & Surplus option.
