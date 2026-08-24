# creative.self-initiated-work — lab notes

**Verdict: REFUSE (`refuse_node: true`).** The row is a label. It is named for the absence of a
client, and the only dimension it could contribute is the author-as-collector level that `00`'s
own template validator rejects by name. Every file it was meant to catch already has a home: a
sibling `creative.*` row when the file carries a positive signal, and one of six residual
templates when it does not.

This memo argues the refusal, then does the work a landed row does anyway — eleven fixtures, ten
never-alone rules, the reciprocal boundaries, the collision fixtures, and four items handed on.

---

## 1. Sources used

- `planning/00-database-agent-product-design.md` — every quoted span below was matched
  mechanically against this file before the memo was written. Thirty-one distinct spans; the
  check script and its result are in §10.
- `planning/domains/CONNECTION.md` §§1–5, 7 — the node test, the activation algorithm shape, the
  closed edge vocabulary.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed `kind: template`, `schema_id: creative`,
  `launch: placeholder`, `inherited_field_keys: []`, and read the `one_line_hint` of all 41
  `creative.*` siblings (the schema row is another agent's; I read its hint and wrote nothing).
- `planning/domains/ROSTER.md` §1a, §1b, §5 — NJ-R1a-1's status, the PR-6 placeholder shape,
  D1's field deferral.
- Landed nodes read for boundary alignment and for the refusal idiom:
  `code.scratch-prototypes.json`, `code.software-project.json`,
  `career.portfolio-work-samples.json`, `business_operations.organisational-records.json`.
- Depth calibration: `finance.crypto-assets.research.md`,
  `medical.wearable-health-exports.research.md`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; every fixture's `source_type` is drawn
  from the closed fourteen.

---

## 2. The question this row is actually asking

The roster hint states the situation with unusual honesty, and in doing so states the problem:

> Work a professional makes with no client — experiments, personal projects, speculative pieces —
> **using the same tools, formats and filenames as their paid work.**

Read that literally. The row asserts that its files are *identical* to another row's files in
tooling, format and naming. What is left to detect on? One thing: that a client is not there.

That is the whole of the row, and it is not evidence. `00` makes the general point about images
and it transfers exactly: *"the system must not mistake the absence of EXIF for proof that an
image is a screenshot."* A missing field is a fact about the search, not about the file. The
activation algorithm has no place to put it — CONNECTION.md §4 step 1 collects deterministic
signals *for* a schema, step 2 strikes any schema whose entire support is never-alone, and step 7
records the outcome when nothing survives: *"An empty set is a correct outcome, not a failure"* — the file routes to residual
review. A row that fires precisely when the engine has found nothing
is the empty activation set wearing a template id.

I want to be careful not to make this argument too cheaply, because a cheap version of it would
also refuse `career.portfolio-work-samples`, which is a landed node and correctly so. §5 handles
that contrast; it is the sharpest test this refusal faced.

---

## 3. The node test, all three limbs

CONNECTION.md §2: *a template row exists only if its detection signals, recommended dimensions, or
privacy rules differ from its schema's default template.* One limb is enough to license a row. All
three fail here, and a fourth thing fails that the three limbs hide.

### Limb 1 — detection signals: the complement of a signal set is not a signal set

The positive evidence in this world is all on the other side of the line. A brief with a stated
objective and a deadline; a purchase order; a client organisation in a labelled slot; an invoice
number; a signed contract; a model or property release. Those belong to `creative.creative-brief`,
`creative.client-engagement` and `creative.licensing-rights` respectively, and each of those rows
detects on the *presence* of its document.

Strip them and the remainder is the creative schema's own raw material: a layered `.psd`, a RAW
frame with EXIF, a `.docx` with heading structure, a session file with unlinked media. `00` reads
those through a generic extractor and says what it gets — *"Design and creative formats such as
PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format,
dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked
asset names, and preview text"*. Nothing in that list can distinguish paid from unpaid. Canvas
dimensions do not know who commissioned them.

So the candidate signal is a negated one — `client_not_found` — and §2 above rules it out.

### Limb 2 — recommended dimensions: `00` names this exact level as invalid, in advance

This is the strongest leg, and it is not an inference. `00`'s custom-template validator enumerates
what a template must not do:

> The engine validates that the proposed template does not repeat a parent dimension, create
> meaningless one-child levels, exceed practical depth limits, **use an author or organization
> merely as a collector**, expose protected information, or produce empty branches when tested
> against the accepted group.

A `Self-Initiated` branch is the author-as-collector level with the author's name left implicit,
because on a personal machine there is only ever one author. `00` states the same prohibition
twice more, in the role-split passage, and this time with the replacement rule:

> It should avoid using authorship or creator identity as a destination dimension. A folder should
> not become a collection point for everything produced by the same person or organization.
> Authorship is usually metadata; the document's purpose, project, subject, or target is more
> informative for placement.

The purpose here — *made it for myself* — is a statement about authorship in different words. And
P9's grouping stop rules bar the same shape from the other end: no supported group *"when one
high-frequency entity acts as the only bridge"*. On a solo practitioner's corpus the maker is the
highest-frequency entity there is.

Two of `00`'s other validator checks fire on the same level. It would *"create meaningless
one-child levels"* on a corpus that is entirely self-initiated, and *"produce empty branches when
tested against the accepted group"* on one that is entirely commissioned. The canvas is instructed
to undo it after the fact as well: *"It should warn when a level produces only one child"* and
*"It should recommend flattening when a dimension does not materially improve retrieval."*

Underneath that phantom level, the order is the schema's default and nothing else. `00`'s general
recommendation applies unchanged: *"For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar
folders."* A personal project and a commissioned one both branch project-first.

### Limb 3 — privacy: strictly *less*, never different

Removing the client removes obligations. The NDA, the unreleased campaign, the confidential brief
and the named individual in a model release are all the client-side rows' material. Nothing is
added. The one sensitivity this row does raise — a proprietary source file the engine cannot read
— is global and already handled: *"unsupported proprietary formats should be recorded as
indexed-but-unreadable rather than silently treated as empty."* `sensitivity: none`, with the
reasoning recorded on the node rather than left implied.

### The fourth thing — `00` already placed this material, outside the template library

"Personal Projects" appears twice in `00`. Both times it is a **user-chosen top-level location on
the canvas**, never a detection template. First as a root the user picks before analysis:

> Potential roots might include Desktop, Documents, Academic, Personal Projects, or a dedicated
> archive location.

Then as a move the *user* makes at the horizontal pass, explicitly against the engine's own
suggestion:

> The user can drag an accepted group into a top-level branch, merge Applications with Career if
> that matches their style, **place a research group under Personal Projects rather than
> Research**, or delete a suggested top-level area entirely.

That sentence is this row's entire content, and note what it does *not* say. It does not say the
engine detects that the research group is personal. It says the user moves it. Self-initiated is a
destination a person chooses, not a fact an extractor reads — and the dispatch prompt's first
rule keeps those apart absolutely: *do not write paths as facts.*

---

## 4. The hobby seam, answered in both directions

The dispatch warned this row sits on the professional-vs-hobby seam and must not quietly become a
hobby-folder row. It does not, because the seam has a floor on both sides and nothing between.

**If the maker is a working professional**, the sibling rows take the material back on its own
positive evidence, and none of them asks who paid:

| Unclienteled file | Row that takes it | On what positive evidence |
|---|---|---|
| A novel written on spec | `creative.book-manuscript` | chapter structure, running heads, draft revisions |
| A self-funded short film | `creative.post-production` | project file referencing media it does not contain |
| A self-released record | `creative.music-session` | session file, takes, stems, proliferating mixes |
| A personal photo series | `creative.raw-photo-catalogue` | RAW + sidecar + catalogue database |
| Textures kept for reuse | `creative.stock-asset-library` | material that *"belongs to no one project"* (roster hint) |
| A speculative poster | `creative.graphic-design-project` | artboard with trim and bleed, press-ready export |

**If the maker is a hobbyist**, `00` built the residual library for exactly this and names the
homes. Reference Clips holds *"saved visual inspiration, product references, quotes, recipes,
short article captures, code snippets, or other material that is useful for later retrieval but
does not belong to a current project."* One-Off Images holds *"images with no event, project,
reference collection, or photo-family association."* Review Later holds *"files whose meaning is
partly understood but whose final location requires a future decision."*

So the row's population is fully partitioned before the row exists. That is the definition of a
label rather than a situation.

---

## 5. The hardest objection: why `career.portfolio-work-samples` survived and this does not

This is the contrast that could have overturned the refusal, so I want it stated fairly. That row
is superficially the same shape — the maker's own work, no live client, `design_creative` source
files — and it is a **node**, not a refusal.

The difference is that *selection leaves traces in the bytes and not-having-a-client does not.*

Its own one_line is built on a purpose: work *"selected and framed to be SHOWN to someone"* (`career.portfolio-work-samples.json`). That
purpose is legible — a cover page with a name and a date range, sequenced spreads each with a
role line and a narrative, a curated `Selected Works.zip`, a cut reel. An extractor can see all of
it. `00` licenses purpose as a first-class facet exactly where files share a purpose and share no
content — its worked example is *"a purpose-defined packet, such as Chinese University Application
Materials, containing a transcript, ID, personal statement, resume, certificate, and research
abstract"* — and the test that makes the
licence usable is whether the purpose is *evidenced*. Showing is. Making-for-oneself is not.

Same maker, same absent client, opposite verdicts, and the discriminator is entirely evidential.
That is what convinced me the refusal is about this row and not about the whole family.

---

## 6. Alignment with the two landed code refusals

The dispatch asked me not to contradict `code.scratch-prototypes` and `code.software-project`, and
to say so explicitly if I diverged. I agree with both and diverge from one on the *reason*.

**Agreement with `code.scratch-prototypes` — the core.** Its first limb is the one I use: a row
defined as the complement of its schema's detection rule has no signal set, because *"A row
detected by the failure of its schema's own detection is the empty activation set wearing a
template id"*. That transfers without modification.

**Divergence, stated.** Its dimension argument does **not** transfer, and I do not borrow it.
Scratch code fails on dimensions because *no field is reachable* — no repository, no project value
without a root marker, only a flattenable `artifact_type`. This row fails the opposite way: the
fields are perfectly reachable. A personal project has a project name, a stage and an artifact
type as legibly as a commissioned one does. They are simply the *same* fields filled the *same*
way as the schema's default, plus one extra level `00` forbids. Scratch code has nothing to file
by; this row has plenty to file by, and none of it is "self-initiated." Two different arguments,
same verdict, neither weakened by the other.

**Agreement with `code.software-project`** — that row refuses because it *is* its schema's default
situation. Not my case: this row is not the creative schema's default either (the default is
whatever the schema's own template will be), it is the default plus an illegal level.

---

## 7. Files: eleven fixtures

Full observation/fact splits are on the node. What each one is *for*:

1. **`Untitled-3.psd`** — the id's most canonical file, and it activates nothing. Every
   observation it offers is universal (canvas dimensions, colour profile) or never-alone
   (extension, editor default name).
2. **`Nightwork_poster_A2_v7.ai` beside `Invoice_2026-014_Acme.pdf`** — **the fixture that decides
   the refusal.** The only evidence that could ever separate self-initiated from commissioned
   lives in a *different file*, and it is `creative.client-engagement`'s evidence, positively
   stated. Activation is per file version from that file's own evidence; this row would have to
   fire on a neighbour's *absent* document. Delete the invoice and nothing fires. P9 may still
   group the two — *"The graph does not automatically copy those missing facts onto sparse
   files"* — which is grouping, not activation.
3. **`IMG_9042.CR3`** — the roster hint made literal. A personal frame and a commissioned frame
   off one card, one body, one day-folder. Identical EXIF. `00` requires abstention where signals
   conflict: *"conflicting signals should lead to abstention rather than an invented
   classification."* Co-holds with `photos` on real camera evidence.
4. **`Nightwork_ch3_draft.docx`** — **collision fixture 1.** Looks like this row's; is
   `creative.book-manuscript`'s on chapter structure, which does not care about a publisher.
5. **`Portfolio_JYung_2026.pdf`** — **collision fixture 2**, and the §5 argument in one file. The
   near-neighbour that legitimately *is* a node.
6. **`sketchbook/2026-03-14 hand studies.jpg`** — the hobby half. Nothing about calling the maker
   a professional changes what the file offers an extractor. → One-Off Images.
7. **`Screenshot 2026-04-02 at 11.03.17.png` in `refs/`** — the look-alike this row would have
   swallowed: *someone else's* work. Depiction is not authorship. `00` places it in Reference
   Clips by name. A Personal Projects branch is a magnet for exactly this, and absorbing it is the
   fragmentation the residual library exists to prevent.
8. **`Nightwork_scene01.blend`** — the unreadable case, shared with every `creative.*` sibling and
   therefore not claimable.
9. **`personal_project_final.zip`** — the archive packet, manifest read without extraction. The
   closest thing to a positive signal this row will ever get — a human typed the words *personal
   project* — and it is precisely the never-alone, user-already-chose-this case. *"the system
   should not infer a purpose from their filename alone."*
10. **`Copyright registration — series 'Nightwork'.pdf`** — the one document genuinely produced
    only by self-initiated practice, and it *still* routes elsewhere: `creative.licensing-rights`
    by document type, co-holding with the `legal` safety schema, Independent Records unattached.
    If the strongest self-initiated-only artifact routes away, the row has no floor.
11. **`brushpack_grain_04.abr`** — the unattached-tooling half a "personal experiments" row would
    claim; `creative.stock-asset-library` already owns it.

---

## 8. Files considered and rejected as this row's evidence

- **A folder literally named `Personal Projects` / `Side Projects` / `Experiments`.** The most
  tempting false positive, because it looks like a labelled slot. It is not: `00` treats Personal
  Projects as a user-chosen root and a user's drag, and separately holds that *"The system learns
  from existing folders but must not silently reorganize them."* A folder name is a destination
  the user already chose, not a fact to re-derive from.
- **`logo_final_v3_FINAL.ai`-shaped names.** Version and finality tokens are the native dialect of
  *all* creative work; `creative.brand-identity`'s own hint is built around that filename. `00`
  names *"duplicate suffixes on unrelated files"* as an observed failure mode. Equally dense on
  both sides of the client line, so it discriminates neither.
- **EXIF `Artist` / PDF `Author` / XMP creator carrying the maker's name.** The author-as-collector
  signal, barred twice, and a token that matches nearly every file on a personal machine.
- **An organisation or venue name inside the artwork.** A speculative festival poster names the
  festival exactly as a commissioned one does. `00`'s institution rule generalises: *"A university
  name alone should not create a group because Columbia can appear as an authoring school, course
  provider, target institution, employer, research venue, or merely a cited organization."*
  Client, subject and mere depiction are the same three roles, and the pixels do not say which.
- **Same-folder or same-download-session company with other unclienteled work.** *"A session
  should never be treated as proof of topic"*, and the folder version is weaker still — the maker
  uses one workflow for both, which is the roster hint's own premise.
- **Bare four-digit tokens.** In this world overwhelmingly pixel dimensions, DPI, colour
  temperatures and export presets; `00` warns they are often *"numbers that look like years but
  are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."*
- **The absence of a licence or release beside the work.** Only the absence of *another row's*
  evidence; it cannot be borrowed as this row's presence.
- **A creative extension or `source_type: design_creative` alone.** `file_kind_plausible` is
  constitutionally never sufficient; *"treat the file extension as a routing signal rather than an
  assumption about meaning"*.
- **OCR of creative-looking text inside another format.** The bytes are an image or a message.

Ten of these are recorded as `never_alone` on the node, headed by the defining one — the absence
of a client — because a refused row's most useful residue is the list of things a future author
must not mistake for a signal.

---

## 9. Reciprocal boundaries — stated in both directions

Because the row is refused it authors **no edges** (following `code.scratch-prototypes` and
`business_operations.organisational-records`, which likewise leave `collides_with` and
`also_holds_with` empty and route only through `falls_through_to`). The boundaries are recorded
here and, where they are owed to another row, handed to R1c in the node's `open_question`.

| Neighbour | This row → neighbour | Neighbour → this row | Same fixture bytes |
|---|---|---|---|
| `creative.client-engagement` | never takes a file from it; a client name, brief, PO or invoice is decisive for the neighbour | takes everything with client evidence, and must **not** copy that evidence to neighbouring files in the same folder | `Nightwork_poster_A2_v7.ai` + `Invoice_2026-014_Acme.pdf` |
| `career.portfolio-work-samples` | never takes selected/framed material | takes it on cover, sequence, narrative, role line — evidence of *showing* | `Portfolio_JYung_2026.pdf` |
| `creative.book-manuscript` and the medium siblings | never takes material with medium-specific structure | take it on that structure, regardless of who commissioned it | `Nightwork_ch3_draft.docx` |
| `creative.stock-asset-library` | never takes reusable, project-less material | takes it by its own definition | `brushpack_grain_04.abr` |
| `photos` (schema) | never competes: camera EXIF is the photos schema's, and co-holding is normal | activates on real camera evidence; absence of EXIF proves nothing | `IMG_9042.CR3` |
| `code` (schema) | no contact — checked because the dispatch cited the code refusals; a creative practice's build scripts are `code`'s on structural markers, not this row's on authorship | — | — |

**Neighbours considered that got no edge, and why.** `career` (schema): the boundary that matters
is with its `portfolio-work-samples` template, argued above; a schema-level edge would say nothing
the template edge does not. `code`: the dispatch listed it as a must-consider neighbour, and I
looked — a designer's personal `.py` render script is `code`'s or nothing's, by repository
markers, and no evidence item is contested. `photos`: co-holding rather than colliding, and the
relevant competition (`creative.raw-photo-catalogue` vs `creative.commissioned-shoot`) is between
two other rows, neither of which is mine to author.

---

## 10. Self-verification

- `python3 -m json.tool` on the node: **parses.**
- Key set: identical to `code.scratch-prototypes.json` (the landed refusal in the same shape) —
  27 keys, same order.
- **Quotation check, mechanical.** Every quoted span in the node and in this memo was extracted by
  script and matched against its named source after normalising curly quotes and dashes — `00` for
  design quotations, and `CONNECTION.md` / `roster.json` / the two landed node files for the four
  spans attributed to those. **All found verbatim.** Four candidates failed an earlier pass and
  were re-attributed rather than kept: *"An empty set is a correct outcome, not a failure"* is
  CONNECTION.md's sentence, not `00`'s; *"belongs to no one project"* is
  `creative.stock-asset-library`'s roster `one_line_hint`; *"files are purpose-coherent but
  content-incoherent"* is the dispatch prompt's phrasing and was replaced with `00`'s own
  purpose-packet sentence; and the *"selected and framed to be SHOWN to someone"* span is
  `career.portfolio-work-samples.json`'s, now cited as such. No `00` quotation is attributed to
  `00` unless it greps out of `00`.
- `fields: []`, `proposed_fields: []`. **No canonical field key minted, none proposed.** The
  reasoning is on the node: the only field this row would want is `client`, and it wants its
  *absence*, which limb 1 rules out as a signal. Proposing a `commission_status` or
  `is_self_initiated` field would be minting a key whose sole purpose is to encode a negation the
  activation algorithm cannot read — the 574's mistake in field form.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: `design_creative` ×2, `image` ×3,
  `text_document` ×3, `archive` ×1, `opaque_binary` ×2. Checked against
  `src/evidence_shape/vocabulary.py`.
- Every `falls_through_to.residual_template` is one of `00`'s nine names.
- No numeric threshold, no confidence score, no handling class, no invented statistic.
- Edge ids: none authored (refused row). No id invented.
- Files written: exactly `creative.self-initiated-work.json` and this memo. Nothing else touched —
  no roster, no `src/`, no sibling node, no other agent's row.

---

## 11. NEEDS-JOSEPH

**NJ-CSIW-1 — dependency on NJ-R1a-1, recorded not resolved.** ROSTER.md §5 marks NJ-R1a-1 closed
in the sense J-IND closed it: the `creative` schema now exists. Its *field set* does not — the row
is `PLACEHOLDER SCHEMA … Writes NO field rows (PR-6; D1's deferral stands)`, and a later pass
decides whether it needs anything beyond `project`, `stage`, `artifact_type` and `client`. This
refusal does not depend on that question: limbs 1, 2 and the fourth ground are about signals, the
collector level, and `00`'s placement of Personal Projects, none of which a field set touches. It
is recorded because limb 2's second half is argued *conditionally* — even once the schema lands
those four fields, the order is the schema's default plus an illegal level. **The revisit
condition, stated so a later pass can test it:** if the creative schema gains a field whose value
genuinely differs between commissioned and self-initiated work *and* which is extractable from the
artifact rather than from a neighbouring invoice, this refusal should be re-opened. I could not
name such a field. The candidate everyone reaches for is `client`, and this row wants its absence.

**NJ-CSIW-2 — an unowned reciprocal, for R1c.** Refusing this row leaves `creative.client-engagement`
holding one half of a boundary whose other half no longer exists. That is correct, but it means
nothing on the roster records what happens to a creative file when client evidence is simply
*missing*. The answer — the medium sibling on its own evidence, then residual — belongs in that
row's `never_alone` list, together with the rule that its client evidence must not be copied onto
neighbouring files in the same folder (the `Nightwork_poster_A2_v7.ai` fixture). Recorded here and
in the node rather than authored there, because that row is another agent's.

**NJ-CSIW-3 — a schema-row edge, for R1c.** The `creative` schema row needs `falls_through_to`
covering Review Later, Reference Clips, One-Off Images, Independent Records and Unsupported or
Encrypted, because the unattached material this row was meant to catch now arrives at the schema's
own fallthrough.

**NJ-CSIW-4 — the one genuinely open product question this row surfaced, for R1c or R3.** Where
does the unattached working file of a *working professional* go — Review Later, or the medium
sibling with a null project? Both are defensible. Review Later is honest about the engine's
uncertainty, but a professional with hundreds of such files would swamp it, which is the
fragmentation `00` built the residual library to prevent. This is a question about residual volume
rather than about templates, and `00` arguably answers it already, in the sentence that closes the
residual library: the library *"must support user-defined residual areas such as Things to Read,
Ideas, Shopping Research, Memes, Travel, Receipts to Process, Clips, or Stuff to Sort, because
residual organization is highly personal and should not be dictated by a universal taxonomy."*
A user-defined **Ideas** area is `00`'s own answer to the thing this row was reaching for — and it
is a user-defined residual, not a roster node. If Joseph wants self-initiated work to be a
first-class place in the product, that is where it belongs, and it costs no template.
