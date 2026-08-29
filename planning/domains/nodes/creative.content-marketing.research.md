# Research memo — `creative.content-marketing`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/creative.content-marketing.json`
Roster row: template on the fieldless `creative` schema, `parent_id: null`, `launch: placeholder`, absorbing the legacy row `media.social-assets`

## Result

**Node accepted, on one leg only, and the memo says which.** The row passes the node test on its **detection signals** and on its **privacy rules**. It **fails** the dimensions leg and does not pretend otherwise: its recommended order is the creative anchor's default, unchanged. CONNECTION.md §2 requires that detection signals, recommended dimensions, **or** privacy rules differ; two of three is a pass, and claiming three would have been the padding this pass exists to prevent.

A fact that shaped everything below: **the string `marketing` does not occur anywhere in `planning/00-database-agent-product-design.md`.** I checked. There is no design sentence about this world, no residual named for it, no worked example. Every claim here is therefore `inference` from named real document types plus 00's general rules, and the JSON's `provenance` is `inference` throughout. The one `design` provenance in the file is on the residual routings, where 00 does speak verbatim.

## THE CHARGE — the strongest case that this row should not exist

I owe this first, and it is a serious case. Six attacks, in ascending order of force.

**1. It is a medium, or a length.** "Blog post, email, landing page, social post" are formats and lengths. The anchor already rules that the whole media-form vocabulary — poster, showreel, stem, cut, edition — is **values of `artifact_type`**, and that no sibling may ask for a node per media form. *Defeated:* the row is not defined by any of those. Its defining objects are a forward-dated calendar, a slug, a search brief and a performance export, none of which is a medium. I have also **enforced the anchor's rule against myself**: the JSON's `template.why` explicitly forbids a `channel` dimension and records that blog/newsletter/social are `artifact_type` values.

**2. It is a work_type value on a neighbour.** "Content" could simply be a value of `artifact_type` under `creative.client-engagement` or `business_operations.go-to-market`. *Defeated, narrowly:* a value cannot carry an editorial calendar whose rows are pieces **that do not yet exist**, and cannot carry a privacy posture that differs in kind from its parent's. Both survive as row-level properties.

**3. It is an organisation name — never-alone evidence.** A brand publishes; is this row anything but "files with a brand's name on them"? *Defeated by 00 itself*, and I made the defeat explicit in `never_alone`: a brand name in this world appears as publisher, as the client the programme is run for, as a customer quoted in a case study, as a competitor in a search brief, and as a platform. That is a direct read-across of 00's Columbia sentence — "A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization." The row never activates on a name.

**4. It is a duplicate of `creative.ad-campaign`.** Both hold material a brand publishes; both are commissioned; both produce sets of resized artwork. This is the hardest attack and I nearly refused on it. *Defeated on a checkable discriminator:* advertising pays for placement on someone else's property, and the paperwork proves it — standard display-unit size matrices, a placements-and-flight-dates plan, a budget, a platform ad-account export. This row publishes on property the brand owns, and its paperwork proves that instead — a slug, a canonical URL, a send with a list, an editorial calendar, an owned-page analytics export. Neither set of artefacts is a subset of the other. The mixed fixture (one artwork resized for both an ad unit and an organic post) is real and is recorded as NJ-CM-1, not smoothed.

**5. It is defined by an absence** — "the marketing that isn't paid." *Defeated:* it has four positive structures nothing else has (calendar, slug/frontmatter, search brief, published-performance export). And I encoded the trap in `never_alone`: "the ABSENCE of a media plan or a paid placement spec read as proof that material is editorial rather than advertising."

**6. It is a duplicate of its own schema's default template.** This is the attack that partly lands, and the memo concedes it. A content programme is a `project`; a draft is a `stage`; a blog post is an `artifact_type`. On the dimensions leg this row **is** the default template and adds nothing. It survives only because the other two legs carry it — see below.

**Verdict: accept.** But note the shape of the acceptance: had 00 or the anchor made privacy uniform across the creative family, attack 6 plus attack 4 would have been enough to refuse and route the coverage to `creative.ad-campaign` plus the Reading Inbox and Independent Records residuals. The row is kept on evidence, not on the roster id.

## The node test, all three legs

**Leg 1 — detection signals: DIFFER.** The anchor's default detection is linked-asset structure, layer/artboard structure, revision rounds, briefs, delivery sets, production paperwork, scripts, timelines, indexed-but-unreadable proprietary formats, releases, catalogue sidecars. Four of this row's signals appear in none of them:

- the **editorial calendar** — rows whose publish dates have not arrived. Every other creative object records something that has happened or is being made; this one enumerates artefacts that do not exist yet. A project plan with predecessors and percent-complete is a different object and is `business_operations.project-delivery`'s.
- the **frontmatter/slug/canonical-URL** interior — a source file whose inside names the permanent public address the piece will occupy. The anchor's linked-asset signal is a file naming media it does not contain; this is a file naming a *location* it does not occupy. Different structure, different consequence.
- the **search brief** — a specification of a piece addressed at a public index (target query, search intent, target length, competitors to outrank, required internal links). A client creative brief is addressed at a commissioner and has fee and deliverables slots instead.
- the **published-performance export** — evidence *about* a piece after publication, keyed by page path or send id. The rest of the creative family ends at delivery and has no post-hoc evidence shape at all.

The remaining signals (CMS export, email send, channel variants, outward approval, gated-asset cluster) are recognisable as specialisations of anchor shapes and are written as such, not oversold.

**Leg 2 — dimensions: DO NOT DIFFER.** `dimension_order: []` by contract, and the prose recommendation is the anchor's own (client where genuinely multi-brand → project as the programme → stage → artifact_type). Two corrections are owed upward and are recorded in the JSON rather than acted on: no `channel` level (media are `artifact_type` values, and a channel level is the collector shape 00's validator rejects when it must not "create meaningless one-child levels"), and this row's stage vocabulary is calendar-shaped (drafting / in review / scheduled / live / updated) rather than approval-shaped, which is a difference in **values** and therefore not a field and not a node.

`time_first: false`, and this deserves its own sentence because the temptation here is the strongest in the family: the editorial calendar is a **period axis lying on the table**. It is a trap. The calendar is one artefact that *plans* the pieces; the pieces do not live on it. 00 settles the general case — "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders" — and the anchor grants the capture-based exception to exactly two siblings (`shoot-day-media`, `raw-photo-catalogue`). This row has no capture evidence and does not claim the exception. A year-first tree would separate a piece from the brief that specified it and the report that measured it.

**Leg 3 — privacy rules: DIFFER, in kind.** The anchor's creative posture protects the maker's **unreleased work**, which stops being sensitive the moment it ships. This row's two sensitive members never stop: a **recipient/subscriber list** (thousands of email addresses, names, signup sources, consent states — personal data about people who are not the user and who cannot consent by the holder possessing the file), and an **unapproved draft quoting a named individual at a named customer**. Publication makes neither harmless; one of them is sensitive precisely *because it is a list rather than a document*. That is why `sensitivity: potentially_sensitive` is taken for a row whose material is overwhelmingly destined to be public, and why `Protected Records` is in `falls_through_to` alongside the ordinary residuals. Enforcement is 00's — "Privacy policy must be enforced before content reaches any model or external connector" — with the concrete consequence written into the JSON: a recipient list must never be summarised remotely to name a programme.

## Files considered and REJECTED

Naming what this row holds proves nothing. These are the tempting false positives.

- **`The-Rise-of-Embedded-Finance-2026.pdf`** — a downloaded third-party report with a designed cover and a gated-download filename. It has the *look* of this row's best gated asset. Rejected: no slug, no calendar row, no draft history, no performance export keyed to it. Routes to Reading Inbox, and `business_operations.market-research` sends it to the same place — the two rows agree.
- **A received newsletter (`.eml`)** — it has a preheader, merge-rendered greeting and an unsubscribe footer, i.e. every surface feature of an owned send. Rejected, and encoded as a `never_alone`: those features prove someone publishes, not that the holder does.
- **`docs/getting-started.md`** — frontmatter, title, description, prose. Byte-shape-identical to a blog post source. Rejected on ancestor evidence: version-control and package manifests, a static-site build config, fenced CLI blocks, and no slug or publish date.
- **`Q3_Launch_Banner_300x250_v4.psd`** — sits in the same launch folder as this row's blog draft. Rejected: a standard display-unit size matrix plus a placements-and-flight plan is advertising. A shared launch token discriminates nothing.
- **`Byline - essay on remote work - final.docx`** — published, edited, professional writing by the same person who runs the programme. Rejected: personal byline, external editor's marks, destination not owned by the brand.
- **A saved competitor blog page (`.html`)** — an HTML file with editorial prose. Rejected: `.html` alone is a saved page, an email template and an export; it is in `never_alone`.
- **A contacts export or CRM contact list** — rejected outright as programme evidence. Contact rows are not made evidence by proximity to a send.
- **A brand style guide PDF** — kept only when it is an *editorial voice* guide inside a programme neighbourhood; a visual identity guide is `creative.brand-identity`'s and is not claimed.
- **An analytics CSV with no page-path key** — rejected; the same table is a product usage export and a finance report. It becomes evidence only when its key column resolves to a piece already anchored.
- **A folder named `Marketing/`** — rejected as a fact. 00 lets it steer retrieval ("Existing curated folders and user-entered labels should influence retrieval because they represent the user's vocabulary") and no further.
- **A stock photo library and a font file** — the anchor already routes these to `creative.stock-asset-library`; proximity to a social set does not move them.

## The collision fixture

The formal one is **`docs/getting-started.md`**: a Markdown file whose delimited frontmatter block, title, sidebar description and heading-structured prose are indistinguishable *inside the file* from `how-to-choose-a-payroll-provider.md`. What discriminates it is entirely outside the file — repository markers and a build config in an ancestor directory on one side; a slug, a canonical URL, a publish date, or a calendar row naming the title on the other. Neither this row nor `code.software-project` may read the frontmatter delimiter itself as proof, and the JSON says so on both sides.

The second, arguably harder one is **`Q3_Launch_Banner_300x250_v4.psd`**, because it fails to be this row's evidence while sitting in this row's folder, made by this row's person, for this row's launch.

## Reciprocal boundaries

Eight `collides_with` edges, each written in both directions and naming the same fixture on both sides. Three of them **reciprocate edges that landed rows already authored against me** — I adopted their wording rather than inventing a second vocabulary:

- **`business_operations.go-to-market`** wrote: "an editorial calendar, a content brief, or an asset production trail supports the content row; the launch plan and readiness record that commissioned it supports this row." Adopted verbatim in sense. Its `open_question` records the boundary as one-way pending this file (its NJ-BO-GTM-1); this file closes that half.
- **`business_operations.market-research`** wrote: "an editorial calendar, a channel, a designed layout and an external audience supports the creative row; an internal decision audience supports this row." Adopted unchanged, plus the reciprocal duty I owe it: I must not claim a research workbook because a published report quotes its numbers.
- **`creative.podcast-episode`** authored `also_holds_with` against me: "Content-marketing owns campaign purpose and distribution context; this template owns the audio lifecycle." Reciprocated as `also_holds_with`, not as a collision.

The five I authored first: `creative.ad-campaign`, `creative.short-form-writing`, `creative.creative-brief`, `code.software-project`, `career.portfolio-work-samples`, and `photos.screenshot-captures`. All three of the assignment's `must_consider_neighbors` (career, code, photos) are answered at template granularity rather than schema granularity, which is the more useful boundary.

## `proposed_fields`: deliberately empty

The creative anchor already proposes `project`, `stage`, `artifact_type`, `client` for R1c. A template may not duplicate its schema's fields, and this row mints nothing. One candidate was seriously considered and **rejected**: `channel`. A content programme's most-used real axis is blog / newsletter / social / landing page — but the anchor's ruling that media forms are values of `artifact_type` is exactly right here, and a `channel` key would be the 574's one-concept-two-vocabularies failure. Rejected. `campaign`, `slug`, `publish_date`, `audience` were rejected on the same principle or as values.

## Deliberate non-edges

- `creative.brand-identity` — a voice guide beside a visual identity guide is adjacency, not same-evidence confusion.
- `creative.stock-asset-library` — the anchor already routes library assets; no ambiguity to arbitrate here.
- `business_operations.customer-account-management` — recorded as an `also_schema` on the customer-story fixture, which is the honest shape; not elevated to an edge from a fieldless row.
- `research.reading-library` — the Reading Inbox residual already carries the third-party-publication case and both competing rows agree on it; a mutex would add nothing.
- `creative.revision-round` — a cross-cutting sibling whose object is the round itself; this row's drafts join rounds without contest.

## NEEDS-JOSEPH

1. **NJ-CM-1** — the `creative.ad-campaign` boundary is one-way (that row has no node file). R1c should confirm the paid-placement-versus-owned-property discriminator reciprocally and decide the genuinely mixed artwork resized for both an ad unit and an organic post.
2. **NJ-CM-2** — `media.social-assets` is absorbed here on the argument that per-platform cutdowns are channel variants of one stem. If real corpora show social assets living entirely apart from any calendar, send or slug — a pure asset library — the alternatives are `creative.stock-asset-library` or `creative.deliverable-handoff`, and this row shrinks to written-and-published material.
3. **NJ-CM-3** — a subscriber/recipient list is personal data about many third parties and is not a making record at all. Alternatives: (a) keep it here with a protected posture, as written; (b) route it out of the creative family to a records row; (c) treat any list-shaped file of contact rows as a cross-cutting protected object regardless of which domain activates. This row cannot settle it.
4. **NJ-CM-4** — a published piece is often **revised in place** years later at the same URL, so its stage returns from live to drafting and the version family has no final member. The anchor's stage progression assumes a terminus; this world has none. A values problem today, a dimensions problem if fields ever land.

## Self-verification

- `python3 -m json.tool` parses the node file.
- Every span in quote marks attributed to 00 was grep-verified verbatim against `planning/00-database-agent-product-design.md` by a script that extracted the quoted strings from the JSON and searched for each; all matched.
- `marketing` confirmed absent from 00 — no design provenance was claimed for any substantive assertion.
- All eight `collides_with` ids, three `also_holds_with` ids and the schema id verified present in `planning/domains/roster.json`.
- All four `falls_through_to` names are 00 residual homes, quoted from 00's own residual paragraph.
- Every `file_examples.source_type` is drawn from `SOURCE_TYPES`; no file example writes a folder path as a fact; `facts_legal` is empty on every fixture because the schema declares no fields.
- Files written: only the two assigned paths. No roster, canonical-fields, neighbour-node, `src/`, `check.py` or SPEC file was touched, and `planning/29-DOMAIN-OWNERSHIP.md` was not edited.
