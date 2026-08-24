# construction_property.progress-photos — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

`00-database-agent-product-design.md` (quotations machine-verified verbatim), `ALIGNMENT.md`,
`_CONTRACT.md`, `CONNECTION.md` (§4's HEIC and no-EXIF worked files), `roster.json`,
`canonical_fields.json`, `DECISION-BRIEF.md` (J-IND, D1, PR-6), `ROSTER.md` §4 →
`13-trades-property-logistics.json` (line 910), `src/evidence_shape/vocabulary.py`. Neighbours read
in full before writing, as the dispatch brief required: `photos.json` (the schema and its six
fields), `photos.camera-events`, and the `photos.*` family listing (screenshot-captures,
scanned-documents, drone-captures, family-archive, home-video, social-media-export,
messenger-export).

## What it is for, and what it holds

Photographs that are the record. Interval capture sets of a site, before-and-after sequences,
pre-cover-up and pre-pour records, stamped and annotated frames from site-photo applications,
generated photo reports, video walkthroughs, and subcontractor-supplied image sets that arrive with
their EXIF stripped.

## Node test — passes, and the argument is about *evidence class*, not subject matter

The dispatch brief flagged this row twice: it collides with the landed `photos.*` family, and it may
be a `work_type` of `construction-project`. Both challenges are answered in the JSON, and the answer
is the same in both directions:

**Every other row on `construction_property` is recognised by document structure** — a header, a
reference, a table, a signature block. **This row is recognised by capture metadata, rhythm and
place.** That is a different detection method, and a `work_type` *value* cannot carry a different
detection method; only a template can. That is leg 1 of the node test and it is decisive.

Leg 2 (dimensions) and leg 3 (privacy) also hold: the row wants site → capture date and nothing
below, and site photography is incidental surveillance in a way a drawing is not.

**Against `photos.camera-events` specifically:** the two rows share a schema's worth of machinery
and are *not* in competition for the same file so much as for the same *bytes*. The discriminator
authored here is **repetition of place across time** — a camera roll visits many places once, a site
walk visits one place many times — plus subject matter and a work-hours rhythm. `photos` is named as
`also_schema` on the capture fixtures, because `00` is explicit that
"One file may hold facts from more than one domain without losing information."

## `time_first` — the one flag worth explaining

Set to **false**, which looks wrong for a capture-based row and is not. `00`'s rule is that for
document and record domains "project, function, or subject usually comes before time because putting
year first scatters related work across calendar folders." A site's photographic record is exactly
the thing a year-first tree destroys: the week-to-week comparison is the product. Time is the
**leaf** here, carrying the meaning, but it is not the root. `photos.camera-events` is the row where
time genuinely leads (it sets `time_first: true`), and this row is deliberately not that row.

## Legacy id absorbed (ROSTER.md §4)

`cons.progress-photos` (ROW), 1:1.

## Files considered and rejected

- **`IMG_2077.HEIC` (the lunch)** — kept, and it is the most important fixture in the row: same
  device, same day, same GPS cluster, and *every deterministic signal the row has is true of it*.
  It is why the `never_alone` list is as long as it is.
- **`IMG-20260311-WA0009.jpg`** — kept for the stripped-EXIF case, which `00` addresses directly.
- **`IMG_1148.HEIC`** — kept deliberately as a *shared* fixture with
  `construction_property.materials-delivery`, authored the same way on both rows so the pair reads
  consistently.
- **A 360 capture from a reality-capture platform** — rejected as too instrument-specific for gist depth.
- **A thermal-imaging survey image** — rejected: it is a survey instrument output and
  `construction_property.site-survey` is nearer.

## proposed_fields

**None.** PR-6 forbids field rows on this schema. Worth flagging for R1c without minting anything:
the `photos` schema already declares `capture_year`, `event`, `location`, `people`,
`camera_information` and `media_type`, and if this row ever needs fields the right move is almost
certainly to reuse those through the `photos` schema on a co-activated file, **not** to mint
construction-flavoured copies of them. Minting `site_capture_year` would be exactly the
one-concept-two-vocabularies failure `_CONTRACT` rule 8 documents.

## Neighbours considered that did NOT get an edge

- **`photos.screenshot-captures`** — screenshots of plans and messages are routed away via the
  `Temporary Screenshots` fallthrough rather than given a collision; the seam is thin.
- **`travel.*`** — a site visit away from home produces both kinds of capture on one phone; genuinely
  real, and too thin to author at gist depth.
- **`construction_property.building-control`** — inspection photographs, but the certificate row and
  the inspector's own record are that agent's to author.

## NEEDS-JOSEPH

- **NJ-CP-9 · Under the project, or beside it?** If this row is a template and the project is also a
  template, a user filing a job expects photographs *inside* it, not in a parallel photographs tree.
  The row cannot resolve this — it is `00`'s frozen-tree question — and it is recorded as the node's
  `open_question` too, so the tension is visible rather than quietly settled.
- **NJ-CP-10 · Faces and GPS on work photographs.** Site photography captures workers, neighbours and
  private homes at metre accuracy as a by-product. Whether work-context captures get the same
  protective posture as personal ones is a policy question that spans this row and the whole
  `photos` family; stated reciprocally so `photos.camera-events` and this row can be answered together.
