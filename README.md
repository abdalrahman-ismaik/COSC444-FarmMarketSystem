# Farm-to-Market

**COSC444 Database Systems | Khalifa University | Lab B1 | Fall 2026–2027**

A Python desktop application for local produce availability. Farmers record crop cycles, harvests and photos; market buyers request supply and confirm deliveries; administrators maintain reference data and assignments. MySQL stores movement-based inventory, reservations and receipts. **Loss & Surplus** supports donation and disposal, and a read-only LangChain/Gemini assistant answers database questions.

[![Farm-to-Market project poster](https://raw.githubusercontent.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/release/final-submission-report/docs/poster/poster-preview.png)](submission/COSC444_Farm-to-market_Poster.pdf)

## Downloads

| Deliverable | File |
|---|---|
| Application, populated SQL, images, poster and setup instructions | [FarmMarketSystem_B1_Submission.zip](submission/FarmMarketSystem_B1_Submission.zip) |
| Final technical report | [FarmMarketSystem_B1_Technical_Report.pdf](submission/FarmMarketSystem_B1_Technical_Report.pdf) |
| Poster | [COSC444_Farm-to-market_Poster.pdf](submission/COSC444_Farm-to-market_Poster.pdf) |
| Editable LaTeX report with figures and PDF | [FarmMarketSystem_B1_Technical_Report_Source.zip](submission/FarmMarketSystem_B1_Technical_Report_Source.zip) |

The GitHub application files match the application ZIP. The technical report and its editable bundle are supplied alongside it. When reading this README from the extracted application ZIP, download the report separately from the [GitHub submission folder](https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/tree/release/final-submission-report/submission). Supporting diagrams, document sources and verification records are under `docs/` in GitHub.

## Setup and run on Windows

Requirements: Windows 10/11, Python 3.12 with Tkinter, a running MySQL 8 server and its credentials. Live assistant answers additionally require internet access and a Gemini API key. Python packages are installed during setup; Python and MySQL are installed separately.

1. Extract the application ZIP, or clone this repository. Confirm `python --version` and `python -m tkinter` work.
2. Run **setup.bat** from the project root. It installs `app/requirements.txt`, creates `app/.env` if needed, and loads the SQL sample database. Enter your own MySQL connection settings.
3. Run **run.bat** and select a demo user. The launcher checks the database connection first. If MySQL is unavailable, start the configured server, check `DB_HOST` and `DB_PORT`, and press **R** to retry.

**Setup recreates `farm_market_db`, replacing its existing data.** Run setup only for initial installation or an intentional reset. Normal launches preserve records and BLOB photos. The SQL targets `farm_market_db`; changing `DB_NAME` alone does not retarget setup.

Manual alternative from the project root:

```powershell
python -m pip install -r app/requirements.txt
Copy-Item app/.env.example app/.env  # First setup only
notepad app/.env
python app/setup_database.py
python app/app.py
```

Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `GEMINI_API_KEY` and `GEMINI_MODEL` in `app/.env`. Never commit real credentials. Each device needs its own database installation and configuration. An existing project `.venv` is preferred by the batch launchers; the original PC's ignored database-start helper is optional and is not distributed.

## Code and required libraries

| File | Role |
|---|---|
| `app/app.py` | Tkinter/ttk role interfaces, forms, tables and background assistant work |
| `app/db.py` | PyMySQL access, validation, ownership, transactions and stock operations |
| `app/assistant.py` | LangChain/Gemini question processing and read-only SQL execution |
| `app/schema.sql` | Complete MySQL schema, views, constraints and populated fictional sample data |
| `app/setup_database.py` | Database initialization from the SQL script |
| `app/check_database.py` | Launcher connection preflight and readable failure messages |
| `app/requirements.txt` | Required third-party Python packages |
| `app/.env.example` | Configuration template without credentials |
| `app/sample_images/` | Four example JPEGs for upload; seeded photos also reside in SQL BLOBs |
| `app/tests/` | Business-rule, validation, GUI-flow and read-only assistant checks |
| `setup.bat`, `run.bat` | Root entry points delegating to the application launchers |

Required pip packages: **PyMySQL**, **cryptography**, **python-dotenv**, **Pillow**, **langchain-core** and **langchain-google-genai**. Tkinter comes with the Python installation and MySQL runs as a separate service. Install packages using `app/requirements.txt`.

## Demo roles

| Role | Sample identity | Main workflow |
|---|---|---|
| Farmer | Omar Saeed, Fatima Rashid or Khalid Nasser | Crop cycles, harvests/photos, allocations, stock and surplus disposition |
| Market buyer | Aisha Salem, Yousef Ali, Noura Ahmed or Hamad Obaid | Search supply, submit requests and confirm delivery discrepancies |
| Administrator | Layla Hassan | Users, farm assignments, reference data and operational review |

All operational data is fictional. The identity selector supports the course demonstration; it is not password authentication. Operational writes check ownership; shared search and assistant reads cover shared operational records. The assistant uses a read-only transaction; its validation boundaries and dated tests are documented below.

## Supporting documentation

- [Requirements and business rules](docs/PROJECT_REQUIREMENTS.md) and [rubric coverage](docs/RUBRIC_AND_COVERAGE.md)
- [Architecture](docs/ARCHITECTURE.md), [database design](docs/DATABASE_DESIGN.md) and [editable ER/schema diagrams](docs/diagrams/)
- [Report source and build instructions](docs/BUILD_DOCUMENTS.md)
- [Testing and dated evidence](docs/TESTING.md), [assistant validation](docs/evidence/AI_VALIDATION.md)
- [Demo and submission guide](docs/DEMO_AND_SUBMISSION.md), [demo script](docs/DEMO_SCRIPT.md)
- [Package inventory and hashes](submission/MANIFEST.md), [image attribution](docs/IMAGE_ATTRIBUTION.md)

The database tests mutate data and assume a disposable seeded database. Do not run setup or mutating tests against records you need to retain. Document/package verification does not rerun application or model tests.

## Team

| Member | Student ID |
|---|---|
| Abd Alrahman Ismaik | 100064692 |
| Ali Alshamsi | 100062530 |
| Mohammad Arwani | 100064908 |
