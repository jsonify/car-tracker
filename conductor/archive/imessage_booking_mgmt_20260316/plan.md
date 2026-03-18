# Plan: iMessage Booking Management

## Phase 1: Parser — add booking and list bookings

- [x] Task 1: Write tests for `add booking` and `list bookings` parsing <!-- commit: 23c7ce7 -->
  - Test valid `add booking <name> <location> <date> <time> <date> <time>` is parsed correctly
  - Test invalid date format (not YYYY-MM-DD) returns empty dict
  - Test invalid time format (not HH:MM) returns empty dict
  - Test `list bookings` command is recognised

- [x] Task 2: Implement `add booking` and `list bookings` parsing in `parse_config_update` <!-- commit: 23c7ce7 -->
  - Add `_ADD_BOOKING_PATTERN` regex
  - Add `list bookings` detection
  - Return `{"action": "add_booking", ...fields}` or `{"action": "list_bookings"}`

- [x] Task: Conductor - User Manual Verification 'Parser' (Protocol in workflow.md)

## Phase 2: Config writer — append booking

- [x] Task 1: Write tests for `apply_config_update` with `add_booking` action <!-- commit: 23c7ce7 -->
  - Test new booking is appended to `bookings:` list
  - Test duplicate name returns False and leaves config unchanged
  - Test git commands called on successful add

- [x] Task 2: Implement `add_booking` branch in `apply_config_update` <!-- commit: 23c7ce7 -->
  - Detect `action == "add_booking"` in updates dict
  - Check for duplicate name, raise `ValueError` if found
  - Append new booking dict to `config["bookings"]`
  - Write, git add/commit/push

- [x] Task: Conductor - User Manual Verification 'Config Writer' (Protocol in workflow.md)

## Phase 3: iMessage reply — `send_imessage` and `list bookings` response

- [x] Task 1: Write tests for `send_imessage` and `list_bookings_reply` <!-- commit: 23c7ce7 -->
  - Test `list_bookings_reply` formats reply string correctly (with and without holding)
  - Test `send_imessage` constructs correct `osascript` command (mocked subprocess)

- [x] Task 2: Implement `send_imessage` and `list_bookings_reply` <!-- commit: 23c7ce7 -->
  - Add `send_imessage(phone, message)` helper in `scripts/update_config.py` (`# pragma: no cover` on osascript call)
  - Add `list_bookings_reply(bookings)` pure function returning formatted string
  - Wire into `check_imessage.main`: handle `list_bookings` action, send reply
  - On `add_booking` success or error, send iMessage reply
  - Fix: use `first service whose service type is iMessage` for osascript <!-- commit: ac90760 -->

- [x] Task: Conductor - User Manual Verification 'iMessage Reply' (Protocol in workflow.md)
