# Audit — every number the product chooses, and whether the model's input is bounded

Read-only. Nothing under `src/` or `tests/` was changed. Every claim below is
either a `file.py:line` citation or a run I made; the runs are named where they
matter, and the corpora that produced them are throwaway `.txt` files in the
scratchpad, not in the repo.

**Headline.** The discipline holds: `src/cli.py` really is the only file in
`src/` that picks a number, and the parts really do refuse rather than default.
So the critiqued project's failure (a) — "you cannot tell a measured number from
a borrowed one" — does not reproduce here in the form it was written. What
reproduces is its *shadow*: almost every number is honestly labelled as this
deployment's own, and almost none of them has ever been exercised. Twelve of the
thirty are unreachable on a shipped run, and three of the reachable ones are
coupled to each other in ways no comment mentions and no test covers.

Failure (b) — "the evidence packet has no size ceiling" — **does** reproduce, and
in a sharper form than the critique describes. See §3.

---

## 1. The inventory

Thirty numbers, plus four non-numeric deployment choices that behave like
numbers. Tags: `DESIGN_STATES_IT` (a number `00` gives), `DERIVED` (computed from
something else in the code), `CHOSEN_FOR_A_FIRST_RUN` (an honest arbitrary
bound), `UNEXAMINED` (nothing in the code, the comments or a run establishes that
this value is the right one, or even that a different one would behave
differently).

| # | Number | Value | Where | Tag | Note |
|---|--------|-------|-------|-----|------|
| 1 | `COMPONENT_VERSION` | `"cli-0.1.0"` | `cli.py:106` | `CHOSEN_FOR_A_FIRST_RUN` | §8.5 requires a version tuple and states no format. Fine. |
| 2 | `support_scale_max` | `1.0` | `cli.py:116` | `DERIVED` — but see §4 | Comment: "the scorer's weights already sum to it". They do not; they sum to 7 and are normalised. The *reachable* max is 0.714. |
| 3 | `minimum_support_threshold` | `0.50` | `cli.py:117` | `DERIVED` | Genuinely well argued, and the arithmetic checks out. §4. |
| 4 | `margin_threshold` | `0.20` | `cli.py:117` | `DERIVED` (undeclared) | The comment calls it "and 0.20 as the margin" with no argument. It happens to be correctly derived. §4. |
| 5 | `CEILING_VALUE` | `8` | `cli.py:123` | `CHOSEN_FOR_A_FIRST_RUN` | Honestly labelled ("Eight is small on purpose"). One of the seven keys it sets changes an outcome, and it makes the report worse. §2. |
| 6 | `max_folder_proposals` | `4` | `cli.py:131` | `DESIGN_STATES_IT`-adjacent | Argued from `00`:256. Cannot bind: the tree is always one branch. §2. |
| 7 | `max_depth` | `5` | `cli.py:131` | `DESIGN_STATES_IT` | Argued from `00`:78's own five-level example. Best-evidenced number in the file. Cannot bind. §2. |
| 8 | `TREE_LIMITS.max_dossier_tokens` | `4000` | `cli.py:131` | `UNEXAMINED` | Read by **nothing** in P10. Dead field. §2, §3. |
| 9 | `excessive_depth_warning` | `4` | `cli.py:132` | `UNEXAMINED` | No comment of its own. Cannot bind (depth is always 1). |
| 10 | `tiny_folder_max_files` | `1` | `cli.py:132` | `UNEXAMINED` | No comment. Cannot bind. |
| 11 | `tiny_folder_count_warning` | `2` | `cli.py:133` | `UNEXAMINED` | No comment. Cannot bind. |
| 12 | `materially_improves_retrieval` | `True` always | `cli.py:138` | `CHOSEN_FOR_A_FIRST_RUN` | Excellent comment; the reasoning for `True` over `False` is stated and correct. |
| 13 | `max_retrieved_neighbors` (P9) | `50` | `cli.py:142` | `CHOSEN_FOR_A_FIRST_RUN` | Never binds: `max_graph_nodes` (10) cuts first and harder. |
| 14 | `max_graph_nodes` | `10` | `cli.py:142` | `CHOSEN_FOR_A_FIRST_RUN` | Live. Also half of the coupling in §5. |
| 15 | `max_candidate_members` | `10` | `cli.py:142` | `UNEXAMINED` | Read by **nothing**. §2, §3. |
| 16 | `GROUPING_LIMITS.max_dossier_tokens` | `4000` | `cli.py:143` | `UNEXAMINED` | Recorded on the dossier as `token_ceiling`; enforced by nobody. §3. |
| 17 | `generic_hub_frequency` | `9` | `cli.py:143` | `UNEXAMINED` — actively harmful | `= max_graph_nodes − 1`. Makes hub suppression a step function on corpus size. §5. |
| 18 | `minimum_independent_anchors` | `1` | `cli.py:144` | `CHOSEN_FOR_A_FIRST_RUN` | 1 is the weakest legal value; effectively "off". Honest for a first run. |
| 19 | `max_excerpt_characters` | `240` | `cli.py:144` | `CHOSEN_FOR_A_FIRST_RUN` | Bounds P9's own record only, not what would reach a model. §3. |
| 20 | `_STRUCTURED` digit floor | `{3,}` | `cli.py:188` | `DERIVED` | Argued at length from `65` §2.1 and a real failed run. The single best-evidenced number in the file. |
| 21 | `context_window` | `240` | `cli.py:415` | `CHOSEN_FOR_A_FIRST_RUN` | Bounds `context_before`/`context_after` only — **not** `raw_value`. §3. |
| 22 | `entity_frequency` per value | `1` always | `cli.py:713` | `UNEXAMINED` | A constant, not a count. Makes #23 dead. §6. |
| 23 | `generic_entity_frequency` | `200` | `cli.py:714` | `UNEXAMINED` | Compared against a constant `1`. Can never fire. §6. |
| 24 | `max_return_cycles` | `1` | `cli.py:741` | `CHOSEN_FOR_A_FIRST_RUN` | Reasonable; unreachable (no model path). |
| 25 | `privacy_rank` | `0` for all | `cli.py:602` | `CHOSEN_FOR_A_FIRST_RUN` | Comment is right: equal-rank is the only ordering that cannot go wrong. |
| 26 | `representative_examples` slice | `[:3]` | `cli.py:724` | `UNEXAMINED` | Undocumented literal inside `residual_partition`. |
| 27 | `NAMES_LISTED_PER_GROUP` | `10` | `cli.py:825` | `CHOSEN_FOR_A_FIRST_RUN` | Well argued — and dead, because #5 caps the same lists at 8 first. §7. |
| 28 | report wrap width | `78` | `cli.py:854` | `CHOSEN_FOR_A_FIRST_RUN` | Fine. |
| 29 | `RESIDUAL_LIBRARY` | `{}` | `cli.py:222` | `CHOSEN_FOR_A_FIRST_RUN` | "enables NONE rather than inventing slot values" — a good, argued zero. |
| 30 | `PLAN_VERSION` | `"plan_0"` | `cli.py:163` | `CHOSEN_FOR_A_FIRST_RUN` | Non-numeric but a deployment identity. |

**Count: 30. `UNEXAMINED`: 11** (#8, 9, 10, 11, 15, 16, 17, 22, 23, 26, and #2's
justification, which is stated and wrong even though the value is harmless).

**Be fair about what is good here.** #20, #7, #12, #25 and #29 are better
justified than anything in the critiqued project: each names the design line or
the failed run it came from, and #20 names the date and the incident. `00` states
no number for any of them, and the file *says so* every time rather than
implying measurement. There is no number in `src/cli.py` presented as measured
that was not measured — the failure class the critique describes is genuinely
absent. The problem is the opposite one: honest labels on numbers nobody has run
a corpus against.

---

## 2. Which numbers actually change behaviour on a shipped run

`_bootstrap` (`cli.py:532-533`) writes `CEILING_VALUE` to `CEILINGS.values()` —
and `CEILINGS` there is **P11's** seven keys (`placement/config.py:26-34`), not
P1's seventeen (`database_agent/budget.py:14-51`).

Dumped from a real run's database (4-file corpus, `p4.sqlite`):

```
model.max_llm_calls_per_thousand_files    8      grouping.max_retrieved_neighbors        -- UNSET --
model.max_cost_per_scan                   8      grouping.max_local_graph_neighborhood   -- UNSET --
model.max_dossier_tokens_per_call         8      grouping.max_candidate_cluster_size     -- UNSET --
placement.max_retrieved_neighbors         8      tree.max_folder_proposals               -- UNSET --
placement.max_local_graph_neighborhood    8      tree.max_depth                          -- UNSET --
placement.max_candidate_cluster_size      8      evidence.context_window                 -- UNSET --
residual.max_files_per_review_batch       8      ocr.* (3), image.* (1)                  -- UNSET --
```

**7 of 17 set; 10 unset.** The ten are not a bug in themselves — P9 and P10 are
handed `GroupingLimits` / `TreeLimits` as literals (`cli.py:126`, `cli.py:141`)
rather than through `grouping_limits(conn)` / `tree_limits(conn)`, so they never
read P1. But it means P1's published budget object, which `budget.py:6-8` calls
the place values are "held and published", disagrees with what the run actually
obeys. Two examples:

* `model.max_dossier_tokens_per_call = 8` in the database, while P9 and P10 are
  each handed `4000` for the same quantity (`cli.py:131`, `cli.py:143`). P7's
  gate reads the **stored** value and never the caller's echo
  (`privacy/gate.py:401-413`, `privacy/denial.py:214-227`), so the day a model is
  wired, every dossier over 8 tokens is denied while P9 believes its budget is
  4000.
* `evidence.context_window` unset while the extractors run at 240
  (`cli.py:415`). `budget.py:44-49` states in terms that this key must be inside
  the extraction fingerprint or "two runs at different context widths look
  identical to §3.4's cache key and §8.5's replay, which is a silent wrong
  answer". The key is unset, so that is the current state.

Now: of the seven that *are* set, which changes an outcome?

| Key | Read by | Binds on a shipped run? |
|---|---|---|
| `placement.max_retrieved_neighbors` | `placement/retrieval.py:169`, `index.py:300` | **No.** The tree is 2 nodes (root + one branch); 2 < 8. |
| `placement.max_local_graph_neighborhood` | `placement/graph.py:138` | **No.** `cli.py:712` supplies `related_files=()`, so the graph is always empty. |
| `placement.max_candidate_cluster_size` | `placement/graph.py:127` | **No.** Same reason. |
| `model.max_llm_calls_per_thousand_files` | `placement/pipeline.py:758` | **No.** `gate=None, model_client=None` (`cli.py:742`); the model path is never entered. |
| `model.max_cost_per_scan` | `placement/pipeline.py:759` | **No.** Same. |
| `model.max_dossier_tokens_per_call` | `placement/pipeline.py:789`, `privacy/gate.py:408` | **No.** Same. |
| `residual.max_files_per_review_batch` | `placement/residual.py:171-173` | **YES — and it is the one that hurts.** |

**One of seventeen ceilings changes a shipped outcome, and it makes the report
worse.** `residual.py:171-173` splits rather than truncates (correctly — §8.6
reduces work and never drops files), so an 8-file ceiling turns one review set
into `ceil(n/8)` sets. Measured:

| corpus | residual sets | report lines | `"Same reason for each"` blocks |
|---|---|---|---|
| 4 files | 1 | ~30 | 1 |
| 40 files | 5 | ~120 | 5 |
| 800 files | 100 | **1,611** | **100** |

At 800 files the report prints the identical four-line explanation one hundred
times and runs to 1,611 lines for 800 files. Extrapolating linearly, 4,000 files
gives 500 sets and roughly 8,000 lines. `report`'s own docstring
(`cli.py:868-874`) and the summarisation note at `cli.py:942-947` say the list
must "stay shorter than the folder it describes". At 800 files it is twice as
long. The mechanism: the review-set label is part of the report's dedup key
(`cli.py:934`), so splitting the set splits the dedup group with it.

Two ceiling *keys* are read by nobody at all:

* `grouping.max_candidate_cluster_size` → `GroupingLimits.max_candidate_members`.
  Declared at `grouping/config.py:32,41`; the only other occurrences in `src/`
  are that declaration. **No code reads it.** The member count of a P9 dossier is
  bounded by `max_graph_nodes` (`grouping/graph.py:205`,
  `grouping/pipeline.py:174`), not by this.
* `TreeLimits.max_dossier_tokens`. Declared at `tree_design/config.py:48,58`;
  read nowhere in `src/tree_design/`. The `4000` at `cli.py:131` is inert.

---

## 3. Is the model's evidence packet bounded?

**Better than the critiqued project on member count and per-excerpt length;
worse on total size, and there is one clean gap.**

What is genuinely bounded, and where:

1. **Member count.** `grouping/pipeline.py:167,174` caps the eligible set at
   `max_graph_nodes − 1 = 9` before any text is read, and
   `grouping/graph.py:203-207` caps again while walking. A dossier holds at most
   10 files. **A group of 200 files never produces a 200-file dossier** — it
   produces a 10-file one, and the other 190 are named in
   `Omissions.neighbourhood_capped` (`dossier.py:265`), not dropped silently.
   This is the discipline the module docstring promises (`dossier.py:16-21`) and
   it is real.
2. **Per-excerpt length in P9's own record.** `dossier.py:221` truncates
   `observation.raw_value[:limits.max_excerpt_characters]` = 240 chars. Note the
   care at `dossier.py:117-120`: the *span* is the observation's own, not derived
   from the truncated text. That is exactly right.
3. **Refusal rather than an empty packet.** `dossier.py:243-253` returns
   `DossierRefused` when withholding leaves no anchor, so an empty question never
   reaches a paid call.

What is **not** bounded:

**(a) Total dossier size is bounded by nothing that runs.** `dossier.py:22-25`
says plainly that P9 runs no token ladder and that the ceiling is P8's
`run_call`'s job. `BudgetSummary.token_ceiling` (`dossier.py:270`) *records* 4000
and enforces nothing. On the enforcement side,
`privacy/gate.py:259-264` only measures if `measure_tokens` was supplied — and it
is an **optional constructor argument defaulting to `None`**
(`privacy/gate.py:101`, `gate.py:85-88`). `src/cli.py` constructs no `Gate` at
all (`gate=None`, `cli.py:742`; `p8_authorities=None`, `cli.py:773`). So on this
deployment there is no size ceiling anywhere in the chain — not a weak one, none.
Confirmed: `group_dossiers` is empty (0 rows) after every run I made.

**(b) `max_excerpt_characters` does not bound what would reach a model.** This is
the gap. P9's 240-char truncation applies to `Excerpt.text`, which never travels.
What travels is `p8_seam.py:216-227`, which builds a `ReleaseExcerpt` carrying the
observation's own span — and `span=None` when the observation has none, meaning
"the whole citation" (`privacy/items.py:110-120`). P7 then materialises the whole
observation. In the 4-file run, **16 of 24 observations have `text_span: null`**
(path, mime_type, extension, normalized_filename), so the whole-citation path is
the ordinary case, not an edge case. And `privacy/items.py:246-259` returns
`False` for `span is None`, so the whole-document backstop does not catch it
either.

**(c) A single enormous excerpt is possible in principle.** `raw_value` has no
cap anywhere in `src/extractors/` — `context_window` bounds only
`context_before`/`context_after` (`structured_text.py:124-125`,
`long_tail.py:242-244`). `structured_text.py:157-160` emits an entire heading
region as `raw_value` with `span=(0, len(heading_text))`. That particular case is
caught by `is_whole_document` (span covers the unit), but the check is
structural — "does this span cover its unit" — not a length. A 50,000-character
span inside a 200,000-character unit passes it and releases 50,000 characters.

**Verdict for the lead's question.** The dossier is capped in COUNT (10 members,
enforced, with named omissions) and in the per-excerpt text P9 *stores* (240
chars). It is capped in SIZE by nothing that is wired. The one clean gap to name
is **(b)**: `max_excerpt_characters` is the only excerpt-length policy the
deployment sets, and the release request does not use it.

---

## 4. The two-condition placement thresholds

**The fractions check out.** `placement/scoring.py:42-48`:

```
DIRECT_FACT: 3   ACCEPTED_GROUP: 2   GRAPH_RELATIONSHIP: 1   STRUCTURAL_RELATIONSHIP: 1
_MAX_WEIGHT = 7
```

`support_score = support_scale_max * weight / 7` (`scoring.py:79`). A direct fact
alone is 3/7 = 0.4286; a direct fact plus an accepted group is 5/7 = 0.7143.
`cli.py:112-114`'s claim is exactly right, and 0.50 does sit between them. The
margin, which the comment does not argue, turns out to be equally well placed:
the achievable score gaps are 1/7 = 0.1428 and 2/7 = 0.2857, and 0.20 is the only
round number between them. Both thresholds sit in wide dead bands — any value in
(0.4286, 0.7143] and any in (0.1428, 0.2857] behave identically — so neither is a
knife edge. That is a good property and nobody wrote it down.

**The two unreachable channels are real, and I confirmed them.** The only place
in `src/` that builds a channel list is `placement/retrieval.py:126-146`. It
appends `DIRECT_FACT`, `ACCEPTED_GROUP`, `CURATED_FOLDER`, `SEMANTIC_NEIGHBOUR`
and nothing else. `GRAPH_RELATIONSHIP` and `STRUCTURAL_RELATIONSHIP` appear only
in the constants (`retrieval.py:38-39,46`), the weight table
(`scoring.py:45-46`), and tests that construct them by hand
(`tests/p11/test_p11_scoring.py:189,222`). No production path emits either.

Consequences, in order of how much they matter:

1. **The maximum achievable score is 5/7 = 0.7143, not 1.0.** `support_scale_max
   = 1.0` is therefore not what `cli.py:112` claims ("the scorer's weights
   already sum to it"). The weights sum to 7 and are divided by 7; the *reachable*
   numerator maxes at 5. The value 1.0 is harmless — every threshold is checked
   against the same normalised scale — but the stated justification is wrong, and
   a reader comparing `support 0.71` against a declared scale of 1.0 will read a
   confident placement as a mediocre one.
2. **The score is a four-value lattice, not a continuum:** {0, 2/7, 3/7, 5/7} =
   {0, 0.286, 0.429, 0.714}. The decimal precision in the stored decisions is
   theatre.
3. **The threshold does not need moving.** Because the reachable values are so
   sparse, dropping the two dead channels and renormalising to `_MAX_WEIGHT = 5`
   would give {0, 0.4, 0.6, 1.0} — and 0.50 would still sit in the same gap,
   between "direct fact alone" and "direct fact plus group". The chosen number
   survives the fix. That is worth saying plainly, because it means this is a
   *documentation and reachability* defect, not a *calibration* defect.

**But there is a fourth consequence that neither audit has named, and it is the
serious one.** On a shipped run, `DIRECT_FACT` cannot fire either. The channel
requires the node to carry an `expected_values` (field, value) pair
(`retrieval.py:129-131`, via `placement/index.py:125-126,170-171`), and
`expected_values` is populated only on child nodes projected from a resolved
dimension (`tree_design/materialise.py:437-463`). Every run I made produced a
single branch node with `"expected_values": []` and `"template_fields": []`.
Measured, from `p4.sqlite`:

```
outcome = abstain
"alternatives": [{"node_id": "node_3", "rank": 1, "support_score": 0.2857142857142857}]
```

0.2857 = 2/7 = `ACCEPTED_GROUP` alone. **The highest support score this
deployment has ever produced is 0.286, against a threshold of 0.50.** Across
every corpus I ran (4, 9, 10, 11, 40, 800 files, and a 9-file mixed-course
corpus), `placed = 0`. The two-condition policy is not mis-tuned; it is
untested, because nothing has ever cleared it.

---

## 5. `generic_hub_frequency = 9` and `max_graph_nodes = 10` are coupled

Not asked for, found while checking #17, and it is the worst number in the file.

`grouping/pipeline.py:167,174` caps a seed's neighbourhood at `max_graph_nodes −
1 = 9`. With retrieval by shared validated fact alone (`cli.py:762-767` turns
every similarity channel off), each neighbour contributes exactly one edge, all
carrying the *same* bridge entity — the group's own fact. `_hub_entities`
(`grouping/graph.py:119-131`) suppresses any entity appearing `>= 9` times.

So the hub rule fires when the graph is exactly full, and never otherwise. It is
a step function on corpus size, not a test of genericity. Measured, one corpus of
identical `PHYS 1401` homework at four sizes:

| files | edges | hub-suppressed |
|---|---|---|
| 8 | 112 | **0** |
| 9 | 144 | **0** |
| 10 | 180 | **90** |
| 11 | 198 | 99 |
| 800 | 14,400 | 7,200 |

At ten files, 100% of the live edges are marked as a hub. The comment directly
above (`graph.py:160-165`) records fixing exactly this failure from the other
direction — reading `detail` as an entity "so the group's own basis became a
'hub' the moment enough files corroborated it, and §4.3's count, which exists to
find an entity that bridges UNRELATED groups, punished the corroboration §4.3
asks the rules to make". The `detail` bug is fixed. The *number* reintroduces it.

On the current path the damage is contained: `seed_anchors` is true
(`pipeline.py:422`), so each seed anchors itself and the group still forms with
all ten members (verified: `anchor_count = 10`, `stop_rule_hits = []`,
`state = supported`). But three things are already wrong, and one is latent:

* `_why_retrieved` (`dossier.py:134-138`) filters suppressed edges, so at ≥10
  members every candidate file's "why was this here" reads as the seed's file id
  instead of a channel name.
* `p8_seam.py:288-290` drops every `Support` for the same reason — the model
  would be told the group has no supporting edges.
* `evaluate_stop_rules` (`graph.py:311-320`): `suppressed and not live` is
  precisely the ≥10 state. Any group whose seed does *not* self-anchor fires SR3
  ("one high-frequency entity acts as the only bridge") purely because ten files
  agreed with each other.

No test covers this: every P9 test that sets `generic_hub_frequency` uses `3`
(`tests/p9/test_p9_graph.py:50,227,244`) against small graphs, which keeps the
value well clear of the node cap. The nine-vs-ten coupling has never been run.

---

## 6. Two numbers that cannot fire, for the same reason

`cli.py:713-714` supplies `entity_frequency={fact.value: 1 for fact in facts}`
and `generic_entity_frequency=200`. The consumer is
`placement/graph.py:154-157`: `entity_frequency.get(entity, 0) >=
generic_entity_frequency`. The left side is the literal `1` for every value the
CLI ever produces; the right side is 200. **P11's generic-entity suppression can
never fire on any corpus.** The comment at `cli.py:711-714` says "Both numbers
are this deployment's; `00` states neither", which is true and says nothing about
the fact that one of them is a constant standing in for a count nobody computes.
`200` is not wrong — it is unexaminable, because no run can distinguish it from
`2` or from `2,000,000`.

---

## 7. Two caps where the smaller one kills the larger

`NAMES_LISTED_PER_GROUP = 10` (`cli.py:825`) has the best comment of any number
in the report section: it explains the rule, cites `tree_design/health.py` as the
precedent, and preserves the protected-group exemption. It is also dead on the
only path that reaches it. `residual.max_files_per_review_batch = 8` splits every
review set into batches of 8, and the batch label is part of the report's dedup
key (`cli.py:934`), so no group of files sharing a key can exceed 8. The
"...and N more, counted here rather than listed one by one" branch
(`cli.py:941-947`) never executes on the residual path. It could execute on the
`PLACE` path — where files share a destination and carry no review set — but
per §4 no file has ever been placed.

Verified in the 800-file run: 800 file names printed, zero "and N more" lines.

---

## 8. What I would flag, in priority order

Flagging only; no fix applied, no repo file changed.

1. **The report's length is unbounded in the number of files** (§2). One shipped
   ceiling changes behaviour and it defeats the summarisation the report was
   rewritten to provide. 1,611 lines for 800 files, measured.
2. **`generic_hub_frequency = 9` against `max_graph_nodes = 10`** (§5). A hub
   rule that fires on corpus size. Cliff verified at exactly 10 files.
3. **The release request does not use `max_excerpt_characters`** (§3b). The one
   excerpt-length policy this deployment sets does not bound the excerpt that
   would leave it, and the `span=None` path skips the whole-document backstop too.
4. **`support_scale_max = 1.0`'s stated justification is false, and the reachable
   maximum is 0.714** (§4). The value is harmless; the sentence is not, and a
   `support: 0.71` in a report reads as weak evidence when it is the strongest
   the system can produce.
5. **`model.max_dossier_tokens_per_call = 8` in the database vs `4000` injected**
   (§2). Inert today, a hard denial of every dossier the day a model is wired.
6. **Two ceiling keys nobody reads** (§2): `grouping.max_candidate_cluster_size`
   and `TreeLimits.max_dossier_tokens`.
7. **`generic_entity_frequency = 200` against a constant `1`** (§6).
8. **Ten of seventeen P1 ceilings unset** (§2), including
   `evidence.context_window`, which `budget.py:44-49` says must be in the
   extraction fingerprint.

## 9. What I checked and found sound

Worth recording so a later reader does not re-audit it.

* The injection discipline is real. `placement/config.py:96-107`,
  `grouping/config.py:47-55` and `tree_design/config.py:70-77` each refuse a
  missing or non-positive limit with a named exception and ship no fallback. I
  found no numeric default anywhere under `src/` outside `cli.py`.
* `SupportPolicy.__post_init__` (`placement/config.py:64-88`) rejects a threshold
  outside the declared scale with an argument for why both directions are bugs.
* `policy_id` genuinely travels: it is on the policy, and the policy is required
  at `scoring.py:69` before any threshold is read.
* `residual.py:158-166` refuses a partition that drops or invents a file, with
  the right reason.
* `dossier.py:117-120` — taking the span from the observation and not from the
  truncated text — is a subtle correctness point handled correctly.
* The protected-container rule holds through every number here: `_protected`
  (`cli.py:911-923`) makes a protected group exempt from `NAMES_LISTED_PER_GROUP`,
  and the protected block is printed before any total (`cli.py:876-885`). No cap
  in this audit can summarise a protected area away.
