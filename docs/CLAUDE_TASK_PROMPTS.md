# Ready-to-paste Claude agent assignments

Open Claude Code in the project root and paste one complete assignment below. Read [the teammate handoff](TEAMMATE_HANDOFF.md) first and claim ownership in [PROGRESS.md](../PROGRESS.md). No agents have been launched by writing these prompts.

Track A is suggested for Ali Alshamsi; Track B for Mohammad Arwani. Confirm actual owners rather than inventing contributions. Both tracks deliver to Abd Alrahman Ismaik for review. The third prompt is an optional read-only reviewer audit.

**Sharing prerequisite:** obtain the snapshot from https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem.git and verify `git log -1` and `git status`. Use separate clones/branches for the tracks. The project originally had no commit/remote; that older state is historical. Never share `.env`, `.venv/` or `.local/` as repository assets.

## Authorized branch and PR workflow

The user explicitly requires pull requests for review. Track A/B agents **may create a feature branch, commit, push that branch and open/update a PR**. They must not push directly to `main`, force-push, merge, self-approve, or submit the course project. These permissions apply to Track A/B, not the optional read-only reviewer prompt.

| Track | Branch | PR title |
|---|---|---|
| A — Ali | `ali/database-diagrams-validation` | `Complete database diagrams and validation evidence` |
| B — Mohammad | `mohammad/report-poster` | `Prepare technical report and poster for review` |

From a clean, current checkout, create the assigned branch from `origin/main`. If that branch already exists locally/remotely, inspect and continue its existing work instead of recreating/resetting it. Do not discard an operator's uncommitted changes. Each teammate uses their own authenticated GitHub account. If branch push access is unavailable, use a fork PR or ask Abd Alrahman for collaborator access; report an authentication/access blocker without exposing tokens and continue independent local work.

Example for **Ali** (Mohammad substitutes his branch/title):

```powershell
git fetch origin
git switch -c ali/database-diagrams-validation origin/main
# Complete the assigned work, inspect changes, and run relevant checks first.
git status --short
git diff --check
# After completing these artifacts, stage this track's files explicitly.
git add -- docs/diagrams docs/DATABASE_DESIGN.md docs/evidence/REMAINING_TEST_RESULTS.md docs/reviews/TRACK_A_REVIEW.md PROGRESS.md
git diff --cached --stat
git diff --cached --check
git commit -m "Complete database diagrams and validation evidence"
git push -u origin ali/database-diagrams-validation
gh pr create --base main --head ali/database-diagrams-validation --title "Complete database diagrams and validation evidence" --body-file docs/reviews/TRACK_A_REVIEW.md --reviewer abdalrahman-ismaik
```

The example assumes the completed Track A paths exist. For a partial/draft PR, stage only existing scoped paths; add any new reproduction script explicitly. Mohammad stages his report/poster/build/attribution/review files instead. No blanket staging of another track's changes. Check staged filenames/content for `.env`, credentials, runtime data and unrelated files. Use the corresponding Track B review note for its `--body-file`; preserve real Markdown/newlines. A PR body must state the problem/result, task/requirement IDs, artifacts/build commands, actual validation, dependencies and limitations, plus any reviewer decisions needed.

If unfinished or blocked by Track A assets, open a **draft** PR (`gh pr create --draft ...`, omitting reviewer request until ready). Keep incomplete artifacts clearly labeled. Track B can draft independently, then integrate reviewed/merged Track A assets into its own branch and finish exports. Mark ready and request review when dependencies/checks are satisfied. Packaging after document acceptance may use a follow-up branch/PR. Never merge another PR yourself to unblock work.

Record the PR URL, branch, date and review status in PROGRESS.md and the track review note. Use `gh pr edit` to update the existing PR instead of creating duplicates. Address review comments with additional commits on the same branch; no force-push. Resolve conflicts only on the assigned branch, preserve both tracks' work, rerun affected checks and explain any unresolved conflict. If GitHub CLI is unavailable, push the branch, prepare the PR body and provide the compare link for a human to open it; label that final PR-creation step blocked rather than claiming a PR exists.

## Track A — Database diagrams and remaining validation

Copy this whole block:

```text
Complete Track A of the existing COSC444 Farm-to-Market project, lab B1. Produce complete reviewable artifacts for Abd Alrahman Ismaik. Do not rebuild the app or accept/submit/publish work yourself.

READ FIRST:
CLAUDE.md, AGENTS.md, README.md, docs/TEAMMATE_HANDOFF.md, PROGRESS.md; then docs/ANNOUNCEMENTS.md including the full rubric, docs/PROJECT_REQUIREMENTS.md, the original proposal PDF, docs/RUBRIC_AND_COVERAGE.md, docs/ARCHITECTURE.md and docs/TESTING.md. Read docs/evidence/VALIDATION.md and AI_VALIDATION.md with relevant JSON/screenshots. Inspect actual app/schema.sql, app/db.py, app/tests/test_business_rules.py and relevant GUI/assistant callers. Do not dump image hex or secrets.

Claim unowned DB-01, DB-02, DB-03 and TEST-01 in PROGRESS.md with actual operator/date. Suggested lead: Ali Alshamsi, 100062530; this does not imply past contributions. Coordinate if tasks are already owned. Preserve MySQL/Python/Tkinter, LangChain/Gemini, BLOB photos, demo-user selection, stock ledger and Loss & Surplus as the one advanced feature. No stack migration, login system or second advanced feature.

DELIVER:
1. docs/diagrams/conceptual-er.drawio plus conceptual-er.svg and conceptual-er.pdf. Author an editable Draw.io conceptual ER diagram, distinct from a schema picture. Justify entities, relationships, participation/cardinalities and rules for farms/users/assignments, crops/cycles, harvest lots/images, stock movements, markets/requests, allocations and deliveries. Show partial fulfilment, forecast/stock separation and derived inventory. Include necessary supporting concepts without turning views into stored entities.
2. docs/diagrams/relational-schema.drawio plus relational-schema.svg and relational-schema.pdf. Map all 15 actual tables with exact columns/types, nullability, PK/composite/unique keys, FKs and important CHECK/ENUM constraints. Explain the two views separately. Do not invent keys, cascades or cross-record SQL constraints. Use multiple readable pages if necessary. Open/parse Draw.io sources, export and inspect every page for clipped labels, misleading lines/cardinalities and legibility.
3. docs/DATABASE_DESIGN.md. Explain cardinalities, mapping/justified normalization, units, forecast separation, movement formulas, history, ownership and transactions. Distinguish SQL-enforced vs application-enforced rules. Document existing allocation-based DELIVERED status (seed request #6: 60 allocated/52 received), one receipt finalizing an allocation, discrepancy-as-loss, reason-based farmer correction and surplus eligibility after released allocations. Do not invent instructor approval of these policies.
4. docs/evidence/REMAINING_TEST_RESULTS.md and minimal guarded reproduction scripts where needed. Reuse prior evidence accurately: 65 checks, 18 tabs, image restart, 14 live AI questions/two GUI AI cases exist. Do not claim you personally reran them. Prioritize uncovered intermediate-failure rollback; competing allocation/release/cancel/delivery; full GUI search/request/allocation/partial receipt; threshold bounds 0/60 and 0/365 and exact-date/age boundaries; image size/format/path/missing/corrupt handling; ownership/reserved stock; and remaining unit/date/error cases. Record environment, commands, preconditions, expected/actual values, assertions, outcome and limits. No fabricated Pass results. Use Blocked for unavailable runtime-dependent checks and continue independent work.
5. docs/reviews/TRACK_A_REVIEW.md. List exact artifacts, requirement IDs covered, diagram QA, observed tests, unresolved findings, minimal proposed fixes, reviewer decisions and inputs ready for Track B. Provide exact export commands/tool versions.

DATABASE SAFETY:
Setup hardcodes DROP/CREATE farm_market_db; changing DB_NAME does not retarget reset. The business-rule script mutates data and executes on import. Never import it for discovery or run reset/tests on valuable/shared data. Use a confirmed disposable instance and your own ignored .env. The original PC's localhost:3307 server/.local helper/.venv are not portable. Do not print or commit passwords/API keys or reset another teammate's instance. Missing credentials block live tests, not drawings/static analysis.

BOUNDARIES:
Do not alter core behavior/schema/status policy/seed data without reviewer authorization. For conflicts or failures, document reproduction, impact, smallest proposed patch and required retest; do not hide them by changing expected results. Any legitimate oracle correction must preserve the original expectation and explain why it was wrong. Do not modify instructor source material or overwrite historical failure evidence.

COORDINATION AND FINISH:
Own diagrams/design/new test evidence and your review note. Do not overwrite Track B report/poster/build sources. Make narrow coordinated shared-document edits. Update only your task rows and append factual contribution/activity entries in PROGRESS.md. Finish real artifacts when source/dependencies suffice, not just a plan/placeholders. Follow this file's authorized branch/PR workflow: use ali/database-diagrams-validation, commit scoped changes, push the branch, open/update a PR into main and request abdalrahman-ismaik. Record PR URL and evidence; deliver Ready for review, never Accepted. Do not push to main, force-push, merge, publish/submit the course project or register/book externally. End with PR/artifact links, actual checks, exact blockers and reviewer decisions needed.
```

## Track B — Report, poster, export workflow and candidate package

Copy this whole block:

```text
Complete Track B of the existing COSC444 Farm-to-Market project, lab B1. Prepare editable documents and final-format artifacts for Abd Alrahman Ismaik to review. Do not redesign/rebuild the app or submit anything externally.

READ FIRST:
CLAUDE.md, AGENTS.md, README.md, docs/TEAMMATE_HANDOFF.md and PROGRESS.md; docs/ANNOUNCEMENTS.md including full rubric, docs/PROJECT_REQUIREMENTS.md and original proposal PDF; docs/RUBRIC_AND_COVERAGE.md, ARCHITECTURE.md, TESTING.md, TEAM.md, DEMO_AND_SUBMISSION.md, PRODUCT.md and DESIGN.md. Read docs/evidence/VALIDATION.md and AI_VALIDATION.md and their results/screenshots; inspect current SQL/source for technical claims. The old Visual_Guide.pdf is historical, not the final technical report.

Claim unowned DOC-01, POSTER-01, BUILD-01, ATTR-01 and PACKAGE-01 with actual operator/date. Suggested lead: Mohammad Arwani, 100064908. Team: Abd Alrahman Ismaik 100064692, Ali Alshamsi 100062530, Mohammad Arwani 100064908, lab B1. Do not invent contributions. Preserve the current MySQL/Tkinter/Python/BLOB/LangChain stack and Loss & Surplus selection; no extra advanced feature.

Track A owns final conceptual/schema diagrams, DATABASE_DESIGN.md and REMAINING_TEST_RESULTS.md. Draft narrative/layout/export tools now; final diagram/test claims depend on their real outputs. Do not fabricate missing drawings/results or create a competing schema. Label blocked draft dependencies, finish independent sections and coordinate via PROGRESS.md.

DELIVER:
1. docs/report/technical-report.md and submission/technical-report.pdf. A concise academic report (6-10 pages is a working target, not an instructor limit): context/team, conceptual ER and separate relational schema, justified rules and constraints, units/forecast separation, ledger formulas, key transactions/ownership, images, selected feature, read-only LangChain and expected/actual test evidence. Include at least ten actual assistant questions with ambiguity/unanswerability, stock calculations, image/GUI and advanced-feature evidence. Cite real results/files, environments and limits; do not claim every acceptance variant passed. Readable diagrams and real results matter; screenshots are optional. No unfinished placeholders in a report called final.
2. Editable poster source under docs/poster/ and submission/poster.pdf. Default one projector-readable landscape page (16:9 unless a later instructor requirement overrides). Include context/introduction, key business rules, system overview/workflow, core GUI/images/LangChain, selected Loss & Surplus, database design including the actual ER diagram, course/B1/all names/IDs. Use the existing green-and-white identity. Support a three-minute explanation, not dense report prose. No invented national-coverage/optional-feature claims.
3. docs/BUILD_DOCUMENTS.md and minimal reproducible export source. Record exact commands, dependencies/versions and diagram inputs. Keep document dependencies separate from app/requirements.txt. Supply editable sources, render every PDF page to ignored output/ or tmp/ previews, inspect every page and correct clipping, overlap, glyph failures and unreadable diagrams/tables. Record page counts and visual QA. If rendering is unavailable, report the blocker rather than claiming visual verification.
4. docs/IMAGE_ATTRIBUTION.md. Verify exact original sample-image creator/source/version/license mapping where possible. The package claims Fruits-360/CC BY-SA 4.0 but mapping is incomplete. Cite verified original sources, preserve existing attribution, and record gaps requiring a reviewer decision. No invented image-source URLs, blanket license for instructor materials or unapproved photo replacements.
5. docs/reviews/TRACK_B_REVIEW.md. List paths, build commands, requirements covered, evidence used, per-page QA, attribution state, unresolved dependencies/claims and reviewer decisions. Preserve the demo runbook's request-before-allocation-before-delivery sequence and fifteen-minute limit.
6. After artifact review dependencies are satisfied: submission/FarmMarketSystem_B1_candidate.zip and submission/MANIFEST.md. Keep PACKAGE-01 Blocked/awaiting review until then. Package the reviewed technical/poster PDFs, root README/launchers, maintained app source/launchers/requirements/.env.example/final SQL and demo images/attribution; include useful diagram sources/exports. Preserve actual runnable paths. Exclude .git, .env, secrets, .venv, .local, logs/caches, archive/original ZIPs, skills and preview artifacts. Never recursively include submission/ or the ZIP itself. List members and SHA-256s in manifest. Extract fresh, check paths/PDFs/placeholders and perform runtime checks only with disposable MySQL/local credentials. Label candidate, not submitted/accepted.

EVIDENCE ACCURACY:
65 existing business checks, 18 tabs, photo restart, 14 live Gemini questions and two GUI AI cases have current evidence. Do not say live AI is untested or relabel earlier observations as your own runs. Preserve initial 12/13 failure, model/filter fixes, reference correction and segmented reruns. Current default is gemini-3.1-flash-lite; model availability may vary. Current policy findings (allocation-based DELIVERED, one receipt/shortfall loss, reason-based correction, regex assistant validation) must be explained or escalated, not hidden or silently changed.

SAFETY AND ADMINISTRATION:
Setup drops hardcoded farm_market_db; the business script mutates on import. Do not run them as document checks, reset a shared instance or expose keys in documents/ZIPs. November 19 is due date; November 16 was the later registration/booking penalty deadline and has passed. Actual registration/slot/location/attendance are unconfirmed here. Human members confirm these; agents must not book/register or invent status/cutoff hours.

FINISH:
Own report/poster/build/attribution/package and your review note; preserve Track A artifacts. Coordinate narrow shared README/rubric/progress edits. Append factual work/evidence to PROGRESS.md, with exact blockers/next steps. Follow this file's authorized branch/PR workflow: use mohammad/report-poster, commit scoped changes, push the branch, open/update a PR into main and request abdalrahman-ismaik. Use a draft PR while diagram/test/review dependencies remain; record the URL and limitations. Deliver Ready for review; only Abd Alrahman marks Accepted. No direct main push, force-push, merge or course-project publication/submission. Finish actual artifacts when dependencies permit; end with PR/artifact links, actual build/visual/test outcomes and remaining decisions.
```

## Optional reviewer — Read-only acceptance audit

```text
Review Track A/B deliverables for Abd Alrahman Ismaik without modifying files, database state or task acceptance. Do not merge/push/publish/submit.

Read AGENTS.md, CLAUDE.md, TEAMMATE_HANDOFF, PROGRESS, original proposal, saved announcements/full rubric and current rubric matrix. Inspect both track review notes, editable drawings/exports, current SQL/code, technical report/poster PDFs, build instructions, expected/actual evidence and candidate ZIP/manifest if present. Render/view real PDF/diagram pages using read-only tools and preview artifacts where possible; do not run DB reset or mutating tests.

Check all ten rubric categories totaling 100 without promising marks. Confirm separate conceptual/schema diagrams, accurate cardinalities/types/keys/constraints, honest policy/transaction explanations, at least ten real assistant questions, actual GUI/image/feature evidence, readable poster/ER, correct team identities and consistent document versions. Check candidate contents, manifest hashes, launch paths and exclusion of secrets/runtime/archive/dev assets. Missing runtime/render evidence is a limitation, not proof of success.

Return severity-ordered findings with file/page/line references, affected requirement, observed issue, smallest fix and validation needed. Recommend Ready for human acceptance / Needs revision / Blocked per task, and list administrative/rehearsal/Q&A work. Only Abd Alrahman records acceptance. Do not silently fix artifacts or invent evidence.
```
