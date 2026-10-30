"""Regression: bounded owner SHA and matching preview/build bytes (synthetic only)."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from rea import guided, mvp
from rea.mvp import DataError, MAX_BYTES, generate, source_sha256


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "owner.csv"
    source.write_text("id,title,category\nA,One,Food\n", encoding="utf-8")
    return source


def test_streamed_sha_matches_exact_original(tmp_path):
    source = make_source(tmp_path)
    assert source_sha256(source) == hashlib.sha256(source.read_bytes()).hexdigest()
    assert guided.preflight(source)["source_sha256"] == source_sha256(source)


def test_full_generation_never_calls_source_read_bytes(tmp_path, monkeypatch):
    source = make_source(tmp_path)
    original_read_bytes = Path.read_bytes

    def forbidden_unbounded_read(path):
        if path == source:
            raise AssertionError("Never load the entire owner source to hash it")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", forbidden_unbounded_read)
    out = tmp_path / "generated"
    manifest = generate(source, out)
    assert manifest["rows"] == 1
    assert manifest["sha256"] == source_sha256(source)
    assert (out / "data.sqlite").is_file()


def test_oversized_file_fails_before_opening_source(tmp_path, monkeypatch):
    source = tmp_path / "giant.csv"
    with source.open("wb") as handle:
        handle.write(b"id,title,category\n")
        handle.seek(MAX_BYTES)
        handle.write(b"x")

    def should_never_open(*args, **kwargs):
        raise AssertionError("Oversized owner file reached os.open")

    with monkeypatch.context() as patch:
        patch.setattr(mvp.os, "open", should_never_open)
        with pytest.raises(DataError, match="10 MiB"):
            source_sha256(source)
    with pytest.raises(DataError, match="10 MiB"):
        generate(source, tmp_path / "never")
    assert not (tmp_path / "never").exists()


def test_owner_symlink_and_non_input_extension_rejected_before_read(tmp_path):
    source = make_source(tmp_path)
    alias = tmp_path / "linked.csv"
    try:
        alias.symlink_to(source)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation unavailable")
    with pytest.raises(DataError, match="symlink"):
        source_sha256(alias)
    with pytest.raises(DataError, match="regular"):
        source_sha256(tmp_path / "note.txt")


def test_preview_refuses_source_changed_during_parse(tmp_path, monkeypatch):
    source = make_source(tmp_path)
    original_parse = guided.parse_input

    def modified_after_parse(path, **kwargs):
        result = original_parse(path, **kwargs)
        source.write_text("id,title,category\nB,Changed,Food\n", encoding="utf-8")
        return result

    monkeypatch.setattr(guided, "parse_input", modified_after_parse)
    with pytest.raises(DataError, match="changed during preview"):
        guided.preflight(source)


def test_generate_refuses_source_changed_during_parse(tmp_path, monkeypatch):
    source = make_source(tmp_path)
    original_parse = mvp.parse_input

    def modified_after_parse(path, **kwargs):
        result = original_parse(path, **kwargs)
        source.write_text("id,title,category\nB,Changed,Food\n", encoding="utf-8")
        return result

    monkeypatch.setattr(mvp, "parse_input", modified_after_parse)
    target = tmp_path / "not-published"
    with pytest.raises(DataError, match="Source changed during generation"):
        generate(source, target)
    assert not target.exists()


def test_pair_append_uses_bounded_streaming_sha(tmp_path, monkeypatch):
    from rea.two_source import _sha256, preflight_pair

    first = make_source(tmp_path)
    second = tmp_path / "second.csv"
    second.write_text("id,title,category\nB,Two,Food\n", encoding="utf-8")
    forbidden = {first, second}
    original = Path.read_bytes

    def no_full_read(path):
        if path in forbidden:
            raise AssertionError("Two-file approval used unbounded read_bytes")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", no_full_read)
    result = preflight_pair(first, second)
    assert result["combined_rows"] == 2
    assert result["sources"][0]["sha256"] == _sha256(first)
    assert result["sources"][1]["sha256"] == _sha256(second)


def test_pair_append_oversize_source_is_rejected_early(tmp_path):
    from rea.two_source import preflight_pair

    first = make_source(tmp_path)
    huge = tmp_path / "oversize.csv"
    with huge.open("wb") as handle:
        handle.seek(MAX_BYTES)
        handle.write(b"x")
    with pytest.raises(DataError, match="10 MiB"):
        preflight_pair(first, huge)


def test_pair_append_refuses_changed_source_since_preview(tmp_path):
    from rea.two_source import _approval

    first = make_source(tmp_path)
    pinned = source_sha256(first)
    first.write_text("id,title,category\nB,Changed,Food\n", encoding="utf-8")
    with pytest.raises(DataError, match="changed after inspection"):
        _approval(first, {"id": "id", "title": "title", "category": "category"},
                  pinned, "APPROVE")
