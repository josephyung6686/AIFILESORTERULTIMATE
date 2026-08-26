# Research memo — `engineering.project`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/engineering.project.json`
Roster row: template on the `engineering` schema, `parent_id: null`, `launch: placeholder`, absorbs legacy `eng.engineering-project`

## Result

**REFUSED.** `engineering.project` is the `engineering` schema's own default template with the word *project* written on it. It fails all three legs of the CONNECTION.md §2 node test measured against that default, and it fails two further independent grounds — it is defined by an absence, and the "branch root" job it is really doing is browse shelving, which PR-5 hands to R1c.

Coverage of the absorbed legacy id is not lost. It routes to the engineering schema's default template and its named siblings (technical definition), `business_operations.project-delivery` (schedule, budget, governance), `construction_property.construction-project` (site and instruction), `manufacturing.production-record` (execution), and the residual templates.

## The charge, stated at full strength before anything else

The strongest case against this row is not that it is thin. It is that **it is a duplicate twice over, and the second duplication is the fatal one.**

The obvious charge is that "project" is a *work_type-adjacent organising noun* — the name of the undertaking that pays for a file, not a description of the file. That charge is real but survivable in principle: `project` is a canonical field, and organising by project is exactly what `00` recommends for record domains.

The fatal charge is narrower. The `engineering` schema row's researched default dimension order is:

> project → design_item → lifecycle_stage → engineering_artifact_type

The schema's **first default dimension is already `project`**, and the schema's landed fixture set is already one project's controlled definition end to end — `SYS-REQ-042_Braking-System-Requirements_RevB.docx`, `BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`, `BPA-210_Product-Structure.xlsx`, `ECR-1187_BPA-210_Bushing-Material.pdf`, `BPA-210_DVT-07_Verification-Report.pdf`, `TDP_BPA-210_Baseline-C.zip`. A template whose subject is "the project" on a schema whose default template already leads with the project, illustrated with a project's own files, is that default template under another name.

I then tried to defeat this charge, five times, with the strongest defences I could construct. All five failed. That work is below, because a refusal is only worth something if the defences were tried honestly.

## Binding material read

Deliberately narrow, per the dispatch's token constraint. Sources actually opened:

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from `make_prompt.py engineering.project`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth calibration.
- `planning/domains/nodes/engineering.json` — my schema anchor. Read `node_test`, `recognition`, `work_types`, `proposed_fields`, `template`, `file_kinds`, `collides_with`, `also_holds_with`, `falls_through_to`, `sensitivity`, `grouping_reasons`. This is the DEFAULT TEMPLATE I am measured against, and it decided the outcome.
- `planning/domains/nodes/engineering.automotive-program.json` and `engineering.commissioning-handover.json` — the only two landed nodes that argue a boundary naming `engineering.project` (found with one `grep -rl`).
- `planning/domains/roster.json` — verified every edge id exists; `planning/domains/ROSTER.md` §Appendix A — confirmed `eng.engineering-project → engineering.project` and enumerated the 24 `engineering.*` siblings.
- `planning/00-database-agent-product-design.md` — by targeted `grep -n` only, never streamed. Four spans verified verbatim (below).

Not opened, on purpose: other rows' research memos, `01-product-design-structured.md`, and the `engineering.research.md` companion — the JSON anchor left the node test decided, so the companion was not needed.

## Quotations, grep-verified verbatim from `00`

Each of these greps back out of `planning/00-database-agent-product-design.md` exactly as written.

1. Line 63 — the never-alone rule I read across to a project name:
   > "A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization."

2. Line 95 — the dimension-order rule that the schema default already cites for putting project first:
   > "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

3. Line 120 — the three residual homes I route to:
   > "Independent Records may live under Personal/Independent Records and hold standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group."
   > "Review Later may hold files whose meaning is partly understood but whose final location requires a future decision."
   > "Unsupported or Encrypted may hold—or, more safely, represent without moving—password-protected archives, unreadable documents, damaged files, and unknown formats."

Everything else in the node is marked `inference` and argued, or is quoted from the `engineering` schema row (which I cite as a sibling artifact, not as `00`).

## The node test, all three legs

### Leg 1 — detection signals: not its own, and the space is already closed

The `engineering` schema's own recognition block closes the space exhaustively, in two clauses I did not have to interpret:

- deterministic, last entry: *"parent-folder context naming an item number or program may raise plausibility only after one controlled-definition structure is present; it never fires the schema by itself"*
- never_alone, second entry: *"a project name or project plan alone. That is business_operations.project-delivery unless controlled technical-definition evidence also appears"*

Put those together and there are exactly two states, not three:

| evidence present | who fires |
|---|---|
| project identity **+** controlled technical-definition structure | the `engineering` schema, on its **default template** (or a named sibling that owns that structure) |
| project identity **without** controlled-definition structure | `business_operations.project-delivery`, or a residual |

There is no third state for a project-root row to occupy. Its candidate signals are the schema default's, minus whichever sibling owns the specific artifact — and the siblings own nearly all of them: `requirements-specification`, `drawing-package`, `cad-model`, `bill-of-materials`, `change-order`, `simulation-analysis`, `verification-validation`, `prototype-build`, `stage-gate-review`, `commissioning-handover`, `material-specification`, `risk-analysis-fmea`, `electrical-schematic`, `pcb-layout`, `embedded-firmware`, `product-certification`, `standards-library`, `industrial-design`, `civil-structural`, `process-plant-design`, `aerospace-airworthiness`, `invention-disclosure`. Perform the subtraction and the residue is a programme name.

A programme name cannot activate anything, by read-across from `00`'s university-name rule (quote 1). The reasoning there is role ambiguity, and a project name is weaker: "Harbour Works" can appear as the client's undertaking, the contractor's job, a cost centre, an email subject prefix, a folder someone made, or a word in a marketing deck. The schema row itself already refuses the identical move for a neighbouring schema, holding that a repository is not engineering merely because its employer builds hardware. An industry, an employer and a project are the same class of never-alone token.

### Leg 2 — dimensions: a truncation of the default, not a different order

Any order this row could recommend is `[project]` or `[project, engineering_artifact_type]`. Both are **prefixes of the schema's default order**, with later levels removed. Their first level is the default's first level. Their justification is the default's justification — `00` line 95 (quote 2), which is the clause the schema's `template.why` already invokes.

A recommendation that is the default's recommendation minus information is not a distinct recommendation; it is the default with the design item and lifecycle state deleted, which makes retrieval worse, not different. And under PR-6 the order must be empty anyway — which is itself part of the finding. A placeholder template whose empty `dimension_order` would resolve, once fields are ratified, to its own schema's order is the schema's default template.

I checked whether the two candidate levels that *feel* project-specific are dimensions. They are not. "Phase" is `lifecycle_stage`, already the default's third level. "Year" is time, which `00` keeps out of first position for record domains (quote 2) and which in practice is a token inside the programme name (`2027 Harbour Works`) rather than an independent fact.

### Leg 3 — privacy rules: identical, object for object

The `engineering` schema is already `potentially_sensitive`, justified by proprietary design definition, supplier data, safety analyses, signatures and export-controlled or critical-technology information. A project folder is a bag of exactly those objects. Aggregating them raises exposure *surface* — a whole programme in one place — but the *rule* is unchanged, and this phase's vocabulary is only `none | potentially_sensitive`, with handling classes belonging to P7. I could not name one file this row would hold that carries a privacy rule the schema does not already state. That is the third leg failing.

### Two further grounds, independent of the three legs

**Definition by absence.** The row's own `one_line_hint` defines it as engineering material carrying a project identity *"but no more specific sub-domain."* That is the residual concept restated inside a schema. `00` already supplies nine residual homes for material that has partial meaning and no better place (quote 3 covers the three I use). A within-schema residual duplicates the residual library.

**Browse, not activation.** "Branch root" is a shelving role. `roster.json`'s own header comment records that *parent_id is everywhere null: PR-5 leaves browse shelving to R1c*, and the dispatch prompt states that `parent_id` is browse-only and must be ignored for activation. A row that exists so a browse tree has a trunk is not a detection node. If R1c wants a trunk, it should express it as browse structure, not as a template carrying detection signals.

## Files considered and rejected — the five defences, and why each failed

**Defence 1 — the multi-artifact project packet.** A whole project archive (`TDP_BPA-210_Baseline-C.zip`, `Harbour_Works_Handover_Pack.zip`) contains many sibling-owned artifacts and no single sibling can hold it; surely the project row holds the packet? *Failed:* the schema's deterministic list already contains *"an archive manifest that exposes several of the above structures under one item/baseline without extracting members to disk"*, and `TDP_BPA-210_Baseline-C.zip` is the schema's own landed fixture. The default already owns manifest-level recognition. A mixed packet is additionally a grouping neighbourhood, and CONNECTION.md keeps grouping separate from activation.

**Defence 2 — engineering project management.** Timing plans, WBS, resource loading, design-review schedules, technical status reports: engineering-flavoured project artifacts nobody else wants. *Failed, decisively:* the schema's collision entry for `business_operations` names this and settles it — *"Sprint-14-Project-Status.xlsx is the collision fixture: an engineering team and project name do not make an engineering schema."* This material is `business_operations.project-delivery`'s. Claiming it here would contradict my own schema anchor.

**Defence 3 — physical trades and engineering services.** The hint mentions "manufacturing and physical-trades material," so perhaps an engineering-services firm's job folder. *Failed:* a trade job with a customer and a site is `construction_property.trade-job` or `construction_property.construction-project`; production execution against a released definition is `manufacturing.production-record`. Neither becomes engineering by having a project name on it, and the schema's collisions with both are already authored.

**Defence 4 — product identity without a lifecycle artifact.** A file that names a design item but carries no requirement, drawing or verification structure. *Failed both ways:* `design_item` is the schema's second default dimension, so an item plus one controlled structure *is* the default firing; and an item identifier with nothing else trips the schema's own never_alone — *"a part number, drawing number or other short identifier alone; it can be a stock code, purchase line, asset tag, site drawing, invoice reference or arbitrary number."*

**Defence 5 — it is needed as a routing target.** `engineering.automotive-program`'s landed refusal routes programme identity here: *"engineering.project is the row that already carries the programme identity when no more specific sub-domain applies."* *Failed:* that is a naming convenience, not evidence. The correct route is "the engineering schema's default template." Two refusals must not route to each other. This is recorded as NJ-1 and as a `collides_with` entry, and I did not edit that row.

Also considered and rejected as this row's evidence: a directory named for a programme (never-alone for every child inside it); a recurring engineering sync `.ics` (`business_operations.meeting-record`); a project cost report (`business_operations.budget-forecast`); a project risk register (`business_operations.risk-register`); a password-protected project archive (residual — no purpose from a filename).

## The collision fixture

**`Harbour-Works_Engineering-Programme-Plan_v7.xlsx`** — tabs named Timing, Resource Loading, RAG and Budget; rows carrying workstream owner, planned start, planned finish, percent complete and forecast cost; workstreams named for engineering disciplines (Structures, Controls, Piping).

This is the file that most looks like `engineering.project`'s evidence: it is the *central* document of an engineering programme and its filename contains both words. **What discriminates it:** every column is schedule, cost or ownership; there is no requirement identifier, drawing number, item number or revision column anywhere in the workbook. Discipline names are not design items. It is `business_operations.project-delivery`, and the engineering schema's own never_alone says so.

A second collision fixture is inherited rather than invented: **`Project Closeout Report - Harbour Works.pptx`**, named on the landed `engineering.commissioning-handover` row against `business_operations.project-delivery`. Both sides of that boundary are already authored by rows that exist. A project-root row inserted between them would give the same deck a third claimant with no discriminating evidence of its own — which is a clean demonstration of the harm this row would do.

## Reciprocal boundaries

Every boundary below is stated in both directions and names the same fixture bytes on both sides. All six neighbour ids were verified present in `planning/domains/roster.json`.

- **`business_operations.project-delivery`** — bytes `Harbour-Works_Engineering-Programme-Plan_v7.xlsx`, `Project Closeout Report - Harbour Works.pptx`. → schedule/budget/governance evidence is theirs whatever the team's industry. ← their row does not become engineering when its project is an engineering programme; crossing requires controlled technical-definition evidence in the same file, and then the schema **default template** or a named sibling holds it.
- **`engineering.stage-gate-review`** — bytes `BPA-210_Design-Review-Pack_CDR.pptx`. → gate packs and phase-exit decisions were the most template-shaped material this row could claim; that row owns the gate-and-decision relation. ← that row does not extend to a programme's whole file population because a gate names the programme.
- **`engineering.commissioning-handover`** — bytes `Project Closeout Report - Harbour Works.pptx`. → close-out and handover language overlap almost exactly, and that landed row already draws this line against business operations. ← that row holds technical acceptance of an installed instance (tag-level acceptance results plus a takeover date) and does not absorb design-definition or schedule material because a programme is closing.
- **`construction_property.construction-project`** — bytes `2027 Harbour Works Engineering Project/`. → when the project identity resolves to a site joined to an instruction or contract, coverage is theirs. ← their row does not gain the engineering schema when a site package contains equipment design definition; both relations may hold, each separately evidenced.
- **`manufacturing.production-record`** — bytes `LOT-24-081_Final-Inspection.xlsx`. → execution records citing a released revision stay there; a project-root row would have pulled them in on the shared programme name alone. ← that row does not become engineering by citing Rev C, and does not own the change record that altered Rev C (`engineering.change-order`, which may also hold manufacturing when a nonconformance triggered it).
- **`engineering.automotive-program`** — bytes `Vehicle-Programme-Timing-Plan_MY27.xlsx`. → that row is already refused and routes programme identity here. ← this row is refused one level up for the same structural reason: it is the schema's default template with a project noun, exactly as that row is this row with an industry adjective. Both must route to the schema default, not to each other.

`also_holds_with` is empty: a refused row cannot legally coactivate. The real coactivations (`ECR-1187` holding engineering and manufacturing; a plant package holding engineering and construction_property) are already authored on the schema row.

`role_split` is empty: no field pair exists to split, and PR-6 leaves the schema fieldless.

## Fields and dimensions

`fields: []` — correct twice over: this is not a schema anchor, and PR-6 leaves `engineering` fieldless.

`proposed_fields: []` — deliberate. I considered proposing nothing and confirmed that is right: `project` is already canonical and already the schema's first proposed default dimension; `design_item`, `lifecycle_stage`, `engineering_artifact_type` and `revision_or_baseline` are already on the schema row awaiting R1c. Minting anything here would be a variant of a live proposal, which the brief forbids. Proposing a field to justify a refused node would also be the 574's exact failure mode.

`template.dimension_order: []`, `time_first: false`.

## Open questions — NEEDS-JOSEPH

**NJ-1 (cross-row repair, for R1c — I did not edit that file).** `engineering.automotive-program`'s refusal routes programme identity and its timing-plan fixture to `engineering.project`. With this row also refused, that route dangles. Alternatives: (a) re-point it at "the engineering schema's default template" plus `business_operations.project-delivery` — my recommendation, since it names an artifact that exists; (b) keep `engineering.project` alive purely as a routing label, which reintroduces a node with no detection signals and is the move this memo argues against; (c) leave both refusals pointing at each other, which is a cycle with no terminal owner.

**NJ-2 (browse shelving).** Twenty-four `engineering.*` rows currently have `parent_id: null`. If a browse trunk is wanted for them, is it expressed as `parent_id` under PR-5, or does R1c want a trunk *row*? If a trunk row is chosen, it must be marked browse-only and carry no detection signals, or this refusal is silently reversed.

**NJ-3 (a genuine gap I could not close).** The refusal is safe only if a project's *engineering-flavoured management* material really is `business_operations.project-delivery` at retrieval time. A user with one engineering programme may reasonably expect its timing plan and its drawings to sit together. That is a **grouping** expectation, and P9 can satisfy it from an exact project anchor without either row changing. If Joseph decides grouping cannot satisfy it, the fix is a P9/browse decision, not a new template — but it should be an explicit decision rather than an assumption inherited from this memo.

**NJ-4 (deferred, not mine).** If PR-6 lifts and `design_item` / `lifecycle_stage` / `engineering_artifact_type` become legal, the schema's default order becomes concrete and this refusal gets *stronger*, not weaker — `project` is level one of that order. R1c should re-check this row at that point only to confirm it stays refused.

## Self-verification

- `python3 -m json.tool` parses `engineering.project.json`.
- Key set matches the landed siblings (`engineering.json`, `engineering.automotive-program.json`), including the optional `node_test` and `grouping_reasons_note` keys those rows carry.
- All four `00` spans in quote marks grep back verbatim from `planning/00-database-agent-product-design.md` (lines 63, 95, 120).
- Every edge id — `business_operations.project-delivery`, `engineering.stage-gate-review`, `engineering.commissioning-handover`, `construction_property.construction-project`, `manufacturing.production-record`, `engineering.automotive-program` — was confirmed present in `roster.json`. `construction_property.project-record` was checked, does **not** exist, and was not used.
- All three `falls_through_to` names are `00` §7.3 residual names in `00`'s spelling.
- Every `file_examples.source_type` is in `SOURCE_TYPES`: spreadsheet, design_creative, text_document, archive, presentation, filesystem, calendar, opaque_binary.
- No threshold numbers, no confidence scores, no handling classes, no folder path written as a fact.
- Wrote only `planning/domains/nodes/engineering.project.json` and this memo. No roster, canonical-fields, `check.py`, `src/`, SPEC or neighbour-node edits.
