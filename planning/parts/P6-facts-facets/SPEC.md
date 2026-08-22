# P6 — Facts and facets

Owns: §3.1–3.14
Status: contract draft

## Purpose

P6 is the layer that turns *observations* into *claims*. P5's extractors report what a file
literally contains; P6 decides what may be asserted about the file on that basis, records the
assertion beside the exact evidence that justifies it, and stamps it with one of six reliability
states (§3.13). It is "the shared memory of the entire pre-sorting engine" (§3.2): everything
downstream — grouping, template population, tree design, placement, residual review — reads facts,
not raw text.

Three properties define the part, and each is a hard boundary rather than a goal:

1. **Facts never replace evidence.** Both the original observation and the conclusion built from it
   survive, so a later resolver can reinterpret without losing what the earlier one saw (§3.2, §8.2).
2. **Facts carry no path.** A fact is a statement about a file, not a destination for it. The same
   fact set supports `Academics/Columbia/2026-Spring/BUSIB 4300/Syllabus` and
   `Academics/BUSIB 4300/Spring 2026/Syllabus` without changing (§3.14).
3. **Insufficient support produces `unknown`, never a plausible guess.** A weak clue may be kept as
   a clue; it must not quietly become a folder proposal or an asserted file property (§3.6).

P6 is deterministic in Wave 2 (segmentation map): every direct and rule-validated fact must be
produceable with no model present. The LLM path (§3.5, §3.6) is an additional producer that writes
into the same tables, not a second fact system.

## Design slice owned

| § | Obligation P6 carries |
|---|---|
| 3.1 | A file is a record of many facts, not one category. Every fact preserves where it came from. |
| 3.2 | Observations ≠ facts. Both the raw evidence and the derived conclusion are retained. |
| 3.3 | Rules are the precision layer; the LLM enters only where language interpretation is required. P6 owns the *fact-side* half — which fields exist, which schema is active. |
| 3.4 | Cache key = content hash + extractor version + analysis tier + model identifier + prompt fingerprint. |
| 3.5 | Three producers writing one format: direct, rule-validated, LLM-supported. |
| 3.6 | Four validation checks before an LLM-produced fact becomes active; `unknown` on insufficient support; weak-but-useful stays a clue. |
| 3.7 | Conservative facet extraction: word boundaries, positional weighting, ranked candidates, minimum score **and** minimum margin. |
| 3.8 | Roles, not entity types. `authored_by` ≠ `target_school`, `our_firm` ≠ `client`. Authorship is never a destination dimension. |
| 3.9 | Purpose is a first-class facet, distinct from topic. A download session is a clue, never proof, and never carries hash-match confidence. **P6 computes the bounded download session** from P3's timestamps and emits it as a `possible` fact only. |
| 3.10 | Narrow dates: explicit regexes, no fuzzy parsing, dedicated academic-term patterns. |
| 3.11 | Small universal field set + per-domain activation. One file may hold facts from several domains at once. **P6 computes the universal `duplicate family` and `version family` facts** (§2.9) and the Photos-domain **`event`** fact (§4.2's deterministic camera/time/GPS event). |
| 3.12 | The tables. New **values** may be created automatically; new **fields** may not. |
| 3.13 | Six reliability states; internal scores may rank but must not replace the recorded kind of evidence. |
| 3.14 | Facts stay separate from the destination tree. |
| 3.15 | **Split ownership.** §3.15 defines each domain as two things — a *fact schema* and a *folder template*. P6 owns the fact schema half; P10 owns the folder template half. |

### Explicitly not owned

- The observation record itself (§2.8) — P4.
- Producing observations (§2.1–2.7, §2.9) — P5.
- The dossier/response/validator *mechanism* (§3.3, §3.6, §4.8, §6.10, §7.9) — P8. P6 supplies its
  inputs and consumes its verdict; see Contract in.
- Group membership and group-level labels (§4) — P9. P6 stores no membership.
- Folder dimensions, dimension order, template libraries (§5) — P10.
- Handling classes and the consent gate (§8.4) — P7.

## Contract in

### From P1 — storage, identity, provenance (§0, §8.2)

Read-only:

```text
file_id              internal, stable across renames and moves
content_hash         + hash algorithm; the identity of a file *version* (§8.2)
current_path         used for filename-derived observations only, never stored on a fact
mime_type / detected_format
sensitivity_state    (§8.2 file record) — see the open question on its relationship to P7
```

Append-only: P6 writes `events` rows through P1 and never mutates them (see Provenance below).

### From P3 — scan and basic filesystem record (§1.2, §2.9)

Read-only, and consumed for exactly two computations:

```text
timestamps                 P3 observes (§1.2) — the input to the bounded download session
parent-folder context      P3 observes (§1.2 spells it "directory position"; §2.9's name is
                           the published one — one field, MINOR 11) — the input to
                           session boundedness
```

P6 never recomputes the §1.2 basic filesystem record and never re-observes the filesystem; it reads
P3's row. This is the only non-P4 input P6 accepts for fact production, and it exists because §3.9's
bounded session is a *temporal* clue that no observation can carry.

### From P4 — the observation record (§2.8)

P6 reads the frozen observation shape and **nothing else**. §2.8 exists so that downstream logic
does not branch per format; P6 therefore treats all of the following as opaque strings or ordered
structures supplied by P4, and must resolve a fixture carrying an unrecognised `source type`
without new code:

```text
observation_key            ← the citation handle P6 stores (M14); content-addressed and
                             version-independent, so a negative example recorded today still
                             resolves after an extractor upgrade (§8.7)
observation_id             per-row, P4-assigned; P6 never cites it
file_id
content_hash
extractor_name / extractor_version
source_type
raw_value                  ← preserved verbatim; a fact never overwrites it (§2.8)
normalized_value
location { zone, … }       ← `zone` is P4's closed vocabulary and is the input to §3.7
                             positional weighting; P6 owns what each zone is worth
context_before             ← §2.8's "surrounding context", split by P4 into three fields (M5)
context_after                so §8.4 can redact a value without dropping its context
context_truncated          ← §8.6 forbids silent truncation; see the rule below
signal_tier ∈ {1,2,3}      ← nullable, §2.6-scoped (M2). P4 assigns it from §2.6's three-band
                             image-signal hierarchy; P6 consumes it and never re-derives it
occurrence_count
observed_at
reliability                ← see open question 12
```

The context split is P4's and is load-bearing: **P6's §3.5 rule context check reads
`context_before` and `context_after` together**, never a single concatenated field, and honours
`context_truncated`. A context check that fails on a record with `context_truncated = true` is not a
clean refusal — the term may have been cut — and is recorded as `unresolved` with reason
`context_truncated` rather than as a silent absence (§8.6: nothing is truncated silently).

`evidence` rows are **immutable to P6**. P6 cites observation **keys**; it never edits, deletes, or
re-normalizes an observation row (§3.2, §8.2, M14).

### From P5 — extractors (§2.1–2.7, §2.9)

Only via P4's shape. P6 requires no per-format knowledge and must not acquire any. Fixtures for
P6 are therefore lists of observation records; no extractor need exist to build or test P6.

Three P5 outputs P6 depends on **by value, never by format** — each arrives as an ordinary P4-shaped
observation, so the no-per-format-knowledge rule is untouched:

- the **perceptual hash** (§2.6), the second input to the duplicate/version-family facts below;
- the **image signal observations**, each tagged with P4's `signal_tier` (§2.6). P5 emits no
  photo/screenshot conclusion — `media type` is a Photos-domain fact and is P6's;
- the **camera, capture-time and GPS EXIF observations** (§2.6), the inputs to the §4.2 photo event.

**Absence is never an observation.** P5 records "no EXIF" on `extraction_runs`, not as an evidence
row, so P6 never receives it and must never treat a missing signal as evidence — §2.6: "the system
must not mistake the absence of EXIF for proof that an image is a screenshot."

P6 publishes one signal back to P5: `no_usable_facts` (see the read surface). It is a return value,
not a request; P6 initiates nothing toward P5.

### From P7 — privacy and consent gate (§8.4)

A handling class per file, resolved **before** P6 requests any model work (§8.4: "enforced before
content reaches any model or external connector"). P6 will not construct an LLM fact request for a
file whose handling class forbids it; the file's direct and rule-validated facts are produced
normally, and the LLM-dependent fields simply remain `unknown` (§3.6) rather than being filled by a
weaker route (§8.6).

### From P8 — LLM harness and validator (§3.3, §3.6)

The seam, stated from P6's side so P8 can be built against it:

**P6 supplies** — the active domain schema for the file as an explicit field allowlist (§3.5: the
model "can only propose facts that belong to the active domain schema"); the observation set the
model may cite from; the existing `direct` and `validated` facts on the file, so contradiction can
be detected (§3.6); and the per-field normalizers that decide whether a proposed value "can be
normalized safely" (§3.6).

**P8 returns** — per proposal: field, value, one or more citations, or an explicit `unknown`; plus a
validation verdict against the four §3.6 checks (field in active schema · cited quote present in
stored evidence · value normalizes safely · no stronger direct or rule-validated fact contradicts).

**P6 applies the verdict** — pass → a `llm_supported` fact (§3.13); `unknown` or any failed check →
no fact **and an `unresolved` row** naming the field and the reason (B7); a proposal that is "useful
but too weak to establish a fact" → at most `possible`, which is excluded from every
proposal-eligible read (§3.6). Ownership is settled: **P8 owns the validator mechanism and the
verdict; P6 owns its inputs and the consequence of each verdict** (O6, closing this part's Open
question 2).

### From P9 — grouping (§4)

P6 accepts **no** fact writes derived from group membership. §4.1 is explicit that the graph "does
not automatically copy those missing facts onto sparse files", and §3.9 forbids using a session as a
basis for automatic semantic propagation. A fact is written only for the file from whose own
evidence it was derived. Group-level conclusions live in P9's membership records. (Open question 9
covers the one case §4.7 leaves ambiguous.)

### From P13 — collected fact-level corrections (§8.4, §8.7)

A user gesture that reclassifies a file's facts as private arrives as P13's `review_action` with
`action = mark_private`, routed jointly to P6 and P7, carrying `subject_ref`, `plan_version`,
`correction_scope` (§8.7) and `presented_state_ref`. P13 presents and collects; it decides nothing.
**P6 authors the fact-level consequence of the correction** (M8) and P1 writes the event.

## Contract out

### Table: `fields` (§3.12)

The organization language of the product. **Not** created automatically at runtime (§3.12).

```text
field_key            stable identifier — the role, not the entity type (§3.8)
                     e.g. subject, term, work_type, authored_by,
                          target_school, our_firm, client, purpose, project, event
display_name
scope                universal | academic | college_applications | research
                     | finance | photos | code           (§3.11 — exactly these; see Deferred)
value_kind           how this field's values normalize; date/term fields must use §3.10 rules
normalizer_id        the safe-normalization check §3.6 requires
destination_eligible whether this field may ever become a folder level.
                     FALSE is mandatory for authorship and creator-identity fields (§3.8).
                     Per-field assignment beyond that rule is deferred.
multiplicity         see open question 6
```

Universal fields, exactly as §3.11 names them: **file type, creation date, language, duplicate
family, version family, sensitivity status**. `duplicate family` and `version family` had no owner
anywhere in the design; P6 computes both (see *Production rules*).

**The universal list is a floor, not a closed set.** §3.11 introduces it with "such as" — verbatim in
the source of truth — the same construction B5 reads as opening §8.2's event list. Exactly one
further universal field is added here, and only because §3.9 + §4.2 require a representation that no
§3.11 field can hold:

| Field | Why it must exist | Constraints |
|---|---|---|
| `download_session` | §3.9 requires a tightly bounded download session to be recorded as a purpose clue, and §4.2 requires it to be retrievable ("files found in a narrow purpose-oriented session"). It is not `purpose`: the session names no purpose value. | `scope = universal`; `destination_eligible = FALSE` — a session must never become a folder level (§3.9: never proof of topic, a review aid); values auto-create per §3.12; facts on it may never exceed `possible` (§3.13). |

No other field is added. Every §3.11 domain row below stays literal, and the domains §3.15 names but
§3.11 gives no field row (Career and recruiting, identity, medical, legal) stay **deferred**.

Domain fields, exactly as §3.11's table names them and no more:

| Domain | Fields (§3.11, literal) |
|---|---|
| Academic | school, term, course, instructor, work type |
| College applications | target university, application cycle, application document type, purpose |
| Research | project, stage, artifact type, lab, venue |
| Finance | institution, account type, tax year, record type |
| Photos | capture year, event, location, people, camera information, media type |
| Code | project, repository, programming language, artifact type |

> **That table is a literal transcription of §3.11 and is deliberately left unchanged. Two of its
> words are NOT stored field keys.** `course` (Academic) is the design's prose for the field whose
> stored key is **`subject`** (**D6**), and `target university` (College applications) is prose for
> **`target_school`** (**D8**). Both are aliases; the `fields` catalogue carries neither as a row.
> The transcription stays literal so the §3.11 citation remains checkable — but an author reading
> it to build `FIELD_ROWS` must take the stored keys, not these words.

§3.11 also states that each domain carries "several additional fields used only for search, privacy
protection, explanation, or later review" — it names none of them. Those are deferred, not invented
here.

### Table: `values` (§3.12)

The changing, user-specific content discovered from files. **May** be created automatically when the
system sees a new course, project, company, university, or event (§3.12).

```text
value_id
field_id             a value belongs to exactly one field (§3.12)
canonical_value      the normalized form — "University of Chicago"
raw_variants[]       every raw wording observed — "U Chicago" (§2.8)
display_label        the user's preferred rendering — "UChicago" (§2.8);
                     plan-versioned, see Plan versioning below
aliases[]            taxonomy aliases (§0); merges record an alias, never delete a value (§8.2)
origin               automatic | user (§3.12)
first_evidence_ref   the observation that introduced it
```

### Table: `file_facts` (§3.12)

One row = one (file, field, value) connection, "while retaining the evidence and reliability state
that justify the connection" (§3.12).

```text
fact_id
file_id                    (P1)
field_id
value_id
reliability_state          one of the six (§3.13)
origin                     which producer created it — deterministic extractor | rule |
                           LLM interpretation | user correction | user-approved folder (§3.1)
evidence_refs[]            one or more P4 observation **keys** (M14) — required for every
                           non-user state; version-independent, so the chain survives an
                           extractor upgrade (§8.7)
cited_quote_refs[]         for llm_supported: the exact spans the model cited, by
                           observation key + text span (§3.6)
cache_key                  content hash + extractor version + analysis tier
                           + model identifier + prompt fingerprint (§3.4)
model_identifier           when model-derived (§3.4)
prompt_fingerprint         when model-derived (§3.4)
internal_score             optional ranking aid; must not replace the recorded evidence kind (§3.13)
active                     a fact is inactive until it passes validation (§3.6)
supersedes / superseded_by / supersede_reason   (§8.2 — supersede, never overwrite;
                           spelled per M1's published set)
preferred                  §8.2's resolver pointer — **this column lives here and nowhere
                           else** (M1). See the rule below.
rejection_reason           for `rejected`: who rejected it and on what evidence (§8.7)
created_at
```

**Negative contract, load-bearing:** `file_facts` has no path column, no destination column, no
folder column, and no group column. A fact does not dictate a path (§3.14) and does not record
membership (§4.3). A reviewer should be able to check this by reading the schema alone.

**`preferred` — the one column M1 places here (§8.2).** §8.2 says a newer result "should
**supersede** an earlier result while retaining the old observation and the reason it was
superseded. … The resolver **may mark the newer value as preferred**." §3.2 places the resolver
after extraction, so the observation layer (P4) does not carry it and neither does any other part.

How P6 sets it:

- It is set **only** on supersession. When a new fact supersedes an earlier fact for the same
  `(file_id, field_id)`, the surviving row gets `preferred = true` and the superseded row
  `preferred = false`. Both rows, both states, and both evidence chains remain readable (§8.2).
- It is set **only by the resolver** — never by an extractor, never by P8, never as a side effect of
  a model proposal.
- A `user_confirmed` fact is always the preferred row for its `(file_id, field_id)`; §3.13's ordering
  is not negotiable and `preferred` never reverses it.
- **`preferred` is a pointer, not a strength.** It never enters the §3.6 contradiction check, never
  breaks a §3.7 margin tie, and never makes a fact destination-eligible. A reader that wants
  strength reads `reliability_state`.
- It is **not plan-versioned**: facts are shared across plan versions (§8.8).

§8.2's worked example is exactly this column's case, and it is P6's: a first OCR pass produces
unreadable text — under B7 that is now an `unresolved` row with reason `no_candidate_evidence`, not
an absence — and a later improved engine recovers a university name. The new fact supersedes, is
marked `preferred`, and both extraction records plus the `unresolved` row remain inspectable.

### Table: `unresolved` (§3.6, §8.5) — the abstention row

**B7.** A §3.6 failure previously produced *no row*, and P2 cannot distinguish a missing row from a
crash or a skip — §8.5 requires evaluation to be "decomposed by stage" and asks under Fact quality:
*"Did it abstain when evidence was absent?"* An absence cannot answer that question. P6 therefore
records its refusals.

```text
unresolved_id
file_id                    (P1)
content_hash               (P1) — the abstention is per file *version* (§8.2, §3.4)
field_id                   the field that was attempted — required
reason                     one of the values below — required
attempted_producers[]      direct | rule | llm — which §3.5 routes were tried
evidence_refs[]            the observation keys considered, where any were (may be empty)
cache_key                  same composition as `file_facts` (§3.4), so an abstention is
                           invalidated by the same events that invalidate a fact
created_at
```

| `reason` | fired by |
|---|---|
| `no_candidate_evidence` | no observation offered a candidate for the field (§3.6 "cannot cite sufficient evidence") |
| `below_score_threshold` | §3.7 minimum score not cleared |
| `below_margin` | §3.7 margin over second-best not cleared — including the conflicting-image-signal case (§2.6) |
| `context_check_failed` | §3.5 rule matched the pattern, found no required context term |
| `context_truncated` | §3.5 context check failed on a record with `context_truncated = true` (§8.6) |
| `field_not_in_active_schema` | §3.6 check 1 |
| `citation_absent_from_evidence` | §3.6 check 2 |
| `normalization_failed` | §3.6 check 3 |
| `contradicted_by_stronger_fact` | §3.6 check 4 |
| `model_returned_unknown` | §3.6 — the model declined |
| `discounted_tool_metadata` | the §2.2/§2.3 producer/creator discount fired (see *Production rules*) |
| `privacy_withheld` | P7's handling class forbids the model route; the field stays `unknown` (§8.4, §8.6) |
| `budget_deferred` | §8.6 ceiling reached — **a distinct value, never merged with abstention** (B7) |

Rules that make the row trustworthy:

1. `unresolved` is **not a fact**. It carries no `value_id`, no reliability state, and is absent from
   every fact read including the proposal-eligible read. It is not a weaker `possible`.
2. It obeys the same negative contract as `file_facts`: no path, destination, folder or group column.
3. A later fact for the same `(file_id, content_hash, field_id)` does not delete the row — it
   supersedes it, and the row remains readable as the record of what was once refused (§8.2, §8.7).
4. `budget_deferred` and `privacy_withheld` are **not** abstentions. §8.6 requires deferred work be
   mark the deferred stage, and leave the file or group in review rather than guessing (§8.6), which "avoids the false impression that an unprocessed file was understood and found unimportant"; conflating them would report a
   budget stop as a considered refusal.

### The six reliability states (§3.13)

| State | Meaning (§3.13) |
|---|---|
| `user_confirmed` | Explicitly accepted, entered, renamed, merged, or corrected by the user |
| `direct` | Read from a reliable and explicit source — content hash, EXIF timestamp, document title, labeled form field |
| `validated` | Found by a deterministic rule and passed contextual checks |
| `llm_supported` | Proposed from a bounded evidence packet, cited exact supporting text or metadata, and passed deterministic validation |
| `possible` | A useful but insufficient clue — a short download session, a low-confidence semantic match |
| `rejected` | A proposal the user or validator marked as incorrect |

Strength for the §3.6 contradiction check follows the design's listed order:
`user_confirmed` > `direct` > `validated` > `llm_supported` > `possible`. `rejected` is not a
strength — it is an exclusion that must persist so the same proposal is not resurfaced (§8.7).
Equal-rank contradiction is open question 10.

**These six literals are canonical, and P6 publishes them once so no part re-spells them.** The
stored and transmitted spelling is **snake_case, lowercase**, exactly as in the table above:

```text
user_confirmed   direct   validated   llm_supported   possible   rejected
```

`LLM-supported`, `User-confirmed`, `llm-supported` and `user-confirmed` are **not aliases and are not
accepted** — a value outside the six literals is a load error, not a spelling to be normalized. §3.13
writes the states as English prose ("A user confirmed fact…", "An LLM-supported fact…"), which is
where the rival spellings came from; prose is not a literal. P4's conformance rule 2 rejects
any value not drawn from the closed vocabularies, so a round-trip through a part that respells them
fails on spelling alone — which is why the spelling is contract and not style.

### Production rules P6 guarantees

**Direct (§3.5)** — from a reliable, explicit source: content hash, EXIF timestamp, document title,
labeled form field. Filesystem timestamps are direct; dates recovered from text or filenames are
not, and take the §3.10 path.

**Rule-validated (§3.5)** — a pattern match *plus* a strict context check. The design's worked
requirement, literal and required: `BUSIB 4300` becomes a `subject` fact **only** when a course-code
pattern is found together with academic context — **"syllabus", "lecture", "credits", "instructor",
or "semester"**. A course-code-shaped string with no such context in its surrounding context window
yields no `subject` fact. (**D6**: the stored key is `subject`; "course" is the design's prose for
the same field. "Course-code" here describes the *shape of the string*, which is unaffected.)

**The §3.5 context-term check is case-insensitive** (N-6). §3.5 writes its five terms in lowercase
and states no matching rule, so P6 states one: a term matches regardless of the case it appears in.
`Syllabus`, `SYLLABUS` and `syllabus` all satisfy the check. This is the §3.5 *context* check only —
it does not relax §3.7 facet matching, whose case discipline is stated below and unchanged. Two
consequences that are contract, not commentary:

- **word-boundary matching still applies** to the context term exactly as it does to a facet value: a
  case-insensitive match is not a substring match, so `semester` must not match inside a longer word;
- **P4's skeleton fixture resolves.** Fixture 1 carries `context_before: "Syllabus — "` with a
  capital S (B8(a)), and B8(a)'s whole purpose was to make the skeleton's one fact resolvable. A
  case-sensitive reading would refuse that fixture and the walking skeleton would produce no fact.

**Facet matching (§3.7)** — mandatory, in this order:
- **word-boundary matching, never substring.** `MIT` must not match inside "sub**mit**"; `UNC` must
  not match inside "**unc**ertainty". These two are named in the design and re-appear in §8.5's
  adversarial suite; both are Done-means assertions.
- **positional weighting** off P4's `location`: a value in a filename or document title outweighs
  the same value in a footer or a late body-page reference (§2.2, §3.7).
- **ranked candidates**, never first-match.
- **two thresholds**: a minimum score **and** a minimum margin over the second-best candidate. Both
  must be cleared before a facet is filled. Failing either leaves the facet unfilled — the design
  permits a clue, never a fill.
- gazetteers must be **validated** gazetteers (§3.7). Their contents are deferred.

**Dates (§3.10)** — no fuzzy parsing, ever. Candidates are identified by explicit regular
expressions and then parsed without fuzzy matching. Three patterns are named in the design and are
required, each with a dedicated pattern rather than generic parsing: `Spring 2025`, `AY 2024-25`,
`Michaelmas Term 2024`. Numbers that resemble years but are course identifiers, version numbers,
build numbers, or ZIP codes must not produce date facts (§3.10, §8.5).

**Purpose (§3.9)** — `purpose` answers what a file was *for*, not what it is *about*, and the two
are separate fields. Purpose may be supported strongly by an existing user-created folder name or
explicit language in a form or portal. A tightly bounded download session supports purpose only
weakly: it may never be recorded above `possible`, and it must not carry the confidence of a hash
match or a directly extracted document fact. **P6 computes the session itself** — see the bounded
download session rule below (G6).

**Roles (§3.8)** — the same entity type in a different role is a different field. `authored_by` and
`target_school` are two fields; `our_firm` and `client` are two fields. No authorship or
creator-identity field is ever `destination_eligible`.

**Domain activation (§3.11)** — the universal set applies to every file. A domain schema activates
only when evidence indicates that domain is plausible; `target_school` is not a field every file
is expected to have. One file may carry facts from several domains simultaneously without either
being dropped — §3.11's worked case is an abstract holding `project = PVA/RDP` and
`document type = abstract` *and* `purpose = university application` and
`target university = UChicago`. P6 preserves all four; deciding which perspective determines
physical location is not P6's decision (§3.11, §3.14).

> **The worked case keeps the design's own words; two of them are not stored keys.** `document
> type` is the design's generic word for whichever field the active domain declares —
> `application_document_type` here — and `target university` is prose for **`target_school`**
> (**D8**). Quoted so the §3.11 citation stays checkable; an implementer stores the keys.

**Producer, creator and author metadata — the discount rule (§2.2, §2.3).** M4: nobody owned this
and both sections require it. There is no marker on the observation; P4 emits the value with
`reliability = direct` because `direct` describes the *slot* (a labeled metadata field), not the
value's usefulness. The discount is P6's, and it has two tiers, both keyed on P4's
`location.zone = metadata` plus the property name (`Producer`, `Creator`, `Author`, `Last Modified
By` and their per-format equivalents):

1. **Suppression.** A value on the deferred tool-string list — §2.2 names `python-docx`,
   `Mozilla/5.0`, and "a browser-generated producer string" — produces **no fact in any field**, and
   an `unresolved` row with reason `discounted_tool_metadata`. §2.2 is literal: such a value "should
   not be mistaken for meaningful content." It is not downgraded to `possible`; a tool name is not a
   weak clue about the document, it is a fact about the software.
2. **Demotion.** Any other producer/creator/author metadata value is *supporting evidence, not
   truth* (§2.2) and *supporting information only* (§2.3). It may populate an authorship role field
   (§3.8 `authored_by`) and nothing else; it may never populate a topic, purpose, project, subject,
   institution or target field on its own; and §3.8 already makes every authorship field
   `destination_eligible = FALSE`. §2.3's reason is the binding one: the value "may identify a prior
   editor, a document template, or a script rather than the meaningful subject or purpose."

The rule fires before facet ranking, so a discounted value never enters §3.7's candidate list and
therefore cannot win a margin it should never have contested. §8.5's adversarial suite names
"generic author metadata" as a required case, and it is a Done-means assertion below. **P5 Open
question 13 closes as answered: there is no marker; the discount is here.**

**Conflicting image signals (§2.6) — resolved by §3.7's ranking, not by a new mechanism.** M2 moves
this to P6. P4 supplies `signal_tier ∈ {1,2,3}` carrying §2.6's hierarchy — tier 1 is camera EXIF
("strong photo evidence"), tier 2 the reinforcing band (capture time, GPS, sensor-shaped
dimensions), tier 3 the screenshot-hypothesis band (exact display resolutions, PNG format, software
metadata). P6 consumes the tier and **never re-derives it** from `extractor_name` or a field label,
which would encode §2.6 in a second place.

Resolution is the ordinary §3.7 procedure over the `media type` field: each tiered observation is a
weighted vote for one candidate (`photograph` or `screenshot`), the candidates are ranked, and the
winner must clear **both** the minimum score and the minimum margin. Conflicting signals that do not
clear the margin fill nothing and emit `unresolved` with reason `below_margin` — which is §2.6's own
requirement stated in P6's vocabulary: *"conflicting signals should lead to abstention rather than
an invented classification."* The tier-to-weight mapping is deferred with the other §3.7 weights.

Two absolutes carry over from §2.6 and are Done-means assertions: a **missing** EXIF signal is never
evidence for anything (P5 puts absence on `extraction_runs`, so no such observation exists), and OCR
text density is never a screenshot signal.

**Duplicate family and version family (§2.9, §3.11) — G5.** Both are universal facts; version family
had **no owner anywhere in the design**. P6 computes them from P1's content hashes and P5's
perceptual hashes, and from nothing else without an authored rule.

- **Duplicate family.** Byte identity. An exact `content_hash` match yields a `direct` fact —
  §3.13 names the content hash a Direct source. A perceptual-hash near-match yields at most
  `possible`: §2.6 distinguishes "duplicates and near-duplicates", and §8.3 is explicit that "a
  content-hash match supports deduplication review; a filename match alone does not."
- **Version family.** Requires **distinct** content hashes — identical hashes are a duplicate family,
  not a version family — plus a relation establishing shared lineage. It is never `direct`: no
  explicit slot states a version relation. A deterministic rule that passes a context check yields
  `validated`; anything weaker is `possible`.
- **The refusal is the load-bearing half.** A filename suffix alone never establishes either family.
  §8.5's adversarial suite names "duplicate suffixes on unrelated files"; §8.3 makes the same point
  for collisions. `report (1).pdf` and `invoice (1).pdf` share a suffix and nothing else.
- The version-family **signal set beyond these two hash inputs is deferred** — §2.9 lists
  "duplicate and version-family signals" and defines neither.

**The bounded download session (§3.9, §4.2) — G6.** P6 computes it from P3's `timestamps` and
`parent-folder context` (§2.9's name for §1.2's "directory position" — one field, MINOR 11) and emits
it on the `download_session` field as a **`possible` fact and never anything else**. §3.9 is unambiguous and every clause of it binds here:

- a session "should never be treated as proof of topic";
- it "should not carry the same confidence as a hash match or a directly extracted document fact" —
  so it may not be promoted to `validated` by any rule, and no §3.7 margin can raise it;
- it is "not a basis for automatic semantic propagation" — a session fact is written for the member
  file only and never copies any other file's facts onto it (§4.3, and P6's standing refusal of
  group-derived writes);
- being `possible`, it is excluded from the proposal-eligible read by construction (§3.6), so it can
  never reach a folder proposal.

P9 consumes it as `support_kind = bounded-session`, and §4.7's rule stands on P9's side: "a tight
download session alone is never sufficient." The session **boundary parameters** — the time window
and what makes a session "tightly bounded" — are deferred; the design states none.

**Photo events (§3.11 Photos `event`, §4.2) — G7.** §4.2 gives "a deterministic event created from
camera, time, and GPS metadata" as an example of a photo-group seed, and no part computed it. P6 does, as an ordinary
Photos-domain `event` fact — it is already a literal §3.11 field, so no new field is created.

- Inputs are P5's camera, capture-time and GPS EXIF observations only (§2.6: "Camera EXIF, GPS, and
  capture time can support deterministic photo-event proposals").
- Reliability is `validated`: the clustering is a deterministic rule that passes a contextual check,
  which is §3.13's definition. It is not `direct` — no slot states the event — and it must not be
  `possible`, because P9 requires a seed fact to be `Direct` or `Validated`.
- `event` values auto-create; §3.12 names "event" in its auto-create list explicitly.
- Absence of EXIF produces no event (§2.6). Tier-3 screenshot signals never contribute to one.
- Clustering parameters — time window, GPS radius, the camera-identity test — are **deferred**; the
  design names the inputs and states no thresholds.

P9 consumes the resulting `event` facts as seeds, which closes P9 Open question 11; P11 retrieves on
them under §6.3. **They are not "§4.2's fourth seed kind"** — an earlier draft said so, and the design
does not: §4.2's four kinds are a strongly identified file, a validated shared fact, a structural
family, and a user-created starting point, and the photo event appears there as an *example* of a seed,
not as a fifth category. Which of its existing `seed_kind` values P9 files it under is P9's to state;
P6 asserts only that the `event` fact is `validated` and never `direct` (§3.11, §3.13, G7).

### Read surface published to neighbours

| Read | Consumer | Guarantee |
|---|---|---|
| facts for a file, by state and domain | P9, P10, P11 | evidence refs are **observation keys**, resolvable to P4 rows across extractor upgrades (M14) |
| **proposal-eligible facts** — excludes `possible` and `rejected` | P10 (§5.4), P11 (§6.3) | §3.6: a weak clue can never reach a folder proposal through this surface |
| active field allowlist for a file | P8 (§3.5) | the model may propose nothing outside it |
| values in a field, with file counts | P10 (§5.5, §5.9) | supports "three schools, five terms, twelve course branches" before the user commits |
| a fact's full evidence chain back to observations | P11 (§6), review UI (§8.2) | every conclusion is inspectable to its origin |
| fact and value history, including superseded rows | P2 (§8.5), review UI | §8.2 |
| **`no_usable_facts(file_id, content_hash) -> bool`** | P5 (§2.2, §2.7), P2 (case A10) | M11 — see below |
| `unresolved` rows for a file, by field and reason | P2 (§8.5), P13 review surface | B7 — a refusal is readable as a refusal, not inferred from a gap |
| Photos-domain `event` facts | P9 (§4.2 seed), P11 (§6.3 retrieval) | `validated`, deterministic from camera/time/GPS (G7) |
| `download_session` facts | P9 (§4.2 `support_kind = bounded-session`) | never above `possible` (§3.9, G6) |
| `duplicate family` / `version family` facts | P9 (§4.2 structural family), P11, P12 (§8.3 collision review) | G5 |

**`no_usable_facts(file_id, content_hash) -> bool` (M11, §2.2, §2.7).** §2.2 permits targeted OCR on a
PDF with a non-empty but *broken* text layer only when its stored evidence yields no usable facts.
P5's spec says "P6's contract must accommodate it"; P2 asserts it in adversarial case A10. It is
accommodated here.

- **Keyed on `(file_id, content_hash)`**, not on the file — it is a statement about one file version,
  and it is re-evaluated after targeted OCR adds observations, because the new run changes the §3.4
  cache key.
- **Defined only after P6's deterministic pass on that content hash has completed.** Consulted
  earlier it would return `true` for every file and trigger OCR on the whole corpus.
- **Computed from the fact tables and nothing else** — the count of active facts at or above the
  usable threshold, `unresolved` rows being evidence *for* the verdict. This negative is load-bearing:
  §2.2 and §2.7 both forbid deciding it from text quality. §2.2: "The system should not use
  unreliable global language-quality checks that incorrectly punish multilingual or
  mathematics-heavy documents." §2.7: OCR runs "not because a broad quality heuristic says the text
  looks unusual."
- **It is a return value, not a request.** P6 answers when asked; P5 decides whether to run OCR.
- The **threshold** — which facts count as "usable", and how many — is a deferred configuration
  value (P5 Open question 1 flags that the design defines it nowhere).

### Write surface

Facts: P6 only. Values: P6 and user corrections. Fields: authored schema changes and user-approved
schema changes only — never runtime, never the LLM (§3.12, §3.5).

### Emitted to P2 — the stage-output envelope (§8.5)

**B7.** P2 was moved to Wave 1 precisely so this envelope would exist before the measured stages did.

P6 emits a P2 `stage_output` with `stage_id = factual_validation` (stage 2 of §8.5's ten), one per
subject it decides about, carrying `inputs[]` — the `subject_ref`s of the `extraction` stage outputs
it consumed — an explicit abstention value, a distinct budget-deferral value, and the version tuple.
`subject_ref` is the content hash (§8.2's identity for a file version).

| P6 result | `outcome` | `budget_state` |
|---|---|---|
| one or more facts written | `produced` | `within_ceiling` |
| every attempted field ended in an `unresolved` row with a non-budget reason | `abstained` | `within_ceiling` |
| an §8.6 ceiling stopped the work — `unresolved` reason `budget_deferred` | `deferred` | `ceiling_reached` |
| the stage failed | `error` | — |
| P6 not built yet | `not_implemented` | — |

The abstention and the budget deferral are **separate outcomes carrying separate `unresolved`
reasons**, which is the whole of B7's second half: without the `unresolved` row, §3.6's "no fact" is
a missing row and P2 cannot tell a considered refusal from a crash or a skip. The version tuple is
P6's slice of §3.4's cache key — extractor version, analysis tier, model identifier, prompt
fingerprint — and is what lets §8.5 replay a bundle against a changed prompt and attribute the diff.

## Deferred — manual design required

Everything below is content someone must author. The design names the slot; it does not fill it.
Nothing here is invented in this spec.

| Deferred item | Defined by | Note |
|---|---|---|
| The 200–300 domain template library | §5.7 | P10 owns the folder-template half; the *fact-schema* half of every library domain beyond the six §3.11 rows lands on P6 and does not exist yet. |
| **Career and recruiting** fact-schema fields | §3.15 names it a launch domain; §3.11 gives it **no** field row | A launch domain with no stated fields. §5.4's Career *template* (company → role/cycle → document type) is a folder dimension list, not a fact schema, and is not copied here. |
| **Identity, medical, legal** fact-schema fields | §3.15 (safety domains) | Named as safety domains; no fields stated anywhere. |
| The "several additional fields used only for search, privacy protection, explanation, or later review" | §3.11 | The design asserts these exist per domain and names none. |
| Gazetteer contents and the validation procedure that makes them "validated" | §3.7 | Universities, course-code formats, institutions, companies, labs, venues. Manual. |
| Minimum score and minimum margin values | §3.7 | The design requires both thresholds and states no numbers. Must be authored and then measured against §8.5's adversarial suite. |
| Positional weight per document zone | §3.7, §2.2 | Zones arrive from P4's `location`; the weights are manual. |
| Rule context-term lists beyond the five literal academic terms | §3.5 | Only "syllabus", "lecture", "credits", "instructor", "semester" are stated. Every other domain's context vocabulary is unauthored. |
| Date and academic-term regex catalogue beyond the three named patterns | §3.10 | `Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024` are stated. The rest is manual. |
| Per-field normalizers and alias tables | §2.8, §3.6 | `U Chicago` → `University of Chicago` → `UChicago` is one worked example, not a table. |
| Domain activation signals | §3.11 ("when the evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which evidence activates which domain is unauthored. |
| Allowed value sets for enum-like fields — work type, application document type, artifact type, record type, media type, stage | §3.11 names the fields | §5.5 shows Syllabus / Homework / Lectures as example branches, not as an authored enum. |
| `destination_eligible` assignment per field beyond the §3.8 authorship rule | §3.8, §3.11 | §3.8 settles authorship. Nothing settles the rest. |
| Residual library contents beyond the nine §7.3 names | §7.2–§7.4 | **P10** — M10 moved the residual-library definitions from P11 to P10; P11 keeps the §7.5–§7.11 workflow and its review surface. Where residual review needs facts, the nine named templates are the only authored set; user-defined residual areas (§7.3) are user content by design. |
| **Tool-generated producer/creator string list** | §2.2 | M4. Three are named literally — `python-docx`, `Mozilla/5.0`, "a browser-generated producer string". The full list is hand-authored. The *rule* that consumes it is not deferred and is stated above. |
| **The `no_usable_facts` threshold** | §2.2, §2.7 | M11, P5 OQ1. Which facts count as usable and how many. The design requires the verdict and states no threshold. |
| **Version-family signals beyond content hash and perceptual hash** | §2.9, §8.3 | G5. §2.9 lists "duplicate and version-family signals" and defines neither. The refusal (a filename suffix alone is never enough) is authored above; the positive rule is not. |
| **Bounded-session boundary parameters** | §3.9, §4.2 | G6. The time window and what makes a session "tightly bounded". §3.9 requires the clue and gives no numbers. |
| **Photo-event clustering parameters** | §2.6, §4.2 | G7. Time window, GPS radius, camera-identity test. §4.2 names the inputs and states no thresholds. |
| **Signal-tier weights for §2.6's three bands** | §2.6, §3.7 | M2. P4 assigns the tier; P6 owns what each tier is worth in §3.7's ranking. The numbers are manual and belong with the other §3.7 weights. |

## Done means

Each item is assertable against P4-shaped fixtures with no other part implemented.

**Schema**
1. `fields`, `values`, `file_facts` exist with the shapes above; `file_facts` contains no path,
   destination, folder, or group column (§3.14).
2. All six universal fields, `download_session`, all six §3.11 domain field sets, **§3.8's four
   role fields** (`authored_by`, `target_school`, `our_firm`, `client`) and **`capture_date`** are
   present, and no field outside them (§3.11, and the "such as" reading recorded under `fields`).
   Career and recruiting, identity, medical and legal have no field rows.

   > **Amended 2026-08-22.** Three changes, each closing a contradiction inside this document.
   > **(a) §3.8's roles are IN.** Round 1's F-1: the design names them outright and Done-means 13
   > and 22 both require `authored_by` to exist, so the old "no field outside them" made two of this
   > SPEC's own Done-means unwritable. **(b) `capture_date` is IN** (F3): Done-means 5 requires it,
   > §3.2 derives it from EXIF `DateTimeOriginal`, and it is distinct from both `creation_date`
   > (filesystem/document timestamp, §3.2's own contrast) and `capture_year` (§3.11's Photos
   > destination dimension). **(c) "and must not acquire any (S3)" is STRUCK** (D1, narrowed by
   > Joseph 2026-08-21): the deferral stands on its own, and a test forbidding the row made P6's
   > suite the thing that would reject a later deliberate reversal of S3 — a decision arriving as a
   > regression. They still have no field rows today; nothing may add one silently.
3. A new value auto-creates on first sight; a new field cannot be created at runtime by any
   producer, including the LLM path (§3.12, §3.5).

**Observation → fact**
4. Given the §3.2 fixture — filename `Syllabus BUSIB 4300 Spring 2026.pdf`, PDF title
   `BUSIB 4300 Syllabus`, page-one heading `Spring 2026` — P6 produces exactly the three facts
   §3.2 names (**`subject`**, term, work type), each with evidence refs to the observations that
   supported it, and each observation's `raw value` unchanged afterwards (§3.2, §2.8).

   > **Amended by D6, 2026-08-21.** This item said `course`. §3.2's own sentence is *"the system can
   > create facts such as subject = BUSIB 4300"*, and §3.1 and §3.12 agree; only §3.11's Academic
   > row says "course". The stored field key is `subject` -- a field key is a join handle and two
   > spellings are two columns -- and §3.11's word survives inside quotations as prose for the same
   > field. The `fields` catalogue carries a `subject` row and no `course` row.
5. An EXIF `DateTimeOriginal` observation produces `capture date` as a `direct` fact, and the EXIF
   observation remains separately readable (§3.2).
6. P6 resolves a fixture whose `source type` is unknown to it, with no per-format branching
   anywhere in the part (§2.8).

**Refusals — these are the point of the part**
7. `submit` produces no `MIT` fact; `uncertainty` produces no `UNC` fact (§3.7, §8.5).
8. A course-code-shaped string with no academic context term in its surrounding context produces no
   `subject` fact (§3.5). Positively: the same string with `context_before: "Syllabus — "` — P4's
   skeleton fixture 1, capital S — **does** produce one, because the §3.5 context check is
   case-insensitive (N-6, B8(a)).
9. Two candidates within the margin of each other fill nothing (§3.7).
10. `v2024`, a build number, and a ZIP code produce no date fact; `Spring 2025`, `AY 2024-25`, and
    `Michaelmas Term 2024` each produce exactly one term fact (§3.10).
11. An LLM proposal citing a quote absent from `evidence` produces no fact; a proposal naming a
    field outside the active schema produces no fact; a proposal contradicted by an existing
    `direct` or `validated` fact produces no fact (§3.6).
12. A `possible` fact is absent from the proposal-eligible read (§3.6) and a session-derived clue
    never exceeds `possible` (§3.9).
13. An `authored_by` value is never returned as destination-eligible (§3.8).

**Multi-fact and history**
14. One file simultaneously holds `project`, the active domain's document-type field, `purpose`,
    and `target_school` with no field dropped and no domain forced to win (§3.11).

    > **Amended 2026-08-22 by D8 and the `document type` ruling.** This item said `document type`
    > and `target university`. Neither is a stored field key, so as written the item could not be
    > tested — it named two things the `fields` catalogue does not contain. `document type` is
    > whichever field the active domain declares (`application_document_type` for College
    > applications, `artifact_type` for Research/Code); the school concept's stored key is
    > `target_school`, with "target university" an alias. §3.11's worked case is unchanged —
    > only the names this item is checked against are.
15. Re-resolution under a bumped extractor version or a changed prompt fingerprint creates a new
    fact that supersedes the old one; the old fact, its state, and its evidence remain readable,
    with the reason it was superseded (§3.4, §8.2).
16. A rename with an unchanged content hash triggers no re-resolution; a content change does
    (§3.4, §8.2).

**Deterministic operation**
17. The whole of items 4–10, 13–16 and 18–27 pass with P8 absent and no model configured — the
    Wave 2 requirement and the walking skeleton's `P6 resolve it to ONE validated fact
    (subject = X) with its evidence link`.

    > **Amended by D6, 2026-08-22.** This quoted the walking skeleton's pre-D6 wording,
    > `course = X`. `02-segmentation-map.md:190` now reads `subject = X`, and the stored
    > field key is `subject` everywhere. Caught by a Task 27 author, whose guard asserts
    > `"(course = X)" not in text` so it cannot silently return.

**Abstention is a record, not a gap (B7)**
18. Every refusal asserted in items 7–12 also writes an `unresolved` row naming the field attempted
    and a reason; no refusal leaves only a missing row (§3.6, §8.5).
19. An `unresolved` row is absent from every fact read including the proposal-eligible read, carries
    no value, and is not a `possible` fact.
20. An §8.6 ceiling produces `reason = budget_deferred` and `stage_output.outcome = deferred` with
    `budget_state = ceiling_reached`; an evidence-based refusal produces `outcome = abstained`. The
    two are distinguishable from the records alone (§8.6, §8.5).
21. P6 emits a `stage_output` with `stage_id = factual_validation`, a populated `inputs[]`, and the
    version tuple, for a file that produced facts and for a file that produced none.

**The new facts**
22. A `Producer` value of `python-docx` produces no fact in any field and one `unresolved` row with
    reason `discounted_tool_metadata`; a human author name in the same slot may populate
    `authored_by` and no other field, and is never destination-eligible (§2.2, §2.3, §3.8, §8.5's
    "generic author metadata").
23. Two byte-identical files share a `direct` duplicate-family fact; two files sharing only a `(1)`
    filename suffix share none (§8.3, §8.5).
24. Files with distinct content hashes never receive a version-family fact from a filename suffix
    alone, and never receive a `direct` one at all (§2.9, §8.3).
25. A session-derived `download_session` fact is `possible`, is absent from the proposal-eligible
    read, and no rule promotes it (§3.9).
26. A camera/time/GPS cluster produces a `validated` Photos `event` fact usable as a P9 seed; an
    image with no EXIF produces none (§2.6, §4.2).
27. Tier-1 and tier-3 image signals in conflict fill no `media type` and emit `unresolved` with
    reason `below_margin`; a missing EXIF signal contributes nothing to either candidate (§2.6).

**Reads and pointers**
28. `no_usable_facts` returns `false` for a file with one active usable fact and `true` for a file
    whose evidence produced only `unresolved` rows; it is computed from the fact tables and no text-
    quality heuristic appears anywhere in its implementation (§2.2, §2.7).
29. A superseding fact carries `preferred = true` and the superseded row `preferred = false`, both
    rows remain readable, and `preferred` appears in no contradiction check, no margin comparison,
    and no destination-eligibility decision (§8.2, M1).
30. Every `evidence_refs[]` entry is an `observation_key`; re-running the same extractor at a bumped
    version leaves every stored reference resolvable (§8.7, M14).

## Cross-cutting answers

### Provenance (§8.2)

**Events P6 appends** — `fact creation` and `fact rejection`, both named literally in §8.2's event
list. Each carries event type, file ID, content hash, responsible subsystem, extractor or model
version, prompt fingerprint where applicable, user identity for explicit user actions, time of
observation, and a structured explanation or evidence reference (§8.2). Value creation, value
merge/alias, and user fact correction are also P6 actions and are appended with the same record
shape.

**What P6 never overwrites** — evidence rows (read-only to P6, §3.2); any prior fact row; any prior
reliability state; any raw value. §8.2's rule is exact and P6 is its principal case: "a newer result
should **supersede** an earlier result while retaining the old observation and the reason it was
superseded." The design's own example is P6's: a first OCR pass produces unreadable text, a later
engine recovers a university name — both extraction records remain, the resolver marks the newer
value preferred, and a user reviewing a placement can still inspect the origin of the conclusion.

The `preferred` marking in that sentence is the `file_facts` column M1 places on P6 and nowhere
else; the rule for setting it is in Contract out. In the same example, the first pass's failure is
now an `unresolved` row rather than an absence (B7), so the record shows *that* the first pass was
attempted and why it yielded nothing.

The `unresolved` table is P6 state read by P2 (§8.5) and the review surface; **P6 claims no new §8.2
event type for it.** §8.2's list names `fact creation` and `fact rejection`, and an abstention is
neither — it is the recorded absence of both, and `stage_output` already carries it to the harness.

Value merges are aliases, never deletions (§0 taxonomy aliases). A `rejected` fact is retained, not
removed (§8.7).

### Budgets and degradation (§8.6)

**Ceilings that bind P6** — from §8.6's list: maximum LLM calls per thousand files, maximum model
cost per scan, maximum dossier tokens per model call. These gate P6's requests into P8; P6 must be
able to report how many fact-resolution requests it deferred against each.

**Degradation order** — §8.6 states it and it is P6's internal order: direct facts and
high-precision rules run first because they are cheap and reliable, and LLM calls are reserved for
bounded ambiguities. So P6 always attempts `direct`, then `validated`, and only then, budget and
privacy permitting, `llm_supported`.

**On exhaustion** — P6 retains the extracted evidence, marks the fact-resolution stage deferred for
that file, and leaves the field `unknown` and the file in review. It does **not** substitute a
weaker route for a stronger one: a field that was only ever reachable by LLM interpretation stays
empty rather than being filled from a `possible` clue, a below-margin facet candidate, or a fuzzy
date. §8.6 is unconditional here — "cost exhaustion must never turn into lower-quality automatic
classification" — and the reporting requirement is P6's too: deferred fact work must be visible as
deferred, never as "understood and found unimportant". That requirement is now discharged by two
concrete records rather than by intent: an `unresolved` row with `reason = budget_deferred`, and a
`stage_output` with `outcome = deferred` and `budget_state = ceiling_reached`. Neither is reachable
from an evidence-based refusal, which reports `abstained`.

### Correction learning (§8.7)

**Actions P6 records** — accepting a proposed fact; correcting a value; renaming a value; merging
two values; rejecting a fact; entering a fact directly. Each produces a `user_confirmed` fact, which
outranks every other state (§3.13), or a `rejected` fact retained with the evidence that produced
it (§8.7).

**Scope** — every correction record carries one of §8.7's six scopes: file / group / node /
template / domain / corpus. Two of §8.7's worked examples are P6's own:

- *File scope:* one particular transcript belongs in a Columbia packet — this must not teach the
  engine that all transcripts belong there.
- *Corpus scope, and it is a §3.8 role:* if the user repeatedly rejects an association between their
  authoring school and application documents, the product may lower the role or weight of
  author-affiliation evidence across that corpus. P6 owns that weight because P6 owns the role
  distinction.

**Negative feedback is mandatory storage** (§8.7). Rejected facts persist with their evidence so the
same attractive-but-incorrect conclusion is not resurfaced. **Before writing a `file_facts` row that
would revive a rejected claim, P6 queries P1 `learning_records`** for `proposal_class = fact` and
`basis_key = (file_id, field, value_id)`. A matching unresected reject leaves the `rejected` row in
place and does not re-propose. [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md). Learned
preferences must be inspectable and resettable (§8.7). P6 performs no global training on the user's
corpus (§8.7).

### Plan versioning (§8.8)

§8.8 settles this directly: "The evidence database remains shared across plan versions." Therefore:

**Shared across all plan versions, not versioned** — `fields`, `values` identity, `file_facts`, all
evidence refs, all reliability states, and all supersession history. Facts are what the system knows
about the corpus; they do not change because the user renamed a branch.

**Belongs to a plan version** — the value's **display label and aliases**. §8.8's plan-version
record lists "User labels and aliases" literally, so `UChicago` vs `University of Chicago` as a
rendering choice is plan-versioned while the underlying value and every fact pointing at it are not.
Template versions and ordering (P10), and accepted/rejected group memberships (P9), are also
plan-versioned and are not P6 state.

**Consequence P6 must honour** — a new plan version never re-resolves, invalidates, or reclassifies
existing facts (§8.8: "A new plan should never silently reclassify or move old files"). Switching or
restoring a plan version changes which projections are valid, not what is known.

## Open questions

Numbered; those marked **[seam]** threaten another part's contract and should be settled in the
joint review, not later.

1. ~~**[seam]** `analysis tier` is never defined.~~ **Settled — I4.** Closed vocabulary
   `filesystem | native | ocr | llm`, owned by P5, consumed here in §3.4's cache key. It is a
   process identity, not §8.6's degradation ladder: native and OCR share a ladder rung and must
   not share a cache slot. [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md).
3. Is `purpose` a universal field or an Applications-domain field? §3.9 requires it to be
   "first-class"; §3.11's universal list omits it and places it only under College applications.
4. ~~Are `subject` (§3.1's `subject = BUSIB 4300`, §3.12's field list) and `course` (§3.11's
   Academic row) the same field under two names, or two fields?~~ **CLOSED — D6, 2026-08-21: one
   field, and its stored key is `subject`.** A field key is a join handle, so two spellings would be
   two columns. §3.11's "course" is the design's prose for the same field and survives inside
   quotations; the `fields` catalogue carries `subject` and no `course`.
5. Finance has a fact schema in §3.11 but is a *safety* domain in §3.15, "detected and protected
   before any cloud or automated placement decision is allowed". Does the Finance fact schema
   activate at launch, or does detection-and-protection precede any field extraction? **[seam with
   P7.]**
6. **Multiplicity.** `people` (§3.11 Photos) and `language` are plainly multi-valued, but §3.12
   describes a fact as connecting "one file to one field and one value" and §3.7 speaks of a margin
   over the second-best candidate before a facet is "filled". May one (file, field) hold several
   simultaneously active values, and if so how does the §3.7 margin rule apply when more than one
   candidate is correct?
8. §3.12 forbids automatic field creation; §5.7 lets an LLM-generated custom template propose a
   schema with "allowed fields" that the user reviews and may save as a reusable personal template.
   Does user approval of a custom template create `fields` rows, and at what scope — corpus-wide or
   plan-version-local? **[seam with P10.]**
9. **[seam]** §4.7 permits the LLM to conclude `purpose = university application submission` for a
   packet, while §4.3 forbids automatic propagation of facts onto members. After the *user accepts*
   the group, does that purpose become a fact on non-anchor members, or does it remain membership
   only?
10. §3.13 orders the six states but does not define the comparison for two equal-rank contradicting
    facts — two `validated` facts asserting conflicting course codes on one file. Reject both,
    surface both as competing candidates, or defer to the internal score §3.13 permits but declines
    to make authoritative?
11. ~~**[seam]** `sensitivity status` is a universal *fact* (§3.11), a *sensitivity state* on the
    file record (§8.2), and a *handling class* in the privacy gate (§8.4). One record or three?~~
    **CLOSED — D2, 2026-08-21.** P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is
    authoritative. `files.sensitivity_state` is its projection, written through P1's
    `set_sensitivity_state`. `Unreadable or unclassified` is a **gate outcome, not a file fact**, so
    it never enters that column. P7 authors its own §8.4 audit record and P1 stores (M8).

    **Two residues, both still open.** Whether P6 keeps a `sensitivity status` field row beside P7's
    record — round 1 F-2 found it has no producer, so create none until asked (NEEDS-JOSEPH C5).
    And whether a user reclassification arrives as a `user_confirmed` fact, which D2 did not reach.
12. **[seam]** §2.8's observation record ends with a "reliability state" field, and §3.13 defines six
    reliability states for *file facts*. Do observations use the same six-value enum, a different
    one, or is the §2.8 field something else? P4 and P6 must agree before either is frozen.
    *Status:* **CLOSED — ratified by Joseph 2026-08-20 (C1).** One vocabulary: §3.13's six states,
    and extractors may stamp only `direct` and `possible` (P4 D11). P6 **states** this rather than
    re-asking it; a seventh state or a separate observation-level vocabulary is now a contract
    revision, not an open alternative. P6's rules were already written to be correct under this
    answer, so nothing in this SPEC changes but the status of the question.
    Consequence P6 must carry: catalogue 01 (`planning/deferred-catalogues/`) is the suppression
    list this vocabulary uses — a match yields no fact in any field, `unresolved` with reason
    `discounted_tool_metadata`, never a demotion to `possible`. It is INJECTED data, never imported
    into `src/extractors/`.

**Closed by `04-resolutions.md`** — retained here so other specs citing these numbers still resolve.
The numbering above is left with gaps rather than shifted, because P2, P4 and P5 cite these by
number.

- **2 — who owns §3.6 validation.** Closed by **O6**: P8 owns the mechanism and the verdict; P6 owns
  the inputs (active field allowlist, citable observation set, existing `direct`/`validated` facts,
  per-field normalizers) and the consequence of each verdict (pass → `llm_supported`; `unknown` or
  any failed check → no fact and an `unresolved` row; useful-but-weak → at most `possible`). Both
  specs already said this; the assignment in this part's brief was the error. Contract in from P8 is
  correct as written and needs no change.
- **7 — who computes the bounded download session.** Closed by **G6**: P6 computes it, from P3's
  `timestamps` and `parent-folder context` (MINOR 11). The second half is answered too — it **does**
  persist as a fact row, on the `download_session` field, and never above `possible` (§3.9, §3.13).
