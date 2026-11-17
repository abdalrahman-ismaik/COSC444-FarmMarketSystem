# Correctness follow-up — November 17, 2026

User decisions: prepare follow-up PRs; preserve the existing settlement policy. This work builds on Ali's PR #2 (`80529fb`) without replacing its original failure evidence. Mohammad's documents will be refreshed against this corrected snapshot in a separate follow-up.

## Changes

- MySQL connections explicitly use **READ COMMITTED**. Availability is read after acquiring the lot lock, so a snapshot taken during ownership checks cannot hide a competing committed movement.
- Request-changing actions lock the parent request before allocation and lot records. Status refresh also locks the request. Cancellation locks allocations in order and affected lots in sorted order. This covers different requests sharing a lot and different allocations sharing one request.
- Allocation prefill inserts `1500`, not `1,500`; normal stock validation still rejects an excessive quantity.
- Image upload verifies the format and fully decodes a reopened image before accepting bytes. A truncated JPEG is rejected before persistence; corrupt existing BLOBs still display a fallback.
- The buyer request screen explains that Delivered means all allocations settled; Received and Difference expose shortfalls. No schema, enum or receipt-policy migration was made.
- Acceptance scripts have `--output-dir`, default to ignored `output/validation/`, return 1 for recorded failures and 2 for blocked cases, and bound concurrency waits. The two GUI phases use the same output directory/state. Original `docs/evidence/track-a/` evidence remains unchanged.
- Normalization documentation qualifies deliberate operational redundancy rather than claiming every table is in 3NF/BCNF.

## Actual results

Windows, Python 3.12.12, MySQL 8.0.46, strict mode, **READ-COMMITTED**, separate loopback port **3318**. Only this disposable instance was reset. The existing demo on 3307 and normal MySQL service/data were not changed.

| Validation | Actual result | Evidence |
|---|---|---|
| Original business-rule suite on fresh seed | **65/65 Pass**, process exit 0 | [Log](fixes-2026-11-17/original-suite.txt) |
| Expanded backend acceptance | **173 Pass, 0 Fail**, process exit 0 | [Expected/actual cases](fixes-2026-11-17/backend.json) |
| GUI phase 1 and fresh-process restart | **22 Pass, 0 Fail, 0 Blocked**, both exits 0 | [Cases](fixes-2026-11-17/gui-flow.json) |
| Validation-support unit tests | **3/3 Pass**: failure/blocked exit codes, concurrent exception reporting, hung-worker deadline | [Log](fixes-2026-11-17/validation-support.txt) |
| Representative live Gemini/read-only checks | **7 Pass**: actual stock answer vs SQL, clarification, refused deletion, empty/overlength input, MySQL write rejection and unchanged DB fingerprint | [Cases](fixes-2026-11-17/assistant.json) |
| Diagram vs live DDL checker | **851 Pass / 0 Fail**, all 32 FKs represented | [Log](fixes-2026-11-17/diagram-check.txt) |

The 173 cases include 20 competing-allocation trials, one deterministic stale-snapshot interleaving, 10 allocation/donation trials, 10 each allocation/loss and allocation/negative-correction trials, and 10 each same-request double release, release/allocation and partial-receipt pairs. All final ledger/status/history invariants passed. The previous proposed-fix simulation is replaced by an assertion of the real connection isolation setting; this is actual application validation, not monkeypatched production behavior.

The GUI flow verified search, request, blocked over-allocation, two allocations, partial and full receipts, the settled-with-shortfall policy (150 allocated/140 received), numeric prefill, threshold errors, rejected truncated upload, corrupt-BLOB fallback, and byte-identical image retrieval in a second process. Screenshots include [settlement explanation](fixes-2026-11-17/gui-requests-status.png), [delivery](fixes-2026-11-17/gui-deliveries-partial.png), [image handling](fixes-2026-11-17/gui-image-unavailable.png), and [restart photo](fixes-2026-11-17/gui-restart-photo.png). New screenshots were inspected; this is widget/callback automation, not full manual accessibility testing.

## Reproduction

Use your own confirmed disposable instance with fresh `app/schema.sql` data for each independent suite. Setup hardcodes `farm_market_db`; never use a valuable database. Set connection settings in your ignored configuration or process environment. The confirmation must match your actual disposable target, not necessarily this test machine's port.

```powershell
$env:FARM_DISPOSABLE_DB_CONFIRM = "127.0.0.1:3318/farm_market_db"
python app/tests/test_validation_support.py
# After fresh seed on the confirmed disposable instance:
python app/tests/test_business_rules.py
# Restore only that disposable instance to seed before the expanded backend suite:
python app/tests/track_a_remaining_checks.py --output-dir output/validation/my-backend-run
# Restore seed before GUI phase 1, but do NOT reset between the two GUI phases:
python app/tests/track_a_gui_flow.py --output-dir output/validation/my-gui-run
python app/tests/track_a_gui_flow.py --restart --output-dir output/validation/my-gui-run
# No reset required; --live explicitly permits three real model questions:
python app/tests/check_assistant_readonly.py --live --output-dir output/validation/my-assistant-run
python docs/diagrams/tools/check_diagrams_vs_sql.py
```

Use the project virtual environment's Python. The original suite still mutates on import: run it directly, never through test discovery. New scripts run only under their main guards. Each suite must be inspected for its exit status; a logged failure is not a successful check. New output paths intentionally differ from historical evidence paths.

## Provenance and limitations

[Machine-readable summary and normalized source hashes](fixes-2026-11-17/summary.json) identify the tested files. Raw GUI JSON retains its original ignored output-directory screenshot paths; copies are linked above. API/database credentials were checked for exclusion before copying evidence. No new claim is made about all possible races, arbitrary model queries, all display scales, or manual usability. The original fourteen-question evidence remains separately available in [AI validation](AI_VALIDATION.md); only representative AI cases were repeated here.

The schema and editable diagram sources are unchanged, so diagram cardinalities/types remain applicable. Final reports/poster must cite this follow-up alongside original failures, then be regenerated and visually inspected. No reviewer acceptance, GitHub merge, booking, attendance or course submission is claimed.
