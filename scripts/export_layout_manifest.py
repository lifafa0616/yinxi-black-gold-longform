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
      font_weight: number(parseFloat(style.fontWeight)),
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
    is_hero_cover: zone.hasAttribute("data-hero-cover"),
    bbox: box(zone),
  }));
  const chapters = Array.from(document.querySelectorAll("[data-layout-chapter]")).map((chapter) => {
    const id = chapter.dataset.layoutChapter;
    const zone = chapter.closest("[data-reading-zone]");
    const labels = zone ? Array.from(zone.querySelectorAll("[data-chapter-label]"))
      .filter((label) => label.dataset.chapterLabel === id) : [];
    if (labels.length !== 1) throw new Error("every [data-layout-chapter] requires one same-ID [data-chapter-label] in its reading zone");
    const internalIndexes = zone ? Array.from(zone.querySelectorAll("[data-internal-index]")) : [];
    return {
      id,
      zone_id: zone ? zone.dataset.readingZone : null,
      display_number: chapter.textContent.replace(/\s+/g, "").trim(),
      bbox: box(chapter),
      font_size: cssSize(chapter),
      label_top: box(labels[0])[1],
      internal_index_font_sizes: internalIndexes.map(cssSize),
    };
  });
  const major_modules = Array.from(document.querySelectorAll("[data-major-module]")).map((module) => {
    const zone = module.closest("[data-reading-zone]");
    return {
      id: module.dataset.majorModule,
      zone_id: zone ? zone.dataset.readingZone : null,
      is_hero_cover: Boolean(zone && zone.hasAttribute("data-hero-cover")),
      chapter_ids: Array.from(module.querySelectorAll("[data-layout-chapter]")).map((chapter) => chapter.dataset.layoutChapter),
    };
  });
  const text_axes = Array.from(new Set(Array.from(document.querySelectorAll("[data-fullwidth-text-axis]"))
    .map((element) => element.dataset.fullwidthTextAxis))).map((id) => {
      const members = Array.from(document.querySelectorAll("[data-fullwidth-text-axis]")).filter(
        (element) => element.dataset.fullwidthTextAxis === id,
      );
      const zones = new Set(members.map((element) => {
        const zone = element.closest("[data-reading-zone]");
        return zone ? zone.dataset.readingZone : null;
      }));
      return {
        id,
        zone_id: zones.size === 1 ? Array.from(zones)[0] : null,
        members: members.map((element) => ({
          role: element.dataset.layoutRole || null,
          bbox: box(element),
        })),
      };
    });
  const gold_keywords = Array.from(document.querySelectorAll("[data-gold-keyword]")).map((element) => ({
    scope: element.dataset.goldKeyword,
    text: element.textContent.replace(/\s+/g, " ").trim(),
  }));
  const protected_boxes = Array.from(document.querySelectorAll("[data-protected-text]")).map((element) => ({
    id: element.dataset.protectedText || null,
    bbox: box(element),
  }));
  const one = (group, selector, label) => {
    const matches = group.querySelectorAll(selector);
    if (matches.length !== 1) throw new Error(`${label} requires exactly one ${selector}`);
    return matches[0];
  };
  const portraits = Array.from(document.querySelectorAll("[data-portrait]")).map((group) => {
    const mode = group.dataset.portrait;
    const intro = one(group, "[data-portrait-intro]", "portrait");
    const region = one(group, "[data-portrait-related-text-region]", "portrait");
    const subject = one(group, "[data-portrait-subject]", "portrait");
    const regionBox = box(region);
    const subjectBox = box(subject);
    const portrait = {
      portrait_mode: mode,
      intro_text_top: box(intro)[1],
      related_text_region: {top: regionBox[1], bottom: number(regionBox[1] + regionBox[3])},
    };
    if (mode === "transparent") {
      portrait.visible_head_top = subjectBox[1];
      portrait.visible_bbox = subjectBox;
    } else {
      portrait.image_rect_top = subjectBox[1];
      portrait.image_rect = subjectBox;
    }
    return portrait;
  });
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
  const heroSurfaces = Array.from(document.querySelectorAll("[data-hero-surface]"));
  const copyAnchors = Array.from(document.querySelectorAll("[data-hero-copy]"));
  let hero = null;
  if (heroes.length === 1 && copyAnchors.length === 1) {
    if (heroSurfaces.length !== 1 || !heroSurfaces[0].contains(heroes[0])) {
      throw new Error("[data-hero] requires one containing [data-hero-surface]");
    }
    const copyBox = box(copyAnchors[0]);
    hero = {
      strategy: heroes[0].dataset.hero,
      copy_anchor_bottom: number(copyBox[1] + copyBox[3]),
      copy_group_height: copyBox[3],
      visible_bbox: box(heroes[0]),
      surface_bbox: box(heroSurfaces[0]),
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
    major_modules,
    text_axes,
    gold_keywords,
    chapters,
    protected_boxes,
    portraits,
    cta_groups: Array.from(ctaIds).map((id) => ({id})),
    background_samples,
    seams,
    measured_elements: roleElements.map(roleBlock),
  };
}"""


def poster_sha256(input_path: Path) -> str:
    """Hash the portable file's stored bytes, without newline translation."""
    return hashlib.sha256(input_path.read_bytes()).hexdigest()


def build_manifest(input_path: Path) -> dict:
    """Measure one portable poster through Chromium and return its manifest.

    This is intentionally shared by the exporter and verifier: verification
    remeasures the supplied poster instead of trusting manifest provenance
    strings or a caller-provided hash.
    """
    document_bytes = input_path.read_bytes()
    document = document_bytes.decode("utf-8")
    validate_portable_document(document)
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as error:
        raise RuntimeError("Playwright is not installed. Run: python3 -m pip install -r requirements.txt") from error

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": 1600}, device_scale_factor=1)
        page.goto(input_path.resolve().as_uri(), wait_until="networkidle")
        fonts_ready = page.evaluate("""async () => {
            await Promise.all([
                document.fonts.load('700 32px "Yinxi Noto Serif SC"'),
                document.fonts.load('400 32px "Yinxi Noto Sans SC"'),
                document.fonts.load('500 32px "Yinxi Noto Sans SC"'),
            ]);
            await document.fonts.ready;
            return document.fonts.check('700 32px "Yinxi Noto Serif SC"') &&
                document.fonts.check('400 32px "Yinxi Noto Sans SC"') &&
                document.fonts.check('500 32px "Yinxi Noto Sans SC"');
        }""")
        if not fonts_ready:
            browser.close()
            raise RuntimeError("bundled production fonts did not load; refusing to export layout from fallback fonts")
        try:
            manifest = page.evaluate(EXPORT_SCRIPT)
        except Exception as error:
            raise RuntimeError(f"could not measure poster layout: {error}") from error
        finally:
            browser.close()

    manifest.update({
        "producer": "playwright-dom",
        "layout_engine": "playwright-chromium",
        "poster_sha256": poster_sha256(input_path),
        "contract": "yinxi-layout-manifest-v3",
    })
    if manifest["canvas"]["width"] != CANVAS_WIDTH or manifest["canvas"]["color"] != CANVAS_COLOR:
        raise RuntimeError("poster.html must declare #longform-canvas data-canvas-color=\"#10100F\" at 1080px")
    if manifest["hero"] is None:
        raise RuntimeError("poster.html must contain exactly one [data-hero] and one [data-hero-copy]")
    if not manifest["background_samples"] or not manifest["seams"]:
        raise RuntimeError("poster.html must include [data-background-sample] and [data-seam-sample] markers on clear canvas")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Export a real Chromium layout manifest from portable poster.html.")
    parser.add_argument("--input", required=True, type=Path, help="self-contained poster.html")
    parser.add_argument("--output", required=True, type=Path, help="generated layout-manifest.json")
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.input)
    except (OSError, UnicodeDecodeError, ValueError, RuntimeError) as error:
        parser.error(f"input must be a portable poster.html made by package_poster_html.py: {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"measured: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
