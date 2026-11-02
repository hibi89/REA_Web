"""Prevent unlisted importable files or forged initializer from passing the synthetic runner gate.

Only self-authored test fixtures are generated; added files are never executed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile

import pytest

from test_project_bundle import package


def _clean_bundle(tmp_path):
    packed, _ = package(tmp_path)
    extracted = tmp_path / "isolated_extraction"
    extracted.mkdir()
    with zipfile.ZipFile(packed) as archive:
        archive.extractall(extracted)
    return extracted


def _check(extracted):
    return subprocess.run([sys.executable, "runtime_entry.py", "--check"],
                          cwd=extracted, text=True, capture_output=True, timeout=15)


@pytest.mark.parametrize("extra", [
    "fastapi.py", "backend/helpers.py", "dashboard/tracker.js", "other/nested.py",
])
def test_unlisted_extracted_file_is_refused_without_running_it(tmp_path, extra):
    extracted = _clean_bundle(tmp_path)
    assert _check(extracted).returncode == 0
    injected = extracted / extra
    injected.parent.mkdir(parents=True, exist_ok=True)
    injected.write_text("raise RuntimeError('NEVER_IMPORT_THIS_MODULE')\n", encoding="utf-8")
    result = _check(extracted)
    assert result.returncode == 2 and "REFUSED" in result.stderr
    assert ("untracked" in result.stderr or "unexpected" in result.stderr)


def test_unlisted_empty_directory_is_refused(tmp_path):
    extracted = _clean_bundle(tmp_path)
    assert _check(extracted).returncode == 0
    (extracted / "unexpected_empty_directory").mkdir()
    result = _check(extracted)
    assert result.returncode == 2 and "unexpected package directory" in result.stderr


def test_modified_backend_initializer_is_refused_even_with_forged_hash_table(tmp_path):
    extracted = _clean_bundle(tmp_path)
    assert _check(extracted).returncode == 0
    initializer = extracted / "backend" / "__init__.py"
    initializer.write_text("# Changed initializer\nraise RuntimeError('NEVER_RUN_THIS')\n", encoding="utf-8")
    hashes_path = extracted / "SHA256SUMS.json"
    hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
    hashes["backend/__init__.py"] = hashlib.sha256(initializer.read_bytes()).hexdigest()
    hashes_path.write_text(json.dumps(hashes), encoding="utf-8")
    result = _check(extracted)
    assert result.returncode == 2 and "trusted backend package initializer changed" in result.stderr
