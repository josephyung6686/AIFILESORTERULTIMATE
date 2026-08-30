# 77 — Everyday life: games, memes, fun, and the kid who uses this

Date: 2026-08-30
Status: **Research and proposal. No code, no test, no manifest and no vocabulary was
changed by this document.** It exists so that one decision — whether a closed vocabulary
gains a member — can be made by the owner with the evidence in front of him.
Reads: `planning/00-database-agent-product-design.md`, `planning/domains/`,
`planning/deferred-catalogues/`, `src/`, and one real CLI run over a real temp corpus.

---

## 1. What was asked

> "we also need to account for miscellaneous stuff like for example gaming stuff and like
> for fun stuff — idk if this is a domain we researched — like for example if this guy
> makes memes and stuff, or random bullshit, or it's a kid who uses it"

The question behind it is the north star's last clause. The user is one multi-role human:
a student and an employee and a litigant and a householder — **and a person with a life
outside institutions**. A product that files a lease, a transcript and a payslip
immaculately and has nothing to say about screenshots, memes, game saves, mods, fan
fiction, a kid's Minecraft worlds and downloads with meaningless names has failed the
person even though every test passes. This document establishes whether that has
happened, and if so where.

**The short answer, stated up front so the rest can be checked against it:** it was
researched, thoroughly, and the design deliberately decided that this material is *not*
a domain — it is what the residual library exists for, and `00` names "Memes" by name as
an example of it. That decision looks right. The failure is not the decision. The failure
is that **the residual library ships empty and its review workflow is called by nothing a
person can run**, so the design's own answer to this question has never once executed
outside a test. It is a missing route, in three places, and not a missing domain.

---

## 2. What ships today

### 2.1 The closed schema vocabulary — 23, and none of them is recreation

`src/facts/domains.py:59` — `SCHEMA_IDS`, the twenty-three schemas the product
recognises, and a schema outside them raises `UnknownSchema`:

```
academic, college_applications, research, career, photos, code,
finance, identity, medical, legal,
business_operations, clinical_practice, construction_property, creative,
engineering, government, hr, law_practice, logistics, manufacturing,
nonprofit, resource_operations, retail_hospitality
```

There is no `recreation`, no `hobby`, no `games`, no `personal_household` and no
`family`. `src/recognition/library/recognition.json` carries exactly the same
twenty-three keys.

### 2.2 The situations a person can actually name — 208

`database-agent --list-situations` prints 208 names, derived from the 208 applicability
rows in `src/tree_design/library/` (`applicabilities.json` plus the four `wave2_*.json`
files), which sit on **63** shipped template definitions. The roster
(`planning/domains/roster.json`, 358 rows) holds 335 template rows, so roughly 38 % of
the researched roster is reachable from the command line.

Of the 208, the ones a person with a life outside institutions might reach for:

| Situation | What it actually is |
|---|---|
| `photos.screenshot-captures` | screenshots — a real home, and the closest thing that ships |
| `photos.family-archive`, `photos.home-video`, `photos.social-media-export` | family and social media material |
| `creative.game-art-asset` | **professional** game art authored for an engine, sitting in a repository (`planning/domains/10-creative-media-design.md:1925`). Not a save file, not a mod, not a screenshot of a raid |
| `creative.short-form-writing`, `creative.book-manuscript` | writing — a fan-fiction draft is expressible here, though the row is written for professional practice |
| `code.pkm-vault`, `code.dotfiles-environment` | a notes vault, a dotfiles repo |
| `academic.k12-schooling`, `academic.homeschool`, `academic.iep-accommodation-plans`, `applications.k12-admission` | the four rows that touch a child |

Nothing else. No leisure, no hobby, no collection, no game library, no fandom.

### 2.3 It was researched — in detail, and then deliberately refused

This is the finding that decides the question, and it is not a gap in the research.

`planning/domains/04-personal-household.md` researched the everyday-life world in full,
with fields, detection signals, never-alone rules and neighbour separations:
`pers.hobby-collection` (:1237 — "Hobbies and collections", with a `pursuit` field and a
recorded sensitivity of `none`), `pers.creative-project`, `pers.recipe-meal`,
`pers.journal`, `pers.pet`, `pers.music-practice`, `pers.fitness-activity`.
`planning/domains/10-creative-media-design.md:1925` researched `game.art-asset` in full.

`planning/domains/ROSTER.md` then triaged all 574 legacy ids and ruled on them. §4's
arithmetic table at :149:

> | Dropped — **no honest schema**, residual library | **8** | genealogy, pets, recipes,
> hobbies, journals, gift occasions, personal faith life: ROSTER §5.6's refusal,
> unchanged by J-IND |

and §5.6 at :224, verbatim:

> Pets/veterinary as an owner's record, religion/faith life as personal practice,
> **hobbies and collections**, genealogy documents, journals, recipes, gift occasions —
> still no honest schema; **their isolated files are what the residual library exists
> for** (Independent Records, Reference Clips, One-Off Images).

The per-id table confirms it row by row (ROSTER.md:494–503):
`pers.hobby-collection` → `DROP·residual`, `pers.journal` → `DROP·residual`,
`pers.recipe-meal` → `DROP·residual`, `pers.pet` → `DROP·residual`;
`pers.music-practice` → row `creative.performing-practice`;
`pers.creative-project` → row `creative.self-initiated-work`;
`game.art-asset` and `soft.game-development-asset` → row `creative.game-art-asset`
("game assets are a creative production", :690).

So the research answer is explicit: **recreation is residual material, by design.**

Two footnotes that matter:

* **The two rows that were kept did not ship.** `creative.performing-practice` ("A
  performer's own practice archive") and `creative.self-initiated-work` ("Self-initiated
  professional creative practice") are `placeholder` rows in `roster.json` and are **not**
  among the 28 `ap.creative.*` applicabilities in `src/`. The two roster rows that carry a
  person's *own* creative practice — as opposed to a client's — are precisely the two the
  shipped library does not have. That is not a vocabulary decision; it is where the
  wave-2 build stopped.
* **`00` names this material once, and it is not as a domain.** `00`:120, the residual
  library section, verbatim: *"the library must support user-defined residual areas such
  as Things to Read, Ideas, Shopping Research, **Memes**, Travel, Receipts to Process,
  Clips, or Stuff to Sort, because residual organization is highly personal and should not
  be dictated by a universal taxonomy."* Across all 286 lines of `00`, the words
  *gaming*, *game*, *hobby*, *leisure*, *recreation* and *entertainment* appear **zero**
  times. "Memes" appears once, at :120, as a user-defined residual area. The design's
  answer to "this guy makes memes" is: *the person names their own Memes folder, and the
  product does not invent one for them.*

### 2.4 The residual answer is fully researched and fully built — and shipped empty

`planning/deferred-catalogues/09-residual-library/` holds `01-nine-templates.json` — all
nine of `00` §7.3's names with all eight slots filled and every value provenance-tagged —
and `02-user-defined-shape.json`, the form a user-authored area fills.
`planning/deferred-catalogues/_RESUME.md:3` states: **"STATUS: COMPLETE."**

`src/tree_design/residuals.py:85` `build_library(slot_values, *, user_defined=())` builds
the nine from injected slot values and accepts user-defined areas alongside them (:127).
`src/placement/residual.py` implements §7.5's surfacing (:133), §7.6's set decision
(:213, :244) and §7.7's eight-action gate. `src/review_surface/` (P13) implements the
review surface. `tests/p11/test_p11_residual_sets.py`: 28 passed.

And then, `src/cli.py:396–401`:

```python
#: §7.3 fixes nine residual template names and leaves their eight attribute slots
#: deferred. This deployment enables NONE rather than inventing slot values: an
#: unplaced file still reaches §7.5's review set with its reason, so it is counted
#: and explained -- which is the property that matters -- and it does so without a
#: folder nobody designed.
RESIDUAL_LIBRARY: dict = {}
```

with `residual_choices=()` at `src/cli.py:1193`. The comment is honest about what it
does and, in 2026-08, was the right call: the slot values did not exist in `src/`. They
exist now, on disk, complete, in a directory `src/` reads never (`grep -rn
"deferred-catalogues" src` → nothing).

### 2.5 Three routes that exist and are called by nothing a person runs

| What | Where it is built | Who calls it |
|---|---|---|
| §7.5 residual **surfacing** | `src/placement/residual.py:133` | `run_corpus` (`src/placement/pipeline.py:1434`) → `src/production.py:627` → CLI. **Reachable.** |
| §7.6/§7.7 residual **review and placement** | `src/placement/pipeline.py:1445` `review_residual_sets` | `tests/p11/*` only. **Unreachable from any command.** |
| P13 **review surface** | `src/review_surface/` (11 modules) | no module in `src/` outside `src/review_surface/` imports it. **Unreachable.** |
| The residual **library** | `src/tree_design/residuals.py:85` | `src/cli.py:1193` passes `{}` and `()`. **Enabled with zero members.** |
| The evidence that identifies a screenshot | `planning/deferred-catalogues/01…04` (complete) | nothing. `src/cli.py:393` ships `MetadataScreen(tool_producer_strings=(), metadata_property_names=())`. **Unread.** |

---

## 3. What the product actually does with such a corpus today

A 14-file temp corpus was built and the real CLI (`python3 -m cli`, `src/cli.py:main`)
was run over it twice. The corpus:

```
Memes/drake-format-when-the-code-compiles.jpg
Memes/distracted-boyfriend-2026.png
Screenshots/Screenshot 2026-08-14 at 11.03.47.png
Screenshots/Screenshot 2026-08-21 at 09.12.02.png
Games/.minecraft/saves/SkyBlockWorld/level.dat
Games/.minecraft/saves/SkyBlockWorld/r.0.0.mca
Games/Mods/JEI-1.20.1-forge-15.2.0.27.jar
Games/Mods/skyrim-enb-pack-v3.zip
Writing/chapter-3-draft.md          (fan-fiction draft, real prose)
Writing/dnd-campaign-notes.txt      (real prose)
Downloads/dQw4w9WgXcQ.mp4
Downloads/file (3).pdf
Downloads/IMG_20260812_223311.jpg
Downloads/tmp_8f2a91.bin
```

### 3.1 Run one — `--situation photos.screenshot-captures --label "Fun stuff"`

The situation deliberately chosen as the most sympathetic one that ships.

```
Protected containers: 0 marked, none opened

Folders in this plan: 9. 0 proposed, 9 yours already. 9 of them are somewhere a file can go.
  Downloads   [yours already]
  Games   [yours already]
    .minecraft   [yours already]
      saves   [yours already]
        SkyBlockWorld   [yours already]
    Mods   [yours already]
  Memes   [yours already]
  Screenshots   [yours already]
  Writing   [yours already]

Files: 14 decided, 0 ready to file

  Waiting for you to say what these are -- 1 file
    Writing/chapter-3-draft.md
    Same reason for each: Deciding this file needed a model, and §8.4 did not
    clear this file for a model call. Nothing about it left this device and
    nothing moved; the evidence is retained.
    Held for review as "Not yet placed (2 of 2)": no destination in this tree
    matched them well enough to decide without asking you.

  Waiting for you to say what these are -- 8 files
    Downloads/IMG_20260812_223311.jpg
    Downloads/dQw4w9WgXcQ.mp4
    Downloads/file (3).pdf
    Downloads/tmp_8f2a91.bin
    Memes/distracted-boyfriend-2026.png
    Memes/drake-format-when-the-code-compiles.jpg
    Screenshots/Screenshot 2026-08-14 at 11.03.47.png
    Screenshots/Screenshot 2026-08-21 at 09.12.02.png
    Same reason for each: This file has not been classified -- nothing has yet
    said what kind of material it is -- so it was not shown to a model and
    nothing moved. It is waiting for you to say what it is, not marked
    sensitive and not judged on thin evidence.
    Held for review as "Not yet placed (1 of 2)": no destination in this tree
    matched them well enough to decide without asking you.

  Waiting for you to say what these are -- 5 files
    Games/.minecraft/saves/SkyBlockWorld/level.dat
    Games/.minecraft/saves/SkyBlockWorld/r.0.0.mca
    Games/Mods/JEI-1.20.1-forge-15.2.0.27.jar
    Games/Mods/skyrim-enb-pack-v3.zip
    Writing/dnd-campaign-notes.txt
    Same reason for each: This file has not been classified -- nothing has yet
    said what kind of material it is -- so it was not shown to a model and
    nothing moved. It is waiting for you to say what it is, not marked
    sensitive and not judged on thin evidence.
    Held for review as "Not yet placed (2 of 2)": no destination in this tree
    matched them well enough to decide without asking you.

Nothing was moved.
```

### 3.2 Run two — `--situation creative.game-art-asset --label "Games"`

Byte-identical file outcomes. `--situation` selects the tree template; it does not
change what recognition can see. The situation that has the word *game* in it does not
help a game file.

### 3.3 What that means, stated plainly

* **Nothing crashed and nothing was refused.** The run completes, exit 0, and every one
  of the 14 files is named on screen with a reason. The standing rule holds: nothing was
  moved, nothing was opened, nothing was silently omitted.
* **13 of 14 files were never classified at all** — not "classified and abstained", but
  *"nothing has yet said what kind of material it is"*. No schema's recognition row
  fired.
* **The two screenshots were not recognised as screenshots**, under the situation named
  `photos.screenshot-captures`. The `photos` schema's recognition row carries five
  context terms (`form field label wording`, `page n of m running head`, `scanned`, `seal
  or stamp caption`, `signature block wording`) and `file_kind_never_alone: true`. Nothing
  in the shipped manifest looks at a filename shaped like `Screenshot 2026-08-14 at
  11.03.47.png`. The catalogue that does — `planning/deferred-catalogues/04-camera-filename-patterns.json`,
  which carries `fnp-macos-screenshot`, `fnp-macos-screenshot-legacy`,
  `fnp-macos-screen-recording`, `fnp-windows-screenshot-numbered`, `fnp-windows-snipping`,
  `fnp-android-screenshot`, `fnp-cleanshot` — is complete on disk and read by nothing.
* **"Held for review" leads nowhere.** The label is real; the folder behind it does not
  exist (`RESIDUAL_LIBRARY = {}`), and the workflow that would act on the set
  (`review_residual_sets`) is called only by tests. A person who reads that line and asks
  "fine — how do I review it?" has no next command.
* **The review sets are one undifferentiated pile.** `src/cli.py:1328` surfaces a single
  set, "Not yet placed" (split into `(1 of 2)`/`(2 of 2)` only by a batch ceiling), and
  says so: *"SPEC Open question 10 leaves the taxonomy open, so this deployment surfaces
  ONE set."* `00`:122 asks for the opposite — *"58 screenshots with no accepted project or
  event," "21 standalone PDFs and forms," "17 receipts, tickets, and confirmations"* —
  because *"a single intimidating pile"* is the thing it is trying to avoid.

### 3.4 The control — this is not a general failure of the CLI

A two-file academic corpus (`syllabus.txt`, `problem-set-3.txt`, both full of
`academic` context terms) run as `--situation academic.coursework`:

```
Files: 2 decided, 0 ready to file

  Waiting for you to say what these are -- 2 files
    Fall 2026/BUSIB 4300/problem-set-3.txt
    Fall 2026/BUSIB 4300/syllabus.txt
    Same reason for each: Deciding this file needed a model, and §8.4 did not
    clear this file for a model call.
```

Also 0 placed — but for a **different reason**, and the difference is the whole point.
The coursework files were *recognised* and stopped at a model call this deployment has
not configured. The memes, screenshots, saves and mods were never recognised at all. One
is a wiring gap already on the ledger; the other is this document's subject.

---

## 4. Missing domain, missing route, or both?

**Missing route. In three places. Not a missing domain.**

The evidence that decides it:

1. **`00` already answers the question, and the answer is not a domain.** :118–129 create
   the residual system precisely for *"a screenshot of a boarding gate, a saved product
   image, a one-off receipt, an unconnected PDF form, a spreadsheet with unclear purpose,
   an article saved to read later, a private document with no project association"* —
   and :120 names **Memes** as a user-defined residual area. Minting a `recreation`
   schema would be inventing a domain `00` declined to name, which is the one thing `00`
   forbids most explicitly (:97, *"without prematurely hand-authoring hundreds of
   specialized schemas"*).
2. **The roster already ruled, with reasons, on exactly these ids.** ROSTER.md §5.6:
   hobbies and collections have *"no honest schema"* — no field set could be authored
   that a real file would fill — *"their isolated files are what the residual library
   exists for."* That ruling is recorded, cited and not re-opened here.
3. **The right behaviour for a `.minecraft` folder is not organisation.** Nobody wants
   their save directory restructured into `Games/Minecraft/2026/SkyBlockWorld/`. The
   right answer is `00`'s own residual treatment slot: *"whether the file should be
   reviewed, retained, or merely kept searchable."* **Kept searchable, left in place.**
   That is a residual treatment, and no schema can express it because a schema's job is
   to propose a hierarchy.
4. **The parts that would deliver the design's answer are complete and unreachable.**
   §2.4 and §2.5 above. This is the codebase's dominant defect class, in its purest form:
   the answer is researched (`09-residual-library`, COMPLETE), built
   (`src/tree_design/residuals.py`, `src/placement/residual.py`, `src/review_surface/`),
   tested (28 passing), and passed `{}` by the only file a person runs.

The honest qualifier: **routing to residual alone will not fully serve the person
either**, and the owner should know why before deciding. The nine residual names are
storage-shaped — Temporary Screenshots, One-Off Images, Reference Clips, Independent
Records, Receipts and Confirmations, Reading Inbox, Review Later, Unsupported or
Encrypted, Protected Records. None of them says *"this is your game stuff"* or *"this is
your writing"*. `00`'s deliberate answer to that is the **user-defined** area, which
`src/tree_design/residuals.py:127` already implements and which ships zero members by
design (`02-user-defined-shape.json`: *"This file ships ZERO user-defined templates — it
is a form, not a library"*). Whether a person will actually author one, unprompted, on a
command line, is a product question and not a vocabulary question — see §6.

---

## 5. Does a vocabulary member need minting?

**On the evidence: no. Nothing in this document asks the owner to approve a new schema
id, and nothing here has been done that would need one.** This section exists to state
that finding precisely, and to name the one thing that would change it.

### 5.1 Why no new member

* **The schema vocabulary needs nothing.** A `recreation` / `games` / `hobby` schema
  would have to be minted from a design sentence that does not exist, over a roster
  ruling that explicitly refused it, to express a hierarchy the material does not want.
* **The residual vocabulary needs nothing.** `00` §7.3 fixes the nine names; they are
  already in `src` (`RESIDUAL_TEMPLATE_NAMES`, `src/tree_design/residuals.py:96`). What is
  missing is their **slot values**, which are authored content, not vocabulary — and they
  are already authored, at `planning/deferred-catalogues/09-residual-library/01-nine-templates.json`.
* **A user-defined area needs nothing either.** It is a *shape*, already specified and
  already implemented, whose members are supplied by the person at runtime and marked
  `user_defined=True` so a shipped name and an authored one can never be confused.

Enabling the residual library is therefore a **wiring and deployment-authoring decision,
not a vocabulary decision** — it needs the owner's approval as a change to what the
product does, but it does not need the "record the ruling at the member" ceremony.

### 5.2 The one thing that would change this

If the owner looks at run one and decides that **a person's own creative and recreational
practice deserves a proposable branch and not a residual home** — that a fan-fiction
draft, a D&D campaign folder or a modding project should get a real tree — then the
member to add is **not new**. It already exists, twice, in the roster, and would only
need to *ship*:

| Existing roster row | Exact spelling | Schema | Terms it would carry | Where it is recorded |
|---|---|---|---|---|
| A performer's own practice archive | `creative.performing-practice` | `creative` | inherits `creative`'s field scope; roster row is `launch: placeholder`, `provenance: proposal` | `planning/domains/roster.json` (node `creative.performing-practice`) |
| Self-initiated professional creative practice | `creative.self-initiated-work` | `creative` | same | `planning/domains/roster.json` (node `creative.self-initiated-work`) |

Shipping either means writing an `ap.creative.<name>` applicability row into
`src/tree_design/library/`, pointing it at an existing definition, and giving it a
recognition signal. **No `SCHEMA_IDS` change. No new canonical field. No new residual
name.** The closed vocabularies are untouched either way; this is the wave-2 build
finishing two of the thirteen `creative` rows it left behind.

### 5.3 What it costs if the owner declines each of these

The owner may decline any of the following independently. The cost of each, stated
honestly:

| If the owner declines… | What stays true |
|---|---|
| **Enabling the nine residual templates** | Everyday material keeps landing in "Not yet placed" with an accurate reason and no destination. Nothing is lost, nothing is wrong, and nothing is *done*. The person is told correctly that the product does not know what their memes are, forever. `00` §7's entire second half stays a research artifact. |
| **Wiring `review_residual_sets` / P13** | Even with the library enabled, there is no command that lets a person answer "review these 58 screenshots" — §7.6's set decision, the one control the design gives the person over residual spend, cannot be exercised. The library would be enabled and still unusable. |
| **Wiring deferred catalogues 01–04** | A macOS screenshot is never recognised as a screenshot on any path. `photos.screenshot-captures` remains a situation a person can name but no file can reach. The residual sets stay one pile because the facts that would split them are not extracted. |
| **Shipping `creative.performing-practice` / `creative.self-initiated-work`** | A person's own creative work has no proposable branch; it is either a client engagement it isn't, or residual. Given §4's point 3, this is a defensible place to stop — it is the least urgent of the four. |
| **All of them** | The product remains excellent at institutional material and silent about the rest of a real disk. It will be honest about that silence, which is worth something — but the north star's last clause is unmet, and this document will read the same in six months. |

**Ranked, if the owner wants one sentence of judgement:** enable the residual library
first (it converts "I don't know" into "here is where I'd put it, is that right?"), wire
§7.6's set decision second (it is what makes the first one usable), catalogues 01–04
third (it is what makes the sets legible), and the two `creative` rows last or never.

---

## 6. The kid case, specifically

A child using this is not a smaller adult, and the design treats the two unevenly.

**What is already covered, and covered well.** Four of the 208 situations concern a child:
`academic.k12-schooling` (`def.household-school-record` — school → school year → report
card / permission slip / enrolment form), `academic.homeschool`
(`def.subject-work-record.household`), `applications.k12-admission`
(`def.addressee-packet.household` — *"A parent says 'the Dalton application'"*), and
`academic.iep-accommodation-plans`. The last one is the strongest piece of child-specific
design in the product: `def.protected-plan-record` carries
`sensitivity_policy_ref: sp.household-member-record@1` and this validation constraint,
verbatim from `src/tree_design/library/definitions.json`:

> `artifact_kind` is not a role of this definition and is recorded as an exclusion on the
> applicability row: its values (iep, 504 plan, eligibility determination, evaluation
> report) would publish a named child's disability determination as a visible folder
> label, in a namespace Finder, Spotlight, backup tools and sync clients all read

That is exactly the right instinct, and it is the one place in the codebase where a wrong
move about a child was anticipated and prevented.

**What is not covered.**

1. **Every one of those four is the *parent's* record about the child.** The role is
   `holder_institution` = the school, the household is the filer. There is nothing in the
   product for a child as the **operator** — the person at the keyboard whose disk is
   mostly game saves, Roblox screenshots, half-finished Scratch projects and Discord
   downloads. Run one is that disk, and it produced 14 files and zero answers.
2. **`00` never mentions a child, a minor, a guardian or an age.** `grep -oniE
   "guardian|children|minor|kid|coppa|under 13"` over all 286 lines of
   `planning/00-database-agent-product-design.md` returns exactly one hit — "children" at
   :104 — and it means *child branches of a folder*. Every occurrence of "child" in `00`
   is the tree sense (`parent and child meanings`, `one-child levels`). There is no design
   sentence about who is allowed to use this, no consent model for a household member, and
   no rule about a second person's material appearing on one person's disk.
3. **`privacy_floor` is `None` on all 208 applicability rows** — including
   `ap.academic.iep-plans`. The IEP protection above is carried entirely by the
   *template's* sensitivity policy, not by the situation row. That is one mechanism deep
   rather than two, on the single most sensitive thing about a child in the whole
   catalogue.
4. **The material differs and the risk of a wrong move differs.** `00`:177's ten
   sensitivity categories (*"identity documents, account statements, tax records, medical
   information, legal records, credentials, private correspondence, GPS metadata,
   employment materials, and educational records"*) were written for an adult's disk. A
   child's screenshots of a group chat are private correspondence about third-party
   minors; the residual library's `Temporary Screenshots` treatment does not know that.

**None of this is a vocabulary question either.** It is a design question `00` did not
ask, and it is the one place in this document where I would put a question to the owner
rather than a recommendation.

---

## 7. Open questions — only the owner can answer these

1. **Enable the nine?** `planning/deferred-catalogues/09-residual-library/01-nine-templates.json`
   is complete and passing its own checks. Does it move into `src/` as this deployment's
   `RESIDUAL_LIBRARY`, or does it stay research? This is the single decision that decides
   whether run one's 14 files ever get an answer. (Note: it changes what the product
   *proposes*, so it is genuinely the owner's call, not a wiring detail.)
2. **Who authors a user-defined residual area, and when?** `00` puts "Memes" in the
   person's hands. On a command-line product with no canvas, is a person ever going to
   type one — and if not, is the honest move to (a) ask them during tree design, (b) offer
   the eight names `00` lists as *suggestions* explicitly marked as the person's to accept
   or ignore, or (c) accept that the nine shipped names are all a CLI user will ever get?
   Option (b) is the one that risks becoming "the product dictated a taxonomy", which
   :120 explicitly forbids.
3. **Does §7.6's set decision get a CLI verb?** `review_residual_sets` needs a person to
   answer "leave in place / review with a model / send to an approved node / create a
   custom branch" per set. That is a new interaction shape for a command that currently
   only takes `--answer QUESTION=OPTION`. Does it fold into `--answer`, or is it its own
   flag?
4. **Do catalogues 01–04 get wired, and by whom?** They are complete, they carry their own
   verification tags, and they are the difference between one pile and `00`:122's seven
   legible review sets. They also touch P5/P6, not P10/P11, so this is a different piece
   of work from questions 1–3.
5. **The two `creative` rows.** Ship `creative.performing-practice` and
   `creative.self-initiated-work`, or leave a person's own creative practice to residual?
   §5.3 ranks this last; the owner may disagree, and a person who writes fan fiction every
   day would.
6. **The kid.** Is a child at the keyboard in scope at all? If yes, it needs a design
   sentence `00` does not have, and that sentence is the owner's to write — not a schema.
   If no, that should be recorded as a scope refusal in the same place the other refusals
   live (ROSTER.md §5), so the next person finds the decision instead of the gap.

---

## 8. What was verified, and what was not

**Verified.** The 23 schema ids, the 208 situations, the 63 definitions and the absence of
any recreation-shaped row among them were read from `src/` directly. The two CLI runs and
the control run are real invocations of `src/cli.py:main` over real temp directories; the
output in §3 is pasted, not paraphrased. `tests/p11/test_p11_residual_sets.py` was run in a single
process: 28 passed. (`tests/p11/test_p11_residual_actions.py` reports errors when its
whole file is collected at once and passes when a test is selected individually — a
harness/concurrency artifact, not a finding about the residual code, and not investigated
here because it is outside this document's question.) The reachability claims in §2.5 were established by grep over `src/` and
`tests/`. Every `00` and ROSTER quotation was grepped verbatim before being written here.

**Not verified.** Whether the nine templates' slot values would pass
`build_library`'s validation unchanged if moved into `src/` (the shapes look compatible;
nothing was executed). Whether wiring catalogues 01–04 would actually classify the two
screenshots (the catalogue has the pattern; the consumer path was not traced end to end).
The behaviour of a corpus containing a genuinely protected container — run one reported
`0 marked, none opened`, which is correct for this corpus but exercises nothing.

**Changed by this document: nothing but this document.**
