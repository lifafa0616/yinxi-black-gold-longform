import importlib.util
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
            self.assertFalse(list(case_dir.glob("**/poster.html")))

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


if __name__ == "__main__":
    unittest.main()
