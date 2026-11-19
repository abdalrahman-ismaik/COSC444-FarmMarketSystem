# Course announcements and logistics

Source: announcement text supplied by the team in this conversation. Announcement publication timestamps were not supplied. The order below follows the supplied order; no authenticated eLearn, spreadsheet, or calendar state was checked.

## Action register

| Item | Supplied instruction | Current status |
|---|---|---|
| Team registration | Three–four students; all members in the team sheet | User reports all three B1 members registered; verify each name appears in the sheet |
| Earlier demo-booking deadline | November 12, 2026 | Historical instruction; user reports a slot booked for November 19 at 1:30 PM |
| Later penalty deadline | Monday, November 16, 2026, for demo booking and team-sheet registration; failure incurs 5% group penalty | User reports both complete; completion date not provided, so confirm with course staff if completed after the deadline |
| Submission | Thursday, November 19, 2026 | No cutoff hour or submission portal instructions supplied |
| Demo dates | Initially November 19, 20, and 23; later slot notice says all available slots are Thursday, November 19 | Confirm actual booked slot directly; do not assume another date is available |
| Demo duration | Strictly fifteen minutes: ~three-minute poster plus ~twelve-minute live demo/questions | Slot booked for November 19 at 1:30 PM per user; rehearsal required |
| Attendance | Every member attends; official excuse needed for absence to avoid lost marks | Attendance unconfirmed |
| Location | To be announced | Not yet provided; confirm before the slot |
| Late/incomplete demo | May incur a 10% penalty | Keep system ready before slot |
| Poster | Digital poster permitted; include in submission and project it instead of printing | `submission/COSC444_Farm-to-market_Poster.pdf` approved by Abd Alrahman Ismaik on 2026-11-19; team projector check and course upload remain |

Team registration: [Project information spreadsheet](https://docs.google.com/spreadsheets/d/1SXa0kR_Kgh19I0jOCFS4hiCuGGMwqTUkNJGFYdy6zrQ/edit?usp=sharing).

Booking: [Project demo calendar](https://calendly.com/ruosi9916/new-meeting).

These are supplied administrative links, not verified evidence of registration or a reservation. No external forms have been submitted. The supplied notices do not explain how multiple penalties combine; do not calculate an invented combined penalty.

## Supplied announcement record

The following preserves the announcement wording, with Markdown formatting and spacing normalized. The detailed scoring expectations are also mapped in the [rubric matrix](RUBRIC_AND_COVERAGE.md).

### Project Announcement

Dear Students,

Kindly note the below updates regarding your project:

Please register your teams of 3-4 students in the following link:

[Team registration](https://docs.google.com/spreadsheets/d/1SXa0kR_Kgh19I0jOCFS4hiCuGGMwqTUkNJGFYdy6zrQ/edit?usp=sharing)

The project instructions are posted on elearn.

The due date is Thursday 19th November.

The demos will happen on the 19th, 20th, and 23rd of November.

Good luck

### Project Demo

Dear Students,

Please use the link below to book a demo slot that suits your group:

[Demo booking](https://calendly.com/ruosi9916/new-meeting)

Now all available slots are on Thursday, Nov. 19. The demo location will be announced later.

You only need to attend at your booked time slot; there is no need to stay for other groups' demos.

Please be on time. The demo will be strictly limited to 15 minutes.

Best regards,

Ruosi

### Announcement on Project and Exam

Dear students,

Thank you for all your hard work this semester. As we finalize all lab assessments next week, we would like to give you some important notices.

Regarding the project:

- Please make sure your team has registered a demo timeslot by the 12th of November, 2026.
- You may create the poster digitally and include it in your submission so that you may present it using the projector rather than printing.
- Keep the poster presentation to about 3-minutes in order to leave time for the demo and questions. All team members should be able to answer any questions and demonstrate or explain all aspects of the project.
- Grading will be based on the Evaluation Criteria in the project description.
- All team members must attend (absence must be officially excused to avoid lost marks).
- Your project should be ready to demo before your presentation slot.
- Groups who are late or cannot complete the demo in the allotted time may incur a penalty of 10%.

### Project demo rubrics

Dear all,

Please ensure that you have booked a demo slot and confirmed that all your group members are registered in the google sheet.

Failure to do so by Monday the 16th of November will result in a group grade penalty of 5%.

As you prepare for the demo please keep in mind the following information and detailed grading rubric.

Your Poster Must Include:

- Project introduction that explains the context of the project and key business rules
- System overview and design (how the application works and its features). Highlight its core features, selected advanced feature, and key business rules.
- Database design including the ER Diagram.

| Criteria | Expectations for a Full Grade |
|---|---|
| ER diagram and Relational schema | 10 pts — Clear conceptual ER diagram with justified entities, relationships, cardinalities, and key rules for farms, crop cycles, harvest lots, requests, allocations, and deliveries. Separate schema diagram accurately maps the ER model and labels tables, primary/foreign keys, data types, and important constraints. |
| Implementation and Population | 15 pts — Submitted SQL script creates and populates the database; includes at least 3 farms, 4 markets, 5 crops, 8 crop cycles, 12 harvest lots, 15 stock movements, 8 market requests, and 6 delivery receipts. Samples cover available, reserved, partially fulfilled, lost stock, delivery discrepancies, and product images; suitable uniqueness, valid-status, and nonnegative-quantity constraints are applied. |
| Python GUI | 10 pts — Functional, user-friendly GUI supports farmer, market-buyer, and administrator workflows, including farm/crop-cycle setup, harvest and stock movements, search and requests, allocations, partial delivery, and discrepancy recording. Role-appropriate screens are clear, and images can be uploaded and retrieved after restart. |
| Back-end Programming and Embedded SQL | 10 pts — Reliable back-end operations support the required workflows with parameterized SQL, sound transaction handling, and appropriate integrity rules. Stock movements, allocations, partial deliveries, discrepancies, and role-based record ownership are persisted consistently. |
| LangChain assistant | 10 pts — In-GUI LangChain assistant answers validated read-only questions accurately, shows supporting records or summaries, and clearly handles ambiguous or unsupported questions without changing data. |
| Advanced feature at least one required per team | 10 pts — At least one Phase 3 option is database-backed, accessible in the GUI, tested, and demonstrated. For analytics, include the specified three analyses, filters, two charts, summary metric, and CSV/PDF export; for matching, use three documented criteria and safe confirmed allocation; for forecasting, compare three cycles and report accuracy; for loss/surplus, support thresholds and two disposition actions; for secure login/audit, demonstrate hashed login, role permissions, two audited operations, and denied access. |
| Error handling and business-rule enforcement | 5 pts — Gracefully handles connection failures, constraint violations, duplicates, invalid dates, unknown crop/unit values, unavailable results, invalid LangChain requests, and unavailable image files. Prevents negative stock and over-allocation; preserves transaction integrity; records movement/status details; and enforces role ownership. |
| Demo and poster presentation (Overall Group Performance) | 5 pts — Within 15 minutes: approximately 3-minute poster overview/design and 12-minute live demo. Demonstrates GUI harvest entry and image retrieval after restart, market search/request and partial delivery, prevention of over-allocation, a supported and an ambiguous/unsupported assistant question, the selected advanced feature, and a user-friendly invalid-input response. Delivery is organized and the team explains key design decisions. |
| Member Demo and Q and A (Individual Member Performance) | 10 pts — Demonstrated a strong understanding of the project and the implemented solution. Presented on time and within the allotted time. Answered all questions clearly and confidently. |
| Technical documentation and test evidence | 15 pts — Concise PDF documents ER and relational schemas, key business rules and database transactions, and test cases with expected and actual results. Test plan covers every major function, valid/invalid/boundary and repeated or concurrent cases where relevant; verifies stock calculations and expected-harvest separation; includes at least 10 assistant questions with ambiguous/unanswerable cases, image and GUI tests, and selected-feature tests. README includes setup and run instructions. |

## Date interpretation

The year 2026 is explicit in the earlier booking notice and consistent with the proposal semester and supplied environment date. November 16 is Monday and November 19 is Thursday in that year. Use the later penalty notice as the urgent operational instruction while retaining the earlier deadline as history. Confirm the actual reservation and any instructor clarification independently.
