# Council seat — what goes wrong

Date: 2026-08-21 (overnight)
Seat: **risk.** One question per item: what is the failure mode of each option, who does it hurt,
and how would anyone find out?
Not this seat's job: the design's plain reading, or build cost. Two other seats hold those.

**Honest ranking is the point.** Two items below are ranked MODERATE and one of my six
recommendations argues *against* the more protective option. If everything here were CRITICAL this
document would be worth nothing.

Everything marked *executed* was run against live `src/` this pass. Nothing in `src/` or `tests/`
was modified. Field census figures come from `planning/domains/*.json` read directly; where they
differ from `NEEDS-JOSEPH.md` the catalogue has grown since that line was written and I say so.

---

## D1 — The field catalogue: how far open?

**Options.** (a) fully open — §3.11's six rows as seed, the 560-domain catalogue as its growth.
(b) narrowly open — §3.8's four role fields plus §3.11's, catalogue demoted to a routing aid that
writes no field rows.

Current catalogue scale, measured this pass: **560 domain entries across 13 files, 2,233 distinct
field names.** (`NEEDS-JOSEPH.md` B1 says 1,287 across 324; five more catalogues have landed since.)
**338 of the 560 entries carry `sensitivity: potentially_sensitive`** — 60%.

### Failure mode of (a), fully open

The surface a model may propose into is not 2,233 fields; §3.11's mechanism keeps roughly five live
per file. **The risk moves from the catalogue to the activation step**, and that is the real change:
under (b) a wrong activation opens 5 of ~37 fields the user could eyeball in one screen; under (a) it
opens 5 of 2,233 drawn from any of 560 schemas.

The path, walked through the plan text:

1. P6 Task 13 (`§3.11 domain activation, and several domains on one file at once`) activates the
   wrong one of several competing schemas. **Misactivation is not speculative here — the catalogue's
   own authors documented it as unresolved.** B6.5: *"§3.11 already gives `project` to Research and to
   Code, this entry adds a business instance, and the personal slice has its own … four domains that
   will compete for every file containing the word."* B6.8: *"this domain is authored THREE times
   across the catalogue … with near-identical templates."* B6.9: four HR entries duplicate four
   career entries and *"§3.6 cannot arbitrate it, because a fact belonging to two allowed schemas
   passes validation in both."* Under (b) those collisions do not exist, because the competing schemas
   do not.
2. Whichever schema wins makes its fields proposable. §3.5: the LLM *"can only propose facts that
   belong to the active domain schema"* — the schema is now active, so it can. The fields at stake
   are named by the catalogue: `subject person` (`med.personal-health-record`),
   `characteristic_category` (`hr.dei-program`), and the third-party client material B6.8 calls
   *"the sharpest privacy problem in this slice."*
3. A fact value is a **candidate label**, and `candidate labels` is one of §8.4's five releasable
   kinds by name. P7 Task 7 makes the nine always-local items unconstructible; a candidate label is
   not among the nine. So the value is releasable to a cloud model under hybrid or cloud-assisted
   mode.
4. `subject person` is not an authorship or creator-identity field, so §3.8's one hard rule does not
   bar it from `destination_eligible`, and C14 records that nothing else decides that column. P10
   can build `Health/<a named person>/`. B6.11 raises the same shape from the other end and declines
   to model it for exactly this reason.

The catalogue's own authors saw this coming and wrote it down. `hr.dei-program` (B6.10) names
`characteristic_category` and deliberately refuses to enumerate its values: *"a catalogue that
enumerated them would be instructing the extractor to look for them, and §3.7's conservative-facet-
extraction discipline argues against building a gazetteer of characteristics at all."* Authoring a
field **is** authoring the instruction to extract it.

**Who is harmed.** The user, and — in the medical, DEI, HR and client-engagement entries — third
parties who never used this product. **How they find out:** for the folder, immediately, because a
directory named after a person is visible. For the cloud release, only by opening the audit record
for that call, which §8.4 does require to name the excerpts. So it is *discoverable* but not
*noticed*.

### Failure mode of (b), narrowly open

1. **As currently specified it drops a launch domain.** P6 Task 2: *"Career and recruiting, identity,
   medical and legal have no field rows and acquiring one fails the test (S3)."* §3.15 names the
   launch set as *"academic coursework, college applications, research and lab work, **career and
   recruiting**, photos and captures, and code projects."* Career and recruiting is in §3.15's six
   and absent from §3.11's table. So a closed-to-§3.11 reading forbids fields for a domain the design
   says ships. This is a second internal contradiction, independent of the §3.8 one B1 already
   proves.
2. **Real facts land in `unresolved`** with reason `field_not_in_active_schema`. §6.10 says *"correct
   abstention is a successful outcome"* — but this abstention is not correct: the evidence was fine
   and the schema was missing. The file gets no domain facts, no destination match, and falls to
   residual review (§7.1). **Visible**, and honestly labelled.
3. **The safety domains have no fields and no detector.** §3.15 requires finance, identity, medical
   and legal to ship *"first as safety domains, meaning the system detects and protects them before
   any cloud or automated placement decision is allowed."* Under (b) they have no field rows, and
   P7's Global Constraints say P7 *"owns no detection rule"* and *"publishes the vocabulary the
   detectors write into"* — with the detectors themselves Deferred in both SPECs. So nothing detects
   a medical record. But absence of a classification resolves to `unreadable_unclassified` (P7 Task
   3), which is `Denied(unclassified)` for cloud. **(b)'s failure on sensitive material is
   over-refusal, not exposure.**

### Severity

**SERIOUS.** Not critical: (a)'s privacy failure needs cloud mode *and* a wrong activation and is
bounded to one file per occurrence; (b)'s failure is a visible residual pile. Neither destroys a
corpus. It earns SERIOUS on cost-of-change — it is cheap now and a data migration after P6 Task 1.

### Recommendation

**Ship §3.15's list, not §3.11's table, and not the catalogue.** Fact schemas for the six §3.15
launch domains plus §3.8's four role fields; the 560-domain catalogue retained as a **recognition and
routing aid that writes no field rows**. This is neither of the stated options exactly, and it is
what §3.15 says in its own words: *"Other domains remain placeholders until user demand and corpus
evidence justify detailed templates. This approach gives the product broad long-term coverage
without prematurely hand-authoring hundreds of specialized schemas."* The catalogue is not wasted —
it is the domain-plausibility evidence §3.11's activation step needs, which is the part that actually
carries the risk.

### Where this seat is weak here

I am ranking a *possible* privacy path — a protected characteristic reaching a prompt as a candidate
label — above a *certain* usability cost. If Joseph ships `offline` or `local_model` as the install
default (C2), (a)'s privacy failure never fires in v1 and my argument collapses to "a bigger surface
is bigger." And the 560 domains are already authored: the cost of not using them is sunk work, which
is a cost a risk seat systematically refuses to see. The "what ships" seat should be believed over me
on that half.

---

## D2 — `sensitivity`: one record or three?

**This is the field that decides what leaves the machine.** Three spellings exist today:
`sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state` (`src/database_agent/db.py`,
the column). The column has **no writer** — verified again this pass.

### Failure mode of (b), three records — and it has already fired once

The concrete path is not hypothetical. It is in the git history of this repository:

- `src/orchestrator.py` passed `handling_class=file_row["sensitivity_state"]` into P2's bundle until
  the 2026-08-21 pass. Two different concepts, one column apart. **No test failed, because both were
  NULL on a live scan.** It now reads `handling_class=None` with a six-line comment explaining why.
- P7 Task 4 introduces `mirror_state(record) -> str` and an injected `SensitivityStateWriter`,
  which gives the column its first writer. Task 22's assertion is *"the Wave-2 bundle carries a
  non-null `handling_class` after a classification."* The shortest edit that satisfies that assertion
  is restoring the deleted line — and once both columns are populated, the right value and the wrong
  value are **indistinguishable at rest**. (Round 3 A10 reaches the same place from the plan side.)

**The worst concrete outcome.** `mirror_state` is called a *mapper* by its own plan, which implies
`files.sensitivity_state` holds a vocabulary that is not `HANDLING_CLASSES` — otherwise it would be
an identity function. If it is a different vocabulary, then a consumer that compares
`files.sensitivity_state == "highly_sensitive_credential"` gets `False` for a scanned passport whose
column holds the mapped spelling. The two consumers that matter are `Gate.release`'s `unclassified`
branch and `may_move_automatically`. So: **a passport scan classified `highly_sensitive_credential`
is read through the mirror column, the comparison misses, `may_move_automatically` returns True, and
P12 moves it without the explicit user policy §8.4 requires** — or, on the release side, it is not
denied.

There is a live second instance of the same shape today. `src/orchestrator.py:298-319` writes
`handling_class=None` for every file and then, unconditionally and with no handling-class filter,
copies **every text unit of every run** into `bundle_text_unit` and seals the bundle. A tax return's
full extracted text is in a sealed replay bundle after one Wave-2 run, and there was no single place
to ask "is this file protected?" before it went there.

**Who is harmed and how they find out.** The user. And they would **not** find out: a NULL column and
a correct column, or two vocabularies for one concept, are indistinguishable from correct behaviour at
rest. `22-p1-p7-connection-contract.md` §5 says this in its own words and lists five prior instances.

### Failure mode of (a), one record

Real, but paid once at design time rather than per file at run time. One record must serve three
lifetimes: a §3.11 fact is per `(file, content_hash)` and supersedable; §8.2's file-record state is
per file and current; §8.4's handling class is per file version and gates release. Collapsing them
means either P6's `file_facts` gains the `protected` and `basis` columns its published shape does not
have (P7's own plan reports this as SPEC-vs-code item 9), or the handling class loses its version
binding. Round 3 A3(b) shows what losing the binding costs: an excerpt citing content hash A released
under the class resolved for hash B.

### Severity

**CRITICAL.** The only item on this list whose failure is invisible at rest, on the one concept the
project has already shipped wrong, gating the one action that cannot be undone.

### Recommendation

**One record.** P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative.
`files.sensitivity_state` either holds a `HANDLING_CLASSES` member verbatim — making `mirror_state` a
**validator, not a translator** — or is dropped from P1's schema. §3.11's `sensitivity status` fact
becomes a read-only projection of the record with no independent writer.

Two test disciplines that must land with it, because the record alone will not hold:

- Every assertion about the value compares **a value**, never non-nullness. A non-null assertion
  cannot tell the two columns apart, which is exactly how the previous instance survived.
- P7 Task 4 states the target vocabulary in one sentence. The plan currently does not, and an
  unstated target vocabulary is how a fourth spelling arrives.

### Where this seat is weak here

I cannot show a live exploit. Both columns are NULL today, so my worst outcome is a forecast about
code nobody has written, and both plans are already alert to it — P7 Task 4 injects the writer and
reports the gap rather than patching it, and the connection contract states a standing rule. My case
is that a standing rule holds only while everyone remembers it, and this project's own history says
memory is the wrong mechanism. That is an argument from precedent, not from a failing test.

---

## D3 — Deletion versus append-only

**Append-only has already shipped, and not only over the log.** Executed this pass: **13 tables carry
`BEFORE DELETE ... RAISE(ABORT)` triggers** — `events`, `evidence`, `text_units`, `extraction_runs`,
`exclusion_verdicts`, and all eight `bundle_*` tables. `text_units.text` is where a scanned passport's
OCR text lives. `evidence.raw_value` is where the extracted account number lives.

So this is not a choice between two futures. §8.4's right to *"review and delete local derived data"*
is **currently unimplementable without a schema migration**, and P7 Task 15 correctly ships
`delete_derived` as a function that refuses and names I6.

### Failure mode of "deletion wins"

If deletion reaches `events`, the product cannot answer *"what did you send, to whom, and when."*
§8.4 makes the retraction limit a `must`, and P7 Task 15's own words are that *"the audit log is what
makes `retraction_limit` truthful and specific rather than a generic disclaimer."* Deleting audit
records converts it into the generic disclaimer.

**Recoverable? No.** `11-ops-runtime.md` §2 is explicit: rebuild-from-filesystem does not reconstruct
`events`, learning records, plan versions, consent grants, or review actions. *"Those have no
filesystem source."* A deleted audit record is gone permanently.

### Failure mode of "append-only wins" (the status quo)

A user marks a passport private and asks the product to forget its OCR text. Either it refuses — an
honest failure — or it reports success while the text remains in `text_units` and `bundle_text_unit`.

**Recoverable? Yes.** The bytes are still present, so a tombstone or redaction-in-place path can be
added later. Deletion later is always available. Un-deletion never is.

### The failure neither option covers, which I rank above both

**A `delete_derived` that succeeds against `text_units` and misses `bundle_text_unit`.** The user is
told the passport's OCR text is gone; a verbatim copy sits in a sealed bundle, put there
unconditionally by `src/orchestrator.py:318` with no handling-class filter. P7 Open question 8 asks
whether a bundle may carry excerpt spans and is open; nothing today stops one carrying full text.

The lie is the harm, and it comes from **"derived" being undefined**. C1's second sub-question — what
counts as derived — is the one that needs answering. The first (which wins) is close to answered by
the substrate already.

**How the user finds out:** they do not, unless they open the SQLite file. That is the property that
makes this worse than an honest refusal.

### Severity

**SERIOUS**, not critical — because the built system currently *refuses* rather than lies, which is
the honest failure. It becomes CRITICAL the day a `delete_derived` ships that touches some tables and
not others.

### Recommendation

Append-only for `events` forever; a **defined, enumerated tombstone** for content. Specifically:

- Enumerate the derived set as a literal table-and-column list in the SPEC — at minimum
  `evidence.raw_value`, `text_units.text`, and every `bundle_*` content row — and make
  `delete_derived` **raise** on any table not in that list rather than silently skipping it. An
  unenumerated table is the failure above.
- Separately, and before P7 ships: stop the unconditional bundle copy at `src/orchestrator.py:318`.
  Today it manufactures a second undeletable corpus of everything on every scan, which makes any
  future deletion story twice as hard.

### Where this seat is weak here

I am treating "told it was deleted and it wasn't" as worse than "asked and could not." A user with a
passport scan they want gone may rank those the other way, and an erasure obligation, if one ever
applies, does not accept "we kept the log" as an answer. My recommendation optimises for the
auditability of a product nobody has yet asked to forget anything.

---

## D4 — Jurisdiction at launch

Measured this pass: **124 of 560 catalogue entries reference jurisdiction** — government 34, law 28,
trades and property 24, finance 21, career 7, the rest scattered. 29 field rows carry a `jurisdiction`
field outright. Three catalogues raised the question independently (B4).

### What happens to a user whose country is not covered

The jurisdiction-shaped material is in two places, and they fail differently.

**Recognition rules fail by not firing.** A catalogue entry's `recognition.deterministic` clause keys
on document shapes — a `W-2` layout, a court-caption format, a permit-number pattern. An Irish `Form
11` does not match a US tax schema. The file gets no domain facts, no destination, and lands in
residual review. **Visibly worse results**, and §8.6's principle is satisfied by accident rather than
by design.

**Detectors fail by not firing too — and that direction is safe.** This is the finding I want to state
plainly rather than inflate. P7's Global Constraints require that *"absence of a classification
resolves to `unreadable_unclassified`, never to `public_low`"*, applying §8.6's *"cost exhaustion must
never turn into lower-quality automatic classification."* So an identity document whose national
format is not in the shipped detector set gets **no** classification, which resolves to
`unreadable_unclassified`, which is `Denied(unclassified)` for a cloud call. **An unsupported
jurisdiction fails toward refusal, not toward exposure.** The residual harm here is quality, not
privacy.

### Does §8.6's principle apply?

In spirit yes; in mechanism, no — and that is the gap. §8.6 is written about within-scan deferral:
*"The user interface should show the difference between completed work and deferred work"* and should
avoid *"the false impression that an unprocessed file was understood and found unimportant."* But
nothing distinguishes a file that fell to residual because its country is not modelled from one that
fell there because it is genuinely a boarding-gate screenshot. The residual surface (§7.5) has no
field that can say *"this domain is not modelled for your region."*

**Who is harmed:** a user outside the shipped jurisdiction, who gets a worse product and is told
nothing about why. **How they find out:** they see a big residual pile and conclude the product does
not work, rather than that it does not do their country.

### Severity

**MODERATE.** It costs quality and honesty, not safety, and the protective default in P7 Task 3 is
what keeps it out of the higher bands. This is the item where crying wolf would be easiest and most
wrong.

### Recommendation

Ship **one** jurisdiction — whichever matches the validation corpus, which from the worked examples
throughout the design (`BUSIB 4300`, `W-2`, `UChicago`) is US-shaped. Then two cheap things:

- Mark jurisdiction-dependent entries with an explicit key in the catalogue. 124 already reference it
  in prose; making it structured costs one field.
- Give the residual surface one string that can say a domain is unmodelled for the user's region.
  One row attribute, not a feature.

Do **not** author a second jurisdiction's gazetteers at launch. §3.15's *"without prematurely
hand-authoring hundreds of specialized schemas"* is describing exactly this temptation.

### Where this seat is weak here

My reassurance rests entirely on one line that is not yet built: P7 Task 3's absence-resolves-to-
`unreadable_unclassified` rule. If Joseph instead ships a jurisdiction-parameterised classifier that
defaults unrecognised document types to `public_low`, the whole item inverts from MODERATE to
something much worse. I am scoring a property, not a program.

---

## D5 — The `no_usable_facts` pass structure

**The framing asks: OCR that runs when it should not, or facts missed that should have been found?
Neither is the answer. The answer is the third thing, and it is what the fix currently does.**

### Failure of today's shape — one loop, a constant `False`

`orchestrator.run_wave2` consults `no_usable_facts` inside `extract()`, before `_write` has handed
P4 a single observation. Every test injects `lambda f, h: False`.

`False` means "the text layer is fine", so §2.2's targeted-OCR route **never fires**. Concrete: an
old tax return or medical record that was scanned and badly OCR'd carries a garbage text layer,
yields no facts, never gets the targeted OCR that would recover them, and falls to residual.
**Facts missed.** Cost is quality; the user sees the file in residual marked unreadable, which is
honest. §8.6 holds.

### Failure of a real P6 wired into today's caller

The verdict returns `True` before the pass has run — SPEC: *"Consulted earlier it would return `true`
for every file and trigger OCR on the whole corpus."* §8.6's `Maximum OCR time per scan` stops it
eventually, but by then the budget has been spent on files that did not need it, and every genuinely
scanned document is deferred. **Both failures at once**, and the progress line reports the scanned
documents as deferred — true, and misleading about why.

Worth stating plainly and not inflating: this is a **cost** failure, not a boundary one. Those files
are already in the corpus and already lawfully readable. It does not touch §4b.

### Failure of the four-pass fix as currently planned — the one that matters

P6 Task 19 raises `FactPassNotRun` when the verdict is asked before the pass, arguing that raising
*"makes a wrong call sequence a failing test rather than a silent behaviour."* Against this caller
that is false, and round 3 A1 executed it:

`src/orchestrator.py:151-158` is a blanket `except Exception` that re-raises only
`ProtectedContainerRefused` and `DatalessRefused`. `FactPassNotRun` is neither. Executed on the
repo's own Wave-2 fixture, the raise becomes:

```
RUN: ('pdf.text', 'native', 'failed',
      'FactPassNotRun: no recorded P6 deterministic pass for this content hash')
scan completed, bundle: True
```

The chain from there: `failed` is one of the `completeness` values P7 Task 3 maps toward
`unreadable_unclassified`; `unreadable_unclassified` is `Denied(unclassified)`. So **the privacy gate
refuses every text-bearing PDF in the corpus while the scan reports success**, the progress line
reports those documents unreadable, and Task 26's own acceptance test — *"injecting a verdict that
raises and running a full corpus without it firing"* — passes, because from `run_wave2`'s vantage
nothing fired.

**Who is harmed and how they find out.** The user, who is told their document library is unreadable
and gets no model help on any of it. They find out by concluding the product does not work. Nobody
finds out *why*, because the scan is green and the tests are green.

### Severity

**CRITICAL** — for the fix, not for the structural choice. The four-pass shape is right and is barely
Joseph's decision; what needs deciding is that Task 26 does not land as written.

### Recommendation

Adopt the four passes — they cost nothing while `readers.ocr_engine is None`, since loops 3 and 4 are
empty. Require both of A1's changes before Task 26 is accepted:

1. `_extract_one` re-raises `FactPassNotRun` beside the two admit refusals. A control-flow signal from
   a downstream part is not a reader failure, and the catcher's own docstring already draws that
   distinction.
2. **Loop 1 hands `extract()` no verdict at all.** "The branch cannot fire early" must be implemented
   as the branch being structurally absent in pass 1, not as a landmine armed behind a catcher. As
   written the plan implements "cannot fire" as "raises", and those are not the same thing when
   something stands between.

### Where this seat is weak here

The finding is round 3's; my seat adds the consequence chain and the ranking, not the discovery. And
if Joseph ships v1 with no OCR engine — P5's still-open question — loops 3 and 4 are empty and none
of this fires. The item is theoretical until an engine is chosen, which is a real discount on my
CRITICAL.

---

## D6 — Field naming

**It is not cosmetic, and the catalogue can be counted.** Measured this pass across all 13 files:

| Measure | Count |
|---|---|
| Distinct field names | **2,233** |
| `snake_case` field names | **959** |
| spaced field names | **914** |
| **Concepts already spelled both ways** | **124** |
| Of those, spellings spread across both `potentially_sensitive` and `none` domains | **58** |

Live examples: `document_role` (27) / `document role` (1) · `artifact type` (43) / `artifact_type` (7)
· `case_reference` (10) / `case reference` (2) · `document_type` (8) / `document type` (3) ·
`account_identifier` (4) / `account identifier` (2) · `capture date` (6) / `capture_date` (1).

### What breaks when one concept has two names — three named paths

1. **Any rule keyed on a field name checks one spelling.** §8.4's releasable list includes
   *"non-sensitive metadata"*, and **nothing anywhere decides which metadata is non-sensitive** —
   P7's `MetadataField` is one of six item kinds and no task supplies the predicate. The natural
   implementation is a name-keyed list. An allowlist authored against `account_identifier` releases
   `account identifier`. Outcome: an account number reaches a cloud prompt because the classifier's
   key was written with an underscore.
2. **`destination_eligible` is a per-field column** (P6 Task 2). §3.8's one hard rule — no authorship
   or creator-identity field is ever a folder level — is enforced per field row. Two spellings are two
   rows, so the rule applies to one of them. Outcome: `subject person` is barred as a folder level and
   `subject_person` is not, and P10 builds `Health/<a patient's name>/`. Harmed: a person who never
   used this product.
3. **Learning suppression fails open.** Round 3 A13, confirmed live: `basis_key` is
   `(file_id, field, value_id)` and `suppressed()` returns **False** when the query matches nothing. A
   user rejects a classification recorded under `document type`; the next run proposes it under
   `document_type`; the rejection does not match; the same wrong claim returns forever. §8.7 exists
   precisely to prevent that.

### The precedent, which is the actual argument

This project has shipped one-concept-two-names **four times**, and none of the four failed a test at
the time:

| # | Instance | How it presented |
|---|---|---|
| 1 | `fingerprint` (P5) vs `config_fingerprint` (P4) | join-break 1, `20-p1-p5-recheck.md` |
| 2 | `apple-vision` / `Apple Vision` / `ocr.apple_vision` | one engine, three spellings |
| 3 | `observation_keys_for_run` — a published order that was uuid4 order | consumer indexed into it positionally |
| 4 | **`handling_class` fed `sensitivity_state`** | **a privacy signal landed on the wrong value.** Both NULL, so nothing failed |

Instance 4 is D2. Instance 3 is still live in a different form (round 3 A2: the §2.9 sensitivity
signal is stored against the *filename's* observation key, so the email address it was raised for
carries no signal — executed).

### Severity

**SERIOUS**, and the cheapest of the six to fix. It is mechanical **today** and stops being mechanical
the moment facts are written against these names, because then it is a data migration.

### Recommendation

Two separable rulings; take the first now regardless of the second.

- **Style: spaced wins.** §3.11's table is the design's own convention and is the artefact both
  readings of D1 agree is canonical. Apply by script across all 13 catalogues before P6 Task 1, and
  add an assertion to `planning/domains/check.py` that no field name contains `_`. This has no design
  content — it is pure mechanics — so it does not need to wait on D1.
- **Identity: `subject` vs `course`, and the other four.** §3.1, §3.2 and §3.12 say `subject` in prose;
  §3.11's table says `course`. Four of P6's five naming questions are one question — the design states
  its field names once in prose and once in a table and the two disagree. One rule (table wins, or
  prose wins) settles all five. I have no risk-based preference between them; either is safe once it
  is one.

### Where this seat is weak here

None of my three harm paths is live. All three need code nobody has written —
`IdentifierClassifier`, P10's templates, P6's learning read. A reasonable person could answer that
these names live in JSON planning artefacts and a normalising loader closes the whole item in one
function. That is true. My counter is that a normalising loader is a second computation of one value,
which is defect class 2, which this project has also shipped — but I concede this is the item a risk
seat is most likely to over-rank.

---

## The §4b question

**Joseph's constraint has two halves. The first is implemented well. The second is promised in two
SPECs, correctly absent from P6 and P7, and its one live artefact is an orphan.**

### First half — never read, never moved: implemented, and defended

`scan_agent.exclusion.is_protected_container` walks the **whole ancestor chain**, not the entry's own
suffix. Its docstring records why: *"An earlier version of this function tested only the path's own
suffix, which protected `Numbers.app` and admitted `Numbers.app/Contents/sheet.numbers` — the exact
read the rule forbids. It passed every test, because every test asked about the bundle."*
`exclusion_for` checks it **first**, before every other §1.1 rule, and takes no keyword that can
switch it off; the `extra` predicate can only add members, never remove one. A rule with no override,
as ratified.

### Second half — findable later, and why P6 and P7 are right not to carry it

- **P6: zero mentions, and correct.** Nothing inside a protected container ever acquires a `file_id`
  or a `content_hash`, so P6 has nothing to resolve. Requiring P6 to carry the promise would require
  P6 to know about files that, by rule, do not exist. `22-p1-p7-connection-contract.md` §2 states the
  same reasoning for why refusal 1 produces no run row: it is *unconstructible*, not merely
  disallowed.
- **P7: three mentions, all vocabulary, and correct.** Task 2 pins `untouched_protected` beside
  `protected_container`, `protected_cloud_target`, `protected_records_template` and P7's own
  `protected` — *"five strings, one stem, and no code that treats any two as the same"* — so a later
  normalisation pass cannot collapse them. Task 21 asserts `src/privacy/` imports neither refusal.
  That is P7's whole obligation and it discharges it.
- **P13 holds the promise, and P13 has a SPEC and no plan.** P3's SPEC states it: *"P13 presents
  protected containers as a distinct, inspectable list (§8.6's progress line names the category; the
  review surface offers no action on the rows, because no action is permitted). A user who wonders why
  nothing was proposed for an application gets an answer instead of silence."* P13's SPEC carries it
  in the `review_action` block, labelled `untouched_protected`, with *"no action at all."*

A promise stated in two SPECs and owned by an unbuilt part is a dependency, not a defect.

### The actual gap, and it is live in code

**`LABEL_UNTOUCHED_PROTECTED` has no writer and no reader.**

- `src/scan_agent/exclusion.py:60` defines it, with a docstring saying it is *"§8.6's category name
  for the progress line and P13's inspectable list."*
- `ExclusionVerdict` has four fields — `path`, `rule`, `rule_subject`, `applies_to`. **No label.** The `exclusion_verdicts` table (`exclusion.py:148-155`) stores those four plus `verdict_id`,
  `scan_run_id` and `observed_at` — **no label column**; `replay.py:142` reads the same four.
- The only use of the constant anywhere in `src/` or `tests/` is
  `tests/p3/test_p3_protected_container.py:56`: `assert LABEL_UNTOUCHED_PROTECTED ==
  "untouched_protected"` — a constant asserted equal to its own literal.
- `summary.R5_COUNTERS` is five values with a comment reading *"There is no sixth."* The
  protected-container count is reachable only as a key inside `paths_excluded_by_rule` under the
  string `"protected container"` — which is `RULE_PROTECTED_CONTAINER`, a **third** spelling, neither
  the reason nor the label.

So the carrier of a promise Joseph made emphatically is a module constant that never reaches the
database, in precisely the shape `22-p1-p7-connection-contract.md` §5 names as this project's
recurring defect: *"a column that exists with no writer... indistinguishable from correct behaviour at
rest."* When P13 is built, its author will find the label does not reach them and will most likely
re-derive it from `rule == "protected container"` — a second computation of one value, defect class 2.

**Answer, stated plainly:** the second half is not carried through P6 or P7, and it should not be —
neither can see these files. It is carried through P3's and P13's SPECs, which is the right place. But
**no built code path puts `untouched_protected` where P13 can read it**, and the fix belongs in P3
now, not P13 later: add `label` to `ExclusionVerdict`, persist it, and add the sixth counter to
`R5_COUNTERS` — or state in the SPEC that the count derives from `rule`, and delete the constant.
Three lines either way. Leaving an orphan string is the option that reads as done and is not.

---

## The single risk I would not ship without resolving

**D2 — `sensitivity`: one record or three.**

It beats the other five on four counts:

1. **It is the only one whose failure is invisible at rest.** Every other item announces itself. D1
   fails into a residual pile the user can see. D3 currently refuses out loud. D4 produces visibly
   worse results. D5 produces a `failed` run someone will eventually investigate. D6 produces a
   duplicate row a reviewer can count. D2 produces a NULL that looks exactly like a correct value, and
   a wrong vocabulary that looks exactly like a right one.
2. **The project has already shipped this defect on this exact concept**, two days ago, and the fix
   survives only as a comment at `src/orchestrator.py:305-311` and a standing rule in a planning
   document. P7 Task 4 is about to give the column its first writer, which is the moment the rule
   stops being self-enforcing.
3. **It is a precondition for two other items.** D3 cannot define "derived" without knowing which
   record holds the sensitivity that decides what is derived-and-protected. D5's whole damage chain —
   `failed` → `unreadable_unclassified` → `Denied` — runs through the record D2 names.
4. **It gates the one action that cannot be undone.** Every other failure here costs quality, time, or
   trust that can be rebuilt. This one decides whether a medical document is in a cloud prompt, and
   §8.4 says in its own words that revocation *"cannot necessarily retract data already sent to an
   external provider."*

**What closing it looks like:** one sentence — *P7's `ClassificationRecord`, keyed
`(file_id, content_hash)`, is the authoritative record; `files.sensitivity_state` holds a
`HANDLING_CLASSES` member verbatim or is dropped; §3.11's `sensitivity status` is a projection with no
independent writer* — plus one test discipline: **every assertion about it compares a value, never
non-nullness.** A non-null assertion cannot tell the two columns apart, and that is exactly how the
previous instance survived.
