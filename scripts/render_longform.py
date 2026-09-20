#!/usr/bin/env python3
"""Render one longform HTML source through bundled-font Playwright Chromium.

This script is deliberately a renderer, not an editor. It renders the existing
continuous HTML/CSS source exactly once and emits both the final PNG and a
machine-produced render proof for the layout checker.
"""

import argparse
import json
import sys
from pathlib import Path


CANVAS_WIDTH = 1080
SKILL_ROOT = Path(__file__).resolve().parents[1]
SERIF_FONT = SKILL_ROOT / "assets" / "fonts" / "NotoSerifCJKsc-Bold.otf"
SANS_FONT = SKILL_ROOT / "assets" / "fonts" / "NotoSansCJKsc-Medium.otf"


def main():
    parser = argparse.ArgumentParser(description="Render a longform HTML source with the bundled fonts.")
    parser.add_argument("--input", required=True, type=Path, help="case HTML source containing #longform-canvas")
    parser.add_argument("--output", required=True, type=Path, help="final 1080px PNG path")
    parser.add_argument("--render-proof", required=True, type=Path, help="machine-produced render proof JSON path")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input HTML does not exist: {args.input}")
    missing_fonts = [str(path) for path in (SERIF_FONT, SANS_FONT) if not path.is_file()]
    if missing_fonts:
        parser.error("bundled production fonts are missing: " + ", ".join(missing_fonts))

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print("Playwright is not installed. Run: python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.render_proof.parent.mkdir(parents=True, exist_ok=True)
    font_css = f'''\n@font-face {{ font-family: "Yinxi Noto Serif SC"; src: url("{SERIF_FONT.as_uri()}") format("opentype"); font-weight: 700; font-style: normal; font-display: block; }}\n@font-face {{ font-family: "Yinxi Noto Sans SC"; src: url("{SANS_FONT.as_uri()}") format("opentype"); font-weight: 500; font-style: normal; font-display: block; }}\n'''

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": 1600}, device_scale_factor=1)
        page.goto(args.input.resolve().as_uri(), wait_until="networkidle")
        page.add_style_tag(content=font_css)
        fonts_ready = page.evaluate("""async () => {
            await Promise.all([
                document.fonts.load('700 32px "Yinxi Noto Serif SC"'),
                document.fonts.load('500 32px "Yinxi Noto Sans SC"'),
            ]);
            await document.fonts.ready;
            return document.fonts.status === 'loaded' &&
                document.fonts.check('700 32px "Yinxi Noto Serif SC"') &&
                document.fonts.check('500 32px "Yinxi Noto Sans SC"');
        }""")
        canvas = page.locator("#longform-canvas")
        if canvas.count() != 1:
            browser.close()
            print("render source must contain exactly one #longform-canvas", file=sys.stderr)
            return 1
        bbox = canvas.bounding_box()
        if not fonts_ready:
            browser.close()
            print("bundled production fonts did not load; refusing system-font fallback", file=sys.stderr)
            return 1
        if not bbox or abs(bbox["width"] - CANVAS_WIDTH) > 0.5:
            browser.close()
            actual = "missing" if not bbox else f"{bbox['width']:.2f}"
            print(f"#longform-canvas must be {CANVAS_WIDTH}px wide; got {actual}px", file=sys.stderr)
            return 1
        canvas.screenshot(path=str(args.output), scale="css")
        proof = {
            "engine": "playwright-chromium",
            "fonts_ready": True,
            "fonts": ["Yinxi Noto Serif SC", "Yinxi Noto Sans SC"],
            "canvas_width": round(bbox["width"], 2),
            "png_direct_from_layout_engine": True,
            "output": str(args.output.name),
        }
        args.render_proof.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        browser.close()
    print(f"rendered: {args.output}")
    print(f"proof: {args.render_proof}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
