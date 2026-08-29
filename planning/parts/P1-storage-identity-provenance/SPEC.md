# P1 — Storage, identity, provenance

Owns: §0, §8.2; and, per resolution S5, two adjuncts over that substrate — the §8.7 learning-record
store (G3) and the §8.6 budget configuration object (G4)
Status: contract draft

## Purpose

P1 publishes the substrate every other part writes to. It answers three questions and nothing else:

1. **What is a file, and what makes it the same file?** Content hash is the stable identity of a file
   version; the path is mutable state with a history (§8.2).
2. **Where does the record of what happened live?** One append-only provenance log, `events`, holding
   every significant event affecting a file (§8.2).
3. **What happens when a later answer disagrees with an earlier one?** The earlier record is never
   overwritten. The newer one supersedes it, carrying the reason, and the resolver may mark the newer
   value preferred (§8.2).

Around those, §0 fixes the storage posture: the filesystem is the system of record, a local SQLite
database is the durable working memory, and the product owns no namespace and no proprietary format.

Resolutions S2 and S5 hang three stores off that substrate. None of them adds a fourth question —
each holds material another part computes, decides, or configures:

- **the §0 vector arrays** — P9 computes the embeddings, P1 stores them as compact local arrays,
  never a vector database (S2, G2);
- **the §8.7 learning-record store** — a scoped projection over `events.correction_scope`, reading
  corrections other parts author (S5, G3; Contract out §7);
- **the §8.6 budget configuration object** — the twelve configurable ceilings, held in one place and
  enforced by nobody here (S5, G4; Contract out §8).

P1 stores. P1 does not interpret. It defines no fact, no group, no destination, no sensitivity class,
and no template. It defines the tables those things are written into and the rules that keep their
history reconstructible.

## Design slice owned

### §0 — storage model and system of record

- **The filesystem is the system of record.** Every file stays a normal file in a normal directory
  legible to Finder, Spotlight, Dropbox, Time Machine, and shell tools. The agent does not own the
  namespace, create a virtual filesystem, or require a proprietary storage format (§0).
- **The database is rebuildable.** The product "can be rebuilt from the filesystem if necessary" (§0).
  No part may treat the database as the only copy of anything the filesystem holds.
- **One local SQLite database is the durable working memory** (§0). §0 names what it records: file
  identity, file state, extracted content, facets, evidence locations, structural relationships,
  destination nodes, taxonomy aliases, movement plans, user corrections, undo history. P1 owns the
  database itself and two of those tables (`files`, `events`); the remaining tables belong to the parts
  that own their design sections and live inside the same database.
- **SQLite is chosen for** fast local lookups, transactional updates, durable state, and easy
  inspection (§0). Those four properties are P1's obligation to preserve — in particular, no part may
  hold a long transaction that defeats "fast local lookups", and every mutation is transactional.
- **Vectors are stored separately as compact local arrays if embeddings are used** — explicitly *not*
  a vector database, which "would add complexity without material value at the initial scale" (§0).
  `files` and `events` hold no vectors. **P1 owns the array store; P9 computes the embeddings** (S2,
  G2). P1 stores an opaque array against the identity its computing part supplies — a content hash
  under R1 where the subject is a file version — and reads none of it: P1 defines no dimensionality,
  no model, and no similarity function, and performs no retrieval. §4.2's and §6.3's retrieval belong
  to P9 and P11. Embeddings stay out of the walking skeleton, which is deterministic by design (S2).

### §8.2 — file identity and provenance

- **Identity is separated from pathname** (§8.2). A path changes on rename, move, cloud sync, backup
  restore, cross-volume copy, or user reorganization outside the product. None of those events change
  what the file *is*.
- **The content hash is the stable identity of a file version** — "the durable fingerprint of a
  byte-identical object" (§8.2).
- **Same content at a new path ⇒ the same file version** (§8.2).
- **Same name, changed content hash ⇒ a new version, and the relevant extractors re-run** (§8.2).
- **Every significant event is preserved in an append-only provenance log** (§8.2), with an enumerated
  event vocabulary and an enumerated event record (both reproduced under Contract out).
- **Supersede, never overwrite** (§8.2): "The product must never overwrite the evidence record merely
  because a later extractor or model produces a different answer." Both the failed first OCR pass and
  the later successful one remain available; a user reviewing a placement can still inspect the origin
  of the conclusion.
- **The file record retains at least thirteen named items** (§8.2), reproduced under Contract out.
- **Checksums are verified at four high-value transition points** (§8.2), establishing *file fixity* —
  the ability to show that a file at its destination is byte-identical to the file it intended to move.

## Contract in

P1 is the first part in wave 1 and consumes no other part's output. It consumes the filesystem and it
accepts writes. Everything below is a boundary declaration: a column P1 stores but whose *values* and
*vocabulary* belong to another part.

| From | What P1 receives | Owner's § | P1's obligation |
|---|---|---|---|
| P3 (scan) | a path, its stat result (size, timestamps), its bytes to hash, and the §1.2 per-file fields — filename, normalized filename, extension, MIME type, parent-folder context (§1.2's "directory position", renamed to §2.9's spelling — MINOR 11), scan state | §1.1, §1.2 | store them; **accept** the `discovery`, `stat observation`, `hashing` and `external modification detection` events **P3 authors** (M8) — P1 originates none of them |
| P5 (extractors) | `extraction status by extractor tier`; §3.4's analysis-tier vocabulary | §2.x, §3.4 | store the status opaquely; P1 defines no tier names |
| P7 (privacy) | `sensitivity state` — one of §8.4's five handling classes | §8.4 | store the class opaquely; P1 defines no class names and enforces no policy |
| P9 (grouping) | computed embedding arrays | §0, §4.2 | store as compact local arrays (S2); P1 reads no vector and computes no similarity |
| P13 (review surface) | appends of the three event types P13 declares — `review presentation`, `review action routed`, `apply review approval` — each carrying §8.2's eleven fields, and `correction_scope` on every collected gesture | §8.2, §8.3, §8.4, §8.7 (S4, B5) | validate them against the registered union (Contract out §3, where P13's declaration is recorded) and append; P1 stores no meaning for any of the three |
| every part | event appends through P1's writer, each event type declared by the part that **authors** it | §8.2 (B5, M8) | append; never update; never delete; validate the type against the registered union |
| P4, P6, P9, P11 | records that adopt P1's supersede columns | §2.8, §3.12, §4, §6.11 | publish the columns and the never-overwrite rule; the owning part decides *when* a record is superseded |
| P6, P7, P9, P10, P11 | user-action events carrying `correction_scope` | §8.7 | project them into the learning-record store (Contract out §7); P1 weights and generalizes nothing |
| P13 (review surface) | P13's `review_action` record — the `correction_scope` chosen at collection time on every gesture, and the learning-preference resets that arrive as `surface = learning` with `action = reset_learning` | §8.7 (S4) | project and reset as above; P13 collects the scope, the acting part authors the correction (M8), P1 weights and generalizes nothing |

P1 validates the *shape* of what it is given (required columns present, event type in the **registered
union** per Contract out §3, hash present and matching its declared algorithm). It does not validate
the *semantics* of another part's vocabulary. Whether it should beyond the event type is unstated —
see Open questions.

**Fixture requirement for neighbours building before P1 exists.** A neighbour can stand up against a
two-table fixture: `files` with the columns below and `events` as an append-only list. The only
behaviours a neighbour may assume are the six identity rules (R1–R6) and the four verification points
(V1–V4) in Contract out. Nothing else about P1's internals is contract.

## Contract out

### 1. Identity rules

- **R1** The content hash is the stable identity of a file *version* (§8.2).
- **R2** The same content observed at a new path is the same file version (§8.2).
- **R3** A file whose content hash changes is a new version; P1 records the change and marks the file's
  extraction state invalid so the relevant extractors re-run (§8.2). P1 does not run them — that is P5.
- **R4** The file record's identity is not its path. Path is mutable state; path history is retained
  (§8.2).
- **R5** P1 supplies the identity half of §3.4's cache key — content hash. The remaining components
  (extractor version, analysis tier, model identifier, prompt fingerprint) are supplied by their owners;
  P1 stores the fingerprint on the event but does not compute or interpret it (§3.4, §8.2).
- **R6** Nothing in `events` is ever updated or deleted (§8.2).

### 2. `files`

The union of §8.2's file-record list and §1.2's per-file record. §8.2 says "at least the following", so
the union is permitted. Every column cites the § that requires it. Columns marked *(mechanics)* are
shape, not design content.

```text
file_id                     Internal file ID                                 §8.2
current_path                Current path                                     §8.2, §1.2 "path"
filename                                                                     §1.2
normalized_filename                                                          §1.2
extension                                                                    §1.2
directory_position          storage name for §2.9's parent-folder context    §1.2, §2.9
volume_id                   Filesystem volume or root identifier             §8.2
content_hash                Content hash                                     §8.2, §1.2
hash_algorithm              …and hash algorithm                              §8.2
observed_size               Observed size                                    §8.2, §1.2 "size"
observed_timestamps         …and timestamps                                  §8.2, §1.2
mime_type                   MIME type                                        §8.2, §1.2
detected_format             …and detected format                             §8.2, §2.9 file signature
scan_state                                                                   §1.2
extraction_status_by_tier   Extraction status by extractor tier              §8.2 (tiers: P5, §3.4)
sensitivity_state           Sensitivity state                                §8.2 (classes: P7, §8.4)
```

**`directory_position` is a deliberate storage-name divergence, not a second field** (MINOR 11).
§2.9's "parent-folder context" is the published name of the field, and it is the name P1 receives it
under (Contract in) and the name every other part uses. P1 keeps `directory_position` — §1.2's own
word — as the physical column spelling only. There is exactly one field; a part that finds both names
in a contract has found a defect, not two columns.

The remaining five items in §8.2's file-record list are **histories, not columns**. P1 satisfies
"the file record should retain" by guaranteeing they are retained and reachable from `file_id`, under
supersede-never-overwrite, through published read surfaces:

```text
file_path_history(file_id)          -> ordered (path, volume_id, observed_at, event_id)
                                       Path history §8.2; projection over events, which carry
                                       "old and new paths where applicable" and "time of observation" §8.2
file_facts_history(file_id)         -> current + historical file facts        §8.2; rows owned by P6 §3.12
group_memberships_history(file_id)  -> current + historical group memberships §8.2; rows owned by P9 §4
placement_history(file_id)          -> current + historical placement proposals §8.2; rows owned by P11 §6.11
user_decisions_history(file_id)     -> current + historical user decisions     §8.2; projection over events
                                       carrying user identity §8.2
```

Whether §8.2 intends these physically on the file record rather than as projections is unsettled — see
Open questions. Consumers see the read surface either way; materialization is not contract.

### 3. `events` — the append-only provenance log

```text
event_id            monotonic ordering key                          (mechanics)
event_type          a reserved §8.2 name, or a type registered by
                    its authoring part                              §8.2, B5
file_id             file ID                                         §8.2
content_hash        content hash                                    §8.2
old_path            old path where applicable                       §8.2
new_path            new path where applicable                       §8.2
subsystem           the responsible subsystem                       §8.2
component_version   extractor or model version                      §8.2
prompt_fingerprint  prompt fingerprint where applicable             §8.2, cf §3.4
user_id             user identity when there is an explicit
                    user action — nullable, populated only then     §8.2, MINOR 10
observed_at         time of observation                             §8.2
explanation         a structured explanation or evidence reference  §8.2
correction_scope    file | group | node | template | domain |
                    corpus — on user-action events only             §8.7 (see Cross-cutting answers)
```

**Event vocabulary (§8.2, nineteen types, verbatim from the design's list):**

```text
discovery                        template application
stat observation                 destination-tree edit
hashing                          placement recommendation
extraction                       filename-collision resolution
OCR                              planned move
fact creation                    executed move
fact rejection                   failed move
graph-edge creation              external modification detection
group membership proposal        undo
user group decision
```

§8.2 introduces this list with "This includes", so nineteen is a **floor, not a ceiling** (B5). P1
therefore publishes a **registration rule** in place of a closed set:

1. The nineteen §8.2 names above are **reserved**. No part may redefine one, narrow it, or reuse the
   name for a different act.
2. **Every other event type is declared by the part that authors it, in that part's own SPEC.** The
   declaration is the definition; P1 stores no meaning for it and validates no semantics.
3. P1's writer validates `event_type` against the **union** of the reserved nineteen and every
   registered declaration. An unregistered type is rejected at the writer, never silently stored.
4. Registration is a spec-level act, not a runtime one: a type declared in no SPEC does not exist, and
   a part cannot mint one at run time.

Registered as of this revision. The names live in the declaring spec, not here — this table records
that the declaration exists and how it relates to the reserved nineteen:

| Declaring part | Count | Form |
|---|---|---|
| P7 (§8.4) | 8 | new types: classification assignment and supersession, policy, consent, model release and denial |
| P8 (§3.6, §8.4) | 5 | new types: model call, response, validation verdict, verdict supersession, refusal |
| P11 (§6.11, §7) | 8 | **typed specializations of the reserved `placement recommendation`** (B5) — each carries `placement recommendation` as its base type plus P11's specialization tag; none is free text and none shadows a reserved name |
| P13 (§6.11, §7.5, §8.3) | 3 | new types: `review presentation`, `review action routed`, `apply review approval` — the review surface's own acts (S4). None shadows a reserved name: P13 records that a record was rendered, that a gesture was collected and where it was routed, and that §8.3's required-review policy was satisfied, rejected, deferred or found to need a refresh. The **decisions** those gestures produce are authored by the acting part (M8), which is why none of the three is a `user group decision`, a `destination-tree edit` or a `placement recommendation` |

P3's `discovery` / `stat observation` / `hashing` and P12's six are **not** registrations. They are
reserved names, authored by those parts (M8) — see Cross-cutting answers → Provenance.

**Twenty-four registered types across four parts** — P7's eight, P8's five, P11's eight and P13's
three. The writer's union is those twenty-four plus the reserved nineteen; anything else is rejected
(rule 3).

**Append-only means:** `INSERT` only. No `UPDATE`, no `DELETE`, no row rewrite, no truncation, no
compaction that drops rows (§8.2). A correction to an event is a new event, not an edit.

### 4. Supersede-never-overwrite

§8.2 requires three things of a superseding result: the old observation is retained, the reason it was
superseded is recorded, and the resolver may mark the newer value as preferred. P1 publishes four
column names so that no part re-spells them (M1). **Three are the shared set every superseding record
type adopts** — P4's evidence records (§2.8), P6's facts (§3.12, §3.13), P9's memberships (§4), P11's
placement proposals (§6.11):

```text
supersedes         id of the record this one replaces               §8.2
superseded_by      inverse link; the old row stays readable         §8.2 "retaining the old observation"
supersede_reason   why it was superseded                            §8.2 "and the reason it was superseded"
```

The spelling is `supersede_reason`. `supersession_reason` is not an alias and is not accepted (M1).

The fourth is **not** in the shared set:

```text
preferred          the resolver's chosen value in this chain        §8.2 "may mark the newer value as preferred"
                   carried on P6's `file_facts` only                M1
```

**`preferred` sits on the resolver's record, not on the observation** (M1). §8.2 says the resolver
*may* mark the newer value, and §3.2 places the resolver after extraction — so the observation layer
records what was read and what superseded it, and nothing about which one wins. P4 does not carry it;
P6 does. P1 publishes the name and the rules below so that the resolver's column means the same thing
wherever it is read.

Rules: at most one record per supersede chain carries `preferred`; a superseded row is never deleted
and never mutated; the newest record is not automatically preferred — §8.2 says the resolver *may*
mark it, so preference is an explicit act. §8.2's worked case is normative: a first OCR pass that
produces unreadable text and a later engine that recovers a university name must **both** remain
available.

### 5. Checksum verification points (§8.2)

P1 publishes `verify_content(file_id, expected_hash) -> match | mismatch`, called at exactly the four
points §8.2 names. **P12 (§8.3) is the only caller** (MINOR 5) — §6 decides where a file should go and
never touches bytes, so P11 calls nothing here; fixity belongs to P12 alone, plus P1's own writes. P1
performs and records, and decides nothing about what a mismatch means.

```text
V1  before preparing a filesystem action                    §8.2
V2  immediately before executing a move or copy             §8.2
V3  after completing the action                             §8.2
V4  cross-volume copy-and-delete: the destination copy is hashed and confirmed
    before the source may be removed                        §8.2
```

Together these establish **file fixity** (§8.2). The consequence P12 depends on: §8.3's staleness rule
("if its content hash differs … the action should be marked stale") is evaluated against V1/V2, and
§8.3's undo precondition ("the file at the destination is still the expected content") against V3.
P1 guarantees the hash comparison; P12 owns the stale/undo decisions.

### 6. Database handle

One local SQLite database (§0), transactional, durably committed, inspectable. P1 publishes the handle
and the transaction boundary; each part owns its own tables within it.

### 7. The §8.7 learning-record store (S5, G3)

A **scoped projection over `events`**, not a new authority and not a second log. §8.7 requires that
user actions "become local learning records **with scope**", and P1 already carries `correction_scope`
on every user-action event, so the store is a read surface over material that exists.

```text
learning_records(scope, subject_id)  -> the user-action events at that scope for that subject,
                                        newest first, each with its §8.2 `explanation`,
                                        `polarity`, `proposal_class`, `basis_key`, and
                                        evidence reference                                 §8.7
reset_preferences(scope, subject_id) -> appends a scoped reset record; deletes nothing     §8.7, R6
```

User-action events carry three opaque fields the acting part supplies and P1 does not interpret
(`polarity`, `proposal_class` and `basis_key`). `polarity ∈ accept | reject` is what makes §8.7's
"rejected groups, rejected destination matches, rejected labels, and rejected residual
recommendations" distinguishable from approvals on read — without it every query-before-propose
reader would have to parse `explanation` free text to tell an approval from a rejection. P1 stores
and returns all three and decides nothing from them. Vocabulary and equivalence are
[`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md).

- **Scope is the filter, and it is exact.** §8.7's six scopes are file / group / destination node /
  template / domain / corpus. A `file`-scoped correction is never returned by a `corpus`-scoped read.
  §8.7's worked case is the reason: one transcript belonging in a Columbia packet "should not teach the
  engine that all transcripts belong there."
- **Negative feedback comes back with its evidence.** §8.7 requires rejected groups, destination
  matches, labels, and residual recommendations to be "stored with the evidence that produced them."
  Because `events` is append-only and rejections supersede rather than delete, both the rejection and
  its evidence reference survive permanently, and the store returns them together.
- **Reset is append-only.** §8.7 requires the user be able to "inspect or reset learned preferences."
  Reset appends a scoped reset record that later reads honour; it never deletes an event (R6), so the
  history of what was learned and un-learned stays inspectable.
- **Who reads.** **P13** is the inspect/reset surface (S4): it renders this projection and collects
  `reset_learning`. **P6, P7, P8, P9, P10 and P11 query before they propose** — that is the half §8.7
  requires and that was previously only implied. P13 applies no learning and P1 applies none either.
  Query-before-propose, `proposal_class`, and `basis_key` are specified in
  [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md). Acceptance is per plan version (M15);
  this store is versionless, which is why SR6 cannot be a read of current-version acceptance alone.
- **P1 does not learn.** No weighting, no generalization, no ranking, no application. What a record
  means is decided by the part that authored the correction — P6, P7, P9, P10, P11. §8.7's ban on
  silent global training is satisfied structurally: the store is one local table inside the one SQLite
  database (§0), and P1 exports nothing.

### 8. The §8.6 budget configuration object (S5, G4)

One configuration object holding §8.6's twelve configurable ceilings — fifteen keys, because three of
the twelve are held by two parts on different graphs and are namespaced accordingly (O10). P1 **holds
and publishes values; P1 enforces none of them.** Enforcement belongs to the part that owns the
bounded operation, and each such part names the ceilings it enforces in its own SPEC (for the model
ceilings, O8 and O9 put that at P8 as the single egress point).

```text
ocr.max_pages_per_file                    Maximum pages OCRed per file                        §8.6
ocr.max_time_per_file                     Maximum OCR time per file                           §8.6
ocr.max_time_per_scan                     Maximum OCR time per scan                           §8.6
image.max_analysis_ops_per_scan           Maximum image-analysis operations per scan          §8.6
model.max_llm_calls_per_thousand_files    Maximum LLM calls per thousand files                §8.6
model.max_cost_per_scan                   Maximum model cost per scan                         §8.6
model.max_dossier_tokens_per_call         Maximum dossier tokens per model call               §8.6
grouping.max_retrieved_neighbors          Maximum retrieved neighbors per target file  (§4.2) §8.6, O10
placement.max_retrieved_neighbors         Maximum retrieved neighbors per target file  (§6.3) §8.6, O10
grouping.max_local_graph_neighborhood     Maximum local graph neighborhood size        (§4.2) §8.6, O10
placement.max_local_graph_neighborhood    Maximum local graph neighborhood size        (§6.4) §8.6, O10
grouping.max_candidate_cluster_size       Maximum candidate cluster size               (§4.2) §8.6, O10
placement.max_candidate_cluster_size      Maximum candidate cluster size               (§6.5) §8.6, O10
residual.max_files_per_review_batch       Maximum residual files in one review batch          §8.6
tree.max_folder_proposals_and_depth       Maximum folder proposals and maximum depth          §8.6
```

- **Three ceilings are namespaced because two parts legitimately hold them on different graphs**
  (O10): P9's grouping neighbourhood (§4.2) and P11's node-local graph (§6.4) are not the same graph,
  so one number for both would be wrong in one of the two places. The remaining nine have a single
  owner and keep §8.6's wording unmodified.
- **Values are configuration, not contract.** P1 stores defaults and user overrides and versions the
  object so a replay can pin the values it ran under (§8.5); it proposes no default here.
- **The object is shared across plan versions**, like the rest of P1's state. §8.8's list of what a
  plan version captures names no ceiling — see Cross-cutting answers → Plan versioning.
- **Reading a ceiling is not enforcing it.** §8.6's closing constraint — "cost exhaustion must never
  turn into lower-quality automatic classification" — binds the enforcing parts, and P1's own form of
  it (budget pressure never weakens a fixity check) is unchanged by holding the values.

### 9. Vector array store (S2, G2)

```text
put_embedding(subject_key, array, producer_version)   store an opaque compact local array   §0
get_embedding(subject_key)                            return it unchanged                   §0
```

§0's exact posture: "store vectors separately as compact local arrays if embeddings are used", never a
vector database. P9 computes; P1 stores and returns bytes. P1 exposes no similarity function, no index,
and no nearest-neighbour query — retrieval over these arrays is P9's (§4.2) and P11's (§6.3). `files`
and `events` hold no vectors.

### 10. The §8.6 per-scan resource observability record (D1)

§8.6's first sentence names six resources: *"Every scan should have an observable budget for **elapsed
time, memory, CPU or accelerator usage, storage, network use, and LLM cost**."* Storage was already
P1's (Cross-cutting answers → Budgets) and LLM cost is P8's to measure as the single egress point (O9),
but the other four had no home, so a scan could not be shown at all. **P1 records all six**, because P1
is the part every other part already writes through and already holds the one object that spans every
part's bounded work (§8). P13 renders them — §8.6's second sentence, *"the user should be able to see
what is running, what has been deferred, and why"*, is P13's `progress_line`, which carries file counts
and now has a typed resource record to read beside them.

```text
scan_resource_usage(scan_id) -> one row per scan, updated as the scan runs

scan_id            the scan these counters belong to                          (mechanics)
elapsed_time       wall-clock since the scan began                            §8.6
memory             process memory, peak and current                           §8.6
cpu_accelerator    CPU and accelerator time consumed                          §8.6
storage            database, log, and derived-artifact bytes                   §8.6
network            bytes sent and received                                    §8.6
llm_cost           supplied by P8, the single egress point (O9)               §8.6
observed_at        time of observation                                        §8.2
```

- **Recording is not bounding.** §8.6 names a configurable ceiling for **none** of these six. P1 holds
  no threshold for any of them, rejects no operation for any value, and invents none — the twelve
  ceilings in Contract out §8 are a separate and unrelated set. This section adds observability only,
  which is exactly what §8.6's first sentence asks for and all it asks for.
- **Who supplies what.** P1 samples `elapsed_time`, `memory`, `cpu_accelerator`, `network` and its own
  `storage` at the process level; `llm_cost` is written by P8, which is the only part that can know it
  (O9). P1 interprets none of the six and derives no quality signal from any of them.
- **`scan_id` is local to this record.** §8.6 says *"every scan"*, so the counters need a scan identity
  and no part publishes one; P1 mints it here. It is **not** added to `events` — §8.2's event record
  keeps its eleven fields (MINOR 1) and Done-means 7 still tests exactly eleven. Whether a scan
  identifier should be published as shared identity is an Open question, not a decision taken here.
- **Absence reads as unknown, never as zero.** A counter that could not be sampled is recorded as
  unavailable. §8.6's whole purpose is that deferred and unmeasured work stay visible as such rather
  than reading as work that completed cheaply.
- **Versionless, like the rest of P1's state.** §8.8's list of what a plan version captures names no
  resource counter (Plan versioning, below).

## Deferred — manual design required

**P1 owns no hand-authored content.** Every list in §0 and §8.2 is fully enumerated in the design:
nineteen event types, eleven event-record fields, thirteen file-record items, four verification points.
There is no library, gazetteer, or template set inside this part's slice. The one thing P1 now holds
that the design does not enumerate is the **values** of §8.6's ceilings — "configurable" is all §8.6
says — and those are deferred below rather than guessed.

What P1 must nonetheless *carry without containing* — deferred to the parts and § that define them:

| Deferred content | Defined by | Carried by P1 as |
|---|---|---|
| The 200–300 domain template library | §5.7 (P10) | `template application` events (§8.2) for templates P1 does not define |
| Domain fact-schema fields beyond the six domains and fields §3.11 literally tabulates | §3.11 (P6) | `file_facts_history` read surface over P6's rows; P1 defines no field |
| Gazetteer contents (the validated gazetteers §3.7 requires) | §3.7 (P6) | nothing — P1 stores no gazetteer |
| Residual library contents beyond the nine templates §7.3 names | §7.2, §7.3 (P10 — M10 moved the definitions there; P11 keeps the §7.5–§7.11 workflow) | `placement recommendation` events (§8.2) naming nodes P1 does not define |
| The five sensitivity handling classes' detection rules | §8.4 (P7) | an opaque `sensitivity_state` value |
| Analysis-tier names | §3.4, §2.x (P5) — **I4 closed the names** as `filesystem \| native \| ocr \| llm` | an opaque `extraction_status_by_tier` map whose keys are those four; P1 still does not interpret completeness |
| The **values** of §8.6's ceilings | §8.6 says only "configurable" — hand-authored, with the enforcing parts | keys in the budget configuration object (Contract out §8); P1 stores whatever is set and proposes no default |

P1 invents none of these and must not be blocked on any of them: the substrate is buildable and
testable with every one of these vocabularies empty.

## Done means

Each item is a check runnable against P1 alone, with fixtures, before any neighbour exists.

1. **Record creation.** Given a path, P1 computes a content hash, records the algorithm alongside it,
   records the volume identifier, and writes a `files` row carrying every column above. The
   accompanying `discovery` event is appended **through P1's writer by its author** — P3 in the
   running system (M8), a fixture in this check (§8.2; walking-skeleton step P1).
2. **Path-change identity.** The same bytes presented at a second path resolve to the same file
   version — R2/§8.2 — and the path change is visible in `file_path_history`.
3. **Content-change identity.** The same path with different bytes is recorded as a new version and
   the file's extraction state is marked invalid so the relevant extractors re-run (R3/§8.2). Verified
   without P5 present, by asserting the invalidation state.
4. **Append-only enforcement.** `UPDATE` and `DELETE` against `events` fail. Asserted, not asserted-by-
   convention (§8.2).
5. **Supersede.** Superseding a record leaves the old row readable, populates `supersede_reason`, and
   leaves `preferred` unset unless explicitly set. The §8.2 OCR case is the fixture: two extraction
   records for one file, both retrievable, the later one markable as preferred (§8.2).
6. **Verification points.** V1–V4 are callable and return match/mismatch; V4 refuses to report success
   until the destination copy's hash is confirmed (§8.2).
7. **Event completeness.** Every event row carries the eleven §8.2 fields, with the "where applicable"
   fields (`old_path`, `new_path`, `prompt_fingerprint`, `user_id`) legitimately empty and every other
   field populated (§8.2).
8. **No interpretation leaked.** P1's code contains no field name, domain name, template name,
   sensitivity class, or tier name (§3.11, §5.7, §7.3, §8.4 belong elsewhere). Checkable by grep. The
   §8.6 ceiling keys and the nineteen reserved event names are not exceptions — both are §0/§8.2/§8.6
   vocabulary the design states literally, and neither names a fact, a domain, or a class.
9. **Storage posture.** No vectors in `files` or `events` (§0). One database file, transactional.
10. **Skeleton participation.** The walking skeleton's P1 step — hash, create the file record, append a
    discovery event — passes, and P12's step reaches P1's V1–V4 and gets true answers.
11. **Event registration.** The writer accepts a type declared by another part's SPEC — the fixture is
    P13's `apply review approval` (Contract out §3) — rejects an undeclared type, and rejects an
    attempt to redefine one of the nineteen reserved names. A P11 specialization is stored with
    `placement recommendation` as its base type (B5, §8.2).
12. **Multi-author types.** Two parts append `external modification detection` for the same file; both
    rows survive, carry different `subsystem` values, and are separable by `subsystem` (M8, §8.2).
13. **Learning projection.** A `file`-scoped user-action event is not returned by a `corpus`-scoped
    read; a rejection is returned together with the evidence reference that produced it; a reset
    appends and deletes nothing, and the pre-reset records stay readable (§8.7, R6).
14. **Budget configuration.** All fifteen keys are readable, `grouping.*` and `placement.*` resolve to
    independent values, and P1 rejects no operation for exceeding any of them — enforcement is
    elsewhere (§8.6, G4, O10).
15. **Vector arrays.** An array supplied by P9 round-trips byte-identically, is stored outside `files`
    and `events`, and P1 exposes no similarity or nearest-neighbour call (§0, S2).
16. **Per-scan resource observability.** A completed scan yields one `scan_resource_usage` row carrying
    all six §8.6 resources, with `llm_cost` written by P8 and the other five sampled by P1. A resource
    that could not be sampled reads as unavailable, never as `0`. **Negative tests:** P1 rejects no
    operation and defers no work for any value of any of the six — there is no threshold to hit; and the
    `events` record still carries exactly eleven fields, `scan_id` among none of them (§8.6, D1,
    MINOR 1).

## Cross-cutting answers

### Provenance (§8.2)

P1 owns the log, so the answer has two halves — but under M8 the halves are **writer** and **author**,
not "P1's types" and "everyone else's". **The acting part authors; P1 writes.** P1 appends no event on
its own initiative, and its "accepts from others" list is now the whole vocabulary.

**Authorship of the nineteen reserved types** (§8.2), every one written through P1's append-only
writer:

| Reserved type | Author |
|---|---|
| discovery, stat observation, hashing | **P3** (§1.1, §1.2) — M8; see the V1–V4 note below |
| extraction, OCR | P5 (§2.x) |
| fact creation, fact rejection | P6 (§3.x) |
| graph-edge creation, group membership proposal, user group decision | P9 (§4) |
| template application, destination-tree edit | P10 (§5) |
| placement recommendation | P11 (§6.11), with P11's eight typed specializations (Contract out §3) |
| filename-collision resolution, planned move, executed move, failed move, undo | **P12** (§8.3) — M8 |
| external modification detection | **two authors: P12** (§8.3 staleness triggers and sync conflicts) **and P3** (§1.2 re-scan) — M8 |

**Authorship of the twenty-four registered types** is the declaring part's, by rule 2 of the
registration rule: P7's eight, P8's five, P11's eight and **P13's three** (Contract out §3). P13 is
the fourth part that appends through this writer under a declaration of its own; its three types
record what was rendered, what gesture was collected and where it was routed, and whether §8.3's
required review was satisfied — never the decision itself, which the acting part authors (M8).

**A type may have more than one author.** §8.2 assigns authorship to nobody, and `external
modification detection` is reached by two independent routes the design names separately, so P1's
framing admits several authors per type rather than forcing one of them to give up the name. The
writer records the author on `subsystem` (§8.2), so two authors of one type stay distinguishable row
by row and a consumer that needs one author's rows filters on `subsystem`, never on `event_type`
alone.

**V1–V4 hashing.** P1 performs the four checksum verifications (§8.2) when a caller asks for one; the
`hashing` event for a verification is authored by the calling part — P12 (§8.3), the only caller of
V1–V4 (MINOR 5) — with `subsystem` naming P1 as the performer. P3 authors scan-time `hashing` (§1.2).
P1's act is the comparison; the decision that a verification was due is never P1's.

**What P1 never overwrites:** any row in `events`; any superseded record in any table adopting the
supersede columns; any prior path in `file_path_history`; any prior content hash. §8.2's rule is
absolute — a later extractor or model producing a different answer is never grounds to overwrite. The
only mutable state in P1 is the *current* projection on `files` (current path, current hash, current
scan/extraction/sensitivity state), and no mutation of it is accepted without the authoring part's
event explaining it.

### Budgets and degradation (§8.6)

§8.6 defines twelve configurable ceilings and **none of them applies to storage, hashing, or the log**.
P1's honest position:

- **P1 holds the configuration object; P1 enforces nothing** (S5, G4). The twelve ceilings live in
  P1's store (Contract out §8) precisely because they belong to no single consumer. Holding the values
  gives P1 no ceiling of its own and no say in what any part does when one is reached.
- **Observability P1 owns:** §8.6's first sentence — *"every scan should have an observable budget for
  elapsed time, memory, CPU or accelerator usage, storage, network use, and LLM cost"* — is recorded in
  full by P1 as `scan_resource_usage` (Contract out §10, D1). Storage was always P1's; the other five
  had no owner, and an unowned counter is an unshowable scan. P1 reports the row to the UI surface §8.6
  requires ("the user should be able to see what is running, what has been deferred, and why"), which is
  P13. **Recording six counters gives P1 no ceiling on any of them** — §8.6 names none, and P1 invents
  none.
- **P1 imposes no ceiling of its own** on hashing time or per-file size, because §8.6 names none.
  Whether one is required for very large files is an Open question, not a decision P1 makes here.
- **On exhaustion:** P1 never drops, truncates, or compacts `events`, and never omits a hash to save
  work. A file whose hashing is deferred is recorded as *deferred*, never as unchanged or assumed —
  §8.6: "retain extracted evidence, mark the deferred stage, and leave the file or group in review
  rather than guessing." An absent hash must never read as a hash match anywhere in the system;
  V1–V4 return *mismatch* on an unknown hash, never *match*.
- §8.6's closing constraint — "cost exhaustion must never turn into lower-quality automatic
  classification" — has a P1-specific form: **budget pressure must never weaken a fixity check.** A
  move never proceeds on an unverified hash because verification was too expensive.

### Correction learning (§8.7)

**P1 records no correction of its own.** §0 and §8.2 contain no user-facing decision — nothing in the
identity or provenance layer is a thing a user corrects. §8.7's enumerated actions (accepting or
rejecting a group, renaming a branch, changing template order, moving a residual file, marking a file
private, disabling a suggestion type) all belong to P6, P7, P9, P10, and P11.

**P1's obligation is to make those parts' corrections durable and scoped.** Two guarantees:

1. Every event carrying an explicit user action carries `user_id` (§8.2) and `correction_scope` — one
   of §8.7's six scopes: **file / group / destination node / template / domain / corpus**. §8.7's
   worked case is why the scope column exists: one transcript belonging in a Columbia packet must not
   teach the engine that all transcripts belong there.
2. **Negative feedback is stored with its evidence.** §8.7: rejected groups, destination matches,
   labels, and residual recommendations "must be stored with the evidence that produced them.
   Otherwise the system will repeatedly resurface the same attractive but incorrect grouping." Because
   `events` is append-only and rejections supersede rather than delete, a rejection and the evidence
   reference that produced it both survive permanently. This is what makes §8.7's "inspect or reset
   learned preferences" possible.

P1 stores; it does not weight, generalize, or learn. **P1 owns §8.7's learning-record store** (S5, G3)
— as a scoped projection over `events.correction_scope`, specified in Contract out §7. Owning the
store changes nothing about that sentence: the projection reads corrections other parts authored and
returns them with their evidence; what any record *means* is decided by the part that authored it.

### Plan versioning (§8.8)

**None of P1's state belongs to a plan version.** §8.8 is explicit: "The evidence database remains
shared across plan versions, but the destination tree and user policy define which projections are
valid in each version." `files`, `events`, content hashes, path history, and the supersede chains are
that shared evidence database. They are versionless by design and survive every plan version, plan
diff, plan restore, and plan adoption.

Cross-checked against §8.8's own list of what a plan version captures — plan ID and version, tree and
node identifiers, node provenance categories, template versions and ordering, accepted and rejected
group memberships, labels and aliases, residual-library configuration, privacy and consent policies,
placement policy, associated review decisions — **not one item is P1-owned**.

**The three adjunct stores are shared too.** The learning-record store is a projection over `events`,
which is versionless, and §8.7's scopes (file / group / node / template / domain / corpus) are not plan
scopes — a correction the user made under plan v1 is still a correction the user made. The vector
arrays are keyed on content identity, which does not change with a plan. The budget configuration
object holds §8.6's ceilings, and §8.8's list names no ceiling. One caveat is recorded as an Open
question: §8.8 does capture "placement policy settings", and `tree.max_folder_proposals_and_depth`
sits close to that boundary.

Two obligations follow:

- **P1 must not become plan-scoped.** No part may add a `plan_version` to `files` or partition `events`
  by plan. Doing so breaks §8.8's guarantee that a new plan "should never silently reclassify or move
  old files" — that guarantee depends on the evidence being the same evidence across versions.
- **P1 must make plan diffs computable.** §8.8's diff needs to state that "twenty-three files now
  require renewed review because their previous destination no longer exists." That count is derived
  from `placement recommendation` events and `files`, which survive across versions precisely because
  they are not versioned.

## Open questions

Ordered by how far the consequences travel. Settled entries keep their original numbers so that
existing citations (`P1 OQ5`, `P1 OQ7`, `P1 OQ8`, `P1 OQ14`) still resolve, and record what settled
them; the rest are unanswered here.

1. **Settled — ratified 2026-08-19 (I1). A content change creates a NEW `files` row.** §8.2's "a new
   version" is taken literally: `file_id` is version-scoped, and every foreign key to it is
   version-scoped with it. The prior row is retained with `scan_state = 'superseded_content'` and its
   extraction state invalidated (R3), so the previous version's facts and evidence continue to point
   at a row that still describes them. *Consumers affected:* P5 (§3.4's per-content-hash cache), P6
   (§3.12), P11, P12.
2. **Settled — ratified 2026-08-19 (I1). Two records sharing a hash.** Two simultaneously live copies
   are two `files` rows with the same `content_hash` and different `file_id` and `current_path`. The
   one-record reading is rejected because §2.9's "duplicate family" has nothing to detect if
   duplicates collapse, and §8.3's collision policy — two files whose "hashes prove the files are
   identical" — presumes both exist and are separately addressable. R2 still holds for the *move*
   case: the same content at a new path where the old path is **no longer live** is the same file
   version, with the path change recorded in history. *Consumers affected:* P3, P6, P12.
3. **How do events with no single file record their subject?** §8.2 requires `file ID` on the event
   record, yet its own vocabulary includes `destination-tree edit`, `template application`, and
   `graph-edge creation`, which are not per-file. *Threatens:* P9, P10.
4. **Are §8.2's thirteen file-record items stored on the file record or reachable as projections?**
   "Current and historical file facts / group memberships / placement proposals / user decisions" are
   other parts' rows. *Threatens:* P6, P9, P11.
5. **Settled — B5.** The vocabulary is **open** under the registration rule in Contract out §3: the
   nineteen §8.2 names are reserved, every other type is declared by its authoring part, and P1
   validates against the union. And it is **one log** — §8.2's event record already carries `prompt
   fingerprint`, which is P7/P8 audit data, so §8.4's consent-aware audit record is this log with
   `correction_scope` and P7's consent fields, not a second sink.
6. **Does §8.5 shadow mode write to `events`?** A new model generating "parallel recommendations
   without changing the user-visible tree" either interleaves with live history or needs a second sink.
   *Threatens:* P2.
7. **Settled — S5 / G3.** **P1** owns §8.7's learning-record store, as a scoped projection over
   `events.correction_scope` (Contract out §7). P1 already holds the log and the scope column; a
   projection over them is coherent and needs no new part.
8. **Settled — S2 / G2.** **P1** owns the vector array store; **P9 computes** the embeddings
   (Contract out §9). Shape is §0's: compact local arrays, never a vector database. Lifecycle follows
   the identity the producing part keys them on.
9. **How is the volume or root identifier derived, and is it stable?** §8.2 requires the field. §8.3
   names cloud-synced directories as externally mutable and subject to sync agents renaming and
   replacing files. Stability across remount, volume rename, and cloud re-sync is unspecified.
   *Threatens:* P12.
10. **Settled — ratified 2026-08-19 (I2). SHA-256.** §8.2 requires storing the algorithm and
    names none; SHA-256 is chosen to match P4's `observation_key = sha256(content_hash ‖
    extractor_name ‖ locator ‖ raw_value)`, which is already the published citation handle. §3.4
    keys every cached extraction result on the content hash, so a later change re-keys the whole
    cache — `hash_algorithm` is stored per row (§8.2) precisely so such a migration is detectable.

11. ~~**What must survive a rebuild?**~~ **Settled in part — ops runtime, ratified 2026-08-19.** The database lives in
    Application Support, never inside a scan root. Rebuild reconstructs identity + deterministic
    extraction + facts those extractors can reproduce. It does **not** reconstruct `events`,
    learning records, plan versions, consent grants, or review actions. P13 must say so before a
    rebuild. [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §2. What a *user* considers
    essential besides that split remains a product-copy question, not a schema one.
12. **Moved to P6 — M1.** `preferred` now sits on P6's `file_facts` alone, so whether it is
    chain-scoped or (file, field)-scoped is the resolver's question, not the substrate's. P1 keeps the
    at-most-one-per-chain rule for the column it publishes; §3.13's ranking across chains is P6's.
13. **Which timestamps?** §8.2 says "observed size and timestamps" (plural); §1.2's stat cache uses
    size and modification time only. Whether creation/birth time must be stored is unstated.
14. **Settled — MINOR 10.** `user_id` is **kept, nullable, and populated only on an explicit user action**.
    §8.2's own wording settles it: the event record carries "user identity when there is an explicit
    user action", so the field is required and its absence on a system-originated event is correct,
    not a gap. That the product is single-user does not make the column redundant — it distinguishes
    an event the user caused from one the engine caused, which is what §8.7's correction learning and
    §8.2's audit trail read it for. P3's `selected_by` (R1) is consistent with this.
15. **Is there a hashing budget?** §8.6 enumerates twelve ceilings and names none for hashing or
    database storage. Behaviour on a multi-gigabyte file is undefined. Owning the configuration object
    (G4) does not answer this: P1 holds the ceilings the design names and will not invent a thirteenth.
    *Also open in* P3 OQ15.
16. **One database, or one per corpus root?** §0 says "a local SQLite database", singular, while §1.1
    lets the user select multiple sources and multiple candidate roots. *Threatens:* P3.
17. **Does P1 validate other parts' vocabularies?** Settled for `event_type` only — B5's registration
    rule makes P1 reject an unregistered type. `sensitivity_state`, tier names, and event subsystems
    are still stored opaquely, and whether the substrate should reject an unknown value there is
    unstated.
18. **Is any §8.6 ceiling plan-versioned policy under §8.8?** New with G4. §8.8's plan version captures
    "placement policy settings", and `tree.max_folder_proposals_and_depth` reads like one, yet §8.8's
    list names no ceiling and P1's state is versionless by design. If any ceiling turns out to be
    plan-scoped, it belongs in the plan version, not in P1's shared object. *Threatens:* P10, P11.
19. ~~**Should the scan identifier be published as shared identity?**~~ **Settled — ratified
    2026-08-20. Yes, and P3 publishes it.** P3 owns the scan (§1.1), so P3's `scan_run_id`
    IS the identity and `scan_resource_usage` is keyed on it. `start_scan` requires it with
    no default: P1 mints nothing, because a value P1 minted is one nothing else can join.
    That join is what lets P13 show §8.6's six counters beside the file counts from the same
    scan, and what lets a P2 bundle name the scan it captured. The original wording follows.
    New with D1. §8.6 says "every
    scan" and no part publishes a scan id — P4's `run_id` is per *(file × extractor)*, not per scan.
    P1 mints one locally for `scan_resource_usage` (Contract out §10) and deliberately keeps it off
    `events`, so §8.2's eleven fields and Done-means 7 are unaffected. If P2's replay or P13's progress
    line needs to join file counts to resource counters, the identifier has to become shared, and it
    belongs wherever the scan is owned — P3 — not invented here. *Threatens:* P2, P3, P13.

16. **UNRESOLVED — deferred to P7 build (I6). Delete-versus-append-only is a genuine design
    contradiction.** §8.4 gives the user the right to "review and delete local derived data"; §8.2's
    R6 forbids ever updating or deleting an event. A v1 that cannot forget a scanned passport's OCR
    text is not shippable; a v1 that `DELETE`s from `events` is not the specified product. **Decision
    deferred to when P7 is built** (ratified 2026-08-19). *Consequence P1 must not foreclose:* if the
    resolution is tombstoning, P1's derived-data tables need tombstone columns and the projections
    need to honour them. P1 therefore does not assume derived rows are permanent, and no P1 schema
    decision may depend on their permanence. `events` stays append-only under every candidate
    resolution — that is not the open part. *Also open in:* P7 OQ4, P5 OQ6, P13 OQ11.
