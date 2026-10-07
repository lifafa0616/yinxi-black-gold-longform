# Legacy Mainline Skill Update Implementation Plan

> **For agentic workers:** Apply the smallest documented change set; do not alter existing case outputs.

**Goal:** Update the restored output-oriented Skill with the six agreed typography, hero, chapter-navigation, rhythm, and intake rules.

**Architecture:** Keep the existing flexible R/L recipe system. Add one bundled Regular font to the portable-HTML pipeline, change only the shared rule chain and its deterministic layout metadata, and retain browser measurement for geometry—not subjective mobile preview.

**Tech Stack:** Markdown rule chain, Python 3 packager/renderer/manifest verifier, Playwright Chromium, bundled Noto CJK OTF files.

**Spec:** User request in this conversation, 2026-09-28.

## Global Constraints

- Preserve existing case outputs and avoid a closed profile/component routing system.
- Formal `poster.html` embeds all three licensed production fonts; no system-font fallback.
- Explanatory body text is Regular; headings, labels, dates, price, CTA, and key data remain Medium or stronger.
- Do not retain a subjective Mobile View Check; test text through size, lines, overflow, and collision measurements.
- Default hero is the theme visual; a supplied mentor portrait is used in the middle unless the user explicitly requests a portrait hero.

### Task 1: Portable typography

**Files:** `assets/fonts/`, `assets/fonts/LICENSES.md`, `assets/template/render.html`, `scripts/package_poster_html.py`, `scripts/render_longform.py`, `scripts/export_layout_manifest.py`, `tests/test_package_poster_html.py`.

- [ ] Add a failing packager test requiring three embedded production fonts, including a 400-weight Yinxi Noto Sans family.
- [ ] Add the licensed Regular OTF and update packaging/rendering/browser font checks plus template classes.
- [ ] Run the focused test and the full Python suite.

### Task 2: Single-source workflow and visual rules

**Files:** `SKILL.md`, `references/content-planning.md`, `references/production-workflow.md`, `references/black-gold-system.md`, `references/text-rendering-rules.md`, `references/layout-recipes.md`, `references/layout-rules.md`, `references/layout-contracts.md`, `references/daily-plan-template.md`, `references/daily-self-check.md`, `README.md`.

- [ ] Replace the separate portrait-confirmation flow with the one copy-confirmation prompt that also requests portrait and QR input.
- [ ] Record the retained internal `portrait_hero_decision`; default to theme hero and respect only an explicit portrait-hero request.
- [ ] Align body/medium roles, gold key-output use, immersive hero checks, chapter-label alignment, rhythm requirements, and QR publishing state across all documents.
- [ ] Remove subjective mobile-proportion/readability wording while retaining deterministic text and layout checks.

### Task 3: Measured chapter navigation and contract checks

**Files:** `scripts/export_layout_manifest.py`, `scripts/verify-case-layout.py`, `tests/test_preconfirmation_tools.py`, `scripts/verify-skill-contracts.sh`.

- [ ] Add a failing manifest test for a chapter label top measurement.
- [ ] Export and verify chapter-number top alignment against `data-chapter-label`, right slot, protected-text collision, and hierarchy metadata.
- [ ] Update distributable-rule checks, run the focused/full suites and contract verifier.
