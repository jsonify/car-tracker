# Spec: Remote Config Updates via GitHub

## Overview
Enable remote editing of the full application config (search parameters,
holding data, email settings) by storing the YAML config file in the
GitHub repository. The cron job performs a `git pull` before each run to
pick up any changes made on GitHub.com from any device.

## Functional Requirements

1. **Config in Repo:** The primary config file (`config.yaml`) is committed
   to the repository and kept up to date in version control.

2. **Remote Editability:** The user can edit `config.yaml` directly on
   GitHub.com (via browser or GitHub mobile app) from any device.

3. **Auto-Sync on Run:** The cron job wrapper performs a `git pull` before
   invoking the scraper, ensuring the latest config is always used.

4. **Sensitive Data Exclusion:** Email credentials and other secrets remain
   in `.env` (git-ignored) and are never committed to the repo. Config
   references secrets via environment variable placeholders.

5. **Conflict Handling:** If `git pull` fails (e.g., merge conflict, no
   network), the run proceeds with the existing local config and logs a
   warning.

## Non-Functional Requirements

- No new dependencies required — uses existing `git` tooling
- `git pull` must complete or time out within a reasonable window (≤10s)
  before the scraper starts
- The `.env` file and any secrets must remain in `.gitignore`

## Acceptance Criteria

- [ ] `config.yaml` is committed to the repo with no secrets
- [ ] Editing `config.yaml` on GitHub.com and triggering a run picks up
      the change automatically
- [ ] `.env` (credentials) is confirmed git-ignored and not committed
- [ ] Cron job wrapper runs `git pull` before the scraper
- [ ] A failed `git pull` logs a warning but does not abort the run

## Out of Scope

- Authentication/authorization to prevent unauthorized edits (repo
  visibility controls this)
- A dedicated web UI or API for config editing
- Automatic config validation before the run starts
