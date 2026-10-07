import re
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VERIFY_CASE_LAYOUT = load_script("verify-case-layout.py")


def recipe_ids(markdown: str) -> set[str]:
    return set(re.findall(r"^\| `([A-Z]+\d{2})` \|", markdown, flags=re.MULTILINE))


class PortraitContractRoutingTests(unittest.TestCase):
    def test_cover_and_inner_portraits_have_separate_contracts_and_namespaces(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        first = (ROOT / "references" / "portrait-first-frame-contract.md").read_text(encoding="utf-8")
        inner_path = ROOT / "references" / "portrait-inner-page-contract.md"

        self.assertTrue(inner_path.is_file(), "inner-page portrait contract must be packaged")
        inner = inner_path.read_text(encoding="utf-8")

        self.assertIn("portrait-first-frame-contract.md", skill)
        self.assertIn("portrait-inner-page-contract.md", skill)
        self.assertEqual(recipe_ids(first), {"P01", "P02", "P03", "P04"})
        self.assertEqual(recipe_ids(inner), {"IP01", "IP02", "IP03", "IP04"})
        self.assertIn("仅在第一屏", first)
        self.assertIn("仅用于首帧之后", inner)

    def test_inner_recipe_router_preserves_the_approved_information_relations(self):
        inner = (ROOT / "references" / "portrait-inner-page-contract.md").read_text(encoding="utf-8")
        layouts = (ROOT / "references" / "layout-recipes.md").read_text(encoding="utf-8")
        contracts = (ROOT / "references" / "layout-contracts.md").read_text(encoding="utf-8")

        for marker in (
            "双人交替信息卡",
            "三人资料列表",
            "紧凑头像网格",
            "四人独立容器阵列",
            "正文人物不得调用 P01–P04",
            "人物与配套文字属于同一信息单元",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, inner)

        self.assertIn("IP01–IP04", layouts)
        self.assertIn("portrait-inner-page-contract.md", contracts)

    def test_distribution_check_requires_both_portrait_contracts(self):
        verifier = (ROOT / "scripts" / "verify-skill-contracts.sh").read_text(encoding="utf-8")
        self.assertIn("references/portrait-first-frame-contract.md", verifier)
        self.assertIn("references/portrait-inner-page-contract.md", verifier)

    def test_inner_portrait_recipe_validation_keeps_it_out_of_the_cover(self):
        portraits = [
            {
                "inner_recipe_id": "IP01",
                "unit_id": f"speaker-{index}",
                "reading_zone_contract": "L13",
                "is_in_hero_cover": False,
                "caption_alignment": "left",
            }
            for index in range(2)
        ]
        issues = []

        VERIFY_CASE_LAYOUT.validate_inner_portrait_recipes(portraits, issues)

        self.assertEqual(issues, [])

        portraits[1]["is_in_hero_cover"] = True
        issues = []
        VERIFY_CASE_LAYOUT.validate_inner_portrait_recipes(portraits, issues)
        self.assertIn("inner portrait recipe IP01 cannot appear inside the hero cover", issues)

    def test_inner_portrait_recipe_validation_rejects_cover_ids_and_wrong_counts(self):
        issues = []
        VERIFY_CASE_LAYOUT.validate_inner_portrait_recipes(
            [
                {
                    "inner_recipe_id": "P03",
                    "unit_id": "speaker-1",
                    "reading_zone_contract": "L13",
                    "is_in_hero_cover": False,
                    "caption_alignment": "left",
                }
            ],
            issues,
        )
        self.assertIn("inner portrait recipe_id must be IP01, IP02, IP03 or IP04", issues)

        issues = []
        VERIFY_CASE_LAYOUT.validate_inner_portrait_recipes(
            [
                {
                    "inner_recipe_id": "IP02",
                    "unit_id": "speaker-1",
                    "reading_zone_contract": "L13",
                    "is_in_hero_cover": False,
                    "caption_alignment": "left",
                },
                {
                    "inner_recipe_id": "IP02",
                    "unit_id": "speaker-2",
                    "reading_zone_contract": "L13",
                    "is_in_hero_cover": False,
                    "caption_alignment": "center",
                },
            ],
            issues,
        )
        self.assertIn("inner portrait recipe IP02 requires exactly 3 units; got 2", issues)
        self.assertIn("inner portrait recipe IP02 must use one caption alignment", issues)


if __name__ == "__main__":
    unittest.main()
