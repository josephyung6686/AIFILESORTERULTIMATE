# 106 — The day the rules stopped deciding: what was done and what was learned, 8 Sep 2026

**Written by the lead at the end of the session.** A standalone account, readable by someone who
was not here. `104` §17 is the register entry with the same facts in the register's own idiom; this
document is the narrative, the reasoning, and the parts that generalise beyond this repository.

Working branch `build/p6-p7-first-packages`. Session start `d1a135e`, session end `9e317ac`.

---

## 1. What this system is, stated once and bindingly

**An LLM is the decision engine that sorts files**, with minimal human input and maximum
customizability. The owner ruled this on 8 Sep. It is not a description of an aspiration; it is the
rule against which every code path is now judged.

The extraction pipeline, the database and the schema packaging exist for exactly one reason: **to
make each model call cheap and well-aimed**. Code therefore does one of two things — it feeds the
model better inputs, or it applies the model's outputs. A path that decides a placement, a category
or a name *without* the model is one of two things:

  (a) **a legitimate deterministic pre-filter** that narrows what the model must decide. `00`:110
      sanctions exactly this and no more: *"The LLM should not be called for direct, unique matches.
      If a file's validated facts uniquely match one frozen path, deterministic matching is faster,
      cheaper, and more stable."*
  (b) **a bug** — a rule masquerading as a decision.

**Every document in this repository that reads as rules-first predates this framing and does not
overrule it.** That includes parts of `104`'s own register and of `103`.

The target architecture, also ruled: **cloud-majority, with local reserved for protected material**,
on the provider already wired. The sequencing is the owner's and is explicit: **the local run
happens first, to prove the pipeline decides at all; the cloud upgrade follows it.**

---

## 2. Where the day started

Chain w1bn had finished on `d1a135e` and nobody had read it. It said **13 failures** and a sorting
row of **0 of 41 placed**, against the previous chain's **5 of 41 "right parent, wrong leaf"**.

That reads as a five-placement regression caused by R-160 (notebooks read as cells). It is not one,
and understanding why reframed the whole day.

---

## 3. The five things that turned out to be true

### 3.1 The five placements were JSON punctuation

Measured at three commits with the same fixture:

| commit | notebook verdict |
|---|---|
| `8eb41e0` (pre-R-160) | `Recognition(schema_id='code')` |
| `29a7d0f` (R-160 merged) | `Abstention(tied: academic, code)` |
| `d1a135e` | same abstention |

The `code` schema's authored terms include **`kernel`, `source`, `cell`, `notebook`, `ipynb`**. A
raw `.ipynb` is JSON containing `"cells"`, `"source"` and `"kernelspec"` **as dictionary keys**. The
term counter matched those keys, `code` led four-plus to one, and four notebooks were "recognised".
The test that pinned this behaviour said so in its own docstring: *"Four of the owner's five
`Python 1006` lecture notebooks come back exactly this way... They are the four the run places."*

R-160 made a notebook's cells be read as their own text. The punctuation went, and with it the
placements. **R-160 did not lose five placements; it deleted a false signal and the row fell to the
number that was always true: 0 of 41.**

This is the register's own best example of §1's rule. A rule masquerading as a decision, scoring as
a win, for weeks, invisible to every instrument the project had.

**The general lesson:** a deterministic matcher fed serialised structure will match the
serialisation. The fix is not a patch for notebooks — it is the rule R-166 now enforces: *the name
of a file's format is not one of its words*, guarded by a test that fails the day any schema term
becomes satisfiable by a container's structural keys.

### 3.2 The gate was never the wall — the register had a cloud statement filed as a general one

The register's account of R-01 and R-32 is: an unclassified file is refused a model call, 95 of 199
files are unclassified, therefore the model never sees them. The lead repeated that framing earlier
in the same day and it is **wrong for the target this project is about to run on**.

- `privacy/denial.py:221` — `UNCLASSIFIED_PERMITS_LOCAL = True`. The owner answered P7 SPEC Open
  question 5 twice (`104` §15.3, R-121): a LOCAL model may be asked about an unclassified file, a
  cloud one may not.
- `unclassified_denies` returns `True` unconditionally for `cloud`; for local it returns
  `not local_calls_on_unclassified`, which is `False`.
- `no_safety_evidence_denies`, in its own docstring: **"LOCAL IS STILL PERMITTED UNCONDITIONALLY,
  evidence or no evidence."**

What actually happens is different and worse. `cli.py:4220` builds site A's activation as
`ActivationSignal(schema_id=schema, activates=lambda facts: True)` — where `schema` is **the run's
single `--situation`**, activating for **every file unconditionally**. So nothing is silent: 617
site-A dossiers over 199 files is everything being asked.

**Every file is asked the questions of the one situation the run was launched with. A vaccination
record is asked which course it belongs to.** That is R-23, and it is where the spillover number
comes from — 17 files labelled as other domains landing in Coursework.

Site G's claim is therefore *larger* than first written: not "unblocks 95 silent files" but "each
file is asked about its own situation instead of the run's". Its payoff will appear in **spillover
and wrong-placement**, not only in exact.

**The general lesson:** a measurement recorded under one configuration becomes a general belief the
moment it is written without its conditions. Every row in a register should name the target it was
measured against.

### 3.3 The evidence dies at release, not at extraction

An external diagnosis argued the root cause was extraction fidelity: two independently-built stages
(the rule matcher and the model) failing for the same reason means the fault is upstream of both.
The inference is sound; the conclusion is contradicted by measurement.

- Extraction produced **18,489 text units and 3.3M characters** over 199 files. The text is there.
- §16.2 already ran the audit that diagnosis recommends: for **23 files the course code IS in the
  extracted text and NOT in the dossier**. For 20 more it is in the folder path, which extraction
  *does* record as an observation.

The loss is at `may_be_released`, whose four exclusions each refuse **the whole request, not the
item** — *"one bad observation among eight costs the file its call"*. The dominant one is the
whole-unit rule: a PDF page arrives as one span-less ~1,500-character unit, so a rule written to
stop a whole-DOCX leak refuses every page of every PDF.

Split by target, measured this session:

| target | files with body readings | of those, get nothing | median released body chars |
|---|---|---|---|
| local | 129 | **12** | 106 |
| cloud | 129 | **76** | **0** |

R-159 had already unstarved local. **Cloud is shown zero characters of any document** — which is
also why cloud currently *looks* safe.

### 3.4 The model's good answers were being thrown away, and the dossier was shaped like the answer

Two causes, both about applying outputs rather than producing them.

**R-162.** 234 of 619 responses are nested and binned on bracket shape — roughly 38% of the model's
answers discarded *after* it answered.

**R-163, and the mechanism is sharper than the register's description of it.** The glossary was a
JSON object mapping each answerable field key to one string. That **is** the answer form, sitting in
the dossier already filled in — while `released_evidence`, the only place a value may legally come
from, is a list keyed by observation and **not by field at all**. So the one structure in the
dossier shaped like the answer was the one place a value could never legitimately come from, and the
model filled the answer out of it: on r15 the literal `work_type` was proposed as a value 16 times,
the phrase from its meaning 6 times, `term`'s own sentence 3 times. It is now a list of
`field`/`meaning` pairs. Every glossary *sentence* is unchanged, deliberately — `104` §16.3 rules
that laundering the symptom out of the answer is not the fix.

The same change fixed a second thing found on the way: `canonical_json` re-sorted that object's
keys, so the dossier printed the vocabulary in the tree's nesting order and the glossary
alphabetically — **two orders of one list in one document**.

### 3.5 The cache cannot see a changed dossier

The next local run could be seeded from the previous run's answers, cutting it from ~7 hours to ~2.
**It must not be.**

`model_facts.call_identity_dimensions` is the reuse key: `content_hash`, `extractor_versions`,
`model_id`, `prompt_fingerprint`, `schema_id`, `policy`, `plan_version`, `context_refs`. **The
dossier's content is not a term.** `extractor_versions` is a *set of `(name, version)` pairs* —
which readers ran, never what they produced.

So any change that alters what the model **sees**, without moving a reader's version, the prompt
template, the schema or the policy, is invisible to the cache. R-164 and R-163 are both exactly
that. It was confirmed twice: `structured_text.VERSION` still read `"0.1.0"` after R-164 changed
what it emits, and the r37 fixture diff shows `HW 3.txt` going from one whole-body observation to
two paragraph observations **with `extractor_version` reading `0.1.0` on both sides**.

`00`:44 says the cache key exists so that *"an upgraded reader invalidates the answers that rested on
its output."* The reader was upgraded and the version was not. Fixed; the version is now `0.2.0`
with the reasoning in the source.

**The general lesson, and it is the most transferable thing here:** a cache key made of *provenance*
(who produced it) is not a cache key over *content* (what they produced). The two coincide only
while producers are immutable.

---

## 4. What was built and merged

Six branches, merged one at a time with a score run after each, because §3.1 is what happens when a
group is merged and chained once.

| Head | What is now true |
|---|---|
| `5ff35c0` | the payload instrument asks release about the target and ceiling the run uses (12 failed → 20 passed) |
| `2a0e3ac` | R-165: every sorting number says who decided it; R-147 aliases so a course named two ways scores as one |
| `15c34a8` | R-166: a file's format name is not one of its words; a tie cites the observations it rests on |
| `409a699` | R-164: plain text is read one paragraph at a time; the opening of a unit is minted as its own reading |
| `198da90` | R-162/R-163: a claim written inside a citation list is read; the glossary stops being shaped like the answer |
| `73b7cd4` | R-161: person-valued fields signalled by the field; site B withholds instead of losing the call |
| `d0ec05d` | R-167: the seventh call site asks each file which situation it is |
| `5aa0898`, `9e317ac` | what the merges exposed, fixed |

**Chain w1bp at `198da90`: 2 failed, 9594 passed, 20 skipped, 21 xfailed, 44:02.** Both failures were
deliberate R-164 changes with assertions still recording the old truth; both are fixed and one of
them is the proof in §3.5.

**The offline coursework row did not move: 0 / 0 / 0 / 0 / 41 throughout.** That is the expected
result and not a disappointment. Every one of these changes bites only when a model is answering,
and an offline run has no model. **The offline scoreboard is not the discriminator for any of this
work. The local run is.**

What *did* visibly change: every SORTING line now reads `-- the model decided none of this run's 2
placements`. §3.1's artifact could not have hidden behind that line.

---

## 5. Three findings that were not on anyone's list

**A person's name was being persisted, not merely released.** `grouping/dossier._excerpts_for`
wrote `observation.raw_value[:limit]` inline into the **stored** group dossier. Verified as harmless
today rather than assumed: site A persists by *reference* — a stored payload carries `evidence_ref`
digests, `kind`, `location` and `excerpt_span`, no raw text — and all 656 stored dossiers in the
local run database were scanned and none carries an author-type field. All 656 are `A_fact`; site B
has **zero rows** because it has never been ratified. The fix lands before site B is ever turned on,
which is the good version of this outcome.

**Site B was the one request builder of four with no signalled-key filter.** `may_be_released`
(site A) and `releasable_excerpts` (site C) already dropped a signalled key from the offer rather
than failing the request — so the trap that made R-161 look dangerous cost nothing at two of four
sites. At site B, `Gate._precheck_items` returns on the first refusal, so one signalled reading among
twenty cost the group its whole call. Four lines.

**An 8× slowdown that is not new code being slow.** The score run went 1.4 → 11.3 minutes at the
R-166 merge. `_precaution` re-runs `_matches` for the safety domain on **every abstention**, and
R-166's guard correctly turned a large number of false recognitions into abstentions. A pre-existing
cost, newly exposed. Correctness is unaffected; at the 5,000-file target of Phase 4 it is hours and
must be fixed there.

---

## 6. What remains — one thing, precisely

Of the three walls the owner granted for site G, **two are open**: `G_situation_sensitivity` is a
member of `CALL_SITES`, and `local_model_situation` is a truthful classification basis so a model
verdict is never recorded as `detector`.

**The third is shut.** No situation prompt is ratified. Both authored candidates —
`situation.unratified.shortlist.2026-09-06` and `situation.unratified.safety-first.2026-09-06` —
carry no `status`, because the agent building site G hit a session limit with the bakeoff undone.
So `observe_locality_permits(G_SITUATION_SENSITIVITY, ...)` refuses, `ask_the_situation` is never
reached, and site G does not run.

`tests/integration/test_site_g_end_to_end.py::test_the_situation_verdict_is_written_under_the_new_basis`
is a **strict xfail** naming exactly this. Its four neighbours pass. It goes green the day the wall
opens, which is the signal — the same instrument `test_situation_site_boundary` was.

**To finish:** run the bakeoff of the two prompts on a fixture set under the local model per
`103` §28.1, set the winner's row to `ratified_local`, and site G is live.

**Then the local run.** `~/.graph-agent/lead/local-w3-r17.sh` is written, **unseeded** for §3.5's
reason, with that reasoning in its own header so a later reader does not "optimise" it. Ollama is up
and `qwen3:8b` is present. Roughly seven hours.

**What "it worked" looks like:** SORTING above 0, and spillover falling from 17. **What "it didn't"
looks like:** still 0 — in which case the run says which stage starved it, because every number now
carries who decided it.

---

## 7. Owner items still open

| Item | What it decides |
|---|---|
| 13 | the grammar-safe response schema; `r162`'s brief on it was never written and is owed |
| 16 | the glossary sentences themselves (the *shape* is fixed; the words are the owner's) |
| 17 | the model-decided bar |
| 18 | site A asked every field |
| **R-82** | the person's own folder labels crossing to a provider — **the last gate before any cloud run** |
| R-168 | 13 facts still *cite* a person-valued reading; value is a content hash, not a name. Needs `facts/discount.py`'s demotion rule, not P5's signal. Not urgent |

Items 14 and 15 are ruled and built.

---

## 8. Method notes worth keeping

- **Merge one at a time and score after each.** The whole of §3.1 happened because a number's
  provenance was unclear.
- **Recapture a golden fixture in the environment the suite runs in.** The first recapture here read
  `.env` and pinned a screen naming a cloud model the suite never configures; `tests/conftest.py`
  sets `GRAPH_AGENT_NO_DOTENV=1`.
- **A widened signature is found by running, not by reading.** R-159 and R-164 each made an argument
  required, and each time a caller written against the old one survived review and died in a chain —
  the payload instrument, then `test_person_field_withheld_not_fatal`.
- **Agents die; commit for them.** Five agents hit session limits mid-task in one day. Three had
  uncommitted worktrees totalling ~600 lines, saved only because the lead ran their targeted tests
  and committed on their behalf. Briefs now carry an explicit commit-early instruction.
- **An agent that refuses to claim a number is worth more than one that produces it.** `r161`
  measured sites A and B and said of site C: *"the count of C calls lost is unknown, not
  zero-by-assertion."* That sentence is why the rest of its report can be trusted.
