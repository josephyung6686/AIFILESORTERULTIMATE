# 107 — The Ideal Multi-Role Personal File Tree (the owner's own text)

> **THE OWNER WROTE THIS. IT IS THE TARGET THIS REPAIR AIMS AT.** Stored on their
> instruction of 18 Sep 2026: *"make a file and then store it there so you can
> reference it."*
>
> **WHY IT IS HERE AT ALL.** Until today it existed only in chat. `104` §18.111
> records that an analyst went looking for it and found only FOUR second-hand
> fragments (`104`:2603, 2617, 2631, 2645, 2766; `00`:350, 366; `106`:3066) —
> every citation of it in this repository was a quote of a quote, and the ideal
> tree specification was correctly built from `00` instead rather than
> reconstructed from paraphrase.
>
> **TRANSMISSION DAMAGE, MARKED AND NOT REPAIRED.** The paste arrived with several
> lines truncated mid-word — the Family and Household opening, a Personal Planning
> line, a Work project line, an Education assignment line, a Finance receipts line,
> a Legal agreements line, a Travel line, a Creative line, and two rows of the file
> placement table. They are left EXACTLY as received and marked `[TRUNCATED IN
> TRANSMISSION]`. Nothing here is invented: a reconstructed line would become a
> citation, and `104` records four separate occasions this session where a
> plausible-looking detail turned out to be the lead's own invention.
>
> **STATUS.** This is a DESIGN BENCHMARK and a qualitative evaluation fixture, in
> the owner's own words — not a taxonomy to be materialised. `00` amendment 12a
> governs: a branch appears only where the person's own files put it, and shipping
> the whole tree as a skeleton every corpus is poured into is forbidden. The
> machine-checkable rules derived from it live in the ideal-tree specification and
> in `tools/groundtruth/ideal_tree.py`.

---

## Purpose

This report defines a gold-standard example tree for the product: deep enough to demonstrate sophisticated organization, broad enough to cover an ordinary person's real digital life, and restrained enough that it remains navigable. The example represents a multi-role adult who works full time, studies part time, teaches occasionally, manages a household with two children, travels, keeps personal records, and has creative and technical projects.

The tree is a template-backed proposal, not a universal taxonomy. The product should activate only relevant branches, derive actual nodes from the corpus, preserve useful existing folders, and let the person rename, relocate, merge, remove, or reorder every proposed branch. This is especially important for residual material: the user wants controlled, customizable homes for one-off images, disconnected PDFs, screenshots, and ambiguous files, with those suggestions surfaced before movement rather than hidden in a generic Misc folder.

## Design principles

Research on personal file collections supports a mixed structure rather than one universal depth. Active files are commonly retrieved from relatively shallow paths — 82% at depth four or less in one study — while large real collections can have a waist around depth six and remain much broader than they are deep. The example therefore keeps common active destinations around three to five decisions from the root, while permitting six levels where stable context genuinely warrants it, such as institution → program → term → course → work type.

The hierarchy follows five principles:

1. **Stable context comes first.** Employer, institution, person, property, trip, project, and year precede volatile document types.
2. **Each branch chooses its own split order.** Education may split by institution and term; taxes by year and record type; photos by year and event; projects by project and stage.
3. **One physical home does not erase multiple meanings.** A paper can physically live in a res[TRUNCATED IN TRANSMISSION] while remaining associated with a course and laboratory in the graph and local search.
4. **Empty template folders are not created.** The tree below illustrates the library's capability; a real proposal materializes only nodes supported by files, an established workflow, or an explicit user choice.
5. **Uncertainty stays broad and visible.** An isolated screenshot can remain under Screenshots or Review and Unsorted; it should not acquire an invented trip, project, or person.

Personal record guidance also supports explicit areas for identity, financial, legal, medical, insurance, housing, and household records. Those categories appear here as protected conceptual homes, but the product must enforce its own local privacy policy rather than treating the folder name alone as protection.

## Example person

The fictional owner is Jordan Lee, who has the following roles: product designer at Northstar Health; part-time master's student at Columbia University; volunteer instructor at City Learning Center; household manager w[TRUNCATED IN TRANSMISSION] a partner and two dependent children, Mia and Evan; homeowner, traveler, photographer, and hobbyist programmer.

Realistic names make the example understandable, while the reusable template dimensions are shown in braces — for example, `{institution}`, `{term}`, `{course}`, and `{work type}`. Person names are appropriate only where the user explicitly creates a private family or dependent workflow. A client, patient, candidate, or employee should use a matter, case, requisition, project, or approved pseudonymous identifier instead of a person-named folder.

## Branch templates

The tree should not be implemented as a static set of paths. It should be represented as a library of branch templates whose split dimensions, labels, privacy behavior, and maximum useful depth can be customized.

| Template | Default split order | Typical depth | Representative files |
| --- | --- | --- | --- |
| Current work | Employer → year → project or activity → stage | 3–5 | DOCX, PDF, PPTX, XLSX, CSV, email exports, design files |
| Career applications | Year → organization and role → application stage | 3–4 | Job descriptions, résumé, cover letters, interview notes, offers |
| Coursework | Institution → program → term → course → work type | 4–6 | Syllabi, lecture PDFs, notes, assignments, notebooks, exams |
| Teaching | Institution → term → course → teaching function | 3–5 | Lesson plans, slides, demos, rubrics, rosters, solutions |
| Family records | Person → context → year or cycle → record type | 3–5 | Report cards, permissions, health records, activity forms |
| Projects | Project → stage or artifact class | 2–4 | Plans, research, data, code, drafts, outputs |
| Taxes | Tax year → record class | 2–3 | W-2/1099 equivalents, receipts, workpapers, filed returns, notices |
| Property | Property → function → project or year | 2–5 | Deeds, mortgage statements, invoices, permits, manuals, photos |
| Health | Person → year or durable category → record type | 3–4 | Visit summaries, results, prescriptions, claims, immunizations |
| Travel | Year → trip → function | 3–4 | Itineraries, tickets, bookings, receipts, claims, notes |
| Photos | Year → event → rendition | 3–4 | HEIC, JPG, RAW, PNG, MOV, edited exports |
| Reference | Status or topic → subtype | 2–3 | Papers, manuals, clips, templates, saved articles |
| Residual | Residual state → optional broad subtype | 1–2 | Ambiguous PDFs, screenshots, isolated images, unsupported files |

The approach deliberately balances depth against scan burden. Research finds that deeper structures can slow navigation, while folders with too many items also increase scanning time; one widely cited recommendation is to avoid placing more than about 21 information items in a single folder. **That number should guide a proposal, not function as a rigid code rule:** the model may recommend a new split when a folder becomes visually burdensome, and the person can accept, reject, or choose a different dimension.

## Customization model

A user should be able to change the tree at the level that affects real behavior — not merely rename cosmetic labels. Each enabled branch should expose the following controls **before freeze**:

| Control | Example |
| --- | --- |
| Enable or disable template | Disable Vehicles; enable Freelance |
| Rename branch | Education → School; Career → Professional |
| Relocate branch | Put Reference Library under Projects |
| Change split order | Coursework by course → term instead of term → course |
| Change depth | Keep all receipts directly under 2026, or split by purpose |
| Merge branches | Combine Career and Work |
| Split branches | Separate Creative Work from Hobbies |
| Adopt existing folder | Map an existing Clips folder to Reference Clips |
| Choose person labels | Permit dependent names; prohibit client or patient names |
| Set privacy | Local-only, protected, searchable only after unlock |
| Set residual behavior | Leave screenshots in place, collect them, or review them later |
| Set placement policy | Suggest only, dry run, or approved narrow automation after launch |

The LLM's job is to interpret the corpus and propose among these approved structures. **It should not invent arbitrary folder names during placement.** If no approved node fits, it should return an unresolved result, propose a user-visible tree edit, or select an approved residual destination. The product should preserve all changes as a versioned plan so a later edit produces an explicit tree diff rather than silently changing prior organization.

## Materialization rules

The displayed tree is intentionally comprehensive, but a real run should build a much smaller personalized projection:

- A template is activated because the corpus supports it or the person confirms that role or workflow.
- A level is instantiated only when its value is grounded in evidence, existing structure, or an explicit user label.
- A child folder is [TRUNCATED IN TRANSMISSION] en it improves retrieval, separates materially different workflows, or reflects a repeated file family — not merely because the library contains that level.
- A single unusual file may remain at the closest meaningful parent rather than creating a one-file leaf.
- Existing curated folders are preserved unless the person asks to redesign them.
- Active paths should usually remain within four navigational decisions; deeper paths are reserved for naturally nested domains such as education, teaching, and large projects.
- Live code repositories, application bundles, build outputs, caches, and package directories are excluded rather than treated as destinations.
- The archive mirrors closed contexts selectively; it does not become a second copy of the active tree.

For research or data-heavy projects, Raw, Processed, Documentation, and Outputs are meaningful semantic distinctions. Guidance for research-data organization commonly recommends preserving raw data separately, keeping paths reasonably shallow, and placing [TRUNCATED IN TRANSMISSION] able project context before granular artifact type.

## Protected records

The detailed identity, medical, financial, legal, household, and dependent branches are included because ordinary people genuinely need them. FEMA's household preparedness guidance groups critical records into household identification, financial and legal documentation, medical information, and household contacts, while consumer guidance separately identifies passports, certificates, deeds, leases, insurance, taxes, and health records as important long-term materials.

**The folder tree must not be mistaken for the security system.** A branch labeled protected should have explicit local handling: contents excluded from cloud model calls, previews and filenames suppressed where policy requires, local search locked or privacy-preserving, and automatic movement disabled. Standard search may report that protected material exists without exposing its contents. A user may still choose detailed person-based structure inside a locally protected fa[TRUNCATED IN TRANSMISSION]ly area, but client, patient, employee, and candidate names should not be generated as folder levels by default.

## Residual structure

`98 Review and Unsorted` is not a dumping ground and should not grow indefinitely. It is a set of explicit states for files that lack enough context:

- **Ambiguous Documents** — the content is readable but several destinations remain plausible.
- **Standalone PDFs** — the document is meaningful but has no accepted group.
- **One-Off Images** — the image has no event or project association.
- **Unclear Spreadsheets** — structure was extracted but purpose remains unknown.
- **Possible Duplicates and Versions** — a separate decision workflow, not a destination category.
- **Unsupported or Encrypted** — the system deliberately could not inspect the contents.
- **Deferred Decisions** — the person chose not to decide now.

Before any residual LLM pass, the product should present counts by type and reason, show representative examples, and let the person choose which sets may be reviewed. The LLM may recover a valid existing group, select one approved broad residual destination, recommend leaving the file in place, or abstain. **It must not invent a deep narrative for an isolated file.**

## What "perfect" means

The ideal output is **not** the full tree. It is a credible, personalized subset whose structure reflects the person's actual roles and files. A successful proposal should make the owner say:

- The top-level areas resemble the major parts of life without forcing every file into an identity category.
- Coursework and teaching are visibly different even when they mention the same institution and course vocabulary.
- Work projects, career applications, family records, taxes, health, travel, and photos each use a split order natural to that domain.
- The tree is deep where context matters and shallow where files are isolated.
- Sensitive records have useful homes without being exposed.
- Existing folders are respected.
- One-off files remain findable without polluting the main structure.
- Every prop[TRUNCATED IN TRANSMISSION]abel can be renamed and every split can be changed before freeze.
- A file with several meanings remains discoverable through every accepted relationship, even though it has one physical path.

**This tree should be used as a design benchmark and qualitative evaluation fixture.** The engine's generated tree can be compared with it branch by branch — not to demand identical labels, but to test whether the proposal achieves equivalent coverage, natural depth, domain-appropriate splitting, protection, residual honesty, and user control.

---

## The tree itself

The owner's tree as pasted. The numbering is optional and is shown only for workflow folders that benefit from staying at the beginning or end of an alphabetically sorted root. Comments following `#` explain purpose and are not part of folder names. **Several lines arrived truncated and are marked; they are not reconstructed.**

See `107-ideal-tree.txt` beside this file for the tree verbatim.
