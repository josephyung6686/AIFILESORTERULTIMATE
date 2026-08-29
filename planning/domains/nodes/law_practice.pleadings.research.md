# Research memo — `law_practice.pleadings`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.pleadings.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Result: **REFUSED** (`refuse_node: true`), coverage routed, no field minted, no neighbour edited

## Result in one paragraph

The pleading is a real and enormous class of document, and it is not a node on this schema. Its identifying structure — a tribunal caption, a bound party pair, numbered allegations, a prayer for relief, a verification or statement of truth, a counsel signature block — is the `legal` safety schema's own proceeding-activation signal. `law_practice`'s default template requires an artefact whose own labelled slots separate a practitioner-or-firm role from a client role; a pleading has no client slot at all. Subtract what `legal` takes and what the landed siblings take, and what is left of `law_practice.pleadings` is a document-type word that the schema already carries as a `work_type` value, sitting at the document-function level the schema's own recommendation already names. That is a label, not a node. The refusal loses no coverage: every fixture below names the row or residual that receives it.

## The charge, stated at its strongest before it is answered

Taking the charge seriously means arguing the row's *best* case first, not its worst.

The best case runs: pleadings are not a mere document type, they are the constitutive act of a proceeding — the originating process defines what the dispute is about, fixes the parties, and everything else in a litigation file (discovery, evidence, submissions, judgment) is downstream of it. In a practitioner's corpus the statements of case are the spine; a matter with no pleadings is a transaction, and a matter with pleadings is litigation. That is arguably an *organizational situation*, not a genre. It is also the single largest object class the legacy `law.pleadings` row was carrying.

Three further points a fair reading must concede: (a) the draft-and-amendment cycle of a pleading is genuinely practitioner-side work, invisible to any public docket; (b) amendment produces a real version family — v1, settled by counsel, served, amended, re-amended — which is structure, not vocabulary; (c) the row is `must_consider_neighbors`-adjacent to three landed rows that survived, so refusal is not the obviously safe answer.

The case fails anyway, and it fails on the node test rather than on taste.

## The node test, all three legs

### Leg 1 — Detection signals: not different from the schema's default, but *owned by the safety neighbour*

The `law_practice` schema's precondition is explicit and two-legged: an exact matter, file or engagement reference repeated across two or more artefacts, **and** at least one artefact whose own labelled slots separate a practitioner or firm role from a client role. It adds the deletion test — delete every entity name and every document-type word, and if nothing structural survives, nothing fires.

Run a pleading through it. Leg (i) can be satisfied incidentally: `Amended Particulars of Claim - 41127-0006 - v4 tracked.docx` carries a matter token that recurs. Leg (ii) cannot be satisfied at all. A pleading's labelled slots are *court*, *parties*, *case number*, *relief sought*, *verification*, *counsel of record*. There is no client slot, no retainer slot, no fee-earner slot, no instruction slot. The nearest thing is the counsel signature block, and the schema rules that out in terms: a role name can never carry a schema.

Worse, the structure the pleading *does* carry is the neighbour's activation signal. The `law_practice` anchor conceded this in writing before this row was dispatched, in its `legal` collision entry, and it names the pleading first in the list: every file inside a practitioner's matter that has an executed-instrument or proceeding shape is `legal`'s on `legal`'s own evidence, and `law_practice` does not displace it — because `legal` is one of 00's four safety domains and its protection runs first. 00 is the source of that ordering: "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed." *(grep-verified verbatim, `00`, para 52.)*

The anchor then states what is left for the schema: the class of artefacts on which `legal`'s signals do not fire at all — intake and conflicts screens, matter-opening records, time-and-disbursement exports, limitation diaries, review and privilege logs, precedent banks whose party and execution slots are blank by design, internal opinions, closure records. A pleading is the exact complement of that list.

A row cannot own detection signals that fire a different schema. This leg does not merely fail; it fails in the direction that would invert 00's safety ordering if it were forced through.

### Leg 2 — Dimension order: this row *is* a value of the schema's own function level

The schema's recommendation, held as prose because PR-6 forbids serialized dimensions: the client only where the corpus genuinely spans more than one and the user has explicitly approved a client-named branch, then the matter, then the **document function**, then the period last.

"Pleadings" is a label at that function level. It does not reorder the levels, it does not remove one, it does not add one, and it does not argue the level away. In a corpus with one proceeding it would produce precisely what 00 requires the engine to reject when it validates a template — that it must not "create meaningless one-child levels." *(grep-verified verbatim, `00`, para 97.)*

The contrast with the landed sibling settles it. `law_practice.court-filing-record` earned its keep by *arguing the function level away*: every member of that situation has the same function, so a function branch would be a one-child level, and its recommendation is that a filing record is a leaf beside the document it evidences rather than a branch of its own. That is a template making a different recommendation from its schema. This row makes the same recommendation with one branch label filled in.

The one ordering claim the row could make — that function must follow the matter, because an amended statement of case is meaningless without its proceeding — is already the schema's own, argued from 00's own words: "A work type such as Homework 3 is meaningful only after the course is known." *(grep-verified verbatim, `00`, para 95.)* Restating a parent's argument is not differing from it. `time_first` is false for the same reason it is false schema-wide: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders" *(verbatim, para 95)*, and nothing here is capture-based.

### Leg 3 — Privacy rules: the same as the default, and in one direction looser

`law_practice`'s claim to a posture stricter than `legal`'s is specific and, in its own domain, correct: `legal` protects the holder's own record, and `law_practice` protects a third party — a client, an adverse party, a witness, a deponent, an accused, a child — who never chose this filesystem and cannot consent. That argument does real work for a privilege log, which is a table of thousands of other people's correspondence metadata, and for an attendance note.

It does not do work here. A pleading's named persons are the proceeding's own parties, and 00 already sweeps them inside the safety perimeter twice — once at para 52 above, and again where it names the isolated case: "Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials; it should normally remain local-only and must not cause filenames or content to be exposed in model prompts." *(verbatim, para 120.)* The posture arrives from `legal` whether or not this id exists.

And in one direction the row's posture is *looser*: a filed pleading is frequently the most public document in a matter, sitting on a public docket. A row whose honest privacy note is "less sensitive than the safety default" has not found a stricter rule; it has found a reason not to exist. (The node still records `potentially_sensitive` — public filing does not mean safe to expose, since the holder's *possession* of the file, its neighbours and its folder label remain private. No handling class is assigned; that is P7's.)

**Three legs, three failures. The node is refused.**

## Four independent kill vectors from the charge

Each of these would be sufficient alone.

1. **It is a `work_type` value.** `law_practice.work_types` contains, verbatim, `"pleading, application, submission and written case"`. The dispatch prompt is unambiguous — work types are an enum of values for a field, not a request for a child node per value.
2. **It is a document type.** Complaint, petition, particulars of claim, statement of claim, defence, answer, counterclaim, reply, rejoinder are genre words. 00 treats even format as routing rather than meaning — "the file extension as a routing signal rather than an assumption about meaning" *(verbatim, para 35)* — and the schema's deletion test finishes the job: strike the document-type word and the entity names, and what survives a pleading is a caption and a party pair, which is `legal`'s.
3. **The rescue is a lifecycle stage.** The strongest save available was "the *draft* is practitioner-side, the *filed* one is `legal`'s." Draft → settled by counsel → served → filed → amended → re-amended is a lifecycle, and the charge names lifecycle stage as a non-node. The tracked-changes draft also still carries the same caption and the same party pair, so `legal`'s signal fires on it too; and the *version family* it produces is a filesystem-level signal 00 already extracts for every file (duplicate and version-family signals), not a domain signal.
4. **The one structurally distinct residue is already a sibling.** There *is* one pleading-shaped artefact on which `legal` genuinely does not fire: the blank firm precedent, `Claim Form N1 - blank - firm precedent v3.docx`, whose party slots are bracketed placeholders and whose statement of truth and signature line are empty **by design**. That is the schema's named inverse-recognition signal, and `law_practice.precedent-bank` is the roster row that owns it. Claiming it here would duplicate a sibling — the last item on the charge's kill list.

## Files considered and rejected

Twelve fixtures are serialized in the JSON with observations split from facts. The reason each was considered, and why none of them is this row's evidence:

- `Complaint - Hartley v Nash - CONFORMED.pdf` — the most tempting file in the world, and it is named on the landed `law_practice.court-filing-record` fixture list too. Its body is `legal`'s proceeding structure; its conformed stamp is a transmission event that the filing-record row already owns. Nothing in it is left over for this id.
- `Amended Particulars of Claim - 41127-0006 - v4 tracked.docx` — the lifecycle rescue, answered above.
- `Defence and Counterclaim - Nash - served 2026-06-11.pdf` — the *side* problem. Two counsel blocks across two documents establish two firms, not the holder's role. This is the family's defining failure mode and it routes to Review Later.
- `Claim Form N1 - blank - firm precedent v3.docx` — precedent-bank's, on the inverse-recognition signal.
- `Instructions to Counsel to settle Particulars of Claim - 41127-0006.pdf` — a document *about* a pleading whose own structure is an instructing/instructed slot pair. That is one of the schema's genuine signals and it belongs to `law_practice.opinions-advice`.
- `Scan 2026-06-11 - petition pages 1-8.pdf` — OCR of the same thing. Every candidate is `possible` at best; a scan date is not a document date, a filing date or a service date.
- `RE Draft POC - your comments by Friday.eml` — matter correspondence. An email discussing a pleading is not a pleading, and an attachment name creates no fact about the attachment.
- `Pleadings bundle - Hartley v Nash - index and tabs.pdf` — its own structure is an *index over members*, which is evidence-exhibits / trial-preparation shape. Bundle membership copies no fact onto a member.
- `Pleadings_41127-0006.zip` (password protected) — manifest read without extraction; not forced open; Unsupported or Encrypted.
- `Screenshot 2026-06-11 at 09.14.02 - e-filing portal - submitted.png` — positive screen-origin evidence activates the capture path; the portal event, if anything, is the filing record's. Absent EXIF proves nothing, per 00's rule.
- `Pleadings - Smith v Jones - specimen from practitioner text.pdf` — the collision fixture, below.
- `Divorce Petition - my own - filed copy.pdf` — the second collision fixture, below.

Also considered and rejected as a class: a practice-management or document-assembly system's live database; a court's public docket search results page; a statute or civil-procedure rule extract; a seminar handout on drafting statements of case. None is a matter document, and the first is a source system rather than one file.

## The collision fixture

**`Pleadings - Smith v Jones - specimen from practitioner text.pdf`.** It carries a complete caption, a party-versus-party line, numbered allegations, a prayer for relief and a full counsel signature block — every surface signal the refused row would have used, all of them, at once. It is a printed illustration in a practitioner textbook.

What discriminates it: a running chapter header, a publisher imprint and ISBN, page numbers continuous with a surrounding volume, commentary footnotes keyed to the paragraphs, a case-number slot that reads as a placeholder pattern, and — decisively — **no matter reference recurring anywhere else in the corpus**. It falls to Reading Inbox: "Reading Inbox may hold papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association." *(verbatim, para 120.)*

Second collision fixture, in the other direction: **`Divorce Petition - my own - filed copy.pdf`**. Court caption, petitioner and respondent slots, signed statement of truth, registry stamp — and the petitioner's name matches the corpus holder's own name on identity and finance material, with no firm letterhead, no matter reference and no engagement record anywhere. The discriminator is the *holder role*: the holder is a party, not counsel. It is `legal.personal-legal-matters`', whose landed one-line claims exactly this — records "held by a person in their own dispute or proceeding."

## Reciprocal boundaries, both directions, same fixture on both sides

**vs `legal` (safety schema).** Fixture: `Defence and Counterclaim - Nash - served 2026-06-11.pdf`. → `legal`'s side: a tribunal caption with a matter-identifier slot, or a bound party pair with an execution block, activates `legal` on `legal`'s own evidence, and as a safety domain it runs first. ← this row's side: nothing is left, because the practitioner/client role split `law_practice` requires is not present on the document. This is a total concession, not a seam, and it is the reason for the refusal. `also_holds_with: ["legal"]` is retained because the fixtures do legitimately co-activate `legal` while sitting in a practitioner corpus.

**vs `legal.practice-matter-file`.** Fixture: `Complaint - Hartley v Nash - CONFORMED.pdf`. → its side: the landed template recommends one shallow, redacted, user-approved matter packet without automatic internal depth. ← this row's side: a Pleadings branch inside that packet *is* automatic internal depth, and would be created for a document class the packet already holds. The neighbour's recommendation forecloses the row.

**vs `legal.personal-legal-matters`.** Fixture: `Divorce Petition - my own - filed copy.pdf`. → its side: the holder is a party in their own proceeding; court vocabulary plus holder-name match, no practitioner anchor. ← this row's side: would need a practitioner-side representation anchor, which is absent; and even with one, the document is `legal`'s.

**vs `law_practice.court-filing-record` (landed).** Fixture: `Complaint - Hartley v Nash - CONFORMED.pdf` — *the same fixture appears on that row's own file-example list.* → its side: the conformed stamp, the notice of electronic filing, the affidavit of service and the fee receipt are a transmission-receipt layer whose authority is neither holder nor client. ← this row's side: it would claim the document *under* the stamp — and does not get it, because that document is `legal`'s. Note the consequence recorded as an open question: that row states it holds neither the document that was filed, its siblings owning that on the document's own evidence, and it lists `law_practice.pleadings` in `collides_with`. With this refusal that deferral points at nothing.

**vs `law_practice.precedent-bank`.** Fixture: `Claim Form N1 - blank - firm precedent v3.docx`. → its side: an instrument-shaped document whose party and execution slots are empty *by design*, with drafting notes and a firm template version marker — the schema's inverse-recognition signal, and the one part of this family holding no third party at all. ← this row's side: would have to claim the blank form as "an unfiled pleading," which is both a lifecycle framing and a duplicate of a sibling.

**vs `law_practice.motions-and-briefs` and `law_practice.appeals`.** Fixture: any captioned, numbered, counsel-signed submission. → their side: a different document-type word on the front page. ← this row's side: the same. The three rows are discriminated only by a genre word, which is never-alone — which is why this refusal's reasoning reaches them and why that is surfaced below rather than acted on.

Neighbours considered that got **no** edge: `career` — a consulting engagement letter shares fees and signature blocks but has no caption and no proceeding, and the schema already argues that seam; `finance` — a court fee receipt is Receipts and Confirmations' or `finance.receipts-expenses`', and it is a receipt rather than a pleading, so there is no same-evidence mutex here; `government.social-services-casework` — casework files mention proceedings but activate on an agency-and-subject casework structure, not a caption; `law_practice.discovery` and `law_practice.evidence-exhibits` — the bundle fixture is theirs on index structure, which is a clean structural boundary rather than a collision.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false`.

Nothing was proposed and nothing was minted. `law_practice` declares no field rows under PR-6 and D1's deferral stands; a refused row proposes none by definition. The candidates that would have been tempting — a case or docket identifier, a pleading kind, a party, a filing date, an amendment number — are all rejected twice over: they are not canonical keys, and the first two are the very tokens the never-alone list strikes. `jurisdiction` remains unavailable under the current decision brief. Whatever a template eventually recommends stays a recommendation: "the user can reverse, remove, add, or flatten dimensions." *(verbatim, para 95.)*

## Where the coverage goes (legacy `law.pleadings` is not dropped)

- Filed, served or conformed statements of case, and the executed/verified ones → `legal`, on `legal`'s own proceeding evidence, with safety protection running first; inside a practitioner corpus they join `legal.practice-matter-file`'s one shallow protected packet.
- The holder's own pleading in the holder's own dispute → `legal.personal-legal-matters`.
- Stamps, notices of electronic filing, proofs of service, filing-fee receipts, docket entries → `law_practice.court-filing-record` (already landed and already claiming them).
- Blank forms and firm precedents with placeholder parties → `law_practice.precedent-bank`; Reading Inbox when inactive, since they contain no client and no third party.
- Instructions to counsel, drafting comments, internal notes on a draft → `law_practice.opinions-advice` and `law_practice.matter-correspondence`.
- Bundles and tabbed indexes → `law_practice.evidence-exhibits` / `law_practice.trial-preparation`.
- Residuals: **Protected Records** (an isolated statement of case about a named third party — the cautious error is the cheap one), **Review Later** (side unresolved: ours or theirs), **Reading Inbox** (specimen and precedent pleadings), **Unsupported or Encrypted** (locked bundles and exports, never forced open), **Temporary Screenshots** (a positively evidenced portal capture whose OCR establishes no matter).

## NEEDS-JOSEPH

**NJ-1 — Sibling symmetry.** `law_practice.motions-and-briefs`, `law_practice.appeals` and `law_practice.orders-and-judgments` rest on the same caption-plus-party-pair structure, separated from this row only by a document-type word. The argument that refuses this row appears on its face to reach all three. Alternatives: (a) refuse them together and route the same way; (b) fold them into one `law_practice.proceeding-documents` row — which must still defeat the `legal` concession before it can exist, and this memo's view is that it cannot; (c) retain them on evidence this row did not see (e.g. an order or judgment is *authored by the tribunal*, which is arguably a distinguishable authority-asserted structure closer to the filing record's than to a pleading's — that is the strongest of the three retentions and R1c should test it first). **This row edited none of them.**

**NJ-2 — A dead deferral to repair.** `law_practice.court-filing-record` defers "the document that was filed" to "its siblings" and names `law_practice.pleadings` in `collides_with`. If this refusal stands, that edge points at a refused row. Recommendation to R1c: redirect the deferral to `legal` and `legal.practice-matter-file`, and drop or downgrade the dead edge. Alternatives: leave the edge as a refusal marker (harmless but misleading), or reopen this row (not recommended, for the reasons above). **This row did not edit that file.**

**NJ-3 — Third-party protection at the right level.** `legal` protects the *holder's* own record. A pleading in a practitioner corpus is about someone else — an adverse party, a child, an accused. Routing to `legal` plus Protected Records is this row's answer and it is defensible, but it inherits a posture designed for a different beneficiary. Alternatives: (a) accept the routing as sufficient; (b) have `law_practice` attach its third-party posture at schema level so it applies to co-activated `legal` material inside a practitioner corpus; (c) let P7 own it entirely. This is a Joseph decision, not a row decision.

**NJ-4 — The narrowing that was considered and not taken.** Reframing the row as *originating process only* — the one document that starts a proceeding — was the last available save. It was rejected because "originating" is a lifecycle position plus a document type, and the resulting row would hold one document per matter, which is a one-child level by construction. Recorded here so the option is visibly closed rather than silently unconsidered.

## Self-verification

- JSON parses (`python3 -m json.tool`); key set is identical to the landed sibling `law_practice.court-filing-record.json`, including `proposed_context_terms`.
- Every quoted span was grep-verified verbatim against `planning/00-database-agent-product-design.md` before it was written (paras 35, 52, 95, 97, 120). No quotation is attributed to `00` that was not matched.
- Every edge id is on the roster: `legal`, `legal.personal-legal-matters`, `legal.practice-matter-file`, `law_practice.court-filing-record`, `law_practice.precedent-bank`, `law_practice.motions-and-briefs`, `law_practice.appeals`. Every `falls_through_to` value is one of 00's nine residual names.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a fact. Sparse and degraded files carry `group_without_copying_facts: true` rather than inventing a matter.
- At least one `never_alone` is true of a tempting false file: the counsel-block entry is tripped by `Pleadings - Smith v Jones - specimen from practitioner text.pdf`.
- No thresholds, no counts, no handling classes, no field keys minted.
- Files written: exactly `planning/domains/nodes/law_practice.pleadings.json` and this memo. No roster, canonical-fields, `check.py`, `src/`, SPEC or neighbour file was touched.

---

## R1b — `collides_with` signal migration

**What changed.** All seven `collides_with` entries were bare id strings; each is now `{domain, signal, provenance}`. The single `also_holds_with` entry (`legal`) was likewise a bare string and is now an object. No neighbour was added or removed — every id on the list survived the exercise, and none of the seven turned out to be a false edge. Nothing else in the JSON was touched.

**Why nothing was deleted.** The refusal argument makes this row's collisions *sharper*, not weaker. A refused row still has to say where each contested item goes, and every one of the seven pairs does compete for a nameable fixture:

| neighbour | the one fixture both sides would claim | what decides it |
|---|---|---|
| `legal` | `Complaint - Hartley v Nash - CONFORMED.pdf` | the caption-plus-matter-identifier structure is `legal`'s own activation signal, read off the document's face; the practitioner/client slot pair that would be needed here is absent |
| `legal.personal-legal-matters` | `Divorce Petition - my own - filed copy.pdf` | which slot the holder occupies — party vs counsel |
| `legal.practice-matter-file` | the same conformed complaint inside a practitioner file | an explicit representation link (holder or holder's firm named as representative, joined to an engagement record) vs genre alone |
| `law_practice.court-filing-record` | the same PDF, and the e-filing screenshot | layer and issuer: a stamp/envelope/service slot asserted by a non-holder, non-client authority is a transmission event, not the document |
| `law_practice.precedent-bank` | `Claim Form N1 - blank - firm precedent v3.docx` | absence *by design* (placeholder party slots, empty statement of truth, template version marker, no case number) vs a live case identifier plus a filing stamp |
| `law_practice.motions-and-briefs` | a captioned, numbered-paragraph, counsel-signed filing in the same matter | whether the operative slot asks for relief short of the final outcome |
| `law_practice.appeals` | an amended/responsive statement of case in a matter that has gone up | the two-tier proceeding-identifier pair, plus the independently paginated record compilation |

**No `design_cite` was added.** `design_cite` is optional and every existing quotation in this row was grep-verified against `planning/00-database-agent-product-design.md`. None of the seven discriminators is stated as a verbatim span in `00` — the discriminators are structural readings of the neighbours' own `recognition.deterministic`, so citing `00` for them would be a fabricated attribution. The `law_practice.precedent-bank` discriminator is stated almost exactly at `planning/domains/07-law-legal-practice.md:456`, but `07` is not the design document `design_cite` points at, so it is paraphrased in the signal and cited here instead.

## R1c items raised by this migration

**R1c-A — kind mismatch on two edges, and this row may not fix it.** `CONNECTION.md` line 241 restricts `collides_with` to *schema ↔ schema, or template ↔ template (same kind only)*, and line 242 restricts `also_holds_with` to *schema ↔ schema only*. This row is `kind: template`, and `legal` is `kind: schema` — so the `legal` entry is malformed on **both** lists, whatever its signal says. It was kept rather than deleted because the underlying confusion is real and the fixture is named; deleting it would lose the finding. The sibling `law_practice.appeals` shows the shape the contract wants: its `collides_with` lists only templates, reaching `legal` through `legal.personal-legal-matters`. R1c should decide between (a) re-pointing this row's `legal` collision at `legal.personal-legal-matters` and `legal.practice-matter-file`, which are already listed and already carry the same fixtures, and deleting the schema-level entry; (b) lifting the schema-level edge to the `law_practice` ↔ `legal` schema pair, where both `collides_with` and `also_holds_with` would be well-typed; or (c) relaxing the kind rule. Option (b) is this row's recommendation for the `also_holds_with` edge specifically, since the co-activation it describes is genuinely a schema-level fact about `law_practice` and `legal`, not a fact about this refused id.

**R1c-B — reciprocity is owed by six neighbours and none of it may be written here.** `collides_with` is symmetric and reciprocity becomes enforced post-migration (`CONNECTION.md` line 241, and the audit note at line 494). Of the seven, only `law_practice.court-filing-record` is known to list this row back. `law_practice.appeals` does **not** list `law_practice.pleadings` even though its own `collides_with` includes the sibling proceeding rows. R1c should reciprocate — or, if this refusal is adopted, drop the pair rather than reciprocate it, which is R1c-C.

**R1c-C — the refusal makes six of these edges provisional.** If `law_practice.pleadings` is accepted as refused, a collision edge *to* a refused id is an edge to something that never activates. The signals above are still worth keeping, because each one records where the contested fixture actually goes — but R1c should decide whether they survive as edges on this id or are re-homed onto the receiving rows (most naturally `legal.practice-matter-file` and `law_practice.court-filing-record`). This is the same dead-deferral problem already recorded in `open_question` item (2), now generalised: it applies to all six, not just to `court-filing-record`.

**R1c-D — `law_practice.precedent-bank` and `law_practice.motions-and-briefs` have no node file yet.** Both are roster rows (`ROSTER.md:636` and `ROSTER.md:619`), so the edges are legal, but the signals above were written against `planning/domains/07-law-legal-practice.md` rather than against an authored neighbour node. When those rows are authored, R1c should re-check that the discriminators here match what the rows actually claim — particularly `precedent-bank`, whose whole discriminator is the inverse-recognition pattern this row's fourth file example already carries.
