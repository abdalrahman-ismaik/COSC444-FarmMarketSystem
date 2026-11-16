---
name: Farm-to-Market
description: Existing green-and-white Tkinter desktop design system
colors:
  primary: "#2E7D32"
  primary-dark: "#1B5E20"
  primary-light: "#E8F5E9"
  background: "#F4F6F4"
  surface: "#FFFFFF"
  text: "#1F2933"
  muted: "#6B7280"
  danger: "#C62828"
  warning: "#EF6C00"
  market: "#1565C0"
  administrator: "#6A1B9A"
typography:
  title:
    fontFamily: "Segoe UI, Helvetica Neue, DejaVu Sans, Arial"
    fontSize: "15pt"
    fontWeight: 700
  section:
    fontFamily: "Segoe UI, Helvetica Neue, DejaVu Sans, Arial"
    fontSize: "11pt"
    fontWeight: 700
  body:
    fontFamily: "Segoe UI, Helvetica Neue, DejaVu Sans, Arial"
    fontSize: "10pt"
    fontWeight: 400
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    padding: "6px 12px"
  button-primary-hover:
    backgroundColor: "{colors.primary-dark}"
---

# Design System: Farm-to-Market

## Overview

This specification records the existing UI in `app/app.py`, particularly `setup_style`, shared widgets, role screens, and status mappings. It is a desktop operational tool: tables, quantities, forms, and clear actions carry the interface. No restyling or accessibility audit is implied by this document.

Keep the green-and-white identity for future refinement. The product's primary visual job is to make stock, ownership, forecast separation, and delivery outcomes easy to understand during everyday tasks and the assessed demonstration.

## Colors

Primary green marks main actions and the farmer role; dark green anchors headers and headings. Light green supports hover and success treatments. White surfaces sit on the pale neutral background. Dark gray is the main text color, with muted gray for secondary information.

Blue identifies market buyers and purple identifies administrators. Danger red and warning amber signal errors, expiry, and shortfalls. Existing table backgrounds include pale red `#FDECEA`, amber `#FFF3E0`, blue `#E3F2FD`, green `#E8F5E9`, and alternating near-white `#FAFBFA`. Selected rows use `#A5D6A7`.

**Future refinement criterion:** every critical status must have readable text as well as color. Validate contrast on Windows before claiming accessibility conformance; the supplied muted/disabled colors are not independently certified.

## Typography

The application selects the first installed family from Segoe UI, Helvetica Neue, DejaVu Sans, and Arial, falling back to TkDefaultFont. Body text is 10 pt, section labels 11 pt bold, and regular screen titles 15 pt bold. The login title is 24 pt bold. Assistant answers use 12 pt and SQL uses Courier 9 pt. Tk point sizes are not CSS pixel sizes.

Use sentence-case task labels and explicit units. Numeric columns align right; dates and identifiers generally align centrally. Existing Unicode symbols supplement text; rendering depends on available fonts.

## Layout

The existing window opens at 1280 × 800 with a minimum size of 1100 × 680. A persistent header identifies the account and role; role-specific notebook tabs organize workflows. A bottom status line displays transient feedback. Tables expand and scroll; harvest/search screens place a product-photo panel beside the results.

Existing spacing uses roughly 6–16 px gaps, 14 px tab padding, and 20 px form-card padding. Treeview rows are 28 px high. Preserve practical density rather than introducing a web landing-page layout.

**Future refinement criteria:** check 100%, 125%, and 150% Windows display scaling, keyboard navigation, long labels, modal overflow, and the minimum window size. Provide scrolling where needed; do not silently hide actions or quantities. These are acceptance targets, not completed tests.

## Elevation & Depth

The incumbent system is flat. White cards, a one-pixel solid border, tinted rows, and header contrast establish hierarchy. There is no custom shadow or animation system.

## Shapes

Use the existing `clam` ttk theme and rectangular native-style controls. No custom rounded-corner scale is defined in the source. Keep borders and selection states consistent with shared styles.

## Components

| Component | Existing behavior | Future refinement/verification criterion |
|---|---|---|
| User selector | Named fictional users grouped by role | Clearly identify demonstration access; retain keyboard reachability |
| Header and tabs | Current user, role, switch-user action, role-specific tasks | Keep context visible and labels understandable |
| Data tables | Row selection, scrollbars, formatted values, record count | Check focus visibility and full values at Windows scaling settings |
| Quantity summaries | Expected, on hand, reserved, and available shown separately | Never merge forecasts or incompatible units |
| Form dialogs | Labels, dropdowns, dates, inline errors; Enter submits, Escape closes | Preserve input after errors and verify logical focus order |
| Primary/danger actions | Green task action and red destructive/disposition styling | Pair consequence with clear labels and appropriate confirmation where needed |
| Product photos | BLOB retrieval, navigation, empty/unavailable states | Check restart persistence and corrupt/missing-image handling |
| Status feedback | Six-second success/error line and message dialogs | Verify important errors remain discoverable and are not color-only |
| Assistant | Background request, disabled Ask button, answer, SQL, supporting records | Verify pending, failure, clarification, empty-result, and user-switch states |
| Loss & Surplus | Thresholds, priority labels, flags, donation/disposal history | Keep affected lot, quantity, unit, and reason clear |

## Do's and Don'ts

- Reuse shared styles and widgets; document intentional deviations.
- Keep exact database statuses distinguishable from friendly labels.
- Use product images for record identification, retaining provenance.
- Treat keyboard access, visible focus, readable contrast, and friendly errors as acceptance criteria to verify.
- Keep documentation layouts readable through short sections, linked sources, and comparison tables.
- Do not represent proposed improvements as completed GUI work, add a web stack for this theme, or import KU Planner's Liquid Glass styling.
