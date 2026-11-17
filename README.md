# Farm-to-Market

**COSC444 Database Systems · Fall 2026–2027 · Khalifa University · Lab B1**

A Python desktop prototype that connects local farms and markets through harvest inventory, supply requests, allocations, and delivery receipts. MySQL is the source of truth; the GUI includes product photos and a read-only LangChain assistant powered by Gemini. The selected advanced feature is **Loss & Surplus management**.

All operational sample data is fictional. This educational system does not represent government systems, national reserves, or complete UAE production.

| Team member | Student ID |
|---|---|
| Abd Alrahman Ismaik | 100064692 |
| Ali Alshamsi | 100062530 |
| Mohammad Arwani | 100064908 |

Repository: [abdalrahman-ismaik/COSC444-FarmMarketSystem](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem).

## Setup and run on Windows

Prerequisites: Windows 10/11, Python with Tkinter, a running MySQL 8 server, and its database credentials. The supplied application states Python 3.10+ support; dependency installation on that minimum version has not been revalidated. A Gemini API key and internet access are required for live assistant answers, but not for the other workflows.

1. Open a terminal in this project folder. Confirm `python --version` and `python -m tkinter` work.
2. Double-click **setup.bat**, or run `.\setup.bat` in PowerShell. Setup installs `app/requirements.txt`, creates `app/.env` if missing, and loads sample data. Enter your MySQL settings; the Gemini key can be added later.
3. Double-click **run.bat**, or run `.\run.bat`. Choose a specific demo user to open their role's screens.

**Database reset:** setup runs SQL that drops and recreates `farm_market_db`. Use it only when you intend to discard that database's current records. Restarting the app with `run.bat` does not reset data. Do not rerun setup between uploading a photo and demonstrating persistence after restart.

Manual alternative from the repository root:

```powershell
python -m pip install -r app/requirements.txt
Copy-Item app/.env.example app/.env
notepad app/.env
python app/setup_database.py
python app/app.py
```

Copy the configuration template only on first setup. Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `GEMINI_API_KEY`, and `GEMINI_MODEL` in `app/.env`. Keep real credentials out of version control. The supplied SQL and setup script target `farm_market_db`; changing `DB_NAME` alone does not retarget setup. The default is `gemini-3.1-flash-lite`, verified with this project's key on November 17, 2026. The previous `gemini-2.5-flash` returned a model-access 404; availability/quota can vary by account and date.

For MySQL Workbench setup, execute **app/schema.sql**, not the archived school-database scripts. Dependencies are PyMySQL, cryptography, python-dotenv, Pillow, langchain-core, and langchain-google-genai. No additional GUI framework is needed.

## Workflows and demo users

| Role | Demo user | Main capabilities |
|---|---|---|
| Farmer | Omar Saeed | Green Oasis and Desert Bloom farms; cycles, harvests, photos, stock movements, allocations, donations/disposals |
| Farmer | Fatima Rashid | Al Dhaid Fresh Farm; same farmer workflows |
| Farmer | Khalid Nasser | Hatta Valley Farm; same farmer workflows |
| Market buyer | Aisha Salem / Yousef Ali / Noura Ahmed / Hamad Obaid | One market each; search, requests, delivery confirmation and discrepancies |
| Administrator | Layla Hassan | Users, farm assignments, reference data, and operational review |

Demo users are fictional application accounts, distinct from the student team. User selection is a demonstration mechanism, not password authentication. Shared search and assistant screens expose operational records; ownership checks restrict changes. Administrators do not directly edit operational transactions.

## Repository map

```text
app/                     Maintained application, SQL, configuration template, tests, photos
docs/                    Requirements, rubric, architecture, tests, demo and team documents
  sources/               Original project proposal and Lab 6 slides
  reference/             Historical visual guide
archive/                 Original ZIP/README and school-database lab example
.agents/skills/          Reusable project-local skills copied from KU Planner
README.md                Setup, run, status, and documentation entry point
PRODUCT.md               Product purpose, users, constraints, and evidence
DESIGN.md                Existing desktop theme and future refinement criteria
AGENTS.md                Instructions for future repository work
setup.bat / run.bat      Root launchers that delegate to app/
```

## Documentation

- **Teammates start here:** [handoff and remaining work](docs/TEAMMATE_HANDOFF.md), [copy-paste Claude assignments](docs/CLAUDE_TASK_PROMPTS.md), and [progress/review ledger](PROGRESS.md).
- [Requirements and business rules](docs/PROJECT_REQUIREMENTS.md)
- [100-point rubric and coverage matrix](docs/RUBRIC_AND_COVERAGE.md)
- [Course announcements and deadlines](docs/ANNOUNCEMENTS.md)
- [Architecture, database, and transactions](docs/ARCHITECTURE.md)
- [Test plan and evidence](docs/TESTING.md)
- [Demo runbook and submission checklist](docs/DEMO_AND_SUBMISSION.md)
- [Team responsibilities](docs/TEAM.md)
- [Repository review and original-file inventory](docs/REPOSITORY_REVIEW.md)
- [Skills and provenance](docs/SKILLS.md)
- [GitHub upload readiness and remaining tasks](docs/GITHUB_READINESS.md)
- [Original proposal](docs/sources/Local_Farm_Market_Food_Availability_Project_Proposal.pdf), [Lab 6 slides](docs/sources/langchain.pptx), and [historical visual guide](docs/reference/Visual_Guide.pdf)

## Verification status

**Current local result: 65/65 business-rule checks passed on isolated MySQL 8.0.46**, plus 18 Windows role-tab checks, GUI valid/invalid harvest submission, and photo retrieval after a full GUI process restart. The actual [validation report and screenshots](docs/evidence/VALIDATION.md) distinguish these results from historical guide claims. On November 17, **fourteen live Gemini questions and two GUI AI checks were verified**, after correcting an observed crop-filter omission and the obsolete model configuration. See the [live AI report](docs/evidence/AI_VALIDATION.md) for initial failures, retests, reference SQL, and remaining limits.

On this PC, the isolated demo database is running on port 3307 and the app is configured locally. Double-click root **run.bat** to explore. After reboot, follow the local-server restart instructions in the validation report. The batch launchers prefer the project `.venv` when present. A fresh GitHub clone still needs the setup instructions above and its own database credentials.

The existing business-rule script changes database records and assumes fresh seed data:

```powershell
python app/tests/test_business_rules.py
```

Run it only against a disposable `farm_market_db` configured in `app/.env`. Restore sample data afterward only if a reset is intended. The script is not a complete replacement for GUI, restart, assistant-answer, or rubric acceptance testing.

**Still required for final submission:** conceptual Draw.io ER diagram, separate relational schema diagram, poster PDF, concise technical PDF with expected/actual test evidence, and verification of team registration/demo booking. Markdown documentation and the historical guide do not substitute for those assessed artifacts.

## Troubleshooting

| Symptom | Action |
|---|---|
| Python/packages unavailable | Check Python is on PATH; run `python -m pip install -r app/requirements.txt` |
| Tkinter unavailable | Install a Python distribution with Tcl/Tk support |
| Database login failed | Correct `DB_USER` and `DB_PASSWORD` in `app/.env` |
| Cannot reach MySQL | Start the configured MySQL service and check host/port; its service name can vary |
| Database not found | Initialize with setup only after confirming the reset target |
| Assistant has no key / service unavailable | Set a valid key and accessible model in `app/.env`, check connectivity, then restart |
| No records / missing photo | Check filters and selected lot; the application provides empty and unavailable-image states |

Sample produce photos are attributed by the supplied package to Fruits-360 under CC BY-SA 4.0. See [sources and attribution](docs/SKILLS.md#sample-image-attribution); exact upstream image provenance remains to be verified.

## Track B review draft on 17 November 2026

Mohammad's [technical report](submission/technical-report.pdf) and [poster](submission/poster.pdf) now exist as review drafts, with [editable sources and build/visual-check instructions](docs/BUILD_DOCUMENTS.md). They include the real, pinned diagrams and newer test findings from [Track A PR #2](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/2), including concurrent overselling and GUI/image defects. This supersedes the earlier “PDFs missing” artifact status above; it does not turn those findings into passes. Both tracks await Abd Alrahman's review. See [Track B review](docs/reviews/TRACK_B_REVIEW.md) and [image attribution gaps](docs/IMAGE_ATTRIBUTION.md). Candidate ZIP creation remains blocked on the review dependencies.
