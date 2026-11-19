# Local runtime validation — November 16, 2026

This records tests actually executed on Windows in this workspace. It supersedes earlier statements that only historical MySQL evidence was available. It is representative validation, not completion of every acceptance case in the test plan.

**November 17 update:** [live AI validation](AI_VALIDATION.md) now documents fourteen live Gemini questions and two Ask AI GUI checks, including fixes/retests and limitations. The no-key/stand-in entries below describe the November 16 run only. Assistant model defaults/prompt/timeout and setup defaults have since changed; the original baseline-preservation statements below are historical.

## Environment and isolation

- Python **3.12.12**, project `.venv`, Windows/Tkinter desktop.
- MySQL **8.0.46**, isolated process listening on **127.0.0.1:3307**, MySQL X disabled. The existing service on port 3306 was not reset or used for these tests.
- SQL mode: `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION`.
- Transaction isolation: **REPEATABLE-READ**.
- Package versions: PyMySQL 1.2.4, cryptography 50.0.2, python-dotenv 1.2.4, Pillow 13.0.0, langchain-core 1.8.1, langchain-google-genai 4.5.0.
- Generated local database credentials are stored only in ignored `app/.env` and `.local/` files. No Gemini key was supplied. Environment/dependency minimum versions were not exhaustively checked.

## Observed results

| Check | Expected | Actual result |
|---|---|---|
| SQL creation and population | Schema and seed load on clean MySQL | **Pass:** 49 statements; setup reported 4 farms, 13 lots, 9 requests, 12 photos |
| Existing business-rule suite | Valid workflows succeed; invalid stock/ownership/date/unit/repeated operations fail | **65/65 passed locally** using `app/tests/test_business_rules.py` |
| Inventory and forecasts | Correct movements; expected harvest not counted as available | **Pass:** existing suite harvest/reservation/release/delivery/loss/correction-related stock assertions and forecast separation |
| Partial delivery | 78 allocated, 70 received, discrepancy 8; release/loss and request status persisted | **Pass:** suite verified receipt, balances and PARTIALLY_DELIVERED status |
| Concurrent allocations | Prevent overselling when separate threads race for same lot | **Pass:** existing three-thread scenario; not proof of all concurrency interleavings |
| Loss & Surplus | Priority query, invalid threshold/excess quantity rejection, two actions and stock integrity | **Pass:** existing suite flag, donate, dispose, ownership/reserved-stock checks |
| Invalid database connection | Friendly failure for wrong password or unavailable port | **Pass:** both existing suite cases |
| GUI role screens | Every role tab constructs and refreshes without errors | **Pass:** farmer 7, buyer 5, administrator 6; **18 tabs total**, with no intercepted error dialogs or Tk callback errors |
| GUI invalid harvest | Negative quantity rejected without new lot | **Pass:** actual form submission showed negative-quantity error; lot count unchanged |
| GUI valid harvest/photo | Form creates 5 kg Cucumber harvest with JPG BLOB | **Pass:** lot #14 had 5 available and one stored image |
| Full GUI process restart | Same uploaded image retrieved and rendered | **Pass:** separate GUI process rendered lot #14 BLOB; image byte count unchanged |
| Buyer photo and advanced-feature screens | Render stored photo and flag/history views | **Pass:** buyer loaded lot #2 image; Loss & Surplus view rendered |
| LangChain integration with deterministic model | Supported query executes against actual SQL; clarification/unsupported/unsafe outputs handled | **Pass:** four response paths tested using `FakeListLLM`; supported query returned lot #2 at 78 kg |
| Database-enforced read-only execution | MySQL rejects a write within read-only transaction | **Pass:** attempted DELETE refused with error 1792; no write performed |
| Missing Gemini key | Friendly configuration error | **Pass:** actual no-key path returned API-key message |
| Live Gemini accuracy | Model generates correct answer from natural language | **Not tested:** no key; stand-in results are not live model evidence |
| Root run launcher | Uses installed project environment and opens real GUI | **Pass:** root `run.bat` executed successfully after launcher update; app left open for manual exploration |

The suite's SQL guard cases treat any raised exception as a pass and therefore provide limited error-type evidence. Direct assistant integration and database read-only checks supplement those cases. This is not an independent audit of every suite assertion.

## Screenshots

- [User selector](gui-user-selector.png)
- [Farmer harvest/stock](gui-farmer.png)
- [Uploaded image after restart](gui-image-after-restart.png)
- [Market search and product image](gui-market.png)
- [Loss & Surplus](gui-loss-surplus.png)

These are actual Windows GUI captures with fictional data, not mockups. GUI automation invoked Tk widgets and callbacks directly; it was not a full manual mouse/keyboard usability test.

## Try it on this PC

The isolated demo server is left running. Double-click the root **run.bat**. The launchers prefer `.venv/Scripts/python.exe` when the project virtual environment exists, and otherwise use Python on PATH.

1. Choose **Omar Saeed**, then **Harvest & Stock**. Lot #14 contains the 5 kg Cucumber/photo created during validation.
2. Select lots to view images; open **Loss & Surplus** to inspect flagged lots and actions.
3. Switch to **Noura Ahmed** to search produce, make requests, and inspect deliveries.
4. Use the [corrected demo runbook](../DEMO_AND_SUBMISSION.md) for allocation and partial-delivery steps. This database is fresh seed plus the GUI-created lot; lot #2 remains 78 kg available and request #7 remains OPEN.
5. For live AI, edit ignored `app/.env`, set your own `GEMINI_API_KEY`, then restart the app. Do not post the key in GitHub or evidence.

After a reboot, root `run.bat` detects that this temporary MySQL process is stopped, runs the ignored local helper, waits five seconds, and checks the connection again. To start it manually instead:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .local/start-demo.ps1
```

The helper/data/password are local-only, not part of a fresh GitHub clone. Other PCs must follow the root README setup instructions with their own MySQL installation and credentials. Setup/reset destroys the configured demo schema; do not reset while demonstrating photo persistence.

## Still to validate

Live Gemini questions (at least ten against independent SQL); GUI end-to-end request/allocation/delivery via widgets; broader rollback and concurrency races; complete threshold/image-boundary matrix; user-switch while AI is pending; keyboard/focus/display-scaling accessibility; and a timed three-person presentation. The 65 checks plus GUI smoke test do not complete all rubric evidence.

Application Python/SQL/images remain unchanged. `app/run.bat` and `app/setup.bat` now prefer the project virtual environment; those two files intentionally differ from the archived baseline. No credentials/runtime data are included in the evidence or staged for Git.
