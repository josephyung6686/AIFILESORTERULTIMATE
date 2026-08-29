# `photos.messenger-export` — lab notes (R1b)

Date: 2026-08-22
Kind: `template` · `schema_id: photos` · `launch: placeholder` · `provenance: proposal`
Verdict: **built, not refused.** The node test passes on all three limbs (detection signals,
privacy rules, dimensions) and the reasoning is recorded in the node's `node_test_note`.

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority. **Every span in
  quote marks in the node file and in these notes was grep-verified against this file before it
  was written**, in two batches of 41 and 13 candidate quotations. One candidate
  ("The system should not force every branch to use the full template…") came back MISS and was
  dropped rather than paraphrased inside quote marks.
- `planning/01-product-design-structured.md` — section locators only (2.5 Archives, 2.6 Images,
  2.7 OCR, 2.9 Format coverage beyond the core four, 3.11 Domain-scoped schemas, 5.7 The template
  library, 7.3 The initial library, 8.4–8.5 privacy). No section number is asserted as `00`'s own.
- `planning/domains/_CONTRACT.md` — rules 5 (sensitivity is `00`'s phrase only), 6
  (`{"residual_template": …}` for residual fallthrough, which is the form used here), 8, 10–15.
- `planning/domains/CONNECTION.md` — sections 2 (node test), 3 (templates reference, never copy),
  5 (closed edge vocabulary; `also_holds_with` joins **schemas only**), 6 (canonical field list),
  7. Present and binding; no disagreement with the dispatch prompt was found.
- `planning/prompts/ALIGNMENT.md` — the two roster kinds; work types are values.
- `planning/domains/roster.json` — id, kind, `schema_id: photos`, `must_consider_neighbors:
  ["identity"]`, `must_consider_residuals: ["Protected Records", "One-Off Images"]` confirmed.
  Every edge target below was checked against the roster's 83 ids.
- `planning/domains/canonical_fields.json` — six photos keys plus the seven universals. **No key
  was minted and `proposed_fields` is empty** (see below).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all seven used here are members, and all
  thirteen `file_examples[].source_type` values were checked mechanically.
- Landed neighbours read for alignment, not rewritten: `photos.json` (the schema),
  `photos.camera-events.json`, `identity.json`. `photos.social-media-export.json` had **not
  landed** when this node was written — its collision is authored one-way from this side and is
  R1c's to reciprocate.
- `planning/deferred-catalogues/04-camera-filename-patterns.json` and
  `07-archive-recognizable-markers.md` — consumed, not extended. See the catalogue-gap note.

## Why this node was not refused

The refuse test asks whether detection signals, dimension order **and** privacy rules are all
identical to the schema's default template. Here none of the three is.

- **Signals.** The photos schema and `photos.camera-events` run on camera EXIF. This situation's
  material has no EXIF, by construction: `00` states the mechanism — "Messaging platforms and
  downloaded web images often strip metadata from real photographs" — and lists it in its own
  adversarial suite as "stripped EXIF on messaging-app photographs". The evidence is therefore
  somewhere else entirely: an export layout read from an archive manifest, catalogue 04's
  messaging filename family, a per-message transcript or JSON sidecar, a `.vcf` member, a
  voice-note container. None of those appears on any sibling except as a `never_alone` trap.
- **Privacy.** Every other photos template holds the holder's own captures. This one holds other
  people's words and other people's identities. `00` names the material ("private
  correspondence"), gives the handling rule for its nearest extractor sibling ("while treating
  addresses and message content as potentially sensitive"), and settles the contact half outright
  ("should normally be privacy-protected rather than used to create folder proposals").
- **Dimensions.** One level where the schema default has two, with the `event` level dropped on
  evidence. See the next section.

The temptation was to refuse this as "the schema's default with different file extensions" —
which the prompt names as a non-node. It is not: extensions are `SOURCE_TYPES`, but a transcript
sidecar, a manifest layout and a stripped-metadata regime are evidence shapes, not formats.

## The dimension decision, and the one it refused to make

Recommended: `["capture_year"]`, one level, `time_first: true` trivially.

Two candidate orders were worked and rejected.

1. **`["media_type", "capture_year"]`, time-first false.** Genuinely attractive: it expresses the
   split this situation actually has (whole bundles versus loose shared media), and `00`'s own
   general rule would support putting function before time here, since a conversation archive
   behaves like a record domain — "putting year first scatters related work across calendar
   folders". **Rejected because it would settle a question the schema row referred upward.**
   `photos.json`'s `open_question` reads, in part: may `media_type` open a folder level in the
   default template? It records that as Joseph's, because `00` gives no sentence for it. A
   template may not answer a question its own schema deferred to the user. This was the closest
   call in the node.
2. **`["capture_year", "event"]`, the schema default unchanged.** Rejected on the canonical role
   of `event` — "the named occasion, trip, or gathering a capture or record belongs to". A
   conversation archive has a *span*, not an occasion, so the level would stand empty for the
   bundle population. `event` survives in the node as an **optional** dimension for loose shared
   media that independently join an accepted photo event, never derived from the thread.

The residue is stated rather than hidden: `capture_year` is honest for loose shared media and is
**not** assertable for a multi-year conversation archive, which should stay whole as one archive
family at the branch root or under a scoped `General`. That, plus `00`'s "remain mostly flat"
option for photo branches and its flattening rule, is why the recommendation is short. Depth was
not manufactured to make the row look substantial.

## Files considered and rejected

Thirteen file examples were written. These were considered and left out:

- **`msgstore.db` / `ChatStorage.sqlite`** (the app's own live database). Real, and common on a
  backed-up phone — but `00` sends databases and unknown binaries to "safe metadata-only indexing
  unless a dedicated extractor has been explicitly approved". Including it would have implied an
  extractor this product has not approved. It belongs to *Unsupported or Encrypted* and needs no
  fixture here to say so.
- **An `.eml` / `.mbox` mail archive.** Tempting, because `00`'s email sentence is the closest
  thing in the design to a specification for this material. Left out deliberately: `email` is a
  `SOURCE_TYPE`, not a domain, and dragging mail into a photos template would be the
  format-as-schema bug in reverse. The email sentence is cited as a *handling* precedent for
  message content, never as a claim that mail is this node's material. It is raised properly in
  `open_question` as the correspondence-schema fork.
- **A group-chat export with a shared album.** It adds no evidence shape the single-thread bundle
  does not already carry, and it would have inflated the example count without testing anything.
- **A forwarded meme / sticker pack.** Real, but it is `Reference Clips` or `One-Off Images`
  material the moment it leaves the bundle, and its only distinguishing signal would have been
  content, which is `needs_llm` and already covered.
- **A chat screenshot with unreadable OCR.** Covered by the schema row's own `IMG_4821.png`
  fixture and by the screenshot sibling; repeating it here would have been a borrowed fixture.

The thirteen that were kept deliberately cover the prompt's ugly cases: a labelled structured
sidecar (`result.json`) against unlabelled prose (`_chat.txt`); an OCR/screenshot of the same
thing (`Screenshot 2026-05-02 at 21.10.04.png`, the collision fixture); an archive packet read by
manifest only (`WhatsApp Chat with Mom.zip`); a contacts file (`Contacts.vcf`); a file that looks
like mine and is a neighbour's (`takeout-20260118.zip`); a file that is also another domain
(`IMG-20260502-WA0011.jpg`, `also_schema: identity`); and an unreadable one
(`chat-backup-2026.zip`).

## `proposed_fields` — empty, and why

Two keys were drafted and both were refused. The refusals are recorded on the node in
`proposed_fields_note` so R1c does not have to reconstruct them.

- **`correspondent` / `conversation`.** This is the field the material screams for. Refused
  because `00` answers it twice in the other direction — "It should avoid using authorship or
  creator identity as a destination dimension" and "A folder should not become a collection point
  for everything produced by the same person or organization" — and because the *search*-side
  need is already met by the schema's `people`, whose canonical row is seeded
  `destination_eligible: false` for exactly this reason. Minting a second person-shaped key
  would be the 574's failure mode with a privacy justification pinned to it. The tension is real
  and is `open_question` #1, for Joseph.
- **`platform`.** Refused as a routing signal rather than a meaning — `00`: "treat the file
  extension as a routing signal rather than an assumption about meaning" — with the universal
  `file_type` already holding the format family. The platform belongs in the observation
  (catalogue 04's pattern id, the manifest layout), never in a fact field and never in a folder
  level.

`capture_date` was **not** re-proposed: `photos.camera-events` already proposes it with a full
justification, and duplicating a proposal is how two spellings of one key get born.

## Neighbours considered that did **not** get an edge

- **`photos.camera-events`** — the obvious candidate, since the stripped WhatsApp photograph is
  one of *its* `never_alone` fixtures. No edge, and the landed neighbour's research file says why
  from the other side: a loose re-encoded JPEG in Downloads is not an export, and that node
  handles the file as an absent-EXIF trap rather than as contested material. The evidence-item
  mutex `collides_with` requires does not exist — my discriminator (an export layout) is simply
  absent on their fixture. Writing the edge would have been `collides_with` meaning "these are
  similar", which CONNECTION section 9 lists as a named failure. The trap is instead stated as
  this node's first `never_alone`.
- **`photos.family-archive`** — also produces EXIF-less JPEGs. Same reasoning, and that node's
  own research file already records the refusal from its side. Agreed, no edge.
- **`travel.trip-photos`** — a thread full of holiday photos looks like a trip. Rejected: the
  trip discriminator is a GPS cluster away from routine, and GPS is the first thing a platform
  strips, so no single evidence item can support both readings.
- **`legal.personal-legal-matters`** — a chat thread with a landlord, with a lease attached, is a
  real file. Rejected as an edge: the discriminating evidence (a signed agreement) sits in the
  attachment, not in the conversation, so it is the attachment that would activate legal, not a
  contest between this template and that one. It is carried as a `needs_llm` line instead.
- **`identity` (the schema)** — named in `must_consider_neighbors`, and it is the sharpest real
  hazard here. It gets **no** `collides_with`, because CONNECTION section 5 makes
  `collides_with` same-kind only and this is a template row. The edge is written to
  `identity.core-documents` (a template) instead, matching what `photos.camera-events` did, and
  the schema-level relationship is carried as `also_schema: "identity"` on the
  `IMG-20260502-WA0011.jpg` fixture.
- **`also_holds_with` is empty on purpose** — it joins schemas only. The photos↔identity and
  photos↔medical relationships this situation meets are authored on the schema rows, where they
  belong.

Edges that *were* written, all one-way from this side pending R1c reciprocity:
`photos.social-media-export`, `photos.screenshot-captures`, `photos.home-video`,
`identity.core-documents`, `photos.scanned-documents`.

## Catalogue findings (consumed, not extended)

- **Catalogue 04 (`camera-filename-patterns`) has a `messaging` family and this node consumes
  it**: `fnp-whatsapp-img`, `fnp-whatsapp-vid`, `fnp-signal`. The catalogue's own rationale is the
  boundary this node keeps — the pattern reports that a file *arrived through a messenger* and
  says nothing about what the content is. Its `unc-telegram-instagram` row is still in the
  uncertain list ("One real exported file each would settle them"), so this node cites the
  Telegram export layout structurally (labelled JSON keys, sibling media folders) and writes no
  pattern.
- **Catalogue 07 (`archive-recognizable-markers`) has no row that would fire on a chat export**,
  and this is by that catalogue's own design: its rule 4 stops the `document name` vocabulary at
  `00`'s five packet names (transcript, personal statement, resume, certificate, form) precisely
  so the archive side does not seed a general document-type vocabulary by accident. So the
  headline deterministic signal in this node — a transcript member beside media members — has
  **no catalogue row today**. That is recorded as a gap in the node's `open_question` and here;
  it is R2's/R5's to settle with evidence. No marker string and no regex was invented.

## NEEDS-JOSEPH — this node only

1. **The correspondent dimension.** Every real person who keeps chat exports keeps them per
   person, and that is the one dimension `00` forbids ("It should avoid using authorship or
   creator identity as a destination dimension"; "A folder should not become a collection point
   for everything produced by the same person or organization"). Either the rule holds and this
   branch stays shallow and time-keyed as recommended, or correspondence is a deliberate
   exception Joseph carves. The same fork governs whether the schema's `people` field ever
   becomes destination-eligible — `canonical_fields.json` already flags that as his call.
2. **Does correspondence belong on the `photos` schema at all?** The roster puts it here because
   the embedded media are captures. But a transcript is a text record with senders, timestamps
   and a thread identity — the shape `00` describes when it specifies email extraction — and
   `email` is a `SOURCE_TYPE`, not a domain, so there is no correspondence schema to point at.
   If Joseph adds one, this template *moves* rather than being rewritten, and the embedded media
   stay dual under `photos`.
3. **The R1c reciprocity list above.** One update after writing: `photos.social-media-export`
   landed mid-session and **does** carry the reciprocal edge to this node, with a compatible
   discriminator (per-media sidecars keyed to a media filename there, conversation transcripts
   with participants and attachment references here) and the same asymmetry — where the reading
   is uncertain, the correspondence side's protective rules apply first. That pair needs no R1c
   repair. The other four edges are still one-way from this side.
   **A divergence R1c should look at, not a defect in either row:** that sibling puts `media_type`
   in its `dimension_order` while this row declined to, on the grounds that `photos.json` records
   the media_type-as-a-folder-level question as Joseph's. Two templates on one schema now answer
   that question differently. Both are defensible for their own material; whether the schema
   default should move is still Joseph's.
4. **`role_split` was left empty after looking.** A transcript names a sender and a recipient —
   one entity type, two roles, which is exactly `00`'s test ("The system must separate roles that
   happen to contain the same entity type"). It was not authored because the canonical list holds
   no such pair, minting one is R1a's and Joseph's, and both halves would be
   destination-ineligible the moment they existed. Flagged rather than resolved.
