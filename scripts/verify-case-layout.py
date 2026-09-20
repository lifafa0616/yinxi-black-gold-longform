#!/usr/bin/env python3
"""Check a browser-produced black-gold layout manifest against its final PNG.

The manifest still describes semantic structure. Unlike the old checker, this
script also opens the final PNG and samples its real pixels. It is a stop-loss
check, not a replacement for browser-DOM measurement or human visual review.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROLE_MINIMUMS = {"title": 110, "module-title": 40, "body": 36, "price": 36, "action": 36, "meta": 26}
CANVAS_WIDTH = 1080
CANVAS_HEX = "#10100F"
CANVAS_RGB = (16, 16, 15)
PIXEL_TOLERANCE = 2
HERO_TOP_GAP_MIN = 64
HERO_TOP_GAP_MAX = 144
HERO_VISIBLE_HEIGHT_MIN = 560
WRAP_ROLES = {"title", "module-title", "body"}
INDEPENDENT_DATA_ROLES = {"data", "metric"}


def fail(issues, message):
    issues.append(message)


def rect(value, label, issues):
    if not isinstance(value, list) or len(value) != 4 or any(not isinstance(v, (int, float)) for v in value):
        fail(issues, f"{label} must be [x, y, width, height]")
        return None
    x, y, width, height = value
    if width < 0 or height < 0:
        fail(issues, f"{label} width and height must be non-negative")
        return None
    return x, y, width, height


def point(value, label, issues):
    if not isinstance(value, list) or len(value) != 2 or any(not isinstance(v, int) for v in value):
        fail(issues, f"{label} must be integer [x, y]")
        return None
    return value[0], value[1]


def inside(child, parent, padding):
    x, y, width, height = child
    px, py, pwidth, pheight = parent
    return x >= px + padding and y >= py + padding and x + width <= px + pwidth - padding and y + height <= py + pheight - padding


def semantic_char_count(line):
    return sum(character.isalnum() for character in line)


def validate_rendered_lines(block, label, issues):
    role = block.get("role") if isinstance(block, dict) else None
    independent_data = block.get("independent_data") is True if isinstance(block, dict) else False
    lines = block.get("rendered_lines") if isinstance(block, dict) else None
    if independent_data:
        if role not in INDEPENDENT_DATA_ROLES:
            fail(issues, f"{label}.independent_data is only allowed for data or metric roles")
        elif not isinstance(lines, list) or len(lines) != 1 or not isinstance(lines[0], str) or not lines[0].strip():
            fail(issues, f"{label}.independent_data requires exactly one non-empty rendered line")
        return
    if role not in WRAP_ROLES:
        return
    if not isinstance(lines, list) or not lines or any(not isinstance(line, str) or not line.strip() for line in lines):
        fail(issues, f"{label} {role} requires non-empty browser-rendered rendered_lines")
        return
    if len(lines) > 1:
        for line_index, line in enumerate(lines):
            if semantic_char_count(line) < 2:
                fail(issues, f"{label}.rendered_lines[{line_index}] is a forbidden single-character orphan line")


def validate_render_proof(path, issues):
    try:
        proof = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(issues, f"cannot read renderer-produced proof: {error}")
        return
    if proof.get("engine") != "playwright-chromium":
        fail(issues, "render proof engine must be playwright-chromium")
    if proof.get("fonts_ready") is not True:
        fail(issues, "render proof must confirm bundled fonts_ready")
    if proof.get("png_direct_from_layout_engine") is not True:
        fail(issues, "render proof must confirm direct PNG export from the layout engine")
    width = proof.get("canvas_width")
    if not isinstance(width, (int, float)) or abs(width - CANVAS_WIDTH) > 0.5:
        fail(issues, f"render proof canvas_width must be {CANVAS_WIDTH}px")


def validate_pixel(rgb, location, label, issues):
    x, y = location
    actual = rgb.getpixel((x, y))
    if any(abs(actual[channel] - CANVAS_RGB[channel]) > PIXEL_TOLERANCE for channel in range(3)):
        fail(issues, f"{label} is {actual}, not master canvas {CANVAS_HEX}")


def validate_png(path, manifest, issues):
    try:
        from PIL import Image
    except ModuleNotFoundError:
        fail(issues, "Pillow is required for PNG inspection; install requirements.txt")
        return
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                fail(issues, "final artwork must be a PNG")
                return
            if image.width != CANVAS_WIDTH:
                fail(issues, f"final PNG width must be {CANVAS_WIDTH}px; got {image.width}px")
            rgb = image.convert("RGB")
            samples = manifest.get("background_samples")
            if not isinstance(samples, list) or not samples:
                fail(issues, "background_samples must declare clear master-canvas sample points")
            else:
                for index, sample in enumerate(samples):
                    location = point(sample.get("point") if isinstance(sample, dict) else None, f"background_samples[{index}].point", issues)
                    if not location:
                        continue
                    x, y = location
                    if x < 0 or y < 0 or x >= image.width or y >= image.height:
                        fail(issues, f"background_samples[{index}] lies outside final PNG")
                    else:
                        validate_pixel(rgb, location, f"background_samples[{index}]", issues)
            seams = manifest.get("seams")
            if not isinstance(seams, list) or not seams:
                fail(issues, "seams must contain real final-PNG sample points at each reading-zone boundary")
            else:
                for index, seam in enumerate(seams):
                    if not isinstance(seam, dict):
                        fail(issues, f"seams[{index}] must be an object")
                        continue
                    samples = seam.get("sample_points")
                    if not isinstance(samples, list) or not samples:
                        fail(issues, f"seams[{index}].sample_points must contain at least one clear-canvas point")
                        continue
                    for sample_index, raw_point in enumerate(samples):
                        location = point(raw_point, f"seams[{index}].sample_points[{sample_index}]", issues)
                        if not location:
                            continue
                        x, y = location
                        if x < 0 or y < 0 or x >= image.width or y >= image.height:
                            fail(issues, f"seams[{index}].sample_points[{sample_index}] lies outside final PNG")
                        else:
                            validate_pixel(rgb, location, f"seams[{index}].sample_points[{sample_index}]", issues)
    except OSError as error:
        fail(issues, f"cannot open final PNG: {error}")


def collect_cta_members(manifest, issues):
    groups = {}
    for index, group in enumerate(manifest.get("cta_groups", [])):
        if not isinstance(group, dict) or not isinstance(group.get("id"), str) or not group["id"]:
            fail(issues, f"cta_groups[{index}] must have a non-empty string id")
            continue
        groups[group["id"]] = {"price": None, "qr": None}
    for container_index, container in enumerate(manifest.get("containers", [])):
        if not isinstance(container, dict):
            continue
        for child_index, child in enumerate(container.get("children", [])):
            if not isinstance(child, dict) or child.get("role") not in {"price", "qr"}:
                continue
            group_id = child.get("cta_group")
            if not isinstance(group_id, str) or not group_id:
                fail(issues, f"containers[{container_index}].children[{child_index}] {child.get('role')} must declare cta_group")
                continue
            if group_id not in groups:
                fail(issues, f"CTA member references undeclared cta_group {group_id!r}")
                continue
            member_box = rect(child.get("bbox"), f"containers[{container_index}].children[{child_index}].bbox", issues)
            role = child["role"]
            if member_box:
                if groups[group_id][role] is not None:
                    fail(issues, f"cta_group {group_id!r} contains more than one {role}")
                groups[group_id][role] = member_box
    return groups


def validate(manifest, png_path, proof_path):
    issues = []
    canvas = manifest.get("canvas", {})
    if canvas.get("width") != CANVAS_WIDTH:
        fail(issues, f"canvas.width must be {CANVAS_WIDTH}")
    if canvas.get("color") != CANVAS_HEX:
        fail(issues, f"canvas.color must be {CANVAS_HEX}")
    validate_render_proof(proof_path, issues)
    validate_png(png_path, manifest, issues)

    hero = manifest.get("hero")
    if not isinstance(hero, dict):
        fail(issues, "hero must record the V1 visible geometry")
    else:
        anchor, copy_height = hero.get("copy_anchor_bottom"), hero.get("copy_group_height")
        visible = rect(hero.get("visible_bbox"), "hero.visible_bbox", issues)
        if not isinstance(anchor, (int, float)) or not isinstance(copy_height, (int, float)) or copy_height < 0 or not visible:
            fail(issues, "hero requires copy_anchor_bottom, non-negative copy_group_height and visible_bbox")
        else:
            top_gap = visible[1] - anchor
            if top_gap < HERO_TOP_GAP_MIN or top_gap > HERO_TOP_GAP_MAX:
                fail(issues, f"hero visible top gap must be {HERO_TOP_GAP_MIN}–{HERO_TOP_GAP_MAX}px after copy_anchor_bottom")
            required_height = max(HERO_VISIBLE_HEIGHT_MIN, 1.2 * copy_height)
            if visible[3] < required_height:
                fail(issues, f"hero visible height must be at least {required_height:g}px")

    text_blocks = manifest.get("text_blocks")
    if not isinstance(text_blocks, list):
        fail(issues, "text_blocks must record browser-rendered lines for non-container reading text")
    else:
        for index, block in enumerate(text_blocks):
            if not isinstance(block, dict):
                fail(issues, f"text_blocks[{index}] must be an object")
                continue
            role, size = block.get("role"), block.get("font_size")
            if role in ROLE_MINIMUMS and (not isinstance(size, (int, float)) or size < ROLE_MINIMUMS[role]):
                fail(issues, f"text_blocks[{index}] {role} font_size must be at least {ROLE_MINIMUMS[role]}")
            validate_rendered_lines(block, f"text_blocks[{index}]", issues)

    zones = manifest.get("reading_zones")
    if not isinstance(zones, list) or not zones:
        fail(issues, "reading_zones must contain the ordered Lxx sequence")
    else:
        contracts = []
        for index, zone in enumerate(zones):
            contract = zone.get("contract") if isinstance(zone, dict) else None
            if not isinstance(contract, str) or not re.fullmatch(r"L(?:0[1-9]|1[0-7])", contract):
                fail(issues, f"reading_zones[{index}].contract must be L01–L17")
            else:
                contracts.append(contract)
        for previous, current in zip(contracts, contracts[1:]):
            if previous == current:
                fail(issues, f"adjacent reading zones reuse {current}")
        for contract, count in Counter(contracts).items():
            if count > 2:
                fail(issues, f"{contract} appears {count} times; maximum is 2")

    for index, frame in enumerate(manifest.get("frames", [])):
        frame_rect = rect(frame.get("rect") if isinstance(frame, dict) else None, f"frames[{index}].rect", issues)
        if frame_rect and frame_rect[2] != CANVAS_WIDTH:
            fail(issues, f"frames[{index}].rect width must be {CANVAS_WIDTH}")

    for index, container in enumerate(manifest.get("containers", [])):
        if not isinstance(container, dict):
            fail(issues, f"containers[{index}] must be an object")
            continue
        parent, padding = rect(container.get("rect"), f"containers[{index}].rect", issues), container.get("padding")
        if not isinstance(padding, (int, float)) or padding < 0:
            fail(issues, f"containers[{index}].padding must be a non-negative number")
            continue
        if not parent:
            continue
        for child_index, child in enumerate(container.get("children", [])):
            if not isinstance(child, dict):
                fail(issues, f"containers[{index}].children[{child_index}] must be an object")
                continue
            child_rect = rect(child.get("bbox"), f"containers[{index}].children[{child_index}].bbox", issues)
            if child_rect and not inside(child_rect, parent, padding):
                fail(issues, f"containers[{index}].children[{child_index}] exceeds its parent padding box")
            role, size = child.get("role"), child.get("font_size")
            if role in ROLE_MINIMUMS and (not isinstance(size, (int, float)) or size < ROLE_MINIMUMS[role]):
                fail(issues, f"containers[{index}].children[{child_index}] {role} font_size must be at least {ROLE_MINIMUMS[role]}")
            validate_rendered_lines(child, f"containers[{index}].children[{child_index}]", issues)

    for group_id, members in collect_cta_members(manifest, issues).items():
        price, qr = members["price"], members["qr"]
        if (price is None) != (qr is None):
            fail(issues, f"cta_group {group_id!r} must contain both price and qr when either is present")
        elif price and qr and abs((price[1] + price[3] / 2) - (qr[1] + qr[3] / 2)) > 96:
            fail(issues, f"cta_group {group_id!r} QR must align with its price data group within 96px")

    protected = []
    for index, box in enumerate(manifest.get("protected_boxes", [])):
        value = rect(box.get("bbox") if isinstance(box, dict) else None, f"protected_boxes[{index}].bbox", issues)
        if value:
            protected.append(value)
    for index, chapter in enumerate(manifest.get("chapters", [])):
        if not isinstance(chapter, dict):
            fail(issues, f"chapters[{index}] must be an object")
            continue
        box, title_top = rect(chapter.get("bbox"), f"chapters[{index}].bbox", issues), chapter.get("title_top")
        if not box or not isinstance(title_top, (int, float)):
            fail(issues, f"chapters[{index}] requires bbox and numeric title_top")
            continue
        if abs((CANVAS_WIDTH - (box[0] + box[2])) - 92) > 8:
            fail(issues, f"chapters[{index}] right gap must be 92px ±8px")
        if abs(box[1] - title_top) > 8:
            fail(issues, f"chapters[{index}] top must align to title_top within ±8px")
        for protected_index, protected_box in enumerate(protected):
            if box[0] < protected_box[0] + protected_box[2] and box[0] + box[2] > protected_box[0] and box[1] < protected_box[1] + protected_box[3] and box[1] + box[3] > protected_box[1]:
                fail(issues, f"chapters[{index}] overlaps protected_boxes[{protected_index}]")

    for index, portrait in enumerate(manifest.get("portraits", [])):
        if not isinstance(portrait, dict):
            fail(issues, f"portraits[{index}] must be an object")
            continue
        mode, intro_top, region = portrait.get("portrait_mode"), portrait.get("intro_text_top"), portrait.get("related_text_region")
        if mode not in {"transparent", "source-crop"}:
            fail(issues, f"portraits[{index}].portrait_mode must be transparent or source-crop")
            continue
        if not isinstance(intro_top, (int, float)) or not isinstance(region, dict):
            fail(issues, f"portraits[{index}] requires intro_text_top and related_text_region")
            continue
        top, bottom = region.get("top"), region.get("bottom")
        if not isinstance(top, (int, float)) or not isinstance(bottom, (int, float)) or bottom < top:
            fail(issues, f"portraits[{index}].related_text_region requires ordered numeric top/bottom")
            continue
        if mode == "transparent":
            anchor, subject, label = portrait.get("visible_head_top"), rect(portrait.get("visible_bbox"), f"portraits[{index}].visible_bbox", issues), "visible_head_top"
        else:
            anchor, subject, label = portrait.get("image_rect_top"), rect(portrait.get("image_rect"), f"portraits[{index}].image_rect", issues), "image_rect_top"
        if not isinstance(anchor, (int, float)) or not subject:
            fail(issues, f"portraits[{index}] {mode} requires {label} and its matching bbox")
            continue
        if abs(anchor - intro_top) > 8:
            fail(issues, f"portraits[{index}] {label} must align to intro_text_top within ±8px")
        if subject[1] < top or subject[1] + subject[3] > bottom:
            fail(issues, f"portraits[{index}] {mode} bbox exceeds its related text region")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Verify final PNG and its browser layout manifest.")
    parser.add_argument("manifest", type=Path, help="layout-manifest.json exported after browser rendering")
    parser.add_argument("--png", required=True, type=Path, help="final PNG from render_longform.py")
    parser.add_argument("--render-proof", required=True, type=Path, help="renderer-produced render-proof.json")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read manifest: {error}", file=sys.stderr)
        return 2
    issues = validate(manifest, args.png, args.render_proof)
    if issues:
        for issue in issues:
            print(f"invalid: {issue}", file=sys.stderr)
        return 1
    print("verified: browser proof, final PNG dimensions, master-canvas samples and layout constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
