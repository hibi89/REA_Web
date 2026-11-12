"""Synthetic-only REA Lite packaging and exact original builder integration tests."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from rea.lite_builder import build_lite
from rea.lite_delivery import DeliveryError, package_lite, verify_lite_zip, FILES


class LiteDeliveryTest(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.source = self.root / "approved.csv"
        self.html = self.root / "catalog.html"
        self.zip = self.root / "customer.zip"
        self.source.write_text("식별자,이름,분류,비고\nA01,콜드브루,음료,합성 테스트\nA02,라떼,음료,합성 테스트\n",
                               encoding="utf-8")

    def create_html(self, theme="cafe"):
        actual = hashlib.sha256(self.source.read_bytes()).hexdigest()
        result = build_lite(self.source, self.html,
                            mapping={"id": "식별자", "title": "이름", "category": "분류"},
                            expected_sha256=actual, confirmation="APPROVE",
                            theme=theme, name="사용자 승인 합성 상품")
        return result

    def pack(self, acknowledgement="ACK_PLAINTEXT_LOCAL_DATA", expected=None):
        if expected is None:
            expected = hashlib.sha256(self.html.read_bytes()).hexdigest()
        return package_lite(self.html, self.zip, expected_html_sha256=expected,
                            acknowledge=acknowledgement)

    def test_all_three_verticals_real_original_builder(self):
        for theme, title in (("cafe", "콜드브루"), ("inventory", "재고품"), ("office", "보고서")):
            with self.subTest(theme=theme):
                self.source.write_text("식별자,이름,분류,비고\nA01," + title +
                                       ",유형,합성 테스트\nA02,두번째,유형,합성 테스트\n", encoding="utf-8")
                self.html = self.root / (theme + ".html")
                self.zip = self.root / (theme + ".zip")
                receipt = self.create_html(theme)
                outcome = self.pack(expected=receipt["html_sha256"])
                self.assertEqual(outcome["rows"], 2)
                self.assertEqual(outcome["columns"], 4)
                self.assertFalse(outcome["sale_approved"])
                self.assertTrue(outcome["plaintext_data_embedded"])
                self.assertEqual(outcome, verify_lite_zip(self.zip))
                with zipfile.ZipFile(self.zip) as archive:
                    self.assertEqual(set(archive.namelist()), set(FILES))
                    self.assertIn(title, archive.read("catalog.html").decode("utf-8"))
                    self.assertNotIn(title, archive.read("manifest.json").decode("utf-8"))

    def test_deterministic_two_archives(self):
        self.create_html()
        one = self.pack()
        original = self.zip.read_bytes()
        self.zip = self.root / "second.zip"
        self.assertEqual(one, self.pack())
        self.assertEqual(original, self.zip.read_bytes())

    def test_existing_output_preserved(self):
        self.create_html()
        self.zip.write_bytes(b"KEEP")
        with self.assertRaises(DeliveryError):
            self.pack()
        self.assertEqual(self.zip.read_bytes(), b"KEEP")

    def test_approval_required(self):
        self.create_html()
        with self.assertRaises(DeliveryError):
            self.pack(acknowledgement="YES")
        self.assertFalse(self.zip.exists())

    def test_changed_source_sha(self):
        self.create_html()
        self.html.write_text(self.html.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaises(DeliveryError):
            self.pack(expected="0" * 64)
        self.assertFalse(self.zip.exists())

    def test_bad_html_contract(self):
        self.create_html()
        source = self.html.read_text(encoding="utf-8")
        self.html.write_text(source.replace("REA_LITE_V1", "REA_LITE_FAKE"), encoding="utf-8")
        with self.assertRaises(DeliveryError):
            self.pack()
        self.assertFalse(self.zip.exists())

    def test_symlink_input_denied(self):
        self.create_html()
        link = self.root / "source-link.html"
        try:
            link.symlink_to(self.html)
        except OSError:
            self.skipTest("symlink creation not supported")
        with self.assertRaises(DeliveryError):
            package_lite(link, self.zip, expected_html_sha256=hashlib.sha256(self.html.read_bytes()).hexdigest(),
                         acknowledge="ACK_PLAINTEXT_LOCAL_DATA")

    def test_output_parent_symlink_denied(self):
        self.create_html()
        directory = self.root / "nested"
        directory.mkdir()
        linked = self.root / "alias"
        try:
            linked.symlink_to(directory, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation not supported")
        with self.assertRaises(DeliveryError):
            package_lite(self.html, linked / "out.zip", expected_html_sha256=hashlib.sha256(self.html.read_bytes()).hexdigest(),
                         acknowledge="ACK_PLAINTEXT_LOCAL_DATA")

    def rewrite_zip(self, change):
        self.create_html()
        self.pack()
        with zipfile.ZipFile(self.zip) as archive:
            files = [(entry.filename, archive.read(entry)) for entry in archive.infolist()]
        change(files)
        with zipfile.ZipFile(self.zip, "w") as archive:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                for name, content in files:
                    archive.writestr(name, content)

    def test_zip_html_modification_refused(self):
        def change(files):
            for pos, (name, data) in enumerate(files):
                if name == "catalog.html":
                    files[pos] = (name, data.replace("콜드브루".encode("utf-8"), "커피위조".encode("utf-8")))
        self.rewrite_zip(change)
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_zip_manifest_modification_refused(self):
        def change(files):
            for pos, (name, data) in enumerate(files):
                if name == "manifest.json":
                    files[pos] = (name, data.replace(b'"rows":2', b'"rows":3'))
        self.rewrite_zip(change)
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_extra_zip_member_refused(self):
        self.rewrite_zip(lambda files: files.append(("../malicious.txt", b"test")))
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_duplicate_member_refused(self):
        self.rewrite_zip(lambda files: files.append(files[0]))
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_replaced_readme_refused(self):
        def change(files):
            for i, (name, content) in enumerate(files):
                if name == "README_KO.txt":
                    files[i] = (name, b"changed")
        self.rewrite_zip(change)
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_oversized_member_refused(self):
        def change(files):
            for i, (name, content) in enumerate(files):
                if name == "manifest.json":
                    files[i] = (name, b"x" * 70000)
        self.rewrite_zip(change)
        with self.assertRaises(DeliveryError):
            verify_lite_zip(self.zip)

    def test_cli_avoids_raw_customer_values(self):
        self.create_html()
        self.pack()
        command = [sys.executable, "-m", "rea.lite_delivery", "verify", "--zip", str(self.zip)]
        result = subprocess.run(command, capture_output=True, text=True,
                                cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["rows"], 2)
        self.assertNotIn("콜드브루", result.stdout)
        self.assertFalse(json.loads(result.stdout)["sale_approved"])

    def test_invalid_zip_fails_without_data_dump(self):
        self.zip.write_bytes(b"invalid ZIP customer private row")
        command = [sys.executable, "-m", "rea.lite_delivery", "verify", "--zip", str(self.zip)]
        result = subprocess.run(command, capture_output=True, text=True,
                                cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(result.returncode, 2)
        self.assertIn("REA_LITE_DELIVERY_BLOCKED", result.stdout)
        self.assertNotIn("private row", result.stdout)


if __name__ == "__main__":
    unittest.main()
