# career.current-work — build notes (`00` amendments 41 and 42, 20 Sep 2026)

Row: `kind: template`, `schema_id: career`, `launch: placeholder`, `provenance: inference`.
Verdict: **node stands** (`refuse_node: false`).

## WHAT THIS MEMO IS, AND WHAT IT IS NOT

**It is not an R1b lab note.** The six sibling `career.*` memos record a research pass over a
roster, with a node test, a sampling audit and a neighbour sweep behind them. This node was not
produced that way and it would be dishonest to dress it as if it were. It was authored at BUILD
time, by the build acting on a ruling the owner had already given, and its job is narrower: to be
the situation `107`'s Current work template needs in order to have a row at all.

**It is written down because the library requires it to be.**
`tests/p10/test_library_commerce.py::test_every_row_traces_back_to_the_node_row_that_justified_it`
resolves every applicability row's `memo:` provenance to a file on disk, for the reason that file
states: *"a compiled row nobody can trace back to the domain research that justified it cannot be
reviewed or retired."* This is that trace. Read it as the record of a decision, not as evidence
gathered.

## WHY THE NODE EXISTS

`107`'s branch-template table names thirteen templates and Current work is the first of them:

| Template | Default split order | Typical depth | Representative files |
| --- | --- | --- | --- |
| Current work | Employer → year → project or activity → stage | 3–5 | DOCX, PDF, PPTX, XLSX, CSV, email exports, design files |

`00` amendment 22 ratified that `year` is bound on exactly two trees and this is one of them.
Nothing was built, and `tests/p10/test_library_year_is_bound_nowhere_else.py` is the file that
measured why. Two blockers, found by two different agents and both reported rather than worked
around:

1. **The keys.** `60` J-3 declares six fields at `career` and neither `project` nor `stage` is
   among them. No schema in the release declared `employer`, `project` and `stage` together, and
   `60` H6.2 settles what that costs: a file whose key is not declared by the active schema
   returns unknown and is never re-routed. So the order could not be SPELLED.
   **`00` amendment 41 declares the two at `career`** and records the schema as a NAMED EXEMPTION
   from `00`:48's six-key ceiling rather than widening the band, *"because `107` asks a single
   schema to hold BOTH a job search and the work itself."*
2. **The situation.** An applicability row is keyed on a `detection_signal_ref` that must name a
   compiled `recognition` row, so the set of situations a row may cite is CLOSED. `career`
   compiled seven and all seven were spoken for: three filed (`recruiting`,
   `employment-records`, `employer-side-hiring`), three refused on keys amendment 41 does not
   declare (`client`, `issuing_body`, `artifact_type`), and the bare kind anchor.
   **`00` amendment 42 ruled a new situation rather than the anchor.** The anchor route mints
   nothing and is precedented — `ap.nonprofit.restricted-fund` cites `recognition:nonprofit` —
   but `cli.signals_for_branch` gives an UNSETTLED branch one signal per situation its files were
   judged to hold, and amendment 30 has the judge name the KIND. An anchor row would therefore
   have become the recipe for every career branch nobody has settled, and 218 of 257 situation
   facts carry only a kind: résumés and offer letters would be offered
   `employer → year → project → stage` by default. The owner declined that.

## WHAT THE NODE ASSERTS, AND ON WHOSE AUTHORITY

`provenance: inference`, not `design`. `00` names Career at launch and records its template
dimensions verbatim — *"a Career template may define company → role or recruiting cycle →
document type"* — and it does not itself split the work from the job. `107` does. Extending a
named domain is `_CONTRACT.md` rule 1's `inference`, and the `design_cite` says so in those
words rather than claiming a design sentence that does not exist.

**Every span inside quote marks in the node was grep-verified against its source file before it
was written**, which is rule 2's discipline and the one failure this catalogue has already had
(*"a previous review in this project invented three of four clauses inside quote marks"*). Four
attributions were WRONG on the first pass and were corrected rather than kept:

* *"An isolated screenshot can remain under Screenshots or Review and Unsorted…"* is `107`'s
  sentence, not `00`'s. Re-attributed.
* *"An application essay can mention the author's current school…"* is in `00` with a typographic
  apostrophe; the straight-quote spelling matched nothing. Corrected to the exact bytes.
* *"for an employee the employer IS the holder's own organization"* and *"the authorship-side
  identity that is never a destination"* are `60` M12 **as `ap.career.employment-records`'
  exclusions quote it**, which is where those exact strings live. Attributed to the quoting row.

## THE THREE THINGS THIS NODE MUST NOT BECOME

1. **It is not `career.employment-records` with a project level.** That row holds the TERMS of a
   job — the agreement, onboarding, benefits, a performance review of the PERSON, the separation
   record. This one holds the OUTPUT. They name the same employer, which is exactly why the
   collision cannot be resolved by the organization and why `collides_with` names it first.
2. **It is not `career.consulting-client-engagement` with the client renamed.** Five Career-life
   rows carry `client → project → stage → artifact_type`, which is `107`'s SHAPE. `client` is the
   counterparty of the `our_firm` split, not an employer of record, and `107` itself keeps them
   apart — listing *"enable Freelance"* as a template to turn on and *"Combine Career and Work"*
   as a merge a person may choose.
3. **It is not a licence to open four folders.** `00`:57 governs: *"a level your files did not
   actually divide is measured and not built."* The employer level will be empty for almost every
   real single-employer corpus and the recipe expects that.

## THE DIMENSION ORDER IS PROSE, LIKE ITS SIX SIBLINGS

`template.dimension_order` is `[]` and the recommendation is held in `template.why`. That is not
an omission: `_CONTRACT.md` rule 8 lets a template branch only on a field the entry's own schema
DECLARES, and `year` is universal — derived from `creation_date`, declared by no schema, reachable
by all — so it could never appear in a checked list however many keys `career` gains. The
executable recipe is the P10 record, `def.employer-project-record` in
`src/tree_design/library/wave2_commerce.json`, where the order is a list of ROLES and the
applicability row binds each role to a key.

## `collides_with` IS ONE-WAY HERE, AND THAT IS STATED

`_CONTRACT.md` rule 14 asks for reciprocity and this node's four edges are one-way, because the
reciprocal halves would mean editing four researched rows that no ruling authorises this build to
touch. **This is the corpus's ordinary state rather than a new exception**, measured before it was
accepted: of 2,419 `collides_with` edges across the 361 node files, 1,267 have no reciprocal half.
Recorded here rather than left for the next reader to discover.

## WHAT IS OWED THE OWNER

* **`career.current-work`** — a new member of a closed vocabulary. Amendment 42 offered it as
  *"`career.current-work` (or your name)"*, so the string is within what was approved and the
  exact spelling is still the owner's to confirm.
* **`name` and `one_line`** — `"Current work at an employer"` and the sentence under it. The
  compiler carries both into `recognition.json`'s `situations`, which is the menu a cloud judge is
  shown (`00` amendment 1 of 14 Sep). They cross the internet and they are not ratified.
* **The four labels the P10 row authors** — `Where I work`, `Work year`, `Project or activity`,
  `How far the work got`. `Work year` deliberately does not reuse `Year`: `00` amendment 35a
  carves that string out for `ap.career.recruiting` alone and says a second row wanting the same
  licence comes back here.
