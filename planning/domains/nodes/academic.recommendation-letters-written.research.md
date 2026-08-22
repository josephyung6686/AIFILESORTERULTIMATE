# academic.recommendation-letters-written — lab notes (R1b)

Date: 2026-08-22
Kind: `template` on `schema_id: academic`. Launch `placeholder`. Provenance `proposal` —
`00` never names this organizational situation; it names **"recommendation form"** only as a
member of an application packet's record list, which is the *received* side, not this one.
`design_cite: null` is therefore correct and deliberate.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Authority. Every quoted span in
  the node JSON was grep-verified against this file **before** it was written, and re-verified
  mechanically after (walk every string, extract every `"…"` segment, assert membership). Zero
  failures at the end; one span initially failed on a trailing period (`…conflicting target
  institution.`) and was corrected to end the quote before the comma that `00` actually has.
- `planning/domains/_CONTRACT.md` — entry shape, rules 8/11–15.
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — both present and binding. Fixture
  7 (teaching vs taking, one schema, split by template) is the direct precedent for this row.
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed id, kind, schema_id, neighbours, and every edge
  target below is a real roster `domain_id`.
- `planning/domains/canonical_fields.json` — both dimensions (`term`, `work_type`) resolve to
  canonical keys and are `destination_eligible: true`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked against every `file_examples`
  entry and the `file_kinds` list.
- Landed neighbour `planning/domains/nodes/academic.teaching.json` — it already carries
  `collides_with: academic.recommendation-letters-written`; this node reciprocates with a
  compatible signal and does not rewrite theirs. Its fixture
  `Recommendation - J Ruiz - Columbia.docx` is reused here deliberately so the two nodes describe
  the same file consistently: teaching lists it as *not* teaching material, this node lists it as
  the canonical member and adds `work_type`.
- `planning/domains/nodes/college_applications.json` and `career.json` — checked for stance.
  `college_applications` already lists `letter of recommendation form` among its
  `application_document_type` values, which is the received side and confirms the split the
  roster hint asserts. `career` declares **no field rows** (D1 as narrowed / PR-6), so the
  `also_schema: "career"` on the EY-internship example legitimises the universal facts only today.
- `01-product-design-structured.md` — not read beyond confirming it is the numbered rendering;
  nothing in this node needed a locator that `00` did not carry directly.
- `planning/deferred-catalogues/` — **not consumed**. Recognition here needs no citation ids and
  no camera patterns. The gazetteers this node leans on (schools, orgs) already exist as
  `gazetteer` markers on the canonical rows; no gazetteer contents and no regexes were invented
  (R4/R2 boundaries respected). The one rule family named — word-boundary matching plus positional
  weighting plus a user-confirmed holder identity — is named as a family, never as a pattern.

## Node test — why this is a node and not padding

Refuse if detection signals, dimension order **and** privacy rules are all identical to the
schema's default template (`academic.coursework`: school → term → subject → work_type). All three
differ, and two of them differ structurally rather than cosmetically:

1. **Detection signals.** Coursework fires on a course-code-shaped token plus `00`'s academic
   context terms on an artifact addressed to a cohort. This node fires on a committee-addressed
   salutation plus one named third-party subject plus a signature block resolving to the corpus
   holder. Nothing in the coursework signal set can produce this node's central discrimination —
   *who signed it relative to the holder* — and nothing in this node's signal set is a course
   artifact.
2. **Privacy rules.** Coursework files are about the holder. Every substantive file here is about
   someone else, evaluative, and frequently confidential (waived-right letters). That is a
   different privacy posture, not a different topic, and it is the difference the roster hint
   itself names.
3. **Dimension order.** `["term", "work_type"]` against the schema default's four levels, with
   `school` and `subject` deliberately dropped for reasons recorded in `template.why`.

The failure mode the node test guards against — "the only difference is work types or file
extensions" — does not apply: `recommendation letter` is a **value** of `work_type` and appears
in `work_types[]`, not as a node; the extension list is illustrative and `file_kinds.never_alone`
is true.

## Files considered and rejected

- **`FERPA waiver - J Ruiz.pdf`** (the applicant's signed confidentiality waiver). Rejected as a
  file example although `waiver form` stays in `work_types[]`: the signed waiver is a document the
  *applicant* executes and the *institution* holds, and in a recommender's corpus it usually
  arrives as a portal line rather than a file. The portal screenshot example already carries the
  waived-right observation, which is where the evidence actually lands.
- **A `.ics` "Letter deadline — Chen" reminder.** Rejected. A calendar item with a person name and
  a deadline is exactly `CONNECTION-EXAMPLES` fixture 5's trap: `source_type = calendar` is
  `file_kind_plausible` only, and the SUMMARY would carry no letter term, no salutation and no
  signer. It would activate nothing, so including it would have been padding a source-type count.
  `calendar` is therefore **absent** from `file_kinds.source_types` for this node, unlike teaching
  (where an ORGANIZER-anchored office-hours invite genuinely fires).
- **A student's CV/transcript as its own example.** Folded into the mail item and into
  `work_types` as `applicant materials received` rather than given a row, because as loose files
  they carry no evidence tying them to this situation and would fall to residual on their own.
- **`Contacts export.vcf` of past applicants.** Rejected outright: `00` requires contact data
  "should normally be privacy-protected rather than used to create folder proposals", and
  `contacts` as a source type here would be a privacy hazard with no organizational payoff. It
  survives only as a `never_alone` entry (a spreadsheet of person-name rows is an address book
  until a letter term appears).
- **A blank recommender form the holder was sent but never filled.** Rejected as a separate row;
  it is covered by the `never_alone` line about a recommendation token in a filename, which is the
  tempting-false-file requirement.

## proposed_fields — none, and why that is the finding

`proposed_fields: []`. This node did **not** mint a key, and the omission is load-bearing enough
to be the node's `open_question`.

The dimension a human would reach for first in a letters corpus is *the person the letter is
about*. No canonical field carries that role: `people` exists but is a Photos field, is seeded
`destination_eligible: false`, and its own canonical row records that widening it is Joseph's
call; `instructor` is the wrong role and is not destination-eligible; `authored_by` is the writer,
not the subject, and `00` forbids it as a destination outright — "It should avoid using authorship
or creator identity as a destination dimension." Minting `letter_subject` or `applicant` here
would be the 574's defining failure reproduced for one node (a private key for one situation), and
even if minted it could not be a dimension until the **Academic schema row** declared it, which is
not this node's to do. A person-named folder level is also precisely the material this node marks
`potentially_sensitive`.

So the node accepts a shallower recommendation and records the fork. That is the honest output;
a two-level tree that admits what it cannot express beats a deep one built on an invented key.

## Dimension order — the tension, recorded rather than hidden

`00` gives two rules that pull opposite ways here:

- "For document and record domains, project, function, or subject usually comes before time
  because putting year first scatters related work across calendar folders."
- and the canvas warning against a level that "produces only one child, repeats a concept already
  expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

`work_type` is this situation's *function* dimension, so the first rule argues `work_type` first.
Against that: `work_type` here is dominated by one value (`recommendation letter`) and would put a
near-single-valued level at the top, while `term` splits the corpus into the batches a recommender
actually re-finds, and the "scatters related work" harm does not materialise — a letter, its
request mail and its portal record share a cycle rather than crossing it. Hence `term` first,
`work_type` second, with the reverse recorded in `template.why` as a legitimate user choice.

`time_first: false`. `term` is an academic-cycle fact from dedicated term patterns, not a capture
date; `00` reserves the time-first exception for capture-based media — "Photos and capture-based
media are the major exception: time often belongs first because capture date is a defining aspect
of the material." This matches the landed `academic.teaching` row, which also leads with `term`
and sets the flag false.

The termless members (the reusable letter template, a multi-cycle tracking sheet) are handled by
`00`'s scoped fallback, quoted in `template.why`, not by inventing a term.

## Neighbours considered that did NOT get an edge

- **`college_applications` and `career` (the schemas, both on `must_consider_neighbors`).** No
  edge from this row. `CONNECTION.md` §5 restricts `also_holds_with` to **schema ↔ schema** and
  `collides_with` to **same-kind pairs**, so a `kind: template` row may not author either against
  a schema id. Where the prompt's edge table implies otherwise, CONNECTION wins (noted as the
  prompt/CONNECTION divergence this node hit). The real join is expressed twice instead: as
  `collides_with` against those schemas' **template** rows, and as `also_schema` on the file
  examples (`college_applications` on the written letter, `career` on the EY-internship letter).
  Authoring `academic ↔ college_applications` as `also_holds_with` is the **academic schema row's**
  business, and `academic.json` already exists — this node does not touch it.
- **`applications.purpose-packet`.** Considered and dropped. A purpose-defined packet is a
  *received* collection; the confusion it creates with this node is already fully covered by the
  undergraduate and graduate packet edges, and a third near-identical signal would be noise.
- **`applications.scholarship-fellowship` / `applications.k12-admission`.** Same reasoning: real
  destinations for letters, identical discriminating evidence (who signed it), no new information
  in a fourth and fifth copy of the same signal.
- **`academic.transcripts-credentials`.** No edge. A transcript and a letter co-occur in a packet
  but never share evidence: a registrar document has no salutation and no signer-as-holder. `00`'s
  multi-membership point — "A transcript may be part of several application packets" — is about
  group membership, not about schema collision.
- **`academic.k12-schooling`.** No edge. A teacher's letter for a pupil is the same situation as
  this node, not a different one; the K-12 confusion that exists is with `academic.teaching`
  (rosters and gradebooks), and that edge lives on the teaching row already.
- **`identity` / `legal`.** No edge. Confidentiality is a sensitivity property, not an identity or
  legal domain activation. The privacy consequence is carried by `sensitivity` plus the
  `Protected Records` fallthrough, which is `00`'s own route.

## Fallthrough choices

`Protected Records` first (the letters and the third-party-data files), `Independent Records` for
the durable-but-ungrouped members (the reusable template, a one-off letter for someone outside any
cycle), `Review Later` for the sparse drafts and request mail whose meaning is partly understood.
`Temporary Screenshots` and `Reading Inbox` appear only at file-example level, where the portal
screenshot and the misread bibliography actually land — they are not this node's fallbacks.

## NEEDS-JOSEPH (this node only)

1. **No canonical field carries "the person a letter is about."** This node recommends *not*
   minting one and *not* widening `people`, and therefore recommends no person dimension. If
   Joseph wants letters filed per applicant, the route is a canonical-field decision plus an
   Academic schema-row change — never a private key on this template. (Copied into the node's
   `open_question`.)
2. **Does this whole situation default to a protected branch, or only its third-party-data
   members?** Protecting everything gates a recommender's ordinary drafts out of model review;
   protecting only some members makes protection depend on `work_type`, a fact that is itself only
   `validated`, and a letter named `letter final v3.docx` would slip past it. Joseph's call; the
   node asserts `potentially_sensitive` and no handling class (P7's vocabulary, untouched).
3. **Prompt vs CONNECTION divergence, recorded as instructed.** The dispatch prompt's edge table
   offers `also_holds_with` to a template row; `CONNECTION.md` §5 and `_CONTRACT.md` rule 14
   restrict it to schema ↔ schema. This node followed CONNECTION and left `also_holds_with` empty.
   R1c should confirm that the schema-level `academic ↔ college_applications` also-hold is
   authored on the schema rows, since two of this node's file examples depend on it being
   expressible.
