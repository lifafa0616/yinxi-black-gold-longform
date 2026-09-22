import importlib.util
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VERIFY_CASE_LAYOUT = load_script("verify-case-layout.py")
EXPORT_LAYOUT_MANIFEST = load_script("export_layout_manifest.py")
PACKAGE_POSTER_HTML = load_script("package_poster_html.py")


class PreconfirmationToolTests(unittest.TestCase):
    def test_create_case_plan_writes_only_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "create_case_plan.py"),
                    "--output-root",
                    str(output_root),
                    "--case",
                    "test-case",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            case_dir = output_root / "cases" / "test-case"
            self.assertTrue((case_dir / "plan.md").is_file())
            self.assertEqual(
                sorted(path.relative_to(case_dir).as_posix() for path in case_dir.rglob("*")),
                ["plan.md"],
            )

    def test_manifest_rejects_poster_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            poster_html = Path(directory) / "poster.html"
            poster_html.write_text("<html>checkpoint poster</html>", encoding="utf-8")
            manifest = {
                "producer": "playwright-dom",
                "layout_engine": "playwright-chromium",
                "contract": "yinxi-layout-manifest-v2",
                "poster_sha256": "0" * 64,
            }
            issues = []

            VERIFY_CASE_LAYOUT.validate_manifest_provenance(manifest, poster_html, issues)

            self.assertEqual(issues, ["layout manifest was not measured from this exact poster.html"])

    def test_exporter_hashes_crlf_poster_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            poster_html = Path(directory) / "poster.html"
            poster_html.write_bytes(b"<html>\r\ncheckpoint poster\r\n</html>\r\n")

            actual = EXPORT_LAYOUT_MANIFEST.poster_sha256(poster_html)

            self.assertEqual(actual, hashlib.sha256(poster_html.read_bytes()).hexdigest())

    def test_manifest_rejects_self_attested_values_that_differ_from_fresh_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            poster_html = Path(directory) / "poster.html"
            poster_html.write_text("<html>checkpoint poster</html>", encoding="utf-8")
            manifest = {
                "producer": "playwright-dom",
                "layout_engine": "playwright-chromium",
                "contract": "yinxi-layout-manifest-v2",
                "poster_sha256": hashlib.sha256(poster_html.read_bytes()).hexdigest(),
                "canvas": {"width": 1080, "color": "#10100F"},
            }
            fresh_measurement = {**manifest, "canvas": {"width": 999, "color": "#10100F"}}
            issues = []

            VERIFY_CASE_LAYOUT.validate_manifest_provenance(
                manifest,
                poster_html,
                issues,
                measure_manifest=lambda _: fresh_measurement,
            )

            self.assertEqual(issues, ["layout manifest differs from a fresh Chromium measurement of poster.html"])

    @unittest.skipUnless(importlib.util.find_spec("playwright"), "Playwright runtime is not installed")
    def test_exporter_extracts_required_markers_from_a_crlf_portable_poster(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "render.html"
            source.write_text(
                """<!doctype html><html><head><style>
                html, body { margin: 0; } #longform-canvas { width: 1080px; min-height: 1400px; background: #10100F; color: white; }
                [data-hero] { display: block; height: 600px; } [data-background-sample], [data-seam-sample] { display: block; height: 1px; }
                </style></head><body><main id=\"longform-canvas\" data-canvas-color=\"#10100F\">
                <section data-reading-zone=\"intro\" data-contract=\"L01\"><div data-hero-copy>Hero copy</div><div data-hero=\"imagegen\"></div><i data-background-sample></i></section>
                <i data-seam-sample=\"intro-body\"></i><section data-layout-chapter=\"one\"><h2 data-chapter-title>Chapter</h2></section>
                <p data-protected-text=\"claim\">Protected claim</p>
                <section data-portrait=\"transparent\"><p data-portrait-intro>Intro</p><div data-portrait-related-text-region><div data-portrait-subject>Portrait</div></div></section>
                </main></body></html>""",
                encoding="utf-8",
            )
            portable, _ = PACKAGE_POSTER_HTML.package_html(source)
            poster_html = root / "poster.html"
            poster_html.write_bytes(portable.replace("\n", "\r\n").encode("utf-8"))

            manifest = EXPORT_LAYOUT_MANIFEST.build_manifest(poster_html)

            self.assertEqual(manifest["poster_sha256"], hashlib.sha256(poster_html.read_bytes()).hexdigest())
            self.assertEqual(manifest["chapters"][0]["id"], "one")
            self.assertEqual(manifest["protected_boxes"][0]["id"], "claim")
            self.assertEqual(manifest["portraits"][0]["portrait_mode"], "transparent")


if __name__ == "__main__":
    unittest.main()
