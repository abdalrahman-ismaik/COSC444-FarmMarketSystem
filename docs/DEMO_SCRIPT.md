# COSC444 Farm-to-Market demo script

**Team:** Lab B1 · **Hard limit:** 15 minutes · **Format:** about 3 minutes on the digital poster, then about 12 minutes for the live GUI and questions.

Use this as a speaking guide, not a promise about live data. Before the panel arrives, open the approved [poster](../submission/COSC444_Farm-to-market_Poster.pdf), start the app with the root `run.bat`, and verify the demo database contents and balances. Do not run `setup.bat` during the demo: it drops and recreates `farm_market_db`. Do not reset between uploading a harvest photo and showing it after restart. If seeded IDs or balances differ, use the live records and adjust quantities while preserving the same workflow.

The poster uses **5 days** as a configurable near-expiry example. The app's default is **3 days**, and the accepted range is 0–60 days. State that distinction if asked. Donation of past-sell-by lots is blocked by the team's conservative app policy; this is not a food-safety determination and was not specified by the proposal. For the feature demo, donate in-date surplus and dispose of the past-sell-by lot.

## Before the 15-minute slot

- Confirm venue, projector, power, all three members, and the actually booked date/time. The repository records a reported November 19, 2026, 1:30 PM booking; confirm if the booking changed.
- Open the poster PDF full-screen. Keep the GUI ready at the user selector.
- Confirm MySQL is available, the Gemini key/model works if demonstrating live AI, and the expected demo users can be selected.
- Check the data in the GUI: Cucumber cycle #2 can accept a 50 kg harvest; Tomato lot #2 and lot #13 have the needed balances/owners; Cucumber lot #3 is past sell-by with 40 kg available; Dates lot #12 is in-date surplus with 40 boxes available. These are expected seed examples, not guaranteed current balances.
- Keep the existing documented GUI walkthrough and technical report available locally. Do not expose `.env`, keys, passwords, or student accounts in the demo.

## 0:00–3:00 · Poster overview

### 0:00–1:00 · Abd Alrahman Ismaik

> “Our project is Farm-to-Market, a COSC444 database systems prototype for making local produce availability easier to record and find. Farmers record crop cycles and harvested lots; market buyers search available stock and submit requests; farmers reserve stock; buyers confirm deliveries and record discrepancies. The application demonstrates database workflows using fictional sample records. Its central rules are that forecast is separate from actual stock, units stay explicit, farmers act on their own farm records, and reserved stock cannot be promised twice.”

Point to project context, user roles, and the stock calculation. Explain that `available` means on-hand stock after reservations.

### 1:00–2:00 · Ali Alshamsi

> “This ER view connects farms to crop cycles and harvest lots, then markets to requests, allocations, and delivery receipts. The 1 and N labels show relationship cardinality. The relational schema maps those concepts into tables with primary and foreign keys and constraints. Stock changes are recorded as movements, so harvest, reservation, release, delivery, loss, donation, and disposal remain explainable. Related allocation and delivery changes run in transactions, with row locking to protect availability.”

Point to the ER diagram and schema-mapping summary. Keep detailed symbol explanation for questions.

### 2:00–3:00 · Mohammad Arwani

> “The desktop app uses Tkinter, Python database logic, and MySQL. It also stores product photos in the database and has a read-only LangChain assistant for supported questions. Our selected advanced feature is Loss & Surplus: it flags expired, near-expiry, and ageing unallocated stock and records a disposition. Thresholds can be changed; the app defaults to three near-expiry days and seven surplus days. We will show harvest and photo persistence, buyer request, safe allocation, partial delivery, the assistant, and the advanced feature.”

Transition directly to the app. The poster's five-day value is a configurable example; do not describe it as the default.

## 3:00–15:00 · Live GUI walkthrough

### 3:00–4:30 · Farmer harvest and photo persistence · Abd

1. Select farmer **Omar Saeed**.
2. Open **Harvest & Stock** and choose Cucumber crop cycle #2.
3. Record **50 kg**, today's harvest date, and a future sell-by date. Upload `app/sample_images/cucumber.jpg`.
4. Save and point out the new harvest lot and its photo.
5. Close the app fully, relaunch with root `run.bat`, select Omar, and open the same lot/photo.

Say:

> “The photo is stored with the lot in MySQL, so it is still available after closing and reopening the application. We did not reset the database between those steps.”

### 4:30–5:45 · Buyer search and request · Ali

1. Select buyer **Noura Ahmed**.
2. Open **Find Produce**, filter for Tomato, and show available quantity and a photo.
3. Request **120 kg** with a future needed-by date. Save and note the generated request ID.

Say:

> “The buyer sees available stock and records a request. The request is separate from an allocation: asking for stock does not reserve it.”

### 5:45–7:30 · Prevent over-allocation and reserve stock · Ali

1. Select **Omar Saeed** and open **Allocate to Markets**.
2. Select the new request and Tomato lot #2. Try allocating **100 kg** when only **78 kg** is available; show the friendly rejection.
3. Allocate the available **78 kg** from lot #2.
4. Select **Fatima Rashid** and allocate the remaining **42 kg** from her Tomato lot #13 to the same request.

Say:

> “The rejected quantity does not create a reservation. The two valid allocations total the 120 kg request, and availability is checked within the allocation transaction.”

Use the actual available quantities shown if prior demo activity changed the seed data. Do not force a quantity that exceeds the current available balance.

### 7:30–8:45 · Partial delivery and discrepancy · Mohammad

1. Select buyer **Noura Ahmed**, open **Deliveries**, and choose the new 78 kg allocation.
2. Confirm **70 kg received** and enter reason: “8 kg damaged in transport.”
3. Show the saved receipt and request status.

Say:

> “The receipt keeps allocated, received, and discrepancy quantities visible. Here the difference is 8 kg. The other 42 kg allocation remains separate, so the request is still partially delivered.”

### 8:45–10:00 · Read-only assistant · Mohammad

Ask:

> “Which deliveries had a shortfall, and by how much?”

Then ask the ambiguous question:

> “How much is available?”

If the assistant asks which crop, market, or date range, explain that it seeks a narrower read-only question. If it lacks a live Gemini connection, say so plainly and continue without pretending the answer is live.

Say:

> “The assistant answers validated read-only questions and shows supporting database information. It does not write or update project records.”

### 10:00–12:00 · Loss & Surplus · Abd

1. Select **Omar Saeed** and open **Loss & Surplus**. Show the threshold fields and explain the default 3-day near-expiry and 7-day surplus values. The poster's 5-day near-expiry example is configurable.
2. Show past-sell-by Cucumber lot #3. Explain that the team policy blocks donation after the recorded sell-by date, while disposal remains available. This app policy is not a claim about food safety.
3. Select **Fatima Rashid** and donate **25 boxes** from in-date surplus Dates lot #12 to “Demo food bank.” Provide the required reason if requested.
4. Return to Omar and dispose of the available **40 kg** from past-sell-by lot #3 with a clear reason. Show both history entries.

Say:

> “Each action records quantity, actor, time, reason, and a stock movement. We donate the in-date surplus lot and dispose of the past-sell-by lot. Both actions reduce available stock.”

Only perform quantities the current screen shows as available. If a balance has changed, lower the action quantity accordingly.

### 12:00–13:00 · Friendly invalid input · Ali

Choose one quick example: enter `abc` for a threshold, or enter a negative harvest quantity without saving. Show the clear validation message and verify no record was created.

Say:

> “Invalid input is rejected with a user-facing message before it can create an invalid stock movement.”

### 13:00–15:00 · Questions · All members

Keep answers short and let the questioner choose the topic. Suggested handoffs:

- **ER/cardinality/keys:** Ali
- **Stock movement and transaction rules:** Ali or Abd
- **GUI, assistant, and advanced feature:** Mohammad
- **Business rules and project scope:** Abd

If asked about authentication, explain that the demo uses a role/user selector; password authentication was not part of the original project description. If asked whether donations after sell-by are a course requirement, say no: the proposal gives donation/disposal as examples of disposition and the team added the sell-by donation block as a conservative project policy.

## Recovery cues

- If Gemini is unavailable, explain the connection issue and demonstrate the GUI/database workflows; do not claim a live assistant result.
- If seeded IDs or balances changed, choose equivalent current records and state the actual quantities shown.
- If the app fails, capture the visible message, avoid setup/reset, and move to the report/diagram explanation rather than risking the database.
- End by 15:00. The supplied announcement warns that a late or incomplete demo may incur a penalty.
