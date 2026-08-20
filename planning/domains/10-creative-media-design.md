# Domain catalogue — creative, media, design and publishing

Supercategory: `creative-media-design`  
Slice: 10  
Entries: 46 — 0 design, 6 inference, 40 proposal  
Contract: [`_CONTRACT.md`](_CONTRACT.md) · Source of truth: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md)

## How to read this file

- **Double quotes are verbatim quotations** from the source of truth and nothing else. In the JSON they are written as curly quotations, which is the form `check.py` verifies by literal substring test; a quotation that does not appear in the source fails the build. Where a claim is mine rather than the design's it is written as plain prose with no quote marks.
- **Single quotes are pattern literals** — tokens a recogniser looks for in a document — following the convention in the contract's own worked example.
- `reliability_ceiling` uses §3.13's six states only. `direct` means a labeled field, a document title or explicit metadata. `validated` means a rule found a pattern **and** passed a context check, so every `validated` field has a matching `recognition.deterministic` line that could actually confirm it. `llm_supported` means the value needs language interpretation and therefore cannot be produced without the model route. `user_confirmed` means no rule and no model can reach it.
- `sensitivity` is §2.9's phrase `potentially sensitive` and nothing more. No handling class is assigned anywhere in this file; handling classes are P7's (§8.4).
- No thresholds, no scores, no counts, no durations. Digits appear only inside `example` values, which are data in the same way the contract's own `BUSIB 4300` is.

## Four findings that apply to the whole slice

**1 — The design gives this supercategory formats, and not one schema. Nothing here is `design` provenance.** §2.9 names the family precisely — "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — and §5.7 names "creative projects" and "client engagements" among the template library's eventual coverage. Both are real and neither is a domain: the first is a **routing fact** about file types and the second is a coverage aspiration. §3.15 is explicit that a domain is two things — "Each domain consists of two related definitions: a fact schema describing the information the system may extract from files in that domain, and a folder template describing the small subset of those facts that may become physical folder levels." — and the design supplies neither half for any entry below. Six entries are `inference` because they extend a domain the design does name (Photos, capture-based media, the research manuscript, §3.8's client role); the other forty are `proposal`. Reading §2.9's format list as a design warrant would be the exact failure the contract's rule 1 names.

**2 — Every recognition rule keyed on metadata *presence* fails on precisely the professional's files.** §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot" and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is overwhelmingly exports: delivered JPEGs, Figma PNGs, re-encoded MP4s, platform round-trips, flattened PDFs. All of them are stripped, and several of them land on exactly the dimensions and formats a screenshot hypothesis looks for. The consequence is structural rather than incidental — a stripped-plus-PNG test would classify a working photographer's entire delivered output, a product designer's whole board export, and every social asset ever re-downloaded as screenshots. Worse, the test *inverts* inside single domains: a scanned drawing carries camera EXIF while an exported digital painting carries none; site photographs carry EXIF while supplier-sent swatches do not; install shots carry EXIF while gallery-supplied artwork images do not. Every entry below therefore carries the absence of metadata in `never_alone`, and recognition rests on **positive structure** instead — layer names, linked-asset manifests, sidecar pairs, shared stems, contiguous frame runs, timecode, perceptual-hash variant sets. §2.6's own instruction governs the residue: "conflicting signals should lead to abstention rather than an invented classification".

**3 — Version families are the organising problem of this slice, and the design defines them only as a universal fact.** §3.1 makes "a member of a version family" a fact about a file; §3.11 lists it among "a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status"; §4.1 gives the rules engine "version stems" to work from. That is the whole of it. So this catalogue does **not** re-declare version family as a domain field. What each domain declares instead is its own **named iteration unit** — `round` in client work, `draft` and `revision colour` in writing, `cut` and `cut version` in post, `mix version` in music, `edition` and `state or proof` in printmaking, `revision` in drawing sets, `asset variant` in social. Two consequences are carried consistently: (a) **no entry lets a rule or a model decide which member is current.** `is current`, `is approved`, `is master` and `clearance state` are all capped at `user_confirmed`, because 'final' is a word rather than an ordinal, the highest version number is routinely an abandoned branch, and modification time is rewritten by a re-export of an *older* file. (b) **Cross-format exports are treated as derivatives, not siblings** — grouped with their source, kept out of the round history — which is a holding position and is raised as an open question on `studio.deliverable-handoff`.

**4 — This slice sits on both sides of §5.5's ordering boundary, and the split runs through single professions.** §5.5: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders. Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." Three entries take the exception (`photo.raw-catalogue`, `film.shoot-day-media`, `perf.performing-artist`) and forty-three do not, and the interesting cases are where one person's work lands on both sides: a photographer's RAW archive is time-first while their commissioned shoots are client-first; a production is project-first while its shoot-day media is day-first. Two near-misses are called out explicitly because they *look* temporal and are not — a fashion season code (`AW26`) is a collection label, and a podcast season and episode are an ordered sequence, so §3.10's warning about date-shaped strings applies rather than §5.5's exception.

## Index

| id | name | provenance | time first | sensitivity |
|---|---|---|---|---|
| `studio.client-engagement` | Client creative engagement (branch root) | inference | no | potentially sensitive |
| `studio.creative-brief` | Creative briefs and commissions | proposal | no | potentially sensitive |
| `studio.revision-round` | Critique, feedback and revision rounds | proposal | no | none |
| `studio.deliverable-handoff` | Deliverable handoff packages | proposal | no | potentially sensitive |
| `studio.licensing-rights` | Licensing, usage rights and releases | proposal | no | potentially sensitive |
| `studio.stock-asset-library` | Stock and reusable asset libraries | proposal | no | none |
| `studio.portfolio-showreel` | Portfolio, showreel and case studies | proposal | no | none |
| `studio.self-initiated-work` | Self-initiated professional creative practice | inference | no | none |
| `design.graphic-project` | Graphic design project | proposal | no | none |
| `design.brand-identity` | Brand identity system | proposal | no | none |
| `design.uiux-product` | UI and UX product design | proposal | no | none |
| `design.design-system-library` | Design system, component and token library | proposal | no | none |
| `design.illustration` | Illustration | proposal | no | none |
| `design.typeface-and-font` | Typefaces, fonts and type licences | proposal | no | none |
| `design.print-production` | Print production and prepress | proposal | no | none |
| `design.presentation-deck` | Presentation and pitch decks | proposal | no | none |
| `design.interior` | Interior design project | proposal | no | potentially sensitive |
| `design.architecture-visual` | Architectural visualisation and drawings | proposal | no | none |
| `design.fashion` | Fashion design collection | proposal | no | potentially sensitive |
| `photo.commissioned-shoot` | Commissioned photography shoot | inference | no | potentially sensitive |
| `photo.raw-catalogue` | RAW archive and photo catalogue | inference | yes | potentially sensitive |
| `film.production` | Film and video production | proposal | no | none |
| `film.shoot-day-media` | Shoot-day camera and sound media | inference | yes | potentially sensitive |
| `film.post-production` | Editing and post-production | proposal | no | none |
| `film.motion-graphics` | Animation and motion graphics | proposal | no | none |
| `cg.3d-asset` | 3D modelling, texturing and rendering | proposal | no | none |
| `game.art-asset` | Game art and interactive assets | proposal | no | none |
| `audio.music-session` | Music recording and production session | proposal | no | none |
| `audio.podcast-episode` | Podcast episode production | proposal | no | potentially sensitive |
| `audio.sound-design` | Sound design and audio post for picture | proposal | no | none |
| `write.manuscript` | Book-length manuscript | inference | no | none |
| `write.short-form` | Short-form writing | proposal | no | none |
| `write.screenplay` | Screenplay and script | proposal | no | none |
| `write.editing-pass` | Editing and proofreading passes | proposal | no | none |
| `write.translation` | Translation project | proposal | no | none |
| `news.reporting` | Journalism and reporting | proposal | no | potentially sensitive |
| `pub.title-production` | Publishing production of a title | proposal | no | none |
| `pub.submission-query` | Submissions, queries and representation | proposal | no | none |
| `pub.periodical-issue` | Periodical and issue production | proposal | no | none |
| `media.content-marketing` | Content marketing assets | proposal | no | none |
| `media.social-assets` | Social media assets | proposal | no | none |
| `media.ad-campaign` | Advertising campaign | proposal | no | none |
| `art.exhibition` | Exhibition and gallery work | proposal | no | none |
| `art.printmaking` | Printmaking, editions and physical craft | proposal | no | none |
| `perf.theatre-production` | Theatre and live performance production | proposal | no | none |
| `perf.performing-artist` | A performer's own practice archive | proposal | yes | none |

---

## `studio.client-engagement` — Client creative engagement (branch root)

Creative work made for a paying client under a brief, where the client and the job — not the file format — are what the files have in common.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** §5.7 names "client engagements" and "creative projects" in the template library the product should eventually carry; the coverage list it belongs to is "financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections". The NAME is design-given; no design sentence gives this domain a schema. §3.8 supplies the one field pair that is design-given: "A consulting document may mention the author’s firm and the client organization." and "The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client."

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Acme Foods | `validated` | §3.8 names the role directly — "The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client." — so `client` is a distinct facet from the studio or freelancer producing the work, not a second instance of one organisation field. A rule reaches it from a labeled contract party, a brief header or a curated parent folder, which is §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `our_firm` | string | Yung Studio | `validated` | The other half of §3.8's pair. It is carried so the client field stays clean, and it is deliberately NOT a folder dimension: §3.8 "It should avoid using authorship or creator identity as a destination dimension." and "A folder should not become a collection point for everything produced by the same person or organization." |
| `project` | string | Spring campaign | `llm_supported` | One client commissions many jobs and a job outlives any single file. §3.11 already uses `project` in the Research row; this is the same field under a different active schema, which §3.11 permits: "One file may hold facts from more than one domain without losing information." |
| `engagement` | string | MSA 2026 — SOW 3 | `validated` | The contractual container a project sits in. It is the fact that distinguishes two projects for the same client that were sold separately, and it is read from a labeled agreement reference rather than inferred |
| `deliverable` | string | Key visual | `llm_supported` | The named thing being handed over. It is the work-type analogue for this branch and the level at which a version family is actually anchored |
| `round` | string | R2 | `validated` | The feedback iteration. A labeled round marker in a filename or a presentation title is a pattern plus a context check, so §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" is reachable; a bare number is not |
| `engagement status` | string | delivered | `llm_supported` | Live, delivered, archived or abandoned. A search and explanation field rather than a folder dimension — §3.11 allows "Each domain activates only a small set of relevant fields, usually three to six that may help build a future folder proposal and several additional fields used only for search, privacy protection, explanation, or later review." |
| `embargo state` | string | unreleased | `user_confirmed` | Whether the work has been made public. Only a person knows; nothing in the file says it. It is carried as a fact so the sensitivity question can be asked, and no handling class is set here — that is P7's |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a labeled agreement or brief field — 'Client:' | 'Prepared for' | 'Scope of Work' | 'Statement of Work' | 'Purchase Order' — carrying an organisation name matched on a word boundary. §3.7: "It should use word-boundary matching rather than substring matching."
- a curated parent folder whose name matches an organisation already established as a client by a labeled agreement field elsewhere in the corpus
- a round or revision marker ('R1' | 'Round 2' | 'rev' | 'v') co-occurring with a client name and a deliverable term in one filename

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a working file whose only client signal is an organisation name inside artwork — a logo placed on a mock-up, a brand name set in a headline — which is content, not a party
- an email or message export that establishes an engagement in prose ('happy to go ahead with the two concepts we discussed') with no labeled field anywhere
- distinguishing a client's own supplied material from work produced for the client, where both sit in one folder

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- an organisation name on its own. §4.9's stop rules apply directly: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge". A brand appears as a client, an employer, a competitor in a deck, a stock-photo watermark and a font vendor
- the authoring application recorded in software metadata. One application serves client work, personal work, coursework and a hobby in the same corpus
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- a folder named for a person or company. §5.7 makes the engine validate that a template does not "use an author or organization merely as a collector"

### Work types

`brief`, `concept`, `working file`, `presentation`, `deliverable export`, `invoice reference`, `handover note`

### Grouping reasons (§4)

- one client's one project across every discipline that touched it — §3.9: "The documents are content-incoherent but purpose-coherent."
- one deliverable across its rounds, working files and exports — §4.2: "files linked by duplicate or version relationships"
- one engagement across the brief, the rounds and the handover, which is a purpose group in §3.9's sense rather than a topic group

### Template (§5)

`client → project → deliverable → round`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a round marked R2 is meaningless until the deliverable is known, and a deliverable named 'Key visual' is meaningless until the project is. §5.5 also: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.", which keeps the delivery date out of the spine. The client leads despite §5.7's warning about a template that would "use an author or organization merely as a collector", because an engagement is not merely a collector: the contract, the brief, the rights and the approvals are all scoped to the client, so the client dimension carries meaning rather than just gathering files

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| studio.self-initiated-work | identical tools, identical formats, identical filenames. The only distinguishing signal is external: a client party in an agreement, a brief, or an invoice reference. Absent that, the file is not weakly client work — it is unclassified between the two | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| career.consulting-engagement | the career catalogue owns the commercial relationship — proposal, contract, rate, invoice, engagement close. This domain owns the work product made inside it. One folder holds both and the split is by document role, not by client | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| career.freelance-contract-work | same boundary. A freelance contract is a career record; the artwork produced under it is this domain. §3.11 permits the folder holding both to carry both sets of facts | §3.11: "One file may hold facts from more than one domain without losing information." |
| pers.creative-project | the personal catalogue owns work made for its own sake. The presence of a paying client is the entire distinction and it is never visible in the artwork | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase and nothing more. Engagement folders routinely carry the correspondence and contact material §2.9 already marks — "while treating addresses and message content as potentially sensitive" — and unreleased work sits beside it. The handling CLASS is P7's (§8.4) and is not set here.

### Open question — Joseph's call, unresolved

> Does Joseph want client creative work as its own top-level branch, or as a dimension inside one Creative branch that also holds personal work? §5.1's example canvas lists "Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material" and names neither. The two shapes are not cosmetic: client-first puts a designer's personal illustration three levels from their commissioned illustration, while a single Creative branch with a client dimension keeps the craft together and splits the business. This catalogue supplies both shapes (`studio.client-engagement` and `studio.self-initiated-work` are deliberately parallel) and resolves neither, because it decides someone's real filing structure. SECOND: is §2.9's binary `potentially sensitive` meant to carry contractual confidentiality — an unreleased campaign, an embargoed identity, a signed NDA — or only personal sensitivity? The design's uses of the phrase are all personal-data uses. Marking embargoed client work with the same flag as a passport is either right or badly wrong, and the answer belongs to Joseph and P7, not here.

---

## `studio.creative-brief` — Creative briefs and commissions

The document that starts a piece of creative work and states what it must do, for whom, by when.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names briefs or commissions. Proposed because a brief is the anchor §4.2 asks for — "A seed may be a strongly identified file, a validated shared fact, a structural family, or a user-created starting point." — for an entire engagement: it is usually the only file in a creative folder that states the client, the deliverable list and the deadline in labeled prose.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Acme Foods | `validated` | §3.8's client role, read here from a labeled 'Client' or 'Prepared for' field, which is §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `brief type` | string | creative brief | `validated` | Creative brief, design brief, commission agreement, art-direction note, request for proposal. A document-title match, which §3.13 makes "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." when it is the title itself |
| `deliverable list` | list of strings | logo; stationery; brand guidelines | `llm_supported` | The brief's own enumeration of what is owed. It is the field that lets a later folder be checked against what was actually commissioned, and it needs prose interpretation because briefs enumerate in sentences as often as in bullets |
| `deadline` | date | 2026-04-30 | `direct` | §3.10 requires the explicit-regex path and forbids fuzzy parsing, because filenames and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values". A labeled 'Due' or 'Deadline' field is §3.13's "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `commissioner role` | string | art director | `llm_supported` | §3.8 requires roles that share an entity type to be separate facets. The person who commissions, the person who approves and the person who pays are frequently three people and one organisation |
| `fee basis` | string | fixed fee | `llm_supported` | Fixed fee, day rate, licence-only, royalty. A search and explanation field; the money record itself belongs to the finance catalogue |
| `usage scope` | string | UK, digital, one year | `llm_supported` | What the client is buying the right to do. It is stated in the brief long before any licence document exists, and it is the field that makes `studio.licensing-rights` reachable from a brief |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document title or heading matching 'creative brief' | 'design brief' | 'commission' | 'artwork request' | 'brief —' co-occurring with a client or project name
- a labeled deliverables or scope section ('Deliverables' | 'Scope' | 'What we need') beside a labeled date field

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an email or message thread that IS the brief — the most common real form — where the requirements are in prose and no section is labeled
- distinguishing a brief the studio received from a brief the studio wrote for a subcontractor, which §3.8 makes two different role assignments of one document type

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the word 'brief' — it is also a legal brief, a press brief and a briefing deck. §3.7: "It should use word-boundary matching rather than substring matching."
- a deadline-shaped date. §3.10 is explicit that documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- a deliverables list, which appears identically in a proposal, an invoice and a handover note

### Work types

`creative brief`, `commission agreement`, `artwork request`, `art-direction note`, `brief response`, `scope change`

### Grouping reasons (§4)

- one brief with the work it commissioned — a purpose group in §3.9's sense, since the brief and the artwork share no content at all
- a brief with its revisions and its scope changes, which are a version family

### Template (§5)

`client → project → brief`

Time first: **no**

A brief has no meaning outside its project and no project has meaning outside its client, which is §5.5's "a parent dimension should provide the context required to understand the child". The brief is the leaf rather than a level of its own in most engagements; §5.7 makes the engine reject a template that would "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.client-proposal | a proposal is written BY the creative to win the work; a brief is written FOR the creative to define it. The two documents look alike, share vocabulary and often share a template. The distinguishing signal is direction of authorship, which §3.8 makes a role question | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.revision-round | a scope change mid-project reads as both a new brief and a feedback round. It is a brief when it changes what is owed and a round when it changes only what has been made | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| legal.contracts | a commission agreement is a contract and a brief at once; the finance and legal catalogue owns it as an instrument, this domain owns it as the work's anchor | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. A brief for unreleased work states what a client intends to launch and when, and briefs commonly carry the contact material §2.9 already treats as "while treating addresses and message content as potentially sensitive". No handling class is set; that is P7's (§8.4).

---

## `studio.revision-round` — Critique, feedback and revision rounds

The iteration record of one piece of creative work — what was shown, what came back, and what changed.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names revision rounds. Proposed because §3.1 makes "a member of a version family" a fact about a file, and §4.1 supplies "version stems" among the hard facts a rules engine extracts, but neither names the ROUND — the named, dated, client-facing iteration — which is the unit creative work actually moves in.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `round` | string | R2 | `validated` | The iteration label. A round marker beside a deliverable term is a pattern plus a context check, which is §3.13's "A validated fact was found by a deterministic rule and passed contextual checks". A bare digit is not, and §3.10 explains why |
| `deliverable` | string | Homepage | `llm_supported` | The thing being revised. A round attaches to a deliverable, never to a project as a whole — two deliverables in one project are on different rounds at the same time |
| `feedback source` | string | client | `llm_supported` | §3.8's role separation. Client feedback, internal critique, art-director notes and peer review are the same document type from four different parties, and they are not interchangeable |
| `decision` | string | approved with changes | `llm_supported` | Approved, approved with changes, rejected, superseded. It is the field that answers which member of a version family is current, and it can only come from language |
| `round date` | date | 2026-03-11 | `direct` | When the round was presented. Read from a labeled date on the presentation or the feedback document, never from mtime, which a re-export rewrites |
| `is current` | boolean-like string | superseded | `user_confirmed` | Deliberately capped at §3.13's "A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user.". No rule and no model can establish which member of a version family is current: 'final' is a word rather than an ordinal, a later mtime often belongs to an older re-export, and the highest version number is frequently an abandoned branch |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a round marker ('R1' | 'Round 2' | 'rev2' | 'v3' | 'WIP') in a filename co-occurring with a deliverable term and a stable version stem shared with sibling files
- a version stem shared across files of differing extensions in one directory. §4.1 names "document type, course codes, dates, target institutions, project identifiers, duplicate relationships, version stems, capture metadata, filename patterns, and structural links", and the stem is the deterministic half of this domain
- a document whose title matches 'feedback' | 'comments' | 'amends' | 'mark-up' | 'review notes' beside a deliverable name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a marked-up PDF or an annotated image where the feedback is handwriting or comment anchors rather than text
- a message thread carrying the approval — the single most common place a creative approval actually lives
- deciding whether two files with different stems are the same deliverable renamed or two different deliverables

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- modification time. A re-export, a font substitution or a colour-profile conversion rewrites it without changing the round
- the highest version number present. Abandoned branches routinely carry the highest number in the folder

### Work types

`presentation`, `feedback document`, `marked-up proof`, `amends list`, `approval note`, `comparison sheet`

### Grouping reasons (§4)

- one deliverable across all its rounds — the version family of §3.1, anchored on a shared stem
- one round across the deck shown, the feedback returned and the files changed because of it
- §4.2's "files linked by duplicate or version relationships" is the retrieval mechanism this domain exists to make legible

### Template (§5)

`deliverable → round`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A round is the child of a deliverable and of nothing else. This template is deliberately shallow — rounds are usually better expressed as a version family within one folder than as folders, and §5.7 makes the engine reject a template that would "create meaningless one-child levels", which a per-round folder does whenever a deliverable was approved first time

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| studio.deliverable-handoff | the approved round and the delivered file are usually the same artwork in two formats. The handoff is defined by the export and the recipient, not by the approval | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| write.editing-pass | an editorial pass on a manuscript is a revision round by another name, with a different vocabulary (structural, line, copy, proof) and a different unit (the whole text, not a deliverable) | §3.11: "It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible." |
| soft.code-review-artifact | a design review on a product screen and a code review on its implementation attach to the same feature and the same sprint; the artifact type is what separates them | §3.11: "Code files may use project, repository, programming language, and artifact type." |

### Sensitivity

`none` — No design sentence puts iteration records in §2.9's "and potentially sensitive" territory. Where the work itself is unreleased, the marking belongs on the engagement rather than being repeated on every round.

---

## `studio.deliverable-handoff` — Deliverable handoff packages

The exported, packaged, format-specified files actually given to a client, and the note that says what they are.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names handover packages. Proposed because §2.9's design and creative extractor — "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — describes the working file, while the handoff is what the working file was flattened INTO, and the design nowhere relates the two.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `deliverable` | string | Logo suite | `llm_supported` | The named thing handed over. It is the anchor the exports hang from and is usually stated only in the handover note |
| `client` | string | Acme Foods | `validated` | §3.8's client role, inherited from the engagement and confirmed by a labeled recipient field on the handover note |
| `export format set` | list of strings | AI; EPS; SVG; PNG; PDF | `direct` | §2.9 makes format a directly observed property: "The engine should treat the file extension as a routing signal rather than an assumption about meaning", and the extension plus the real signature are read, not inferred. The SET is what makes a folder a handoff rather than a working folder |
| `colour space` | string | CMYK | `direct` | §2.6 has the image extractor store colour information among the properties it records for every supported image, so an embedded ICC profile or a labeled export preset is a direct read. It is the field that separates a print handoff from a screen handoff, and §3.13 makes a labeled metadata slot "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `handoff date` | date | 2026-05-02 | `direct` | Read from a labeled date on the transmittal note. §3.10 forbids fuzzy parsing of any other date-shaped string on the package |
| `recipient` | string | Acme brand team | `llm_supported` | §3.8: the party who receives is not always the party who commissioned or the party who pays. Kept as a fact and never as a folder dimension |
| `source file reference` | string | acme-logo-master.ai | `possible` | Which working file an export came from. §2.9 has the design extractor yield "linked asset names", but a flattened export usually loses the link entirely, so this is capped at §3.13's "A possible fact is a useful but insufficient clue" |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a directory containing several files that share one normalised filename stem across different extensions, at least one of which is a lossless working format and at least one a delivery format
- a document titled 'handover' | 'delivery note' | 'asset list' | 'read me' | 'artwork release' beside that set
- an archive whose manifest shows that stem-plus-format shape. §2.9: "Compressed archives should yield their manifests without extraction"

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a folder of exports with no note, where only the format mix and the filenames suggest that this was a delivery rather than a working directory
- distinguishing a delivery package from a backup or a portfolio copy of the same files

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- a ZIP archive. §2.9 has archives read "Compressed archives should yield their manifests without extraction", and the manifest, not the container, carries whatever signal exists
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`export set`, `handover note`, `asset list`, `packaged archive`, `transmittal email`, `specification sheet`

### Grouping reasons (§4)

- one deliverable across every format it was exported to — a duplicate-or-version relationship in §4.2's sense
- one handoff across its exports, its note and the message that sent it
- an export with the working file it came from, where a link survives

### Template (§5)

`client → project → deliverable → handoff`

Time first: **no**

Delivery is the terminal state of a deliverable, so it belongs beneath it rather than beside it: §5.5's "a parent dimension should provide the context required to understand the child". A date level is deliberately absent — §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| studio.revision-round | the approved round's artwork and the delivered export are the same image. Only the format set and a recipient distinguish them | §4.2: "files linked by duplicate or version relationships" |
| studio.portfolio-showreel | the same exports are copied into a portfolio months later. The copy is identical and only its parent folder and purpose differ | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| studio.stock-asset-library | an asset pack sold as a product and an asset pack delivered to one client have identical shape; the difference is whether a client party exists | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. A handoff package for unreleased work is the complete artwork of something not yet public, and transmittal notes carry the contact material §2.9 marks as "while treating addresses and message content as potentially sensitive". Handling classes are P7's (§8.4) and none is set.

### Open question — Joseph's call, unresolved

> Is a cross-format export a member of the same version family as its source file, a member of the duplicate family, or neither? §3.11 names both "a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status" as universal facts and defines neither for this case. It matters everywhere in this supercategory: a logo delivered as AI, EPS, SVG, PDF and three PNG sizes is one work in eight files, none of which is a copy of another and all of which share a stem. If they are one version family, every creative folder collapses into a handful of families and rounds become invisible inside them. If they are eight unrelated files, the corpus looks eight times larger than it is. This catalogue treats an export as a DERIVATIVE — grouped with its source, not folded into its round history — but that is a holding position and the universal fact definition is not this catalogue's to write.

---

## `studio.licensing-rights` — Licensing, usage rights and releases

The documents that say who may use a piece of creative work, for what, where and for how long — and the releases that made it lawful to make.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names creative licensing. Proposed because §3.8's role separation is unusually load-bearing here — "The system must separate roles that happen to contain the same entity type." — a single licence names an author, a licensor, a licensee and a depicted subject, and collapsing any two of them produces a confident, wrong filing path.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `licensed work` | string | Untitled No. 4 | `llm_supported` | The work the licence attaches to. It is named in prose in the licence and rarely matches the filename of the artwork it governs |
| `licensor` | string | Yung Studio | `validated` | §3.8: "The agent should model these as distinct facets, such as authored_by and target_school, or our_firm and client.". The licensor is the party granting; on a stock purchase it is a company, on a commission it is the creative |
| `licensee` | string | Acme Foods | `validated` | The party receiving. §3.8 requires it to be a distinct facet from the licensor even though both hold organisation names |
| `usage scope` | string | worldwide, digital, non-exclusive | `llm_supported` | Territory, media, exclusivity and duration, which arrive as a sentence rather than as fields. It is the fact that decides whether a later reuse is permitted, and it is why the domain exists |
| `licence term` | date range | 2026-01-01 to 2027-12-31 | `direct` | Read from labeled term fields. §3.10 requires explicit patterns; a term stated as 'two years from first use' is not a date and must stay unresolved rather than being computed |
| `release type` | string | model release | `validated` | Model release, property release, minor's release, talent agreement. A document-title match with a signature block beside it |
| `depicted subject` | string |  | `user_confirmed` | §3.8 again: the person depicted is not the author and not the client. §2.9 already requires contact-shaped data to be "but should normally be privacy-protected rather than used to create folder proposals", and this field inherits that restraint — it is carried for search and never becomes a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document title matching 'licence' | 'license agreement' | 'model release' | 'property release' | 'usage rights' | 'royalty-free' beside a signature or grant clause
- a labeled grant clause ('hereby grants' | 'Territory:' | 'Media:' | 'Exclusivity:' | 'Term:') co-occurring with a named work
- a stock-provider invoice or licence certificate carrying an asset identifier and a labeled licence type

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- usage rights stated in a paragraph of an engagement contract rather than in a standalone licence — the normal case for commissioned work
- deciding whether a release covers the shoot, one image, or a campaign, which is stated in prose and changes what may be filed with what

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the word 'rights' | 'copyright'. A copyright line sits in the footer of essentially every creative file
- a signature block, which is common to every agreement in the corpus
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"

### Work types

`licence agreement`, `model release`, `property release`, `usage grant`, `stock licence certificate`, `rights reversion notice`

### Grouping reasons (§4)

- one work with every licence granted over it
- one shoot with the releases that cover the people and places in it — a purpose group, since the release and the photograph share no content
- one licensee across the works they hold rights in

### Template (§5)

`work or project → licence`

Time first: **no**

A licence is meaningless without the work it governs, which is §5.5's "a parent dimension should provide the context required to understand the child". Licensor and licensee are deliberately NOT levels: §3.8 "A folder should not become a collection point for everything produced by the same person or organization.", and a licensee folder is exactly that collector

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| legal.ip-registration | a registration establishes ownership with a registry; a licence disposes of it privately. Both carry a work title and a rights vocabulary and the finance-legal catalogue owns the registry side | §3.11: "One file may hold facts from more than one domain without losing information." |
| legal.contracts | a licence IS a contract. This domain exists because the licence is retrieved from the work, not from the counterparty, and a general contracts branch loses that path | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| studio.stock-asset-library | a stock licence certificate is a licence document that belongs to an inbound asset rather than to an outbound work; the direction of the grant is the only distinguishing signal | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. Releases carry a named individual's signature, and often a home address or a guardian's details, which is precisely the contact-shaped material §2.9 says should be "but should normally be privacy-protected rather than used to create folder proposals". No handling class is set; that is P7's (§8.4).

---

## `studio.stock-asset-library` — Stock and reusable asset libraries

Bought, downloaded or self-made material kept to be used again — textures, footage, mockups, icons, brushes, presets, loops — which belongs to no one project.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names asset libraries. Proposed because they break the design's central assumption for this stage: §5.5 orders branches by "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.", and a reusable asset has no project, no subject and no time — the fields the whole template mechanism is built on are simply absent.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `asset type` | string | texture | `validated` | Texture, mockup, icon set, brush, preset, LUT, sound effect, font, 3D model. It is the only dimension a reusable asset reliably has, confirmed from the real format plus a directory manifest |
| `provider` | string |  | `validated` | Where it came from. §3.8 keeps it distinct from the client and from the author — a stock provider is neither — and it is read from a licence certificate or a provider-shaped directory name |
| `licence class` | string | royalty-free | `llm_supported` | Royalty-free, rights-managed, editorial-only, personal-use-only, purchased-outright. It determines whether the asset may be used in client work at all, which is the question the library exists to answer |
| `asset identifier` | string |  | `direct` | The provider's own id, usually embedded in the filename at download. It is the only reliable link back to a licence certificate and is read literally — §2.8: "The system must retain raw evidence separately from normalized values." |
| `collection` | string |  | `user_confirmed` | The user's own grouping of a library. Only a person defines it; nothing in the files says which textures belong together |
| `acquisition date` | date | 2026-02-08 | `possible` | Capped at §3.13's "A possible fact is a useful but insufficient clue" because it is normally filesystem mtime, which a copy or a re-download rewrites; a labeled purchase date on a certificate reaches higher, but the asset file itself does not carry one |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a directory of many files of one format sharing a provider-shaped identifier stem and carrying no project-, client- or date-bearing sibling
- a licence certificate or read-me from a known provider co-occurring with assets whose filenames contain its identifier
- an application's own asset-library directory layout — a presets, brushes, LUTs or plug-in content directory identified by its manifest rather than by its name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- distinguishing a downloaded reference image kept for inspiration from a licensed asset intended for use, which is a purpose question with no observable difference
- a self-made asset promoted into the library from a past project, where the only signal is that the same file also exists inside a project folder

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- presence in a Downloads directory. §3.9: "A session should never be treated as proof of topic"
- a large directory of images. That describes a photo archive, a scan batch and a screenshot pile equally well

### Work types

`stock image`, `stock footage`, `texture`, `mockup template`, `icon set`, `brush or preset`, `font file`, `3D model`, `audio loop`, `licence certificate`

### Grouping reasons (§4)

- one provider's purchase with its licence certificate — a purpose group, since the certificate and the asset share no content
- one asset pack as distributed, kept intact rather than dispersed
- identical assets appearing in several projects, which §4.2's "files linked by duplicate or version relationships" links as duplicates rather than as copies to be resolved

### Template (§5)

`asset type → collection`

Time first: **no**

A reusable asset has no project and no subject, so §5.5's normal ordering has nothing to order by; asset type is the only dimension every member has. This is one of the branches §5.9 exists for: "It should recommend flattening when a dimension does not materially improve retrieval."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.typeface-and-font | a font is a licensed reusable asset AND a designed work. The library owns the licensed copy; the type-design domain owns the source and the production files | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.licensing-rights | a stock licence certificate belongs to both: it is a licence document, and it is the asset's provenance record | §3.11: "One file may hold facts from more than one domain without losing information." |
| pers.hobby-collection | a personal collection of downloaded material and a professional asset library are the same directory shape; the licence class is the only real distinguishing fact and it is usually absent | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — Nothing in §2.9 puts purchased reusable assets in "and potentially sensitive" territory. Where a library contains a client's confidential material it has been misfiled, and the marking belongs on the engagement.

---

## `studio.portfolio-showreel` — Portfolio, showreel and case studies

Copies of finished work assembled to be shown to someone else — a portfolio site, a PDF book, a reel, a case study.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names a portfolio in the creative sense. Proposed because it is the clearest case in this slice of §3.9's distinction: "Topic answers what a file is about, while purpose answers what the file was for." — a portfolio file is byte-identical to the deliverable it was copied from and differs only in what it is for.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `portfolio artefact` | string | 2026 folio | `user_confirmed` | Which portfolio this belongs to. A person assembles a portfolio; the corpus contains no statement of it |
| `showcased work` | string | Acme rebrand | `llm_supported` | The project being shown. It links the portfolio copy back to the engagement, which is the fact that makes a duplicate explainable rather than a mess |
| `case study role` | string | art direction | `llm_supported` | §3.8: on collaborative work the portfolio claim is a role claim, and the role differs per contributor for one identical artefact |
| `audience` | string | agency pitch | `llm_supported` | A folio sent for a job, a client pitch, an award entry or a grant application is a different edit of the same material. It is the purpose fact §3.9 makes first-class |
| `showreel cut` | string | 90s cut | `validated` | Reels exist in several durations at once. §2.9 has audio and video yield "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present", so duration is directly observed and a labeled cut name is a rule-confirmed pattern over it |
| `clearance state` | string | cleared | `user_confirmed` | Whether the client has permitted the work to be shown. Only a person knows, and it is the single most common reason a portfolio item must be withdrawn |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a file whose content hash matches a file already established as a deliverable, sitting under a differently-named parent. §2.6: "Exact hashes and perceptual hashes can identify duplicates and near-duplicates.", which extends the same test to a re-exported copy
- a document titled 'portfolio' | 'folio' | 'case study' | 'showreel' | 'selected work' containing several project names
- a directory whose members are single representative files drawn from several unrelated projects

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a case-study document that narrates a project rather than naming it, where the client is described but not identified
- deciding whether an edited compilation is a showreel or a client deliverable, since both are a single video file with no distinguishing metadata

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- being a duplicate. A duplicate is equally a backup, an export, a stock copy or an accident — §4.9's stop rules apply
- the authoring application recorded in software metadata. One application serves client work, personal work, coursework and a hobby in the same corpus
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`portfolio PDF`, `case study`, `showreel`, `selected-works export`, `website asset set`, `award entry`

### Grouping reasons (§4)

- one portfolio artefact with every work in it — purpose-coherent and content-incoherent in §3.9's exact sense
- one showcased project with the portfolio copies made from it, which keeps the duplicate explainable
- one showreel with its alternate cuts, a version family in §3.1's sense

### Template (§5)

`portfolio artefact → showcased work`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Nothing else in this domain has meaning above the portfolio it was assembled for. Time is excluded as a level even though folios are dated, per §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| career.portfolio | the career catalogue owns the portfolio as a job-application artefact — sent with a CV, tailored to a posting. This domain owns it as a body of creative work maintained continuously. One PDF is frequently both, and the distinguishing signal is whether a job application exists around it | §3.9: "The documents are content-incoherent but purpose-coherent." |
| studio.deliverable-handoff | byte-identical files. Only the parent context and the audience separate them | §4.9: "A file may validly belong to more than one accepted group" |
| acad.arts-jury-portfolio | a portfolio submitted for a jury, a degree show or an admissions review is an academic submission carrying the same artwork | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — A portfolio is assembled to be shown. Where an item is uncleared the concern is contractual rather than §2.9's "and potentially sensitive", and this catalogue does not stretch that phrase to cover it — see the open question on `studio.client-engagement`.

---

## `studio.self-initiated-work` — Self-initiated professional creative practice

Work a professional makes with no client — experiments, personal projects, speculative pieces — using the same tools, formats and filenames as their paid work.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends §5.7's named "financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections" coverage of creative projects to the professional case. The NAME is design-given; the fields are not. It exists as a separate entry from the personal catalogue's `pers.creative-project` because the professional case carries an eventual commercial intent that changes what must be tracked — rights, clearance and portfolio use.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string |  | `user_confirmed` | The work being made. Only a person names a self-initiated project; there is no brief, no client and no contract to read it from |
| `medium` | string |  | `validated` | Confirmed from the real formats present rather than asserted from a filename. §2.9 makes the format observable: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |
| `stage` | string | sketch | `llm_supported` | §3.11 names `stage` in the Research row — "Research files may use project, stage, artifact type, lab, and venue." — and self-initiated creative work has the same shape: sketch, study, work in progress, finished, shown |
| `intent` | string | speculative client pitch | `user_confirmed` | Practice, portfolio piece, competition entry, product to sell, speculative pitch. It is the purpose fact of §3.9 and the reason this is not simply a hobby |
| `rights held` | string | sole author | `user_confirmed` | Whether the maker holds the rights outright — usually yes, and usually the reason the work can be shown. Contrast the commissioned case where §3.8's licensor and licensee are different parties |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- creative working files in a directory that contains no client party, no brief, no invoice reference and no agreement — an absence test, and stated as one
- a project directory whose sibling directories are all established as client engagements, and which alone has no engagement anchor

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a piece that later became client work, where the same files exist on both sides of a commission
- deciding whether an experiment is professional practice or a private hobby, which is a claim about the person rather than about the file

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of a client. Absence is not evidence: the brief may simply be in an email account the corpus does not contain. §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"
- the authoring application recorded in software metadata. One application serves client work, personal work, coursework and a hobby in the same corpus
- a folder named 'personal' | 'me' | 'own'. It is a strong clue and a §3.13 "A possible fact is a useful but insufficient clue" at most, since these names also appear inside client folders

### Work types

`sketch`, `study`, `working file`, `finished piece`, `competition entry`, `experiment`

### Grouping reasons (§4)

- one self-initiated project across its stages and formats
- one piece across its version family — §3.1's "a member of a version family"
- a body of experiments in one technique, which the maker names and the engine cannot

### Template (§5)

`project → stage`

Time first: **no**

§5.5's "a parent dimension should provide the context required to understand the child" with the shallowest depth this slice contains: self-initiated work usually has no client, no round and no deliverable, and §5.7 makes the engine reject a template that would "create meaningless one-child levels". §5.9's "It should recommend flattening when a dimension does not materially improve retrieval." applies to this branch more than to any other here

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.creative-project | the same person, the same tools, the same formats. The personal catalogue owns work made for its own sake; this owns work made without a client but with professional intent. The distinction is the maker's, not the file's, and this catalogue does not pretend a rule can find it | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| studio.client-engagement | a speculative pitch becomes client work the moment it is accepted, with no change to any file | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.portfolio-showreel | self-initiated work exists largely to be shown, so it appears in the portfolio almost by definition | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — No design sentence puts a maker's own unshown work in §2.9's "and potentially sensitive" category, and this catalogue does not invent one.

---

## `design.graphic-project` — Graphic design project

A piece of two-dimensional design work — a poster, a layout, a piece of collateral — from artwork file to press-ready or screen-ready export.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names graphic design as a domain. §2.9 names the family and what may be read from it: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — that is a FORMAT family and a routing fact, not a schema, and this entry supplies the schema the design does not.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Spring poster series | `llm_supported` | The design job. §3.11 already uses `project` in the Research row and §3.11 permits one field under several active schemas: "One file may hold facts from more than one domain without losing information." |
| `artefact` | string | A2 poster | `llm_supported` | The designed thing. It is this domain's work-type analogue and the level a version family anchors on |
| `output medium` | string | print | `validated` | Print, screen, environmental, packaging. Confirmed by a rule from colour space, bleed marks or pixel dimensions rather than asserted, which is §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `canvas dimensions` | string | 420 x 594 mm | `direct` | §2.9 has the design extractor yield "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text", so canvas properties are directly observed. Kept for search and explanation, never as a folder level |
| `linked assets` | list of strings | acme-logo.ai; hero-shot.tif | `direct` | §2.9 names "linked asset names" among what a design file yields. It is the strongest structural edge this slice has: a placed-link graph relates a layout to its photography, its logo and its fonts without any language interpretation |
| `round` | string | R2 | `validated` | Shared with `studio.revision-round`; carried here so the working file can be ordered inside its family without the round document being present |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a layout or artwork file signature (PSD, AI, INDD, AFDESIGN, SVG) whose extracted properties include artboards or layers, co-occurring with a project- or client-shaped parent folder. §2.9: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text"
- a placed-link manifest naming assets that themselves exist in the corpus — a structural relationship, not a similarity one
- an export carrying crop marks, bleed or a CMYK profile beside a source file with a shared normalised stem

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a flattened PDF or PNG with no layers, no links and a filename like 'poster3.pdf', where the only signal is what the artwork depicts
- distinguishing a design artefact from a photograph of one, and from a screenshot of one — §2.7: "A screenshot is always a screenshot of something"

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- pixel dimensions matching a common paper or screen size. Every export from every discipline lands on the same handful of sizes

### Work types

`artwork file`, `layout`, `export`, `proof`, `asset pack`, `mock-up`, `specification`

### Grouping reasons (§4)

- one artefact across its working file, its rounds and its exports — a version family plus its derivatives
- a series designed together — a poster set, a collateral suite — which shares linked assets rather than content
- a layout with the photography, illustration and fonts it places, discovered from §2.9's linked asset names

### Template (§5)

`client → project → artefact`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — an artefact named 'A2 poster' is meaningless until the project is known. Where there is no client the level is simply absent; §5.8 permits that: "The product should not force every branch to use the full template or have the same number of levels."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| media.social-assets | the same artwork resized for a feed is a marketing asset and a design artefact at once. The distinguishing signal is the channel-specific size set and a publish schedule, not anything in the file | §3.11: "One file may hold facts from more than one domain without losing information." |
| design.print-production | the press-ready export belongs to production; the artwork it came from belongs here. They share a stem and differ only by an added bleed and a colour conversion | §4.2: "files linked by duplicate or version relationships" |
| design.brand-identity | a piece of collateral applying an identity contains the identity's own artwork. A rule that keys on the presence of a logo will file the collateral as identity work | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — No design sentence puts design artwork in §2.9's "and potentially sensitive" category. Where the work is unreleased, the marking belongs on `studio.client-engagement`.

---

## `design.brand-identity` — Brand identity system

The mark, the type, the colour and the rules that govern how an organisation is allowed to look — plus the file that is the joke: logo_final_v3_FINAL.ai.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names identity design. §2.9 names the family and what may be read from it: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — the extractor's "layers or artboards where accessible" is exactly the evidence a logo master file yields, but a format is not a domain and this entry supplies the schema.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `brand` | string | Acme Foods | `validated` | The organisation the identity belongs to. §3.8 keeps it distinct from the client who commissioned it — a holding company frequently commissions an identity for a subsidiary |
| `identity component` | string | primary logotype | `llm_supported` | Logotype, symbol, lockup, wordmark, colour palette, type system, icon set, guideline document. It is the dimension an identity system is actually navigated by |
| `variant` | string | reversed mono | `validated` | Horizontal, stacked, mono, reversed, favicon. It is a labeled token in the filename in nearly every real identity folder, confirmed against a controlled variant vocabulary — §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `palette` | list of strings | Acme Red; Bone; Ink | `direct` | Named swatches, read from the file's own swatch table where the format exposes it. §2.8: "The system must retain raw evidence separately from normalized values." — the swatch name is the raw observation and a hex value is a normalisation of it |
| `guideline version` | string | v2 | `validated` | An identity outlives its designer and its guidelines are versioned deliberately, unlike the accidental version families around them. A labeled version on the guideline document's own cover is rule-confirmable |
| `is master` | boolean-like string | master | `user_confirmed` | Which file is the authoritative artwork. Capped at §3.13's "A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user." deliberately: this is the domain where the version-family problem is worst, and neither a filename token nor a modification time can answer it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a vector artwork file (AI, EPS, SVG) whose stem carries a controlled variant token beside an organisation name, in a set of siblings sharing that stem
- a document titled 'brand guidelines' | 'identity guidelines' | 'brand book' | 'visual identity' containing a colour or clear-space section
- a directory containing a logo stem exported across the lossless-plus-raster format spread that identity handoffs always take

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an unlabeled mark with no organisation name anywhere in the file, which is the normal state of an exported logo
- deciding whether a mark is the identity being designed or a client logo placed inside someone else's layout

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the presence of a logo. Every piece of collateral, every deck template and every invoice in the corpus contains one
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member. This domain is where that failure mode is worst: logo_final_v3_FINAL_reallyfinal.ai is a real filename shape and every token in it is a claim about currency that the file cannot support
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`logo master`, `logo variant set`, `guideline document`, `colour specification`, `type specification`, `application example`, `asset export pack`

### Grouping reasons (§4)

- one brand across every component of its identity — a purpose group, since a colour specification and a logotype share no content
- one component across its variants and its export formats, which is the version family plus its derivatives
- an identity with the collateral that applies it, discovered through §2.9's linked asset names rather than through similarity

### Template (§5)

`brand → identity component → variant`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — 'reversed mono' means nothing until the component is known and the component means nothing until the brand is. Time is excluded entirely: an identity is a standing system rather than a dated event, which is the plain case of §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.design-system-library | a brand system and a product design system share colour and type and increasingly share tokens. The brand system governs how the organisation looks; the design system governs how the product is built | §3.8: "The system must separate roles that happen to contain the same entity type." |
| design.graphic-project | collateral applying an identity carries the identity's artwork inside it, so any presence test misfiles it | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| legal.ip-registration | a trade-mark registration and a logo master describe the same mark; the registry filing is the finance-legal catalogue's | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — An identity exists to be seen. Pre-launch confidentiality is real but is a contractual state, not §2.9's "and potentially sensitive", and this catalogue does not stretch the phrase — see the open question on `studio.client-engagement`.

---

## `design.uiux-product` — UI and UX product design

Screen design for a software product — flows, wireframes, prototypes, specs — living in a tool whose files are usually not files.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names product design. §2.9 names the family and what may be read from it: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" names "Figma exports" specifically, which is the important word: what reaches the filesystem is an EXPORT of work whose real home is a hosted document, so this domain is systematically under-represented on disk.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `product` | string | Acme app | `llm_supported` | The software being designed. It is the same value the software catalogue holds as `project`, which §3.11 permits: "One file may hold facts from more than one domain without losing information." |
| `surface` | string | checkout | `llm_supported` | The screen, flow or feature. §5.5's parent-context rule makes this the level a screen name becomes meaningful under |
| `artefact type` | string | prototype | `validated` | Wireframe, mock-up, prototype, flow diagram, spec, redline, research summary. §3.11 already uses `artifact type` in the Research and Code rows: "Code files may use project, repository, programming language, and artifact type." |
| `platform` | string | iOS | `validated` | Confirmed from artboard dimensions matching a known device frame plus a platform term in the document, which is a pattern with a context check |
| `design stage` | string | exploration | `llm_supported` | Exploration, refinement, handoff-ready, shipped. It is the fact that separates three near-identical boards |
| `source document reference` | string |  | `possible` | The hosted document an export came from. Capped at §3.13's "A possible fact is a useful but insufficient clue" because an exported PNG or PDF usually retains no link at all — the export is an orphan by construction |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an export whose artboard or page dimensions match known device frames, in a set covering several such frames
- a document containing screen-flow vocabulary ('empty state' | 'error state' | 'happy path' | 'redline' | 'component spec') beside a product name
- a design-tool export naming convention that preserves page and frame names in the filename, which several tools do and which yields the surface directly

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a flat PNG of a screen, which is indistinguishable by every observable property from a screenshot of the shipped product. §2.6 is explicit that dimension and format tests are not a screenshot detector
- research artefacts — interview notes, usability findings — that carry no product name and read as generic documents

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. A Figma export has neither camera metadata nor document metadata and is not thereby a screenshot
- device-shaped pixel dimensions. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and the mirror error is equally available — a design mock-up at exactly a device resolution is not a screenshot either
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`wireframe`, `mock-up`, `prototype export`, `user flow`, `component spec`, `redline`, `research summary`, `usability findings`

### Grouping reasons (§4)

- one surface across its explorations, its states and its handoff artefacts
- one release or milestone across the surfaces it changed
- a design export with the implementation ticket or spec it was handed to, a purpose group in §3.9's sense

### Template (§5)

`product → surface → artefact type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — 'checkout' is meaningless without the product and 'prototype' is meaningless without the surface. Platform is deliberately not a level: it multiplies branches without improving retrieval, which is what §5.9's "It should recommend flattening when a dimension does not materially improve retrieval." is for

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.source-project | design exports frequently live inside the repository they describe. The software catalogue owns the repository; this owns the design artefacts, and one directory holds both | §3.11: "Code files may use project, repository, programming language, and artifact type." |
| pers.screenshot | the hardest collision in this slice. A screen mock-up and a screenshot of the shipped screen are the same PNG at the same size with the same absent metadata. §2.6 forbids the absence test that would separate them | §2.6: "conflicting signals should lead to abstention rather than an invented classification" |
| design.design-system-library | a component used in a screen and a component defined in the system are the same object at two levels of authority | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — Screen design is not personal data. Where mock-ups contain real user records rather than placeholder content the concern is genuine, but it belongs to the data inside them and is P7's to classify (§8.4), not this catalogue's.

---

## `design.design-system-library` — Design system, component and token library

The reusable definitions a product's design is assembled from — components, tokens, colour and spacing scales, icon sets — maintained as a standing artefact rather than a project.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names design systems. Proposed because it is the creative artefact that most resembles §3.11's Code row — "Code files may use project, repository, programming language, and artifact type." — a versioned, released, consumed library, and it therefore needs a schema closer to software than to artwork.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `system` | string | Acme Design System | `validated` | The named library. Confirmed from a manifest, a package name or a guideline title rather than inferred |
| `component` | string | Button | `validated` | The unit of the library, read from a page, frame, directory or token-file name — a structural read with a context check |
| `token set` | string | colour primitives | `direct` | Colour, spacing, typography and elevation scales, usually held in a structured data file. §2.9 has structured data yield "schema keys", so this is a direct read |
| `system version` | string | 3.2 | `validated` | A design system is versioned deliberately and semantically, unlike the accidental version families elsewhere in this slice. Read from a manifest or a labeled release note |
| `consumer` | string | Acme app | `llm_supported` | Which products use it. Kept as a fact for retrieval and explicitly not as a folder level — §3.8: "A folder should not become a collection point for everything produced by the same person or organization." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a structured token file whose schema keys are design-token names (colour, spacing, radius, typography scales) rather than application configuration
- a directory of component definitions each carrying a documentation file and a set of state variants
- a package manifest declaring a design-system dependency, which links a repository to this library deterministically

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a guideline document that reads as brand guidelines but governs product components, where only the vocabulary distinguishes them
- deciding whether a component file is the system's definition or a project's local copy of it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a colour palette. Every identity, every deck template and every stylesheet carries one
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- the word 'system' | 'library' | 'components' in a directory name

### Work types

`component definition`, `token file`, `documentation page`, `icon set`, `release note`, `migration guide`, `audit`

### Grouping reasons (§4)

- one system across its components, tokens and documentation
- one component across its states, variants and documentation
- one system version across everything released together, which is a deliberate version family rather than an accidental one

### Template (§5)

`system → component`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Version is deliberately not a level despite being reliable here — a per-version tree duplicates the whole library on every release, and §5.9 has the engine warn where a split "It should recommend flattening when a dimension does not materially improve retrieval."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.brand-identity | shared colour and type. The identity governs the organisation's appearance, the system governs the product's construction, and increasingly one file feeds both | §3.8: "The system must separate roles that happen to contain the same entity type." |
| soft.library-package | a design system shipped as a code package is both. The software catalogue owns the published package; this owns the design definitions | §3.11: "One file may hold facts from more than one domain without losing information." |
| studio.stock-asset-library | both are standing reusable libraries with no project. The design system is authored and versioned; a stock library is acquired | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — Nothing here is personal data and no design sentence puts it in §2.9's "and potentially sensitive" territory.

---

## `design.illustration` — Illustration

Drawn or painted image-making, commissioned or not, where the working file carries the whole history of the piece in its layers.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names illustration. §2.9 names the family and what may be read from it: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" supplies the observable material — layers, artboards, canvas properties — and this entry supplies the schema the design does not give.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `piece` | string | Cover — issue 12 | `llm_supported` | The illustration itself. It is the anchor of the version family and is usually named only in a brief or a filename |
| `commission` | string |  | `validated` | The job it was made for, where one exists. §3.8 keeps the commissioner distinct from the publisher and from the depicted subject |
| `technique` | string | digital ink and wash | `llm_supported` | How it was made. It matters for retrieval and for portfolio assembly, and it is visible in the artwork rather than stated anywhere |
| `canvas dimensions` | string | 3000 x 4000 px | `direct` | §2.9 has the design extractor yield "dimensions or canvas properties", and §2.6 has the image extractor store pixel dimensions. A direct read either way |
| `stage` | string | line art | `llm_supported` | Thumbnail, rough, line art, colour, final. Illustration's stages are unusually well-defined and unusually invisible: they are layers inside one file as often as they are separate files |
| `usage scope` | string | editorial, one use | `llm_supported` | Illustration is licensed rather than sold more often than any other discipline in this slice, so the usage fact belongs in the schema and links to `studio.licensing-rights` |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a raster artwork file whose extracted layer names carry drawing vocabulary ('sketch' | 'lineart' | 'flats' | 'shading' | 'bg'). §2.9: "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — layer names are the readable structure here
- a set of exports sharing a stem with a layered source file of the same stem

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a flat JPEG or PNG of finished artwork, which is the form almost every illustration reaches the filesystem in, and which carries no structure at all
- distinguishing the maker's own illustration from a downloaded reference or a stock illustration kept for inspiration

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. This is the domain where the failure bites hardest: a scanned or photographed drawing DOES carry camera EXIF and an exported digital painting carries none, so the metadata test inverts the truth
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- a large image with dense colour, which describes a photograph equally well

### Work types

`sketch`, `rough`, `line art`, `working file`, `final artwork`, `export`, `reference sheet`

### Grouping reasons (§4)

- one piece across its stages and its exports — the version family, anchored on a shared stem
- a series or a set commissioned together
- an illustration with the layout that placed it, discovered from §2.9's linked asset names

### Template (§5)

`commission or series → piece → stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Where the work is uncommissioned the first level is simply absent, which §5.8 permits: "The product should not force every branch to use the full template or have the same number of levels."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.creative-project | drawing for oneself and drawing for a client produce identical files. Only an external commission record separates them | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| design.graphic-project | illustration made as part of a layout is both; the layout's linked-asset manifest is what relates them rather than any property of the image | §3.11: "One file may hold facts from more than one domain without losing information." |
| photo.commissioned-shoot | a photographed or scanned drawing carries the camera EXIF of a photograph and the content of an illustration. §2.6's signal hierarchy will read it as a photo | §2.6: "conflicting signals should lead to abstention rather than an invented classification" |

### Sensitivity

`none` — No design sentence marks artwork as "and potentially sensitive".

---

## `design.typeface-and-font` — Typefaces, fonts and type licences

Type as a designed work and type as a licensed asset — the source, the build, the installed font file, and the licence that governs it.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names type. Proposed because a font file sits on both sides of a boundary the design does draw: §2.9's "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" treats creative files as documents to read, while a font is a dependency other files consume, which is closer to §3.11's Code row.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `typeface` | string | Acme Grotesk | `direct` | The family name, read from the font file's own name table. §3.13: "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." — a font's name table is a labeled metadata slot and one of the most reliable in any creative corpus |
| `style` | string | Bold Italic | `direct` | Weight, width and slope, read from the same name table rather than parsed from the filename |
| `font role` | string | licensed | `llm_supported` | Whether this file is a typeface being DESIGNED, a font LICENSED for use, or a font EMBEDDED in a handoff package. The three are the same format and belong in different places; §3.8's "The system must separate roles that happen to contain the same entity type." is the rule that requires the distinction |
| `licence class` | string | desktop + web | `llm_supported` | Desktop, web, app, broadcast, and the seat or impression limits attached. It is stated in a licence document, never in the font |
| `foundry` | string |  | `direct` | Read from the font's manufacturer or vendor name table entry. §3.8 keeps it distinct from the designer and from the licensee |
| `source format` | string | UFO source | `validated` | Source, build output or installed binary. It is what distinguishes type design work from a type library, confirmed from the real format signature — §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a font file signature whose name table yields a family, a style and a vendor — three labeled fields from one read
- a type-source project layout: glyph sources beside a build configuration and a features file
- a licence document naming a typeface family that also exists in the corpus as a font file

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- deciding whether a font directory is a licensed library, a client handoff or a designer's own release, which the files themselves do not say
- a foundry's specimen document, which reads as a brochure and is the only evidence of a purchase where the certificate is lost

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a font file. Fonts arrive embedded in handoff packages, bundled with templates and installed by applications; presence says nothing about intent
- a family name matched inside prose. §3.7: "It should use word-boundary matching rather than substring matching." — type families are named after cities, people and common nouns
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`glyph source`, `build configuration`, `font binary`, `specimen`, `licence document`, `webfont package`, `installation set`

### Grouping reasons (§4)

- one family across its styles and its build outputs — a version family whose members are deliberately distinct rather than accidentally so
- one licence with the fonts it covers, a purpose group in §3.9's sense
- fonts embedded in a handoff with the handoff they belong to, rather than merged into the type library

### Template (§5)

`typeface → style`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Foundry is deliberately not the first level despite being reliably readable: §3.8 "A folder should not become a collection point for everything produced by the same person or organization.", and a foundry folder is a collector

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| studio.stock-asset-library | a licensed font is a purchased reusable asset. The library owns the licensed copy; this domain owns type as designed work and as a licensing question | §3.8: "The system must separate roles that happen to contain the same entity type." |
| design.brand-identity | a bespoke typeface commissioned for an identity belongs to both, and its files are usually inside the identity folder | §3.11: "One file may hold facts from more than one domain without losing information." |
| studio.deliverable-handoff | fonts embedded in a package are part of the package, not of the type library; merging them silently breaks the package and misstates the licence position | §4.8: "that each fact or label belongs to an allowed domain schema" |

### Sensitivity

`none` — No design sentence marks type as "and potentially sensitive".

---

## `design.print-production` — Print production and prepress

What happens to designed artwork on its way to a press — imposition, proofs, colour, plates, the printer's own paperwork.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names print production. Proposed because it is the clearest case in this slice where §5.5's "a parent dimension should provide the context required to understand the child" is violated by the obvious template: production files are named for the PRINTER's job number, which is meaningless in the designer's tree.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `job` | string | Spring poster series | `llm_supported` | The design job going to press. It is the value that links production back to `design.graphic-project` |
| `printer` | string |  | `validated` | §3.8's supplier role, distinct from the client and from the designer. Read from a labeled quote or docket field |
| `print job number` | string | J-40218 | `direct` | The printer's own reference, read from a labeled field. It is the key everything at the printer is filed under and the key nothing in the designer's corpus uses |
| `proof stage` | string | wet proof | `validated` | Soft proof, contract proof, wet proof, press pass. A controlled vocabulary matched with a context check — §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `stock and finish` | string | 170gsm uncoated, matt lam | `llm_supported` | Stated in a specification in prose. It is what makes two otherwise identical jobs different objects |
| `colour space` | string | CMYK + Pantone 485 | `direct` | Read from the embedded profile and spot-colour list. It is the field that separates a production file from the screen artwork it came from |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a PDF carrying prepress structure — crop and bleed marks, a spot-colour list, an output intent — beside a source artwork file with a shared stem
- a document titled 'proof' | 'imposition' | 'plate' | 'print spec' | 'docket' | 'delivery note' carrying a job-number-shaped labeled field
- a printer's quote or invoice naming a job that also exists as artwork in the corpus

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a printer's email confirming a change in prose, which is where most production decisions actually live
- deciding whether a PDF is the press-ready file or a proof of it — often identical apart from a mark

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a PDF. §2.9 routes PDFs to a text extractor and says nothing about their purpose
- a job-number-shaped string. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`press-ready artwork`, `imposition`, `proof`, `print specification`, `docket`, `colour target`, `delivery note`

### Grouping reasons (§4)

- one print job across its artwork, proofs, specification and dockets — purpose-coherent and content-incoherent
- one artwork across its screen version and its press version, which are a version family separated by a colour conversion

### Template (§5)

`client → project → print job`

Time first: **no**

The print job belongs beneath the design project it realises, not beside it: §5.5's "a parent dimension should provide the context required to understand the child". The printer's own job number is carried as a fact and is explicitly not a level, because it is the supplier's index and not the owner's

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.graphic-project | the press-ready export and the artwork share a stem and differ by a bleed and a colour conversion | §4.2: "files linked by duplicate or version relationships" |
| biz.procurement-po | the printer's quote, PO and invoice are finance records that name the same job | §3.11: "One file may hold facts from more than one domain without losing information." |
| art.printmaking | both are printing. Commercial production reproduces a design; printmaking makes an artwork through the printing itself, and the vocabulary overlaps almost completely | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — No design sentence marks production files as "and potentially sensitive".

---

## `design.presentation-deck` — Presentation and pitch decks

Slides built to persuade — a new-business pitch, a client presentation, a conference talk — which the design catalogue owns as artefacts and other catalogues own by content.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names decks as a domain, but §2.9 gives the extractor for them precisely: "Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries." — again a FORMAT family, and this entry supplies the schema.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `deck` | string | Acme pitch — round two | `llm_supported` | The presentation itself, named on its own title slide more often than in its filename |
| `audience` | string | Acme marketing team | `llm_supported` | §3.9's purpose fact. The same slides shown to a client, a jury and an internal team are three different decks with one content |
| `occasion` | string | pitch meeting | `llm_supported` | Pitch, review, conference talk, internal share. It is the fact that decides which catalogue should own the file |
| `presented date` | date | 2026-03-11 | `direct` | Read from a labeled date on the title slide. §2.9 has slide extraction yield "Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries.", and a title slide is a title, not a body paragraph — §3.7's positional weighting applies |
| `deck version` | string | v4 | `validated` | Decks are the single most version-proliferated document type in professional corpora, and the version token is nearly always in the filename |
| `template used` | string | Acme brand template | `validated` | Which brand template a deck was built from, read from the theme or master-slide name. It links a deck to `design.brand-identity` structurally |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a presentation file signature whose extracted structure yields slide titles and a master or theme name. §2.9: "Presentations such as PPTX, PPT, ODP, and PDF slide decks should yield slide titles, text boxes, speaker notes where available, hyperlinks, embedded tables, and slide-level page boundaries."
- a PDF whose page dimensions are a presentation aspect ratio and whose pages carry a repeated master layout
- a title slide bearing a labeled date and an organisation name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- deciding what a deck is FOR, which is the only fact that distinguishes a pitch from a talk from a report and is never labeled
- a deck exported to PDF with a generic filename, which is how most decks reach a corpus

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a presentation file extension. §2.9 makes it a routing signal: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- a sixteen-by-nine page shape, which is also every video still and every screen mock-up
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`pitch deck`, `client presentation`, `conference talk`, `internal review`, `leave-behind PDF`, `template`

### Grouping reasons (§4)

- one deck across its versions and its exported PDF — a version family plus one derivative
- one pitch across the deck, the brief that prompted it and the outcome, a purpose group in §3.9's sense
- one template with the decks built from it, discovered from the theme name rather than from similarity

### Template (§5)

`client or occasion → deck → version`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". A version level is included here and nowhere else in this slice because deck versions are deliberate and numerous; §5.9 has the engine warn where that produces tiny folders, and the version level should collapse when it does

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| res.talk | a conference talk deck belongs to the research catalogue by content and to this by artefact. §3.11 permits both sets of facts on one file | §3.11: "One file may hold facts from more than one domain without losing information." |
| corp.fundraising-investor | an investor deck is a finance record and a designed artefact. The finance catalogue owns the raise; this owns the design work if the deck was designed as a job | §3.8: "The system must separate roles that happen to contain the same entity type." |
| career.client-proposal | a new-business pitch deck IS the proposal in most creative businesses | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`none` — A deck's content may be sensitive and its classification then belongs to that content, which is P7's to handle (§8.4). No handling class is set here and no blanket marking is applied to the artefact type.

---

## `design.interior` — Interior design project

Designing a physical space — drawings, schedules, specifications, samples, site photographs — for one property.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names interior design. §2.9 names "CAD files" in the creative format family — "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — which is a routing fact only; this entry supplies the schema, and the space rather than the file is its organising subject.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Flat 4, Bedford Row | `llm_supported` | The scheme. Interior projects are named for a property, which makes the project name and the location the same string and requires care — §3.8: "The system must separate roles that happen to contain the same entity type." |
| `space` | string | kitchen | `llm_supported` | The room or zone. It is the natural second dimension and it is stated on drawings rather than in filenames |
| `drawing type` | string | reflected ceiling plan | `validated` | Plan, elevation, section, detail, reflected ceiling plan, schedule. A controlled vocabulary read from a drawing title block — a labeled field, so §3.13's "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." is reachable where the block is machine-readable and "A validated fact was found by a deterministic rule and passed contextual checks" where it is not |
| `drawing number` | string | IA-204 | `direct` | Read from a labeled title block. It is the profession's own identifier and the only reliable key across a drawing set |
| `revision` | string | Rev C | `validated` | Drawing revisions are lettered, sequential and recorded in a revision table — the one place in this whole slice where a version family is properly documented inside the file |
| `specification item` | string |  | `llm_supported` | Finishes, fittings and furniture named in a schedule. It is what links a sample photograph and a supplier quote to a drawing |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a drawing file or PDF carrying a title block with labeled drawing number, revision and scale fields
- a schedule document whose table columns are specification vocabulary (item, location, finish, supplier, quantity). §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."
- a CAD or BIM file signature. §2.9 warns that where it cannot be read it must be recorded as indexed-but-unreadable: "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty"

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- site and sample photographs, which are ordinary camera images whose only project signal is what they depict
- a mood or concept board, which is a collage of unattributed images with no readable structure

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a CAD extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- an address-shaped string, which appears in every letterhead and every supplier record in the corpus
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — site photographs DO carry EXIF and sample photographs shared by a supplier do not, so the two halves of one project split on the metadata test

### Work types

`plan`, `elevation`, `detail`, `schedule`, `specification`, `mood board`, `site photograph`, `supplier quote`, `sample record`

### Grouping reasons (§4)

- one project across drawings, schedules, photographs and correspondence — purpose-coherent and content-incoherent
- one drawing across its revisions, which is a documented version family
- one specification item with the drawings, samples and quotes that reference it

### Template (§5)

`project → stage or space → drawing type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a drawing type is meaningless without the space and the space without the project. Time is excluded despite a project having clear phases, per §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.architecture-visual | the same drawing set, the same title blocks, the same software. The scope of the work — a building or its interior — separates them and is often not visible in a single file | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| pers.home-tenure | a homeowner's own renovation produces the same drawings and photographs as a professional project. The personal catalogue owns the property record; this owns professional design work on a property | §3.8: "The system must separate roles that happen to contain the same entity type." |
| photo.commissioned-shoot | the finished-project photography is a commissioned shoot in its own right and belongs to both | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. An interior project is filed under a private residential address and its site photographs show the inside of a home — the address is contact-shaped material that §2.9 says should be "but should normally be privacy-protected rather than used to create folder proposals". The handling class is P7's (§8.4) and none is set.

---

## `design.architecture-visual` — Architectural visualisation and drawings

The visual side of architecture — drawing sets, renders, models, competition boards — for one building or scheme.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names architecture. §2.9 names "CAD files, and 3D files" in the creative format family — "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" — a routing fact only. This entry claims the visual side and deliberately does not claim the contractual, planning or construction record.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `scheme` | string | Bedford Row infill | `llm_supported` | The building or project. It is the top of everything else in this domain and is stated in a title block |
| `drawing number` | string | A-1102 | `direct` | Read from a labeled title block, which is the profession's own filing key and one of the few genuinely reliable identifiers in this whole supercategory |
| `drawing type` | string | section | `validated` | Site plan, floor plan, elevation, section, detail, axonometric. A controlled vocabulary with a context check |
| `project stage` | string | planning | `llm_supported` | Concept, planning, tender, construction, as-built. It changes what a drawing means and is stated in a title block or a transmittal |
| `revision` | string | Rev B | `validated` | A lettered revision recorded in the drawing's own revision table — a documented version family, unlike the filename-token families elsewhere in this slice |
| `render view` | string | street approach, dusk | `llm_supported` | Visualisations are made in named views and iterated in passes; the view is the only thing that distinguishes twenty near-identical images |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a drawing PDF or CAD file with a labeled title block yielding scheme, drawing number, scale and revision together
- a transmittal or drawing-issue sheet listing drawing numbers that exist in the corpus
- a render output directory: many large images sharing a view stem with a frame or pass suffix

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a competition or presentation board, which is a designed layout containing drawings rather than a drawing
- distinguishing a render of an unbuilt scheme from a photograph of a built one — the explicit goal of the render is that they be indistinguishable

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. A photorealistic render carries no camera EXIF and is not thereby a screenshot; §2.6 "the system must not mistake the absence of EXIF for proof that an image is a screenshot"
- a CAD or 3D extension. §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- a drawing-number-shaped string, which collides with part numbers, invoice references and course codes alike

### Work types

`drawing set`, `render`, `model file`, `competition board`, `survey`, `transmittal`, `photomontage`

### Grouping reasons (§4)

- one scheme across drawings, renders, models and boards
- one drawing across its revisions
- one render view across its iterations and passes, which is a version family that no filename token orders correctly

### Template (§5)

`scheme → project stage → drawing type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Stage precedes drawing type because a planning elevation and a construction elevation are different documents that share a name; the revision stays inside a version family rather than becoming a level, which §5.7's "create meaningless one-child levels" check would otherwise punish

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.interior | identical drawing conventions, identical software, frequently the same project. Scope separates them and a single sheet rarely states it | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| cg.3d-asset | an architectural model is a 3D asset and the render pipeline is identical to any other. The scheme is what makes it architecture | §3.8: "The system must separate roles that happen to contain the same entity type." |
| soft.hardware-design-file | the software catalogue holds CAD for hardware. Both are CAD and §2.9 routes them identically; only the subject separates them | §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |

### Sensitivity

`none` — A scheme is a building, not a person. Where the scheme is a private residence the address concern is the same one marked on `design.interior`; it is not repeated here as a blanket marking.

---

## `design.fashion` — Fashion design collection

Designing garments — sketches, technical drawings, specification packs, patterns, fittings, lookbooks — organised by collection and season.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names fashion. Proposed because it is the one domain in this slice where a SEASON is a genuine organisational dimension and is nevertheless not a time fact: 'AW26' is a collection label, and §3.10 would misparse it as a year.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `collection` | string | AW26 | `validated` | The season-collection label. It looks like a date and is not: §3.10 requires explicit patterns because documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values", and a season code needs a dedicated pattern exactly as §3.10 says academic terms do |
| `style` | string | Coat 04 | `validated` | The garment. A style number or name is the profession's key and is carried on every document in the pack |
| `document role` | string | tech pack | `validated` | Sketch, technical flat, tech pack, pattern, grading, bill of materials, fitting note, lookbook. A controlled vocabulary with a context check |
| `fabric or component` | string |  | `llm_supported` | Named in a bill of materials. It is what links a supplier record and a swatch photograph to a style |
| `sample stage` | string | second proto | `llm_supported` | Proto, fit sample, salesman sample, production. It is this domain's round, and it orders the fitting photographs that would otherwise be an undifferentiated pile |
| `supplier or factory` | string |  | `validated` | §3.8's supplier role, kept distinct from the brand and from the client. A fact, not a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document whose table columns are tech-pack vocabulary (style, size, measurement, tolerance, component, supplier). §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."
- a season-collection code matched by a dedicated pattern beside a style identifier, both present in one filename or title block
- a technical flat: a vector artwork file whose layer names carry construction vocabulary

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- fitting photographs, which are ordinary camera images of a person and carry no style reference
- a lookbook, which is a designed layout of photographs and belongs equally to `design.graphic-project` and `photo.commissioned-shoot`

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a season-shaped code. 'SS25' collides with a course code, a room number and a product SKU, and §3.10's warning is specifically about this shape
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — fitting photographs carry camera EXIF, supplier-sent swatch images carry none, and both belong to the same style
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`sketch`, `technical flat`, `tech pack`, `pattern`, `grading sheet`, `bill of materials`, `fitting note`, `lookbook`, `line sheet`

### Grouping reasons (§4)

- one collection across every style in it
- one style across its sketch, tech pack, pattern, samples and photographs — purpose-coherent and content-incoherent in §3.9's sense
- one sample stage across the fitting notes and photographs made at it

### Template (§5)

`collection → style → document role`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a tech pack is meaningless without its style and a style without its collection. The collection level LOOKS like time-first and is not: a season code is a named collection, not a capture date, so §5.5's capture-based exception does not apply and `time_first` stays false

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| photo.commissioned-shoot | lookbook and campaign photography for a collection is a commissioned shoot that also belongs to the collection | §3.11: "One file may hold facts from more than one domain without losing information." |
| design.graphic-project | line sheets, lookbooks and labels are graphic design artefacts made inside a fashion project | §3.8: "The system must separate roles that happen to contain the same entity type." |
| biz.vendor-management | factory and supplier records are finance-catalogue material that names the same styles | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only, and narrowly: fitting photographs are identifiable photographs of a named individual's body, which is the same contact-shaped and personal material §2.9 says should be "but should normally be privacy-protected rather than used to create folder proposals". The rest of the domain is not marked and no handling class is set — that is P7's (§8.4).

---

## `photo.commissioned-shoot` — Commissioned photography shoot

Photography made as a job — a client, a brief, a shoot, a selection, a delivery — as distinct from the same camera's personal pictures.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the Photos domain the design names — §3.11: "Photos may use capture year, event, location, people, camera information, and media type." — to the professional case, and inherits §2.6's image pipeline whole. The extension is that a commissioned shoot has a client, a brief and a delivery, none of which §3.11's Photos row contains, and that its output is mostly stripped exports rather than camera originals.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `client` | string | Acme Foods | `validated` | §3.8's client role. It is the fact that makes this domain rather than the personal Photos domain, and it is never in the image — it is read from a brief, a contract or a curated folder |
| `shoot` | string | Spring product shoot | `llm_supported` | The job. One client shoots several times a year and each shoot is the unit of work, of delivery and of licensing |
| `capture date` | date | 2026-03-14 | `direct` | §3.2's own worked example of a derived fact, and §3.13's "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." names the EXIF timestamp explicitly. It is direct on camera originals and ABSENT on delivered exports, which is the asymmetry that defines this domain's recognition problem |
| `shoot stage` | string | selects | `validated` | Camera original, select, retouched, delivered. Confirmed from the real format plus the directory structure rather than from a filename token |
| `camera information` | string | Canon EOS R5 | `direct` | §3.11 names `camera information` in the Photos row and §2.6 has the extractor store EXIF make and model. A labeled metadata slot, so §3.13's "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `usage scope` | string | UK, digital, one year | `llm_supported` | Commissioned photography is licensed rather than sold. The scope is stated in a brief or a licence and is the fact that makes `studio.licensing-rights` reachable from an image |
| `people` | string |  | `user_confirmed` | §3.11 names `people` in the Photos row. Capped at §3.13's "A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user.": the design authorises no automatic producer for it, and on a commissioned shoot the depicted people are also the subjects of the releases held in `studio.licensing-rights` |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a run of camera-original files sharing one camera body and a bounded capture window. §2.6: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."
- a directory tree matching the profession's own shape — a camera-original directory, a selects directory and a delivery directory sharing one parent whose name carries a client or shoot name
- a sidecar or catalogue file referencing image filenames that exist in the corpus, which relates a stripped export to its original structurally rather than by content

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- delivered JPEGs with a client-shaped folder name and nothing else: no EXIF, no sidecar, no catalogue. This is the normal state of most professional photography on a filesystem
- deciding whether a shoot was commissioned or personal, where the same camera produced both on the same day

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. §2.6 is written for exactly this corpus: a delivered photograph is stripped, and treating stripped-plus-PNG as a screenshot hypothesis will classify a professional's entire delivered output as screenshots
- camera EXIF on its own, which is equally the photographer's holiday. §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"
- a large directory of JPEGs, which is also a scan batch, an asset library and a download folder

### Work types

`camera original`, `select`, `retouched image`, `delivered export`, `contact sheet`, `shot list`, `call sheet`

### Grouping reasons (§4)

- one shoot across originals, selects, retouches and deliveries — a version family whose members span formats and lose their metadata as they go
- one client across their shoots
- a shoot with the releases, brief and licence that govern it, a purpose group in §3.9's sense
- an image with its sidecar and catalogue entry, which is §4.2's "files linked by duplicate or version relationships"

### Template (§5)

`client → shoot → shoot stage`

Time first: **no**

This is the deliberate exception to §5.5's capture-based rule and it needs stating. §5.5 says "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.". A commissioned shoot IS capture-based media — but the capture date is not what defines it; the job does, and the job is what a working photographer retrieves by. The capture date is retained as a direct fact and as the natural label of the shoot level, so time is present without leading. Contrast `photo.raw-catalogue`, where no job exists and §5.5's exception applies in full

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.photo-event | the personal catalogue's photo event is created deterministically from camera, time and GPS — exactly the metadata a commissioned shoot's originals also carry. Every professional shoot will look like a personal photo event to that rule, and nothing in the image distinguishes them. Only an external client or brief record does | §2.6: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals." |
| pers.photo-occasion | a paid wedding or event shoot and the couple's own photographs of the same wedding are the same occasion from two roles. §3.8's role separation is the whole distinction | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pers.travel-photos | a travel-photography assignment produces trip photographs, and a trip produces images sold as stock. The same files, two purposes | §4.9: "A file may validly belong to more than one accepted group" |
| photo.raw-catalogue | the camera originals of a commissioned shoot are also members of the RAW archive. This is a deliberate double membership rather than a conflict | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. Commissioned photography contains identifiable people and, on camera originals, GPS — §3.11 names `people` and §2.6 names GPS among what is stored. §2.9 already requires contact-shaped data to be "but should normally be privacy-protected rather than used to create folder proposals" and the same restraint applies here. No handling class is set; that is P7's (§8.4).

### Open question — Joseph's call, unresolved

> Where is the boundary between this domain and the personal Photos domain, and who draws it? One camera, one person, one filesystem produces both, and §2.6's signal hierarchy cannot separate them because it is built to distinguish photographs from screenshots, not paid photographs from unpaid ones. The catalogue's position is that a client or brief record external to the image is the only admissible signal, and that in its absence the engine should abstain rather than guess — §2.6: "conflicting signals should lead to abstention rather than an invented classification". But abstention here means a professional photographer's corpus lands mostly unclassified, which may be the wrong trade for the actual user. Whether a photographer's default is 'assume professional unless personal' or the reverse is a statement about a real person's working life and is Joseph's to make.

---

## `photo.raw-catalogue` — RAW archive and photo catalogue

The camera-original archive itself — RAW files, sidecars and the catalogue database that indexes them — organised by when it was shot because nothing else is universal.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the Photos domain of §3.11 — "Photos may use capture year, event, location, people, camera information, and media type." — with the archive layer §2.6 describes the evidence for: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals.". No design sentence names a RAW archive or a catalogue database; the extension is that the archive is a standing store rather than an event or a project.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `capture date` | date | 2026-03-14 | `direct` | §3.13 names the EXIF timestamp among the sources of a direct fact: "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." On camera originals it is present and correct essentially always, which is why it can carry the template |
| `capture year` | year | 2026 | `direct` | §3.11 names `capture year` in the Photos row. A projection of the direct capture date rather than a second observation, so it inherits that ceiling and never outlives it |
| `camera information` | string | Canon EOS R5 | `direct` | §3.11 names `camera information`; §2.6 has the extractor store EXIF camera make and model, lens data, ISO and focal length |
| `ingest batch` | string | 2026-03-14 card 1 | `validated` | The card or import the files arrived in. It is the archive's real unit, confirmed from a bounded capture window on one body plus a contiguous frame-number run |
| `media type` | string | RAW | `direct` | §3.11 names `media type` in the Photos row. Read from the real signature — §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |
| `catalogue reference` | string |  | `direct` | The identifier a catalogue database or sidecar holds for an image. It is the only thing that survives an export and links a stripped JPEG back to its RAW |
| `rating or flag` | string | picked | `direct` | Read from a sidecar's own labeled field. It is the photographer's selection recorded in a machine-readable place, and it is the closest thing this slice has to a documented current-version marker |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a RAW file signature carrying EXIF camera make, model and capture time together — three labeled fields from one read
- a sidecar file sharing a stem with an image file in the same directory. §4.1 names "document type, course codes, dates, target institutions, project identifiers, duplicate relationships, version stems, capture metadata, filename patterns, and structural links"
- a catalogue or database file whose referenced paths resolve to images in the corpus
- a contiguous camera frame-number run within a bounded capture window on one body

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- nothing, by design. This is the one domain in this slice that should never need the model route: it is defined by metadata that is present, and where the metadata is absent the file is not in this domain

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — an archive is defined by metadata being PRESENT, so the absence test would be inverted here and is still wrong
- a proprietary RAW extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning", and manufacturers reuse extensions for unrelated formats
- a directory of large image files, which is equally a scan batch or a render output

### Work types

`RAW file`, `sidecar`, `catalogue database`, `preview cache`, `import log`, `backup set`

### Grouping reasons (§4)

- one ingest batch — a card, an import, a day
- one image with its sidecar, its previews and its derivatives, which is §4.2's "files linked by duplicate or version relationships"
- a run of captures that camera identity, time and GPS already relate, which §2.6 makes deterministic

### Template (§5)

`capture year → capture date → ingest batch`

Time first: **yes**

§5.5's stated exception applies here in full and without qualification: "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.". A RAW archive has no client, no project and no subject — the fields §5.5's normal ordering requires are simply not present — while capture date is `direct` on every member. This is the cleanest time-first case in the whole supercategory

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| photo.commissioned-shoot | every commissioned shoot's originals are also archive members. Deliberate double membership rather than a conflict; the archive is the store and the shoot is the job | §4.9: "A file may validly belong to more than one accepted group" |
| pers.photo-event | the personal catalogue's deterministic photo event is built from the same three metadata fields on the same files. The archive is the container and the event is a group inside it | §2.6: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals." |
| studio.stock-asset-library | a photographer's archive is also their stock library, and the same RAW may be licensed repeatedly | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. A camera archive carries GPS and identifiable people on every frame — §2.6 names GPS among what is stored and §3.11 names `people` as a Photos field. No handling class is set; that is P7's (§8.4).

---

## `film.production` — Film and video production

A production as an organising whole — its script, schedule, paperwork, media and cuts — from development to delivery.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names film production. §2.9: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" gives the extractor and "and—only under an explicit privacy and compute policy—speech-to-text transcripts" gates the transcript route, but neither is a schema. This entry supplies one, and deliberately splits the capture layer into `film.shoot-day-media`.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `production` | string | Acme — Spring film | `llm_supported` | The title. Everything else in this domain is meaningless without it, which is why it heads the template |
| `production phase` | string | post | `validated` | Development, pre-production, production, post, delivery. A controlled vocabulary confirmed from the document types present rather than asserted |
| `scene` | string | 14 | `validated` | The script unit. It appears in a slate, a filename, a script heading and a shot list, and a scene-shaped token needs a context check exactly as §3.5's course code does |
| `take` | string | 14B/3 | `validated` | The capture unit. Scene-slash-take notation is the profession's own and is machine-readable where a slate or a camera-report is present |
| `shoot date` | date | 2026-04-02 | `direct` | Read from a call sheet or a camera report's labeled field, and directly from media creation time on camera originals. §2.9 has A/V yield "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" |
| `role or department` | string | camera | `llm_supported` | §3.8's role separation applied to a crew: the same person is a producer on one production and an editor on another, and no department becomes a folder level |
| `deliverable spec` | string | ProRes 422 HQ, 1080p | `direct` | §2.9 has A/V yield container and codec metadata directly, so a delivery specification can be checked against the file rather than trusted |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- production paperwork by document title — 'call sheet' | 'shot list' | 'shooting schedule' | 'camera report' | 'sound report' | 'continuity' — carrying a labeled production title and date
- a script file with scene headings, which are a machine-readable structure rather than prose
- a media directory whose filenames match a camera's own clip naming and whose container metadata yields creation time. §2.9: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present"

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a video file with a generic filename and no adjacent paperwork, where only the content says what production it belongs to
- distinguishing a production's own reference material from its output, since both are video files in one tree

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a video file extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- a scene- or take-shaped token, which collides with version numbers, part numbers and dates alike. §3.10 "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- media creation time, which a transcode rewrites while the shoot date stays what it was

### Work types

`script`, `call sheet`, `shot list`, `schedule`, `camera report`, `sound report`, `continuity`, `cut`, `delivery master`

### Grouping reasons (§4)

- one production across every department and phase — the largest purpose group in this slice, and content-incoherent throughout
- one scene across its takes, its script pages and its continuity
- one cut across its versions, which is a version family with a genuine sequence

### Template (§5)

`production → production phase → department or artefact`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Phase precedes department because a camera report from pre-production and one from the shoot are different objects. Shoot date is deliberately not a level HERE — it belongs to `film.shoot-day-media`, which is where §5.5's capture-based exception actually applies

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| film.shoot-day-media | the media is part of the production and is split out because it obeys a different ordering rule. A deliberate split, not a conflict | §5.5: "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." |
| write.screenplay | the script belongs to the writer's domain until it is in production, and to the production afterwards, with the same file on both sides | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| pers.home-video | the personal catalogue owns family video. A production's behind-the-scenes footage shot on a phone is indistinguishable from it by every observable property | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — Production paperwork carries crew contact details and §2.9 already requires that material to be "but should normally be privacy-protected rather than used to create folder proposals", but the marking is applied where the personal data actually is — call sheets — rather than to the whole production. No handling class is set (§8.4).

---

## `film.shoot-day-media` — Shoot-day camera and sound media

Camera originals, sound rolls and dailies as they came off the cards — the one body of files in this slice that is organised by the day it was shot.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the capture-based material §5.5 names — "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." — from photographs to camera and sound originals, using §2.9's A/V extractor: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present". No design sentence names shoot-day media; the extension is that a shoot day is a capture run in exactly §2.6's sense.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `shoot date` | date | 2026-04-02 | `direct` | §2.9 has A/V yield creation time directly and §3.13 makes an explicit metadata slot a "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field.". It is the field the whole domain is ordered by |
| `unit` | string | main unit | `llm_supported` | Main, second, splinter, aerial. Two units shooting the same day produce two disjoint media sets that must not merge |
| `card or roll` | string | A001 | `validated` | The camera's own reel identifier, present in clip filenames and in the camera report. It is the profession's own key and a contiguous run confirms it |
| `camera or recorder` | string | A-cam | `direct` | Read from container metadata. §2.6's equivalent for stills is EXIF camera make and model, and the reasoning is identical |
| `media role` | string | camera original | `validated` | Camera original, sound roll, proxy, daily, transcode. Confirmed from the real codec and container rather than from the filename — §2.9 yields "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" |
| `timecode start` | string | 10:04:22:11 | `direct` | Read from container metadata. It is what syncs picture to sound and is the strongest structural edge available between two files that share no content |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a contiguous clip-name run under one reel identifier with container creation times inside one bounded window — the moving-image equivalent of §2.6's "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."
- a camera or sound report naming reels that exist in the corpus
- a card-dump directory structure reproduced verbatim from a camera's own card layout, identified from its manifest rather than its name

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- media whose card structure was flattened on copy and whose container metadata was rewritten by a transcode, leaving only content
- assigning orphaned media to a production where several were shot in the same period

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. The moving-image case is worse than the stills case: a transcode or an upload strips or rewrites container metadata as a matter of course, and treating a stripped MP4 as not-camera-original is the same error §2.6 forbids
- a video extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- media creation time on its own, which a transcode sets to the transcode date

### Work types

`camera original`, `sound roll`, `proxy`, `daily`, `transcode`, `camera report`, `sound report`

### Grouping reasons (§4)

- one shoot day across every unit, camera and recorder that ran on it
- one card or roll as a contiguous run
- picture and sound related by timecode, which relates files that share no content at all

### Template (§5)

`shoot date → unit → card or roll`

Time first: **yes**

§5.5's exception applied deliberately: "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.". Camera original media IS capture-based material — the shoot day is how it is ingested, how continuity is tracked, how a camera report indexes it and how an editor finds it. Every other dimension (unit, card, camera) is a child of the day. The production sits ABOVE this template as the branch this domain lives in, so the day leads within it

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| film.production | the media belongs to the production; it is split out because it is the one part of a production that orders by time | §5.5: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." |
| pers.home-video | a phone clip shot on a set and a phone clip shot at a family lunch are the same container with the same metadata shape | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| photo.raw-catalogue | stills shot on the same day by a unit stills photographer land in both, ordered identically | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only. Camera media contains identifiable people throughout and §2.9 gates transcription explicitly — "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — which is the design's own signal that recorded speech is not ordinary content. No handling class is set; that is P7's (§8.4).

---

## `film.post-production` — Editing and post-production

The assembly of a production — project files, bins, cuts, grades, mixes, versions — where the working file references media it does not contain.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names post-production. Proposed because an editing project file is the extreme case of §2.9's "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" pattern: it is almost entirely "linked asset names", and the file itself contains none of the material it describes.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `production` | string | Acme — Spring film | `llm_supported` | Inherited from `film.production`, and the anchor every post artefact hangs from |
| `cut` | string | director's cut | `llm_supported` | Assembly, rough, fine, picture lock, director's cut, broadcast version. It is the unit a version family anchors on, and it is named in prose |
| `cut version` | string | v14 | `validated` | A labeled version token beside a cut name. Editing produces more version-family members than any other activity in this slice, and the token is the only ordering signal available |
| `post stage` | string | grade | `validated` | Offline, online, grade, VFX, sound mix, master. Confirmed from the artefact type and the application signature together |
| `linked media` | list of strings | A001C003_260402.mov | `direct` | §2.9 names "linked asset names" among what a creative file yields. In post this is the whole content of the project file and the strongest structural edge in the supercategory |
| `duration` | string | 00:02:31:04 | `direct` | §2.9 has A/V yield duration directly. It is what distinguishes a rough cut from a finished one when the filenames do not |
| `delivery spec` | string | ProRes 422 HQ, 1080p, stereo | `direct` | Read from container and codec metadata rather than from a specification document, so a master can be verified against what was asked for |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an editing or grading project file whose extracted link list names media that exists in the corpus
- an edit-decision or conform list, which is a structured text file naming reels and timecodes
- a render or export directory whose members share a cut stem with a version token and differ in codec

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a flat export with a generic filename, which is what most finished video actually is on a filesystem
- deciding which of fourteen version-token siblings is the delivered master when several were re-exported later

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member. Post is where the joke in the brief is literally true: a cut named final_v3_FINAL is routine and the token orders nothing
- the highest version number, which in editing is very often an abandoned experiment
- modification time, which a re-render rewrites on an old cut

### Work types

`project file`, `bin`, `edit decision list`, `cut export`, `grade`, `mix`, `master`, `conform list`, `VFX pull`

### Grouping reasons (§4)

- one cut across its versions and its exports — the version family this slice's whole problem is named after
- one project file with the media it links, which §2.9's linked asset names make deterministic
- one production across its post stages

### Template (§5)

`production → cut → post stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a grade is meaningless without the cut and a cut without the production. Version stays inside a version family rather than becoming a level: a per-version folder would create the tiny one-child folders §5.7 makes the engine reject when it checks that a template does not "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| film.shoot-day-media | proxies and transcodes are made in post and are media by every observable property | §4.2: "files linked by duplicate or version relationships" |
| film.motion-graphics | titles and graphics are made in a separate application and delivered back into the edit as media; the same frames exist as a project and as a render | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.portfolio-showreel | a reel is an edit made from finished work, with the same project files and the same export shape | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`none` — The recorded people are marked on `film.shoot-day-media`, where the capture is. Repeating the marking on every derived cut would flatten the distinction rather than protect anything, and no handling class is set here (§8.4).

---

## `film.motion-graphics` — Animation and motion graphics

Moving image made rather than filmed — titles, explainers, animated identity, character animation — where every frame is an output of a project file.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names animation. Proposed because it is the domain that most breaks the design's file-is-the-work assumption: the deliverable is a render, the work is a project file plus a directory of source assets, and §2.9's "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" is the normal outcome for the project file itself.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | Acme explainer | `llm_supported` | The animation being made |
| `sequence or shot` | string | sh020 | `validated` | The unit of animation work. Shot codes are a controlled shape and appear in filenames, render paths and review documents together |
| `animation stage` | string | animatic | `llm_supported` | Storyboard, animatic, blocking, animation, comp, render. It is what makes twenty near-identical previews legible |
| `render pass` | string | beauty | `validated` | Beauty, matte, depth, AO. A controlled vocabulary carried in filenames and directory names, confirmed with a context check |
| `frame range` | string | 1001-1240 | `direct` | Read from an image-sequence filename run rather than parsed as a number. §2.8: "The system must retain raw evidence separately from normalized values." — the padded frame number is the raw observation |
| `linked assets` | list of strings |  | `direct` | §2.9 names "linked asset names" among what a creative file yields; a comp project is a graph of them |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an image sequence: many files sharing a stem with a zero-padded incrementing suffix in one directory — a structural family in §4.2's sense, and the single most reliable recogniser in this domain
- a compositing or animation project file whose link list names assets present in the corpus
- a render directory tree organised by shot and pass, identified from the directory manifest

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a rendered MP4 with a generic filename, which is indistinguishable from any other video
- a project file in a proprietary format that §2.9 requires be recorded as indexed-but-unreadable, leaving only the filename and the parent folder

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a directory of many images, which is equally a photo import, a scan batch or a page-image set
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`storyboard`, `animatic`, `project file`, `asset`, `render pass`, `image sequence`, `final render`, `style frame`

### Grouping reasons (§4)

- one shot across its stages, passes and renders
- an image sequence as one object rather than as hundreds of files — a structural family in §4.2's sense
- one project file with every asset it links

### Template (§5)

`project → sequence or shot → animation stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Render passes and frame ranges stay inside the shot rather than becoming levels — a per-pass folder tree multiplies branches without improving retrieval, which is what §5.9's "It should recommend flattening when a dimension does not materially improve retrieval." addresses

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| cg.3d-asset | 3D assets are made for animation and rendered by it; one directory usually holds both and the pipeline is continuous | §3.8: "The system must separate roles that happen to contain the same entity type." |
| film.post-production | titles and graphics are delivered into an edit as media, so the same frames are both an animation output and post media | §4.2: "files linked by duplicate or version relationships" |
| game.art-asset | animation for a game is authored in the same applications with the same file types and differs only in what consumes it | §3.11: "Code files may use project, repository, programming language, and artifact type." |

### Sensitivity

`none` — Nothing here is personal data and no design sentence marks it as "and potentially sensitive".

---

## `cg.3d-asset` — 3D modelling, texturing and rendering

Three-dimensional work — models, textures, rigs, scenes, renders — where the source file is frequently one §2.9 says the engine cannot read.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** §2.9 names "CAD files, and 3D files" in "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text". That is a FORMAT family and a routing fact, not a domain, and this entry is careful to claim only the schema. §2.9's "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" is the operative constraint on everything below.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `asset` | string | Acme bottle | `llm_supported` | The modelled thing. It is the unit of work, of reuse and of version history |
| `asset stage` | string | lookdev | `llm_supported` | Block-out, model, UV, texture, lookdev, rig, scene, render. It is what distinguishes near-identical files in one directory |
| `scene or shot` | string | sh020 | `validated` | Where the asset is used. Kept distinct from the asset itself, because §3.8 requires roles that share an entity type to be separate facets and an asset is not a shot |
| `geometry format` | string | USD | `direct` | Read from the real signature. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning", and here the distinction between a readable interchange format and an unreadable application format decides whether the domain is recognisable at all |
| `texture set` | string |  | `direct` | Texture maps share a stem with a channel suffix, which is a structural family readable without opening anything |
| `render engine` | string |  | `validated` | Read from a render-settings file or an output naming convention. It is a search and explanation field, not a folder level |
| `readability state` | string | indexed-but-unreadable | `direct` | §2.9 requires it: "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty". This domain carries the state as an explicit fact because for most of its files it is the ONLY fact, and a folder built from filenames alone must be marked as such |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a texture set: several images sharing a stem with channel-name suffixes (basecolor, normal, roughness, metallic) in one directory
- an interchange geometry format signature (OBJ, FBX, glTF, USD) whose header yields object and material names
- a project directory whose subdirectory names are a standard 3D pipeline layout, identified from the manifest

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a proprietary scene file §2.9 requires be recorded as indexed-but-unreadable, where only the filename and the folder exist as evidence
- deciding whether a render output is a finished deliverable or a test, which no property of the image records

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a 3D file extension. §2.9 names the family precisely so that it is treated as routing: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — a render has no camera metadata by construction and the absence means nothing

### Work types

`model`, `texture set`, `material`, `rig`, `scene file`, `render output`, `turntable`, `interchange export`

### Grouping reasons (§4)

- one asset across its stages, its textures and its exports
- a texture set as one object, discovered from a shared stem and channel suffixes
- one scene with every asset it references, where the format permits the reference to be read

### Template (§5)

`project → asset → asset stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". This template is unusually dependent on filenames because §2.9's indexed-but-unreadable state removes content evidence entirely, so it is kept shallow: a deeper tree built on filenames alone would assert structure the evidence does not support

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| film.motion-graphics | 3D is authored for animation and the two live in one pipeline directory | §3.8: "The system must separate roles that happen to contain the same entity type." |
| game.art-asset | the same model in the same format is a game asset once a game engine consumes it, and nothing in the file changes | §3.11: "Code files may use project, repository, programming language, and artifact type." |
| design.architecture-visual | an architectural model and a product model are both 3D scenes; the subject is the only distinction | §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |

### Sensitivity

`none` — No design sentence marks 3D work as "and potentially sensitive".

### Open question — Joseph's call, unresolved

> Can a domain legitimately be recognised when §2.9 requires its central file to be recorded as indexed-but-unreadable? §2.9 is explicit that "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty", but for 3D, CAD and several proprietary design and audio formats the unreadable file IS the work; everything readable around it is a derivative. That leaves recognition resting on filename and parent-folder context alone, which §4.9 warns against — "Unreadable, encrypted, corrupted, or unsupported files should retain basic metadata and remain eligible for manual attachment to a user-created group, but the system should not infer a purpose from their filename alone.". So either this catalogue may build a domain on filename-plus-folder evidence, marking every resulting fact as weak, or these domains can only ever be created by the user by hand. This catalogue takes the first position and carries an explicit `readability state` field to make it auditable, but which of the two the product intends is Joseph's call and it applies well beyond this slice.

---

## `game.art-asset` — Game art and interactive assets

Art authored to be consumed by a game engine — sprites, models, animations, audio, atlases — where the source and the imported copy both exist.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names game art. Proposed as the art-side counterpart to the software catalogue's game-development entry, using §3.11's Code row — "Code files may use project, repository, programming language, and artifact type." — as the shape a project-plus-repository domain takes.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `game` | string |  | `llm_supported` | The title. It is usually the repository or project directory name and is rarely inside any art file |
| `asset class` | string | character | `llm_supported` | Character, environment, prop, UI, effect, audio. It is the dimension a game's art directory is actually navigated by |
| `asset` | string |  | `validated` | The named thing, confirmed from a shared stem across a source file, its texture set and its imported copy |
| `pipeline state` | string | source | `validated` | Source, exported, imported, packed. It is the fact that explains why the same asset exists three times, confirmed from the format and the directory position together |
| `engine reference` | string |  | `direct` | An engine's own metadata or import file, which is structured data §2.9 has yield schema keys. It links an imported copy to its source deterministically |
| `platform target` | string |  | `validated` | Compressed variants are produced per platform and are duplicates that must not be merged. A search and explanation field, not a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- an engine metadata or import file sitting beside an art file and referencing it by identifier
- a project directory containing both an art source tree and an engine project manifest
- a sprite atlas plus its coordinate map, which is a structured pair readable without interpretation

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- art in a generic format in a directory with no engine manifest, where only the content suggests a game
- distinguishing a purchased asset-store pack from the team's own art, which is a licensing question with no observable answer

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- presence in a repository, which is equally true of documentation, tooling and test fixtures
- an image of a character, which is equally an illustration or a piece of concept art

### Work types

`concept art`, `model`, `texture`, `sprite`, `animation clip`, `atlas`, `audio asset`, `import settings`, `asset pack`

### Grouping reasons (§4)

- one asset across its source, export and imported copies — a version family whose members are deliberately duplicated by the pipeline
- one asset class across a game
- an art source with the engine record that imported it, which is a structural link rather than a similarity one

### Template (§5)

`game → asset class → asset`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Pipeline state is deliberately not a level: engines impose their own source-and-imported layout and a template that fought it would break the project

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| soft.game-development-asset | the software catalogue owns the game project, its code and its build. This owns the art authored for it, and both live in the same repository | §3.11: "One file may hold facts from more than one domain without losing information." |
| cg.3d-asset | identical source files, identical applications. Only the engine consuming them makes it game art | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.stock-asset-library | purchased asset-store packs are a stock library sitting inside a game project | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — No design sentence marks game art as "and potentially sensitive".

---

## `audio.music-session` — Music recording and production session

A song being made — session files, takes, stems, mixes, masters — where the working file references audio it does not contain and the mix versions multiply.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names music production. §2.9: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" gives the extractor for the audio itself; the session file is the same linked-reference problem §2.9 describes for design formats, and §2.9's "unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty" applies to most session formats.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project or artist` | string |  | `llm_supported` | The record, the release or the artist. It is the top of the tree and is almost never inside an audio file |
| `song` | string |  | `llm_supported` | The unit everything else attaches to. §5.5's parent-context rule makes it the level a take number becomes meaningful under |
| `session date` | date | 2026-03-14 | `direct` | §2.9 has audio yield creation time directly. It is a fact and deliberately not the first template level — see the template rationale |
| `take` | string |  | `validated` | The capture unit. A take number is meaningless without the song, which is §5.5's parent-context rule stated as a field constraint |
| `audio role` | string | stem | `validated` | Raw take, comp, stem, rough mix, mix, master, instrumental. Confirmed from duration, channel count and directory position together — §2.9 yields "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" |
| `mix version` | string | mix 7 | `validated` | Mixes are numbered, numerous and dated, and the number is the only ordering signal. It never establishes which is approved — that is `is approved` |
| `is approved` | boolean-like string | approved | `user_confirmed` | Capped at §3.13's "A user confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user." for the same reason as `studio.revision-round`: nothing in an audio file says which mix was accepted, and the most recently modified is routinely a later re-bounce of an older one |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a session directory whose layout is a known DAW project shape — a session file beside an audio-files directory of same-length recordings
- a set of audio files of identical duration and sample rate in one directory, which is a stem set and a structural family
- embedded audio tags yielding artist, album and track together. §2.9: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present"

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- bounced mixes with generic filenames, which is how most finished audio reaches a filesystem
- distinguishing the maker's own recordings from a reference library or a downloaded track, where tags are absent

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- an audio extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member, which in music is 'mix7_FINAL_master_v2' and orders nothing
- embedded tags on their own — a downloaded reference track carries better tags than the maker's own bounce

### Work types

`session file`, `raw take`, `comp`, `stem`, `rough mix`, `mix`, `master`, `reference track`, `session notes`

### Grouping reasons (§4)

- one song across its takes, stems, mixes and masters — the version family with the largest membership in this slice
- a stem set discovered from identical durations, which relates files no filename relates
- one session date across everything recorded at it

### Template (§5)

`project or artist → song → audio role`

Time first: **no**

A recording session is capture-based, which invites §5.5's "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.". It is nevertheless false here, and deliberately: §5.5's other half is "a parent dimension should provide the context required to understand the child", and a take is meaningless without the song while a song is perfectly meaningful without the date. Session date is retained as a direct fact and as the label of a session grouping inside the song. Contrast `film.shoot-day-media`, where the day genuinely IS the unit because a day's media spans every song equivalent at once

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| pers.music-practice | the personal catalogue owns practice recordings. A phone recording of a rehearsal and a professional take are the same container with the same absent tags | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| audio.sound-design | score and sound design for picture are made in the same applications with the same file shapes; only the picture they attach to distinguishes them | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.stock-asset-library | sample libraries and loops sit inside session directories and are licensed assets rather than recordings | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`none` — §2.9 gates transcription of recorded speech — "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — and that gate applies to any audio, but music recording is not personal data and no blanket marking is made. No handling class is set (§8.4).

---

## `audio.podcast-episode` — Podcast episode production

An episode of a show — the recording, the edit, the transcript, the artwork, the publish record — repeated on a schedule.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names podcasting. Proposed because it is the domain where §2.9's transcript gate bites hardest: "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — a podcast is speech, its transcript is its only searchable content, and the design puts that content behind an explicit policy.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `show` | string |  | `validated` | The series. Read from embedded tags or a feed record, which are labeled fields |
| `episode` | string | S3E12 | `validated` | The unit. A season-episode token is a controlled shape and appears in filenames, tags and feed records alike |
| `episode title` | string |  | `direct` | Read from embedded tags or a feed entry. §2.9 has audio yield "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present" |
| `guest` | string |  | `llm_supported` | §3.8's role separation: a guest is not the host and not the producer, and none of the three becomes a folder level |
| `audio role` | string | host track | `validated` | Host track, guest track, edited episode, published master, promo. Multi-track remote recordings produce one file per participant and they must not merge |
| `publish date` | date | 2026-04-09 | `direct` | Read from a feed record's labeled field. §3.10 forbids fuzzy parsing of any other date-shaped string on the file |
| `transcript state` | string | not transcribed | `direct` | Whether a transcript exists and where it came from. §2.9 makes transcription conditional — "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — so the state must be a recorded fact rather than an assumption |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- embedded audio tags carrying a series name plus an episode or track number
- a set of same-duration audio files in one directory, one per participant, which is a multi-track remote recording and a structural family
- an episode directory containing audio beside a square cover image and a show-notes document

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an untagged recording where only the spoken content identifies the show — and §2.9 gates access to that content behind an explicit policy, so the route may simply be unavailable
- distinguishing an interview recorded for a podcast from one recorded for research or journalism, which is a purpose question about identical files

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- an audio extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- a long duration, which describes a lecture, an interview and a rehearsal equally
- a square cover image, which is also an album cover and a social asset

### Work types

`raw recording`, `participant track`, `edited episode`, `published master`, `transcript`, `show notes`, `cover art`, `promo clip`

### Grouping reasons (§4)

- one episode across its tracks, edit, transcript, artwork and notes — purpose-coherent and content-incoherent in §3.9's exact sense
- one show across its episodes
- a multi-track set discovered from identical durations

### Template (§5)

`show → season → episode`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — an episode number is meaningless without the season and the season without the show. Season and episode LOOK temporal and are not: they are an ordered sequence, so §5.5's capture-based exception does not apply and `time_first` stays false. Publish date is retained as a fact

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| audio.sound-design | music beds, stings and mixing for a podcast are sound design work inside a podcast project | §3.8: "The system must separate roles that happen to contain the same entity type." |
| news.reporting | a reported audio story is journalism and a podcast episode at once, with one recording and two schemas | §3.11: "One file may hold facts from more than one domain without losing information." |
| res.qualitative-coding | an interview recording is a research artefact or a podcast depending only on why it was made | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only, and for a design-given reason: §2.9 puts speech-to-text behind a policy — "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — which marks recorded speech as material the design already treats with restraint. Guest recordings are identifiable individuals speaking. No handling class is set; that is P7's (§8.4).

---

## `audio.sound-design` — Sound design and audio post for picture

Audio made to sit under something else — effects, foley, atmospheres, score, the mix that ties them to picture.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names sound design. Proposed because it is the only domain in this slice whose artefacts are defined by a relationship to a file in ANOTHER domain: a sound stem means nothing without the picture it is timed to, which is §5.5's "a parent dimension should provide the context required to understand the child" expressed across a domain boundary.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `production` | string | Acme — Spring film | `llm_supported` | The picture being scored or mixed. It is the parent this domain has no meaning without |
| `reel or sequence` | string | reel 2 | `validated` | The unit audio post works in, carried in filenames and conform lists |
| `audio element` | string | atmosphere | `validated` | Dialogue, foley, effects, atmosphere, music, mix stem. It is the controlled vocabulary the whole discipline files by |
| `mix format` | string | 5.1 | `direct` | Read from channel count and container metadata. §2.9 has A/V yield "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present", and the channel layout distinguishes deliverables that share every other property |
| `sync reference` | string | 01:00:00:00 | `direct` | Timecode start, read from metadata. It is what relates an audio file to a picture file that shares none of its content |
| `library source` | string |  | `validated` | Whether an element came from a licensed effects library or was recorded for this job. §3.8 keeps the library provider distinct from the sound designer |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- audio files carrying a timecode start that matches a picture file present in the corpus — a structural link across two formats
- a stem set: same-duration multichannel files whose stems carry element vocabulary
- a session or conform list naming reels and picture files that exist in the corpus

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an unlabeled effects recording, which is indistinguishable from any other field recording
- deciding whether a music file is score written for the picture or a temp track from a library

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- an audio extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"
- element-shaped vocabulary in a filename, which effects libraries use as their own naming convention
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`field recording`, `foley`, `effects build`, `atmosphere`, `score cue`, `mix stem`, `final mix`, `conform list`

### Grouping reasons (§4)

- one production across every audio element made for it
- one reel across its elements and mixes
- audio related to picture by timecode, which relates files sharing no content

### Template (§5)

`production → reel or sequence → audio element`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child", and here the parent is in another domain entirely — the production. That is the point of the entry: a sound-design branch that does not sit under its picture is unusable

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| audio.music-session | score is music production; the same sessions, stems and mixes, differing only in being timed to picture | §3.8: "The system must separate roles that happen to contain the same entity type." |
| film.post-production | the final mix is a post deliverable and a sound-design output at once | §3.11: "One file may hold facts from more than one domain without losing information." |
| studio.stock-asset-library | licensed effects libraries sit inside sound-design sessions and are acquired assets rather than authored work | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`none` — No design sentence marks sound-design work as "and potentially sensitive". Recorded dialogue is speech and §2.9's transcript gate applies, but the marking sits on the capture domains where the speakers are.

---

## `write.manuscript` — Book-length manuscript

A book being written — fiction or non-fiction — through its drafts, its structure, its research and its submission.

**Provenance:** **inference** — extends a domain the design does name

**Cite:** Extends the manuscript artefact the design names in a research context — §4.2: "For a research group, it might be a manuscript, abstract, or protocol with a known project identifier" — to authorship outside academia. The extension is that a trade manuscript has no project identifier, no lab and no venue; it has a title, drafts and an agent, and §3.11's Research row "Research files may use project, stage, artifact type, lab, and venue." does not fit it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `work` | string |  | `llm_supported` | The book. A working title changes repeatedly during writing, which is why the version family cannot be keyed on the filename stem in this domain |
| `draft` | string | third draft | `validated` | The named revision. Writers number drafts deliberately and the token is usually in the filename, so a controlled pattern with a context check reaches §3.13's "A validated fact was found by a deterministic rule and passed contextual checks" |
| `structural unit` | string | Chapter 9 | `validated` | Chapter, part, section. Read from document headings — §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information." makes headings a structural read rather than a prose one |
| `genre or form` | string | literary fiction | `llm_supported` | It changes nothing about the files and everything about where they belong; it is a search and explanation field |
| `word count state` | string | complete draft | `llm_supported` | Outline, partial, complete draft, revised, submitted. Deliberately expressed as a state rather than a number, because §3.11's universal facts hold no counts and a catalogue holds no numbers |
| `collaborator role` | string | editor | `user_confirmed` | §3.8: author, co-author, ghostwriter, editor and agent are distinct roles over one manuscript, and "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a long text document whose heading structure is chapter-shaped and repeated. §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information."
- a set of documents sharing a title stem with draft tokens, in one directory
- a writing-application project directory whose manifest lists documents as chapters

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- distinguishing fiction from non-fiction, and a manuscript from a report, which only the prose says
- relating renamed drafts of one book where the working title changed between them, which no stem match can do

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- document length. A long document is equally a report, a thesis, a transcript or a legal bundle
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- chapter-shaped headings, which every textbook, manual and thesis also has

### Work types

`outline`, `synopsis`, `draft`, `chapter`, `revision`, `research note`, `submission copy`, `proof`

### Grouping reasons (§4)

- one work across its drafts — the version family, and the one in this slice most likely to be broken by renaming
- one work with its research notes and outline, which share no content with the text
- one draft across its chapter files

### Template (§5)

`work → draft`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a chapter number is meaningless without the draft and a draft without the work. Deliberately shallow: chapters as folders would create the one-child levels §5.7 makes the engine reject when it validates that a template does not "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| acad.thesis-dissertation | a thesis is a book-length manuscript with drafts, chapters and a supervisor. The academic catalogue owns it because a degree hangs on it; this owns trade and literary authorship. A thesis later published as a book is genuinely both | §3.11: "One file may hold facts from more than one domain without losing information." |
| res.manuscript-preparation | the research catalogue owns manuscripts headed for a journal. The vocabulary, the drafts and the version families are identical; the destination is what differs | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pers.journal | memoir drafts and a private diary are the same prose in the same format, and the personal catalogue's marking is the more protective one | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — No design sentence marks a manuscript as "and potentially sensitive". Memoir and journal material shades into the personal catalogue's territory and its marking should govern there, not be duplicated here.

---

## `write.short-form` — Short-form writing

Essays, short stories, poems, columns and criticism — many small works by one writer, each with its own submission history.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names short-form writing. Proposed because it inverts the shape every other entry in this slice assumes: one writer produces hundreds of small independent works, so the PROJECT dimension §5.5's ordering relies on — "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." — does not exist at all.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `piece` | string |  | `llm_supported` | The individual work. It is the only unit, and its title is usually the document's own first heading |
| `form` | string | essay | `llm_supported` | Essay, short story, poem, column, review, flash. It is the closest thing this domain has to a second dimension and it cannot be read from structure |
| `collection` | string |  | `user_confirmed` | Where a writer has grouped pieces into a book, a pamphlet or a sequence. Only a person defines it |
| `draft` | string |  | `validated` | Short work is redrafted as heavily as long work and with far weaker filename discipline |
| `submission state` | string | under submission | `llm_supported` | Unsubmitted, under submission, accepted, published, withdrawn. It is the fact that makes a folder of small documents navigable and it links to `pub.submission-query` |
| `published venue` | string |  | `llm_supported` | §3.8's role separation: the venue that published a piece is not its author and not its commissioner. Kept as a fact and not made a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a directory of many short documents each with a distinct title heading and no shared stem
- a submission-tracking document listing piece titles that exist as files in the corpus
- a document carrying a standard manuscript-format header block, which is a labeled structure

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- distinguishing a poem from a note, a fragment or a list — a structural test cannot, and this is the single hardest recognition problem in the writing domains
- relating a piece to a collection where the writer's grouping exists only in their head

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- short document length. Every note, snippet and scratch file in a corpus is short
- a directory of text files, which describes notes, drafts, exports and documentation equally
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`draft`, `final text`, `submission copy`, `published version`, `collection manuscript`, `cover letter`

### Grouping reasons (§4)

- one piece across its drafts
- a collection across its pieces, which only the writer's grouping establishes
- one submission round across the pieces sent together and the letter that sent them

### Template (§5)

`form → piece`

Time first: **no**

There is no project to lead with, so §5.5's usual ordering has nothing to order by and form is the only available parent. This is a branch §5.9 exists to warn about — "It should recommend flattening when a dimension does not materially improve retrieval." — and a flat piece-level branch is frequently the right answer

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.manuscript | a collection of essays becomes a book, and the same files serve both | §3.11: "One file may hold facts from more than one domain without losing information." |
| news.reporting | a column and a reported piece are the same document type; the presence of reporting — sources, notes, verification — is the distinction and it lives in adjacent files | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pers.journal | personal essays and diary entries are indistinguishable as documents | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |

### Sensitivity

`none` — No design sentence marks short-form writing as "and potentially sensitive".

---

## `write.screenplay` — Screenplay and script

A script for screen or stage — the one document type in this slice with a strictly machine-readable structure, and the one most often reduced to a flat PDF.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names screenwriting. Proposed because §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information." makes headings and structure extractable, and screenplay format is a rigid heading grammar — scene headings, character cues, transitions — which makes this the most deterministically recognisable text domain in the supercategory.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `script` | string |  | `llm_supported` | The title. Read from the title page, which §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information." makes a structural read where the document is not flattened |
| `draft` | string | shooting draft | `validated` | First draft, revised, production draft, shooting draft, and the coloured revision pages that follow it. Screenwriting has the most formal draft vocabulary of any writing discipline and it is printed on the title page |
| `revision colour` | string | blue | `validated` | The industry's own version-family marker, in a fixed order, printed on the page. It is the only version scheme in this whole slice that is both standardised and self-describing |
| `scene` | string | 14 | `direct` | Read from numbered scene headings, which are a labeled structure rather than prose. §3.13's "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." applies where the heading grammar is intact |
| `format` | string | feature screenplay | `validated` | Feature, television episode, short, stage play, radio. Each has a different heading grammar and the grammar identifies it |
| `writer role` | string | co-writer | `user_confirmed` | §3.8: written by, story by, rewrite, polish. Credit is contested, contractual and never a folder level — "It should avoid using authorship or creator identity as a destination dimension." |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- screenplay heading grammar: scene headings, character cues and transitions in their fixed positions. §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information."
- a title page carrying a labeled draft designation and a revision colour
- a scripting-application project file, or a plain-text screenplay markup file, identified by signature

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a flattened PDF where the heading grammar survives visually but not structurally, which is how most scripts circulate
- deciding whether a script is the writer's own or a read copy of someone else's — the corpus of a working writer contains far more of the latter

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a revision colour word, which is a colour name and appears everywhere
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- screenplay-shaped formatting, which templates and coverage documents reproduce

### Work types

`treatment`, `outline`, `draft`, `revision pages`, `shooting script`, `coverage`, `sides`

### Grouping reasons (§4)

- one script across its drafts and revision colours — a version family with a documented order, which is rare here
- one script with its treatment, outline and notes
- revision pages with the draft they amend, which is a structural relationship rather than a similarity one

### Template (§5)

`script → draft`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Revision colours stay inside the draft as a version family rather than becoming folders, since each contains a handful of pages and §5.7 makes the engine reject a template that would "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| film.production | the script becomes production paperwork once shooting starts, with the same file on both sides of that moment | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| perf.theatre-production | a stage play script belongs to the writer until a production takes it, and then to both | §4.9: "A file may validly belong to more than one accepted group" |
| write.manuscript | an adaptation exists as a novel and a screenplay with one title and two grammars | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No design sentence marks scripts as "and potentially sensitive". Unproduced work is a confidentiality question, raised as an open question on `studio.client-engagement` rather than settled here.

---

## `write.editing-pass` — Editing and proofreading passes

Work done ON someone else's text — structural, line, copy and proof passes — which produces a version family in a document the editor does not own.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names editing. Proposed because §3.8's "The system must separate roles that happen to contain the same entity type." is the whole entry: an edited file names an author and an editor, and treating either as the owner files it in the wrong person's tree.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `edited work` | string |  | `llm_supported` | The text being edited. §3.8 keeps it distinct from the editor: the work belongs to its author |
| `author` | string |  | `validated` | §3.8's authored_by role. A fact and explicitly not a folder level — "A folder should not become a collection point for everything produced by the same person or organization." |
| `pass type` | string | copy edit | `validated` | Developmental, structural, line, copy, proof, fact-check. A controlled vocabulary; each pass is a distinct engagement with a distinct deliverable |
| `markup state` | string | tracked changes | `direct` | Clean, tracked, marked-up, queried, accepted. Tracked changes are a labeled structure inside the document and a direct read where the format exposes them |
| `query state` | string | queries outstanding | `llm_supported` | Whether author queries remain open. It is what makes one of six near-identical files the current one, and it is only in the comments |
| `style authority` | string |  | `llm_supported` | The style guide or house rules governing the pass. It is the fact that explains a change and it lives in a separate document entirely |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document containing tracked revisions or comment anchors, which is a labeled structure. §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information."
- a filename carrying an editor-shaped suffix beside an otherwise identical clean document in the same directory
- a style sheet or query list naming a work that exists in the corpus

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an edit returned as a clean file with no markup, which is indistinguishable from the author's own next draft
- deciding which pass a marked-up file represents, since the vocabulary is not in the file

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the presence of tracked changes, which every collaboratively written document carries
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member
- an editor's name in a filename, which is a convention rather than a fact and is used inconsistently by everyone

### Work types

`marked-up manuscript`, `clean copy`, `query list`, `style sheet`, `proof`, `fact-check report`, `editorial report`

### Grouping reasons (§4)

- one work across its editorial passes — a version family whose members alternate between two people
- one pass with its query list and style sheet, a purpose group in §3.9's sense
- an editor's engagements across the works they worked on, which is a role grouping and not a folder level

### Template (§5)

`edited work → pass type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". The author is deliberately not the first level even though it is the most reliable fact available: §3.8 "A folder should not become a collection point for everything produced by the same person or organization.", and an author folder in an editor's tree is exactly the collector the design warns about

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.manuscript | the same file is a draft to its author and an edit to its editor, and both hold copies. §3.8 makes this a role question, not a duplicate to resolve | §3.8: "The system must separate roles that happen to contain the same entity type." |
| studio.revision-round | an editorial pass is a revision round with a different vocabulary and a different unit | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| write.translation | a translation revision and an editing pass are the same activity over a text that exists in two languages | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`none` — Editing another person's unpublished text is confidential in practice, but that is a contractual state and not §2.9's "and potentially sensitive", which this catalogue does not stretch. See the open question on `studio.client-engagement`.

---

## `write.translation` — Translation project

One text existing in two or more languages — source, target, glossary, memory — where language is a first-class fact rather than a property of the file.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names translation. Proposed because §3.11 already names `language` among "a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status" — so the field exists universally, and this domain is what happens when language stops being a property and becomes the organising relationship.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `work` | string |  | `llm_supported` | The text being translated. It is the parent of both language versions and belongs to neither |
| `source language` | string | ja | `validated` | §3.11 names `language` as a universal fact; this domain requires the PAIR, and the source half is confirmed from the source document's own detected language |
| `target language` | string | en | `validated` | The other half. §3.8's role logic applies exactly: two values of one entity type that are not interchangeable and must be separate facets |
| `translation stage` | string | revised | `validated` | Draft, revised, reviewed, proofed, delivered. Professional translation has a defined stage sequence and a distinct deliverable at each |
| `terminology resource` | string |  | `direct` | Glossaries and translation memories are structured data files. §2.9 has structured data yield schema keys, so they are read rather than interpreted |
| `segment alignment` | string |  | `direct` | A bilingual file's own alignment structure, which is the strongest possible link between two documents that share no characters |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a bilingual interchange file whose structure holds source and target segments together — a labeled structure, read directly
- two documents in one directory with a shared stem and different detected languages
- a translation-memory or glossary file identified by signature, referencing a work present in the corpus

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- relating a translation to its source where the filenames share nothing and the languages share no script
- deciding whether a second-language document is a translation or an independent work on the same subject

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- detected language on its own. §3.11 makes it universal precisely because every file has one
- a language code in a filename, which also marks locale variants of assets, subtitles and builds
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`source text`, `draft translation`, `revised translation`, `glossary`, `translation memory`, `bilingual file`, `certification`

### Grouping reasons (§4)

- one work across its languages — a group whose members share no content whatsoever, which is §3.9's "The documents are content-incoherent but purpose-coherent." in its purest form
- one language pair across a client's works
- a translation with the glossary and memory that produced it

### Template (§5)

`work → target language → translation stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a target language is meaningless without the work. Language leads over stage because a two-language project splits cleanly and a stage does not; §5.9's "It should recommend flattening when a dimension does not materially improve retrieval." governs whether the stage level survives

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.editing-pass | revision of a translation is an editing pass over a text with two authors | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pub.title-production | a translated edition is an edition of a title, and the publisher's record and the translator's record are different views of one work | §3.11: "One file may hold facts from more than one domain without losing information." |
| studio.deliverable-handoff | localised asset sets — subtitles, localised artwork, per-locale exports — are a handoff that is also a translation output | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — No design sentence marks translation work as "and potentially sensitive".

---

## `news.reporting` — Journalism and reporting

A reported story — the assignment, the notes, the recordings, the documents, the drafts, the published piece — where the source material must not be filed like the output.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names journalism. Proposed because §3.8's "The system must separate roles that happen to contain the same entity type." has an unusually sharp consequence here: a source, a subject and a byline are three roles over one story, and §2.9's contact-shaped restraint — "but should normally be privacy-protected rather than used to create folder proposals" — should govern the first two.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `story` | string |  | `llm_supported` | The piece being reported. It is the only thing the notes, recordings, documents and drafts have in common |
| `beat or desk` | string |  | `llm_supported` | The standing subject area a story sits in. It is the closest thing to a project dimension in a domain that otherwise has none |
| `material role` | string | interview recording | `validated` | Assignment, interview, document, data, draft, published piece. It is the fact that decides whether a file may leave the device at all |
| `publication` | string |  | `llm_supported` | §3.8: the outlet that published is not the reporter and not the source. A fact and not a folder level |
| `publish date` | date | 2026-04-09 | `direct` | Read from a labeled field on the published piece. §3.10 forbids fuzzy parsing of the many other date-shaped strings a reported story contains |
| `source protection state` | string | protected | `user_confirmed` | Whether the material identifies a source who must not be identified. Only a person knows, and it is the fact the whole domain's restraint depends on. No handling class is set here; the class is P7's |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a published piece carrying a labeled byline, publication and date together
- a directory containing an assignment or pitch document beside interview recordings and drafts sharing a story stem

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- interview recordings and notes, which carry no story reference and whose content §2.9 gates behind a policy: "and—only under an explicit privacy and compute policy—speech-to-text transcripts"
- distinguishing reporting from research, from a podcast interview and from a personal recording — identical files, four purposes

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a byline-shaped name, which appears in every document that credits anyone
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- an interview recording, which is equally research, oral history, a podcast or a meeting

### Work types

`pitch`, `assignment`, `interview recording`, `interview notes`, `obtained document`, `data set`, `draft`, `published piece`, `correction`

### Grouping reasons (§4)

- one story across its notes, recordings, documents and drafts — purpose-coherent and content-incoherent in §3.9's sense
- one beat across its stories
- an obtained document with the story that used it, which no similarity measure would ever relate

### Template (§5)

`beat or desk → story → material role`

Time first: **no**

§5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." is followed rather than the date-first convention newsrooms use, because a reporter retrieves by story and a date-first tree scatters one story's material across the calendar exactly as §5.5 warns. Material role is the last level and is load-bearing: it is what keeps source material separable from output

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| audio.podcast-episode | a reported audio story is both, with one recording and two schemas | §3.11: "One file may hold facts from more than one domain without losing information." |
| res.qualitative-coding | interview recordings and their notes are the research catalogue's material too; the purpose is the only distinction and the files are identical | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| write.short-form | a column and a reported piece are the same document; the reporting apparatus in adjacent files is the distinction | §3.8: "The system must separate roles that happen to contain the same entity type." |

### Sensitivity

`potentially_sensitive` — §2.9's phrase only, and on the strongest available grounds in this slice: source material identifies individuals, and §2.9 already requires contact-shaped data to be "but should normally be privacy-protected rather than used to create folder proposals" while gating recorded speech — "and—only under an explicit privacy and compute policy—speech-to-text transcripts". The handling CLASS is P7's (§8.4) and is deliberately not set, but this is the entry where getting that class wrong has the highest cost.

---

## `pub.title-production` — Publishing production of a title

A book moving through a publisher — manuscript to typeset pages to printed edition — where the same text exists as a document, a layout and a product.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names publishing. Proposed because it is where three of this slice's format families meet on one work: §2.9: "Text documents such as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text, headings, metadata, links, and structural information.", "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text" for the typeset layout, and a product record that is neither.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `title` | string |  | `llm_supported` | The book. It is the top of everything and outlives every file below it |
| `edition` | string | first edition | `validated` | Editions are a deliberate, documented version family — the only one in this slice with an external authority behind it |
| `production stage` | string | first pages | `validated` | Manuscript, copy-edit, typesetting, first pages, revised pages, press-ready, printed. A controlled vocabulary, confirmed from the artefact type |
| `format` | string | paperback | `validated` | Hardback, paperback, ebook, audiobook. Each is a distinct product with distinct files and they are routinely merged by mistake |
| `product identifier` | string |  | `direct` | Read from a labeled field on a metadata sheet. §2.8: "The system must retain raw evidence separately from normalized values." — it is stored as observed, and §3.10's warning about digit strings that look like other digit strings applies to it directly |
| `contributor role` | string | cover designer | `llm_supported` | §3.8: author, translator, editor, designer, illustrator over one title. None becomes a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a page-layout file or press-ready PDF whose stem matches a manuscript document present in the corpus
- a metadata or title-information sheet carrying labeled title, format and identifier fields. §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."
- a proof PDF carrying page-proof structure beside a manuscript of the same title

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- distinguishing an author's own draft from the publisher's copy of the same text, which are byte-different and semantically identical
- relating cover artwork to a title where the cover file names neither

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a long PDF, which is every report and every bundle in the corpus
- an identifier-shaped digit string. §3.10: documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- the token 'final' | 'FINAL' | 'v2' | 'rev3' anywhere in a filename. It orders members of a version family and nothing else: it identifies neither the work nor the domain, and it is present on every member

### Work types

`accepted manuscript`, `copy-edited text`, `typeset pages`, `proof`, `cover artwork`, `metadata sheet`, `press-ready file`, `ebook package`, `audiobook master`

### Grouping reasons (§4)

- one title across its editions and formats
- one edition across its production stages — a version family with a documented sequence
- a title with its cover, its metadata sheet and its marketing assets, which share no content

### Template (§5)

`title → edition → production stage`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a proof is meaningless without the edition and an edition without the title. Format sits as a fact rather than a level because most titles have one format and §5.7 makes the engine reject a template that would "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.manuscript | the author's manuscript and the publisher's accepted manuscript are the same text held by two parties | §3.8: "The system must separate roles that happen to contain the same entity type." |
| design.print-production | press-ready pages and cover artwork are print production carrying a book's content | §3.11: "One file may hold facts from more than one domain without losing information." |
| design.graphic-project | cover design is a design job commissioned inside a publishing project | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — No design sentence marks publishing production as "and potentially sensitive".

---

## `pub.submission-query` — Submissions, queries and representation

Sending work out — queries, submission packets, agent correspondence, responses — the purpose group that assembles files sharing no content at all.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names literary submission, but §3.9 describes its exact shape for another domain: "The documents are content-incoherent but purpose-coherent.". A submission packet is a synopsis, a sample, a biography and a letter — content-incoherent, purpose-coherent, and assembled for one recipient.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `submitted work` | string |  | `llm_supported` | What is being sent. It links the packet back to the manuscript or piece and is the only shared fact across the packet |
| `recipient` | string |  | `validated` | Agent, publisher, magazine, competition, prize. §3.8 keeps it distinct from the eventual publisher and from the author |
| `submission round` | string |  | `llm_supported` | Work is submitted in batches to many recipients at once, and the round is what makes twenty near-identical letters legible |
| `packet component` | string | synopsis | `validated` | Query letter, synopsis, sample chapters, biography, full manuscript. A controlled vocabulary and the level a packet is navigated by |
| `submission date` | date | 2026-02-20 | `direct` | Read from a labeled date on the letter. §3.10 requires the explicit-regex path |
| `outcome` | string |  | `llm_supported` | No response, rejection, request for full, offer. It is what closes the group, and it arrives as an email rather than as a field |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a letter carrying a labeled recipient and date beside a synopsis and a sample from a work present in the corpus
- a submission-tracking document listing recipients and works that exist in the corpus

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- recognising the packet as a packet, since its members share no content — precisely the case §3.9 says content similarity will split
- an emailed submission and its response, where the whole record is correspondence

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a letter, which is the most generic document type in any corpus
- a recipient-shaped organisation name. §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"

### Work types

`query letter`, `synopsis`, `sample chapters`, `biography`, `full manuscript copy`, `response`, `tracking sheet`, `contract offer`

### Grouping reasons (§4)

- one submission to one recipient across its components — the paradigm §3.9 purpose group
- one submission round across its recipients
- one work across every submission made of it

### Template (§5)

`submitted work → recipient`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". The work leads rather than the recipient, because a recipient folder is the collector §3.8 warns about — "A folder should not become a collection point for everything produced by the same person or organization." — and because a writer retrieves by what they sent, not by who ignored it

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.short-form | the submission copy of a piece is a copy of the piece; the packet claims it by purpose and the writing domain by content | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| career.job-application | a literary submission and a job application are structurally the same packet — a letter, a sample and a biography sent to a recipient | §3.9: "The documents are content-incoherent but purpose-coherent." |
| legal.contracts | a publishing contract that follows an offer is the finance-legal catalogue's instrument and this domain's outcome | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No design sentence marks submissions as "and potentially sensitive", though the correspondence inside them is the material §2.9 already treats with restraint: "while treating addresses and message content as potentially sensitive". No handling class is set (§8.4).

---

## `pub.periodical-issue` — Periodical and issue production

A magazine, journal or newspaper issue — many independent pieces assembled into one dated container on a repeating schedule.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names periodicals. Proposed because the issue is the one container in this slice that is simultaneously a project and a date, which puts it exactly on the boundary §5.5 draws between "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." and its capture-based exception.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `publication` | string |  | `validated` | The title. Read from a masthead or a labeled field and stable across every issue |
| `issue` | string | March 2026 | `validated` | The container. It is a label that happens to be date-shaped, which §3.10's warning about date-looking strings makes a hazard rather than a convenience |
| `section` | string | features | `llm_supported` | Front, features, reviews, back. It is how an issue is actually assembled and how a flat-plan is read |
| `article` | string |  | `llm_supported` | The individual piece. §3.8 keeps its author distinct from the publication and from the commissioning editor |
| `issue artefact` | string | flat-plan | `validated` | Flat-plan, page layout, proof, press file, cover. It is the vocabulary an issue's production files carry |
| `cover date` | date | 2026-03-01 | `direct` | Read from a labeled field and deliberately kept distinct from the publication date, which differs — §3.8's principle applied to two dates rather than two organisations |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a layout or press file whose stem carries a publication name plus an issue-shaped label
- a flat-plan document: a table of page numbers against sections. §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."
- a directory of article documents beside page layouts referencing them

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an individual article file with no issue reference, which is the normal state of a contributor's copy
- distinguishing an issue's own artwork from stock and supplied images inside one production folder

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- an issue-shaped date label. §3.10: documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values", and a cover date is precisely such a string
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`flat-plan`, `article copy`, `page layout`, `proof`, `cover`, `press file`, `contributor brief`, `issue archive`

### Grouping reasons (§4)

- one issue across every article, layout and proof in it — content-incoherent and purpose-coherent
- one article across its copy, its layout and its published page
- one publication across its issues

### Template (§5)

`publication → issue → section`

Time first: **no**

The publication leads, so `time_first` is false even though the issue level is date-labelled. §5.5's exception is for material whose capture date defines it — "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." — and an issue label is an edition name, not a capture date. §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." governs instead

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| news.reporting | the reporter's story file and the issue's article copy are the same text held by two parties with two schemas | §3.8: "The system must separate roles that happen to contain the same entity type." |
| design.graphic-project | page layout and cover design are graphic design work inside a publishing schedule | §3.11: "One file may hold facts from more than one domain without losing information." |
| res.published-article | an academic journal issue is a periodical; the research catalogue owns the article as scholarship and this owns the issue as production | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — No design sentence marks periodical production as "and potentially sensitive".

---

## `media.content-marketing` — Content marketing assets

Written and visual material made to be published by a brand — articles, guides, emails, landing pages — organised by the programme that commissioned it.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names marketing content. Proposed because it is the clearest instance of §3.9's distinction inside this supercategory: "Topic answers what a file is about, while purpose answers what the file was for." — a marketing article and an editorial article are the same document and differ only in what they were for.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `brand` | string | Acme Foods | `validated` | Whose marketing this is. §3.8 keeps it distinct from the agency producing it and from the publisher hosting it |
| `programme` | string |  | `llm_supported` | The standing content effort a piece belongs to. It is the project dimension, and it is named nowhere in the assets themselves |
| `asset type` | string | landing page | `validated` | Article, guide, case study, email, landing page, whitepaper. A controlled vocabulary confirmed from structure and format together |
| `channel` | string | email | `validated` | Where it is published. It determines the format and the size constraints and is confirmed from those rather than asserted |
| `publish state` | string | scheduled | `llm_supported` | Draft, approved, scheduled, live, retired. Marketing corpora accumulate retired assets that are indistinguishable from current ones |
| `campaign reference` | string |  | `llm_supported` | Where a piece belongs to an advertising campaign as well as to a content programme, which links to `media.ad-campaign` |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document or asset in a directory whose siblings carry channel-specific size or format conventions for one brand
- a content calendar or plan listing asset titles that exist as files in the corpus. §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an article, which is a document. Only its purpose makes it marketing and no property records purpose
- distinguishing a live asset from a retired one, which nothing in the file states

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a brand name, which appears in every asset a brand touches and in its competitors' decks
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain
- web-shaped image dimensions, which every screen asset shares

### Work types

`article`, `guide`, `case study`, `email`, `landing page`, `whitepaper`, `content calendar`, `brief`

### Grouping reasons (§4)

- one programme across its assets
- one asset across its channel variants and versions
- a content calendar with the assets it schedules, which is a structural link rather than a similarity one

### Template (§5)

`brand → programme → asset type`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Channel is not a level: it multiplies branches per asset and §5.9 has the engine warn and "It should recommend flattening when a dimension does not materially improve retrieval."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| media.social-assets | the same copy and the same image resized for a feed. The channel is the only difference and it is often just a folder name | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| write.short-form | a commissioned article is a writer's piece and a brand's asset simultaneously, held by two parties | §3.8: "The system must separate roles that happen to contain the same entity type." |
| design.graphic-project | marketing assets are designed artefacts and belong to both by different fields | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — Published marketing material is public by intent. Unreleased campaigns are a confidentiality question raised on `studio.client-engagement` rather than marked here.

---

## `media.social-assets` — Social media assets

Small, numerous, channel-shaped exports of the same artwork — the domain most likely to be mistaken for duplicates, and most likely to lose all its metadata.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names social assets. Proposed because §2.6's warning is about these files more than any others: "Messaging platforms and downloaded web images often strip metadata from real photographs." — social platforms strip and re-encode on upload, so the version that comes back down is metadata-free and re-compressed.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `account or brand` | string | Acme Foods | `validated` | Whose feed this is for. §3.8 keeps it distinct from the agency and from the platform |
| `campaign or series` | string |  | `llm_supported` | The grouping an asset belongs to. Where none exists the asset is always-on content and this field is legitimately empty |
| `channel` | string |  | `validated` | Confirmed from the asset's aspect ratio and duration against channel conventions, which is a pattern with a context check rather than a filename read |
| `asset variant` | string | square | `validated` | Square, portrait, story, banner. It is the fact that explains why one image exists six times and prevents the set being collapsed as duplicates |
| `scheduled date` | date | 2026-04-11 | `llm_supported` | Read from a content calendar rather than from the asset, which carries no date at all |
| `copy text` | string |  | `llm_supported` | The caption that goes with the asset, which lives in a separate document and is the only searchable content the asset has |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a set of images sharing one visual and differing only in aspect ratio, related by perceptual hash. §2.6: "Exact hashes and perceptual hashes can identify duplicates and near-duplicates." — this is the one recogniser that survives platform re-encoding
- a content calendar naming assets that exist in the corpus
- channel-conventional dimensions across a set of siblings in one directory

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a single downloaded asset with no siblings, no calendar and no metadata, which is indistinguishable from any other image
- deciding whether a set is a social asset set or a responsive web asset set, since both are one image at several sizes

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition. This is §2.6's own example territory: a re-downloaded social image has no metadata and is a real photograph or a real design, not a screenshot
- a square or vertical aspect ratio, which is also an album cover, a poster and a phone screenshot
- near-duplicate detection alone, which would collapse a variant set into one file and destroy the deliverable

### Work types

`feed image`, `story asset`, `short video`, `carousel set`, `caption document`, `content calendar`, `template`

### Grouping reasons (§4)

- one visual across its channel variants — a version family whose members are deliberately different sizes of one work, not duplicates
- one campaign across its assets
- an asset with the caption and calendar entry that publish it, which share no content with it

### Template (§5)

`account or brand → campaign or series → asset variant`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". Always-on content has no campaign, so that level is legitimately empty and §5.9's scoped General branch is the right answer rather than a date level or a global catch-all — "A global catch-all folder should not become the product’s default answer to ambiguity."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.graphic-project | a social asset IS the design artwork at another size. The brief said 'and social', and one export step separates them | §3.11: "One file may hold facts from more than one domain without losing information." |
| pers.screenshot | a downloaded social image and a screenshot of a social post are both stripped PNGs of similar dimensions. §2.6 forbids the absence test that would separate them | §2.6: "conflicting signals should lead to abstention rather than an invented classification" |
| media.ad-campaign | paid social assets belong to a campaign and organic ones do not, and the files are identical | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |

### Sensitivity

`none` — Published social assets are public by intent. No design sentence marks them as "and potentially sensitive".

---

## `media.ad-campaign` — Advertising campaign

A campaign as a whole — the idea, the executions, the media formats, the versions per market — where one concept becomes hundreds of files.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names advertising. Proposed because a campaign is the largest single fan-out in this supercategory: one execution becomes every format, market, language and duration, and §3.11's "a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status" gives version family and duplicate family as the only universal handles on it.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `brand` | string | Acme Foods | `validated` | §3.8's client role. Kept distinct from the agency, which is `our_firm` |
| `campaign` | string |  | `llm_supported` | The named idea. It is the only thing hundreds of otherwise unrelated files have in common |
| `execution` | string |  | `llm_supported` | One idea's individual expression. It is the level a version family anchors on, not the campaign |
| `media format` | string | 6-sheet | `validated` | Out-of-home size, print size, broadcast duration, digital unit. Confirmed from dimensions and duration, which §2.6 and §2.9 both make direct reads |
| `market` | string |  | `validated` | Territory and language variant. It is what makes a set of near-identical files legitimately distinct rather than duplicates to resolve |
| `clearance state` | string |  | `user_confirmed` | Whether an execution has been approved to run — legal, compliance, rights. Only a person knows and it decides which of many versions is usable |
| `flight period` | date range | 2026-05-01 to 2026-06-15 | `llm_supported` | When the campaign ran, read from a media plan rather than from any asset |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a set of assets sharing one visual across a spread of standard media dimensions, related by perceptual hash. §2.6: "Exact hashes and perceptual hashes can identify duplicates and near-duplicates."
- a media plan or asset schedule listing formats and markets that match files in the corpus. §2.9: "Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells."
- a directory tree whose subdirectory names are a format-by-market matrix, identified from its manifest

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- the campaign idea itself, which exists only in a deck and a line of copy
- distinguishing a live execution from a rejected route, which look identical and often sit in the same directory

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a brand name, which appears throughout a competitor's deck too
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition
- standard media dimensions, which are shared across every campaign ever made

### Work types

`concept deck`, `key visual`, `execution artwork`, `format adaptation`, `broadcast cut`, `media plan`, `clearance record`, `asset matrix`

### Grouping reasons (§4)

- one campaign across every execution, format and market
- one execution across its formats — a version family whose members are deliberately different shapes of one image
- one market across its localised versions, which links to `write.translation`

### Template (§5)

`brand → campaign → execution → media format`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a 6-sheet is meaningless without the execution and the execution without the campaign. Market is deliberately below format or absent: a market level multiplies the tree by the number of territories and §5.9 has the engine warn where a split creates a large number of tiny folders

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| media.social-assets | paid social executions belong to the campaign and organic posts do not, with identical files | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| film.production | a broadcast execution is a film production in its own right, with a script, a shoot and a post pipeline | §3.11: "One file may hold facts from more than one domain without losing information." |
| design.graphic-project | campaign artwork is design work; the campaign claims it by idea and the design project by artefact | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — A campaign exists to be seen. Pre-launch confidentiality is contractual and is raised on `studio.client-engagement` rather than marked here with §2.9's "and potentially sensitive" phrase.

---

## `art.exhibition` — Exhibition and gallery work

Showing work in a space — the show, the works in it, the documentation, the texts, the install — where the artwork files and the exhibition files are different objects.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names exhibitions. Proposed because an exhibition is a §3.9 purpose group with an unusually literal justification: "The documents are content-incoherent but purpose-coherent." — a floor plan, a price list, a wall text, an install photograph and an artwork image share nothing except that they belong to one show.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `exhibition` | string |  | `llm_supported` | The show. It is the purpose that assembles otherwise unrelated documents |
| `venue` | string |  | `validated` | §3.8: the gallery is not the artist and not the buyer. A fact and not a folder level |
| `work shown` | string |  | `llm_supported` | The individual artwork. It has its own life before and after the show, which is why the exhibition cannot own it outright |
| `exhibition artefact` | string | install shot | `validated` | Floor plan, hang list, price list, wall text, invitation, install shot, catalogue. A controlled vocabulary and the level the show is navigated by |
| `exhibition dates` | date range | 2026-09-04 to 2026-10-18 | `direct` | Read from labeled fields on an invitation or a press release. §3.10 requires explicit patterns |
| `work status` | string | sold | `user_confirmed` | Available, reserved, sold, on loan. It changes nothing in any file and is the fact a gallery actually retrieves by |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document titled 'price list' | 'hang list' | 'checklist' | 'wall text' | 'press release' carrying a venue name and a date range
- a floor plan or hang diagram beside a list of work titles that also exist as image files
- install photographs: camera-original images sharing a bounded capture window at one location. §2.6: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- images of individual works, which are ordinary photographs of objects and carry no exhibition reference
- distinguishing an artist's documentation of their own show from a visitor's photographs of it

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a venue-shaped organisation name, which is also a client, a printer and a stockist
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — install photographs carry camera EXIF and the artwork images supplied by the gallery do not, so one show splits on the metadata test
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"

### Work types

`floor plan`, `hang list`, `price list`, `wall text`, `press release`, `invitation`, `install shot`, `catalogue`, `loan form`

### Grouping reasons (§4)

- one exhibition across every document and image belonging to it — content-incoherent, purpose-coherent
- one work across its documentation and the shows it appeared in, which is a membership rather than a folder
- install photography as a capture run, which §2.6 makes deterministic

### Template (§5)

`exhibition → exhibition artefact`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child". The venue is deliberately not the parent: §3.8 "A folder should not become a collection point for everything produced by the same person or organization.", and a gallery folder collects unrelated shows across years. Individual works keep their own home and appear here by membership, which §4.9 permits — "A file may validly belong to more than one accepted group"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| studio.portfolio-showreel | exhibition documentation is the primary source of portfolio material and the same images serve both | §3.9: "Topic answers what a file is about, while purpose answers what the file was for." |
| photo.commissioned-shoot | install and artwork photography is commissioned photography with its own client and licence | §3.11: "One file may hold facts from more than one domain without losing information." |
| acad.arts-jury-portfolio | a degree show is an exhibition and an academic submission with the same documents | §4.9: "A file may validly belong to more than one accepted group" |

### Sensitivity

`none` — No design sentence marks exhibition records as "and potentially sensitive". Price lists and buyer records are finance and personal material and belong to those catalogues' markings.

---

## `art.printmaking` — Printmaking, editions and physical craft

Work whose output is a physical object made in a numbered edition — prints, ceramics, textiles, bindings — where the files are only ever documentation of it.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names craft. Proposed because it inverts the assumption the whole design rests on: here the file is not the work. The corpus contains only photographs, plans and records OF an object, and §2.6's "Images require their own extraction pipeline because filenames often carry little semantic meaning." therefore applies to almost every file in the domain.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `work` | string |  | `user_confirmed` | The physical piece. Only the maker names it; no file contains it |
| `edition` | string | edition of 30 | `llm_supported` | The run. It is the field that makes prints a documented version family rather than an accidental one, and it is expressed as a run description rather than a count because a catalogue holds no numbers |
| `process` | string | screenprint | `llm_supported` | Screenprint, etching, letterpress, risograph, throwing, weaving, binding. It determines what the intermediate files are and is visible only in the work |
| `matrix or plate` | string |  | `llm_supported` | The physical thing the edition is pulled from — a plate, a screen, a mould, a block. It is reused across works and is the strongest real-world grouping this domain has |
| `state or proof` | string | artist's proof | `llm_supported` | State proofs, artist's proofs and the edition itself. It is printmaking's own version-family vocabulary and it is centuries older than the filename problem |
| `documentation role` | string | artwork shot | `validated` | Artwork shot, process photograph, plan, separation file, edition record. It is the fact that keeps a photograph OF the work separate from the file that MADE it |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a separation or plate file set: several artwork files sharing a stem with colour or layer suffixes, matching a process vocabulary
- an edition record document listing work titles, edition descriptions and dates
- process photographs: camera originals in a bounded capture window at one location. §2.6: "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- a photograph of a finished object, which is the only trace most craft work leaves and which reads as an ordinary photograph
- distinguishing a photograph of the maker's work from a reference photograph of someone else's

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — process photographs carry camera EXIF while a gallery-supplied artwork shot carries none, and the two document one work
- an image of an object, which describes a product photograph, a listing image and a documentation shot equally
- a creative file extension on its own. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning" — the format family it names is a routing fact, not a domain

### Work types

`design file`, `separation`, `plan`, `process photograph`, `artwork shot`, `edition record`, `test print`, `specification`

### Grouping reasons (§4)

- one work across its plans, separations, proofs and documentation
- one matrix across every work pulled from it, which is a physical relationship no file records
- process photography as a capture run

### Template (§5)

`work → documentation role`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child", with deliberate shallowness. Most craft work leaves a handful of files and a deeper tree would create the one-child levels §5.7 makes the engine reject when it checks that a template does not "create meaningless one-child levels"

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| design.print-production | the vocabulary is nearly identical — plates, proofs, separations, editions — and the intent is opposite: production reproduces a design, printmaking makes the artwork through printing | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pers.hobby-collection | craft as a hobby and craft as a practice produce identical documentation. The personal catalogue owns the first | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| design.fashion | textile and garment craft sits in both, with patterns and samples common to each | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — No design sentence marks craft documentation as "and potentially sensitive".

---

## `perf.theatre-production` — Theatre and live performance production

Mounting a show — script, design, rehearsal, technical, run — where the paperwork outnumbers the artefacts and nearly all of it is dated.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names theatre. Proposed because a production is a purpose group of exceptional heterogeneity — §3.9: "The documents are content-incoherent but purpose-coherent." — holding a script, a lighting plot, a costume bible, a rehearsal recording and a programme, which share nothing but the show.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `production` | string |  | `llm_supported` | The show as mounted. The same play produced twice is two productions with two sets of everything |
| `department` | string | lighting | `validated` | Direction, design, lighting, sound, costume, stage management, production. It is how theatre paperwork is actually organised and the vocabulary is standard |
| `production document` | string | lighting plot | `validated` | Plot, plan, cue sheet, prompt copy, rehearsal note, running order, risk assessment. A controlled vocabulary with a context check |
| `production phase` | string | technical | `llm_supported` | Pre-production, rehearsal, technical, run, archive. It changes what a document means: a rehearsal cue sheet and a running cue sheet are different objects |
| `performance date` | date | 2026-11-14 | `direct` | Read from a labeled field on a running order or a programme. §3.10 requires the explicit-regex path |
| `venue` | string |  | `validated` | §3.8: the venue is not the company and not the producer. A fact and not a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- a document titled with theatre vocabulary — 'cue sheet' | 'lighting plot' | 'prompt copy' | 'running order' | 'rehearsal call' | 'get-in' — beside a production title
- a script with scene and character structure sitting beside departmental paperwork in one tree
- a rehearsal recording set: same-location A/V with bounded creation times. §2.9: "Audio and video files should yield duration, container and codec metadata, creation time, embedded tags, subtitles or captions where present"

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- rehearsal recordings and production photographs, which are ordinary media with no production reference
- distinguishing this production's documents from the previous production of the same play, which share every title

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a play title, which is shared by every production of it ever made. §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"
- a four-digit year in a filename. §3.10: file names and documents "frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values"
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition

### Work types

`script`, `prompt copy`, `lighting plot`, `sound plot`, `costume bible`, `model box photograph`, `cue sheet`, `rehearsal note`, `running order`, `programme`, `production photograph`

### Grouping reasons (§4)

- one production across every department — the most content-incoherent purpose group in this slice
- one department across a production's run
- rehearsal and performance recordings as capture runs, which §2.6's reasoning makes deterministic

### Template (§5)

`production → department → production phase`

Time first: **no**

§5.5: "a parent dimension should provide the context required to understand the child" — a cue sheet is meaningless without the department and the department without the production. Time is not a level despite every document being dated, per §5.5's "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| write.screenplay | a stage script belongs to the writer and to the production, one file on both sides | §4.9: "A file may validly belong to more than one accepted group" |
| perf.performing-artist | a performer's own materials for a show they are in — their score, their sides, their recordings — belong to their practice as well as to the production, and they hold their own copies | §3.8: "The system must separate roles that happen to contain the same entity type." |
| film.production | the vocabularies overlap heavily (call sheet, schedule, run) and a filmed performance sits in both | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — Company contact sheets carry the material §2.9 already treats as "while treating addresses and message content as potentially sensitive", but the marking belongs where the personal data is rather than across the whole production. No handling class is set (§8.4).

---

## `perf.performing-artist` — A performer's own practice archive

What a musician, dancer or actor accumulates across a career of dated performances — programmes, parts, recordings, reviews — where the performance is the unit and the date is its name.

**Provenance:** **proposal** — new — the design does not name this domain

**Cite:** No design sentence names a performer's archive. Proposed because it is the one document-and-record domain in this slice that meets §5.5's capture-based exception on its own terms: "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material." — the archive is a run of dated events and its recordings are capture media.

### Schema — the fields this domain, and only this domain, legitimises

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `performance date` | date | 2026-11-14 | `direct` | §2.9 has A/V yield creation time directly and a programme carries a labeled date. It is the field the whole archive is ordered by and the one every artefact shares |
| `performance` | string |  | `llm_supported` | The named event — a recital, a concert, a run, an audition. It is the unit, and the date is its most reliable label |
| `repertoire` | string |  | `llm_supported` | What was performed. It recurs across a career and is the second axis a performer retrieves by, which is why it is a fact and an alternate view rather than the spine |
| `performer role` | string | soloist | `llm_supported` | §3.8: soloist, ensemble member, understudy, deputy. The same person in the same repertoire in different roles has different materials |
| `artefact role` | string | performance recording | `validated` | Part or score, programme, rehearsal recording, performance recording, review, photograph. It is the vocabulary the archive is navigated by within a performance |
| `venue` | string |  | `validated` | §3.8: kept distinct from the ensemble and from the promoter. A fact and not a folder level |

### Recognition

**Deterministic** — a pattern *plus* corroborating context, never a bare pattern (§3.3, §3.5):

- recordings whose container creation times cluster in a single evening at one location — the audio and video equivalent of §2.6's "Camera EXIF, GPS, and capture time can support deterministic photo-event proposals."
- a programme document carrying a labeled date, venue and repertoire list together
- a scanned or annotated part or score sitting beside recordings of the same date

**Needs the LLM** — language interpretation a rule cannot do safely (§3.3, §3.5):

- an untitled recording, which is the majority of a performer's archive and carries only a creation time
- distinguishing a rehearsal from a performance, which differ in intent and not in any observable property

**Never alone** — patterns that over-fire, and what must corroborate them (§3.7, §3.10, §2.6):

- a repertoire title, which recurs across a whole career and merges decades of unrelated events. §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge"
- the absence of EXIF or of any embedded metadata. §2.6: "the system must not mistake the absence of EXIF for proof that an image is a screenshot", and "Messaging platforms and downloaded web images often strip metadata from real photographs." A professional creative corpus is mostly exports, and an export is stripped by definition — a shared or re-encoded performance recording loses its creation time, and its absence does not make it something else
- an audio or video extension. §2.9: "The engine should treat the file extension as a routing signal rather than an assumption about meaning"

### Work types

`part or score`, `programme`, `rehearsal recording`, `performance recording`, `review`, `photograph`, `audition material`, `contract`

### Grouping reasons (§4)

- one performance across every artefact from it — a capture run plus the paperwork around it
- one repertoire across a career, which is a membership view rather than a folder
- recordings related by a single evening's creation times, which §2.6's reasoning makes deterministic

### Template (§5)

`performance year → performance → artefact role`

Time first: **yes**

§5.5's exception applied deliberately: "Photos and capture-based media are the major exception: time often belongs first because capture date is a defining aspect of the material.". A performer's archive is a run of dated events and its central artefacts are recordings whose creation time is direct and whose other facts are usually absent. Repertoire is the obvious alternative spine and is rejected: the same work performed across twenty years would merge two decades into one folder, which is the collector failure §5.7's validation checks for. Repertoire is retained as a fact so the alternate view stays available

### Collides with

| domain | signal that separates them | cite |
|---|---|---|
| perf.theatre-production | a performer in a production holds their own copies of production material; the production owns the show and the performer owns their career record of it | §3.8: "The system must separate roles that happen to contain the same entity type." |
| pers.music-practice | the personal catalogue owns practice recordings. A professional's practice recordings are the same files and the distinction is the person's, not the file's | §4.9: "It should not form a supported group when there is no valid anchor, when the graph is connected only by embeddings, when one high-frequency entity acts as the only bridge" |
| acad.arts-jury-portfolio | recitals and juries taken for credit are academic submissions and career artefacts at once | §3.11: "One file may hold facts from more than one domain without losing information." |

### Sensitivity

`none` — §2.9's transcript gate — "and—only under an explicit privacy and compute policy—speech-to-text transcripts" — applies to any recording, but a performer's own archive is not personal data in §2.9's sense and no blanket marking is made. No handling class is set (§8.4).

---
