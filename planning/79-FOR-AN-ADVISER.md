# 79 — For an adviser: the product, the person it is for, and one open decision

Date: 2026-08-31
Status: **Briefing document, written to be handed to somebody outside the project.**
It changes no code, no test, no manifest and no vocabulary.

This document assumes you have never seen this codebase, this design, or this team. It gives
you three things in order — **how the product is built**, **who it is for**, and **the one
decision that is open** — because the decision cannot be judged without the first two.

The short version of the ask: *a person types one sentence about who they are, and something has
to turn that sentence into a filing structure. We need to decide what that something should be,
and in particular whether a language model is allowed anywhere in that step.*

---

## Part one — the structure

### 1.1 What the product is

It is a local command-line tool. You point it at a folder. It reads every file in it, works out
what the files are, proposes a folder tree, and tells you which file would go where.

**It moves nothing.** Every run ends with the line `Nothing was moved.` The apply-and-undo
machinery exists but is not yet reachable from anything a person types. Today the product's
entire output is a *proposal*, on screen, that the person can accept, overrule, or ignore.

Two architectural commitments shape everything else, and both are stated in the first two
paragraphs of the canonical design:

> *"The filesystem is the system of record. Every file continues to live as a normal file in a
> normal directory that Finder, Spotlight, Dropbox, Time Machine, shell tools, and other
> applications can understand. The database agent does not own the namespace, create a virtual
> filesystem, or require a proprietary storage format. It can be rebuilt from the filesystem if
> necessary."*

> *"A local SQLite database acts as the durable working memory of the product."*

So: no lock-in, no proprietary store, nothing the user cannot inspect with ordinary tools, and a
local database that is a cache of reasoning rather than a home for the files themselves.

### 1.2 How it is built — thirteen parts

The system is divided into thirteen parts, each with its own written specification, its own
tables in the shared database, and its own test suite. They form a pipeline:

| | part | what it does |
|---|---|---|
| P1 | storage, identity, provenance | file identity, content hashes, what is known about each file version |
| P2 | evaluation and replay | reconstruct any past run exactly, from a bundle, with no live database |
| P3 | scan and corpus selection | which folders participate; what is excluded and never touched |
| P4 | evidence shape | *where* a piece of evidence appeared — page, heading, filename, offset |
| P5 | extractors | read PDFs, DOCX, text, images; never decide meaning |
| P6 | facts and facets | turn evidence into facts (a course code, a term, an organisation) |
| P7 | privacy and consent gate | the one gate anything must pass to reach a model |
| P8 | model harness and validator | if a model is used at all, it is used here, bounded and audited |
| P9 | grouping | which files belong together |
| P10 | tree design and freeze | propose the folder tree; freeze it as a plan version |
| P11 | placement and residual | which file goes where; and what to do with files that fit nowhere |
| P12 | apply and undo | actually move files; reverse it |
| P13 | review and approval surface | everything the person sees and every gesture they make |

A fourteenth capability — local search, so a person can *find* a file having granted no
authority at all — is designed but deliberately unbuilt.

There is also a fifteenth workstream, the **questions and onboarding system**, which is where
the open decision lives. It is the machinery by which the product asks a person something and
remembers the answer.

### 1.3 The one rule that explains most of the design

**Absent means refuse, never guess.**

A single file, `src/cli.py`, is the only place in the entire system permitted to choose a number
or a policy. No part package may contain a numeric literal other than 0 or 1. If a threshold has
not been supplied, the code does not fall back to a sensible default — it refuses the run and
says what it needed.

This is unusual and it is deliberate. It means every judgement the product makes is traceable to
a decision somebody made on purpose, rather than to a default nobody remembers choosing.

### 1.4 What the product will and will not say

The design forbids the product from claiming more than it knows. Concretely:

- A file it cannot classify is reported as **unclassified**, not filed on a guess.
- Files it cannot place are surfaced in a **review set** with the reason they could not be placed
  — counted and named, never quietly dropped.
- Material judged sensitive is **marked and counted, never opened, and never silently omitted**.
  A protected file is named on screen; its contents are not read, indexed, classified or moved.
- Where the product had to decide something without asking, it prints a section headed
  *"Decisions made for you, because nobody was at the screen to ask."*

### 1.5 Where a model fits, and where it does not

The product is **not** an LLM wrapper. The great majority of what it does is rules, extraction
and structure. A model, where one is used, is confined to P8 and may only propose facts that
belong to the categories already active for that run.

**As shipped today, no model is wired at all.** Every model path exists, is tested, and is passed
`None`. A file that would need a model to decide is reported as *"Deciding this file needed a
model, and this deployment did not clear this file for a model call."*

This matters for the decision below: introducing a model into the onboarding step would not be
adding a feature to an AI product. It would be the first live model call in a product that has so
far done everything without one.

---

## Part two — the person it is for

### 2.1 The north star, stated

The project's standing instruction, quoted exactly:

> **North star.** Judge every decision by what a real, multi-role human would want. Not the
> lawyer OR the parent OR the researcher — the person who is several of those at once, whose
> research paper is also school homework, whose legal document is part of an application.

Every design argument in this project is settled against that sentence. It is the reason the
product is hard: filing software normally assumes one role per user, and this one may not.

### 2.2 Why that makes the problem difficult

Most filing tools work because they can assume a context. A photo manager assumes photos. A legal
document system assumes matters. A reference manager assumes papers.

This product has to work on a single laptop that contains, simultaneously:

- coursework for a degree the person is taking
- teaching material for a course the same person is *giving*
- a lease, an insurance claim, and two children's report cards
- a legal matter in which they are a party rather than a professional
- and a large volume of material that belongs to no institution at all — screenshots, memes,
  game saves, downloads with meaningless names, a novel draft

The last category is not an afterthought. It is most of a real disk, and the design has a
specific answer for it: those files go to *residual areas* — deliberately broad, shallow homes
the person enables by name — rather than being forced into a category that does not fit.

### 2.3 The four people the product is tested against

These are not hypothetical. Each is a real folder of files on disk, and the shipped command is
run over all four, with the output recorded.

| who | what is in their corpus |
|---|---|
| **Mara**, a litigator | a motion, a deposition, a privilege log, an e-filing receipt, and a client's passport |
| **Priya**, a PhD student who also teaches | her own problem sets and notes for one course; the solution set and rubric she *wrote for her students* in another |
| **Tom**, a two-child household | two report cards, a lease, an insurance claim |
| **all three at once** | the union of the above — one person, three lives, thirteen files |

The fourth row is the north star made concrete, and it is the one that exposes the problem below.

### 2.4 The failure that motivates the decision

When the product was run over Priya's corpus, **her entire disk was filed as coursework** —
including the material that was teaching, which the product's own library has a separate and
better-fitting category for.

Nothing was broken. Every test passed. The failure was that the product had been told, by a
single word on the command line, that this person was a student — and she is also a teacher, and
nothing in the system could hold both facts at once.

That is the problem the open decision is about.

---

## Part three — the open decision

### 3.1 What is at stake, measured rather than asserted

The product carries 23 named categories and 208 named situations under them. Each builds a
different shape of folder. Three *identical* files — a syllabus, a homework sheet, lecture notes,
all naming the same course and term — were run three times, changing only the declared situation:

| declared as | the folder shape then offered |
|---|---|
| coursework | school › term › subject › kind of work |
| teaching | term › subject › kind of work |
| engineering drawings | design item › artifact type — *"would create no child branches"* |

Three conclusions, and they are the whole stake:

1. **A right answer and a nearly-right answer differ by a whole folder level.** Coursework has a
   *school* level; teaching does not. Priya's teaching material filed as coursework acquires a
   folder for a school she teaches at rather than attends. Quietly wrong, and wrong in a way she
   would only find by going looking.

2. **A wrong category does not produce a wrong tree. It produces no tree.** Under the engineering
   situation the product offered a shape that would create no folders at all, because those
   fields are not facts her files carry. Everything would sit in one undifferentiated pile. That
   is the safer failure, and it is still a failure.

3. **It has already happened**, to a real corpus, as described in §2.4.

### 3.2 The question

The design says the product should ask the person, in their own words — *tell us what you do* —
and should support several answers at once, because being more than one thing is normal.

**The open question is the single step in the middle: how does a sentence a person types about
themselves become the small set of categories the product then offers to turn on?**

The design's first answer was a *matcher*: map the free text onto the closed list, and record an
answer that matches nothing as unmatched rather than snapping it to the nearest neighbour. It is
categorical on one point:

> *"'I'm a sound engineer' must not silently activate an engineering or software-project schema
> merely because the words are superficially similar."*

The owner overturned that as a mechanism on 29 August 2026:

> *"These should not just be directly matched — the LLM uses that information to judge. This
> cannot be rule based and that simplified in this sense."*

and added that fuller guidance was owed and that nothing should be built until it arrived. It has
not yet been given. That is what this document is for.

**The two positions disagree about exactly one step and agree about everything either side of
it.** Both agree the person may hold several roles at once, each with a scope and possibly a time
period; both agree the raw wording is kept; both agree an answer matching nothing stays unmatched;
both agree a role must never become a folder name. The disagreement is only about how wording
becomes candidates.

### 3.3 Two harms that are already structurally impossible

Worth knowing so the discussion stays on what is genuinely at risk.

- **A person's self-description can never become a folder name.** In the code, a free-text answer
  selects no option from any list, and only a selected option reaches the machinery that builds
  folder labels. There is no path to write down. This is a property of the data model, not a
  policy somebody has to remember to apply.
- **Nothing moves.** A wrong answer costs a bad proposal, which is shown and can be overruled —
  not a lost file.

One caveat that belongs on the record: the general risk of a private value leaking into a folder
name is *not* hypothetical here. A different mechanism once turned a client's passport number
into a proposed folder label. That defect is elsewhere and is recorded as blocking. It matters
only as evidence that this class of leak is live in the product, so the exemption above should be
re-verified rather than assumed whenever this path is wired to anything new.

### 3.4 The five options

Each differs in exactly one step: what happens between the sentence and the shortlist.

**Option 1 — No model. The person picks from the product's own list.**
No wording-to-category step at all; the person does the mapping, visibly and reversibly.
Nothing sent, zero cost, errors are the person's own and visible to them.
*Weakness:* the 23 category names are internal vocabulary — `resource_operations`,
`retail_hospitality` — not words a person recognises about themselves. The useful choice lives
one level down among the 208 situations, and 208 is not a list anyone reads. It is also precisely
the flattening the owner objected to: the sentence becomes one token and everything else in it is
discarded.

**Option 2 — A local model proposes a shortlist; the person confirms.**
The model sees the sentence and the closed list, and may return only items drawn from that list,
with "none of these" as a first-class answer. Nothing activates until the person taps one.
Nothing leaves the device.
*Weakness:* requires the privacy gate to release something that is not about a file, and that
gate is the most load-bearing mechanism in the product.

**Option 3 — A cloud model proposes a shortlist; the person confirms.**
Identical in shape to option 2; different in where the sentence goes.
*Weakness:* irreversible. The design already states that revocation cannot retract what has
already been sent to an external provider, and requires the product to say so plainly.

**Option 4 — No proposal step. The declaration becomes standing context.**
Nothing is matched; the sentence travels with judgements the product already makes, colouring
them. This is arguably the most faithful reading of the owner's actual sentence.
*Weakness:* the sentence goes out repeatedly rather than once; the prompt becomes effectively
permanent because its bytes are fingerprinted into every audit record; and the product could no
longer answer *"what did my answer do?"* — a question its own design says it must answer.

**Option 5 — Do not ask who the person is. Ask what *this folder* is.**
The product already asks narrow questions at the moment a specific decision is blocked. This
extends that rather than adding an interview.
*Weakness:* never builds a picture of the person, so it cannot help with anything the folder in
front of it does not already raise.

### 3.5 The central risk

The sharpest risk is not a model being wrong. It is a model being *plausibly* wrong.

A shortlist is an endorsement. A list of three with the wrong item first is read by most people
as the product's opinion, and the confirmation step is weak against a plausible-looking first
item. This is what separates options 2 and 3 from the rest.

Mitigations exist — present candidates unordered rather than ranked; give "none of these" equal
visual weight; show what each candidate *would build*, since the product already prints exactly
that — but all of them would need approval, and none of them is free.

Option 4 carries a different risk that is harder to see: there is no match to be wrong, but the
declaration colours every ambiguous file, with nothing on screen connecting the two.

### 3.6 What is fixed, and what is genuinely open

**Fixed by the design. A ruling has to live inside these.**

- A role answer never becomes a folder name or an automatic-filing permission.
- An answer that matches nothing must remain unmatched, not snapped to a similar category.
- Nine kinds of data are always local and may never appear in a model request.

**Open. The design is silent and this document does not fill it.**

- **Whether a person's typed self-description is a "user edit"**, which is the seventh of those
  nine always-local kinds. If it is, options 3 and 4 are closed by the design as written and no
  consent can open them. If it is not, the design is silent about a category of data it never
  anticipated. *This is the single most consequential unresolved point.*
- **What the product says to a person whose words match nothing.** The outcome must exist and the
  path must be explicit, but the wording is specified nowhere, and it is the sentence most likely
  to be read as rejection.

### 3.7 The questions we would value an opinion on

1. **Should a model be involved in this step at all** — and if so, may its output ever be
   anything other than a proposal the person confirms before anything activates?
2. **If a model is involved, may the person's own sentence leave the device** — never, only under
   explicit consent, or freely? This is the only question here whose wrong answer cannot be
   undone.
3. **Is a typed self-description the kind of data that should never leave the device by default?**
   (In our terms: is it a "user edit"?) A view from outside the project would be valuable, because
   inside it this is a reading of our own document that we cannot settle by reading it again.
4. **Should the declaration be able to activate a category at all**, or should it only ever be
   context that informs a judgement the product was already making?
5. **Should a person choose from 23 broad categories or 208 specific situations?** 23 is short
   enough to read and too coarse to be useful; 208 is useful and unreadable.
6. **What should the product say to someone whose words match nothing?**

### 3.8 Our own current view, offered as a view and not a decision

The strongest option on the evidence is **2** — a local model proposing a shortlist the person
confirms — with **5** kept alongside it and **1** as the fallback wherever no local model exists.

- It honours both positions without straining either. The objection to a matcher is that it
  *discards* everything in the sentence except one token; a model that reads and proposes discards
  nothing, and the person still does the deciding.
- It makes questions 2 and 3 not arise, because nothing leaves the device — and those are exactly
  the questions that would otherwise hold the whole workstream.
- Its failure mode is the one this product handles best: a visible list a person can reject,
  rather than a silent colouring.

**The strongest argument against it**, on the record because it is not weak: options 2 and 3 both
require the privacy gate to release something that is not about a file. That gate is the most
load-bearing mechanism in the product; extending it is not a small change, and the cost is not
visible from any design document. If that is judged too high, **option 5 plus option 1 is a real
answer and not a retreat.**

The option we would most value scrutiny of is **4**, because it is the most faithful reading of
what the owner actually said and the one whose consequences are hardest to see from its face.

---

## What this document did not do

No prompt wording is drafted, proposed or settled anywhere in it. In this project prompt text is
a mechanism and is approved manually by the owner; it is also close to permanent, because the
prompt bytes are fingerprinted into every audit record and every cache key they produce. Where an
option above describes what a model would be shown, it describes the *shape and the content
requirements* only, and every such description is a proposal requiring approval.

The fuller internal version of this analysis, with a file and line reference behind every claim
about behaviour, is `planning/78-ROLE-MATCHER-DECISION.md`.
