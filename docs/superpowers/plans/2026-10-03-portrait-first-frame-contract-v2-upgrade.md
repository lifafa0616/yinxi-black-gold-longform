# Portrait First-Frame Contract v2 Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the approved P01–P04 portrait-first-frame recipes measurable and enforceable without changing the generic black-gold Skill routing.

**Architecture:** Extend the existing Chromium manifest with a recipe identifier and caption sub-measurements, then dispatch recipe-specific validation from the existing portrait ensemble validator. Migrate the four approved cases to the shared semantics and prove the contract against their packaged HTML and PNG outputs.

**Tech Stack:** Python 3, Playwright Chromium DOM measurement, HTML/CSS data attributes, `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-03-portrait-first-frame-contract-v2.md`

## Global Constraints

- Do not modify `SKILL.md`, `references/layout-contracts.md`, `references/layout-recipes.md`, or the daily Skill route in this phase.
- Preserve the approved P01–P04 visual output and exact person/copy identity.
- Use `data-hero="portrait-ensemble"` plus `data-portrait-recipe="P01|P02|P03|P04"` for every recipe.
- All geometry comes from Chromium DOM measurement; never trust handwritten manifest values.
- Portrait alpha assets remain non-generative, hash-locked, and subject to external `asset-qa.json` records.
- Keep the content safe area at `x=112–968`, head overlap at zero, body overlap at or below `1/3`, and lower fade at or above `240px`.

## Review Focus

- A P04 layout with valid heads but hidden rear shoulders must fail recipe validation.
- A vertical label whose top differs from its role text by more than `4px` must fail.
- `AI`, `12`, and `B端` must be measured as protected unbroken tokens, not inferred from text.
- P02 must accept exactly one subject while P01/P03/P04 reject the wrong subject count.
- Existing non-portrait hero validation must remain unchanged.

---

### Task 1: Add recipe-aware manifest fields

**Files:**
- Modify: `scripts/export_layout_manifest.py`
- Test: `tests/test_preconfirmation_tools.py`

**Interfaces:**
- Consumes: DOM attributes `data-portrait-recipe`, `data-depth`, `data-caption-alignment`, `data-caption-orientation`, `data-hero-subject-label`, `data-hero-subject-role`, and `data-no-split-token`.
- Produces: `hero.recipe_id`; subject fields `depth`, `label_bbox`, `role_bbox`, `caption_alignment`, `caption_orientation`, and `protected_tokens`.

- [ ] **Step 1: Write a failing exporter-source contract test**

Add a test asserting that the export script contains and emits every field in the Produces list from the named DOM attributes.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `.venv/bin/python -m unittest tests.test_preconfirmation_tools.PreconfirmationToolTests.test_portrait_manifest_exports_recipe_caption_and_token_fields -v`
Expected: FAIL because the new recipe and caption fields do not exist.

- [ ] **Step 3: Implement the minimal manifest extension**

Read the recipe from the hero element, require one label and one role element per subject when those selectors are declared, and measure their DOM boxes. Export protected token text from each `[data-no-split-token]` descendant.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the command from Step 2.
Expected: PASS.

### Task 2: Dispatch recipe-specific validation

**Files:**
- Modify: `scripts/verify-case-layout.py`
- Test: `tests/test_preconfirmation_tools.py`

**Interfaces:**
- Consumes: Manifest v4 fields from Task 1.
- Produces: `validate_portrait_ensemble(hero, issues)` with shared checks plus `P01–P04` branches.

- [ ] **Step 1: Write failing count and recipe tests**

Add one accepted minimal manifest per recipe and one wrong-count rejection per recipe. Assert exact messages naming `P01`, `P02`, `P03`, or `P04`.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `.venv/bin/python -m unittest tests.test_preconfirmation_tools.PreconfirmationToolTests -k portrait_recipe -v`
Expected: FAIL because the current validator has no recipe dispatch and rejects P02.

- [ ] **Step 3: Implement shared checks and recipe dispatch**

Keep asset, fade, safe-area, head intersection, and body overlap checks shared. Apply recipe-specific subject counts, depth rules, caption modes, and focal-layer rules without changing non-portrait validation.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the command from Step 2.
Expected: all portrait recipe tests PASS.

### Task 3: Enforce P04 rear shoulders and vertical typography

**Files:**
- Modify: `scripts/verify-case-layout.py`
- Test: `tests/test_preconfirmation_tools.py`

**Interfaces:**
- Consumes: P04 depth, shoulder, label/role boxes, caption alignment/orientation, and protected tokens.
- Produces: deterministic failures for hidden rear shoulders, label/role top mismatch, and split Latin/numeric tokens.

- [ ] **Step 1: Write three failing P04 regression tests**

Create tests for: rear subject shoulder coverage, label/role top delta of `5px`, and an expected protected token missing from `protected_tokens`.

- [ ] **Step 2: Run the three tests and verify RED**

Run each test directly with `unittest`; expected failures must be caused by missing P04 enforcement.

- [ ] **Step 3: Implement the minimal P04 rules**

Validate front/background presence, rear shoulder exposure metadata, label/role top delta `<=4px`, vertical/top caption settings, and declared protected-token coverage.

- [ ] **Step 4: Run the three tests and verify GREEN**

Expected: all three PASS without weakening shared portrait checks.

### Task 4: Migrate the four approved cases

**Files:**
- Modify: `cases/portrait-three-equal-contract-test/render.html`
- Modify: `cases/portrait-solo-contract-test/render.html`
- Modify: `cases/portrait-dual-equal-contract-test/render.html`
- Modify: `cases/portrait-four-tiered-contract-test/render.html`
- Modify: matching `plan.md` and `asset-qa.json` files only where required by the v2 schema

**Interfaces:**
- Consumes: Manifest and validator contracts from Tasks 1–3.
- Produces: four packaged cases using `portrait-ensemble` plus the correct recipe ID.

- [ ] **Step 1: Add semantic markers without changing visual CSS**

Add the recipe, depth, label/role, alignment/orientation, and protected-token attributes required by the spec.

- [ ] **Step 2: Repackage, measure, render, and verify each case**

Run the four standard production commands for each case.
Expected: each case passes its matching recipe validator and keeps the approved 1080px output.

- [ ] **Step 3: Visually compare the four final PNGs**

Confirm that migration introduced no person, copy, background, or spacing change. Keep status `human-review-needed`; do not claim automatic aesthetic approval.

### Task 5: Freeze contract evidence

**Files:**
- Modify: `docs/superpowers/specs/2026-10-02-portrait-hero-contract-design.md`
- Modify: `docs/superpowers/specs/2026-10-03-portrait-first-frame-contract-v2.md`
- Modify: `KNOWN-ISSUES.md`

**Interfaces:**
- Consumes: successful four-case verification evidence from Task 4.
- Produces: a supersession pointer from v1 to v2 and an evidence table with verification date/status.

- [ ] **Step 1: Mark the v1 design as superseded**

Add a top-level note linking to the v2 contract; preserve the original v1 contents as historical design evidence.

- [ ] **Step 2: Record verified outputs and remaining human-review boundaries**

Update the v2 evidence table and remove only the now-resolved multi-person first-frame item from `KNOWN-ISSUES.md`; keep unrelated issues unchanged.

- [ ] **Step 3: Run the full repository verification**

Run: `.venv/bin/python -m unittest discover -s tests -v`
Run: `bash scripts/verify-skill-contracts.sh`
Expected: both commands exit `0` with no failures.

## Self-Review

- Spec coverage: asset QA, four recipes, text binding, vertical tokens, background, hard failures, migration boundary, and human review all map to Tasks 1–5.
- Type consistency: `recipe_id`, `depth`, `label_bbox`, `role_bbox`, `caption_alignment`, `caption_orientation`, and `protected_tokens` are named identically across Tasks 1–3.
- Scope: Skill routing files are explicitly excluded; only the contract, measurement, validation, cases, and evidence are changed.
- Risk: P04 shoulder exposure is the least directly measurable rule and must use explicit measured metadata rather than inference from z-index alone.
