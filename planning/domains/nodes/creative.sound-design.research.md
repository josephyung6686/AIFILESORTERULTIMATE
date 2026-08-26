# creative.sound-design — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.sound-design.json`](creative.sound-design.json).
Salvage: none — no prior draft of either file existed.
Verdict: **node kept**, on a narrower ground than its name implies, with the strongest case against it
recorded as open_question item 1 rather than smoothed away.

## Sources actually used

- `RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py creative.sound-design`
  (`must_consider_neighbors: career, code, photos`; `must_consider_residuals: Independent Records,
  Review Later`).
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` only:
  the extractor paragraph, the dimension-ordering paragraph, the validator/abstention paragraph.
  Every phrase attributed to `00` was `grep -c -F`'d back out verbatim before it was written.
- `planning/domains/_CONTRACT.md` rule 14 (lines 168–186) — it decided two edges: `also_holds_with`
  **joins schemas only**, `collides_with` **joins same-kind pairs**.
- `planning/domains/nodes/creative.json` — the schema anchor, read for the **default template** this
  row is measured against, its recognition preconditions, its sensitivity reasons and NJ-R1a-1.
- `finance.crypto-assets.research.md` — the one landed launch row read for calibration, per the brief.
- Landed siblings read for boundary alignment, none edited: `creative.post-production.json`,
  `creative.music-session.json`, `creative.podcast-episode.json`, `creative.stock-asset-library.json`,
  plus a targeted grep of `creative.film-production.json`.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES`.

Not read, deliberately: `01-product-design-structured.md` (00 wins and 00 answered) and the anchors'
`.research.md` companions — the anchor JSON left nothing about the node test undecided.

## THE CHARGE — the strongest case that this row should not exist

I put the case at full strength before writing anything, because five of the seven disqualifying
shapes in the brief apply to this id on their face.

1. **It is a lifecycle stage.** `creative.post-production`'s own `one_line` reads: *"A bounded
   moving-image or audio production being assembled from referenced media through ingest, edit,
   review, grade or mix, master/export and approval."* "Mix" is in that list. Audio post is the
   audio branch of post. Under 00's parent-context rule — *"a parent dimension should provide the
   context required to understand the child. A work type such as Homework 3 is meaningful only after
   the course is known"* — `Reel 2 Predub FX v04` is meaningless without `Harbour Film`, which is the
   signature of a **child work_type value**, not of a node.
2. **It is a work_type value already in the enum.** The creative anchor's `work_types[]` already
   contains `"stem or take"`, `"cut or edit version"`, `"master"` and `"render"`. ALIGNMENT is
   explicit that work types are values of a field, never nodes.
3. **It is a medium.** If the only difference from post-production is that the bytes are `.wav`
   rather than `.mov`, that is a `SOURCE_TYPE` plus an extension — the brief's named non-node.
4. **It is a department name.** "Sound" is a crew department, exactly like "camera" or "grip". A
   department is an organisation-shaped label and therefore never-alone evidence that can never
   activate on its own.
5. **It duplicates two neighbours.** `creative.music-session` already holds DAW sessions, takes,
   stems, mix recalls and masters. `creative.stock-asset-library` already holds a sound library —
   `CityAmbience_TransitLoop_03.wav` is its own named fixture. Between them the audio corpus looks
   fully spoken for.
6. **It may duplicate its own default template.** creative's default is client-where-plural →
   project → stage → artifact_type, not time-first, `potentially_sensitive`. If this row recommends
   that and nothing else, it is the default template wearing an audio-coloured name.

That is a serious case, and (1) and (5) are the two I could not dismiss cheaply. What defeats it is
below; what it does **not** defeat is recorded as open_question item 1, which offers refusal as
option (c).

## Did this row survive the node test? — all three legs

CONNECTION's test: a template exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template.

### Leg 1 — detection signals: DIFFER, and this is the leg the row survives on

The creative default detects a linked-asset structure, a layer/artboard structure, a revision-round
family, a brief, a delivery set, production paperwork and a script. This row detects six structures
that appear on **none** of the landed audio-adjacent siblings' signal lists, verified by grep:
`foley`, `field recording`, `spotting`, `sound report` and `M&E` return **zero** substantive matches
in `creative.post-production.json` and `creative.film-production.json`; `.aaf` appears in both, but
only inside an extension list, and film-production's own never_alone already refuses it.

The six:

- **The broadcast-wave slot.** A `bext` chunk (Originator, OriginationDate, a `TimeReference`
  sample-count offset) plus an `iXML` block naming scene, slate, take, per-track names and a circled
  take. This is a *labelled structured slot*, so it is `direct`-reliability evidence in 00's sense,
  not a filename guess. A music bounce, a podcast edit and a purchased library MP3 do not carry it.
  This is the single most sound-specific machine-readable structure in the whole family.
- **The sound report** — the audio counterpart of the camera report, and one of the few strictly
  formatted documents in this world.
- **The spotting/cue list**, whose diagnostic is *tense*: a review note responds to an artefact that
  exists; a spotting row commissions one that does not. Post-production's fourth deterministic signal
  is explicitly the responding kind ("names the cut/session being reviewed and a later responding
  render or session"). These are different documents.
- **The conform handoff** (`.aaf`/`.omf`/`.edl` with departmental track groups), whose entire reason
  for existing is a department boundary crossing at picture lock.
- **The stem/M&E split set**, whose members are full-length, equal in duration and differ only by a
  departmental token — a delivery set that exists so the same picture can be *rebuilt in another
  territory*, a purpose no other creative sibling's delivery set has.
- **The self-recorded library shape** — a category-token filename grammar plus an embedded recordist
  and recording date, with no vendor, order or licence anywhere.

That answers charge (1): post-production detects the picture-side project apparatus; this row detects
a sound-side apparatus that post-production's five deterministic signals do not reach. It answers
charge (3) and (4) too: nothing above is an extension and nothing above is a department word — the
JSON's `never_alone` explicitly refuses both, including the word `sound` itself.

### Leg 2 — recommended dimensions: DIFFER, by splitting the default in two

The project-bound half takes the creative default **unchanged**, and this memo says so rather than
inventing a difference: the parent-context test puts the picture above the reel above the artefact,
exactly as the anchor prescribes.

The library half must **not** take it. A self-recorded ambience filed under the film it was first cut
into is destroyed as a reusable asset, because reuse across unrelated jobs is the only reason it was
kept. Its correct parent is the sound's own **category**. That is a genuine dimension-level departure
from a default that asserts one order for the whole family — and it is honest about its cost: the
key it needs does not exist (open_question 2), and no key is minted here.

The row also **declines a time-first exception it superficially qualifies for**. Field recordings are
capture-based, and 00 grants *"Photos and capture-based media are the major exception: time often
belongs first because capture date is a defining aspect of the material."* It is refused because a
rain recording is sought by weather and surface, never by the afternoon it happened — its defining
aspect is what it is a recording *of*. The anchor grants time-first to `creative.shoot-day-media` and
`creative.raw-photo-catalogue` by name and to nobody else; claiming it here would be claiming the
photos exception without the photos evidence. `time_first: false`.

### Leg 3 — privacy rules: DIFFER, by one reason the anchor does not carry

The anchor gives four reasons for `potentially_sensitive`: unpublished work, third-party identity in
releases and paperwork, source material, and client confidence. All four are inherited. This row adds
a fifth that is on no other creative sibling: **raw production audio is an inadvertent recording of
private speech** — a lav left open between takes, a recorder rolling before the slate. Unlike an
unpublished poster the harm is to a *person*, not to the work; and unlike a call sheet the exposure is
invisible in metadata and reachable only by listening or transcribing, which is precisely what 00
fences: *"Audio and video files should yield duration, container and codec metadata, creation time,
embedded tags, subtitles or captions where present, and—only under an explicit privacy and compute
policy—speech-to-text transcripts."* Against it, unchanged: *"Privacy policy must be enforced before
content reaches any model or external connector."*

No `is_safety_domain`, no handling class — that vocabulary is P7's.

**Verdict:** two legs differ substantively, one is honestly conceded. Node kept. Charge (6) fails.

## The collision fixtures

Two, both real files, both already named by a landed neighbour so the boundary is reciprocal on the
same bytes.

1. **`North Star_S04_Mix_Recall_03.pdf`** — the primary. It contains the word *Mix*, a channel list,
   per-channel processing settings and a version index: every surface feature of an audio-post
   document. It is `creative.music-session`'s, and that row states the claim against me directly:
   *"North Star_S04_Mix_Recall_03.pdf must not be claimed by sound design solely because it contains
   mix notes."* Accepted. **The discriminator:** it names a song, performers and take/playlist
   families, and carries no timecode against any picture and no cue, scene or reel reference. The
   reciprocal half, also that row's wording and also accepted: *"The same Harbour Film_Sound_Mix_05.aaf
   must remain sound-design/post-production evidence."*
2. **`CityAmbience_TransitLoop_03.wav`** — `creative.stock-asset-library`'s own fixture, and its
   filename grammar is indistinguishable from my `AMB_Rain_Gutter_Overflow_Heavy_02.wav`. **The
   discriminator is the apparatus around it, not the name:** an order confirmation, a vendor licence
   and a pack manifest naming the same product make it that row's governed inventory; a recordist and
   a recording date with no purchase record anywhere make it this row's. This is the seam I am least
   confident about, because that row's fifth deterministic signal reaches "a self-made component pack
   with a manifest, specimen or contact sheet" — flagged for R1c in the `collides_with` entry.

## Files considered and rejected

- **`Harbour Film_Edit_v12.prproj`** — carries the same production name and contains audio tracks.
  Rejected: it is `creative.post-production`'s picture timeline and its own named fixture. Every
  picture timeline has audio tracks; that is the edit's material, not a handoff. Encoded as a
  `never_alone` entry by name.
- **`Harbour Film_Delivery_QC.xlsx`** and **`Harbour Film_Rough Cut 03.mov`** — post-production's,
  same reasoning. Tempting because the production stem matches.
- **`North Star_S04_Stems_2026-07-18.zip`** — music-session's named fixture. Stems are not mine by
  extension or by the word *stem*; the departmental DX/MX/FX split against picture is.
- **`Ep114_Guest_Interview_RAW.wav`** — podcast. Speech-led, host/guest continuity, transcript and
  show notes. Rejected even though it is a multitrack with a mix.
- **A `.pkf`/`.sfk` peak-cache sidecar** — sits beside every session and looks like content. Rejected:
  a machine-generated derivative with no independent evidence. Recorded in the `.ptx` example's
  `must_not_conclude`.
- **A location or performer release form** — third-party identity, but the *instrument* is `legal`'s.
  Rule 14 forbids a template writing `also_holds_with`, so this is recorded here and in the
  sensitivity note rather than edged.
- **A stock-music invoice or a font invoice** — `finance`/`business_operations`, or the
  *Receipts and Confirmations* residual. The business of running the studio is not the making record.
- **`theme_loop.ogg` inside a game repository** — the repository root explains the folder, so `code`'s
  layout is preserved and nothing inside it is re-filed. Covered by the `creative.game-art-asset` edge.
- **`REC0031.WAV`** — kept as a *file example* precisely because it must be rejected: a device-default
  recorder name is the field-recorder analogue of an untitled camera file and belongs to no domain.

## Neighbours considered that did **not** get an edge

- **`career`, `code`, `photos`** — the three `must_consider_neighbors`, all **schemas**. Rule 14
  restricts `collides_with` to same-kind pairs and `also_holds_with` to schemas only, and the landed
  launch row `finance.crypto-assets` follows exactly that (template collisions only, empty
  `also_holds_with`). So all three are argued here and in `never_alone` instead of edged:
  *career* — a sound designer's reel and credit list is self-presentation, and a credit line naming a
  production can never activate this row; reciprocally this row never claims a reel merely because its
  members are mixes. *code* — a Wwise/FMOD or middleware repository under version control is explained
  by its manifest and layout, and this row proposes no re-filing inside a preserved repository root;
  reciprocally code must not claim a source library merely because a build consumes it. *photos* — a
  field recording carries device and time metadata exactly as a photograph does, and that alone is not
  a sound-design fact; reciprocally a personal recording never acquires a production because a
  professional recorder made it. **Recommendation to R1c:** if template↔schema collisions are in fact
  permitted, add `photos` and `code` here.
- **`creative.theatre-production`, `creative.exhibition`** — live and installation sound genuinely
  contain cue lists, and a QLab cue list is structurally close to a spotting list. No edge, because
  their anchor is a performance run or an installation rather than a picture version, and neither has
  landed to align against. Surfaced as open_question 3 rather than guessed.
- **`creative.screenplay`** — a script's action lines describe sounds. No edge: the element grammar is
  the screenplay's own signal, and a described sound in prose is not a cue at a timecode.
- **`creative.licensing-rights`** — a sync licence names a work and a grant. No edge from this row:
  the grant is that row's organizing situation, and the anchor already records the rights-key hole.

## proposed_fields

**Empty, deliberately.** This is a `launch: placeholder` template on a schema that declares no field
rows (D1 as narrowed, `_CONTRACT` rules 10/12/15, CONNECTION PR-6), so `fields: []` and the four
candidate keys (`project`, `stage`, `artifact_type`, `client`) are referenced as the anchor's pending
proposals rather than re-declared here — rule 12 forbids a template copying its schema's fields.

The one key this row would want, and does **not** propose, is a **sound-category** key for the library
half. It is not proposed because minting a key on a field-less placeholder is the 574's exact mistake
at the point of maximum temptation; it is recorded as open_question 2 for R1c, next to the anchor's
own rights-and-licence hole. `proposed_context_terms` is likewise empty: the design floor lists
academic terms only, and I will not pretend 00 listed a sound vocabulary.

## Sparse-file discipline

Three examples carry `group_without_copying_facts: true` and none of them writes a fact:
`Audio 1.wav` (may join the session's neighbourhood without acquiring a production, reel or cue),
`REC0031.WAV` (joins nothing), and `AMB_Rain_Gutter_Overflow_Heavy_02.wav` — the interesting one,
because it must be grouped with its category run while being actively *prevented* from inheriting the
production it was first used in. Activation ≠ grouping is load-bearing in both directions here.

## Audits run before returning

- `json.load` parses; key set diffed mechanically against `finance.crypto-assets.json` and
  `creative.post-production.json` — mine is a subset of both (their extras are the optional `*_note`
  keys and `proposed_context_terms`) and matches the assignment's canonical shape exactly.
- All 13 `file_examples.source_type` values and all 10 `file_kinds.source_types` are `SOURCE_TYPES`
  members. All six `collides_with` ids resolve in `roster.json`; `also_holds_with` empty per rule 14;
  all four `falls_through_to` names are among 00's nine residuals.
- Every `00` span was `grep -c -F`'d against 00 and returned 1: the audio/video extractor sentence,
  the archive-manifest clause, the extension-as-routing-signal clause, the parent-context sentence,
  the project-before-time sentence, the capture-exception sentence, the recommend-and-reverse
  sentence, the privacy-enforcement sentence, and all four residual definitions.
- No threshold number, no confidence score, no handling class, no `public_low`, no invented edge.
- `fields`, `proposed_fields` and `dimension_order` all empty by contract, recommendation held as prose.
- Files written: **only** `creative.sound-design.json` and this memo — no neighbour, roster,
  `canonical_fields.json`, `check.py`, `src/` or SPEC touched (CODEX works in the same directory).

## NEEDS-JOSEPH (this node only)

- **NJ-SD-1 — the post-production overlap.** `creative.post-production` claims "moving-image **or
  audio** production … edit, review, grade or **mix**", which makes this row's project-bound half
  arguably a stage value inside that row. Alternatives, spelled out in the JSON's `open_question`:
  (a) keep both, accepting that `Harbour Film_R1_AAF_v05.aaf` is post-production's output and this
  row's input; (b) fold the project-bound half into post-production and keep this row as the
  recording-and-library row only; (c) refuse this row and route to post-production / music-session /
  stock-asset-library, at the cost of losing the only coverage of self-recorded, unlicensed,
  uncatalogued field material. **This row recommends (a) and names (b) as second-best.**
- **NJ-SD-2 — post-production's `collides_with` is empty**, so this edge is currently one-directional.
  Adding the reciprocal is a **RECOMMENDATION to R1c**, not an edit I am permitted to make.
- **NJ-SD-3 — the library half's missing dimension.** A self-recorded library's correct parent is the
  sound's category; no canonical key holds it and `artifact_type` names the document rather than what
  a recording is *of*. No key proposed. Alternatives: mint one at R1c alongside the anchor's rights
  key, reuse `artifact_type` and accept the loss, or leave the library half dimensionless.
- **NJ-SD-4 — the self-recorded/purchased seam with `creative.stock-asset-library`.** That row's fifth
  deterministic signal reaches self-made component packs. Alternatives: keep acquisition-apparatus as
  the sole discriminator (current), or give that row purchased assets exclusively and this row all
  self-recorded material regardless of catalogue shape.
- **NJ-SD-5 — live and installation sound.** `creative.theatre-production` and `creative.exhibition`
  hold cue lists that are structurally close to spotting lists. Alternatives: reciprocal
  `collides_with` on the cue-list fixture, or a stated rule that live cueing is theirs and
  picture-locked cueing is this row's.
- **NJ-SD-6 — template↔schema edges.** Rule 14's same-kind restriction is why `photos`, `code` and
  `career` are argued but not edged here, while landed siblings such as
  `creative.podcast-episode.json` and `creative.motion-graphics.json` **do** carry schema ids in
  `collides_with`. The family is inconsistent; R1c should pick one reading and normalise. This row
  followed the contract and the launch row.
