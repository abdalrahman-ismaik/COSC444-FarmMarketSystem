# Repository review and verification

Reviewed on **November 16, 2026**. The working folder was not a Git repository at intake; this pass did not initialize Git, create commits, or publish a remote. No MySQL reset, business-rule execution, live Gemini request, registration, or booking was performed.

**Later updates:** This November 16 intake snapshot predates the GitHub publication and teammate PRs. The repository was subsequently pushed to the supplied remote and PRs were opened; use `PROGRESS.md` and GitHub for current branch/PR status. This page records the earlier intake observations only. Ignore rules were later extended for private-key files and coverage output; see [GitHub readiness](GITHUB_READINESS.md) for the original upload audit. Empty-folder deletion was retried after the user's explicit request and again rejected by automatic approval review with “blocked by policy.” Git does not track those empty directories.

### GitHub preparation checks

| Check | Observed result |
|---|---|
| Ignore behavior | 9/9 checks passed for `.env` variants, example template inclusion, virtual environment/cache/private key/output exclusions, SQL and source-material inclusion |
| Eligible upload contents | 168 files, 11,274,768 bytes at scan time; no local credential filenames included |
| Credential-pattern scan | No common token/private-key pattern matches in eligible UTF-8 text or text within the original ZIP's 16 file members |
| Maintained documentation | 15 Markdown documents, 43 local links/anchors resolved; code fences balanced |
| Python syntax | All six application/lab Python files parsed; no imports, database operations, or model calls |
| Original application preservation | All 16 files still match original ZIP contents byte-for-byte |
| Git staging preview | `git add --dry-run -- .` succeeded; nothing staged; no commits or remote configured; branch `main` |

File byte counts describe the scan snapshot and will change with documentation updates. Secret-pattern scanning does not prove absence of every possible credential. These checks establish local upload preparation, not runtime/rubric completion.

## GitHub publication — November 17

The user supplied and authorized https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem.git. It was empty and public. Initial commit `e67b94a` containing 184 project/source/evidence/skill files was pushed to `origin/main`. Exact local API key/database password checks and common credential-pattern scans passed; `.env`, `.local/`, `.venv/` and caches remained excluded. A whitespace check reported pre-existing formatting issues in copied/reference material; those original materials were preserved rather than reformatted. No new application runtime tests were needed for this publication-only change. Earlier no-commit/no-remote statements below are historical snapshots.

## Current verification

**November 17 live AI update:** see [AI validation](evidence/AI_VALIDATION.md) for fourteen live questions, two GUI checks, model-access/provider failures, the crop-filter prompt fix and integrity results. `assistant.py`, `setup_database.py`, and `.env.example` intentionally changed to support the working model, bounded calls, and clearer prompts. Existing historical file hashes are baseline records, not claims that those current files still match the ZIP. Runtime credentials remain ignored.

**Later runtime validation:** the existing business-rule suite now passes **65/65 locally on isolated MySQL 8.0.46**. Eighteen Windows role tabs, actual harvest-form valid/invalid submission, and uploaded-photo retrieval after process restart also passed. See [runtime evidence](evidence/VALIDATION.md). `app/setup.bat` and `app/run.bat` were updated to prefer the project virtual environment, so those two baseline files intentionally differ; original Python/SQL/images remain unchanged. The table below preserves the earlier organization-pass snapshot.

| Check | Actual result |
|---|---|
| Original ZIP member preservation | 16/16 files match byte-for-byte |
| Python syntax | 6/6 files parsed with Python 3.13.14 (no imports or database calls) |
| External image integrity | 4/4 JPEGs verified with Pillow |
| Source visual spot-check | Rendered proposal page 1 and historical guide page 5 inspected alongside all four external produce photos; consistent with documented desktop theme and image purpose |
| Skill preservation | 128/128 source files match byte-for-byte |
| Root launcher delegation | 2/2 wrappers pass arguments and return child exit code 23 from a temporary path containing spaces; no MySQL/GUI executed |
| Markdown validation | 14 maintained Markdown documents; 37 local links and heading targets resolve; code fences balanced |
| Rubric and team consistency | 10 categories sum to 100; all three names/IDs agree in README and team record; 15 assistant cases specified |
| Seed row counts | Static INSERT tuple counts: {"allocations": 10, "crop_cycles": 10, "crops": 6, "delivery_receipts": 6, "emirates": 7, "farm_users": 4, "farms": 4, "harvest_lot_images": 12, "harvest_lots": 13, "market_requests": 9, "markets": 4, "request_status_history": 25, "stock_movements": 38, "units": 3, "users": 8} |
| Schema objects | 15 tables; 2 views |

These are repository/static and isolated launcher checks. They are not a fresh reproduction of the guide's 65/65 MySQL result, a full dependency install, or a GUI acceptance run.

## Review coverage

Read the Python, SQL, batch files, requirements, configuration template, and original README; extracted all pages of both PDFs and all twelve slides' text from the PPTX; inspected seed data, BLOB linkage, and external JPEG integrity. The ZIP's file entries were compared byte-for-byte with relocated files. Binary photo hex was treated as image content rather than source prose. Copied skill implementation files are support tooling, not an additional farm application.

## Findings and pending work

| Finding | Implication / next action |
|---|---|
| Conceptual ER, separate relational schema diagram, poster PDF and technical PDF absent | Produce assessed artifacts; architecture prose and historical visual guide do not substitute |
| Guide reports 65/65 tests but has no current execution log in this workspace | Retain as historically reported; run fresh tests on disposable MySQL and record actual results |
| Historical AI screenshots use a stand-in | Run live Gemini supported/ambiguous/unsupported tests before demo; do not claim live success from screenshots |
| Historical guide shows delivery before creating required allocations | Follow corrected Markdown runbook: request → allocation(s) → receipt |
| DELIVERED uses processed allocation totals, not received total | Seed request #6 is 60 allocated/52 received and DELIVERED; justify or review policy against intended partial-fulfilment semantics |
| One receipt per allocation; all shortfalls recorded as LOSS | Explain finalization semantics; remaining shipment cannot use a second receipt on the same allocation |
| Correction action says approved but has no independent approval mechanism | Document actual farmer permission and required reason, without inventing an admin approval workflow |
| Surplus excludes non-released allocations, rather than all historical allocations | Lots with only released allocations can qualify; corrected documentation avoids “never allocated” claim |
| SQL validator uses regex and keyword/table checks | Not a full parser/sandbox; read-only transaction does not prove semantic accuracy or complete query safety |
| Assistant has no user/role parameter and shared search allows operational reads | Mutation ownership exists; do not claim row-scoped assistant confidentiality or password authentication |
| Summarizer receives only 50 of up to 200 query rows | Check aggregate/large-answer completeness against supporting records |
| Lot/request locking exists but transaction isolation and every race are untested here | Existing concurrency scenario does not prove all interleavings; test release/cancel/delivery/allocation conflicts and rollback |
| Cross-record unit equality and aggregate nonnegative stock rely on application logic | CHECK/FK constraints alone do not enforce all business invariants for direct SQL writes |
| Setup hardcodes DROP/CREATE farm_market_db; DB_NAME only configures runtime connection | Changing DB_NAME does not make reset safe for another database; use disposable instance for tests |
| Business-rule script runs and mutates on import | Do not use automatic test discovery/import; run explicitly on fresh disposable seed |
| Dependencies unpinned; minimum-version and current model availability unverified | Record actual working versions/model during clean-room validation; no new compatibility claims |
| Image license/source mapping incomplete in supplied package | Preserve claimed Fruits-360/CC BY-SA attribution; verify exact upstream provenance before redistribution |
| Registration, booking, time/location and member attendance unconfirmed | Complete administrative checks; retain both supplied deadline notices |

No functional corrections or UI restyling were made in this pass. The limitations above are review findings, not newly observed runtime failures.

Automatic approval review rejected the command to remove the empty original `FarmMarketSystem_Team/FarmMarketSystem/` wrapper directories, reporting only “blocked by policy.” Those empty directories remain; all their original files have been relocated and accounted for. No deletion workaround was attempted.

## Original-file inventory

All supplied files are accounted for below. Hashes identify the preserved bytes at their current locations. ZIP-contained members also matched the original ZIP directly. For independent root inputs, hashes were recorded after relocation; no independent pre-move digest was captured.

| Original path | Current path | SHA-256 |
|---|---|---|
| `FarmMarketSystem_Team.zip` | `archive/original-package/FarmMarketSystem_Team.zip` | `fd2ff2e1627b7037b3b0a68d3552abc0f8f8d0475504ae38a7c32b7eb1213653` |
| `FarmMarketSystem_Team/FarmMarketSystem/.env.example` | `app/.env.example` | `900117c413837bc4834f78af8bdc9842a4666d9ffc4f8c059612089a26265b9b` |
| `FarmMarketSystem_Team/FarmMarketSystem/README.md` | `archive/original-package/README.md` | `0cda34d38caccc7e517df31df5b197f6a774930250dcf217c40ecdb5e2cde8a7` |
| `FarmMarketSystem_Team/FarmMarketSystem/Visual_Guide.pdf` | `docs/reference/Visual_Guide.pdf` | `1d6db15bf3d8344a909dcecb35213fa0ae80e931bd34fe442efdef70596ccf2d` |
| `FarmMarketSystem_Team/FarmMarketSystem/app.py` | `app/app.py` | `fe55f47e94d92ad03d7d4449cce26d81532e86126681ccb278ce728666e1bfc2` |
| `FarmMarketSystem_Team/FarmMarketSystem/assistant.py` | `app/assistant.py` | `e3061a7939839206d7ec4282e997bde31330c5f1283713464747f2fec8e91a32` |
| `FarmMarketSystem_Team/FarmMarketSystem/db.py` | `app/db.py` | `4f4d45cfe41aa3147b72816b799c259502f18e5dbddb82e25d8694c8051c8da6` |
| `FarmMarketSystem_Team/FarmMarketSystem/requirements.txt` | `app/requirements.txt` | `386c35d4bd5dc487e08a348f8f45ed252cbf4e799afee33a961103c4e5878c4e` |
| `FarmMarketSystem_Team/FarmMarketSystem/run.bat` | `app/run.bat` | `01932e3c88176b9ba7a457c3aa98142930d265bfb3067f84ac3625e6c352fd91` |
| `FarmMarketSystem_Team/FarmMarketSystem/sample_images/bell_pepper.jpg` | `app/sample_images/bell_pepper.jpg` | `88a6cfc58176871df8ff1f6661d85dfec60c4aea6a4e5cf8076dd2a6ef1a32c0` |
| `FarmMarketSystem_Team/FarmMarketSystem/sample_images/cucumber.jpg` | `app/sample_images/cucumber.jpg` | `3c74bce72aef8b8f72df4dad099c5e97321166b09f2d3060a15aac0d4dcd594d` |
| `FarmMarketSystem_Team/FarmMarketSystem/sample_images/eggplant.jpg` | `app/sample_images/eggplant.jpg` | `dd3696cf02dd657bfe1979d33c40664980a97bf95ddc0d1deb5565fa4506676a` |
| `FarmMarketSystem_Team/FarmMarketSystem/sample_images/zucchini.jpg` | `app/sample_images/zucchini.jpg` | `89ad8bc9423f74b446c54ccc99d843c70eab81baf53d2218d64a3394c0ec57bb` |
| `FarmMarketSystem_Team/FarmMarketSystem/schema.sql` | `app/schema.sql` | `b038c2fb29051f074ce2f48f57f79e1d522bd04cc4cd545e4ad5f0a807aa68c7` |
| `FarmMarketSystem_Team/FarmMarketSystem/setup.bat` | `app/setup.bat` | `97fa20501dd2c19b4ff7351d134f84e077e71be34937dcdc813087789e90801f` |
| `FarmMarketSystem_Team/FarmMarketSystem/setup_database.py` | `app/setup_database.py` | `5a325c94c9a1aa4b8b3b9db2ed82115a693af4d0de4f67f04fb1958335190364` |
| `FarmMarketSystem_Team/FarmMarketSystem/tests/test_business_rules.py` | `app/tests/test_business_rules.py` | `2d79c9764e8c3674faadd3259e5cd743ff4ccd91e05e3a9de06041010069583e` |
| `Local_Farm_Market_Food_Availability_Project_Proposal.pdf` | `docs/sources/Local_Farm_Market_Food_Availability_Project_Proposal.pdf` | `1857c1da4b0ef1a59e74476c5eade2bfbc126a64c08794dbeb582b9d55b4b417` |
| `application.py` | `archive/lab-example/application.py` | `4e4c475f037b59a9dc183c55326846380507333de8818c5190872f27bce98b42` |
| `data.sql` | `archive/lab-example/data.sql` | `de0c04e0b6bcf9ad727a5b41792ebb7713fe4cf232fbe33119b7f2929e22b72b` |
| `langchain.pptx` | `docs/sources/langchain.pptx` | `fed0cd084b0d146e8fa5a5c940bed11cf1d56fec2877f14c77d8ec25a1450d53` |
| `schema.sql` | `archive/lab-example/schema.sql` | `8034612497ee1fbf7905b0d7bbef365d4dcc702c0a55ad38fe1154703d8f9c0d` |

## Evidence boundaries

Root README, product/design specifications, agent guidance, root launchers, documentation, and ignore rules are new. Original application Python, SQL, configuration template, requirements, batch files, tests and photos remain unchanged. Original README/guide paths are historical and intentionally preserved rather than rewritten. The original ZIP remains a baseline, not a newly verified final submission package.
