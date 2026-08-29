# 70 — How the mechanism actually works

Date: 2026-08-29. Written to be handed to someone whose job is to **find what is wrong with it.**

---

## 0. How to read this document

**What this is.** A description of the machine as it stands, part by part, at the level of
*mechanism* rather than code: what happens to a file, in what order, who decides what, what is
refused and why, and what a person ends up seeing. It is long because the machine is not simple and
a short version would hide exactly the places where it does not work.

**What this is not.** It is not a design document, not a proposal, and not an argument that the
product is good. Where the code and the design disagree, this document follows **the code**, and
says the design disagrees. Every section ends with a heading called **"What looks wrong here"**,
written by the person who read that part most closely.

**The three states you must keep apart while reading.** The single most common way to
misunderstand this project is to blur them:

| | means | example |
|---|---|---|
| **Built and running** | code exists, has a caller in `src/`, and executes on a real run | grouping files by a shared course code |
| **Built and inert** | code exists and nothing calls it, or a field is written and no decision depends on it | `sensitivity_policy_ref` — required on every template definition, parsed from the catalogue, carried on the record, and consulted by nothing: `grep` finds it declared (`templates.py:301`), required (`:338`), loaded (`catalogue.py:94`) and present in the shipped library, and in no branch anywhere |
| **Designed and absent** | a document says it, no code does it | everything in `66` — Find, filing, onboarding questions |

A reader who assumes the third category is the first will conclude the product does far more than
it does. **The product today reads files, decides which belong together, proposes folders, says
where each file would go — and moves nothing.** There is no search. There is no filing. There are
no onboarding questions. Section 9 is the inventory of that gap and is the most important section
for a critic.

**The authority order**, which explains why several arguments in this document end the way they do:

```
planning/00-database-agent-product-design.md   (the owner's design; wins every dispute)
  → planning/66-FIND-FILE-AND-ONBOARDING.md and the eleven part SPECs
    → the PLANs
      → the live code in src/
```

**A note on how this document was written, because it bears on how much to trust it.** Nine
readers each took one part, read the source, and wrote their section against the code rather than
against the SPECs — with instructions to flag rather than fix, and to end with what a critic should
press on. The sections carry roughly 1,700 `file.py:line` citations between them; check any of them.
One reader found a defect while writing (**the shipped command crashed on its own second run**),
which was reproduced, traced to three separate causes, fixed and committed as `86edf8b` before this
document was assembled. Both sections that reported it are annotated in place rather than rewritten,
so the finding and its resolution are both on the record. Everything else marked as wrong is still
wrong.

**Two standing constraints** bind every part and are worth having in mind from the first page:

1. **Protected material is MARKED AND COUNTED, NEVER OPENED.** Reports, applications, system files
   and anything sensitive in that sense are present-but-untouched, with a reachable explanation, and
   are **never silently omitted**. A protected container is not skipped quietly — it is named,
   counted, and declared not to be a place anything can be filed.
2. **The north star is a real, multi-role human.** Not the lawyer OR the parent OR the researcher,
   but the person who is several of those at once — whose research paper is also school homework,
   whose legal document is part of an application. Several mechanisms below only make sense as
   answers to that person, and several failures below are failures to serve them.

---

## 1. The shape of the whole thing, on one page

Eleven parts, numbered P1 to P11, each owning its own tables inside **one** SQLite database. Nothing
in the chain decides anything it was not given: every threshold, ceiling, clock, catalogue, policy
and user answer arrives as an **injected authority with no default**. Absent means *refuse*, never
*guess*. That discipline ends in exactly one file — `src/cli.py`, the composition root — which is
where all the actual numbers live and which section 8 inventories.

| | part | the question it answers | what it must never do |
|---|---|---|---|
| **P1** | storage, identity, provenance | *Which file is this, and what has happened to it?* | enforce a ceiling it publishes |
| **P2** | eval / replay harness | *Would this run reproduce?* | judge quality |
| **P3** | scan and corpus selection | *Which files are we even looking at?* | look inside a protected container |
| **P4** | evidence shape | *What did we see, and where exactly?* | interpret what it saw |
| **P5** | extractors | *What do the bytes of this format say?* | invent a pattern; ship a catalogue |
| **P6** | facts and facets | *What do we now believe about this file?* | let a weak clue become an asserted property |
| **P7** | privacy and consent gate | *May anything about this file leave, or be acted on?* | default an absent classification to "public" |
| **P8** | bounded model harness | *What did a model say, and may we believe it?* | be reached except through the gate |
| **P9** | grouping | *Which files belong together, and why?* | name a destination or a folder |
| **P10** | tree design and freeze | *What folders should exist?* | move a file, or invent a user's answer |
| **P11** | placement and residual | *Where would each file go?* | create a destination, or guess between two homes |
| **P12** | apply and undo | *Actually move it, reversibly* | **DOES NOT EXIST** |
| **P13** | review and approval surface | *Show a person the decision and take their answer* | **DOES NOT EXIST** |

The two absent parts are not incidental. **P12 is why nothing moves. P13 is why nothing is really
reviewed** — and section 8 shows what the shipped command puts in P13's place, which is the largest
single reason a person's proposed tree is one folder deep.

---

## 2. The journey of one file, end to end

This is the spine. Every later section is a magnification of one step of it. Follow one file — say
`Problem Set 3.pdf`, sitting in `Downloads`, containing the text `PHYS 1401`.

**1. It is selected, or it is not.** A scan run records a corpus selection: which roots, which
source. Before anything is read, the exclusion pass runs by PATH. If this file were inside
`Notes.app`, the walk would stop at the bundle, write an **exclusion verdict** naming it, and never
descend. The bundle is counted and named; its interior never becomes a row. *(Section 1.)*

**2. It gets an identity.** Its bytes are hashed. The identity that matters downstream is not the
path and not the filename — it is the pair `(file_id, content_hash)`. Edit the file and it is a new
content version; the old row survives as `superseded_content`. Move the file and the path history
records the move, and the identity is unchanged. Almost every table below is keyed on that pair.
*(Section 1.)*

**3. It is read, and the reading is recorded whether or not it produced anything.** An extractor is
chosen by detected format — by extension, deliberately, because the class of file that must never be
opened is decided by path before any format question is asked. The extractor emits **observations**
in a shape every extractor shares: raw value, a locator saying exactly where in the document it came
from, occurrence count, reliability. Separately, an **extraction run** row records what happened —
`complete`, `capped`, `partial`, `unreadable`, `unsupported`, `dataless`, and four more. A complete
run that emitted zero observations *is* the record that the file carried nothing; absence is
recorded here or nowhere. *(Section 2.)*

**4. Something in the text is recognised as structured.** The parts ship no patterns at all — the
caller supplies them. The shipped deployment supplies exactly ONE regular expression, for identifier
tokens: letters then digits, like `PHYS1401`. Until 2026-08-29 it could not read `PHYS 1401` with a
space, and a real folder of coursework therefore produced nothing at all. It now reads one separator,
and both spellings canonicalise to the same value. *(Sections 2 and 3.)*

**5. The observation becomes a fact — or does not.** P6 runs three stages: `direct`, `rule`, `llm`.
The shipped deployment supplies only `direct`, and a stage that is `None` means *this stage does not
exist* rather than *this stage found nothing*. The direct stage reads the identifier into the field
`subject` at reliability `direct`. Two spellings of one identifier reach one `value_id`. A fact the
run could not reach stays visible in `unresolved` rather than being recorded as absent. *(Section 3.)*

**6. The privacy gate is asked, and on a real run it says no.** P7 wants a handling class for the
file. **No detector ships**, so nothing classifies it, and P7 refuses to default an absent
classification to a public class — the file resolves to `unreadable_unclassified`, which is a *gate
outcome*, not a property of the file. The consequence runs all the way to the person: no dossier may
be assembled, no model may be asked, and the placement decision at the end will abstain. *(Section 4.)*

**7. Grouping asks what this file belongs with.** P9 takes the file's strongest facts as **seeds** —
at a bar deliberately narrower than P6's, so a model conclusion cannot confirm its own earlier guess.
It retrieves neighbours through named channels, of which only a shared validated fact may *anchor*;
it builds a typed-edge graph; it runs six stop rules before spending anything. The group's address is
the **identity the seed states** — since 2026-08-29 — so four files each stating `PHYS1401` are one
group of four rather than four groups of one. *(Section 5.)*

**8. A tree is proposed.** P10 takes accepted groups, matches them against a shipped template
catalogue (208 situations), routes through eight composition gates, materialises candidate branches,
validates them through six checks, and offers the user options with counts and warnings. The user
approves and **freezes** a plan version. A protected container appears in that tree as a node that is
explicitly *not a legal destination*. *(Section 6.)*

**9. Each file is placed against the frozen tree — or is not.** P11 indexes the tree's destinations,
retrieves candidates for the file's facts, scores them against two conditions (support and margin),
and either places or abstains **with a named reason**. Two legal homes is not a confidence failure and
does not read as one. A file nothing could classify abstains as blocked, waiting on the person.
Everything unplaced lands in a review set that carries its reason. *(Section 7.)*

**10. A report is printed, and nothing has moved.** The protected containers come first, by name and
count, with the sentence that says nothing inside them was read. Then the proposed folders. Then the
files, grouped by *kind of outcome* rather than one line per file. Then what this needs from the
person. *(Section 8.)*

**11. And there it stops.** There is no step 11. Nothing applies the plan, because P12 does not
exist. Nothing shows the person a real review, because P13 does not exist. Nothing lets them search
for the file afterwards, because Find is designed and unbuilt. *(Section 9.)*

---

## 3. What a critic should already know before starting

Three facts about this project's history that make the rest legible.

**The suite is large and it has been wrong.** 5,232 tests pass, in fixed and randomised order.
On 2026-08-29 the composition root was found to write `scan_state = "scanned"` while the grouping
part's retrieval admitted only `"included"` — so on **every live run, every file had an empty
neighbourhood**, no shared-fact edge could ever be built, and no group could ever hold two files.
Five thousand green tests agreed with a production path that could not work, because the grouping
part's own tests wrote the value it expected. Every defect fixed that day was found by running the
command over files on a disk; none by the suite. **A claim in this document that "the tests cover
it" is not a claim that it works.**

**The parts are honest and the seams are where it fails.** Each part refuses loudly, names its
refusals, and declines rather than guessing. The failures found so far have almost all been at the
boundary between two parts that each behaved correctly in its own vocabulary.

**The product's current terminal state is the same for everybody.** Four personas — a litigator, a
student who also teaches, a two-child household, and one person who is all three — were run through
the shipped command on 2026-08-29. All four ended identically: **zero files ready to file, a
one-folder tree, every file "waiting for you to say what these are."** Nothing was misfiled and
nothing was lost. Nobody was organised. Sections 8 and 9 explain why, and the reasons are not the
ones a reader would guess from the size of the engine.

---

## Contents

- **1. Intake and identity — how a file enters the system**
- **2. Reading a file — extraction and evidence**
- **3. From evidence to facts — what the product believes**
- **4. The privacy gate and the model harness**
- **5. Grouping — which files belong together**
- **6. Tree design and freezing — proposing the folders**
- **7. Placement — where each file would go**
- **8. The composition root — what the shipped command chooses**
- **9. Designed and not built — the gap**

Every section from 1 to 9 ends with **What looks wrong here** — the findings the person who read that part most closely wanted a critic to press on. Those nine sections are the fastest route into this document if you are here to break it.


---

# 1. Intake and identity

This section describes how a file gets into the system: what happens between the moment a
person names a directory and the moment a row exists that later parts can read. Two parts do
this work. **P3** (`src/scan_agent/`) owns the corpus boundary — which paths are in, which are
out, and why. **P1** (`src/database_agent/`) owns identity and the log — which row a path
resolves to, and what is written down about the resolution. Everything downstream reads what
these two produce and nothing else about the filesystem.

The two are deliberately not symmetrical. P3 decides and P1 records; P3 authors events and P1
writes them; P3 computes the ten per-file fields and P1 is forbidden from re-deriving any of
them (`files_table.py:31-33`, `basic_record.py:8-11`). Most of the sharp edges in this section
are places where that split is either enforced by a mechanism or merely asserted in a comment.

---

## 1.1 What happens when a directory is pointed at

### The database is opened before the corpus is touched

`cli.py:1053` calls `open_database(database, scan_roots=[directory])`. `open_database`
(`db.py:28-62`) resolves the database path, then refuses if that path is the scan root or lives
underneath it — `DatabaseInsideCorpus` (`db.py:15-17`, raised at `db.py:39`). The reason given
is that P3's exclusion rules would otherwise have to special-case the agent's own storage. The
default location is `~/Library/Application Support/<bundle_id>/agent.sqlite`
(`db.py:19-25`), and the bundle identifier is supplied by the caller rather than invented.

The same call sets the connection's durability and integrity posture, and one of those settings
is load-bearing rather than cosmetic: `PRAGMA recursive_triggers = ON` (`db.py:52`). Without it,
SQLite's `INSERT OR REPLACE` deletes a conflicting row *without firing delete triggers*, which
would let any caller rewrite an event row in place and silently forge the append-only log. The
schema is created eagerly at the end of `open_database` (`db.py:60`) so no neighbour has to
remember a second call.

### A selection is recorded before anything is walked

P3 has no corpus until one is handed to it. `record_selection` (`selection.py:40-65`) writes one
`corpus_selections` row carrying §1.1's three user choices: `sources`, `candidate_roots`, and
`cross_folder_moves`, plus `selected_at` and a nullable `selected_by`. All four keyword
arguments are required with no defaults, so P3 cannot derive a corpus from the machine's layout
(`selection.py:45-51`).

In the shipped CLI the selection is degenerate: `cli.py:583-585` passes
`sources=[directory], candidate_roots=[], cross_folder_moves=False`. The candidate-root half of
the design — the "high-level locations that may serve as roots for a future file tree" — is
always empty in a live run, which means every mechanism below that distinguishes the two sides
of the scan is exercised only by tests.

`cross_folder_moves` is recorded and enforced nowhere. The DDL comment says so in the schema
itself: "the user's selection (§1.1); enforced nowhere in P3 -- SPEC Q12 is OPEN"
(`selection.py:31-32`). No module in `src/` reads the column.

### A scan run is opened, and committed, before the first file

`scan()` (`scan.py:55-81`) is the whole run. In order:

| Step | Where | Note |
|---|---|---|
| Read the selection's two path sets | `scan.py:66-67` | |
| Check Full Disk Access on every root | `scan.py:68` → `access.py:38-51` | Before the run row exists |
| Mint and commit the `scan_runs` row | `scan.py:73` → `run.py:30-43` | Deliberately outside the write batches |
| Walk, recording each item | `scan.py:74-79` | Inside `batched_writes` |
| Close the run, sample resources | `scan.py:80` → `run.py:46-57` | |

The access check is a real attempt to list each root, not a table of TCC-protected paths:
`unreadable_roots` (`access.py:24-35`) calls `os.scandir` and treats `PermissionError` as the
whole test. If any selected root refuses, `require_access` raises `FullDiskAccessRequired` and
the scan performs *zero* traversal rather than a partial one (`access.py:38-51`). A root that is
merely absent is not a permission problem and falls through to the traversal.

The run row is committed before the first file so that an interrupted scan is a *visible
incomplete run* rather than an absent one (`scan.py:70-73`). `start_scan_run` inserts P3's row
first and only then registers the run with P1's `start_scan`, because `selection_id` is a
foreign key and a bad selection should fail before P1 opens a counter row (`run.py:34-42`).

`scan_run_id` is minted by P3 (`run.py:37`) and adopted by P1. That was P3 OQ16 / P1 OQ19,
ratified 2026-08-20 and recorded in the module docstring (`run.py:1-11`). It is published
identity but deliberately *not* an event field: §8.2's event record stays at eleven fields.

### Writes are batched, and why

Every walked item is recorded inside `batched_writes(conn, size=512)` (`scan.py:74`,
`db.py:105-169`). The connection is autocommit with `synchronous = FULL`, so without a boundary
every one of the five rows a file admission writes would be its own fsync — on macOS an
`F_FULLFSYNC`, a full device cache flush. The measured numbers are in both docstrings:
13.7 ms per file unbatched against 2.2 ms with a transaction held open, i.e. 11.5 ms of every
13.7 was fsync (`db.py:120-125`, `scan.py:30-34`). 512 was chosen by interleaved measurement
against 1/32/128 (`scan.py:41-48`).

The honest statement of what a crash costs is made in both places and is worth repeating,
because it is the kind of claim a critic should check: nothing is made *damageable* —
`synchronous` is untouched — and what a power cut loses is at most 512 *files not yet recorded*,
which the next scan re-records because no cache verdict exists for them
(`db.py:126-133`, `scan.py:44-48`). `batched_writes` catches `BaseException`, not `Exception`,
so a hand interrupt rolls back the batch in flight rather than leaving it for the next statement
to commit by accident (`db.py:162-168`).

---

## 1.2 The corpus boundary: traversal and exclusion

### The walk is pure

`traversal.walk` (`traversal.py:55-68`) is a generator over a `CorpusSource`. It opens no
database and writes no row (`traversal.py:5-7`). Every §1.1 decision is therefore finished
before any record exists, which is what makes it structurally impossible for a curation signal
or any other later-computed value to influence an exclusion or a cache verdict.

It yields four things, and `scan._record` (`scan.py:84-142`) dispatches on their types:

| Yielded | Written by | Table |
|---|---|---|
| `ExclusionVerdict` | `record_exclusion` | `exclusion_verdicts` |
| `Deferred` | `record_deferral` | `scan_deferrals` |
| `ObservedDirectory` | `record_directory` | `directory_inventory` |
| `ObservedFile` | `record_basic_record` → P1 | `files` + `events` |

`walk` runs the scanned sources first, then the candidate roots (`traversal.py:65-68`), tagging
each item with `applies_to`. Candidate-root *files* are yielded but dropped at the writer:
`scan.py:96-97` returns early for any `ObservedFile` whose `applies_to` is not
`"scanned source"` — "roots are context, not corpus". Their directories still produce inventory
rows.

The source abstraction (`corpus_source.py`) has two implementations: `FilesystemCorpusSource`
(`corpus_source.py:52-81`) and `SnapshotCorpusSource` (`corpus_source.py:84-107`), the latter
for §8.5 replay against a frozen corpus with no filesystem at all. Entries are sorted by path in
both so two runs agree (`corpus_source.py:81`, `:103-104`). `stat(follow_symlinks=False)`
throughout: a symlink is reported as `KIND_OTHER`, so it is never descended (a loop would make
traversal non-terminating) and never handed to a hasher (`corpus_source.py:59-68`).

### The exclusion predicate

`exclusion_for` (`exclusion.py:117-143`) is the single place a §1.1 rule fires. It returns an
`ExclusionVerdict` or `None`, and it tests four things in a fixed order:

1. **Protected container** — first, always (`exclusion.py:130-133`). See §1.3.
2. **Software-project-root descendant** (`exclusion.py:134-136`), if the entry's *parent*
   directory contained one of the four markers. Applies to files and directories alike.
3. **Literal directory name** (`exclusion.py:137-138`), directories only, against the eleven
   names §1.1 spells: `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`,
   `Pods`, `site-packages`, `Library`, `__pycache__` (`exclusion.py:23-26`).
4. **Category** (`exclusion.py:139-142`), directories only.

Rule 4 can never fire. §1.1 names five categories — build artifacts, caches, auto-save folders,
previews, generated dependency trees — and enumerates no member of any of them, so
`CATEGORY_MEMBERS` maps each to an empty tuple (`exclusion.py:32-43`). The loop is wired against
the mapping so that authoring the list is a data change rather than a code one, which is a
defensible choice, but as shipped `RULE_CATEGORY` is a constant with no reachable producer.
The same applies to marker extension: `PROJECT_ROOT_MARKERS` is fixed at four
(`exclusion.py:40-42`) and `project_root_markers_in` (`exclusion.py:145-157`) accepts no
additions.

`project_root_markers_in` requires the marker to be a *file*, so a directory named
`package.json` is not one (`exclusion.py:156`). Markers are computed once per directory listing
(`traversal.py:96-98`) and applied to every entry in it. Whether the marker-bearing directory
*itself* is excluded is P3 SPEC Q9 and is explicitly left open (`exclusion.py:150-154`) — only
descendants are rejected.

An exclusion is a **prune**: the verdict is yielded, the entry is never enqueued and never
listed (`traversal.py:120-122`). No `files` row, no descendants, no inventory row for it.

### Verdicts are permanent

`exclusion_verdicts` has an `exclusion_verdicts_no_delete` trigger (`exclusion.py:171-175`) —
"an exclusion verdict survives a later rule-set change". This matches the SPEC's statement that
an R3 record explaining why a path was skipped is not deleted when the path later becomes
eligible. Note the asymmetry with `events`: the events table is protected against UPDATE,
DELETE *and* replace (`db.py:265-274`); `exclusion_verdicts` is protected against DELETE only.

---

## 1.3 Protected containers — marked and counted, never opened

This is the project's one absolute rule. The P3 SPEC states it at length: an application bundle,
a macOS package, and anything under a system location is a protected container; P3 "does not
descend into one, does not stat its contents, does not hash a byte of it, and does not create a
`files` row for anything inside it", and "no policy, approval, or user gesture makes it
movable". `upstream.py:263-266` quotes the product owner's own words for it.

### Where the predicate lives

`is_protected_container(path, *, extra=None)` (`exclusion.py:69-89`). Two properties matter:

- **The unit of protection is the subtree, not the entry.** The function walks
  `(candidate, *candidate.parents)` and returns True if *any* ancestor carries a protected
  suffix (`exclusion.py:83-89`). The docstring records that an earlier version tested only the
  path's own suffix — which protected `Numbers.app` and admitted
  `Numbers.app/Contents/sheet.numbers`, the exact read the rule forbids — and that every test
  passed because every test asked about the bundle. It was found by injecting the predicate into
  P5's gate and watching the gate admit the file (`exclusion.py:74-80`).
- **`extra` can only add.** A caller-supplied predicate is OR'd in; there is no way to return
  False for a `.app`, because a predicate that could would be the override the rule says does
  not exist (`exclusion.py:80-82`).

The authored membership is one suffix: `PROTECTED_BUNDLE_SUFFIXES = (".app",)`
(`exclusion.py:66`). The SPEC also names the *category* "system location" and enumerates no
member, so P3 authors none — inventing `/System`, `/Library` or `/usr` here would be a
gazetteer the project refuses to write. The comment says "A deployment supplies the rest through
`extra`." **It cannot.** Neither `exclusion_for` call site passes `is_protected`
(`traversal.py:73`, `traversal.py:118-119`), and neither `walk()` nor `scan()` takes a parameter
that could reach it. The extension point exists and is unreachable from the scan.

### What an exclusion verdict is

`ExclusionVerdict` (`exclusion.py:96-114`) is a frozen record of five fields:

```text
path          the rejected path
rule          which §1.1 rule fired
rule_subject  the literal name, the category, or the marker file observed
applies_to    "scanned source" | "candidate root"
label         §8.6's display category — non-None only for protected containers
```

`label` is a **field rather than a constant**, and the docstring explains why at length
(`exclusion.py:103-114`): `LABEL_UNTOUCHED_PROTECTED` previously existed as a documented
constant whose only use anywhere was a test asserting it equalled its own literal. It reached no
verdict, no row and no summary, so P13 would have found it missing and re-derived it from
`rule` — one value computed twice, which this codebase repeatedly names as its most expensive
defect class. Only the protected container carries a label; the other three rules get `None`,
because inventing display names for them would be P3 authoring a vocabulary nobody asked for.

Ordering is what makes the label honest. Because the protected test runs first, a `.app` inside
`node_modules` is recorded as protected rather than under the weaker rule that would understate
why it was skipped (`exclusion.py:127-129`).

### How the mark reaches a person

Four independent mechanisms, in the order a file would meet them:

| Layer | Mechanism | Cite |
|---|---|---|
| Scan | `exclusion_for` tests protection first; the subtree is pruned, so no interior `files` row is ever created | `exclusion.py:130-133`, `traversal.py:120-122` |
| Extraction | `admit()` is the first statement of every extractor and raises `ProtectedContainerRefused` before its reader is touched | `safety.py:49-64` |
| Tree design | `protected_areas()` turns P3's verdicts into `ProtectedArea` records that reach the canvas | `upstream.py:283-303` |
| Report | The count and every path print **first**, before anything else | `cli.py:878-887` |

`SafetyPolicy` (`safety.py:38-46`) has exactly two fields "and deliberately no third: a `force`,
`override` or `approved` field would be the override 11 §4b says does not exist". The CLI wires
P3's own predicate into it (`cli.py:410`) rather than a second spelling.

`protected_areas` filters on `rule`, not on `label` (`upstream.py:290-292`) — the rule is the
decision, the label is the display string, and selecting on the display string would make a
presentation change silently alter which areas the tree represents. The `ProtectedArea`
docstring states the point of the whole record: "a protected container that is pruned and then
never mentioned has been silently omitted, and silent omission is the one outcome the rule
forbids" (`upstream.py:268-272`).

The report block is the reachable end of it (`cli.py:864-889`). It prints
`Protected containers: N marked, none opened`, then each area's display label, label and path,
then a sentence: nothing inside was read, indexed, classified or moved, and none of them is a
place anything can be filed. The docstring is explicit that position is part of the guarantee:
"'Marked and counted, never opened' is only true if the count is somewhere the person reads, and
a line at the bottom of a long report is not that." The later per-file listing, which truncates
to ten names per kind (`cli.py:809`), never truncates a protected group — `_protected`
(`cli.py:849-861`) treats any of three signals as protection, on the stated reasoning that the
cost of over-including is a longer list and the cost of the reverse is silent omission.

**The rule is enforced for `.app` bundles and for nothing else.** That is the honest summary. A
scan of a home directory protects `Foo.app`; it does not protect `/System`, `/usr`, `~/Library`
(which is excluded by the *weaker* literal-name rule, unlabelled and unreported), or anything a
deployment might consider sensitive, because there is no wiring by which a deployment can say so.

---

## 1.4 File identity

### The hash is the identity of a *version*

`HASH_ALGORITHM = "sha256"` (`identity.py:14`), chosen to match P4's `observation_key` formula
(P1 OQ10, ratified 2026-08-19). `hash_file` (`identity.py:49-65`) streams in 1 MiB chunks and
returns 64 lowercase hex characters. `is_content_hash` (`identity.py:43-46`) publishes the
predicate so no consumer re-spells "64 lowercase hex" as a second definition of one rule; it is
deliberately *not* algorithm-prefixed while P4's citation keys are, so a citation key stored in
a `content_hash` column cannot pass for a hash (`identity.py:31-39`).

`hash_file` takes `materialized: bool` **with no default** (`identity.py:53-60`). It is the
caller's declaration that P3's dataless check has run. Passing False raises
`DatalessFileRefused`. P1 has no ubiquity API and invents no detection heuristic; the required
keyword is the mechanism that stops any caller reaching P1's bytes without having made the
check.

### `volume_id` is per-process and therefore inert

`volume_id_for` (`identity.py:68-83`) returns `f"{OBSERVATION_SESSION}:{os.stat(path).st_dev}"`,
where `OBSERVATION_SESSION` is a UUID minted once per process (`identity.py:19`). P1 OQ9 — is
`st_dev` stable across remount, volume rename, or cloud re-sync? — is open, so the value is
deliberately poisoned across processes: within one process it compares correctly, across
processes it can never accidentally match, so no cross-session decision can be built on it.
`files.volume_id` is nullable for the same reason (`db.py:180`).

The practical consequence is that the column is written on every row and is meaningful to
nothing. `file_path_history` (`files_table.py:486-499`) publishes `volume_id` as a literal
`NULL` because `events` has no volume column at all (`files_table.py:489-493`). Note also that
`volume_id_for` uses `os.stat` (follows symlinks) while every other identity call in this module
uses `lstat` (does not) — see §1.10.

### Resolving a path to a row

`observe_path` (`files_table.py:369-483`) is the whole of R2/R3. It hashes the file, then asks
up to three questions in a fixed order:

1. **Is there a live row at exactly this path with these bytes?** (`files_table.py:408-412`) —
   an indexed lookup on `(current_path, content_hash)`. A re-scan of an unchanged corpus takes
   this branch for every file, so a duplicate family of any size costs nothing to re-observe.
   Exact path wins first so a deleted twin with an earlier rowid cannot steal a still-live
   copy's identity.
2. **Is one of the rows for these bytes *this very inode*?** — `_row_for_this_inode`
   (`files_table.py:113-168`), answered from the `files_inode` index on
   `(st_dev, st_ino, content_hash)` (`db.py:220-222`).
3. **Has the oldest recorded home of these bytes gone?** — `_relocated_row`
   (`files_table.py:171-216`), R2's cross-volume move.

The `st_dev`/`st_ino` columns are the most interesting piece of mechanism here and the schema
comment is emphatic that they are **not a second identity** (`db.py:190-198`). Inodes are
recycled, so a stored pair can name a file that no longer exists. Every index hit is a
*candidate*, confirmed against what the filesystem says now, and there are exactly two ways a
candidate confirms (`files_table.py:126-141`): its recorded path is still live and *is* this
inode (one file under two spellings of its name — NFC/NFD on APFS — which is one record), or its
recorded path is **gone**, which is what a rename necessarily leaves behind. A candidate whose
recorded path is live but is a different inode is rejected, and that is the recycled-inode case.

This index replaced a walk over the whole duplicate family that cost O(k) syscalls per file
admitted and O(k²) to admit a family of k (`files_table.py:117-121`) — empty files, `.DS_Store`,
stub configs and repeated downloads make families that size on a real disk.

`_relocated_row` is a **deliberate narrowing** and says so (`files_table.py:186-199`). Deletion
leaves nothing in the database, so no index can answer "is any recorded copy of these bytes
missing?"; only one filesystem call per recorded copy can, which is the O(k²) being removed. So
the question asked is narrower: *is the oldest recorded home of these bytes gone?* Inside a
family with several live copies whose oldest member is still live, a cross-volume move is now
recorded as a **new file** rather than as a relocation. The stated justification is that it can
only ever mint an extra record, never merge two files into one, and that the walk's answer there
was a guess anyway.

`_path_is_taken` (`files_table.py:99-110`) guards both relocation branches: a row whose home
vanished is never moved on top of a live row recording different bytes at the observed path.

`_lstat_or_none` (`files_table.py:36-63`) is used everywhere rather than string comparison,
because comparing `current_path` as a Python string would mint a second row for the NFC and NFD
spellings of one name — and §8.3's collision policy, seeing two rows whose hashes "prove the
files are identical", would offer to delete one copy and delete the only copy. Normalising the
string instead would be wrong on a filesystem that does not fold. `lstat`, never `stat`, so a
symlink and its target stay two records.

### When bytes change: `superseded_content`

If no row matches by content but a live row sits at the observed path, that row's bytes changed
(`files_table.py:450-467`). Three things happen, in one transaction:

1. An `external modification detection` event is appended under the *caller's* author, carrying
   the **new** hash and the explanation "content at this path changed; this version is
   superseded (R3)".
2. The prior row's `scan_state` is set to `SUPERSEDED_CONTENT` — the literal
   `"superseded_content"` (`files_table.py:24`).
3. `invalidate_extraction_state` resets that row's `extraction_status_by_tier` to `{}`
   (`files_table.py:293-305`).

Then a **new row with a new `file_id`** is created (`files_table.py:469-477`) and a `hashing`
event appended (`files_table.py:478-482`). This is P1 OQ1, ratified 2026-08-19 (I1): `file_id`
is version-scoped and every foreign key to it is version-scoped with it, so the previous
version's facts and evidence keep pointing at a row that still describes them.

`superseded_content` is P1's own sentinel and a caller may not supply it:
`_require_caller_scan_state` (`files_table.py:219-223`) raises `ReservedScanState`. Every
identity query in the module excludes superseded rows (`scan_state != SUPERSEDED_CONTENT` at
`files_table.py:109`, `:157`, `:206`, `:411`, `:452`), which is the mechanism that keeps a dead
version from answering for a live one.

### Why almost everything downstream is keyed on `(file_id, content_hash)`

Because the two answer different questions and neither alone is sufficient. `file_id` names a
*version*; `content_hash` names the *bytes*. Two live copies of identical bytes are two
`file_id`s sharing one `content_hash` — required, because §2.9's duplicate family has nothing to
detect if duplicates collapse and §8.3's collision policy presumes both exist and are separately
addressable (P1 OQ2, I1; `files_table.py:388-391`). Conversely, one file whose bytes change is
two `file_id`s with two hashes, and the old one must stay resolvable.

So a cache or an audit record keyed on `file_id` alone would survive a content change it should
not survive; keyed on `content_hash` alone it could not tell two live copies apart. P7's
`ClassificationRecord` is keyed on the pair and is authoritative, with `files.sensitivity_state`
as its projection onto the current row (`files_table.py:351-356`). P4's evidence, P6's facts and
P9's embeddings follow the same pattern — `vector_embeddings` has a partial unique index on
`(file_id, content_hash, scope, model, version) WHERE superseded_by IS NULL` (`db.py:326-329`).

---

## 1.5 `scan_state`

The column is `TEXT NOT NULL` on `files` (`db.py:187`). P1 defines exactly one value —
`superseded_content` — and refuses to accept it from a caller. Every other value is P3's, and
**P3 invents none**: `record_basic_record` takes `scan_state` as a caller parameter with the
note that SPEC Q4 (the enumeration) is open (`basic_record.py:44-51`).

The value a live run writes is `"included"`, meaning "this file is in the corpus". Its one
named home is `P1_INCLUDED_SCAN_STATE` in `grouping/vocabulary.py:91`, declared there because
P1 and P3 publish no constant for it and P9 wanted one home rather than a second literal
(`grouping/vocabulary.py:79-89`). Its reader is P9's retrieval: `_corpus`
(`grouping/retrieval.py:128-142`) selects `FROM files WHERE scan_state = ?` and admits nothing
else, on the reasoning that "an excluded file reaching a dossier would be the scan boundary
failing silently".

**This was a live defect, fixed 2026-08-29** (commit `53c41d1`). The composition root wrote the
literal `"scanned"`; P9's `_corpus` admits `"included"` and nothing else. The comment left at
the fix site is the clearest statement of the consequence (`cli.py:395-404`): on every live run
the neighbourhood of every file was empty, no shared-fact edge was ever built, and every group
was a group of one whatever the corpus said. P9's own tests write `included`, so thousands of
passing tests agreed with a production path that could not form a group of two. The fix is an
**import** of P9's constant rather than a corrected literal.

The type-level guard that remains is weak: `P1P7Authorities.__post_init__` checks only that
`scan_state` is a non-empty string (`production.py:123-126`). Any other misspelling reproduces
the same silent emptiness with the same test suite green.

---

## 1.6 The append-only event log

### The vocabulary is closed at import

`RESERVED_EVENT_TYPES` (`events.py:30-37`) is §8.2's nineteen names, verbatim. `_REGISTERED`
(`events.py:42-78`) is the table of types other parts' SPECs declare, compiled from those SPECs
and frozen at import — **there is no runtime registration call**, because registration is a
spec-level act (P1 SPEC Contract out §3, rule 4). Two consistency checks run at import and raise
`ImportError` rather than deferring to a runtime rejection: a registered name shadowing a
reserved one (`events.py:82-84`), and a specialization whose base is not a reserved name
(`events.py:85-87`).

The registered set is P7's eight, P8's five, P13's three, and P11's nine typed specializations
of the reserved `placement recommendation`. **The SPEC says eight for P11 and totals
twenty-four** (P1 SPEC, Contract out §3); the code registers nine and therefore twenty-five. The
divergence is deliberate and documented (`events.py:62-68`): P11's SPEC:689 is one bullet
carrying two state changes — a residual set *surfaced* and a set *decided* — and §7.6 gates
model spend on the second, so they are two names. The SPEC text has not been updated to match.

### Who may write, and what is checked

`append_event(conn, **fields)` (`events.py:118-154`) is the only writer. It rejects any field
outside `EVENT_FIELDS` + `CORRECTION_FIELDS` + `base_event_type` (`events.py:124-126`), requires
five fields to be present and non-empty — `event_type`, `subsystem`, `component_version`,
`observed_at`, `explanation` (`events.py:115`, `:127-130`) — rejects an unregistered
`event_type` (`events.py:132-136`), and validates `correction_scope` against §8.7's six scopes,
requiring a `correction_subject` alongside it (`events.py:137-144`). A typed specialization gets
its `base_event_type` filled in automatically (`events.py:145-147`).

`subsystem` is never filled in by P1. The rule is M8 — *the acting part authors, P1 writes* —
and P3 enforces its half in `authorship.event_defaults` (`authorship.py:33-56`), which refuses
to build a row for an event type P3 does not author and refuses a `subsystem` that is not `"P3"`.
P3 authors exactly four reserved names: `discovery`, `stat observation`, `hashing`,
`external modification detection` (`authorship.py:25-30`). The fourth has two authors — P3 on
re-scan and P12 on §8.3 staleness — and the two are separable by `subsystem`.

P1's own mutators take `author` and `component_version` and **append no event of their own**:
`invalidate_extraction_state`, `set_extraction_status`, `set_sensitivity_state`
(`files_table.py:293-366`). The stated reason is that P1 minting an event there would name the
storage substrate as the thing that classified the file, "which is exactly what §8.2's
reconstruction requirement cannot survive" (`files_table.py:358-361`). The parameters are
consequently accepted and unused — see §1.10.

### Supersede, never overwrite

"Append-only" is enforced three ways, not by convention:

| Mechanism | Cite | Covers |
|---|---|---|
| `events_no_update` / `events_no_delete` triggers | `db.py:265-270` | UPDATE, DELETE |
| `events_no_replace` trigger | `db.py:271-274` | `INSERT OR REPLACE` onto an existing `event_id` |
| `PRAGMA recursive_triggers = ON` | `db.py:52` | Makes the replace trigger reachable at all |
| Connection authorizer | `db.py:65-76` | `DROP TABLE events`, `DROP TRIGGER` on the three |

For records that *do* change, `supersede.py` publishes the three shared column names —
`supersedes`, `superseded_by`, `supersede_reason` (`supersede.py:12-14`) — so no part re-spells
them. `mark_superseded` (`supersede.py:22-55`) requires a non-empty reason, refuses
self-supersession, refuses to re-supersede an already-superseded row so the *first* reason
sticks, and walks the forward chain to refuse a cycle. `chain()` (`supersede.py:58-72`) returns
every link, oldest first. In practice this means: the old row stays readable and queryable
forever, the new row points back at it, and the reason the transition happened is recorded once
and never rewritten. `preferred` is deliberately *not* in the shared set — it lives on P6's
`file_facts` alone (`supersede.py:3-6`).

---

## 1.7 Absence is recorded, never assumed

Four tables exist because "we did not look" and "there was nothing there" must be
distinguishable. §8.6's requirement is that no unscanned file reads as one that was understood
and found unimportant.

### Deferrals — `scan_deferrals`

Four reasons, each naming the design rule or open question that produced it
(`deferrals.py:19-36`):

| Constant | Value | Produced when |
|---|---|---|
| `DEFERRED_BUDGET` | `scan budget exhausted` | `budget_exhausted()` fires mid-listing |
| `DEFERRED_TRAVERSAL_UNRESOLVED` | `traversal behaviour unresolved (SPEC Q7)` | Entry is neither file nor directory |
| `DEFERRED_PATH_ABSENT` | `path absent at scan time (SPEC Q14)` | `FileNotFoundError` / `NotADirectoryError` on listing |
| `DEFERRED_DIRECTORY_UNREADABLE` | `directory not readable at scan time` | `PermissionError` below a cleared root |

None is a judgement about the file and none is a status from P4's closed vocabulary
(`deferrals.py:8-10`). Budget exhaustion is thorough: the unreached entries in the current
listing, the current directory itself, *and* every directory still queued are each recorded as
deferred before the walk returns (`traversal.py:104-115`). No inventory row is emitted for a
partially-listed directory, because R6 has no field for a partial count and P3 does not invent
one (`traversal.py:105-107`). A `PermissionError` on one directory yields the directory and no
inventory row — nothing inside is known, because the listing never happened
(`traversal.py:88-94`).

### Dataless detections — `dataless_detections`

`is_dataless` (`dataless.py:38-45`) reads one bit: `SF_DATALESS = 0x40000000` from macOS's
`sys/stat.h`, named here with its source because Python's `stat` module does not publish it
(`dataless.py:32-35`). It is outside macOS's `SF_SETTABLE` mask, so a test cannot set it. A
platform without `st_flags` reads as not-dataless, which is the honest answer.

The detection happens during `scandir` (`corpus_source.py:79`), i.e. *before* any hash, because
`os.stat` does not download and `open` does. `scan._record` then splits two cases
(`scan.py:98-126`):

- **Never hashed** — the detection row is the whole record and the function returns
  (`scan.py:100-106`). No `files` row exists and none can be made: hashing downloads the bytes
  and P1 refuses to mint a row without a hash.
- **Hashed, then evicted** — scanned while local, since moved to iCloud by "Optimize Mac
  Storage". The row, hash and history exist, so a cache verdict is computed and recorded, and a
  `stat observation` appended if it says REUSE (`scan.py:107-126`). A RECOMPUTE verdict is
  **recorded and not followed**: following it means hashing, and appending an external
  modification event without the recompute would assert a content change P3 cannot confirm. The
  comment records that an unconditional skip used to sit here and dropped the file out of the
  scan silently.

The orchestrator then intersects P3's detections with the extraction roster
(`orchestrator.py:545`, `:552-553`). The comment at `orchestrator.py:363-375` is the honest
account of why: there are *two* predicates for one question — P3's scan-time detection and P5's
`SafetyPolicy.is_dataless` — and this module is the only place that sees both. It wired neither
to the other, so a caller passing the usual `is_dataless=lambda p: False` (which the CLI does,
`cli.py:411`) re-extracted an evicted file and on a real machine would have triggered the
iCloud download the rule exists to prevent. P3's observation wins because it is the one made
before any read.

### Stat-cache verdicts — `stat_cache_verdicts`

`cache_verdict` (`stat_cache.py:46-69`) is disjunctive and a **difference** test, never a
newer-than test — an mtime that moves backwards is a change, which is what protects restores and
migrations. Two verdicts and four reasons, the SPEC's words and no fifth
(`stat_cache.py:26-33`). Size is compared before mtime so a file where both changed reports one
deterministic reason, with all four values on the record either way.

`prior_observation` (`stat_cache.py:92-104`) joins the verdict to `files.current_path`, which
is what stops a verdict left behind by a file that has since moved away from being reused for a
different file that later appears at the old path.

A verdict row is written for **every** file the scan reaches, REUSE and RECOMPUTE alike
(`scan.py:142`), and `file_id` is nullable for §8.5's metadata-safe form where there are no
bytes to hash (`stat_cache.py:76-77`). This table is therefore the roster: the orchestrator
iterates `cache_verdicts(conn, scan_run_id)` to find every file this scan saw
(`orchestrator.py:547`, `production.py:528`), and `scan_run_summary` counts
`DISTINCT file_id` from it for `files_indexed` (`summary.py:27-30`).

On REUSE nothing is re-read: no hash, no `observe_path`, no `files` write — only a
`stat observation` event (`scan.py:129-132`). That is resumption, done without being called
that.

### Directory inventory — `directory_inventory`

One row per fully-listed non-excluded directory (`inventory.py:56-70`), carrying parent,
non-excluded file count, subdirectory count, extension mix, and a curation signal with its
evidence. `curation_evidence` (`inventory.py:28-39`) records *every* project-root marker
observed in the directory, where the exclusion verdict records only the one that fired.

`curation_signal` (`inventory.py:42-53`) **returns `CURATION_UNDETERMINED` unconditionally.**
This is deliberate and documented: §1.1 gives one worked case and no number, no ratio, and no
list of which extensions read as software material, so the honest value is `undetermined` for
every directory and no directory is ever rounded to `incidental`. P10 renders the three values
and refuses a fourth (`upstream.py:243-249`), and `candidates.py:302` compares against
`_CURATED` — a comparison that is currently always False.

---

## 1.8 Budgets and ceilings

`budget.py` publishes seventeen ceiling keys (`budget.py:13-51`) and enforces none of them. The
module docstring is unambiguous: "P1 holds and publishes values; P1 enforces none of them.
Reading a ceiling is not enforcing it" (`budget.py:6-7`).

The arithmetic: §8.6 names twelve ceilings; three of them are held by two parts on different
graphs and are namespaced `grouping.*` / `placement.*` (O10), giving fifteen; the sixteenth is
`evidence.context_window`, ratified 2026-08-20; the seventeenth is `tree.max_depth`, 2026-08-29.

**The 2026-08-29 split.** The list previously carried one key,
`tree.max_folder_proposals_and_depth`, because `00`:256 names two numbers on one line —
"Maximum folder proposals and maximum depth". Every other line in that list is one quantity;
this one is two, and P10 was reading the single value four times: how many options the picker
offers, how deep a candidate may go, how wide a date level may be, and the sample size of the
printed lists. The first two want opposite values — `00`:78's own recommended tree is five
levels deep, and a picker offering five options per branch is not a picker — so no P10 change
could reconcile them, and a test named
`test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` failed for as long as the key
was one (`budget.py:28-40`). The split publishes what §8.6 already names.

`evidence.context_window` was added because §2.8 requires surrounding context be stored and
§8.6 forbids silent truncation, yet none of the other sixteen is a context length — so the
budget had nowhere to live and P4 held it caller-supplied with no number. It belongs in the
extraction run's `config` fingerprint too: a ceiling outside the fingerprint makes two runs at
different context widths look identical to §3.4's cache key and §8.5's replay
(`budget.py:43-50`).

Access is guarded by `_check` (`budget.py:62-66`): reading or writing a key outside the
seventeen raises `KeyError`. `set_ceiling` bumps `object_version` on every write
(`budget.py:72-77`), which is what lets a replay pin the values it ran under. Consumers name
their own keys and assert at import that P1 publishes them —
`extractors/budgets.py:35-40` raises `ImportError` if P5 names a key P1 does not.

**What a live run actually does with this.** `_bootstrap` (`cli.py:531-533`) sets ceilings for
`CEILINGS.values()` imported from `placement.config` — seven keys (`placement/config.py:26-34`)
— all to the same value, 8 (`cli.py:123`). The other ten keys are never written. Grouping and
tree design read their ceilings through `get_ceiling` in their own config modules
(`grouping/config.py:67`, `tree_design/config.py:88`), where a missing value raises
`ConfigurationRequired` — but the CLI bypasses both by constructing `TreeLimits` and
`GroupingLimits` in Python with different numbers entirely (`cli.py:126-144`:
`max_folder_proposals=4, max_depth=5`, `max_retrieved_neighbors=50`). So the two keys split out
on 2026-08-29 are published by P1 and read from the database by nobody in the live path.
`facts/budgets.py:34` still says "P1 publishes sixteen".

---

## What looks wrong here

Ordered by how much a reader should press.

1. **The standing rule protects one file extension.** `PROTECTED_BUNDLE_SUFFIXES = (".app",)`
   (`exclusion.py:66`) is the entire authored membership. The `extra` predicate that was meant
   to carry a deployment's additions is threaded through `is_protected_container` but reaches
   the scan through no call path: `traversal.py:73` and `traversal.py:118-119` both omit it, and
   `walk()`/`scan()` accept no parameter that could. `watch.py:63` and `recognition/detector.py:309`
   *can* pass one; the scan cannot. A person scanning their home directory gets `.app` bundles
   marked, and `/System`, `/usr`, keychains, `.photoslibrary` and everything else treated
   ordinarily or swept up by the unlabelled `Library` rule.

2. **"Never silently omitted" holds for one of the four exclusion rules.** Only
   `RULE_PROTECTED_CONTAINER` carries a label, only protected verdicts become `ProtectedArea`
   records (`upstream.py:290-292`), and only those print (`cli.py:880-887`). A directory with a
   `package.json` has every descendant pruned and nothing in the report says so. Deferrals —
   including `directory not readable at scan time`, which is a whole subtree the person cannot
   see into — are written to `scan_deferrals` and read by nothing that reaches a person.

3. **R5, the §8.6 progress line, is inert.** `scan_run_summary` (`summary.py:25-62`) has no
   caller anywhere in `src/`; only `tests/p3/test_p3_summary.py` invokes it. The counters the
   SPEC calls "the legibility surface" are computed by a function nothing calls. `scan_deferrals()`
   and `file_path_history()` are in the same position — tested, and unreachable from any
   production path.

4. **`curation_signal` is a constant.** `inventory.py:42-53` returns `undetermined`
   unconditionally, and `candidates.py:302`'s `folder.curation_signal == _CURATED` is therefore
   always False. §1.1's "existing folder structures should mainly be preserved" has an
   observation pipeline, a database column, a validated vocabulary and no decision behind it.
   Similarly `RULE_CATEGORY` (`exclusion.py:139-142`) can never fire, because all five category
   memberships are empty.

5. **The `scan_state` fix removed one instance of a class of defect, not the class.** The only
   check on the value is "non-empty string" (`production.py:123-126`), the constant lives in
   P9's vocabulary module rather than P1's or P3's (`grouping/vocabulary.py:91`), and the
   failure mode is silent: every group becomes a group of one and every test stays green. Ask
   what else in this codebase is a string agreed on by convention between a writer and a reader
   that no schema, enum or assertion connects.

6. **P1's budget object is authoritative for one consumer.** Seven of seventeen keys are set,
   all to 8 (`cli.py:531-533`, `placement/config.py:26-34`); grouping and tree read hardcoded
   Python objects instead (`cli.py:126-144`). The 2026-08-29 split of `tree.max_folder_proposals`
   from `tree.max_depth` was made to fix a real contradiction, and the numbers that resolve it
   (4 and 5) are literals in the CLI, not values in `budget_ceilings`. Press on whether the
   ceiling table is doing any work at all.

7. **Dead code and dead parameters.** `basic_record.py:103-104` is unreachable — two statements
   after `return file_id`, one of which is a second `append_stat_observation` call, i.e. an
   intended behaviour that never happens. `supersede_ddl(table)` (`supersede.py:17-19`) ignores
   its only argument. `invalidate_extraction_state`, `set_extraction_status` and
   `set_sensitivity_state` (`files_table.py:293-366`) all take `author` and `component_version`
   and use neither; the rationale is documented, but a required-and-ignored parameter reads to a
   caller as a promise that something is recorded. `database_agent/verify.py` (V1–V4) has no
   caller in `src/` because P12 does not exist.

8. **`volume_id` is written on every row and is meaningless.** `OBSERVATION_SESSION`
   (`identity.py:19`) makes the value incomparable across processes by design, so the column
   accumulates one distinct garbage prefix per run, and `file_path_history` publishes the field
   as literal `NULL` anyway (`files_table.py:489-497`). §8.2 requires the field; what is stored
   satisfies the letter and nothing else. Note also `volume_id_for` uses `os.stat`
   (`identity.py:83`) — following symlinks — while the surrounding identity code is uniformly
   `lstat` precisely so a link and its target stay two rows.

9. **The cross-volume move rule is narrower than R2 and quietly so.** `_relocated_row`
   (`files_table.py:171-216`) only recognises a move when the *oldest* recorded copy of those
   bytes is the one that vanished. The docstring argues this errs safely (an extra record, never
   a merge), and that is probably right — but it means a user who moves the second of three
   identical files across volumes gets a new `file_id`, a new `discovery` event, and no path
   history connecting it to what they moved. Whether the report ever shows them the same file
   twice is worth checking.

10. **P11 registers nine event types where the SPEC says eight and totals twenty-four.**
    `events.py:62-78` explains the discrepancy and is likely correct; the SPEC (Contract out §3)
    has not been amended, so the two documents disagree on a closed, import-frozen vocabulary.

11. **Append-only is enforced against SQL, not against the file.** The triggers and authorizer
    (`db.py:65-76`, `:265-274`) stop `UPDATE`, `DELETE`, `REPLACE`, `DROP TABLE` and
    `DROP TRIGGER`. They do not stop `PRAGMA writable_schema`, a second connection opened with
    plain `sqlite3.connect` (which installs neither authorizer nor pragma), or anything at all
    at the filesystem level. Whether the guarantee is meant to hold against a hostile process or
    only against an inattentive one is not stated anywhere.

12. **The candidate-root half of §1.1 is dead in production.** `cli.py:584` passes
    `candidate_roots=[]`, so `APPLIES_TO_CANDIDATE_ROOT`, the second `_walk_root` loop
    (`traversal.py:67-68`), the `applies_to` column on three tables, and the early return at
    `scan.py:96-97` are all exercised only by tests. `cross_folder_moves` is likewise recorded
    and read by nothing (`selection.py:31-32`).

---

# 2. Reading a file — extraction and evidence

## 2.0 The split: who reads bytes and who fixes the shape

Two parts do the work this section describes, and the division between them is
strict.

**P5 (`src/extractors/`)** knows about formats. It has one module per format family
— `pdf.py`, `docx.py`, `image.py`, `archive.py`, `structured_text.py`,
`long_tail.py`, `ocr.py`, `filesystem.py` — and a router that decides which one a
file goes to. It opens nothing itself; every actual file read arrives as an injected
callable (§2.7 below).

**P4 (`src/evidence_shape/`)** knows nothing about formats. It fixes the *shape* of
what an extractor may say: three record types, six closed vocabularies, a canonical
address string, a twelve-rule validator, and the SQLite tables all three land in. It
has no `if pdf` anywhere; `src/evidence_shape/` imports nothing from
`src/extractors/`, and the dependency runs one way only (`src/evidence_shape/store.py:376-378`
states this deliberately: "P5 depends on P4; the reverse would make the evidence layer
unbuildable without a sorter").

The consequence a reader should hold onto: **an extractor cannot invent a field, a
zone name, or an outcome word.** Every closed vocabulary lives in
`src/evidence_shape/vocabulary.py`, and `check()` (`vocabulary.py:109-117`) raises
`NotInVocabulary` on anything outside it — "No case folding, no stripping, no nearest
match." P5's own builder module says so explicitly: `src/extractors/shape.py:11-14`
declares that `zone`, segment `kind`, `source_type` and `completeness` are *not*
restated in P5 and that P4's validator is the gate.

Three records exist, and nothing else:

| Record | Module | Grain |
|---|---|---|
| `evidence` (the observation) | `evidence_shape/observation.py` | one located value |
| `extraction_runs` | `evidence_shape/runs.py` | one (file version × extractor) attempt |
| `text_units` | `evidence_shape/text_units.py` | one addressable stretch of bulk text |

---

## 2.1 The observation — one located reading of one value

`Observation` is a frozen dataclass with eighteen emitted fields
(`observation.py:126-146`). The stored row adds four more: `observation_id` and P1's
three supersede columns (`observation.py:71-73`).

### Raw and normalized are separate fields, on purpose

`raw_value` is the source substring, byte for byte. `normalized_value` is a
*candidate*, nullable, and produced only by `normalize_mechanical`
(`shape.py:275-287`), which does exactly four things: strip soft hyphens, repair
line-break hyphenation, collapse whitespace, and Unicode NFC. The docstring names the
test case: `U Chicago` stays `U Chicago`. Expanding it to `University of Chicago`
would be resolution, and resolution is P6's.

`raw_value` is never rewritten. Two mechanisms enforce it. First, the DDL
(`evidence_shape/schema.py:108-111`) installs a `BEFORE UPDATE` trigger over
`raw_value, location, occurrence_count, observed_at, extractor_name,
extractor_version, run_id` that aborts with "RAW-2: never updated; a better extractor
emits a new observation and a new run". Second, `evidence_no_delete`
(`schema.py:101-105`) aborts any DELETE at all. The only legal write to an existing
row is the three supersede columns.

An empty `raw_value` is refused at two points, both calling the *same* function:
`check_non_empty` in `observation.py:99-107`, called by the record's `__post_init__`
and by P5's builder (`shape.py:220-221`). The comment at `observation.py:81-89`
records why the second call site exists — the builder used to accept an empty raw
value and the refusal arrived at database-write time, deep in a scan.

### `occurrence_count ≥ 1`: presence only, never absence

Enforced in three places (`observation.py:165-168`, `shape.py:195-196`,
`conformance.py:174-178`). The reasoning is the same everywhere: a count of zero
would be an absence, and an absence written as evidence is a value P6 could rank. The
run record is the only home for absence.

### The locator, and why an observation with no span cannot be released

`Location` (`location.py:154-185`) is a structured record, never a per-format string:

- `zone` — one of fifteen (`vocabulary.py:22-26`): `filename`, `path`, `metadata`,
  `title`, `heading`, `body`, `table`, `header_footer`, `notes`, `link`,
  `annotation`, `reference_list`, `manifest`, `ocr`, `transcript`. It answers *what
  kind of place*.
- `container_path` — an ordered tuple of `Segment`s, outermost first. It answers
  *which one*. Twelve indexed kinds (`page`, `slide`, `sheet`, `heading`,
  `paragraph`, `table`, `row`, `column`, `cell`, `region`, `layer`, `artboard`) and
  three label-addressed kinds (`field`, `entry`, `key`) — `vocabulary.py:31-41`.
  Indices are 1-based, checked at `location.py:55-59`.
- `text_span` — 0-based, half-open, in Unicode scalar values (`location.py:62-76`).
- `time_span` — integer milliseconds (`location.py:79-93`). A location may carry one
  span or the other, never both (`location.py:181-185`).
- `region` — a bounding box, `{x, y, w, h, unit}` with `unit ∈ {px, norm}`
  (`location.py:96-111`).

The **locator** is the canonical string serialization of that record. Its grammar is
stated at `locator.py:4-9`:

```
locator := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
```

Labels are percent-encoded over `% / = # @ :` and control characters
(`locator.py:51-59`) — archive member paths contain `/`, so this is not optional.
The bounding box has no term in the grammar and is deliberately absent
(`locator.py:21-22`).

The locator is redundant with the structured fields *by construction*, and both
directions are checked: `location_from_mapping` refuses a stored mapping whose stated
`locator` does not re-serialize from its own fields (`locator.py:223-228`), and
conformance rule 4 checks `parse(serialize(x)) == addressing(x)`
(`conformance.py:192-206`). `addressing` (`locator.py:116-131`) strips descriptive
labels off indexed segments and drops the region, because those are the two things
the grammar deliberately cannot carry.

The locator is one of the four inputs to `observation_key`:

```
observation_key = sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)
```

(`observation.py:108-118`). `extractor_version` is deliberately excluded so that an
upgraded extractor's row and the row it improves on share one handle — which is what
`store._supersede` (`store.py:421-463`) pairs on, and what `observations_by_key`
(`store.py:206-212`) returns a *list* from. `sha256_of` length-prefixes each part
(`canonical.py:51-59`) because plain concatenation is not injective.

**Why a spanned observation with no unit is unreleasable.** Conformance rule 10:
every observation with a non-null `text_span` must have a `text_units` row on the
*same* `run_id` whose `container_path` equals the observation's, and RAW-1 must hold
against that row's text — `raw_value == unit.text[start:end]`
(`text_units.py:134-163`, reported through `conformance.check_run:285-298`). Without
that anchor, a citation resolves to nothing: the span is an offset into a text that
does not exist, and P8's excerpts, P13's review surface and §8.2's explanations all
cite spans. `check_span_anchor` compares on the *address*, not the record
(`text_units.py:145-153`), because a labelled `slide=6` and a bare `slide=6` are one
address and `(run_id, unit_locator)` is the primary key (`schema.py:123`).

Extractors that emit a value with no span degrade to the coarser address rather than
faking one — e.g. `image.py:193-198` emits the filename-pattern match at
`zone=filename` with no span, because the filename's text unit belongs to the
*filesystem* run and rule 10 keys units on the same run.

### Reliability: an extractor may write two of six

`RELIABILITY_STATES` has six (`vocabulary.py:53-55`); `EXTRACTOR_RELIABILITY_STATES`
has two, `direct` and `possible` (`vocabulary.py:61`). `validated`, `llm_supported`,
`user_confirmed` and `rejected` are fact-layer outcomes. Refused at
`shape.py:190-194` (`ForbiddenReliability`) and again at `conformance.py:165-171`.

In practice `direct` means an explicit labelled machine slot — a PDF metadata key
(`pdf.py:122-128`), a DOCX core property (`docx.py:154-157`), an EXIF tag
(`image.py:180-181`) — and `possible` means free text, OCR, a filename or an
unlabelled position.

### `signal_tier` and `confidence`

`signal_tier ∈ {1,2,3}` carries §2.6's image hierarchy on the record so it is never
re-derived (`vocabulary.py:82`, catalogue in `image.py:46-54`). Rule 11 checks the
structural half only: a non-null tier implies `source_type = "image"`
(`conformance.py:180-190`). P4 authors no EXIF-name-to-tier list; that is P5's
catalogue.

`confidence` is stored with **no asserted range** (`observation.py:169-175`): §3.13
says confidence is not comparable across extractors, so P4 refuses to pretend it is.
Only OCR sets it (`ocr.py:180`).

### D10 — collapsing repeats

One observation per `(run, exact raw value, zone)`; `occurrence_count` counts within
that zone and `location` addresses the first occurrence in document order.
`collapse_key` publishes the tuple (`observation.py:253-260`) but P4 enforces no
uniqueness on it. The collapse itself happens once, for every extractor, in
`ExtractionResult.__post_init__` (`sink.py:33-66`), and its docstring records that
six extractors promised D10 and two delivered it before this moved to the result
object. The collapse also renumbers, so it publishes `collapsed_index` — the map from
submitted position to surviving position — because `long_tail`'s sensitivity signals
carry batch positions (`sink.py:69-94`, consumed at `long_tail.py:346-354`).

Note that `pdf.py:185-226` and `archive.py:195-227` still run their *own* collapse
before handing the batch over. `sink._collapse` is idempotent (it sums
`occurrence_count`), so this is duplication rather than a bug — but it is two
implementations of one rule.

---

## 2.2 The extraction run — why outcomes need their own record

`ExtractionRun` (`runs.py:76-125`) is one row per (file version × extractor).
`runs.py:3-9` states the reason plainly: §2.4 forbids conflating "unsupported format"
with "empty document", §2.5 requires "partially inspected", §2.7 requires
provider/version/languages/configuration/complete-or-capped be preserved, §2.9
requires "indexed-but-unreadable", §8.6 requires the deferred stage be marked — and
**none of those can live on an observation, because the cases that need them produce
zero observations.**

Fields: `run_id`, `file_id`, `content_hash`, `extractor_name`, `extractor_version`,
`source_type`, `analysis_tier`, `config`, `config_fingerprint`, `completeness`,
`coverage`, `observation_count`, `started_at`, `finished_at`, `failure_reason`
(`runs.py:32-36`).

`coverage` is `{units, processed, total}` with `processed ≤ total` enforced
(`runs.py:62-70`, and again at `extractors/runs.py:50-64`). `config` is an opaque
mapping P4 defines no schema for; `config_fingerprint` is
`sha256_of(canonical_json(config))` (`runs.py:46-48`), and P5 *calls* that function
rather than recomputing it — `shape.py:101-124` records the incident where P5's own
`hashlib.sha256` over the same canonical bytes produced a different digest (P4
length-prefixes) and P4 therefore rejected every run P5 emitted.

### The nine `completeness` values

`vocabulary.py:63-68`:

| value | means | who writes it in `src/` |
|---|---|---|
| `complete` | ran to the end | every native extractor's success path |
| `capped` | stopped at a configured ceiling | `ocr.py:188` when the engine reports `capped` |
| `partial` | some parts readable, some not | `archive.py:177-178` only |
| `metadata_only` | deliberate safe stop, no content extractor run | `router.py:185` → `filesystem.unrouted_result` |
| `deferred` | not attempted; budget exhausted first | `budgets.py:75` — **no caller in `src/`** |
| `unsupported` | no extractor exists for this format | `failure.unsupported_result:50-81` |
| `unreadable` | encrypted, malformed, damaged; indexed-but-unreadable | `archive.py:172`, `router.py:184` |
| `failed` | a reader ran and raised | `failure.failed_result:84-104` |
| `dataless` | the bytes are not on this machine | `filesystem.dataless_result:175-231` |

`failure_reason` is free text and is *only* legal on `unreadable` and `failed`
(`runs.py:39`, enforced `runs.py:117-125`). A `capped` run did not fail;
`metadata_only` is a policy stop; `dataless` is not damage. `filesystem.py:208-216`
records that the first version of `dataless_result` wrote a `failure_reason` and P4
rejected it — correctly, because a file in iCloud has not failed.

### The load-bearing principle: a `complete` run with zero observations

`runs.py:16-18`: "A `complete` run that emitted no `metadata` observations IS the
record that the file carried no such metadata; §2.6's 'no EXIF' is exactly this case.
No field is added for it and no observation is written for it."

So three zero-observation states are distinguishable in one query:

- `complete` + 0 observations → the file genuinely contained nothing extractable.
- `unsupported` + 0 observations → **no reader exists in this deployment**; the bytes
  were never looked at (`failure.py:58-62`).
- `metadata_only` + 0 observations → a deliberate stop; the file is still indexed
  through its separate `filesystem` run (`filesystem.py:11-17`).

And `unreadable` is a fourth thing: it carries rows. `ZERO_OBSERVATION_COMPLETENESS`
(`vocabulary.py:75-76`) is `unsupported, deferred, failed, metadata_only, dataless` —
`unreadable` and `partial` are deliberately absent, so an indexed-but-unreadable PSD
keeps its filename and format rows (`filesystem.py:130-156`, fixture 18). Rule 9
checks this at `conformance.py:252-255`.

### Analysis tier

`filesystem | native | ocr | llm` (`vocabulary.py:79`). P5 writes the first three and
`shape.run` raises `ForbiddenAnalysisTier` on `llm` (`shape.py:252-256`).
`extraction_status_by_tier` (`extractors/runs.py:80-101`) folds a file's runs into
the map P1 stores opaquely, and raises `TierConflict` if two runs at one tier
disagree rather than picking a winner. This is why an unrouted or dataless run is
stamped `format.unrouted` at tier `native` rather than reusing `filesystem.record`
(`filesystem.py:32-40` records that the earlier spelling raised `TierConflict` on the
first `.dmg`).

---

## 2.3 Dispatch — how a file reaches an extractor

Two modules, deliberately separate.

**`router.py`** decides. `route()` (`router.py:205-242`) takes an injected
`detect_format`, computes `operative = detected or declared_extension`, records
`disagree` when they differ, looks up `SOURCE_TYPE_BY_FORMAT` (a 50-entry table,
`router.py:40-149`), then `HANDLER_BY_FORMAT` (only `pdf` and `docx` have dedicated
handlers) and finally `HANDLER_BY_SOURCE_TYPE` (`router.py:159-173`). A file with no
handler leaves with `unrouted_completeness` from `UNROUTED_COMPLETENESS`
(`router.py:183-186`): `design_creative → unreadable`, `opaque_binary →
metadata_only`, everything else → `unsupported`. The decision is persisted to P5's
own `extraction_routing` table (`router.py:245-279`), which is not one of P4's three.

The table is honest about its provenance: `router.py:89-115` marks the WebP/GIF/TIFF/
BMP/AVIF/HEIF keys as **inference**, not design text, and `router.py:122-148` does
the same for the five audio/video extensions.

**`dispatch.py`** executes. `extract_initial` (`dispatch.py:153-230`) switches on
`decision.extractor_name`. The interesting case is `text.structured`, which serves
*eight* source types through two halves: `structured_text.py` claims
`text_document, code_structured` and `long_tail.py` claims the other six. Since both
halves answer to one extractor name, the **source type** picks the half
(`dispatch.py:206-225`). `dispatch.py:16-21` records that without this a real corpus
raised `WrongFamily` on its first `.xlsx` while every unit test still passed.

A format nothing supports never reaches this switch — the router already returned
`extractor_name = None`, and `extract_initial:163-165` produces `unrouted_result`
instead. A router that names a handler nothing implements raises `UnknownFamily`
(`dispatch.py:296-307`), which is a `ContractViolation` — a statement about the call,
not the file — and therefore propagates past the orchestrator's catch-all
(`orchestrator.py:312-321`) rather than being recorded as that file's `failed` run.

### Route by extension, not by sniffing

`detect_format` is injected, and the shipped one is:

```python
return {".pdf": "pdf", ".txt": "txt", ".md": "md"}.get(path.suffix.lower())
```

(`cli.py:341-348`). Its docstring states the reason: "sniffing means opening the
file, and the one class of file this command must never open is decided by PATH
(`is_protected_container`) before any format question is asked."

That gate is `safety.admit` (`safety.py:49-70`), called as the **first statement of
every extractor** (`pdf.py:103`, `docx.py:116`, `image.py:133`, `archive.py:121`,
`structured_text.py:109`, `long_tail.py:223`, `ocr.py:152`, `filesystem.py:63`). It
raises `ProtectedContainerRefused` — "There is no override" — before the reader is
touched, and the protected check runs before the dataless check because inside a
protected container P5 must not even stat the contents. `SafetyPolicy`
(`safety.py:38-47`) has exactly two fields "and deliberately no third: a `force`,
`override` or `approved` field would be the override 11 section 4b says does not
exist."

The two refusals are asymmetric, and the orchestrator owns the asymmetry
(`orchestrator.py:594-600`): a protected container produces **nothing at all** — no
run row, no status write — while a dataless file produces one `dataless` run,
because its identity is already known and §8.6 requires unfinished work to stay
visible.

---

## 2.4 The readers layer — every format library is injected

`src/extractors/` imports no third-party library. `reading.py:3-8` states the rule
and `readers/__init__.py:4-12` restates the direction: `readers/` depends on
`extractors/` for the shapes it fills, never the reverse.

`Readers` (`dispatch.py:56-77`) is the injection point — twelve callables:
`read_pdf`, `read_docx`, `read_text_document`, `read_long_tail`, `read_manifest`,
`read_image`, `find_structured_strings`, `recognize_markers`, `dimension_signal`,
`filename_pattern`, and optionally `ocr_engine` + `ocr_config`. `ocr_engine` may be
`None`, which is a *deployment* state: §2.2's and §2.7's OCR routes simply stop, and
no run is written (`dispatch.py:131-132`).

Each reader has a declared return shape as a frozen dataclass: `PdfDocument`
(`pdf.py:56-68`), `DocxDocument` (`docx.py:86-95`), `ImageRecord`
(`image.py:91-106`), `ArchiveManifest` (`archive.py:60-75`), `TextDocument`
(`structured_text.py:87-94`), `LongTailFile` (`long_tail.py:118-125`), `OcrOutput`
(`ocr.py:100-112`). A reader that returns `None` means "this deployment ships no
library for this format" and becomes an `unsupported` run.

### What macOS actually supplies

`readers/deployment.py:59-86` wires exactly three real readers:

- **`read_pdf`** → `pdfminer_reader()` (`readers/pdf_pdfminer.py`). Chosen because
  `Region`'s contract needs per-character font size and position to produce honest
  heading zones (`pdf_pdfminer.py:4-12`). It also renders PDF date syntax into
  `iso_dates` (`pdf_pdfminer.py:63-79`), which is D8's fourth mechanical transform.
- **`read_text_document`** → `read_text_file`, which does one thing: decode UTF-8
  with `errors="replace"`. No heading detection, on purpose (`deployment.py:48-56`).
- **`ocr_engine`** → `vision_ocr()` (`readers/ocr_vision.py`), Apple Vision via
  PyObjC/Quartz. It rasterises PDF pages at the configured DPI
  (`ocr_vision.py:72-86`), numbers regions *within* their page, and flips Vision's
  bottom-left origin to top-left because P4's `Region` carries no origin key
  (`ocr_vision.py:119-141`).

Everything else — `read_docx`, `read_long_tail`, `read_manifest`, `read_image` — is
`_no_reader`, returning `None` (`deployment.py:43-45, 72-76`). `recognize_markers`,
`dimension_signal` and `filename_pattern` are stubs returning `()` / `None`
(`deployment.py:77-82`).

**So on the shipped macOS deployment, only PDF, TXT and Markdown are actually read.**
DOCX, spreadsheets, presentations, email, calendar, contacts, archives and images all
route to a real extractor whose reader returns `None`, and therefore record
`unsupported`.

`VISION_CONFIG` (`deployment.py:36-40`) is `{languages: ["en-US"], dpi: 200,
recognition_level: "accurate"}`. It is a `config` mapping, not constructor arguments,
precisely so it lands in `extraction_runs.config` and is fingerprinted into §3.4's
cache key.

---

## 2.5 Structured strings — the seam P5 ships empty

`StructuredString` (`reading.py:35-47`) is `{kind, start, end}`. Its docstring is
explicit: "no pattern lives in `src/extractors/` and the finder is supplied by the
caller." `find_structured_strings: Callable[[str], tuple]` is a required field of
`Readers` with no default, and `deployment.py:14-19` explains why a default returning
`()` would be *worse* than none: "it silently claims a file contains no URLs, no
emails and no identifiers, and every downstream count would agree with it."

Every text-bearing extractor calls it and places what it returns: `pdf.py:150-167`,
`docx.py:170-175`, `structured_text.py:162-177`, `long_tail.py:307-318`,
`ocr.py:164-181`. Placement is by `ZONE_BY_STRUCTURED_KIND` (`reading.py:56-61`):
`url`, `email`, `doi` → `link`; `citation` → `reference_list`; anything else takes
the zone of the region it was found in.

### What the shipped deployment supplies: one regular expression

`cli.py:188`:

```python
_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")
```

`find_structured_strings` (`cli.py:304-307`) emits every match as
`kind="identifier"`. That is the whole of it. No URL pattern, no email pattern, no
DOI pattern, no citation pattern ships — so `ZONE_BY_STRUCTURED_KIND` never fires in
production, and the `link` and `reference_list` zones are unreachable on a live scan.

The comment block (`cli.py:170-187`) records both the posture and one change: the
`[ -]?` separator was added on **2026-08-29** so that `PHYS 1401` and `PHYS-1401`
read as identifiers. The recorded cause is that the first run on a real folder
returned `NothingToDesign` because the files said `PHYS 1401` and the pattern wanted
`PHYS1401`.

Verified behaviour of the current pattern:

| input | matches |
|---|---|
| `PHYS 1401 syllabus` | `PHYS 1401` |
| `Invoice INV20261` | `INV20261` |
| `ABC-4471 x` | `ABC-4471` |
| `see 2026 budget` | *(none)* |
| `Chapter 12` | *(none)* |

A bare year, a page number, a sum of money and ordinary prose are all invisible to
it. So is `phys 1401`, and so is a course code written `Phys 1401`.

---

## 2.6 OCR — policy, the deferred stage, and the two text-layer paths

### The policy module holds no heuristic

`ocr_policy.py` names §2.2's three states (`ocr_policy.py:33-35`):

- `text_layer_absent` — no text at all → route directly to OCR.
- `text_layer_broken` — text exists, but the stored evidence yields no usable facts →
  **targeted** OCR, and only after P6 says so.
- `text_layer_usable` — no OCR.

The state is neither an observation nor a run field. `ocr_policy.py:11-16` is
explicit: an extractor may not write a "no text layer" observation, because an
absence written as evidence is a value P6 can rank. The requirement that the two be
*distinguished* is met by the two paths behaving differently.

There is no language-quality check anywhere in P5, and `ocr_policy.py:18-23` says so
outright — the only permitted input about a non-empty text layer is P6's injected
`no_usable_facts(file_id, content_hash)` verdict, with no default. The threshold
behind that verdict is P5 SPEC Open question 1 and is not answered in code.

### The two passes

`extract_initial` runs the native PDF pass, then calls
`direct_document_ocr_needed(result=...)` (`ocr_policy.py:56-63`) — which is just "did
this run store any non-blank text?" — and OCRs immediately if not
(`dispatch.py:171-181`).

`extract_targeted_ocr` (`dispatch.py:233-272`) is the second, post-P6 pass, PDF-only.
It verifies that the supplied prior result really is *this* file version's native
`pdf.text` run (`dispatch.py:249-260`) and raises `ContractViolation` on any
mismatch, then asks `document_ocr_decision`, which asks `no_usable_facts`.

For **images**, `image_ocr_decision` (`ocr_policy.py:135-149`) fires when the run
yielded no usable text *and* no usable metadata. "Usable metadata" is narrowed to
`signal_tier ∈ {1,2}` (`ocr_policy.py:72, 96-98`) — the docstring at
`ocr_policy.py:75-98` records that counting *any* `zone=metadata` row made §2.7's
main path dead, because `image.py` emits `format` and `pixel dimensions` for every
image and an opaque PNG screenshot therefore always looked like it had metadata.

### The OCR run itself

`extract_ocr` (`ocr.py:140-195`) writes one `text_units` row per recognised page or
region, and observations only for the structured strings found inside them. The
extractor name is built from what the engine reports —
`extractor_name_for("Apple Vision") → "ocr.apple_vision"`
(`ocr.py:120-137`), folding case and word breaks so one engine has one identity
across machines. `extractor_version` is the *provider's*, which is why
`current_versions()` deliberately omits OCR (`dispatch.py:324-328`): P5 cannot state
a version it would have to ask an uninstalled engine for.

`FIELD_HOMES` (`ocr.py:71-81`) maps §2.7's nine required fields onto records P4
already publishes — no OCR-specific record and nothing OCR-specific on an
observation.

An engine that *raises* becomes a `failed` OCR run rather than propagating
(`dispatch.py:115-150`); the docstring records the incident where a raising engine
discarded a native result that had already succeeded.

### The deferred stage and budget exhaustion — the honest answer

`budgets.py` names four §8.6 ceilings in P1's spelling
(`budgets.py:29-34`): `ocr.max_pages_per_file`, `ocr.max_time_per_file`,
`ocr.max_time_per_scan`, `image.max_analysis_ops_per_scan`. A membership check at
import turns a P1 rename into an `ImportError` (`budgets.py:36-41`).

`deferred_result` (`budgets.py:60-76`) is the run for an extractor the budget stopped
*before it started*: zero observations, `coverage 0/total`, and **no
`failure_reason`** — "a deferral carrying a failure reason reads as a failure."
Nothing here downgrades: `budgets.py:12-14` says there is no fallback extractor, no
filename guess, and nothing to downgrade to.

A budget exhausted *mid-read* is a different value: the engine reports `capped` and
the run keeps what it recognised, with `coverage` saying how far it got
(`ocr.py:188-190`). `ocr_vision.py:184-209` is the only place in `src/` that can set
it — it breaks the page loop on `page_cap` or `time_limit_seconds` and sets
`capped=stopped_early`, distinguishing "a limit stopped this" from "the document
ended".

**But:** `VISION_CONFIG` supplies neither `page_cap` nor `time_limit_seconds`
(`deployment.py:36-40`), and `settings.get(...)` therefore returns `None` for both
(`ocr_vision.py:156-157`). And nothing in `src/` imports `extractors.budgets` at all.
So on the shipped deployment, `capped` never occurs and `deferred` is never written.
The SPEC ratification B3 says the four ceilings "stay unset until a real OCR engine
is wired, then chosen empirically" — the engine is wired and the ceilings are still
unset.

---

## 2.7 Golden fixtures — building downstream parts with no extractor present

`evidence_shape/fixtures.py` publishes the SPEC's nineteen worked examples as
constructed records, not files (`fixtures.py:9-12`: a JSON file would need a loader
that reconstructs exactly what this module already constructs). P4's Done-means 9
requires that "P6 resolves `course = BUSIB 4300` from fixture 1 with no extractor
present", and `privacy/fixtures.py:67` shows a downstream part consuming them for
real.

Each `Fixture` (`fixtures.py:56-64`) is a number, the design case it comes from, one
`ExtractionRun`, its observations and its text units. Fixture 1 is the walking
skeleton (a syllabus heading at `page=1/heading=2`); fixture 8 is an OCR region with
a `norm` bounding box and confidence 0.92; fixture 11 is a span into a *filename*;
fixture 17 is a caption addressed by `time_span`; fixture 18 is an `unreadable` run
that still carries a metadata row; fixture 19 is a `metadata_only` run with no
observations at all.

The coverage shortfall is **computed and published rather than filled**
(`fixtures.py:14-17`, `fixtures.py:247-260`). Verified by running it: the fixtures
cover 10 of the 15 zones — `path`, `header_footer`, `link`, `annotation` and
`reference_list` have no worked example — and 13 of the 14 source types (`contacts`
is missing). No fixture carries a `signal_tier`, because §2.6 makes
`DateTimeOriginal` both camera EXIF and a capture time and the design does not settle
which tier wins (`fixtures.py:19-22`).

---

## 2.8 The write seam

An extractor returns one `ExtractionResult` — run + observations + text units, none
carrying a `run_id` (`sink.py:22-31`). `RunWriter` (`store.py:360-419`) is the sink:
it mints the `run_id`, refuses a batch that carries one (`store.py:387-395`),
validates the whole batch through `validate_run` *before* the run row exists, then
writes run → text units → observations → the one §8.2 event, in one transaction.

The event is last because its evidence reference is the observation keys, which do
not exist until the rows do (`store.py:9-13`, `record_run_event:95-117`). P4 authors
no event: `author` is required at construction and `P1` is refused
(`evidence_shape/authorship.py`), because M8 says the acting part authors and P1
writes.

`record_observation` (`store.py:120-145`) recomputes the run's `observation_count`
from the rows on every insert — a stored count that disagrees with the rows is a fact
nobody downstream can use.

`observation_keys_for_run` (`store.py:174-198`) orders by `rowid`, and its docstring
records the bug that made this necessary: it once ordered by `observation_id`, a
uuid4, so `long_tail`'s sensitivity signals attached to the wrong values.

Conformance is twelve rules (`conformance.py:43-71`). `check_observation` reports
*every* violation before raising (`conformance.py:8-9`), because a gate that stops at
the first problem makes an extractor author fix one thing per run. Rule 8
(determinism) needs two runs and lives in `determinism.py`; its comparison excludes
`run_id`, `observed_at` and `file_id` (`determinism.py:53`) and keys on four fields
rather than rule 8's stated three — `determinism.py:17-23` reports that SPEC/design
discrepancy rather than resolving it.

---

## 2.9 Inert surface — concepts with no live reader

Verified by grepping `src/` for callers:

- **`extractors/budgets.py` entirely.** Nothing imports it. `deferred_result`,
  `p5_ceilings` and `extraction_counts` have no caller, so the `deferred`
  completeness value is unreachable on any live scan and the four §8.6 ceilings are
  never read from P1.
- **`extractors/stage_output.py` entirely.** `extraction_stage_output` and
  `extractor_versions` have no caller in `src/`; §8.5's extraction envelope is never
  produced live. `facts/stage_output.py:10` cites it as the pattern it follows.
- **`extractors/runs.py:analysis_tier_for`** — no caller. It would also `KeyError` on
  `format.unrouted`, which is a name `current_versions()` publishes
  (`dispatch.py:339`).
- **`extractors/runs.py:cache_key`** — no caller. §3.4's cache key is never computed.
- **`evidence_shape/determinism.py`** — `observation_set_digest` and
  `assert_identical_observation_sets` have no caller in `src/`. Rule 8 is never
  checked outside tests.
- **`evidence_shape/conformance.py:validate_observation`** — no caller; only
  `validate_run` is used (via `RunWriter`).
- **`extractors/events.py`** — says so itself at `events.py:24-25`: "NOTHING IN
  `src/` CALLS EITHER ONE."
- **`ocr.PERSISTED_FIELDS` / `ocr.FIELD_HOMES`** — documentation tables with no
  reader in `src/`.
- **`observation.SECTION_2_8_LINES`**, **`observation.collapse_key`**,
  **`router.routing_decisions`**, **`safety.UNTOUCHED_PROTECTED`** — no `src/`
  caller.
- **`ZONE_BY_STRUCTURED_KIND`'s four keys** — live code, but unreachable in
  production, because the only shipped pattern emits `kind="identifier"`.
- **Vocabulary members nothing writes:** `deferred`; the `heading`-only subset of
  `LABEL_SEGMENT_KINDS` is used, but `cell`, `layer` and `artboard` segment kinds are
  written by no extractor in `src/`; the `header_footer` zone is written only by
  `docx.py` (whose reader is unwired), and `annotation`, `link` and `reference_list`
  likewise.

---

## What looks wrong here

1. **`vocabulary.py:63` says "B1's eight" above a tuple of nine values.** The P5 SPEC
   Done-means 1 also says "one of the eight enumerated values" and the P4 SPEC's
   `completeness` table lists eight rows — `dataless` (ratified C4, 2026-08-20) was
   added to the code and not to either table. `stage_output.py:56` and
   `stage_output.py:91` say nine. Two documents and one comment disagree with the
   code.

2. **The whole budget layer is inert, and `capped` is unreachable on the shipped
   deployment.** `VISION_CONFIG` (`deployment.py:36-40`) passes no `page_cap` and no
   `time_limit_seconds`, and nothing imports `extractors.budgets`. P5 SPEC Done-means
   9 requires "the 400-page fixture is marked `capped` rather than `complete`"; live,
   a 400-page scanned PDF is OCRed to the end with no ceiling. §8.6's
   "89 scanned PDFs deferred after the OCR limit" line cannot be produced.

3. **A scanned PDF in a deployment with no OCR records `complete`.**
   `extract_pdf` hardcodes `completeness="complete"`
   (`pdf.py:178`) regardless of whether any text came out, and if `ocr_engine` is
   `None` the OCR run simply does not happen (`dispatch.py:131-132`). P4's own
   semantics say `complete` + zero observations means "the file genuinely contained
   nothing extractable" (`runs.py:16-18`) — which is precisely the false statement
   §2.4 exists to prevent. The same applies to `docx.py:213`,
   `structured_text.py:185`, `image.py:206` and `long_tail.py:328`: five of the six
   native extractors can only ever write `complete`.

4. **Images reach OCR because a reader is missing, not because the image is
   opaque.** `read_image` is `_no_reader` (`deployment.py:75`), so `extract_image`
   returns `unsupported_result` with zero observations and zero text units
   (`image.py:137-142`); `image_ocr_decision` then sees no text and no
   tier-1/2 metadata and returns `run_ocr=True` (`ocr_policy.py:143-149`). Every
   routed image on the live deployment therefore produces
   `image.metadata · unsupported` plus a full Apple Vision run. §2.7's trigger is
   being satisfied by a deployment gap rather than by a fact about the image.

5. **`_detect_format` recognises three extensions**, so `disagree` is always `False`
   and `detected_format` is `NULL` for everything except `.pdf`, `.txt`, `.md`
   (`cli.py:341-348`). P5 SPEC Done-means 10 ("routing follows signature over
   extension on the disagreeing fixture") cannot be exercised live, and
   `router.route`'s detected-wins branch (`router.py:214-215`) is dead in production.
   The `unreadable` path in `unrouted_result` also emits its `format` observation
   only `if detected` (`filesystem.py:147-156`), so an indexed-but-unreadable file
   gets a filename row and no format row.

6. **Targeted OCR is switched off by a lambda.** `usable_threshold=lambda facts,
   unresolved: True` (`cli.py:392`) with the comment "targeted OCR is never
   triggered". So §2.2's `text_layer_broken` path — the whole reason
   `no_usable_facts`, `extract_targeted_ocr`, `authoritative_result` and the
   two-phase orchestrator exist — never fires. A large amount of machinery
   (`dispatch.py:233-272`, `store.py:272-302`, `orchestrator.py:660-706`) is live
   code reachable only by changing that lambda.

7. **One shipped regular expression is the entire structured-string catalogue.**
   `\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b` (`cli.py:188`) means the product's *only*
   in-document evidence beyond metadata and headings is an uppercase-then-digits
   token. It misses `Phys 1401`, every URL, every email address, every DOI and every
   citation — and `deployment.py:14-19` argues at length that a finder returning `()`
   would be a lie, which is close to what a finder this narrow does for most content.
   It will also match `A 1234` in ordinary prose.

8. **D10 is implemented twice.** `sink._collapse` (`sink.py:69-94`) collapses every
   batch, and `pdf._collapse` (`pdf.py:185-226`) and `archive._collapse`
   (`archive.py:195-227`) collapse again beforehand with a slightly different
   mechanism (candidate objects vs. dicts). The result is idempotent today, but this
   is exactly the "one concept, two homes" defect the codebase's comments repeatedly
   name as its costliest.

9. **D10 collapses across container paths, and rule 10 is checked only on the
   survivor.** The key is `(zone, raw_value)` (`sink.py:83-84`) with no container
   path. Two identical strings in two different table cells become one observation
   whose `location` addresses the first — which is D10 as specified, but it means
   `occurrence_count` silently spans places the record no longer names, and P6's
   §3.7 zone weighting sees one row where the document had two positions.

10. **`ExtractionResult.__post_init__` mutates a frozen dataclass** via
    `object.__setattr__` on every construction (`sink.py:61-66`), including
    overwriting the `observation_count` the extractor computed. The count on the run
    is therefore never the extractor's own number, which contradicts
    `stage_output.py:117-140`'s claim that it is ("Both are P4's own numbers, counted
    by the extractor").

11. **`extraction_counts` exists twice under two owners.** `budgets.py:79-103` (P5,
    uncalled) and `eval_harness/counts.py:31-73` (P2, called) compute §8.6's line
    with different bucket sets — P2's version added a `dataless` bucket that P5's
    lacks, and P2's own docstring admits its `files_indexed` disagrees with P5's
    mapping and reports both.

12. **The fixtures do not meet P4's Done-means 5.** It asks for "all 14 zones and all
    14 source types"; there are 15 zones (`vocabulary.py:22-26`) and the fixtures
    cover 10 of them and 13 of 14 source types. The shortfall is honestly published
    (`fixtures.py:255-260`) rather than hidden — but a downstream part built only
    against fixtures has no worked example for `link`, `annotation`,
    `reference_list`, `header_footer`, `path` or `contacts`.

13. **`analysis_tier_for` would crash on a name the same package publishes.**
    `ANALYSIS_TIER_BY_EXTRACTOR` (`extractors/runs.py:17-24`) has no entry for
    `format.unrouted`, which `current_versions()` returns (`dispatch.py:339`) and
    which every unrouted and dataless run carries. The function has no caller today,
    so this is latent rather than live.

14. **`observation_count` is corrected by the sink but `coverage` is not.** An
    `unsupported` run reports `coverage {files, 0, 1}` (`failure.py:78`) while a
    `complete` PDF reports `{pages, n, n}` (`pdf.py:178`) — the `units` string is
    caller-supplied with no vocabulary (`runs.py:56`), so `files`, `pages`,
    `entries`, `images` and `paragraphs` all appear. Any consumer aggregating
    coverage across runs is adding incommensurable numbers.

15. **`UNREPORTED_PROVIDER_NAME = "ocr"`** (`ocr.py:56`) is stamped as the
    `extractor_name` when an engine crashes before reporting itself, and the module
    flags its own spelling as unsettled ("Whether this is the right spelling is a
    vocabulary question -- see NEEDS-JOSEPH"). It is also the one `extractor_name`
    that does not match `OCR_EXTRACTOR_PREFIX = "ocr."`, so
    `analysis_tier_for("ocr")` would fall through to the dict and `KeyError`.

---

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

---

# 4. The privacy gate and the model harness

P7 and P8 are one story told in two halves. P7 decides whether anything about a file may
leave the machine and mints a single-use token that says so. P8 is the only thing in the
product that could spend one. Neither half is exercised on the run the product actually
ships, and the interesting part of this section is exactly *why* that is true and what it
costs.

Everything below was read out of `src/`. Where a SPEC promises something the code does not
do, the section says so and cites the line.

---

## 4.0 Two corrections to the map before we start

Two things a reader arriving from the SPECs or from a briefing will have wrong.

**The module names differ from the SPEC's prose.** `src/privacy/` holds twenty-two modules,
not the seven a summary would name: `gate.py`, `release.py`, `denial.py`, `consent.py`,
`policy.py`, `defaults.py`, `binding.py`, `items.py`, `redaction.py`, `resolve.py`,
`classification.py`, `classification_store.py`, `audit.py`, `moves.py`, `display.py`,
`revocation.py`, `learning_seam.py`, `transport_guard.py`, `schema.py`, `vocabulary.py`,
`authorship.py`, `fixtures.py`. The decomposition matters: several of the properties P7
claims are structural are structural *because* a rule lives in a module that cannot reach
the thing it must not touch.

**A detector does ship, and it is wired.** The claim that "no detector ships" is false as of
this commit. `src/recognition/detector.py` implements `orchestrator.ClassificationProducer`;
`src/cli.py:565` constructs one from a compiled 358-row rule library and hands it to the
production run at `src/cli.py:393`; `src/orchestrator.py:713` calls it once per file version
and `:722` writes the result. What is true — and what makes the "no detector" claim
*directionally* right — is that the detector is deliberately built so that it classifies
almost nothing. §4.1 works through why.

---

## 4.1 What a handling class is, and how a file gets one

### The closed set

§8.4 names five handling classes. `src/privacy/vocabulary.py:86-92` publishes them in the
design's order:

```
public_low · personal_non_sensitive · sensitive_personal ·
highly_sensitive_credential_bearing · unreadable_unclassified
```

Closed means a caller may not add a member. `check_handling_class` (`vocabulary.py:105`)
routes through `_check` (`vocabulary.py:58`), and `_check` does something unusual: it
refuses an outsider **without naming any member of the set**. The docstring gives the
reason — `check_handling_class("public")` answering with a suggestion of `public_low` is how
a misspelling becomes a silent downgrade, which is the failure §8.6 names by name
(`vocabulary.py:59-67`). The design's own vocabularies are carried beside the identifiers as
prose (`HANDLING_CLASS_LABELS`, `vocabulary.py:96`; `MODE_SEMANTICS`, `vocabulary.py:119`)
so that a paraphrase is a failing test rather than a drift.

### The record

`ClassificationRecord` (`classification.py:107`) is eight fields: `file_id`, `content_hash`,
`handling_class`, `protected`, `basis`, `evidence_refs`, `reliability_state`, `observed_at`.
Three of its construction-time checks are load-bearing:

- **It is keyed on bytes.** `content_hash` is required non-empty. A classification is about a
  file *version*; new bytes at a path inherit nothing (`classification.py:10-13`).
- **`basis = detector` must carry evidence.** `classification.py:155` raises
  `UnbackedClassification` for a detector classification with an empty `evidence_refs`,
  quoting §8.4's "evidence-backed". `user` and `safety_domain` are exempt — the user's act
  *is* the evidence, and a safety domain is a rule about a domain rather than a reading of a
  span (`classification.py:70-72`).
- **Every ref must be a P4 `observation_key`, never an `observation_id`.**
  `_is_observation_key` (`classification.py:92`) validates by *shape*, derived at import from
  one probe key (`classification.py:77-79`) so that a change in P4's hashing propagates
  rather than drifting. The reason is M14: a per-row id dies on extractor upgrade, so a
  negative example recorded today would silently stop resolving and the same false
  protection would return (`classification.py:163-167`).
- **`protected` is supplied, never derived.** `classification.py:142` requires a real bool
  and the docstring cites Open question 1 — whether `protected` is exactly the top two
  classes is unsettled, so nothing in the codebase infers one from the other.

### The store

`ClassificationStore` (`classification_store.py:117`) is concrete, not injected — D2 removed
the old `SensitivityFacts` seam. It never overwrites: the table has a `BEFORE UPDATE` trigger
over all eight published fields (`schema.py:63-67`) and a `BEFORE DELETE` trigger
(`schema.py:58`), so supersession is the only legal write to an existing row. The index is
deliberately **not** unique (`schema.py:52`) — an early detector and a later one may disagree
and both survive, which is §8.2's own OCR example.

`current` resolves several live rows through `strongest` (`classification_store.py:88`),
which ranks by §3.13's six reliability states in the design's listed order, derived from P4's
tuple with `rejected` removed in place (`classification_store.py:56`). A tie raises
`AmbiguousCurrentClassification` rather than picking.

### How a file actually gets one, today

`recognition/detector.py` is two steps with a contract between them. *Recognition* says which
domain schema a file version's own P4 observations make plausible. *Classification* says
which handling class it carries. The rule library carries no handling class at all —
`planning/domains/_CONTRACT.md` rule 5 forbids it: "A catalogue that assigns one is inventing
P7's vocabulary" (`detector.py:11-14`). So `handling_for` is an injected map with no default.

`Detector.explain` (`detector.py:296`) runs, in order:

1. **Protected container first, before any evidence is read.** `is_protected_container` is
   P3's own predicate, and a hit returns `Abstention("protected_container", ...)` whose
   sentence is *"marked, counted and never opened; it is unclassified because nothing
   looked, not because nothing was found"* (`detector.py:309-314`).
2. No authored term matched → `Abstention("no_evidence")`.
3. Fewer than two distinct matched terms for the leading schema → `Abstention`
   `"no_corroboration"`. All 358 rows set `file_kinds.never_alone: true`, read literally as
   "two" (`detector.py:24-32`, `:330-338`).
4. Leading schema implausible for this file kind → `"file_kind_implausible"`.
5. Two schemas tied → `"ambiguous"`. Nothing breaks the tie; a tie-breaker would be the
   invented threshold this package exists without (`detector.py:354-356`).
6. Schema recognised but the caller's `handling_for` states no class for it →
   `"unassigned_handling"`. "Recognition is not classification" (`detector.py:367-378`).

`cli.py:566` passes `handling_for=SAFETY_DOMAIN_HANDLING`, which covers exactly four schema
ids — `finance`, `identity`, `medical`, `legal` (`recognition/vocabulary.py:64`) — each
mapped to `sensitive_personal`, `protected=True`, `basis=safety_domain`
(`detector.py:117-121`). The class is the detector's own hand-authored choice and says so:
`00` names five classes and never says which one a safety domain carries
(`detector.py:106-116`).

**Consequence.** Every file that is not decisively one of four safety domains, on two or more
authored terms, on a plausible file kind, with no tie, resolves to `Abstention`.
`Detector.__call__` (`detector.py:392`) turns an `Abstention` into `None`, and
`resolve_class(None)` returns `unreadable_unclassified` (`classification.py:179-180`). On an
ordinary folder of coursework, invoices and screenshots, the overwhelming majority of files —
plausibly all of them — carry no classification record at all.

### Why absence never resolves downward

`resolve_class` is four lines and its docstring is the whole argument: a file that has not
been classified has not met §8.4's precondition for escalation, "so the gate denies it rather
than guessing at it downward" (`classification.py:170-186`). There is no
default-to-`public_low` code path anywhere under `src/privacy/`; the module docstring states
this as a property of the file (`classification.py:4-8`) and §8.6 supplies the reason: *"Cost
exhaustion must never turn into lower-quality automatic classification."* Defaulting an
unclassified file to public so the pipeline can continue is precisely the failure that
sentence forbids.

`src/cli.py:351-372` records the same argument being lost and then recovered. This deployment
used to classify every unrecognised file `highly_sensitive_credential_bearing,
protected=True` as a precaution, because P11 raised on an unclassified file and one such file
refused an entire corpus. The comment on the fix is the clearest statement of the principle
anywhere in the repo: *"'We deliberately did not look' and 'we could not tell' are different
answers, they ask the user for different things, and a product that says the first when it
means the second is lying in the direction that happens to feel safe."*

---

## 4.2 `unreadable_unclassified` is a gate outcome, not a file fact

This is D2, and it is enforced structurally in four places rather than by discipline.

- **The module that produces the value cannot reach a column.** `classification.py` contains
  no writer at all: no `set_`, `write_`, `record_`, `mirror_` or `update_`, and it does not
  import `database_agent.files_table`. The docstring states this as the mechanism: *"'Nothing
  has looked' and 'this file carries nothing' must never become the same value in the same
  column, and the durable way to hold them apart is for the string meaning the first to be
  produced by a decision function in a module that can reach no column"*
  (`classification.py:17-24`).
- **The store refuses it as a row.** `ClassificationStore.write` raises
  `GateOutcomeNotAFileFact` (`classification_store.py:129`).
- **The store refuses it as a projection.** `mirror_state` raises the same
  (`classification_store.py:197`), so it can never reach `files.sensitivity_state`.
- **A detector cannot assign it.** `Handling.__post_init__` raises
  (`recognition/detector.py:87-91`).

The distinction exists because absence of a record already carries the meaning. A stored row
saying `unreadable_unclassified` would claim, as a fact, exactly what the absence of a row
says — and the two could then disagree (`classification_store.py:23-26`).

`completeness_implies_unclassified` (`classification.py:228`) is the adjacent reader: it maps
each of P4's nine completeness markings to whether a run at that marking leaves nothing to
classify, with the deciding sentence carried per value in `COMPLETENESS_RULE`
(`classification.py:194-225`). Six of the nine imply unclassified. **It has no caller in
`src/`.** It is a published predicate nothing asks.

### The defect fixed on 2026-08-29

`planning/66-FIND-FILE-AND-ONBOARDING.md` §4 forbids five states from sharing one message:
*"'Protected by your privacy policy' means the product deliberately did not reveal more.
'Unreadable' means the product could not obtain usable content. 'Still indexing' … 'Unsupported
format' … 'No strong match' … These states should never share one vague message such as
'could not find.'"*

The user-facing sentence for a privacy-blocked, unclassified file used to end *"nothing has
been able to read enough of it"*. Commit `53c41d1` caught it on a live run: all four files
had a `direct` fact in `file_facts` and zero rows in `classifications`. Reading is the step
that **worked**, and it was the step the sentence blamed — two of §4's five states sharing
one message. The current sentence is at `src/placement/pipeline.py:585-590`:

> "This file has not been classified -- nothing has yet said what kind of material it is --
> so it was not shown to a model and nothing moved."

The comment above it states the discipline that produced it: P11 knows nothing classified the
file; whether it was *readable* is P4's `extraction_runs`, which P11 does not read and must
not guess at, "so the sentence names the step that stopped and claims nothing about the one
before it" (`placement/pipeline.py:570-584`).

The same conflation survives one layer down. See §4.12, finding 3.

---

## 4.3 The policy: modes, grants, redaction

### One version is the whole snapshot

`Policy` (`policy.py:122`) carries `operation_mode`, `consent_grants`, `redaction_settings`,
`automatic_move_permissions`, `plan_version`, `set_at` and its own `policy_version`. All of
it travels together, and a change to any of it mints a new version
(`policy.py:5-11`). The reason is a binding one: `policy_version` is a term of every release
binding, so a consent grant that did not mint a new version would leave a release minted
before the grant still spendable after it — "the least acceptable silent change in the
product".

The caller may not supply a version: `_persist` raises `CallerSuppliedPolicyVersion` unless
`policy_version == UNSET_POLICY_VERSION` (`policy.py:209`). The row and its event commit in
one transaction (`policy.py:260-266`) so a committed policy change cannot exist with no event
accounting for it. Supersession is enforced by trigger (`schema.py:94-98`).

`grant_consent` and `revoke_consent` derive a *complete* next snapshot from the one handed
in, so the supplied version is a concurrency token: `_require_in_force` raises
`StalePolicyVersion` inside the write transaction (`policy.py:185-203`). `set_policy` is
exempt — it replaces rather than derives.

### The four modes and what `offline` costs

`OPERATION_MODES` (`vocabulary.py:112`) is `offline · local_model · hybrid · cloud_assisted`,
with the design's four sentences carried verbatim (`vocabulary.py:119-129`).

The only predicate that reads the mode for egress is `mode_forbids`
(`denial.py:151`): it returns True when `locality == "cloud"` and the mode is one of
`("offline", "local_model")` (`denial.py:86`). It refuses the *target's locality*, never the
call — a local model is permitted under both, per §8.4's "only local rules and local models
may run".

**The shipped deployment chooses `offline`.** `src/cli.py:150`:

```python
OPERATION_MODE: str = "offline"
```

with the comment: *"`offline` is chosen, not defaulted: it is the only mode under which
nothing about any file can leave the device, and a first run on somebody's home directory is
not the moment to ask for less."* `cli.py:658-667` puts it in force with
`consent_grants=()`, `redaction_settings={}`, `automatic_move_permissions={}`.

### `local_only` versus `dossier_permitted` is P11's vocabulary, not P7's

This pair does not exist in `src/privacy/`. It is P11's `model_eligibility`
(`placement/vocabulary.py`), and `placement/privacy.py:14-16` says so plainly: *"`model_eligibility`
is DERIVED rather than read, because §8.4's three values have no producer in
`src/privacy/` at all."*

`privacy_state_for` (`placement/privacy.py:100`) derives it from three P7 authorities
(`placement/privacy.py:125-133`):

```python
unclassified = handling_class == UNREADABLE_UNCLASSIFIED and unclassified_denies(
    locality=CLOUD, local_calls_on_unclassified=False)
local_only = (unclassified
              or mode_forbids(policy.operation_mode, CLOUD)
              or protected)
```

Under `offline`, `mode_forbids(..., "cloud")` is True for every file, so **every file in
every shipped run is `local_only`** regardless of its classification. The classification only
changes *which sentence the person reads*, not the outcome.

### The model-release decision, and the two open questions the code refuses to close

`unclassified_denies` (`denial.py:177`) has no default for
`local_calls_on_unclassified` — Open question 5 ("does `unreadable_unclassified` permit a
*local* model call?") is unanswered, so the caller answers it and P7 names no winner. The
`Gate` constructor takes it as a required keyword (`gate.py:96`, constructor at `:95-102`), alongside two more
required, defaultless parameters for the same reason: `classifier`/`transform` (identifier
classes and the redaction transform are enumerated nowhere in the design) and `scope_for`
(Open question 3, "what is a corpus area?"). `gate.py:14-21` names all three.

`P11` answers OQ5 in one direction and says so at the call site: it passes
`local_calls_on_unclassified=False` but only ever asks about `cloud`, where the answer is
True before the flag is read (`placement/privacy.py:121-126`).

### W1's local-first floor is built and unreachable

`privacy/defaults.py` is the whole of §8.4's *"The default posture must therefore be
local-first and data-minimizing"*. `LOCAL_FIRST_MODES` is `(offline, local_model)`
(`defaults.py:52`); `MORE_REDACTING` maps all five display facets to `redacted`
(`defaults.py:55`); `_check_install_mode` raises `DefaultPostureViolation` for `hybrid` or
`cloud_assisted` (`defaults.py:67`); `resolve_default_policy` fills absent facets but leaves
a user-set one alone (`defaults.py:96`); `assert_local_first` raises on a cloud starting mode,
an unresolved facet, or any facet left shown (`defaults.py:108-129`). The module reads no
file, no environment variable and no build flag, deliberately: "a module that cannot reach
one cannot be handed a mode by one" (`defaults.py:31-34`).

**None of `effective_policy`, `resolve_default_policy` or `assert_local_first` has a caller
anywhere in `src/`.** `defaults.py:102` calls `effective_policy` "the one composition the gate
calls" — the gate does not call it. `Gate.release` calls `current_policy` directly and raises
`NoPolicyInForce` when nothing is stored (`gate.py:123-130`), explicitly deferring the floor
to a module nobody invokes. `display_policy` reaches the same floor by re-implementing the
fill against `MORE_REDACTING` (`display.py:110-115`) rather than composing
`resolve_default_policy`, and `moves.py:28-32` explains at length why it too declines to
compose it.

---

## 4.4 Release: the ledger, what may leave, and the audit record

### The request carries references only

`ModelCallRequest` (`release.py:113`) has exactly seven fields: `stage`, `target`,
`model_target`, `requested_items`, `prompt_template_id`, `prompt_fingerprint`,
`max_dossier_tokens`. No field accepts a document string, a path, or an `Observation`
(`release.py:116-120`). `call_site` is deliberately *not* a field — B2 puts it inside
`prompt_fingerprint` (`release.py:121-122`).

`release.py` also publishes two guards *as data* so a test asserts against a named constant
rather than a literal: `RELEASE_PARAMETERS = {"self", "request"}` (`release.py:270`) proves no
unpublished parameter exists on `Gate.release`, and `FORBIDDEN_PARAMETER_NAMES`
(`release.py:278`) is a fourteen-word blacklist compared token-wise so that a legitimate
`unclassified_permits_local` is not caught by substring matching.

### The six releasable kinds and the nine that are not

`ITEM_KINDS` (`vocabulary.py:157`) is `excerpt`, `redacted_identifier`, `candidate_label`,
`metadata_field`, `evidence_reference`, `filename`. §8.4 names five; `filename` is the sixth
and it is held unratified. `items.py` builds it, names it, and makes it **unadmittable**:
`check_item` raises `UnratifiedItemKind` unless the caller passes `allow_unratified=True`
(`items.py:281-290`), and the exception is deliberately not one of the eight denial reasons
because "this is a build defect, not a policy outcome, and it must reach the developer rather
than a user who might try to consent around it" (`items.py:69-75`).

`ALWAYS_LOCAL` (`vocabulary.py:142`) is §8.4's nine. Two of the refusals fire at
*construction*, not at the gate: `MetadataField.__post_init__` raises `AlwaysLocalRequested`
for a name that normalises to one of the nine (`items.py:165`), and `Filename.__post_init__`
raises for a `file_id` containing a path separator — "a path wearing an id's field name"
(`items.py:186-193`). A request naming one of the nine is therefore not constructible, so it
cannot be a fixture either.

`items.py` is candid about the limits of this. `_normalise` is `strip().lower().replace(" ",
"_")` and nothing wider (`items.py:85-92`); the consequence, stated in the module docstring,
is that `MetadataField(name="current_path")` is **not** caught, "and that gap is deliberate
and tested: a synonym list would be a detection rule P7 is forbidden to own"
(`items.py:26-30`).

The one per-value sensitivity signal in the product is P5's, read through
`sensitive_observation_keys` (`items.py:320`): an `Excerpt` whose key P5 marked
`POTENTIALLY_SENSITIVE` is refused as `always_local_item`, with the remedy that the same key
is releasable as a `RedactedIdentifier` (`items.py:302-309`). An empty set means *nothing was
signalled*, never *nothing is sensitive*.

### The decision order, published as data

`DECISION_ORDER` (`release.py:259`) is:

```
collect_request_denials · needs_consent · materialise ·
collect_content_denials · append_audit · mint_release
```

It is forced, not chosen: nothing materialises until every check that could deny has run,
because a gate that resolved first would hold the text in memory before deciding it was
allowed to (`release.py:255-258`). `denial.py` states the same principle as
`DECIDABLE_FROM_REQUEST` (`denial.py:76`) — six of the eight reasons need only the request,
the policy and a row lookup, and every one of them precedes the two that need resolved text.
`Gate.release` asserts the first element on entry (`gate.py:122`).

The gate decides no precedence itself: it collects *every* triggered reason into a dict of
builders and asks `first_reason` which wins (`gate.py:212`, `denial.py:136`), because
`DENIAL_ORDER` (`denial.py:63`) is `denial.py`'s and a second total order in the gate would be
a second home for it.

### The eight denial reasons

`DENIAL_REASONS` (`vocabulary.py:180`): `protected_cloud_target`, `unclassified`,
`policy_revoked`, `protected_records_template`, `whole_document_requested`,
`dossier_over_budget`, `always_local_item`, `mode_forbids_target`. There is deliberately no
bare `protected` — collapsing the two protected reasons would produce a denial that cannot
say which rule fired (`vocabulary.py:175-179`).

Every `Denied` requires a non-empty explanation *and* at least one remedy
(`release.py:231-240`, `denial.py:119-128`): "a denial with no legitimate alternative is a
dead end the user cannot act on (§8.6)". `denial.py` is explicit that `unclassified` is the
ordinary case and is written for it — "it carries the longest explanation and the most
remedies, because it is what the audit log will be full of" (`denial.py:3-8`).

### The ledger is what makes a `Released` a capability

`Released` (`release.py:181`) is an ordinary frozen dataclass; anyone may construct one and it
buys nothing. The authority is the ledger. `mint_release` (`binding.py:112`) inserts
`(release_id, model_target, prompt_fingerprint, policy_version, audit_id, minted_at,
spent_at=NULL)` with `release_id = "release-" + secrets.token_hex(16)`.

`consume_release` (`binding.py:132`) is ordered: **issued, then bound, then spent**.

1. Not in the ledger → `ReleaseNotIssued`. This is the refusal that makes the door real
   (`binding.py:70-76`).
2. Any of the three binding terms differs → `BindingMismatch`, before any spend. "A mis-wired
   caller must not be able to burn an authorization the user granted"
   (`binding.py:15-17`).
3. The `Released`'s own echoed `model_target` / `policy_version` must agree with the call.
4. `UPDATE ... WHERE spent_at IS NULL`; `rowcount != 1` → `ReleaseAlreadySpent`. The check and
   the mark are one statement so single use survives a concurrent second caller
   (`binding.py:179-185`).

`audit_id` is carried and never compared — B2's rule that two releases differing only in audit
record are the same authorization. It is `NOT NULL` in the DDL because `append_event` returns
`lastrowid`, so a mint with no audit id is a mint whose audit record was never written and
SQLite refuses it (`binding.py:18-22`, `binding.py:63`).

### The audit record, and what "egress" means

§8.4 requires six fields. `AuditRecord` (`audit.py:90`) carries nineteen plus three, and lands
them under three constraints that are jointly satisfiable exactly one way (`audit.py:9-14`):
P1's `append_event` accepts seventeen named columns and rejects an eighteenth; §8.2's list is
fixed at eleven forever; B5 settles that there is **one** log. So five fields land in columns
— `file_id`, `content_hash`, `prompt_fingerprint`, `observed_at`, `user_id`
(`audit.py:61-63`) — and the other sixteen become canonical JSON in `explanation`, which is
§8.2's own "structured explanation or evidence reference" slot. P7 adds no column to `events`.

Two properties are structural rather than procedural:

- **`audit_id` cannot exist before the record does.** It *is* the `event_id` a completed
  insert returns (`audit.py:139-150`), so §6's ordering guarantee — the audit record is
  appended before `Released` is returned — is not a discipline anyone can forget.
  `Gate.release` shows the sequence at `gate.py:272-287`: `append_audit`, then `mint_release`,
  then construct `Released`.
- **The record says what left without holding a copy of it.** `excerpts_included` is
  `(observation_key, span)` pairs; re-running `resolve.materialise` over them reproduces the
  payload exactly (`audit.py:20-25`). §8.4 puts raw sensitive values in the always-local set
  and the text already exists once.

**What may leave.** Only `Excerpt` and `RedactedIdentifier` are text-bearing
(`gate.py:78`); `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry
no local content and are never materialised and never echoed back. `_materialise`
(`gate.py:467`) is the only path from a reference to a string, through
`resolve.materialise` — "the one module under `src/privacy/` that binds a P4 text
materialiser". The redaction it applies replaces the *value* and not its context, and the
released type has no place to put the context: `ReleasedItem` (`release.py:159`) carries
`observation_key`, `span`, `value`, `zone`, `unit_length` and deliberately no
`context_before`/`context_after`, with the docstring recording the bug that made this
necessary — "for as long as this type was `Materialised`, an 8-character requested span
released every character of its 61-character unit, the value redacted and the account number
beside it not" (`release.py:166-171`).

**What never may.** Paths are never releasable in any form. §8.4's nine always-local names are
unconstructible as a request item, and the `filename` reading — that a directory path is not a
filename, which is the only reading under which §7.3's carve-out is not vacuous — is adopted,
flagged, and gated behind an explicit `allow_unratified` (`vocabulary.py:151-156`,
`items.py:281`).

### Consent events

`NeedsConsent` (`consent.py:155`) carries `consent_request_id`, a `ConsentRequirement`, and
`options`, which must be §8.4's four **in order** — fewer raises `IncompleteConsentOptions`,
quoting P13: "A surface that offers fewer has silently made the user's decision for them"
(`consent.py:172-176`). It carries **no `reason` field**, and that is load-bearing: it is not
a `Denied` in disguise and cannot be mapped onto a denial reason by accident
(`consent.py:13-15`).

There is no consent table. The log is the state (`consent.py:22-26`), which is what makes
Done-means 7 falsifiable: a `consent_requested` event and no `model_release` for that request
until a choice is recorded. `open_consent_request` (`consent.py:213`) writes one audit record
with `outcome="consent_requested"` and the requirement carried as `(observation_key, span)`
pairs — never the text, because "a consent prompt that embedded the value would have released
it in order to ask permission to release it" (`consent.py:143-146`).

`grant_authorizes` (`consent.py:98`) is the table that says which *target* an answer
authorizes: `local_model → {local}`, `cloud_model → {local, cloud}`, `redacted_prompt →
{local, cloud}`, `no_model_use → {}` (`consent.py:90-95`). The comment records the bug it
fixes: the gate used to keep only the scope and drop the option, "so answering `local_model` to
a local-model prompt authorized a CLOUD release of the same protected file". A table rather
than a chain of `if`s, "for the reason `CONSENT_AUTHORIZES` is one: the negated form is a
single edit away from silently granting."

### Revocation

`revoke` (`revocation.py:125`) is forward-only. It requires a non-empty `retraction_limit` —
§8.4 makes the statement mandatory and the SPEC defers its wording to P13, so presence is
enforced and no sentence lives in P7 (`revocation.py:139-145`). It calls `revoke_consent` to
mint the new version, reads the prior releases out of the one audit log, and appends one
`consent_revoked` event. `_prior_releases` (`revocation.py:167`) is deliberately **not**
filtered to the revoked policy version: §8.4's purpose is to tell the user what has already
been sent, and a list narrowed to one version answers a different question.

`delete_derived` (`revocation.py:190`) always raises, on both sides of D3's literal
enumeration: `ScopeNotDerived` outside it, `UnratifiedResolution` inside it. There is no third
branch, no tombstone column exists, and the function writes nothing. `Gate.delete_derived`
(`gate.py:368`) is `staticmethod` returning `NoReturn`, because "D3 built no tombstone column,
so there is nothing here that could read or write one".

---

## 4.5 Protected material

`protected` is a boolean on the record, supplied by whoever classified and never derived from
the handling class. Open question 1 leaves the relation between flag and class unsettled, and
every consumer in the codebase reads the flag:

- **Egress.** `protected_cloud_denies` (`denial.py:196`) returns False unless the file is
  protected *and* the target is cloud; the carve-out is `cloud_assisted` plus an explicit
  grant naming this scope. `scope` is an opaque string because Open question 3 is open.
- **Movement.** `may_move_automatically` (`moves.py:88`) checks **absence first**, then the
  flag, then the policy. The order is not interchangeable: checking the flag first would
  answer `not_protected` for every file in a corpus nothing has classified, which is §8.6's
  forbidden move reached from a different direction (`moves.py:93-98`). Four closed reasons:
  `unreadable_unclassified` (bound to `resolve_class(None)` rather than typed a second time,
  `moves.py:58`), `not_protected`, `policy_permits`, `protected_without_permitting_policy`.
  P11 asks it rather than re-deriving it (`placement/privacy.py:162`) and only for protected
  files, "not an optimisation, it is the only case the answer can change"
  (`placement/pipeline.py:295-303`).
- **Display.** `summarize_protected` (`display.py:124`) returns counts only, with
  `class_breakdown` over every file in scope by resolved class and `scope_total` separated
  from `count` "because they answer two questions, and one number cannot answer both without
  lying about one" (`display.py:135-140`).
- **Prompts.** `ProtectedItemRequested` (`items.py:78`) refuses a `filename` on a protected
  file **for any target**, because §7.3's sentence carries no locality qualifier
  (`items.py:292-300`).

### The standing rule: marked and counted, never opened

The rule holds at three layers and no layer trusts the one above it.

1. **P3** writes an exclusion verdict for a protected container and creates no `files` row for
   anything inside it, so a file inside one never acquires the `(file_id, content_hash)` pair
   the gate keys on.
2. **The detector** checks `is_protected_container` *first*, before it reads even a stored
   observation, and returns an abstention naming the file rather than an error or a silent
   skip. The comment says why the check is there at all given P3: "this should be unreachable
   through a live scan -- it is here because a detector must not be the part that makes it
   reachable" (`detector.py:304-314`).
3. **The report** prints the count and the labels and never the contents.
   `src/cli.py:881-887`: `"Protected containers: {n} marked, none opened"`, then per area a
   display label and a path, then *"Nothing inside these was read, indexed, classified or
   moved, and none of them is a place anything can be filed."*

`vocabulary.py:31-39` pins the distinction that makes this legible: five strings share the
stem "protected" and no two are the same word. P3's `untouched_protected` and
`protected_container` are about **reading**; P7's `protected` flag,
`protected_cloud_target` and `protected_records_template` are about **release**, which is a
policy the user can override through consent. `src/privacy/` imports neither of P3's
constants.

---

## 4.6 `sensitivity_policy_ref`: carried, required, read by nothing

Verified by exhaustive grep over `src/`. `sensitivity_policy_ref` appears in exactly four
files, all under `src/tree_design/`:

- `templates.py:301` — a required `str` field on `TemplateDefinition`.
- `templates.py:338` — `_require(self.sensitivity_policy_ref, ...)`, so an empty one is a load
  error.
- `template_schema.py:81, 216-218` — the JSON schema requires it as a non-empty string.
- `catalogue.py:94` — read out of the raw JSON into the dataclass.
- `fixtures.py:394` — one fixture value, `"policy.public"`.

Nothing reads `.sensitivity_policy_ref` off a `TemplateDefinition` anywhere. Nothing under
`src/privacy/` or `src/llm_harness/` mentions the name at all. It is an **inert field**: every
one of the shipped template definitions must carry one, and no code path consults it.

What it is eventually for: `66` §4 makes the *wording and visible level of detail* of a
protected result follow the user's protected-display policy — "On a shared screen, even
'Identity documents' may reveal more than the user wants; a generic protected count may be
safer." A template's `sensitivity_policy_ref` is the per-destination hook for that: the
policy a node's contents are displayed and searched under, so that a Finance branch can be
visible as a protected area without its filenames being visible (§5.2). P7's SPEC *Deferred*
places the templates' `privacy rules` / `sensitivity policy` fields outside its contract as
hand-authored per-template content; the field is the slot that content will land in. Today the
slot is empty of consequence.

---

## 4.7 P8: what a dossier is, and why a model never sees a file

A dossier is the model's entire world for one call. `Dossier` (`records.py:328`) carries
`dossier_id`, `call_site`, `subject_ref`, `eligibility_reason`, `plan_version`,
`policy_version`, `allowed_vocabulary`, `evidence_items`, `conflicts`, `released_evidence`,
`max_dossier_tokens`, `reduction_rung`, `release_id`. It refuses to exist without a
`policy_version` and a `release_id`: "Dossier is content-bearing only after P7 release"
(`records.py:354-358`).

The asymmetry that makes the gate unbypassable is that P8 holds two different shapes for the
same evidence:

- `EvidenceItem` (`records.py:218`) — the *builder's* reference metadata: `evidence_ref`,
  `kind`, `location`, `excerpt_span`, `reliability_state`, `basis`. No value. This is what
  goes into the `ModelCallRequest`.
- `ReleasedEvidence` (`records.py:241`) — one P7 `ReleasedItem` as the model saw it:
  `observation_key`, `address`, `value`, `zone`. This only exists after `Gate.release`
  returned, and `build_dossier` constructs it from `released.materialised_items`
  (`dossier.py:45-54`).

`ReleasedEvidence` also carries a fixed leak in its docstring: it used to hold
`context_before`/`context_after`/`context_truncated`, copied from P7 into the canonical
model-visible bytes, "and nothing in P8 ever read them" — so the three fields were removed
from the record rather than emptied in it (`records.py:246-253`, `dossier.py:67-79`).

`dossier_id` is the content address of the model-visible bytes, deliberately not the
`release_id`: a release id is a single-use spend capability, so using it as an identity meant
two calls over identical content had two identities and no call could be recognised as a
replay of another (`dossier.py:11-14`, and `CallPayload` refuses `dossier_id ==
release_id` at `records.py:135-140`).

Call eligibility is closed per site. `ELIGIBILITY_BY_SITE` (`vocabulary.py:150`) maps the five
sites to closed reason lists quoted from the design, and `assess_call` (`eligibility.py:60`)
returns `PreCallAbstention(NOT_ELIGIBLE_FOR_MODEL)` for a reason outside its site's list —
before anything is reserved or released.

---

## 4.8 The validation architecture

### Universal validation

`validate_response` (`validation.py:440`) parses the response bytes once, keeps them
untouched, and checks claims in input order. No model is consulted anywhere.

Per claim (`_validate_claim`, `validation.py:316`):

1. Not a mapping, or a non-mapping payload → `reject` / `SCHEMA_INVALID`.
2. `unknown` present → `abstain`, with no reasons and `may_propose=False`. `unknown` plus a
   non-empty `citations` list is `SCHEMA_INVALID` — the two are mutually exclusive.
3. No citations and no `unknown` → `reject` / `UNCITED_CLAIM`. This is the "cites nothing"
   case, and it is never softened into a low-confidence accept (`validation.py:365-374`).
4. Every citation checked. Any failure → `reject` carrying every failing code.
5. The injected `contradicts` oracle. **`None` is `ValidationUnavailable`, not a pass**
   (`validation.py:411-412`).
6. Acceptance split: if every cited evidence item's `basis` is `context-supported`, the
   outcome is `accept_context_supported`; otherwise `accept_direct`
   (`_acceptance_outcome`, `validation.py:306`). `basis` is supplied by the builder and never
   inferred by P8.
7. The site validator may replace the verdict.

### The citation check: two checks, two sources

`_check_citation` (`validation.py:130`) is the mechanism the whole grounding claim rests on:

- `CITATION_NOT_IN_DOSSIER` — the ref is not among the dossier's `evidence_items`, or it is
  but nothing about it was released.
- `CITATION_NOT_FOUND` — `evidence_resolver(ref)` returns `None`; this resolves against the
  store.
- `CITATION_SPAN_MISMATCH` — the quoted span is compared against **`released.value`**, what
  the model actually saw, and never against P4's stored raw text. The docstring gives the
  reason: with redaction on, matching against the store "would accept a quotation the model
  could not have read and reject the one it did" (`validation.py:137-142`).

Three fixed bugs are recorded in place, and each is worth reading as evidence of what this
check is exposed to:

- An empty `cited_span` used to reach the substring test, where `"" in anything` is True, "so
  neither check ever ran" (`validation.py:168-172`).
- Site A ran its own citation check against P6's `FactRequest` — every observation for the
  file version — and set `span_matched` to a copy of `resolved`. "A key P7 withheld, quoted
  with a span the model invented, was accepted and the fact was written"
  (`check_citations`, `validation.py:187-192`).
- `run_call` used to take a `site_validator` callable straight from the caller. `lambda *a,
  **k: None` was a valid value "and it disabled every site-specific check … while the
  universal citation checks still ran and the result still looked like a real verdict"
  (`sites.py:4-8`). The mapping from call site to validator is now fixed in `sites.dispatch`
  and callers may inject only *authorities*.

### The verdict

`P8Verdict` (`records.py:388`) enforces three invariants at construction:
`accept_context_supported` always sets `requires_review=True` (`records.py:418`); `weak`
forbids `may_propose=True` (`records.py:422`); and every `reason` must be in
`ALL_REASON_CODES` (`records.py:410`). `outcome`, `disposition` and `scope` are each checked
against their closed vocabulary.

`OUTCOMES` and `DISPOSITIONS` are two vocabularies, not one — the outcome is uniform across
sites and the disposition names what the owning part does with it (`vocabulary.py:40`,
`:388`).

A call that produced several verdicts returns exactly one, chosen by
`worst_outcome` (`harness.py:311`) against `OUTCOME_SEVERITY`
(`vocabulary.py:50`, worst first). The docstring records why this is one function and not two:
the shard reducer used severity and the claim reducer took the last verdict by position, "so a
two-claim response whose FIRST claim was rejected returned `accept_direct`. A caller told
`accept_direct` must be able to take it as true of the whole call."

### Per-site fact validation

`sites.dispatch` (`sites.py:255`) routes by `dossier.call_site` and requires a typed authority
bundle per site; a missing one is `ValidationUnavailable`, never a pass. `SiteDependencies`
(`sites.py:84`) rejects a bare callable outright: "P8 owns which validator runs at each site
and takes no acceptance callback" (`sites.py:102-105`).

Site A alone writes into another part's store — `apply_verdict` writes P6's fact or its
`unresolved` row — which is why `apply_consequence` has no default and separates a live call
from a replay (`sites.py:270-276`). `_fact_site` (`sites.py:176`) parses every claim, refuses
a response with two claims about one field because `claim_ref` is the field key and two
verdicts would be indistinguishable (`sites.py:208-213`), and hands both P6's bare-key
`Proposal` and P8's span-carrying `Citation` list down, "because a key alone cannot say
whether the model quoted what P7 released or invented the quotation" (`sites.py:140-143`).

`_addressed_to_the_response` (`sites.py:233`) appends a digest of the response bytes to every
`verdict_id`. The reason is a real crash: `verdict_id` was `dossier_id:claim_ref`, "which is
the identity of a question rather than of an answer", and `llm_verdict.verdict_id` is a
primary key — so a re-scan of an unchanged file collided on the insert "and crashed out of
`run_call` with the reservation already taken."

Sites C and D each call an injected `sensitivity_policy(dossier, payload) -> bool` and reject
on False, as `SENSITIVITY_POLICY_VIOLATION` (`placement_validation.py:237-238`) and
`SENSITIVITY_RESTRICTION_IGNORED` (`placement_validation.py:328-329`). P8 authors neither
predicate; `placement/p8_seam.py:83, 96` constructs the dependency objects that would carry
them.

---

## 4.9 Budgets, ceilings, and failing closed

### Refused before it is made

Three things can stop a call before `Gate.release` is even asked:

1. **Ineligibility.** `assess_call` returns `PreCallAbstention(NOT_ELIGIBLE_FOR_MODEL)` for a
   reason outside the site's closed list (`eligibility.py:69-74`).
2. **A standing user rejection.** `suppressed_by_learning` (`eligibility.py:37`) queries P1's
   `learning_records` for a matching `(proposal_class, basis_key)` with `polarity == reject`
   and returns `USER_REJECTED_EQUIVALENT`. Equivalence is that pair, not dossier bytes.
3. **The token ceiling.** `plan_reduction` (`budgets.py:297`) walks §8.6's ladder — unreduced,
   summarized, anchors, split — over *injected* fit flags. P8 measures nothing: "Fit flags are
   injected; this module does not measure." Nothing fits → rung `deferred` and a
   `PreCallAbstention`.

Then, per unit, `reserve_call` (`budgets.py:166`) takes a scan-scoped reservation in one
conditional SQL statement (`_RESERVE_COUNTER_SQL`, `budgets.py:31`) that inserts-or-increments
only while `calls_reserved + 1 <= allowed` and the cost ceiling holds. No row returned →
`BudgetExhausted` → `PreCallAbstention(BUDGET_EXHAUSTED)` and the loop breaks
(`harness.py:429-440`).

**`call_refused` is a real event and it is written on both refusal paths.** Every refusal
produces a *zero-count grounding report* — `report_for_pre_call_terminal`
(`validation.py:506`) builds one with all nine counts at zero, a one-entry histogram naming
the reason, `reduction_rung = deferred` for `BUDGET_EXHAUSTED` and `none` otherwise, and
`release_audit_id=None`. `record_refusal` (`store.py:320`) and `record_pre_call_abstention`
(`store.py:339`) each write a typed row, the report, and one `call_refused` event
(`_append_call_refused`, `store.py:303`) in a single transaction. So a gate `Denied`, an
ineligible call, a suppressed equivalent and an exhausted budget are each first-class recorded
outcomes with a code, never a silent skip — which is §8.6's requirement that the interface
distinguish completed from deferred work. `NeedsConsent` writes none of the three, and that is
the point.

### Fail closed

"Fail closed" here has a precise meaning and it is not "return a safe default". Every missing
capability is a distinct, non-outcome value:

- `ValidationUnavailable` (`records.py:556`) names the missing injected capabilities and is
  documented as "Never an abstain outcome". A missing `contradicts` oracle, a missing site
  bundle, a missing `evidence_resolver`, a missing `conn` — all become this, and none becomes
  a pass or a verdict.
- `CallResult` (`records.py:536`) refuses to wrap a `NeedsConsent` at all.
- `run_call` checks *every* field of `CallDependencies` before doing anything
  (`harness.py:111-152`), and checks the site's own request requirements before the spend —
  `_missing_request_inputs` (`harness.py:155`) exists because `record_cd_verdict` used to raise
  for a missing `evidence_snapshot_id` "only after the release was consumed, the model was
  called and the response was stored: a call paid for that produced no verdict and no report."
- The reservation is released on **any** exception between reserve and settle
  (`harness.py:470-477`), not just the gate's terminal branches — "a binding mismatch, an open
  transaction, a malformed record, an interrupt … removed a call and its estimated cost from
  the scan budget permanently, with nothing left holding the reservation id."

### The release-consuming transport: the gate is asked before assembly

The ordering in `run_call` is the whole of P8's egress claim, and it is visible in one
sequence (`harness.py:424-478`):

```
reserve_call → gate.release(unit.model_call_request) → build_dossier(request, released)
             → build_call_payload → record_dossier → issue(...)
```

`build_dossier` (`dossier.py`) takes `released` as a required argument and reads
`released.materialised_items` to construct the only content-bearing part of the dossier. There
is no path that assembles a dossier and then asks. `NeedsConsent` and `Denied` both release
the reservation and return before `build_dossier` is reached (`harness.py:448-456`), and
`NeedsConsent` is returned **unchanged** — no verdict, no abstention, no report, no event.

`transport.issue` (`transport.py:163`) is the only egress. It refuses an already-open
transaction so a rollback cannot unspend a release after bytes have left
(`transport.py:151-156`); recomputes the fingerprint and the model-visible bytes from
immutable sources and raises if they do not match (`_require_sources`, `transport.py:82`);
checks that `model_client.model_target == payload.model_target == released.model_target`
(`transport.py:95-104`); then, inside one transaction, consumes the release and appends
`model_call_issued`; and only then calls `model_client.invoke(payload.model_visible_bytes)`.
`ModelClient` (`transport.py:49`) is target-bound — its `model_target` is a field, so "callers
cannot supply a second destination to invoke".

`privacy/transport_guard.py` is the mechanised inspection behind P7 Done-means 3. It resolves
annotations with `inspect.signature(..., eval_str=True)` rather than scanning source text,
walks containers and unions, requires exactly one public entry point, bans `Path` /
`Observation` / `TextUnit` module-wide and `str` / `bytes` on the egress surface, and requires
the entry point to take a `Released` (`transport_guard.py:332-...`). `assert_single_call_site`
(`transport_guard.py:303`) is a second instrument over the module's AST, because a second
`model_client.invoke(...)` inside the one entry point changes no signature. Both are called
only from `tests/`; nothing in `src/` invokes them.

---

## 4.10 What actually happens on the shipped run

`src/cli.py` is the only composition root a person can run. Three lines decide everything in
this section.

```python
OPERATION_MODE: str = "offline"                                   # cli.py:150
model_route_permitted=lambda file_id: False                       # cli.py:327
embeddings=EmbeddingsOff(), p8_run_call=None, p8_authorities=None # cli.py:757
```

`production.CorpusAuthorities.__post_init__` enforces that `p8_run_call` and `p8_authorities`
are both present or both absent (`production.py:405-409`), and `None` for both "is a legal
deterministic run: `group_subject` returns a candidate with `no_model_call_configured` rather
than synthesising a verdict" (`production.py:369-371`).

The consequences, each verified by grep over `src/`:

- **No `Gate` is ever constructed.** `Gate(` appears in `src/` only inside
  `privacy/fixtures.py:288`'s docstring. `Gate.release` is therefore never called, no release
  is ever minted, `release_ledger` stays empty, and no `model_release`,
  `model_release_denied` or `consent_requested` event is ever appended. The audit log is empty
  by construction, which is exactly what P7's Done-means 13 walking-skeleton obligation
  asserts.
- **No model client, no prompt, no budget.** `ModelClient(`, `PromptDefinition(`,
  `ScanBudget(` and `CallDependencies(` have no constructor call anywhere in `src/` outside
  `llm_harness/fixtures.py`.
- **P8's tables are never created.** `create_llm_schema` (`schema.py:205`) and
  `create_budget_schema` (`budgets.py:141`) have no caller in `src/`. `production.py:238-246`
  creates P1's, P3's, P4's, P5's, P6's, P7's and P2's schemas and not P8's. If a model were
  wired tomorrow without also wiring these, `record_dossier` would fail on a missing table
  after the release was already minted and the audit record already written.
- **The deterministic engine's answer is what a person gets.** `FactResolver` ships with
  `stages={"direct": ..., "rule": None, "llm": None}` and `None` means "this stage does not
  exist" rather than "an empty one", "so a fact this run could not reach stays unresolved and
  visible instead of being recorded as absent" (`cli.py:318-327`).
- **Every file is `local_only` anyway.** Under `offline`,
  `mode_forbids(policy.operation_mode, "cloud")` is True unconditionally, so
  `privacy_state_for` returns `LOCAL_ONLY` for every file regardless of class or flag
  (`placement/privacy.py:127-133`).
- **Nothing moves.** `automatic_move_permissions={}` (`cli.py:663`), so
  `may_move_automatically` returns `protected_without_permitting_policy` for every protected
  file and `unreadable_unclassified` for every unclassified one. The only `allowed=True` branch
  a shipped run can reach is `not_protected`, for a file the detector classified into one of
  the four safety domains — which by construction it never does, since all four are
  `protected=True`.

So the product a person runs today is: a scanner, a reader, a deterministic fact engine, a
tree designer, and a placement engine that names a destination or explains why it cannot. The
privacy gate is a correctly-built door in a wall nobody walks up to. The harness is a
correctly-built validator with no model to validate.

That is the honest v1 posture and `denial.py:3-8` says so in as many words — "a correct locked
door when nobody has been given a key". The cost is that the property most of P7 and P8 exist
to guarantee has never been exercised end to end outside the test suite.

---

## What looks wrong here

Flagged, not resolved. Ordered by how much a real person would care.

**1. The consent loop does not close.** `record_consent_choice` (`consent.py:292`) links a
user's answer to the question by writing `consent_request_id` into a `consent_granted` event,
and `pending_consent` / `ConsentAlreadyRecorded` both look it up with
`json_extract(explanation, '$.consent_request_id')` (`consent.py:205-210`). But for the three
*authorizing* options the function delegates to `policy.grant_consent`
(`consent.py:325`), whose event explanation is built by `policy._explanation`
(`policy.py:230-245`) and contains `policy_version`, `plan_version`, `operation_mode`,
`consent_grants`, `redaction_settings`, `automatic_move_permissions`, `granted_scope`,
`granted_option` — and **no `consent_request_id`**. So: after a user answers `cloud_model`,
`pending_consent` still returns the open question forever, and `ConsentAlreadyRecorded` never
fires, so the same request can be answered again and again. Only `no_model_use` — the branch
that appends its own event at `consent.py:328-340` — is correctly linked. P7 Done-means 7's
falsifiable form ("the audit log holds a `consent_requested` event and no `model_release` for
that request until a choice is recorded") is not decidable from the log as written.

**2. W1's local-first floor is unreachable.** `defaults.py` is complete, tested-looking, and
has zero callers in `src/`. `effective_policy` describes itself as "the one composition the
gate calls" (`defaults.py:102`) and `Gate.release` does not call it — it calls
`current_policy` and raises `NoPolicyInForce` (`gate.py:123-130`). `display.py:110-115`
re-implements the facet fill rather than composing `resolve_default_policy`, so the floor now
has two implementations, one of which is dead. Done-means 12's negative half ("no code path,
build flag, packaged configuration file, or first-run flow produces a starting mode of
`hybrid` or `cloud_assisted`") is satisfied today only because `cli.py:150` happens to write
`"offline"` — not because anything enforces it.

**3. The gate's own `unclassified` explanation still commits `66` §4's error, and puts a JSON
blob in front of a person.** `Gate._completeness` (`gate.py:395`) reads P1's
`extraction_status_by_tier` column — a per-tier JSON map like `{"native": "complete"}` — and
returns `str(stored)`. `deny_unclassified` (`denial.py:306`) then renders it as *"its
extraction completeness is '{...}'"* (`denial.py:315-316`). Two problems. First, that value is
not one of P4's nine completeness markings, which is what `COMPLETENESS_RULE` and the
parameter name both promise; the sentence has the wrong shape of value in it. Second, and
worse, it re-attaches a *reading* claim to a *classification* refusal — the exact conflation
`53c41d1` removed one layer up at `placement/pipeline.py:585`. The fix landed in P11's user
sentence and did not reach P7's.

**4. `ProtectedItemRequested` is denied under the wrong reason.** `Gate._precheck_items`
catches `ProtectedItemRequested` — raised for a `filename` on a protected file
(`items.py:292`) — and maps it to `deny_protected_records_template` (`gate.py:176-179`). That
denial's explanation tells the user the file is *"held under the 'Protected Records' residual
template"* (`denial.py:349-351`), which is a different rule and is almost certainly false:
`template_for` is `None` in every `Gate` construction in the repo, so no file is ever under a
residual template. `vocabulary.py:175-179` argues at length that collapsing the two protected
reasons "would produce a denial that cannot say which rule fired" — and then the gate collapses
them anyway, in the one direction that produces a factually wrong sentence.

**5. `BUDGET_EXHAUSTED` names two different things.** `plan_reduction` returns a
`PreCallAbstention(reason=BUDGET_EXHAUSTED)` when no rung of the token ladder fits
(`budgets.py:351-355`), and `reserve_call` failure produces the same code
(`harness.py:430-434`). The first is a *dossier too large for one call*; the second is *the
scan has spent its call or cost ceiling*. P2's mapping table sends both to `deferred` /
`ceiling_reached`, so a reader of the metrics cannot tell a corpus that ran out of money from
a single unsplittable file. There is no second code and the reason registry has no room for
one.

**6. Supersession only covers one of the three things the SPEC says triggers it.** All five
declared P8 event types are written (`transport.py:182`, `store.py:172`, `store.py:228`,
`store.py:269`, `store.py:303`). But `verdict_superseded` has exactly one route to it:
`supersede_verdict` ← `revalidate_for_plan` (`placement_validation.py:632`) ←
`placement/versions.py:143`, with `reason="plan_or_snapshot_changed"` hard-coded. The SPEC's
*Provenance* section says "A re-run under a new model, prompt, **or validator version**
supersedes"; only the plan-or-snapshot case exists, it applies only at sites C and D, and
nothing in `run_call` supersedes anything. A second call at site A over the same dossier
produces a second independent verdict distinguished only by the response digest
(`sites.py:248`), with no link recording that one replaced the other.

**7. `sensitivity_policy_ref` is a required field with no reader.** Every
`TemplateDefinition` must carry a non-empty one (`templates.py:338`) and nothing consults it.
It is a schema obligation on hand-authored content that buys nothing today, and a field that
has never been read is a field whose values have never been checked against anything.

**8. `always_local` is name-matching, and says so.** `items._normalise` is
`strip().lower().replace(" ", "_")` (`items.py:92`), so `MetadataField(name="current_path")`,
`"filepath"`, `"full_text"` and `"exif_gps"` all pass. The module argues that a synonym list
would be a detection rule P7 may not own (`items.py:26-30`), which is a coherent position —
but the guarantee "nothing in §8.4's always-local set can be named as a releasable item kind"
is then true only of nine exact strings, and the SPEC states it without that qualifier.

**9. Several published surfaces have no caller in `src/`.** Beyond `defaults.py`:
`classification.completeness_implies_unclassified`, `classification.sensitivity_signal_keys`,
`policy.transcription_authorized_for`, `audit.audit_extra`, `consent.pending_consent`,
`consent.record_consent_choice`, `budgets.report_for_budget_exhausted`,
`stage_output.emit_stage_output`, `Gate.reclassify` / `display_policy` /
`summarize_protected` / `revoke` / `delete_derived` (the whole facade, since no `Gate` is
constructed), and both `transport_guard` assertions. Some are legitimately waiting on P13.
`transcription_authorized_for` is different: `extractors/long_tail.py:224` calls a
zero-argument `transcription_authorized()` declared at `:215`, and `TranscriptionAuthorization`
(`policy.py:331`) exists specifically to close over the scope that call site cannot pass — a
seam built for a caller that does not use it.

**10. The one number in `may_move_automatically` that a person can reach is the wrong-shaped
answer.** `moves.may_move_automatically` returns `allowed=True, reason=not_protected` for any
classified, unprotected file (`moves.py:102-104`). Combined with a detector that classifies
only four protected safety domains, the predicate has exactly two reachable answers on a real
corpus — `unreadable_unclassified` (refuse) and `protected_without_permitting_policy`
(refuse). `policy_permits` requires `automatic_move_permissions[file_id] is True`, keyed on
individual file ids; nothing in the product ever writes that map, and it is not obvious that a
per-file-id key is the right granularity for a user policy the design describes in terms of
areas.

**11. The detector's handling-class choice is a P7 vocabulary decision made in P-recognition.**
`SAFETY_DOMAIN_HANDLING` (`detector.py:117`) assigns `sensitive_personal` to all four safety
domains, and the comment admits `00` names no class for them and that this is "this
detector's own hand-authored choice". It is recorded honestly and it is still a policy
decision living in a detection module — the exact boundary
`planning/domains/_CONTRACT.md` rule 5 was written to hold.

**12. A wired model would hit a missing table.** `create_llm_schema` and
`create_budget_schema` have no caller in `src/`, while `run_call`'s success path calls
`record_dossier` *after* `gate.release` has already minted a release and written the audit
record (`harness.py:290`). A deployment that supplied `p8_run_call` and `p8_authorities`
without also calling both schema creators would spend a release, write an audit record saying
content was released, and then crash — leaving a log that says a release happened and no
record of what it carried.

---

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

**1. A second run over the same plan database crashes with an unhandled traceback.** **[FIXED after this section was written — `86edf8b`. Left in place with its evidence, because the finding is how the fix was found, and a critic should be able to check the fix against the symptom. There were THREE collisions behind it, not one: the clock; the review step stamping `superseded_by` onto a membership the next run re-derives empty; and the composition root minting `version_0` from a counter that restarted every run. Verified live: three consecutive runs, no traceback.]** Reproduced:

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

---

# 6. Tree design and freezing — proposing the folders (P10)

P10 is where the product stops describing the corpus and starts proposing a shape for it. It takes
accepted groups (P9), validated facts (P6), the existing-folder inventory and the protected-container
verdicts (P3), and per-file handling classes (P7), and produces **one artefact: a frozen destination
tree** — a closed set of node identifiers that every later part is permitted to place into and
nothing may add to. It moves no file, composes no filesystem path, and writes no fact.

Twenty-four modules under `src/tree_design/`, about 9,100 lines. The chain that runs them in order is
`src/tree_design/pipeline.py:493` (`design_tree`), and its eleven named steps are
`src/tree_design/pipeline.py:76-88`.

---

## 6.1 The template catalogue

### What the four records are

The library is not a list of folder shapes. It is four record kinds kept deliberately apart
(`src/tree_design/templates.py:1-32`):

| Record | What it is | Holds |
|---|---|---|
| `TemplateFragment` (`templates.py:184`) | reusable organisation logic | semantic **roles**, relative order, optionality, metadata-only roles, allowed values, a privacy floor, provenance |
| `TemplateDefinition` (`templates.py:292`) | a recipe composing exact fragment versions | fragment refs, **candidate orders**, sensitivity policy ref, example label chains |
| `TemplateApplicability` (`templates.py:474`) | the join row — one recipe, **exactly one** schema | `uses_schema`, allowed fields, **detection signal refs**, **role bindings**, provenance |
| `BranchTemplateBinding` (`templates.py:602`) | what one branch in one draft chose | resolved dimensions, accepted group ids, state, chosen order id, validation report ref, approval action ref |

Nothing about a fragment or a definition names a user's data. A fragment says "there is a level
called `subject`"; the applicability row says "in an `academic` context, `subject` resolves to the P6
field `subject` and is called *Course*"; only materialisation turns that into `PHYS1401`.

**A role binding carries a label, and the label is required** (`templates.py:441-470`). It lives on
the applicability row rather than the definition because "one role reads differently per audience,
and the audience is what a `TemplateApplicability` row selects" — `work_type` is *"homework, exams,
labs"* to a student and *"figures, drafts, protocols"* to a researcher.

**Ordering is a runtime choice, enforced structurally.** A definition carries `candidate_orders`, not
a single `dimensions` tuple, and must mark exactly one default (`templates.py:379-391`). A recipe
with more than one dimension must offer at least two orders **or** record prose in
`sole_order_attestation` saying its corpora attest only one (`templates.py:404-425`). The reasoning
is recorded at the record: enforcing a two-order floor with no exit "manufactured its own defect:
alternative orders authored to satisfy the record rather than argued from a corpus … An invented
alternative is worse than an absent one, because the user cannot tell it is invented"
(`templates.py:319-325`).

### The shipped library

Loaded through an injected reader, never by scanning (`src/tree_design/catalogue.py:122`). The seven
packaged files are named in `src/production.py:144-152`; `shipped_catalogue_manifest`
(`production.py:183`) joins them, **refuses a record that appears in two files** rather than merging
(`production.py:210-216`), and derives `release_id` as a SHA-256 digest of exactly the bytes read, in
file order — "a library that changed moves the id, and one that did not cannot"
(`production.py:189-192`). `load_catalogue` refuses a manifest with no `release_id` because "two
different libraries are indistinguishable in a frozen tree" (`catalogue.py:136-140`).

Counted from `src/tree_design/library/`:

| | count |
|---|---|
| fragments | **22** |
| definitions | **63** |
| applicability rows | **208** |
| distinct `uses_schema` values | **19** |
| rows citing **no** detection signal | **0** |
| distinct detection signals | **208** |

The last two lines matter. Every row cites exactly one signal, and no two rows share one — so the
mapping from **situation → row** is 1:1, and `--list-situations` (`src/cli.py:1021-1026`) printing
208 names is printing the row set under another name.

### What a "situation" is, and how it selects a recipe

A situation is a compiled recognition row, referenced as `recognition:{row_id}` — e.g.
`recognition:academic.coursework` beside `recognition:academic.study-abroad`
(`src/tree_design/routing.py:78-92`). `eligible_rows` (`routing.py:179`) selects a row when **both**
hold: its `uses_schema` is one of the branch's domains, **and** the branch's evidence carried one of
its detection signals.

The asymmetry is deliberate and documented (`routing.py:207-217`): a row that cites signals is
selected only on a match; a row citing **none** stays eligible on schema alone, because an empty list
is the row saying *"wherever this schema is, I apply"*, and reading it as "nothing recognises me"
"would silently retire every such row, which is a library change made by a router". In the shipped
library that branch is dead — zero rows cite no signal.

The reason schema alone was the wrong grain is recorded with numbers
(`routing.py:187-205`): eleven of the launch library's rows are `academic` and five share one
definition; collecting on schema handed all five to one composition, whose rows called `school`
*"My school"*, *"Course provider"*, *"Course platform"* and *"Host university"* — four correct names
for four audiences, "merged into one recipe that necessarily refused at C4. Twenty-nine of the
shipped library's fifty-four rows sat inside such a refusal."

**Nothing in `src/` produces a row-level signal.** `src/recognition/library/recognition.json` reports
`compiled_rows: 358` and `refused_rows: 44`, but its usable index is `schemas` — 23 entries — because
`compile_rules` unions every row's terms per schema. `pipeline.py:150-160` says so outright: "the
vocabulary exists upstream and the row-level producer does not; P10 reads the answer and writes no
rule of its own." The shipped CLI closes the gap with a person: `--situation` is a **required**
argument (`cli.py:1030-1036`), validated against the catalogue's own signal set
(`cli.py:537-551`), and then injected as a constant —
`detection_signals_for=lambda group: frozenset({signal})` (`cli.py:591`). Every group in the run is
declared to be in the same situation.

---

## 6.2 Routing and its gates C1–C8

Routing is `evaluate_composition` (`routing.py:294`) wrapped by `route_branch` (`routing.py:537`).
It takes a `BranchContext` (`routing.py:68`) — groups, domains, member file ids, handling classes,
purpose profile refs, detection signals — and returns a `RoutingReport` of **inert** candidates plus
the conflicts. It writes no node.

### The eight gates

| Gate | Refuses when | Consequence |
|---|---|---|
| **C1** | a referenced definition, fragment or version is not in the release; fragment imports cycle | `refuse` |
| **C2** | a resolved role's field is not a live, **destination-eligible** P6 field | `refuse` |
| **C3** | the branch's evidence does not satisfy the row's authored purpose profile; or no row is eligible at all | `refuse` |
| **C4** | one role resolves to two fields, **or** one (role, field) pair carries two labels | `warn` |
| **C5** | combined relative orders cycle; leave roles unordered; or allowed-value sets intersect to nothing | `warn` |
| **C6** | a member of an accepted group would be silently dropped from the preview | `refuse` |
| **C7** | (intended) the combined privacy floor is weaker than an included fragment's | `refuse` |
| **C8** | (intended) a valid composition activates without branch-specific approval | `refuse` |

The meanings are in `src/tree_design/vocabulary.py:170-179`; the consequence map is
`vocabulary.py:206-215`, and `NON_OVERRIDABLE_GATES` / `OVERRIDABLE_GATES` are **derived** from it
(`vocabulary.py:225-232`) rather than listed beside it, "because a hand-written second list is the
copy that goes stale the day a gate changes class."

The split is an owner ruling, stated at `vocabulary.py:184-205`: making the eight uniform "is wrong
in both directions — a uniform refusal makes the product unusable on an ambiguous library, and a
uniform warning makes privacy overridable by a click."

### `CompositionConflict` — what a refusal is

`CompositionConflict` (`templates.py:74`) is the one refusal object. Three properties matter:

1. **It reads its own class.** `self.consequence = COMPOSITION_GATE_CONSEQUENCE[gate]` and
   `self.overridable = self.consequence == GATE_WARN` (`templates.py:98-99`). Neither is passed in:
   "A conflict that could be told which it was would eventually be told wrong."
2. **It always offers the same five ways out** (`templates.py:88-94`): *omit one fragment, change the
   order, flatten a level, keep the branch shallow, defer.*
3. **The message names the conflicting inputs** and the choices, so a surface can render it without
   consulting anything else (`templates.py:100-104`).

`RoutingReport` then splits the conflicts into `refusals` and `resolvable` by reading each conflict's
own `overridable` (`routing.py:167-176`) — "so a surface can offer the user the choices and only the
choices."

### What a person would see

A branch whose situation nothing recognises gets a **named** C3, and the code distinguishes two
absences that would otherwise read alike (`routing.py:576-599`): *"this library holds nothing for
finance"* versus *"this library holds eighteen finance recipes and this branch's evidence recognises
none of their situations"* — "one message for both would send them to the wrong one half the time."

A branch spanning two lives is not a refusal. `route_branch` composes **one candidate per coverage**
(`routing.py:606-631`): each recipe is asked only about the groups its schemas reach, and material no
recipe reaches becomes its own C6, "named by file, non-overridable, and — unlike before — it no
longer annihilates the candidates that do cover the rest of the branch" (`routing.py:648-660`). The
history behind it is quoted at `routing.py:607-612`: a branch holding "a practice beside a degree
beside a child's health records … is a HARD ERROR on every candidate".

### Overrides

`CompositionOverride` (`routing.py:98`) **cannot be constructed for a refuse-class gate** — its
`__post_init__` raises a `CompositionConflict` if the gate is not in `OVERRIDABLE_GATES`
(`routing.py:118-124`). The reasoning is that "a record that CAN hold `gate="C7"` is one click from
honouring it". It also requires `approved_by`, "because an override with no recorded action is the
same defect C8 exists to prevent, one gate earlier" (`routing.py:125-130`). Two overrides answering
one gate is itself a conflict — "a question with two answers has none" (`routing.py:222-229`).

C4's override must name a field one of the rows actually offered; anything else is refused as "a
second door into a field no row allows" (`routing.py:387-395`). C5's override is only recorded as an
override when the derived order was a genuine **cycle**; an under-determined merge the user answered
is §5.3's runtime choice working, not a gate waved through (`templates.py:900-905`).

### The gates do not run in their numbered order

Actual execution order in `evaluate_composition`: **C1** (`routing.py:322`) → **C3**
(`routing.py:341`) → **C4** (`routing.py:353`) → **C2** (`routing.py:398`) → **C5**
(`routing.py:405`) → **C6** (`routing.py:480`) → C7 (`routing.py:496`) → C8 (`routing.py:499`).
C3 runs before C2 "so a branch that was never eligible does not spend field lookups"
(`routing.py:341-342`); C4 runs before C2 because C2 needs to know which field won.

C2 delegates to `upstream.resolve_role_to_field` (`src/tree_design/upstream.py:203`), which refuses
both an undefined field and a field P6 marks **not destination-eligible** — "§3.8 keeps an authoring
role out of the tree; it is supporting evidence, not a folder level" (`upstream.py:224-231`).

---

## 6.3 Horizontal candidates and vertical options

Two passes answer two different questions. **Horizontal**: which top-level branches should exist.
**Vertical**: how should this one branch be split.

### Horizontal (`candidates.py:217`)

A `BranchCandidate` (`candidates.py:71`) is §5.1/§5.2's card as data: label, why it was suggested,
supporting file count, accepted group ids, representative group labels, resembling existing folders,
whether sensitive content is present, source, and the actions available. **No score.**

Candidates are derived from three sources, never from a shipped list of branch names — the module
"ships no branch names at all" (`candidates.py:1-14`):

1. **accepted groups** — one card per group;
2. **existing folders** — carrying P3's curation signal verbatim, with `curated` and `undetermined`
   producing *different* `source` values and different sentences, because the scan "could not tell
   whether it is curated or incidental, so it is shown as it is and nothing is assumed"
   (`candidates.py:300-321`);
3. **user labels** — passed in.

**The only thing that removes a candidate is a recorded rejection** (`candidates.py:240`,
`provenance.py:191`). A group whose domain did not activate is still offered, with the card saying
so. The comment records why: dropping it "is how a multi-life person loses a whole life — P9
categorises their matters `law_practice`, activation does not name that schema, and every matter they
own disappears from the canvas with nothing to click and nothing to read"
(`candidates.py:255-268`).

### Vertical (`candidates.py:436`)

One `VerticalOption` (`candidates.py:102`) per routed candidate, **plus `opt_no_split`, always last
and always present**. Each option carries:

| Field | §5.5 question it answers |
|---|---|
| `resulting_child_counts` | how many branches each **level** makes |
| `total_child_branches` | how many folders in total this option creates |
| `children` (`ChildPreview`, `candidates.py:87`) | label chain + **file count** per child |
| `example_members` + `member_count` | a sample, and the true total |
| `unresolved_file_ids` | files this option gives no folder |
| `warnings` | §5.9's four warnings and the flattening recommendation |
| `validation` | the V1–V6 report |
| `protected_file_ids` | protected members — present and counted, never removed |
| `summary` | §5.5's sentence: *"This option would create three schools, five terms, and twelve courses."* |

`_summarise` (`candidates.py:342`) is that sentence. `unresolved` is the **union** of two different
absences — files routing never covered (C6) and files a level settled no value for
(`candidates.py:492-497`) — because "Both are 'unresolved' to the user, and only the first was
reported."

**A failing option stays on the canvas with its reason.** The summary appends *"It does not pass
V2 (…)"* (`candidates.py:504-509`), and the preview underneath it is built under a provisional
accepted report (`pipeline.py:399-412`) so the counts exist to show — while "Nothing is written from
a preview; the build path below uses the REAL report and is refused by it."

**Sampling.** `example_members` is `members[:sample_size(limits)]` (`candidates.py:519`). The prior
form was `members[:len(members)]` — "a slice that truncates nothing written in the shape of a
truncation, so every option carried its own copy of the branch's whole membership: at 20,000 files
that is the corpus, once per option" (`candidates.py:106-113`).

**Deferral is visible.** When `route_branch` cuts surplus candidates at
`limits.max_folder_proposals` (`routing.py:667-669`), the no-split option's summary says how many
were deferred and adds that they "are not judgements about your evidence"
(`candidates.py:530-534`).

### How an option is chosen — and that the shipped command chooses non-interactively

`vertical_options` decides nothing. The choice is `TreeDesignDecisions.choose_option`, a callable
receiving the candidate and every option (`pipeline.py:198-204`) — "a callable rather than a mapping
because the options do not exist until the chain has computed them, and a caller naming `opt_0` in
advance has chosen nothing."

The shipped CLI supplies `choose_option` at `src/cli.py:490`, and **says so in its own docstring**:

> "§5.5, non-interactively: the first nesting §5.7's checks say may be built. Stated rather than
> hidden, because it IS a choice and a person at a review screen would make a different one."

It takes the first option with children whose validation passes, and falls back to the last option —
always `no-split` — rather than raising. There is no review screen; the entire vertical surface is
computed, rendered into records, and then answered by four lines of code.

---

## 6.4 Materialisation and V1–V6

`materialise_branch` (`materialise.py:106`) is the one place evidence becomes structure. For each
resolved dimension it collects the **distinct settled values the branch's own files carry**, in P6's
spelling, via `preferred_value_for`. A file with no settled value at a level is unresolved at that
level and produces no branch. Nesting is by **shared files**, so the counts are intersections and not
products — "§5.5's 'three schools, five terms, and twelve course branches' is twelve real
combinations, not one hundred and eighty cells" (`materialise.py:15-19`).

One pass produces two views (`materialise.py:20-24`): `MaterialisedCandidate` for the checks,
`BranchEvidence` for the projection, "because a validator that saw a different shape from the builder
would pass a tree that cannot be built, or refuse one that can."

**Protected members are marked, not removed** (`materialise.py:126-146`, `materialise.py:164-166`).
They stay members, stay under their value, stay in every count, and are named in
`protected_file_ids` — "a file dropped out of the evidence is uncounted, and uncounted is worse than
present-but-untouched."

### The six checks (`src/tree_design/validation.py`)

All six run, and `run_checks` collects **every** failure rather than stopping at the first — "which
is how a review surface teaches someone that the product cannot be trusted to tell them what is
wrong" (`validation.py:249-254`). No check returns a score.

| Check | Refuses | Notes |
|---|---|---|
| **V1** (`validation.py:80`) | a level repeating a concept an ancestor or earlier level already expresses | compares on `field_ref`, falling back to the **role** for a template-local level, because comparing those on `field_ref` compared every local level against `None` and "every two-level novel-domain branch failed V1 on a difference the check could not see" (`validation.py:65-77`) |
| **V2** (`validation.py:104`) | a level producing exactly one child | *"a folder the user opens to find one folder"* |
| **V3** (`validation.py:121`) | `ancestor_depth + folder levels > limits.max_depth` | reads `tree.max_depth`; nothing is hard-coded |
| **V4** (`validation.py:145`) | a branch whose **only** level is an author/organisation field | `Applications/Columbia/Essays` is fine; a branch that is only `Columbia` is not. **Raises `ConfigurationRequired` if the collector field set is empty** — P6 owns which fields those are |
| **V5** (`validation.py:173`) | a level whose **values** would disclose protected material as folder names | asks about the **value string**, not the files under it |
| **V6** (`validation.py:227`) | a level value with no member in the accepted group | |

**V5 is the one a critic should read closely.** It previously read `handling_classes_by_value`, the
union of member classes, which meant "one passport scan under `Columbia` gave the string 'Columbia' a
protected class and V5 refused the branch. A university's name is not protected material; the
passport is. The user lost the organisation and kept none of the protection"
(`validation.py:190-196`). It now asks an **injected** predicate about the value string, and refuses
to run without one, because "P6 classifies fields and P7 classifies files, and neither classifies the
string a folder is named after" (`validation.py:202-209`).

**The ones a person actually hits are V2 and V6.** A corpus where most files carry one value at a
level produces one child (V2); a level defined for a field most members lack produces values with
zero members (V6). V3 fires only on a deliberately deep recipe, V4 only on a single-level
organisation branch, and V5 fires **never** under the shipped deployment, whose disclosure predicate
answers `False` for every value (`cli.py:600-603`).

### Date coarsening

`narrow_wide_date_levels` (`materialise.py:513`) is the one width control, applied before previews,
counts and warnings so "no number the user sees can disagree with the tree beside it"
(`candidates.py:465-471`). A level whose values are **all** whole days (or all whole months) and
wider than `max_folder_proposals` is coarsened by dropping the last hyphen component — day → month →
year — which is a **prefix of the value the fact already carries**, so no label is invented and no
file leaves the branch.

Only dates. The reasoning is at `materialise.py:526-536`: capping a level of 400 courses "means
either dropping 300 courses, which is the silent omission the standing rule forbids, or merging them
by something the evidence never said, which is invention. There is no third option for values with no
structure." The trigger was a real run: "A capture-date split on a real photo library proposed 337
folders with that ceiling set to six."

---

## 6.5 The depth and breadth ceilings

Until **2026-08-29** P1 published one key, `tree.max_folder_proposals_and_depth`, for the two numbers
`00`:256 names on one line ("Maximum folder proposals and maximum depth"). P10 read that single value
for **four** questions (`src/tree_design/config.py:6-13`):

1. how many **options** the picker offers (`routing.route_branch`);
2. how **deep** a candidate may go (`validation._v3`);
3. how **wide** a date level may be before coarsening (`materialise.narrow_wide_date_levels`);
4. the **sample size** of the printed lists (`health.sample_size`).

The first two want opposite values and no P10 change could reconcile them: `00`:78's own recommended
tree, `Academics/Columbia/2026-Spring/PHYS1401/Homework`, is five levels deep, "and a picker offering
five options per branch is not a picker" (`config.py:14-18`). The failure was standing evidence, not
an argument — `test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit`.

Since 2026-08-29 P1 publishes both (`src/database_agent/budget.py:41-42`, with the ruling recorded at
`budget.py:28-40`):

| key | controls | read by |
|---|---|---|
| `tree.max_folder_proposals` | **breadth of what the interface shows at once** — options offered per branch, width of a date level before coarsening, sample size of every printed list | `routing.py:667`, `candidates.py:472`, `health.py:53` |
| `tree.max_depth` | **how deep a candidate may nest** | `validation.py:135`, and nothing else |

`config.py:22-25` is honest that this is not fully clean: "That is still three questions on one
number, and it is the reading §8.6's words plainly carry: all three are 'how many things does the
interface put in front of the user at once'. Depth was never that question, which is why it is the
one that left."

§5.9's own thresholds — excessive depth, tiny-folder size, tiny-folder count, and the
materially-improves-retrieval test — have **no ceiling key at all** and are mandatory injected
arguments (`config.py:78-106`). Absent, or non-positive, raises `ConfigurationRequired`: "a default
here would be P10 authoring the design" (`config.py:70-74`).

---

## 6.6 Health and warnings

`warnings_for` (`health.py:287`) is the single implementation of §5.9, used both for the live preview
of an unchosen option (`candidates.py:416-434`) and for a built tree — "a second copy of §5.9 is a
second copy that drifts."

Five findings:

| kind | fires when |
|---|---|
| `one-child-level` | a level has exactly one child **and nothing below it divides**, and its parent is not itself single-child |
| `repeated-parent-concept` | this level's `dimension` equals one an ancestor already expresses |
| `excessive-depth` | depth > `excessive_depth_warning` **and** the levels above express fewer distinct concepts than the depth |
| `tiny-folder-distribution` | ≥ `tiny_folder_count_warning` children hold ≤ `tiny_folder_max_files` files |
| `flatten-recommendation` | the injected retrieval test returns `False` — `None` never rounds to `False` (`config.py:62-65`) |

**Two of these used to measure the wrong thing and fired on the design's own recommended path**
(`health.py:300-326`). `Academics/Columbia/2026-Spring` is three single-child levels in a row, and
`00` recommends it, because each supplies context for the work-type folders that *do* divide beneath.
So one-child now asks whether anything below divides, and fires **once for the whole run** rather than
once per level. And excessive depth is no longer a second absolute-depth rule — V3 is the absolute
one, and refuses; the warning asks whether the path is deeper than the number of distinct concepts it
expresses. There is deliberately **no** uneven-depth warning: §5.8 makes uneven depth a requirement.

### Ranking, sample size, and the 2,991

Recorded history: a 3,200-node tree produced **2,991 warnings**, one node per sentence, unranked
(`health.py:328-329`; measured in `planning/58-SCALE-STRESS.md:393`, where the ratio climbs to 1.18
warnings per node at 12,800 — more warnings than folders). §5.11 asks for "a good enough structural
gist … so that only a LIMITED NUMBER of high-leverage changes remain", and "a warning that fires on a
correct tree spends that budget on nothing and teaches the user to skip the list, which is worse than
having no list at all" (`health.py:13-17`).

`_ranked_and_summarised` (`health.py:426`) sorts by **subtree size** — "a fact already computed and
not a score: fixing the level that holds nine hundred folders is worth more than fixing the one that
holds two" — then, per kind, keeps `sample_size(limits)` and replaces the rest with one counted line.
Post-repair: **21 warnings, ranked** (`planning/63-IMPLEMENTATION-PLAN.md:222`).

**One exemption, and it is the standing rule.** A warning on a `protected` node or an
isolated-sensitive one sorts first and is **never** summarised away, because "a shortened list that
dropped the line saying 'this area was protected and not opened' would be that omission arriving as a
usability improvement" (`health.py:330-334`).

The `_TreeIndex` (`health.py:87`) computes children, depth, distinct ancestor concepts, descendant
counts and "does anything divide below" in one O(n) pass; the previous shape took 3.3s at 3,200 nodes
and projected to fourteen minutes at 50,000. A node the breadth-first walk never reaches sits under a
cycle — `tree_nodes.parent_node_id` carries no foreign key — and is refused by name rather than
hanging the canvas (`health.py:144-151`, `health.py:219-230`).

`tree_health` (`health.py:480`) returns §5.11's six measures — per-group coverage, files with enough
facts, unresolved nodes, context-supported nodes, sensitive-isolated nodes, nodes needing decisions —
and deliberately **no completeness score**: "A single number would be read as a grade to raise, which
is the opposite."

---

## 6.7 Freezing

### What a freeze record contains

`FreezeRecord` (`freeze.py:86`) is §8.8's adopted-version row — **ids and configuration only**:

`plan_version_id` · `created_at` · `node_ids` · **`legal_destination_ids`** · `template_bindings` ·
`labels_and_aliases` · `residual_configuration` · `shared_material_policy_ids` ·
`cross_folder_moves` · `selection_id` · **`catalogue_release_id`** · **`template_versions`**.

`legal_destination_ids` is a frozenset, and legality is a set-membership test —
`is_legal_destination` (`freeze.py:150`) is one line. That shape is the whole design: "an answer that
needed a join could disagree with itself the day the join changed" (`freeze.py:4-8`). The set is
read off `node.accepts_placement` and re-derives nothing (`freeze.py:459-464`).

`FrozenTree` (`freeze.py:117`) is what freeze **hands over**: the record plus the nodes plus the
§6.1 profiles plus the resolved shared-material policy **value** (not an id list, "because §6.9 makes
P11 branch on which of four rules applies, and an id list cannot tell it which"). The bundle is
written once, as canonical JSON, inside one transaction with the version flip and the adoption event
(`freeze.py:484-499`) — rebuilding profiles at read time "would consult all three, against a P9/P4/P6
state that has moved on since the user adopted this plan."

### `catalogue_release_id`

`planning/64-USER-EDITS-AND-CATALOGUE-UPGRADE.md:37` named this the fourth hole: "A frozen tree does
not record which catalogue release built it. A library upgrade is therefore not merely unhandled — it
is *undetectable*." The value already existed — `load_shipped_catalogue` derives it as a digest — and
was simply not carried onto the tree (`freeze.py:99-107`).

`catalogue_release` (`freeze.py:133`) **refuses rather than reporting `None`**: "Reporting `None` as
the release would be worse than refusing — two different libraries would compare equal."
`template_versions` sits beside it as the deduplicated `(template_id, template_version)` set the tree
actually used, "so an upgrade that republished one definition can be told from one that republished
all of them" (`freeze.py:109-113`).

### What freeze refuses

`validate_for_freeze` (`freeze.py:155`) returns **every** reason at once, not the first: "a user who
fixes one and is handed the next has no idea how many remain" (`freeze.py:57-61`). The reasons:

1. the version holds no node;
2. a named approved branch is not in this version;
3. **a node that is a legal destination carries no `refinement_disposition`** — checked on
   `accepts_placement`, not only on what the caller names, because P11's index "raises
   `FrozenTreeRequired` on any legal node with a falsy `refinement_disposition`, so a version that
   froze without one broke at the consumer — where the user cannot act on it — instead of here"
   (`freeze.py:189-202`);
4. a `protected` node that accepts placement;
5. **a protected area the scan marked with no node in this version** — matched on `display_label`,
   which is the only identifier a protected node can carry, and the limit is reported rather than
   papered over (`freeze.py:208-224`);
6. **no §6.9 shared-material policy** (below);
7. a residual template with no recorded enablement state.

### The shared-material policy (§6.9) and why freeze refuses without one

§6.9's four answers are `shared-branch`, `primary-home`, `reference-or-alias`, `mandatory-review`
(`vocabulary.py:352-354`). Three of the four resolve to a destination; `mandatory-review` deliberately
does not, "so a branch created for it would answer the question the policy exists to keep open"
(`vocabulary.py:356-367`).

The gate is **unconditional**, and that is argued rather than assumed (`freeze.py:226-237`): whether
any file will turn out to belong in two homes is computed during *placement*, from retrieval, "so
whether any file will turn out to belong in two homes is not knowable at freeze by anyone. The
question is never contentless — it is 'what should happen IF'". Without the gate "the user designs a
tree, reviews it, approves it, presses freeze, IT FREEZES — and `build_destination_index` refuses at
the next stage, phrased as a contract violation about a policy nobody asked them to choose."

The policy is stored with an explicit `policy_scope` column, `NULL` meaning tree-global, with a
partial unique index allowing exactly one global row per version (`schema.py:91-103`) — SPEC open
question 9 (global or per-branch) is answered **per record** rather than settled by the schema.
`_carry_shared_material` (`store.py:268`) copies it onto every new draft with a fresh `policy_id`,
because previously a draft lost it and "A user who chose `primary-home` and then renamed one folder
was told they had chosen nothing."

### Refinement dispositions

`refined` / `shallow-by-choice` / `refine-later` (`vocabulary.py:78-84`) — three, not two, because
"collapsing them would make a deliberate design look like unfinished work". A disposition without a
`refinement_reason` is refused at construction (`records.py:226-236`).

The field is optional on `Node` and required in a `FrozenTree`, deliberately: "a draft node has not
been approved yet — a required field would make the state the user is actually in while editing
unstorable" (`records.py:166-173`). Nothing in P10 wrote it until `_with_refinement`
(`pipeline.py:444`) — "every tree P10 actually built carried `None` on every node, and
`build_destination_index` refuses such a tree WHOLE." The answer arrives injected as
`decisions.refinement_for`, applied at the one place that writes, and only to nodes that accept
placement.

### Residual enablement decisions

The nine §7.3 names are fixed (`vocabulary.py:268-278`); the eight §7.2 slots are enumerated
(`vocabulary.py:299-308`); §7.3's four stated default parents are recorded and the other five are
**not invented** (`vocabulary.py:282-287`). `build_library` (`residuals.py:85`) refuses a template
missing any slot but `default_parent_location`, which is the one slot whose absence is legal.

The six §7.4 actions (`vocabulary.py:336-339`) are named `RESIDUAL_LIBRARY_ACTIONS`, not
`RESIDUAL_ACTIONS`, because `llm_harness.vocabulary.RESIDUAL_ACTIONS` is already live and holds
§7.7's **eight review actions** — "Two different closed sets under one name in one pipeline is a
misspelling waiting to become a silent downgrade" (`vocabulary.py:328-335`).

`project_residual_nodes` (`residuals.py:140`) turns the choices into nodes. `disable` is the only
action producing none, and that is the whole enforcement mechanism: "a template the user did not
enable has no node, so no placement decision can name it and no model can return it"
(`residuals.py:179-191`). Enabling without a disposition is refused; enabling without a root anchor is
refused, "so the anchor is the user's to choose and P10 has none to fall back on"
(`residuals.py:214-219`); two decisions for one template are refused because they "produced two
branches with the same display name and nothing said which one P11 would place into".

`derive_accepts_placement` (`records.py:64`) **deliberately does not read the disposition**
(`records.py:73-84`): all three dispositions produce legal nodes; the disposition governs what happens
*when* a node is chosen, not whether it can be.

**The shipped CLI enables none of them.** `RESIDUAL_LIBRARY = {}` (`cli.py:222`), with the reason
stated: this deployment "enables NONE rather than inventing slot values: an unplaced file still
reaches §7.5's review set with its reason, so it is counted and explained … without a folder nobody
designed."

---

## 6.8 User edits and catalogue upgrades

### The overlay key

`user_level_edits` is keyed on **`(uses_schema, role_ref, field_ref)`** and on nothing else
(`schema.py:125-139`, `user_edits.py:10-29`). Two obvious keys fail:

- **`node_id` fails.** §8.8 mints a new one per plan version — "exactly the bug the seam pass found in
  `learned_preferences_still_applicable`: filtering on `node_id` made every learned preference
  silently stop applying at the first tree edit."
- **`template_id@version` fails.** "It is the PACKAGING, and packaging is precisely what a library
  upgrade changes."
- **The triple holds** because it is the **vocabulary**: *"whatever level shows my `subject` field in
  an `academic` context, I call it Class"* stays true across a re-route, a re-version and an upgrade.

It is **per-schema, not global**: renaming *Course* to *Class* in an academic context renames nothing
in a research one — the same reason `RoleBinding.label` lives on the applicability row.

`basis` is P7's `USER` constant, imported rather than respelled (`vocabulary.py:145-151`), and a
record with any other basis is refused: "an inferred basis here would be the system overruling the
person on their own words" (`user_edits.py:111-115`). A path separator in `display_label` is refused
at construction, before storage (`user_edits.py:120-125`).

### It applies at the END of routing

`apply_user_level_edits` (`user_edits.py:194`) is called as the last statement of
`evaluate_composition`, after every gate (`routing.py:502-508`). The reason is stated in both places:
"two rows that name one role two ways is a C4 refusal, and a rename applied first would collapse them
into the user's single name and let a composition C4 exists to refuse ship as valid."

Only `display_label`, `action` and `proposed_label` move; `field_ref`, `order_index` and `scope` are
untouched, "because a rename that changed any of those would be a structural edit wearing a label's
clothes" (`user_edits.py:207-212`). The release's own proposed name is preserved as `proposed_label`
so an upgrade can say *"the library called this Course when you renamed it to Class; it now calls it
Module"* (`user_edits.py:80-85`).

An edit naming a level this composition does not have is **surfaced, not resolved**, as an
`UnappliedUserEdit` (`user_edits.py:132`) carrying one of `diff.py`'s own words — `re-templated` if
the role exists under another field, `removed` if the level is gone — so "'what changed when I
updated' and 'what changed when I edited' read the same way". Two of the user's own edits disagreeing
across two schemas in one composition raises `UserEditRefused`: "One question with two answers has
none" (`user_edits.py:244-254`).

### Only a rename has a writer

The record can hold any of the six `DIMENSION_ACTIONS`, so the overlay is shaped to carry a reorder or
an omission the day one is built. The **writer** refuses everything but `renamed`, before storing
anything (`user_edits.py:155-163`): "an edit nothing can apply is a silent no-op that survives every
future session, and the user would see their edit accepted and never honoured."
`OVERLAY_ACTIONS_WITH_A_WRITER` is a one-element tuple (`user_edits.py:64`) and is "where that list
grows, one action at a time."

### The diff (`src/tree_design/diff.py`)

`diff_versions` (`diff.py:50`) compares two versions **by `origin_node_id`**, "which is what survives
a copy", and emits §8.8's seven kinds — added, removed, renamed, re-parented, re-ordered,
re-templated, type-changed — each with a semantic undo label, "because a diff the user cannot act on
is a report rather than a control" (`diff.py:10-11`).

`_PARENT_NOT_IN_VERSION` (`diff.py:118`) is a sentinel distinct from `None`: reporting a dangling
parent as `None` would say the node moved to the top level, and reporting the raw `parent_node_id`
"is worse still — that id is minted PER VERSION (§8.8), so the two sides can never compare equal and
every child of a removed node reads as re-parented."

### What `66` §17 requires and what is not built

`planning/66-FIND-FILE-AND-ONBOARDING.md:576-580` requires that when a user edits or re-runs a
**structural answer**, "the product creates a draft plan version. It shows a meaningful diff: which
schemas become active or inactive, which templates are affected, which branches may need review,
which placement proposals become invalid or newly possible, whether any protected area changes, and
whether any filing policy is paused."

**The storage half is built. The consent-and-presentation half is P13 and is not built.** The overlay
persists; the diff computes; `apply_review_action` opens the draft. But nothing in `src/` calls
`diff_versions`, and the surface that would present a diff and collect an adoption is P13 —
specification only, with `pipeline._Action` (`pipeline.py:423`) standing in as `src/`'s copy of P13's
`review_action` "because a source module may not import a test one, and the day P13 ships both are
replaced by its record."

---

## 6.9 Protected areas in the tree

The standing rule is quoted verbatim in the code (`candidates.py:150-153`): *"reports, apps and system
files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE."* A protected container
is **marked and counted, never opened**, present-but-untouched with a reachable explanation, never
silently omitted.

The mechanism is four independent pieces that agree:

1. **P3 marks it.** `upstream.protected_areas` (`upstream.py:283`) selects on
   `rule == RULE_PROTECTED_CONTAINER`, not on the display label — "Selecting on the display string
   would make a presentation change silently alter which areas the tree represents."
2. **P10 builds a node for it.** `protected_area_nodes` (`candidates.py:143`) mints one
   `node_type=PROTECTED` node per area, with an explanation stating that the scan "marked and counted
   it and never opened it … It is shown here so that it is accounted for rather than missing."
   There is deliberately **no** `protected_movement_permitted` parameter: §8.4 contemplates a user
   policy permitting movement for other protected material, but P3's rule for applications and system
   items is stronger and says "no policy, approval, or user gesture makes them movable"
   (`candidates.py:168-180`). The scope bound is explicit — this producer is for P3's containers and
   nothing else; "sensitive personal material is not the same thing as `Numbers.app`."
3. **The flag derives to `False`.** `derive_accepts_placement` returns
   `bool(protected_movement_permitted)` for a protected node (`records.py:89-90`), and
   `Node.__post_init__` refuses a stored flag that disagrees with the derivation
   (`records.py:197-207`). So the node is in the tree and is **not a legal destination**.
4. **Freeze refuses to lose it.** `validate_for_freeze` refuses a protected node that accepts
   placement, and refuses a version missing any area the scan marked (`freeze.py:203-224`).

`represent_protected_areas` (`freeze.py:257`) is the join, and it runs **before** the profiles are
built, "not inside `freeze`", because §6.1 requires a profile for every frozen node and "nodes written
after the profiles were computed would be nodes P11's index refuses to build over". The history is
recorded: for a while nothing in `src/` connected `upstream.protected_areas` to
`candidates.protected_area_nodes`, "so a protected container was pruned by the scan and then absent
from the tree — silently omitted, the one outcome the owner's standing rule names."

Two other places carry the same rule. `materialise_branch` marks protected members rather than
removing them (§6.4 above). `profiles.redacted_for_egress` (`profiles.py:194`) drops file
identifiers and excerpt handles from a protected profile and **nothing else** — "Dropping the profile
entirely would be the omission; dropping only what reads or exposes contents is the rule."

---

## What looks wrong here

**1. C7 and C8 never refuse anything.** Every other gate raises `CompositionConflict` with its own
constant; C7 is `floor = merged.privacy_floor` (`routing.py:496-497`) and C8 is a comment
(`routing.py:499`). A grep for `CompositionConflict(C7` or `CompositionConflict(C8` finds nothing in
`src/`. Yet every returned candidate sets `gates_passed=tuple(COMPOSITION_GATES)`
(`routing.py:528`) — asserting all eight passed. C7's actual behaviour is `max(floors,
key=privacy_rank)` inside `merge_fragment_constraints` (`templates.py:920`), which cannot fail as
long as `privacy_rank` totally orders the floors; if it does not, the code raises
`ConfigurationRequired`, not a C7 conflict. "C1–C8 are independently falsifiable" is P10 SPEC Done-means
13; two of the eight have no failure path at all.

**2. No production caller can construct an override, so the two warn-class gates behave as refusals.**
`CompositionOverride` is referenced only inside `routing.py`. Neither `pipeline.design_tree` nor
`cli.py` builds one, and `route_branch`'s `overrides` parameter defaults to `()`. A C4 or C5 conflict
therefore ends the candidate exactly as a C1 does, and the "resolvable" half of `RoutingReport` is
always empty in a real run. The distinction the vocabulary carefully derives has no consumer.

**3. §8.7's negative-feedback loop reads a record nothing writes.** `suppressed_branch_basis_keys`
(`provenance.py:191`) filters on `polarity == REJECT_POLARITY`. All three `record_tree_edit` call
sites pass `polarity="accept"` (`store.py:452`, `:558`, `:601`), and no other P10 code writes a
learning record. A deleted branch candidate therefore cannot be suppressed — the SPEC's "A deleted
branch candidate must not reappear on the next pass" has a reader, a key function, and no writer.

**4. Five whole modules are inert.** No caller in `src/` outside their own file:
`diff.diff_versions` (§8.8's node-level diff), `health.tree_health` (§5.11's six measures),
`profiles.redacted_for_egress`, `stage_output.emit_tree_design_stage` and
`emit_template_generation_stage` (so **P2 receives no envelope from either of P10's two §8.5
stages**), `provenance.record_template_application` (so §8.2's `template application` event is never
appended), `user_edits.record_user_level_edit` (the overlay has a reader and no writer),
`freeze.catalogue_release`, `freeze.is_legal_destination`, `templates.branch_dimension_roles`, and
`upstream.rejected_group_ids` / `renders_as_branch`. Tests exercise most of them; production does not.

**5. `BranchTemplateBinding` is never constructed in `src/`.** The record that is supposed to be the
one thing that may contribute nodes to a tree — "Only a branch-local binding that passes the
composition checks … and receives explicit user approval may contribute nodes" (SPEC) — exists only
as a class. `chosen_order_id`, `state`, `approval_action_ref` and `validation_report_ref` are written
by nothing. Consequently `branch_dimension_roles`, its "only reader", reads nothing, and the C8
promise that approval is recorded is enforced by no code path that runs.

**6. No node in a real run carries a `template_context`.** The CLI injects
`template_context_for=lambda field_ref, order_index: None` (`cli.py:604`). So
`FreezeRecord.template_bindings` is always empty, `DestinationProfile.template_binding` is always
`None`, and `diff._template_key` always compares `None` to `None` — the "re-templated" diff kind
cannot fire.

**7. The CLI's ceilings and its `TreeLimits` disagree.** `_bootstrap` writes `CEILING_VALUE = 8` to
**every** key including `tree.max_folder_proposals` and `tree.max_depth` (`cli.py:123`, `:533`), then
the run uses a hand-built `TREE_LIMITS` with `max_folder_proposals=4, max_depth=5` (`cli.py:131`).
`config.tree_limits` — the function whose entire purpose is to read those keys and refuse an absent
one — has **no caller in `src/`**. The stored ceilings are decoration.

**8. Stale counts in three docstrings.** `store.apply_review_action` says "this function writes three"
and "The other twelve are named in `ACTIONS_WITH_NO_WRITER`" (`store.py:484-491`); the sets are
actually five and ten (`store.py:93-108`). The comment at `store.py:583` repeats "`ACTIONS_WITH_A_WRITER`
has three members". `user_edits.py:35` says `apply_review_action` "refuses its twelve".
`health.py:316` says V3 "uses §8.6's published `tree.max_folder_proposals`" — it reads `tree.max_depth`
(`validation.py:135`). `records.py:171` says "`freeze` refuses to hand over a bundle carrying a `None`
anywhere"; `validate_for_freeze` checks only approved-or-legal nodes, so a protected or ignored node
with `None` freezes fine.

**9. Ordinals collide.** `_write_overlap_answer` gives a new child `ordinal=parent.ordinal + 1`
(`store.py:428`) — the parent's own sibling index, applied to a child. `project_residual_nodes`
numbers residual nodes from 0 across all parents (`residuals.py:160`, `:281`), and
`_project` numbers each level's children from 0 (`materialise.py:427`). Two nodes under one parent can
share an ordinal, and `ordinal` is what §5.12 calls "sibling order as the user arranged it".

**10. `residual_refinement` can produce an unfreezeable tree.** `_enable_residual_library`
(`pipeline.py:745`) applies `decisions.residual_refinement` to every residual node. If that is `None`
— which is exactly what the CLI passes (`cli.py:615`) — an enabled residual node accepts placement,
carries no disposition, and `validate_for_freeze` refuses the whole version. The CLI escapes only
because `residual_choices=()`.

**11. The situation detector does not exist, and the CLI substitutes a single global answer.**
`recognition.json` compiles at schema grain (23 schemas), the template library keys on 208 row-level
signals, and nothing bridges them. The CLI asks a human for one `--situation` and asserts it for every
group in the corpus (`cli.py:591`). For the north-star multi-role person — whose disk holds coursework
*and* a legal practice *and* a child's records — this is precisely the case the per-coverage routing
in `route_branch` was built to handle, and the shipped entry point makes it unreachable.

**12. `protected` node role vs. type is still ambiguous, and the code carries both.**
`protected_area_nodes` sets `node_type=PROTECTED` **and** `node_role=ORDINARY`
(`candidates.py:196`, `:208`), while `handling_class` carries P7's answer separately. SPEC open question 3
is open. `health._protected` (`health.py:417`) therefore has to check *two* records to decide whether
a warning may be summarised away — and a protected area with a non-protected `handling_class` and no
`sensitive_isolated` count would fall through both.

**13. `validate_for_freeze` matches protected areas by `display_label`.** Two protected bundles with
the same basename in different directories are indistinguishable, and the code says so
(`freeze.py:212-216`) rather than fixing it. A user with `~/Projects/build/Numbers.app` and
`~/Archive/Numbers.app` gets one node and a freeze that believes both are represented.

**14. `health._INDEX_CACHE` holds exactly one entry and clears on every miss** (`health.py:172-184`).
`warnings_for` and `branch_counts` are called per node with the whole tree, so alternating between two
trees — a preview and the built tree, which `vertical_options` does per option — thrashes the cache
back to O(n²). Nothing measures it.

---

# 7. Placement — where each file would go

P11 is the last part that exists. It takes a **frozen tree** from P10 and, for every file and every
accepted group, names **one approved node in that tree — or says it cannot**. It moves nothing:
`src/placement/records.py:14-15` states the boundary in the record itself — *"No field here can
hold a filesystem path, a deletion, or an expiry."* P12, which turns a named node into a path and a
move, does not exist.

The part owns §6 (everything except §6.1, which is P10's) and §7 (everything except §7.2–§7.4, the
residual *library*, which is also P10's). Its SPEC is
`planning/parts/P11-placement-residual/SPEC.md`, 838 lines. Its code is sixteen modules under
`src/placement/`, 6,555 lines. Roughly a third of that code has no caller on the shipped run path,
and §7.13 below is the inventory.

Two sentences from the design govern everything here, and both are in the code as constants rather
than as comments:

> No system component may invent a new destination after freeze, silently override a direct fact, or
> move an uncertain file simply because it resembles an existing folder. (§6.12)

> **Correct abstention is a successful outcome.** (§6.10)

The second is the one a reader must hold onto, because on a real run today it is the *only* outcome
that happens. §7.14 says what that looks like to a person.

---

## 7.1 The destination index — turning a frozen tree into something searchable

**What P10 hands over.** A `FrozenTree` carrying, per node: a `node_id`, a `node_role` (`ordinary` |
`scoped-general` | `residual` | `shared-material`), a `display_label`, a `parent_node_id`, a
`root_anchor`, a `handling_class`, a `refinement_disposition`, an `accepts_placement` flag, a list
of `expected_values`, and — on residual nodes only — a `disposition`. Beside the nodes it hands over
one **§6.1 destination profile** per node, and a `freeze_record` naming the legal set.

**Legality is P10's, and P11 proves it is only projecting it.** `index.py:502-508` compares the set
of nodes it indexed against `tree.freeze_record.legal_destination_ids` and raises if they differ:
*"P10 owns legality and P11 only projects it."* One entry exists per node with `accepts_placement =
true` and per nothing else (`index.py:490-493`). That single line is where §5.10's guarantee lives —
a folder the user marked `ignored` is not *rejected* at validation time, it **never enters the
index**, so it can be neither retrieved nor suppressed and a file that resembles it produces an
abstention rather than a warning the user has to read (`index.py:7-10`, `retrieval.py:21-22`).

**What an entry holds.** `IndexEntry` (`index.py:47-71`) is 22 fields: the node's identity and
ancestry (`depth`, `ancestor_labels`, computed by walking `parent_node_id` and raising on a cycle or
a missing parent, `index.py:74-91`), and the §6.2 ingredients flattened out of P10's profile —
`template_fields`, `expected_values`, `accepted_group_ids`, `group_labels`, `representative_files`,
`anchor_excerpt_keys`, `known_document_types`, `parent_context`, `child_context`,
`known_exclusions`, `user_edits`.

**Expected values** are the `field = value` assertions a node makes: a node meaning *Columbia
application* asserts `target institution = Columbia`. They arrive as P10's frozen `ExpectedValue`
objects and are flattened to `(field, value)` pairs (`index.py:125-127`).

**What is actually indexed is narrower than what is stored.** `TERM_SOURCES` (`index.py:153-155`)
is three fields — `expected_values`, `accepted_group_ids`, `display_label` — and the docstring gives
the rule: *"Anything else on the entry — the ancestor labels, the representative files, the document
types — is read AFTER a node is already a candidate, so indexing it would build a term nothing
queries."*

So the index is two tables. `placement_index_entries` holds one JSON payload per node (the record
store). `placement_index_terms` holds one row per `(node, source_field, term_key, term_value,
ordinal)` — the inverted projection retrieval actually reads. Labels are casefolded once at build
time (`index.py:174-175`), because *"`retrieve` casefolds the SUBJECT's labels, which are few, and
never the tree's, which are many."*

**A third table exists only to make a count honest.** `placement_index_term_counts` stores, per
`(plan_version, source_field, term_key)`, how many term rows the build wrote for it. Its whole
reason is §6.3's suppression count (see §7.2). If a term matched or contradicted something and has
no aggregate row, `reachable_entries` raises `IndexCountsUnavailable` rather than falling back to
the length of a list — *"the count would fall back to the bounded list and report four destinations
ruled out where the plan ruled out eight hundred"* (`index.py:429-446`).

**One legality authority, shared with P8.** `index.node_exists` (`index.py:595-608`) returns a
closure over one plan version and is handed to P8's Site C and Site D as their `node_exists`
authority. A dossier stamped with a different plan version answers `False`. The point is stated at
`index.py:12-15`: two sources could disagree and *"the disagreement would look like a model error."*

---

## 7.2 Retrieval — matching a file's evidence against nodes, and suppressing what conflicts

**Six channels, none of which decides.** `retrieval.py:36-48` names §6.3's six: `direct_fact`,
`accepted_group`, `graph_relationship`, `structural_relationship`, `semantic_neighbour`,
`curated_folder`. Two of them — semantic and curated — are declared `NON_DECIDING_CHANNELS`
(`retrieval.py:52`): a node reached only by those is recorded in `semantic_only_node_ids` and can
never carry a placement on its own, which is §6.5's *"a semantic embedding alone is insufficient."*

**Only two of the six are ever assigned.** `retrieve`'s loop (`retrieval.py:125-148`) appends
`DIRECT_FACT`, `ACCEPTED_GROUP`, `CURATED_FOLDER` and `SEMANTIC_NEIGHBOUR`. `GRAPH_RELATIONSHIP` and
`STRUCTURAL_RELATIONSHIP` are declared, weighted in the scorer, and **never assigned to a
candidate anywhere in `src/`.** This has a direct arithmetic consequence, which §7.3 works out.

**What a matching fact is.** A `MatchingFact` (`records.py:173-184`) is `(file_fact_id, field,
value, reliability, evidence_ref)` — P6's row, carried, with the `evidence_ref` being P4's
content-addressed `observation_key` rather than a per-row uuid, so a rejection recorded today still
resolves to its evidence after an extractor upgrade (SPEC:203-211). A fact matches a node when the
subject's `(field, value)` pair equals one of the node's `expected_values` pairs — exact, not fuzzy.

**Facts are filtered before they can reach a node at all.** `_eligible_facts`
(`retrieval.py:72-83`) drops any fact whose field P6's catalogue marks
`destination_eligible = False`. This is where `00`:44's prohibition on person-shaped destinations is
enforced: `authored_by`, `our_firm`, `instructor` and `people` never reach a candidate node.
`groups.py:23-29` explicitly declines to re-check it — *"A second check here would be a second
opinion with no way to be reconciled."*

**Retrieval is one bounded read, not a scan.** `reachable_entries` (`index.py:282-465`) issues
seven SQL reads sized to the *answer*, not to the tree: four to find what the subject's own evidence
reaches (matched pairs, group ids, labels, semantic node ids), a fifth asking only those nodes which
of the subject's stated fields they state *differently*, a sixth reading a bounded sample of
further ruled-out nodes per field, and a seventh reading one integer per field. The earlier
implementation deserialised every legal node once per file — O(files × nodes) — measured at ×4.2 per
file in `planning/58-SCALE-STRESS.md` §2.

**What a conflict is.** The subject states `target institution = Duke`. Every legal node stating
`target institution` with any other value is suppressed. The suppression happens *inside* retrieval,
not as a later filter, because §6.3 makes it part of retrieval (`pipeline.py:305-306`).
`Reachable.contradicted_node_ids` is the suppression set and is kept separate from the naming list,
so a node the sample had no room to name is still barred from the candidates
(`index.py:360-370`, `240-251`).

**The recorded failure: naming everything.** `index.py:196-223` records why the list is bounded. On
`planning/58-SCALE-STRESS.md` §2's tree the suppression list is 799 long *for every file*, eight
million ids across a 10,000-file disk, and *"the sentence the user reads names every folder they
own."* The document's own words for the same failure elsewhere: *"the warning list outgrows the tree
it describes."*

**So the list is a bounded sample and the count is exact.** `ConflictConsidered`
(`records.py:210-263`) carries `suppressed_node_ids` (named) and `suppressed_node_count` (total),
and refuses a record where the count is smaller than the list. Which nodes get named is not
arbitrary: the ones a retrieval channel actually **reached** go first — *"they are the ones the user
is about to ask 'why not that one?'"* — and the remainder of the budget is filled from the field's
own stable index order. The budget is `max_retrieved_neighbors`, the same ceiling that bounds the
candidate list, deliberately: *"both answer one question — how many destinations should a human read
about one file — from opposite sides."*

**What the person sees.** `pipeline._explain` (`pipeline.py:499-521`) renders it as
`ruled out A, B and 795 further destinations on conflicting evidence`, or, when nothing the file's
evidence reached was ruled out, `ruled out 799 destinations on conflicting evidence, none of which
this file's evidence reached`.

**Candidates are ranked deterministically** — strongest channel first, then node id, never insertion
order (`retrieval.py:159-169`) — and truncated to `max_retrieved_neighbors`.

---

## 7.3 The node-local graph — §6.4 and §6.5

`build_node_local_graph` (`graph.py:79-164`) builds one graph per candidate node. Vertices are the
subject plus the files already accepted in that node (`entry.representative_files`); edges are typed
relationships supplied by the caller from P6 facts, P9 memberships and P3 folder context. P11
discovers no relationship of its own — *"that would be a second grouping engine and P9 owns
grouping"* (`graph.py:84-86`).

Five edge types (`graph.py:39-52`): `shared_validated_fact`, `duplicate`, `version_family`,
`compatible_document_type`, `existing_related_folder`. A semantic neighbour is **deliberately not an
edge type** — it is a retrieval channel only, *"because an embedding alone is insufficient and an
edge type would make it look like evidence of the same kind as a shared fact."* An untyped edge
raises.

Locality is structural, not declared: an edge survives only if it touches a file already accepted in
*this* node (`graph.py:103-107`), so *"there is no code path along which whole-corpus reclustering
could happen."* `foreign_node_ids` is a seam assertion on top of that and raises if non-empty.

Two §8.6 ceilings apply, in an order the code argues for: the **cluster** (`max_candidate_cluster_
size`, a bound on files) is cut before the **neighbourhood** (`max_local_graph_neighborhood`, a
bound on edges), because the other order does not converge (`graph.py:111-136`).

`is_typed_support` (`graph.py:167-182`) is §6.5's bar: a graph supports a placement only if it has
at least one entity that is *not* a high-frequency entity. The frequency cut-off is injected; P11
picks none.

---

## 7.4 Scoring and the two conditions (§6.10)

**The score.** `scoring.py` computes a weighted count of independent channels, normalised to the
policy's declared scale:

```
_CHANNEL_WEIGHT = {DIRECT_FACT: 3, ACCEPTED_GROUP: 2,
                   GRAPH_RELATIONSHIP: 1, STRUCTURAL_RELATIONSHIP: 1}   # _MAX_WEIGHT = 7
support_score = policy.support_scale_max * weight / _MAX_WEIGHT          # scoring.py:81
```

The weights are structural rather than tuned: *"a direct fact outweighs a group membership
outweighs a relationship, which is §3.13's own ordering, and the two non-deciding channels
contribute nothing at all"* (`scoring.py:38-47`). Semantic and curated weigh 0.

**The channels are deduplicated before they are weighed.** `retrieval.py:146` stores
`tuple(dict.fromkeys(channels))`, so a candidate whose five direct facts all match scores exactly
the same 3 as a candidate matching one. The score counts *kinds of evidence*, not *amount*.

**Condition one: support.** `best.support_score >= policy.minimum_support_threshold`
(`scoring.py:129`).

**Condition two: margin.** `policy.margin_predicate(best, next_best)`, which is
`best - next_best >= margin_threshold` (`config.py:88-90`). Where there is no next-best, B8(b)
applies: `margin_over_next` is `None` and `meets_margin` is the string `true_vacuous`, never a
measured `true` (`scoring.py:130-142`). `TwoCondition.__post_init__` (`records.py:298-324`) enforces
the pairing both ways — a vacuous margin with a number is malformed, and a measured margin without
one is malformed.

**Both thresholds are injected and both are recorded.** `SupportPolicy` (`config.py:48-90`) carries
`policy_id`, `support_scale_max`, `minimum_support_threshold`, `margin_threshold`, and refuses a
threshold outside `0..scale` — *"a threshold no score can reach abstains on everything and a
threshold every score clears gates nothing."* `require_policy` refuses `None`: *"Absent means
refuse, not guess"* (`config.py:111-117`). The SPEC leaves both numbers open (Open questions 1 and
2) and the code ships no default for either.

**The shipped deployment's numbers** are in `src/cli.py:115-117`:

```python
SUPPORT_POLICY = SupportPolicy(
    policy_id="cli-support-v1", support_scale_max=1.0,
    minimum_support_threshold=0.50, margin_threshold=0.20)
```

with the reasoning at `cli.py:108-115`: *"0.50 as the support bar because that is the band a direct
fact alone (3/7) falls below and a direct fact plus an accepted group (5/7) clears."*

**What that arithmetic means in practice.** Since two of the four weighted channels are never
assigned (§7.2), the reachable scores are exactly: `0`, `0.286` (group only), `0.429` (direct fact
only), `0.714` (direct fact + group). Against a threshold of `0.50`, **a placement in this
deployment requires the accepted-group channel to fire.** A file whose facts uniquely and correctly
match one node's expected values, with no group, scores `0.429` and cannot be placed.

**`policy_id` does not travel on the decision.** `cli.py:113-114` asserts *"A run under these is
auditable because `policy_id` travels on every decision — change a number and change the id with
it."* It does not. `TwoCondition` (`records.py:280-296`) carries `support_threshold` and
`margin_threshold` and no id; `PlacementDecision` has no policy field; `store.PROJECTION_COLUMNS`
has none; `placement/events.py` never logs one. `grep -rn policy_id src/` returns hits only in
`config.py`, `cli.py`'s comment, and P10's unrelated shared-material policy table. Two runs under
different policies with the same numbers are indistinguishable, and the audit trail the comment
promises is the two floats.

**"Unique direct match" is a property of the facts, not of the candidate set**
(`scoring.py:154-186`). It is true when exactly one candidate carries the `DIRECT_FACT` channel,
that candidate is the best-scoring one, **and** both §6.10 conditions hold. The code argues both
exclusions explicitly: keying it on "there was only one candidate at all" would make B8(b)
unsatisfiable, and requiring a graph anchor would mean *"a syllabus whose subject fact names exactly
one course could never be decided deterministically, which is the case §6.6 exists to keep off the
model."*

A unique direct match sets `verdict = accept_direct`, `confidence_class = "exact fact match"`,
`requires_review = False`, and — via `needs_model_call` (`scoring.py:230-237`) — **issues zero model
calls**. Anything else that clears both conditions is `accept_context_supported` with
`requires_review = True`, because *"calling it `accept_direct` would name a fact match that never
happened"* (`scoring.py:188-198`). `records.py:320-324` refuses an `accept_context_supported` record
that does not require review.

**The degenerate case stays binding.** With one legal candidate the margin is vacuous and the
support threshold is the sole gate. A file below it abstains `no_supported_destination` *even though
that one destination is the only one available* — *"the scarcity of destinations is not evidence
about the file, and a tree with one branch must not become a funnel"* (`scoring.py:16-18`).

---

## 7.5 The outcomes, and what a person is told for each

Seven outcomes on one record shape (`vocabulary.py:105-116`): `place`, `return_to_placement`,
`mark_review_later`, `leave_in_place`, `mark_state`, `ask_user`, `abstain`. Exactly one
outcome-shaped field may be filled, and `PlacementDecision.__post_init__` (`records.py:416-436`)
enforces presence *and* absence in both directions: `destination` exists exactly on `place`,
`return_target` exactly on `return_to_placement`, `marked_state` exactly on `mark_state`, `ask`
exactly on `ask_user`, `abstention_reason` exactly on `abstain` — *"an unexplained one is silence,
and a reason on any other outcome contradicts the decision."*

**Only `place` produces a plan.** `PLAN_BEARING_OUTCOMES` is a one-member tuple
(`vocabulary.py:118-120`). `abstain` is not a deferred move.

### The nine abstention reasons

`ABSTENTION_REASONS` (`vocabulary.py:240-244`) holds nine. The SPEC enumerates eight —
`multiple_supported_homes` appears **zero times** in `planning/parts/P11-placement-residual/SPEC.md`
and is P11's own addition, made because of a finding in `planning/59-FINAL-UX-EVALUATION.md` §3a.

The sentence a person reads is built by `_abstention_explanation` (`pipeline.py:535-607`). Its
governing rule is stated in its own docstring: two reasons get a rewritten sentence because *"the
default sentence describes [them] falsely"*, and every other reason keeps the default, because
*"giving all of them a reassuring new voice would erase the one honest report of a genuine evidence
failure."*

| reason | when | what the person is told |
|---|---|---|
| `no_supported_destination` | nothing cleared the support threshold, or nothing was retrieved | the default: *"No legal destination cleared §6.10's conditions (no_supported_destination). Abstaining is the correct outcome; the evidence is retained and the file has not moved."* |
| `low_margin` | the margin failed and **only one** candidate cleared support on its own | the default sentence, with `low_margin` in the parentheses |
| `multiple_supported_homes` | the margin failed and **two or more** candidates cleared support on their own | its own sentence: *"…each cleared §6.10's support threshold and nothing in the evidence separates them, so this file has more than one supported home. Nothing moved: which one is its home is a choice about your material, not a gap in the evidence."* |
| `semantic_only` | the best candidate was reached only by embedding/label similarity | the default |
| `generic_hub_only` | the best candidate's graph has anchors but no informative entity | the default |
| `conflicting_facts` | nothing survived retrieval **and** a conflict fired | the default |
| `no_shared_branch` | §6.9 multi-home with no shared branch | never reaches this function — `_multi_home_decision` writes its own sentence (below) |
| `budget_deferred` | an §8.6 ceiling stopped the work | the default, with `budget_deferred` in the parentheses |
| `privacy_blocked` | §8.4 declined the dossier | three distinct sentences, below |

**`multiple_supported_homes` is the important one.** Two legal homes is a real state, not a
confidence failure. `scoring._reason` (`scoring.py:87-117`) tells the two margin failures apart by
counting how many candidates cleared the support threshold *on their own* — counted over all
candidates, not the top two, *"so three tied homes read the same as two"* (`scoring.py:144-151`).
The docstring names the defect it fixes: *"a research paper that is also school homework, reported
as an evidence-quality complaint… one makes them distrust the extraction and the other lets them
just pick."* Nothing about routing changes — both are `weak`, both require review, neither moves a
file. Only the sentence differs.

**`privacy_blocked` has three distinct causes and three distinct sentences**
(`pipeline.py:563-602`):

1. **Unclassified** — nothing has said what kind of material this is.
   > *"This file has not been classified — nothing has yet said what kind of material it is — so it
   > was not shown to a model and nothing moved. It is waiting for you to say what it is, not marked
   > sensitive and not judged on thin evidence."*

   This sentence was **corrected on 2026-08-29**. It used to end *"nothing has been able to read
   enough of it"*, and `planning/65` §4.1 caught that on a live run: all four files had a `direct`
   fact in `file_facts` and zero rows in `classifications`. *"Reading is the step that WORKED and it
   was the step the sentence blamed."* The comment at `pipeline.py:565-584` records the rule it now
   obeys: P11 knows nothing classified the file; whether it was *readable* is P4's
   `extraction_runs`, which P11 does not read *"and must not guess at"*, so the sentence names the
   step that stopped and claims nothing about the one before it.

2. **Protected** — the user marked this material sensitive.
   > *"This file is protected material (§8.4), so nothing about it was assembled for a model and it
   > was left exactly where it is. That is a deliberate decision about sensitivity, not a failure to
   > find a destination."*

3. **Offline install / mode denial** — the operation mode forbids cloud egress.
   > *"Deciding this file needed a model, and §8.4 did not clear this file for a model call. Nothing
   > about it left this device and nothing moved; the evidence is retained."*

The three are kept apart by `privacy.py`. `is_unclassified` is a single definition
(`privacy.py:138-145`) precisely because *"two callers ask it for two different purposes… and a
second spelling is how the two would come to disagree about the same file."* The module is emphatic
that unclassified and protected never collapse: *"A passport is material the user marked sensitive
and the product deliberately did not open; an unreadable scan is material nothing could tell
anything about."*

**`no_shared_branch`** is written by `_multi_home_decision` (`pipeline.py:993-996`) with its own
sentence for all three of §6.9's outcomes:

> *"This file has accepted membership in more than one packet. §6.9 permits a shared branch, a
> question, or an abstention, and never an arbitrary choice between the packets."*

**Budget deferral is structurally separated from abstention.** `_abstention`
(`pipeline.py:620-624`) refuses a record where `reason == budget_deferred` and `deferred_stage` is
`None`, or the reverse; `records.py:455-460` refuses the same shape; and `stage_output.py:43-65`
maps P11's three results to three *distinct* P2 envelopes, asserted distinct at import, so a
deferral is `deferred`/`ceiling_reached` and never `abstained`/`within_ceiling`. The reason is
stated at `stage_output.py:11-14`: scored as `abstained`, P2 *"would grade a ceiling-truncated run
`abstained_correctly` or `abstained_incorrectly` — a judgement about evidence — when no judgement
was made."*

That separation holds in the record and in the P2 envelope. It does **not** hold in the sentence:
see §7.15.

---

## 7.6 Group plans — placing a group rather than a file (§6.8)

`place_group` (`pipeline.py:802-868`) runs §6.8 in §6.8's order:

1. **Read the group as this plan version sees it.** `accepted_group_as_of`
   (`groups.py:99-125`) asks P9's `group_state_as_of` at P10's frozen version and refuses anything
   that is not `accepted`. Reading `Group.state` directly *"would answer `supported` in every
   version, and P11 would place a group nobody accepted."*
2. **Classify each member through the ordinary path**, passing `group_plan_id` down so the
   **stored row** carries it. It is passed in rather than patched on afterwards because *"a row
   written without it would make the review surface show several unrelated file moves while the
   in-memory plan looked correct"* (`pipeline.py:281-284`).
3. **Confirm the shared parent.** `confirm_shared_parent` (`groups.py:191-200`) returns the single
   distinct parent if all members agree, and `None` otherwise. It is explicitly **never a majority
   vote**: *"A majority would place the minority members somewhere their own evidence does not
   support, which is exactly the 'moved because it resembles a folder' failure §6.12 prohibits."*
4. **Exclude outliers.** A member P9 flagged is excluded and explained, never forced in.
   `excluded_outlier_for` (`groups.py:203-231`) refuses to build an exclusion for a member P9 did
   *not* flag — *"building an exclusion for a member P9 called `none` would publish a finding P9
   never made."* The exclusion carries P9's competing values as `conflicting_fact`, an
   `evidence_ref`, and a route: the node it went to instead, or `review_queue`.

`GroupPlan.__post_init__` (`groups.py:154-177`) enforces two invariants: every member decision
shares the plan's id — *"that shared id is what makes the review surface show one plan rather than
several unrelated file moves"* — and no file appears both as a member and as an excluded outlier,
because *"one presentation cannot say a file was placed with the group and left out of it."*

`_record_group_plan` (`pipeline.py:871-910`) persists it to `placement_group_plans`, superseding any
live plan for the same group first. Without it *"a review surface reopened a day later would find
four file decisions and no evidence they were ever one plan."*

**§6.9, the multi-home file.** `run_corpus` detects multi-home membership **before anything is
placed** (`pipeline.py:1231-1246`) and passes those file ids to every `place_group` as
`skip_file_ids`, because *"placing it inside the first plan and correcting afterwards would mean the
arbitrary choice was made and then withdrawn, which is not the same as never making it."*

`resolve_multi_home` (`groups.py:234-279`) then returns `(place, shared_branch)`,
`(ask_user, competing_ids)` or `(abstain, no_shared_branch)`. Its guarantee is structural:
*"There is no branch of this function that returns a member of `candidate_node_ids`."* It raises
`InstitutionalDestinationRefused` if the shared branch offered *is* one of the competing homes —
*"§6.9's shared branch is a destination above the competition, not one side of it."* Whether the
answer is `abstain` or `ask_user` is SPEC Open question 6; the selector is injected and its absence
refuses.

---

## 7.7 Residual sets (§7.5) and the set-level gate (§7.6)

**Residual runs second, enforced by a raise.** `surface_residual_sets`
(`residual.py:133-205`) refuses a caller passing `placement_pass_complete=False`: *"Surfacing now
would call a file unplaceable before the engine finished trying."* `run_corpus` calls it once, after
every group and every file has been through §6 (`pipeline.py:1304-1310`).

**The partition is injected. P11 invents no set names.** `residual.py:145-150` refuses a `None`
partition, citing §7.5's own preface — *"'It may show' — illustrative counts, not a fixed
taxonomy (SPEC Open question 10)."*

**Nothing may be dropped and nothing invented.** `residual.py:158-166` checks that the partition's
member ids are exactly the unplaced ids, and names both directions of the failure: *"Every unplaced
file appears in exactly one review set or it is never shown."* The reason is that *"the residual
screen is the last place a file can be mentioned at all."*

**Seven attributes each set must carry**, plus its id, label and members (`ResidualSet`,
`residual.py:74-108`):

| attribute | §7.5's question |
|---|---|
| `representative_examples` | what is in here? |
| `file_type_distribution` | what kinds? |
| `age_range` | how old? |
| `evidence_availability` | is there OCR/text, or nothing? |
| `sensitivity_status` | is any of this sensitive? |
| `weak_graph_neighbours` | what is it faintly connected to? |
| `reason_not_placed` | why could the pipeline not safely place these? |

`reason_not_placed` is required by a raise: *"a set with no reason is a pile."* `file_count` must
equal `len(member_file_ids)`, *"or the review screen reports a number no one can expand."*
`protected` must be a real boolean, never `None`, because *"a null here would be read as `false` by
every consumer that tests it — a protected set becoming an ordinary one."*

**The batch ceiling splits; it never truncates.** `residual.py:171-177`:

```python
batches = [members[i:i + ceiling] for i in range(0, len(members), ceiling)]
```

with the comment *"Split, never truncate: §8.6 reduces work and never drops files."* Each batch
becomes its own set, labelled `(1 of 2)`, `(2 of 2)`. `planning/68-PERSONA-RERUN.md` §3 F7 records
this working on a real corpus: 13 unplaced files, `residual.max_files_per_review_batch = 8`, two
sets of 8 and 5 — and records that its first draft misdiagnosed the cause and was corrected.

**The set-level gate.** `require_set_decision` (`residual.py:244-261`) raises if the set has no
recorded decision, and `require_model_call_permitted` (`residual.py:280-305`) is the one gate in
front of a per-file model call. It has **three** refusals in a deliberate order:

1. **Protected first, and independently of any decision.** `ProtectedSetNotReadable` — *"a
   protected set that refuses for want of a decision would invite the fix 'decide it', and the
   answer to a protected set is never a decision. It is counted, explained and left closed."* It
   raises rather than returning `False` because *"`False` is indistinguishable from 'the user chose
   to leave this alone'… one is a choice, the other is a prohibition"* (`residual.py:15-21`).
2. No set decision → `SetDecisionRequired`.
3. A decision that did not ask for a model → `ModelCallNotAuthorised`. Exactly one of §7.6's four
   choices asks for one; a set the user chose to leave in place produces **zero** calls.

**The residual library is P10's.** P11 holds no template definitions (M10). An enabled residual
branch arrives as an ordinary node carrying `node_role = residual` and a `disposition`, and a
template the user did not enable has **no node** — *"so the §7.7 model cannot name it and P11 needs
no residual-specific legality path at all"* (`residual.py:23-26`). Which fallback folders exist is
therefore entirely a function of what the user enabled at tree design.

---

## 7.8 The eight actions and the loop back to §6

`ACTION_OUTCOME` (`residual.py:323-334`) maps §7.7's eight actions onto §6's outcomes, and asserts
at import that its keys are exactly P8's `RESIDUAL_ACTIONS` — *"a P8 addition break[s] here loudly
rather than fall[s] through to a default"* — and that `ask_user` is not among the values, because
the residual path is closed to it.

| §7.7 action | outcome | qualifier |
|---|---|---|
| return to a confirmed domain group | `return_to_placement` | `return_target.kind = confirmed_domain_group` |
| return to an accepted graph/purpose packet | `return_to_placement` | `return_target.kind = accepted_graph_or_purpose_packet` |
| choose one approved residual destination | `place` | `destination.node_role = residual` |
| choose an approved broad parent branch | `place` | `node_role = ordinary`, levels in `unsupported_levels[]` |
| mark for Review Later | `mark_review_later` | — |
| leave in current location | `leave_in_place` | — |
| mark protected or unsupported | `mark_state` | `marked_state` |
| abstain | `abstain` | `abstention_reason` |

`outcome_for_action` (`residual.py:342-390`) requires a target exactly where the record needs one and
refuses one exactly where it does not, because *"Returning `(place, None)` for a destination-less
choice would build a decision `PlacementDecision` cannot construct, and the failure would land a
stage away from the action that caused it."*

**The §7.9 loop.** When a residual review finds a credible connection, the file goes back through
§6. `_review_set_with_model` (`pipeline.py:1196-1208`) writes the residual decision, calls
`place_file` with `returned_from` set to it, then calls `link_return`. Both records persist —
`link_return` (`residual.py:393-427`) refuses to log the traversal unless the placement names the
residual decision, and refuses if the two records concern different subjects: *"§7.9 hands ONE file
back, and a loop joining two subjects explains neither of them."*

The loop is bounded by an injection. `check_return_cycle` (`residual.py:430-465`) refuses without
`max_return_cycles`, citing SPEC Open question 8 — *"an unbounded loop is a replay that never
terminates."* It counts only live rows, because counting superseded ones *"would make the number
mean 'times somebody edited the record'."*

---

## 7.9 Review policy — how much trust a decision demands

Three values (`vocabulary.py:255-260`): `auto_eligible`, `review_required`, `blocked_pending_user`.
`review_policy_for` (`privacy.py:197-241`) is the single producer, and **every** path to
`auto_eligible` is narrow: six things each forbid it on their own, in this order.

```
is_unclassified                        -> blocked_pending_user
not moves_files(disposition)           -> review_required   (§7.4 review-only / leave-in-place)
protected and not automatic_move_permitted -> review_required   (Design:185)
two_condition.requires_review          -> review_required   (§6.10)
group_support.membership == user-attached -> review_required (M12)
not unique_direct_match                -> review_required   (§6.6)
                                       -> auto_eligible
```

**The ordering is argued, not incidental.** The unclassified check is first because
`blocked_pending_user` and `review_required` are different obligations: *"a reviewer can confirm a
decision that merely needs confirming and cannot confirm one whose subject nothing has
classified"* (`privacy.py:244-250`). The disposition check is second because 00:121's word is
*"never"*, and *"a disposition gate placed after the scoring checks would be one a high enough score
could reason its way past."*

**This is where §6.11's demand — that a direct placement and a context-supported one must not demand
the same trust — is realised.** Only a `unique_direct_match` can be `auto_eligible`. A
context-supported placement always carries `requires_review = True` from
`assess` (`scoring.py:198`), and `records.py:462-471` refuses an `auto_eligible` record whose
verdict requires review or which rests on a `user-attached` membership.

`destination_disposition` has **no default parameter**, deliberately: *"A caller that forgot it
would get the ordinary-node answer and silently lose the gate, which is precisely the state this
field was already in — written, validated, and read by nothing"* (`privacy.py:221-223`). That is the
record of a real prior defect: `IndexEntry.disposition` was built and validated by `index.py` and
read by nothing until this function was wired to it.

**`model_eligibility` is derived, not read** (`privacy.py:10-24`), because §8.4's three values have
no producer in `src/privacy/`. Three separate causes produce `local_only`: an unclassified file, a
mode that forbids cloud egress, or the protected flag. Each gate is a live P7 predicate —
`mode_forbids`, `unclassified_denies`, `may_move_automatically` — asked rather than re-derived, *"so
if P7 ever moves a mode across the line P11 moves with it."*

**An absent classification blocks the file, not the run.** `privacy.py:26-35` records the change and
its reason: raising *"meant ONE such file refused an entire corpus. A person with ten thousand files
and one ambiguous scan got a traceback where a plan with one file marked for review was the correct
answer."*

---

## 7.10 Correction learning (§8.7)

**A correction record is an event, not a second store.** `record_correction`
(`learning.py:166-193`) appends to P1's `events` table with §8.7's columns: `correction_scope`,
`correction_subject`, `polarity` (`accept` | `reject`), `proposal_class` (`placement` | `residual`),
`basis_key`, plus the action name, the user id, and an explanation. *"P1 owns `events` and its §8.7
columns, and `learning_records` already honours a reset as a cutoff without deleting anything."*

**The basis key is the pair §8.7 names**: `basis_key_for` (`learning.py:76-78`) returns
`f"{subject_id}->{node_id}"`. It deliberately **omits the content hash**: *"§8.7 is about what the
user decided, and editing a file does not un-decide it — a versioned key would silently stop
matching on the next save and resurface exactly the destination the user rejected."*

**Scope is the whole safety property, and it is never widened.** Six scopes: `file`, `group`, `node`,
`corpus`, `template`, `domain`. `_subject_ids` (`learning.py:81-121`) can address four of them — the
file, the group, each candidate node, and a corpus subject the caller names — and **refuses**
`template` and `domain` outright:

> *"answering `()` for them would report 'the user rejected nothing' for a question that was never
> asked. That is the difference between a suppression that is absent and one that was never looked
> for, and only one of them is safe to auto-place on."*

That is the code's expression of §8.7's governing example: one transcript belonging in a Columbia
packet must not teach the engine that all transcripts do. `learning.py:8-11` states it as the rule
the module exists for.

**Suppression is consulted before `place` is emitted.** `pipeline.py:316-337` queries
`suppressed_nodes` at the `file` scope only, and drops the rejected nodes from the candidate set.
Only `file` — *"asking for them here would look like a wider check and perform none."* A hit means
the node is skipped, *"never auto-placed and never silently re-ranked, because a silent re-rank
would hide from the user that their own correction was the reason"* (`learning.py:128-133`).

**A residual rejection is not a placement fact.** `review._PROPOSAL_CLASS` (`review.py:55-58`) maps
each of P13's four surfaces to the store the correction belongs in: *"A rejection taken on a
residual surface is a residual fact: read back as a placement fact it would suppress a node the user
never saw in the §6 pass."*

**`change_destination` records the node moved *away from*, not to.** `_node_in_question`
(`review.py:176-196`) reads the live decision's own node, because *"Keying the rejection on the
payload instead would suppress the destination the user had just chosen, and the mistake would only
surface on a later run."*

**`defer` has no polarity.** `_POLARITY` (`review.py:70-75`) maps six actions and asserts `defer` is
absent: *"it is a decision to decide later, and recording it under either polarity would teach the
engine something the user did not say."* The action is still logged, because *"a deferral the log
cannot show is a gap in the reconstruction §8.2 exists to make possible."*

**Creating a folder is P10's edit, and the routing is readable.** `routes_to_p10`
(`review.py:103-110`) returns `()` and writes one log line, *"because the prohibition (§6.12) is
about the SYSTEM inventing one and this is the user"* — and *"a receiver that swallowed it silently
would look identical from every assertion about what did NOT happen."*

---

## 7.11 Plan versions (§8.8)

Every P11 table carries `plan_version`, because a decision, a group plan, a set decision and the
whole index are *projections of one frozen tree* (`schema.py:1-8`). Every table is append-only by
trigger: a `BEFORE DELETE` raise and a `BEFORE UPDATE OF <every non-supersede column>` raise
(`schema.py:176-190`), so a writer correcting an outcome in place fails rather than losing the
original.

`store.record_decision` (`store.py:78-149`) does the supersede, the insert and the event in **one
transaction**, and supersedes *before* it inserts because `one_current_placement_decision` is a
partial unique index over unsuperseded rows.

`versions.reproject` (`versions.py:67-…`) is §8.8's re-projection and *"marks, and it never
matches."* It matches through **lineage** — `decision.node_id → from-version entry →
origin_node_id → to-version entry` — because P10 mints a new `node_id` per version, so matching on
`node_id` *"would mark every decision for renewed review after any tree edit at all — including a
pure rename, which §8.8 forbids by name."* There is deliberately no third branch: a removed node
usually has a plausible survivor, and matching onto it *"is the 'silent reclassification' §8.8
prohibits by name."* It writes nothing to `placement_decisions`; the mark is a computed diff.

---

## 7.12 Where P11 is measured (§8.5)

Two stage ids, drawn from P2's closed ten: `candidate_node_retrieval` and `placement_scoring`
(`vocabulary.py:356-358`). `P11` is not a stage id.

`stage_output.py` maps P11's three results — `decision_written`, `evidential_abstention`,
`budget_deferral` — onto three distinct `(outcome, budget_state)` envelopes, asserted distinct at
import. The retrieval stage's subject ref is namespaced `candidates:{plan_version}:{subject_ref}`
(`stage_output.py:134-150`) because `retrieval` is already P9's dimension name and an un-namespaced
ref *"would make a full-pipeline replay raise `IntegrityError` the moment P9 and P11 both keyed a
`retrieval` row on the same file."*

Both stage emissions are conditional on a `P2Run` injection (`pipeline.py:264-267`, `338-341`). The
shipped CLI passes `p2=None` (`cli.py:731`), so **a real run writes no stage outputs at all** — a
declared state, not a gap (`pipeline.py:140-149`).

---

## 7.13 What is built and inert

Grepped across `src/`, excluding each function's own module, the following P11 entry points have
**no caller anywhere on the run path**:

- The whole §7 review workflow: `review_residual_sets`, `run_residual_file`, `record_set_decision`,
  `require_model_call_permitted`, `model_calls_permitted`, `outcome_for_action`, `link_return`,
  `check_return_cycle`, `ACTION_OUTCOME`. `surface_residual_sets` is the only §7 function `run_corpus`
  reaches. **The eight §7.7 actions exist, are mapped, are tested — and nothing in a shipped run can
  invoke one.**
- The whole §8.7 receiver: `placement/review.py` (`apply_review_action`, `correction_scope_of`,
  `routes_to_p10`) and `learning.record_correction`. Corrections can be *read* (`suppressed_nodes`
  is called by `place_file`) but nothing in `src/` can *write* one. The learning store is
  permanently empty on a real run.
- §8.8's `versions.reproject` and `learned_preferences_still_applicable`. Only mentioned in a P10
  docstring.
- `store.decision_history`, `store.placed_node_ids`, `index.entries_for_plan`,
  `privacy.moves_files` as a public predicate, `placement/fixtures.py`.
- Two of the four weighted retrieval channels — `GRAPH_RELATIONSHIP` and
  `STRUCTURAL_RELATIONSHIP` — are declared in `CHANNELS` and weighted in `_CHANNEL_WEIGHT` and are
  **never assigned to a candidate**.
- `Subject(kind="group")` is a legal record shape with validation of its own and is **never
  constructed in `src/`**. §6.8 places a group as N file decisions sharing a `group_plan_id`, not as
  one group-subject decision.
- `CorpusResult.group_plans`, `CorpusResult.unplaced_file_ids` and `GroupPlan.excluded_outliers`
  are read by **nothing** in `cli.py` or `production.py`.

The common cause for the first three bullets is P13: every one of them is a receiver for a user
gesture, and the review screen that produces the gesture does not exist.

---

## 7.14 What actually happens on a real run today

`planning/68-PERSONA-RERUN.md` ran the shipped command over four corpora — a litigator, a PhD
student who TAs, a two-child household, and one person who is all three — 26 files total.

**Every file abstained. Zero files were placed. In all four runs.**

The chain that produces this, in the code:

1. **No classifier ships.** The CLI injects a detector that produces nothing;
   `classifications` holds zero rows in all four databases while `file_facts` holds a `direct` fact
   for every file. `privacy_state_for` (`privacy.py:118-135`) therefore resolves every file to
   `unreadable_unclassified`, and `unclassified_denies` makes `model_eligibility = local_only`.
2. **The support threshold is not reached deterministically.** The deployment writes one direct
   fact per file (`cli.py`'s `DIRECT_SLOTS`, one regular expression). One direct-fact channel scores
   `3/7 = 0.429` against a threshold of `0.50`, so `meets_threshold` is `False`, so
   `unique_direct_match` is `False` (`scoring.py:180-186`), so `needs_model_call` returns `True`.
3. **The privacy gate fires before the model-path check.** `place_file` (`pipeline.py:372-374`)
   asks `may_assemble_dossier(privacy)` first and returns the abstention immediately.
4. So the recorded reason is `privacy_blocked`, cause **unclassified**, and the sentence is the one
   corrected on 2026-08-29.

**What the person reads.** The report (`cli.py:864-975`) leads with protected containers, then the
tree, then one block per *kind* of outcome. For all 26 files that block is:

```
  Waiting for you to say what these are -- 5 files
    motion-to-compel.pdf
    ...
    Same reason for each: This file has not been classified -- nothing has yet
    said what kind of material it is -- so it was not shown to a model and
    nothing moved. It is waiting for you to say what it is, not marked sensitive
    and not judged on thin evidence.
    Held for review as "Not yet placed": no destination in this tree matched them
    well enough to decide without asking you.

Nothing was moved.
```

`68` §4 is fair to this: *"Nothing was misfiled anywhere… the product placed nothing it could not
justify, invented no destination, and moved nothing"* and *"The refusals are legible. A person
reading the report knows what stopped, that nothing moved, and that the product is waiting on them
rather than confused."*

It is also blunt about the result: *"Four people, four disks, one outcome. Nothing was misfiled and
nothing was lost… but nobody got an organisation, and nobody got a single file placed."*

Note what this means for reading the rest of this section: **almost none of the machinery described
above executes on a real run.** No model call, no graph edges, no group plan with a shared parent
that matters, no residual review, no correction, no reprojection. What runs is: build the index,
retrieve candidates, score, fail the threshold, hit the privacy gate, abstain, surface one residual
set.

---

## What looks wrong here

1. **`policy_id` does not travel on any decision, and a comment says it does.** `cli.py:113-114`
   justifies the shipped thresholds on the grounds that *"`policy_id` travels on every decision —
   change a number and change the id with it, or a replay silently compares two different rules."*
   `TwoCondition` (`records.py:280-296`) carries the two floats and no id, `PlacementDecision` has no
   policy field, and `placement/events.py` logs none. Two policies with different ids and identical
   numbers are indistinguishable in the store, which is the exact failure the comment claims is
   prevented. SPEC:802-804 requires both thresholds recorded and does not require the id; the code
   satisfies the SPEC and contradicts its own justification.

2. **Two of the four weighted scoring channels are unreachable, which caps the score at 0.714.**
   `GRAPH_RELATIONSHIP` and `STRUCTURAL_RELATIONSHIP` are weighted in `scoring._CHANNEL_WEIGHT`
   (`scoring.py:42-47`) and are never appended to `Candidate.channels` anywhere in `retrieval.py`.
   The reachable support scores are `{0, 0.286, 0.429, 0.714}`. Against `cli.py`'s threshold of
   `0.50`, **a placement in the shipped deployment is impossible without the accepted-group
   channel** — a file whose facts uniquely and correctly match one node scores `0.429`. The scale
   normalises by 7 for a maximum only 5 of which can occur.

3. **The score counts kinds of evidence, not amount.** `retrieval.py:146` deduplicates channels
   before `scoring.py:75` weighs them, so a candidate matching five of the subject's facts scores
   identically to one matching one. A five-fact match and a one-fact match against the same node are
   the same number on the record, and `alternatives[]` cannot tell a reviewer them apart.

4. **A budget deferral prints as an ordinary abstention, and tells the person the abstention was
   correct.** The record, the P2 envelope and `stage_output.py`'s three-way assert all keep deferral
   apart from abstention. `_abstention_explanation`'s default branch
   (`pipeline.py:603-607`) then renders it as *"No legal destination cleared §6.10's conditions
   (budget_deferred). Abstaining is the correct outcome; the evidence is retained and the file has
   not moved."* `cli.py:800` heads the block *"Waiting for you to say what these are"*, and `cli.py`
   reads `deferred_stage` nowhere. That is precisely the *"understood and found unimportant"*
   impression §8.6 exists to forbid, arriving in the one place a person actually reads. Done-means
   14 is satisfied in the record and defeated in the sentence.

5. **`multiple_supported_homes` is not in the SPEC.** It appears zero times in
   `planning/parts/P11-placement-residual/SPEC.md`, including in the Contract-out mapping table that
   enumerates the non-budget abstention reasons P2 must score as `abstained`. It is a good change —
   `59` §3a's finding is real — but it was made to a vocabulary the SPEC enumerates in three places,
   without amending any of them, while SPEC Open question 4 explicitly asks whether that vocabulary
   is closed.

6. **With no model injections, a context-supported match places without ever consulting the judge
   §6.6 designates.** `place_file` (`pipeline.py:372-401`) calls the model only
   `if inputs.model_path_available()`; when it is not available and `assessment.abstention_reason` is
   `None`, control falls straight through to the `place` at `pipeline.py:407`. The result is a
   `place` with `confidence_class = "context-supported group match"` and `requires_review = True` —
   so not auto-eligible — but §6.6's *"hierarchical destination judge"* was silently skipped rather
   than the decision being deferred. `PipelineInputs.model_path_available`'s docstring defends a
   model-free run on the grounds that *"§6.6 decides a unique direct match with zero model calls"*,
   which is a narrower claim than the code's behaviour.

7. **An outlier's decision row is stamped with the plan that excluded it.** `place_group`
   (`pipeline.py:834-860`) calls `place_file(..., group_plan_id=group_plan_id)` for **every**
   membership, then drops the flagged ones from `member_decisions`. `GroupPlan`'s invariant only
   inspects `member_decisions`, so it passes — but the stored row for the excluded file carries the
   `group_plan_id` of the plan that excluded it. Anything reading `placement_decisions` by
   `group_plan_id` reconstructs a plan that includes its own outliers.

8. **An excluded outlier is invisible in the report.** Its decision is not in
   `CorpusResult.decisions` (`pipeline.py:1258-1260` extends only `plan.member_decisions`), its file
   id is in `covered` so it is never re-placed, and it is therefore not in `unplaced` and never
   reaches a residual set. `cli.py` reads neither `group_plans` nor `excluded_outliers`. A file P9
   flagged as an outlier is decided, stored, and **never mentioned to the person** — the silent
   omission the residual screen exists to prevent, arriving through the group path.

9. **§6.8's "one coherent group plan" is computed, stored, and never shown.** `group_plans`,
   `excluded_outliers` and `unplaced_file_ids` have no reader in `cli.py` or `production.py`. The
   report groups files by `(outcome, destination, explanation)`, which is a grouping by *reason*, not
   by *plan*. The invariant at `groups.py:160-166` — the shared id *"is what makes the review surface
   show one plan rather than several unrelated file moves"* — is enforced against a surface that does
   not consume it.

10. **The shipped residual partition hardcodes `protected: False` and `sensitivity_status: "none"`
    for every set.** `cli.py:710-711`. `ResidualSet` argues at length (`residual.py:101-108`) that a
    null here would turn a protected set into an ordinary one, and then the one partition in `src/`
    asserts `False` unconditionally — including for a set containing a client's passport. It is inert
    today only because `require_model_call_permitted` has no caller; the moment §7 review is wired
    up, `ProtectedSetNotReadable` never fires.

11. **The shipped `evidence_for` hands every file every accepted group id.** `cli.py:692`:
    `group_ids=tuple(accepted_ids)`. The `ACCEPTED_GROUP` channel therefore fires for every file
    against every node associated with any accepted group, regardless of whether that file is a
    member. Given finding 2 — that a placement requires this channel — the only channel that can lift
    a file over the support threshold is one the deployment fires indiscriminately.

12. **Re-running against the same plan version raises `IntegrityError`.**
    `build_destination_index` (`index.py:518-524`) and `surface_residual_sets`
    (`residual.py:192-197`) both plain-`INSERT` with a deterministic `record_id`, and neither
    supersedes an existing row. Both tables carry supersede columns nothing writes.
    `placement_decisions` and `placement_group_plans` handle this correctly; the index and the
    residual sets do not.

13. **`ProtectedSetNotReadable` propagates out of `review_residual_sets`.** `pipeline.py:1344-1351`
    deliberately does not catch it, with a good argument. But the caller is a corpus-level loop: one
    protected set aborts the review of every set after it in `result.residual_sets`, including
    unprotected ones. That is the same shape as the defect `privacy.py:26-35` records and fixed for
    unclassified files — *"ONE such file refused an entire corpus"* — reintroduced one level up.

14. **The `explanation` on a residual decision states an outcome and nothing about the file.**
    `pipeline.py:1092-1095`: *"Residual review of set {set_id} returned {outcome!r}. The set-level
    decision authorised this review and the file has not moved."* §6.11 requires the explanation to
    *"state the actual basis"*. `{outcome!r}` renders as `'place'` or `'mark_review_later'` — a
    Python repr of a machine token, in the field a person reads — and the sentence claims *"the file
    has not moved"* even on `outcome = place`, which is the one outcome that becomes a move.

15. **`ResidualContext.lifecycle_policy_ref` is always `None`.** Every construction site
    (`pipeline.py:1026`, `1151`) passes `None`. §7.11's non-destructive lifecycle has a field on the
    record and no producer; the guarantee that a lifecycle policy is *"a review policy — never a
    deletion or expiry"* is currently true by vacuity.

16. **`ReturnTarget.id` is set to the file id, not to the target.**
    `pipeline.py:1073-1074`: `ReturnTarget(kind=qualifier, id=subject.file_id)`. The SPEC's field is
    the id of the group or packet the file is being returned **to** (SPEC's `return_target { kind,
    id }`, §7.9), and `outcome_for_action` (`residual.py:360-367`) refuses the action unless the
    caller supplies that target — then discards it and stores the subject's own file id. A consumer
    reading `return_target.id` learns which file, not which group.

17. **`_multi_home_decision`'s explanation is the same sentence for all three outcomes**, including
    `place` into a shared branch (`pipeline.py:993-996`). A user whose transcript was successfully
    filed into a shared branch is told that §6.9 *"permits a shared branch, a question, or an
    abstention"* — a statement of policy where the record has an actual answer, and the only §6
    `place` in the codebase whose explanation names no destination.

18. **A third of the part is inert, and the inert third is the half a person interacts with.**
    §7.13 lists it. The eight §7.7 actions, the whole §8.7 write path, `reproject`, and the group-plan
    surface are complete, argued, tested, and unreachable. `suppressed_nodes` is called on every
    placement and queries a table nothing can write to — a correctness check that can only ever
    return empty. Every one of these waits on P13, which does not exist.

---

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

*Landed as `86edf8b`, after this section was written.* The account below was written while the
fix was still uncommitted and is correct about it; two things it could not know are that the clock
was only the FIRST of three collisions (the review step's `superseded_by` stamp and the
composition root's restarting id counter were the other two, each hidden behind the last), and
that the `REFUSALS` point it makes at the end **still stands** and is the more valuable half of
this finding. The original note follows.

An uncommitted fix appeared in the working tree at 04:04 UTC — another agent
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

---

# 9. Designed and not built

Sections 1–8 describe a machine that exists: eleven parts, 5232 passing tests, a command that
runs over a folder on disk and prints a report. This section describes the other thing the repo
contains — a body of design, some of it canonical, some of it dated *after* the machine was
built, whose implementation is zero or nearly zero.

The distinction matters more than any other in this document. A reader who takes `planning/` as
a description of the product will conclude that the product finds files, files files, and asks
the user structural questions. It does none of those. A reader who takes `src/` as a description
of the product will conclude that the design does not exist. Both readings are wrong, and the
gap between them is the subject here.

**Rule followed throughout:** every claim that something is *not* built was verified by search
against the live tree, and the verification command is stated beside the claim. Every quotation
from `00`, `66`, `68`, `69` or either PLAN was grepped before it was quoted.

---

## 9.0 How the absences were verified

Six searches, run against the checkout at commit `dfdc015` (branch
`build/p6-p7-first-packages`), working tree clean except for `planning/70-mechanism/` and
`.superpowers/`:

| Question | Command | Result |
|---|---|---|
| Is there a search entry point? | `grep -rn "def search" src/` | no matches |
| Is there any query/find surface? | `grep -rln "def find(\|def query(\|def search_\|class Search\|SearchResult\|search_index" src/` | two files, both false positives — `src/facts/families.py:209`, `:262` and `src/facts/photo_event.py:191` are union-find `find` helpers with body `while parent[file_id] != file_id` |
| Does anything move, copy, rename or delete? | `grep -rn "shutil\.\|os\.rename\|os\.replace\|os\.remove\|os\.unlink\|Path\.rename\|\.unlink(\|rmtree\|copyfile\|copy2" src/` | **no matches** |
| Does anything write a file at all? | `grep -rn "open(.*['\"][wax]\|write_text\|write_bytes\|subprocess\|os\.system\|os\.symlink\|os\.link\|touch(" src/` | **no matches** |
| Does anything create a directory? | `grep -rn "mkdir\|makedirs" src/` | one hit, `src/database_agent/db.py:44` — `path.parent.mkdir(parents=True, exist_ok=True)`, creating the parent of the SQLite file |
| Do the P12/P13 packages exist? | `ls src/mutation src/review_surface` | `No such file or directory`, both |

Two further checks bear on Find and on onboarding specifically:

- **No function in `src/` accepts a user query string.** The two modules named `retrieval.py`
  take structured inputs, not text. `grouping/retrieval.py:361` is
  `retrieve_neighbors(conn, *, seed, limits, knowledge, embeddings_enabled)` — a seed is a fact
  or a user-designated file, not a phrase. `placement/retrieval.py:86` is
  `retrieve(conn, *, subject, plan_version, limits, facts, group_ids, curated_folder_labels,
  semantic_neighbours, …)` — it retrieves *destination nodes* for a file, the inverse of what a
  person searching wants. `placement/index.py:282` `reachable_entries` indexes tree nodes, not
  file content.
- **The CLI has no verb.** `pyproject.toml` has no `[project.scripts]`; `src/cli.py:988–1016`
  builds one `ArgumentParser` over a positional `directory` plus `--situation`, `--label`,
  `--user`, `--list-situations`. There is no `find`, no `search`, no `apply`, no `undo`, no
  `review` subcommand, because there is nothing for them to call.

---

## 9.1 `planning/66-FIND-FILE-AND-ONBOARDING.md` — canonical, supplied 2026-08-29, implemented nowhere

`66` is 736 lines. Its own header says `**Implementation:** No code written`, and that header is
still accurate. It arrived by commit `b57590d`, one commit before the P12/P13 plans. It is not a
proposal: `69-HANDOFF.md` puts it second in the authority order — *"`00-database-agent-product-design.md`
wins → `66` and the part SPECs → PLANs → live `src/`"* — and both new PLANs restate that, with P13's
version adding the reason: *"`66` is dated 2026-08-29 and the SPEC 2026-08-20."*

So `66` outranks the eleven SPECs the built machine was built from, and none of it is built. That
is the single largest fact in this section.

### 9.1.1 Find (§1–§6) — nothing

**§1, local read-only retrieval.** `66` requires that Find operate on the local index and that
the product *"does not send a user's query, filenames, paths, extracted text, OCR output,
embeddings, file facts, destination tree, or search-result set to a cloud model in order to
return ordinary search results."* It gives the reason as a threat model, not a preference: *"A
file search query can disclose as much as the file itself."*

There is no Find. `grep -rn "def search" src/` returns nothing; no module accepts a query
string; there is no CLI verb. The privacy property §1 protects is currently satisfied
vacuously — nothing leaks a query because nothing accepts one.

**§2, one retrieval model not two rankings.** The requirement is that Find reuse the existing
evidence and retrieval model and *"must not create a second, unrelated ranking system whose
results disagree with the model used for group retrieval or destination-node retrieval"*, and
that raw scores stay out of the primary result in favour of an explanation
(*"Matched in document text," "Part of accepted group: 2026 Job Search"*).

The two retrieval modules that would have to be reused answer different questions from the one
Find asks. `grouping/retrieval.py` finds *neighbouring files for a seed*; its own docstring says
its channels find candidates and *"none of them decides anything."* `placement/retrieval.py`
finds *candidate destination nodes for a file*. Neither ranks files against a phrase. A future
Find that honours §2 has to derive a third use from these two, and no design document says how.
This is not merely unbuilt; the reuse §2 mandates is undemonstrated.

**§3, the six location states.** §3 is the most specific thing in Part I. It gives a table of
six distinct result elements that *"must not be collapsed into one ambiguous list of paths"*:

| State | What `66` says it means |
|---|---|
| Current location | *"The actual path where the file exists now"* |
| Filed home | *"A user-approved physical destination in the active organization plan"* |
| Also related to | an accepted relationship *"that does not imply another physical copy"* |
| Shared-material relationship | *"used by several packets or branches under an approved shared-material policy"* |
| Historical location | *"A prior path recorded in provenance"* — details, not a current home |
| Possible placement | a candidate *"never presented as a home"* |

Nothing in `src/` distinguishes them. The nearest thing is the P13 PLAN's file-structure entry
`src/review_surface/locations.py   \`66\` §3's six-state result element` (P13 PLAN:98) — a
filename in a plan for a package that does not exist. Note the direction of the dependency: §3 is
a *Find* requirement, but the only code slotted to satisfy it lives in P13, the review surface.
Nothing owns it on the Find side.

**§4, protected material present-but-unopened, with a separate unlock.** Two states are
required: standard search shows a *"privacy-preserving indicator"*; unlocked protected search
*"requires explicit local re-authentication or an equivalent deliberate unlock action."* And five
absence states must never share one message — protected, unreadable, still indexing, unsupported
format, no strong match.

The privacy machinery for the first half is partly live: `src/privacy/display.py` publishes
`RedactionSettings`, `DISPLAY_FACETS`, `REDACTION_VALUES == ("shown", "redacted")` and
`ProtectedSummary(count, scope_total, class_breakdown)`, and `privacy.gate.Gate.summarize_protected`
exists. The **unlock** does not: `grep -rn "def undo\|def revoke" src/` returns
`privacy/policy.py`, `privacy/gate.py`, `privacy/revocation.py`, all of which concern *model
consent* revocation, not a local re-authentication gate over search results. There is no
authentication of any kind in `src/`.

The five distinct states are, again, a P13 filename: `src/review_surface/states.py   \`66\` §4's
five distinct absence states` (P13 PLAN:99). Unbuilt.

**§5, index completeness and no-result behaviour.** `66` gives a worked status block
(*"Searching 18,432 indexed files locally / 89 files are still processing / 14 protected items
are hidden in standard search / 27 unreadable or unsupported files are not text-searchable"*).
The counting machinery exists in fragments — `scan_agent.summary.scan_run_summary`,
`evidence_shape.runs.COMPLETENESS`, `database_agent.budget.all_ceilings` — and P13's Task 15
would assemble them into a `progress_line`. But that is the *review* progress line, not the
*search* status line, and §5's specific requirement (*"a no-result response should say…"*) has no
consumer at all, because there is no result set to be empty.

**§6, the first-run screen that asks nothing.** *"The first-run screen should offer local index
setup, not a profile interview."* There is no first-run screen. `src/cli.py:984` `main` parses
argv and runs the whole engine; the only interactive affordance in the repo is
`--list-situations`, which prints 208 situation ids.

**Verdict on Part I: no search capability exists anywhere in `src/`.** Verified by
`grep -rn "def search" src/` (empty), by inspecting the two `retrieval.py` signatures (neither
takes a query), and by reading the full argparse surface at `src/cli.py:988–1016` (no search
verb, no `[project.scripts]` entry point).

### 9.1.2 File (§7–§11) — nothing

**§8's nine policy dimensions.** `66` §8 gives a table binding all nine before a filing policy
may exist: source scope, destination scope, file eligibility, evidence standard, review cadence,
exclusions, collision policy, undo period, pause-and-revoke control. Its governing sentence is
*"A branch permission alone is not an automatic-filing policy"* — source scope is treated as
equal in weight to destination scope.

`grep -rin "filing_policy" src/` returns nothing. There is no policy record, no policy table, no
policy vocabulary. **Both new PLANs record this as a hole in their own coverage rather than
working around it.** P12's "not built" table lists *"a filing policy"* under ratified decision
**A7** (no invented authorities). P13's is blunter:

> A dry-run surface (`66` §9) — *"There is no filing-policy record in any part's Contract-out and
> no `src/` package for automatic filing… Task 11's `ActivityEntry` carries the gap explicitly.
> This is a real hole in P13's coverage of `66`, not an omission of convenience."*

**§9's dry run and progressive authorisation.** *"The first run of every filing policy is a dry
run."* The escalation ladder — narrow policy → dry preview → user review → approve → reviewable
plans → *"Only after repeated successful review may the user enable direct moves"* — has no
implementation and no record to hold the trust state that would gate it. `grep -rin "dry_run" src/`
returns nothing.

**§10's required declines with distinct language.** `66` enumerates roughly a dozen conditions
that must produce a decline, each with its own sentence (*"This file has two approved homes,"*
*"I could not read this file,"* *"This item is protected by your privacy policy,"* *"This file
changed after the preview,"* *"No approved destination fits"*). P13's "not built" table divides
these honestly: some map onto records that exist (`placement.vocabulary.ABSTENTION_REASONS`'
nine, the five staleness triggers P12 would publish), and *"the rest — 'This file has two
approved homes', 'No approved destination fits' — are **filing-policy refusals with no
producer**."*

**§11's 90-day conditional undo and stale plans.** *"The recommended default undo retention
period is 90 days"* with 30 / 90 / one year / until-cleared as alternatives; every move
*"remains conditionally undoable"* subject to five verification conditions; a plan whose inputs
changed *"becomes stale"* and must be refreshed rather than applied.

None of it exists. The undo journal is P12's Task 8 and Task 11; the retention period is P12's
Task 13.

**Verdict on Part II: nothing in `src/` moves, copies, renames or deletes a file.** Verified by
`grep -rn "shutil\.\|os\.rename\|os\.replace\|os\.remove\|os\.unlink\|Path\.rename\|\.unlink(\|
rmtree\|copyfile\|copy2" src/` → **no matches**, and by
`grep -rn "open(.*['\"][wax]\|write_text\|write_bytes\|subprocess\|os\.system\|os\.symlink\|os\.link" src/`
→ **no matches**. The only `mkdir` in the tree creates the parent directory of the SQLite
database (`src/database_agent/db.py:44`). The product is, at this commit, incapable of touching a
user's files, and every "materialise" in `src/tree_design/materialise.py` composes records, not
directories.

### 9.1.3 Onboarding (§12–§17) — one thing, and it is the storage half of one section

**§12, not a profile questionnaire.** *"Onboarding must therefore be redesigned as a
structural-question system embedded in the relevant product mechanisms. It is not a weekly
questionnaire, a generic profile, a growth loop, or a casual conversational feature."* The
mechanism must ask *"only when a specific decision is blocked."*

`grep -rin "onboarding\|questionnaire\|structural_question\|question_registry" src/` returns
nothing that is a mechanism. The hits are: `src/cli.py:182`, a comment quoting `63` §10's rule
(*"No onboarding answer could have…"*); library JSON rows about HR onboarding-offboarding as a
*domain*; and `applicabilities.json` ids. There is no question, no registry, no trigger, no
answer store.

**§13, structural versus contextual.** The table is a safety boundary, not a nicety. A
contextual answer *"must not… Create, remove, hide, or rename folders; gate placement; authorize
movement; change privacy state; or silently become a structural rule."* Since there are no
answers of either class, the boundary is unenforced but also unviolated — there is nothing to
enforce it against, and nothing in `src/` records an answer class.

**§14, ask only when needed.** The Columbia example (*"We found files connected to Columbia. /
Which describes your relationship to Columbia?"* with `I study there` / `I teach or work there` /
`Both` / `It is not about me` / `Skip for now`, and the closing line *"It will not create or move
folders by itself"*) is the design's model of a good question. Nothing asks it. `src/cli.py` is
explicitly a no-questions deployment: its `ask_or_abstain` seam is
`lambda node_ids: pv.ABSTAIN` (`src/cli.py:724`).

**§15, other people and person-shaped folders.** The permission table — person-shaped folders
permitted for self, for a *"dependant or child whose records the user manages"* (protected family
area, review-only by default), optional for a household member; **prohibited** for client,
patient, employee, candidate, student, and unknown — has no code. There is no relationship
category, no protected family area, no name store.

The engine has a *negative* alignment here that is real and worth stating: `people` is a declared
field with `destination_eligible=False`, so no person's name can currently become a folder level.
`68` F5 records the consequence honestly — Tom's two children's report cards form one group,
because *"no field names a person in a way a destination may use"* — and adds *"No code should
guess at it in the meantime, and none does."* That is correct behaviour and it is also the
absence of the feature.

**§16, the profession and role matcher.** `66` calls it *"an open design problem"* requiring a
dedicated subsystem, multi-role support, an unmatched state that stays unmatched (`66` §16 uses the
example verbatim: *I'm a sound engineer* *"must not silently activate an engineering or
software-project schema merely because the words are superficially similar"*), and four possible
outcomes. Nothing. `69` §4 item 3 lists *"The role-declaration guidance he still owes
(`66` §16). Nothing in §16 should be built until it arrives."*

**§17, re-running structural questions with a versioned draft plan — the one implemented thing.**
§17 requires that changing a structural answer *"creates a draft plan version"* showing a diff
across six dimensions, and that it *"must not silently rename folders, reclassify files, reveal
protected records, or move anything as a consequence of a changed answer."*

The **storage half** of that shipped in `dfdc015`, the tip commit:

- `src/tree_design/user_edits.py` (286 lines) stores a user's rename durably, keyed on
  `(uses_schema, role_ref, field_ref)` rather than on a node id or a template version. Its
  docstring argues the key choice at length: *"`node_id` fails. §8.8 mints a new one per plan
  version"*; *"`template_id@version` fails. It is the PACKAGING"*; the vocabulary triple *"stays
  true across a re-route, a re-version and an upgrade."* It publishes `UserLevelEdit`,
  `UnappliedUserEdit`, `user_level_edits`, `describe_applied_edits`,
  `OVERLAY_ACTIONS_WITH_A_WRITER`. Four of six dimension actions are refused by name at the
  writer, because *"A stored edit nothing can apply is a silent no-op that outlives every
  session."*
- A test pins the non-mutation property:
  `tests/p10/test_p10_user_edits.py:509`
  `test_an_edit_is_readable_as_the_users_own_assertion_before_any_plan_adopts_it`. Its two
  assertions are the edit's readability by vocabulary key, and, at lines 538–541:
  *"the approved structure did not move because the answer changed. The edit is stored; the
  frozen tree is untouched until something designs again and the user adopts what comes back"* —
  asserted as `frozen_tree(...) == before`.

The test's own docstring names what is missing: *"The presentation half — a draft the user adopts,
with a diff — is P13's and is not built."*

**So the exact answer to "which of §12–§17 has any code" is: §17's storage half, and only that.**
One module and one test. Everything else in Part III — the question registry, the ask-when-blocked
trigger, the structural/contextual split, the family workflow, the relationship categories, the
profession matcher, the draft-plan presentation — is unbuilt.

And even the built half is partial in a way the P13 plan quantifies: **three of `66` §17's six
diff dimensions have no producer anywhere** (P13 PLAN:7464). *"Which schemas become active or
inactive"* — none, because `UserLevelEdit.uses_schema` is *"a schema name on an edit, not a schema
activation delta."* *"Whether any protected area changes"* — none, because
`tree_design.freeze.represent_protected_areas` builds protected nodes and *"nothing diffs them
across versions."* *"Whether any filing policy is paused"* — none, same missing filing-policy
record as everywhere else. The plan carries all three as `None` with a note *"never faked and
never quietly dropped."*

### 9.1.4 §21's open design work and §22's release order

**§21** names five cross-cutting contracts that *"are not minor interface details"* and must be
designed before implementation: the **profession and role matcher**; the **structural-question
system** (*"a registry of questions, their trigger conditions, the decisions they unblock, allowed
answer types, data classifications, scopes, revocation behavior, plan-version effects"*);
**protected search** (unlock behaviour, re-authentication, search-history controls, shared-screen
behaviour, *"test cases for metadata leakage"*); **automatic filing** (policy schema, dry-run
contract, stale-plan detection, cloud-sync behaviour, conditional undo, *"an evaluation suite
built around harmful misfiling cases"*); and **multi-home organization** (the §3 six states).

Of those five, one has a written implementation plan (automatic filing's execution half, as P12),
none has code, and three have not been designed at all.

**§22's release order, reproduced:**

1. **Find first** — *"Find should ship first as a local, read-only capability,"* with local
   indexing, unprotected retrieval, current locations, accepted relationships, match explanations,
   index-status language and protected-presence indicators.
2. **Connect Find to the review surfaces** — *"to the existing evidence inspector, accepted groups,
   destination-tree canvas, and review surfaces so that users can move from 'I found this' to 'I
   understand why this is related' without any hidden state change."*
3. **The onboarding question registry** — *"The team should first define the structural-question
   registry and how each answer connects to a specific schema, template, privacy rule, or policy
   gate. Only then should product design implement the task-triggered interaction flows."*
4. **P12** — not named as "P12" in §22, but the mutation layer everything after Find depends on.
5. **Automatic filing last** — *"It should not be scheduled until P1–P11 are verified and the team
   can demonstrate that the product declines unsafe cases reliably."*

**Where the project actually stands against that order:** at step **zero**. `69-HANDOFF.md` §4
lists the next actions and its item 5 restates the sequence verbatim — *"Then `66` §22's sequence,
unchanged: **Find** (local, read-only) → connect Find to the review surfaces → the onboarding
question registry → P12 → automatic filing"* — and immediately adds:

> **Do not start P12 or P13 from their new PLANs yet.** They exist so that the work is ready when
> the sequence reaches it.

Three of `69` §4's four preceding items are decisions owed by Joseph, not work: the classifier
sizing question, confirmation of `66` §24's judgement repair, and the §16 role guidance. The
fourth is an unanswered scoping question about Find itself — *"What subset of P1–P11 does Find
actually need? Find needs the index, evidence, retrieval and privacy. It does not obviously need
frozen trees or placement, in which case it ships earlier than the full gate. Still open from `67`
§6."*

So the first item in the release order does not yet have an answer to *what it is built on*, let
alone a plan or code.

---

## 9.2 P12 and P13 — full plans, written 2026-08-29, no code

Commit `93b788d`, `docs(p12,p13): implementation plans for apply/undo and the review surface`.
Two PLAN documents of 8592 and 8607 lines. `ls src/mutation src/review_surface` →
`No such file or directory`, both.

### 9.2.1 P12 apply/undo — 14 tasks

**What it would build**, in its own words: *"a deterministic transaction layer over P1's file
record, verification points and event log. It resolves a P10 frozen-tree `node_id` to a filesystem
path, builds a §8.3 move plan, evaluates preconditions twice, applies one action at a time, and
appends a journal entry."* Twenty-one source modules under `src/mutation/`, six tables inside P1's
single database, append-only by SQL trigger.

**Move plans.** `src/mutation/plan.py` would build the §8.3 record and refuse to build one where
the design says so. Four of the ten refusal classes are evaluated at construction —
`node_not_in_frozen_tree`, `node_refuses_placement`, `node_path_collision`,
`cross_folder_not_permitted` — and `review_policy_unsatisfied` is *deliberately* excluded from
that set, because §8.3 requires the plan to be built so it can be shown to the user.

**The five staleness triggers** (P12 PLAN:631, `vocabulary.py`): `content_hash_differs`,
`source_path_changed`, `destination_changed`, `source_vanished`, `permission_lost`. Task 5's
done-means is that each *"is independently reproducible against a fixture and yields
`stale:<trigger>`, no mutation, an `external modification detection` event, and a refresh prompt —
never an automatic apply."* The plan draws one distinction worth flagging: an occupied destination
is a *collision*, not staleness; `destination_changed` means occupancy changed **between the two
checkpoints**, *"which is why `evaluate_preconditions` takes `occupant_at_prepare` from the V1
verdict rather than reading it off the plan."*

**The four collision behaviours** (P12 PLAN:668): `preserve_both_deterministic_suffix`,
`merge_only_if_hashes_identical`, `retain_newer_older_to_version_family_review`, `stop_and_ask` —
each with its own outcome constant, and no path that overwrites. The suffix *format* is
unspecified by the SPEC (flag F4) and is injected with no default.

**The four verification points** already exist in P1 and P12 would be their only caller:
`database_agent.verify.VerificationPoint` publishes V1 *"before preparing a filesystem action"*,
V2 *"immediately before executing a move or copy"*, V3 *"after completing the action"*, V4
*"cross-volume copy-and-delete destination confirmation"*. The plan documents two traps it found
by reading P1's source: `verify_content` hashes `files.current_path` rather than a path passed in,
so the correct order is *"move → `observe_path(destination)` → `verify_content(V3)`"*; and
`verify_content` swallows `OSError` and returns `"mismatch"`, so P12 must test existence and
readability *before* calling it or `source_vanished` and `permission_lost` *"can never fire and
both collapse into `content_hash_differs`."*

**The journal** (`src/mutation/journal.py`) is append-only; **conditional undo**
(`src/mutation/undo.py`) reverses or surfaces a conflict and touches nothing, with five undo
verdicts; `src/mutation/directories.py` reverses the directories one action created on the same
conditional terms; `src/mutation/retention.py` implements `66` §11's retention period. Task 13 is
the one task whose done-means are entirely `66`'s rather than the SPEC's.

**Seventeen conflicts are flagged and none resolved.** The rule is stated at the top: *"An
implementer who hits one should build what the task says and leave the flag standing."* F1 —
`root_anchor` *"has a consumer and no producer"*, nothing in `src/` maps a `root_anchor` string to
a filesystem path. F15 — §8.4's *"user policy that explicitly permits it"* has no producer, so
*"with none present, every protected file is refused."* F10 — `66` §8 puts the undo period inside
a filing policy, which is item 5 of §22's order, *after* P12, so *"P12 therefore owns a
corpus-wide retention setting that a later per-policy setting will have to reconcile with."*

### 9.2.2 P13 review/approval surface — 20 tasks

**What it would build:** twenty-four modules under `src/review_surface/`, and explicitly *not* a
GUI. *"There is no framework, no HTML, no TUI, no template engine and no rendering loop anywhere
in this plan. Every 'renders' in the SPEC becomes 'is reachable as a field on a frozen dataclass,
and a negative test proves the forbidden thing is not reachable.'"*

**Review items.** Task 5 builds the placement review item (*"trust is not uniform, and a deferral
is not an abstention"*), Task 6 the group-plan item carrying `66` §4's five absence states, Task 7
the residual screen with seven attributes where *"a missing one is a failure"*, Task 11 the apply
item, the five staleness triggers and the undo-conflict item.

**The one `review_action` record.** The SPEC publishes it at `SPEC:246-280`: `action_id`,
`surface` (eleven values), `subject_ref`, `plan_version`, `session_id`, `action` (seventeen
values), `bulk_member_refs[]`, `bulk_basis`, `correction_scope`, `routed_to[]`,
`presented_state_ref`, `user_id`, `acted_at`. *"Routing is the whole contract"* — P13 collects the
gesture and hands it to the owning part; placement and residual to P11, tree edits to P10, consent
and redaction to P7, refresh and apply approval to P12, group changes to P9, a reclassification to
P7 and P6, a reset to P1. *"An action may route to more than one part; it is still **one**
collected gesture."*

**The progress line.** Task 15: completed and deferred never merged, and no indexed file absent
from every entry, assembled from `scan_agent.summary`, `evidence_shape.runs` and
`database_agent.budget.all_ceilings`.

**The review approval.** Task 12 builds `ReviewApproval(approval_id, plan_id,
placement_decision_ref, plan_version, required_review_policy, verdict, …)` — *"§8.3's gate,
finally consumed."* P12's side of that seam is deliberately hollow: P12's "not built" table says
*"A `review_approvals` table — P13 owns the producer. P12 publishes the typed record and reads
through an injected callable, so no source module impersonates P13."*

**The plan-version diff.** Task 18 consumes `tree_design.diff.diff_versions`,
`tree_design.user_edits` and `placement.versions.reproject`, and covers three of `66` §17's six
dimensions with the other three carried as `None` (see 9.1.3).

**P13 flags six conflicts plus ten still-open SPEC questions.** The sharpest is the one that
cannot be resolved without Joseph: **B3 forbids P13 a path and §8.3 demands four** (P13 PLAN:4550).
The Explicitly-not-owned table says P13 *"shows a **node and its ancestor labels**, never a
resolved path"*, but the apply item requires all thirteen §8.3 precondition fields, two of which
are paths, and the undo-conflict item requires *"the original source path, destination path,
expected content hash and observed content hash."* The plan's resolution: *"P13 CARRIES paths that
P12 composed and P13 COMPOSES none"* — and it adds *"Under the second reading, Done-means 13 is
unsatisfiable as written."*

Also unresolved and consequential: `evidence_shape.runs.COMPLETENESS` has **nine** members live
and the SPEC lists **eight** — `dataless` is missing — so *"a file whose only run is `dataless`
therefore has no bucket, which the SPEC's own rule that 'no indexed file may be absent from every
entry' forbids."* The plan gives `dataless` its own entry rather than folding it in.

---

## 9.3 Two conflicts that are about the repo as it stands — both verified here

`69` §3a separates the plans' flags into *"an authority with no producer yet"* (which stay in the
plans) and *"claims about the repo as it stands today."* There are two of the second kind. I
verified both by reading the files.

### 9.3.1 Three incompatible `review_action` fixtures already exist, and only one matches the SPEC

Three test-only files publish a class named `ReviewActionFixture`, each shaped by the part that
expects to *receive* the action. All three exist and are shipped:

| File | Identity field | Timestamp | How the subject is named | Actions |
|---|---|---|---|---|
| `tests/p9/p13_fixtures.py:35-60` | **none** — the record has no id of its own | `decided_at` (:56) | `group_id` + `membership_id` (:52-53) | 7: `accept, edit, reject, defer, restore, reset-suggestion, exclude-from-packet` (:18-26) |
| `tests/p10/p13_fixtures.py:13-24` | `review_action_id` (:15) | `observed_at` (:23) | `subject_ref` (:17) | 6, by function: `accept, rename, ignore, restore_version, add-scoped-general, set-shared-material-policy` |
| `tests/p11/p13_fixtures.py:32-46` | `action_id` (:34) | `acted_at` (:45) | `subject_ref` + `session_id` (:36, :38) | 11, in `ACTIONS` (:25-29) |
| **P13 SPEC:246-280** | `action_id` | `acted_at` | `subject_ref` | **17** |

**Only `tests/p11` matches.** Its own docstring states the provenance: *"The field list is P13
SPEC:247-279 restricted to the four surfaces P13 routes to P11 (P13 SPEC:294)."*

The other two carry field names and action values the SPEC's record cannot supply. `edit`,
`restore`, `reset-suggestion`, `exclude-from-packet`, `rename`, `ignore`, `add-scoped-general`
and `set-shared-material-policy` are not among the SPEC's seventeen actions; `review_action_id`,
`plan_version_id`, `group_id`, `membership_id`, `basis`, `user_edited_label`, `decided_at` and
`observed_at` are not among its fields.

Three further wrinkles, all verified:

- **They differ in strictness, not only in shape.** `tests/p9` validates its action against
  `REVIEW_ACTIONS` and requires seven fields non-empty (`__post_init__`, :62-71). `tests/p11`
  validates surface, action and six required fields (:48-56). `tests/p10` has **no
  `__post_init__` at all** — it validates nothing.
- **Two of the three have live consumers in `src/`.** P13's plan records that
  `tree_design.store.apply_review_action` reads `.action` against `TREE_EDIT_ACTIONS` (fifteen
  values, none of them in the SPEC's list) and `grouping` reads `.basis`, `.group_id` and
  `.membership_id`. So these are not idle fixtures; source modules are written against two of
  these three vocabularies.
- **All three declare themselves stand-ins and forbid `src/` from importing them**, and each says
  a test enforces that. `tests/p9`'s docstring: *"No source stub impersonates P13 — a stub in
  `src/` would be P9 deciding what a user action looks like, which is P13's to say."*
  `tests/p11`'s: *"`src/placement/` may never import this module and a test asserts it does not."*

P13's plan refuses to fix it: *"Reconciling the four vocabularies is a decision for Joseph, not for
a plan author. Do not widen P13's `ACTIONS` to absorb P10's or P9's; do not narrow P10's or P9's;
do not write a translation table."* Task 9 ships a compatibility **report** — a test that prints
every field and action value P13 cannot supply and fails with that list — rather than a shim. The
plan names the defect class: *"Three parts each guessed at a record its owner had not published…
here it has produced three producers and no consumer."*

One incidental finding: `tests/p11/p13_fixtures.py:4` cites `database_agent/events.py:59-61` for
P13's registered event names. Those line numbers are still correct at this commit — `"review
presentation"`, `"review action routed"`, `"apply review approval"` are at exactly 59–61 — but the
P13 PLAN:48 warns *"the line numbers have moved — do not propagate the citation."* Either the plan
was written against a different checkout or it is defensively wrong; either way the citation is a
fragile one and the plan is right about the risk.

### 9.3.2 §8.2's event vocabulary has `failed move` and nothing for a refusal

Verified at `src/database_agent/events.py:30-37`. `RESERVED_EVENT_TYPES` is a frozenset of
nineteen names taken verbatim from `00`'s provenance sentence
(`planning/00-database-agent-product-design.md:136`), which lists *"…placement recommendation,
filename-collision resolution, planned move, executed move, failed move, external modification
detection, and undo."*

The six P12 would author are all present: `planned move`, `executed move`, `failed move`,
`filename-collision resolution`, `external modification detection`, `undo`. **There is no name
for an action that was refused, or paused, before it was attempted.**

Registration cannot supply one at run time. `events.py:39-41`: *"Registration is a spec-level act
(rule 4), so this table is compiled from the declaring SPECs and frozen at import. There is no
run-time registration call."* An import-time check at :82-84 raises `ImportError` if a registered
name shadows a reserved one.

P12's Done-means 13 requires that *"Every applied, refused, stale, paused, and undone action
appended its §8.2 events"* — five result kinds against six event names that cover four of them.
P12's plan resolves it under protest at PLAN:4260: it appends **`failed move`** for a refused or
paused attempt, carries the exact result string in the structured explanation, and states plainly
*"**A refusal is not a failure and calling it one is wrong.**"* The durable, correctly-named record
is P12's own `execution_records` row; the event is the trace. The code it plans to write carries
the note inline (PLAN:5053): `"note": "not a failure -- §8.2 has no refused/paused type (F13)"`.

`69` §3a states the ownership: *"Adding an event type is Joseph's, not a part's."*

The distinction being lost here is one the project already enforces elsewhere. `69` §3 records
fixing exactly this class of error at the report layer — *"The refusal blamed the step that
worked. Every file said 'nothing has been able to read enough of it' when `file_facts` held a
`direct` fact and `classifications` held nothing. Read, not classified."* The same conflation is
about to be written into the permanent, append-only event log.

---

## 9.4 The stand-ins that exist because the real thing does not

`src/cli.py` is 1078 lines and is not part of P1–P11. It is a composition root, and four of its
components are stand-ins for parts that were never built. Each one says so.

**1. `review_and_accept` (`src/cli.py:429`) stands in for P13's review screen.** Its docstring:
*"The review screen, non-interactively: keep everything, as one named group."* It supplies two
things the engine cannot produce for itself and which are *"both the user's"*: a **name** (because
`grouping/pipeline.py` writes `display_label=None` on every group and `tree_design.upstream`
refuses an unlabelled group) and a **category** (because `group_category` is `None` and an
accepted group with no category *"is eligible for no applicability row at all"*). `--label` and
`--situation` are those two answers.

The cost is that it merges. Lines 452-470 build one `Group` whose `group_id` is
`f"{PLAN_VERSION}:{label}"`, whose `anchor_facts` are every group's facts concatenated, and whose
`coherence_verdict` is hardcoded `COHERENT`; every membership is then carried onto that one id.
P10 receives exactly one accepted group. This is `68` F3, below.

**2. `AcceptedGroupEnumeration` (`src/cli.py:246`) stands in for an enumeration P9 never
published.** Its docstring: *"Three of its four methods delegate straight to P9. The fourth,
`accepted(plan_version_id)`, has NO live P9 implementation: P9 publishes `group_state_as_of` for
ONE group and nothing that enumerates the groups a plan version accepted (`src/tree_design/
upstream.py` records this as SPEC corrections row 17). P10 deliberately does not work around it,
because 'an enumeration P10 wrote itself would be P10 deciding which groups a plan version
contains.' So it is written HERE, by the composition root that created the acceptances in the
first place."* It runs a raw `SELECT` against `group_acceptance` (:265-288) — the composition root
reaching into P9's table because P9 published no reader.

**3. `residual_partition` (`src/cli.py:700`) stands in for §7.5's review-set taxonomy.** Its
docstring: *"§7.5's review sets. SPEC Open question 10 leaves the taxonomy open, so this deployment
surfaces ONE set holding everything §6 could not place — the smallest partition that still shows
every file with a reason."* It returns a single dict labelled `"Not yet placed"` with hardcoded
`file_type_distribution: ()`, `age_range: ()`, `evidence_availability: "partial"`,
`sensitivity_status: "none"`, `protected: False`. Five of the seven attributes P13's Task 7
requires are stubbed constants here.

**4. `ask_or_abstain` (`src/cli.py:724`) stands in for the multi-home question.** It is
`lambda node_ids: pv.ABSTAIN`, with the reason stated inline: *"§6.9, when a file has two homes.
This deployment abstains rather than asking, because there is no screen here to ask on and
choosing one institution is the failure §6.9 exists to prevent."* `66` §10 names the same case as
one requiring its own refusal sentence — *"This file has two approved homes"* — and there is no
screen to say it on.

Two more, for completeness. `RESIDUAL_LIBRARY` is `{}` (`src/cli.py:222`) — §7.3's nine residual
template names are all disabled, because enabling one would mean inventing its eight attribute
slots. And `DIRECT_SLOTS` (`src/cli.py:206`) contains exactly one slot,
`cli.text.identifier → subject`, which is `68` F2's finding: a litigator's case number, a
household's claim number and a passport number all become the academic field `subject`.

---

## 9.5 The three blockers a real person hits

`planning/68-PERSONA-RERUN.md` ran the shipped command over four corpora on disk — a litigator, a
PhD student who TAs, a two-child household, and one person who is all three — and recorded the
output. Its §2 table: 26 files, four corpora, **1 folder proposed each, 0 files ready to file
each**. Its §5 verdict: *"G10 does not close, and it should not be recorded as closing."*

**Blocker 1 — no classifier ships, so every file for every person stops unclassified (F1).**
26 of 26 files returned the same sentence:

> *"This file has not been classified — nothing has yet said what kind of material it is — so it
> was not shown to a model and nothing moved. It is waiting for you to say what it is, not marked
> sensitive and not judged on thin evidence."*

The database confirms which step stopped: `file_facts` holds a `direct` fact for every file and
`classifications` holds **zero rows** in all four databases. Reading worked; classification
declined *correctly*, because no detector is supplied and P7 refuses to default an absent
classification to a public class. `68` frames the cost rather than the mechanism: *"it is not one
persona's problem or an edge case, it is the terminal state of the product for **everyone**, and
no other improvement is visible to a user until it is decided."* `69` assigns it: **Joseph**,
`65` §2.2's sizing question, open by decision.

**Blocker 2 — the review merge means the tree is one folder (F3).** Described in 9.4 above as a
mechanism; `68` calls it *"the largest user-visible defect and it is a **deployment** defect, not
an engine one."* The engine's own records are better than the report:

| | groups P9 formed | what the person was shown |
|---|---|---|
| Priya | `PHYS1401` (2 files), `PHYS2801` (2) | one folder, `Coursework` |
| Mara | `CV20261234` (4), `X12345678` (1) | one folder, `Matters` |
| Tom | `SPRING2026` (2), `CLM88213` (1), `PR20264410` (1) | one folder, `Household` |
| multi-life | `CV20261234`, `PHYS1401`, `PHYS2801`, `SPRING2026` | one folder, `Coursework` |

Verified by experiment, not argument: patching the review to accept each group as itself gave
Priya `PHYS1401` and `PHYS2801` as two folders. The patch was reverted, and `68` explains why it
is not a proposed fix — *"it also **drops the branch name the user asked for** (`Coursework`
disappears entirely) and it is not this command's place to decide whether a person's two courses
are two top-level folders or two children of one. That decision is a review screen, and the review
screen is **P13**."*

**Blocker 3 — a client's passport number became a group label and would become a folder name
(F4).** Mara's corpus produced a group whose `display_label` is **`X12345678`** — a passport number
printed in a client identity document. Under the shipped merge it stays in the database; under the
per-group experiment, the run printed a proposed folder named `X12345678`.

`68`: *"Two gaps compound to produce it: nothing classified the file as protected (F1), and nothing
anywhere says that an identifier lifted from an identity document may not name a folder."* It cites
`66` §4's governing sentence — that on a shared screen *"even 'Identity documents' may reveal more
than the user wants"* — and `66` §15, which prohibits person-shaped folders for clients and patients
on exactly this reasoning. Its instruction: *"This must be closed before anything materialises a
folder from a group label. It is upstream of P12 (which composes paths) and belongs in P13's review
contract (which is where a label is approved)."*

Two further findings are recorded as design work already owed rather than implementation gaps.
**F5**: no field names the child, so Tom's two report cards are one group — `66` §15's territory,
and *"No code should guess at it in the meantime, and none does."* **F6**: `--situation` is one
value per run, so Priya's teaching material is labelled `academic.coursework` — `66` §13's
structural-versus-contextual question in its sharpest form.

`68` also records a withdrawn finding rather than deleting it: F7's two review blocks were first
reported as two placement passes and are actually `00` §8.6's review-batch ceiling
(`residual.max_files_per_review_batch` = 8; 13 unplaced files → 8 + 5). *"A re-run that silently
drops a claim it made is not a record anyone can check."*

---

## What looks wrong here

Flagged, not resolved.

1. **The canonical user-facing design outranks eleven SPECs that eleven built parts were built
   from.** `69`'s authority order puts `66` above the part SPECs, and `66` is nine days newer.
   Nobody has audited P1–P11 *against* `66`. The two new PLANs each found `66`-versus-SPEC
   conflicts in their own part within days of `66` landing (P12's F9 and F10, P13's four
   `66`-binding tasks and its B3 path conflict). There is no reason to expect the eight parts
   nobody re-read are clean.

2. **`66` §3's six location states are a Find requirement whose only planned implementation is in
   P13.** `src/review_surface/locations.py` sits in a plan for the review surface, which §22's
   release order puts *second*, behind Find. If Find ships first as §22 requires, either it ships
   without the six states — the thing §21 says *"Without this model, Find will either hide genuine
   organizational context or present a confusing list of paths that users cannot interpret"* — or
   the ordering is wrong.

3. **Find has a release position and no scope.** `69` §4 item 4 is still asking *"What subset of
   P1–P11 does Find actually need?"* Step 1 of the release order has no answer to what it is built
   on, no SPEC, and no plan, while steps 4 and 5 have 17,199 lines of plan between them. The work
   that exists is the work the sequence says to do last.

4. **`66` §2 mandates reusing "the same local evidence and retrieval model," and the two modules
   named `retrieval.py` answer different questions from the one Find asks.** `grouping/retrieval`
   finds neighbouring files for a seed; `placement/retrieval` finds destination nodes for a file.
   Neither ranks files against a phrase. The prohibition on a second ranking system is clear; the
   claim that the first one is reusable for search is unexamined.

5. **P12's plan will write `failed move` for a refusal, into an append-only log, while stating
   that doing so is wrong.** The event log is the one artefact that cannot be corrected later. The
   plan is right that minting a name is Joseph's call, and right that the `execution_records` row
   carries the truth — but the §8.2 trace is what §8.2 exists to be, and it will be permanently
   miscategorised for every refused action until a nineteenth name is added and old rows cannot be
   rewritten.

6. **Three fixtures, two live consumers, no producer.** `tree_design.store.apply_review_action`
   and `grouping` are written against two vocabularies that the SPEC's `review_action` does not
   contain. When P13 ships the real record, those two source modules break — and the P13 plan
   forbids itself from writing the translation table. Who fixes P9's and P10's consumers, and in
   which plan, is unassigned. `tests/p10/p13_fixtures.py` also validates nothing at all
   (no `__post_init__`), so P10's guesses are the least constrained of the three.

7. **P12 will own a corpus-wide undo retention setting that `66` §8 says belongs to a filing
   policy** (F10). Building the narrower thing's setting on the wider thing's schedule, four
   release steps early, is a reconciliation debt taken on deliberately.

8. **`66` §17's diff is half-built, and the built half is the half nobody sees.** The storage
   exists and is tested; the presentation is P13's. A user who edits a structural answer today
   gets a durable record and no diff, no draft plan, and no adoption gesture — the exact
   *"silently"* §17 prohibits, minus the silent mutation, which is prevented only because nothing
   mutates anything.

9. **Three of §17's six diff dimensions have no producer and two of the three are blocked on the
   same missing record** — the filing policy, which is also what `66` §9's dry run, `66` §10's
   distinct refusals, and P13's activity list are all blocked on. One unbuilt record is load-bearing
   for four separate design promises across three sections.

10. **`68` F4's passport-number folder is assigned to "P13 + P12," both unbuilt and both scheduled
    late.** It is the only finding in `68` with a disclosure consequence rather than a usability
    one, and nothing in the release order brings it forward. Meanwhile the label is already written
    to the database on every run of the shipped command; only the merge is hiding it, and `68` §6
    notes the merge *"is now hiding four correct, distinct, populated groups"* — the hiding is an
    accident of a stand-in, not a control.

11. **The security invariant is currently satisfied by absence, not by design.** Protected material
    is never opened because *nothing opens anything*: the tree contains no write, no move, and no
    file-create. Every guard described in sections 1–8 will face its first real test on the day
    `src/mutation/` exists. `grep` proving the absence today proves nothing about that day.

12. **`68` §5's honest verdict and `69` §1's scoreboard sit uneasily together.** Nine of ten gates
    green, and the tenth is *"whether a person can use it"* — which is the whole product. A reader
    who scans the gate table sees 90%; a reader who reads `68` sees four people, four disks, zero
    files filed. The scoreboard's shape invites the first reading.
