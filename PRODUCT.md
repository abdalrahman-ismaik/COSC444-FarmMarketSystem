# Product

<!-- impeccable:product-schema 1 -->

## Platform

Windows desktop application using Python and Tkinter/ttk. This is a desktop platform outside Impeccable's web/iOS/Android platform vocabulary; do not infer a web migration.

## Users

Farmers maintain assigned farms, growing cycles, harvests, and stock. Market buyers discover supply, request produce, and confirm their markets' receipts. Administrators maintain accounts and reference data and inspect operational records. Student demonstrators and assessors need a repeatable, understandable workflow within a 15-minute presentation.

## Product Purpose

Make local produce availability visible while keeping forecasts separate from real stock. Every reservation, delivery, loss, correction, donation, and disposal must preserve an explainable inventory history. The context is UAE local food availability using fictional or public sample data.

## Operating Context

COSC444, Fall 2026–2027, Khalifa University, lab B1. Three students share design and implementation responsibilities. The submission is due November 19, 2026, with no announced cutoff time in the supplied text. A demo uses approximately three minutes for a poster and twelve minutes for the live system and questions.

## Capabilities and Constraints

- Existing stack: MySQL 8, PyMySQL, Tkinter, Pillow, python-dotenv, LangChain, and Gemini.
- SQL remains the source of truth; application transactions enforce ownership and multi-record stock changes.
- Photos are stored as BLOBs linked to harvest lots. The GUI supports image retrieval after restart by design; current local evidence is pending.
- Demo accounts select roles without passwords. Secure-login/audit is an unselected advanced option.
- Loss & Surplus is the selected advanced feature: adjustable expiry/age thresholds and recorded donation/disposal actions.
- Core workflows, LangChain, and image support are mandatory and do not count as advanced features.
- This documentation pass preserves behavior. Coverage assertions require the evidence labels in docs/RUBRIC_AND_COVERAGE.md.

## Brand Commitments

Keep the existing name, Farm-to-Market, and green-and-white desktop identity as the baseline. Use direct, readable English appropriate to farmers, market buyers, and an academic demonstration. Document the incumbent UI without importing KU Planner's visual theme.

## Evidence on Hand

The original four-page proposal, twelve-slide Lab 6 deck, source code, seed SQL, four external sample images, archived ZIP, existing business-rule script, and historical 37-page visual guide are preserved. The guide reports 65 passing checks and discloses stand-in assistant screenshots. Fresh MySQL/Gemini/GUI evidence and final assessed diagrams/PDFs are not supplied by that claim.

## Product Principles

- Derive availability from recorded movements, with units visible.
- Preserve ownership and transaction integrity across every change.
- Keep forecast quantities distinct from saleable inventory.
- Explain invalid inputs and unavailable results in plain language.
- Prefer a simple, demonstrable implementation and evidence over unsupported completion claims.
