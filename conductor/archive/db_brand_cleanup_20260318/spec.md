# Spec: Strip Brand Names from Vehicle Type in Database

## Overview
Vehicle names are currently stored in the `vehicles` table as `"Economy Car (Alamo)"` —
combining category and brand into a single field. This contaminates category lookups
(sparklines, delta tracking, holding comparisons). Brand data should be preserved but
stored in a dedicated `brand` column.

## Functional Requirements
1. **Audit** — identify all rows in `vehicles` where `name` contains a brand suffix
   matching the pattern `" (Brand)"`.
2. **Migrate existing data** — for each dirty row, extract the category (before `" ("`)
   into `name` and the brand (between `"("` and `")"`) into a new `brand` column.
3. **Schema change** — add a `brand TEXT` column (nullable) to the `vehicles` table.
4. **Write layer guard** — update `__main__.py` to store `v.name` and `v.brand`
   separately when calling `save_vehicles()`, so brand names never enter `name` again.
5. **Update `VehicleRecord`** — add optional `brand` field to the dataclass.

## Non-Functional Requirements
- Migration must be idempotent (safe to re-run).
- No existing functionality should break (delta tracking, sparklines, holding comparison).

## Acceptance Criteria
- [ ] `vehicles.name` contains no entries matching `"% (%)"` after migration.
- [ ] `vehicles.brand` column exists and is populated for migrated rows.
- [ ] New scraper runs write clean names to `vehicles.name`.
- [ ] All existing tests pass; new tests cover migration and write guard.

## Out of Scope
- Changing how brand is displayed in the email (email shows `v.name` only today, that's fine).
- Altering the `runs` table or `holding_vehicle_type` field.
