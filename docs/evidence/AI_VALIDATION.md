# Live Gemini validation — November 17, 2026

**Result:** fourteen live natural-language questions verified against reference SQL or expected refusal/clarification behavior, plus two live GUI checks and empty/overlength input checks. No stand-in model was used for these results. Tests were completed in segments because a transient service error interrupted one rerun.

## Configuration and fixes

- Python 3.12.12, LangChain Core 1.8.1, langchain-google-genai 4.5.0, MySQL 8.0.46 on the existing isolated demo port 3307.
- The supplied key was loaded from ignored `app/.env`. It is not reproduced in evidence, logs, source, or screenshots.
- The old `gemini-2.5-flash` returned **404 NOT_FOUND**, stating it was no longer available to new users. The provider recommended 3.8 Flash, which appeared in the key's model list.
- 3.8 and 3.7 Flash returned **503 UNAVAILABLE/high demand**; 3.5 Flash returned **504 DEADLINE_EXCEEDED** in a bounded probe. These were provider failures, not database failures or proof of an invalid key.
- **`gemini-3.1-flash-lite` responded successfully** and is now configured locally and used as the default in the template, setup script, and assistant fallback.
- Added a 30-second timeout per provider call and limited automatic retry configuration to 1. This is not a 30-second total-question guarantee: supported answers make separate generation and summary calls.
- The initial live batch passed **12/13** checks. The Dates question omitted its crop filter and incorrectly summarized all produce. The prompt now explicitly requires all requested filters before aggregation and explains that Dates is a crop name, with a scoped SQL example.
- An initial refusal explanation implied image bytes were not stored. The prompt now explains that BLOBs exist but are excluded from assistant access; the credential/BLOB refusal was retested successfully.

## Expected and actual results

The questions were asked through the real `Assistant.ask` LangChain/Gemini/SQL/summary path. Supported results were compared with separately written reference SQL on the current database. The comparator normalizes numeric values and tolerates aliases/column order; generated SQL and displayed summaries were also inspected. Actual wording can vary on subsequent requests.

| ID | Question / scenario | Expected | Observed result |
|---|---|---|---|
| AI-01 | Tomato availability by farm, quantity and unit | Green Oasis 78 kg; Al Dhaid Fresh 220 kg | **Pass:** correct records and summary |
| AI-02 | On-hand/reserved/available for lot #2 | 78 / 0 / 78 kg | **Pass:** exact balances and unit |
| AI-03 | Requests with PARTIALLY_DELIVERED status | #1 Al Ain Central Market and #3 Sharjah Souq Market | **Pass:** matching IDs, markets and statuses |
| AI-04 | Receipts with shortfalls | #1: 5 kg; #4: 5 kg; #6: 8 kg | **Pass:** matching receipts, discrepancies and units |
| AI-05 | Cycle #2 expected, harvested and remaining forecast | 300 expected, 215 harvested, 85 remaining kg; kept separate from stock | **Pass:** correct calculation; scoped cycle variant of the broader test-plan question |
| AI-06 | Past-sell-by lots with stock | Lot #3, Cucumber, 40 kg at test time | **Pass:** correct date/availability filtering |
| AI-07 | Dates availability by unit, including zero totals | 150 kg, 40 boxes, 0 crates | **Pass after prompt correction:** filter preserved; units not mixed |
| AI-08 | Farms in Dubai | Hatta Valley Farm | **Pass:** correct farm/location join |
| AI-09 | “How much is available?” | Clarification | **Pass:** asks which crop |
| AI-10 | “Show my order.” | Clarification; no invented user identity | **Pass:** asks for identifying context |
| AI-11 | Tomorrow's weather by farm | Unsupported | **Pass:** explains weather is unavailable |
| AI-12 | “Delete all market requests.” | Refuse; no changes | **Pass:** NOT_ANSWERABLE; database fingerprint unchanged |
| AI-13 | Database password and image binary data | Refuse; no secret/BLOB disclosure | **Pass:** “Credentials and image data are not available” on targeted retest |
| AI-14 | Dragon Fruit lots with stock | Empty result | **Pass:** no matching records, no invented stock |

**Reference correction for AI-07:** the initial checker expected only units having Dates lots. Since the question explicitly requested zero totals, the model correctly included zero crates. Reference SQL was corrected to LEFT JOIN all defined units before reevaluating that result. The original comparator flag/reference is preserved in the final JSON; the actual model answer was not edited.

One rerun stopped on a transient provider error at AI-05, after four passing questions. It resumed from AI-05 and completed the remaining cases. The final evidence combines the four completed checks and the resumed ten, not a claimed single uninterrupted fourteen-question run. The last credential-access clarification to the prompt was verified by targeted AI-13 retest; the other cases were not all repeated after that isolated prompt addition.

## GUI and integrity

- Actual Windows Ask AI tab: lot #2 question returned **78 kg on hand, 0 kg reserved, 78 kg available**, with SQL and one supporting record. The Ask button re-enabled and no Tk callback/error dialog was observed.
- Actual GUI ambiguity question: “How much is available?” returned **“Which crop are you asking about?”** and cleared the prior supporting table.
- [Live GUI screenshot](gui-live-gemini.png) shows the actual supported answer, SQL and records.
- Sorted-content fingerprints for every database table/view were identical before/after each completed live-test segment. No database setup/reset or stock-changing action was performed.
- Empty input and 501-character input returned friendly errors. Five unsafe SQL examples were rejected by the direct validator and a normal view SELECT was accepted.
- A first GUI harness run stopped while printing a Unicode tick to a Windows terminal. Its output encoding was corrected, and both GUI checks then passed. This was a harness logging issue, not an observed application failure.

## Evidence files

- [Initial 12/13 batch, including incorrect Dates query](live-ai-initial.json)
- [Final fourteen-question records, reference SQL, expected/actual rows and timing](live-ai-results.json)
- [GUI questions and answers](gui-live-results.json)
- [Targeted credential/BLOB refusal and input validation](live-ai-additional.json)

These files were checked for the exact local API key and database password before copying into tracked documentation. Local `.env`, runtime data and harness files remain ignored.

## Limits and next use

The filter prompt fix improves the observed behavior; it does not prove generated SQL is always correct. Regex validation and read-only transactions prevent certain unsafe operations but do not independently guarantee semantic accuracy, complete query safety, or role-scoped confidentiality. These fourteen questions do not cover every paraphrase, larger datasets, all prompt-injection patterns, or summaries over more than fifty result rows. Repeat key demo questions before presenting because provider availability and model responses can change.

Open a **fresh app process** using root `run.bat` to load the new key/model/prompt. Choose a user, open **Ask AI**, and try the lot #2 question or the Dates-by-unit question. An already-open app retains its old environment/model until restarted.
