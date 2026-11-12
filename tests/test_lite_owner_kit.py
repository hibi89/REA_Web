"""Offline owner-kit acceptance: real original parser and safe rollback on failures."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rea.lite_owner_kit import (CONTRACT, HTML_NAME, ZIP_NAME, build_owner_kit)
from rea.lite_delivery import DeliveryError, verify_lite_zip

SAMPLE = "식별자,이름,분류,비고\nA01,콜드브루,카페,합성\nA02,나무의자,비품,합성\n"


class OwnerKitTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "source.csv"
        self.source.write_text(SAMPLE, encoding="utf-8")
        self.output = self.root / "kit"
        self.output.mkdir()
        self.options = {
            "mapping": {"id": "식별자", "title": "이름", "category": "분류"},
            "expected_source_sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
            "confirm": "APPROVE", "acknowledge_plaintext": "ACK_PLAINTEXT_LOCAL_DATA"
        }

    def build(self, **changes):
        return build_owner_kit(self.source, self.output, **{**self.options, **changes})

    def test_three_independent_business_cases(self):
        for theme, product in (("cafe", "콜드브루"), ("inventory", "재고자산"),
                               ("office", "문서보관")):
            with self.subTest(theme=theme):
                self.output = self.root / theme
                self.output.mkdir()
                self.source.write_text(
                    "식별자,이름,분류,비고\nA01," + product + ",품목,합성\nA02,두번째,품목,합성\n",
                    encoding="utf-8")
                self.options["expected_source_sha256"] = hashlib.sha256(self.source.read_bytes()).hexdigest()
                result = self.build(theme=theme)
                self.assertEqual(result["contract"], CONTRACT)
                self.assertFalse(result["sale_approved"])
                self.assertFalse(result["buyer_accepted"])
                self.assertFalse(result["remote_transfer"])
                self.assertTrue(result["source_data_embedded_plaintext"])
                self.assertEqual(result["rows"], 2)
                self.assertEqual(result["columns"], 4)
                self.assertEqual(result["html_file"], HTML_NAME)
                self.assertEqual(result["delivery_zip"], ZIP_NAME)
                self.assertEqual(verify_lite_zip(self.output / ZIP_NAME)["html_sha256"], result["html_sha256"])
                self.assertIn(product, (self.output / HTML_NAME).read_text(encoding="utf-8"))
                self.assertEqual(self.source.read_text(encoding="utf-8").count(product), 1)

    def test_existing_html_preserved(self):
        target = self.output / HTML_NAME
        target.write_text("KEEP", encoding="utf-8")
        with self.assertRaises(DeliveryError):
            self.build()
        self.assertEqual(target.read_text(encoding="utf-8"), "KEEP")
        self.assertFalse((self.output / ZIP_NAME).exists())

    def test_existing_zip_preserved_without_creating_html(self):
        target = self.output / ZIP_NAME
        target.write_bytes(b"KEEP_ZIP")
        with self.assertRaises(DeliveryError):
            self.build()
        self.assertEqual(target.read_bytes(), b"KEEP_ZIP")
        self.assertFalse((self.output / HTML_NAME).exists())

    def test_explicit_approval_required_before_any_file(self):
        for change in ({"confirm": "YES"}, {"acknowledge_plaintext": ""}):
            with self.subTest(change=change):
                with self.assertRaises(DeliveryError):
                    self.build(**change)
                self.assertEqual(list(self.output.iterdir()), [])

    def test_stale_sha_source_refused(self):
        self.source.write_text(SAMPLE + "A03,변경된상품,카페,합성\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_invalid_owner_field_mapping_refused(self):
        with self.assertRaises(ValueError):
            self.build(mapping={"id": "식별자", "title": "이름", "category": "이름"})
        self.assertEqual(list(self.output.iterdir()), [])

    def test_rollback_if_zip_build_fails(self):
        with patch("rea.lite_owner_kit.package_lite", side_effect=DeliveryError("SYNTHETIC_FAILURE")):
            with self.assertRaises(DeliveryError):
                self.build()
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertEqual(self.source.read_text(encoding="utf-8"), SAMPLE)

    def test_rollback_if_independent_zip_recheck_fails(self):
        with patch("rea.lite_owner_kit.verify_lite_zip", side_effect=DeliveryError("SYNTHETIC_RECHECK_FAIL")):
            with self.assertRaises(DeliveryError):
                self.build()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_rollback_if_original_sha_changes_after_package(self):
        real = verify_lite_zip
        def change_original_and_verify(path):
            self.source.write_text(SAMPLE + "A03,새로운행,사무,합성\n", encoding="utf-8")
            return real(path)
        with patch("rea.lite_owner_kit.verify_lite_zip", side_effect=change_original_and_verify):
            with self.assertRaises(DeliveryError):
                self.build()
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertIn("새로운행", self.source.read_text(encoding="utf-8"))

    def test_refuse_symlink_output_directory(self):
        actual = self.root / "target"
        actual.mkdir()
        alias = self.root / "link"
        try:
            alias.symlink_to(actual, target_is_directory=True)
        except OSError:
            self.skipTest("symlink unsupported")
        with self.assertRaises(ValueError):
            build_owner_kit(self.source, alias,
                            **self.options)
        self.assertEqual(list(actual.iterdir()), [])

    def test_cli_success_no_raw_cells(self):
        argv = [sys.executable, "-m", "rea.lite_owner_kit", "--source", str(self.source),
                "--out-dir", str(self.output), "--source-sha256",
                self.options["expected_source_sha256"], "--id-field", "식별자",
                "--title-field", "이름", "--category-field", "분류",
                "--confirm", "APPROVE", "--acknowledge-plaintext", "ACK_PLAINTEXT_LOCAL_DATA",
                "--theme", "cafe", "--name", "합성 테스트"]
        done = subprocess.run(argv, capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(done.returncode, 0, done.stderr)
        output = json.loads(done.stdout)
        self.assertEqual(output["rows"], 2)
        self.assertNotIn("콜드브루", done.stdout)
        self.assertTrue((self.output / HTML_NAME).is_file())
        self.assertTrue((self.output / ZIP_NAME).is_file())
        second = subprocess.run(argv, capture_output=True, text=True,
                                cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(second.returncode, 2)
        self.assertIn("REA_LITE_OWNER_KIT_BLOCKED", second.stdout)
        self.assertNotIn("콜드브루", second.stdout)

    def test_rollback_does_not_unlink_swapped_output(self):
        import rea.lite_owner_kit as module
        current = self.root / "replacement"
        current.write_text("MUST_BE_PRESERVED", encoding="utf-8")
        def swap_and_fail(_zip_path):
            target = self.output / HTML_NAME
            target.unlink()
            current.replace(target)
            raise DeliveryError("SYNTHETIC_REPLACEMENT")
        with patch.object(module, "_identity", side_effect=module._identity):
            with patch("rea.lite_owner_kit.package_lite", side_effect=swap_and_fail):
                with self.assertRaises(DeliveryError):
                    self.build()
        self.assertEqual((self.output / HTML_NAME).read_text(encoding="utf-8"), "MUST_BE_PRESERVED")


if __name__ == "__main__":
    unittest.main()
