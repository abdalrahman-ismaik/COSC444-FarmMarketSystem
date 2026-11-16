# Farm-to-Market
Local Farm and Market Food Availability System — COSC444 Database Systems project.
Python + MySQL + Tkinter desktop GUI + LangChain (Google Gemini).

## What you need
- Windows 10/11
- MySQL Server 8 (MySQL Installer → "Server only"; remember your root password)
- Python 3.10 or newer (tick **"Add python.exe to PATH"** when installing)
- A free Gemini API key from aistudio.google.com (only needed for the Ask AI tab)

## Run it (3 steps)
1. Unzip the `FarmMarketSystem` folder (e.g. on your Desktop).
2. Double-click **setup.bat**
   - installs the packages from `requirements.txt`
   - asks for your MySQL password and Gemini key and saves them in `.env`
   - creates the `farm_market_db` database with sample data and photos
3. Double-click **run.bat** → choose a demo user.

Run **setup.bat** again any time to reset the sample data (do this before the live demo).

### Manual way
```
pip install -r requirements.txt
copy .env.example .env        (then edit DB_PASSWORD and GEMINI_API_KEY)
python setup_database.py      (or run schema.sql in MySQL Workbench)
python app.py
```

## Demo users
| Role | User | Owns |
|---|---|---|
| Farmer | Omar Saeed | Green Oasis Farm, Desert Bloom Farm |
| Farmer | Fatima Rashid | Al Dhaid Fresh Farm |
| Farmer | Khalid Nasser | Hatta Valley Farm |
| Market buyer | Aisha Salem / Yousef Ali / Noura Ahmed / Hamad Obaid | one market each |
| Administrator | Layla Hassan | reference data |

## Files
| File | Purpose |
|---|---|
| `app.py` | Desktop GUI (Tkinter) |
| `db.py` | Database access, business rules, transactions |
| `assistant.py` | LangChain + Gemini read-only assistant |
| `schema.sql` | Creates and populates the database (photos stored as BLOBs) |
| `setup_database.py`, `setup.bat`, `run.bat` | One-click setup and start |
| `sample_images/` | Real produce photos for the upload demo (Fruits-360, CC BY-SA 4.0) |
| `tests/test_business_rules.py` | 65 automated tests (`python tests\test_business_rules.py`, then re-run setup) |
| `Visual_Guide.pdf` | Screenshots, demo walkthrough, requirements coverage |

## Advanced feature: Loss & Surplus management
SQL rules (thresholds adjustable in the GUI):
- **Expired**: available > 0 and sell-by date before today (priority 1)
- **Near expiry**: available > 0 and sell-by within N days (priority 2)
- **Unallocated surplus**: available > 0, never allocated, harvested ≥ M days ago (priority 3)

Actions: **Donate** or **Dispose** (recorded as stock movements with user, date and reason; only unreserved stock).

## Stock formula (from `stock_movements`)
- on hand = harvest added + corrections − delivered − loss − donated − disposed
- reserved = reserved − released − delivered
- available = on hand − reserved
- Expected harvest (crop cycles) is a forecast and is never added to stock.

## Troubleshooting
| Message | Fix |
|---|---|
| Database login failed | Fix `DB_PASSWORD` in `.env` |
| Cannot reach the MySQL server | Start the MySQL80 service |
| The database was not found | Run `setup.bat` |
| Packages are missing | Run `setup.bat` |
| Add your GEMINI_API_KEY | Put your key in `.env` and restart |

All data is fictional (educational prototype).
