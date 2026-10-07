# Cover Structure Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five reusable cover, text-axis, chapter and gold-keyword rules without changing any case output.

**Architecture:** Keep semantic and visual judgment in the references and Plan. Extend the browser manifest only for measurable DOM facts: cover identity, full-bleed hero surface, text-axis geometry and chapter sequence. The verifier rejects objective structural violations; it labels semantic and visual questions for human review.

**Tech Stack:** Markdown rules, HTML data attributes, Python 3, Playwright Chromium, unittest.

**Spec:** User request in this conversation, 2026-09-28.

## Global Constraints

- Do not alter `cases/` or any poster artifact.
- Preserve existing font, hero, chapter, Plan and contract rules unless the new rule explicitly refines them.
- Do not claim automatic verification for visual integration, information redundancy or semantic keyword accuracy.
- Keep the optional Plan check structural: it may confirm registration, not the truth of the stated semantic rationale.

## Review Focus

- A cover accidentally marked as a major module must fail instead of receiving a chapter number.
- A chapter sequence with a missing or duplicated number must fail after the cover.
- A declared full-width axis whose children use different boxes must fail.
- A hero surface that does not reach both canvas sides must fail, while visual blending remains human review.
- A Plan with a missing gold-keyword registration must be reported only when the Plan checker is explicitly supplied.

### Task 1: Write the semantic rules and Plan fields

**Files:**
- Modify: `SKILL.md`, `references/layout-rules.md`, `references/black-gold-system.md`, `references/text-rendering-rules.md`, `references/daily-self-check.md`, `references/daily-plan-template.md`, `references/layout-contracts.md`, `references/content-planning.md`, `references/production-workflow.md`

- [ ] Define the cover as `data-hero-cover`, prohibit cover chapters, require post-cover `01…N`, and document `data-hero-surface` and `data-fullwidth-text-axis` markers.
- [ ] Add the one-eyebrow/no-duplicate-cover-copy requirement, explain semantic gold keyword selection, and add corresponding Plan and human-review fields.
- [ ] Document which items are browser-checkable and which require `human-review-needed`.

### Task 2: Add measured structural facts and verifier gates

**Files:**
- Modify: `scripts/export_layout_manifest.py`, `scripts/verify-case-layout.py`, `references/text-rendering-rules.md`, `scripts/verify-skill-contracts.sh`
- Test: `tests/test_preconfirmation_tools.py`

**Interfaces:**
- Produces manifest keys `hero.surface_bbox`, `reading_zones[].is_hero_cover`, `text_axes`, chapter `display_number`, and major-module cover state.
- Consumes optional `--plan <plan.md>` from the verifier to check that required gold-keyword registration fields are present, not semantically correct.

- [ ] Write failing unit tests for the cover/sequence, full-bleed surface, axis equality and optional Plan registration checks.
- [ ] Implement the smallest exporter and verifier changes that make the tests pass.
- [ ] Update the distributable-Skill contract markers.

### Task 3: Validate the edited Skill and deployment target

**Files:**
- Modify: none beyond Tasks 1–2.

- [ ] Run the focused tests, then the full unit suite and Skill-contract check.
- [ ] Run whitespace and rule-conflict scans; verify that `cases/` is untouched.
- [ ] Sync only the changed Skill resources from the project source to the configured installed Skill target, then validate that installed copy.
