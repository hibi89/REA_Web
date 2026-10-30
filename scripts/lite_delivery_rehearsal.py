"""Three synthetic Lite deliveries through the actual seller inspect/build CLI.

No customer data and no production/release action. Outputs are CI evidence only.
Usage: python scripts/lite_delivery_rehearsal.py --out-dir .tmp-lite-rehearsal
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from zipfile import ZipFile, ZIP_DEFLATED

REPO = Path(__file__).resolve().parents[1]

CASES = (
    {
        "theme": "cafe",
        "title": "가상 카페 메뉴",
        "columns": ["item_code", "item_name", "group", "price"],
        "mapping": {"id": "item_code", "title": "item_name", "category": "group"},
        "rows": [
            ["A001", "아메리카노", "커피", "4500"],
            ["A002", "카페라테", "커피", "5000"],
            ["B001", "레몬에이드", "음료", "5500"],
        ],
    },
    {
        "theme": "inventory",
        "title": "가상 부품 목록",
        "columns": ["part_no", "part_name", "segment", "quantity"],
        "mapping": {"id": "part_no", "title": "part_name", "category": "segment"},
        "rows": [
            ["P101", "M8 볼트", "금속", "280"],
            ["P102", "십자 드라이버", "도구", "45"],
            ["P103", "알루미늄 판", "금속", "12"],
        ],
    },
    {
        "theme": "office",
        "title": "가상 사무 기록",
        "columns": ["entry_key", "entry_title", "division", "state"],
        "mapping": {"id": "entry_key", "title": "entry_title", "category": "division"},
        "rows": [
            ["R001", "비품 확인", "운영", "완료"],
            ["R002", "회의실 정비", "시설", "진행"],
        ],
    },
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def cli(*args: str, expected: int = 0) -> dict | str:
    proc = subprocess.run(
        [sys.executable, "-m", "rea.lite_builder", *args],
        cwd=REPO, text=True, encoding="utf-8",
        errors="replace", capture_output=True, timeout=45,
    )
    if proc.returncode != expected:
        raise AssertionError(
            f"CLI returned {proc.returncode}, expected {expected}; "
            f"stderr={proc.stderr[-250:]} stdout={proc.stdout[-250:]}"
        )
    if expected:
        return proc.stdout
    return json.loads(proc.stdout)


def write_csv(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def parse_payload(html: str) -> dict:
    tag = '<script id="rea-payload" type="application/json">'
    if html.count(tag) != 1:
        raise AssertionError("Missing or repeated application payload")
    payload_text = html.split(tag, 1)[1].split("</script>", 1)[0]
    return json.loads(payload_text)


def checked_delivery(case: dict, out_dir: Path) -> dict:
    theme = case["theme"]
    source = out_dir / f"{theme}_SOURCE.csv"
    target = out_dir / f"{theme}_DEMO.html"
    write_csv(source, case["columns"], case["rows"])
    source_hash = digest(source)

    started = time.perf_counter()
    inspection = cli("inspect", "--source", str(source))
    inspect_ms = round((time.perf_counter() - started) * 1000, 2)
    assert inspection["sha256"] == source_hash
    assert inspection["columns"] == case["columns"]
    assert inspection["row_count"] == len(case["rows"])
    assert not target.exists()

    m = case["mapping"]
    args = (
        "build", "--source", str(source), "--out", str(target),
        "--id-field", m["id"], "--title-field", m["title"],
        "--category-field", m["category"],
        "--source-sha256", source_hash, "--confirm", "APPROVE",
        "--theme", theme, "--name", case["title"],
    )
    started = time.perf_counter()
    receipt = cli(*args)
    build_ms = round((time.perf_counter() - started) * 1000, 2)
    assert receipt["status"] == "CREATED_UNAPPROVED_FOR_SALE"
    assert receipt["rows"] == len(case["rows"])
    assert receipt["source_sha256"] == source_hash
    assert target.is_file()

    html = target.read_text(encoding="utf-8")
    embedded = parse_payload(html)
    assert embedded["theme"] == theme
    assert embedded["sourceColumns"] == case["columns"]
    assert embedded["mapping"] == case["mapping"]
    assert embedded["title"] == case["title"]
    assert len(embedded["records"]) == len(case["rows"])
    for entry, row in zip(embedded["records"], case["rows"], strict=True):
        original = dict(zip(case["columns"], row, strict=True))
        assert entry["id"] == original[m["id"]]
        assert entry["title"] == original[m["title"]]
        assert entry["category"] == original[m["category"]]
    assert "http://" not in html and "https://" not in html
    assert "connect-src 'none'" in html
    assert "src=\"http" not in html and "<script src=" not in html
    assert digest(source) == source_hash

    html_hash = digest(target)
    # Existing output MUST be refused, preserving exact bytes.
    cli(*args, expected=2)
    assert digest(target) == html_hash
    assert digest(source) == source_hash
    assert not list(out_dir.glob(".rea-lite-*.tmp"))

    return {
        "theme": theme, "input_sha256": source_hash,
        "html_sha256": html_hash, "rows": len(case["rows"]),
        "html_bytes": target.stat().st_size,
        "inspect_cli_ms": inspect_ms, "build_cli_ms": build_ms,
        "unchanged_input": True, "no_overwrite": True,
        "self_contained_no_network": True,
    }


def create_package(out_dir: Path, deliveries: list[dict]) -> dict:
    # Cafe updates match the seller-generated four-column mapping, not
    # unrelated historical standalone demos.
    cafe = CASES[0]
    valid = out_dir / "cafe_VALID_update.csv"
    invalid = out_dir / "cafe_INVALID_duplicate_id.csv"
    write_csv(valid, cafe["columns"], [
        ["A010", "아이스, 아메리카노", "커피", "4700"],
        ["A011", "카페라테", "커피", "5100"],
        ["B011", "레몬에이드", "음료", "5600"],
        ["C010", "초코케이크", "디저트", "7000"],
        ["C011", "녹차케이크", "디저트", "6900"],
    ])
    write_csv(invalid, cafe["columns"], [
        ["A001", "첫 번째", "커피", "4500"],
        ["A001", "중복", "커피", "5000"],
    ])
    readme = out_dir / "WINDOWS_HUMAN_PILOT_README.txt"
    readme.write_text(
        "REA_WEB Lite human Windows pilot — synthetic only.\n"
        "This package was built with the real Pro parser through the Lite CLI.\n"
        "1. Unpack into a NEW folder. Double-click cafe_DEMO.html, then\n"
        "   inventory_DEMO.html and office_DEMO.html in Chrome and Edge.\n"
        "2. Confirm file:/// URL, no Python/server, search/filter/sort/details.\n"
        "3. In cafe, choose cafe_INVALID_duplicate_id.csv: error and old 3 rows.\n"
        "4. Choose cafe_VALID_update.csv: exactly 5 rows.\n"
        "5. Click '변경 내용 HTML로 저장', close and re-open the NEW HTML.\n"
        "   Five updated rows must remain. Originals must be byte-identical.\n"
        "6. Record browser/version, outcomes and human elapsed time separately.\n"
        "No personal/customer data. HTML embeds plaintext. Not approved for sale.\n",
        encoding="utf-8",
    )
    package_paths = [
        *(out_dir / f"{c['theme']}_DEMO.html" for c in CASES),
        *(out_dir / f"{c['theme']}_SOURCE.csv" for c in CASES),
        valid, invalid, readme,
    ]
    manifest = out_dir / "SHA256SUMS.txt"
    manifest.write_text("".join(
        f"{digest(p)}  {p.name}\n" for p in sorted(package_paths, key=lambda p: p.name)
    ), encoding="ascii")
    package_paths.append(manifest)
    package = out_dir / "REA_WEB_Lite_Synthetic_Pilot.zip"
    with ZipFile(package, "x", compression=ZIP_DEFLATED) as archive:
        for p in sorted(package_paths, key=lambda p: p.name):
            archive.write(p, p.name)
    with ZipFile(package) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(package_paths)
        for p in package_paths:
            assert archive.read(p.name) == p.read_bytes()
    return {"name": package.name, "sha256": digest(package),
            "bytes": package.stat().st_size, "entries": len(package_paths)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    out_dir = args.out_dir.resolve()
    # No overwrite/cleanup of someone else's files.
    out_dir.mkdir(parents=True, exist_ok=False)
    deliveries = [checked_delivery(case, out_dir) for case in CASES]
    package = create_package(out_dir, deliveries)
    report = {
        "status": "SYNTHETIC_AUTOMATED_DELIVERY_PASS",
        "not_human": True, "not_seller_approval": True,
        "not_customer_data": True, "not_windows_human_acceptance": True,
        "cases": deliveries, "package": package,
    }
    (out_dir / "rehearsal_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
