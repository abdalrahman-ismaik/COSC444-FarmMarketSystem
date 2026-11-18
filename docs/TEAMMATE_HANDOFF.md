# Teammate handoff and completion instructions

**Snapshot: November 17, 2026 · COSC444 Database Systems · Lab B1.** This is the starting document for teammates and their Claude agents. Current task ownership/status belongs in [PROGRESS.md](../PROGRESS.md); use the [copy-paste agent prompts](CLAUDE_TASK_PROMPTS.md) to begin work. Abd Alrahman Ismaik will review the deliverables before acceptance/submission.

## Team and purpose

| Member | Student ID | Suggested role for this completion pass |
|---|---|---|
| Abd Alrahman Ismaik | 100064692 | Reviewer, integration/administrative coordination, cross-topic preparation |
| Ali Alshamsi | 100062530 | Track A: database drawings, remaining validation, policy findings |
| Mohammad Arwani | 100064908 | Track B: technical report, poster, reproducible exports, candidate package |

This is a proposed work split, not a claim that these members authored the imported code or completed the assigned tasks. Confirm ownership when claiming a task. Every member must still contribute to and understand database design/implementation and be able to explain the entire solution. [TEAM.md](TEAM.md) contains the broader proposed responsibility matrix.

The app connects farmers and markets using a movement-based inventory ledger: farmers record crop cycles/harvest lots, buyers request produce, farmers reserve lots through allocations, and buyers confirm actual deliveries/discrepancies. Administrators manage users/reference data. The project uses fictional operational data in a UAE local-food context; it is not a government system or a national supply database.

## Are the requirements and announcements saved?

**Yes: all project announcement/rubric text supplied in this conversation is saved**, with the original proposal and lab slides. No claim is made that eLearn or the booking/registration websites were checked for newer information.

| Source | Location | Use |
|---|---|---|
| Original project proposal, four pages | [Proposal PDF](sources/Local_Farm_Market_Food_Availability_Project_Proposal.pdf) | Normative phases, rules, deliverables, original assessment weights |
| Supplied announcements and full detailed rubric | [ANNOUNCEMENTS.md](ANNOUNCEMENTS.md) | Preserved announcement wording, deadlines, penalties, poster/demo instructions and registration/booking links |
| Structured requirements | [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) | IDs, core business rules, sample minimums, selected/unselected advanced options |
| Current 100-point coverage matrix | [RUBRIC_AND_COVERAGE.md](RUBRIC_AND_COVERAGE.md) | Current evidence and remaining acceptance work for every category |
| Lab 6 teaching slides | [langchain.pptx](sources/langchain.pptx) | Teaching reference, not the farm database schema |

Submission is **Thursday, November 19, 2026**; no cutoff time was supplied. Earlier booking notice: November 12. Later notice: registration/demo booking by **November 16**, failure incurs **5% group penalty**. That later date has now passed. Abd Alrahman reports all three members registered and a demo booked for November 19 at 1:30 PM; verify the sheet entries, completion date (for any deadline penalty), venue and attendance. Initial demo dates were November 19/20/23; later notice said available slots were November 19. Demo is strictly fifteen minutes, approximately three minutes of poster and twelve of live demo/questions. All members attend unless officially excused; late/incomplete demos may incur 10%. Do not invent how penalties combine.

## What is already implemented and verified?

| Area | Current work/evidence | Important limit |
|---|---|---|
| Application | MySQL, PyMySQL, Tkinter/ttk, Pillow, LangChain/Gemini, three role workflows, BLOB photos | Preserve the working implementation; diagrams, report, poster and review-candidate ZIP are present; review and demo rehearsal remain |
| Database | 15 tables, two views; sample SQL includes 4 farms, 4 markets, 6 crops, 10 cycles, 13 lots, 38 movements, 9 requests, 6 receipts, 12 BLOB photos | Counts/state change after testing; dates are relative to SQL execution date |
| Business rules | **65/65 existing checks passed locally** on MySQL 8.0.46 | Representative suite, not exhaustive coverage or independent verification of every assertion |
| GUI | 18 role tabs; follow-up GUI automation 21/21 plus restart 22/22 covering full request/allocation/partial-delivery/photo path | Automated widget/callback checks; manual accessibility/scaling/projector checks remain |
| Live AI | 14 baseline questions and seven follow-up assistant/read-only cases; DB unchanged in follow-up | Not a proof of arbitrary-question accuracy; final demo-PC check remains |
| Selected advanced feature | Loss & Surplus query, adjustable thresholds, donation/disposal and stock checks implemented/tested in suite | Full threshold/image/boundary/permission matrix still needs completion |
| Documentation | Root README, architecture, test plan/evidence, announcements, rubric, team, product/design spec, runbook, technical report and poster PDFs | Files are review candidates; human approval/demo remains |
| Repository | App/docs, editable diagrams, dated evidence, review-candidate ZIP/manifest, ignore rules; PRs #1–#5 open/unmerged | Check `git status`/PR state; reviewer acceptance and course submission are not inferred |

Evidence sources: baseline [Windows/MySQL](evidence/VALIDATION.md) and [live AI](evidence/AI_VALIDATION.md) reports plus the later isolated [integrity follow-up](evidence/FIX_VALIDATION.md), raw JSON and screenshots. Preserve each run's tester/source/date; do not attribute another person's checks to yourself.

Gemini default is **`gemini-3.1-flash-lite`**. The older 2.5 Flash returned a new-user model-access 404; several newer models were busy/timed out. The prompt was corrected after one Dates-filter failure, and requests now have a 30-second timeout per provider call with limited retry configuration. Initial and corrected results are both retained. Each teammate provides their own permitted local credentials; no shared API key is in the repository.

## Repository and documentation map

| Path | Purpose / how to use it |
|---|---|
| `README.md` | Main install/run instructions, team, current verification and document links |
| `AGENTS.md`, `CLAUDE.md` | Project boundaries and agent entry instructions |
| `PRODUCT.md`, `DESIGN.md` | Product truth and current green/white desktop theme; not instructions to redesign |
| `app/app.py` | Actual Tkinter GUI, role tabs, forms/tables/photos, background assistant UI |
| `app/db.py` | Connections, validation, ownership, parameterized SQL, transactions, stock and reference-data actions |
| `app/assistant.py` | LangChain/Gemini prompts, validated read-only SQL, result summary, model/timeout defaults |
| `app/schema.sql` | Authoritative schema + seed data + image BLOBs; do not dump image hex into reports |
| `app/setup_database.py` | Configuration/bootstrap and SQL loader; drops/recreates the hardcoded `farm_market_db` |
| Root and `app/` batch files | Setup/run; prefer root `.venv` if present, otherwise Python on PATH |
| `app/requirements.txt`, `app/.env.example` | Runtime dependency list and nonsecret configuration template |
| `app/tests/test_business_rules.py` | Existing 65-check script; mutates seed database; **do not import for discovery** |
| `app/sample_images/` | Four external JPGs for upload demo; main product images are embedded in SQL |
| `docs/ARCHITECTURE.md` | Model/table descriptions, formulas, transactions and exact current behavior |
| `docs/TESTING.md` | Full acceptance matrix; combine with dated observed evidence, not just Pending/Pass labels |
| `docs/DEMO_AND_SUBMISSION.md` | Corrected dependency order, proposed presentation split, PDF/ZIP checklist |
| `docs/REPOSITORY_REVIEW.md` | Original-file inventory, historical checks, later updates and implementation findings |
| `docs/GITHUB_READINESS.md` | Initial Git/upload preparation and later testing updates |
| `docs/SKILLS.md`, `.agents/skills/` | Skill provenance; reusable skills are repository-only and omitted from the course ZIP |
| `archive/` | Original ZIP/README and separate school-enrollment lab sample; retained in repo, omitted from course ZIP |
| `.env`, `.venv/`, `.local/` | Ignored local configuration/environment/runtime. Not shared, not submission inputs |

When sources appear inconsistent: use the proposal/announcements for requirements; current SQL/source for implemented behavior; dated evidence for observed results; and PROGRESS for assignment/review status. Older guide screenshots or initial review paragraphs never override later observed results. Report discrepancies rather than silently rewriting instructor text.

## Running on a teammate's Windows PC

Get the shared snapshot by cloning [the project repository](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem). Use separate clones/branches for the two tracks. This project began as an uncommitted local folder; that older state is historical. Run `git log -1` and `git status` to verify your current checkout. Do not copy only `.git` or assume local ignored runtime files are shared.

```powershell
git clone https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem.git
Set-Location COSC444-FarmMarketSystem
```

Open PowerShell in the project root. Use Python 3.12 with Tcl/Tk, the version tested here:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r app\requirements.txt
if (-not (Test-Path app\.env)) { Copy-Item app\.env.example app\.env }
notepad app\.env
```

Configure your own MySQL host/port/user/password and `DB_NAME=farm_market_db`; add your own Gemini key if testing AI. The template is not working credentials. Do not overwrite an existing `.env`, post it in chat, or commit it.

**Only on a confirmed disposable MySQL instance**, initialize and run:

```powershell
.\.venv\Scripts\python.exe app\setup_database.py
.\run.bat
```

Setup hardcodes `DROP DATABASE IF EXISTS farm_market_db`. Changing `DB_NAME` does not retarget its reset. Use a separate disposable server/instance if your normal server has valuable data under that name. The original PC's temporary localhost:3307 server/helper and `.venv` are not provided by a Git clone; teammates must set up their own runtime.

On fresh disposable seed data only, the mutating suite is:

```powershell
.\.venv\Scripts\python.exe app\tests\test_business_rules.py
```

The script changes balances/statuses; reset only that disposable instance afterward if a fresh demo is intended. Do not reset between photo upload and restart verification. New lot IDs and time-dependent results differ from saved evidence; lot #14 in screenshots is a GUI-created record, not part of the thirteen-lot seed SQL. Missing credentials/runtime is a documented blocker for live tests, not permission to fabricate outcomes.

## What remains from the rubric?

| Rubric category | Points | Remaining work |
|---|---:|---|
| ER and relational schema | 10 | Human review of conceptual notation/cardinalities and relational schema; decide acceptance |
| Implementation/population | 15 | Review verified SQL counts/constraints and fresh-extraction database results; demo-machine check |
| Python GUI | 10 | Manual accessibility/scaling/usability checks and demo-PC rehearsal |
| Backend/embedded SQL | 10 | Reviewer confirms fixes and current settlement/correction/surplus policies |
| LangChain | 10 | Demo-PC live check and remaining prompt robustness review |
| Advanced feature | 10 | Rehearse Loss & Surplus and explain thresholds/disposition behavior |
| Errors/business rules | 5 | Review dated passing evidence; human usability checks |
| Group demo/poster | 5 | Projector check and timed 3 + 12 minute rehearsal |
| Individual demo/Q&A | 10 | All three rehearse all topics and attend; only actual participation counts |
| Technical PDF/test evidence | 15 | Reviewer acceptance; actual final course upload |
| **Total** | **100** | Categories indicate assessment scope, not marks already earned/lost |

Still outstanding: exact image attribution/source mapping, human confirmation of registration/booking/location, Abd Alrahman’s acceptance, projector check, timed rehearsal, and final course upload. A review-candidate ZIP exists but is not a final or submitted package. **Do not implement a second advanced feature**: analytics/export dashboards, secure password login, matching and forecasting are optional alternatives, not extra obligations of Loss & Surplus.

## Required deliverable contract

These paths are present in the review candidate. Use the ledger for current readiness and do not mark Accepted before Abd Alrahman reviews.

| Owner | Deliverables for review |
|---|---|
| Track A | `docs/diagrams/conceptual-er.drawio`, `conceptual-er.svg`, `conceptual-er.pdf`; `relational-schema.drawio`, `relational-schema.svg`, `relational-schema.pdf`; `docs/DATABASE_DESIGN.md`; `docs/evidence/REMAINING_TEST_RESULTS.md`; `docs/reviews/TRACK_A_REVIEW.md` |
| Track B | `docs/report/technical-report.md`; editable poster source under `docs/poster/`; `submission/technical-report.pdf`, `submission/poster.pdf`; `docs/BUILD_DOCUMENTS.md`; `docs/reviews/TRACK_B_REVIEW.md` |
| Review package | `submission/FarmMarketSystem_B1_review_candidate.zip`, `submission/MANIFEST.md`; validated from fresh extraction, not submitted or accepted |
| Everyone | Own task rows/evidence/contribution entries in [PROGRESS.md](../PROGRESS.md); factual gaps and review requests |

Use a small documented export/build workflow with document-generation dependencies separate from runtime requirements. Include editable sources and commands, not only PDFs. Render every PDF page and inspect it; record visual checks, page counts, legibility and unresolved defects. Keep final artifacts in `submission/` and generated previews in ignored `output/` or `tmp/`.

The original Track A and Track B PRs remain open. Their later integrity/document follow-up is recorded separately; preserve historical failures and both teammates' authorship. Review [PROGRESS.md](../PROGRESS.md) and [review notes](reviews/) before making changes.

## Policies to explain or escalate

- Current DELIVERED status uses completed allocated totals, not received totals; seed request #6 is 60 allocated/52 received and DELIVERED.
- One receipt finalizes an allocation; any shortfall is released from reservation and recorded as loss.
- “Approved correction” is currently a farmer action with a required reason, without separate admin approval.
- Surplus means no non-released allocation; released historical allocations do not disqualify a lot.
- Cross-record unit equality/aggregate stock invariants partly rely on application logic. Row locks do not prove every race is correct.
- Assistant SQL validation is regex-based; no row-specific user context is supplied to the assistant, and summaries use only the first fifty of up to two hundred records.

Document current behavior accurately. If it contradicts requirements or a new test fails, deliver a minimal proposed fix, impact and test evidence for Abd Alrahman's decision. Do not silently change statuses/schema/seed data to make a report look correct.

## Collaboration and reviewer handoff

1. Claim an unowned task in PROGRESS with date/owner and status **In progress**. Check dependencies and files before editing.
2. Keep each track's artifacts separate. Track A owns diagrams/design/test results; Track B owns report/poster/export/package. Only edit shared README/rubric/progress in narrow coordinated changes.
3. On shared disk, do not run two Git checkouts/resets or database resets against the same directory/instance. Prefer separate clones once an initial commit exists.
4. Preserve prior evidence; append dated runs rather than altering failed results into passes. Cite actual environment, setup, expected/actual results and limitations.
5. Update your task to **Ready for review**, with exact paths, build/test commands, observations, known gaps and decisions requested. Create the assigned review note.
6. Abd Alrahman reviews artifacts and may mark them **Accepted** or return them for revision. PR authors never self-accept or merge. Branch commits, pushes and PR creation follow the task owner’s explicit authorization; course submission and external registration remain with the human team.

The main success criterion is a complete, reproducible, honest set of reviewable deliverables, not merely more Markdown or an assertion that all rubric points are satisfied.
