# Spec: Remote Config Updates via iMessage

## Overview
A Python script + macOS Shortcuts integration that lets the user send a
natural-language iMessage to update `holding_price` and/or
`holding_vehicle_type` in `config.yaml`, then automatically commits and
pushes the change to GitHub. The next cron run picks up the updated config
via the existing `git pull --rebase` in `run.sh`.

## Functional Requirements

### 1. Message Source — iMessage (Primary)
- A Python script (`scripts/check_imessage.py`) reads recent messages from
  the macOS Messages database (`~/Library/Messages/chat.db`)
- It looks for unprocessed messages from a configured sender (defaults to
  the user's own Apple ID / phone number)
- Can be triggered on-demand via a macOS Shortcut or run as a cron job

### 2. Natural Language Parsing
- `parse_config_update(text)` extracts field updates from free-form text
- Supported patterns (examples):
  - "update holding price to 375"
  - "change my holding price to $400"
  - "set holding type to SUV"
  - "update holding price to 350 for Standard Car"
- Returns a dict of fields to update, e.g. `{"holding_price": 350.0}`
- Validates: price must be a positive number; vehicle type must be
  non-empty string
- Returns empty dict if no recognized update intent is found
- Regex-based — no external API required

### 3. Config Update + Git Push
- `apply_config_update(updates, config_path)` patches only the specified
  fields in `config.yaml` (preserves all other values and comments)
- Runs `git add config.yaml && git commit && git push`
- Commit message: `chore(config): update holding config via iMessage`
- Idempotent: if parsed values match current config, skips commit/push

### 4. Processed Message Tracking
- Tracks the `rowid` of the last processed Messages DB row in
  `data/imessage_state.json` to avoid re-processing old messages

### 5. macOS Shortcut (Documented)
- A setup guide (`docs/imessage_shortcut_setup.md`) documents how to create
  a macOS Shortcut that triggers `scripts/check_imessage.py` on-demand or
  on a schedule

## Non-Functional Requirements
- Requires **Full Disk Access** granted to Terminal (or the app running the
  script) in macOS System Settings to read `chat.db`
- No external services, APIs, or paid accounts required
- Script is safe to run frequently (idempotent, no side effects on no-op)

## Acceptance Criteria
- [ ] Sending "update holding price to 400" via iMessage (to self or a
      designated contact) causes `config.yaml` to update and push to GitHub
- [ ] `holding_price` and `holding_vehicle_type` can be updated independently
      or in the same message
- [ ] Unrecognized / irrelevant messages are silently skipped (no crash, no
      partial update)
- [ ] Previously processed messages are not re-processed on subsequent runs
- [ ] Parser tests cover ≥80% of `parse_config_update` logic
- [ ] `docs/imessage_shortcut_setup.md` documents the Shortcut setup steps

## Out of Scope
- Updating search dates, times, or location via message
- Email as a trigger channel (future enhancement)
- Authentication / sender allowlist
- SMS via Twilio or other external services
