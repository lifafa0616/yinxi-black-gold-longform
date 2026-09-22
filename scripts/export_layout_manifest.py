#!/usr/bin/env python3
"""Export measured layout data from a portable poster.html through Chromium.

The source document supplies semantic data attributes; this script supplies the
numbers.  It deliberately refuses to accept a hand-written manifest so checks
such as card overflow, orphan lines and hero placement are based on the same
browser layout tree that produces final.png.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from package_poster_html import validate_portable_document


CANVAS_WIDTH = 1080
CANVAS_COLOR = "#10100F"


EXPORT_SCRIPT = r"""() => {
  const number = (value) => Math.round(value * 100) / 100;
  const box = (element) => {
    const rect = element.getBoundingClientRect();
    return [number(rect.x + window.scrollX), number(rect.y + window.scrollY),
      number(rect.width), number(rect.height)];
  };
  const cssSize = (element) => number(parseFloat(getComputedStyle(element).fontSize));
  const textLines = (element) => {
    const rows = new Map();
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      for (let index = 0; index < node.data.length; index += 1) {
        const character = node.data[index];
        const range = document.createRange();
        range.setStart(node, index);
        range.setEnd(node, index + 1);
        const rect = Array.from(range.getClientRects()).find((candidate) => candidate.width || candidate.height);
        if (!rect) continue;
        const key = Math.round((rect.y + window.scrollY) * 2) / 2;
        rows.set(key, (rows.get(key) || "") + character);
      }
    }
    return Array.from(rows.entries()).sort((a, b) => a[0] - b[0])
      .map(([, line]) => line.replace(/\s+/g, " ").trim()).filter(Boolean);
  };
  const roleBlock = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return {
      id: element.dataset.layoutId || null,
      role: element.dataset.layoutRole,
      bbox: box(element),
      font_size: cssSize(element),
      rendered_lines: textLines(element),
      independent_data: element.dataset.independentData === "true",
      cta_group: element.dataset.ctaGroup || null,
      overflow_x: element.scrollWidth > element.clientWidth + 0.5,
      overflow_y: element.scrollHeight > element.clientHeight + 0.5,
      is_visible: style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0,
    };
  };
  const canvas = document.querySelector("#longform-canvas");
  if (!canvas) throw new Error("missing #longform-canvas");
  const roleElements = Array.from(document.querySelectorAll("[data-layout-role]"));
  const containers = Array.from(document.querySelectorAll("[data-layout-container]")).map((container) => {
    const style = getComputedStyle(container);
    return {
      id: container.dataset.layoutContainer,
      rect: box(container),
      padding: number(parseFloat(style.paddingLeft)),
      children: roleElements.filter((element) => element.closest("[data-layout-container]") === container)
        .map(roleBlock),
    };
  });
  const topLevelText = roleElements.filter((element) => !element.closest("[data-layout-container]")).map(roleBlock);
  const zones = Array.from(document.querySelectorAll("[data-reading-zone]")).map((zone) => ({
    id: zone.dataset.readingZone,
    contract: zone.dataset.contract || null,
    bbox: box(zone),
  }));
  const samplePoint = (element) => {
    const rect = element.getBoundingClientRect();
    return [Math.round(rect.left + window.scrollX + rect.width / 2), Math.round(rect.top + window.scrollY + rect.height / 2)];
  };
  const background_samples = Array.from(document.querySelectorAll("[data-background-sample]")).map((element) => ({point: samplePoint(element)}));
  const seams = Array.from(document.querySelectorAll("[data-seam-sample]")).map((element, index) => ({
    id: element.dataset.seamSample || `seam-${index + 1}`,
    sample_points: [samplePoint(element)],
  }));
  const heroes = Array.from(document.querySelectorAll("[data-hero]"));
  const copyAnchors = Array.from(document.querySelectorAll("[data-hero-copy]"));
  let hero = null;
  if (heroes.length === 1 && copyAnchors.length === 1) {
    const copyBox = box(copyAnchors[0]);
    hero = {
      strategy: heroes[0].dataset.hero,
      copy_anchor_bottom: number(copyBox[1] + copyBox[3]),
      copy_group_height: copyBox[3],
      visible_bbox: box(heroes[0]),
      measured_from_dom: true,
    };
  }
  const ctaIds = new Set(roleElements.map((element) => element.dataset.ctaGroup).filter(Boolean));
  return {
    canvas: {width: number(canvas.getBoundingClientRect().width), color: canvas.dataset.canvasColor || null},
    hero,
    text_blocks: topLevelText,
    containers,
    reading_zones: zones,
    cta_groups: Array.from(ctaIds).map((id) => ({id})),
    background_samples,
    seams,
    measured_elements: roleElements.map(roleBlock),
  };
}"""


def main():
    parser = argparse.ArgumentParser(description="Export a real Chromium layout manifest from portable poster.html.")
    parser.add_argument("--input", required=True, type=Path, help="self-contained poster.html")
    parser.add_argument("--output", required=True, type=Path, help="generated layout-manifest.json")
    args = parser.parse_args()
    try:
        document = args.input.read_text(encoding="utf-8")
        validate_portable_document(document)
    except (OSError, ValueError) as error:
        parser.error(f"input must be a portable poster.html made by package_poster_html.py: {error}")
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print("Playwright is not installed. Run: python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": 1600}, device_scale_factor=1)
        page.goto(args.input.resolve().as_uri(), wait_until="networkidle")
        fonts_ready = page.evaluate("""async () => {
            await document.fonts.ready;
            return document.fonts.check('700 32px "Yinxi Noto Serif SC"') &&
                document.fonts.check('500 32px "Yinxi Noto Sans SC"');
        }""")
        if not fonts_ready:
            browser.close()
            print("bundled production fonts did not load; refusing to export layout from fallback fonts", file=sys.stderr)
            return 1
        try:
            manifest = page.evaluate(EXPORT_SCRIPT)
        except Exception as error:
            browser.close()
            print(f"could not measure poster layout: {error}", file=sys.stderr)
            return 1
        browser.close()

    manifest.update({
        "producer": "playwright-dom",
        "layout_engine": "playwright-chromium",
        "poster_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
        "contract": "yinxi-layout-manifest-v2",
    })
    if manifest["canvas"]["width"] != CANVAS_WIDTH or manifest["canvas"]["color"] != CANVAS_COLOR:
        print("poster.html must declare #longform-canvas data-canvas-color=\"#10100F\" at 1080px", file=sys.stderr)
        return 1
    if manifest["hero"] is None:
        print("poster.html must contain exactly one [data-hero] and one [data-hero-copy]", file=sys.stderr)
        return 1
    if not manifest["background_samples"] or not manifest["seams"]:
        print("poster.html must include [data-background-sample] and [data-seam-sample] markers on clear canvas", file=sys.stderr)
        return 1
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"measured: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
