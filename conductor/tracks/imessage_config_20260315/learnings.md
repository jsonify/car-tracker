# Track Learnings: imessage_config_20260315

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Always import from `car_tracker.*` (installed package via uv), never `src.car_tracker.*`
- Add `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `pyproject.toml` to make `scripts/` importable in tests
- `scripts/` directory needs `__init__.py` to be importable as a package in tests
- I/O-only functions marked `# pragma: no cover` — same rationale as `send_email`
- Mock `subprocess.run` for git operations in tests (never actually run git in unit tests)
- Email credentials loaded from `.env` via `python-dotenv` — never store secrets in tracked files
- SQLite FK enforcement: run `PRAGMA foreign_keys = ON` per connection
- Use `git pull --rebase` not `--ff-only` in shell scripts

---

## [2026-03-15] - Phase 2 Tasks 1-2: Config Update & Git Push
- **Implemented:** Tests for `apply_config_update` + confirmed implementation
- **Files changed:** `tests/test_update_config.py`
- **Commit:** 343cadc
- **Learnings:**
  - Patterns: Use `tempfile.TemporaryDirectory()` for isolated config file tests; no real disk state affected
  - Gotchas: `yaml.dump` with `sort_keys=False` preserves field order; always use it to avoid confusing diffs
  - Context: `subprocess.run` mocked with `patch("subprocess.run")` — check `mock_run.call_args_list` to assert all 3 git commands fired
---

<!-- Learnings from implementation will be appended below -->

## [2026-03-15] - Phase 1 Tasks 1-2: Natural Language Parser
- **Implemented:** Regex-based `parse_config_update(text)` in `scripts/update_config.py`
- **Files changed:** `scripts/update_config.py`, `tests/test_update_config.py`
- **Commit:** c267e37
- **Learnings:**
  - Patterns: Use 3 regex patterns — combined (price+type in one message), price-only, type-only — check combined first to avoid partial matches
  - Gotchas: `re.VERBOSE` flag requires escaping spaces inside character classes; use `\s` not literal spaces in verbose patterns
  - Context: `apply_config_update` lives in the same file; Phase 1 tests only cover the parser (63% of file), Phase 2 will bring total to 100%
---
