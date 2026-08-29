# 5. Grouping — which files belong together

This is the part that decides "these four files are one course". It reads facts that P6 has
already validated, finds other files that might be related, refuses to form a group when any
of six rules says it should not, and publishes a group with its members. It writes no folder,
no path and no destination — where a group's files go is P10's and P11's question, and no
column in P9's seven tables names one (`store.py:14-17`, `schema.py:13-15`).

Everything below is what `src/grouping/` actually does. Where the SPEC promises something the
code does not do, it is said so in place.

---

## 5.1 The shape of one pass

`group_subject` (`pipeline.py:371`) is the whole part, run once per file in the corpus.
`production.py:540-551` calls it in a loop over the scan roster; there is no batch mode and no
corpus-level clustering step anywhere.

For one file it does, in order:

1. **Seeds** — find the legal starting points for this file (`pipeline.py:400`).
2. **Embeddings** — compute and store vectors, if a runtime was supplied (`pipeline.py:406`).
3. **Retrieval** — find a bounded neighbourhood (`pipeline.py:410`).
4. **Graph** — turn the neighbourhood into typed edges, suppress hubs, cap it
   (`pipeline.py:415`).
5. **Stop rules** — five of the six, decided here (`pipeline.py:441`).
6. **Record** — write the edges, join or mint the group, write this file's membership
   (`pipeline.py:478-503`).
7. **Dossier** — assemble a reference-only packet (`pipeline.py:505`).
8. **Model** — hand it to P8 if a model was configured (`pipeline.py:521-576`).

Two orderings are load-bearing and the module says so at the top (`pipeline.py:9-16`). The stop
rules run **before** the dossier is assembled and before any model call, so a group that cannot
form costs neither. And the set of files eligible for embedding is bounded **before** any text
is read, because encoding is paid at read time and a cap applied afterwards has already been
exceeded.

Only `seeds[0]` is used (`pipeline.py:405`). A file with several qualifying facts seeds exactly
one group; the rest are discarded — finding 10 below.

---

## 5.2 Seeds: where a group's claim to exist starts

### The four kinds

`vocabulary.py:39-47` fixes the closed set:

```
strongly-identified-file | validated-shared-fact | structural-family |
user-created-starting-point
```

Three of them are derived from a fact, and which one is chosen is a lookup on the fact's
**field key**, not on any judgement (`seeds.py:119-130`):

- the field is `duplicate_family` or `version_family` → `structural-family`. A family value
  "names a structural relationship rather than a subject".
- the field is P6's photo `event` field → `validated-shared-fact`. A photo event is a
  deterministic clustering over camera, time and GPS metadata that P6 already did.
- anything else → `strongly-identified-file`.

P9 spells no domain field name of its own. `EVENT_FIELD`, `DUPLICATE_FAMILY_FIELD` and
`VERSION_FAMILY_FIELD` are imported from `facts.read_surface` (`seeds.py:29-36`), so a rename
upstream moves this with it.

### P9's own anchor bar, and why it is narrower than P6's

This is the most deliberate decision in the module and the docstring argues it at length
(`seeds.py:4-17`).

P6 publishes a read called `proposal_eligible`. Its state set is
`PROPOSAL_ELIGIBLE_STATES = STRENGTH_ORDER[1:]` (`facts/read_surface.py:79`), which resolves to
four states: `llm_supported`, `validated`, `direct`, `user_confirmed`
(`facts/states.py:53-59`). That is the surface a **folder proposal** may rest on. P9 does not
use it as its anchor authority; it applies its own filter afterwards:

```python
ANCHOR_STATES: frozenset[str] = frozenset({"direct", "validated"})   # seeds.py:47
```

`Seed.__post_init__` refuses anything below it (`seeds.py:92-97`): "a proposal-eligible fact is
a candidate, not an anchor". Two states are excluded, for two different reasons.

**`llm_supported` is excluded because it is a model conclusion.** Letting one seed a group lets
the model confirm its own earlier guess — the loop the stop rules exist to break
(`seeds.py:8-10`). The dossier P9 builds is handed to a model; if the model's own prior output
could have started the group, the model's answer would be evidence for a question the model
already answered.

**`user_confirmed` is excluded even though it is the strongest state P6 has** (it sits above
`direct` in `STRENGTH_ORDER`). The reasoning (`seeds.py:11-14`): user intent should enter
through the door built for it, carrying a decision the user made *about this group*, rather
than by widening the evidence bar so that any confirmed fact anywhere starts one. A user who
once confirmed `employer = Acme` on a single file has not thereby asked for an Acme group.

A seed must also cite the observation that states it (`seeds.py:98-102`): "one that cites
nothing cannot be checked or replayed."

### How the anchor rows are gathered

`_anchor_rows` (`seeds.py:133-147`) reads three of P6's published surfaces —
`proposal_eligible`, `event_facts`, `family_facts` — deduplicates on
`field_key:value_id`, puts **every** row through `ANCHOR_STATES`, and returns them in sorted
key order. The extra two reads exist because a structural or event fact can sit at `validated`
without being a proposal candidate.

There is an asymmetry here worth noticing. `proposal_eligible` filters three things —
state, `active`, and `superseded_by IS NULL` (`facts/read_surface.py:167-169`). `event_facts`
and `family_facts` filter **none** of those; they are plain field-key selections over
`facts_for_file` (`facts/read_surface.py:284-305`). So a deactivated or superseded family or
event fact that is still at `validated` will pass P9's bar and seed a group.

### The user seed, and why it answers alone

The one channel user intent enters by is a callback, `user_seed_for(file_id, content_hash)`,
injected into `group_subject`. If it returns a `UserSeed`, `seeds_for_file` returns **that and
nothing else** (`seeds.py:162-180`):

> An explicit user seed answers on its own: the user said where a group starts, and P9 does not
> add fact-backed seeds beside that decision.

A `UserSeed` carries `file_id`, `content_hash`, `basis` (the decision the user made) and
`decided_at`, all required (`seeds.py:55-66`). The `basis` is mandatory a second time inside
`Seed.__post_init__` (`seeds.py:85-91`): "a user seed carries the decision the user made;
without it nothing can say why this file starts a group." In exchange, a user seed is exempt
from the anchor-state and observation-key checks — it has no field, no value, no reliability
state and no observation key (`pipeline` builds it that way at `seeds.py:169-180`).

Anything returned that is not a `UserSeed` is refused rather than interpreted
(`seeds.py:164-168`).

**The shipped deployment passes `user_seed_for=lambda file_id, content_hash: None`**
(`cli.py:756`). There is no user-seed path in the command a person can run.

---

## 5.3 The group address — the change of 2026-08-29

This is the most important mechanism in the section, and it is one commit old.

### What it was, and what it cost

The group id used to be derived from the seed's **file**: `group:{file_id}:{seed_kind}`. A file
that identified itself strongly enough became its own group. `65` §4.2 records what that did on
the first run over a real folder:

```
group:e46ba371-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:84d59bfc-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:96020a5e-…:strongly-identified-file   academic   PHYS1401   coherent   engine
group:9db8361f-…:strongly-identified-file   academic   PHYS1401   coherent   engine
```

Four files each stating `subject = PHYS1401` minted four one-file groups carrying the same
`display_label`. The `Coursework` branch was proposed and left empty, and all four placements
abstained. `65` calls it "a north-star defect, not a cosmetic one" — a person with four files
from one course is shown four identically-named groups and an empty folder.

The diagnosis in `65` is precise and the fix follows it exactly: "The strategy is not wrong in
general: a strongly self-identifying file *should* be able to stand alone when nothing else
shares its identity. The defect is that the strategy does not check whether anything else
resolved to the same identity before minting a singleton for it."

### What it is now

`group_address` (`pipeline.py:224-259`):

```python
if not (seed.field_key and seed.value):
    return f"group:{seed.file_id}:{seed.seed_kind}"
digest = hashlib.sha256("\x1f".join((seed.field_key, seed.value)).encode("utf-8")).hexdigest()
return f"group:{seed.field_key}:{digest}:{seed.seed_kind}"
```

The address is derived from the **identity the seed states**, not from the file that states it.
The docstring's own statement of the principle (`pipeline.py:238-241`): "A fact-backed seed's
claim is not about its file. It is `subject = PHYS1401`, and every file that states it is
stating the SAME thing, so the address is that claim."

The value is digested rather than spelled into the id because a field value is arbitrary user
text — a course code, a client name, a filename with a colon in it — and an id is parsed and
read in logs (`pipeline.py:249-254`). The field key and the seed kind stay in plain sight;
`anchor_facts` carries the value itself.

A `user-created-starting-point` keeps the file address, and the docstring argues this is not an
inconsistency (`pipeline.py:243-248`): the user said *this file* starts a group, and two users'
two decisions about two similar files are two groups. It falls out of the same branch as any
other seed with no field and value, since a user seed has neither.

Verified on a live three-file corpus: one group, `anchor_count = 3`, three memberships.

```
group:subject:0a1fcb6e…:strongly-identified-file | supported | PHYS1401 | academic | 3
```

### The join path

After the stop rules pass, `pipeline.py:480-503` does three different things depending on what
is already at the address.

**A second file stating the same identity — the join.** `_standing_group` reads the recorded
row (`pipeline.py:318-329`). If a group is there and its `seed_ref` differs from this file's,
the file's own membership is written against the **standing** group and the pass returns
(`pipeline.py:481-488`). No second group is minted, no dossier is assembled and no model is
called for the joining file.

`_standing_group` exists because `record_group` would answer the same question only by raising:
it refuses a second row under one id whose content differs, and two files that legitimately
share an identity **do** differ in `seed_ref` — the group started from whichever file the
corpus loop reached first. "That difference is not a conflict, it is the join"
(`pipeline.py:321-328`).

**The same file again — a rerun.** If the standing group's `seed_ref` matches, the recorded row
is taken as it stands and is not rewritten (`pipeline.py:489-497`). The stated reason: the
anchor set is a fact about the corpus **as scanned**, and scanning more of the corpus later
would otherwise rewrite a group's evidence underneath it. §8.2 supersedes rather than
overwrites, and a supersession needs a new id — which an address, by construction, cannot have.
The docstring is explicit that whether a widened anchor set should mint a superseding group is
a real open question and is **not** answered there.

**Nothing at the address — mint.** `engine_proposal` fills in the verdict, label and category
(§5.8), and `record_group` writes the row (`pipeline.py:498-500`).

### Why the standing group is not re-judged

`pipeline.py:466-472` states the reason directly:

> The standing group is taken as recorded and is not re-judged here. Its verdict was written
> once, from the graph that already contained these files; re-asking would spend a second
> dossier and a second model call to answer a question P9 has answered, and could return a
> different verdict for the same material depending on which file the corpus loop reached
> first.

The second half of that is the real argument. Re-judging on every join would make the group's
verdict a function of corpus iteration order. Whether a **later** member should reopen
coherence is flagged as §4.5's question and left open.

The load-bearing assumption is that the first file's graph already reached the others. It does,
when the shared-fact channel finds them: `anchoring_files` counts every file the graph reached
by an unsuppressed `shared-validated-fact` edge, plus the seed itself (`graph.py:249-265`), so
`anchor_count` is 3 on the first file of a three-file course, not 1. `_group_for`'s comment
records that this was previously wrong — a one-tuple of the seed's own file made the count 1
for a group of four, "understating to P10 and P11 the very support the group was formed on"
(`pipeline.py:263-268`).

---

## 5.4 Retrieval: bounding the neighbourhood before anything is read

`retrieve_neighbors` (`retrieval.py:361`) returns a `Neighborhood` — a seed, a tuple of
neighbours, omissions, and a `capped` flag. It "decides nothing" (`retrieval.py:369`).

### The six channels

| # | Channel | May anchor? | How it finds a file |
|---|---|---|---|
| 1 | `shared-validated-fact` | **yes**, above the bar | candidate's `proposal_eligible` rows contain the seed's `(field_key, value)` (`retrieval.py:175-197`) |
| 2 | `duplicate-or-version-link` | no | candidate shares a `duplicate_family` or `version_family` value (`retrieval.py:200-237`, via `family_facts`) |
| 3 | `compatible-document-type` | no | injected `document_compatible(domain, left, right)` predicate says so (`retrieval.py:240-261`) |
| 4 | `existing-related-folder` | no | candidate's `directory_position` equals the seed's (`retrieval.py:264-292`) |
| 5 | `bounded-session` | no | candidate shares a download-session value (`retrieval.py:398-400`, via `session_facts`) |
| 6 | `mutual-semantic-retrieval` | no | both directions of an injected similarity clear an injected threshold (`retrieval.py:295-341`) |

Channel 1 is the only one that may set `anchors=True`, and only when the *candidate's own*
fact is at `ANCHOR_STATES` (`retrieval.py:193`). Every other channel hardcodes `anchors=False`,
including the ones that feel strongest — "A duplicate link brings a genuinely related file and
is not evidence of shared purpose" (`retrieval.py:10-15`, `retrieval.py:208-212`).

Channel 6 is **mutual** by construction: both `similarity(seed, other)` and
`similarity(other, seed)` must clear the threshold (`retrieval.py:329-331`). The reason
(`retrieval.py:302-305`): one-way nearness is what a hub produces — it is near everything, and
nothing is near it in return.

### The bound

`_corpus` (`retrieval.py:127-148`) reads only files at `scan_state = 'included'` — P3's
boundary. "an excluded file reaching a dossier would be the scan boundary failing silently."
The result is then ranked and cut (`retrieval.py:404-412`):

```python
weight = knowledge.channel_weights.get(neighbor.channel, 0)
return (-weight, neighbor.content_hash, neighbor.file_id)
...
kept = ordered[: limits.max_retrieved_neighbors]
```

The cap bounds the **result**, not the scan, and `retrieval.py:27-31` explains why: P6 publishes
only per-file reads, so matching a shared fact means reading each candidate's facts rather than
consulting an index — "P9 inventing one would be P9 querying P6's tables."

`DEFAULT_CHANNEL_ORDER` (`retrieval.py:56-63`) documents the intended priority — direct evidence
first, proximity last — and **has no reader anywhere in `src/`.** The live ranking is
`channel_weights`, and the shipped deployment passes `channel_weights={}` (`cli.py:749`), so
every channel weighs 0 and the cut is decided entirely by `(content_hash, file_id)`. At a cap of
50 over a small corpus this never bites; over a large one it would drop shared-fact neighbours
in favour of folder-mates.

### Absent means omit, never assume

`RetrievalKnowledge` (`retrieval.py:74-83`) holds six injected authorities, and
`retrieval.py:21-25` states the rule: a missing one omits its channel and says so, "rather than
assuming a permissive default — treating every document type as compatible would quietly widen
every group in the corpus." Channel 3 honours that exactly: absent predicate → channel skipped,
`"missing_document_compatibility"` appended to `omissions` (`retrieval.py:391-396`).

Semantic retrieval honours it in the opposite direction: with `embeddings_enabled` true and any
of `similarity`, `similarity_threshold` or `embedding_identity` missing, the call raises
`ConfigurationRequired` (`retrieval.py:344-358`, `retrieval.py:375-376`). That is right — a
semantic channel with no similarity measure is not a narrower answer, it is an unanswerable one.

### What the shipped deployment turns off

`cli.py:745-755` supplies `document_compatible=None`, `channel_weights={}`, `similarity=None`,
`similarity_threshold=None`, `embedding_identity=None`, `domain=None`,
`conflicts_for=lambda file_ids: ()` and `duplicate_or_version=None`, with
`embeddings=EmbeddingsOff()` (`cli.py:757`). The comment calls it "the deterministic path P9 is
explicit is a complete path."

That leaves **channels 1, 2, 4 and 5 live**; channel 3 omitted with a named omission; channel 6
off. On the live three-file run the graph carried six `shared-validated-fact` edges and six
`existing-related-folder` edges and nothing else. It also means **SR4 can never fire** in the
shipped deployment, and channel 2 is a live landmine — findings 4 and 5 below.

---

## 5.5 The typed-edge graph

### What an edge is

`TypedEdge` (`records.py:305-330`) is a directed pair of file ids, an `edge_type` from a closed
seven-value set, an `evidence_ref`, an optional weight, an optional `bridge_entity_ref`, a
`hub_suppressed` flag and a timestamp. A self-edge is refused: "an edge from a file to itself
relates nothing" (`records.py:329`).

Seven edge types over six retrieval channels (`vocabulary.py:114-125`), because
`duplicate-or-version-link` is one way of *finding* a neighbour and a `duplicate` is not a
`version-family`. Which of the two an edge is cannot be read off the channel name, so the
discriminator `duplicate_or_version` is injected — "absent means the channel is omitted, and
never guessed" (`graph.py:4-9`). Getting it wrong "puts two revisions of one document into a
group as two documents, or two different documents into one version family."

Edge ids are content-derived (`graph.py:82-93`): a SHA-256 over
`(group_id, from, to, edge_type, bridge)`. A replay re-derives the graph, and a
`Support.edge_ref` recorded yesterday has to resolve to the same edge today; a uuid would make
every replay a different graph over the same evidence.

### `evidence_ref` and `bridge_entity_ref` are different fields

An edge stores what a later reader resolves to **prove** the edge existed, and separately the
thing the edge runs **through** (`graph.py:11-14`).

This split was a bug fix and the comment is emphatic (`graph.py:160-165`). The graph used to
read the neighbour's `detail` — prose like `subject=PHYS1401`, `pdf ~ pdf`, `mutual >= 0.8` —
as the bridge entity. That "promoted every description to an entity identity, so the group's own
basis became a 'hub' the moment enough files corroborated it — and §4.3's count, which exists to
find an entity that bridges UNRELATED groups, punished the corroboration §4.3 asks the rules to
make." `Neighbor`'s docstring says the same from the other side (`retrieval.py:88-99`): "A
description is not an entity, and the basis value is never the hub."

**Exactly one channel publishes a bridge entity**: `existing-related-folder`
(`retrieval.py:264-292`). A folder is a named thing that exists independently of the two files
it joins, which is what makes `~/Downloads` bridging half the corpus the case worth suppressing.
Verified on the live run: `shared-validated-fact` edges carry a null bridge; the folder edges
carry the folder path.

### Hub suppression

`_hub_entities` (`graph.py:116-130`) counts how many edges each bridge entity appears on and
returns those at or above `limits.generic_hub_frequency`. Every edge is then rebuilt with
`hub_suppressed = bridge_entity_ref in hubs` (`graph.py:184-195`).

The rule is a **count, not a list** (`graph.py:119-122`): "A hard-coded university suffix or
mail provider here would be P9 authoring a policy that belongs to configuration, and the corpus
it was tuned on is not this user's." The frequency is injected with no default
(`config.py:43-44`); the shipped value is 9 (`cli.py:143`).

Suppression does not delete the edge. It sets a flag, and every downstream reader filters on it:
`anchoring_files` (`graph.py:260-262`), `evaluate_stop_rules`'s `live` set (`graph.py:298`),
`_why_retrieved` (`dossier.py:135-138`), `_edge_support` (`p8_seam.py:288-291`). The edge is
still written and still inspectable.

### `anchoring_files`

```python
def anchoring_files(graph, *, seed_anchors: bool) -> frozenset[str]:   # graph.py:249
```

Every file the graph reached by an unsuppressed `shared-validated-fact` edge, plus the seed
itself when the seed's own fact is validated. The reason the seed is included
(`graph.py:252-257`): "a group of one, seeded by a direct fact, has an anchor even though no
edge points at it. Counting only edge endpoints would say a file cannot anchor itself, which is
the opposite of what a strongly-identified seed is."

`seed_anchors` is computed at `pipeline.py:422` as `bool(seed.observation_key and
seed.reliability_state)` — true for every fact-backed seed by construction, false for every
user seed.

### The cap

`build_graph` (`graph.py:142-220`) ranks edges before cutting: anchoring edges first, then
everything else by edge id (`graph.py:133-139`) — "Dropping an anchor to keep a semantic edge
leaves a graph that still reads as connected while the evidence that made it a group is gone."
It then walks the ranked list, admitting a new file only while `len(reached) <
limits.max_graph_nodes`, and records each dropped file id in `omissions` with the limit that
dropped it (`graph.py:198-219`).

### The graph was drawn, decided on, and thrown away

`record_edges` (`store.py:277`) — the writer for the `group_edges` table — **had no caller
anywhere under `src/` until 2026-08-29.** Every run built a graph, decided the stop rules on it,
built a dossier from it, and dropped it. `pipeline.py:471-477` records the fix: "`66` §3 makes
'also related to' a state a person is shown — 'a relationship, not as uncertainty' — and a
relationship whose typed edge exists only in memory cannot be shown, reviewed or replayed."

The write sits **after** the stop rules and before the group, "so a graph belonging to a group
that never formed is not stored as though it did" (`pipeline.py:476-477`). Edge ids are
content-derived and the writer uses `INSERT OR IGNORE`, appending the §8.2
`graph-edge creation` event only when the row is genuinely new (`store.py:292-323`) — so a join
and a rerun add no duplicate events.

`edges_for_group` (`store.py:327`) reads them back and has **no caller in `src/`** — the write
now happens, the read is still unwired. Both functions discard their `group_id` argument
(`store.py:290`, `store.py:332`), because an edge outlives the group that first drew it, so
`edges_for_group` in fact returns every edge in the database.

---

## 5.6 The stop rules

Five of the six are decided by `evaluate_stop_rules` (`graph.py:283-348`), before the dossier
and before any model call. It returns `None` when nothing fired.

| Rule | Fires when | Code |
|---|---|---|
| SR1 | `anchoring_files(...)` is empty — **zero** anchors | `graph.py:302-306` |
| SR2 | there are live edges and **every one** is `mutual-semantic-retrieval` | `graph.py:308-311` |
| SR3 | some edge was hub-suppressed **and no live edge remains** | `graph.py:313-323` |
| SR4 | the injected `conflicts_for` oracle returns anything | `graph.py:325-331` |
| SR6 | P1 holds a current `reject` learning record for this exact equivalent | `graph.py:333-335` |
| SR5 | — | not here; see below |

**SR1 is zero anchors, not "below the bar".** The distinction is drawn twice
(`graph.py:303-305`, `graph.py:268-280`). `meets_support_bar` is a separate function applying
`limits.minimum_independent_anchors`, and it decides whether a formed group may become
`supported` rather than whether it exists at all. "Conflating the two made a one-anchor group
vanish instead of waiting for confirmation."

**SR3 is stated as "a hub was suppressed and nothing else is left holding the graph together."**
`graph.py:315-321` explains why the obvious alternative is wrong: asking whether every
entity-bearing edge was suppressed says the same thing only while every edge carries an entity,
which stopped being true when `bridge_entity` became its own field — and would then fire on a
graph whose anchors are perfectly alive, "destroying the group for having sat in a busy folder."

**SR6 reads P1's learning store, not the acceptance table.** `_standing_reject`
(`graph.py:228-246`) queries `learning_records(conn, "group", group_id)`, matches
`proposal_class` and `basis_key` exactly, and treats only `polarity == "reject"` as suppression.
The comment notes that P8's own `suppressed_by_learning` reads the same rows the same way —
"two readings that disagreed would mean a proposal P8 refuses to call about and P9 keeps
surfacing." The `basis_key` for a group is its anchor facts, sorted
(`learning.py:74-83`): sorted "because `anchor_facts` is a list and the same two facts can
arrive either way round; two orderings producing two keys would be two proposals, and a
rejection of one would not stop the other."

**SR5 is absent by construction** (`graph.py:16-18`, `graph.py:294-296`). It means P8 could not
explain the group with valid citations, which is only knowable after `run_call` returns.
Deciding it here "would be P9 predicting what P8 was going to say." It is mapped in the P8 seam
from four reason codes — `CITATION_NOT_IN_DOSSIER`, `CITATION_NOT_FOUND`,
`CITATION_SPAN_MISMATCH`, `UNCITED_CLAIM` (`p8_seam.py:87-92`, `p8_seam.py:364-370`).

### The outcome

```python
outcome=TENTATIVE_DISCOVERY if fired == [SR1] else NO_GROUP     # graph.py:347
```

§4.9 permits an anchorless group to be shown "only as tentative discovery candidates, if at
all". The code reads that permission as belonging to **SR1 alone**: "every other rule is a
positive reason not to form the group, and one of those outranks a permission to show it
hesitantly" (`graph.py:343-346`).

When a rule fires, `group_subject` returns immediately with the outcome and the unrecorded group
(`pipeline.py:445-450`). **Nothing is written**: no group row, no membership, no edges (the
`record_edges` call is below this return), and no stop-rule row — finding 3 below.

---

## 5.7 What a group record holds

`Group` (`records.py:149-232`) is frozen and validates itself. The fields P9's own code fills:

- `group_id` — the address (§5.3).
- `seed_ref` — `f"{file_id}:{content_hash}"`, the file the group started from.
- `seed_kind`, checked against the closed four.
- `proposed_basis` — `f"{field_key}={value}"` for a fact seed, the user's `basis` for a user
  seed (`pipeline.py:283-286`). Required non-empty: "the engine writes the reason a group exists
  BEFORE the model sees anything; a group with no proposed basis has none" (`records.py:212-215`).
- `anchor_facts` — one `AnchorFact` carrying the field, the value, **every** anchoring file id,
  the reliability state and the observation key — or an empty tuple when the seed states no
  value (`pipeline.py:269-278`).
- `anchor_count` — `len(facts[0].file_ids)`, i.e. the number of files that independently state
  the basis value.
- `pre_model_signals` — `{"anchor_count": anchor_count}` and nothing else.
- `conflicts` — the oracle's answer over this graph, taken rather than hardcoded
  (`pipeline.py:303-306`). The comment records that hardcoding `()` meant "a group SR4 destroyed
  came back claiming no conflict, with the reason surviving only as a formatted string in
  `stop_rule_outcome.evidence_refs`."
- `state` — `supported` when `meets_support_bar` holds, else `candidate` (`pipeline.py:437-440`).
- `created_by` — always `rules`.
- `sensitivity_state` — always `none` (`vocabulary.py:201-210` defines a second value,
  `sensitive-present`, which nothing writes).

`coherence_verdict`, `coherence_citations`, `group_category`, `display_label` and `label_source`
are blank at construction **and blank only here** (`pipeline.py:294-299`): the builder runs
before the stop rules, so it cannot know whether the group will form at all, "and a verdict
written on a group SR4 is about to destroy would be a claim about material that never became a
group."

`dossier_id`, `llm_response_ref` and `validation_verdict_ref` are `None` at construction and
nothing ever sets them — the group is recorded before the dossier is assembled, and the P8 seam
deliberately writes no field back onto the group (§5.9).

---

## 5.8 Coherence, naming and category — what the engine may decide by rule

`naming.engine_proposal(group)` (`naming.py:128-156`) is the only thing that ever fills in a
verdict and a label in a deterministic deployment. `cli.py` runs with `p8_run_call=None`, "so if
the engine says nothing about a group, nothing does" (`naming.py:8-10`).

It takes one argument, and that argument is the group record. With no connection and no path it
cannot open a container — which is what lets a corpus P7 declined to classify still be named
from facts P6 already holds, "present, counted, never opened"
(`tests/p9/test_p9_group_naming.py:581-592`).

**The verdict.** `engine_proposal` returns the group unchanged unless
`group.state == SUPPORTED` (`naming.py:142-143`). The argument (`naming.py:15-23`): §4.9's
minimum-independent-anchor bar is a **count over facts P6 already validated**, and
`meets_support_bar` has already applied it. A group at that bar is one whose files
independently state the same validated fact, and saying so is reporting a rule computation, not
synthesising a judgement. A group below it gets nothing written about it at all.

**The label is the anchor values themselves**, deduplicated and joined with an em dash
(`naming.py:118-125`, `LABEL_JOIN` at `naming.py:70`). The separator is "the only character in a
label this file contributes" (`naming.py:68-69`). The reasoning is §5.7's: "The system does not
invent PHYS1401, UChicago, Spring 2026, or PVA/RDP; those names emerge from validated facts,
user-confirmed groups, and accepted labels" (`naming.py:48-54`).

**The category is an intersection over P6's schemas.** `_SCHEMAS_BY_FIELD` (`naming.py:76-83`)
is inverted from `facts.domains.schema_fields` rather than written down. `domain_for`
(`naming.py:97-115`) intersects the owning schema sets of every anchor fact and returns the
single survivor, or `None`.

`None` is the common answer and the module argues it is the right one (`naming.py:30-37`):
seventeen of P6's field keys are referenced by more than one schema and six more are universal.
"a group with `domain=None` reaches P10 as a branch candidate that no applicability row claims,
which the user can see and act on, while a group with a CONFIDENT WRONG domain files their
matters into their coursework." Three of P6's twenty-three schemas — `identity`, `medical`,
`legal` — declare no field at all, so the engine returns `None` for a group of passports, which
the module says is right: P7 decides a file is identity material, not P9 (`naming.py:39-46`).

**Absent, not empty.** `Group.__post_init__` refuses a `display_label` or `group_category` on a
group whose `coherence_verdict` is not `coherent` (`records.py:220-227`), and the SQL enforces
the same thing as a table CHECK (`schema.py:56-60`). An unrecognised `group_category` is a load
error, not a label (`records.py:200-211`): P10 selects an applicability row *by* this value, so
an unrecognised one reaches no row and looks exactly like a group the library has no template
for, and "a wrong-but-plausible one is worse still — it files the material under a schema whose
recipes speak for somebody else's life."

The verdict and the label cannot come apart (`naming.py:134-140`): both are written from the
same facts or neither is, so an engine-coherent group always carries a name P10 can put on a
branch — `tests/p9/test_p9_group_naming.py:565-576` names the consequence of the alternative,
that `tree_design.upstream._label` raises for the whole plan version. The category may still be
`None` beside a label, and that pairing is deliberate: "a coherent group whose facts do not name
one domain is nameable and unroutable, which is exactly what it is."

`label_source` is one of `engine | llm-proposed | user-edited` (`vocabulary.py:135-139`).
`engine` is written here; **`llm-proposed` is written nowhere in `src/`** (§5.9);
`user-edited` is written by the CLI's review step (`cli.py:463`).

---

## 5.9 Membership

`Membership` (`records.py:233-296`) records that one file version belongs to one group, and
why.

**Two vocabularies that must not merge.** `basis` is the direct / context / user axis
(`direct-anchor | context-supported | user-attached`). `support[].support_kind` is the retrieval
channel a support came through. `vocabulary.py:4-7` and `records.py:105-110` both say not to
merge them, and `records.py:108-110` records what happened when they were one name: "a validator
checking 'the' vocabulary rejected every valid value from the other side."

**The direct-anchor invariant is enforced in the record.** A `direct-anchor` membership must
carry at least one `shared-validated-fact` support (`records.py:271-283`). The comment explains
why there is one check and not two: requiring that kind already excludes every set that is only
non-anchoring channels, and "a guard with no reachable cause is a claim about behaviour that is
not there." This is where "semantic retrieval and a bounded session propose a neighbour; they
never anchor one" is actually enforced.

A membership with no support at all is refused: "a membership with no support cannot say why the
file belongs" (`records.py:265-268`).

**Membership never writes a fact onto the member file.** Nothing in `src/grouping/` writes to
P6's fact tables — the only writes are to P9's own seven tables, P1's event log and P1's vector
store. A file that joins a PHYS1401 group does not thereby acquire `subject = PHYS1401`.

**A file may hold memberships in more than one group.** The `membership_id` is scoped by group
(`{group_id}:{file_id}` for the engine path, `{group_id}:{file_id}:{verdict_id}` for the model
path), and `memberships_for_group` filters by `group_id` (`store.py:266-274`). Nothing anywhere
constrains a file to one group. On the live run each file held two memberships — its P9 group
and the CLI's merged review group.

### Direct-anchor membership (the engine path)

`_self_membership` (`pipeline.py:332-368`) writes one membership per file that states the
identity: `basis = direct-anchor`, `decision = included`, `decision_source = rules`, one
`shared-validated-fact` support citing the seed's observation key, `outlier_flag = none`,
`validation_verdict_ref = None`.

Its name is a leftover and the docstring says so (`pipeline.py:336-341`): "It was named for the
group of one it used to be the only inhabitant of. Since `65` §4.2 a group is addressed by the
identity its seed states, so this is the record written once per file that states that identity
— four of them for a course with four files."

### Context-supported membership (the model path)

`apply_p8_verdict` (`p8_seam.py:294`) is the only place `context-supported` memberships are
written. On `accept_context_supported` it iterates `dossier.candidate_files`, writes each with
`basis = context-supported`, `decision = uncertain`, `decision_source = llm`, and support built
from every unsuppressed edge touching the file in either direction
(`p8_seam.py:273-291`, `p8_seam.py:385-411`).

**The membership and its review obligation are written in one transaction**
(`p8_seam.py:384`), and the module names this as the rule that costs the most if it is wrong
(`p8_seam.py:11-15`): "A context-supported member is a file the model was not sure about; making
it visible without the obligation that makes it safe is how an uncertain guess becomes a silent
decision." A context-supported result with no `plan_version_id` is refused outright
(`p8_seam.py:372-379`).

The seam also refuses to resolve a disagreement in the model's favour: an accepting outcome with
`may_propose=False` raises (`p8_seam.py:351-357`).

**What the seam deliberately does not write** (`p8_seam.py:308-328`). It writes no
`group_category` and no `display_label`: §4.5 task 4 *is* the model's, and P8's validator even
has a reason code for proposing a label without coherence — but `P8Verdict` has no field for
either, "so the answer the model gave never arrives here." Deriving one from `result.outcome`
would be P9 authoring the model's proposal on its behalf. This is why `label_source =
llm-proposed` is unreachable.

It writes no `coherence_verdict` either, and that one is flagged in the code itself as a
**reported gap rather than a settled rule**: `result.outcome` genuinely carries P8's coherence
answer, but the group row is already on disk, §8.2 supersedes rather than overwrites, and a
superseding group row needs a new `group_id` that every membership and acceptance row already
names by the old one. "That is a record-lifecycle change across the acceptance seam, not a field
fix, and it is not taken here quietly."

---

## 5.10 Acceptance and plan versions

`group_acceptance` is the only plan-versioned record P9 publishes (`acceptance.py:4-7`,
`schema.py:5-8`, `records.py:3-11`). Groups, memberships, dossiers and edges live in the shared
evidence database and survive every plan version; putting a version on `groups` would duplicate
the group, its dossier, its model response and every line of its evidence per version.

`accepted` and `rejected` are therefore **not members of `GROUP_STATES`**
(`vocabulary.py:17-35`). The stored lifecycle is four values —
`candidate | supported | tentative-discovery | unresolved`. The other two are resolved at read
time by an accessor, "published as a call rather than left to a consumer looking for `rejected`
in an enum that does not contain it — a consumer that looks and does not find is a consumer
about to invent one" (`acceptance.py:9-12`).

`pending-review` and `deferred` never become lifecycle states: "They are things a plan version is
doing, not things a group is" (`acceptance.py:14-15`).

### `group_state_as_of` is a question about lineage

```python
def group_state_as_of(conn, *, group_id, plan_version_id) -> str:   # acceptance.py:248
```

It does **not** resolve on the exact version id alone. `acceptance.py:22-37` gives the reason:
§8.8 makes a plan version a versioned object with a predecessor, and P10 opens a new draft
version for every recorded edit — a rename, a reorder, a moved branch. Resolved on the exact id,
the acceptance the user gave would name an ancestor of the version being asked about and every
later version would see none of it. So `_nearest` (`acceptance.py:224-245`) checks this
version's own row first, then walks the ancestry (`acceptance.py:186-221`) and returns the
closest opinion.

Three sub-rules ride with it:

- **Nearest wins, and a version that has spoken ends the walk whatever it said.** A version
  holding `deferred` is still deciding; answering it with an ancestor's `accepted` would
  overrule the live decision with the one it replaced (`acceptance.py:33-35`,
  `acceptance.py:260-263`).
- **An opinion does not leak sideways.** A version outside the ancestry inherits nothing.
- **`pending-review` and `deferred` are not returned.** They end the search but the caller gets
  the stored `Group.state` instead (`acceptance.py:268-270`).

The walk reads exactly one column of one foreign table — `plan_versions.predecessor_id` — which
the docstring defends as the minimum needed to give the opaque `plan_version_id` a meaning:
"Nothing here reads a node, a label or a shape" (`acceptance.py:188-195`). It handles a P9-only
database by asking whether `plan_versions` exists rather than catching `OperationalError`, which
"would also swallow a real one" (`acceptance.py:171-183`), and carries a `seen` set because
`predecessor_id` is a self-reference with no cycle constraint.

### Absence is not a state

`membership_review_state_as_of` (`acceptance.py:273`) **raises** `AcceptanceStateAbsent` rather
than returning `pending-review` for a membership no writer has recorded: "A `context-supported`
membership does not imply a pending review, and inventing one would put a review in front of the
user that no plan version asked for." That is why `record_context_review_pending`
(`acceptance.py:125-151`) exists and is called inside the membership-write transaction — "the
state a reader sees is one a writer put there."

`record_acceptance` (`acceptance.py:70-116`) appends and links, requiring a reason and an
existing predecessor for any supersession. The link is written **before** the insert, because
the unique index `one_current_group_acceptance` (`schema.py:220`) is over unsuperseded rows:
linking after would mean two current opinions existed for the length of one statement, "and the
database would refuse the insert that was about to resolve it" (`acceptance.py:94-98`).

### The review receiver

`learning.apply_review_action` (`learning.py:103`) maps P13's seven actions onto exactly two
writes: the plan-version acceptance row and a scoped learning event in P1's log
(`learning.py:142-171`). The mapping is stated one line per action rather than derived, "because
'reject implies negative' is the kind of derivation that quietly acquires an eighth case"
(`learning.py:54-67`). Every field is required and none defaulted (`learning.py:92-100`), the
scope most of all: "A guessed scope teaches the engine from one file that every file like it
belongs there, which is the failure the six scopes prevent."

`apply_review_action` has **no caller anywhere in `src/`**. P13 does not exist yet.

---

## 5.11 The dossier, and what happens with no model

`assemble_group_dossier` (`dossier.py:166`) builds a **reference-only** packet. Nothing in the
module reaches a model, a gate or a released span (`dossier.py:3-8`); it selects observation
keys, file-version identities and typed edges, and records what it left out. P8 alone
materialises released evidence through P7.

For each file in the bounded graph it resolves the handling class through P7's
`classification_store`, and a file P7 has not classified is **withheld and named**
(`dossier.py:199-204`): "Marked and counted, never opened. §8.4 requires classification before
escalation, so an unclassified file is withheld — and named in `omissions`, so a later reader
shows it as present-but-untouched rather than as a file that was never there."

Files then split by whether they state the group's basis: anchors on one side, candidates on the
other. The two arrays are **never merged**, and `CandidateGroupDossier.__post_init__` enforces
it (`records.py:530-556`) — an anchor file must carry `direct-anchor`, a candidate must not, a
candidate must name `why_retrieved`, and no file may appear on both sides. The reason
(`dossier.py:12-15`): "The model must be able to say a group is coherent while still marking
particular members uncertain, and it can only do that if direct evidence and inferred context
arrive apart."

Excerpts are one per cited observation key, truncated to the injected
`max_excerpt_characters` (`dossier.py:97-122`) — how short a short excerpt is "decides how much
of a file reaches a model. That is a policy, and it arrives injected" (`dossier.py:218-221`). A
key that resolves to nothing is skipped rather than carried, because P8 verifies a citation by
resolving it. `text_span` is the observation's **own** span, `None` included, and explicitly not
derived from the truncated text: `records.py:400-421` records that the previously computed
`(0, len(text))` was "a span the observation never claimed" and that P7 refuses any other,
*after* the release is minted.

Three omission kinds are separate fields, never one (`dossier.py:17-20`, `records.py:465-475`):
budget-dropped, privacy-redacted, neighbourhood-capped. "Silence about a dropped file is the
failure, not the drop." `budget_cap_dropped` is empty by construction because **P9 runs no token
ladder** (`dossier.py:22-25`, `dossier.py:258-259`): it measures no tokens, summarises no fact,
drops no excerpt and splits no request. That ladder is P8's `run_call`.

`DossierRefused` (`dossier.py:62-68`) is returned — never a dossier with the reason missing —
when withholding leaves no anchor file, and it distinguishes the two causes: "every file
carrying direct evidence was withheld" versus "no file in the graph states the group's basis
directly" (`dossier.py:226-236`). The `dossier_id` **is** the fingerprint, a SHA-256 over the
assembled references excluding `created_at`, "or the same dossier assembled twice would be two"
(`dossier.py:142-163`).

### With no model configured

`p8_run_call=None` is a legal deterministic run, not an exception (`pipeline.py:18-21`,
`pipeline.py:521-531`). The pass returns a group with its memberships, the dossier, and
`not_implemented_reason = "no_model_call_configured"` — named rather than left blank because "a
candidate with no reason reads as a candidate nobody looked at, and this one was looked at and
deliberately not decided" (`pipeline.py:85-88`).

`ModelCallAuthorities` (`pipeline.py:90-121`) is the bundle of six authorities P9 forwards
without understanding. Every annotation is `object` because P9 may not import `CallDependencies`
or the privacy gate — a boundary test fails the build if any file under `src/grouping/` imports
either, since "an import is a second route to a model." The one file allowed to import
`llm_harness` is `p8_seam.py` (`p8_seam.py:172-175`).

Two fixes in that seam are worth naming because both made the first real group call impossible:
the request used to bind the privacy release to the **dossier's** fingerprint rather than the
prompt's, which the transport recomputes and refuses after the release is spent
(`p8_seam.py:159-179`, `pipeline.py:551-559`); and `model_target` used to be
`knowledge.retrieval.embedding_identity` — the local vector model — off which the gate reads
`.locality` to decide whether bytes may leave the machine (`pipeline.py:534-548`).

---

## 5.12 What the shipped deployment actually produces

Run on a three-file corpus (`Lecture 08.txt`, `Midterm Practice.txt`, `Syllabus.txt`, each
stating PHYS1401 / Columbia University / Spring 2026):

| Table | Rows | |
|---|---|---|
| `groups` | 2 | one P9 group `group:subject:0a1fcb6e…` (`supported`, `PHYS1401`, `academic`, `anchor_count=3`) and the CLI's merged review group |
| `memberships` | 6 | three `direct-anchor` on the P9 group, three carried onto the merged group |
| `group_edges` | 12 | 6 `shared-validated-fact`, 6 `existing-related-folder`, none suppressed |
| `group_dossiers` | 0 | assembled in memory, never persisted |
| `stop_rule_outcomes` | 0 | nothing writes this table |
| `group_failure_points` | 0 | |
| `group_acceptance` | 2 | |

The shipped limits (`cli.py:141-144`): `max_retrieved_neighbors=50`, `max_graph_nodes=10`,
`max_candidate_members=10`, `max_dossier_tokens=4000`, `generic_hub_frequency=9`,
`minimum_independent_anchors=1`, `max_excerpt_characters=240`. `config.py` ships no fallback for
any of them — "a fallback number would be P9 authoring a policy that belongs to configuration,
and the failure mode it hides is the worst kind — running with a limit nobody chose and no error
to say so" (`config.py:5-7`).

---

## What looks wrong here

Ordered by how much a real person would care.

**1. A second run over the same plan database crashes with an unhandled traceback.** Reproduced:

```
File "src/grouping/pipeline.py", line 503, in group_subject
    record_membership(conn, membership)
File "src/grouping/store.py", line 210, in record_membership
    raise MalformedGroupRecord
grouping.records.MalformedGroupRecord: membership group:subject:0a1fcb6e…:be7c64a7… is
already recorded with different content; a revision supersedes rather than replaces
```

`_self_membership` stamps `created_at` from `authorities.now()` (`production.py:583`), which is
a fresh clock on every run. `record_membership` compares the whole record for equality
(`store.py:209`) and the timestamps differ, so the rerun path at `pipeline.py:489-503` — the one
whose docstring is entirely about handling reruns gracefully — raises. The database path
defaults to `Path.cwd() / "database-agent-plan.sqlite"` (`cli.py:1050`), so this is the default
second invocation, not an exotic case. It escapes `cli.py`'s named-refusal handler
(`cli.py:1063-1071`), whose own comment says "A traceback here would turn an answer the design
worked hard to give into a crash."

**2. A user-created starting point always trips SR1 and produces no group at all.** A user seed
has `field_key = None` and `value = None` (`seeds.py:169-180`), so `_shared_fact_neighbors`
returns `[]` (`retrieval.py:179-180`), `seed_anchors` is false (`pipeline.py:422`), and
`anchoring_files` is empty — SR1 fires (`graph.py:302`). `group_subject` returns before
`record_group` and `record_membership`, so nothing is written. The SPEC calls this the only
channel user intent enters by, and `Membership.basis = user-attached` exists for it
(`vocabulary.py:53`) — nothing writes that value. The only pipeline-level test of a user seed
uses it *as the SR1 fixture*
(`tests/p9/test_p9_group_naming.py:548-563`).

**3. Nothing writes the `stop_rule_outcomes` table.** `record_stop_rule_outcome` (`store.py:346`)
has no caller in `src/`. `evaluate_stop_rules` returns an outcome that travels only in the
in-memory `GroupingResult`; the SR5 outcome built in `p8_seam.py:367-369` is likewise only
returned. Meanwhile `cli.py:296` reads `stop_rule_outcome_for`, which will always answer `None`.
This is the same defect class as `record_edges` — computed, decided on, dropped — and it was not
fixed alongside it. `Group.stop_rule_hits` is also always `()`; nothing ever sets it.

**4. `duplicate_or_version=None` is a crash, not an omission.** `graph.py:4-9` and
`graph.py:100-106` both say the channel is "omitted, never guessed" when the discriminator is
absent. But retrieval runs the family channel unconditionally (`retrieval.py:387-390` — there is
no check on `duplicate_or_version` anywhere in `retrieval.py`), and `_edge_type` then raises
`ConfigurationRequired` for the first such neighbour. The shipped CLI passes `None`
(`cli.py:755`). Any corpus containing a duplicate or version family will take down the whole
run. Nothing omits the channel; the code says it does.

**5. `_edge_support` constructs a `Support` with a value outside `SUPPORT_KINDS`.**
`p8_seam.py:280-291` passes `support_kind=edge.edge_type`, but `duplicate` and `version-family`
are edge types and not support kinds (`vocabulary.py:103-125`), and `Support.__post_init__`
checks against `SUPPORT_KINDS` (`records.py:120`). Confirmed:

```
Support(support_kind='duplicate', …) -> OutOfVocabulary
```

So every `accept_context_supported` verdict over a graph containing a duplicate or version edge
raises inside the write transaction. This is exactly the collision the vocabulary module warns
about twice (`vocabulary.py:4-7`) reappearing in the seam.

**6. `pre_model_signals` carries one of the five computations the SPEC names.** The contract
lists "independent anchor count for the same value; presence of a defining document type in the
neighbourhood; compatibility of work types and term evidence; detected conflicting codes;
suppressed generic hubs." `pipeline.py:292` writes `{"anchor_count": anchor_count}`. Similarly
`engine_flagged_outliers` is hardcoded `()` (`dossier.py:256`) and `outlier_flag` is always
`none` — §4.2's "pre-model outlier flagging" is not implemented, and its absence is not recorded
anywhere.

**7. `active_schema_for` and `signal_evaluator_for` are required and never called.**
`_require_knowledge` (`dossier.py:71-87`) refuses a dossier without them, with a strong argument
about not inventing a category — and then neither appears anywhere else in the module. They are
mandatory arguments with no reader.

**8. The dossier is never persisted.** `store.record_dossier` (`store.py:402`) has no P9 caller;
the `record_dossier` in `llm_harness/harness.py:290` is P8's own, with a different signature.
With `p8_run_call=None` the dossier is built, returned in an in-memory result, and dropped —
`group_dossiers` had 0 rows after the live run. `Group.dossier_id` is `None` on every path, as
are `llm_response_ref` and `validation_verdict_ref`.

**9. Three whole modules are inert.** `grouping/stage_output.py` (all three P2 emitters) has no
importer in `src/` — P9 emits no `stage_output` at all, so §8.5's separation of retrieval,
graph and grouping quality cannot be computed from a run. `grouping/failure_points.py` has no
importer either; the P8 seam writes failure points through `store.record_failure_point`
directly, bypassing `record_failure`'s stage check, so `LOGGED_STAGES` never runs.
`grouping/learning.py`'s `apply_review_action` — the entire P13 receiver — has no caller;
only `group_basis_key` is imported (`pipeline.py:55`). Smaller inert items:
`retrieval.DEFAULT_CHANNEL_ORDER`, `vocabulary.NON_ANCHORING_SUPPORT`,
`vocabulary.GROUP_STATES_AS_OF`, `vocabulary.SENSITIVE_PRESENT`, `vocabulary.RULES_AND_GRAPH`,
`vocabulary.UNRESOLVED` as a group state, `store.edges_for_group`, `store.stored_dossier`,
`store.current_membership`, `acceptance.membership_review_state_as_of`,
`limits.max_candidate_members` (read from a P1 ceiling, never enforced).

**10. The join depends on alphabetical field-key ordering being identical across files.**
`seeds_for_file` returns seeds sorted by `field_key:value_id` (`seeds.py:141-147`) and
`group_subject` takes `seeds[0]` and discards the rest (`pipeline.py:405`). Two files from the
same course will only land in the same group if their first-sorting anchor fact is the same
field. A file that also carries, say, a `course_code` fact seeds on `course_code` and forms a
separate group from its siblings, silently. Nothing records that the other seeds existed. The
same mechanism means a file with two validated values in one field contributes only whichever
`value_id` sorts first.

**11. The event and family seed reads bypass P6's three-way filter.** `_anchor_rows`
(`seeds.py:142`) reads `event_facts` and `family_facts`, which filter neither `active` nor
`superseded_by` (`facts/read_surface.py:284-305`), unlike `proposal_eligible`, whose docstring
records what happened the last time two reads in that module disagreed — "a replaced conclusion
reached P10's and P11's folder-proposal read, so a tree was proposed from stale truth"
(`facts/read_surface.py:161-165`). A superseded validated family fact can still start a group.

**12. The join makes the CLI's `anchor_count` triple.** `cli.py:458` sums
`result.group.anchor_count` over grouped results; three results now point at one group with
`anchor_count = 3`, so the merged review group records 9 for three files. Confirmed on the live
run. This is CLI code, not P9, but it is a direct and unnoticed consequence of the address
change.

**13. `minimum_independent_anchors=1` makes the "candidate below the bar" state unreachable in
the shipped deployment.** `pipeline.py:26-30` and `naming.py:19-23` both describe a group below
§4.9's bar staying `candidate` with all four naming fields blank, and call that "the SPEC's
`deferred` row and an honest thing for a deployment with no model to show." With the shipped
value of 1 (`cli.py:144`), every fact-backed seed clears it, so every group that forms at all is
`supported` and named by the engine. The honest state described at length is never produced.

**14. Two SPEC promises with no implementation and no marker.** §4.7's purpose packet
(`purpose` facet, purpose-coherence) appears nowhere in `src/grouping/`. §4.9's
"rare sensitive files may surface below a normal group-size threshold as protected records" has
no code: `sensitivity_state` is hardcoded `none` (`pipeline.py:309`) and there is no group-size
threshold anywhere. Both are listed in the SPEC's Done-means, not in its Deferred table.
