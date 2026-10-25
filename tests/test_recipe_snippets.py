"""Browser smoke tests: recipe isolation and cover/body classification.

Run with .venv/bin/python -m unittest discover -s tests -p test_recipe_snippets.py
These do not certify semantic quality or replacement portrait geometry.
"""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / 'assets/recipes'
SHELL = '<style>html,body{margin:0}</style>'


class RecipeSnippets(unittest.TestCase):
    def test_seed_has_cover_and_distinct_flowing_modules(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            page.set_content((ROOT / 'assets/template/render.html').read_text())
            self.assertEqual(page.locator('[data-hero-cover]').count(), 1)
            self.assertEqual(page.locator('[data-hero-cover] [data-layout-chapter]').count(), 0)
            self.assertEqual(page.locator('[data-layout-chapter]').all_text_contents(), ['01','02','03'])
            surface = page.locator('[data-hero-surface]').bounding_box()
            self.assertEqual((surface['x'], surface['width']), (0,1080))
            before = page.locator('[data-reading-zone="L04"]').bounding_box()['y']
            page.locator('h1').evaluate('(e)=>e.textContent="一个需要完整表达且不能缩小字号的核心主张".repeat(3)')
            self.assertGreater(page.locator('[data-reading-zone="L04"]').bounding_box()['y'], before)
            self.assertGreaterEqual(float(page.locator('h1').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')),110)
            browser.close()

    def test_seed_module_headers_are_compact_without_chapter_collision(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            page.set_content((ROOT / 'assets/template/render.html').read_text())
            for zone in page.locator('[data-major-module]').all():
                label = zone.locator('[data-chapter-label]').bounding_box()
                heading = zone.locator('.section-heading').bounding_box()
                chapter = zone.locator('[data-layout-chapter]').bounding_box()
                self.assertEqual(zone.locator('.section-heading [data-protected-text]').count(), 1)
                title_ink = zone.locator('.section-heading [data-protected-text]').bounding_box()
                self.assertLessEqual(heading['y'] - (label['y'] + label['height']), 36)
                self.assertTrue(title_ink['x'] + title_ink['width'] <= chapter['x'] or
                                title_ink['y'] >= chapter['y'] + chapter['height'])
            browser.close()

    def test_audience_statement_fragment_has_separate_fact_roles(self):
        fragment = RECIPES / 'content/L02-audience.html'
        self.assertTrue(fragment.exists())
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            page.set_content(SHELL + '<style>' + (RECIPES / 'common.css').read_text() + '</style>' + fragment.read_text())
            self.assertEqual(page.locator('[data-contract="L02"]').count(), 1)
            self.assertEqual(page.locator('[data-layout-container="L02-audience"]').count(), 1)
            self.assertEqual(page.locator('[data-layout-container="L02-audience"] [data-layout-role="metric"]').count(), 1)
            self.assertEqual(page.locator('[data-layout-container="L02-audience"] [data-layout-role="module-title"]').count(), 1)
            self.assertEqual(page.locator('[data-layout-container="L02-audience"] [data-layout-role="body"]').count(), 1)
            self.assertEqual(page.locator('[data-layout-container="L02-audience"] [data-layout-role="data"]').count(), 1)
            browser.close()

    def test_content_fragment_titles_avoid_chapter_navigation(self):
        fragments = list((RECIPES / 'content').glob('*.html')) + list((RECIPES / 'body').glob('*.html'))
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            for fragment in fragments:
                with self.subTest(fragment=fragment.name):
                    page.set_content(SHELL + '<style>' + (RECIPES / 'common.css').read_text() + '</style>' + fragment.read_text())
                    heading = page.locator('.section-heading')
                    if heading.count() == 0:
                        continue
                    label = page.locator('[data-chapter-label]').first.bounding_box()
                    title = heading.first.bounding_box()
                    ink = heading.first.locator('[data-protected-text]')
                    self.assertEqual(ink.count(), 1)
                    ink_box = ink.bounding_box()
                    chapter = page.locator('[data-layout-chapter]').first.bounding_box()
                    self.assertLessEqual(title['y'] - (label['y'] + label['height']), 36)
                    self.assertTrue(ink_box['x'] + ink_box['width'] <= chapter['x'] or
                                    ink_box['y'] >= chapter['y'] + chapter['height'])
            browser.close()

    def test_portrait_fragments_keep_cover_and_body_separate(self):
        expected = [('hero/P02', 1), ('hero/P03', 2), ('hero/P01', 3),
                    ('hero/P04', 4), ('body/IP01', 2), ('body/IP02', 3), ('body/IP04', 4)]
        self.assertTrue((RECIPES / 'common.css').exists(), 'missing reusable recipe library')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            for name, count in expected:
                with self.subTest(recipe=name):
                    fragment = (RECIPES / (name + '.html')).read_text()
                    page.set_content(SHELL + '<style>' + (RECIPES / 'common.css').read_text() + '</style>' + fragment)
                    cover = name.startswith('hero/')
                    self.assertEqual(page.locator('[data-hero-cover]').count(), int(cover))
                    self.assertEqual(page.locator('[data-layout-chapter]').count(), int(not cover))
                    self.assertEqual(page.locator('[data-hero-subject]' if cover else '[data-portrait-unit]').count(), count)
                    self.assertEqual(page.locator('[data-asset-qa="passed"]').count(), 0)
                    if name == 'hero/P01':
                        for caption in page.locator('[data-hero-subject-caption]').all():
                            self.assertEqual(caption.evaluate('(e)=>getComputedStyle(e).textAlign'), 'center')
                    if name == 'body/IP04':
                        people = page.locator('[data-portrait-unit]').all()
                        bottoms = [e.bounding_box()['y'] + e.bounding_box()['height'] for e in people]
                        self.assertLess(max(bottoms) - min(bottoms), 1)
                        tops = [e.bounding_box()['y'] for e in page.locator('[data-portrait-intro]').all()]
                        self.assertLess(max(tops) - min(tops), 1)
                    if not cover:
                        self.assertEqual(page.locator('[data-contract="L13"]').count(), 1)
                        self.assertEqual(page.locator('[data-portrait-recipe]').count(), 0)
                        width = page.locator('[data-inner-portrait-recipe]').bounding_box()['width']
                        self.assertEqual(width, 856)
                        for box in page.locator('[data-portrait-intro]').all():
                            rect = box.bounding_box()
                            self.assertGreaterEqual(rect['x'], 112)
                            self.assertLessEqual(rect['x'] + rect['width'], 968)
            # Loading different fragments together must not restyle the first.
            first = (RECIPES / 'body/IP01.html').read_text()
            page.set_content(SHELL + '<style>' + (RECIPES / 'common.css').read_text() + '</style>' + first)
            before = page.locator('[data-portrait-intro]').first.bounding_box()
            page.set_content(SHELL + '<style>' + (RECIPES / 'common.css').read_text() + '</style>' + first + (RECIPES / 'body/IP04.html').read_text())
            self.assertEqual(before, page.locator('[data-portrait-intro]').first.bounding_box())
            browser.close()
