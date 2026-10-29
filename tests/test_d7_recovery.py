"""D7 local synthetic security + recovery regression (not penetration certification)."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sqlite3
import zipfile

import pytest
from fastapi.testclient import TestClient

from rea import delivery, mvp, orchestrator, safe_publish
from rea.delivery import DeliveryError, create_delivery, verify_delivery
from rea.orchestrator import build

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "samples" / "qa_cafe.csv"
JSON = ROOT / "samples" / "qa_products.json"


def client(folder: Path):
    spec = importlib.util.spec_from_file_location("rea_d7_local_app", folder / "app.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return TestClient(mod.app), mod


@pytest.mark.parametrize("source", [CSV, JSON])
def test_atomic_directory_publish_rejects_racing_empty_owner_dir(tmp_path, monkeypatch, source):
    target = tmp_path / "result"
    before = source.read_bytes()
    atomic = safe_publish.publish_directory

    def racer(stage, dest):
        dest.mkdir()  # owner creates a target at the last possible moment
        with pytest.raises(FileExistsError):
            atomic(stage, dest)
        raise FileExistsError("racing directory owned by someone else")

    monkeypatch.setattr(mvp, "publish_directory", racer)
    with pytest.raises(FileExistsError):
        mvp.generate(source, target)
    assert target.is_dir() and list(target.iterdir()) == []
    assert source.read_bytes() == before
    assert not list(tmp_path.glob(".rea-staging-*"))


def test_orchestrator_last_moment_collision_preserves_owner(tmp_path, monkeypatch):
    target = tmp_path / "owner"
    original = orchestrator.publish_directory

    def racing(stage, dest):
        dest.mkdir()
        (dest / "important.txt").write_text("OWNER", encoding="utf-8")
        with pytest.raises(FileExistsError):
            original(stage, dest)
        raise FileExistsError("Owner target exists")

    monkeypatch.setattr(orchestrator, "publish_directory", racing)
    with pytest.raises(FileExistsError):
        build(CSV, target)
    assert (target / "important.txt").read_text(encoding="utf-8") == "OWNER"
    assert not list(tmp_path.glob(".rea-orchestrator-*"))


def test_broken_symlink_output_cannot_redirect_generator(tmp_path):
    original = tmp_path / "real"
    redirect = tmp_path / "pointer"
    redirect.symlink_to(original, target_is_directory=True)
    with pytest.raises(FileExistsError):
        mvp.generate(CSV, redirect)
    with pytest.raises(FileExistsError):
        build(JSON, redirect)
    assert redirect.is_symlink() and not original.exists()


def test_failed_file_copy_rolls_back_staging_and_preserves_source(tmp_path, monkeypatch):
    before = JSON.read_bytes()
    out = tmp_path / "target"
    def fail_copy(*a, **kw):
        raise OSError("simulated broken destination")
    monkeypatch.setattr(mvp.shutil, "copytree", fail_copy)
    with pytest.raises(OSError, match="simulated"):
        build(JSON, out)
    assert not out.exists()
    assert not list(tmp_path.glob(".rea-orchestrator-*"))
    assert JSON.read_bytes() == before


def test_existing_owner_dir_is_not_touched_or_deleted(tmp_path):
    dest = tmp_path / "exists"
    dest.mkdir()
    (dest / "owner.txt").write_text("DO NOT DELETE", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build(CSV, dest)
    assert (dest / "owner.txt").read_text(encoding="utf-8") == "DO NOT DELETE"


@pytest.mark.parametrize("source", [CSV, JSON])
def test_last_moment_zip_collision_is_atomic_and_preserves_owner(tmp_path, monkeypatch, source):
    archive = tmp_path / "product.zip"
    original = source.read_bytes()
    atomic = safe_publish.publish_archive
    def concurrent_writer(stage, dest):
        dest.write_bytes(b"OWNER ARCHIVE")
        atomic(stage, dest)  # os.link -> FileExistsError without replacing
    monkeypatch.setattr(delivery, "publish_archive", concurrent_writer)
    with pytest.raises(FileExistsError):
        create_delivery(source, archive)
    assert archive.read_bytes() == b"OWNER ARCHIVE"
    assert source.read_bytes() == original
    assert not list(tmp_path.glob(".rea-export-*"))


@pytest.mark.skipif(os.name != "nt", reason="Windows rename branch only")
def test_windows_zip_publication_uses_atomic_rename_without_hardlinks(tmp_path, monkeypatch):
    archive = tmp_path / "published.zip"
    stage = tmp_path / "staged.zip"
    stage.write_bytes(b"complete verified ZIP")

    def forbidden_link(*a, **kw):
        pytest.fail("Windows archive publication must not require hard links")

    monkeypatch.setattr(safe_publish.os, "link", forbidden_link)
    safe_publish.publish_archive(stage, archive)
    assert archive.read_bytes() == b"complete verified ZIP"
    assert not stage.exists()

    collision = tmp_path / "owner.zip"
    collision.write_bytes(b"OWNER ARCHIVE")
    stage.write_bytes(b"other ZIP")
    with pytest.raises(FileExistsError):
        safe_publish.publish_archive(stage, collision)
    assert collision.read_bytes() == b"OWNER ARCHIVE"
    assert stage.read_bytes() == b"other ZIP"


def test_zip_atomic_publish_failure_does_not_create_partial_archive(tmp_path, monkeypatch):
    archive = tmp_path / "not-created.zip"
    def no_atomic_publish(*a, **kw):
        raise OSError("simulated unsupported destination filesystem")
    if os.name == "nt":
        monkeypatch.setattr(safe_publish.os, "rename", no_atomic_publish)
    else:
        monkeypatch.setattr(safe_publish.os, "link", no_atomic_publish)
    with pytest.raises(OSError, match="unsupported"):
        create_delivery(CSV, archive)
    assert not archive.exists()
    assert not list(tmp_path.glob(".rea-export-*"))


def test_zip_failure_before_publication_rolls_back(tmp_path, monkeypatch):
    archive = tmp_path / "not-created.zip"
    def corrupt(*a, **kw):
        raise DeliveryError("simulated verification failure")
    monkeypatch.setattr(delivery, "verify_delivery", corrupt)
    with pytest.raises(DeliveryError, match="verification"):
        create_delivery(CSV, archive)
    assert not archive.exists()
    assert not list(tmp_path.glob(".rea-export-*"))


def test_broken_symlink_archive_target_is_never_replaced(tmp_path):
    archive = tmp_path / "link.zip"
    redirect = tmp_path / "missing.zip"
    archive.symlink_to(redirect)
    with pytest.raises(FileExistsError):
        create_delivery(CSV, archive)
    assert archive.is_symlink()
    assert not redirect.exists()


def test_truncated_zip_is_rejected(tmp_path):
    target = tmp_path / "valid.zip"
    broken = tmp_path / "truncated.zip"
    create_delivery(CSV, target)
    broken.write_bytes(target.read_bytes()[:100])
    with pytest.raises((zipfile.BadZipFile, DeliveryError)):
        verify_delivery(broken)


def test_generated_sqlite_is_query_only_and_http_has_no_write_route(tmp_path):
    out = tmp_path / "app"
    build(JSON, out)
    api, mod = client(out)
    assert api.get("/api/items").json()["total"] == 4
    with mod.connection() as connection:
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError):
            connection.execute(
                "INSERT INTO items(id,title,category,attributes_json) VALUES ('X','X','X','{}')")
    assert api.post("/api/items", json={"id": "X"}).status_code == 405
    assert api.put("/api/items/J01", json={"title": "changed"}).status_code == 405
    assert api.delete("/api/items/J01").status_code == 405
    assert api.get("/openapi.json").status_code == 200  # schema only, not admin UI
    assert api.get("/docs").status_code == 404
    assert api.get("/redoc").status_code == 404
    for route in ("/manifest.json", "/schema_preview.json", "/data.sqlite",
                  "/review/fable_review.json", "/requirements.txt"):
        assert api.get(route).status_code == 404


def test_sql_injection_like_and_wildcards_cannot_expose_extra_rows(tmp_path):
    out = tmp_path / "app"
    build(CSV, out)
    api, _ = client(out)
    for needle in ("' OR 1=1 --", "%", "_"):
        r = api.get("/api/items", params={"q": needle})
        assert r.status_code == 200
        assert r.json()["total"] == 0
    assert api.get("/api/items").json()["total"] == 4


def test_spreadsheet_formula_values_remain_inert_text(tmp_path):
    source = ROOT / "samples" / "qa_formula.csv"
    out = tmp_path / "app"
    build(source, out)
    api, _ = client(out)
    info = api.get("/api/items/F01").json()
    assert info["title"] == "=1+1"
    assert info["attributes"]["note"].startswith("=CMD")
    js = (out / "static" / "app.js").read_text(encoding="utf-8")
    assert "textContent" in js and "innerHTML" not in js
    assert api.get("/api/items").json()["total"] == 4


def test_json_summary_provenance_never_pretends_csv(tmp_path):
    out = tmp_path / "json-app"
    build(JSON, out)
    api, _ = client(out)
    assert api.get("/api/summary").json()["source_kind"] == "customer_supplied_json_snapshot"
