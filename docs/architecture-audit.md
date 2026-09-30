# Architecture audit

Read of this repository on 2026-09-30, after the scan-root exception, the
profile record, and the declared-life gate on this branch. The three claims
below are what a reader of the product might expect to find already built.
Each section says what the code does, what is only written down, and what is
not there. Paths are from `src/` unless noted.

This is not a line-by-line reading of every planning note, and it is not a
run of the founder's Downloads folder.

## 1. Correction memory

The claim: every approve, reject, and undo teaches the user's structure, per
user.

What exists is narrower than that.

The store is an append-only projection over `events`, plus a cutoff table
`learning_resets`. The module that owns it says so in its first lines:
`database_agent/learning.py` — "P1 does not learn: no weighting, no
generalization, no ranking, no application." `learning_records` returns rows
for one `(correction_scope, correction_subject)` where `user_id IS NOT NULL`
and the event is newer than the latest reset for that pair
(`database_agent/db.py` defines the tables). It does not filter to the user
who is running the command. `--user` defaults to `getpass.getuser()`
(`cli.py`). One SQLite file is the practical boundary between operators.
There is no user-profile table in `database_agent`. The profile questions
added on this branch are a different record; see section 2.

A hit is exact. `facts/learning.py` `is_suppressed` returns true only when
the same `proposal_class`, the same `basis_key` (file, field, value), and
polarity `reject` are still unreset. An accept at the same basis is not a
suppression. The same shape is used by:

- `placement/learning.py` `suppressed_nodes`, called from
  `placement/pipeline.py` with the file scope only. A rejected node is
  skipped. It is not re-ranked and it does not become a prior for a schema.
- `grouping/graph.py`, which drops a standing reject of that group.
- `tree_design/provenance.py` `suppressed_branch_basis_keys`.
- `llm_harness/eligibility.py` `suppressed_by_learning`.
- `privacy/learning_seam.py` `suppressed`.

`src/recognition/` does not read `learning_records` or `review_actions`. A
correction does not change which schema the term detector names.

Approve, in the apply path, records that a move was allowed
(`review_surface` `review_approvals`, and the mutation journal). It does not
write a schema prior. Undo (`mutation/undo.py`) reverses one applied journal
entry and records the attempt. It does not call `reset_preferences` and it
does not write a learning basis.

`reset_preferences`, `learning_view`, and `collect_reset` are not called from
`cli.py`. `tests/integration/test_cli_correction_loop.py` marks that gap as
an expected failure. `review_run/learning.py` defines `learning_projection`
and `learning_lines`; nothing else under `src/` imports them.

Planned, not running: `planning/10-i4-learning-ops.md` describes the
correction store. The code that shipped is the exact-match guard above.

Missing relative to the claim: no per-user structure model, no weighting, no
generalization from one file to similar files, no path from approve or undo
into recognition, and no command that resets learning.

## 2. Profile templates

The claim: a library of pre-researched profile templates, such as one student
profile with course-to-deliverable and application-to-requirements workflows,
that an agent can look back on.

There is no such object.

Three catalogues exist, and they are not that library.

1. Recognition situations. `recognition/library/recognition.json` is the
   compiled term index (built by `recognition/compile.py` from
   `planning/domains/nodes/*.json`). The runtime loads the JSON. It does not
   import `planning/`. The index is a list of situations and the words that
   activate them. It is not a workflow, and it is not selected by a student
   profile. Twenty-three schemas are in `facts/domains.py` `SCHEMA_IDS`,
   including the professional ones that mis-labelled the founder's folder.

2. Folder templates. `tree_design/catalogue.py` loads
   `tree_design/library/` (`fragments.json`, `definitions.json`,
   `applicabilities.json`, and the wave-2 files). An applicability names an
   ordered set of fields. `ap.academic.coursework` is school, term, subject,
   work type. `ap.applications.undergraduate-packet` is target university,
   application cycle, application document type. `purpose_profile_ref` on
   those rows is null. Nothing walks "this course requires these
   deliverables" or "this application requires these documents" as a
   procedure. `planning/111-LIBRARY-COVERAGE.md` records that many
   professional situations are recognised and not bound to a tree template.

3. Planning research. JSON under `planning/domains/` includes nodes whose
   kind is `template`. That tree is source for the compiler and for people
   reading the design. The running program does not query it.

`planning/104` puts onboarding, a role matcher, and automatic filing in a
later release. That is a document, not a callable library.

What this branch adds, and what it is not: `questions/profile.py` and
`questions/store.py` store confirmed answers for declared lives, refused
lives, project names, leave-alone names, course names, and free-text wording.
The wording stays in the local database. The detector's allow-list reads
`declared_lives` and nothing else in that record. Course names are not
matched against files. There is still no agent-facing workflow library.

## 3. Graphs

The claim: the architecture has graphs.

It has two specialised graphs. It does not have a general graph database, and
the repository does not depend on a graph library.

- `grouping/graph.py` `LocalEvidenceGraph` is a neighbourhood of file
  versions. Retrieval has six channels; the graph stores seven edge types
  (`grouping/vocabulary.py` `EDGE_TYPES`): shared validated fact, duplicate,
  version family, compatible document type, existing related folder, bounded
  session, mutual semantic retrieval. Edges are persisted in `group_edges`
  (`grouping/schema.py`). A standing reject can suppress a group. This graph
  does not decide a destination folder.
- `placement/graph.py` is a second, node-local graph: the file being placed
  plus files already accepted in that one candidate node. It is not stored in
  `group_edges`. Its own module says it is local by construction so the
  placement pass cannot recluster the corpus.

Destinations are a tree. `tree_design/schema.py` stores
`tree_nodes.parent_node_id`. A parent pointer is not the evidence graph.

Missing relative to the claim: no graph of the person's life domains, no
graph the profile is queried through, and no engine that plans a workflow
over either graph.

## 4. Persistent index and a virtual library

A virtual library, as asked here, would mean: files indexed and arranged
inside the product, originals never moved, and choosing an item opens the
original path.

The index that exists is one SQLite database. The default path is under
Application Support, `agent.sqlite` (`database_agent/db.py`). The `files`
table stores `file_id`, `current_path` (indexed), `content_hash`, name,
extension, size, and timestamps. Other packages create their own tables in
that same file when a run starts: scan, evidence, extraction, facts, privacy,
grouping, questions, the model harness, tree design, mutation, and review.
The folder-template catalogues are packaged JSON, not rows in a template
table.

Apply moves bytes. `mutation/execute.py` renames a file, or copies it when
the destination is another volume. The journal keeps `original_source_path`
so undo can put the file back (`mutation/undo.py`). That path is an audit
field on a move, not a click target.

Leaving a file where it is already exists as a residual policy.
`tree_design/vocabulary.py` names `leave-in-place`. Placement treats that
policy as no move (`placement/pipeline.py`, `placement/residual.py`). The
product design in `planning/00-database-agent-product-design.md` still treats
the filesystem as the system of record. There is no in-repository interface
that lists indexed files and opens `current_path`.

So the database can back a later virtual library: every scanned file has an
id and a current path, and a leave-in-place decision already means "do not
move this." Nothing in this repository presents that as a library, and apply
still moves files when the person approves a move.

## What this reading did not check

- Every command-line gesture that can write a review action. The learning
  readers above were traced from their call sites; a gesture that writes an
  event and has no reader would not show up as teaching.
- A database shared by two people. The schema allows many `user_id` values
  and the reader does not isolate them.
- The whole of `planning/`. Citations above are the notes that the code or
  this audit actually opened.
- The founder's Downloads folder. No scan of those 1,833 files was run for
  this note.
