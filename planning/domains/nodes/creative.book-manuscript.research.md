# creative.book-manuscript — lab notes (R1b)

Date: 2026-08-27
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: creative`, `launch: placeholder`, `parent_id: null`.
Output: [`creative.book-manuscript.json`](creative.book-manuscript.json).
**SALVAGE ROW.** A JSON existed with no memo. It was verified line by line, repaired in four places,
and is now owned as if written here. The repairs are itemised in *What I changed in the salvaged
draft*, below.

**Verdict: `refuse_node: false`.** The row survives on the **first leg only** — a compile container
that enumerates ordered members of its own kind, plus a front-and-back-matter apparatus bracketing a
repeated section level. Neither structure is declared by the creative schema's default template and
neither can be reduced to a length, a word, a format or a stage. The **second leg is conceded**: this
row's dimension recommendation is the schema default unchanged, plus one prohibition. The **third leg
is argued but partial**, and its residue is NJ-BM-1.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from
  `make_prompt.py creative.book-manuscript` — the six depth requirements, the node test, the closed
  edge vocabulary, and the `one_line_hint` naming the absorbed legacy row `write.editing-pass`.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -c -F` only,
  never streamed. Seventeen spans checked; the audit is at the bottom.
- `planning/domains/nodes/creative.json` (full) — the schema anchor and, per the brief, the **default
  template** this row is measured against. It is where both legs were decided.
- `planning/domains/nodes/creative.screenplay.research.md` — the depth calibration, chosen because it
  doubles as a reciprocal boundary: a landed sibling on my own schema that had already argued a
  boundary against me, and whose NJ-SCREENPLAY-1 names this row by id.
- `planning/domains/CONNECTION.md` at the `also_holds_with` rows only (line 242, quoted below);
  `roster.json`, which mechanically confirmed the row, **all eleven** edge targets, every
  `also_schema` value and every residual name; and four landed creative siblings read at their key
  sets and `also_holds_with` only, to fix the house key order.

I did **not** read `01-product-design-structured.md` (`00` wins by rule), nor the other 37 creative
siblings. Reading forty siblings to place one row would have been the wrong spend.

## THE CHARGE, taken first

I was asked to state the strongest case that this row should not exist. That case is six cases, and
five of them land.

**1. "Book-length" is a LENGTH, and a length is a value.** This is the charge in its purest form and
it is fatal to the row *as named*. A length is not an organizational situation; it is a scalar
property of a file, and the node test's own rule — that work types and file extensions are values,
not nodes — applies to it identically. A row that says *the long ones go here* has invented nothing.
**Conceded in full.** No threshold, page count or word count appears anywhere in the node, and
`never_alone` bars them by name so that none can be introduced downstream.

**2. "Manuscript" is a DOCUMENT-TYPE WORD owned more heavily by a neighbour.** The creative schema's
own `work_types` already lists **"manuscript draft"** as a value, and the token is polluted:
`manuscript_R1_clean.docx` is a journal article in a revision round, which is
`research.manuscript-publication`'s. **Conceded in full**, and the word is the first entry of this
row's `never_alone`.

**3. It is a MEDIUM, and its formats are a routing signal only.** `00` requires the engine to "treat
the file extension as a routing signal rather than an assumption about meaning". `.epub` and `.scriv`
feel book-specific and are not — the first is also every purchased ebook, the second is also a
screenplay, a podcast series bible or a thesis. **Conceded**; extension-alone is barred.

**4. It absorbs a LIFECYCLE STAGE.** The `one_line_hint` says this row absorbs `write.editing-pass`.
An editing pass is a stage, and `creative.revision-round` was **already refused** on exactly that
evidence. **Conceded**: the absorbed coverage survives as `version_family` plus P9 graph structure and
explicitly **not** as a stage node. The editorial-return pair is a detection signal for *this row's
group* and the JSON says in terms that it does not reopen the refusal.

**5. It duplicates its own schema's default template.** The schema declares a REVISION-ROUND signal
(a version token across a run of same-stem files plus a same-stem export) and a BRIEF signal. A book
in drafts trips the first; a book proposal looks like the second. **This is the charge that had to be
defeated and it is the reason the row exists.**

**6. It is a duplicate of `creative.short-form-writing` distinguished only by charge 1.** If length
is the only seam, the two rows are one row. **This is the second charge that had to be defeated.**

### Defeating 5 and 6: the compile container

There is exactly one structure in this material that is not a length, not a word, not a format and
not a stage: **a container file or manifest that enumerates ordered members of its own kind, in
reading order.** An InDesign book file (`.indb`) listing member `.indd` documents in page order. A
writing-app binder manifest naming a draft folder of ordered documents. An EPUB package spine. A
LaTeX master whose `\include` lines name chapter sources in sequence. A `book.toml` naming chapter
sources in order.

This is a **different structure** from the schema's LINKED-ASSET signal, which it would otherwise be
mistaken for. `00`'s licensing sentence for that signal reads: "Design and creative formats such as
PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format,
dimensions or canvas properties, embedded metadata, layers or artboards where accessible, **linked
asset names**, and preview text". A *linked asset* is media of a **different kind** that the file does
not contain. Here the enumerated members are the **same kind** as the container and carry a **reading
order** — a Premiere project references clips, a Logic session references audio, and none of them
enumerate documents in a sequence that *is* the work.

That defeats charge 6 as well, and defeats it without touching length: a short-form piece has nothing
to compile, because it is not assembled from ordered same-kind parts. The seam is **assembly**, not
size. A twelve-page chapbook with a compile container is this row; a 200-page standalone essay
without one is not.

The second structure, weaker but real, is the **book apparatus bracket**: front matter and back
matter wrapped around a repeated same-level heading run — title page, copyright or CIP block,
generated contents, running heads pairing work title with section title, chapter-scoped notes,
bibliography, index. `00` licenses the observation directly for this file class: "Text documents such
as PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, and OpenDocument files should yield full text,
headings, metadata, links, and structural information." Note what this is **not**: an apparatus is
present or absent. It is not a count.

## The node test, all three legs

**Leg 1 — detection signals. PASS, and the row stands on this leg.** The schema's twelve
deterministic signals were checked one by one against the compile container and the apparatus
bracket; neither appears. The closest is LINKED-ASSET, separated by same-kind/reading-order above.
The ordered same-stem section run is the schema's universal version-family evidence and would **not**
on its own carry this leg — which is why the JSON's third signal requires the run to be **resolved by
a compile container, a full-manuscript sibling or a compiled output of the same stem**. Unresolved,
the run is a run.

**Leg 2 — dimensions. CONCEDED. This row does not differ from the schema default.** Stated plainly
because the brief asks for the honest answer, not the flattering one. `dimension_order` is `[]` for
all 38 creative siblings by construction: a dimension may only branch on a field the schema declares
(D6, `_CONTRACT` rule 8) and the creative placeholder declares none (D1 as narrowed, rules 10 and 15,
CONNECTION PR-6). I tested the leg the only honest way — by asking what this row would recommend if
option (b) of NJ-R1a-1 landed. The answer is **the default order unchanged**: `client` (normally
absent, because a book usually has no commissioning party) → `project` (the book title) → `stage` →
`artifact_type`. Not time-first, per "For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders" —
and a book is the extreme case, since a work drafted across several calendar years would be shredded
by a year-first order.

The one thing this row adds is a **prohibition, not a level**: the ordered section must never become
a folder level. A per-chapter branch is `00`'s named validator failure twice over — it would "create
meaningless one-child levels" and would "produce empty branches when tested against the accepted
group" for every chapter not yet written. `00`'s parent-context rule is the reasoning: "a parent
dimension should provide the context required to understand the child", and "A work type such as
Homework 3 is meaningful only after the course is known, and a course code may require the school or
term to disambiguate it." Chapter 12 is meaningless without the book in exactly that way. Whether a
prohibition is expressible in the template contract at all is NJ-BM-2.

**Leg 3 — privacy. ARGUED, PARTIALLY.** The schema's unpublished-work posture already names "a
manuscript before submission" by name, so simply repeating it would be no difference at all. The
difference this row claims is narrower and, I think, real: **the sensitive third-party data is inside
the work's own text, not in a separable sidecar.** A memoir names living family members; a biography
or an investigative book names subjects who never took part and never consented to anything; a novel
drawn from life carries recognisable people under thin cover. In every other creative row the
identifying material sits in a detachable artefact — a model release, a call sheet, a cast list —
which can be handled apart from the work. Here it cannot: redact the names and the book is gone.

The handling consequence is concrete rather than rhetorical: **there is no safe excerpt.** The usual
expedient of sending a bounded passage out for enrichment is unavailable to this row specifically,
because any excerpt of a memoir *is* the sensitive content. Against that: "Privacy policy must be
enforced before content reaches any model or external connector."

I mark the whole of this leg **inference, not design** — `00` does not discuss manuscripts as a
privacy class — and I flag honestly that it overlaps the protection `creative.journalism-reporting`
claims for sources. The distinction offered is *subjects who never took part* versus *sources who
spoke under an expectation*. If R1c judges those indistinguishable, the row keeps the node on leg 1
alone and this paragraph reduces to an inherited posture. That is NJ-BM-1.

## What I changed in the salvaged draft

The draft was strong — a full fixture set, eleven argued edges, a genuine collision fixture — and it
was **not** discarded. It carried four defects, all repaired:

1. **A FABRICATED `00` ATTRIBUTION.** The compile-container signal attributed the string *"placed
   images, linked footage, referenced samples, external textures, imported fonts"* to `00` "in the
   design-format extractor sentence." `grep -c -F` returns **0** for that span in `00`. It is
   `creative.json`'s own illustrative prose. Repaired: the signal now quotes the real `00` sentence
   verbatim (count 1), names "linked asset names" as the operative span, and states in the node that
   the earlier attribution is withdrawn. This was the most serious defect and the one that most
   justified the salvage instruction — an unverified quotation in a landed row propagates.
2. **NO `provenance` ON ANY EDGE.** All eleven `collides_with` entries were `{domain, signal}` only.
   Landed siblings carry `{domain, provenance, signal}`. Repaired: `provenance: "inference"` on all
   eleven. (The edges were *not* bare strings — the draft had avoided the defect the brief warned
   about — but they were incomplete objects.)
3. **`also_holds_with` POPULATED ON A TEMPLATE ROW.** Four entries. CONNECTION line 242 restricts
   the edge to "schema ↔ schema only", and `_CONTRACT` rule 14 says the same; one entry
   (`creative.journalism-reporting`) was doubly illegal, being template-to-template. Emptied, losing
   nothing: the three schema-level readings (legal, career, photos) are **already declared by the
   creative schema anchor itself**, so restating them duplicated a parent's assertion, and each is
   now carried where a template legally may — as `also_schema` on the fixture holding the double
   reading. The journalism reading has no legal home and became NJ-BM-5.
4. **AN EDGE POINTING AT A NODE REFUSED THIS WEEK.** The draft edged `creative.screenplay`, which is
   `refuse_node: true`. Its memo's NJ-SCREENPLAY-1 names this row as the holder of the dangling edge
   and recommends re-pointing at `creative.film-production` / `creative.theatre-production`. **Taken,
   on my own side only**, with the same fixture pair (`MidnightRiver_*`) and the same discriminator
   preserved. One edge, not two: the discriminating evidence item against theatre is identical, and a
   second edge would record nothing new.

Also added to match the landed key set: `proposed_context_terms` (27 book-apparatus and
book-workflow terms not already on the schema), `also_holds_with_note`, `role_split_note`.

**Verified and left alone:** all eleven neighbour ids resolve to `roster.json` (**no dangling id** —
the sibling-salvage defect the brief warned about is absent here); all five residual names are among
`00`'s nine; all seventeen fixture `source_type`s and all eleven `file_kinds.source_types` are in the
fourteen-member `SOURCE_TYPES` list; every `also_schema` value is a roster schema id; `fields: []`
and `proposed_fields: []` are correct for a placeholder; every fixture carries "a folder path" in
`must_not_conclude`; no threshold, score or handling class appears anywhere.

## Files considered and rejected

Seventeen fixtures are on the node. The tempting false positives, and why each is not this row's
evidence:

- **`The Overstory - Richard Powers.epub`** — the principal collision fixture; treated below.
- **`Dissertation - Full Draft - Chen.docx`** — front matter, chapter run and bibliography,
  structurally *identical* to a non-fiction book draft. Rejected on the **degree apparatus**: a
  committee approval page, a formatting-compliance checklist, a programme and degree on the title
  page. That is `research.thesis-dissertation`'s.
- **`manuscript_R1_clean.docx`** — carries the row's own defining word and is a journal article.
  Rejected; kept on the node precisely to prove the word activates nothing.
- **`Scan_typescript_1974_p001.jpg`** — an ordered page run of hundreds, which may equally be a will,
  a ledger or a family album. `photos.scanned-documents` owns the scan family; this row claims the
  members only where a title reference or a same-stem transcription resolves them.
- **`nightwork-book/`** — a repository whose `book.toml` enumerates chapter sources in reading order.
  The container *is* this row's signal, but the enclosing structure is a preserved repository root
  and `code.software-project` owns it. Recognition only; **no re-filing inside a repository root.**
- **`Nightwork_Book_Proposal_2026.docx`** — its Author Platform section genuinely is a professional
  biography. Carried with `also_schema: "career"`; it must not smuggle the manuscript into a
  portfolio branch.
- **`Nightwork_audiobook_ch01_take02.wav`** — this row owns the *work being narrated*; the recording
  **session package** is its own making record and is not claimed.

Rejected from the corpus entirely, so they are **not** on the node:

- **A reading-app annotation or highlight export** — evidence of reading, not making; `Reading Inbox`
  or `Reference Clips`.
- **A downloaded book template, a manuscript-formatting cheat sheet, a Vellum preset** — stock and
  reference material with no work around it: "useful for later retrieval but does not belong to a
  current project."
- **A writing-app autosave or backup directory** — bulk machine state, fully covered by the schema's
  version-family universal. Adding it would have widened the row into a backup detector.
- **A word-count or writing-streak tracker spreadsheet** — the temptation to include it is exactly
  charge 1 wearing a spreadsheet, and it would smuggle a count back in through the fixture list.
- **A blog archive export or a newsletter back-issue set** — ordered same-stem text runs with no
  compile container and no apparatus. `creative.short-form-writing`'s, or `creative.periodical-issue`'s.

## The collision fixture

**`The Overstory - Richard Powers.epub`** — a purchased retail ebook. It is the file that most looks
like this row's evidence, and it is worse than that: **its book apparatus is more complete than any
draft's will ever be.** A full package spine listing content documents in reading order — the row's
own defining structure — publisher-generated front matter, a copyright page with an ISBN-shaped
token, a cover image, a generated contents. An apparatus-based detector would rank it top of the
corpus, above every real manuscript on the disk.

What discriminates it is **positive on both sides, not an absence**: retailer or distributor
identifiers in the package metadata, an author-and-title filename pattern used by no working file on
the disk, and a folder of other single-file books by other authors — against, on the making side, a
same-stem working container, an ordered draft run, and a version family. The holder is **reading**
this. It routes to `Reading Inbox`: "Reading Inbox may hold papers, articles, reports, and saved PDFs
that appear to be reading material but have no active research, course, or project association."

This fixture is why `never_alone` bars **complete front matter alone**, and why the JSON's second
`needs_llm` entry is phrased as *made versus read*. Front matter proves a book exists; it does not
prove the holder is making it.

## Reciprocal boundaries

Eleven `collides_with` edges, each naming the same fixture on both sides. All eleven targets verified
against `roster.json`.

| Neighbour | Shared fixture | Their side | This row's side |
|---|---|---|---|
| `creative.short-form-writing` | `Nightwork_ch03_draft.docx` | complete in itself; own addressee or outlet; a run of unrelated stems | a section of one continuous sequence, resolved by a container, a full-manuscript sibling or a compiled output |
| `creative.submission-query` | `Nightwork_partial_50pp.docx` | a purpose-coherent packet: query letter, synopsis, agency tracking list | a compiled *state* of the work, carrying `version_family` back to the manuscript it was cut from |
| `creative.publishing-title` | `Nightwork - 1st pass pages.pdf` | publisher-side: proofs inside a production set with schedule, print spec, jacket brief, distribution metadata, **and other titles** | author-side: proofs arriving into one work's folder beside that work's own version family |
| `research.thesis-dissertation` | `Dissertation - Full Draft - Chen.docx` | the degree apparatus — committee page, compliance checklist, programme and degree | the trade apparatus — proposal with comparable titles, agency addressee, style sheet, permissions log |
| `research.manuscript-publication` | `manuscript_R1_clean.docx` | abstract, sectioned argument, reference list, reviewer responses, submission receipt | **never claims it** — no container, no front matter, no chapter run |
| `research.reading-library` | `The Overstory ….epub` | a book the holder READS: retail packaging, distributor metadata | a book the holder MAKES: working container, ordered draft run, version family |
| `creative.film-production` | `MidnightRiver_screenplay_adaptation_v2.fdx` beside `MidnightRiver_ch01-12_draft7.docx` | script element grammar inside a production neighbourhood | the prose side: chapter run and compile container |
| `creative.translation-project` | an ordered target-language run mirroring a source-language run | the parallel/aligned structure and the source–target pairing | the target-language book as one work, with its own container and apparatus |
| `code.software-project` | `nightwork-book/` | the preserved repository root; internal layout preserved, not re-filed | the ordered-section container inside it, for **grouping only** |
| `career.portfolio-work-samples` | a compiled `.epub` beside a resume and an author bio | self-presentation: finished outputs, no working files, ordered for showing | the making record: container, draft run and paperwork family present on the same disk |
| `photos.scanned-documents` | `Scan_typescript_1974_p001.jpg` | the scan family on scanner-origin evidence and page-run structure | the same members as sections of one work **only** where a title reference resolves them |

Where neither side resolves, both abstain — "Correct abstention is a successful outcome because the
product’s goal is reliable organization, not maximum file movement."

The reciprocal that mattered most is `creative.publishing-title`'s, because it turns on **other
titles**, which is a corpus-level observation and not a file-level one. Both sides need the same
discriminator or the same proof pages activate twice. That asymmetry is NJ-BM-4.

`also_holds_with: []` by contract — see the repair note above. `role_split: []`: the two pairs this
material wants are **author against publisher** (already the schema's declared `client` / `our_firm`
split, inherited not re-minted) and **ghostwriter against credited author** (genuinely
unrepresentable, because *both* sides are authorship and "Authorship is usually metadata; the
document’s purpose, project, subject, or target is more informative for placement"). A split joins
two *fields*, and this schema declares none, so there is nothing to split.

## Neighbours considered that did NOT get an edge

- **`creative.revision-round`** — refused already, on the version-token evidence this row's
  `never_alone` bars. The absorbed `write.editing-pass` coverage is stated in prose and on the
  `Nightwork_copyedit_returned_TRACKED.docx` fixture instead. Edging a refused row records nothing.
- **`creative.periodical-issue`** — a back-issue set is an ordered same-stem run, which is why it
  appears in `needs_llm`. It never competes for the *container*, because a periodical's members are
  separate works. No shared evidence item, no edge.
- **`creative.print-production`** — the printer-side of a proof file. Its seam runs through
  `creative.publishing-title`, not through this row; adding it would give one proof PDF three
  claimants.
- **`creative.self-initiated-work`** — refused; and the professional/hobby seam is not this row's
  question, since an unpublished novel with a compile container is this row either way.
- **`identity`** — a permissions log and grant letters hold third-party contact details. Carried as
  `also_schema: "legal"` on the fixture plus the sensitivity posture; the identity reading belongs to
  the *release form* pattern the schema anchor already owns.

## proposed_fields

**Empty, deliberately.** `fields: []` by rule. Two keys were genuinely tempting and both were
refused:

- **A book identifier** (the token printed on the copyright page). Stable, machine-shaped, and
  useless: it identifies *any* copy of the book, including the retail ebook that must not activate
  this row at all. It would be bare-identifier evidence of exactly the kind `00` warns about.
- **A section-position key.** A chapter number is a coordinate *inside* one document, not a property
  of the file, and it could never be a folder level without producing the one-child directories
  `00`'s validator rejects. Recommendation, offered and not taken: reuse `artifact_type` for the
  section *kind* and represent order only as P9 graph structure.

Minting on a field-less schema at the point of maximum temptation is the 574's original mistake. The
schema's own `open_question` already records the adjacent rights-and-licence hole for R1c; this row
does not widen it.

## NEEDS-JOSEPH (this node only)

- **NJ-BM-1 — the third leg overlaps `creative.journalism-reporting`.** The claim that third-party
  identity is inseparable from the work's own text is an inference, and journalism claims a similar
  posture for sources. (a) Keep both rows with the **subject** / **source** distinction as recorded
  here; (b) let journalism own the protective posture and have this row inherit it, keeping the node
  on leg 1 alone; (c) raise the distinction to the schema, where it would apply to every prose
  sibling. **No recommendation — this is a policy call, not a research finding.**
- **NJ-BM-2 — leg 2 is conceded, and the row's only dimension contribution is a prohibition.** If
  option (b) of NJ-R1a-1 lands, R1c must decide whether "no per-chapter level" is expressible in the
  template contract at all, or whether it must live as a validator rule beside `00`'s existing
  "meaningless one-child levels" check. (a) Template-expressible; (b) validator rule; (c) dropped and
  left to the validator's empty-branch test to catch. **Recommendation: (b)** — the check is
  general, not book-specific.
- **NJ-BM-3 — no key is minted and one hole is real.** See *proposed_fields*. (a) Leave both
  unrepresented; (b) let the identifier ride as a searchable observation with no field; (c) reuse
  `artifact_type` for section kind, order as P9 structure. **Recommendation: (c), not taken here.**
- **NJ-BM-4 — the author-side / publisher-side seam is corpus-level in one direction.** The boundary
  against `creative.publishing-title` turns on whether **other titles** are present; the activation
  algorithm reasons about files. (a) Permit a corpus-shape observation to inform activation; (b) draw
  the seam per-file on a production schedule plus distribution metadata — weaker but local; (c) merge
  the two rows, which loses the holder-role distinction `00` requires be modelled as distinct facets.
  **Recommendation: (b).** *A cross-row question; recorded, not acted on.*
- **NJ-BM-5 — a co-activation that has no legal edge.** A long-form reported book is genuinely both
  this row's material and `creative.journalism-reporting`'s, on disjoint evidence, and the fixture
  `Interview - Marisol Vega - 2026-03-04.m4a` sits on both sides. They do not compete for the same
  evidence item, so it is not a collision — but `also_holds_with` is schema-to-schema only, so a
  template-to-template co-activation cannot be expressed. (a) Leave it unasserted, which CONNECTION
  permits since "unlisted just means unasserted"; (b) raise the pair to schema level, where it
  collapses to creative-with-creative and says nothing; (c) extend the vocabulary, a contract change
  and not this row's to make. **Recommendation: (a).**
- **NJ-BM-6 (inherited, cross-row) — `creative.screenplay.research.md`'s NJ-SCREENPLAY-1 is now
  half-closed.** This row's dangling edge is repaired on my side. The other half — whether the
  refused `creative.screenplay` id itself is re-pointed, documented as a marker, or revived — remains
  R1c's. *No neighbour file was touched.*

## Audits run before returning

- `python3 -m json.tool` — parses. 29 top-level keys, matching the landed creative siblings including
  the two house `*_note` keys.
- **Seventeen `00` spans checked with `grep -c -F` before writing; sixteen matched verbatim (count 1
  each), including the curly apostrophe in "the product’s goal". The seventeenth — the salvaged
  draft's "placed images, linked footage…" — returned 0 and was removed as a fabricated attribution.**
  No `00` quotation now in the node or this memo is fabricated or paraphrased inside quote marks.
  Spans attributed to `creative.json`, `creative.screenplay.research.md` and `CONNECTION.md` are
  quoted from those files and labelled as such.
- All 11 `collides_with.domain` values resolve to `roster.json` `domain_id`s (11/11) — **no dangling
  id**; every entry is an object carrying `domain`, `signal` and `provenance`; every signal names the
  same fixture on both sides.
- All 5 `falls_through_to` residuals and all 17 `falls_through_if_inactive` values are among `00`'s
  nine residual names. Every `file_examples.source_type` (17/17) and every `file_kinds.source_types`
  member (11/11) is in the fourteen-member `SOURCE_TYPES` list. Every `also_schema` value resolves to
  a roster schema id (5/5).
- `fields`, `proposed_fields`, `also_holds_with`, `role_split` and `template.dimension_order` are all
  empty, each with a stated reason. All 17 fixtures carry "a folder path" in `must_not_conclude`; 5
  carry `group_without_copying_facts: true`.
- No number in the file is a threshold, score or evidence count. No handling class is assigned;
  `sensitivity: potentially_sensitive`, and `is_safety_domain` is not claimed.
- Only the two assigned files were written. No neighbour node, roster entry, canonical field, `src/`
  file or SPEC was touched, and `planning/29-DOMAIN-OWNERSHIP.md` was not opened.
