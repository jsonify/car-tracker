"""Tests for scripts/check_imessage.py — read_pending_messages and main pipeline."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.check_imessage import read_pending_messages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_fake_chat_db(path: Path, messages: list[tuple[int, str]]) -> None:
    """Create a minimal chat.db with a message table."""
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE message (rowid INTEGER PRIMARY KEY, text TEXT, is_from_me INTEGER)"
    )
    conn.executemany(
        "INSERT INTO message (rowid, text, is_from_me) VALUES (?, ?, 1)", messages
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# read_pending_messages tests
# ---------------------------------------------------------------------------


class TestReadPendingMessages:
    def test_returns_messages_newer_than_last_rowid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "chat.db"
            state = Path(tmpdir) / "state.json"
            _make_fake_chat_db(db, [(1, "hello"), (2, "update price to 400"), (3, "bye")])
            state.write_text(json.dumps({"last_rowid": 1}))

            result = read_pending_messages(db, state)

        assert len(result) == 2
        assert result[0] == (2, "update price to 400")
        assert result[1] == (3, "bye")

    def test_returns_empty_list_when_no_new_messages(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "chat.db"
            state = Path(tmpdir) / "state.json"
            _make_fake_chat_db(db, [(1, "old message"), (2, "another old")])
            state.write_text(json.dumps({"last_rowid": 2}))

            result = read_pending_messages(db, state)

        assert result == []

    def test_creates_state_file_if_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "chat.db"
            state = Path(tmpdir) / "state.json"
            _make_fake_chat_db(db, [(1, "first message"), (2, "second message")])
            # state file does NOT exist

            result = read_pending_messages(db, state)

            assert len(result) == 2
            assert state.exists()
            saved = json.loads(state.read_text())
            assert saved["last_rowid"] == 0

    def test_returns_all_messages_when_last_rowid_is_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "chat.db"
            state = Path(tmpdir) / "state.json"
            _make_fake_chat_db(db, [(1, "msg1"), (2, "msg2"), (3, "msg3")])
            state.write_text(json.dumps({"last_rowid": 0}))

            result = read_pending_messages(db, state)

        assert len(result) == 3

    def test_skips_null_text_messages(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Path(tmpdir) / "chat.db"
            state = Path(tmpdir) / "state.json"
            _make_fake_chat_db(db, [(1, None), (2, "real message")])
            state.write_text(json.dumps({"last_rowid": 0}))

            result = read_pending_messages(db, state)

        texts = [text for _, text in result]
        assert None not in texts
        assert "real message" in texts
