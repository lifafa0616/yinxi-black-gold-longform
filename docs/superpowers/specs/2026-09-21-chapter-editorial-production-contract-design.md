# Evaluator-Centered Black-Gold Production Contract

## Decision

`black-gold-editorial-v1` becomes the executable black-gold design system. `chapter-editorial-v1`, derived from the approved “AI 影视共创免费线下工作坊” case, becomes its default composition profile.

The system is not a reference-image copier and is not an eight-section template:

- A **reference case** is a human-approved quality anchor. It is never a source of current-case copy or assets.
- A **composition profile** is reusable layout grammar: continuous charcoal master, rails, right-side chapter navigation, deep panels and editorial rhythm. It does not prescribe content, exact zone count or fixed coordinates.
- The **design system** is shared across profiles: colors, typography, semantic gold signals, spacing and component hierarchy.

Every normal case publishes through one mechanism, the **Evaluator**. The Evaluator is not a checklist document and not `evaluation.json`; it is the only orchestrator allowed to decide whether a browser-rendered candidate may become `final.png`. `evaluation.json` is merely its hash-bound result receipt.

The Skill's running Agent already has image-generation and image-viewing capability. The visual decision is therefore a mandatory action by that same Agent, using the generated review bundle; it does **not** call, configure, or depend on a separate visual-model API. Scripts contribute measured facts. They do not pretend to infer aesthetic correctness from those facts.

## Outcome

```text
confirmed source + allowed assets
  -> candidate poster
  -> prepare_evaluation
       input / route / design-system / render checks
       immutable review bundle + evaluation session
  -> same Agent opens the bundle and writes visual-review receipt
  -> finalize_evaluation
       verifies receipt, bindings and unchanged evidence
  -> pass: promotion promotes candidate.png to final.png
  -> fail: named repair items; no final.png
  -> uncertain: human-review-needed
```

Normal cases that pass every automated and visual check promote automatically. Human review is required only when the visual check is uncertain, a new/changed profile is used, or the user explicitly requests approval before release.

## Trust and scope boundary

This contract prevents ordinary Skill/Agent and workflow mistakes: omitted profiles, false L labels, unapproved assets, Token drift, skipped checks and accidental direct release. It does **not** claim to defend against a malicious person with unrestricted local filesystem and script-write access. The records below provide reproducibility and auditability, not a security boundary against the repository owner.

## Case contract

Each active case has a versioned `case-contract/` directory with canonical UTF-8 JSON serialization and SHA-256 hashes. The existing prose `plan.md` remains a human-readable explanation; it is not a gate input.

| Record | Purpose |
|---|---|
| `input-manifest.json` | Normalized source-copy hash; fact-lock IDs; allowed assets with realpath, SHA-256, media type, intended slot, origin and permission reference. |
| `confirmation.json` | Source hash; display-copy/fact mapping; copy-confirmed result; hero decision and required human confirmation reference. |
| `route-spec.json` | Selected `Rxx`; ordered source/fact groups; relationship type; narrative responsibility; allowed L sequence. |
| `layout-spec.json` | Design system/profile; ordered zones; L contract variant; components; peer/item counts; type roles; semantic signals; optional asset slots. |
| `case-state.json` | Contract version, current state, input/spec hashes, evaluator version and legal transition evidence. |

`preflight_case.py` validates schema completeness and hash consistency, then alone moves a case to `approved-for-production`. It verifies integrity only; a recorded human confirmation is responsible for approving copy meaning, source/fact mapping and asset rights.

The lifecycle is:

```text
awaiting-copy-confirmation / awaiting-hero-confirmation
  -> approved-for-production
  -> candidate-rendered
  -> evaluation-preparing
  -> awaiting-visual-review
  -> evaluation-passed | evaluation-failed | human-review-needed
  -> promoted
```

No tool may write a publishable `final.png` before `promoted`. The renderer writes `candidate.png`; `promote_candidate.py` performs the only final-name write after rehashing all required inputs immediately before an atomic promotion. Legacy cases are read-only references. The legacy direct-to-`final.png` command path is deprecated and rejected for new contract-version cases.

## Executable design system

`black-gold-editorial-v1` owns named CSS tokens and named text/component roles. Profile-owned styles are emitted as ordered inline `<style>` blocks in `render.html`; external `<link>`, CSS `@import`, remote URL and untracked stylesheet dependencies are rejected by the packager. A case-local override may set content-driven dimensions and declared assets but may not replace owned computed properties.

### Fixed visual tokens

| Role | Value |
|---|---|
| canvas | `#10100F` |
| panel | `#181816` |
| display ink | `#F0ECE2` |
| body/meta | `#94918A` |
| signal gold | `#CCAA77` |
| rule / chapter / rail | versioned profile values derived from the approved case |

### Canonical roles, editable text and signal rules

`layout-spec.json` uses three disjoint role namespaces. A node may have one role in each applicable namespace; it must not overload one ambiguous `role` value.

| Namespace | Canonical values | What it owns |
|---|---|---|
| text | `hero-title`, `section-title`, `module-title`, `body`, `meta`, `kicker`, `index`, `metric`, `price`, `action`, `quote` | An editable reading-text DOM leaf and its type token. |
| media | `hero-asset`, `person-image`, `evidence-image`, `qr`, `logo` | An approved asset slot; it is never a text role. |
| structure | `zone`, `component`, `panel`, `rail`, `chapter`, `seam`, `connector` | Layout ownership and measurable geometry; it is never copy or media. |

The legacy HTML attribute maps exactly once before validation: `title` maps to the schema-declared `hero-title` or `section-title`; `module-title`, `body`, `meta`, `action`, `price`, and `metric` keep their names; legacy `data` maps to `metric` only for an independently declared numeric datum; legacy `qr` maps to media `qr`. Any other legacy role, a role with two mappings, or a text/media/structure role on the wrong node fails migration.

- Every factual or action-bearing string—including a result number, date, price, QR instruction and gold-highlighted conclusion—must remain as editable DOM text with a stable source/fact binding. An artistic image may contain lettering only when that lettering is non-required decoration, declares `decorative-art-text: true`, and names the source-text hash it may echo. It cannot be the only carrier of required information.
- Display roles use the bundled serif face; body/meta/kicker use the bundled sans face. The profile declares exact face, weight, line-height, tracking and size minima: hero title `110px/700/1.05`, section title `56px/700/1.12`, module title `40px/700/1.18`, body/action `36px/500/1.55`, meta/kicker/index `26px/500/1.40`, and metric `64px/700/1.00`. A variant may increase size or height budget, never reduce these minima.
- The hero declares exactly one `data-signal-id` with purpose `keyword` and computed signal-gold color. Every later zone declares either no semantic signal or exactly one named signal, with purpose `keyword`, `result`, `conclusion`, `quote`, `action`, or `metric`. Structural indices, rails, borders and chapter numerals are not semantic signals and cannot satisfy the allowance.
- Plain body text cannot receive signal gold. The Evaluator validates computed paint color, role, signal ID, source binding, scope and visible contribution; it never relies on raw-string matching.

### Default composition profile

`chapter-editorial-v1` requires the approved case’s reusable composition grammar:

- continuous 1080px charcoal master rather than independent black pages;
- two outer rails at the profile coordinates, a content safe axis and at most three low-contrast internal structural lines;
- right-side chapter navigation where the zone/spec declares a chapter; chapter geometry, size and collision clearance are measurable;
- restrained deep panels, rules, index and action-panel components;
- changing editorial rhythm between zones rather than a repeated list/card wall.

The profile does not require eight zones, a particular hero asset, exact copy, exact zone heights or an exact reference-case image layout.

### Profile package and component registry

The executable profile is a versioned package, not prose that a renderer may reinterpret:

```text
profiles/chapter-editorial-v1/
  profile.json                 # profile token values and permitted component IDs
  profile.css                  # only profile-owned chrome and token declarations
  components/registry.json     # component ID -> variant schema, DOM root and CSS module
  components/<component-id>/schema.json
  components/<component-id>/template.html
  components/<component-id>/component.css
  fixtures/<component-id>/     # source data, expected manifest and approved screenshot
```

`profile.json` fixes the black-gold values that used to live only in prose: 1080px canvas; outer rails `x=48/1032`; content-safe axis `x=112–968`; at most three internal rules; chapter right edge `92px ±8px`; chapter size `176–184px`; both bundled font families/weights; all type parameters above; title-to-body gap `24–36px`; panel padding `32px`; and at most one semantic-gold signal in each reading zone. Component schemas own item count, line budgets, slot geometry, allowed content fields and permitted signal position. A case may fill fields and choose an allowed declared height; it cannot invent component CSS, change profile tokens or replace a component root.

Every `registry.json` entry has `variant_id`, `schema_path`, `template_hash`, `css_hash`, `root_selector`, `named_slots`, `required_descendant_roles`, `topology_predicate`, `fixture_ids` and `status`. `named_slots` are the only template locations that source data may fill; every other element/class is fixed by the template. For example, `L12-6` fixes one root → six `.peer` children → title/body leaves in a `2 × 3` CSS grid; `L13-M04-3C` fixes one root → 9–18 `.person` children → image/name/specialty/body leaves in three columns; `L16-G4` fixes one root → four ordered `.stage` children plus one `.outcome-strip`. The generator instantiates that component from schema data; it does not hand-write an arbitrary column/list and add an L label afterwards. The Evaluator rejects an L variant absent from the selected profile registry, a root whose component ID/schema/hash does not match, or a DOM topology that differs from the registered template except at declared data slots.

## Route and layout contracts

`route-spec.json` is the R-level contract. Each zone maps named fact/source groups to one narrative responsibility: `establish`, `explain`, `evidence`, `compare`, `progress`, `benefit`, `conclude`, or `action`. It declares the selected R skeleton and the permitted ordered L sequence. Automation verifies structural consistency; a human confirmation owns factual/semantic truth.

`layout-spec.json` is the L-level contract. It uses versioned, per-contract schemas rather than a generic `items` field. Every schema defines component IDs, ownership, required visible text/media roles, optional slots, peer sets, permitted variants and numerical geometry tolerances.

The initial v1 allowlist is deliberately finite: `L01`, `L02`, `L03`, `L04`, `L05`, `L06`, `L08`, `L09-H1`, `L09-H2`, `L09-V1`, `L09-V2`, `L10`, `L12-6`, `L13-M04-3C`, `L15-H3`, and `L16-G4`. An allowlisted identifier becomes runnable only after its profile-registry entry and fixture test exist; otherwise the router returns `unsupported-in-v1` instead of silently substituting a generic layout. `L07`, `L11`, `L14`, `L15`'s generic time/schedule variants, `L16`'s generic path variants, `L17`, and `L13` M01–M03 remain outside v1 until separately implemented and proven. The verified recipes from the approved cases therefore enter v1 precisely as `L12-6`, `L13-M04-3C`, `L15-H3` and `L16-G4`; verification does not authorize their unregistered neighbors.

Required v1 contract predicates include:

| Contract | Mechanical predicate |
|---|---|
| L01 | one visible hero and title group; declared profile chrome. |
| L02 | one visible editorial statement group with declared title/body hierarchy; it cannot impersonate a peer grid. |
| L03 | exactly three visible peer cards in one horizontal three-column track. |
| L04 | exactly four visible peer cards in a two-column, two-row grid. |
| L05 | exactly two visible comparison tracks with a declared shared comparison dimension. |
| L06 | indexed vertical process nodes with declared order and axis geometry. |
| L08 | named visible core plus peripheral relationship nodes and declared connectors; a plain list cannot satisfy it. |
| L09 | declared `horizontal` or `vertical` image/text split, correct slot orientation and required media/text pairing. |
| L10 | one action panel; populated QR only when an approved QR slot/asset exists. |
| L12-6 | exactly six visible peers in a `2 × 3` component track; required title/body leaves stay inside their owned peer. |
| L13-M04-3C | 9–18 visible person units on three equal columns; each binds approved image, name, specialty tag and one/two-line description; a short final row is centered. |
| L15-H3 | 3–5 real historical/strategic milestones on one vertical rail with square nodes and ordered metadata/title/description groups. |
| L16-G4 | exactly four progressive stage units in the frozen `2 × 2` reading order plus one source-bound outcome strip; it is not interchangeable with L04 or L06. |

Every component is marked with `data-layout-component`, zone ownership and stable component ID. Marker-only proxy DOM is prohibited. A component counts as visibly contributing only if a fixed Chromium paint-difference probe passes: take a normal screenshot and a second screenshot with that component subtree `visibility:hidden !important` while preserving layout; intersect the component’s measured rect with the canvas; then require at least `max(16, ceil(intersection-area × 0.0005))` changed source pixels in that intersection. The probe runs at the locked render DPR, ignores only fully transparent pixels, and records both screenshots, diff count and threshold in the Manifest. This rejects invisible, clipped and fully occluded proxy nodes without treating a CSS declaration as visible evidence.

Visible reading text in HTML, SVG or canvas must belong to a declared role/component; unsupported pseudo-element or canvas text is rejected until explicitly modeled. A component's owned visible pixels must overlap its declared source/text/media descendants; decorative paint may not by itself satisfy a text-, media- or topology-required component.

## Evaluator mechanism

The Evaluator is a three-part Agent orchestration, not one Python command that claims it has seen the image:

1. `prepare_evaluation.py <case>` rehashes the case, regenerates all derived artifacts and runs deterministic checks 1–4. On success it creates an immutable `evaluation-session.json` and `review-bundle/`, sets `case-state` to `awaiting-visual-review`, and returns their hashes. It cannot write `evaluation-passed`, `evaluation.json` or `final.png`.
2. The same Agent opens the complete candidate and every required review artifact using its native image/browser viewing capability, applies the rubric below, and uses `record_visual_review.py <case>` only to serialize its findings into `visual-review.json`. The helper validates required fields and hashes; it never generates a verdict, finding or visual inference.
3. `finalize_evaluation.py <case>` verifies that the session, candidate, profile, source/spec hashes, viewed-artifact list and visual receipt are mutually current and valid. It writes `evaluation.json` and changes state to `evaluation-passed`, `evaluation-failed`, or `human-review-needed`. Only an `evaluation-passed` result may enter `promotion`.

Changing any candidate/spec/source/profile artifact after preparation invalidates the session and forces a new preparation and native review. A mechanical pass never substitutes for that action.

### 1. Input check

Verifies current source hash, record schemas, confirmation/hero decision, fact-lock/display mapping completeness, allowed asset hashes and declared asset slots. The packager validates all HTML/CSS/SVG/media references against the manifest before inlining: realpaths are normalized, symlink escapes and parent-directory traversal fail, and unsupported asset mechanisms are banned until a parser is added. The portable proof retains asset-manifest ID/hash-to-embedded-byte mapping.

### 2. Route check

Verifies that route and layout specs share source/spec versions; zones occur in declared order; R responsibilities match the chosen skeleton; and only the L contracts/variants permitted by the route appear. It reports a structural mismatch, not a claim that it has proved business truth.

### 3. Design-system check

Runs against Chromium computed styles and measured boxes. It validates profile identity, owned token values, type role/font/weight/size/color, semantic signal rules, rails, chapter geometry, safe axis, panel padding, title-to-body rhythm, allowed internal lines and component ownership. It validates computed properties and boxes, not just CSS variable names or data attributes.

### 4. Render check

Freshly invokes the Manifest exporter from the exact `poster.html`; supplied Manifests are never trusted. It checks visible paint, DOM-to-canvas ownership, L geometry, overflow, orphan lines, continuity, asset load, portable HTML and renderer proof.

Zones must be an ordered, non-overlapping, 1080px-wide continuous sequence within explicit tolerance. The Evaluator derives every adjacent boundary, then requires a named seam marker with `from-zone` / `to-zone` identifiers located in that boundary corridor. It captures the specified seam pixels rather than accepting arbitrary dark points.

### 5. Visual check — same-Agent, mandatory

`prepare_evaluation` builds a deterministic `review-bundle/`: full candidate, first-frame crop, named risk-zone crops, fixed mobile-view screenshot, profile baseline ID/hash, computed design summary and deterministic validation result. The same Agent running this Skill must then open the full candidate and every supplied crop with its native image/browser viewing capability before it returns a verdict. It may not infer a visual pass from HTML, CSS, the Manifest, or prior approval alone.

The Agent records one of `pass`, `fail`, or `human-review-needed` in `visual-review.json`: evaluation-session/candidate/review-bundle/profile hashes; every viewed artifact; each rubric finding; verdict; and concrete repair instructions on failure. `finalize_evaluation` rejects a missing, stale, malformed or non-pass receipt; it does not contain an imaginary vision classifier.

The profile rubric has seven named checks. Each gets `pass`, `fail`, or `uncertain`, evidence artifact IDs and a short finding:

| Check | Pass condition | Release-blocking fail | `uncertain` is allowed only when |
|---|---|---|---|
| hero integration | one visual center explains the title and preserves the text quiet zone | generic/unrelated hero, multiple competing centers, broken crop or text collision | source intent or crop-rights evidence cannot be determined visually |
| material and asset integrity | black-gold material is restrained; no baked required copy or unapproved/altered person | broken face/identity, baked necessary text, visible edge/mask defect, fake QR/logo | an approved source asset itself is ambiguous |
| editorial rhythm and profile coherence | continuous master, rails/panels/chapters support reading rather than repeat cards | page-like breaks, a card wall, missing profile rhythm or dominant decorative chrome | a new profile deliberately changes the approved grammar |
| hierarchy and text | heading/body hierarchy, line breaks and alignment remain readable at full and mobile views | clipped/overlapping/unreadable required copy or failed hierarchy | a source-language/rendering issue cannot be judged from proof |
| semantic-gold restraint | gold marks only declared keyword/result/conclusion/quote/action/metric signals | body text is broadly gold, signal is semantically wrong, or permitted signal is visually lost | source wording makes the semantic class genuinely ambiguous |
| factual/action integrity | required DOM text, numbers, action and QR/asset relations visually match their declared bindings | a required fact/action is absent, substituted or visually mis-bound | supplied source/approval evidence is incomplete |
| mobile readability | fixed review image retains order, clear hierarchy and readable necessary copy | required copy cannot be read or action/QR becomes unusable | the required review screenshot cannot be reproduced |

`fail` on any release-blocking condition writes `evaluation-failed`; one or more `uncertain` checks write `human-review-needed`; `pass` requires all seven checks to pass. The Agent's review uses this decision table rather than free-form aesthetic approval.

This is an executable workflow gate, not a claim that a local script can prove an Agent literally looked at pixels. The receipt binds the Agent's decision to immutable review evidence, while the Skill's required workflow makes native viewing the action that produces it. Under the stated ordinary-workflow trust model, that is the correct enforcement boundary.

Rendering and review use a checked-in `toolchain-lock.json`. Production render is Chromium at the locked revision/browser version, `1080 × full-height` CSS viewport and `deviceScaleFactor: 1`. Mobile review embeds that exact candidate image at `360 CSS px` width (`1/3` scale) in a fixed review page at `deviceScaleFactor: 2`, producing a `720px`-wide proof screenshot. `render-proof.json` and `review-proof.json` record lock-file hash, Playwright version, Chromium revision/version, viewport, DPR, full-page mode, source scale and output hashes. A version/DPR/scale mismatch is a render-check failure. This is an inspection of the fixed-width longform, not a claim of responsive-page support.

## Evaluator result and release

`evaluation.json` records evaluator version, input/spec/profile hashes, candidate hash, fresh manifest hash, validation result, evaluation-session hash, review-bundle hashes, renderer/review proof hashes, the hash-bound `visual-review.json`, all checker results and named failure evidence.

- Any input, route, design-system or render failure yields `evaluation-failed`.
- A passing visual check yields `evaluation-passed`; promotion is automatic for an existing approved profile unless the user requested review.
- `human-review-needed` blocks promotion until a human records approval or rejection against the exact bundle/candidate/spec hashes.
- `promote_candidate.py` rehashes candidate, specs, validation, session, review receipt and evaluation immediately before atomically writing `final.png` and `release.json`.

## Migration

- Existing cases remain unmodified, read-only reference material and cannot satisfy v1 promotion without explicit migration.
- New cases use the v1 contract directory and only candidate-first commands.
- Existing direct render commands remain available only for reference reproduction and produce clearly non-publishable artifacts.
- Documentation, examples and Skill commands migrate in the same release; no canonical example may instruct direct `final.png` output.

## Tests and adversarial fixtures

Implementation is staged, with a red test before every behavior change:

1. Define canonical JSON/schema parsing, lifecycle transitions, candidate-first rendering and atomic promotion. Test missing/stale/illegal records and final-name bypasses.
2. Harden portable CSS and asset allowlisting. Test external stylesheets, `@import`, remote/file URLs, symlink escapes, unlisted paths and source deletion after packaging.
3. Build the `chapter-editorial-v1` profile package, component registry and contract validators. Test the current one-column-L03/list-L08/three-item-L04 failure; every active L variant must fail when its root/schema/topology differs from the registry; test hidden/off-canvas/opaque/occluded marker bypasses with the pixel-contribution probe, wrong variants, wrong zone order and bad seams.
4. Add computed Token/type/signal/chapter/rail/rhythm checks. Test fallback fonts, wrong weights/colors, missing or duplicate semantic signals, structural-index spoofing, artistic-image-only required copy, case-CSS cascade overrides and every numeric profile token boundary.
5. Add the `prepare_evaluation` → same-Agent native review → `finalize_evaluation` flow and optional human review. Forward-test a realistic poster request: the Agent must open the complete candidate and risk crops, identify a deliberately injected visual defect not caught by structural checks, record it, repair it and only then promote. Also test stale session/bundle hashes, omitted viewed artifacts, failed/uncertain review states, fixed Chromium/DPR/mobile proof and promotion only on a valid finalized pass.
6. Update legacy docs/commands and retain the approved film-workshop case only as a profile/visual reference fixture. Run the existing portable-HTML tests and distributable-skill checks throughout.

## Acceptance criteria

- An active v1 case cannot render a list as L03/L04/L08, omit required profile chrome, or use an unpermitted L variant and still pass the Evaluator.
- An active v1 case cannot silently use wrong fonts, sizes, Token colors, gold signal semantics, rails, chapters, panel rhythm or unmarked visible reading content and still pass.
- An active v1 case cannot use an unconfirmed source/hero route, unlisted asset, stale record, hand-authored Manifest, missing seam, hidden proxy component or unportable stylesheet and still pass.
- An active v1 case cannot skip the same-Agent native visual review, use a stale/unviewed review bundle, or promote from `prepare_evaluation`; it can promote only after `finalize_evaluation` validates a current all-pass receipt.
- An active v1 case cannot route into a documented-but-disabled L contract; the router must return `unsupported-in-v1` until a matching registry component and fixture are enabled.
- Normal approved-profile cases that fully pass the Evaluator automatically receive `final.png`; uncertain/new-profile/user-review cases remain blocked pending human review.
- The default profile remains content-flexible and never treats reference-case copy, images or coordinates as current-case inputs.
