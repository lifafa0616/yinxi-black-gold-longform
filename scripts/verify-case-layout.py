#!/usr/bin/env python3
"""Verify objective black-gold case geometry from a renderer-produced manifest.

This checker deliberately does not score material, semantic relevance, or human
aesthetic approval. Those remain visual-review responsibilities.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROLE_MINIMUMS = {
    "title": 110,
    "module-title": 40,
    "body": 36,
    "price": 36,
    "action": 36,
    "meta": 26,
}
CANVAS_WIDTH = 1080
HERO_TOP_GAP_MIN = 64
HERO_TOP_GAP_MAX = 144
HERO_VISIBLE_HEIGHT_MIN = 560
WRAP_ROLES = {"title", "module-title", "body"}


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


def inside(child, parent, padding):
    x, y, width, height = child
    px, py, pwidth, pheight = parent
    return x >= px + padding and y >= py + padding and x + width <= px + pwidth - padding and y + height <= py + pheight - padding


def semantic_char_count(line):
    """Count visible CJK/Latin/digit characters, ignoring whitespace and punctuation."""
    return sum(character.isalnum() for character in line)


def validate_rendered_lines(block, label, issues):
    role = block.get("role") if isinstance(block, dict) else None
    if role not in WRAP_ROLES:
        return
    lines = block.get("rendered_lines")
    if not isinstance(lines, list) or not lines or any(not isinstance(line, str) or not line.strip() for line in lines):
        fail(issues, f"{label} {role} requires non-empty browser-rendered rendered_lines")
        return
    if len(lines) > 1:
        for line_index, line in enumerate(lines):
            if semantic_char_count(line) < 2:
                fail(issues, f"{label}.rendered_lines[{line_index}] is a forbidden single-character orphan line")


def validate(manifest):
    issues = []
    canvas = manifest.get("canvas", {})
    if canvas.get("width") != CANVAS_WIDTH:
        fail(issues, f"canvas.width must be {CANVAS_WIDTH}")
    if canvas.get("color") != "#10100F":
        fail(issues, "canvas.color must be #10100F")

    render_proof = manifest.get("render_proof")
    if not isinstance(render_proof, dict):
        fail(issues, "render_proof must record the final browser render path")
    else:
        if render_proof.get("engine") != "browser":
            fail(issues, "render_proof.engine must be browser")
        if render_proof.get("fonts_ready") is not True:
            fail(issues, "render_proof.fonts_ready must be true before geometry export")
        if render_proof.get("png_direct_from_layout_engine") is not True:
            fail(issues, "final PNG must be directly exported from the layout browser engine")

    hero = manifest.get("hero")
    if not isinstance(hero, dict):
        fail(issues, "hero must record the V1 visible geometry")
    else:
        anchor = hero.get("copy_anchor_bottom")
        copy_height = hero.get("copy_group_height")
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
            role = block.get("role")
            size = block.get("font_size")
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
        parent = rect(container.get("rect"), f"containers[{index}].rect", issues)
        padding = container.get("padding")
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
            role = child.get("role")
            size = child.get("font_size")
            if role in ROLE_MINIMUMS and (not isinstance(size, (int, float)) or size < ROLE_MINIMUMS[role]):
                fail(issues, f"containers[{index}].children[{child_index}] {role} font_size must be at least {ROLE_MINIMUMS[role]}")
            validate_rendered_lines(child, f"containers[{index}].children[{child_index}]", issues)
        price_boxes = [
            rect(child.get("bbox"), f"containers[{index}].children[{child_index}].bbox", issues)
            for child_index, child in enumerate(container.get("children", []))
            if isinstance(child, dict) and child.get("role") == "price"
        ]
        qr_boxes = [
            rect(child.get("bbox"), f"containers[{index}].children[{child_index}].bbox", issues)
            for child_index, child in enumerate(container.get("children", []))
            if isinstance(child, dict) and child.get("role") == "qr"
        ]
        if price_boxes and qr_boxes:
            price = price_boxes[0]
            qr = qr_boxes[0]
            if price and qr:
                price_center = price[1] + price[3] / 2
                qr_center = qr[1] + qr[3] / 2
                if abs(price_center - qr_center) > 96:
                    fail(issues, f"containers[{index}] QR must align with its price data group within 96px")

    protected = []
    for index, box in enumerate(manifest.get("protected_boxes", [])):
        value = rect(box.get("bbox") if isinstance(box, dict) else None, f"protected_boxes[{index}].bbox", issues)
        if value:
            protected.append(value)
    for index, chapter in enumerate(manifest.get("chapters", [])):
        if not isinstance(chapter, dict):
            fail(issues, f"chapters[{index}] must be an object")
            continue
        box = rect(chapter.get("bbox"), f"chapters[{index}].bbox", issues)
        title_top = chapter.get("title_top")
        if not box or not isinstance(title_top, (int, float)):
            fail(issues, f"chapters[{index}] requires bbox and numeric title_top")
            continue
        right_gap = CANVAS_WIDTH - (box[0] + box[2])
        if abs(right_gap - 92) > 8:
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
        mode = portrait.get("portrait_mode")
        intro_top = portrait.get("intro_text_top")
        region = portrait.get("related_text_region")
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
            anchor = portrait.get("visible_head_top")
            subject = rect(portrait.get("visible_bbox"), f"portraits[{index}].visible_bbox", issues)
            label = "visible_head_top"
        else:
            anchor = portrait.get("image_rect_top")
            subject = rect(portrait.get("image_rect"), f"portraits[{index}].image_rect", issues)
            label = "image_rect_top"
        if not isinstance(anchor, (int, float)) or not subject:
            fail(issues, f"portraits[{index}] {mode} requires {label} and its matching bbox")
            continue
        if abs(anchor - intro_top) > 8:
            fail(issues, f"portraits[{index}] {label} must align to intro_text_top within ±8px")
        if subject[1] < top or subject[1] + subject[3] > bottom:
            fail(issues, f"portraits[{index}] {mode} bbox exceeds its related text region")

    seams = manifest.get("seams")
    if not isinstance(seams, list):
        fail(issues, "seams must be a list of manual canvas samples")
    else:
        for index, seam in enumerate(seams):
            if not isinstance(seam, dict) or seam.get("canvas_sample") != "#10100F" or seam.get("inspection") != "manual":
                fail(issues, f"seams[{index}] must record manual #10100F canvas sampling")
    return issues


def main():
    if len(sys.argv) != 2:
        print("usage: verify-black-gold-case-layout.py <layout-manifest.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read manifest: {error}", file=sys.stderr)
        return 2
    issues = validate(manifest)
    if issues:
        for issue in issues:
            print(f"invalid: {issue}", file=sys.stderr)
        return 1
    print("verified: objective black-gold layout manifest constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
