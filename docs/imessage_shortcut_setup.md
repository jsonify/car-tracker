# iMessage Config Update Setup

This guide explains how to trigger `scripts/check_imessage.py` — the script
that reads your iMessages and updates `config.yaml` — either on-demand via a
macOS Shortcut or automatically via cron.

---

## Prerequisites

### 1. Grant Full Disk Access to Terminal

The script reads `~/Library/Messages/chat.db`, which requires Full Disk Access.

1. Open **System Settings → Privacy & Security → Full Disk Access**
2. Click **+** and add **Terminal** (or whichever app will run the script)
3. Toggle it **on**

> If you run the script via a macOS Shortcut, you may need to add **Shortcuts**
> to the Full Disk Access list instead of (or in addition to) Terminal.

---

## How it works

`scripts/check_imessage.py` does the following each time it runs:

1. Reads messages from `~/Library/Messages/chat.db` with a `rowid` greater
   than the last processed row (tracked in `data/imessage_state.json`)
2. Parses each message for recognized update commands (see examples below)
3. Applies matching updates to `config.yaml`
4. Commits and pushes the updated config to GitHub
5. Saves the latest `rowid` to `data/imessage_state.json` so messages are
   never processed twice

The next scheduled cron run picks up the updated config automatically via
`git pull --rebase` in `run.sh`.

---

## Message Format

Send yourself (or a designated contact) an iMessage with any of these patterns:

| Intent | Example message |
|--------|----------------|
| Update holding price | `update holding price to 375` |
| Update holding price (with $) | `change my holding price to $400.50` |
| Update vehicle type | `set holding type to SUV` |
| Update both at once | `update holding price to 350 for Standard Car` |

- Price must be a positive number
- Vehicle type is matched as-is (case-sensitive) — use the exact category name
  shown in the email report (e.g. `Economy Car`, `SUV`, `Minivan`)
- Unrecognized or irrelevant messages are silently skipped

---

## Option A: Run manually from Terminal

```bash
cd /path/to/car-tracker
uv run python -m scripts.check_imessage
```

With a custom config path:

```bash
uv run python -m scripts.check_imessage --config /path/to/config.yaml
```

---

## Option B: macOS Shortcut (on-demand)

Create a Shortcut that runs the script with a single tap from the menu bar,
Dock, or Home Screen.

1. Open **Shortcuts** → click **+** to create a new shortcut
2. Search for and add the **Run Shell Script** action
3. Set **Shell** to `/bin/zsh`
4. Set **Input** to nothing (leave blank)
5. Paste the following script:

```zsh
cd /Users/<you>/code/car-tracker
source .venv/bin/activate
python -m scripts.check_imessage --config config.yaml
```

Replace `/Users/<you>/code/car-tracker` with your actual repo path.

6. Name the shortcut (e.g. **"Check iMessage Config"**)
7. Optionally add it to the **Menu Bar** via the shortcut's settings

> **Full Disk Access for Shortcuts:** If the script can't open `chat.db` when
> run via Shortcuts, go to **System Settings → Privacy & Security →
> Full Disk Access** and add **Shortcuts** to the list.

---

## Option C: cron (automatic, recommended)

`run.sh` already calls `check_imessage.py` automatically before each scraper
run. If you have the cron job set up per the README, no additional configuration
is needed — iMessage updates will be applied at the start of every scheduled run.

To run the iMessage check on its own schedule (e.g. every 30 minutes):

```bash
crontab -e
```

Add:

```
*/30 * * * * cd /Users/<you>/code/car-tracker && source .venv/bin/activate && python -m scripts.check_imessage >> /tmp/car-tracker-imessage.log 2>&1
```

Replace `/Users/<you>/code/car-tracker` with your actual repo path.

---

## Troubleshooting

**"operation not permitted" or "unable to open database"**
→ Terminal (or Shortcuts) does not have Full Disk Access. See Prerequisites above.

**Script runs but config never updates**
→ Check that `data/imessage_state.json` exists and `last_rowid` is not ahead
  of the message you sent. Reset by setting `last_rowid` to `0` to reprocess
  all messages.

**Git push fails**
→ Ensure your SSH key or HTTPS credentials are configured for the remote.
  Run `git push` manually from the repo to verify.

**Message parsed but values unchanged**
→ The script is idempotent — if the parsed values already match `config.yaml`,
  no commit is made. This is expected behavior.
