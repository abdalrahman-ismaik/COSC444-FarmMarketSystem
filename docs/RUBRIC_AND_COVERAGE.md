# Detailed rubric and coverage

Source: the user-supplied **Project demo rubrics** announcement, reproduced in [announcements](ANNOUNCEMENTS.md). The categories total **100 points**. This matrix records evidence, not predicted marks or a completion guarantee.

**Current as of November 18, 2026:** historical [baseline validation](evidence/VALIDATION.md) and [live AI validation](evidence/AI_VALIDATION.md) are supplemented by the later isolated [integrity follow-up](evidence/FIX_VALIDATION.md). That follow-up records 65/65 original-suite checks, 173 backend checks, 22 GUI checks including restart, and seven assistant/read-only checks. The revised Lab 7 diagrams separately pass the current offline check for 15 tables, 100 columns, 32 foreign keys, and 13 named CHECK constraints. The older 851-check result applies to the previous diagram layout only. Earlier Track A failures remain preserved as historical. The current diagrams, report, poster, and review package have been accepted by Abd Alrahman; human demo and upload work remains. Use [PROGRESS.md](../PROGRESS.md) for status.

## Evidence labels

- **Implemented:** relevant source/SQL exists.
- **Statically reviewed:** implementation or seed statements were inspected without executing the live workflow.
- **Historically reported:** the original guide or supplied development narrative reports an outcome; not a fresh local test.
- **Locally tested:** a check was actually executed in this workspace; see [repository review](REPOSITORY_REVIEW.md) for exact results and limits.
- **Missing / pending:** required artifact or current verification is not present.

## Assessment matrix

| Criterion | Points | Full-grade expectations | Existing implementation/evidence | Remaining acceptance work |
|---|---:|---|---|---|
| ER diagram and relational schema | 10 | Justified entities, relationships, cardinalities, and farm/cycle/lot/request/allocation/delivery rules; separate relational schema with PK/FK, types, and constraints | Accepted five-sheet conceptual ER and three-sheet schema; current offline check passes 15 tables, 100 columns, 32 FKs, and 13 named checks; plain-language notation guide lists all 31 conceptual relationships | Instructor grading remains; screen zoom/projector readability should be checked |
| Implementation and population | 15 | Executable creation/population SQL; at least 3 farms, 4 markets, 5 crops, 8 cycles, 12 lots, 15 movements, 8 requests, 6 receipts; available/reserved/partial/lost/discrepant examples and images; suitable constraints | SQL has 4/4/6/10/13/38/9/6 and 12 image records; original 65 checks and follow-up 173 checks passed; fresh-extraction MySQL load and 65-check rerun passed | Human review and final demo-machine check; exact image-source mapping remains an attribution issue |
| Python GUI | 10 | Friendly role workflows for setup, stock, search/requests, allocations, partial delivery/discrepancies; photo upload/retrieval after restart | 18 tabs; follow-up GUI path recorded 22/22 across search/request/allocation/partial receipts/over-allocation/images/restart; screenshots saved | Manual keyboard/accessibility, scaling, projector and overall usability checks remain |
| Back-end programming and embedded SQL | 10 | Reliable parameterized SQL, sound transactions, integrity, stock/allocation/delivery/discrepancy persistence and ownership | 173 follow-up backend checks passed including competing stock movements, request release, partial receipt races, rollback and ownership; bounded race tests | Team should understand the documented settlement/correction/surplus policies for questions |
| LangChain assistant | 10 | Accurate validated read-only answers in GUI with supporting records/summaries; clear ambiguity and unsupported handling; no data changes | Fourteen historical live questions plus seven follow-up assistant/read-only checks; fresh DB fingerprint unchanged and MySQL rejected writes | Demo-PC live key/model check, broader prompt/injection/large-result testing, and reviewer inspection remain |
| Advanced feature: at least one | 10 | One Phase 3 option database-backed, in GUI, tested, demonstrated; Loss & Surplus needs thresholds, priority, two disposition actions, valid movements and checks | Loss & Surplus is database-backed and accessible in GUI; follow-up backend and GUI evidence includes threshold validation and donation/disposal flows | Team must rehearse the feature and explain thresholds/disposition rules in the demo |
| Error handling and business rules | 5 | Friendly connection/constraint/duplicate/date/crop/unit/empty-result/assistant/image failures; no negative stock or over-allocation; atomic changes, status/movement history, ownership | Follow-up suite and GUI flow cover connection failure, invalid input/date/unit, duplicates, over-allocation, truncated/corrupt images, rollbacks and stock constraints | Remaining manual usability and unusual model/network cases; see dated evidence limits |
| Demo and poster: group | 5 | Fifteen minutes: ~3-minute poster and ~12-minute demo; restart/photo, buyer search/request/partial delivery, over-allocation block, supported and ambiguous/unsupported assistant, advanced feature, friendly invalid input; explain decisions | Poster PDF and runbook are present; flow screenshots/evidence support core scenarios | Three-minute poster plus twelve-minute demo rehearsal, projector check and Q&A are still outstanding |
| Member demo and Q&A: individual | 10 | Strong understanding; on time; within time; clear, confident answers | Three B1 members identified; proposed leads and shared preparation documented | Confirm contributions, all-member attendance, presentation allocation, and cross-topic rehearsal; no individual performance claim yet |
| Technical documentation and test evidence | 15 | Concise technical PDF with diagrams/rules/transactions and expected/actual evidence; major-function valid/invalid/boundary/repeated/concurrent testing, stock/forecast checks, ten assistant questions, images/GUI/feature tests; README setup/run | Accepted 13-page technical PDF includes both diagrams, rules/transactions, expected/actual test evidence, and 14 AI questions; the ZIP passed fresh extraction, path/hash, and exclusion checks | Exact image-source mapping is unresolved; team demo rehearsal and course upload remain |
| **Total** | **100** | | | |

## Relationship to proposal weights

The proposal groups database design/implementation as 25%, GUI/backend/LangChain as 30%, advanced feature as 10%, error handling as 5%, demo/poster as 15%, and technical documentation/test evidence as 15%. The detailed announcement divides the demo category into **5 group + 10 individual** and the 30-point application category into **10 GUI + 10 backend + 10 assistant**. These totals agree.

## Remaining completion priorities

1. The project reviewer accepted the diagrams, report, poster, integrity fixes, and package. Instructor grading and approval are not implied.
2. The team reports all three members registered and a November 19, 2026 demo slot booked for 1:30 PM. Confirm the venue and attendance; the November 16 booking deadline has passed.
3. Rehearse the 3 + 12 minute demo on the actual display/PC, with every member ready to explain all workflows and design decisions.
4. Exact product-photo source/version/transform mapping remains unresolved despite dataset-level attribution; see `IMAGE_ATTRIBUTION.md`.
5. The accepted ZIP is prepared for course upload but has not been uploaded. Perform the actual course submission through the course process.

No optional second advanced feature is required. Password login, analytics charts/exports, matching criteria, and forecast accuracy analyses are not obligations of the selected Loss & Surplus option.
