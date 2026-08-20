# Council seat — the design's plain reading

Date: 2026-08-21 (overnight)
Seat: **what does `00-database-agent-product-design.md` most plainly say?**
Not what is cheap, not what is safe. The other two seats hold those.
Source of truth: [`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md)
Method matched to: [`../reviews/round-1-fidelity.md`](../reviews/round-1-fidelity.md)

**Every quotation below was verified by exact string match against `00`.** The finished file was
then re-audited mechanically, the way round 1 audits plans: all quoted spans extracted by regex, split
on ellipses, punctuation- and markdown-normalized, matched against the source — **29 blockquote
segments, 0 failures** (26 from `00`; 3 are `01`'s header lines, verbatim except that the markdown
link around the filename is rendered as a plain path); **72 inline quotations, 61 resolved to `00`**,
the remaining 11 being quotations of the council brief, of `NEEDS-JOSEPH.md`, of P6's
`PLAN-SKELETON.md`, or my own glosses, each attributed in place.

Three defects that audit caught in my own draft are fixed and recorded rather than quietly corrected:
a dropped "and" inside a quotation of §3.11's Finance row, a capitalised first letter inside a
quotation of §3.11, and — the one that changed a conclusion — **a precedence rule I said did not
exist, which does.** See D6.

Where I infer, the line says **INFERENCE** and names what it is inferred from. Where the design says
nothing, the line says **silent** — that is a finding, not a gap in my work.

---

## A structural fact that reframes three of the six questions

**`00` contains no tables.** Not in §3, not in §5. It is 286 lines of continuous prose, and it
carries no section numbers either, despite its own preamble claiming "It is numbered so that
implementation can proceed part by part". The §-numbers everyone in this project cites, and the six-row
`| Domain | Fields |` table that D1 and D6 are both arguments about, exist only in
`01-product-design-structured.md` — a sectioned rendering of `00`, produced for implementation
reference.

`01` says so itself, in its own header, and this turns out to matter more than anything else in this
document:

> Status: **structured view** — derived from the source of truth, **not a substitute for it**
> Source of truth: `00-database-agent-product-design.md` — **Joseph's wording is authoritative**

So the project **does** have a precedence rule. It is not in `00` — I searched and there is none —
it is in `01`'s header, and it says `00` wins. `01` attributes the *wording* to Joseph ("Author:
Joseph (worked out manually); sectioned here for implementation reference"); it does not claim he
authored the table, and it declares in advance that where the two differ, his wording governs.

I use the §-numbers below because the whole project does. But **the table is a sectioning artifact
that `01` itself subordinates to the prose**, and what it replaced matters enormously. `00`'s §3.11
reads:

> Academic files **may use** school, term, course, instructor, and work type. College application
> files **may use** target university, application cycle, application document type, and purpose.
> Research files **may use** project, stage, artifact type, lab, and venue. Finance files **may use**
> institution, account type, tax year, and record type. Photos **may use** capture year, event,
> location, people, camera information, and media type. Code files **may use** project, repository,
> programming language, and artifact type.

Six sentences, each hedged with "may use". `01` rendered them as a table with a column headed
`Fields`, and the modal disappeared. **P6's Done-means 2 closes a list that Joseph never wrote as a
list, on the authority of a rendering that disclaims its own authority.** Three of the six decisions
below turn partly on this, and it is the single most useful thing in this document.

---

# D1 · The field catalogue — open or closed, and how far

## What the design says

**The mechanism, verbatim (§3.11):**

> The fields used to describe files should not be one enormous universal list. The product should
> have a small shared set of universal file facts, such as file type, creation date, language,
> duplicate family, version family, and sensitivity status. It should then activate domain-specific
> schemas only when the evidence indicates that a domain is plausible.

**The design never closes a field list anywhere.** I checked every enumeration of fields, domains or
templates in `00`. Every single one is hedged:

| § | Enumeration | Hedge, verbatim |
|---|---|---|
| 3.11 | universal file facts | "**such as** file type, creation date, language, duplicate family, version family, and sensitivity status" |
| 3.11 | the six domains | "Academic files **may use** …" (×6) |
| 3.8 | role facets | "The agent should model these as distinct facets, **such as** `authored_by` and `target_school`, or `our_firm` and `client`." |
| 3.12 | the `fields` table | "The fields table defines the kinds of facts the product understands, **such as** subject, purpose, target university, project, event, or sensitivity." |
| 5.4 | folder templates | "An Academic template **may define** school → term → course → work type; … a Career template **may define** company → role or recruiting cycle → document type" |
| 8.2 | the file record | "The file record should retain **at least** the following information" |
| 8.2 | provenance events | "**This includes** discovery, stat observation, hashing, extraction, OCR, …" |
| 8.5 | replay measures | "The replay harness should measure **at least** the following" |

And the design **does** have closed vocabularies — it just writes them differently. §3.13's six
reliability states are definitional prose with no hedge. §8.4's five handling classes are introduced
"The system should classify data into handling classes before LLM escalation:" — flat, no hedge.
§8.4's four operation modes, likewise. §8.3's plan preconditions are introduced as "the **complete**
expected precondition".

**The design marks a list open when it means it open. It does this for every field and domain list
without exception, and for no state or mode vocabulary.** That is a checkable internal convention,
and it is the answer to "open or closed".

**Three independent proofs that §3.11 is not the whole catalogue,** each from a different section:

1. **§3.8** names four facets — "such as `authored_by` and `target_school`, or `our_firm` and
   `client`" — none of which is in any §3.11 row. (Round 1's F-1 found this.)
2. **§5.4** gives a Career template — "a Career template may define company → role or recruiting
   cycle → document type" — and then says "Each template is populated from the facts and accepted
   groups that already exist in the evidence database." `company` and `role or recruiting cycle` are
   therefore facts, and neither is in any §3.11 row. **This is a second, independent proof, and I do
   not believe it has been stated before in this project.**
3. **§3.15** names the launch domains — "academic coursework, college applications, research and lab
   work, **career and recruiting**, photos and captures, and code projects" — a six that is *not*
   §3.11's six. Career and recruiting is a launch domain with zero §3.11 fields; Finance has §3.11
   fields but is demoted in §3.15 to a safety domain.

**And the design explicitly anticipates the catalogue growing (§5.7):**

> The product should eventually maintain a library of roughly 200–300 domain-specific templates,
> covering common organizational situations such as academic programs, university applications,
> recruiting processes, client engagements, research workflows, financial records, travel, legal
> matters, creative projects, software repositories, personal administration, and photo collections.
> **Each template should define the domain's allowed fact fields**, detection signals, recommended
> folder dimensions, preferred dimension order, optional branch patterns, privacy rules, and
> validation constraints.

and (§3.11):

> Across the whole product, there may eventually be many specialized fields because different domains
> genuinely require different information.

**But it also states a scope, twice, and both statements are against the catalogue as a launch
artifact.** §3.15's closing sentence:

> This approach gives the product broad long-term coverage **without prematurely hand-authoring
> hundreds of specialized schemas**.

and §5.7's:

> The product does not need to fully implement every template at launch; **it can begin with the core
> domains and expand the library as recurring user needs and corpus evidence justify additional
> coverage.**

## What it does not say

- It never says how many fields may exist. "many specialized fields" is the only quantity given for
  fields; "roughly 200–300" is the only quantity given for *templates*.
- It never says the six §3.11 rows are complete, and never says they are examples either. It says
  "may use" and leaves it.
- It gives no rule for *authoring* a new domain schema — only for an LLM-generated one at run time
  (§5.7), which "cannot invent unsupported facts, silently create new high-level domains, or become
  active merely because it is syntactically valid."
- It says nothing at all about a hand-authored pre-launch catalogue, except the one clause in §3.15
  that calls the activity premature.

## My reading

**The catalogue is open, and the design says so five different ways — but the design also states a
launch scope that the 560-domain catalogue is roughly twice past, and names the exact activity that
produced it as the thing to avoid doing early.**

Broken into the two halves, because they carry different confidence:

| Claim | Confidence |
|---|---|
| §3.11's six rows are not a closed catalogue; P6's Done-means 2 states something the design does not | **states it** — six "may use" sentences, plus §3.8, §5.4 and §3.15 each naming fields outside them |
| The product's eventual field set is large and domain-scoped, and that is the design's intent | **states it** — §3.11 "many specialized fields"; §5.7 "Each template should define the domain's allowed fact fields" |
| Launch scope is the six §3.15 domains fully supported plus four safety domains, with the rest as placeholders | **states it** — §3.15, verbatim, in one sentence |
| A 560-entry, 2,233-field hand-authored catalogue is what the design asks for **now** | **the design says the opposite** — §3.15's "without prematurely hand-authoring hundreds of specialized schemas"; §5.7's expansion trigger is "recurring user needs and corpus evidence", and no catalogue entry has either |

So on the lead's framing — open fully, or open narrowly — the design's plain answer is neither of
the offered options. It is: **the catalogue is legitimate and the design wants it eventually; §3.15
says which ten domains are live at launch and the rest are placeholders.** The design already
contains the answer to "how far open" and it is a *scope* answer, not a *cardinality* answer. The
catalogue does not need to shrink; it needs a launch/placeholder flag, which is §3.15's own word.

One more thing the design settles that the framing gets wrong: the lead's alternative asks whether
the domain catalogue becomes "a routing aid rather than a fact schema". §3.15 draws the split
differently and explicitly —

> Each domain consists of two related definitions: a **fact schema** describing the information the
> system may extract from files in that domain, and a **folder template** describing the small subset
> of those facts that may become physical folder levels.

— so a domain is *both*, and the folder template is a small subset of the fact schema. "Routing aid
instead of fact schema" is not a distinction the design offers.

## Where my seat is weak on this one

**The strongest argument against me is §3.11's own first sentence.** "The fields used to describe
files should not be one enormous universal list" is a sentence about restraint, and I am using the
rest of the section to authorize 2,233 field names. Someone reading only that sentence, in a document
whose §3.7 warns about "polished but completely false filing paths" and whose §3.15 warns against
premature schemas, would reasonably conclude the author's *disposition* is restrictive and that P6's
SPEC read the room correctly even if it misread the grammar. I think the grammar wins, but the
disposition is genuinely the other way and I should not pretend otherwise.

Second: **"may use" is not unambiguous.** It can mean "these are the permitted fields" (a permission
grant, which is closed) as easily as "these are among the fields it might use" (illustrative, which
is open). I lean open because §3.8, §5.4 and §3.15 each independently name fields outside the six
rows — but the modal alone does not settle it, and I would be overreaching to say it does.

Third: **S3.** [`04-resolutions.md`](../../04-resolutions.md) already resolved the Career hole as
"Career/recruiting fact schema (§3.11) and Code + Finance templates (§5.4) stay deferred … Joseph
authors these when those parts come up." S3's own reasoning agrees with me — it calls it "a hole in
the design, not a spec defect" — but it means the project has a standing decision here, and P6's
Task 2 hardening "deferred" into "acquiring one fails the test" is a drift from S3, not from the
design. Whether S3 was ever Joseph-ratified I could not establish; `04` is marked "binding" but
carries no ratification stamp on that row, unlike C1 and B4 elsewhere.

---

# D2 · `sensitivity` — one record or three

## What the design says

**It is a fact. §3.1, verbatim, is the clearest sentence in the design on this:**

> A file can simultaneously be a syllabus, part of a particular course, created for a particular
> semester, related to a university, included in an application package, a member of a version
> family, and **potentially sensitive. These are separate facts about the same file.**

**§3.11** puts it in the universal set: "such as file type, creation date, language, duplicate family,
version family, and **sensitivity status**."

**§3.12** puts it in the `fields` table by name: "The fields table defines the kinds of facts the
product understands, such as subject, purpose, target university, project, event, or **sensitivity**."

**§8.2** lists it on the file record — under "The file record should retain at least the following
information:" — as the line `Sensitivity state`. That same list separately carries the line
`Current and historical file facts`.

**§8.4** is the only place with a value vocabulary. "The system should classify data into handling
classes before LLM escalation:" followed by five: `Public or low sensitivity` · `Personal but
non-sensitive` · `Sensitive personal` · `Highly sensitive or credential-bearing` ·
`Unreadable or unclassified`. And then:

> The classification is itself **evidence-backed** and can be revised by the user.

**It is not three homes. It is at least six.** Beyond §3.11 / §8.2 / §8.4, `00` also carries:
§8.4's separate `protected state` ("A scanned passport, tax statement, medical document,
authentication key, or account record should enter a protected state immediately"); §8.3's plan-record
line `Sensitivity and consent state`; §5.7's template field "privacy rules"; §7.2's residual-template
"sensitivity restrictions". §7.5 displays "sensitivity status" and §7.7's dossier carries
"sensitivity state" — **both spellings are in Joseph's own prose, four sections apart.**

**On the user-reclassification half,** §8.4 states the right twice — "can be revised by the user" and
"The user should be able to … reclassify a file as private" — and §3.13 states what a user revision
of a fact *is*:

> A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the
> user.

## What it does not say

- It never equates the §3.11 fact, the §8.2 state and the §8.4 handling class. Not once, in any
  direction. There is no sentence in `00` containing both "sensitivity" and "handling class".
- It never gives the §3.11 `sensitivity status` fact a value vocabulary. §8.4's five classes are
  introduced as a classification for a *purpose* ("before LLM escalation"), not as the values of a
  file fact.
- It never states the relation between the five handling classes and the "protected state". §8.4
  gives five classes and, in a separate paragraph, five *kinds of document* that "enter a protected
  state immediately", and joins them nowhere. (This is C5 in NEEDS-JOSEPH, and it is real.)
- It never says which subsystem writes it.

## My reading

**One record, in the fact layer, and §8.4's five classes are its values. Confidence: implies it.**

The argument is three sentences long and every step is quoted. §3.1 says a file's being sensitive is
a *fact* about it, in a sentence whose whole purpose is to enumerate what facts are. §3.11 puts
`sensitivity status` in the universal fact set. §8.4 says its own classification is
"evidence-backed" — and "stores them … with the evidence that supports each one" (§3.1) is the
design's definition of what makes something a fact rather than an observation. A thing that is a
universal file fact, sits in the `fields` table by name, and is evidence-backed and user-revisable, is
a fact. §8.2's `Sensitivity state` is then the file record's denormalized view of it — which is
exactly what §8.2's list is for, since it also denormalizes `MIME type and detected format` and
`Extraction status by extractor tier`, both of which live elsewhere.

**And a user reclassification does arrive as a `user_confirmed` fact — conditionally. Confidence:
states it, given the above.** §3.13's definition is not hedged: a fact "explicitly accepted, entered,
renamed, merged, or **corrected** by the user" is user-confirmed. §8.4's reclassification is a
correction by the user. If sensitivity is a fact, §3.13 applies to it with no further reasoning. The
conditional is the whole risk: the second question is entirely downstream of the first and the design
answers it only through the first.

## Where my seat is weak on this one

**§8.2 lists `Sensitivity state` and `Current and historical file facts` as two separate lines.** If
sensitivity were simply a fact, the first line is redundant with the second. That is a real textual
argument against me and it is the best one available. My answer — that §8.2's list denormalizes other
things too — is a reading of the list's purpose, and §8.2 does not state its purpose.

**Second, and I think this is genuinely unresolved rather than merely awkward:** a "handling class"
and a "sensitivity status" may not be the same *kind* of thing at all. `Sensitive personal` answers
"what is this file"; `Unreadable or unclassified` answers "why can I not decide" — an extraction
outcome, not a property of the content. A five-value vocabulary that mixes those two is not obviously
a fact's value space, and §3.13's reliability states already carry the "we could not decide" role. If
`Unreadable or unclassified` belongs to the gate rather than to the file, then §8.4's list is a gate
vocabulary and the §3.11 fact needs its own — two records, not one. **The design does not resolve
this, and I cannot honestly say it implies my answer over that one.** It is round-1's F-9 seen from a
different angle: the fifth handling class has no design source for its inputs, because it may not be
the same kind of value as the other four.

---

# D3 · Deletion versus append-only

## What the design says

**The deletion right (§8.4), verbatim and in its full sentence:**

> The user **should be able to** review and delete local derived data, revoke a policy for future
> runs, and reclassify a file as private. Revocation cannot necessarily retract data already sent to
> an external provider, so the product **must** communicate that distinction clearly.

**The append-only obligation (§8.2), verbatim:**

> Every significant event affecting a file **should be preserved** in an append-only provenance log.

**The overwrite prohibition (§8.2), verbatim and complete — note where the sentence ends:**

> The product **must never overwrite the evidence record merely because a later extractor or model
> produces a different answer.** A newer result should supersede an earlier result while retaining
> the old observation and the reason it was superseded.

**The strongest retention statement in the design is neither of those. It is §8.1:**

> The key principle is that the system **must** be able to reconstruct what it knew, what it proposed,
> what the user approved, what changed on disk, and why every change occurred.

**The design uses "derived" exactly once in a technical sense, in §3.2:**

> an EXIF field called `DateTimeOriginal` is raw metadata; `capture date = 2026-07-17` is the file
> fact **derived** from it.

**And §0 makes a claim about the whole database:**

> The database agent does not own the namespace, create a virtual filesystem, or require a proprietary
> storage format. **It can be rebuilt from the filesystem if necessary.**

**§8.7 runs the same collision, in two adjacent sentences, and also does not resolve it:**

> Rejected groups, rejected destination matches, rejected labels, and rejected residual recommendations
> **must** be stored with the evidence that produced them. Otherwise the system will repeatedly
> resurface the same attractive but incorrect grouping. The user **should be able to** inspect or
> **reset** learned preferences, so personalization remains understandable and reversible.

## What it does not say

- It never defines "local derived data". §3.2's technical usage (a fact derived from an observation)
  and §0's implicit usage (the whole database, since it is rebuildable) point at different scopes, and
  the design never chooses.
- **It never says audit records are or are not deletable.** §8.4 requires them ("Every model call
  should be recorded in a consent-aware audit record") and gives the deletion right in the next
  paragraph, without connecting them.
- It never says what "append-only" means against a *user* action. §8.2's whole paragraph is about the
  system's own behaviour when re-extracting.
- It never states a retention period for anything. (C7 in NEEDS-JOSEPH is genuinely absent from the
  design.)

## My reading

**The design does not actually put these two in conflict, and the conflict as stated is an artifact of
reading §8.2's `must` more broadly than its own sentence goes. Confidence: states it, for the narrow
claim; silent, for everything the decision actually needs.**

The narrow claim, which I hold firmly: **§8.2's only `must` is scoped by "merely because a later
extractor or model produces a different answer."** It forbids one thing — clobbering evidence as a
consequence of re-extraction disagreeing — and prescribes the remedy in the next sentence
(supersede-and-retain). It does not address a user asking to erase a passport's OCR text, and reading
it as though it does is reading past the clause. What actually collides with §8.4's deletion right is
§8.2's *first* sentence ("should be preserved in an append-only provenance log") — and that is a
`should` against a `should`, with no stated tiebreak.

Two further things the design does state, both of which favour the deletion right being real:

- §8.4's contrast only works if local deletion is effective. "Revocation cannot necessarily retract
  data already sent to an external provider" is drawn as a *limit*, against an implied local case that
  is not so limited. A right that deleted nothing anywhere would need no such caveat.
- The `must` in that sentence attaches to the disclosure ("the product must communicate that
  distinction clearly"), not to the deletion. P7's SPEC derives from this that audit records of
  external sends can never be deleted, because the disclosure is impossible once the record is gone.
  **That derivation is sound and it is the best-argued inference in the P7 SPEC** — but it is an
  inference, and it covers only audit records of *external sends*. It says nothing about local model
  calls or about the rest of the log.

**On "what counts as derived", the design is silent and the two candidate readings are far apart:**

| Reading | Grounded in | Reaches |
|---|---|---|
| Narrow — derived = conclusions built from observations | §3.2's own use of the word | facts, groups, placements, plan versions. **Not** OCR text, **not** extracted text — §3.2 calls those raw |
| Broad — derived = everything the product computed from your files | §0's "It can be rebuilt from the filesystem if necessary" | the entire SQLite database |

**The narrow reading is the design's own vocabulary, and it excludes exactly the thing P7's SPEC says
the product cannot ship without** — "The product cannot ship unable to forget a scanned passport's OCR
text." Under §3.2, OCR output is raw evidence, not derived data. I flag this because it cuts against
the convenient answer and I think it is the most consequential unnoticed reading in this decision.

**On whether audit records are deletable: silent.** An audit record is a record of the product's own
action, not data derived from file content, so it does not obviously fall under either reading. §8.1's
"must be able to reconstruct … what the user approved, … and why every change occurred" is the closest
thing to an answer and it is a `must`, but it is a statement about system capability, not about what
survives a user's deletion request.

## Where my seat is weak on this one

**"Append-only" is a term of art and I am reading it narrowly.** In ordinary engineering usage an
append-only log is one whose entries are never removed, full stop — the phrase carries that meaning
without needing a second sentence to say so. My argument that §8.2's `must` is scoped is correct about
that sentence, but it lets me sidestep the fact that the *first* sentence probably already forbids
deletion in the way any reader would understand it.

**And §8.1's `must` is against me.** "The system must be able to reconstruct what it knew, what it
proposed, what the user approved, what changed on disk, and why every change occurred" is unhedged,
unscoped, and stated as *the key principle* of the entire trust layer. A product that honours a
deletion request cannot always reconstruct what it knew. That is a real collision between a `must` in
§8.1 and a `should` in §8.4, and on modal strength alone §8.1 wins. The honest summary is: **the
design's `must` favours retention, its `should` favours the user, and it never noticed.**

---

# D4 · Jurisdiction

## What the design says

**Nothing.** I checked mechanically over `00`:

| Term | Occurrences in `00` |
|---|---|
| `jurisdiction` | **0** |
| `country` | **0** |
| `locale` | **0** |
| `GDPR` / `HIPAA` / `United States` | **0** each |

The four occurrences of `region` are all "OCR region" or "table-like regions".

**But it is not silent on internationalization, and that is a different thing.** Four statements, all
verbatim:

- §2.7: "appropriate language support including **CJK** where required"
- §3.3: "real file collections contain vague filenames, indirect language, **multilingual documents**, screenshots, unlabeled forms…"
- §2.2: "The system should not use unreliable global language-quality checks that incorrectly punish **multilingual** or mathematics-heavy documents."
- §3.11: `language` is one of the six universal file facts.
- §3.10: "Academic terms such as `Spring 2025`, `AY 2024-25`, and **`Michaelmas Term 2024`** require dedicated patterns rather than generic parsing." — a British collegiate term, named as a required pattern.

**And every field the design names is jurisdiction-neutral by construction.** §3.11's Finance row is
"institution, account type, **tax year**, and record type" — every jurisdiction has a tax year; none of
them share a form catalogue. §3.15's safety domains are "Finance, identity, medical, and legal
material" — categories of material, not regulatory regimes. §7.3's Protected Records names "passport
scans, medical documents, account statements, **visas**, legal forms, or credentials" — international
by nature, regime-free in description.

**The design scopes exactly one thing, and it is not jurisdiction.** §2.7: "**On macOS**, Apple Vision
should be configured explicitly with accurate recognition…"

## What it does not say

- No jurisdiction, named or implied, anywhere.
- No statement that jurisdiction-neutrality is deliberate.
- No guidance on gazetteers, which §3.7 requires ("validated gazetteers") and which are
  jurisdiction-scoped in practice — the design names the mechanism and never asks where its contents
  come from.

## My reading

**Silent — and structurally silent, not accidentally so.** Confidence: **silent**, with one
observation attached.

The observation: the design's field vocabulary is jurisdiction-neutral in every instance, and this
does not look like luck. `tax year`, `record type`, `account type`, `institution`, `work type`,
`document type` — these are the shapes you get when someone is deliberately naming the *slot* rather
than the *artifact*. The catalogues that hit the jurisdiction wall hit it because they went one level
finer than the design ever goes: the design says `record type`, the catalogue wants to know whether
that record is a W-2 or a P60. **INFERENCE**, from the six field names above: the design's chosen
altitude does not require a jurisdiction answer, and a catalogue that needs one has descended below
the design's altitude. That is a fact about the catalogue, not a licence for it.

The second observation, weaker: §2.7 scopes the product to macOS explicitly. Joseph expressed a
scoping instinct where he had one. He expressed none for jurisdiction. **INFERENCE**, and a weak one —
absence of a statement is not a statement of absence.

**This is Joseph's to invent, entirely.** There is nothing in the design to read.

## Where my seat is weak on this one

My "structurally silent" framing is doing work the text does not authorize. Six jurisdiction-neutral
field names in a document that names `Michaelmas Term 2024`, `Columbia`, `UChicago`, `BUSIB 4300`,
`MIT` and `UNC` — a corpus that is otherwise overwhelmingly American with one British academic term —
could just as easily mean the author was writing about his own files and never thought about it. The
neutrality may be the neutrality of a small vocabulary rather than of a considered position, and I
have no way to tell from the text. I would not want the phrase "structurally silent" read as "the
design has quietly decided to be jurisdiction-agnostic". **It has not decided anything.**

---

# D5 · The `no_usable_facts` pass structure

## What the design says

**Six ordering statements exist, and together they cover more of the sequence than I expected.**

**§1.2 — extraction is one pass, and it decides nothing:**

> The engine next performs one reusable local extraction pass for each file version. **This pass does
> not decide what a file means or where it belongs.**

**§2.1 — read once per content version, and reuse:**

> The engine should read each file once per content version, store the resulting evidence in SQLite,
> and allow every later stage—domain routing, fact extraction, template fitting, proposal generation,
> LLM interpretation, and user review—to reuse that same evidence.

**§3.2 — facts come after extraction, and the word is "directly":**

> The fact layer sits **directly after** universal extraction and becomes the shared memory of the
> entire pre-sorting engine.

**§2.2 — the fallback is permitted:**

> A file with no text should route directly to OCR; a file that technically produces text but yields
> no usable facts **may** receive targeted OCR as a fallback because scanned PDFs can contain
> unreadable or corrupted extracted text.

**§2.7 — and it is *conditioned*. This is the "only", and it is in §2.7, not §2.2:**

> A document with a non-empty but unusable text layer should receive OCR **only when its extracted
> evidence fails to produce usable facts**, not because a broad quality heuristic says the text looks
> unusual.

**§8.2 — and this is the sentence nobody in this project seems to have used. It describes the fourth
pass:**

> For example, if a first OCR pass produces unreadable text and a later improved OCR engine recovers a
> university name, both extraction records should remain available. **The resolver may mark the newer
> value as preferred**, but a user reviewing a placement should still be able to inspect the origin of
> the conclusion.

**§3.4 — and the second run is a different cache slot, by construction:**

> The cache key includes content hash, extractor version, **analysis tier**, model identifier when
> relevant, and prompt fingerprint for model-derived results.

**§8.6 — the degradation order, which is a budget priority and not a pipeline:**

> The engine should degrade in a predictable order. Direct facts and high-precision rules run first
> because they are cheap and reliable. Full local extraction and OCR run within the configured budget.

## What it does not say

- It never uses the words "pass", "phase" or "stage" to describe a *corpus-wide* loop. Every ordering
  statement above is a statement about **one file**.
- It never says facts are re-resolved after targeted OCR. §8.2's sentence describes re-resolution
  after *a later improved OCR engine* — the same shape, a different trigger.
- It never says how many times a file may re-enter. §2.7's "only when" is a precondition, not a bound.
- It says nothing about whether the second fact pass sees the first pass's facts, supersedes them, or
  starts clean. §3.4 makes them different cache keys; §8.2 says the older record survives; neither says
  what the resolver does with both.

## My reading

**The design states the ordering constraint and states the precondition. It does not state a pass
architecture, and "four passes" is a caller design, not a design reading.** Confidence, split:

| Claim | Confidence |
|---|---|
| Facts must be attempted before targeted OCR on a broken text layer | **states it** — §2.7's "only when its extracted evidence fails to produce usable facts", plus §3.2's "directly after" |
| Consulting `no_usable_facts` inside the extraction loop is wrong | **states it** — same sentence; the condition is unevaluable before the fact pass exists |
| The fact layer runs again after targeted OCR adds observations | **implies it** — §8.2's resolver sentence describes exactly this for the improved-OCR case; §2.1's "every later stage … reuse that same evidence"; §3.4's separate cache key |
| The caller becomes four corpus-wide passes | **silent** — the design describes per-file preconditions and never a batching architecture |

The last row is the one that matters for the council. **The design fully supports the four-pass
plan's *correctness*; it does not require its *shape*.** A per-file state machine that runs
extraction → facts → OCR → facts for one file at a time satisfies every sentence quoted above, and so
does a four-pass corpus loop. §8.6's budget language ("Maximum OCR time per **scan**", "Maximum LLM
calls per thousand files") arguably favours batching, since scan-level ceilings are easier to honour
when the OCR-eligible set is known at once — **INFERENCE**, from §8.6's ceiling list. But the design
does not say it.

**One tension worth flagging, because it looks like a contradiction and is not.** §2.1's "read each
file once per content version" reads as forbidding a second read at the same hash. It does not: the
sentence's own justification is "A PDF should not be reopened separately for the Academic,
Applications, Research, and Career templates" — it is a rule against re-reading *per consumer*, not
against a fallback tier. §3.4 puts `analysis tier` in the cache key precisely so that `native` and
`ocr` results coexist for one hash, and §8.2 requires both extraction records to remain available.
The design contemplates multiple extraction records per content version explicitly.

## Where my seat is weak on this one

**§8.2's resolver sentence is doing more work in my argument than its context supports.** Its scenario
is a *software upgrade* — "a later improved OCR engine" — arriving weeks later, not a fallback tier
firing seconds later in the same scan. I am reading a sentence about version drift as a sentence about
pipeline order. The shape is the same and I think the reading holds, but it is one worked example in a
provenance section, and a careful reader could fairly say §8.2 is telling me what to *retain*, not
when to *re-run*.

**Second: §8.6's degradation order is not on my side as much as it looks.** "Direct facts and
high-precision rules run first … Full local extraction and OCR run within the configured budget" puts
facts before extraction, which is the reverse of §1.2 and §3.2. That is because §8.6 is ordering
*budget priority*, not execution. But someone could read §8.6 as the design's actual pipeline
statement, in which case the whole facts-after-extraction ordering I rely on is contested by the one
section that uses the word "order". Round 1's F-21 found the same passage being over-read in the other
direction.

---

# D6 · Field naming

## What the design says

**On `subject` vs `course` — both are Joseph's prose, and the count is four against four.**

`subject`:
- §3.1: "A fact is a statement such as **subject = BUSIB 4300**, term = Spring 2026, work type = syllabus, capture date = 2026-07-17, or purpose = university application."
- §3.12: "The fields table defines the kinds of facts the product understands, such as **subject**, purpose, target university, project, event, or sensitivity."
- §3.14: "A fact such as **subject = BUSIB 4300** does not itself dictate one permanent folder path."
- §3.8: "Authorship is usually metadata; the document's purpose, project, **subject**, or target is more informative for placement."

`course`:
- §3.5: "For example, BUSIB 4300 becomes a **course fact** only when the engine finds a course-code pattern together with academic context…"
- §3.11: "Academic files may use school, term, **course**, instructor, and work type."
- §5.4: "An Academic template may define school → term → **course** → work type"
- §5.5: the worked Academic tree, where the level holding `BUSIB 4300` is the course level.

**On `capture date` / `creation date` / `capture year` — three names, and on a careful reading three
different things:**

- §3.1: "**capture date** = 2026-07-17" · §3.2: "an EXIF field called `DateTimeOriginal` is raw metadata; **capture date** = 2026-07-17 is the file fact derived from it."
- §3.11 universal: "such as file type, **creation date**, language, duplicate family, version family, and sensitivity status"
- §3.11 Photos: "Photos may use **capture year**, event, location, people, camera information, and media type"
- §5.4 Photos template: "a Photos template may define **year** → event"

**On spaced vs snake_case.** `00` writes field names in English throughout — `work type`,
`target university`, `application document type`, `capture year`, `media type`, `camera information`,
`account type`, `tax year`, `record type`, `artifact type`, `programming language`, `creation date`,
`duplicate family`, `version family`, `sensitivity status`, `file type`. It writes something
identifier-shaped **exactly once**, in §3.8:

> The agent should model these as distinct facets, such as `authored_by` and `target_school`, or
> `our_firm` and `client`.

**On a precedence rule.** I searched `00` for every form of one: `precedence`, `takes priority`,
`authoritative`, `in case of conflict`, `wins`. **Zero occurrences** — `00` states no rule for
resolving its own internal disagreements.

**But `01` does, in its own header, verbatim:**

> Status: **structured view** — derived from the source of truth, **not a substitute for it**
> Source of truth: `00-database-agent-product-design.md` — **Joseph's wording is authoritative**

That is a precedence rule, it is unambiguous, and it has been sitting at the top of the document
every SPEC in this project was written against.

## What it does not say

- Nothing about which of `subject` / `course` is the field and which is the description.
- Nothing about a key/display-name distinction, which is the concept that would dissolve the whole
  problem.
- Nothing about identifier spelling — no convention, no example beyond §3.8's four.
- Nothing about `capture year`'s derivation from anything.

## My reading

**Prose wins, and this is already ratified — not by me, by `01`'s own header. Confidence: states
it.** The `| Domain | Fields |` table is `01`'s rendering of six "may use" sentences, in a document
whose first two lines declare it "not a substitute for" `00` and declare Joseph's wording
authoritative. **There is no prose-vs-table question to decide. It was decided on 2026-08-19 and the
project has been citing the table anyway.**

What that leaves is the real conflicts, which are prose against prose inside `00`.

**On `subject` vs `course`: the design is silent on the name and clear on the count. Confidence:
silent for the name, implies it for "one field, not two".**

The count argument: §3.14 says "A fact such as `subject = BUSIB 4300` does not itself dictate one
permanent folder path" — and §5.4's Academic template dimension holding `BUSIB 4300` is `course`. If
`subject` and `course` were two fields, `BUSIB 4300` would be stored twice, under two field rows, from
the same evidence — and §3.12's model ("connects one file to one field and one value") would carry it
as two facts with identical provenance. Nothing in the design suggests that, and §3.11's own argument
against "one enormous universal list" is an argument against exactly that kind of duplication.
**INFERENCE**, from §3.14 and §5.4 naming the same value under two words.

The one non-arbitrary signal on which word: **§3.12 is the only sentence in the design that enumerates
the contents of the `fields` table by name**, and it says `subject`. Every `course` occurrence is in a
sentence about something else — a validation rule (§3.5), a domain's activated set (§3.11), a template
dimension (§5.4). If one sentence is *about field identity*, it is §3.12's. That is the strongest
thing available and it is thin.

**On `capture date` / `creation date` / `capture year`: this is not a naming conflict, and I think the
project has misclassified it. Confidence: implies it.** Three distinct quantities:

| Name | § | What it is |
|---|---|---|
| `creation date` | §3.11 universal | a fact every file has — file or document creation |
| `capture date` | §3.1, §3.2 | a fact derived from EXIF `DateTimeOriginal`; §3.2 states the derivation explicitly |
| `capture year` | §3.11 Photos, §5.4 (`year`) | the Photos *folder dimension* — §5.4's Photos template is "year → event" |

A photo has all three and they differ. `capture year` appears in the Photos domain row and in the
Photos template, and §3.11 says a domain's fields are "usually three to six that may help build a
future folder proposal" — a year is a folder level; a full date is not. **NEEDS-JOSEPH's C15 frames
this as "Done-means 5 requires a field Done-means 2 forbids from existing", which is true — but the
underlying design is not in conflict here. §3.2 states `capture date` outright as a file fact. It is
missing from P6's catalogue because the catalogue was closed to §3.11, not because the design is
ambiguous.**

**On spaced vs snake_case: the design never addresses it, and it is not a design question.**
Confidence: **silent**. `00` is prose. `work type` in prose is English, not a key spelling —
`00` also writes "content hash", "file fact" and "handling class" the same way and nobody proposes
`content hash` as a column name. The design states display names because prose has no other option.
Choosing an identifier convention is an implementation decision the design does not reach, and there
is nothing here to overturn.

If Joseph wants the design's one signal anyway: **§3.8's snake_case is it**, because §3.8 is the only
place the design is naming *fields as fields* ("model these as distinct **facets**, such as
`authored_by` and `target_school`") rather than describing what a domain's fields are about. Every
spaced name appears inside a sentence describing content; the four snake_case names appear inside a
sentence prescribing identity. **INFERENCE**, from the grammatical role of the two lists.

## Where my seat is weak on this one

**On the table's standing I was initially too cautious, and I want to record the correction rather
than quietly present the stronger version.** My first draft said the design states no precedence rule
and that "Joseph never wrote the table" is a weaker claim than "the table has no standing". `01`'s own
header settles it — "not a substitute for it", "Joseph's wording is authoritative" — so the standing
question is closed and was closed before any SPEC was written. The residual weakness is smaller but
real: `01` is what the project has actually built against for weeks, and if Joseph read and accepted
the table it is his by adoption. Adoption would not, however, override a precedence rule printed on
the same page, so I hold this firmly.

**The remaining genuine weakness in D6 is `subject` vs `course`, where my §3.12 argument is thinner
than I would like.** §3.12's list is introduced with "such as" — it is an illustrative list like
every other, and I am giving it definitional weight because of the clause it sits in. Someone could
reasonably say §3.5's "becomes a **course fact**" is the more operational sentence, since it describes
a rule the system executes rather than an example of a table's contents, and that §3.11 and §5.4 both
back it. **The count argument (one field, two words) is much stronger than the name argument, and
Joseph should treat my lean toward `subject` as a tiebreak, not a reading.**

---

# What the design settles, and what is Joseph's to invent

This is the distinction the seat exists to produce, so I have kept it strict. "Settles" means a
sentence answers the question with no inference — from `00` in every row but one, where the sentence
is `01`'s own precedence header. Everything else is his.

## Settled by the design — no decision required, only compliance

| # | What the design settles | The sentence that settles it |
|---|---|---|
| **D1** | §3.11's six domain rows are **not** a closed catalogue. P6's Done-means 2 is wrong as written, and this is not a matter of judgement. | Six "may use" sentences; §3.8's four facets; §5.4's Career dimensions; §3.15's Career launch domain |
| **D1** | Launch scope is six fully-supported domains plus four safety domains; everything else is a placeholder. | §3.15, one sentence, unhedged: "The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: …" |
| **D1** | A domain is a fact schema **and** a folder template, the latter a small subset of the former. | §3.15: "Each domain consists of two related definitions…" |
| **D5** | Facts must be attempted before targeted OCR fires on a broken text layer; consulting `no_usable_facts` earlier is a defect. | §2.7: "should receive OCR **only when** its extracted evidence fails to produce usable facts"; §3.2: "directly after universal extraction" |
| **D6** | **Prose beats table, already ratified.** Where `00` and `01` differ, `00` governs — including everywhere the table dropped a "may use". | `01`'s header: "derived from the source of truth, **not a substitute for it**" · "Joseph's wording is authoritative" |
| **D6** | `capture date` is a file fact the design states outright. Its absence from P6's catalogue is a consequence of D1, not a naming question. | §3.2: "`capture date = 2026-07-17` is the file fact derived from it" |
| **D6** | `subject` and `course` are one field under two words, not two fields. (The *word* is not settled.) | §3.14 and §5.4 naming the same value, `BUSIB 4300`, under each |
| **D3** | §8.2's `must` does not forbid user-initiated deletion. It forbids one thing: clobbering evidence because a re-extraction disagreed. | §8.2: "must never overwrite the evidence record **merely because a later extractor or model produces a different answer**" |

## Genuinely Joseph's to invent — the design gives nothing to read

| # | What he must invent | Why the design cannot help |
|---|---|---|
| **D4** | **Jurisdiction, entirely.** Which ones ship, and whether the product has a jurisdiction concept at all. | Zero occurrences of `jurisdiction`, `country`, `locale`. Not under-specified — absent |
| **D3** | **What "local derived data" means.** §3.2's narrow sense excludes OCR text; §0's broad sense includes the whole database. | The design uses the word once, technically, and never in §8.4's sense |
| **D3** | **Whether audit records are deletable**, and all retention periods. | §8.4 requires the record and grants the deletion right two sentences apart, and joins them nowhere |
| **D2** | **Whether §8.4's five handling classes are the values of the §3.11 fact or a separate gate vocabulary.** | No sentence in `00` contains both "sensitivity" and "handling class". `Unreadable or unclassified` may not even be the same kind of value as the other four |
| **D6** | **`subject` or `course`** — the word itself. And identifier spelling, which the design does not reach at all | Four occurrences each, in different grammatical roles, with no precedence rule anywhere in `00` |
| **D5** | **Whether the caller batches.** Four corpus passes or a per-file state machine — both satisfy every sentence in the design | Every ordering statement in `00` is about one file |

## The middle band — the design leans, and the lean is worth knowing

- **D1, the 560-domain catalogue.** The design does not forbid it and expects something like it
  eventually — but §3.15's "**without prematurely hand-authoring hundreds of specialized schemas**"
  names the activity, and §5.7's expansion trigger is "recurring user needs and corpus evidence",
  which no entry has. **The design's answer is a launch flag, not a deletion.** 560 entries against
  §5.7's "roughly 200–300" and §3.15's ten launch domains.
- **D2, sensitivity.** The design leans hard toward **one record in the fact layer** — §3.1 calls it a
  fact, §3.11 makes it universal, §3.12 puts it in the `fields` table by name, §8.4 calls the
  classification "evidence-backed", which is what a fact is. §8.2's separate `Sensitivity state` line
  is the only real evidence the other way. **This is the closest of the six to being settled without
  being settled.**
- **D3, deletion.** The design's `must` favours retention (§8.1: "must be able to reconstruct what it
  knew…"); its `should` favours the user (§8.4). It never noticed the collision, and it runs the same
  collision again in §8.7 between a `must` to store rejections and a `should` to let the user reset
  them. **The pattern is the design's habit, not a one-off — which is itself worth knowing before
  answering, because whatever rule Joseph writes will need to cover §8.7 too.**

---

## The one thing I would most want said out loud

Two of these six questions exist because of `01-product-design-structured.md`.

**D1** is largely an argument about a table Joseph never wrote, whose column header (`Fields`) replaced
six instances of the words "may use". **D6**'s "prose vs table" framing is only a question because a
transcription introduced a table for prose to conflict with. Both would look different if every SPEC
had been written against `00`.

`01` is a good document and it made the project navigable. But it is a **rendering**, and four
downstream artifacts treat its table as the design: P6's SPEC reproduces it as
`| Domain | Fields (§3.11, literal) |`; P6's PLAN-SKELETON requires "the six §3.11 domain rows
verbatim" three times; `04-resolutions.md`'s S3 reasons from "§3.11's **table**"; round 1's F-1
reproduces it in full to make its case.

**The one artifact that quotes `00`'s actual sentence is the domain catalogue** — its `design_cite`
fields carry "§3.11 'Academic files may use school, term, course, instructor, and work type.'"
verbatim. It read the source of truth, and it is the artifact currently accused of overreach.

**And the rule that would have prevented all of it already exists.** `01`'s header, dated 2026-08-19,
before any SPEC in this wave was written:

> Status: **structured view** — derived from the source of truth, **not a substitute for it**
> Source of truth: `00-database-agent-product-design.md` — **Joseph's wording is authoritative**

Nothing needs to be decided here. A rule was written, printed at the top of the document, and then not
applied — four times, by four different authors, in the same direction each time. **The durable fix is
not a new rule. It is a pass over `01` restoring the hedges its tables dropped, so that citing the
table and citing the prose stop producing different answers.** That is a mechanical edit and it closes
the largest open question in the wave without Joseph deciding anything at all.

Joseph still has to decide D2, D3, D4, and the one word in D6. He does not have to decide D1 —
**§3.15 already told him the launch scope, in one sentence, and `01`'s header already told the project
which document to read it from.**
