# creative.ad-campaign — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.ad-campaign.json`](creative.ad-campaign.json).
Salvage: none. No prior JSON and no prior memo existed for this id; both files are new.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and
  `python3 planning/domains/dispatch/make_prompt.py creative.ad-campaign` — the standing brief and
  the stamped assignment, which supplied the row metadata, the node test, the output shape and the
  done-when list this memo is audited against.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep` for each
  phrase used rather than in full. Every span in quote marks in the JSON was re-extracted
  mechanically and re-matched (audit below).
- `planning/domains/nodes/creative.json` — the schema anchor. **This is the document this row is
  measured against**, and the whole node test below is a comparison with the DEFAULT TEMPLATE held
  as prose in its `template.why`.
- `planning/domains/nodes/business_operations.go-to-market.json` — the one landed row that had
  already argued a boundary against this id, found by one grep. It names `creative.ad-campaign` as
  "the load-bearing collision on this row" and states its own NJ-BO-GTM-1: the boundary was
  authored one-way because this row had no node file. It now has one, and the edge is reciprocated
  from this side using that row's own fixture and its own discriminator, unaltered.
- `planning/domains/nodes/finance.crypto-assets.research.md` — read once, as the brief's named
  depth calibration.
- `planning/domains/roster.json` — every edge endpoint checked. All twelve `collides_with` targets
  are roster ids; all seven `falls_through_to` names and every `falls_through_if_inactive` value
  are §7.3 residual names.
- `src/evidence_shape/vocabulary.py` (via the assignment's verbatim listing) — every `source_type`
  checked against the fourteen-member `SOURCE_TYPES` list.

## THE CHARGE — the strongest case that this row should not exist

Written before the JSON, as instructed, and it is a serious case rather than a formality.

**The charge.** `creative.ad-campaign` is not an organizational situation; it is a *brand name plus
a folder habit*. Look at what the roster already contains. `creative.creative-brief` owns the
brief. `creative.revision-round` owns the round. `creative.deliverable-handoff` owns the export
set. `creative.client-engagement` owns the counterparty relationship. `creative.brand-identity`
owns the visual system. `creative.content-marketing` owns the dated grid of published material.
`business_operations.go-to-market` owns the launch. Every artifact a campaign folder contains is
already somebody's evidence. Subtract them all and what is left of "campaign" is one advertiser's
name recurring across files — which is precisely the never-alone evidence `00` forbids as sole
proof, read across from its university warning. On that reading this row is a **duplicate of its
neighbours**, and worse, a duplicate of its own schema's default template: the creative anchor
recommends client → project → stage → artifact_type, and an ad campaign is exactly a client, a
project, a stage and an artifact. Three of the brief's named failure modes fire at once — a
neighbour duplicate, a default-template duplicate, and an organisation name doing the work.

A second, sharper form of the charge: "campaign" may be nothing but a **value of the project
field** the anchor has parked. Not a node — a name a person types into a folder.

**Why the charge is defeated.** Three structures survive the subtraction, none of which belongs to
any of the seven siblings above, and none of which any of them could take without becoming this
row.

1. **The spec matrix.** A campaign's files fan out across a grid whose coordinates are *not the
   maker's own choices*: 300x250, 728x90, 160x600, 970x250, 320x50; 1x1, 4x5, 9x16; 6s, 15s, 30s.
   These recur across corpora belonging to unrelated makers and unrelated brands, because a media
   owner published a spec sheet. That is a genuinely unusual property for a creative signal — it
   is externally fixed vocabulary in a world where almost everything else is the maker's private
   naming habit. No sibling has it. A `@1x/@2x/@3x` export ladder is *density*, not a placement
   grid, and that is where `creative.deliverable-handoff` and `creative.uiux-product-design` live.
2. **The flight window.** A start date and an end date attached to *named creative*: the work has a
   scheduled public life and then stops. `creative.brand-identity` is perpetual. A handoff is one
   moment. A revision round is one date. `business_operations.go-to-market` has an instant, not a
   window — its own file says the anchor is "the crossing from private to public at a stated
   instant". A window is a different temporal object from all four.
3. **The media plan.** Channel + placement + a date *range* + a bought quantity, in one row. Any
   three of the four is a budget, a schedule or an analytics export; the four together is a buying
   document, and it exists in no other row on the roster.

Each is checkable on a real file. Each is absent from every competing sibling *by construction*,
not by convention: a brief precedes the matrix, a round sits inside the window, a handoff is a
moment inside it, an engagement spans several of them. The row stands. The charge is recorded in
the JSON's `open_question` with the re-examination trigger that would revive it, rather than
smoothed away.

## The node test, all three legs

CONNECTION.md's test: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default. This row differs on all
three, which matters, because on any one alone I would have been reluctant.

**Leg 1 — detection signals differ from the creative default.** The anchor's twelve deterministic
signals are LINKED-ASSET, LAYER/ARTBOARD, REVISION-ROUND, BRIEF, DELIVERY/HANDOFF,
PRODUCTION-PAPERWORK, SCRIPT, TIMELINE-AND-MEDIA, INDEXED-BUT-UNREADABLE, RELEASE/RIGHTS and
CATALOGUE-SIDECAR. This row adds five the anchor does not have — SPEC-MATRIX, MEDIA-PLAN,
FLIGHT-WINDOW, VARIANT-AXIS and IN-SITU PROOF — and one it sharpens (the anchor's DELIVERY signal
says "an export set whose members share one stem across format and size variants"; this row's
version requires the variation to be an *externally published* coordinate, which is a strictly
narrower and strictly more checkable claim). The five additions are the difference between "files
that vary" and "a grid", and the anchor's DELIVERY signal cannot be narrowed to them without
breaking the eleven other creative rows that legitimately rely on its broad form.

**Leg 2 — recommended dimensions differ.** The anchor's default, held as prose because the schema
declares no fields: *client where the corpus genuinely serves more than one, then project, then
stage, then artifact_type as an optional deepest level.* This row recommends *campaign (the
project level under this world's name), then **concept route**, then the **variant axis** — market
or placement — with **stage demoted** to an optional leaf.* Two substantive changes, both argued
from evidence rather than taste. **Stage is a weak level here.** A campaign's files do not sort
into concept / production / delivery, because a route that survived selection carries files at
every stage at once while a killed route carries only early ones — so a stage level scatters one
idea across three branches. The parent-context test decides it: `00` requires that "a parent
dimension should provide the context required to understand the child. A work type such as
Homework 3 is meaningful only after the course is known", and `300x250_v2.jpg` becomes
intelligible when you know the route, not when you know it is a production file. **And the client
level is dropped more often than the default drops it**, because an in-house or single-brand
campaign corpus has exactly one advertiser and a level with one value is a collector level.
The row does **not** claim `time_first`; the anchor grants the capture exception by name to
`creative.shoot-day-media` and `creative.raw-photo-catalogue` only, and a flight window is a
scheduled property of the work, not a capture date of the file. Claiming time-first on a flight
window would be claiming the photos exception without the photos evidence.

**Leg 3 — privacy rules differ in kind, not degree.** This is the leg I did not expect to carry
weight and it turned out to be the strongest. The anchor's posture is that unpublished work is
confidential *indefinitely*. Here the confidentiality has a **known expiry**, and the material
splits into three lifetimes on one date: the creative is embargoed before the flight start and
deliberately the most public artifact the maker owns after it; the media plan, the rates and the
bought quantities never flip, because they expose a counterparty's commercial terms; the usage
grants never flip at all, because they carry a third party's name, date of birth and signature.
One row holding material with three different privacy lifetimes distinguished by a single date is
not the schema default at a different intensity — it is a different rule. Against all of it,
`00`'s boundary sentence: "Privacy policy must be enforced before content reaches any model or
external connector."

## The organizational situation, bottom up — twelve fixtures

| Fixture | Why it is in the list |
|---|---|
| `AURA_Spring_KeyVisual_RouteB_Master_v4.psd` | the happy layered case, and the one where `Master`/`v4` must not become a stage |
| `AURA_Spring_RouteB_300x250_EN-GB_v2.jpg` | one matrix cell; the file that proves grid coordinates are **not** a version family |
| `AURA_Spring_Media_Plan_v7.xlsx` | the four-column buying document; also the finance false positive (cost without settlement) |
| `Campaign Brief - AURA Spring 2026.docx` | the brief, which a sibling owns more strongly than this row does — an honest concession |
| `AURA_TVC_30s_TXTLESS_ONLINE_ProRes.mov` | broadcast delivery-state vocabulary; the duration ladder that is a matrix, not revisions |
| `Talent_Usage_Grant_ODonnell_TV+OLV_EU_2026-04-01_to_2027-03-31.pdf` | third-party identity; term+territory+media is the ad-specific bound |
| `AURA_Spring_Assets_FINAL.zip` | the archive packet — the matrix is legible from the member list without unpacking |
| `Screenshot 2026-04-09 at 08.12.44.png` | the tearsheet, and the OCR/screenshot discipline case |
| `RE_ AURA legal sign-off on the 15s cutdown.eml` | mail; approval date is not a flight date |
| **`Brand_Guidelines_AURA_v3.pdf`** | **the collision fixture** (see below) |
| `AURA_Launch_Readiness_GoNoGo.xlsx` | the neighbour's fixture, reciprocated with the neighbour's own discriminator |
| `Untitled-3.psd` | the sparse file — the `HW 3.pdf` of this node |

Two carry `group_without_copying_facts`. `Untitled-3.psd` is the pure case: no stem, no brand, no
version token, a canvas size that is simultaneously a matrix coordinate, a default social export
size and a stock preview size, sitting beside nine files that *do* carry the campaign stem. It may
join the neighbourhood; nothing may be copied onto it. Note that because this schema declares no
field rows, *every* fixture's `facts_legal` is the universals only — the copying question here is
about group membership rather than about which fact travels, which is a weaker but still real form
of the same discipline.

## The collision fixture

**`Brand_Guidelines_AURA_v3.pdf`.** It looks exactly like this row's evidence and is not. It
carries the same brand string, the same colour values, the same lockups and the same typeface
names as every campaign file in the corpus; it even ships with an export set of logos at many
sizes, which reads as a matrix at a glance. It belongs to `creative.brand-identity`.

**What discriminates it:** *no dates and no external grid.* A guidelines document has no start
date, no end date, no channel names and no placement grid, because it is perpetual and it
*governs* campaigns rather than being one. Its size ladder varies by format and density — the
maker's own choice — not by a media owner's published ad-unit set. The discriminator is therefore
a conjunction with two independent halves, which is what makes it robust: shared brand evidence
plus a size ladder is not enough; the window or the grid must be present.

## Reciprocal boundaries

Twelve, each written in both directions with the same fixture named on both sides. The four that
matter most:

- **`business_operations.go-to-market`** — the only one that already existed one-way. Its file
  states the discriminator as: a cross-functional readiness plan with gates and owners across
  product, sales, support and legal supports that row; a channel plan, creative concepts, asset
  versions, media buying and a revision round support the campaign row; neither activates on an
  offering name and a date alone. I adopted it **unaltered**, on its own fixture. Reciprocally:
  this row does not claim the readiness sheet because the campaign is gated on it, and that row
  does not claim the media plan because the launch depends on it.
- **`creative.deliverable-handoff`** — the closest competitor, over `AURA_Spring_Assets_FINAL.zip`.
  The zip is the handoff row's when it is the last thing anyone can see; it is this row's when a
  window or media plan elsewhere explains what the enclosure was for.
- **`creative.brand-identity`** — the collision fixture, both directions, per the paragraph above.
- **`creative.translation-project`** — over the locale axis. A locale token *crossing* a size token
  over one campaign stem is this row's; a locale pair with a source document and a delivery of its
  own is the translation row's, even when the client and the brand are identical.

The other eight (`creative-brief`, `revision-round`, `content-marketing`, `client-engagement`,
`licensing-rights`, `post-production`, `photos.screenshot-captures`,
`career.portfolio-work-samples`) are written to the same standard in the JSON.

## Files considered and REJECTED — the tempting false positives

- **A competitor swipe folder / awards-annual downloads.** The single loudest false positive on
  this node: it is dense with brand strings, ad-unit sizes and campaign vocabulary, and every one
  of those points at the wrong owner. Routed to **Reference Clips**, whose design text carries the
  exact test — material that "does not belong to a current project".
- **An analytics or performance export** (impressions, clicks, spend by placement, by day). It
  shares the media plan's whole vocabulary. Rejected because it is a *measurement of what already
  ran*, has no creative attached, and would drag this row into reporting; where it matters, it is
  `business_operations.market-research`'s neighbourhood. Kept only as a `never_alone` on channel
  names.
- **An advertising invoice from the media agency.** Costs, placements, dates — and a payer, an
  invoice identity and settlement terms, which the media plan has none of. That triad is finance's,
  and adding it here would give one evidence item two homes.
- **A downloaded platform spec sheet** (the PDF listing the ad units). Tempting because it is the
  literal source of this row's grid vocabulary. Rejected: it is reference material with no work
  around it, identical across every campaign anyone ever ran. **Reference Clips**.
- **A stock or licensed music track used in the spot.** A library asset, not a campaign artifact;
  the anchor already carries "stock or library asset" as a work-type value, and the licence for it
  is `creative.licensing-rights`.
- **A social media export of the brand's own account.** Superficially a dated grid of published
  material. It is `photos.social-media-export` or `creative.content-marketing`: owned channel, no
  purchase, no placement.
- **A font file shipped in the delivery zip.** The anchor's own never-alone rule covers it — an
  installed or licensed font is a stock asset, not a project.
- **A casting or shoot day's call sheet.** Real, and adjacent, but it is
  `creative.commissioned-shoot` and `creative.shoot-day-media` evidence: it names a day, not a
  window, and produces the input this row multiplies.

## `proposed_fields` — empty, deliberately

`fields: []` by `_CONTRACT` rule 12, and because the creative schema anchor declares no field rows
at all (D1 as narrowed, rules 10 and 15, CONNECTION PR-6). `proposed_fields: []` is the harder
decision and it is deliberate. Two keys were genuinely tempting:

- **a PLACEMENT key** — the ad-unit slot a file is cut for. It is the most characteristic string in
  this world and it is still not a template row's to mint: minting it would widen the schema from
  below, and it would immediately raise whether a folder may be named for a pixel dimension, which
  is a product-wide decision about the field table.
- **a MARKET / locale key** — same objection, plus it collides head-on with whatever key
  `creative.translation-project` would want for the same token. Two template rows minting two
  variants of one key is exactly the overnight failure mode.

Both are recorded as NJ-ADCAMP-1 instead, so R1c adjudicates one key for the family.

Two **work-type values** are proposed (values, not fields, not nodes): `media plan` and
`in-situ proof of placement`. Both are recurring artifact classes the anchor's enum does not name
and neither is expressible as an existing value. Flagged as NJ-ADCAMP-3.

## Neighbours considered that did NOT get an edge

- **`creative.motion-graphics`** — real overlap on the animated banner set, but every discriminator
  I could write was already carried by the `creative.post-production` edge on the same fixture
  ladder. A third claimant on one file is worse than two.
- **`creative.graphic-design-project`** — the generic sibling. Deliberately no edge: if a general
  design project row collides with this one, the collision is with the *schema default*, and
  writing it would restate leg 1 of the node test as an edge.
- **`creative.self-initiated-work`** — a spec-built personal poster series. Rejected: the anchor
  already rules that absence of a counterparty *selects a template*, it does not deactivate the
  schema, and there is no shared discriminating evidence beyond that absence.
- **`career.consulting-client-engagement`** — declined in favour of `creative.client-engagement`,
  which is the same seam on the correct schema.
- **`code.software-project`** — an HTML5 banner build directory is real and does have a repository
  shape. Left out because the discriminating evidence (a build config, a package manifest) never
  competes with the grid; the `.html` extension is in `file_kinds` and nothing more.
- **`also_holds_with`** — empty **by contract**: rule 14 restricts it to schema rows. The genuine
  co-activation (a campaign asset that is also a career work sample) is written as a collision with
  a reciprocal discriminator, which is where a template's claim belongs.
- **`role_split`** — empty, and the most interesting refusal on the node. Four organisations sit in
  the same page footer playing four roles: advertiser, agency, media owner, licensor. That is a
  textbook role split and it cannot be written, because `role_split` points at different **field
  keys** and this schema declares none. Minting an advertiser/agency/publisher trio to solve one
  template row's problem is the move that produced thousands of private field names overnight. The
  consequence is carried by the brand-name `never_alone` rule instead — the strongest rule here.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All nineteen quoted spans of twenty-five characters or more were extracted mechanically and
  matched against `00` under whitespace and curly-quote normalization. Seventeen matched verbatim.
  One non-match is the extractor splitting on nested quotation marks (connective prose between two
  quoted spans, read by hand). The other was a phrase quoted from the **roster hint**, not from
  `00`; it has been rewritten as unquoted prose with the attribution stated inline, so no span in
  quote marks in this node is attributed to `00` without matching it. **No `00` quotation here is
  fabricated or paraphrased inside quote marks.** Note that `Existing curated folders and
  user-entered labels…` matches under apostrophe normalization only — `00` uses a curly apostrophe
  in "user's".
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12); every entry in
  `file_kinds.source_types` likewise (11/11).
- Every `collides_with.domain` is a roster id (12/12); every `falls_through_to.residual_template`
  and every `falls_through_if_inactive` is one of §7.3's nine residual names.
- `fields`, `proposed_fields`, `also_holds_with` and `role_split` are all empty, each with a note
  stating why rather than left bare.
- No numeric threshold, score or evidence count appears. Digits present are pixel dimensions and
  durations inside fixture names, and years inside fixture names.
- No handling class assigned; `sensitivity` is `potentially_sensitive` only; `is_safety_domain` not
  claimed.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-ADCAMP-1 — the placement/market key, and who is allowed to mint it.** The two strings this
  material is saturated with (an ad-unit placement, a market/locale) have no canonical key and this
  row refused to propose one. Three answers, three different products: (a) no key — the grid stays
  *detection* evidence and never becomes a folder level, which is what the row recommends today and
  what keeps a directory from being named `300x250`; (b) one shared key minted on the schema
  anchor, adjudicated once for `creative.ad-campaign`, `creative.translation-project`,
  `creative.deliverable-handoff` and `creative.print-production` together; (c) per-row keys, which
  guarantees two spellings of one idea. **Recorded, not resolved. Nothing was minted.** This is
  also a decision the schema anchor must make, and a template row may not edit the anchor — the two
  should be updated together.
- **NJ-ADCAMP-2 — four of the twelve boundaries are one-way.** `creative.deliverable-handoff`,
  `creative.creative-brief`, `creative.revision-round` and `creative.client-engagement` have no
  node files yet, so their halves of the reciprocal boundaries above are authored from this side
  alone. Each names the fixture the far side must agree on. If any of the four lands with a
  different discriminator, this row's edge must be re-cut — for R1c, not silently.
- **NJ-ADCAMP-3 — two proposed work-type values.** `media plan` and `in-situ proof of placement`
  are proposed for the creative schema anchor's `work_types` enum. Values, not fields, not nodes.
  If R1c declines them, the two fixtures that rely on them lose nothing structural — the values are
  vocabulary, not evidence — but the memo should be corrected rather than left claiming them.
- **NJ-ADCAMP-4 — which residual owns the talent usage grant.** `Protected Records` fits because
  the third-party identity is the load-bearing fact; `Independent Records` fits because a signed
  standalone grant has a durable purpose and no group. The row states a preference (Protected
  Records, because a protection outcome must not wait on an unresolved campaign question) and
  routes the campaign-attached copy accordingly. Confirm, or invert. This is the same shape as
  NJ-CRYPTO-2 and the two should probably be answered by one rule rather than two.
