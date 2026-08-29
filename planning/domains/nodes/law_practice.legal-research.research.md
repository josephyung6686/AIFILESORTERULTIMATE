# Research memo — `law_practice.legal-research`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.legal-research.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Team: OTHER-TEAM · Result: **REFUSED** (`refuse_node: true`), coverage routed, no field minted, no neighbour edited

## Result in one paragraph

Legal research is a real activity and an enormous pile of files, and it is not a node on this schema. Memoranda that survey authorities, tables of authorities, citator printouts and annotated case PDFs are either (a) the `law_practice` schema's own INTERNAL WORK-PRODUCT signal and its already-listed work_type value, (b) addressed reliance-bearing advice already owned by `law_practice.opinions-advice`, (c) standing know-how already owned by `law_practice.precedent-bank`, (d) an authorities section of a hearing compilation already owned by `law_practice.trial-preparation`, or (e) published third-party reading that falls to Reading Inbox / `research.reading-library` until an exact accepted purpose joins them to a matter group. Subtract those five homes and what remains of `law_practice.legal-research` is a document-type word. That is a label, not a node. The refusal loses no coverage.

## Binding material read

Stamped dispatch via `make_prompt.py law_practice.legal-research`. Authority stack: `planning/domains/dispatch/RESEARCH-BRIEF.md`, `planning/42-HANDOFF-FINISH-THE-CATALOGUE.md` §6–§7, `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` §2 node test, `planning/domains/nodes/law_practice.json` (schema anchor only — memo not re-read), calibration memo `legal.practice-matter-file.research.md`, and landed siblings `law_practice.opinions-advice`, `law_practice.precedent-bank`, `law_practice.matter-correspondence` (refusal idiom), `law_practice.deadlines-diary` (refusal idiom), `law_practice.trial-preparation`, `research.reading-library`. Every span in quote marks attributed to `00` was `grep`-verified verbatim before writing.

Controlling design consequences:

- D1 / PR-6 leave `law_practice` fieldless; templates write `fields: []` and empty `dimension_order`.
- CONNECTION §2: a template exists only when detection signals, recommended dimensions, or privacy rules differ from its schema's default.
- Work types are values, not nodes. The schema already enumerates `"legal research note, authorities list and opinion or advice record"`.
- `also_holds_with` is schema ↔ schema only; bare-string edges are forbidden; collision edges carry SAME FIXTURE BOTH SIDES.

## The charge, stated at its strongest before it is answered

Taking the charge seriously means arguing the row's *best* case first.

The best case runs: finding out what the law is is not a genre — it is an organizational situation. A practitioner keeps a purpose-coherent, content-incoherent packet: an internal research memorandum, a table of authorities, citator reports, legislative-history extracts, and annotated copies of published opinions. The members look like Reading Inbox material until the research purpose joins them. That is exactly 00's licence for a group: "The documents are content-incoherent but purpose-coherent." *(grep-verified, `00`.)* The landed sibling `law_practice.opinions-advice` already reserved this id in writing — it says it does NOT hold "the internal research note or authorities list behind the advice (`law_practice.legal-research`)" and authors a `collides_with` edge into this id distinguishing SURVEY structure from ADDRESSEE-AND-RELIANCE structure. Citator reports and issue-to-authority maps look like structures, not mere filenames. Privacy could be argued as two-tier: clean public downloads are low-disclosure; the memo, the selection and the annotations disclose strategy and must stay protected.

Three further points a fair reading must concede: (a) the legacy hint names a real drawer every practice keeps; (b) refusing appears to orphan the opinions-advice reciprocal; (c) `research.reading-library` survived on inverted detection and a `none` privacy posture for third-party publications — a cousin argument is available here for authorities.

The case fails anyway, and it fails on the node test rather than on taste.

## The node test, all three legs

### Leg 1 — Detection signals: identical to the schema default

The `law_practice` schema's precondition is two-legged: an exact matter reference repeated across artefacts, and at least one artefact whose labelled slots separate a practitioner or firm role from a client role. Inside that default it already names, as INTERNAL WORK-PRODUCT: a memorandum whose sections separate "instructions or facts supplied, issues, research and authorities, analysis, options, risk and next steps" with a practitioner-side producer marker. That sentence is this row's world.

The schema's `work_types` already contains, verbatim, `"legal research note, authorities list and opinion or advice record"`. Its own `work_type` proposal states the governing kill rule: a template justified only by holding a different legal document kind is the schema's default with a narrower filename filter.

Run the tempting fixtures through the deletion test the schema imports: delete every entity name and every document-type word (`research`, `memo`, `authorities`, `KeyCite`, case names). What survives a research memo is the section grammar the schema already claims. What survives a downloaded opinion is a caption — which is `legal`'s proceeding signal, not this schema's. What survives a citator report with no matter reference is a database masthead — an organisation name, never-alone under 00's Columbia rule: "A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization." *(verbatim.)*

The structural rescues fail in turn:

- **Survey / authorities list.** Named on the schema as a work_type value and as a section of work product. Not a new detection set.
- **Citator / legislative-history export.** Without a matter anchor it is Reading Inbox tooling output; with one it is a matter member under the schema's first grouping reason. No third detection set appears.
- **Annotated opinion.** Annotations are observations. 00's purpose rule — "Topic answers what a file is about, while purpose answers what the file was for." *(verbatim)* — is the only separator, and purpose here arrives as a sticky-note clue at best, not as template activation.

A row cannot differ in detection from a default that has already written its detection down.

### Leg 2 — Dimension order: a label at the parent's function level

Under PR-6 both orders are `[]`. Identical by contract.

The schema's prose recommendation is client (only on explicit approval) → matter → **document function** → period. "Research" and "Authorities" are labels at that function level. They do not reorder, remove, or argue a level away. Contrast `law_practice.court-filing-record` / `trial-preparation`, which earned keep-votes by arguing the function level into a leaf or a sitting. This row would fill one branch name.

Authority- or topic-first filing would "use an author or organization merely as a collector" and "create meaningless one-child levels" *(both verbatim from `00`'s custom-template validator sentence)* in a single-matter corpus — court names, reporter series and statute titles as collectors. Parent-before-child already settles the rest: "A work type such as Homework 3 is meaningful only after the course is known" *(verbatim, continues with the course-code clause).* A pinpoint citation is meaningless without the matter that asked the question. `time_first` is false family-wide: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." *(verbatim.)*

### Leg 3 — Privacy: the schema's posture, and often looser

The schema protects a third party who never chose this filesystem. A research memo naming a client and laying out issues and strategy is exactly that interest — already fixed on the privilege-log and work-product fixtures. No stricter rule appears.

In the other direction the characteristic "authorities" members are public. Clean Supreme Court PDFs, statute extracts and citator reports contain no client and no third-party subject of record. Their honest residual is Reading Inbox: "Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association." *(verbatim.)* A row whose honest note is "often less sensitive than the default" has not found a privacy difference that justifies a node.

Annotated copies are the hard case. Public text plus private highlights can disclose strategy. That is still the schema's third-party / strategy posture applied to work product, delivered by Protected Records when a matter anchor is accepted — "Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials; it should normally remain local-only and must not cause filenames or content to be exposed in model prompts." *(verbatim.)* It is not a new template rule.

**Three legs, three failures. The node is refused.**

## Four independent kill vectors from the charge

Each would be sufficient alone.

1. **It is a `work_type` value.** Schema enum entry already present.
2. **It is a document type / medium.** Memo, note, authorities list, citator PDF, legislative-history zip. 00: "treat the file extension as a routing signal rather than an assumption about meaning" *(verbatim)*.
3. **It is a lifecycle stage.** "Research" before pleading, filing or advice — the charge names lifecycle stages as non-nodes.
4. **Every structurally distinct residue is already a sibling.** Addressed advice → `opinions-advice`. Blank-slot know-how → `precedent-bank`. Hearing authorities compilation → `trial-preparation`. Unanchored publications → Reading Inbox / `research.reading-library`. Caption-bearing judicial opinions → `legal` first.

## Files considered and rejected

Twelve fixtures are serialized in the JSON. Why each was considered, and why none is this row's evidence:

1. `Research memo - limitation under s.2 - 41127-0006.docx` — proof fixture; schema INTERNAL WORK-PRODUCT verbatim.
2. `Table of Authorities - Motion for Summary Judgment - 41127-0006.pdf` — work_type "authorities list"; caption may coactivate `legal`.
3. `KeyCite report - Acme Holdings v Beta Trading.pdf` — citator without matter → Reading Inbox.
4. `Supreme Court Opinion - Example Holdings v Example Agency - annotated.pdf` — public opinion + annotations; purpose clue only; `legal` on caption.
5. `Authorities bundle - Day 1 hearing - 41127-0006.zip` — trial-preparation compilation collision.
6. `Advice on merits - limitation defence - 41127-0006.pdf` — opinions-advice collision (addressee + reliance).
7. `PRECEDENT - Research note - limitation under the Limitation Act - firm know-how v3.docx` — precedent-bank collision.
8. `Supreme Court Opinion - Example Holdings v Example Agency.pdf` — collision fixture; clean public download.
9. `Legislative history pack - Limitation Act 1980 - Westlaw export.zip` — topical archive name manufactures no purpose.
10. `Screenshot 2026-08-18 at 11.02.14 - Westlaw search - limitation.png` — Temporary Screenshots; account chrome redacted.
11. `Market-entry legal issues memo - Acme Holdings - prepared for board.pdf` — career consulting collision.
12. `Research DMS export - 41127 - privileged.7z` — Unsupported or Encrypted; filename invents nothing.

Also considered and rejected as a class: live Westlaw/Lexis sessions (source systems, not files); bibliography managers' whole libraries without a matter anchor; CLE handouts and law-review PDFs kept for professional reading; opposing counsel's authorities served as a production (discovery / evidence territory).

## The collision fixture

**`Supreme Court Opinion - Example Holdings v Example Agency.pdf`.** Caption, citation, bench, reasoning, dispositive section — every surface token a research row would cite — and no matter reference, no annotation, no practitioner header. It is a public download.

What discriminates it: absence of an accepted purpose. "Topic answers what a file is about, while purpose answers what the file was for." *(verbatim.)* With neither a matter research-memo reference nor a research-project association it falls to Reading Inbox. A byte-identical annotated copy elsewhere in the corpus establishes `duplicate_family` and copies no matter fact onto the clean download — "The graph does not automatically copy those missing facts onto sparse files" is the schema's own grouping discipline, and 00's stop rules refuse groups with no valid anchor: "It should not form a supported group when there is no valid anchor" *(verbatim, opening clause of the stop-rule sentence).*

Second collision, other direction: **`Market-entry legal issues memo - Acme Holdings - prepared for board.pdf`.** Citations and legal issues on a consulting deliverable. Discriminator: prepared-for / prepared-by roles and milestones → `career.consulting-client-engagement`, not practitioner apparatus.

## Reciprocal boundaries, both directions, same fixture both sides

**vs `law_practice.opinions-advice`.** Fixture: `Advice on merits - limitation defence - 41127-0006.pdf`. → sibling: addressee-and-reliance pair plus opinion grammar. ← this row / schema: survey-without-reliance absorbed as INTERNAL WORK-PRODUCT. The sibling already wrote this edge into this id; refusal creates reciprocity debt for R1c (see NEEDS-JOSEPH).

**vs `law_practice.precedent-bank`.** Fixture: the firm know-how research note. → blank matter/client slots + drafting apparatus. ← live matter memo with reference and producer marker → schema default.

**vs `law_practice.trial-preparation`.** Fixture: `Authorities bundle - Day 1 hearing - 41127-0006.zip`. → continuous pagination + sitting index spanning document families. ← free-standing research pile without compilation grammar → schema matter group or Reading Inbox.

**vs `research.reading-library` / Reading Inbox.** Fixture: clean Supreme Court PDF. → third-party publication structure, no holder purpose. ← matter membership only through exact accepted reference elsewhere; never by topic.

**vs `legal`.** Fixture: annotated or captioned judicial opinion. → caption / disposition on the face; safety ordering first: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." *(verbatim.)* ← annotations and matter clues do not displace that.

**vs `career.consulting-client-engagement`.** Fixture: board legal-issues memo. → prepared-for / prepared-by + milestones. ← matter reference + practitioner/client apparatus.

**vs `legal.personal-legal-matters`.** Fixture: opinion or research-looking note in the holder's own dispute. → holder as party. ← holder as practitioner for someone else. Citations decide nothing about the side.

**Deliberate non-edges.** `finance` — a research memo is not a bill; no same-evidence mutex. `photos.screenshot-captures` — coactivation candidate for a Westlaw screenshot, not a mutex. `law_practice.motions-and-briefs` — a table of authorities beside a motion is a matter member, not a research-world claim. `academic` — a marked-up sample research memo from an LPC course is training material (schema already fixtures this class); no edge authored.

## Grouping without copied facts

When an exact matter reference joins a research memo to authorities, membership is the schema's ONE MATTER group. The anchor supports candidate membership and copies no client, issue, citation or privilege fact onto members. Archives are inspected without unpacking: "the normal scan should never extract archive contents to the filesystem" *(verbatim, continues with the security clause).* Cross-matter bridging by shared citation or issue similarity stays suppressed. "A file may validly belong to more than one accepted group" *(verbatim)* covers a published opinion that is both reading material and a matter authority on disjoint evidence — that is `also_holds_with` onto `research` and `legal`, lifted for R1c to schema pairs, not a licence for this template.

## Residual routing

- **Protected Records** — matter-anchored memos, strategy-disclosing annotations, authorities lists tied to an accepted matter when no group is active. Also licensed without a group: "Rare but sensitive files such as passports, visas, and legal documents may be surfaced as protected records even when they do not meet a normal group-size threshold." *(verbatim.)*
- **Reading Inbox** — clean published opinions, statutes, citator reports, legislative-history packs with no accepted purpose.
- **Review Later** — consulting-versus-legal ambiguity; weak sticky-note purpose clues. "Review Later may hold files whose meaning is partly understood but whose final location requires a future decision." *(verbatim.)* "Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement." *(verbatim.)*
- **Unsupported or Encrypted** — password-protected research exports. "Password-protected, malformed, nested, or oversized archives should be marked as unreadable or partially inspected rather than forced open" *(verbatim)*; "Unreadable, encrypted, corrupted, or unsupported files should retain basic metadata and remain eligible for manual attachment to a user-created group, but the system should not infer a purpose from their filename alone." *(verbatim.)*
- **Temporary Screenshots** — research-database screen captures without a matter.
- **Independent Records** — blank personal research templates with durable purpose and no group.

## External artifact shapes (existence only)

Used only to confirm artefact shapes occur in real practice; no legal rule imported:

- United States Courts / BAILII-style published opinions — captioned third-party publications anyone may download.
- Commercial citator printouts (KeyCite / Shepard's-shaped treatment histories) — database exports with mastheads and flags.
- Practitioner tables of authorities attached to motions and appellate briefs — survey lists with pinpoints.
- Firm know-how notes and blank research-memo templates — standing notes without a live matter.

No retention period, privilege conclusion, jurisdiction rule or citator-flag legal effect is derived.

## Proposed fields

`proposed_fields: []`. Nothing minted. The schema already proposes `work_type` for exactly this enum; proposing `authority`, `citation`, `issue` or `research_question` would be synonym mints and destination-disclosive. Authorship of a memo is never a destination: "It should avoid using authorship or creator identity as a destination dimension." *(verbatim.)*

## NEEDS-JOSEPH

1. **NJ-LPLR-1 — Reciprocity debt.** `law_practice.opinions-advice` collides_with points at this refused id. Re-point to the `law_practice` schema (survey / INTERNAL WORK-PRODUCT) while keeping reliance on opinions-advice. This row did not edit the neighbour.
2. **NJ-LPLR-2 — Annotated public opinions.** Protected Records when the annotation states an exact accepted matter reference; otherwise Reading Inbox, with Review Later for weak sticky-note clues. Alternatives spelled out so Joseph can pick the stricter default.
3. **NJ-LPLR-3 — `law_practice` ↔ `research` coactivation.** Confirm whether court opinions in a practitioner corpus coactivate `legal` alone, `research` alone, or both on disjoint evidence. The `also_holds_with` entries here are authored for lift to schema pairs.
4. **NJ-LPLR-4 — PR-6 re-test.** If `work_type` is later declared on the schema, re-run the node test once; expected answer remains refusal (enum value), but run it.

## Final recommendation

Refuse `law_practice.legal-research`. Keep coverage on the `law_practice` default (matter-anchored work product), `opinions-advice` (reliance-bearing advice), `precedent-bank` (standing know-how), `trial-preparation` (hearing authorities compilations), `legal` (captioned instruments, safety-first), and Reading Inbox / `research.reading-library` (unanchored publications). Inventing a node to save the legacy drawer name is the 574 failure mode this pass exists to refuse.
