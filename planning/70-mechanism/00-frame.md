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
