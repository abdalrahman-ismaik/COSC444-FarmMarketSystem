# Demo runbook and submission checklist

**Time limit:** fifteen minutes total, approximately three for the poster and twelve for live demonstration/questions. **Submission:** Thursday, November 19, 2026; cutoff time not provided. Abd Alrahman reports all three members are registered and the demo is booked for **1:30 PM**. Confirm the sheet entries, venue and attendance using the [announcement links](ANNOUNCEMENTS.md). All three members must attend unless officially excused.

## Preparation before the booked slot

Use the [approved poster](../submission/COSC444_Farm-to-market_Poster.pdf) for the three-minute overview and the [ready-to-read demo script](DEMO_SCRIPT.md) for the fifteen-minute sequence. The [screenshot GUI walkthrough](notebooklm/GUI_Walkthrough.pdf) is dated evidence. Use the live script for AI and invalid-input demonstrations.

- Confirm the booked 1:30 PM slot and venue, verify projector/power, Python/Tkinter/MySQL, dependencies, and a working live Gemini key/model. The team reports all three members registered.
- Rehearse on the Windows demo machine. Have source/SQL and final PDFs locally accessible.
- Reset **only the intended disposable/demo database** before rehearsal/demo if needed. Setup drops `farm_market_db`; never reset between the image upload and restart demonstration.
- Confirm fresh-seed lot #2 has 78 kg Tomato available, lot #13 has 120 kg Tomato, lot #3 has 40 kg past-sell-by Cucumber available, and lot #12 has 40 in-date Dates boxes available and flagged as surplus. Verify actual balances and flags before starting; the demo database may have been changed by earlier runs.
- Use fictional accounts Omar Saeed, Fatima Rashid, and Noura Ahmed; these are not student identities.
- Open the poster and start screen before the slot begins. Do not install packages or debug credentials during the assessed fifteen minutes.

## Poster: 0:00–3:00

| Time | Proposed speaker | Content |
|---|---|---|
| 0:00–1:00 | Abd Alrahman Ismaik | Context, prototype objective, actors, and central business rules: forecast vs stock, units, ownership, no over-allocation |
| 1:00–2:00 | Ali Alshamsi | Conceptual ER and relational mapping, stock movements, reservation/delivery transactions and integrity |
| 2:00–3:00 | Mohammad Arwani | System flow, GUI/images/LangChain, Loss & Surplus, and transition to demo |

These assignments are proposals. Every member must understand the complete solution, regardless of speaker ownership.

## Live demo and questions: 3:00–15:00

This sequence corrects the historical guide's dependency problem: **create allocations before confirming their deliveries**. Record actual generated IDs instead of assuming a new ID.

| Time | Action | Observable evidence |
|---|---|---|
| 3:00–4:45 | Omar → Harvest & Stock → record 50 kg on cycle #2 (Cucumber), today's date and a future sell-by; upload `app/sample_images/cucumber.jpg`. Note new lot ID. Close the application completely and relaunch with root `run.bat`; select the same lot. | New lot, HARVEST_ADDED and photo; same database photo after restart; no setup/reset in between |
| 4:45–6:00 | Noura → Find Produce → filter Tomato and an availability date/quantity; inspect a product image. Request 120 kg Tomato with a future needed-by date. Note the new request ID. | Search results and image; newly persisted OPEN request owned by Sharjah Souq Market |
| 6:00–7:30 | Omar → Allocate to Markets → select that request and lot #2. Try 100 kg; show rejection. Allocate 78 kg instead. Switch to Fatima and allocate remaining 42 kg from lot #13 to the same request. | Friendly over-allocation prevention, no failed write, two valid reservations, fully allocated request |
| 7:30–8:45 | Noura → Deliveries → select the new 78 kg allocation from lot #2. Confirm 70 kg received with reason “8 kg damaged in transport.” Inspect receipt and request. | Receipt 78 allocated / 70 received / 8 discrepancy; delivery/release/loss movements; other 42 kg remains reserved; request PARTIALLY_DELIVERED |
| 8:45–10:15 | Ask AI: “Which deliveries had a shortfall, and by how much?” Then “How much is available?” or an unsupported weather question. | Live supported answer with supporting records; clarification or unsupported response; read-only behavior |
| 10:15–12:00 | Omar → Loss & Surplus → show the 3-day default / 7-day surplus threshold and past-sell-by lot #3; explain the poster's 5-day near-expiry example is configurable. Switch to Fatima and donate 25 boxes from in-date surplus lot #12 to “Demo food bank.” Switch back to Omar and dispose of the 40 kg remaining on lot #3. Show both history rows. | In-date donation and past-sell-by disposal are separately recorded with actor/time/reason; availability changes only for the selected lots. Do not demonstrate the new rejection until its pending regression check has been run. |
| 12:00–13:00 | Try threshold “abc” or a negative harvest quantity. Show clear error and unchanged data. | Friendly invalid-input response; no crash or partial write |
| 13:00–15:00 | Questions and brief database/schema explanation as requested | All members explain decisions, transactions, units, status policy and selected feature |

Do not read scripted answer claims if the observed database differs. If the assistant is unavailable, disclose it and explain the failure state; historical stand-in screenshots do not fulfill a live supported-answer demonstration. Rehearse a shorter pace so questions fit within the allotted time.

## Poster content checklist

- [ ] Project introduction: UAE local-food context, educational prototype, fictional/public data.
- [ ] Core business rules and three roles.
- [ ] System overview/design showing how workflows connect.
- [ ] Core GUI, photo, and LangChain features.
- [ ] Selected Loss & Surplus feature, thresholds, donation and disposal.
- [ ] Database design, including the final conceptual ER diagram.
- [ ] Course, lab B1, all member names and IDs.
- [ ] Digital PDF readable when projected; approximately three-minute explanation.

## Required diagrams and technical PDF

- [x] Conceptual ER diagram in Draw.io: entities, relationships, cardinalities and rules; accepted by Abd Alrahman.
- [x] Separate relational schema diagram: SQL tables, PK/FK, types and constraints; accepted by Abd Alrahman.
- [x] Technical PDF includes both diagrams, rules, transactions and expected/actual test evidence; accepted by Abd Alrahman.
- [x] Test evidence covers major workflows, boundaries/concurrency, stock/forecast separation, images/GUI, Loss & Surplus and fourteen assistant questions including ambiguous/unanswerable cases.
- [x] Report distinguishes live Gemini evidence, stand-ins, historical results and follow-up observations.
- [x] Reviewer acceptance recorded for diagrams, report, poster, and package.
- [ ] Final projector check, timed three-person rehearsal, and course upload.

Suggested technical PDF order: introduction/team; conceptual and relational designs; rules and transaction explanations; compact completed test evidence; limitations and references. Screenshots are not required by the proposal. Abd Alrahman Ismaik approved the replacement poster on 2026-11-19; the prior `submission/poster.pdf` was removed. The projector check, rehearsal, and course upload remain.

## Accepted ZIP package

The accepted ZIP and SHA-256 manifest are under `submission/`. The team must complete projector/rehearsal checks and upload through the course process. The preserved original ZIP is archival input, not the current submission.

| Include | Intended source / destination |
|---|---|
| README with setup/run and required packages | Root README plus `app/requirements.txt` |
| All maintained Python source and batch launchers | `app/` and root launchers |
| Final SQL creation/population script | `app/schema.sql` |
| Configuration example, no secrets | `app/.env.example`; exclude `.env` |
| Upload-demo images and attribution | `app/sample_images/` plus attribution notes; stored product images are already embedded in SQL |
| Concise technical PDF and poster PDF | `submission/FarmMarketSystem_B1_Technical_Report.pdf` and `submission/COSC444_Farm-to-market_Poster.pdf` |
| Diagram sources/exports and evidence | Future `docs/diagrams/` and completed test evidence, alongside final PDFs as useful supporting material |

Exclude virtual environments, caches, logs/secrets, development-only skill bundles, archived lab examples, and the original ZIP from the final submission ZIP unless the instructor explicitly asks for them. Preserve them in the working repository. Extract the final ZIP into a fresh folder and verify setup paths, run paths, SQL, and PDF readability before submission.
