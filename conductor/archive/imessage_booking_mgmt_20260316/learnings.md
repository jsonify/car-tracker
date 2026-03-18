# Track Learnings: imessage_booking_mgmt_20260316

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `attributedBody` TypedStream fallback for macOS Ventura+ message content (from: imessage_config_20260315)
- iMessage state tracked via `data/imessage_state.json` with `last_rowid` key (from: imessage_config_20260315)
- `parse_config_update` returns a dict; `apply_config_update` dispatches on its keys (from: multi_booking_20260316)
- Booking identifier resolved by name or 1-based index via `_resolve_booking()` (from: multi_booking_20260316)
- `scripts/` needs `__init__.py`; use `pythonpath = ["."]` in pyproject.toml for test imports (from: import_history_20260315)
- `osascript` subprocess calls marked `# pragma: no cover` — I/O only, not unit testable

---

<!-- Learnings from implementation will be appended below -->
