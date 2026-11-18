# Correctness follow-up for PR #2

PR: https://github.com/abdalrahman-ismaik/COSC444-FarmMarketSystem/pull/4

Prepared by Codex under Abd Alrahman Ismaik's approved implementation plan. Status: **Accepted by Abd Alrahman Ismaik on 18 November 2026** and included in the integrated review branch. Base: Ali's Track A commit `80529fb` / PR #2. No schema or seed change; original Track A drawings/results remain preserved.

## Resulting behavior

- Stock checks see the latest committed movements after waiting for a lot lock; competing requests cannot both spend the same tested availability.
- Request, allocation and lot locks follow a consistent parent-first order; related status/history changes are serialized.
- Editable quantity prefill has no thousands separator.
- Invalid truncated image data is decoded and rejected before storage; valid images and existing corrupt-BLOB fallbacks remain supported.
- The retained Delivered/settlement policy is explained in the buyer GUI. A shortfall still closes that allocation's single receipt and records release/loss.
- Acceptance runners no longer signal success with recorded failures, wait indefinitely for workers, or default to overwriting published historical evidence.
- The normalization discussion acknowledges functional dependencies and deliberate redundancy instead of blanket BCNF claims.

## Validation

[Expected/actual report](../evidence/FIX_VALIDATION.md) and dated JSON/screenshots/logs record isolated MySQL 8.0.46 on port 3318 with READ COMMITTED. Existing demo data on 3307 was untouched.

| Check | Result |
|---|---|
| Original suite | 65/65 |
| Expanded backend, including new same-request and removal races | 173/173 |
| GUI plus separate-process image restart | 22/22 |
| Exit/deadline/exception support tests | 3/3 |
| Representative live Gemini/input/read-only/fingerprint checks | 7/7 |
| Diagram checker | 851/851; all 32 FKs |

Actual reproduction commands, source hashes, historical limitations and evidence paths are in the report. Neither these counts nor an isolation-level change prove every concurrency schedule or arbitrary AI question safe. Manual display-scaling/accessibility and human rehearsal remain outside these automated checks.

## Review and integration

The fixes were reviewed with Ali's PR #2. The original application failures remain preserved as historical findings; follow-up results are not relabeled as earlier passes. Abd Alrahman chose the settlement policy; no instructor endorsement is inferred. These changes are accepted in the integrated review branch. The dated tests do not prove every possible concurrency schedule or arbitrary assistant query safe.
