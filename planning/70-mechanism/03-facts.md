# 3. From evidence to facts

P6 is the part that turns *what a document said* into *what the product believes about
the file*. P5's extractors produce readings; P4 freezes each reading into an immutable
observation; P6 decides which of those readings may be asserted as a claim, records the
claim beside the exact evidence that justifies it, and stamps it with one of six
reliability states. Everything downstream — grouping (P9), tree design (P10), placement
(P11), the review surface (P13) — reads facts, never raw text
(`planning/parts/P6-facts-facets/SPEC.md:7-12`).

The code lives in `src/facts/` (29 modules, ~6,100 lines). Four tables are the published
product: `fields`, `values`, `file_facts`, `unresolved` (`src/facts/__init__.py:3-6`).
Two more exist as internal bookkeeping: `fact_passes` and `value_renderings`
(`src/facts/schema.py:194-222`).

This section describes the machine. Where the shipped deployment exercises only a
fraction of it, that is stated rather than glossed; the last two subsections are a list
of what nothing calls and what looks wrong.

---

## 3.1 An observation is not a fact, and they are different records

The distinction is the load-bearing one in the whole part, and it is a *storage*
distinction, not a naming convention.

An **observation** is P4's: a content-addressed record of a reading, immutable, with
`raw_value` preserved verbatim. P6 never writes the `evidence` table, never edits it,
never re-normalises it. P4's `evidence_never_overwritten` trigger makes that
unfalsifiable rather than merely promised
(`src/facts/resolver.py:245-247`, SPEC line 141).

A **fact** is P6's: one row in `file_facts` connecting one file version to one field and
one value, carrying the reliability state and the citation list that justify it
(`src/facts/file_facts.py:2-4`).

The design's worked example is the university name, implemented as three columns on one
`values` row rather than one field overwritten three times (`src/facts/values.py:16-19`,
quoting §2.8):

> "If a document says U Chicago, the raw observation remains exactly that wording, while
> a resolver may normalize it to University of Chicago and the user may later choose to
> display it as UChicago."

- `canonical_value` — the resolver's normalised form.
- `raw_variants[]` — every raw wording ever seen, byte-exact
  (`src/facts/values.py:156-170`; `add_raw_variant` refuses an empty string and records
  each wording once).
- `display_label` — the user's preferred rendering (`src/facts/values.py:173-188`).

None of the three overwrites another — which is what lets a later resolver reinterpret
without destroying what the earlier one saw.

The separation is enforced at the write, not by discipline. `write_fact` refuses a
non-`user_confirmed` fact with no citation ("only a user_confirmed fact may stand
without one"), and refuses any citation that is not a P4 observation *key* — `sha256:`
plus 64 hex (`src/facts/file_facts.py:126-136`).

The citation is the **key**, never the row id. The key hashes content hash, extractor
name, locator and raw value — and deliberately *excludes* `extractor_version` — so a
citation recorded today still resolves after an extractor upgrade
(`src/facts/file_facts.py:24-27`; `src/facts/read_surface.py:224-230`). A fact whose
provenance cannot be resolved is refused at write time; a citation that resolves to
nothing at read time raises `DanglingCitation` rather than returning a shorter list,
because "returning a shorter list would let an evidence-walk check pass by counting
zero" (`src/facts/read_surface.py:82-88`).

`fact_id` is content-addressed over the whole conclusion — file, hash, field, value,
state, origin, cache key, sorted citations (`src/facts/file_facts.py:163-170`). Writing
the same conclusion twice is one row and one event. A second write at the same identity
that *diverges* on a non-identity column (`active`, `model_identifier`,
`rejection_reason`, …) is refused outright rather than silently dropped
(`src/facts/file_facts.py:173-192`).

---

## 3.2 The field catalogue

### What a field is

A field is the product's long-term organisation language: `subject`, `term`,
`authored_by`, `client`, `capture_year`. A value is the user-specific content discovered
inside their files: `PHYS1401`, `Spring 2026`, `University of Chicago`. §3.12 makes the
asymmetry a rule — **values may auto-create, fields may not**:

> "The system may create new values when it sees a new course, project, company,
> university, or event, but it should not invent new fields automatically."
> (`src/facts/fields.py:4-6`)

That is enforced by there being no code that could do otherwise. There is no
`add_field`, no `register_field`, and no producer path that inserts a `fields` row;
`create_fields` loads a module-level authored table and is the only writer
(`src/facts/fields.py:9-13`, `src/facts/fields.py:659-677`). `get_field` raises
`FieldNotInCatalogue` for an unknown key (`src/facts/fields.py:680-697`), and both the
value path and the abstention path route through it — so creating a value is not a back
door into creating a field (`src/facts/values.py:91-98`), and neither is recording a
refusal (`src/facts/unresolved.py:83-94`).

Field keys are `snake_case`, ratified as D6 (`planning/parts/_PLAN-AUTHORING-BRIEF.md:79`).
Every stored key in `FIELD_ROWS` obeys it.

### `planning/domains/canonical_fields.json` is a source, not a dependency

The file exists — 37 field definitions with `key`, `type`, `role`, `role_split_with`,
`destination_eligible`, `aliases` and a grep-verified `00_cite` each — and **nothing in
`src/` imports it**. Greping for `canonical_fields` or `planning/domains` returns only
prose comments (`src/tree_design/catalogue.py:4`) and memo strings inside a template
library JSON: no loader, no path, no read. The catalogue in `src/facts/fields.py` was
*read from* that file when the plan was written and then written down as Python
literals — "**`planning/domains/` is not this catalogue and is never imported.** That
directory is a research artifact" (`src/facts/fields.py:15-21`).

The distinction changes what a mistake looks like. Loaded at runtime, editing a research
artifact would silently change what the product believes; transcribed, a divergence is a
code change with a diff, and each departure is recorded beside its row — two of them:
`sensitivity_status` withheld and `capture_date` added (`src/facts/fields.py:17-19`).
The cost is that the two *can* drift and nothing detects it.

### The shipped set

56 rows, verified by executing the module — the original 37 plus 19 minted by
`planning/60-VOCABULARY-RULINGS.md` §4 (`src/facts/fields.py:576-596`).

Six universal fields apply to every file: `file_type`, `creation_date`, `language`,
`duplicate_family`, `version_family`, `download_session`
(`src/facts/fields.py:598-600`). §3.11 names six universals, but its sixth —
`sensitivity_status` — is deliberately absent, and the module says so in the strongest
terms a comment allows: "This is knowingly at odds with SPEC Done-means 2's 'all six';
do not close it by adding the row" (`src/facts/fields.py:137-139`). `download_session`
is P6's one recorded addition, required by §3.9 and §4.2. The remaining 50 are scoped:
`academic` (5), `college_applications` (4), `research` (5), `finance` (5), `photos` (7),
`code` (2), §3.8's four role fields at universal scope, and the professional schemas'
19.

### Declaration scope versus reference

Two different questions, kept apart on purpose. `FieldRow.scope` records where a key is
**declared**; `DOMAIN_FIELDS` records which schema **references** it
(`src/facts/fields.py:621-670`). `project` is declared at `research` and referenced by
eight schemas; `record_type` is declared at `finance` and referenced by seven. Five
schemas — `creative`, `retail_hospitality`, `government`, `nonprofit`,
`clinical_practice` — declare *nothing* and reference a real field set (verified by
execution).

This is why `active_field_allowlist` is built on `DOMAIN_FIELDS` and not on declaration
scopes. Under the older rule, activating `creative` would have allowed the model to
propose no field at all, "and §3.5 would have been enforcing a schema nobody wrote"
(`src/facts/domains.py:146-154`). The bug it replaced was narrower and real: an active
Code file could not be proposed a `project`, because `project` is declared at `research`
(`src/facts/domains.py:148-150`).

### Destination eligibility

`destination_eligible` answers one question: **may this field ever become a folder
level?** It is a property of the *key*, not of a template.

39 of 56 fields are eligible; 17 are not (verified by execution): the six universals,
plus `authored_by`, `our_firm`, `instructor`, `account_holder`, `people`,
`camera_information`, `capture_date`, `programming_language`, `organization`,
`workforce_unit`, `subject_of_record`. The reasons are heterogeneous and each is
recorded:

- **Authorship.** §3.8: the product "should avoid using authorship or creator identity
  as a destination dimension", so `authored_by` and `our_firm` are never eligible. D9
  splits §3.8's four roles two and two: `target_school` and `client` are *targets*, not
  authorship, so both **are** eligible (`src/facts/fields.py:39-45`; an earlier reading
  had all four FALSE — `planning/parts/_PLAN-AUTHORING-BRIEF.md:547`).
- **Privacy.** `people` is barred because "person-folders are privacy-loaded (§8.4).
  Widening either is Joseph's call, never a schema's" (`src/facts/fields.py:344-346`).
  `subject_of_record` carries the same bar on the key rather than per template: "a folder
  bearing the subject's name discloses membership of a matter, personnel, grant or
  clinical file" (`src/facts/fields.py:562-570`).
- **Structure.** `programming_language` is barred because "scattering a project by
  language would break" the structural unit (`src/facts/fields.py:364-367`).
- **Seeded false, promotable later.** `organization` and `workforce_unit` are seeded
  ineligible and marked template-time promotable: a folder of everything one company
  produced is "the collection point §3.8 forbids", while §00 still puts a company first
  in a folder template (`src/facts/fields.py:428-437`).

The read that answers the question refuses to guess: `is_destination_eligible` raises
`FieldNotInCatalogue` on an unknown field rather than answering `False`, "so a typo
cannot read as a policy" (`src/facts/read_surface.py:307-315`).

### Four authored columns that are not stored

`FieldRow` carries `reliability_ceiling`, `aliases`, `role_split` and `notes` beyond the
seven stored columns, and none is written to the table: `FIELDS_COLUMNS` is deliberately
shorter, and `create_fields` names its seven columns explicitly so a new dataclass field
cannot leak into the INSERT (`src/facts/fields.py:77-109`,
`src/facts/fields.py:109-117`, `src/facts/fields.py:666-676`). The rationale is "a
column with no reader is a claim the product does not make"
(`src/facts/fields.py:95-99`) — which is also why they are worth flagging: 19 rows carry
a `reliability_ceiling` (`account_holder` → `possible`, `consignment` → `validated`, …)
and nothing in `src/` reads it. A ceiling no producer consults caps nothing.

---

## 3.3 Reliability states, and the ladder

Six states, spelled once, in `src/facts/states.py`. The module re-exports P4's
`RELIABILITY_STATES` as the *same object*, not a copy, so the two cannot drift
(`src/facts/states.py:9-11`, `src/facts/states.py:30-34`).

| State | What it means (§3.13) |
|---|---|
| `user_confirmed` | Explicitly accepted, entered, renamed, merged or corrected by the user |
| `direct` | Read from a reliable, explicit source — content hash, EXIF timestamp, document title, labelled form field |
| `validated` | Found by a deterministic rule that passed contextual checks |
| `llm_supported` | Proposed from a bounded evidence packet, cited exact supporting text, passed deterministic validation |
| `possible` | A useful but insufficient clue — a short download session, a low-confidence match |
| `rejected` | A proposal the user or validator marked incorrect |

**The producer is a column, not a schema.** One `file_facts` table, one set of six
states. §3.5: "A file fact is not inherently rule-based or LLM-based. It is the common
format into which both systems write their conclusions"
(`src/facts/file_facts.py:5-8`). There is no rules table and no model table; `origin`
records which of five producers wrote the row — `deterministic_extractor`, `rule`,
`llm_interpretation`, `user_correction`, `user_approved_folder`
(`src/facts/file_facts.py:69-82`).

**`rejected` has no strength.** `STRENGTH_ORDER` holds five states, weakest first, so
`strength()` is an index and a larger number means stronger
(`src/facts/states.py:50-59`). `rejected` is absent from it by construction, and asking
for its strength **raises**:

```python
raise NotInVocabulary(
    f"{EXCLUDED_STATE!r} is §3.13's exclusion, not a rank: 'a proposal that "
    f"the user or validator marked as incorrect'. Compare membership, never "
    f"strength — a rejected fact that merely ranked below 'possible' would be "
    f"resurfaced by any comparison that picks the strongest candidate (§8.7).")
```
(`src/facts/states.py:73-78`)

§8.7's named failure is that without stored negative feedback the system "will
repeatedly resurface the same attractive but incorrect grouping". A `rejected` fact that
merely sorted last would be resurfaced by any "pick the strongest candidate" comparison;
making the question raise removes that failure mode from the code rather than from the
reviewer's memory.

**Proposal eligibility is derived, not spelled.** `PROPOSAL_ELIGIBLE_STATES` is
`STRENGTH_ORDER[1:]` — slice off the weakest and `rejected` is already absent, so one
slice drops both exclusions and no state name is written down in the read module
(`src/facts/read_surface.py:62-79`). The four eligible states are therefore
`llm_supported`, `validated`, `direct`, `user_confirmed`.

The comment beside it records a real near-miss: the plan's own task body said
`STRENGTH_ORDER[:-1]` and called the last member the weakest, which "would have excluded
`user_confirmed` — a user's own answer — from every folder proposal while still
excluding nothing weak" (`src/facts/read_surface.py:75-78`). Shipped code went the other
way.

`rejected` stays **readable but not proposable**. `facts_for` returns it unfiltered,
because "the review UI has to be able to see what was rejected or §8.5's 'Did it abstain
when evidence was absent?' is unanswerable from the outside"
(`src/facts/read_surface.py:113-116`). `proposal_eligible` excludes it.

**What actually writes each state.** Grepping every `reliability_state=` in `src/facts/`:
`direct` (`direct.py:149`, `families.py:177`), `validated` (`rules.py:163`,
`facets.py:210`, `photo_event.py:219`), `possible` (`session.py:217`,
`families.py:239`), `llm_supported` (`llm_seam.py:279`). **Nothing in `src/` writes a
`user_confirmed` or a `rejected` fact into `file_facts`.** `privacy/learning_seam.py:254`
writes `USER_CONFIRMED` into P7's `ClassificationRecord`, a different table with its own
vocabulary; `grouping/vocabulary.py:182` has a `rejected` that belongs to group
*acceptances*, not to facts. The two user-side states are reachable through `write_fact`
but nothing calls it with them.

---

## 3.4 The three-stage resolver

`FactResolver` is P6's single entry point and sequences three producers in §8.6's order:
`direct`, then `rule`, then `llm` (`src/facts/resolver.py:1-17`;
`DEGRADATION_ORDER` at `src/facts/budgets.py:48`).

The order is a contract: "Direct facts and high-precision rules run first because they
are cheap and reliable" (`src/facts/resolver.py:5-7`). Degradation is *subtraction,
never substitution* — by the time any ceiling is consulted, `direct` and `rule` have
already run, so the only route a ceiling can close is the model route and there is no
cheaper fallback (`src/facts/budgets.py:9-13`). The resolver imports none of the
producers; each arrives as an injected callable of one shape, so no threshold,
gazetteer, regex catalogue or producer-string list can reach it
(`src/facts/resolver.py:9-12,34`).

### `None` means the route does not exist

The constructor requires the stage map to be exactly the three producers
(`src/facts/resolver.py:141-145`), but a stage may be `None`:

> "`None` means the route does not exist — which is the ordinary case for `llm`, because
> P8 does not exist. A route that does not exist is NOT a route that was barred: nothing
> is withheld, nothing is deferred, and no `unresolved` row is written for it."
> (`src/facts/resolver.py:105-109`)

The loop honours it at `src/facts/resolver.py:186-187`: `if stage is None: continue`, before
any privacy or budget gate is consulted. The distinction is between "we could not do
this" (which owes the user a row) and "this product has no such route" (which owes
nothing, because nothing was attempted).

### What that produces on a real run

The shipped deployment binds **`direct` only** —
`stages={"direct": _direct_stage, "rule": None, "llm": None}` (`src/cli.py:323-325`,
docstring at `src/cli.py:316-321`). The one direct slot reads an identifier out of body
or heading text into `subject` (`src/cli.py:207-213`). Every other injected authority is
a stub: `pending_fields` returns `()`, `budget_exhausted` returns `False`,
`model_route_permitted` returns `False`, and `screen_metadata` is a no-op lambda
(`src/cli.py:325-332`); `METADATA_SCREEN` is empty on both catalogues
(`src/cli.py:214-215`).

So on a real run: one producer runs, `subject` facts are written at state `direct`, one
`fact_passes` row is recorded, and **no `unresolved` row is ever written**. Not because
the run refused nothing — because the two paths that write refusals in this composition
are both disabled. `screen_metadata` is a no-op, so `discounted_tool_metadata` cannot
fire; `pending_fields` returns the empty tuple, so even if a stage *were* barred,
`_write_bars` would loop over nothing (`src/facts/resolver.py:250-257`).

The bookkeeping matters for P2's replay: the resolver snapshots the `unresolved` ids
that existed *before* the pass and subtracts them afterwards, so `reason_counts` reports
**this pass's** rows and not the version's whole history — a second resolve of one
version used to write one row and be charged two, breaking the byte-stability of the
§8.5 payload (`src/facts/resolver.py:161-171,215-222`). `version_has_unresolved` answers
the other question — the *state* of the version — separately
(`src/facts/resolver.py:80-86`).

`record_pass` is called only after every stage has returned. A producer that raised
skips it, so `no_usable_facts` still raises `FactPassNotRun` rather than answering from
a half-written table (`src/facts/resolver.py:209-213`).

---

## 3.5 Suppression versus demotion

This is the pair the design most wants a reader to get right, and getting it backwards
is the mistake `src/facts/discount.py` is explicitly written against
(`src/facts/discount.py:3-5`).

Both tiers key on the same thing: P4's `location.zone == metadata` plus the
`field`-kind segment's label — `Producer`, `Creator`, `Author`, `Last Modified By` and
per-format equivalents (`src/facts/discount.py:88-98`).

**Suppression (§2.2).** A generic *tool* string — `python-docx`, `Mozilla/5.0`, a
browser-generated producer string — produces **no fact in any field**, `authored_by`
included, plus one `unresolved` row with reason `discounted_tool_metadata`
(`src/facts/discount.py:7-14`). The reasoning is that not-meaningful is not the same as
weak:

> "a tool name is a true fact about the software and no evidence about the document, so
> there is nothing for a `possible` fact to be weak about, and letting one into §3.7's
> ranking starts a contest §2.2 says should never start."
> (`src/facts/discount.py:11-14`)

**Demotion (§2.3, §3.8).** Any other producer/creator/author value — a human name — is
**kept**. It may populate `authored_by` and no other field; it is never
destination-eligible; and it gets **no** `unresolved` row, because "an abstention that
did not happen must not be recorded as one" (`src/facts/discount.py:16-21`). The
permitted set is one key wide: `AUTHORSHIP_FIELDS = ("authored_by",)`
(`src/facts/discount.py:78`).

The two tiers collapse into one predicate, `field_permitted`: a suppressed value
supports nothing, a demoted value supports `authored_by` and nothing else, and an
observation the discount does not read is not this module's to restrict
(`src/facts/discount.py:114-129`).

### Why the difference matters to a person

Two Word documents. One has `creator = python-docx` because a script generated it; the
other has `creator = <a former colleague's name>`, who wrote the first draft three years
ago.

Under suppression the first gets no `authored_by` fact and one visible row saying the
product looked at that slot and refused it — the person can see *why* the field is
empty. Under demotion the second gets `authored_by = <colleague>` as supporting evidence
— kept, inspectable, searchable — but it can never become a folder named after that
person. §2.3's reason is the binding one: the value "may identify a prior editor, a
document template, or a script rather than the meaningful subject or purpose of the
file" (`src/facts/discount.py:17-20`).

Collapse the two and you get one of two bad products: a folder tree with a
`python-docx` branch in it, or a product that discards the one piece of authorship
information a person might actually want to search on.

### Two things about the ordering

`screen_metadata` fires **before any producer** and is required by the constructor with
no default (`src/facts/resolver.py:110-114`, called at `src/facts/resolver.py:182`).
Without it `python-docx` can become a `direct` fact, because `direct` describes the
*slot* and not the value's usefulness — P4's own fixture 6 marks `python-docx` as
`direct` for exactly that reason (`src/facts/direct.py:6-9`).

But the screen's return value is **not** the whole story, and the resolver says so:

> "While the return value here was treated as the whole story, `python-docx` reached
> `subject` as a `validated` fact with the row beside it saying it had been refused."
> (`src/facts/resolver.py:178-181`)

Suppression can be decided without knowing a field; demotion cannot, because "may
populate `authored_by` and no other field" is only answerable once a producer has
*picked* a field. So the two catalogues travel to the producer as a `MetadataScreen`,
and `direct.py` and `rules.py` call `field_permitted` at the point of choosing
(`src/facts/discount.py:132-146`, `src/facts/direct.py:131-135`).

One suppression writes **one** row for the whole version, citing every suppressed
observation, because "a DOCX commonly writes the same generator into `creator` and
`lastModifiedBy`, and two rows would double-count one refusal"
(`src/facts/discount.py:164-170`). The comparison normalisation is NFC plus whitespace
strip, for comparison only, never written back (`src/facts/discount.py:203-211`).

**None of this fires in the shipped deployment.** `METADATA_SCREEN` carries no producer
strings and no property names (`src/cli.py:214-215`), and the resolver's
`screen_metadata` is a no-op lambda (`src/cli.py:332`). The mechanism is built and
tested; the catalogue that would drive it is empty.

---

## 3.6 The `unresolved` table — a refusal is a record

§3.6 stops at "no fact": "A model that cannot cite sufficient evidence must return
unknown." §8.5 then asks, under Fact quality, "Did it abstain when evidence was absent?"
— and **an absent row cannot answer a question about absence**
(`src/facts/unresolved.py:4-9`). Without the table P2 cannot distinguish a considered
refusal from a crash, a skip, or a file never reached; and from the person's side
silence reads as a verdict, which is §00's "false impression that an unprocessed file
was understood and found unimportant" (`src/facts/resolver.py:238-240`). Each row names
the field attempted, the reason, the routes tried, the observation keys looked at, and
the cache key it was computed under (`src/facts/unresolved.py:136-166`).

Four properties make it trustworthy, and each is structural:

1. **It is not a fact.** No `value_id`, no reliability state — *absent from the schema,
   not merely null* (`src/facts/schema.py:168-181`). "A reader that treats it as a
   weaker `possible` has broken it" (`src/facts/unresolved.py:13-15`).
2. **It obeys `file_facts`' negative contract** — no path, destination, folder or group
   column. The forbidden-substring list is imported from `file_facts` rather than copied
   (`src/facts/unresolved.py:16-18`, `src/facts/file_facts.py:97-99`).
3. **A later fact supersedes it and never deletes it.** The table carries P1's three
   supersede columns and a `record_id` projection, and `unresolved_for_file` returns
   superseded rows deliberately — "hiding them here would delete the history at the read
   instead of at the write, which is the same loss by a quieter route"
   (`src/facts/unresolved.py:172-179`).
4. **`budget_deferred` and `privacy_withheld` are not abstentions.** They are rows; they
   are not answers (`src/facts/vocabulary.py:122-135`).

Thirteen reasons, one named constant each, checked through P4's `check` so a misspelling
raises rather than storing (`src/facts/vocabulary.py:77-109`). The list is a census: "a
reason with no producer or a producer with no reason is visible by reading this list"
(`src/facts/vocabulary.py:92-93`). `direct.py` fires none of them by design — "this
producer never abstains", because a field no direct slot filled is a field the next
producer has not tried, and a row there "would answer §8.5's 'Did it abstain when
evidence was absent?' with a claim that had not happened yet"
(`src/facts/direct.py:34-38`).

The two bar reasons are kept apart from each other too. A privacy bar is a
**prohibition** — a file that may never reach a model is not a file waiting for budget
to free up, and "reporting it as a deferral would promise work that will never be done"
(`src/facts/resolver.py:189-194`). Every ceiling is asked, not just the first, so a
simultaneous exhaustion is not blamed on whichever key sorted first
(`src/facts/budgets.py:69-76`). `evidence_refs` on a bar row is empty and the code
argues that is correct rather than lazy: the barred route never looked at an
observation, and the evidence is retained where it always was, in P4's `evidence` table
(`src/facts/resolver.py:241-247`).

---

## 3.7 Values, `value_id`, and why two spellings must collapse

`value_id` is content-addressed over `(field_key, canonical_value)`
(`src/facts/values.py:101-104`). Three consequences: `ensure_value` is idempotent with
no read-then-write race (`src/facts/values.py:122-153`); two databases that saw the same
corpus produce the same value ids, which is what makes §8.5's replay comparable; and
**"a value belongs to exactly one field" becomes a property of the identifier** rather
than a rule someone has to remember (`src/facts/values.py:21-24`). The same string under
two fields is two different values — §3.8's role separation expressed in this table.
`write_fact` re-checks it anyway (`src/facts/file_facts.py:228-233`) and the DDL carries
`UNIQUE (field_key, canonical_value)` (`src/facts/schema.py:82`).

`first_evidence_ref` is the observation that introduced the value, and it is never
overwritten on a second sighting (`src/facts/values.py:126-128`). An automatically
created value *must* cite one; a user-created value need not
(`src/facts/values.py:133-138`).

Values are never deleted. `merge_values` records an alias and leaves the merged row
readable with a pointer to the survivor, so every fact that pointed at it still resolves
(`src/facts/values.py:191-244`), and a database trigger enforces it —
`RAISE(ABORT, 'a merge records an alias; a value is never deleted (§0, §8.2)')`
(`src/facts/schema.py:89-91`).

### Why two spellings of one identifier must reach the same `value_id`

Because `value_id` is a hash of the canonical value, two spellings that canonicalise
differently are **two different values**, and everything downstream treats them as two
different things. The 2026-08-29 change to the deployment's canonicaliser is the worked
example.

The first real run on a person's folder produced `NothingToDesign` — no tree at all.
The files said `PHYS 1401`; the deployment's structured-string pattern was
`\b[A-Z][A-Z0-9]*[0-9]{3,}\b`, which wants `PHYS1401`. No match, no observation, no
fact, no group, no tree (`planning/65-FIRST-REAL-RUN.md:45-46`).

The pattern was widened to allow one separator (`src/cli.py:188`):

```python
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")
```

That alone would have made things *worse in a subtler way*. With the pattern matching
but no canonicalisation, `PHYS 1401` and `PHYS1401` are two canonical values, two
`value_id`s, two `subject` facts sharing no value — and P9 groups on shared validated
facts. `planning/65-FIRST-REAL-RUN.md:143-157` records that failure in its original
form: four files carrying one course code became **four one-file groups**, each with the
same display label, and the course folder was proposed and left empty. The person sees
four identical folders holding one file each, with no explanation.

So the same commit added the canonicaliser (`src/cli.py:195`):

```python
_SEPARATOR = re.compile(r"(?<=[A-Z])[ -](?=[0-9])")
```

applied inside the direct slot, after whitespace collapse and before the value is
created (`src/cli.py:210-212`). `PHYS 1401`, `PHYS-1401` and `PHYS1401` now hash to one
`value_id` — one course, one value, one group, one folder. The raw wording is not lost:
it stays in P4's observation, which P6 never overwrites.

Both changes landed in `53c41d1`, 2026-08-29, "fix(p9,p11,cli): one course is one group,
and the refusal stops blaming the reader".

Two things about the canonicaliser deserve a critic's attention. It is the
**deployment's**, not P6's — `DirectSlot.canonical` is an injected callable
(`src/facts/direct.py:77-94`), and round 4's C-5 records that `normalize(field,
raw_value)` is "claimed by P8's Contract-in and disowned by P6's Task 17, so no part
builds it" (`src/facts/direct.py:84-87`). And `normalizer_id` — the column the SPEC
designates for "the safe-normalization check §3.6 requires" — is NULL on all 56 rows
(`src/facts/fields.py:120-122`).

`raw_variants` and `display_label` are built, tested, and **never populated on a real
run**: `add_raw_variant` and `set_display_label` have no caller anywhere in `src/`, and
`direct_facts` calls neither. §2.8's "U Chicago" survives in P4's evidence but never
appears in the `values` row the design's own example puts it in.

---

## 3.8 The read surface

`src/facts/read_surface.py` is described as "the only shape P9, P10, P11, P13, P2 and
the review UI see" (`src/facts/read_surface.py:2`). Three properties hold across every
function, each asserted by a test:

- it is a **pure read** — nothing writes, appends an event, or resolves;
- it returns **no filing decision** — asserted from the keys of every row handed out, so
  a future `destination_node_id` column fails twice;
- it **imposes its own total order** — `(field_key, canonical_value, fact_id)` — because
  P4's reads are insertion-ordered, "which is a property of one database and not of the
  corpus" (`src/facts/read_surface.py:5-14`, `src/facts/read_surface.py:91-98`).

| Read | For | What it gives |
|---|---|---|
| `facts_for` | general | every fact for one version, optionally narrowed by state or field scope; **includes `rejected`** (`read_surface.py:108-147`) |
| `proposal_eligible` | P10 §5.4, P11 §6.3 | the facts a folder proposal may rest on (`read_surface.py:150-169`) |
| `event_facts` | P9 §4.2 seed, P11 §6.3 | the Photos `event` fact — "a P9 seed, never a placement" (`read_surface.py:284-288`) |
| `family_facts` | P9, P11, P12 | duplicate family and version family (`read_surface.py:300-304`) |
| `session_facts` | P9 (`support_kind = bounded-session`) | the download session, held at `possible` so it never reaches `proposal_eligible` (`read_surface.py:291-297`) |
| `values_with_counts` | P10 §5.5 | the branch preview — "three schools, five terms, twelve course branches" (`read_surface.py:183-219`) |
| `evidence_chain` | P11, review UI | one fact walked back to the P4 observations it cites (`read_surface.py:236-258`) |
| `history` | P2, review UI | every row ever written for one slot, superseded included (`read_surface.py:261-269`) |
| `unresolved_for` | P2 §8.5, P13 | the abstentions, which appear in no fact read (`read_surface.py:272-281`) |
| `active_allowlist_for` | P8 §3.5 | the fields the model may propose into (`read_surface.py:172-180`) |
| `is_destination_eligible` | P10, P11 | may this field become a folder level (`read_surface.py:307-315`) |

Three design details. **A misspelled filter raises rather than returning empty** — "an
empty list is how a caller concludes there are no facts, and a typo must not read as an
answer" (`src/facts/read_surface.py:118-119`). **`evidence_chain` is the one function
returning something other than P6's own rows**: P4 `Observation` objects verbatim, whose
`location.container_path` is a locator *inside* a document
(`heading:page=1/heading=2`), never a filesystem destination — so it is not a breach of
the negative contract (`src/facts/read_surface.py:16-23`). **An abstention is not a weak
fact**: `unresolved_for` rows carry "no value and no reliability state, so nothing
downstream can read one off it and start treating it as a `possible`"
(`src/facts/read_surface.py:277-279`).

### The incident: two reads in one module disagreed about the same file

This is documented in the code and is the clearest illustration of why a read surface is
a surface rather than a convention.

`values_with_counts` — the branch preview — has always filtered three things: `active =
1`, `superseded_by IS NULL`, and membership of `PROPOSAL_ELIGIBLE_STATES`
(`src/facts/read_surface.py:207-215`). `proposal_eligible` originally filtered only the
reliability state.

The disagreement ran in both directions, and both directions are recorded:

> "Counting every live fact previewed a branch for a `rejected` conclusion and for a
> `possible` one … The preview promised folders no proposal could rest on, and the two
> reads in this one module disagreed about the same file."
> (`src/facts/read_surface.py:197-201`)

> "They disagreed in the other direction too: a replaced conclusion reached P10's and
> P11's folder-proposal read, so a tree was proposed from stale truth."
> (`src/facts/read_surface.py:162-164`)

The fix was to give `proposal_eligible` all three filters
(`src/facts/read_surface.py:166-169`), landed in `6bcc0e0`, "fix(P6,P7): the final
review's blocker and majors — including one I introduced". What a person would have
seen before the fix: a preview promising "12 course branches", a tree built from a
superseded reading, and folders that could not be filled by the facts that previewed
them.

The shape of the bug recurs: `active`, `superseded_by` and `reliability_state` answer
three different questions, and §8.2's rule that a replaced row stays **readable** is not
the same as saying it stays **proposable**. `facts_for` and `history` still return the
old row — deliberately (`src/facts/read_surface.py:164`).

---

## 3.9 Schemas and domains — what "active" means

§3.11 says the universal set applies to every file and a domain schema activates "only
when the evidence indicates that a domain is plausible". `target_school` is not a field
every file is expected to have (`src/facts/domains.py:4-8`).

Two structural rules follow (`src/facts/domains.py:18-26`):

- **Activation adds; it never chooses.** `active_domains` returns a frozenset, not a
  winner. No domain suppresses another and nothing here ranks
  (`src/facts/domains.py:124-134`). The design's worked case is an academic abstract
  submitted with a university application, which keeps `project` *and* `purpose` *and*
  `target university` at once: "At the pre-sorting stage, the product does not need to
  decide which of those perspectives will ultimately determine its physical location"
  (`src/facts/domains.py:10-16`).
- **P6 authors no activation signal.** Which evidence activates which domain is
  unauthored. Signals arrive as an injected `ActivationSignals` with no default, and "an
  empty one activates nothing, which is the honest behaviour of an unauthored rule"
  (`src/facts/domains.py:22-26`, `src/facts/domains.py:112-121`).

Twenty-three schemas are recognised — §3.11's six with field rows, §3.15's four safety
domains, and thirteen professional schemas adopted from `60` J-1
(`src/facts/domains.py:59-64`). A schema outside the twenty-three raises
`UnknownSchema`, "which is the half of 'recognised' that gives it meaning"
(`src/facts/domains.py:57-58`).

**Three declare no fields at all**, derived rather than written down:
`FIELD_LESS_SCHEMA_IDS` computes to `('identity', 'medical', 'legal')` — §3.15's
out-of-scope safety domains (`src/facts/domains.py:82-83`, verified by execution).
Activating one contributes nothing to the allowlist, "which is exactly right, because a
schema with no authored fields must not cause fields to be invented"
(`src/facts/domains.py:30-33`); the loop reaches that case and explicitly `continue`s
(`src/facts/domains.py:168-172`). Twenty schemas do have a field set, five of them
referencing other schemas' keys entirely.

The **active field allowlist** is the universal fields plus every active schema's field
set, deduplicated, in the catalogue's own order (`src/facts/domains.py:137-176`). This
is the object §3.5's sentence turns on — the model "can only propose facts that belong
to the active domain schema" — and it is one computation, not two
(`src/facts/domains.py:141-144`).

**Nothing in the shipped run uses any of it.** `active_domains`,
`active_field_allowlist` and `active_allowlist_for` have no caller in `src/` outside
`facts/`. The deployment gets its active domain from the user's `--situation` argument
by string split — `schema = situation.split(".", 1)[0]` (`src/cli.py:559`) — and hands
it straight to P10 as `active_domains=(schema,)` (`src/cli.py:576`). P6's evidence-driven
activation never runs.

---

## 3.10 What is inert

Verified by grep over `src/` (call sites, not definitions or comments). "Inert" here
means: shipped, tested, and reachable by no production caller.

**Producers with no call site anywhere in `src/`:**

| Producer | Module | What it would write |
|---|---|---|
| `apply_rules` | `rules.py:105` | §3.5 rule-validated `subject` facts, the `BUSIB 4300` + academic-context case |
| `fill_or_abstain` | `facets.py:161` | §3.7 ranked facet fills with score and margin |
| `duplicate_family` / `version_family` | `families.py:148,244` | §2.9's two universal family facts |
| `photo_events` / `media_type` | `photo_event.py:173,239` | G7's Photos `event` fact; the §2.6 photograph/screenshot decision |
| `bounded_sessions` | `session.py:181` | G6's `download_session` `possible` fact |
| `build_request` / `apply_verdict` | `llm_seam.py:191,226` | the P8 seam and every `llm_supported` fact |

`direct_facts` is the only P6 producer called in `src/` (`src/cli.py:311`).

The consequence is worth stating plainly: `event_facts`, `family_facts` and
`session_facts` **are** called — by `grouping/seeds.py` and `grouping/retrieval.py` —
but the producers that would populate the fields they read are never invoked. On a live
run those three reads return empty lists forever, and P9's photo-event seeds,
structural-family seeds and bounded-session support channel are all fed by nothing.

**Read surfaces with no caller in `src/`:** `facts_for` (used only internally by
`proposal_eligible`), `values_with_counts`, `evidence_chain`, `unresolved_for`,
`history`, `active_allowlist_for`. So §5.5's branch preview, the review UI's evidence
walk, the §8.2 history read, and P13's refusal list are all published and unconsumed.

**Other unreachable machinery**, all with no caller in `src/`:
`facts.learning.is_suppressed` — I4's query-before-propose guard, whose own docstring
says the obligation "is currently enforced by nothing" and that it cannot be wired by
import because the resolver's permitted-import test forbids it
(`src/facts/learning.py:14-27`); `facts.learning.record_correction`, the surface P13
will route corrections into (`src/facts/learning.py:29-33`);
`facts.stage_output.fact_stage_output`, P6's §8.5 envelope;
`facts.budgets.deferred_counts` and `ceiling_values`, §8.6's per-ceiling reporting;
`facts.values.add_raw_variant`, `set_display_label` and `merge_values` — §2.8's second
and third renderings and §0's taxonomy aliases; `facts.plan_versions.set_display_label`
/ `display_label`, §8.8's plan-versioned rendering; `FieldRow.reliability_ceiling` (19
rows), `.role_split`, `.aliases`, `.notes`; `ValueRow` and `ValueRow.from_row`, never
constructed; `facts.usable.create_fact_passes` (`src/facts/usable.py:77-88`); and
`facts.vocabulary.NOT_ABSTENTIONS`, published "so a caller can make the distinction
without a second copy of the rule" (`src/facts/unresolved.py:22-24`) — no caller makes
it.

**States nothing writes into `file_facts`:** `user_confirmed` and `rejected` (§3.4
above).

---

## What looks wrong here

Flagged, not resolved.

**1. The shipped product exercises one of three producers and one of 56 fields.**
`stages={"direct": …, "rule": None, "llm": None}` (`src/cli.py:323`) with a single slot
writing `subject` (`src/cli.py:207-213`). A 56-field catalogue with 39
destination-eligible keys, 23 schemas and an activation mechanism sits behind a run that
can produce exactly one kind of fact. Whether that is honest minimalism or a catalogue
built far ahead of its producers is the question a critic should put first.

**2. The one live claim is an assertion, not an inference.** The direct slot's stated
claim is "an identifier printed in a document is what that document is ABOUT"
(`src/cli.py:200-201`), and it fires on any `body#`/`heading` locator matching
`[A-Z][A-Z0-9]*[ -]?[0-9]{3,}`. §3.5's `direct` state is for "a reliable, explicit
source — content hash, EXIF timestamp, document title, labelled form field". A regex
over body text is none of those; §3.5's own worked requirement for a course code is
*rule-validated with a context check*, which is `apply_rules` — the producer that is not
bound. The result is that `INV20261` on an invoice or `AC4471` in a footnote becomes a
`direct` `subject` fact, at the second-strongest state on the ladder, with no context
check, and reaches `proposal_eligible`.

**3. `cli.py` bypasses the read surface and hardcodes the reliability it reports.**
`evidence_for` reads `file_facts` with raw SQL (`src/cli.py:672-678`) and then labels
every fact `reliability=pv.DIRECT` / `reliability_state="direct"` regardless of what the
row stores (`src/cli.py:684,689`). `read_surface.py:2` says it is "the only shape P9,
P10, P11, P13, P2 and the review UI see". In this deployment every fact happens to be
`direct`, so the lie is currently true — which is precisely the condition under which it
will survive the day it stops being true.

**4. Two cache-key compositions in one pass.** Facts and suppression rows use
`pass_cache_key`, a real §3.4 five-part digest (`src/facts/direct.py:151-152`,
`src/facts/discount.py:183-184`). Bar rows use the injected `cache_key_for`, which in
the deployment is the literal `f"cli-native-v1:{content_hash}"` (`src/cli.py:331`). The
SPEC requires an `unresolved` row to carry the "same composition as `file_facts` (§3.4),
so an abstention is invalidated by the same events that invalidate a fact"
(SPEC line ~382; `src/facts/cache.py:72-77`). `is_stale` compares cache keys literally
(`src/facts/cache.py:119-147`), so a bar row would never share a slot with the facts of
its own pass. It does not bite today only because `pending_fields` returns `()`.

**5. `sensitivity_status` is missing and the SPEC's Done-means 2 says "all six".** The
module states the conflict and instructs the reader not to close it
(`src/facts/fields.py:132-139`). A universal field named by the design has no row, no
producer, and an open NEEDS-JOSEPH label.

**6. Two live keys for one concept, in a catalogue whose whole point is one key per
concept.** D8 rules that `target_school` is the stored key and "target university" is an
alias — and the catalogue ships **both** `target_school` and `target_university`
(`src/facts/fields.py:248-251`). The module flags it as an open violation, which is
better than hiding it, but a fact can currently be written under either and nothing
reconciles them. `values_with_counts` on one would silently miss the other.

**7. `reliability_ceiling` caps nothing.** Nineteen rows declare one — `account_holder`
→ `possible`, `consignment` → `validated` — and no code reads the attribute. A key
declared `possible` can be written `direct` by any producer that picks it.

**8. `normalizer_id` is NULL on all 56 rows.** §3.6's third validation check is "value
normalizes safely", and the SPEC gives `normalizer_id` as the column that names the
check. There is no per-field normalizer anywhere; the only normalisation on a live run
is a lambda in `cli.py`. `NORMALIZATION_FAILED` is a published `unresolved` reason with
no producer.

**9. I4's rejection guard is not wired, and cannot be wired by import.**
`facts.learning.is_suppressed` exists so that a `rejected` claim is not revived. Nothing
calls it, and `FactResolver` has no slot for it — the fix requires changing a published
constructor contract (`src/facts/learning.py:14-27`). Meanwhile §8.7's stated failure —
"repeatedly resurface the same attractive but incorrect grouping" — is unguarded. It
does not bite today only because nothing writes a `rejected` fact either.

**10. P6 emits no §8.5 stage output.** `fact_stage_output` is built and uncalled, so
P2's "decomposed by stage" evaluation gets nothing from the factual-validation stage on
a real run — which is the stage B7 restructured the whole `unresolved` table to make
measurable.

**11. The `unresolved` table is empty on every live run, for two independent reasons.**
`screen_metadata` is a no-op and `pending_fields` returns `()` (`src/cli.py:326,332`).
So the mechanism built to prevent "the false impression that an unprocessed file was
understood and found unimportant" produces exactly that impression today: files with no
facts and no rows saying why.

**12. `fields.py` is 712 lines and roughly two thirds of it is adjudication prose.**
Rows carry multi-paragraph `notes` citing documents by number (`60` §5, `57` §5.3, `49`
§1.5) that a reader of `src/` cannot see. The reasoning is genuinely load-bearing —
several rows are incomprehensible without it — but it means the catalogue's authority
lives in `planning/`, in documents the code cannot check itself against, while the code
claims not to depend on that directory.

**13. `download_session` is a universal field with a producer nothing calls.** It is one
of the six universals — so `active_field_allowlist` offers it on every file — and
`bounded_sessions` has no call site. Same shape for `duplicate_family` and
`version_family`: three of six universal fields can never be filled.
