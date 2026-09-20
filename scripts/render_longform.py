#!/usr/bin/env python3
"""Render the formal portable poster.html through Playwright Chromium.

This script is deliberately a renderer, not an editor. It renders the exact
self-contained delivery produced by package_poster_html.py, then emits the
published PNG and machine-produced proof from the same browser layout tree.
"""

import argparse
from io import BytesIO
import json
import sys
from pathlib import Path

from package_poster_html import validate_portable_document


CANVAS_WIDTH = 1080
MAX_DIRECT_CAPTURE_HEIGHT = 16000
SEGMENT_HEIGHT = 8000


def save_browser_raster(page, canvas, bbox, output_path):
    """Save one browser-rendered canvas, segmenting only when Chromium needs it.

    The segmented route never revisits layout: each strip is captured from the
    same DOM and then copied pixel-for-pixel into one PNG.
    """
    if bbox["height"] <= MAX_DIRECT_CAPTURE_HEIGHT:
        canvas.screenshot(path=str(output_path), scale="css")
        return "direct", 1
    try:
        from PIL import Image
    except ModuleNotFoundError as error:
        raise RuntimeError("Pillow is required for browser-raster pixel stitching") from error
    total_height = round(bbox["height"])
    if abs(bbox["x"]) > 0.5:
        raise RuntimeError("segmented capture requires #longform-canvas to start at x=0")
    stitched = Image.new("RGBA", (CANVAS_WIDTH, total_height))
    segment_count = 0
    for offset in range(0, total_height, SEGMENT_HEIGHT):
        height = min(SEGMENT_HEIGHT, total_height - offset)
        page.set_viewport_size({"width": CANVAS_WIDTH, "height": height})
        expected_scroll = round(bbox["y"] + offset)
        actual_scroll = page.evaluate("""(top) => {
            window.scrollTo(0, top);
            return window.scrollY;
        }""", expected_scroll)
        if abs(actual_scroll - expected_scroll) > 1:
            raise RuntimeError("browser could not reach a required segmented-capture scroll position")
        png = page.screenshot(scale="css")
        with Image.open(BytesIO(png)) as segment:
            stitched.paste(segment.convert("RGBA"), (0, offset))
        segment_count += 1
    stitched.save(output_path, format="PNG")
    return "browser-segmented-pixel-stitch", segment_count


def main():
    parser = argparse.ArgumentParser(description="Render a longform HTML source with the bundled fonts.")
    parser.add_argument("--input", required=True, type=Path, help="formal self-contained case poster.html containing #longform-canvas")
    parser.add_argument("--output", required=True, type=Path, help="final 1080px PNG path")
    parser.add_argument("--render-proof", required=True, type=Path, help="machine-produced render proof JSON path")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input HTML does not exist: {args.input}")
    try:
        portable_proof = validate_portable_document(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(f"input must be a portable poster.html made by package_poster_html.py: {error}")

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print("Playwright is not installed. Run: python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.render_proof.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": 1600}, device_scale_factor=1)
        page.goto(args.input.resolve().as_uri(), wait_until="networkidle")
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
        broken_images = page.evaluate("""() => Array.from(document.images)
            .filter((image) => !image.complete || image.naturalWidth === 0)
            .map((image) => image.getAttribute('src') || '(missing src)')""")
        if broken_images:
            browser.close()
            print("embedded poster contains broken image assets", file=sys.stderr)
            return 1
        if not bbox or abs(bbox["width"] - CANVAS_WIDTH) > 0.5:
            browser.close()
            actual = "missing" if not bbox else f"{bbox['width']:.2f}"
            print(f"#longform-canvas must be {CANVAS_WIDTH}px wide; got {actual}px", file=sys.stderr)
            return 1
        try:
            capture_mode, segment_count = save_browser_raster(page, canvas, bbox, args.output)
        except RuntimeError as error:
            browser.close()
            print(str(error), file=sys.stderr)
            return 1
        proof = {
            "engine": "playwright-chromium",
            "fonts_ready": True,
            "fonts": ["Yinxi Noto Serif SC", "Yinxi Noto Sans SC"],
            "canvas_width": round(bbox["width"], 2),
            "browser_raster_from_layout_engine": True,
            "png_direct_from_layout_engine": capture_mode == "direct",
            "portable_html": portable_proof["portable_html"],
            "embedded_font_count": portable_proof["embedded_font_count"],
            "embedded_asset_reference_count": portable_proof["embedded_asset_reference_count"],
            "images_ready": True,
            "capture_mode": capture_mode,
            "segment_count": segment_count,
            "pixel_stitched": capture_mode == "browser-segmented-pixel-stitch",
            "output": str(args.output.name),
        }
        args.render_proof.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        browser.close()
    print(f"rendered: {args.output}")
    print(f"proof: {args.render_proof}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
