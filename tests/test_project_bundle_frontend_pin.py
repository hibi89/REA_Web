"""Reject post-extraction frontend edits even when the SHA256SUMS table is forged.

The backend and UI are exclusively self-authored synthetic test fixtures.
No modified frontend is launched or served in these negative cases.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile

import pytest

from test_project_bundle import package


@pytest.mark.parametrize("member", [
    "dashboard/app.js",
    "dashboard/style.css",
    "dashboard/index.html",
    "dashboard/manifest.json",
    "dashboard/README_KO.md",
])
def test_rewritten_checksum_table_cannot_approve_changed_frontend(tmp_path, member):
    archive, _ = package(tmp_path)
    output = tmp_path / "FRONTEND_HASH_PIN"
    output.mkdir()
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(output)

    def check():
        return subprocess.run(
            [sys.executable, "runtime_entry.py", "--check"],
            cwd=output, capture_output=True, text=True, timeout=15,
        )

    baseline = check()
    assert baseline.returncode == 0, baseline.stderr

    altered = output / member
    altered.write_bytes(altered.read_bytes() + b"\n/* not approved */\n")
    hashes_file = output / "SHA256SUMS.json"
    hashes = json.loads(hashes_file.read_text(encoding="utf-8"))
    hashes[member] = hashlib.sha256(altered.read_bytes()).hexdigest()
    hashes_file.write_text(json.dumps(hashes), encoding="utf-8")

    refused = check()
    assert refused.returncode == 2, refused.stderr
    assert "frontend differs from approved synthetic bundle" in refused.stderr
