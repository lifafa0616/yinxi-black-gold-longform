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
  -> Evaluator
       input-check
       route-check
       design-system-check
       render-check
       visual-check
  -> pass: promote candidate.png to final.png
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
  -> evaluating
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

### Text and signal roles

Each visible reading-text leaf must declare a stable ID and one role: `hero-title`, `section-title`, `module-title`, `body`, `meta`, `kicker`, `index`, `metric`, `action`, or `quote`.

- Display roles use the bundled serif face; body/meta/kicker use the bundled sans face.
- Minimum sizes are: hero title 110px, section title 56px, module title 40px, body/action 36px, metadata 26px. A contract may declare a larger value, never a smaller one.
- The hero declares exactly one `data-signal-id` with purpose `keyword` and computed signal-gold color.
- Every later zone declares an explicit signal policy: no semantic signal, or one/more named `signal-id` nodes permitted by its L-contract variant. Each signal declares `keyword`, `result`, `conclusion`, `quote`, `action`, or `metric` purpose. Structural indices are separately marked and cannot satisfy a semantic signal requirement.
- Plain body text cannot receive signal gold. The Evaluator validates computed paint color, role, signal ID, scope and visible contribution; it never relies on fragile raw-string matching.

### Default composition profile

`chapter-editorial-v1` requires the approved case’s reusable composition grammar:

- continuous 1080px charcoal master rather than independent black pages;
- two outer rails at the profile coordinates, a content safe axis and at most three low-contrast internal structural lines;
- right-side chapter navigation where the zone/spec declares a chapter; chapter geometry, size and collision clearance are measurable;
- restrained deep panels, rules, index and action-panel components;
- changing editorial rhythm between zones rather than a repeated list/card wall.

The profile does not require eight zones, a particular hero asset, exact copy, exact zone heights or an exact reference-case image layout.

## Route and layout contracts

`route-spec.json` is the R-level contract. Each zone maps named fact/source groups to one narrative responsibility: `establish`, `explain`, `evidence`, `compare`, `progress`, `benefit`, `conclude`, or `action`. It declares the selected R skeleton and the permitted ordered L sequence. Automation verifies structural consistency; a human confirmation owns factual/semantic truth.

`layout-spec.json` is the L-level contract. It uses versioned, per-contract schemas rather than a generic `items` field. Every schema defines component IDs, ownership, required visible text/media roles, optional slots, peer sets, permitted variants and numerical geometry tolerances.

Required v1 contract predicates include:

| Contract | Mechanical predicate |
|---|---|
| L01 | one visible hero and title group; declared profile chrome. |
| L03 | exactly three visible peer cards in one horizontal three-column track. |
| L04 | exactly four visible peer cards in a two-column, two-row grid. |
| L05 | exactly two visible comparison tracks with a declared shared comparison dimension. |
| L06 | indexed vertical process nodes with declared order and axis geometry. |
| L08 | named visible core plus peripheral relationship nodes and declared connectors; a plain list cannot satisfy it. |
| L09 | declared `horizontal` or `vertical` image/text split, correct slot orientation and required media/text pairing. |
| L10 | one action panel; populated QR only when an approved QR slot/asset exists. |
| L12 / L14 | declared approved grid/list variant with exact item count and peer topology. |
| L13 | each visible person unit binds approved image, name, role and description. |
| L16 | indexed progressive stages with declared order and shared reading axis; it is not interchangeable with L06. |

Every component is marked with `data-layout-component`, zone ownership and stable component ID. Marker-only proxy DOM is prohibited: required marked components must contribute visible paint inside the canvas, have nonzero opacity, be within the measured canvas intersection, not be fully clipped, and not be fully occluded by an unrelated layer. Visible reading text in HTML, SVG or canvas must belong to a declared role/component; unsupported pseudo-element or canvas text is rejected until explicitly modeled.

## Evaluator mechanism

`evaluate_case.py <case>` is the one release decision entry point. It regenerates every derived artifact from the current case and writes `case-contract/evaluation.json` only after all checks complete. Its first four checks are deterministic; its fifth is a required same-Agent review action. A mechanical pass never substitutes for that action.

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

The Evaluator first builds a deterministic `review-bundle/`: full candidate, first-frame crop, named risk-zone crops, fixed mobile-view screenshot, profile baseline ID/hash, computed design summary and deterministic validation result. The same Agent running this Skill must then open the full candidate and the supplied crops with its native image/browser viewing capability before it returns a verdict. It may not infer a visual pass from HTML, CSS, the Manifest, or prior approval alone.

The Agent follows the profile rubric and records one of `pass`, `fail`, or `human-review-needed` in `visual-review.json`: candidate/review-bundle hashes; baseline ID/hash; viewed artifacts; each rubric finding; verdict; and concrete repair instructions on failure. The rubric judges hero integration, material quality, editorial rhythm, profile coherence, text hierarchy, semantic-gold restraint and mobile readability. `evaluate_case.py` rejects a missing, stale, malformed or non-pass review receipt; it does not contain an imaginary vision classifier.

This is an executable workflow gate, not a claim that a local script can prove an Agent literally looked at pixels. The receipt binds the Agent's decision to immutable review evidence, while the Skill's required workflow makes native viewing the action that produces it. Under the stated ordinary-workflow trust model, that is the correct enforcement boundary.

Mobile review uses a fixed Chromium version, 1080px source canvas, documented DPR, documented scale-to-mobile screenshot method and a versioned readability rubric. It is an inspection of the fixed-width longform, not a claim of responsive-page support.

## Evaluator result and release

`evaluation.json` records evaluator version, input/spec/profile hashes, candidate hash, fresh manifest hash, validation result, review-bundle hashes, the hash-bound `visual-review.json`, all checker results and named failure evidence.

- Any input, route, design-system or render failure yields `evaluation-failed`.
- A passing visual check yields `evaluation-passed`; promotion is automatic for an existing approved profile unless the user requested review.
- `human-review-needed` blocks promotion until a human records approval or rejection against the exact bundle/candidate/spec hashes.
- `promote_candidate.py` rehashes candidate, specs, validation and evaluation immediately before atomically writing `final.png` and `release.json`.

## Migration

- Existing cases remain unmodified, read-only reference material and cannot satisfy v1 promotion without explicit migration.
- New cases use the v1 contract directory and only candidate-first commands.
- Existing direct render commands remain available only for reference reproduction and produce clearly non-publishable artifacts.
- Documentation, examples and Skill commands migrate in the same release; no canonical example may instruct direct `final.png` output.

## Tests and adversarial fixtures

Implementation is staged, with a red test before every behavior change:

1. Define canonical JSON/schema parsing, lifecycle transitions, candidate-first rendering and atomic promotion. Test missing/stale/illegal records and final-name bypasses.
2. Harden portable CSS and asset allowlisting. Test external stylesheets, `@import`, remote/file URLs, symlink escapes, unlisted paths and source deletion after packaging.
3. Build profile components and contract validators. Test the current one-column-L03/list-L08/three-item-L04 failure, hidden/off-canvas/opaque/occluded marker bypasses, wrong variants, wrong zone order and bad seams.
4. Add computed Token/type/signal/chapter/rail/rhythm checks. Test fallback fonts, wrong weights/colors, missing or duplicate semantic signals, structural-index spoofing and case-CSS cascade overrides.
5. Add review-bundle, same-Agent visual-review receipt and optional human-review flow. Forward-test a realistic poster request: the Agent must open the complete candidate and risk crops, identify a deliberately injected visual defect not caught by structural checks, record it, repair it and only then promote. Also test stale bundle hashes, failed/uncertain review states, fixed mobile evidence and automatic promotion only on a valid pass.
6. Update legacy docs/commands and retain the approved film-workshop case only as a profile/visual reference fixture. Run the existing portable-HTML tests and distributable-skill checks throughout.

## Acceptance criteria

- An active v1 case cannot render a list as L03/L04/L08, omit required profile chrome, or use an unpermitted L variant and still pass the Evaluator.
- An active v1 case cannot silently use wrong fonts, sizes, Token colors, gold signal semantics, rails, chapters, panel rhythm or unmarked visible reading content and still pass.
- An active v1 case cannot use an unconfirmed source/hero route, unlisted asset, stale record, hand-authored Manifest, missing seam, hidden proxy component or unportable stylesheet and still pass.
- Normal approved-profile cases that fully pass the Evaluator automatically receive `final.png`; uncertain/new-profile/user-review cases remain blocked pending human review.
- The default profile remains content-flexible and never treats reference-case copy, images or coordinates as current-case inputs.
