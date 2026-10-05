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
    def test_embeds_local_assets_and_injects_google_fonts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "hero.png").write_bytes(b"fake png")
            (root / "render.html").write_text(
                """<!doctype html><html><head><style>.hero { background-image: url('hero.png'); }</style></head>
                <body><main id=\"longform-canvas\"><img src=\"hero.png\"></main></body></html>""",
                encoding="utf-8",
            )
            html, proof = PACKAGE.package_html(root / "render.html")
            self.assertIn(PACKAGE.RENDER_DOCUMENT_MARKER, html)
            self.assertIn("data:image/png;base64,", html)
            self.assertIn(PACKAGE.GOOGLE_FONTS_STYLESHEET.replace("&", "&amp;"), html)
            self.assertNotIn("data:font/", html)
            self.assertEqual(proof["font_source"], "google-fonts-css2")
            self.assertEqual(proof["required_fonts"], ["Noto Serif SC 700", "Noto Sans SC 400", "Noto Sans SC 500"])
            self.assertEqual(proof["embedded_local_asset_count"], 2)
            self.assertTrue(proof["render_document"])

    def test_rejects_remote_image_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "render.html"
            source.write_text(
                '<html><head></head><body><img src="https://example.com/hero.png"></body></html>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "remote asset"):
                PACKAGE.package_html(source)

    def test_rejects_render_document_without_google_fonts(self):
        with self.assertRaisesRegex(ValueError, "missing yinxi render-document marker"):
            PACKAGE.validate_render_document("<html></html>")

    def test_rewrites_legacy_font_family_names_for_existing_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "render.html"
            source.write_text(
                """<!doctype html><html><head><style>
                .title { font-family: "Yinxi Noto Serif SC"; }
                .body { font-family: "Yinxi Noto Sans SC"; }
                </style></head><body><main id="longform-canvas">课程</main></body></html>""",
                encoding="utf-8",
            )

            html, proof = PACKAGE.package_html(source)

            self.assertNotIn("Yinxi Noto", html)
            self.assertIn('font-family: "Noto Serif SC"', html)
            self.assertIn('font-family: "Noto Sans SC"', html)
            self.assertEqual(proof["font_source"], "google-fonts-css2")

    def test_rejects_unapproved_external_stylesheet(self):
        html, _ = PACKAGE.package_html(Path(__file__).resolve().parents[1] / "assets" / "template" / "render.html")
        injected = html.replace("</head>", '<link rel="stylesheet" href="https://example.com/font.css"></head>')
        with self.assertRaisesRegex(ValueError, "unapproved external stylesheet"):
            PACKAGE.validate_render_document(injected)

    @unittest.skipUnless(importlib.util.find_spec("playwright"), "Playwright runtime is not installed")
    def test_font_probe_rejects_system_fallback_when_web_fonts_are_missing(self):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body>字体探针</body></html>")
            self.assertFalse(page.evaluate(PACKAGE.FONT_READY_SCRIPT))
            browser.close()


if __name__ == "__main__":
    unittest.main()
