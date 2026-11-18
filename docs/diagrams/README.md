# Lab 7 diagram sources and exports

Revised 18 November 2026 by Mohammad / Codex at Mohammad's request, based on Ali's Track A model. Reviewer: Abd Alrahman. No schema or business-policy changes.

Reference: supplied `Lab 7 Slides (1).pptx`, slides 2–8. Conceptual entities use rectangles, attributes use ovals, identifiers are underlined, relationships use diamonds, and mandatory participation uses double lines. Maximum cardinalities are shown at the entity end; explicit (min,max) annotations remove optionality ambiguity. Dashed ovals are derived values. Receipt discrepancy is stored and therefore has a solid oval.

- `conceptual-er.drawio` / `.pdf`: five landscape sheets. Two attribute sheets define the 14 entities; three relationship sheets connect them, including all actor/unit relationships. Repeated names identify the same entity, not separate entities. The 31 conceptual relationships map to 32 FKs because FARM–USER assignment becomes a two-FK junction.
- `relational-schema.drawio` / `.pdf`: three landscape sheets, all 15 relations as horizontal rows. Underlined PKs, highlighted FKs, explicit FK targets, SQL types, nullability, defaults, unique and named CHECK constraints. Views are explained in DATABASE_DESIGN.md, not presented as stored relations.
- SVG exports: base filename for page 1; `-p2.svg` etc for following pages.

## Rebuild

From the repository root with Python and the document dependencies installed:

```powershell
python docs/diagrams/tools/build_lab7.py
python docs/diagrams/tools/check_lab7.py
python docs/report/build_documents.py
```

The first command generates Draw.io, PDF and SVG from the same layout. It reuses the original generator's SQL transcription and conceptual definitions. Do not run the original `generate_diagrams.py` entry point: that restores the superseded layout. Draw.io sources remain editable; manual edits must also be reflected in the builder before rebuilding.

The report input manifest deliberately pins export hashes. After intentional diagram changes, update only its four diagram hashes, then rebuild the report. Do not replace evidence/source hashes to bypass a failed validation.

The old live-database checker and its 851-check result are historical evidence for the former layout. Use `check_lab7.py` for this layout; it reads SQL and XML without connecting to MySQL. No normalization exercise is requested by the saved project rubric; none is included.
