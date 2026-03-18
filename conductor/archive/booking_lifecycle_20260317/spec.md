# Spec: Booking Countdown & Expiration

## Overview
Two related enhancements to the booking lifecycle:
1. Each booking's holding banner in the email gains a countdown line showing days until the pick-up date.
2. After the pick-up date passes, the booking is removed from `config.yaml` and pushed to git. If no bookings remain, a one-time "monitoring paused" notification email is sent.

## Functional Requirements

### FR-1: Countdown Display in Email Banner
- For each booking rendered in the email, the holding banner header includes a second line showing the number of days until the booking's pick-up date.
- Format: `X days until your booking` (where X is the integer number of days remaining).
- When the pick-up date is today (countdown = 0): display `Today is your booking day!` instead.
- The countdown line appears on its own line below the main booking banner header.

### FR-2: Booking Expiration
- On each run, after computing the current date, check each booking in `config.yaml`.
- If a booking's pick-up date is strictly in the past (i.e., today > pick-up date), remove it from `config.yaml`.
- After removal: auto-commit the updated `config.yaml` and push to git (consistent with existing config-change patterns).
- Multiple expired bookings may be removed in a single run.

### FR-3: Empty Bookings — Monitoring Paused Notification
- If all bookings are removed (or the bookings list was already empty) and no email has been sent yet for this "paused" state, send a one-time notification email informing the user that monitoring is paused until a new booking is added.
- On subsequent runs with no bookings, skip silently (no email sent) — the notification is only sent once per transition to the empty state.
- A state flag in `data/imessage_state.json` tracks whether the paused notification has been sent. This flag resets when a new booking is added.

## Non-Functional Requirements
- The countdown is computed relative to the local machine date at runtime (no timezone conversion required — personal-use tool running on local macOS).
- Config file writes follow the existing `config.yaml` write + git commit/push pattern.

## Acceptance Criteria
- [ ] Email for a booking with a future pick-up date shows `X days until your booking` on a separate line in the booking header area.
- [ ] Email for a booking whose pick-up date is today shows `Today is your booking day!`.
- [ ] On the first run where today > pick-up date, the booking is removed from `config.yaml`, committed, and pushed.
- [ ] If that removal leaves `bookings: []`, a single notification email is sent stating monitoring is paused.
- [ ] Subsequent runs with no bookings send no email.
- [ ] When a booking is added again, the paused-notification flag resets.

## Out of Scope
- No changes to how bookings are added or edited (iMessage booking management is handled by existing track).
- No changes to the scraping logic or price comparison pipeline.
- No per-booking email suppression (if a booking still has days remaining, the full email is sent as normal).
