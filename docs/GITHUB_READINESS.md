# GitHub readiness and remaining tasks

Initial preparation was checked on November 16, 2026; publication preparation updated November 17. This is a working coursework repository, not a completed submission. Local branch: **main**. The user supplied the public repository https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem.git, now configured as `origin`. The initial snapshot is being published; `git status` and `git rev-parse HEAD origin/main` establish current synchronization. Older statements below describe the original preparation snapshot.

**Later runtime update:** the [validation report](evidence/VALIDATION.md) documents a current 65/65 suite pass, 18 Windows role tabs, GUI harvest/photo persistence, and deterministic assistant integration. Runtime data, generated passwords and the virtual environment are local and ignored. Two application batch launchers now prefer that environment. Live Gemini and the remaining full acceptance cases are still pending; the initial verification checklist below is not a claim that no runtime testing has occurred.

**November 17 AI update:** [live Gemini validation](evidence/AI_VALIDATION.md) now records fourteen questions, reference SQL, two live GUI checks, model/prompt corrections and no database changes. The live-AI requirement has current evidence, while broader robustness and final assessed artifacts remain unfinished. Source defaults and assistant prompts/timeouts intentionally changed; no API key is included in source/evidence.

## Local upload preparation

- The maintained application is in `app/`; the root README documents setup and running.
- `.gitignore` excludes local `.env` variants, private-key files, Python environments/caches, logs, and generated output. `app/.env.example` remains eligible for tracking.
- A scan of text files found no common Google/GitHub/OpenAI/AWS token patterns or private-key headers. No `.env`, PEM, KEY, PFX, or P12 files were present. ZIP member names and text contents were checked separately. Pattern scanning is not a guarantee that arbitrary secrets cannot exist.
- The workspace contents before Git metadata were approximately 11.3 MB; the largest file was approximately 3.46 MB. The original ZIP and teaching PDFs/PPTX are intentionally preserved, rather than treated as generated output.
- Python syntax, local documentation links, original package integrity, image integrity, and launcher delegation are checked independently of database/model availability. Exact checks are in [repository review](REPOSITORY_REVIEW.md).
- Automatic approval review rejected removal of the old empty `FarmMarketSystem_Team/FarmMarketSystem/` directory and its parent, reporting only “blocked by policy.” They remain on disk, contain no files, and will not be tracked by Git.

The repository includes the team's names/IDs, instructor materials, and image assets. A **private coursework repository** is the default recommendation for this existing content. Public redistribution needs verified permissions/attribution. No blanket LICENSE was added because no code license was chosen and third-party/instructor materials have separate ownership.

## Upload procedure

Create an empty repository on GitHub under the intended account/team, without an automatically generated README. From the local project root, review and create the initial commit:

```powershell
git status --short
git add .
git diff --cached --stat
git diff --cached --check
git commit -m "Organize Farm-to-Market application and project documentation"
```

Then replace the account/repository placeholders below with the actual GitHub destination:

```powershell
git remote add origin https://github.com/ACCOUNT/REPOSITORY.git
git push -u origin main
```

Publication update: the supplied destination is configured as `origin`, existing Git author identity is available, and GitHub reports the repository is public. Collaborator access remains a human administration task. For this configured checkout use `git push -u origin main` rather than adding `origin` again. The example above remains a generic first-time upload procedure. Never include real keys in screenshots or commits. A fresh clone should follow the README before being considered runtime-verified.

## Missing required artifacts

| Priority | Task | Rubric relationship |
|---|---|---|
| 1 | Confirm all three members are registered and a demo is booked; record actual slot/location | Later notice: November 16 registration/booking deadline, 5% group penalty; attendance/timing also assessed |
| 2 | Create the conceptual ER diagram in Draw.io, with justified entities, relationships and cardinalities | ER + relational schema: 10 points shared |
| 2 | Create a separate relational schema diagram with actual tables, PK/FK, types and constraints | ER + relational schema: 10 points shared |
| 3 | Produce the concise technical PDF with both diagrams, rules, transactions, and completed expected/actual test evidence | Technical documentation/test evidence: 15 points |
| 3 | Produce the digital poster PDF covering context, system/features, advanced feature, rules and ER design | Group demo/poster: 5 points |
| 4 | Assemble a new final submission ZIP and verify it from a fresh extraction | Required submission package; archived original ZIP is not the final version |

## Implemented capabilities still needing current evidence

| Area | Points | Outstanding verification |
|---|---:|---|
| Database implementation/population | 15 | Execute creation/population SQL on disposable MySQL 8; save counts, constraints, sample scenarios and stock results |
| Python GUI | 10 | Windows walkthrough of all roles; image upload and retrieval after full restart; clear valid/invalid/empty states |
| Backend and embedded SQL | 10 | Transaction rollback, ownership, allocation/delivery persistence, repeated and concurrent operations |
| LangChain assistant | 10 | At least ten questions checked against SQL, including ambiguous/unanswerable cases; a live Gemini supported answer and no-write evidence |
| Loss & Surplus | 10 | Adjustable-threshold boundaries, priorities, donation and disposal with persisted movements/history and ownership checks |
| Error handling/business rules | 5 | Connection/duplicate/date/crop/unit/image/assistant errors; negative-stock/over-allocation rejection; no partial updates |
| Group demo/poster | 5 | Timed rehearsal of ~3-minute poster + ~12-minute demo/questions with all required scenarios |
| Individual demo/Q&A | 10 | All three members attend, understand the whole solution, and can explain/demonstrate each subsystem |

These point values identify affected categories, not marks automatically lost or earned. The full rubric sums to 100; some artifacts affect more than one category. Existing code and the historical “65/65 passed” guide do not substitute for fresh observed results.

## Decisions/findings to resolve before claiming full compliance

- **Delivery status:** DELIVERED currently depends on completed allocation totals even when actual receipts are short. Explain the policy or revise/test it against intended partial fulfilment.
- **Shortfalls and corrections:** each allocation has one receipt; all shortfalls become loss. “Approved correction” has a farmer-entered reason but no separate approval step. Document these decisions explicitly.
- **Assistant validation:** regex/keyword checks plus read-only transactions are not a full SQL parser or proof of answer accuracy. Verify generated queries, supporting records, and summaries, especially beyond 50 rows.
- **Concurrency/integrity:** test additional release/cancel/delivery races and rollback; some cross-record unit/stock invariants depend on application logic.
- **Reproducibility:** verify working dependency versions and the configured Gemini model; supplied dependencies are unpinned.
- **Attribution:** verify exact Fruits-360 source/license mapping before redistribution; the supplied attribution is incomplete.

See [test cases](TESTING.md), [corrected demo runbook](DEMO_AND_SUBMISSION.md), and [full rubric matrix](RUBRIC_AND_COVERAGE.md). A second advanced feature, password login, analytics charts/exports, matching, and forecasting are **not required** when completing the selected Loss & Surplus option.
