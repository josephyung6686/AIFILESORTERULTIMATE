# Item and relationship model

Date: 2026-09-30. Status: proposal, except the sections marked **Exists**, and except stage (a) in section 11, which is implemented on branch `app`.

Branch: `app`, starting from `cursor/item-relationship-model-29aa` (that branch stacks the sorting pipeline and context onboarding). `main` is untouched. Nothing here is merged.

The owner decided the product is a context graph over what a person already has. Files, folders, emails, calendar events, tasks, people, and projects are items. Relationships are built from evidence. The folder tree is one view among Graph, Timeline, Board, Table, and Folder. Files stay where they are on disk; choosing an item opens the original path. Gmail and Calendar are read-only. A student profile is the first profile, and profiles are pluggable. The agent has one ladder: connector, nudge, assistant. It acts only with approval. It does not change anything silently, and it does not send a protected hold to the cloud.

This note starts from `docs/architecture-audit.md` and from the code that audit names. Anything below marked **Proposal** is not in the repository.

## What was not verified

- The founder's Downloads folder (1,833 files). No name list and no rescan. Stage (a)'s tests rename, edit, and delete files under pytest's temporary directory. Nothing in that stage has been run on the owner's Downloads.
- Whether the macOS run passed `--semantic-model`.
- A line-by-line reading of every `group_edges.weight` writer. The column exists (`src/grouping/schema.py`). This note does not adopt that float as a confidence.
- A platform filesystem watcher. `SessionWatch.poll` is the stdlib stand-in; FSEvents is still not bound. Stage (a) re-finds a renamed file through `observe_path` on the next `reconcile_tree` or live scan. `scan_agent/scan.py` still has a path that does not re-hash when size and mtime are unchanged.
- Gmail and Calendar APIs, scopes, and payload shapes. No ingester exists in `src/`. A search for those products in Python found only academic-calendar wording in the sorter.
- Whether an edited structural answer now creates a draft plan version. `planning/75` recorded that link as missing on 2026-08-30. This pass did not re-audit it.
- A database shared by two people. `learning_records` requires `user_id IS NOT NULL` and does not filter to the current user (`src/database_agent/learning.py`).

## Goal

One local model of the person's items and the evidenced links between them, so a later connector can propose links, a nudge can warn, and an assistant can answer, without moving files and without a second, silent copy of the truth.

## Global constraints

- Files do not move on disk. Opening an item uses the stored original path.
- Every relationship carries why, a closed confidence, a source, and a state a person can approve, reject, or undo.
- An empty profile leaves today's recognition unchanged. That is already the rule in `Detector.explain` when `declared_lives` is empty (`tests/recognition/test_declared_lives_gate.py`).
- Safety holds stay independent of the profile and of any link. `finance`, `identity`, `medical`, and `legal` are the four domains in `src/recognition/vocabulary.py` `SAFETY_DOMAIN_IDS`.
- Protected material and anything in `privacy.vocabulary.ALWAYS_LOCAL` does not gain a new way off the laptop. `ALWAYS_LOCAL` stays nine members. No tenth member is added by this plan.
- Cloud AI does not invent a destination, does not bypass a hold, and does not approve a link.
- Abstaining is a success. A wrong link and a wrong type are counted apart from an unplaced item.
- Kill and continue numbers below are **proposals**. They are not rulings. The release bar on the pinned 41-file corpus (30/41 exact, 0 wrong) stays in force for sorting and is a different measurement from the fixture checks in this note.
- Students are the first profile package. The detector must not grow a branch on the string `student`.

---

## 1. What exists, and what this model refuses to pretend

**Exists.** One SQLite database, default `agent.sqlite` (`src/database_agent/db.py`, `SCHEMA_VERSION = 2`). `files` stores `file_id`, `current_path` (indexed), `content_hash`, name, extension, size, timestamps, `st_dev`, `st_ino`.

**Exists.** `observe_path` resolves a path to a file version:

- Same path and same bytes: the same `file_id`.
- Same bytes, new path, old path gone: the same `file_id`, `current_path` updated, a `stat observation` event. A same-volume rename keeps the inode and is confirmed that way. A cross-volume move is narrower: only the oldest recorded home of those bytes, and only when that home is gone. Two live copies stay two rows.
- New bytes at a path that already has a live row: the old `file_id` is marked superseded (`external modification detection`) and a new `file_id` is minted.

**Exists.** A file-version evidence graph. `grouping/vocabulary.py` `EDGE_TYPES` has seven values: `shared-validated-fact`, `duplicate`, `version-family`, `compatible-document-type`, `existing-related-folder`, `bounded-session`, `mutual-semantic-retrieval`. Rows live in `group_edges` (`from_file_id`, `to_file_id`, `edge_type`, `evidence_ref`, `weight`, `bridge_entity_ref`, `hub_suppressed`, supersession columns). Both ends are file ids. `mutual-semantic-retrieval` and `bounded-session` are `NON_ANCHORING_SUPPORT`: they cannot by themselves make a group supported.

**Exists.** A second graph, `placement/graph.py`, local to one candidate destination node. It is not stored in `group_edges`. Destinations are a tree: `tree_nodes.parent_node_id`.

**Exists.** Correction memory is append-only `events` plus `learning_resets`. `learning.py` says P1 does not learn: no weighting, no generalization. A reject suppresses the same `proposal_class` + `basis_key` until reset. An accept is stored and is not read as a prior. Scopes are the closed tuple `file`, `group`, `node`, `branch`, `template`, `domain` (`database_agent/events.py` `CORRECTION_SCOPES`). Recognition does not read it. Undo reverses a move and does not write a learning basis.

**Exists.** A declared-life profile on this branch: `questions/profile.py`, readers in `questions/store.py` (`declared_lives`, `refused_lives`, `named_projects`, `left_alone`, `named_courses`, `profile_wording`). `Detector.explain` admits only declared schemas when that set is non-empty. A declined winner is cited on `matched_terms`. `schema_id` stays empty so a later vote cannot file the file under that schema. Course names and leave-alone phrases are stored and are not matched against filenames.

**Exists.** Apply still renames or copies (`mutation/execute.py`). Leave-in-place is a residual policy (`tree_design/vocabulary.py` `leave-in-place`). There is no in-repo screen that opens `current_path`.

**Proposal.** The context graph is a new pair of tables, items and relationships. It does not reuse `group_edges` as its storage. Those edges are file-to-file, they carry a float `weight`, and they exist to group files before a model sees a dossier. A life link from an email to a project does not fit that row. The seven edge types may be *projected* into relationships (the witnessed-links stage after the thin slice). They stay where they are.

**Proposal.** `tree_nodes` stays the proposed filing tree of the sorter. The Folder view in this product reads `files.current_path`. It does not read `tree_nodes`, and it does not call `mutation/execute.py`. Until a later owner ruling turns apply off, the sorter can still move files. This plan does not turn apply off. A view that promises "nothing moved" must not share a button with apply.

## 2. Items and identity

**Proposal.** An item is one thing the person can point at. Closed types for the first profile, and the list is data in the profile package (section 4), not a branch in the detector:

| Type | First profile | Identity that survives a rename |
|---|---|---|
| `file` | yes | `file_id` of the live version, chained across supersession |
| `folder` | yes | directory inode when `lstat` works, else the path string, reattached by the same vanished-home rule as files |
| `email` | later, stage (b) | provider message id + local account id |
| `event` | later, stage (b) | provider event id + calendar id |
| `project` | yes, as a declared name | the profile's project id, not a folder path |
| `course` | yes, as a declared name | the profile's course id |
| `person` | no, until a profile asks | a local id; an address is an alias |
| `task` | no | a local id, only if a profile includes tasks |

**Exists, and the file case is already half-solved.** A rename or move of *unchanged bytes*, done outside the app, keeps `file_id` on the next recording scan (`observe_path`). Path history is `file_path_history`, a projection over events with `old_path` and `new_path`.

**Exists, and an edit is a new version.** New bytes at the same path supersede the old `file_id` and mint another. If the product called the new row a new life-item, a homework file the person saved would fall out of every link.

**Proposal.** `file` items use a durable `item_id` that is not the version id.

- First observation of a path mints `item_id` and points it at that `file_id`.
- A rename that `observe_path` resolves to the same `file_id` updates `open_target` to the new `current_path`. Links stay on `item_id`.
- A content change that supersedes `file_id` keeps `item_id` and moves the pointer to the new live `file_id`, recording the old id on a version chain. The chain is the supersession `observe_path` already writes. The item layer reads it. It does not invent a second hash.
- Two live copies (same hash, both paths exist) are two items. `observe_path` already refuses to merge them. A `duplicate` relationship may connect them. Merging them would be a silent change.
- A recycled inode is not an identity. `files_table.py` already treats `st_dev`/`st_ino` as a candidate confirmed against the live filesystem. The item layer uses that result. It does not store an inode as a primary key.

**Proposal.** `open_target` for a file or folder is `current_path`. Choosing the item opens that path. For an email or event it is the provider's own deep link, stored locally, and the bytes stay on the laptop. There is no virtual filesystem.

**Proposal.** A missing path does not delete the item. The item's `presence` becomes `missing` until a later scan finds it. Links to it stay, with the same state they had. Deleting a row because the file moved is how a rename looks like data loss.

## 3. Relationships

**Proposal.** A relationship is one directed claim: item A is related to item B in one way, for one reason. The first closed set, and a profile may enable a subset:

| `rel_type` | Meaning | Typical evidence |
|---|---|---|
| `duplicate-of` | same bytes, two live paths | `content_hash` equality from `files` |
| `version-of` | later bytes of the same item chain, or a grouping `version-family` edge | supersession, or a projected `group_edges` row |
| `attached-to` | a file was an attachment of an email, or one file's bytes are named inside another | hash match against an attachment part; the part's message id |
| `about` | an email or file is about an event or a project | the person approved it, or a witnessed id (a course code the profile named, an event id in the subject) |
| `member-of` | a file or email belongs to a project or course the person declared | an approved link, or a folder the person named in `named_projects` / `named_courses` |
| `occurs-on` | an item is tied to an event's time | the event id, or a date the person confirmed |
| `from-person` | an email's from-address alias | the address on the stored header, not a guessed display name |

**Proposal.** These are not the seven `EDGE_TYPES`. A projection stage may copy a `duplicate` or `version-family` edge into `duplicate-of` or `version-of` and set `source` to `grouping`. It copies `evidence_ref` through. It does not copy `mutual-semantic-retrieval` or `bounded-session`. Those two are already forbidden from anchoring a group. Showing them as life links is how the graph becomes a hairball.

**Proposal.** Every relationship row carries:

- `why`: one or more evidence refs already in the database (an observation key, a `group_edges.evidence_ref`, a message-id plus attachment hash). Empty `why` is not a row. The writer refuses it.
- `confidence`: a closed word, not a float. `witnessed` means the bytes or the provider id say so. `declared` means the person typed it (a project name, a course). `inferred` means the connector proposed it from a shared topic and it is not yet witnessed. `corroborated` means two independent witnessed facts. `group_edges.weight` is not this field.
- `source`: a closed word. `scan`, `grouping`, `profile`, `gmail`, `calendar`, `connector`, `person`.
- `state`: `proposed`, `approved`, `rejected`, `withdrawn`. New rows from the connector and from projection start at `proposed`. Nothing in the agent ladder writes `approved`.
- Supersession columns in the same shape as `group_edges` (`supersedes`, `superseded_by`). Undo inserts a new row and links it. Undo does not delete.

**Proposal.** A link is approvable, rejectable, and undoable as events, not as a mute flag. The event log is the one that already exists (`append_event`). The relationship row is the projection a view reads. Section 5 says how the basis key is formed so a reject survives a rebuild of the row.

**Proposal.** A witnessed `duplicate-of` may be shown without a click, because both paths are the person's files and the hash is the whole reason. It is still `proposed` until they approve it, and the view says so. An `inferred` link is never drawn on the default graph. It appears in a review list.

## 4. Profile packages

**Exists.** Declared lives gate schemas. Refusals win. Projects, courses, leave-alone names, and wording are stored locally and do not steer the recogniser. `purpose_profile_ref` on folder applicabilities is mostly null. There is no workflow engine.

**Proposal.** A profile is a JSON package the process loads the way `tree_design/catalogue.py` loads applicabilities: packaged data, versioned, refused if the shape is wrong. The student package is the first file. A second package with a different type list must load through the same function. No function checks `if profile == "student"`.

A package names:

- `profile_id` and `profile_version`
- item types it turns on
- relationship types the connector is allowed to propose
- which declared-life schema ids map to which item type (`academic` → a `course` item when the person also named a course; `career` → no automatic project)
- required pairs for the nudge, as data: for example a `course` item expects a `member-of` file whose recognition is `academic` before the course event's date. Missing means a warning. Missing does not create a file or a link.
- the default view and the graph cap (section 7)

**Proposal.** The package does not include safety schemas as optional. `SAFETY_DOMAIN_IDS` stay holds whether or not the package lists them. A package that omits `identity` does not release a passport. That matches the gate test: an identity document stays protected when identity is not a declared life.

**Proposal.** Binding the package to a person uses the question records that already exist. `declared_lives` chooses which schemas may type a file. `named_projects` and `named_courses` mint `project` and `course` items (state `declared`, source `profile`). `left_alone` mints nothing and forbids `member-of` links whose evidence is only that name. `profile_wording` stays in the local database and is not a relationship and not a cloud request. The wording reader already refuses to build a `SelfDescription`.

**Proposal.** An empty package is the absence of a package. Recognition stays the full catalogue. No relationships of type `about` or `member-of` are proposed. `duplicate-of` may still be proposed from hashes, because that claim does not depend on a life.

## 5. Correction memory

**Exists.** Exact-match suppression of a reject. Accept is not a prior. No generalization. No per-user filter beyond `user_id IS NOT NULL`. Recognition ignores it.

**Proposal.** Link decisions are a new scope `link` on the same event row. `CORRECTION_SCOPES` is a closed tuple. Adding `link` is an owner edit of that tuple, the same kind of edit as `branch` on 11 Sep 2026. This plan does not sneak the scope in under `file`.

**Proposal.** `basis_key` for a link is a canonical JSON of:

- `rel_type`
- the two endpoint identities (`item_id`, which for a file follows the durable id, not the path)
- the evidence fingerprint (sorted evidence refs)

It is not the relationship row id. A rebuild that mints a new row id for the same claim hits the same basis. That is the difference from today, where a new proposal id would look like a new fact and the reject would miss.

**Proposal.** Polarity is read, for this scope only:

- `reject`: the connector does not re-propose that basis until `reset_preferences` for scope `link` and that subject. Other pairs are untouched. A file's schema recognition does not change.
- `accept`: the projection's state is `approved`. The same basis is not asked again. The accept does not approve a different pair that shares a topic word.
- Undo: a new event, polarity recorded as the reversal, newer than the accept, so `learning_records`' cutoff is the wrong tool (a reset would drop history). The reader walks events after the last reset and the latest polarity wins. Rows before the reset stay in `events`. Nothing is deleted. This is the one place the reader does more than `is_suppressed`. It is still exact. It is not a weight.

**Proposal.** Generalization ("they rejected one business link, so suppress the schema") is out of this plan. `learning.py` forbids it, and the declared-life gate exists because a weight would not have stopped a unique wrong winner. A later plan can propose generalization only with a fixture where a reject of one link leaves an unrelated file's type unchanged, and a kill if it does not.

**Exists, and it stays.** Fact-level `is_suppressed`, placement `suppressed_nodes` at file scope, and grouping's standing reject keep their keys. Link learning does not replace them.

## 6. Storage

**Exists and stays.**

- `files`, `events`, `learning_resets`, inode columns, `SCHEMA_VERSION` 2 path in `database_agent/db.py`
- `group_edges` and the rest of the grouping schema
- `tree_nodes` and placement tables
- structural questions, including the profile answers on this branch
- classifications and privacy tables

**Proposal.** New tables, created by a new `src/items/schema.py` `create_items_schema`, called from `cli._bootstrap` the way questions are. They are not folded into `FILES_DDL`. A failure to create them must not stop `observe_path`. `user_version` stays P1's. The items package records its own version in a one-row `items_meta` table so an old database gains the tables idempotently (`CREATE TABLE IF NOT EXISTS`) without pretending P1's version bumped for a package P1 does not own.

```sql
CREATE TABLE IF NOT EXISTS items (
    item_id        TEXT PRIMARY KEY,
    item_type      TEXT NOT NULL,
    display_label  TEXT NOT NULL,
    file_id        TEXT,
    open_target    TEXT,
    external_key   TEXT,
    presence       TEXT NOT NULL,  -- live, missing
    typing_state   TEXT NOT NULL,  -- typed, unplaced, held
    type_schema    TEXT,
    profile_id     TEXT,
    created_at     TEXT NOT NULL,
    superseded_by  TEXT
);

CREATE TABLE IF NOT EXISTS item_versions (
    item_id        TEXT NOT NULL,
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    became_live_at TEXT NOT NULL,
    PRIMARY KEY (item_id, file_id)
);

CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,
    rel_type        TEXT NOT NULL,
    from_item_id    TEXT NOT NULL,
    to_item_id      TEXT NOT NULL,
    confidence      TEXT NOT NULL,
    source          TEXT NOT NULL,
    state           TEXT NOT NULL,
    evidence_refs   TEXT NOT NULL,
    basis_key       TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    supersedes      TEXT,
    superseded_by   TEXT
);
```

`evidence_refs` is a JSON array. `basis_key` is the canonical JSON from section 5. Indexes: `(item_type)`, `(file_id)`, `(external_key)`, `(from_item_id, rel_type, state)`, `(to_item_id, rel_type, state)`, `(basis_key)`.

**Proposal.** `typing_state = held` is set when the classification is protected or the basis is `safety_domain`. The schema id may still be `identity`. Held is not unplaced, and it is not a filing destination.

## 7. Gmail and Calendar

**Exists.** Nothing ingests either. Academic-year parsing in `cli.py` is a date fact for coursework, not a calendar account.

**Proposal.** An ingester is a later stage, off by default, read-only, local.

What it stores on the laptop:

- Account id (a local label the person picks, plus the provider's account id).
- Email: message id, thread id, internal date, From and To as addresses, subject, attachment filenames, attachment hashes, and a pointer to a local file item when a hash matches `files.content_hash`.
- Event: event id, calendar id, start, end, title, and a status word from the provider.
- The OAuth refresh token, in the operating system's credential store or in a file beside the database that no dossier builder reads. It is not a column in `items`.

What it does not store as a releasable excerpt, and what must not leave the laptop:

- Full message bodies, raw RFC822, attachment bytes, calendar descriptions, and attendee lists beyond the addresses needed for `from-person`.
- Any of the nine `ALWAYS_LOCAL` members, by a new door. Bodies are complete extracted text. Tokens and message ids joined to a path are paths-and-edits territory.
- Protected-kind material (`identity_document`, `medical_record`, financial statements, credentials, legal documents naming the person). If an attachment hash matches a file whose classification is protected, the email item's `typing_state` is `held` and the body is not passed to a model call. The local link `attached-to` may exist. The hold reads the same precaution path the detector already uses. The gate does not get a special case for "it came from Gmail".

**Proposal.** Scopes are read-only. The ingester has no send and no modify. A test that sees a network call other than the read, or a body byte inside a model-request fixture, fails the stage.

**Proposal.** Subjects and titles can themselves be sensitive. They stay in `items.display_label` locally. A cloud assistant may see a subject only when the item is not held and the existing release gate would already allow that text. This plan adds no new releasable kind.

## 8. Views

**Exists.** No Graph, Timeline, Board, or Table screen. The CLI prints a gist, a tree proposal, and set-asides. Apply moves bytes.

**Proposal.** Each view is a query function over items and live (not superseded) relationships. A screen can come later. The queries are the contract. Default limits are part of the student package and are overridable by another package.

| View | Query | Default that avoids a hairball |
|---|---|---|
| Folder | Live file and folder items, grouped by the parent of `open_target`. | The on-disk tree. No inferred edges. Click opens `open_target`. |
| Table | One row per live item: type, label, typing_state, open target, count of approved links. | No edges drawn. Unplaced is a column value, not a hidden drop. |
| Board | One column per declared `project` or `course` item. Cards are items with an approved or witnessed `member-of` to that column. | A last column, Unplaced, for `typing_state = unplaced` with no such link. Held items are a separate strip, not a column the person can drop a card into by accident. |
| Timeline | Items that have a time: email internal date, event start, or file timestamp labeled as filesystem time. | A window of 90 days (package data). Files with only an mtime are not mixed into the event lane unless a relationship `occurs-on` is approved. |
| Graph | Neighborhood of one item the person selected, or of one project. | Cap 40 nodes (package data). Edges drawn: `approved`, plus `witnessed` `duplicate-of` and `attached-to`. `inferred` edges are omitted and counted in a line under the figure ("12 proposed links hidden"). Semantic and session edges are never drawn. If the person has not selected a center, the graph shows the project and course items and their approved members, not the corpus. |

**Proposal.** The default graph query returns at most the cap, and returns the hidden count. A query that returns every item is a test failure. Density is not solved by a force-directed layout.

## 9. How the recognition gate types an item

**Exists.** With a non-empty `declared_lives`, only those schemas can be a `Recognition`. Otherwise the catalogue behaves as it does today. `outside_declared_lives` cites the would-be winner on `matched_terms` only. Safety holds still fire when the winning schema was not declared.

**Proposal.** After `explain` and the classification record:

- `Recognition` of a declared schema: `typing_state = typed`, `type_schema` is that id. This is a type, not a folder.
- Abstention `outside_declared_lives`, `ambiguous`, `no_evidence`, `no_corroboration`, or `file_kind_implausible`: `typing_state = unplaced`. `type_schema` stays null. The citation may be stored on the item as a local note for the review list. It is not the type. Putting it in `type_schema` would undo the gate's reason for leaving `schema_id` empty.
- Classification protected, or basis `safety_domain`: `typing_state = held`, even when the schema is also a declared life. Held wins over typed for the privacy strip. The type can still be recorded beside it for the person. It is not sent to the cloud.
- No profile: `typing_state` may be `typed` from today's recognition, and relationship types that need a profile stay off. This keeps `test_an_empty_declaration_leaves_recognition_unchanged` as the regression net.

**Proposal.** Wrong and unplaced are different counts.

- Wrong: `typing_state = typed` with a `type_schema` the person later rejects, or a relationship whose state becomes `rejected` after it was shown as approved or witnessed.
- Unplaced: `typing_state = unplaced`, or a file with no `member-of` link. Unplaced is a success when the alternative was a professional schema the person did not declare.
- The synthetic pair already in `tests/recognition/test_declared_lives_gate.py` is the typing fixture. Coursework-plus-business vocabulary with the founder allow-list types as `academic` (a hit, not unplaced). Business-only vocabulary stays unplaced and must not count as wrong.

## 10. Agent ladder

**Proposal.** Three capabilities, one store, increasing privilege. None of them write `state = approved` or call `mutation/execute.py`.

1. Connector. Notices a witnessed or inferred claim and inserts `proposed`. It prefers `witnessed` (hash, attachment, declared course id in the file's own name). An inferred link requires two declared lives and at least two terms on each side inside the allow-list. One shared ordinary word is not a link. That is the same failure mode as the professional catalogues: ordinary words outvoted coursework.
2. Nudge. Reads the profile's required pairs and the calendar times. A missing item produces one local warning with the evidence refs. It does not create the missing item and does not approve a stand-in.
3. Assistant. Answers from local rows a question can cite. The citation is an `item_id` and an evidence ref. A held item is omitted from any cloud request and named locally as held, without its body. The assistant does not invent a destination folder.

Approval is a person event (section 5). Silent approval is a test failure at every stage that has a writer.

## 11. Staged build

The first three stages are a thin slice. Later stages stay after that slice and are not started with it. This document's reorder is stage 0. Checks are fixture counts. The Downloads tree is not a stage gate, because it is not in the repo.

Wrong and unplaced stay separate counts on every stage. A wrong count is an identity, type, or link the stage showed as true and the check rejects. An unplaced count is `typing_state = unplaced`, or a file with no `member-of` once links exist. A missing path is neither: the item row stays, and `presence` is `missing`.

### Stage 0 — this document

The stage order below. Done when the thin slice is the first build order in this file.

### Stage (a) — a path index that survives a rename or move done outside the app

**Implemented on `app`.** Files: `src/items/schema.py`, `src/items/identity.py`, `tests/items/test_file_identity.py`, `create_items_schema` from `cli._bootstrap`, and `project_after_scan` at the end of the live scan (`orchestrator.run_p1_p7`).

**What this stage reuses.** The `files` table and `content_hash` (`hash_file`). `observe_path`, reached through `record_basic_record`, for same-bytes rename and move, for an edit that supersedes a `file_id`, and for two live copies staying two file rows. Inode confirmation stays inside `observe_path`; the item layer does not store an inode as identity. `reconcile_disappearances` and `set_path_no_longer_exists` retire a gone path from the corpus and delete nothing. The walk is `scan_agent.traversal.walk` over `FilesystemCorpusSource`, after `require_access`. `SessionWatch.poll` is the existing session watcher (a stdlib stand-in for FSEvents). A detection still does not rewrite `files`; the reconcile pass is what applies the fingerprint after the watch has seen a change. The live scan already calls `observe_path` on a recompute and already retires disappearances; `project_after_scan` only points items at those rows.

**What this stage adds.** `items` and `item_versions`, so an edit that mints a new `file_id` keeps one `item_id`. `presence = missing` when the path is gone. `reconcile_tree`, the pass the tests run: walk, `observe_path`, disappearance, then the same item projection the live scan runs.

**Check.** A temporary fixture, rescanned through `reconcile_tree`.

- A file renamed or moved outside the process, including a move onto a new inode: same `item_id`, `open_target` updated, 0 new items. Wrong (a second item): 0.
- An in-place edit: same `item_id`, the new `file_id` and the old one both on `item_versions`. Wrong (a new item): 0.
- Two live copies of the same bytes: two items. Wrong (one item for two live paths): 0.
- A deleted file: the `items` row remains and `presence` is `missing`. The `files` row remains with `scan_state = path_no_longer_exists`. That missing count is not the unplaced count and not the wrong count.
- Unplaced: these file items stay `typing_state = unplaced`, because this stage does not type them. A missing path does not change that count.

**Kill (proposal).** Any rename or fingerprint move produces a second item, any copy collapses two live paths into one item, or a deleted file has no `items` row. Stop and keep `file_id` as the only file identity until the chain is fixed.

**Continue (proposal).** Wrong identity changes: 0. Every deleted fixture file is still a row with `presence = missing`. Unplaced is reported on its own and is not the name for missing.

### Stage (b) — read-only Gmail and Calendar, stored locally as items

**Not started.** Files, when it starts: `src/items/ingest_mailbox.py`, `tests/items/test_mailbox_local.py`. A fixture message and a fixture event, not a live account.

**Check.** One message, one attachment whose hash matches a local file: an email item, stored locally, with the message id and the hash, and no body in any table the model-release path reads. One calendar event: an event item with the provider event id, start, end, and title, and no description. A protected local file matched by attachment hash: the email item's `typing_state` is `held`, and a model-request builder returns no body and no attachment text. The test double has no network and no send.

- Wrong: a body, token, or raw message stored as a releasable excerpt, or an item written as approved. Count those as wrong, not as unplaced.
- Unplaced: an attachment hash that matches no local file stays an email item with no file link. That is unplaced relative to the library, not a wrong link, and the email item is still stored.

**Kill (proposal).** A body, token, or raw message appears in a releasable excerpt, or the ingester writes `approved`, or it sends or modifies.

**Continue (proposal).** The fixture message and the fixture event are local items. Wrong excerpts: 0. Held stays held. Unplaced attachments (no matching file) stay unplaced and are still listed.

### Stage (c) — one deadline-to-files view

**Not started.** One query, not the five views. Files, when it starts: `src/items/deadline_view.py`, `tests/items/test_deadline_view.py`.

**Check.** One event item with a start time, two file items with a witnessed or approved link to it, and one file the fixture expects at that deadline with no such link.

- The two linked files appear on the deadline.
- The expected file with no link appears as missing from the deadline, and its `items` row is still there. That is a missing count.
- Wrong: a file shown as linked when the relationship is not witnessed or approved. Count 0.
- Unplaced: a file with `typing_state = unplaced` and no link stays in the unplaced count. It is not counted as a wrong link, and it is not dropped from the result to make the deadline look complete.

**Kill (proposal).** The view hides the gap, shows an inferred link as though it were witnessed, or omits the unplaced count.

**Continue (proposal).** Linked count matches the witnessed or approved rows. Missing count matches the expected file with no such row. Wrong links shown: 0. Unplaced stays its own count.

### Later — witnessed links only

**Files:** `src/items/relationships.py`, `tests/items/test_witnessed_links.py`.

Project `duplicate` and `version-family` from `group_edges` when `evidence_ref` is non-empty. Add `duplicate-of` from equal `content_hash` on two live items. Do not project semantic or session edges.

**Check.** Two files, same hash, both live: one `duplicate-of`, confidence `witnessed`, source `scan` or `grouping`, state `proposed`, evidence refs non-empty. A third unrelated file: no link. A `mutual-semantic-retrieval` edge: no relationship row.

**Kill (proposal).** A row with empty evidence, or a semantic edge copied into `relationships`.

**Continue (proposal).** Wrong links on the fixture: 0. Unplaced files: still unplaced. The business-only gate fixture gains no `member-of`.

### Later — approve, reject, undo

**Files:** `src/database_agent/events.py` (scope `link`, owner permitting), `src/items/decisions.py`, `tests/items/test_link_decisions.py`.

**Check.** Reject a basis. Rebuild the proposal. It stays suppressed. A different pair with the same `rel_type` is still proposed. Accept, then undo: the live projection is `proposed` or `withdrawn` as the undo event says, and the accept event is still in `events`. Run `Detector.explain` on the same file before and after the reject: the schema id is unchanged.

**Kill (proposal).** A link reject changes a recognition, or a reject of one pair suppresses another.

**Continue (proposal).** 0 schema changes. 0 cross-pair suppressions. Undo leaves the prior event in place. Wrong links (one reject suppressing a different pair): 0. Unplaced files stay unplaced.

### Later — a pluggable profile

**Files:** `src/items/profiles/student.json`, `src/items/profiles/files_only.json`, `src/items/profile_loader.py`, `tests/items/test_profile_packages.py`.

Student turns on file, folder, project, course, and the relationship subset in section 4. `files_only` turns on file and `duplicate-of` only.

**Check.** Loading `files_only` proposes no `member-of`. Loading student with declared `academic` and a named course mints a course item and still does not approve a link. A passport fixture stays `held` under both packages. Empty package: the existing gate test still passes.

**Kill (proposal).** A branch on the profile name inside `detector.py`, or a package that clears `protected` on a safety classification.

**Continue (proposal).** Both packages load through one loader. Holds: unchanged on the passport fixture. Wrong types: 0 on the coursework gate fixture. Unplaced: the business-only file.

### Later — the five queries

**Files:** `src/items/views.py`, `tests/items/test_views.py`.

**Check.** A 200-file fixture with a dense set of semantic edges (written as `group_edges`, not as relationships) plus 10 witnessed duplicates and 3 projects. The graph query, with no center selected, returns at most 40 nodes and a hidden count greater than 0. Semantic edges do not appear. The board has an Unplaced column. The folder query's paths equal `files.current_path`. No call path from these functions reaches `mutation/execute.py`.

**Kill (proposal).** The default graph returns the full 200, or any query renames a file.

**Continue (proposal).** Cap respected. Wrong links shown as approved: 0, because nothing has been approved. Unplaced count equals the files with `typing_state = unplaced`.

### Later — nudge, then assistant

**Files:** `src/items/nudge.py`, `src/items/assistant.py`, `tests/items/test_nudge.py`.

**Check.** A course item, an event tomorrow, and no `member-of` academic file: one warning, zero new approved rows, zero moves. Assistant, asked which files are in the course, cites `item_id`s and returns no row for a held item's body.

**Kill (proposal).** Any silent state change, any move, any held body in the answer payload.

**Continue (proposal).** Warnings: 1 on that fixture. Silent approvals: 0. Wrong citations (a file that is not a member, cited as a member): 0.

## 12. Risks

- Treating `group_edges` as the context graph locks every link into file-to-file and drags semantic edges into the picture. Section 3 refuses that reuse on purpose.
- Teaching the recogniser from link rejects would re-open the professional-schema failure. Section 5 keeps those stores apart.
- An edit that mints a new `file_id` looks like a new document unless stage (a)'s version chain is in place. Shipping relationships before that chain orphans links on every save.
- Inodes do not exist for an email. Using a path as the only identity for mail will break when the provider rewrites a label.
- Gmail subjects and calendar titles are often more sensitive than a filename. Storing them is required for a timeline and is a standing local-only obligation. A later "just this once" excerpt is the risk.
- The sorter still moves files on apply. A Folder view that opens `current_path` is honest only while nothing else relocates the file in the same session. The two behaviours need separate commands.
- The default graph cap is a product choice (40, 90 days). A wrong cap is a bad picture. An absent cap is an unreadable one. The kill is the absent cap, not the particular number.
- Extending `CORRECTION_SCOPES` and `RESERVED_EVENT_TYPES` is a closed-vocabulary edit. It needs the same kind of owner note `branch` and `refused move` already have. Implementing the approve/reject stage without that note should stop.
- Profile JSON that can name arbitrary relationship types is a plug-in. Profile JSON that can name a safety domain as "not held" is a bypass. The loader must ignore hold-related keys.
- There is no GUI in the repo. The thin slice and the later query stages can be tested as functions. A screen is not a stage in this plan.

## 13. Self-check against the request

| Asked | Where |
|---|---|
| Start from the audit's real stores | Section 1 |
| Item types and identity across rename and edit | Section 2 |
| Relationship types with why, confidence, source, approve/reject/undo | Section 3 and 5 |
| Pluggable profiles, student first | Section 4 |
| Correction memory that learns exact link decisions and does not only suppress by accident | Section 5 |
| Tables and migrations versus what stays | Section 6 |
| What mail and calendar store, and what stays on the laptop | Section 7 |
| Five views, including a default that is not the full graph | Section 8 |
| Recognition gate feeds typing; wrong and unplaced apart | Section 9 |
| Staged order, a check per stage, kill/continue as proposals | Section 11 |
| Risks and what was not verified | Sections 12 and the opening list |
| Connector, nudge, assistant; approval; no silent change; no cloud bypass | Section 10 |
| Mark proposal versus what exists | Each section |
