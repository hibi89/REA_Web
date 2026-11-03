"""A forged package manifest must not pass the trusted synthetic launcher gate.

Only an independently authored synthetic fixture is generated. This test never
executes the backend application and does not check arbitrary customer archives.
"""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile

import pytest

from test_project_bundle import package


@pytest.mark.parametrize("field, forged", [
    ("status", "CUSTOMER_PRODUCTION_APPROVED"),
    ("trusted_synthetic_only", False),
    ("file_count", 999),
])
def test_edited_manifest_is_rejected_even_without_digest_table_entry(tmp_path, field, forged):
    archive, _ = package(tmp_path)
    extracted = tmp_path / "CLEAN_MANIFEST_PIN"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as z:
        z.extractall(extracted)

    def check():
        return subprocess.run(
            [sys.executable, "runtime_entry.py", "--check"],
            cwd=extracted, capture_output=True, text=True, timeout=15,
        )

    initial = check()
    assert initial.returncode == 0, initial.stderr

    path = extracted / "MANIFEST.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[field] = forged
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check()
    assert result.returncode == 2, result.stderr
    assert "synthetic project manifest differs from approved bundle" in result.stderr
