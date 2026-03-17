# Spec: iMessage Booking Management

## Overview
Extend the iMessage command interface to support creating new bookings and
listing existing bookings. Replies are delivered back via iMessage using
`osascript` to the configured phone number.

## Functional Requirements

### `add booking` command
- Format: `add booking <name> <location> <pickup_date> <pickup_time> <dropoff_date> <dropoff_time>`
  - e.g. `add booking hawaii HNL 2026-05-01 10:00 2026-05-08 10:00`
- Appends a new booking entry to the `bookings:` list in `config.yaml`
- Holding price/type not set on creation — can be added later via `update holding`
- Commits and pushes `config.yaml` after adding
- Sends an iMessage reply confirming the booking was added (or an error if parsing fails)
- Duplicate booking names are rejected with a clear error reply

### `list bookings` command
- Triggered by: `list bookings` (case-insensitive)
- Sends an iMessage reply listing all current bookings:
  ```
  1. hawaii_may — $420.00 Economy Car
  2. vegas_june — $199.00 Standard Car
  3. portland — no holding
  ```
- Reply sent to `imessage.phone_number` in `config.yaml` via `osascript`

### iMessage reply mechanism
- All replies use `osascript` to send via the Messages app
- Phone number read from `config.yaml` under `imessage.phone_number`
- `send_imessage(phone, message)` helper in `scripts/update_config.py` (marked `# pragma: no cover`)

## Non-Functional Requirements
- `add booking` and `list bookings` are parsed in `parse_config_update()` alongside existing commands
- `osascript` failures are caught and logged — they do not crash `check_imessage`
- Date format validation: reject `add booking` commands with non-YYYY-MM-DD dates or non-HH:MM times

## Acceptance Criteria
- [ ] `add booking` appends to `config.yaml`, commits, pushes, and replies via iMessage
- [ ] Duplicate name produces an error reply, no config change
- [ ] Invalid date/time format produces an error reply, no config change
- [ ] `list bookings` replies with index, name, and holding info per booking
- [ ] `send_imessage` helper is testable (pure string construction) with `osascript` call mocked
- [ ] All new logic has unit tests

## Out of Scope
- Removing/deleting bookings via iMessage
- Updating search dates via iMessage
- Support for multiple phone numbers
