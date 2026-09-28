import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_poster_html.py"
SPEC = importlib.util.spec_from_file_location("package_poster_html", SCRIPT)
PACKAGE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(PACKAGE)


class PackagePosterHtmlTests(unittest.TestCase):
    def test_embeds_html_and_css_assets_and_fonts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "hero.png").write_bytes(b"fake png")
            (root / "render.html").write_text(
                """<!doctype html><html><head><style>.hero { background-image: url('hero.png'); }</style></head>
                <body><main id=\"longform-canvas\"><img src=\"hero.png\"></main></body></html>""",
                encoding="utf-8",
            )
            html, proof = PACKAGE.package_html(root / "render.html")
            self.assertIn(PACKAGE.PORTABLE_MARKER, html)
            self.assertIn("data:image/png;base64,", html)
            self.assertIn("data:font/otf;base64,", html)
            self.assertEqual(proof["embedded_font_count"], 3)
            self.assertIn('font-weight: 400', html)
            self.assertEqual(proof["embedded_local_asset_count"], 2)
            self.assertTrue(proof["portable_html"])

    def test_rejects_remote_image_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "render.html"
            source.write_text(
                '<html><head></head><body><img src="https://example.com/hero.png"></body></html>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "remote asset"):
                PACKAGE.package_html(source)

    def test_rejects_non_embedded_portable_document(self):
        with self.assertRaisesRegex(ValueError, "missing yinxi portable-poster marker"):
            PACKAGE.validate_portable_document("<html></html>")


if __name__ == "__main__":
    unittest.main()
