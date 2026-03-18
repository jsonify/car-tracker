# Plan: Strip Brand Names from Vehicle Type in Database

## Phase 1: Schema Migration

- [x] Task 1: Write and apply DB migration
  - Add `brand TEXT` column to `vehicles` table (if not exists) — use `ALTER TABLE ... ADD COLUMN` in `try/except OperationalError` per codebase pattern
  - For each row where `name` LIKE `'% (%)'`, extract category into `name` and brand into `brand`
  - Wire into `migrate_db()` called from `init_db()` so existing DBs auto-upgrade on next run
  - Comment migration block with `# v<N>:` for traceability

- [x] Task 2: Write tests for migration
  - Seed a test DB with dirty rows (e.g., `"Economy Car (Alamo)"`)
  - Assert `name` = `"Economy Car"` and `brand` = `"Alamo"` after migration
  - Assert re-running migration is a no-op (idempotent)
  - Assert rows already clean are untouched

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Schema Migration' (Protocol in workflow.md)

## Phase 2: Write Layer Guard

- [x] Task 1: Update `VehicleRecord` dataclass
  - Add optional `brand: str | None = None` field to `VehicleRecord` in `database.py`

- [x] Task 2: Update `save_vehicles()` in `database.py`
  - Accept and insert `brand` field alongside existing columns in the INSERT statement

- [x] Task 3: Update `__main__.py` write call
  - Change `name=f"{v.name} ({v.brand})"` to `name=v.name, brand=v.brand`

- [x] Task 4: Write tests for write layer
  - Assert saved vehicle `name` contains no brand suffix (no `" ("` pattern)
  - Assert `brand` column is populated correctly from `VehicleRecord.brand`

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Write Layer Guard' (Protocol in workflow.md)
