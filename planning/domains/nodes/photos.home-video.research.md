# `photos.home-video` — R1b lab notes

Roster row: `kind: template`, `schema_id: photos`, `launch: placeholder`, `provenance: inference`.
Output: [`photos.home-video.json`](photos.home-video.json). **Not refused** — see the node test below.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every span this node puts inside
  quote marks was grep-verified against this file before it was written; the check was re-run
  mechanically over the finished JSON (extract every `"…"` span from every string, membership-test
  against `00`). One bracketed alteration —
  `appear[s] to be reading material but ha[s] no…` — was caught by that pass and rewritten to
  `00`'s own wording. Nothing else failed.
- `planning/01-product-design-structured.md` — §2.9 only (the audio/video bullet and the format
  coverage list). `00` wins and nothing here depends on 01's numbering.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (fixture 5, the
  `.ics` case, which is why a calendar file appears in this row's file list as a *not-mine* fixture
  rather than as a claimed format).
- `planning/domains/roster.json` — confirmed the id, kind, `schema_id`, `must_consider_neighbors`
  (`medical`), `must_consider_residuals` (One-Off Images, Review Later), `file_kind_owner`
  (`audio_video`).
- `planning/domains/canonical_fields.json` — the six photos keys are referenced, none copied, none
  respelled, no destination flag widened.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` membership for every file example;
  `ZONES` contains `transcript`, which is where an authorized speech-to-text run lands and is why
  the caption-vs-transcript split below is expressible rather than notional.
- `planning/domains/nodes/photos.json`, `photos.camera-events.json`, `photos.family-archive.json`
  — read to align edges, not rewritten. Two collisions on this row are reciprocals of edges those
  rows already carry.
- `planning/deferred-catalogues/04-camera-filename-patterns.json` — consumed by row id only
  (`fnp-android-vid`, `fnp-dcf-mov`, `fnp-gopro-gopr`, `fnp-gopro-chaptered`, `fnp-whatsapp-vid`,
  `fnp-macos-screen-recording`, `fnp-android-mvimg`). No regex is reproduced here and no pattern is
  invented; the catalogue's own grade rule (one observation at the filename zone, `possible`, **no
  signal tier**) is carried across verbatim in meaning.

---

## The node test, applied before anything was written

The refusal condition for a template is that detection signals, dimension order **and** privacy
rules all match the schema's default. Two of the three differ here, and the third does not, and the
row says so rather than manufacturing a difference.

- **Detection signals — the row's strongest limb.** Every other template on the photos schema is
  fed by image evidence: EXIF slots, pixel dimensions, PNG format, known display resolutions,
  perceptual hashes. None of it exists on this material. A voice memo has no pixels at all, and a
  home movie's capture time lives in a container tag, not in `DateTimeOriginal`. The whole signal
  set — container/codec/duration/creation-time, embedded tags, an already-present caption track,
  chaptered-recording families — appears on no sibling.
- **Privacy — the sharper limb.** `00` gates exactly one extraction step in the audio/video
  sentence and gates nothing an image sibling does: transcripts run *only under an explicit privacy
  and compute policy*. Continuous recorded speech also captures people who are not the holder. That
  is a second privacy regime, not a narrowing of the schema's.
- **Dimensions — earns nothing, and is recorded as earning nothing.** `capture_year → event` is
  the schema default and `photos.camera-events`' order too. `00` states one order for
  capture-based media and this is capture-based media. Inventing a different order to justify the
  row would have been the padding failure; the duplication is logged in `open_question` as the same
  R1c fork `photos.camera-events` already left open.

**The finding worth carrying forward:** the roster line *Owns the audio_video family* is
**SOURCE_TYPE ownership, not situation ownership**. A macOS screen recording is `audio_video` by
container and belongs to `photos.screenshot-captures` by organizational situation. That is why
this row carries a `collides_with` to the screenshot sibling rather than silently absorbing every
`.mov` in the corpus, and why `file_kinds` on this row is not a claim on every file that routes to
the audio/video extractor.

---

## Files considered and rejected

Fourteen made the list. These did not:

| Considered | Why it is not on the list |
|---|---|
| `voice-memos-export.zip`, a platform bundle of recordings | The manifest-layout discriminator is `photos.social-media-export`'s whole reason to exist. Duplicating its fixture here would put the same evidence item on two rows without a discriminator between them. |
| A ripped DVD / `VIDEO_TS` folder | It is a directory structure, not a file, and the useful signal is a folder marker. `00`'s preserve-existing-structure rule already covers it and no fact of this schema attaches. |
| A `.aae` edit sidecar | Already `photos.camera-events`' fixture, and it is a still-editing artifact. |
| A `.wav` field recording made for a research project | The disjoint-evidence pair (capture facts + project facts) is real, but `also_holds_with` joins schemas only, and the `photos ↔ research` pair is already authored on `photos.json`. Adding a fourteenth fixture to restate a schema-level edge added length, not information. |
| A recorded job interview | The tempting `career.recruiting` collision — see the neighbours table. |
| A DRM-protected purchased film | Collapses into the same finding as `podcast_ep_142.mp3` (consumed media, publisher tags) plus the same finding as the unparseable container. Two fixtures already carry both. |
| An email with a recording attached (`.eml`) | The attachment name is `email`-family evidence about a *different* file. This row would have to claim a source type it does not own to say anything, which is the format-as-schema bug. |

The one file that decided the shape of the row is **`podcast_ep_142.mp3`**. It presents exactly the
container, codec and duration a forty-minute home movie presents. Nothing deterministic separates
them except a publisher-shaped tag set — and when the tags are stripped, nothing separates them at
all. That is the `never_alone` this row most needed and the reason `needs_llm` leads with
*made-versus-consumed* rather than with event naming.

---

## `proposed_fields` justification

**One proposed: `duration`.** `00` names it first in the audio/video sentence and the canonical
list has no key for it. It is not `media_type` (a home movie and a podcast episode share that
value), not `capture_year`, and not a universal fact. Two reasons specific to this situation make
it a stored fact rather than loose evidence: an Apple motion-still sidecar and a standing home
movie share a container, a stem family and a capture second, and duration is what separates the
fragment from the recording; and a shelf of recordings is unsearchable without it, which is what
`00` reserves the non-dimension fields for. Ceiling `direct` (labelled container slot),
`destination_eligible: false` deliberately — a continuous value would produce either one child or
very many tiny ones, both of which `00` asks the tree to warn about. No dimension on this row
branches on it. **Proposed for R1c; nothing was written into `canonical_fields.json`.**

**`capture_date` — concurrence, not a second proposal.** `photos.camera-events` proposed it with a
strong `00` citation. This row needs the identical fact for the identical reason (the container
creation-time tag is day- and second-grained exactly as `DateTimeOriginal` is), so re-proposing it
would put one concept in front of R1c twice. Recorded as concurrence in the JSON's
`why_no_existing_key_works` and here, not as a row.

**What was deliberately not proposed:** a `transcript` field (an authorized transcript is *evidence*
at the `transcript` zone, not a fact, and P4/P6 already hold the shape); a `codec` or `container`
field (routing signals, and `00` is explicit that format is not meaning); a `recorded_by` field
(the recorder-versus-recorded role split — see below).

---

## Neighbours considered that did **not** get an edge

| Neighbour | Why no edge |
|---|---|
| `career.recruiting` | A recorded interview looks like a collision and is not one. The evidence sets are disjoint — container facts on this side, recruiting language and an employer on that — so the honest edge would be `also_holds_with`, which joins **schemas only**. This is a template row, so it is carried on the `Lecture 08 recording.m4a`-shaped mechanism instead (`also_schema` on a fixture). Career fields are deferred anyway (D1 as narrowed / PR-6), so no field of that schema could be legitimised today. |
| `academic.coursework` | Same reasoning, and it *is* carried: `Lecture 08 recording.m4a` has `also_schema: "academic"`. Whether the `photos ↔ academic` pair should be authored on the schema rows is R1c's call across siblings, not one template's. |
| `photos.social-media-export` | Its discriminator is a takeout manifest layout, which this row has no signal for and does not want one. Non-overlapping evidence, so an edge would assert a confusion that does not occur. |
| `photos.scanned-documents` | A photographed page is image evidence end to end. Nothing in the audio/video signal set can be confused with it. |
| `photos.drone-captures` | Drone footage is `audio_video` and would activate this row's signals, but the sibling's own discriminator (flight-log, altitude and gimbal metadata) is one this row cannot read, and the failure is benign in one direction only — a drone clip filed as a recording loses nothing. `photos.camera-events` already carries the drone edge for the stills case. Left for R1c to decide whether the reciprocal belongs here; noted rather than authored, because an unreciprocated edge is a gate finding. |
| `identity.core-documents` | The image siblings collide with it because a phone photograph of a passport is a genuine capture. There is no audio analogue that this row's signals would misfile: a recording of someone reading a document number is not a document, and inventing the edge would be padding. `medical.personal-health-records` is different and **did** get an edge, because a recording made in a clinical setting is a real, common file. |
| `finance.*` | Considered for the recorded account call. Rejected for the same reason as identity: the signal that would identify it exists only inside speech, which is policy-gated, so this row cannot claim to discriminate it. The hazard is instead recorded where it is actionable — in `sensitivity_why` and in the `Protected Records` fallthrough. |

**`role_split`, checked rather than skipped.** The sharpest near-case in the whole photos schema
lives here: the person recording and the people recorded are one entity type in two roles, which is
`00`'s own test for a split. But `canonical_fields.json` holds no such pair — `people` is the only
person-key on the schema and is seeded destination-ineligible, and the recorder has no key beyond
`camera_information`. Minting the pair to fill the slot would invent a field relationship the
canonical list does not hold, and both keys would be destination-ineligible anyway under `00`'s
authorship rule. Left empty, recorded here for R1c.

---

## The distinction this node contributes

`00` puts two things in one sentence and separates them with a policy gate: *subtitles or captions
where present*, and — *only under an explicit privacy and compute policy* — *speech-to-text
transcripts*. A caption track already inside the container was authored by whoever made the file
and is readable text evidence with no gate. A transcript is generated by this product from
someone's voice and is gated. Collapsing the two would let a recognition rule read speech that was
never authorized. The row keeps them apart in `recognition.deterministic` (caption tracks) and in
`never_alone` (*an assumed transcript* — no rule may be written as though the words were
available), and the `medical` collision inherits the consequence: the discriminating evidence for
that pair is frequently unavailable **by design**, so abstention is the correct outcome rather than
a guess in either direction.

---

## NEEDS-JOSEPH — this node only

1. **No residual home exists for a standalone recording.** None of `00`'s nine is written for one:
   *One-Off Images* says images, *Temporary Screenshots* says screenshots, *Reference Clips* is
   scoped to saved visual inspiration and short captures. An isolated home movie or voice memo
   therefore has no exact home, and this row routes it to *Review Later* — a real fit for `00`'s
   "partly understood", but a queue rather than a destination, so a shelf of them never settles.
   `00` leaves the door open ("the library must support user-defined residual areas") without
   naming one. **Fork:** does R3 stretch *One-Off Images* to cover recordings, or is a tenth
   residual name proposed? This one has a consumer waiting (R3) and is the most actionable of the
   three.
2. **Whether `media_type` should open a level here** — separating audio recordings from video at
   the top. Every real shelf of this material mixes voice memos with home movies, and a user who
   wants them apart wants it first. But `00`'s Photos menu offers only year, event, location or
   flat, and a level nobody asked for is the one `00` warns about. A decision about someone's real
   filesystem; not taken.
3. **The duplicated `dimension_order`** (R1c, not Joseph, unless R1c escalates): this row and
   `photos.camera-events` both carry the schema default because `00` states one order for
   capture-based media. Either both keep it and the schema default is read as pointing at the
   camera-roll case, or the orders are consolidated and each row keeps only its detection signals
   and privacy rules.

Nothing else on this row is undecidable. No numeric threshold, no confidence score, no handling
class, and no folder path appears anywhere in the JSON.
