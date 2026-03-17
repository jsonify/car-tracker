# Plan: Remote Config Updates via iMessage

## Phase 1: Natural Language Parser
<!-- execution: sequential -->

- [x] Task 1: Write tests for `parse_config_update(text)` <!-- commit: c267e37 -->
  - Test: extracts `holding_price` from "update holding price to 375"
  - Test: extracts `holding_price` from "change my holding price to $400.50"
  - Test: extracts `holding_vehicle_type` from "set holding type to SUV"
  - Test: extracts both fields from "update holding price to 350 for Standard Car"
  - Test: returns empty dict for unrecognized/irrelevant text
  - Test: returns empty dict for empty string
  - Test: validates price is a positive number (rejects "set price to -50")

- [x] Task 2: Implement `parse_config_update(text)` in `scripts/update_config.py` <!-- commit: c267e37 -->
  - Regex-based extraction of `holding_price` (float) and `holding_vehicle_type` (str)
  - Returns `dict` of matched fields only; empty dict if no match
  - Add `scripts/__init__.py` if not present

- [x] Task 3: Conductor - User Manual Verification 'Phase 1: Natural Language Parser'

---

## Phase 2: Config Update & Git Push
<!-- execution: sequential -->

- [x] Task 1: Write tests for `apply_config_update(updates, config_path)` <!-- commit: 343cadc -->
  - Test: updates `holding_price` only — other fields unchanged
  - Test: updates `holding_vehicle_type` only — other fields unchanged
  - Test: updates both fields in one call
  - Test: no-op when values already match (returns False, no git call)
  - Test: raises on invalid config path
  - Mock `subprocess.run` for git commands

- [x] Task 2: Implement `apply_config_update(updates, config_path)` in `scripts/update_config.py` <!-- commit: c267e37 -->
  - Load YAML with PyYAML
  - Patch only the specified fields under `search:`
  - Write back to disk
  - Run `git add config.yaml`, `git commit`, `git push` via `subprocess.run`
  - Returns `True` if changes committed, `False` if no-op

- [x] Task 3: Conductor - User Manual Verification 'Phase 2: Config Update & Git Push'

---

## Phase 3: iMessage Integration
<!-- execution: sequential -->

- [x] Task 1: Write tests for `read_pending_messages(db_path, state_path)` <!-- commit: cddf17d -->
  - Test: returns messages with rowid > last processed rowid
  - Test: returns empty list when no new messages
  - Test: creates state file if missing (last_rowid = 0)
  - Mock SQLite DB for isolation

- [x] Task 2: Implement `read_pending_messages(db_path, state_path)` in `scripts/check_imessage.py` <!-- commit: cddf17d -->
  - Connect to `~/Library/Messages/chat.db` (read-only)
  - Query messages with `rowid > last_rowid` from `data/imessage_state.json`
  - Return list of (rowid, text) tuples

- [x] Task 3: Implement `scripts/check_imessage.py` main entrypoint <!-- commit: cddf17d -->
  - Calls `read_pending_messages()` → `parse_config_update()` → `apply_config_update()`
  - Updates `data/imessage_state.json` with latest processed rowid
  - Prints summary of changes applied (or "no changes")
  - Safe to run repeatedly (idempotent)

- [x] Task 4: Conductor - User Manual Verification 'Phase 3: iMessage Integration'

---

## Phase 4: Documentation
<!-- execution: sequential -->

- [x] Task 1: Create `docs/imessage_shortcut_setup.md` <!-- commit: 1e72e1a -->
  - macOS Full Disk Access setup (Terminal / app)
  - How to create a macOS Shortcut that runs `scripts/check_imessage.py`
  - How to set up a cron job as an alternative trigger
  - Example messages that work

- [x] Task 2: Conductor - User Manual Verification 'Phase 4: Documentation'
