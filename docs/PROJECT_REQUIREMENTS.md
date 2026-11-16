# Project requirements and business rules

**Course:** COSC444 Database Systems, Fall 2026–2027, Khalifa University. **Team:** three students from lab B1; see [team](TEAM.md). **System:** Local Farm and Market Food Availability System (Farm-to-Market).

## Sources and interpretation

The [original proposal](sources/Local_Farm_Market_Food_Availability_Project_Proposal.pdf) defines the required capabilities, phases, submission, and assessment. The [supplied announcements](ANNOUNCEMENTS.md) add logistics and the detailed grading rubric. The [Lab 6 slides](sources/langchain.pptx) and archived school example are teaching references, not the farm application's schema. The [rubric matrix](RUBRIC_AND_COVERAGE.md) connects requirements to implementation and evidence.

Preserve the proposal's requirements while applying the later announcements' more specific logistics and scoring breakdown. When dates or wording differ, record both; do not invent an instructor clarification. This prototype supports UAE food-security context using fictional/public data and makes no government integration or national-coverage claim.

## Phase 0 — Planning and team setup

| ID | Requirement |
|---|---|
| P0-01 | Form a team of 3–4 students from the same lab section; this team has three B1 members. |
| P0-02 | Register every member in the supplied team spreadsheet and book a demo slot. Status is unconfirmed. |
| P0-03 | Document analysis, database, GUI, LangChain, testing, and documentation responsibilities. Every member contributes to database design and implementation. |

## Phase 1 — Database design and population

| ID | Requirement |
|---|---|
| P1-01 | Create a clear conceptual ER diagram in Draw.io with justified entities, relationships, cardinalities, and key business rules. |
| P1-02 | Create a separate relational schema diagram with tables, primary/foreign keys, data types, and important constraints. |
| P1-03 | Submit SQL creating and populating the relational database. Apply uniqueness, valid-status, and suitable nonnegative-quantity constraints. |
| P1-04 | Include available/reserved/partially fulfilled/lost stock, discrepancies, and sample product images. |

| Required sample | Minimum | Present in supplied SQL (static count) |
|---|---:|---:|
| Farms | 3 | 4 |
| Markets | 4 | 4 |
| Crops | 5 | 6 |
| Crop cycles | 8 | 10 |
| Harvest lots | 12 | 13 |
| Stock movements | 15 | 38 |
| Market requests | 8 | 9 |
| Delivery receipts | 6 | 6 |
| Product images | Required; no numeric minimum stated | 12 embedded BLOB records, plus 4 upload-demo JPGs |

These counts describe SQL statements, not a fresh database execution. Core entities include Farms, Users, Crops, CropCycles, HarvestLots, HarvestLotImages or equivalent references, StockMovements, Markets, MarketRequests, Allocations, and DeliveryReceipts. Justify supporting entities in the database design.

## Core business rules

| ID | Rule |
|---|---|
| BR-01 | A farm has multiple crop cycles and harvest lots. Each lot belongs to one cycle and has a crop, quantity, explicit unit, harvest date, and optional sell-by date. The crop may be derived through the cycle. |
| BR-02 | Expected harvest is a forecast stored separately from harvested inventory; never include it in current stock. |
| BR-03 | Derive availability from dated movements: harvest, reservation, delivery, loss, release, and approved correction. |
| BR-04 | Requests may be partially fulfilled. Never allocate more than the lot's available quantity; related changes must be atomic. |
| BR-05 | Receipts store actual received quantity and clearly record any difference from the allocation. |
| BR-06 | Every quantity has a unit. Do not add or compare incompatible units without a documented conversion. No conversion feature is selected. |
| BR-07 | Farmers change only assigned farms' records. Market buyers manage only their markets' requests and receipts. Administrators maintain reference data and do not directly modify operational transactions outside documented correction procedures. |
| BR-08 | Movements and request-status changes retain date, responsible user, and reason where applicable. Preserve history through deactivation where appropriate. |
| BR-09 | Associate every image/reference with a harvest lot; handle unavailable files/images gracefully and retrieve stored images after restart. |
| BR-10 | Use fictional or public sample operational data, avoiding real personal, financial, and sensitive government data. Student authorship details are documentation, not operational seed data. |

## Phase 2 — Python GUI, embedded SQL, and LangChain

| ID | Required capability |
|---|---|
| P2-01 | A functional, user-friendly Python GUI connected to SQL with parameterized queries. Desktop or web frameworks are acceptable; console-only submission is not. This implementation uses Tkinter. |
| P2-02 | Add farms and crop cycles, including expected dates/quantities. Record harvest lots and stock movements; show expected, on-hand, reserved, and available quantities separately. |
| P2-03 | Buyers search local supply by crop, location, availability date, and quantity, then create/update requests. Farmers allocate assigned lots; buyers confirm actual deliveries and discrepancies. |
| P2-04 | Search/status views filter by farm, market, crop, emirate, date, availability, and request status, with relevant quantities/details. Custom analytics/export is an advanced option. |
| P2-05 | Upload valid JPG/PNG product images and display them to buyers. SQL BLOB or database-backed external references are allowed; images survive restart. Selected approach: SQL BLOB. |
| P2-06 | Provide role-appropriate farmer/buyer/admin workflows using demo accounts or a specific-user selector. Password login is mandatory only for the secure-login advanced option. |
| P2-07 | Include an in-GUI LangChain assistant that answers natural-language questions with validated read-only queries or approved tools, shows supporting records/summaries, and handles ambiguity/unanswerability. |
| P2-08 | Keep SQL as source of truth. No unrestricted AI-generated writes; any data-entry assistance would require a reviewable, explicitly confirmed draft. No such write assistance is selected. |

## Phase 3 — One advanced feature required

Every team must implement, expose in the GUI, test, and demonstrate at least one database-backed option. A second is optional and does not replace core requirements. GUI, image support, LangChain, and basic manual allocation are core functions.

| Option | Full capability required if selected | Selection |
|---|---|---|
| Analytics/reporting | Admin dashboard; three SQL analyses: supply vs demand, fulfilment/discrepancies, and loss/ageing; filters; at least two charts; summary metric; filtered CSV or PDF export | Not selected |
| Smart demand matching | At least three documented criteria; ranked farms/lots; multi-lot recommendation where needed; explanation; user-confirmed safe allocation | Not selected |
| Harvest forecasting | Documented method and historical data; crop/date predictions; comparison against actual harvests for at least three cycles; accuracy measure; separate from stock | Not selected |
| Loss & Surplus | Documented SQL rules and adjustable thresholds; prioritized near-expiry/unallocated lots; at least two recorded disposition actions, responsible users, valid movements and transaction checks | **Selected: donation and disposal** |
| Secure login/audit | Hashed passwords, logout/session handling, role permissions/ownership; at least two sensitive-operation audit types; denied access and audit demonstration | Not selected |

Selected defaults are three days for near expiry and seven days for unallocated ageing. Their exact implementation and limitations are documented in [architecture](ARCHITECTURE.md#loss--surplus).

## Phase 4 — Error handling

| ID | Required behavior |
|---|---|
| P4-01 | Handle connection failures, constraint violations, duplicates, invalid dates, unknown crops/units, and empty searches. |
| P4-02 | Reject negative/invalid stock changes and reservations/allocations beyond availability. Signed approved corrections require an explained exception to positive-movement rules. |
| P4-03 | Show friendly GUI errors; preserve transaction integrity after failed operations. Do not leak credentials or raw internal Python/SQL errors. |
| P4-04 | Handle ambiguous, unsupported, unsafe, and unavailable assistant responses; reject unrestricted writes. Handle unavailable image files. |

## Phase 5 — Testing, documentation, and final submission

| ID | Required evidence/artifact |
|---|---|
| P5-01 | Test every major function with valid, invalid, boundary, and relevant repeated/concurrent cases; record expected and actual results. |
| P5-02 | Verify stock after harvest, reservation, release, delivery, loss, correction, and selected disposition actions. Confirm forecast separation. |
| P5-03 | Test at least ten assistant questions, including ambiguous and unanswerable cases, against SQL results. Cover images, GUI operations, and selected-feature valid/invalid cases. |
| P5-04 | Submit concise technical PDF containing conceptual ER and relational schema diagrams, key business rules, database transactions, and expected/actual test evidence. Screenshots are not required for that PDF. |
| P5-05 | README provides packages, setup, configuration, and run instructions. |
| P5-06 | Submit one ZIP containing technical PDF, poster PDF, all Python source, final creation/population SQL, external images where applicable, and README. |
| P5-07 | Present approximately three minutes of poster overview/design and twelve minutes of demo/questions within fifteen minutes. Every member attends, understands every aspect, and can answer questions. |

The [demo checklist](DEMO_AND_SUBMISSION.md) enumerates the required live scenarios. The current Markdown documents prepare the assessed artifacts; they do not replace the final PDFs or diagrams.
