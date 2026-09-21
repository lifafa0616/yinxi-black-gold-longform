# Chapter Editorial Production Contract Design

## Purpose

Make `chapter-editorial-v1`, distilled from the approved “AI 影视共创免费线下工作坊” case, the default black-gold layout profile. A case must no longer be able to claim an `Lxx` contract, use black-gold tokens, or publish `final.png` without proving those claims against the browser-rendered DOM and a recorded visual evaluation.

The profile preserves the approved case’s design language, not its content or fixed eight-section count: continuous charcoal master background, side rails, right-side chapter navigation, restrained deep panels, serif/sans typography, warm-white/body-gray/single-gold hierarchy, and changing editorial rhythm across reading zones.

## Non-goals

- Do not make every case reproduce the approved case’s wording, images, 8 × 1920 height, or exact coordinates.
- Do not permit old project files to become current-case assets.
- Do not attempt automatic semantic image judgement in Python. The visual evaluator remains an explicit browser/image-review step, but its report becomes a required, machine-checked release input.

## Architecture

```text
Plan + confirmed copy
  -> layout-spec.json (profile and per-zone contract)
  -> chapter-editorial-v1 component CSS + DOM
  -> poster.html / candidate.png
  -> browser layout manifest
  -> contract validator + visual evaluation report
  -> promote candidate.png to final.png
```

### 1. Executable profile

Add `chapter-editorial-v1` as the default profile. Its reusable CSS and DOM conventions supply the real design tokens and chrome:

- `--canvas`, `--panel`, `--title`, `--body`, `--gold`, `--rule`, `--chapter`, `--rail`;
- the two 48px outer rails, content safe axis, optional low-contrast internal grid, and chapter-number slot at the established right-side geometry;
- canonical classes for frame/zone, content, chapter, rail, panel, index, card, action panel, and profile-owned typography.

`render.html` must declare `data-layout-profile="chapter-editorial-v1"` and import the profile CSS before a case-local override sheet. Case CSS may set content-driven height and assets, but may not redefine a profile token or replace a required component’s geometry.

### 2. Machine-readable layout specification

Each approved production case includes `layout-spec.json`, whose schema contains:

```json
{
  "version": 1,
  "profile": "chapter-editorial-v1",
  "zones": [
    {
      "id": "V2",
      "contract": "L03",
      "chapter": "02",
      "components": ["chapter", "three-column-grid"],
      "items": 3
    }
  ]
}
```

The spec is created from the selected R/L route before rendering and is the single contract shared by rendering, DOM validation, visual review, and promotion. It records only structural facts: profile, ordered zones, selected `Lxx`, chapter/navigation use, required component types, item counts, and any real asset slots. It does not duplicate copy or invent coordinates for content that requires natural height.

### 3. Contract-to-component mapping

The profile owns an explicit mapping for the contracts used by routine black-gold cases:

| Contract | Required component and browser-verifiable condition |
|---|---|
| L01 | one hero, one title group, profile chapter/navigation chrome |
| L03 | exactly three peer cards in three horizontal columns |
| L04 | exactly four peer cards in a 2 × 2 grid |
| L05 | exactly two peer comparison tracks |
| L06 / L16 | indexed vertical path with shared reading axis |
| L08 | declared core and peripheral relationship elements; no plain list substitute |
| L09 | declared image/text split matching the selected orientation |
| L10 | one action panel; QR slot only when source QR exists |
| L12 / L14 | their approved grid/list variants with declared item count |
| L13 | person unit binds image, name, role and description |

The renderer uses these component classes and `data-layout-component` markers. The validator measures the resulting boxes, counts peers, verifies expected row/column relationships, and rejects a contract label unsupported by the actual DOM.

### 4. Token and profile validation

Extend the manifest exporter to collect computed foreground color, background color, font family, component markers, chapter boxes, rail boxes, and per-zone component boxes. Extend the validator to enforce:

- exact profile identity and approved token values on profile-owned elements;
- bundled serif/sans font usage for title/body roles;
- exactly one gold signal in each allowed scope;
- required rails, chapter boxes, safe-axis geometry, and no chapter overlap when the profile declares navigation;
- no unapproved case-local override of profile-owned token variables;
- selected contract geometry and item count from `layout-spec.json`.

The current `ai-design-efficiency` layout is a required failing fixture: its one-column L03, list-shaped L08, three-item L04, and absent chapter chrome must all produce named failures.

### 5. Release evaluator and promotion gate

Rendering produces `candidate.png`, never a publishable `final.png`. The evaluator reviews the candidate, the approved profile baseline, and the contract-validation result, then records `evaluation.json` with:

- profile and candidate hashes;
- pass/fail results for profile rhythm, contract realization, token fidelity, hero integration, and mobile readability;
- concise visual evidence for each result;
- overall `passed` only when every mandatory category passes.

`promote_candidate.py` verifies the report schema, hashes, validator success, and overall pass before creating `final.png`. Missing, stale, incomplete, or failed evaluation blocks promotion. The Plan status mirrors this lifecycle: `approved-for-production` → `candidate-rendered` → `evaluation-passed` → `rendered`; a candidate never masquerades as final output.

### 6. Skill workflow

After user copy and hero decisions are confirmed, the Skill must:

1. choose `chapter-editorial-v1` unless a future named profile is explicitly selected;
2. write the profile and zone/component route to `plan.md` and `layout-spec.json`;
3. load only the profile’s relevant component contracts;
4. compose from profile CSS/components, package, render `candidate.png`, export manifest, and run contract validation;
5. inspect the candidate against the profile baseline and write `evaluation.json`;
6. promote only after the evaluator passes; otherwise repair the named failed component and repeat the limited candidate cycle.

## Error handling

- Missing profile marker, malformed spec, unknown component, absent required component, or failed geometry is a pre-promotion failure.
- A case with no source QR cannot declare a populated L10 QR slot.
- A visual judgement that cannot be made automatically is recorded as failed/pending, not silently passed; it requires explicit human approval.
- Existing historic cases remain references. They are not automatically converted into active production cases or usable assets.

## Test strategy

1. Unit tests cover parsing and validating layout specs, tokens, component counts, grid geometry, chapter geometry, and promotion requirements.
2. A minimal invalid fixture reproduces the current failure and must fail with L03, L08, L04, and profile-chrome errors.
3. A minimal compliant chapter-editorial fixture must pass structural validation.
4. Promotion tests prove that a missing, stale, failed, or hash-mismatched evaluation cannot create `final.png`; a valid passing evaluation can.
5. Existing portable-HTML tests and the distributable-skill contract check continue to pass.

## Acceptance criteria

- A case cannot label a vertical list as `L03`, `L04`, or `L08` and pass.
- A case selecting the default profile cannot omit its declared chapter/rail/token structure and pass.
- `final.png` cannot exist through the new command path without a valid passing evaluation report tied to the exact candidate and manifest.
- The profile remains content-flexible and does not reuse reference-case content or assets.
