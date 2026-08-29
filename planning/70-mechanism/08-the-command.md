# 8. The composition root — what the shipped command chooses, and what a person sees

Every part P1–P11 decides nothing it was not given: thresholds, ceilings, clocks, catalogues,
policies and user answers all arrive as injected authorities with no default, and each part
refuses rather than guesses when one is missing. That discipline ends in `src/cli.py`, which
says so itself (`src/cli.py:1-10`):

> "That discipline has to end somewhere, because a real run needs actual numbers -- and this
> module is where it ends. **Every constant below is a deployment decision, and this is the
> only file in `src/` that makes one.** If a number appears here that `00` states, the comment
> says where; if `00` states none, the comment says that instead and names who owns the
> question."

This section inventories those decisions, the stand-ins where `cli.py` supplies what a person
or an unshipped part would, and what the person reads at the end. It closes with a run
performed for this document — real output, real database rows.

---

## 8.1 How to run it

```
python3 src/cli.py <directory> --situation <situation> --label <label> \
    [--user <user>] [--database <path>] [--list-situations]
```

No console-script entry point exists; `src/cli.py` is run as a file, with `python3` (there is
no `python` on PATH). The parser is built at `src/cli.py:988-1017`, `prog="database-agent"`,
described as: *"Read a directory, propose a folder tree for it, and say where each file would
go. Nothing is moved."* (`src/cli.py:990-991`). `tests/test_cli.py:100` pins that last
sentence — "`00`'s promise, in the first sentence a person reads."

### Why `--situation` and `--label` are required rather than guessed

The module docstring (`src/cli.py:12-22`) and `review_and_accept` (`src/cli.py:436-443`) give
the same argument twice: `--situation` "says which of the researched situations this corpus
is, which is what selects the applicability row that routes it", and cannot be answered
upstream because "P9 emits `group_category = None` on every path it has
(`src/grouping/pipeline.py:230` is the only writer and it is unconditional)"; `--label` "names
the branch. §5's tree is the user's, and P9's deterministic run produces no `display_label`
either."

**That justification is false, and §8.6's run disproves it.** `engine_proposal`
(`src/grouping/naming.py:128`), called unconditionally at `src/grouping/pipeline.py:499`,
writes `group_category=domain_for(...)`, `display_label=label`, `label_source=ENGINE`
(`src/grouping/naming.py:153-155`). The engine group in the run below carried
`display_label='PHYS1401'`, `group_category='academic'`, `label_source='engine'`. The citation
is also stale: `group_category=None` is `src/grouping/pipeline.py:300`, and it is the
pre-naming default `engine_proposal` replaces.

Neither flag is `required=True` in argparse, for a stated reason (`src/cli.py:995-998`):
"`--list-situations` exists to tell a person what to pass to `--situation`. A discovery flag
that requires the answer it supplies is a closed door: the only way to learn a situation name
would be to already know one." argparse cannot express "required unless another flag is set",
so the requirement is enforced by hand at `src/cli.py:1029-1034` through `parser.error`, so
the message and exit code are argparse's own:

```
usage: database-agent [-h] [--situation SITUATION] [--label LABEL]
                      [--user USER] [--database DATABASE] [--list-situations]
                      [directory]
database-agent: error: the following arguments are required: --situation, --label
```

`tests/test_cli.py:28` and `:45` pin both halves — the discovery flag reachable without its
own answer, and a real run still refusing to guess.

### `--list-situations`

`src/cli.py:1021-1025`, handled before the requirement check. Prints every distinct
`detection_signal_refs` entry across all applicability rows, `recognition:` prefix stripped.
Verified: **208 lines**, 11 under `academic.`, beginning `academic.continuing-education`,
`academic.coursework`, `academic.homeschool`, …

`_validate_situation` (`src/cli.py:536-551`) checks `--situation` against that same set rather
than a local list, "so a library that gains or loses a situation moves this check with it and
a typo is refused before a single file is read":

```
$ python3 src/cli.py <corpus> --situation nope.nope --label X --database <path>
This run was refused, and here is what it needed:
  'nope.nope' names no situation the shipped template library recognises. It carries 208; `--list-situations` prints them.
```

That is `NotConfigured` (`src/cli.py:228`), caught at `:1061`, exit 2.

### `--user` and the database location rule

`--user` defaults to `getpass.getuser()` (`src/cli.py:1010-1011`), help "who this plan belongs
to (recorded, never sent)". It becomes `selected_by` on the selection (`:562-564`), `user_id`
on the design decisions (`:633`) and on the privacy policy write (`:666`).

`--database` defaults to `Path.cwd() / "database-agent-plan.sqlite"` (`:1051`). The connection
is opened through `open_database(database, scan_roots=[directory])` (`:1053`), not
`sqlite3.connect`, for two reasons given at `:1046-1050`: it sets WAL, autocommit and
recursive triggers — and `build_destination_index` issues a `wal_checkpoint`, "which fails
outright ('database table is locked') on a connection in Python's implicit-transaction mode" —
and **it refuses a database inside the folder being scanned**, "which is why the roots are
passed in". `DatabaseInsideCorpus` is caught at `:1054`, exit 2:

```
/private/tmp/.../corpus/in.sqlite is inside the declared root /private/tmp/.../corpus; the database is never created inside a scan root (11-ops-runtime.md §2)
```

The rule is not decoration: a database inside the corpus is a file the next scan indexes, so
the plan would grow a row about itself.

**Exit codes.** `0` on a completed run and on `--list-situations`; `2` for a non-directory
(`:1037-1039`), a database inside the corpus, and `NotConfigured`; `1` for a named refusal
from `REFUSALS` (`:1065-1072`). Anything else is an uncaught traceback — which matters (§8.8).

---

## 8.2 The complete inventory of deployment decisions

Everything below sits between `src/cli.py:99` and `:238`, under a banner reading "THE CHOICES.
Nothing above this line and nothing in `production.py` picks a number."

**`COMPONENT_VERSION = "cli-0.1.0"`** (`:106`). Stamped on every row written. "§8.5 requires
the version tuple to be recorded; it states no format for it." Travels as
`p7_component_version` (`:421`), `component_version` on the design decisions (`:634`), the
policy write (`:666`) and the downstream authorities (`:763`).

**`SUPPORT_POLICY`** (`:115-117`) — `SupportPolicy(policy_id="cli-support-v1",
support_scale_max=1.0, minimum_support_threshold=0.50, margin_threshold=0.20)`. §6.10's two
conditions. "SPEC Open questions 1 and 2 leave BOTH the thresholds and the scale open, so
these are declared here rather than derived": `1.0` "because the scorer's weights already sum
to it"; `0.50` "because that is the band a direct fact alone (3/7) falls below and a direct
fact plus an accepted group (5/7) clears"; `0.20` as the margin, unargued. Auditability rests
on `policy_id`: "change a number and change the id with it, or a replay silently compares two
different rules." **The arithmetic does not match a real run** — every measured support score
in §8.6 was `0.2857…` = 2/7, not 3/7.

**`CEILING_VALUE = 8`** (`:123`). "`00` §8.6 names the ceilings and states no values, so these
are this deployment's. Eight is small on purpose: it bounds a first run on a real person's
disk rather than optimising one." Applied to **all seven** ceilings in one loop (`:532-533`)
over `CEILINGS` (`src/placement/config.py:26-34`). Read back out of the run's database:

| key | value |
|---|---|
| `placement.max_retrieved_neighbors` | 8 |
| `placement.max_local_graph_neighborhood` | 8 |
| `placement.max_candidate_cluster_size` | 8 |
| `residual.max_files_per_review_batch` | 8 |
| `model.max_dossier_tokens_per_call` | **8** |
| `model.max_llm_calls_per_thousand_files` | 8 |
| `model.max_cost_per_scan` | **8** |

Two are not quantities eight makes sense for: a **token** budget of eight tokens, and a
**cost** of eight unstated units. Both contradict the `max_dossier_tokens=4000` this same file
sets twelve lines later, and `max_retrieved_neighbors=8` contradicts `GROUPING_LIMITS`'
`max_retrieved_neighbors=50` on the adjacent line.

**`TREE_LIMITS`** (`:126-138`) — `max_folder_proposals=4, max_depth=5,
max_dossier_tokens=4000, excessive_depth_warning=4, tiny_folder_max_files=1,
tiny_folder_count_warning=2, materially_improves_retrieval=lambda option: True`. §5.7's and
§5.9's bounds; "`00` states no numbers for these either."

The first two fields were **one field until 2026-08-29**. Commit `f5132a1` split
`max_folder_proposals_and_depth=5` into the pair. Its message states the problem: `00`:256
reads "Maximum folder proposals and maximum depth" — two quantities on one line — and P1
published one key for both, which P10 read four times: "how many OPTIONS the picker offers,
how DEEP a candidate may go, how WIDE a date level may be before coarsening, and the sample
size of the printed lists. Two of those want opposite values."
`test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` had failed over it since it
was written; the split closed gate G2 (scale stress 19 passed, from 18/1). The comment left
behind (`:127-130`): "Four options is a picker a person can read; five levels is `00`:78's own
recommended tree, `Academics/Columbia/2026-Spring/PHYS1401/Homework`, which a depth limit of
four would refuse." `00`:78 is the line `        Syllabus/` — the fifth level of a *different*
example (`…/BUSIB 4300/Syllabus/`); the named tree is at `00`:98/105/106/111.

`materially_improves_retrieval` answers `True` because (`:134-137`) "A deployment with no
retrieval telemetry cannot measure it, and answering `False` would suppress every vertical
option; this answers `True` and leaves the judgement to the user, who sees the option's counts
and warnings before taking it." Nothing prints those counts and warnings.

**`GROUPING_LIMITS`** (`:141-144`) — `max_retrieved_neighbors=50, max_graph_nodes=10,
max_candidate_members=10, max_dossier_tokens=4000, generic_hub_frequency=9,
minimum_independent_anchors=1, max_excerpt_characters=240`. "P9's bounds. Same status as the
tree limits: named by §8.6, valued here." No per-number reasoning for any of the seven.

**`OPERATION_MODE = "offline"`** (`:150`), the strongest-argued choice in the file
(`:146-149`): "`offline` is chosen, not defaulted: it is the only mode under which nothing
about any file can leave the device, and a first run on somebody's home directory is not the
moment to ask for less." Reaches P1–P7 as `policy_settings` (`:419`) and P11 as
`Policy.operation_mode` (`:659-667`). Confirmed: `privacy_policies.operation_mode='offline'`.

**`ORDINARY_CLASS = "personal_non_sensitive"` / `PROTECTED_CLASS =
"highly_sensitive_credential_bearing"`** (`:156-157`). "The set is P7's vocabulary; which one a
node carries is a deployment decision, and the protected one is deliberately the strongest so
a marked container can never inherit a weaker floor than its contents would require." Used at
`:593` (every member is ordinary), `:594-595` (collapse yields protected if present at all),
`:596` (every protected area), `:597` (`protected_handling_classes`), `:614` (residuals).
Confirmed on both tree nodes. Note the asymmetry: `handling_class_for_member=lambda member:
ORDINARY_CLASS` declares **every file non-sensitive by fiat**, whatever P7 said; the
protection argument is about containers only.

**`ROOT_ANCHOR = "root_documents"`** (`:160`) — §1.1's root anchor. Confirmed on both nodes.

**`PLAN_VERSION = "plan_0"`** (`:163`) — "The review this run's groups and acceptances belong
to." It is what P9 writes against and P10 designs from (`:610`, `:776`). P10 then mints its
own: the run below produced `version_0` (draft) and `version_2` (frozen).

**`COLLECTOR_FIELD_KEYS = frozenset({"authored_by", "organization"})`** (`:168`). "§3.8's
collector roles, which V4 uses and refuses to receive empty. P6 owns which fields collect and
its vocabulary is still widening, so this names the two that plainly do rather than pinning a
count that other work would break."

**The single structured-string pattern** (`:188`):
`_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")`. §2.2's patterns. "P5's SPEC
puts these in its Deferred table and ships none, so they are the deployment's. ONE, and
deliberately narrow" — an identifier token, "like PHYS1401, INV20261, AC4471 -- which is
§2.2's own 'identifiers' class". The narrowness is argued (`:173-175`): "A wider pattern would
put more of the file's text into P4's observations, and a first run on somebody's disk is not
the place to widen what gets read." The single separator was added 2026-08-29 because the
first real run returned `NothingToDesign` over files saying `PHYS 1401`; `63` §10's ruling is
quoted and verified at `planning/63-IMPLEMENTATION-PLAN.md:291`: "**Ruling: widen the
extractor. Do not add a question.** No onboarding answer could have recovered that course
code." The posture is stated unchanged — uppercase token, three or more digits — "so a date, a
sum of money, a page number and a sentence are all still invisible to it".
`tests/test_cli.py:387` is the negative twin.

**`_SEPARATOR`** (`:195`) — `re.compile(r"(?<=[A-Z])[ -](?=[0-9])")`. "`PHYS 1401`,
`PHYS-1401` and `PHYS1401` are one course code and must reach P6 as ONE value: `65` §4.2
records what happens when one identity arrives as several -- four files from one course became
four one-file groups carrying the same label, and the course folder was proposed and left
empty."

**The single direct slot** (`:206-213`) — one `DirectSlot`, `slot_id="cli.text.identifier"`,
`field_key="subject"`, matching locators starting `body#` or `heading`, canonicalising by
collapsing whitespace then removing the separator. §3.5's slot set. "`DirectSlots` has no
default because the slot is the caller's; this deployment reads ONE… The claim it makes is
narrow and it is this deployment's to make: an identifier printed in a document is what that
document is ABOUT." The `/Title` slot §3.5 also names is deliberately absent, by a chain
(`:203-205`): "its observation carries no text span, P7's gate cannot release a span-less
excerpt, and a group anchored on it could never be reviewed."
`METADATA_SCREEN = MetadataScreen(tool_producer_strings=(), metadata_property_names=())`
(`:214-215`) — §2.2/§2.3's suppression catalogue, empty, uncommented.

**`RESIDUAL_LIBRARY = {}`** (`:222`). "§7.3 fixes nine residual template names and leaves
their eight attribute slots deferred. This deployment enables NONE rather than inventing slot
values: an unplaced file still reaches §7.5's review set with its reason, so it is counted and
explained -- which is the property that matters -- and it does so without a folder nobody
designed."

**The absent model route**, in three parts. P6: `stages={"direct": _direct_stage, "rule":
None, "llm": None}` (`:324`), with `model_route_permitted=lambda file_id: False` — "§3 allows
all three stages. This deployment ships no authored rule set and no model route, and
`FactFesolver` treats `None` as 'this stage does not exist' rather than as an empty one -- so
a fact this run could not reach stays unresolved and visible instead of being recorded as
absent." (The docstring misspells `FactResolver`.) P9: `p8_run_call=None, p8_authorities=None`
(`:757`), which `production.py:414-418` enforces as both-or-neither. P11: `gate`,
`model_client`, `prompt`, `call_dependencies`, `model_call_request`, `chosen_node_of`,
`residual_action_of`, `sensitivity_policy`, `p2` all `None` (`:729-731`) — "with them `None`,
a file that needs a judgement abstains with a reason instead of being decided by nothing."

**The absent rule stage** is the same line — `"rule": None` at `:324`.

**The detector, which is not absent.** `classifier` (`:351-377`) wraps a real `Detector` built
at `:565-567` from `src/recognition/library/recognition.json` with `SAFETY_DOMAIN_HANDLING`
and `is_protected_container`. What is absent is any fallback behind it: "A file the detector
declines to answer about stays UNCLASSIFIED, and that is the whole policy." The docstring
records what it replaced — a blanket `highly_sensitive_credential_bearing, protected=True` —
and why it went (commit `6be2ada`, "an unreadable file is not a passport"): "It made an
unreadable scan and a passport identical in P7's store -- same class, same flag, same sentence
to the user -- and made the honest unclassified path unreachable from this command… Over-
protecting is not free. 'We deliberately did not look' and 'we could not tell' are different
answers, they ask the user for different things, and a product that says the first when it
means the second is lying in the direction that happens to feel safe." The supporting
quotation "sensitive personal material is not the same thing as `Numbers.app`" is attributed
to `` `00` `` (`:366`); it is not in `00` — it is
`planning/59-FINAL-UX-EVALUATION.md:251`.

### The rest, for completeness

* `context_window=240` (`:417`) — §2.6's excerpt window in characters, "`00` states none".
  Matches `max_excerpt_characters=240`.
* `transcription_authorized=lambda: False` (`:418`) — "Transcription opens audio and video.
  Not authorised, and saying so is what keeps it off rather than the absence of a transcriber."
* `usable_threshold=lambda facts, unresolved: True` (`:392`) — §3.6, always "usable", so
  targeted OCR never fires; answering `False` "would send every text-bearing PDF through Apple
  Vision on the strength of a threshold nobody chose."
* `_detect_format` (`:341-348`) — `{".pdf": "pdf", ".txt": "txt", ".md": "md"}`, by **extension only**, argued:
  "sniffing means opening the file, and the one class of file this command must never open is
  decided by PATH (`is_protected_container`) before any format question is asked."
* `scan_state=P1_INCLUDED_SCAN_STATE` (`:404`) — imported, never respelled, with the bug it
  fixed recorded: "This wrote the literal `\"scanned\"`; P9's `_corpus` admits `scan_state =
  'included'` and nothing else, so on every live run the neighbourhood of every file was
  EMPTY, no shared-fact edge was ever built, and every group was a group of one whatever the
  corpus said. P9's own tests write `included`, so 5,000 of them agreed with a production path
  that could not form a group of two."
* `SafetyPolicy(is_protected_container=…, is_dataless=lambda path: False)` (`:410-411`) — "THE
  standing rule, at its first enforcement point."
* `sensitive_group_ids=frozenset()` (`:581`) — no group declared sensitive, "P7 classifies
  FILES and publishes no group-level answer".
* `privacy_rank=lambda floor: 0` (`:586`) — everything ranks equal, "the only ordering that
  cannot give a branch a weaker floor than one of its files by accident."
* `value_discloses_protected_material=lambda field_ref, value: False` (`:603`) — §5.11, with
  the alternative named: answering `True` "would suppress every label in the tree."
* `rank_candidates=lambda candidates: list(candidates)` (`:592`) — library order kept "rather
  than inventing a score."
* `satisfies_purpose_profile=lambda ref, groups: True` (`:587`) — **no comment**.
* `max_return_cycles=1` (`:725`) — **no comment**.
* `evaluation=None` (`:763`) — §8.5's replay declared absent: this command "scans a person's
  own folder, which has none, so it declares no evaluation rather than publishing a score
  against a baseline that does not exist."
* `EmbeddingsOff()` and an all-`None` `RetrievalKnowledge` (`:746-749`) — "every similarity
  channel is off and retrieval is by shared validated fact alone."
* `generic_entity_frequency=200` with `entity_frequency={fact.value: 1 …}` (`:697-698`) —
  §6.5's suppression. "Both numbers are this deployment's; `00` states neither." Every value is
  hard-coded 1, so nothing can ever reach 200.
* `REFUSALS` (`:235-238`) — six exception types printed rather than raised, "because a refusal
  with a reason is an answer and a traceback is not. Imported here rather than caught as
  `Exception`: an unexpected error must still crash loudly."

---

## 8.3 The stand-ins

Where `cli.py` supplies what a person, or an unshipped part, would.

### `review_and_accept` — the review screen, and the one-folder tree

`src/cli.py:429-478`. *"The review screen, non-interactively: keep everything, as one named
group."* It writes **one** `Group` under `group_id = f"{PLAN_VERSION}:{label}"` —
`plan_0:Coursework` — whose `proposed_basis` is `f"the user confirmed these files are
{label!r}"` (`:455`), `anchor_facts` is every group's facts concatenated (`:456-457`),
`pre_model_signals` is `{"reviewed_proposals": len(grouped)}` (`:458`), `anchor_count` is the
**sum** across results (`:459`), `coherence_verdict` is `COHERENT` asserted not derived
(`:460`), `group_category` is `situation.split(".", 1)[0]` (`:451`, `:463`), `display_label` is
`--label` with `label_source=USER_EDITED`, and `supersedes` is the **first** group's id
(`:467`). Every membership is re-recorded against the merged id (`:470-472`, `:481-487`) and
one `GroupAcceptance` is written (`:473-477`).

**The consequence: the tree is one folder deep on every corpus.** P10 builds the top level out
of accepted groups (§5.3); there is exactly one. `planning/68-PERSONA-RERUN.md` F3 measured it
across four:

| | groups P9 formed | what the person was shown |
|---|---|---|
| Priya | `PHYS1401` (2), `PHYS2801` (2) | one folder, `Coursework` |
| Mara | `CV20261234` (4), `X12345678` (1) | one folder, `Matters` |
| Tom | `SPRING2026` (2), `CLM88213` (1), `PR20264410` (1) | one folder, `Household` |
| multi-life | four groups | one folder, `Coursework` |

and verified the counterfactual by experiment:

> "Patching the review to accept each engine group as itself and re-running Priya's corpus
> produced:
> ```
> Proposed folders: 2. 2 of them are somewhere a file can go.
>   PHYS1401
>   PHYS2801
> ```
> — which is the structure a person would expect, and which the shipped merge discards. The
> patch was reverted; it is not a proposed fix, because it also **drops the branch name the
> user asked for** (`Coursework` disappears entirely)… That decision is a review screen, and
> the review screen is **P13**."

That reasoning holds. Three arithmetic side effects of the merge are *not* covered by it, and
are visible in §8.6: with four `GroupingResult`s pointing at the *same* engine group,
`anchor_count` came out **16** for four files, `reviewed_proposals` came out **4** for one
distinct proposal, and `anchor_facts`/`coherence_citations` each hold four duplicate copies.
The merge does not deduplicate by group identity.

### `choose_option`

`src/cli.py:490-503`. *"§5.5, non-interactively: the first nesting §5.7's checks say may be
built. Stated rather than hidden, because it IS a choice and a person at a review screen would
make a different one. The options carry their counts, their warnings and their validation
report; this takes the first that passes and has children, and falls back to the last option
-- which is always `no-split` -- rather than raising, because a branch nobody could nest is
still a branch."* Nothing prints those counts, warnings or reports.

### `refinement_for`

`src/cli.py:506-519`. Every legal destination needs an answer or freeze refuses. Top-level →
`REFINED` with *"The levels beneath this branch were populated from facts that were already
settled in your files."* Anything below → `SHALLOW_BY_CHOICE` with *"This branch holds few
enough files that splitting it further would not help you find anything."* Both asserted, not
computed. In §8.6 the first sentence was written to `node_3` — a branch with **no levels
beneath it**.

### The shared-material answer — `mandatory-review`

`src/cli.py:626-631`. §6.9's policy, marked non-optional (`:615-620`): "`validate_for_freeze`
refuses a plan version without one, because a file that belongs to two homes leaves P11 having
to pick an institution. `mandatory-review` is the answer that keeps that decision with the
person, file by file, which is the only one a command with nobody to ask may make on their
behalf." The reason string reaching the record: *"Nobody was at the screen to say where
material shared between two of these folders belongs, so it stays your decision, one file at a
time."* `display_label="Shared Material"`, `policy_scope=None`.

Beside it `scoped_general=()` (`:632`) stays deliberately unanswered (`:621-624`): "`00`:99's
scoped General is genuinely optional… an unasked question answered by default is a folder
nobody wanted."

### `ask_or_abstain` — always abstain

`src/cli.py:724`: `lambda node_ids: pv.ABSTAIN`. "This deployment abstains rather than asking,
because there is no screen here to ask on and choosing one institution is the failure §6.9
exists to prevent." Consequence: `OUTCOME_WORDS[pv.ASK_USER]` — "Waiting for you to choose
where these go", the sentence a two-homes file should produce — is redirected to
`OUTCOME_WORDS[pv.ABSTAIN]`, "Waiting for you to say what these are", a different question.

### The residual partition — one set

`src/cli.py:700-714`. *"§7.5's review sets. SPEC Open question 10 leaves the taxonomy open, so
this deployment surfaces ONE set holding everything §6 could not place -- the smallest
partition that still shows every file with a reason."* The set is hard-coded:
`label="Not yet placed"`, `representative_examples=unplaced[:3]`, `file_type_distribution=()`,
`age_range=()`, `evidence_availability="partial"`, `sensitivity_status="none"`,
`protected=False`, `weak_graph_neighbours=()`, and `reason_not_placed="no destination in this
tree matched them well enough to decide without asking you."`

Two fields are asserted for every set it will ever make: `protected=False` and
`sensitivity_status="none"`. `_protected` (`:849-861`) reads `item.protected` as one of three
signals deciding whether a group is listed in full rather than summarised — so this stand-in
permanently disables one of three, and its docstring's justification ("the cost of the reverse
is the silent omission the standing rule exists to forbid") rests on the other two.
`representative_examples` holds raw file ids; they are stored but never printed, so the UUID
defect `bb898ce` fixed survives inside the database.

### `AcceptedGroupEnumeration` — a seam P9 has not published

`src/cli.py:246-296`. The clearest case of the composition root supplying a **part's** missing
API rather than a person's missing answer:

> "Three of its four methods delegate straight to P9. The fourth, `accepted(plan_version_id)`,
> has NO live P9 implementation: P9 publishes `group_state_as_of` for ONE group and nothing
> that enumerates the groups a plan version accepted (`src/tree_design/upstream.py` records
> this as SPEC corrections row 17). P10 deliberately does not work around it, because 'an
> enumeration P10 wrote itself would be P10 deciding which groups a plan version contains'.
> So it is written HERE, by the composition root that created the acceptances in the first
> place. The day P9 publishes the enumeration this class loses its first method and keeps the
> rest."

`accepted` is hand-written SQL over `group_acceptance` (`:266-271`); its one non-obvious choice
is commented (`:277-279`) — the acceptance state is re-asked per group via `group_state_as_of`
"rather than read off the row, so a superseded opinion cannot be reported as current."
`group`, `memberships` and `stop_rule_outcome` (`:289-296`) delegate to `grouping.store`.

The argument is honest and the seam is real. The consequence is that the only place in the
system that can answer "which groups does this plan version contain" is the file explicitly
documented as where policy discipline *stops*.

### `approve_plan` — an approval nobody gave

`src/cli.py:641-656`. *"The user approves the frozen plan, and the groups in it with it.
Non-interactively, that means: this command showed nobody the plan, so it carries forward
exactly the acceptance the review already recorded and adds none."* It writes a second
`GroupAcceptance` per group against the **frozen** version, "because that is the version P11
asks about". `production.py:441-467` explains why it exists at all: §8.8 mints a new plan
version for every edit, so the version P11 reads is never the one P9 wrote against; without
this, §6.8 refuses every group with `GroupNotAcceptedInVersion`. And why it is a decision:
"approving the frozen plan IS the user accepting those groups in it. A composition that wrote
the row itself would be recording an approval nobody gave, in a version nobody saw." The
composition does not write it; this command does, and stamps `decided_by='user'`.

### `evidence_for`

`src/cli.py:669-698`. Reads active `file_facts` joined to `values`, building `MatchingFact` at
`reliability=pv.DIRECT` plus `EvidenceItem`. Three constructions are asserted rather than
observed: `location="heading"` for every fact whatever the locator (the slot accepts `body#…`
too, `:209`), `basis="direct-anchor"` for every fact, and `excerpt_span=(0,
len(canonical_value))` (`:688`) — a span into the *canonical value*, not into the document.
`group_ids=tuple(accepted_ids)` reads a list mutated through closure by `accept_and_remember`
(`:766-769`), the one piece of mutable cross-stage state in the file.

---

## 8.4 `production.py`: what is composed, and in what order

Docstring, one sentence: "This module chooses plumbing, lifecycle and ORDER only."

**`run_production_p1_p7`** (`src/production.py:288`) — a wrapper over
`compose_p1_p7(conn, authorities=…)(selection_id)`. `compose_p1_p7` (`:249`) re-runs
`authorities.__post_init__()` — "Revalidate here so bypassing dataclass construction cannot let
a scan start" — binds three storage adapters (`RunWriter`, `ClassificationStore`,
`targeted_ocr_needed_for`) and calls `orchestrator.run_p1_p7`. It ends at a `P1P7Run`:
`scan_run_id`, fact results, a sealed bundle. `P1P7Authorities.__post_init__` (`:97-127`)
refuses a `None` `classify` (`MissingClassificationAuthority`), non-`FactResolver` resolvers,
eight non-callable authorities, four `None` fields, three empty strings, and a non-positive
`context_window`.

**`run_production_p8_p11`** (`:554`) owns the order, and lists five contractual points, each
"a raise somewhere else if it is broken": acceptance before design (`design_tree` raises
`NothingToDesign`); the approval and the policy before the index (`accepted_group_as_of` and
`privacy_state_for` both refuse); the index before the placements; groups before files —
"which is why the whole corpus goes through one call rather than a loop of `place_file`"; and
§8.5's replay last or not at all — "running it first would only mean a failed measurement
stopped a plan the user could otherwise have had."

The executed sequence (`:571-655`): one clock read once; `corpus_roster`; `_group_corpus` (P9,
one subject at a time); `decisions.accept_groups` (**the review screen**); `design_authorities`
then `design_tree` (P10); `approve_plan`; `set_privacy_policy`; `build_destination_index`;
`run_corpus` (P11); `evaluate_bundle` or `None`.

Four guards sit between those steps: accepted ids must be non-empty strings (`:588-591`);
`design_authorities` must return a real `TreeDesignAuthorities` (`:594`); the design must route
against the **same catalogue object** the run was checked against (`:597-601` — "a tree frozen
under an unchecked catalogue names a library nobody validated"); and
`tree_decisions.from_plan_version` must equal `decisions.plan_version_id` (`:607-612`). The
group ids handed to P11 are read off the **design**, not off P9 (`:637-639`): "A group the user
accepted and then did not keep as a branch has no destination in this tree, and asking P11 to
plan it would be planning into a node nobody approved."

**`run_production_corpus`** (`:658`) calls both in order, with `downstream` as a **factory over
the finished `P1P7Run`**, because `scan_run_id` is minted by P3 inside the scan: handing this
module a record with a placeholder "would be exactly the thing every authority record in this
project exists to prevent -- a policy-bearing value chosen by the composition."

**The roster.** `corpus_roster` (`:513`) reads P3's stat-cache verdicts, not
`P1P7Run.fact_results`, "and the difference is a file": a REUSE file, unchanged since the last
scan, is skipped by the extraction loop and has no entry, so "Grouping and placing only the
re-extracted files would leave every unchanged file out of the plan with nothing to say so."
It restates the standing rule at this seam: "Nothing inside a protected container is here,
because P3 never wrote a `files` row for one. That is the marking; the counting is
`TreeDesignResult`'s."

**The shipped library.** `LIBRARY_FILES` (`:144`) names seven JSON files;
`read_packaged_library_file` (`:167`) is "THE filesystem touch, named and in one place" and
refuses any other name. `shipped_catalogue_manifest` (`:183`) joins them and **derives** the
`release_id` as `f"lib-{sha256(bytes in LIBRARY_FILES order)[:16]}"` — "a constant here would
make every edit to the library indistinguishable from the release before it" — and refuses a
record repeated across two files rather than merging, "because a duplicate that quietly won
would make which definition a tree froze depend on the order this module happens to read in."
`load_shipped_catalogue` (`:224`) notes what it fixed: "until it existed, the 22 fragments, 63
definitions and 208 applicability rows under `src/tree_design/library/` were loaded by
nothing, and a production run had no recipes at all."

**The roster of results.** `ProductionRun` (`:486`) carries `p1_p7`, `grouping`, `tree`,
`destinations`, `placement`, `evaluation`. Two carry anti-omission comments: `grouping` is "One
per file in P1's roster, in roster order, INCLUDING the files that produced no group", and
`evaluation=None` "means nobody asked for a measurement, not that one was taken and lost".
`protected_areas` is a property (`:503`) forwarding to `tree.protected_areas`, on the run
rather than in `tree` because "'marked and counted, never opened' needs the count to be
reachable from the thing the user was handed."

---

## 8.5 The report a person reads

`report()` (`src/cli.py:864-981`). *"The run, in the order a person would ask about it. Four
questions, in this order: what was left alone, what folders are being proposed, what happens
to each file, and what this needs from you."*

**1. Protected containers, first** (`:880-887`), and never folded into a total:

> "'Marked and counted, never opened' is only true if the count is somewhere the person reads,
> and a line at the bottom of a long report is not that. The grouping below never reaches this
> block -- count, name, path and sentence are what the rest of the report is shortened around,
> not with."

A count line, a label-and-internal-label line, a path line, and — only if there are any — *"Nothing
inside these was read, indexed, classified or moved, and none of them is a place anything can
be filed."* `tests/test_cli.py:263` pins all four against the `bb898ce` rewrite.

**2. Proposed folders** (`:889-903`) — `Proposed folders: {n}. {places} of them {is|are}
somewhere a file can go.`, then a recursive `draw` over `parent_node_id`, two spaces per level,
with `"   [marked, not a destination]"` on any node whose `accepts_placement` is false.
`places` is `len(result.destinations)` — the index, which holds only placement-accepting nodes.

**3. Files, grouped by KIND of outcome** (`:905-967`) — the block `bb898ce` rewrote:

> "One line per KIND of outcome, not one per file. Four files that stopped for the same reason
> are four names and one reason, because the reason was one fact the first time it was printed
> and stayed one fact the other three."

The key is `(outcome, destination_label, reason, review_notes)` (`:935`), where `reason` is
`""` for a placement — "A placement's folder is its whole answer; every other outcome owes the
person the sentence saying why it stopped" (`:930-931`). Review sets are deduplicated **by
identity, not by value** (`:922-923`): "two review sets that happen to read alike are still two
sets, and folding them would lose one." Ordering (`:939-942`) is protected first — "exactly as
`tree_design.health` ranks its warnings" — then `OUTCOME_WORDS` declaration order, then label,
then reason.

`OUTCOME_WORDS` (`:793-801`), in declaration order, which is "what is settled first, what needs
the person last":

| P11 outcome | printed as |
|---|---|
| `place` | Ready to file |
| `leave_in_place` | Staying exactly where they are |
| `mark_state` | Marked and left alone |
| `mark_review_later` | Set aside for you to look at later |
| `return_to_placement` | Sent back round for another look |
| `ask_user` | Waiting for you to choose where these go |
| `abstain` | Waiting for you to say what these are |

with the anti-omission rule stated (`:789-791`): "An outcome missing from this table prints its
own name rather than nothing: a gap in this deployment's vocabulary must never become a file
that vanished."

`NAMES_LISTED_PER_GROUP = 10` (`:809`) caps names per group, following
`src/tree_design/health.py` — "a list longer than the thing it describes is not a summary of
anything" — including its one exemption: a protected group is listed in full (`:953`). The
overflow line (`:959-962`): *"...and {rest} more, counted here rather than listed one by one so
that the list stays shorter than the folder it describes; none of them is a protected area,
which is never summarised away"*. The shared reason prints once as `Same reason for each: …`
(`:964`).

Names come from `file_names` (`:812-834`), reading `files.current_path` relative to the scanned
root, falling back to the absolute path outside it. The docstring is blunt about what it
replaced: "a report printing `74ce335f-110b-42c0-8a50-ecdc8f8734b7` was never showing the only
thing it had. A person cannot tell which of their own files that is, which makes every line
built on it unusable." `names` is required, not optional, because "a default would let the
id-only report back in by nothing more than a forgotten argument."

**4. Review sets** (`:969-978`) — folded in beside the files they cover; a set covering no
decided file gets its own line: "§7.5's sets are printed where the files they cover are
printed, so the same four files are never counted twice in two vocabularies… shortening the
report may not drop one."

**5. The footnote** (`:980-981`) — `Nothing was moved.` then `Plan version: {id}  (the name
this proposal is saved under)`.

### The defects `bb898ce` fixed

**There is no `bb858ce` in this repository.** The report rewrite is `bb898ce` alone ("fix(cli):
a report a person can act on", 2026-08-29), and it names **five** defects:

> "The output named every file by UUID, printed one shared reason four times verbatim, headed
> the folder list with the internal plan version, counted the same four files twice in two
> vocabularies, and wrote a bare `-` where a destination would go. All five made it unreadable
> rather than wrong."

`git show bb898ce^:src/cli.py` shows each in the prior `report()`:

1. **UUIDs.** The old loop printed `f"  {decision.outcome:<10} {where:<24}
   {decision.subject.file_id}"` — the raw UUID and nothing else. Fixed by `file_names`; pinned
   by `tests/test_cli.py:185` and `:338`.
2. **One reason four times.** The old loop printed `f"    {decision.explanation}"` per
   decision. Fixed by the outcome/reason grouping; pinned by `tests/test_cli.py:201` — "The
   wording is right and stays verbatim; saying it four times is not."
3. **The plan version as a headline.** The old header was `f"\nPlan {tree.plan_version_id}:
   {len(tree.nodes)} folders, …"`, so the first thing a person read about their own folders was
   `Plan version_2`. Moved to the footnote; pinned by `tests/test_cli.py:281`.
4. **The review set counted twice.** The old code printed `f"\nFor review: {item.label}
   ({item.file_count} files)"` unconditionally, so `Files: 4 decided, 0 placed` and `For
   review: Not yet placed (4 files)` were one fact in two vocabularies. Pinned by
   `tests/test_cli.py:300`, with negative twin `:312`.
5. **A bare `-`.** The old `where` was `"-"` when `destination` was `None`. Now `where` is
   `None` and the heading omits the `into …` clause. Pinned by `tests/test_cli.py:324` — "A
   bare `-` reads as a missing value. 'Nowhere yet' is a decision."

Also changed: the header said "`{n}` placed" and now says "`{n}` ready to file", matching
`OUTCOME_WORDS[pv.PLACE]`. The commit's guarantee — "Nothing is dropped to make it shorter" —
is enforced by `tests/test_cli.py:212`, `:233` and `:312`. Seventeen tests cover `cli.py`.

---

## 8.6 The run, end to end

*Provenance.* Everything below was observed at **2026-08-29 03:51:34 UTC** against
committed HEAD `2ef3874`, with a clean `src/` and `tests/` working tree. Another agent in
this session began editing `src/grouping/store.py` (04:04:43 UTC) and
`src/grouping/acceptance.py` (04:05:28 UTC) afterwards, so the tree as it stands is
mid-edit and does not currently complete a run. Re-run this against `2ef3874` to reproduce.

Corpus built for this document, outside the repository, under
`…/da9ffc7f-c259-4c21-8014-3a25650964d6/scratchpad/corpus`:

```
hw1.txt          "PHYS 1401 Homework 1"      — space separator
hw2.md           "# PHYS 1401 Homework 2"    — space separator, markdown heading
lab-report.txt   "PHYS-1401 Lab Report"      — hyphen separator
syllabus.txt     "PHYS1401 Syllabus"         — no separator
Notes.app/       index.sqlite, data.blob     — a protected container
```

```
$ cd "/Users/jy/GRAPH AGENT" && python3 src/cli.py .../scratchpad/corpus \
      --situation academic.coursework --label Coursework \
      --database .../scratchpad/mech08.sqlite
```

```
Plan database: /private/tmp/claude-501/-Users-jy-GRAPH-AGENT/da9ffc7f-c259-4c21-8014-3a25650964d6/scratchpad/mech08.sqlite

Protected containers: 1 marked, none opened
  Notes.app  (untouched_protected)
    /private/tmp/claude-501/-Users-jy-GRAPH-AGENT/da9ffc7f-c259-4c21-8014-3a25650964d6/scratchpad/corpus/Notes.app
  Nothing inside these was read, indexed, classified or moved, and none of them is a place anything can be filed.

Proposed folders: 2. 1 of them is somewhere a file can go.
  Coursework
  Notes.app   [marked, not a destination]

Files: 4 decided, 0 ready to file

  Waiting for you to say what these are -- 4 files
    hw1.txt
    hw2.md
    lab-report.txt
    syllabus.txt
    Same reason for each: This file has not been classified -- nothing has yet
    said what kind of material it is -- so it was not shown to a model and
    nothing moved. It is waiting for you to say what it is, not marked
    sensitive and not judged on thin evidence.
    Held for review as "Not yet placed": no destination in this tree matched
    them well enough to decide without asking you.

Nothing was moved.
Plan version: version_2  (the name this proposal is saved under)
```

Exit 0. The corpus is byte-identical afterwards.

### What worked

* **The protected container.** Marked, counted, named, pathed and explained, first, in four
  lines. `exclusion_verdicts` holds one row — `rule='protected container'`,
  `rule_subject='protected_container'`, `applies_to='scanned source'`,
  `label='untouched_protected'` — and `files` holds **no row** for `index.sqlite` or
  `data.blob`. The marking is real, not cosmetic.
* **The separator fix.** All four spellings canonicalised to one value:

  ```
  f22ab39c  subject='PHYS1401'  direct   (hw1.txt,        "PHYS 1401")
  73887964  subject='PHYS1401'  direct   (hw2.md,         "PHYS 1401")
  63eaf190  subject='PHYS1401'  direct   (lab-report.txt, "PHYS-1401")
  a99b261d  subject='PHYS1401'  direct   (syllabus.txt,   "PHYS1401")
  ```
* **One course, one group.** P9 formed a single group of four
  (`group:subject:0a1fcb6e…:strongly-identified-file`, `anchor_count=4`), not four of one.
  `65` §4.2's defect and the `scan_state` seam beneath it are genuinely closed.
* **The report is readable.** Names, one reason, no headline plan version, no double count.

### What the database recorded

**`files`** — four rows. Nothing from inside `Notes.app`.
**`classifications`** — **0 rows.** The detector shipped, ran, and declined on all four.

**`groups`** — two rows:

```
group:subject:0a1fcb6e…:strongly-identified-file
  display_label='PHYS1401'  group_category='academic'  label_source='engine'
  anchor_count=4  created_by='rules'  superseded_by='plan_0:Coursework'

plan_0:Coursework
  display_label='Coursework'  group_category='academic'  label_source='user-edited'
  anchor_count=16  created_by='user'  supersedes='group:subject:0a1fcb6e…'
```

The supersession chain is intact — what P9 proposed and what the "user" answered are both on
disk, exactly as the docstring promises. Note `anchor_count=16` for four files, and note that
the engine group already carried both a label and a category.

**`memberships`** — eight rows: four against the engine group, four carried onto
`plan_0:Coursework` with `supersede_reason='carried onto the group the user confirmed'`.

**`group_acceptance`** — two rows, both `decided_by='user'`, `review_state='pending-review'`:
`acc:plan_0:Coursework` (`plan_0`) and `acc:version_2:plan_0:Coursework` (`version_2`).

**`plan_versions`** — `version_0` (draft) → `version_2` (frozen), same `selection_id`. `plan_0`
never appears here; it exists only on group and acceptance rows.

**`tree_nodes`** — three rows:

```
node_1  version_0  proposed   'Coursework'  accepts=1  personal_non_sensitive               refinement='refined'
node_3  version_2  proposed   'Coursework'  accepts=1  personal_non_sensitive               refinement='refined'
node_4  version_2  protected  'Notes.app'   accepts=0  highly_sensitive_credential_bearing  refinement=None
```

The protected node exists in the frozen tree, is not a destination, and carries the strongest
handling class — the standing rule as a row. Its `existing_path` is `None`; the path the report
printed came from `TreeDesignResult.protected_areas`.

**`placement_index_entries`** — one entry for `node_3`, with
`accepted_group_ids=['plan_0:Coursework']`, `representative_files=[all four]`, and
`expected_values=[]`, `template_fields=[]`, `anchor_excerpt_keys=[]`,
`known_document_types=[]`. `placement_index_terms` holds **2** terms.

**`placement_decisions`** — four rows, all `outcome='abstain'`, `node_id=NULL`,
`review_policy='blocked_pending_user'`, against `version_2`. One payload, elided:

```json
{ "abstention_reason": "privacy_blocked",
  "alternatives": [{"node_id": "node_3", "rank": 1, "support_score": 0.2857142857142857}],
  "confidence_class": "abstain: no supported destination",
  "explanation": "This file has not been classified -- nothing has yet said what kind of material it is -- so it was not shown to a model and nothing moved. It is waiting for you to say what it is, not marked sensitive and not judged on thin evidence.",
  "privacy": {"handling_class": "unreadable_unclassified", "model_eligibility": "local_only", "protected": false},
  "two_condition": {"support_score": 0.2857142857142857, "support_threshold": 0.5,
                    "meets_threshold": false, "margin_threshold": 0.2,
                    "margin_over_next": null, "meets_margin": "true_vacuous",
                    "requires_review": true, "verdict": "weak"} }
```

`handling_class='unreadable_unclassified'`, `protected=false` — the honest unclassified path
`6be2ada` restored, working exactly as designed.

**`placement_group_plans`** — one row for `plan_0:Coursework`, naming all four member
decisions, `excluded_outliers=[]`.
**`residual_sets`** — one row, `Not yet placed`, `file_count=4`, `protected=false`.
**`privacy_policies`** — one row, `operation_mode='offline'`, all permission maps empty.
**`budget_ceilings`** — seven rows, all 8.

### What the person got

A folder called `Coursework` that nothing goes into, and four files told to wait. The engine
knew the course code, formed the right group, named it `PHYS1401`, and built a destination —
and then no file could be placed, because nothing classified any of the four. `68` §2 records
the same outcome across four corpora: "Four people, four disks, one outcome. Nothing was
misfiled and nothing was lost — the product is honest at every step — but nobody got an
organisation, and nobody got a single file placed."

---

## 8.7 The two refusal paths that work

An empty `--label`:

```
No plan was made for .../corpus, and this is why:
  UpstreamUnavailable: group 'plan_0:' carries no label. P9 sets `display_label` only when `coherence_verdict` is 'coherent', so an unlabelled accepted group is a real state and a branch cannot be named from it.
```

Exit 1, via `REFUSALS` (`src/cli.py:235-238`, caught at `:1065`). An unknown `--situation`
(§8.1) exits 2 via `NotConfigured`. Both are exactly the experience the file aims for. The
problem is what falls outside those two lists.

---

## What looks wrong here

Flagged, not resolved. Ordered by how much a real person would be hurt.

**1. The stated reason for the two required flags is no longer true, and the run disproves
it.** `src/cli.py:16-20` and `:436-443` argue that `--situation` and `--label` are required
because P9 answers neither. `src/grouping/naming.py:128-155` (`engine_proposal`, called
unconditionally at `src/grouping/pipeline.py:499`) answers both, and this run's database shows
`display_label='PHYS1401'`, `group_category='academic'`, `label_source='engine'` on the engine
group. The citation is stale too: `group_category=None` is `pipeline.py:300`, not `:230`. The
flags may still be right; the argument for them is not, and a reader of the docstring is
misled about what the engine can already do.

**2. Re-running against an existing plan database crashes with a traceback.** Reproduced
twice. `MalformedGroupRecord` is not in `REFUSALS`, so:

```
grouping.records.MalformedGroupRecord: membership group:subject:0a1fcb6e…:f22ab39c… is already recorded with different content; a revision supersedes rather than replaces
```

comes out as a bare Python traceback. Since `--database` **defaults to a fixed filename in the
cwd** (`:1051`), the natural second run of the product — same folder, adjusted label — is a
crash. The store is refusing correctly; nothing catches it, and the exit code is
indistinguishable from a named refusal.

*In flight.* An uncommitted fix appeared in the working tree at 04:04 UTC — another agent
this session is adding `_same_derivation` to `src/grouping/store.py`, so that a record
re-derived from unchanged evidence and differing only in `created_at`, `superseded_by` and
`supersede_reason` is accepted rather than refused. Its own docstring names the same
symptom: "The consequence was that the shipped command crashed on its own SECOND
invocation against the default database, with a traceback rather than a named refusal."
That addresses the *cause* here. It does not address finding 3, and it does not add either
exception type to `REFUSALS` — so the general defect (the chain raises more types than
`REFUSALS` enumerates, and the surplus reach the user as tracebacks) stands.

**3. A `--label` containing a path separator crashes rather than refusing.** `--label
"../../etc"`:

```
tree_design.records.MalformedTreeRecord: Node.display_label holds a path separator. P10 publishes root_anchor plus the ancestor label chain; P12 composes the path and applies §8.3's case-sensitivity, Unicode and length rules (resolution B3).
```

The guard is right; `MalformedTreeRecord` is simply not in `REFUSALS`. An **empty** label, by
contrast, produces a clean printed refusal — so two adjacent bad inputs to the same flag behave
completely differently. Same root cause as (2): `REFUSALS` enumerates six types and the chain
raises more than six.

**4. `CEILING_VALUE = 8` is applied to seven ceilings that are not the same kind of
quantity.** `:532-533` writes 8 to every key in `CEILINGS`, including
`model.max_dossier_tokens_per_call` (**8 tokens**) and `model.max_cost_per_scan` (8 of an
unstated unit), contradicting `max_dossier_tokens=4000` set twelve lines earlier and
`max_retrieved_neighbors=50` on the adjacent line. Nothing reads the model ceilings today
because there is no model — which is what makes it dangerous: the first deployment that turns a
model on inherits an eight-token dossier budget under a comment reading "Eight is small on
purpose."

**5. The support threshold is justified against arithmetic the run contradicts.** `:110-113`
says 0.50 was chosen "because that is the band a direct fact alone (3/7) falls below and a
direct fact plus an accepted group (5/7) clears". Every measured `support_score` was
`0.2857…` = **2/7**, for a file with a direct fact *and* an accepted group. Neither claimed
number appeared. The threshold may be correct; the stated derivation is not what the scorer
does.

**6. The merge does not deduplicate by group identity, and writes a false number.** `:456-459`
concatenates `anchor_facts` and sums `anchor_count` across **`GroupingResult`s**, not distinct
groups. Four files sharing one group produced `anchor_count=16`, `reviewed_proposals=4` for one
proposal, and four duplicate copies each in `anchor_facts` and `coherence_citations`. This is
separate from `68` F3's one-folder finding and is not covered by F3's "wait for P13"
reasoning — it is a counting bug that writes strength evidence a later reviewer would trust.

**7. Two different reasons are printed to the same person about the same four files.** "Same
reason for each: This file has not been classified…" and, two lines later, "Held for review as
'Not yet placed': no destination in this tree matched them well enough…". Different diagnoses.
The first is true (0 classifications); the second is a hard-coded string (`:712-713`) that
cannot know why anything was unplaced, since `residual_partition` is handed only a list of ids.
The payload adds a third framing: `abstention_reason: "privacy_blocked"` beside an explanation
ending "not marked sensitive".

**8. `residual_partition` asserts `protected: False` for every set it will ever make.**
`:707-710`. `_protected` (`:849-861`) reads `item.protected` as one of three signals deciding
whether a group is listed in full rather than summarised, and justifies the OR by saying "the
cost of the reverse is the silent omission the standing rule exists to forbid." One of those
three signals is permanently `False` by construction from this file. The property holds today
only because the other two do the work. `sensitivity_status: "none"` is asserted the same way.

**9. `handling_class_for_member=lambda member: ORDINARY_CLASS` declares every file
non-sensitive.** `:593`. The surrounding comments argue carefully that the protected class is
deliberately strongest so a *container* cannot inherit a weaker floor — but every *file* is
asserted `personal_non_sensitive` regardless of what P7 said. `sensitive_group_ids=frozenset()`
(`:581`) makes the same assertion at group level, with a comment; the member-level one has
none.

**10. `refinement_for` writes a sentence that is false about the tree it describes.**
`:514-516` tells the user "The levels beneath this branch were populated from facts that were
already settled in your files" for every top-level node. In this run — and, per `68` F3, in
every run — there *are* no levels beneath the branch. The claim was stored on `node_3`.

**11. `approve_plan` stamps `decided_by='user'` on a plan version nobody saw.** `:641-656`,
writing `acc:version_2:plan_0:Coursework`. The docstring is candid that "this command showed
nobody the plan"; `production.py:462-465` names the principle it brushes against — "recording
an approval nobody gave, in a version nobody saw." The composition does not do it; the
composition root does. Whether that distinction is meaningful is exactly what a critic should
press.

**12. `entity_frequency` makes §6.5's generic-entity suppression unreachable.** `:697`:
`{fact.value: 1 for fact in facts}` against `generic_entity_frequency=200`. Every value is 1,
so nothing can ever be suppressed as a hub. The comment presents 200 as a chosen threshold; it
is a threshold on a constant.

**13. `evidence_for` hard-codes provenance it does not have.** `:686-689`:
`location="heading"` for every fact whatever the locator; `basis="direct-anchor"` for every
fact; and `excerpt_span=(0, len(canonical_value))` — a span into the canonical value rather
than the document, which is not what a span means anywhere else. The `/Title` slot was excluded
(`:203-205`) precisely because "its observation carries no text span"; the slot that *was*
included reaches P11 with a span naming the value, not the file.

**14. Three citations in `cli.py` do not point where they say.** (a) `:129` cites "`00`:78's
own recommended tree, `Academics/Columbia/2026-Spring/PHYS1401/Homework`"; `00`:78 is
`        Syllabus/`, the leaf of a different example, and that tree is at `00`:98/105/106/111.
(b) `:366` attributes "sensitive personal material is not the same thing as `Numbers.app`" to
`` `00` ``; the string is not in `00` — it is `planning/59-FINAL-UX-EVALUATION.md:251`.
(c) `:17` cites `src/grouping/pipeline.py:230`; the line is `:300`. In a file whose stated
contract is "If a number appears here that `00` states, the comment says where", three broken
pointers matter more than they would elsewhere.

**15. The brief's own commit reference is wrong.** `bb858ce` does not exist in this repository.
The report rewrite is `bb898ce` alone, and it names **five** defects, not four — the fifth being
"wrote a bare `-` where a destination would go".

**16. Two deployment decisions are justified by a review surface that does not exist.**
`choose_option` (`:494-497`) argues that taking the first passing option is acceptable because
"The options carry their counts, their warnings and their validation report"; and
`materially_improves_retrieval` (`:134-137`) "leaves the judgement to the user, who sees the
option's counts and warnings before taking it." Nothing in `report()` prints counts, warnings,
or a validation report. The user sees neither.

**17. `ask_or_abstain` always abstains, so one of the seven `OUTCOME_WORDS` is unreachable from
its natural cause.** `:724`. A two-homes file should produce "Waiting for you to choose where
these go"; it is redirected to "Waiting for you to say what these are", which asks a different
question about a file the system already understands.

**18. The destination profile is nearly empty, which may be why nothing scores.** The one index
entry carries `expected_values=[]`, `template_fields=[]`, `anchor_excerpt_keys=[]`,
`known_document_types=[]`, and `placement_index_terms` holds 2 terms. `00`:105 calls a
destination node "an evidence-backed representation of what belongs there… a small,
user-approved corpus of evidence". A support score of 2/7 against a 0.50 threshold is not
obviously a threshold problem — the threshold may be taking the blame for an empty profile.
Worth attention because finding 5 and this one name different culprits for the same zero.

**19. Two deployment decisions in the file carry no comment at all.**
`satisfies_purpose_profile=lambda ref, groups: True` (`:587`) and `max_return_cycles=1`
(`:725`). In a file whose opening contract is that every constant is a documented deployment
decision and "if `00` states none, the comment says that instead and names who owns the
question", two silent answers are two answers nobody owns. `GROUPING_LIMITS`' seven numbers
(`:141-144`) are covered collectively by one sentence and individually by none.

**20. No run can ever measure itself.** `evaluation=None` (`:759-763`) is well-argued. The
consequence is that the shipped command cannot tell whether it is getting better or worse
between versions — a real gap for a product whose central claim is careful judgement. `68` had
to hand-build four corpora to find out.
