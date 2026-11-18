# How to read the database diagrams

**COSC444 Database Systems · Lab B1 · Farm-to-Market**  
This guide explains the symbols and lines in the revised Lab 7 diagrams. It accompanies the diagrams and does not change the implemented schema.

## Open the diagrams

- [Conceptual ER diagram (PDF)](conceptual-er.pdf): five landscape sheets. Sheets 1–2 show entities and attributes; sheets 3–5 show relationships.
- [Relational schema (PDF)](relational-schema.pdf): three landscape sheets with all 15 database tables.
- Editable Draw.io files and build instructions are in the [diagram README](README.md).

## Conceptual ER notation

| Shape or mark | Meaning |
|---|---|
| Rectangle | Entity: a kind of thing the system stores, such as `FARM`, `CROP_CYCLE`, or `MARKET_REQUEST`. An entity is implemented as a database table. |
| Oval | Attribute: a fact about an entity, such as `farm_name`. An attribute is implemented as a table column. |
| Underlined attribute | Entity identifier (primary key), such as `farm_id`, used to distinguish one entity instance from another. |
| Dashed oval | Derived attribute: calculated from stored data rather than entered independently. Examples include remaining expected harvest and lot stock totals. |
| Solid oval `discrepancy_quantity` | Stored receipt attribute. Although its value is calculated from allocated and received quantities, the application records it with the receipt for history. |
| Diamond | Named relationship between entities. Read its label as a verb or phrase between the endpoint entities. |
| Oval attached to a diamond | An attribute of that relationship. `assigned_at` records when a particular user-farm assignment was made. |
| `(unique)` beside a conceptual attribute | The value must be distinct among rows, such as a farm name. The relational diagram marks the corresponding unique constraint as `UQ`. |
| Repeated entity name on another sheet | The same entity repeated to keep the large diagram readable; it does not represent a second table. |

### How to read relationship lines and cardinality

Each endpoint has a maximum label (`1` or `N`) next to its line and a more explicit `(minimum,maximum)` pair beneath the relationship. Read the pair beside an entity from that entity's point of view. `N` means many.

- `(1,1)` means exactly one: the entity must participate once.
- `(0,1)` means participation is optional, with at most one relationship.
- `(0,N)` means zero or many.
- `(1,N)` means one or many.
- A single line means participation may be optional. A double line means the minimum is one and participation is mandatory.
- `*` after a pair means the app guarantees the minimum in the same transaction; a foreign key alone does not guarantee it.

For example, `FARM (0,N) — RUNS — CROP_CYCLE (1,1)` means a farm may have no cycles or many cycles, while every crop cycle belongs to exactly one farm. The `N` and `1` above the line show the maxima; the pairs below it show both minimum and maximum.

### Meaning of every conceptual relationship line

| Diamond label | Endpoint meaning |
|---|---|
| `LOCATED IN` (FARM–EMIRATE) | Each farm belongs to exactly one emirate; an emirate can have zero or many farms. |
| `LOCATED IN` (MARKET–EMIRATE) | Each market belongs to exactly one emirate; an emirate can have zero or many markets. |
| `ASSIGNED TO` (USER–FARM) | A user may be assigned to zero or many farms, and a farm may have zero or many assigned users. `assigned_at` records the assignment. The app restricts assignments to farmers. |
| `BUYS FOR` (USER–MARKET) | A user may link to zero or one market; a market may link to zero or many users. The role rule requires a market-buyer user to have a market and leaves other roles without one. |
| `RUNS` (FARM–CROP_CYCLE) | A farm may run zero or many cycles; every cycle belongs to exactly one farm. |
| `OF CROP` (CROP_CYCLE–CROP) | Each cycle is for exactly one crop; a crop can appear in zero or many cycles. |
| `REQUESTS` (MARKET_REQUEST–CROP) | Each request asks for exactly one crop; a crop can appear in zero or many requests. |
| `PLACES` (MARKET–MARKET_REQUEST) | A market may place zero or many requests; every request belongs to exactly one market. |
| `RECORDS` (MARKET_REQUEST–REQUEST_STATUS_CHANGE) | Every history row belongs to exactly one request; each request has at least one history row. `*` marks the app-created initial history row. |
| `DEFAULT UNIT` (CROP–UNIT) | Each crop has exactly one default unit; a unit may be the default for zero or many crops. |
| `FORECAST IN` (CROP_CYCLE–UNIT) | Each crop-cycle forecast uses exactly one unit; a unit may be used by zero or many forecasts. Forecast is kept separate from actual stock. |
| `REQUESTED IN` (MARKET_REQUEST–UNIT) | Each request quantity uses exactly one unit; a unit may be used by zero or many requests. |
| `YIELDS` (CROP_CYCLE–HARVEST_LOT) | A cycle may yield zero or many lots; every lot comes from exactly one cycle. A lot's farm and crop are found through its cycle. |
| `MEASURED IN` (HARVEST_LOT–UNIT) | Each lot quantity uses exactly one unit; a unit may be used by zero or many lots. |
| `PICTURED BY` (HARVEST_LOT–LOT_IMAGE) | A lot may have zero or many images; each image belongs to exactly one lot. |
| `CHANGED BY` (HARVEST_LOT–STOCK_MOVEMENT) | Each movement belongs to exactly one lot; every lot has one or more movements. `*` marks the app-created initial harvest movement. |
| `SUPPLIES` (HARVEST_LOT–ALLOCATION) | A lot may supply zero or many allocations; each allocation draws from exactly one lot. |
| `FULFILLED BY` (MARKET_REQUEST–ALLOCATION) | A request may have zero or many allocations; each allocation belongs to exactly one request. Multiple allocations permit partial fulfilment. |
| `CONFIRMED BY` (ALLOCATION–DELIVERY_RECEIPT) | An allocation may have no receipt yet or one receipt; every receipt confirms exactly one allocation. A unique FK enforces the one-receipt limit. |
| `CAUSES` (ALLOCATION–STOCK_MOVEMENT) | An allocation causes one or more movements; each movement may refer to zero or one allocation. `*` marks the app-created reservation movement. |
| `CREATED BY` (CROP_CYCLE–USER) | Every cycle has exactly one responsible user; a user may create zero or many cycles. |
| `CREATED BY` (HARVEST_LOT–USER) | Every lot has exactly one responsible user; a user may create zero or many lots. |
| `UPLOADED BY` (LOT_IMAGE–USER) | Every image has exactly one uploader; a user may upload zero or many images. |
| `CREATED BY` (MARKET_REQUEST–USER) | Every request has exactly one responsible user; a user may create zero or many requests. |
| `CHANGED BY` (REQUEST_STATUS_CHANGE–USER) | Every status-history row has exactly one responsible user; a user may make zero or many changes. |
| `MEASURED IN` (ALLOCATION–UNIT) | Every allocation has exactly one unit; a unit may be used by zero or many allocations. The app requires it to match the request and lot. |
| `ALLOCATED BY` (ALLOCATION–USER) | Every allocation has exactly one responsible user; a user may create zero or many allocations. |
| `MEASURED IN` (DELIVERY_RECEIPT–UNIT) | Every receipt has exactly one unit; a unit may be used by zero or many receipts. |
| `CONFIRMED BY` (DELIVERY_RECEIPT–USER) | Every receipt has exactly one responsible user; a user may confirm zero or many receipts. |
| `MEASURED IN` (STOCK_MOVEMENT–UNIT) | Every movement has exactly one unit; a unit may be used by zero or many movements. |
| `USER ID` (STOCK_MOVEMENT–USER) | Every movement records exactly one responsible user; a user may be responsible for zero or many movements. |

The 31 conceptual relationships map to 32 foreign keys because `USER ASSIGNED TO FARM` is implemented by the `farm_users` junction table, which has one FK to each endpoint. See [database design](../DATABASE_DESIGN.md) for the complete rationale and enforcement details.

## Relational schema notation

Each horizontal group is one table. Its heading is the table name; each box beneath it is one column. The three sheets divide the 15 tables for legibility, but together they describe one database.

| Mark | Meaning |
|---|---|
| Underlined column name | Primary key (`PK`): identifies a row. |
| Blue column box | Foreign key (`FK`): points to another table. The text below the row states the exact target, for example `farm_id -> farms.farm_id`. |
| `[UQ]` after a column name | Unique constraint: duplicate values are rejected. |
| Type below the column | SQL data type and size/precision, such as `INT`, `VARCHAR(100)`, `DATE`, `DECIMAL(12,2)`, or `MEDIUMBLOB`. |
| `NULL` / `NOT NULL` below the type | Whether a value is optional or required. A non-null FK requires a parent row. |
| `DEFAULT` in the note | Value MySQL supplies when an insert omits that column. |
| `CHECK` in the note | SQL condition that values must satisfy, for example a nonnegative quantity. |
| `PK,FK` on a column | That column both forms part of the primary key and references another table. If several columns are marked, the combined values form a composite key. |

The blue FK mark and its `column -> table.column` note are the relational connectors. Unlike a Crow's Foot drawing, these pages do not use connector lines between table boxes. Follow the written target to see the relationship. `NOT NULL` indicates mandatory participation from the child row; `NULL` indicates an optional FK. A `UNIQUE` FK limits the parent to at most one referencing child row.

The conceptual PDF's double line and cardinality labels describe the business relationship. The relational PDF's FK, nullability, uniqueness, and explicit target show how the SQL implements it. The final authority is [`app/schema.sql`](../../app/schema.sql); some cross-row rules, such as unit equality and available-stock checks, are enforced by [`app/db.py`](../../app/db.py).

## Related references

- [Project requirements and business rules](../PROJECT_REQUIREMENTS.md)
- [Diagram sources, exports, and checks](README.md)
