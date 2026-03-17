# Plan: iMessage Booking Management

## Phase 1: Parser — add booking and list bookings

- [ ] Task 1: Write tests for `add booking` and `list bookings` parsing
  - Test valid `add booking <name> <location> <date> <time> <date> <time>` is parsed correctly
  - Test invalid date format (not YYYY-MM-DD) returns empty dict
  - Test invalid time format (not HH:MM) returns empty dict
  - Test `list bookings` command is recognised

- [ ] Task 2: Implement `add booking` and `list bookings` parsing in `parse_config_update`
  - Add `_ADD_BOOKING_PATTERN` regex
  - Add `list bookings` detection
  - Return `{"action": "add_booking", ...fields}` or `{"action": "list_bookings"}`

- [ ] Task: Conductor - User Manual Verification 'Parser' (Protocol in workflow.md)

## Phase 2: Config writer — append booking

- [ ] Task 1: Write tests for `apply_config_update` with `add_booking` action
  - Test new booking is appended to `bookings:` list
  - Test duplicate name returns False and leaves config unchanged
  - Test git commands called on successful add

- [ ] Task 2: Implement `add_booking` branch in `apply_config_update`
  - Detect `action == "add_booking"` in updates dict
  - Check for duplicate name, raise `ValueError` if found
  - Append new booking dict to `config["bookings"]`
  - Write, git add/commit/push

- [ ] Task: Conductor - User Manual Verification 'Config Writer' (Protocol in workflow.md)

## Phase 3: iMessage reply — `send_imessage` and `list bookings` response

- [ ] Task 1: Write tests for `send_imessage` and `list_bookings_reply`
  - Test `list_bookings_reply` formats reply string correctly (with and without holding)
  - Test `send_imessage` constructs correct `osascript` command (mocked subprocess)

- [ ] Task 2: Implement `send_imessage` and `list_bookings_reply`
  - Add `send_imessage(phone, message)` helper in `scripts/update_config.py` (`# pragma: no cover` on osascript call)
  - Add `list_bookings_reply(bookings)` pure function returning formatted string
  - Wire into `check_imessage.main`: handle `list_bookings` action, send reply
  - On `add_booking` success or error, send iMessage reply

- [ ] Task: Conductor - User Manual Verification 'iMessage Reply' (Protocol in workflow.md)
