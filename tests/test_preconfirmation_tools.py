import importlib.util
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VERIFY_CASE_LAYOUT = load_script("verify-case-layout.py")
EXPORT_LAYOUT_MANIFEST = load_script("export_layout_manifest.py")
PACKAGE_POSTER_HTML = load_script("package_poster_html.py")


def portrait_recipe_fixture(recipe_id, subject_count=None):
    expected_counts = {"P01": 3, "P02": 1, "P03": 2, "P04": 4}
    count = expected_counts[recipe_id] if subject_count is None else subject_count
    heads_by_recipe = {
        "P01": [(170, 650), (460, 650), (750, 650)],
        "P02": [(390, 610)],
        "P03": [(220, 650), (700, 650)],
        "P04": [(190, 620), (650, 620), (330, 850), (710, 850)],
    }
    heads = heads_by_recipe[recipe_id][:count]
    while len(heads) < count:
        heads.append((170 + len(heads) * 190, 650))
    subjects = []
    for index, (head_x, head_y) in enumerate(heads):
        if recipe_id in {"P01", "P03"}:
            caption = [head_x - 30, 1230, 220, 70]
            alignment, orientation = "center", "horizontal"
        elif recipe_id == "P02":
            caption = [head_x + 184, head_y + 40, 190, 82]
            alignment, orientation = "left", "horizontal"
        else:
            caption = [max(112, head_x - 76), head_y + 180, 92, 220]
            alignment, orientation = "top", "vertical"
        if recipe_id == "P04":
            depth = "background" if index < 2 else "foreground"
        elif recipe_id == "P01":
            depth = "foreground" if index == 1 else "background"
        elif recipe_id == "P03":
            depth = "equal"
        else:
            depth = "foreground"
        subjects.append({
            "id": f"person-{index + 1}",
            "depth": depth,
            "asset_qa": "passed",
            "silhouette_cut_mode": "lower-fade-only",
            "lower_fade_start_y": head_y + 300,
            "lower_fade_transition_px": 260,
            "head_bbox": [head_x, head_y, 160, 160],
            "face_bbox": [head_x + 24, head_y + 30, 112, 112],
            "eye_line_y": head_y + 72,
            "shoulder_below_y": head_y + 280,
            "shoulder_bbox": [head_x - 35, head_y + 190, 230, 1],
            "visible_bbox": [head_x - 60, head_y, 280, 560],
            "body_visible_bbox": [head_x - 35, head_y + 280, 230, 280],
            "caption_bbox": caption,
            "label_bbox": [caption[0], caption[1], 42, 70],
            "role_bbox": [caption[0] + 50, caption[1], max(1, caption[2] - 50), caption[3]],
            "caption_alignment": alignment,
            "caption_orientation": orientation,
            "required_protected_tokens": [],
            "protected_tokens": [],
            "z_index": index + 1,
        })
    if recipe_id == "P01" and len(subjects) >= 2:
        subjects[1]["z_index"] = count + 1
        subjects[0]["visible_bbox"] = [112, subjects[0]["visible_bbox"][1], 278, subjects[0]["visible_bbox"][3]]
        subjects[2]["visible_bbox"] = [690, subjects[2]["visible_bbox"][1], 278, subjects[2]["visible_bbox"][3]]
    pairs = []
    for left in range(len(subjects)):
        for right in range(left + 1, len(subjects)):
            pairs.append({
                "a": subjects[left]["id"],
                "b": subjects[right]["id"],
                "head_intersection": 0,
                "face_intersection": 0,
                "body_overlap_ratio": 0,
            })
    if recipe_id == "P02" and subjects:
        subjects[0]["visible_bbox"] = [112, heads[0][1], 856, 560]
    group_bbox = [112, 580, 856, 760] if recipe_id != "P02" else [112, 550, 856, 800]
    return {
        "strategy": "portrait-ensemble",
        "recipe_id": recipe_id,
        "title_bbox": [112, 210, 856, 300],
        "group": {
            "visible_bbox": group_bbox,
            "center_offset_x": 0,
            "depth_order": [subject["id"] for subject in sorted(subjects, key=lambda subject: subject["z_index"])],
        },
        "subjects": subjects,
        "pairwise_overlap": pairs,
    }


class PreconfirmationToolTests(unittest.TestCase):
    def test_skill_asks_plain_language_first_screen_choice_in_the_copy_confirmation_round(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        planning = (ROOT / "references" / "content-planning.md").read_text(encoding="utf-8")
        plan_template = (ROOT / "references" / "daily-plan-template.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "production-workflow.md").read_text(encoding="utf-8")
        combined = "\n".join((skill, planning, plan_template, workflow))

        for wording in (
            "这张长图的开头第一屏，你希望读者第一眼先记住什么？",
            "先记住内容主题",
            "先记住导师或嘉宾",
            "由我根据内容判断",
        ):
            with self.subTest(wording=wording):
                self.assertIn(wording, combined)
        self.assertIn("选项 1：`theme-imagegen`", combined)
        self.assertIn("选项 2：`mentor-portrait-by-request`", combined)
        self.assertIn("没有足够依据或用户未选择时，使用选项 1", combined)
        self.assertIn("不增加新的确认轮次", combined)

    def test_public_workflow_does_not_keep_the_old_portrait_opt_in_rule(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "production-workflow.md").read_text(encoding="utf-8")

        self.assertNotIn("只有用户明确要求时才作为首帧", readme)
        self.assertNotIn("默认首帧使用主题主视觉", workflow)

    def test_skill_routes_requested_portrait_hero_to_frozen_recipe_contract(self):
        portrait_contract = ROOT / "references" / "portrait-first-frame-contract.md"
        self.assertTrue(portrait_contract.is_file())

        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = portrait_contract.read_text(encoding="utf-8")
        plan = (ROOT / "references" / "daily-plan-template.md").read_text(encoding="utf-8")
        self_check = (ROOT / "references" / "daily-self-check.md").read_text(encoding="utf-8")
        text_rules = (ROOT / "references" / "text-rendering-rules.md").read_text(encoding="utf-8")

        self.assertIn("portrait-first-frame-contract.md", skill)
        self.assertIn("mentor-portrait-by-request", skill)
        self.assertIn("scripts/decontaminate_alpha_edges.py", contract)
        for recipe_id, count in {"P01": 3, "P02": 1, "P03": 2, "P04": 4}.items():
            with self.subTest(recipe_id=recipe_id):
                self.assertIn(f"`{recipe_id}`", contract)
                self.assertIn(f"人物数：`{count}`", contract)
        for marker in (
            'data-hero="portrait-ensemble"',
            "data-portrait-recipe",
            "lower-fade-only",
            "data-no-split-token",
            "yinxi-layout-manifest-v4",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract + text_rules)
        self.assertIn("portrait_recipe：P01 / P02 / P03 / P04", plan)
        self.assertIn("人像首帧 P01–P04", self_check)

    def test_portrait_ensemble_accepts_safe_three_person_group_with_labels_below(self):
        hero = {
            "strategy": "portrait-ensemble",
            "group": {"visible_bbox": [112, 620, 856, 680], "center_offset_x": 0, "depth_order": ["wizard", "yuyi", "cisi"]},
            "subjects": [
                {"id": "wizard", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 910, "lower_fade_transition_px": 260, "head_bbox": [150, 650, 220, 220], "eye_line_y": 751,
                 "shoulder_below_y": 910, "visible_bbox": [112, 650, 280, 560], "body_visible_bbox": [112, 910, 280, 300],
                 "caption_bbox": [140, 1232, 260, 60], "z_index": 1},
                {"id": "cisi", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 910, "lower_fade_transition_px": 260, "head_bbox": [430, 650, 220, 220], "eye_line_y": 751,
                 "shoulder_below_y": 910, "visible_bbox": [392, 650, 296, 560], "body_visible_bbox": [392, 910, 296, 300],
                 "caption_bbox": [420, 1232, 260, 60], "z_index": 3},
                {"id": "yuyi", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 910, "lower_fade_transition_px": 260, "head_bbox": [710, 650, 220, 220], "eye_line_y": 751,
                 "shoulder_below_y": 910, "visible_bbox": [688, 650, 280, 560], "body_visible_bbox": [688, 910, 280, 300],
                 "caption_bbox": [700, 1232, 260, 60], "z_index": 2},
            ],
            "pairwise_overlap": [
                {"a": "wizard", "b": "cisi", "head_intersection": 0, "body_overlap_ratio": 0},
                {"a": "wizard", "b": "yuyi", "head_intersection": 0, "body_overlap_ratio": 0},
                {"a": "cisi", "b": "yuyi", "head_intersection": 0, "body_overlap_ratio": 0},
            ],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [])

    def test_portrait_ensemble_accepts_head_aligned_centered_pair(self):
        hero = {
            "strategy": "portrait-ensemble",
            "group": {"visible_bbox": [112, 600, 856, 780], "center_offset_x": 0, "depth_order": ["tingting", "wizard"]},
            "subjects": [
                {"id": "tingting", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 1170, "lower_fade_transition_px": 300, "head_bbox": [174, 650, 280, 330], "eye_line_y": 790,
                 "shoulder_below_y": 1170, "visible_bbox": [90, 650, 440, 730], "body_visible_bbox": [90, 1170, 440, 210],
                 "caption_bbox": [176, 1400, 260, 34], "z_index": 1},
                {"id": "wizard", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 1170, "lower_fade_transition_px": 300, "head_bbox": [622, 650, 286, 331], "eye_line_y": 793,
                 "shoulder_below_y": 1170, "visible_bbox": [540, 650, 450, 730], "body_visible_bbox": [540, 1170, 450, 210],
                 "caption_bbox": [630, 1400, 250, 34], "z_index": 2},
            ],
            "pairwise_overlap": [{"a": "tingting", "b": "wizard", "head_intersection": 0, "body_overlap_ratio": 0.12}],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [])

    def test_portrait_ensemble_rejects_any_pre_shoulder_silhouette_cut(self):
        hero = {
            "strategy": "portrait-ensemble",
            "group": {"visible_bbox": [112, 600, 856, 780], "center_offset_x": 0, "depth_order": ["tingting", "wizard"]},
            "subjects": [
                {"id": "tingting", "asset_qa": "passed", "silhouette_cut_mode": "container-crop", "lower_fade_start_y": 1080, "lower_fade_transition_px": 160, "head_bbox": [174, 650, 280, 330], "eye_line_y": 790,
                 "shoulder_below_y": 1170, "visible_bbox": [90, 650, 440, 730], "body_visible_bbox": [90, 1170, 440, 210],
                 "caption_bbox": [176, 1400, 260, 34], "z_index": 1},
                {"id": "wizard", "asset_qa": "passed", "silhouette_cut_mode": "lower-fade-only", "lower_fade_start_y": 1170, "lower_fade_transition_px": 300, "head_bbox": [622, 650, 286, 331], "eye_line_y": 793,
                 "shoulder_below_y": 1170, "visible_bbox": [540, 650, 450, 730], "body_visible_bbox": [540, 1170, 450, 210],
                 "caption_bbox": [630, 1400, 250, 34], "z_index": 2},
            ],
            "pairwise_overlap": [{"a": "tingting", "b": "wizard", "head_intersection": 0, "body_overlap_ratio": 0.12}],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.subjects[0].silhouette_cut_mode must be lower-fade-only",
            "hero.subjects[0].lower_fade_start_y must not precede shoulder_below_y",
            "hero.subjects[0].lower_fade_transition_px must be at least 240px",
        ])

    def test_portrait_asset_qa_rejects_hash_that_does_not_match_the_hero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "tingting.png"
            asset.write_bytes(b"frozen alpha asset")
            for name in ("tingting-dark.png", "tingting-light.png"):
                (root / name).write_bytes(b"qa preview")
            asset_qa = root / "asset-qa.json"
            asset_qa.write_text(
                """{
                  "status": "agent-checked-human-review-needed",
                  "subjects": [{
                    "id": "tingting", "alpha_asset": "tingting.png",
                    "sha256": "%s", "agent_alpha_check": "passed",
                    "human_review": "needed",
                    "qa_previews": ["tingting-dark.png", "tingting-light.png"]
                  }]
                }""" % hashlib.sha256(asset.read_bytes()).hexdigest(),
                encoding="utf-8",
            )
            issues = []

            VERIFY_CASE_LAYOUT.validate_portrait_asset_qa(
                {"subjects": [{"id": "tingting", "asset_sha256": "0" * 64, "asset_qa": "passed"}]},
                asset_qa,
                issues,
            )

            self.assertEqual(issues, ["asset QA hash for 'tingting' differs from hero asset_sha256"])

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
            self.assertEqual(
                sorted(path.relative_to(case_dir).as_posix() for path in case_dir.rglob("*")),
                ["plan.md"],
            )

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

    def test_exporter_hashes_crlf_poster_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            poster_html = Path(directory) / "poster.html"
            poster_html.write_bytes(b"<html>\r\ncheckpoint poster\r\n</html>\r\n")

            actual = EXPORT_LAYOUT_MANIFEST.poster_sha256(poster_html)

            self.assertEqual(actual, hashlib.sha256(poster_html.read_bytes()).hexdigest())

    def test_manifest_rejects_self_attested_values_that_differ_from_fresh_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            poster_html = Path(directory) / "poster.html"
            poster_html.write_text("<html>checkpoint poster</html>", encoding="utf-8")
            manifest = {
                "producer": "playwright-dom",
                "layout_engine": "playwright-chromium",
                "contract": "yinxi-layout-manifest-v2",
                "poster_sha256": hashlib.sha256(poster_html.read_bytes()).hexdigest(),
                "canvas": {"width": 1080, "color": "#10100F"},
            }
            fresh_measurement = {**manifest, "canvas": {"width": 999, "color": "#10100F"}}
            issues = []

            VERIFY_CASE_LAYOUT.validate_manifest_provenance(
                manifest,
                poster_html,
                issues,
                measure_manifest=lambda _: fresh_measurement,
            )

            self.assertEqual(issues, ["layout manifest differs from a fresh Chromium measurement of poster.html"])

    def test_cover_is_unnumbered_and_content_chapters_start_at_01(self):
        manifest = {
            "reading_zones": [
                {"id": "V1", "is_hero_cover": True},
                {"id": "V2", "is_hero_cover": False},
                {"id": "V3", "is_hero_cover": False},
            ],
            "major_modules": [
                {"id": "overview", "zone_id": "V2", "is_hero_cover": False, "chapter_ids": ["overview"]},
                {"id": "action", "zone_id": "V3", "is_hero_cover": False, "chapter_ids": ["action"]},
            ],
            "chapters": [
                {"id": "overview", "zone_id": "V2", "display_number": "01"},
                {"id": "action", "zone_id": "V3", "display_number": "02"},
            ],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_cover_and_chapter_navigation(manifest, issues)

        self.assertEqual(issues, [])

    def test_chapter_cannot_exist_outside_a_noncover_major_module(self):
        manifest = {
            "reading_zones": [
                {"id": "V1", "is_hero_cover": True},
                {"id": "V2", "is_hero_cover": False},
            ],
            "major_modules": [],
            "chapters": [{"id": "orphan", "zone_id": "V2", "display_number": "01"}],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_cover_and_chapter_navigation(manifest, issues)

        self.assertEqual(issues, ["chapter 'orphan' must belong to exactly one non-cover major module"])

    def test_fullwidth_axis_requires_shared_measured_bounds_and_full_bleed_hero_surface(self):
        manifest = {
            "hero": {"surface_bbox": [0, 680, 1080, 720]},
            "text_axes": [
                {
                    "id": "V1-copy",
                    "zone_id": "V1",
                    "members": [
                        {"role": "title", "bbox": [112, 160, 856, 132]},
                        {"role": "body", "bbox": [112, 320, 856, 86]},
                    ],
                }
            ],
        }
        issues = []

        VERIFY_CASE_LAYOUT.validate_hero_surface_and_text_axes(manifest, issues)

        self.assertEqual(issues, [])

    def test_plan_gold_keyword_check_requires_separate_keyword_and_source_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "plan.md"
            plan.write_text(
                """## 首帧语义与金色关键词\n\n| 金色关键词 | 原文依据 |\n|---|---|\n| 作品集 | source-01：AI 作品集第一步 |\n| 拆解 | source-02：拆解真实 JD |\n""",
                encoding="utf-8",
            )
            manifest = {
                "gold_keywords": [
                    {"scope": "hero-title", "text": "作品集"},
                    {"scope": "hero-title", "text": "拆解"},
                ]
            }
            issues = []

            VERIFY_CASE_LAYOUT.validate_plan_gold_keyword_registration(manifest, plan, issues)

            self.assertEqual(issues, [])

    def test_portrait_manifest_exports_recipe_caption_and_token_fields(self):
        script = EXPORT_LAYOUT_MANIFEST.EXPORT_SCRIPT

        expected_contract_fragments = [
            "recipe_id: heroes[0].dataset.portraitRecipe",
            "title_bbox: title ? box(title) : null",
            "depth: subject.dataset.depth",
            "face_bbox: face ? box(face) : box(head)",
            "label_bbox: box(labelElement)",
            "role_bbox: box(roleElement)",
            "shoulder_bbox: box(shoulderVisible)",
            "caption_alignment: caption.dataset.captionAlignment",
            "caption_orientation: caption.dataset.captionOrientation",
            "required_protected_tokens: (caption.dataset.requiredProtectedTokens || \"\")",
            "protected_tokens: Array.from(caption.querySelectorAll(\"[data-no-split-token]\"))",
        ]

        for fragment in expected_contract_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, script)

        exporter_source = (SCRIPTS / "export_layout_manifest.py").read_text(encoding="utf-8")
        self.assertIn('"contract": "yinxi-layout-manifest-v4"', exporter_source)

    def test_portrait_recipe_accepts_its_frozen_subject_count(self):
        for recipe_id in ("P01", "P02", "P03", "P04"):
            with self.subTest(recipe_id=recipe_id):
                issues = []

                VERIFY_CASE_LAYOUT.validate_portrait_ensemble(
                    portrait_recipe_fixture(recipe_id),
                    issues,
                )

                self.assertEqual(issues, [])

    def test_portrait_recipe_rejects_the_wrong_subject_count(self):
        expected_counts = {"P01": 3, "P02": 1, "P03": 2, "P04": 4}
        for recipe_id, expected_count in expected_counts.items():
            wrong_count = expected_count + 1
            with self.subTest(recipe_id=recipe_id):
                issues = []

                VERIFY_CASE_LAYOUT.validate_portrait_ensemble(
                    portrait_recipe_fixture(recipe_id, wrong_count),
                    issues,
                )

                self.assertIn(
                    f"portrait recipe {recipe_id} requires exactly {expected_count} subjects; got {wrong_count}",
                    issues,
                )

    def test_portrait_recipe_p04_rejects_hidden_rear_shoulders(self):
        hero = portrait_recipe_fixture("P04")
        hero["subjects"][0]["shoulder_bbox"][2] = 140
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P04 background subject 'person-1' must expose both shoulders beyond the head width",
        ])

    def test_portrait_recipe_p04_rejects_label_role_top_mismatch(self):
        hero = portrait_recipe_fixture("P04")
        hero["subjects"][1]["role_bbox"][1] += 5
        hero["subjects"][1]["role_bbox"][3] -= 5
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P04 subject 'person-2' label and role tops must align within 4px",
        ])

    def test_portrait_recipe_p04_rejects_missing_protected_token_node(self):
        hero = portrait_recipe_fixture("P04")
        hero["subjects"][2]["required_protected_tokens"] = ["AI"]
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P04 subject 'person-3' must preserve protected token 'AI' as one DOM node",
        ])

    def test_portrait_recipe_p02_accepts_caption_whose_center_clears_head_edge(self):
        hero = portrait_recipe_fixture("P02")
        subject = hero["subjects"][0]
        subject["head_bbox"] = [461, 834, 380, 380]
        subject["caption_bbox"] = [730, 1010, 238, 80]
        subject["label_bbox"] = [730, 1010, 238, 43]
        subject["role_bbox"] = [730, 1060, 238, 30]
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [])

    def test_portrait_recipe_p04_allows_head_boxes_to_overlap_when_faces_do_not(self):
        hero = portrait_recipe_fixture("P04")
        hero["pairwise_overlap"][4]["head_intersection"] = 1800
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [])

    def test_portrait_recipe_p04_rejects_face_overlap(self):
        hero = portrait_recipe_fixture("P04")
        hero["pairwise_overlap"][4]["head_intersection"] = 1800
        hero["pairwise_overlap"][4]["face_intersection"] = 12
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.pairwise_overlap[4].face_intersection must be 0 for portrait recipe P04",
        ])

    def test_portrait_recipe_accepts_subpixel_caption_edge_rounding(self):
        hero = portrait_recipe_fixture("P04")
        hero["subjects"][1]["caption_bbox"] = [840, 852, 128.13, 240]
        hero["subjects"][1]["label_bbox"] = [840, 852, 42, 70]
        hero["subjects"][1]["role_bbox"] = [890, 852, 78, 220]
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [])

    def test_portrait_recipe_p01_rejects_wrong_depth_identity(self):
        hero = portrait_recipe_fixture("P01")
        hero["subjects"][0]["depth"] = "foreground"
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P01 requires the central subject foreground and side subjects background",
        ])

    def test_portrait_recipe_p03_rejects_caption_baseline_mismatch(self):
        hero = portrait_recipe_fixture("P03")
        hero["subjects"][1]["caption_bbox"][1] += 5
        hero["subjects"][1]["label_bbox"][1] += 5
        hero["subjects"][1]["role_bbox"][1] += 5
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P03 caption tops must align within 4px",
        ])

    def test_portrait_recipe_p03_rejects_visible_exposure_mismatch(self):
        hero = portrait_recipe_fixture("P03")
        hero["subjects"][1]["head_bbox"][1] += 60
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P03 visible exposure must align within 5%",
        ])

    def test_portrait_recipe_rejects_detached_shoulder_marker(self):
        hero = portrait_recipe_fixture("P04")
        hero["subjects"][0]["shoulder_bbox"][0] = 0
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.subjects[0].shoulder_bbox must stay inside visible_bbox",
        ])

    def test_portrait_recipe_rejects_label_outside_caption(self):
        hero = portrait_recipe_fixture("P03")
        hero["subjects"][0]["label_bbox"][0] = 900
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.subjects[0].label_bbox must stay inside caption_bbox",
        ])

    def test_portrait_recipe_p02_rejects_underfilled_visible_width(self):
        hero = portrait_recipe_fixture("P02")
        hero["subjects"][0]["visible_bbox"][2] = 700
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "portrait recipe P02 visible portrait width must align to title width within 5%",
        ])

    def test_portrait_recipe_rejects_subject_visible_bbox_outside_content(self):
        hero = portrait_recipe_fixture("P03")
        hero["subjects"][0]["visible_bbox"][0] = 100
        hero["subjects"][0]["shoulder_bbox"][0] -= 60
        hero["subjects"][0]["body_visible_bbox"][0] -= 60
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.subjects[0].visible_bbox must remain inside the portrait content bounds",
        ])

    def test_portrait_recipe_rejects_body_marker_outside_visible_bbox(self):
        hero = portrait_recipe_fixture("P03")
        hero["subjects"][0]["body_visible_bbox"][0] = 0
        issues = []

        VERIFY_CASE_LAYOUT.validate_portrait_ensemble(hero, issues)

        self.assertEqual(issues, [
            "hero.subjects[0].body_visible_bbox must stay inside visible_bbox",
        ])

    @unittest.skipUnless(importlib.util.find_spec("playwright"), "Playwright runtime is not installed")
    def test_exporter_extracts_required_markers_from_a_crlf_portable_poster(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "render.html"
            source.write_text(
                """<!doctype html><html><head><style>
                html, body { margin: 0; } #longform-canvas { width: 1080px; min-height: 1400px; background: #10100F; color: white; }
                [data-hero-surface], [data-hero] { display: block; height: 600px; } [data-background-sample], [data-seam-sample] { display: block; height: 1px; }
                </style></head><body><main id=\"longform-canvas\" data-canvas-color=\"#10100F\">
                <section data-reading-zone=\"intro\" data-contract=\"L01\" data-hero-cover><div data-hero-copy>Hero copy</div><div data-hero-surface><div data-hero=\"imagegen\"></div></div><i data-background-sample></i></section>
                <p data-layout-role=\"body\">Body copy</p>
                <i data-seam-sample=\"intro-body\"></i><section data-reading-zone=\"chapter-zone\" data-contract=\"L02\" data-major-module=\"one\"><p data-chapter-label=\"one\">Section</p><span data-layout-chapter=\"one\">01</span><span data-internal-index>01</span></section>
                <p data-protected-text=\"claim\">Protected claim</p>
                <section data-reading-zone=\"speakers\" data-contract=\"L13\" data-major-module=\"speakers\"><div data-inner-portrait-recipe=\"IP01\">
                <section data-portrait=\"transparent\" data-portrait-unit=\"speaker-a\"><p data-portrait-intro style=\"text-align:left\">Intro</p><div data-portrait-related-text-region><div data-portrait-subject>Portrait</div></div></section>
                </div></section>
                </main></body></html>""",
                encoding="utf-8",
            )
            portable, _ = PACKAGE_POSTER_HTML.package_html(source)
            poster_html = root / "poster.html"
            poster_html.write_bytes(portable.replace("\n", "\r\n").encode("utf-8"))

            manifest = EXPORT_LAYOUT_MANIFEST.build_manifest(poster_html)

            self.assertEqual(manifest["poster_sha256"], hashlib.sha256(poster_html.read_bytes()).hexdigest())
            self.assertEqual(manifest["chapters"][0]["id"], "one")
            self.assertIn("label_top", manifest["chapters"][0])
            self.assertEqual(manifest["chapters"][0]["display_number"], "01")
            self.assertTrue(manifest["reading_zones"][0]["is_hero_cover"])
            self.assertEqual(manifest["hero"]["surface_bbox"][2], 1080)
            self.assertIn("font_weight", manifest["text_blocks"][0])
            self.assertEqual(manifest["protected_boxes"][0]["id"], "claim")
            self.assertEqual(manifest["portraits"][0]["portrait_mode"], "transparent")
            self.assertEqual(manifest["portraits"][0]["inner_recipe_id"], "IP01")
            self.assertEqual(manifest["portraits"][0]["unit_id"], "speaker-a")
            self.assertEqual(manifest["portraits"][0]["reading_zone_contract"], "L13")
            self.assertFalse(manifest["portraits"][0]["is_in_hero_cover"])
            self.assertEqual(manifest["portraits"][0]["caption_alignment"], "left")


if __name__ == "__main__":
    unittest.main()
