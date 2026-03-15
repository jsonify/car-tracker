# Plan: Remote Config Updates via GitHub

Based on: spec.md

---

## Phase 1: Audit & Validate Repo State

- [x] Task 1: Confirm config.yaml has no secrets
  - Read `config.yaml` and verify no credential fields (email passwords, API keys)
  - Confirm `config.yaml` appears in `git ls-files`
  - Confirm `.env` is listed in `.gitignore`
  - Confirm `data/*.db` is covered by `*.db` in `.gitignore`

- [x] Task 2: Write config safety test
  - Test that loading `config.yaml` produces no credential-related keys
    (guard against accidentally adding secrets in future edits)
  - Test that config file is parseable YAML

- [x] Task: Conductor - User Manual Verification 'Audit & Validate Repo State' (Protocol in workflow.md)

---

## Phase 2: Git Pull Wrapper Script

- [x] Task 1: Write `run.sh` cron wrapper
  - Script steps:
    1. `cd` to repo root
    2. `git pull` with a 10s timeout; on failure, log a warning to `car-tracker.log`
    3. Activate `.venv` and exec the scraper (same args as current crontab)
  - Make script executable (`chmod +x`)

- [x] Task 2: Test wrapper script locally
  - Run `./run.sh` manually; confirm scraper executes
  - Simulate pull failure (disable network or use `--dry-run`); confirm warning logged and scraper still runs

- [x] Task: Conductor - User Manual Verification 'Git Pull Wrapper Script' (Protocol in workflow.md)

---

## Phase 3: Update Crontab

- [x] Task 1: Replace crontab entry
  - Update crontab: replace direct `python -m car_tracker ...` call with `run.sh`
  - Verify new crontab entry with `crontab -l`

- [ ] Task 2: End-to-end remote test
  - Edit `config.yaml` directly on GitHub.com (change a holding value)
  - Trigger `run.sh` manually; confirm git pull picks up the change
  - Confirm scraper uses updated config values

- [ ] Task: Conductor - User Manual Verification 'Update Crontab' (Protocol in workflow.md)
