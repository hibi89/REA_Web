"""Regression: offline self-check must release the SQLite handle on Windows.

The SQLite context-manager by itself commits or rolls back; it does not close.
A retained read-only handle prevents deleting temporary recovery directories.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
import zipfile

import pytest

from rea import customer_self_check
from rea.delivery import create_delivery


ROOT = Path(__file__).resolve().parents[1]


class TrackingConnection(sqlite3.Connection):
    close_called = False

    def close(self):
        self.close_called = True
        return super().close()


def test_extracted_selfcheck_closes_sqlite_after_readonly_audit(tmp_path, monkeypatch):
    archive = tmp_path / "delivery.zip"
    create_delivery(ROOT / "samples" / "qa_cafe.csv", archive)
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(extracted)

    real_connect = sqlite3.connect
    handles = []

    def tracked_connect(*args, **kwargs):
        # Observe the real read-only SQLite connection; do not mock the data.
        conn = real_connect(*args, **kwargs, factory=TrackingConnection)
        handles.append(conn)
        return conn

    monkeypatch.setattr(customer_self_check.sqlite3, "connect", tracked_connect)
    result = customer_self_check.inspect(extracted)

    assert result["database"] == "READONLY_OPEN_SUCCESS"
    assert result["row_count_only"] == 4
    assert len(handles) == 1
    assert handles[0].close_called
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        handles[0].execute("SELECT 1")
    # This must also work on Windows, where open SQLite handles lock files.
    restored_db = extracted / "app" / "data.sqlite"
    renamed = restored_db.with_suffix(".sqlite.closed")
    restored_db.rename(renamed)
    renamed.rename(restored_db)
