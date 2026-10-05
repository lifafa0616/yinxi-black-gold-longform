#!/usr/bin/env python3
"""Check a browser-produced black-gold layout manifest against its final PNG.

The manifest still describes semantic structure. Unlike the old checker, this
script also opens the final PNG and samples its real pixels. It is a stop-loss
check, not a replacement for browser-DOM measurement or human visual review.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from package_poster_html import validate_render_document
from export_layout_manifest import build_manifest

ROLE_MINIMUMS = {"title": 110, "module-title": 40, "body": 36, "price": 36, "action": 36, "date": 36, "data": 36, "metric": 36, "meta": 26}
ROLE_MINIMUM_WEIGHTS = {"module-title": 500, "price": 500, "action": 500, "date": 500, "data": 500, "metric": 500}
CANVAS_WIDTH = 1080
CANVAS_HEX = "#10100F"
CANVAS_RGB = (16, 16, 15)
PIXEL_TOLERANCE = 2
HERO_TOP_GAP_MIN = 64
HERO_TOP_GAP_MAX = 144
HERO_VISIBLE_HEIGHT_MIN = 560
PORTRAIT_CONTENT_LEFT = 112
PORTRAIT_CONTENT_RIGHT = 968
PORTRAIT_BOUND_TOLERANCE = 0.5
PORTRAIT_LABEL_GAP_MIN = 16
PORTRAIT_LABEL_GAP_MAX = 48
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


def inside_with_tolerance(child, parent, tolerance=PORTRAIT_BOUND_TOLERANCE):
    x, y, width, height = child
    px, py, pwidth, pheight = parent
    return (x >= px - tolerance and y >= py - tolerance and
            x + width <= px + pwidth + tolerance and
            y + height <= py + pheight + tolerance)


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


def validate_font_weight(block, label, issues):
    role, weight = block.get("role"), block.get("font_weight")
    if not isinstance(weight, (int, float)):
        fail(issues, f"{label} must record browser-measured font_weight")
    elif role == "body" and weight != 400:
        fail(issues, f"{label} explanatory body font_weight must be Regular 400")
    elif role in ROLE_MINIMUM_WEIGHTS and weight < ROLE_MINIMUM_WEIGHTS[role]:
        fail(issues, f"{label} {role} font_weight must be at least {ROLE_MINIMUM_WEIGHTS[role]}")


def validate_render_proof(path, issues):
    try:
        proof = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(issues, f"cannot read renderer-produced proof: {error}")
        return
    if proof.get("engine") != "playwright-chromium":
        fail(issues, "render proof engine must be playwright-chromium")
    if proof.get("fonts_ready") is not True:
        fail(issues, "render proof must confirm Google Fonts are ready")
    if proof.get("font_source") != "google-fonts-css2":
        fail(issues, "render proof font_source must be google-fonts-css2")
    if proof.get("browser_raster_from_layout_engine") is not True:
        fail(issues, "render proof must confirm browser raster came from the layout engine")
    if proof.get("png_direct_from_layout_engine") is not True:
        if proof.get("pixel_stitched") is not True or proof.get("capture_mode") != "browser-segmented-pixel-stitch":
            fail(issues, "non-direct PNG output is only allowed for browser-segmented pixel stitching")
    if proof.get("render_document") is not True:
        fail(issues, "render proof must confirm the PNG came from poster.html render document")
    if proof.get("images_ready") is not True:
        fail(issues, "render proof must confirm embedded images loaded")
    width = proof.get("canvas_width")
    if not isinstance(width, (int, float)) or abs(width - CANVAS_WIDTH) > 0.5:
        fail(issues, f"render proof canvas_width must be {CANVAS_WIDTH}px")


def validate_poster_html(path, issues):
    try:
        proof = validate_render_document(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(issues, f"poster.html render document is invalid: {error}")
        return
    if proof.get("font_source") != "google-fonts-css2" or proof.get("embedded_font_count") != 0:
        fail(issues, "poster.html must use approved Google Fonts without embedded font files")


def validate_manifest_provenance(manifest, poster_html_path, issues, measure_manifest=build_manifest):
    """Reject a manifest unless it exactly matches a fresh Chromium measurement.

    Producer strings and an HTML hash are public, self-attested metadata.  A
    second measurement made during verification is the workflow trust anchor:
    a caller cannot alter, omit, or hand-fill a layout value and still pass.
    """
    try:
        actual_hash = hashlib.sha256(poster_html_path.read_bytes()).hexdigest()
    except OSError as error:
        fail(issues, f"cannot hash poster.html for layout-manifest provenance: {error}")
        return
    if manifest.get("poster_sha256") != actual_hash:
        fail(issues, "layout manifest was not measured from this exact poster.html")
        return
    try:
        measured_manifest = measure_manifest(poster_html_path)
    except (OSError, UnicodeDecodeError, ValueError, RuntimeError) as error:
        fail(issues, f"cannot freshly measure poster.html for layout-manifest provenance: {error}")
        return
    if manifest != measured_manifest:
        fail(issues, "layout manifest differs from a fresh Chromium measurement of poster.html")


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
    # Use the flattened browser-measured element list, rather than container
    # children, so a price and QR remain one CTA group even when designers
    # place them in separate visual containers.
    for element_index, element in enumerate(manifest.get("measured_elements", [])):
        if not isinstance(element, dict) or element.get("role") not in {"price", "qr"}:
            continue
        group_id = element.get("cta_group")
        if not isinstance(group_id, str) or not group_id:
            fail(issues, f"measured_elements[{element_index}] {element.get('role')} must declare cta_group")
            continue
        if group_id not in groups:
            fail(issues, f"CTA member references undeclared cta_group {group_id!r}")
            continue
        member_box = rect(element.get("bbox"), f"measured_elements[{element_index}].bbox", issues)
        role = element["role"]
        if member_box:
            if groups[group_id][role] is not None:
                fail(issues, f"cta_group {group_id!r} contains more than one {role}")
            groups[group_id][role] = member_box
    return groups


def validate_cover_and_chapter_navigation(manifest, issues):
    zones = manifest.get("reading_zones")
    if not isinstance(zones, list) or not zones:
        return
    covers = [(index, zone) for index, zone in enumerate(zones) if isinstance(zone, dict) and zone.get("is_hero_cover") is True]
    if len(covers) != 1:
        fail(issues, "reading_zones must contain exactly one data-hero-cover")
        return
    cover_index, cover = covers[0]
    if cover_index != 0:
        fail(issues, "data-hero-cover must be the first reading zone")
    cover_id = cover.get("id")
    chapters_by_id = {}
    for index, chapter in enumerate(manifest.get("chapters", [])):
        if not isinstance(chapter, dict):
            continue
        chapter_id = chapter.get("id")
        if not isinstance(chapter_id, str) or not chapter_id:
            fail(issues, f"chapters[{index}] requires a non-empty id")
            continue
        if chapter_id in chapters_by_id:
            fail(issues, f"chapter id {chapter_id!r} is duplicated")
        chapters_by_id[chapter_id] = chapter
        if chapter.get("zone_id") == cover_id:
            fail(issues, "data-hero-cover must not contain a chapter navigation number")
    expected_number = 1
    referenced_chapter_ids = set()
    for index, module in enumerate(manifest.get("major_modules", [])):
        if not isinstance(module, dict):
            continue
        if module.get("is_hero_cover") is True or module.get("zone_id") == cover_id:
            fail(issues, f"major_modules[{index}] must not be the hero cover")
            continue
        chapter_ids = module.get("chapter_ids")
        if not isinstance(chapter_ids, list) or len(chapter_ids) != 1:
            fail(issues, f"major_modules[{index}] must contain exactly one chapter navigation number")
            continue
        chapter = chapters_by_id.get(chapter_ids[0])
        if chapter is None:
            fail(issues, f"major_modules[{index}] references an unmeasured chapter")
            continue
        referenced_chapter_ids.add(chapter_ids[0])
        if chapter.get("display_number") != f"{expected_number:02d}":
            fail(issues, f"chapters after data-hero-cover must be continuous 01…N; expected {expected_number:02d}")
        expected_number += 1
    for chapter_id, chapter in chapters_by_id.items():
        if chapter.get("zone_id") != cover_id and chapter_id not in referenced_chapter_ids:
            fail(issues, f"chapter {chapter_id!r} must belong to exactly one non-cover major module")


def validate_hero_surface_and_text_axes(manifest, issues):
    hero = manifest.get("hero")
    if isinstance(hero, dict):
        surface = rect(hero.get("surface_bbox"), "hero.surface_bbox", issues)
        if surface and (surface[0] > 0.5 or surface[0] + surface[2] < CANVAS_WIDTH - 0.5):
            fail(issues, "hero.surface_bbox must extend to both canvas sides")
    axes = manifest.get("text_axes", [])
    if not isinstance(axes, list):
        fail(issues, "text_axes must be a list when present")
        return
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict) or not isinstance(axis.get("id"), str) or not axis["id"]:
            fail(issues, f"text_axes[{index}] requires a non-empty declared axis id")
            continue
        members = axis.get("members")
        if not isinstance(axis.get("zone_id"), str) or not axis["zone_id"] or not isinstance(members, list) or not members:
            fail(issues, f"text_axes[{index}] requires one reading zone and at least one member")
            continue
        boxes = [rect(member.get("bbox") if isinstance(member, dict) else None, f"text_axes[{index}].members[{member_index}].bbox", issues)
                 for member_index, member in enumerate(members)]
        boxes = [box for box in boxes if box]
        if not boxes:
            continue
        left, right = boxes[0][0], boxes[0][0] + boxes[0][2]
        for member_index, box in enumerate(boxes[1:], start=1):
            if abs(box[0] - left) > 1 or abs((box[0] + box[2]) - right) > 1:
                fail(issues, f"text_axes[{index}].members[{member_index}] must share the declared axis left and right bounds")


def validate_plan_gold_keyword_registration(manifest, plan_path, issues):
    try:
        lines = plan_path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        fail(issues, f"cannot read Plan for gold-keyword registration: {error}")
        return
    keywords = [item.get("text") for item in manifest.get("gold_keywords", [])
                if isinstance(item, dict) and item.get("scope") == "hero-title" and isinstance(item.get("text"), str) and item["text"]]
    if not keywords:
        fail(issues, "Plan check requires at least one data-gold-keyword=hero-title in the manifest")
        return
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == "## 首帧语义与金色关键词")
    except StopIteration:
        fail(issues, "Plan must contain the '首帧语义与金色关键词' registration section")
        return
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] and cells[0] != "金色关键词" and set(cells[0]) != {"-"}:
            rows.append(cells)
    for keyword in keywords:
        if not any(keyword in row[0] and len(row) > 1 and row[1] and set(row[1]) != {"-"} for row in rows):
            fail(issues, f"Plan must register hero-title gold keyword {keyword!r} with a non-empty original-source basis in its own row")


def _validate_portrait_ensemble_legacy(hero, issues):
    """Validate the measurable L01-P01 relationships for one portrait group."""
    group = hero.get("group")
    subjects = hero.get("subjects")
    if not isinstance(group, dict) or not isinstance(subjects, list) or not 2 <= len(subjects) <= 4:
        fail(issues, "portrait-ensemble requires a group and 2–4 subjects")
        return
    group_box = rect(group.get("visible_bbox"), "hero.group.visible_bbox", issues)
    offset = group.get("center_offset_x")
    depth_order = group.get("depth_order")
    if not isinstance(offset, (int, float)) or abs(offset) > 24:
        fail(issues, "portrait-ensemble group must be centered within 24px")
    if group_box and (group_box[0] < PORTRAIT_CONTENT_LEFT or group_box[0] + group_box[2] > PORTRAIT_CONTENT_RIGHT):
        fail(issues, "portrait-ensemble group must remain inside the portrait content bounds")
    if group_box and group_box[3] > group_box[2]:
        fail(issues, "portrait-ensemble group must present a landscape rectangular silhouette")
    if not isinstance(depth_order, list) or len(set(depth_order)) < 2:
        fail(issues, "portrait-ensemble requires at least two depth levels")
    records = []
    for index, subject in enumerate(subjects):
        label = f"hero.subjects[{index}]"
        if not isinstance(subject, dict) or not isinstance(subject.get("id"), str) or not subject["id"]:
            fail(issues, f"{label} requires a non-empty id")
            continue
        if subject.get("asset_qa") != "passed":
            fail(issues, f"{label} asset_qa must be passed")
        head = rect(subject.get("head_bbox"), f"{label}.head_bbox", issues)
        visible = rect(subject.get("visible_bbox"), f"{label}.visible_bbox", issues)
        body = rect(subject.get("body_visible_bbox"), f"{label}.body_visible_bbox", issues)
        caption = rect(subject.get("caption_bbox"), f"{label}.caption_bbox", issues)
        eye, shoulder, z_index = subject.get("eye_line_y"), subject.get("shoulder_below_y"), subject.get("z_index")
        cut_mode = subject.get("silhouette_cut_mode")
        fade_start, fade_transition = subject.get("lower_fade_start_y"), subject.get("lower_fade_transition_px")
        if cut_mode != "lower-fade-only":
            fail(issues, f"{label}.silhouette_cut_mode must be lower-fade-only")
        if not isinstance(fade_start, (int, float)) or not isinstance(shoulder, (int, float)) or fade_start < shoulder:
            fail(issues, f"{label}.lower_fade_start_y must not precede shoulder_below_y")
        if not isinstance(fade_transition, (int, float)) or fade_transition < 240:
            fail(issues, f"{label}.lower_fade_transition_px must be at least 240px")
        if not all((head, visible, body, caption)) or not isinstance(eye, (int, float)) or not isinstance(shoulder, (int, float)) or not isinstance(z_index, (int, float)):
            continue
        label_gap = caption[1] - (visible[1] + visible[3])
        if label_gap < PORTRAIT_LABEL_GAP_MIN or label_gap > PORTRAIT_LABEL_GAP_MAX:
            fail(issues, f"{label}.caption_bbox must begin 16–48px below its visible portrait")
        horizontal_gap = max(head[0] - (caption[0] + caption[2]), caption[0] - (head[0] + head[2]), 0)
        if horizontal_gap > head[2] * 0.5:
            fail(issues, f"{label}.caption_bbox is not spatially bound to its head")
        if body[1] < shoulder:
            fail(issues, f"{label}.body_visible_bbox must begin at shoulder_below_y")
        records.append((subject["id"], head, visible, body, eye, shoulder, z_index))
    if len(records) != len(subjects):
        return
    head_heights = [item[1][3] for item in records]
    if min(head_heights) <= 0 or max(head_heights) / min(head_heights) > 1.03:
        fail(issues, "portrait-ensemble head heights must align within 3%")
    eyes = [item[4] for item in records]
    if max(eyes) - min(eyes) > min(head_heights) * 0.08:
        fail(issues, "portrait-ensemble eye lines must align within 8% of head height")
    exposure_heights = [visible[1] + visible[3] - head[1] for _, head, visible, *_ in records]
    if min(exposure_heights) <= 0 or max(exposure_heights) / min(exposure_heights) > 1.05:
        fail(issues, "portrait-ensemble visible exposure must align within 5%")
    if len({item[6] for item in records}) < 2:
        fail(issues, "portrait-ensemble subjects must use different z_index values")
    if len(records) >= 3:
        central = min(records, key=lambda item: abs(item[1][0] + item[1][2] / 2 - CANVAS_WIDTH / 2))
        if central[6] != max(item[6] for item in records):
            fail(issues, "portrait-ensemble central subject must occupy the foremost z_index")
    subject_ids = {item[0] for item in records}
    pairs = hero.get("pairwise_overlap")
    if not isinstance(pairs, list) or len(pairs) != len(records) * (len(records) - 1) // 2:
        fail(issues, "portrait-ensemble requires one overlap record for every subject pair")
        return
    for index, pair in enumerate(pairs):
        label = f"hero.pairwise_overlap[{index}]"
        if not isinstance(pair, dict) or pair.get("a") not in subject_ids or pair.get("b") not in subject_ids or pair.get("a") == pair.get("b"):
            fail(issues, f"{label} must name two subjects")
            continue
        head_intersection, body_overlap = pair.get("head_intersection"), pair.get("body_overlap_ratio")
        if not isinstance(head_intersection, (int, float)) or head_intersection != 0:
            fail(issues, f"{label}.head_intersection must be 0")
        if not isinstance(body_overlap, (int, float)) or body_overlap < 0 or body_overlap > 1 / 3:
            fail(issues, f"{label}.body_overlap_ratio must be 0–1/3")


def _validate_portrait_recipe_common(hero, recipe_id, subjects, issues):
    group = hero.get("group")
    if not isinstance(group, dict):
        fail(issues, f"portrait recipe {recipe_id} requires a measured group")
        return None
    group_box = rect(group.get("visible_bbox"), "hero.group.visible_bbox", issues)
    offset = group.get("center_offset_x")
    if not isinstance(offset, (int, float)) or abs(offset) > 24:
        fail(issues, f"portrait recipe {recipe_id} group must be centered within 24px")
    if group_box and (group_box[0] < PORTRAIT_CONTENT_LEFT or group_box[0] + group_box[2] > PORTRAIT_CONTENT_RIGHT):
        fail(issues, f"portrait recipe {recipe_id} group must remain inside the portrait content bounds")
    if recipe_id != "P02" and group_box and group_box[3] > group_box[2]:
        fail(issues, f"portrait recipe {recipe_id} group must present a landscape rectangular silhouette")

    records = []
    for index, subject in enumerate(subjects):
        label = f"hero.subjects[{index}]"
        if not isinstance(subject, dict) or not isinstance(subject.get("id"), str) or not subject["id"]:
            fail(issues, f"{label} requires a non-empty id")
            continue
        if subject.get("asset_qa") != "passed":
            fail(issues, f"{label} asset_qa must be passed")
        head = rect(subject.get("head_bbox"), f"{label}.head_bbox", issues)
        shoulder_box = rect(subject.get("shoulder_bbox"), f"{label}.shoulder_bbox", issues)
        visible = rect(subject.get("visible_bbox"), f"{label}.visible_bbox", issues)
        body = rect(subject.get("body_visible_bbox"), f"{label}.body_visible_bbox", issues)
        caption = rect(subject.get("caption_bbox"), f"{label}.caption_bbox", issues)
        label_box = rect(subject.get("label_bbox"), f"{label}.label_bbox", issues)
        role_box = rect(subject.get("role_bbox"), f"{label}.role_bbox", issues)
        eye = subject.get("eye_line_y")
        shoulder = subject.get("shoulder_below_y")
        z_index = subject.get("z_index")
        cut_mode = subject.get("silhouette_cut_mode")
        fade_start = subject.get("lower_fade_start_y")
        fade_transition = subject.get("lower_fade_transition_px")
        if cut_mode != "lower-fade-only":
            fail(issues, f"{label}.silhouette_cut_mode must be lower-fade-only")
        if not isinstance(fade_start, (int, float)) or not isinstance(shoulder, (int, float)) or fade_start < shoulder:
            fail(issues, f"{label}.lower_fade_start_y must not precede shoulder_below_y")
        if not isinstance(fade_transition, (int, float)) or fade_transition < 240:
            fail(issues, f"{label}.lower_fade_transition_px must be at least 240px")
        if not all((head, shoulder_box, visible, body, caption, label_box, role_box)):
            continue
        if not isinstance(eye, (int, float)) or not isinstance(shoulder, (int, float)) or not isinstance(z_index, (int, float)):
            continue
        if body[1] < shoulder:
            fail(issues, f"{label}.body_visible_bbox must begin at shoulder_below_y")
        if (visible[0] < PORTRAIT_CONTENT_LEFT - PORTRAIT_BOUND_TOLERANCE or
                visible[0] + visible[2] > PORTRAIT_CONTENT_RIGHT + PORTRAIT_BOUND_TOLERANCE):
            fail(issues, f"{label}.visible_bbox must remain inside the portrait content bounds")
        if not inside_with_tolerance(shoulder_box, visible):
            fail(issues, f"{label}.shoulder_bbox must stay inside visible_bbox")
        if not inside_with_tolerance(body, visible):
            fail(issues, f"{label}.body_visible_bbox must stay inside visible_bbox")
        if not inside_with_tolerance(label_box, caption):
            fail(issues, f"{label}.label_bbox must stay inside caption_bbox")
        if not inside_with_tolerance(role_box, caption):
            fail(issues, f"{label}.role_bbox must stay inside caption_bbox")
        if (caption[0] < PORTRAIT_CONTENT_LEFT - PORTRAIT_BOUND_TOLERANCE or
                caption[0] + caption[2] > PORTRAIT_CONTENT_RIGHT + PORTRAIT_BOUND_TOLERANCE):
            fail(issues, f"{label}.caption_bbox must remain inside the portrait content bounds")
        records.append({
            "id": subject["id"],
            "depth": subject.get("depth"),
            "head": head,
            "shoulder_box": shoulder_box,
            "visible": visible,
            "body": body,
            "caption": caption,
            "label": label_box,
            "role": role_box,
            "eye": eye,
            "shoulder": shoulder,
            "z_index": z_index,
            "caption_alignment": subject.get("caption_alignment"),
            "caption_orientation": subject.get("caption_orientation"),
            "required_protected_tokens": subject.get("required_protected_tokens"),
            "protected_tokens": subject.get("protected_tokens"),
        })
    if len(records) != len(subjects):
        return None

    subject_ids = {record["id"] for record in records}
    pairs = hero.get("pairwise_overlap")
    expected_pair_count = len(records) * (len(records) - 1) // 2
    if not isinstance(pairs, list) or len(pairs) != expected_pair_count:
        fail(issues, f"portrait recipe {recipe_id} requires one overlap record for every subject pair")
    else:
        for index, pair in enumerate(pairs):
            label = f"hero.pairwise_overlap[{index}]"
            if not isinstance(pair, dict) or pair.get("a") not in subject_ids or pair.get("b") not in subject_ids or pair.get("a") == pair.get("b"):
                fail(issues, f"{label} must name two subjects")
                continue
            head_intersection = pair.get("head_intersection")
            face_intersection = pair.get("face_intersection")
            body_overlap = pair.get("body_overlap_ratio")
            if recipe_id == "P04":
                if not isinstance(face_intersection, (int, float)) or face_intersection != 0:
                    fail(issues, f"{label}.face_intersection must be 0 for portrait recipe P04")
            elif not isinstance(head_intersection, (int, float)) or head_intersection != 0:
                fail(issues, f"{label}.head_intersection must be 0")
            if not isinstance(body_overlap, (int, float)) or body_overlap < 0 or body_overlap > 1 / 3:
                fail(issues, f"{label}.body_overlap_ratio must be 0–1/3")
    return group_box, records


def _validate_equal_head_scale(recipe_id, records, issues, tolerance_ratio=0.03, minimum_px=0):
    if len(records) < 2:
        return
    heights = [record["head"][3] for record in records]
    if min(heights) <= 0 or max(heights) - min(heights) > max(minimum_px, min(heights) * tolerance_ratio):
        tolerance = f"max({tolerance_ratio:.0%}, {minimum_px}px)" if minimum_px else f"{tolerance_ratio:.0%}"
        fail(issues, f"portrait recipe {recipe_id} head heights must align within {tolerance}")


def _validate_below_portrait_captions(recipe_id, records, issues):
    alignments = {record["caption_alignment"] for record in records}
    orientations = {record["caption_orientation"] for record in records}
    if len(alignments) != 1:
        fail(issues, f"portrait recipe {recipe_id} captions must use one shared alignment")
    if orientations != {"horizontal"}:
        fail(issues, f"portrait recipe {recipe_id} captions must be horizontal")
    caption_tops = [record["caption"][1] for record in records]
    if max(caption_tops) - min(caption_tops) > 4:
        fail(issues, f"portrait recipe {recipe_id} caption tops must align within 4px")
    for index, record in enumerate(records):
        gap = record["caption"][1] - (record["visible"][1] + record["visible"][3])
        if gap < PORTRAIT_LABEL_GAP_MIN or gap > PORTRAIT_LABEL_GAP_MAX:
            fail(issues, f"hero.subjects[{index}].caption_bbox must begin 16–48px below its visible portrait")


def _validate_recipe_p01(records, issues):
    _validate_equal_head_scale("P01", records, issues)
    _validate_below_portrait_captions("P01", records, issues)
    eyes = [record["eye"] for record in records]
    head_height = min(record["head"][3] for record in records)
    if max(eyes) - min(eyes) > head_height * 0.08:
        fail(issues, "portrait recipe P01 eye lines must align within 8% of head height")
    exposures = [record["visible"][1] + record["visible"][3] - record["head"][1] for record in records]
    if min(exposures) <= 0 or max(exposures) / min(exposures) > 1.05:
        fail(issues, "portrait recipe P01 visible exposure must align within 5%")
    central = min(records, key=lambda record: abs(record["head"][0] + record["head"][2] / 2 - CANVAS_WIDTH / 2))
    if central["z_index"] != max(record["z_index"] for record in records):
        fail(issues, "portrait recipe P01 central subject must occupy the foremost z_index")
    if central["depth"] != "foreground" or any(record["depth"] != "background" for record in records if record is not central):
        fail(issues, "portrait recipe P01 requires the central subject foreground and side subjects background")


def _validate_recipe_p02(hero, records, issues):
    record = records[0]
    if record["depth"] != "foreground":
        fail(issues, "portrait recipe P02 subject depth must be foreground")
    if record["caption_orientation"] != "horizontal":
        fail(issues, "portrait recipe P02 caption must be horizontal")
    head = record["head"]
    caption = record["caption"]
    caption_center = caption[0] + caption[2] / 2
    head_right = head[0] + head[2]
    if caption_center < head_right or caption[0] > head_right + head[2] * 0.5:
        fail(issues, "portrait recipe P02 caption must sit to the right of and remain bound to the head")
    title = rect(hero.get("title_bbox"), "hero.title_bbox", issues)
    if title and abs(record["visible"][2] - title[2]) > title[2] * 0.05:
        fail(issues, "portrait recipe P02 visible portrait width must align to title width within 5%")


def _validate_recipe_p03(records, issues):
    _validate_equal_head_scale("P03", records, issues)
    _validate_below_portrait_captions("P03", records, issues)
    if {record["depth"] for record in records} != {"equal"}:
        fail(issues, "portrait recipe P03 subjects must use equal depth")
    eyes = [record["eye"] for record in records]
    head_height = min(record["head"][3] for record in records)
    if max(eyes) - min(eyes) > head_height * 0.08:
        fail(issues, "portrait recipe P03 eye lines must align within 8% of head height")
    exposures = [record["visible"][1] + record["visible"][3] - record["head"][1] for record in records]
    if min(exposures) <= 0 or max(exposures) / min(exposures) > 1.05:
        fail(issues, "portrait recipe P03 visible exposure must align within 5%")


def _validate_recipe_p04(group_box, records, issues):
    _validate_equal_head_scale("P04", records, issues, tolerance_ratio=0.04, minimum_px=8)
    if group_box and group_box[2] < (PORTRAIT_CONTENT_RIGHT - PORTRAIT_CONTENT_LEFT) * 0.82:
        fail(issues, "portrait recipe P04 group width must occupy at least 82% of the portrait content width")
    depths = [record["depth"] for record in records]
    if depths.count("background") != 2 or depths.count("foreground") != 2:
        fail(issues, "portrait recipe P04 requires exactly two background and two foreground subjects")
    else:
        background_z = [record["z_index"] for record in records if record["depth"] == "background"]
        foreground_z = [record["z_index"] for record in records if record["depth"] == "foreground"]
        if max(background_z) >= min(foreground_z):
            fail(issues, "portrait recipe P04 foreground subjects must occupy the foremost z_index levels")
    for record in records:
        subject_id = record["id"]
        if record["caption_alignment"] != "top" or record["caption_orientation"] != "vertical":
            fail(issues, f"portrait recipe P04 subject {subject_id!r} caption must use vertical top alignment")
        if abs(record["label"][1] - record["role"][1]) > 4:
            fail(issues, f"portrait recipe P04 subject {subject_id!r} label and role tops must align within 4px")
        if record["depth"] == "background" and record["shoulder_box"][2] <= record["head"][2]:
            fail(issues, f"portrait recipe P04 background subject {subject_id!r} must expose both shoulders beyond the head width")
        required_tokens = record["required_protected_tokens"]
        protected_tokens = record["protected_tokens"]
        if not isinstance(required_tokens, list) or any(not isinstance(token, str) or not token for token in required_tokens):
            fail(issues, f"portrait recipe P04 subject {subject_id!r} requires a protected-token declaration list")
            continue
        if not isinstance(protected_tokens, list):
            fail(issues, f"portrait recipe P04 subject {subject_id!r} requires measured protected_tokens")
            continue
        for token in required_tokens:
            if token not in protected_tokens:
                fail(issues, f"portrait recipe P04 subject {subject_id!r} must preserve protected token {token!r} as one DOM node")


def validate_portrait_ensemble(hero, issues):
    """Validate legacy ensembles or dispatch the frozen P01–P04 first-frame recipes."""
    recipe_id = hero.get("recipe_id")
    if recipe_id is None:
        _validate_portrait_ensemble_legacy(hero, issues)
        return
    expected_counts = {"P01": 3, "P02": 1, "P03": 2, "P04": 4}
    if recipe_id not in expected_counts:
        fail(issues, "portrait-ensemble recipe_id must be P01, P02, P03 or P04")
        return
    subjects = hero.get("subjects")
    if not isinstance(subjects, list):
        fail(issues, f"portrait recipe {recipe_id} requires a subjects list")
        return
    expected_count = expected_counts[recipe_id]
    if len(subjects) != expected_count:
        fail(issues, f"portrait recipe {recipe_id} requires exactly {expected_count} subjects; got {len(subjects)}")
        return
    measured = _validate_portrait_recipe_common(hero, recipe_id, subjects, issues)
    if measured is None:
        return
    group_box, records = measured
    validators = {
        "P01": lambda: _validate_recipe_p01(records, issues),
        "P02": lambda: _validate_recipe_p02(hero, records, issues),
        "P03": lambda: _validate_recipe_p03(records, issues),
        "P04": lambda: _validate_recipe_p04(group_box, records, issues),
    }
    validators[recipe_id]()


def validate_portrait_asset_qa(hero, asset_qa_path, issues):
    """Check frozen portrait assets against the external QA record, not HTML data attributes."""
    try:
        record = json.loads(asset_qa_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(issues, f"cannot read portrait asset QA record: {error}")
        return
    if record.get("status") != "agent-checked-human-review-needed":
        fail(issues, "portrait asset QA record must be agent-checked-human-review-needed")
    records = record.get("subjects")
    if not isinstance(records, list):
        fail(issues, "portrait asset QA record must contain subjects")
        return
    by_id = {item.get("id"): item for item in records if isinstance(item, dict) and isinstance(item.get("id"), str)}
    for subject in hero.get("subjects", []):
        if not isinstance(subject, dict):
            continue
        subject_id, expected_hash = subject.get("id"), subject.get("asset_sha256")
        entry = by_id.get(subject_id)
        if entry is None:
            fail(issues, f"portrait asset QA record is missing {subject_id!r}")
            continue
        if entry.get("sha256") != expected_hash:
            fail(issues, f"asset QA hash for {subject_id!r} differs from hero asset_sha256")
        asset_relative = entry.get("alpha_asset")
        if not isinstance(asset_relative, str) or not asset_relative:
            fail(issues, f"asset QA record for {subject_id!r} requires alpha_asset")
        else:
            asset_path = asset_qa_path.parent / asset_relative
            try:
                actual_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
            except OSError as error:
                fail(issues, f"cannot hash frozen alpha asset for {subject_id!r}: {error}")
            else:
                if actual_hash != entry.get("sha256"):
                    fail(issues, f"frozen alpha asset hash mismatch for {subject_id!r}")
        if entry.get("agent_alpha_check") != "passed":
            fail(issues, f"asset QA record for {subject_id!r} must have agent_alpha_check=passed")
        if entry.get("human_review") not in {"needed", "approved"}:
            fail(issues, f"asset QA record for {subject_id!r} must retain human_review status")
        previews = entry.get("qa_previews")
        if not isinstance(previews, list) or len(previews) != 2:
            fail(issues, f"asset QA record for {subject_id!r} requires dark and light qa_previews")
        elif any(not isinstance(preview, str) or not (asset_qa_path.parent / preview).is_file() for preview in previews):
            fail(issues, f"asset QA previews for {subject_id!r} must exist")


def validate(manifest, png_path, proof_path, poster_html_path, plan_path=None, asset_qa_path=None):
    issues = []
    canvas = manifest.get("canvas", {})
    if canvas.get("width") != CANVAS_WIDTH:
        fail(issues, f"canvas.width must be {CANVAS_WIDTH}")
    if canvas.get("color") != CANVAS_HEX:
        fail(issues, f"canvas.color must be {CANVAS_HEX}")
    validate_render_proof(proof_path, issues)
    validate_poster_html(poster_html_path, issues)
    validate_manifest_provenance(manifest, poster_html_path, issues)
    validate_png(png_path, manifest, issues)

    hero = manifest.get("hero")
    if not isinstance(hero, dict):
        fail(issues, "hero must record the V1 visible geometry")
    else:
        strategy = hero.get("strategy")
        if strategy not in {"imagegen", "mentor-portrait", "portrait-ensemble"}:
            fail(issues, "hero.strategy must be imagegen, mentor-portrait or portrait-ensemble")
        if hero.get("measured_from_dom") is not True:
            fail(issues, "hero geometry must be measured from [data-hero] and [data-hero-copy] in Chromium")
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
        if strategy == "portrait-ensemble":
            validate_portrait_ensemble(hero, issues)
            validate_portrait_asset_qa(hero, asset_qa_path or poster_html_path.parent / "asset-qa.json", issues)
    validate_hero_surface_and_text_axes(manifest, issues)

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
            validate_font_weight(block, f"text_blocks[{index}]", issues)
            validate_rendered_lines(block, f"text_blocks[{index}]", issues)
            if block.get("overflow_x") is True or block.get("overflow_y") is True:
                fail(issues, f"text_blocks[{index}] has browser-measured overflow")

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
            validate_font_weight(child, f"containers[{index}].children[{child_index}]", issues)
            validate_rendered_lines(child, f"containers[{index}].children[{child_index}]", issues)
            if child.get("overflow_x") is True or child.get("overflow_y") is True:
                fail(issues, f"containers[{index}].children[{child_index}] has browser-measured overflow")

    for group_id, members in collect_cta_members(manifest, issues).items():
        price, qr = members["price"], members["qr"]
        if (price is None) != (qr is None):
            fail(issues, f"cta_group {group_id!r} must contain both price and qr when either is present")
        elif price and qr and abs((price[1] + price[3] / 2) - (qr[1] + qr[3] / 2)) > 96:
            fail(issues, f"cta_group {group_id!r} QR must align with its price data group within 96px")

    qr_boxes = [item for item in manifest.get("measured_elements", []) if isinstance(item, dict) and item.get("role") == "qr"]
    for qr_index, qr in enumerate(qr_boxes):
        qr_box = rect(qr.get("bbox"), f"measured_elements[qr:{qr_index}].bbox", issues)
        if not qr_box:
            continue
        for item_index, item in enumerate(manifest.get("measured_elements", [])):
            if not isinstance(item, dict) or item.get("role") in {"qr", "price"}:
                continue
            other = rect(item.get("bbox"), f"measured_elements[{item_index}].bbox", issues)
            if not other:
                continue
            if qr_box[0] < other[0] + other[2] and qr_box[0] + qr_box[2] > other[0] and qr_box[1] < other[1] + other[3] and qr_box[1] + qr_box[3] > other[1]:
                fail(issues, f"QR overlaps measured {item.get('role')} text or data")

    protected = []
    for index, box in enumerate(manifest.get("protected_boxes", [])):
        value = rect(box.get("bbox") if isinstance(box, dict) else None, f"protected_boxes[{index}].bbox", issues)
        if value:
            protected.append(value)
    validate_cover_and_chapter_navigation(manifest, issues)

    for index, chapter in enumerate(manifest.get("chapters", [])):
        if not isinstance(chapter, dict):
            fail(issues, f"chapters[{index}] must be an object")
            continue
        box, label_top, chapter_font_size = (
            rect(chapter.get("bbox"), f"chapters[{index}].bbox", issues),
            chapter.get("label_top"),
            chapter.get("font_size"),
        )
        if not box or not isinstance(label_top, (int, float)) or not isinstance(chapter_font_size, (int, float)):
            fail(issues, f"chapters[{index}] requires bbox, numeric label_top and numeric font_size")
            continue
        if abs((CANVAS_WIDTH - (box[0] + box[2])) - 92) > 8:
            fail(issues, f"chapters[{index}] right gap must be 92px ±8px")
        if abs(box[1] - label_top) > 8:
            fail(issues, f"chapters[{index}] top must align to label_top within ±8px")
        for internal_index, internal_font_size in enumerate(chapter.get("internal_index_font_sizes", [])):
            if not isinstance(internal_font_size, (int, float)) or chapter_font_size <= internal_font_size:
                fail(issues, f"chapters[{index}] must be larger than internal_index_font_sizes[{internal_index}]")
        for protected_index, protected_box in enumerate(protected):
            if box[0] < protected_box[0] + protected_box[2] and box[0] + box[2] > protected_box[0] and box[1] < protected_box[1] + protected_box[3] and box[1] + box[3] > protected_box[1]:
                fail(issues, f"chapters[{index}] overlaps protected_boxes[{protected_index}]")

    for index, portrait in enumerate(manifest.get("portraits", [])):
        if not isinstance(portrait, dict):
            fail(issues, f"portraits[{index}] must be an object")
            continue
        mode, intro_top, region = portrait.get("portrait_mode"), portrait.get("intro_text_top"), portrait.get("related_text_region")
        if mode not in {"transparent", "masked", "source-crop"}:
            fail(issues, f"portraits[{index}].portrait_mode must be transparent, masked or source-crop")
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
    if plan_path is not None:
        validate_plan_gold_keyword_registration(manifest, plan_path, issues)
    return issues


def main():
    parser = argparse.ArgumentParser(description="Verify final PNG and its browser layout manifest.")
    parser.add_argument("manifest", type=Path, help="layout-manifest.json exported after browser rendering")
    parser.add_argument("--png", required=True, type=Path, help="final PNG from render_longform.py")
    parser.add_argument("--render-proof", required=True, type=Path, help="renderer-produced render-proof.json")
    parser.add_argument("--poster-html", required=True, type=Path, help="intermediate poster.html render document")
    parser.add_argument("--plan", type=Path, help="plan.md; checks structured hero-title gold-keyword registration when supplied")
    parser.add_argument("--asset-qa", type=Path, help="asset-qa.json; defaults beside poster.html for portrait-ensemble")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read manifest: {error}", file=sys.stderr)
        return 2
    issues = validate(manifest, args.png, args.render_proof, args.poster_html, args.plan, args.asset_qa)
    if issues:
        for issue in issues:
            print(f"invalid: {issue}", file=sys.stderr)
        return 1
    print("verified: poster render document, Google Fonts proof, final PNG dimensions, master-canvas samples and layout constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
