# Track Learnings: remote_config_20260315

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Email credentials loaded from `.env` via `python-dotenv` — never stored in `config.yaml` or any tracked file
- `.env` is git-ignored; `data/*.db` covered by `*.db` in `.gitignore`
- `config.yaml` is already committed to the repo with no secrets
- Cron entry: `45 6 * * 1,4` running `python -m car_tracker --config /Users/jasonrueckert/code/car-tracker/config.yaml`

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-15] - Phase 2 Task 1: Write run.sh cron wrapper
- **Implemented:** Created run.sh — git pull (non-fatal), activate .venv, exec scraper
- **Files changed:** run.sh
- **Commit:** 69843c9
- **Learnings:**
  - Gotchas: `timeout` is GNU coreutils — not available on macOS without Homebrew. Removed it; git fails fast on its own when network is down.
  - Patterns: `exec python ...` at end of script replaces the shell process — cleaner than a subshell for cron
  - Patterns: `set -euo pipefail` + non-fatal git pull via `if/else` is the right pattern for best-effort operations in bash
## [2026-03-15] - Phase 3 Task 1: Replace crontab entry
- **Implemented:** Updated crontab to call run.sh instead of python directly
- **Files changed:** crontab (system)
- **Commit:** n/a
- **Learnings:**
  - Patterns: run.sh handles venv activation and logging internally — crontab entry becomes a single clean line
---

## [2026-03-15] - Phase 3 Task 2: End-to-end remote test
- **Implemented:** Verified full flow — edit config.yaml on GitHub.com → run.sh pulls → scraper uses updated config
- **Files changed:** run.sh (fix: --ff-only → --rebase), pushed local commits
- **Commit:** 25c1505
- **Learnings:**
  - Gotchas: `--ff-only` fails when local branch has unpushed commits; `--rebase` handles this correctly
  - Gotchas: Must push all local implementation commits before the first cron run — otherwise local/remote diverge and pull fails
  - Patterns: In steady-state (scraper never commits), `git pull --rebase` will always fast-forward cleanly
---

## [2026-03-15] - Phase 2 Task 2: Test wrapper script locally
- **Implemented:** Manual test — confirmed git pull succeeded and scraper ran
- **Files changed:** run.sh (fix: removed timeout)
- **Commit:** bb93c50
- **Learnings:**
  - Gotchas: macOS `timeout` not a built-in — always test shell scripts on the target OS before committing
---

## [2026-03-15] - Phase 1 Task 1: Confirm config.yaml has no secrets
- **Implemented:** Audited config.yaml — no credential fields present; tracked in git; .env and *.db git-ignored
- **Files changed:** (no code changes — audit only)
- **Commit:** 876c472
- **Learnings:**
  - Patterns: config.yaml already clean and safe for repo; no migration needed
  - Gotchas: None
  - Context: Audit took seconds — repo was already in the right state from prior tracks
---

## [2026-03-15] - Phase 1 Task 2: Write config safety test
- **Implemented:** Added 3 safety tests to test_config.py: parseable YAML, no credential keys, loads via load_config
- **Files changed:** tests/test_config.py
- **Commit:** 876c472
- **Learnings:**
  - Patterns: `_collect_keys()` recursive helper walks nested YAML dicts/lists — reusable if we ever need to audit other YAML files
  - Patterns: `Path(__file__).parent.parent / "config.yaml"` anchors tests to the real repo config without hardcoding paths
  - Gotchas: Tests directly reference the real config.yaml — if dates go stale the file should still be valid YAML (load_config validates format, not future-ness of dates)
---
