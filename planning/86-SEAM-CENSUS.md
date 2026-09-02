# 86 — The seam census: is every part connected to every part it must be?

`84` §5.5 names the dominant defect class: *"The suite tests PARTS. The defect lives in
the WIRING."* Three shipped defects — a residual library built and passed `{}`, a
learning guard with no caller, an egress guard nothing reached — had passing tests,
because every test that touched them constructed BOTH sides itself.

Numbered `86-` as the brief asked; `86-PROMPT-STRESS-RESULTS.md` is a peer's and this
sits beside it, which is this repo's own convention (`13-`, `18-`, `19-`, `26-`, `28-`,
`42-`, `43-`, `70-`, `71-` are all doubled).

`85` counts unreachable MECHANISMS. This counts SEAMS: for each ordered pair of parts
the design says must talk, does data actually cross on a run of `cli.main`?

**Status: 57 ordered pairs measured, 31 of them design-named and triaged here with a
verdict — 18 connected, 7 dark on an owner decision, 1 dark and a gap, 5 carried;
the remaining edges are the ones every part has to P1 and to the composition
root, which are triaged as one row each rather than 26. P12↔P13 and P13↔P9/P10 are
carried untriaged on purpose — two peers are mid-flight in them (§7).**

---

## 1. The measurement

Not an import graph. An import proves a name is visible, and all three of `84` §5.5's
defects had the import and no call. This runs the product under `sys.setprofile` and
records, for every Python call, the package each end lives in.

```
python3 -m pytest tests/integration/test_seam_census.py -q -p no:randomly -rx
```

The map is asserted, both ways, in `tests/integration/test_seam_census.py`: eighteen
seams the design requires must carry traffic, and eleven it names that do not must stay
dark. Wiring one of the eleven turns the suite red and forces this document to be
updated, which is what stops a census rotting. Both directions were proved by
sabotaging the implementation — P7 given its own `canonical_json`, P11 given one call
into P12, the root asking P12 for a plan, the destination segment lower-cased, the
gate's mode branch disabled, and P7's remedy spliced into P11's sentence.

**Always re-measure. Never quote a number from this file.** `85` §1's warning applies
here for the same reason: the population moves as parts land.

### What counts as a part

`02`'s thirteen, one package each, plus three units that are not parts and are named as
such: `src/questions/` (`84` §3 — what "P15" means in this repo), `src/readers/` (P5's
deployment layer, `02` "not a fourteenth part either") and `src/recognition/` (the
injected sensitivity rule set D2 leaves to a deployment). Fourteen units on the P-scale,
seventeen nodes counting the composition root.

### One caveat, stated so nobody over-reads a green row

An edge is any frame in package B entered from a frame in package A, which includes a
shared record's `__post_init__`. `P11 -> P9` is partly that: P11 constructs P9's
membership records. It is still data crossing the seam — it is not a call to a
decision. Where that matters the row says so.

---

## 2. The measured map, 2026-09-02

Union over every gesture a person can type — a plain run, a second run over the same
disk, `--residual`, `--send-set`, `--reject`, `--answer`, `--list-situations`,
`--list-residuals`. A seam that only one gesture reaches still counts as connected; the
call counts in §4 are that union's, not one run's.

```
ROOT         -> P1 P2 P3 P4 P5 P6 P7 P8 P9 P10 P11 P12 P13 QUESTIONS READERS RECOGNITION
P2           -> P1
P3           -> P1  ROOT
P4           -> P1
P5           -> P1 P3 P4 READERS  ROOT
P6           -> P1 P4  ROOT
P7           -> P1 P4
P8           -> P1 P4
P9           -> P1 P4 P6 P7  ROOT
P10          -> P1 P3 P4 P6 P7  ROOT
P11          -> P1 P6 P7 P9  ROOT
P12          -> P1
P13          -> P1
QUESTIONS    -> P1 P4 RECOGNITION
RECOGNITION  -> P1 P3 P7  ROOT
```

`ROOT -> P8` is `create_llm_schema` and `create_budget_schema`. `ROOT -> P12` is
`create_mutation_schema`. `ROOT -> P13` is `create_review_schema`. **Three whole parts
whose only contact with a person's run is `CREATE TABLE`**, and their `-> P1` traffic
above is that schema creation, not use.

---

## 3. The three verdicts

Borrowed from `85` §2 unchanged, because the rule that separates an honest verdict from
a whitelist entry is the same one: it earns its place by a reason that is TRUE OF THAT
SEAM.

- **Connected.** Data crosses on a real run and the test asserts it.
- **Dark, and the reason is an owner decision.** Nothing is broken; something is
  unanswered. Wiring it would mean an agent answering it.
- **Dark, and it is a gap.** The design promises it, nothing is blocking it, and a
  person feels its absence.

---

## 4. Connected — 18 seams, asserted

| Seam | Evidence (calls, union over every gesture) | Why the design requires it |
|---|---|---|
| P3 → P1 | 432 calls; `record_file`, `append_event` | `02`: P3 publishes a populated `files` |
| P4 → P1 | 1,141 | `P4 SPEC` Contract in |
| P5 → P4 | 138; `observation.check_non_empty`, `runs.config_fingerprint` | §2.8 — the reason P4 precedes P5 |
| P5 → P3 | 6; `exclusion.is_protected_container` | `P5 SPEC`: an excluded path never reaches an extractor |
| P5 → READERS | 3; `readers.deployment.read_text_file` | `02`: the deployment's libraries fill P5's shapes |
| P6 → P4 | 1,418; `observation.locator`, `canonical.sha256_of` | `22` §1 |
| P7 → P4 | 30; `canonical_json` from `policy`, `learning_seam`, `classification_store` | `22` §1 — M5's three context fields |
| P7 → P1 | 295 | `02` D2: P7 authors the §8.4 audit record, P1 stores |
| P9 → P6 | 51; `read_surface.{proposal_eligible,event_facts,family_facts,session_facts}` | `30` seam ledger P6→P9 |
| P9 → P4 | 31; `store.observations_by_key` | `P9 SPEC`: P9 cites `observation_key` |
| P9 → P7 | 18; `classification.resolve_class`, `classification_store.current` | `P9 SPEC`: §3.11's sensitivity status |
| P10 → P6 | 72; `fields.get_field`, `read_surface.is_destination_eligible`, `supersede.preferred_fact` | `38` §4 |
| P10 → P7 | 18; `classification_store.current` | `38` §11.5 |
| P10 → P3 | 18; `exclusion_verdicts`, `directory_inventory`, `selection.get_selection` | `P10 SPEC`: the person's existing folders |
| P11 → P9 | 12; `acceptance.group_state_as_of`, `store.memberships_for_group` | `P11 SPEC` §6.8 |
| P11 → P6 | 12; `read_surface.is_destination_eligible` | `P11 SPEC` |
| P11 → P7 | 60; `denial.mode_forbids`, `denial.unclassified_denies`, `policy.current_policy` | `38` §11.5 |
| RECOGNITION → P7 | 6; `ClassificationRecord` construction | `02` D2 |

**P6 → P9 was the seam the brief said to suspect, and it is live.** `proposal_eligible`
is really called, a group is really proposed, and the run's report names it. It is now
asserted rather than assumed.

**P11 → P7 deserves its own note, because it looks like a bypass and is not.** P11 calls
`privacy.denial.mode_forbids` and `unclassified_denies` rather than `Gate.release`.
`placement/privacy.py`'s module docstring is 70 lines explaining exactly why: those are
P7's own published predicates, `model_eligibility` has no producer in `src/privacy/`,
and the alternative is P11 restating §8.4. `84` §5.1 — read the docstring before calling
something a bug. Not a defect.

---

## 5. Dark, and the reason is an owner decision — 7 ordered pairs, 4 causes

### 5.1 P7 → P8, and P8 → P7. **The most important seam in the product.**

`cli.py:1656` passes `gate=None, model_client=None, prompt=None`; `cli.py:1697` passes
`p8_run_call=None, p8_authorities=None`. `Gate.release` is never called. §8.4's door has
never been opened on a person's run.

**Blocked, not broken.** `run_call` requires a `PromptDefinition` with non-empty
`template_bytes` (`llm_harness/records.py:89`); `84` §1 forbids an agent authoring or
adopting prompt text; `planning/82` is a draft the owner has not ratified. The agent
`wire-deepseek` reached the same blocker independently.

**What was proved instead.** `22` §6 check 4 records itself as *"vacuous in the safe
direction"* — "no content reaches a model before P7's classification" is trivially true
while nothing is classified. `src/recognition/` classifies on a live run now, so the
door can be asked for real, and
`test_the_gate_refuses_the_call_the_report_says_was_not_cleared` asks it: over the
policy, classifications, files and observations a real run wrote, `Gate.release` returns
`Denied(mode_forbids_target)` — the same verdict the person was shown. That agreement is
now a guard. Check 4 is no longer vacuous.

**And one finding.** The gate's answer carries `RemedyOption("use_local_model", "§8.4:
local rules and local models may run under this mode")`. `remedy_options` has **no
consumer anywhere in `src/` outside `privacy/`**. §8.6 requires the surface show "what
has been deferred, and why", and `privacy/denial.py` refuses to build a denial with no
remedy because *"a denial with no legitimate alternative is a dead end the user cannot
act on"*. P7 composes two remedies for this exact refusal from the design's own
sentences, and a person is shown neither — including the one that says a LOCAL model is
allowed under the mode they are running. P8's `Refusal` is specified to carry them
(`P8 SPEC` Contract in) and P8 is unwired; P11 re-derives the verdict without them.
Recorded as a strict xfail; not fixed, because the sentence is authored prose with
rulings behind it (`59` §3c, `66` §4).

### 5.2 P6 → P8 and P8 → P6 — fact validation

`30`'s ledger names `facts.llm_seam.build_request` → `validate_fact_proposal` →
`apply_verdict`. Same cause as 5.1. `facts.llm_seam` has no live caller.

### 5.3 P9 → P8 and P8 → P9 — group validation

`grouping/pipeline.py:612` is explicit that `p8_run_call=None` is a legal deterministic
run. Correctly dormant while 5.1 holds.

### 5.4 P11 → P8 — Site C placement validation

`placement/pipeline.py:505` asks `model_path_available()` BEFORE assembling a dossier,
which is the property `38` §6 wanted. With the injections `None`, a file that needs a
judgement abstains with a reason. Correct behaviour of an unwired seam, not a failure.

---

## 6. Dark, and it is a gap — 1 seam, and it is the expensive one

### 6.1 P11 → P12. **The product proposes a move and can never make one.**

`cli.py:130` imports only `mutation.schema.create_mutation_schema`. `cli.py:2467` prints
`"Nothing was moved."` unconditionally.

**The contract is sound; only the caller is missing, and that was measured rather than
assumed.** A `--send-set` run writes 6 real rows to `placement_decisions` and 0 to
`move_plans`, and prints *"Ready for you to approve, then file into Reading Inbox — 2
files"*. `test_the_place_decisions_a_real_run_writes_are_ones_p12_can_plan` takes those
decisions and P10's real frozen nodes — nothing hand-built — hands them to
`mutation.build_plan`, and P12 accepts every one and composes the right destination
path. Every field P12's Contract in reads is present and correct on what P11 really
wrote.

**Why no hunk was authored.** Applying a plan moves a person's files. It needs P13's
`review_approval` (P12 SPEC:207-215: absence is a refusal and no configuration skips the
check; `74` §9: the gate stays shut until Wave G2) and it needs seven composition-root
values, **four of which are open owner questions** — `collision_policy` (`74` §8 Q3),
`expiration_state` (Q8), `volume_of`'s cross-volume answer (Q7), and the filesystem
constraints of a real target volume. `84` §1: absent means refuse, never guess. An agent
picking those would be picking the rule by which someone's files get moved.

**This is the connection whose absence hurts a real person most.** Everything under it
is built and tested. Written up for the lead as entry 3 of the scratch `CLI-PATCH.txt`.

**Its person-facing half, flagged with it.** `cli.py:1948-1949` prints "Ready to file
into {where}" and "Ready for you to approve, then file into {where}". Neither is false —
the plan IS ready — but both name an act, and `--help` offers neither. `84` §6's second
standing ruling is that what the screen tells a person to type has to be true; this is
its neighbour. The two should move in one commit.

---

## 7. Carried untriaged, on purpose

Not laziness, and each row says whose it is. `85` §3 makes the same call about
`mutation.*` and `review_surface.*`: they are in flight and triaging them now would
produce a verdict about a half-landed part.

| Seam | Why not triaged here |
|---|---|
| P12 → P13, P13 → P12 | `p12-waveG-finish` is mid-flight in Wave F/G and has already filed the open defect (`retention.py:272` fills §9's `authorizing_policy` from the policy that DEMANDED review). Both parts are `CREATE TABLE`-only on a live run, which is all this census can add. |
| P13 → P9, P13 → P10, P13 → P11 | `81` §14 makes P9's and P10's vocabularies re-exports of P13's and `p13-eighteen-actions` is implementing it right now. The brief says coordinate by not touching them. Not touched. |
| P*, → P2 (`stage_output`) | Every part publishes a `stage_output` emitter and none is called on a live run: `ROOT -> P2` is bundle writes only. `85` §3 already names P2's replay driver as a probable third single cause; that reading is consistent with what this measured, and belongs in `85`'s frame rather than duplicated here. |
| QUESTIONS → P6 | Absent. `_raise_blocked_questions` runs after P1–P7 and reads the corpus's own ambiguities through `RECOGNITION`, not through facts. Whether `75`'s onboarding plan requires a fact read is not settled by reading the trace, and inventing the requirement would be worse than the gap. |
| P5 → P7 | `02` M10's acknowledged back-edge: audio/video transcription is authorized by §8.4. No audio or video in any corpus this was measured on, so the seam is untested rather than dark. Needs a corpus, not a wire. |

---

## 8. What this changes

1. **`22` §6 check 4 is no longer vacuous.** It has a test that asks §8.4's door about a
   file a real run really classified, and would go red if P7's door and P11's
   re-derivation ever disagreed.
2. **The wiring map is now a guard rather than a document.** Eighteen required seams and
   eleven dark ones are asserted on every run of the suite. All six twins were proved by
   sabotage.
3. **Two causes, not thirty findings.** `85` §3 found the reachability backlog collapses
   into "no model transport" and "P13 unreachable". The seam census independently
   collapses into the same two plus one more: **nothing applies a plan.** Every dark
   seam in §5 and §6 is one of those three, and each of the three is one decision.
