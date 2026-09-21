# Chapter Editorial Production Contract Design

## Purpose

Make the existing black-gold design system executable, and make `chapter-editorial-v1`, distilled from the approved “AI 影视共创免费线下工作坊” case, the default composition profile. A case must no longer be able to claim an `Lxx` contract, use black-gold tokens, or publish `final.png` without proving those claims against the browser-rendered DOM and a recorded visual evaluation.

The profile preserves the approved case’s composition language, not its content or fixed eight-section count: continuous charcoal master background, side rails, right-side chapter navigation, restrained deep panels, and changing editorial rhythm across reading zones. The global black-gold system separately owns serif/sans typography, the warm-white/body-gray/single-gold hierarchy, and semantic text signals.

## Terms

- **Reference case:** a human-approved output used to establish quality and to evaluate a candidate. It is neither copied nor treated as a source of current-case assets.
- **Template:** a concrete HTML starting point with fixed content slots. The default workflow must not force every case into the reference case's eight sections or coordinates.
- **Design system:** shared tokens and rules that remain true across profiles: color, typography, semantic signal, spacing and component hierarchy.
- **Composition profile:** a reusable arrangement grammar that chooses how the design system appears on a longform. `chapter-editorial-v1` is the default profile: it requires the chapter-oriented chrome and editorial rhythm, while R/L routing determines the number, content and component type of the reading zones.

## Non-goals

- Do not make every case reproduce the approved case’s wording, images, 8 × 1920 height, or exact coordinates.
- Do not permit old project files to become current-case assets.
- Do not attempt automatic semantic image judgement in Python. The visual evaluator remains an explicit browser/image-review step, but its report becomes a required, machine-checked release input.

## Architecture

```text
source/input manifest + confirmed copy
  -> preflight case state + route/layout spec
  -> chapter-editorial-v1 component CSS + DOM
  -> poster.html / candidate.png
  -> freshly re-exported browser layout manifest + validation.json
  -> review bundle + visual evaluation report
  -> promote candidate.png to final.png
```

### 0. Hash-bound case records and state machine

The current prose-only Plan remains a human-readable production record, but it is not evidence for a gate. Each production case additionally uses small, machine-readable records:

- `input-manifest.json`: immutable source-copy hash, fact-lock IDs, explicit current-case input/asset allowlist, source origin/permission reference and SHA-256 for every allowed asset;
- `confirmation.json`: source-copy hash, display-copy/fact mapping, recorded copy-confirmed state and recorded hero-route decision;
- `route-spec.json`: selected `Rxx`, ordered source/fact groups, their relationship type, expected zone role, and permitted `Lxx` sequence;
- `layout-spec.json`: design system/profile plus the per-zone component, item-count, type-role and semantic-signal requirements described below;
- `case-state.json`: hash-bound lifecycle record.

Only `preflight_case.py` may transition a case from `awaiting-copy-confirmation` / `awaiting-hero-confirmation` to `approved-for-production`. It verifies that the confirmed copy, fact locks, hero decision, input allowlist, R route and L layout specification all refer to the same current source hash.

The only valid artifact lifecycle is:

```text
approved-for-production
  -> candidate-rendered
  -> validation-passed
  -> evaluation-passed
  -> rendered (publishable final)
```

Pack/render scripts reject cases lacking a current `approved-for-production` state. They only write `candidate.png`. A promotion script is the sole writer of `final.png` and only after matching validation and evaluation records pass. A stale state, source hash, asset hash, manifest hash, candidate hash or report hash is a hard failure.

### 1. Executable design system and profile

Create a global `black-gold-editorial-v1` design system and make `chapter-editorial-v1` its default composition profile. The system owns the real tokens and semantic hierarchy; the profile owns composition chrome. Their reusable CSS and DOM conventions supply:

- `--canvas`, `--panel`, `--title`, `--body`, `--gold`, `--rule`, `--chapter`, `--rail`;
- named type roles: hero title, section title, module/card title, body, metadata, kicker, index, metric, action and quote/conclusion;
- the semantic signal rule: the hero title contains exactly one declared key phrase in gold; each later zone declares either no semantic gold signal or one exact signal string with a purpose of `keyword`, `result`, `conclusion`, `quote`, `action` or `metric`; structural indices may use gold but do not count as a semantic signal; body paragraphs never receive blanket gold styling;
- default type scale and fonts: bundled serif for hero/section/module/action/quote display roles; bundled sans for body/meta/kicker; hero title 110px minimum, section title 56px minimum, module/card title 40px minimum, body/action 36px minimum and metadata 26px minimum. A profile component may use a larger declared value, but a case override cannot silently reduce a role below its token minimum;
- the two 48px outer rails, content safe axis, optional low-contrast internal grid, and chapter-number slot at the established right-side geometry;
- canonical classes for frame/zone, content, chapter, rail, panel, index, card, action panel and type roles.

`render.html` must declare `data-design-system="black-gold-editorial-v1"` and `data-layout-profile="chapter-editorial-v1"`, then import system CSS and profile CSS before a case-local override sheet. Case CSS may set content-driven height and assets, but may not redefine a system token or replace a required component’s geometry.

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

The spec is created from the selected R/L route before rendering and is the single contract shared by rendering, DOM validation, visual review, and promotion. It records only structural facts: design system, profile, ordered zones, selected `Lxx`, chapter/navigation use, required component types, item counts, selected type roles, declared semantic signal text/purpose, and any real asset slots. It does not duplicate copy or invent coordinates for content that requires natural height.

`route-spec.json` is the R-level companion to `layout-spec.json`. It prevents a plan from claiming R6 while rendering unrelated sections: every zone declares its source/fact group IDs, relationship type and one narrative responsibility from `establish`, `explain`, `evidence`, `compare`, `progress`, `benefit`, `conclude`, or `action`. The validator verifies the declared R skeleton and L sequence against this spec. It does not pretend that CSS can determine truthfulness; preflight and visual review are responsible for checking the source/fact mapping.

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

The renderer uses these component classes and `data-layout-component` markers. Every visible reading-zone text, image, card, rail, chapter, portrait, protected box and CTA must be represented by a required marker rather than an optional annotation. The validator measures the resulting boxes, counts peers, verifies expected row/column relationships, and rejects a contract label unsupported by the actual DOM. Hidden markers cannot satisfy a requirement.

### 4. Token and profile validation

Extend the manifest exporter to collect computed foreground color, background color, font family, component markers, chapter boxes, rail boxes, and per-zone component boxes. Extend the validator to enforce:

- exact design-system/profile identity and approved token values on their owned elements;
- bundled serif/sans font usage and minimum sizes for all named type roles;
- the declared gold signal string/purpose and exactly one gold signal in each allowed scope;
- required rails, chapter boxes, safe-axis geometry, and no chapter overlap when the profile declares navigation;
- no unapproved case-local override of profile-owned token variables;
- selected contract geometry and item count from `layout-spec.json`.

The exported manifest must include all four computed padding edges, direct-child anchors, computed CSS grid/flex placement, font family/weight/color, component/zone ownership, chapter boxes, rail boxes, protected boxes, portrait boxes, visible status and media boxes. Zone bboxes are validated as an ordered continuous 1080px-wide sequence; their derived adjacent boundaries define the complete seam list. A seam marker must exist for every adjacent pair, not merely for one arbitrary boundary.

Validation never trusts a supplied JSON attestation. `verify_case.py` regenerates a temporary Manifest from the exact `poster.html` in Chromium and validates that fresh measurement. On success it writes a hash-bound `validation.json` covering the source HTML, candidate PNG, render proof, poster proof, manifest and both specs.

The current `ai-design-efficiency` layout is a required failing fixture: its one-column L03, list-shaped L08, three-item L04, and absent chapter chrome must all produce named failures.

### 5. Release evaluator and promotion gate

Rendering produces `candidate.png`, never a publishable `final.png`. The evaluator reviews the candidate, the approved profile baseline, and the contract-validation result, then records `evaluation.json` with:

- profile and candidate hashes;
- pass/fail results for profile rhythm, contract realization, token fidelity, hero integration, and mobile readability;
- concise visual evidence for each result;
- overall `passed` only when every mandatory category passes.

`promote_candidate.py` verifies the report schema, hashes, validator success, and overall pass before creating `final.png`. Missing, stale, incomplete, or failed evaluation blocks promotion. The Plan status mirrors this lifecycle: `approved-for-production` → `candidate-rendered` → `evaluation-passed` → `rendered`; a candidate never masquerades as final output.

The evaluator receives a deterministic `review-bundle/`: the full candidate, first-frame crop, all named risk-zone crops, browser mobile-view screenshot, profile baseline identifier, computed layout/token summary and validation result. `evaluation.json` records the bundle hashes, evaluator/reviewer identity and time, and an explicit pass/fail for every mandatory category. If visual quality, semantic relevance or material treatment cannot be determined automatically, the result is `human-review-needed`, not pass. A human approval record tied to the same hashes is then required for promotion.

### 6. Skill workflow

After user copy and hero decisions are confirmed, the Skill must:

1. choose `chapter-editorial-v1` unless a future named profile is explicitly selected;
2. write the source/input, confirmation, R-route, L-layout and profile/component records; use `preflight_case.py` to obtain `approved-for-production`;
3. load only the profile’s relevant component contracts;
4. compose from profile CSS/components, package, render `candidate.png`, export manifest, and run contract validation;
5. inspect the candidate against the profile baseline and write `evaluation.json`;
6. promote only after the evaluator passes; otherwise repair the named failed component and repeat the limited candidate cycle.

## Error handling

- Missing profile marker, malformed spec, unknown component, absent required component, or failed geometry is a pre-promotion failure.
- A case with no source QR cannot declare a populated L10 QR slot.
- Missing, ambiguous or unapproved source copy / fact lock / hero route / input asset is a preflight failure, not a reason to render a draft final.
- The packer only embeds local assets named in `input-manifest.json`; parent-directory, historical-case and unlisted local paths fail packaging.
- A missing marker, invisible marker, incomplete seam set, unmeasured component, or manually supplied Manifest fails validation.
- A visual judgement that cannot be made automatically is recorded as failed/pending, not silently passed; it requires explicit human approval.
- Existing historic cases remain references. They are not automatically converted into active production cases or usable assets.

## Test strategy

1. Unit tests cover parsing/validation of input, confirmation, route, layout and state records; token/type roles; component counts; grid geometry; chapter/rail geometry; all-zone seam coverage; and promotion requirements.
2. A minimal invalid fixture reproduces the current failure and must fail with R-route, L03, L08, L04, profile-chrome, token and missing-seam errors.
3. A minimal compliant chapter-editorial fixture must pass the structural/profile validator. The human-approved film-workshop case is preserved as a visual reference fixture, not as a current-case asset fixture.
4. Provenance tests prove that an unlisted local asset, wrong source hash, missing confirmation, stale Manifest, hand-written Manifest, or unapproved state cannot reach packaging/rendering.
5. Promotion tests prove that a missing, stale, failed, pending-human, or hash-mismatched validation/evaluation cannot create `final.png`; a valid passing evaluation and human approval can.
6. Existing portable-HTML tests and the distributable-skill contract check continue to pass.

## Acceptance criteria

- A case cannot label a vertical list as `L03`, `L04`, or `L08` and pass.
- A case selecting the default profile cannot omit its declared chapter/rail/token structure and pass.
- A case cannot claim an R route, source/fact mapping, user confirmation, hero strategy or current-case asset without a matching hash-bound record and pass preflight.
- The packer cannot consume an asset outside the input allowlist.
- `final.png` cannot exist through the new command path without a fresh successful validation, valid passing evaluation, explicit human approval and records tied to the exact candidate and manifest.
- The profile remains content-flexible and does not reuse reference-case content or assets.
