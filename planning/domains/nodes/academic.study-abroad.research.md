# academic.study-abroad — R1b lab notes

Row: `kind: template`, `schema_id: academic`, `launch: placeholder`, `provenance: proposal`.
Node file: `planning/domains/nodes/academic.study-abroad.json`.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node
  file was `grep -F`-verified against it before it was written; the verification pass covered 40
  candidate spans and dropped none silently (one candidate paraphrase of the `submission.zip`
  sentence failed the check and was cut rather than trimmed into a quote).
- `planning/prompts/ALIGNMENT.md` — the two-kinds rule, "subdomain" = folder depth or an optional
  branch pattern, work types are values.
- `planning/domains/CONNECTION.md` — the node test (section 2), the closed edge vocabulary
  (section 5), activation ≠ grouping (section 4 step 9), field identity (section 6). Binding where
  it and the dispatch prompt differ; the one place they differ is recorded below.
- `planning/domains/CONNECTION-EXAMPLES.md` — fixtures 1, 3, 4, 6 and 7. Fixture 7 is the direct
  precedent for this row: `tpl.academic-teaching` is licensed by "differs in detection signals and
  recommended dimensions", which is the same test this row is built to pass.
- `planning/domains/_CONTRACT.md` — rules 8 (snake_case; a dimension may only branch on a declared
  field), 11–15 (kinds, `uses_schema`, browse-only `parent_id`, closed edges).
- `planning/domains/canonical_fields.json` — `school`, `term`, `subject`, `instructor`,
  `work_type` reused as-is; no synonym minted.
- `planning/domains/roster.json` — id, kind, schema, neighbours, and every edge target confirmed
  present.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` membership for every file example.
- Neighbour nodes already landed: `academic.json`, `academic.coursework.json`, `identity.json`.
  `academic.coursework.json` is the row this node had to differ from, so it was read closely;
  `identity.json` was read to keep the immigration seam consistent with how that row states its own
  collisions.
- `planning/01-product-design-structured.md` — not read beyond confirming it contains nothing on
  study abroad, exchange programs, host institutions or credit transfer (grep, zero hits, same in
  `00`). Nothing in the node cites it.
- `planning/deferred-catalogues/` — not consumed. This node's recognition needs a schools gazetteer
  (R4) and a term-pattern catalogue extended to academic-year and non-English shapes (R6), but it
  names those rule families rather than supplying their contents.

## The node test — why this row survives

`00` never says "study abroad", so the row is `proposal` and had to earn its place on the node
test's three grounds. It passes on all three, and two of them are independent of the third:

1. **Detection signals differ.** The coursework template fires on a course code plus one of `00`'s
   five academic context terms. That rule fires identically on a host-institution syllabus and
   tells you nothing about the situation. What identifies this situation is an exchange-program
   context term plus an institution hit, or — the shape unique to it — *two* institution names in
   two separately labelled slots naming opposite roles. No other academic row has a two-institution
   signal, because no other academic situation has two institutions of enrolment at once.
2. **Privacy rules differ, and differ in kind.** Coursework's privacy concern is grades and other
   people's names. This situation's is an ordering problem: an exchange assembles immigration
   paperwork, a housing agreement, a grant with an account slot and geotagged captures into one
   folder, and three of `00`'s four safety domains sit inside the same program. The rule this row
   carries — the safety material must be detected and protected *before* this template is offered
   as a home — is not a stricter version of coursework's rule, it is a different rule.
3. **Recommended dimensions differ**, at exactly one level: `term` is dropped. Reasoning below.

Had only the third been true I would still have written the row; had only a foreign language and
foreign file extensions been true, I would have refused, because language is a value and an
extension is a `SOURCE_TYPE`.

## The dimension decision — dropping `term`

The schema default is `00`'s own: school → term → course → work type. This row recommends
`school → subject → work_type`.

The reason is structural, not stylistic. A study-abroad branch is by construction one host
institution and, in the common case, one term — so a `term` level beneath it produces a single
child. `00` tells the canvas to warn on exactly that ("warn when a level produces only one child")
and to act on it ("recommend flattening when a dimension does not materially improve retrieval").
`term` stays a *fact* — it is still extracted, still validated by the term-pattern rule, still
searchable; it just stops being a folder level. That is the facts-are-not-paths distinction doing
real work rather than being restated.

The optional branch pattern that restores `term` is the full-academic-year exchange, where two
terms of host coursework sit under one program and one agreement. `00` explicitly permits the
resulting unevenness between this branch and the home-coursework branch beside it.

What I did **not** do: invent a "program" or "mobility" dimension. There is no canonical field for
it, a template may only branch on fields its schema declares, and inventing one to make the order
look distinctive is the failure mode this row exists to avoid.

## `proposed_fields` — `host_school`, and why it is a proposal and not an edit

The situation puts two institutions in one `school` field simultaneously. The canonical row for
`school` reads "the person's own school, never the application target"; during an exchange both
institutions are the person's own school, in two different roles — the institution of record that
awards credit, and the institution of study that teaches and grades. `target_university` does not
fit: once a placement is granted nothing is being applied to.

The concrete failure under one key: a learning agreement names both institutions in two labelled
table rows and cannot say which value plays which role; and under `school`-led dimensions, a
credit-transfer approval issued by the home registrar and the host courses it approves land in two
different branches.

`00`'s own rule is the licence for the proposal — "The system must separate roles that happen to
contain the same entity type" — and its example is one hop away (an essay's current school versus
the university it is addressed to). CONNECTION.md agrees that a role split is the *only* licence
for a near-duplicate field, which is exactly what this is.

I did not write it into `canonical_fields.json`, did not branch a dimension on it, and did not
write a fact to it. It is recorded in `proposed_fields`, referenced from `role_split` as explicitly
PROPOSED, and stated as the node's `open_question` with the cheaper alternative named honestly:
keep one `school` field, let one file carry two values, and accept that the folder dimension can no
longer separate them. Both branches of that fork have a real cost; picking one is Joseph's or
R1c's, not a template agent's.

## Files considered and rejected

- **Passport scan / visa sticker photograph.** The obvious study-abroad artifact, and it is not
  this node's file. It evidences identity and nothing academic; including it as a file example
  would model the exact mistake the row's privacy rule forbids (an academic branch acquiring a
  passport by proximity). It appears only as a manifest entry inside `exchange_packet.zip`, where
  the lesson is that a manifest name is a protection signal about a member not yet read, not a
  fact.
- **Language-proficiency certificate (TOEFL/IELTS score report).** Real, but it is
  `academic.standardized-testing`'s file: a test name in the `subject` slot, a score-report
  structure, no institution of enrolment. Modelling it here would have duplicated that row.
- **Host-university course catalogue PDF.** Kept only implicitly, through the Reading Inbox
  fallthrough. As a file example it adds nothing the foreign syllabus does not already show, and it
  usually carries hundreds of course codes, so no single `subject` describes it.
- **Study-abroad application essay.** Genuinely ambiguous, and that ambiguity is already carried by
  the portal screenshot fixture and the `applications.undergraduate-packet` collision. A second
  essay-shaped example would have restated it.
- **Travel photo album from the exchange.** `photos` / `travel.trip-photos` own it. One image
  example (`IMG_3390.HEIC`) is kept because it makes the GPS-is-not-a-school point, which is a real
  temptation specific to this situation.
- **`.eml` from an international office.** Listed under `file_kinds` but not given an example: the
  coursework row already works that shape, and the exchange variant would only repeat it.
- **Insurance certificate for the mobility period.** Sits inside the archive manifest. As its own
  example it would have pulled in the finance/medical insurance templates without teaching anything
  this row needs to state.

## Neighbours considered that got no edge

- **`academic.online-course`** — both can lack a term and both can carry a provider that is not the
  holder's degree institution. No edge: the discriminator is not shared evidence but a plain
  absence — an online course has no host *enrolment*, no coordinator, no credit-transfer artifact.
  The confusion is between platform-vs-university, which `academic.coursework` already states.
- **`academic.transcripts-credentials` beyond the one collision** — considered whether the host
  transcript should be modelled as jointly held. Declined: co-holding between two templates on the
  *same* schema is not a thing the vocabulary expresses, and the discriminating signal is already
  written on the collision.
- **`travel.trip-photos`** — geotagged captures during the exchange are that row's, cleanly. The
  only crossing case (a whiteboard photo) is handled inside a file example's `must_not_conclude`
  rather than by an edge, because there is no evidence item that would confuse the two situations;
  there is only a folder that holds both.
- **`identity.core-documents`** — the passport itself. The edge goes to
  `identity.immigration-visa` instead, which is where the shared evidence item (an institution name
  on a document that also carries a passport number and a consular addressee) actually lives.
- **`medical.personal-health-records`** — mandatory health insurance and vaccination records travel
  with an exchange. No edge: nothing in the shared evidence would confuse a vaccination record with
  a course record. It is folder adjacency, not evidence collision, and writing an edge for
  adjacency is how `collides_with` got overloaded in the 574.
- **`research.project-workspace`** — a research stay abroad is real but is a different situation
  (project, lab, venue), and no evidence item pulls both ways that the academic schema row does not
  already state.
- **`applications.scholarship-fellowship`** — the mobility grant edge went to
  `finance.student-financial-aid` instead, because the discriminating item is an amount and a
  disbursement schedule, which is that row's evidence, not an application cycle.

## Where CONNECTION.md overrode the dispatch prompt

The prompt lists `also_holds_with` among the edges this node may write. CONNECTION.md section 5
restricts `also_holds_with` to **schema ↔ schema**, and CONNECTION wins. The array is therefore
empty, with the reason recorded inline in the node so it does not read as an oversight — and the
same choice was made by `academic.coursework.json`, so the two rows are consistent.

Two schema-level co-holdings this situation genuinely produces are **findings for R1c**, since this
row may not author them:

- `academic ↔ identity` — an enrollment certificate issued for a visa application carries school,
  term and work_type from its own labelled slots while carrying identity material in the same
  header block. Disjoint evidence, two readings, protection first. `identity.json` today asserts
  `also_holds_with` toward `college_applications` on the same packet logic, so the pattern exists;
  the academic pair is not yet stated from either side.
- `academic ↔ finance` — a mobility grant award letter carries the home institution, the program and
  the term alongside an amount, a schedule and an account slot. `academic.json` today lists
  `also_holds_with` toward college_applications, research, photos and career, but not finance.

Both are reciprocity work, which is R1c's job by contract.

## NEEDS-JOSEPH (this node only)

- **NJ-SA-1 · `host_school`: a canonical role-split field, or two values in one `school` field?**
  The node's `open_question`, restated for the roll-up. (a) Admit `host_school` with a `role_split`
  against `school`: a learning agreement can then state both roles, and this template can branch on
  the host value — at the cost of a near-duplicate field, which the contract licenses only for a
  genuine role split, and which R1c would have to reciprocate in `canonical_fields.json`. (b) Keep
  one `school` field carrying two values on one file: cheaper, consistent with facts being
  multi-valued, but the folder dimension cannot keep host coursework apart from home
  administration, and a credit-transfer approval and the courses it approves land in different
  branches. This node builds on neither answer — `dimension_order` names only declared fields
  either way.
- **NJ-SA-2 · Who owns an exchange-placement application?** The evidence is identical to a degree
  admission (target institution, portal, deadline, essay register) and differs only by the holder's
  existing enrolment. Either `applications.undergraduate-packet` owns the arc until a placement is
  granted and this template takes over afterwards, or this template owns the whole arc. Recorded as
  a collision either way, so nothing is blocked; the answer changes which row a portal screenshot
  is offered under.
- **NJ-SA-3 · Should `term` be dropped from the recommended order, given `subject` values here are
  foreign course codes?** The flattening argument rests on a study-abroad branch holding one term.
  Where the exchange runs a full academic year and the host numbering repeats codes across
  semesters, dropping `term` merges two terms of host coursework — the same defect `00` warns about
  for course codes ("A course code alone should not merge different semesters"). The node states
  the full-year case as the optional branch pattern that restores `term`; whether that should
  instead be the default is a judgement about real corpora, not about the design text.
