# Document and package follow-up review

**Owner:** Codex, authorized by Abd Alrahman Ismaik. **Status:** Ready for review, not Accepted.

This follow-up integrates Mohammad's report/poster and Ali's diagrams with the tested integrity fixes. It retains both teammates' contributions and evidence. Historical failures remain visible and are labeled historical; later outcomes have a separate source/date and hash manifest.

## Changes

- Report and poster distinguish the original Track A failures from the subsequent passing fixes and current reviewer dependencies.
- The PDF builder uses checked-in, SHA-256-verified inputs instead of requiring another branch's Git objects. It checks both historical and follow-up result totals and the tested source hashes.
- The progress ledger includes both teammates' activity and the fix follow-up; no acceptance or course submission is recorded.
- Candidate packaging will be explicit, include a member SHA-256 manifest, and exclude secrets/local environments and archived ZIPs.

## Verification

The original and follow-up application evidence is linked in `docs/evidence/FIX_VALIDATION.md` and `docs/evidence/fixes-2026-11-17/`. PDF structural checks verified 12 report pages and one poster page. All 12 report pages and the 1920 × 1080 poster were rendered and inspected after the final wording update; build and fresh-extraction results are in `docs/report/build-validation-followup.json` and `submission/MANIFEST.md`.

## Human review remaining

Abd Alrahman should review the code/drawings/report/poster, decide the unresolved exact image-source mapping (or authorize replacement), and personally mark Accepted. The team still needs a projector check and timed demo rehearsal. No PR is merged and no course upload has occurred.
