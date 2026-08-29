# R1b lab notes — `college_applications` (kind: schema)

Date: 2026-08-22
Node: [`college_applications.json`](college_applications.json)
Verdict: **not refused.** `00` names the domain and its four fields outright, `purpose` lives only
here (PR-1), and `target_university` is the design's own role split from `school`. The field set is
genuinely distinct, so the node test passes on its first clause.

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; the authority for every quoted span
  in the node. Every quotation was grep-verified against this file **before** it was written, and
  re-verified mechanically afterwards (43 quoted spans, all matched; the one span in quote marks
  that was mine and not `00`'s was un-quoted rather than left ambiguous).
- `planning/01-product-design-structured.md` — read §3.8 (roles), §3.9 (purpose), §3.10 (narrow
  dates), §3.11 (domain-scoped schemas), §5.6 (Applications and purpose-defined packets), §5.7
  (template library). Used as a locator only; no § number appears in the node, because `00` has no
  numbered sections and `00` wins on any conflict.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
  `planning/domains/CONNECTION-EXAMPLES.md` (examples 2, 3, 4, 6 are directly about this node),
  `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed the row, its `schema_id`, its four neighbours, its two
  residuals, and its `file_kind_owner: ["archive"]`. Also read the five `college_applications`
  template rows so this schema's default template does not eat their situations.
- `planning/domains/canonical_fields.json` — every field on the node is a key from this table.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, `RELIABILITY_STATES`, and D11 (an extractor
  writes only `direct` or `possible`; the other four are fact-layer outcomes).
- No `planning/deferred-catalogues/` file was consumed: this node cites the *existence* of a schools
  gazetteer as R4's content and writes none of its contents, and it writes no regex (R2/R6's).
- Neighbour node files: none had landed when this was written (`planning/domains/nodes/` held only
  `.gitkeep`). Edges were authored against roster ids and the CONNECTION fixtures; reciprocity is
  R1c's.

## Where CONNECTION overrode the dispatch prompt

The prompt says "D6 is unset". It is not: D6 and D2 are ratified (snake_case keys, the academic key
is `subject`). The node follows the ratification — `subject`, not `course`, appears in the academic
file examples, and `00`'s wording survives only inside quotations.

CONNECTION §5 invariant 1 was taken as binding over the prompt's softer framing: Academic and
College-applications carry **both** `collides_with` and `also_holds_with`, and the collision
therefore carries a non-empty discriminating `signal`. Both edges are authored.

## The 3–6 field decision

Four destination-eligible fields, exactly `00`'s sentence: `target_university`,
`application_cycle`, `application_document_type`, `purpose`. One search/explanation extra: `school`.

`school` is the only judgement call on the row, and it is deliberate rather than decorative. `00`'s
role paragraph is explicitly about *this* document type — an application essay mentioning both the
writer's own school and the university it is addressed to — and states "Those are not the same
field." If `school` is not legal when this schema is active, the applicant-side institution has
nowhere to land while the Applications schema is the only active one, and the pressure to write it
into `target_university` is exactly the failure `00` names. So the row **references** the existing
canonical key (it mints nothing) and narrows it: `destination_eligible: false` for this domain. A
schema may narrow its own field as a folder level and may never widen one, per CONNECTION §6, and
the narrowing has an independent reason in `00`: "It should avoid using authorship or creator
identity as a destination dimension."

Marked `provenance: inference`, not `design` — `00` does not list `school` in the College
applications sentence, and pretending otherwise would be the `design_cite`-that-does-not-say-it
failure the contract calls the worst possible one. **If R1c disagrees, deleting this one field is
safe**: nothing else on the node depends on it except the readability of the academic collision
signal.

## `proposed_fields` — none

No key was minted. Two temptations were refused:

- A `sponsor` / `target_organization` field for the scholarship-and-fellowship situation. The roster
  row for that template already flags the tension and says not to mint a field to fix it. It is
  recorded in `open_question` instead.
- A per-domain `purpose` clone (`application_purpose`). PR-1 forbids it, and a second spelling of one
  concept is the 131-duplicate-key defect D6 exists to kill.

`target_school` was left alone. The canonical table holds it unreferenced pending Joseph's answer on
whether it folds into `target_university`; referencing it here would quietly close that question.

## Reliability ceilings, and why they are not all `validated`

- `target_university` → `validated`. The rule family is real and namable: schools gazetteer,
  word-boundary matched and positionally weighted, **plus** application-role context. `00` supplies
  both halves — the word-boundary rule ("MIT can be found inside") and the reason role context is
  mandatory (Columbia's six possible roles).
- `application_cycle` → `validated`, via dedicated term/cycle patterns only. `00`'s narrow-date rule
  is what forbids the tempting shortcut of reading `2026` out of `Resume 2026.pdf`.
- `application_document_type` → `direct`, because a labelled form slot or portal upload label is
  `00`'s own example of a reliable and explicit source. It degrades to `llm_supported` on unlabelled
  prose; a ceiling is the best attainable, not the usual.
- `purpose` → `llm_supported`. This is the honest ceiling: `00` gates purpose on a model judging a
  packet dossier with direct application evidence. It can reach `user_confirmed` the way any fact
  can, through review — that is a review outcome, not a claim about the extractor.

## Files considered and rejected

- **A generic "Common App" file.** Rejected as a *vendor* fixture: the discriminating evidence would
  be a product name, which drifts toward a detector regex (R2's) and toward a gazetteer entry (R4's).
  The labelled-form example carries the same evidence shape without naming a product.
- **A recommendation letter received from a teacher.** Rejected because its honest reading is
  another person's document held by the applicant; it raises a privacy question this row should not
  answer alone, and it adds no new observation/fact split beyond the transcript example.
- **A `.vcf` of an admissions counsellor.** Rejected on `00`'s own rule that contact data "should
  normally be privacy-protected rather than used to create folder proposals" — it would have been a
  format-as-domain fixture with nothing to teach here.
- **A financial-aid tax form.** Rejected as belonging to the finance safety domain first; it would
  have smuggled a safety-domain fixture into a `full`-launch row.
- **A screenshot of a decision letter.** Folded into the portal-screenshot example, which already
  carries the OCR-of-the-same-thing case.

The thirteen kept examples cover, deliberately: labelled form vs unlabelled prose (`Application Form
- Personal Details.pdf` vs `Wash U.docx`); OCR of the same thing (`Screenshot …png`); the archive
packet (`submission.zip`, `00`'s own); calendar and mail (`.ics`, `.eml`); a file that **looks** like
this domain but is a neighbour's (`Columbia BUSIB 4300 Syllabus Spring 2026.pdf`); a file that is
**also** another domain (`PVA-RDP Abstract.pdf` → `also_holds_with research`); shared material with
no institution fact (`Transcript.pdf`, `Resume 2026.pdf`); the conflicting-institution outlier (`Duke
Why Us Essay.docx`); and the file that evidences nothing at all (`IMG_4821.png`).

`group_without_copying_facts: true` is set on exactly the files where the temptation is real —
`Transcript.pdf`, `Resume 2026.pdf`, and `submission.zip`'s members. That is the applications-side
restatement of the `HW 3.pdf` rule: a membership record may exist while the fact does not.

## Neighbours considered that did NOT get an edge

- **`photos`** — a portal screenshot is an `image` with OCR, not a photos-domain file; its media-type
  facts are the photos schema's business only if that schema activates on its own evidence. Nothing
  about the same evidence item confuses the two, so neither edge applies. `never_alone` carries the
  absence-of-EXIF rule instead, which is where the real error would occur.
- **`finance`** — application fees and financial-aid records touch money, but the discriminating
  evidence (an institution acting as a payee vs an addressee) is a *finance* row's problem, and
  `finance` is a safety domain whose activation unlocks protection, not a deep template. Left to
  R1c if a real confusion shows up.
- **`legal` / `medical`** — no evidence path from this domain's files; asserting an edge to a
  field-less placeholder with no confusion behind it would be decoration.
- **`code`** — `submission.zip` can be a code archive instead, but that is discriminated by the
  manifest's own members (a package manifest vs the packet document set), and the confusion lives on
  the archive extractor, not between these two schemas.
- **`research`** got `also_holds_with` but deliberately **no** `collides_with`: `00`'s abstract case
  is disjoint evidence, and calling it a collision would be the exact edge-misuse CONNECTION §9.3
  names.
- **`career`** got `collides_with` but deliberately **no** `also_holds_with`. One resume file can be
  submitted to both a university and an employer, so the co-hold is arguable — but `career` is a
  field-less placeholder today (PR-6), so an `also_holds_with` would assert co-activation of a schema
  that legitimises nothing. Flagged for R1c to revisit **when the Career fields land** (they are owed
  before P10).

## Residual choices

`falls_through_to`: `Independent Records` and `Review Later` — the roster's two, and both are
defensible from `00`'s own descriptions (a standalone certificate or form with a durable purpose but
no broader group; a file whose meaning is partly understood but whose location needs a future
decision). Per-file `falls_through_if_inactive` values reach beyond those two where the file demands
it (`Temporary Screenshots`, `One-Off Images`, `Protected Records`) — all nine names are `00`'s, and
the per-file field is a fixture, not the node's edge list.

`Protected Records` on the labelled form is the one worth flagging: that file carries a date of birth
and a passport number, so it co-activates `identity` and inherits protection. It is a fixture of the
`also_holds_with identity` edge, not a claim that this domain routes to Protected Records.

## Sensitivity

`potentially_sensitive`, and only that phrase. The packet routinely contains an identification
document (`00`'s own listing) and transcripts, and `00` counts educational records among the highly
personal corpus. No handling class is assigned; that vocabulary is P7's.

## NEEDS-JOSEPH — this node only

1. **The addressee field is named for universities but the situation is not.** `target_university` is
   `00`'s spelling, and this schema also has to serve scholarship sponsors, programs, and secondary
   schools (three of its own roster templates). Widen the field's *role* while keeping the key, or
   add one canonical role field? Recorded as the node's `open_question`; **no field was minted to
   paper over it.**
2. **Is `school` legal when only this schema is active?** The node says yes, as a non-destination
   search field (`provenance: inference`). If the answer is no, the applicant-side institution is
   unrecordable on an application essay unless `academic` independently activates — which is a real
   loss on exactly the file `00` uses to introduce the role split.
3. Carried, not re-opened: **NJ-3** (is `purpose` Applications-scoped or universal — this node builds
   on PR-1) and the **`target_school` / `target_university` fold** already recorded in ROSTER.md.
