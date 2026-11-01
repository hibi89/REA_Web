"""Owner pilot output tests. No customer records, no public release claim."""
import hashlib
import json
import zipfile
import pytest

from scripts.rea_lite_owner_pilot import create, THEMES


def test_three_theme_archive_digests_html_and_updates(tmp_path):
    out = tmp_path / "owner.zip"
    receipt = create(out)
    assert receipt["status"] == "PILOT_ONLY_NOT_APPROVED_FOR_SALE"
    assert receipt["sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    with zipfile.ZipFile(out) as zipped:
        names = zipped.namelist()
        assert names == sorted(names)
        assert len(names) == 9
        assert all(not x.startswith("/") and ".." not in x.split("/") for x in names)
        manifest = json.loads(zipped.read("MANIFEST.json"))
        hashes = json.loads(zipped.read("SHA256SUMS.json"))
        assert manifest["status"] == receipt["status"]
        assert not manifest["contains_real_customer_data"]
        assert manifest["themes"] == list(THEMES)
        assert set(hashes) == set(names) - {"SHA256SUMS.json"}
        assert set(manifest["files"]) == set(hashes) - {"MANIFEST.json"}
        for name, sha in hashes.items():
            assert hashlib.sha256(zipped.read(name)).hexdigest() == sha
        for theme in THEMES:
            html = zipped.read(f"{theme}.html").decode("utf-8")
            assert "__REA_PAYLOAD_JSON__" not in html
            assert html.count('<script id="rea-payload" type="application/json">') == 1
            assert "합성" in html
            assert "http://" not in html and "https://" not in html
            assert zipped.read(f"updates/{theme}_update.csv").startswith(b"item_code")
        assert b"real customer data" not in zipped.read("README_FIRST_KO.txt")


def test_reproducible_zip_and_no_overwrite(tmp_path):
    one, two = tmp_path / "one.zip", tmp_path / "two.zip"
    first = create(one)
    second = create(two)
    assert first["sha256"] == second["sha256"]
    old = one.read_bytes()
    with pytest.raises(ValueError):
        create(one)
    assert one.read_bytes() == old


def test_invalid_destination_refused_without_mutation(tmp_path):
    with pytest.raises(ValueError):
        create(tmp_path / "bad.txt")
    assert not (tmp_path / "bad.txt").exists()
