# Research memo — `law_practice.client-intake`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.client-intake.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

Accepted, but narrowly, and with one merge question left open for R1c. The row survives because it holds a positively structured artefact family — the prospective-party enquiry form, the client due-diligence pack, the enquiry register and the non-engagement letter — that the `law_practice` schema's own default template **cannot activate on**, and because its exposed party is a person who may never have become a client at all. It does not survive as "the first stage of a matter", and most of the work below is spent proving the difference.

## The charge against this row, put at its strongest

Before writing anything I argued the case for killing it. Four of the eight disqualifiers in the brief land, and two of them land hard.

**1. It is a lifecycle stage.** Intake is the opening phase of a matter, the way "draft" is a phase of a document. Phases are not nodes. On this reading `law_practice.client-intake` is `law_practice` restricted to `t = 0`, and the roster is one row poorer for splitting a timeline.

**2. It is a duplicate of its own schema's default template.** This is the sharpest form. The `law_practice` schema anchor lists, as its *second* deterministic signal and in its own words, "AN INTAKE-AND-CONFLICTS structure, and it is the family's cleanest signal because `legal`'s signals do not fire on it at all", describing a form pairing a prospective-client slot with a matter-description slot, a responsible-practitioner slot, a conflict clearance and a review action. The schema also carries "client intake, identification and conflicts screen" as the first entry in its `work_types[]`. A template whose whole content is one of its schema's own named signals *and* one of its schema's own work-type values is, on its face, a duplicate wearing a value as a hat.

**3. It is squeezed to nothing by two siblings.** `law_practice.conflicts-check` and `law_practice.engagement-terms` are both live roster rows. Conflicts owns the search and clearance; engagement owns the retainer, scope and funding basis. If those two are subtracted, "intake" may be a residue rather than a thing.

**4. It is a row defined by an absence.** The most tempting distinguishing feature — no matter reference has been allocated yet — is the absence of something. The brief names that as a disqualifier explicitly, and it is exactly the trap this row would fall into if allowed to lead with it.

Two further disqualifiers were checked and do not apply: it is not a file format or medium (the fixtures span `text_document`, `spreadsheet`, `image`, `ocr`, `email`, `archive`), and it is not an organisation name (nothing here activates on a firm's name — the deletion test is inherited from the schema unchanged).

## Why the charge is defeated

**Against (2), the duplicate charge — the decisive argument.** The schema's default requires **both legs**: "(i) an exact matter, file or engagement reference repeated across two or more artefacts, and (ii) at least one artefact whose own labelled slots separate a PRACTITIONER OR FIRM role from a CLIENT role." Leg (i) is unavailable in this world by construction. The matter reference is *allocated by* the matter-opening record, which is downstream of the decision this row's material feeds; on a declined enquiry it is never allocated at all. So the schema's default recognition **cannot fire** on the enquiry form, the due-diligence pack, the enquiry register or the decline letter, no matter how clean the schema thinks the intake signal is. A template whose material is invisible to its schema's default two-leg rule differs from that default in the leg that matters most — detection — and CONNECTION's node test asks exactly that. The schema naming intake among its signals is evidence that this material is in-family; it is not evidence that the family's default can recognise it.

**Against (4), the absence charge.** The row does *not* lead with the absence. It leads with three positive labelled structures, each of which exists on paper and each of which I can name a real document type for: a form whose own slots read prospective/proposed party plus nature of enquiry plus disposition; a verification checklist whose rows are per identity document with a *certified-by* attestation; and a letter whose body states that the practice will not act and that no retainer arises. The missing matter reference appears in the JSON demoted to a *corroborating condition* with the explicit sentence that it activates nothing alone. That demotion is the difference between a node and a hole.

**Against (1), the stage charge.** The discriminator is not earliness. An intake pack collected in year three of a long client relationship, for a new instruction, is this row's; a first draft pleading written on day one of an opened matter is not. Time does not sort the fixtures — labelled role and disposition do. A stage would also have no distinct residual rule; this row has one, below.

**Against (3), the squeeze.** After subtracting both siblings there is a real remainder, and it is not scraps: the requested-work/instructions form, the identity due-diligence pack and its source-of-funds evidence, the pre-opening interview note, the enquiry register, and the non-engagement letter — which neither sibling can hold, because conflicts-check's structure is a searched-names list and a clearance result, and engagement-terms' begins at a retainer that by definition does not exist here. I nevertheless think this is a genuine question and have surfaced it as **NJ-1** rather than smoothing it: in many practices intake and conflicts are one sheet of paper.

**And the privacy leg, which is independent of all four.** The schema's posture protects a third-party *client*. This row's exposed person may have been **refused**. No engagement justifies the practice holding their passport, their bank statements and an account of their trouble; nobody stands in a position to consent for them; and the record's mere existence discloses that a named individual approached this practice about this kind of problem and was turned away. That is a stricter posture than the schema default on a specific, argued axis, which is the second of the three legs CONNECTION allows.

**The third leg — dimensions — the row concedes and then wins differently.** Under PR-6 no field exists, so `dimension_order` is empty for every row in this family and no template can distinguish itself there. What this row *can* say, and did, is that the schema's prose recommendation (client, then matter, then function, then period) has its **top two levels struck outright** here: there is no matter, and there is no client — only a person who asked. The recommendation held as prose is therefore no person level at any depth, the intake episode as one shallow protected unit, function inside it only on request, period last.

**Verdict.** Two of three legs differ substantively and the third differs in prose. `refuse_node: false`.

## Sources actually read

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from `make_prompt.py law_practice.client-intake`; `planning/domains/nodes/legal.practice-matter-file.research.md` in full as the depth calibration; `planning/domains/nodes/law_practice.json` read by key extraction (`template`, `recognition`, `work_types`, `sensitivity_why`, `falls_through_to`, `collides_with`) rather than streamed; `planning/domains/roster.json` for id verification; and `planning/00-database-agent-product-design.md` by targeted string lookup only. Every `00` span quoted in the node was located verbatim in `00` before it was written, by exact-substring search rather than paraphrase: the stop rule "It should not form a supported group when there is no valid anchor"; the direct-fact clause ending "or a labeled form field"; "The default posture must therefore be local-first and data-minimizing"; the corpus sentence beginning "identity documents, account statements"; the Protected Records, Review Later and Unsupported or Encrypted residual sentences; the safety-domain sentence ending "before any cloud or automated placement decision is allowed"; the time-ordering sentence "For document and record domains, project, function, or subject usually comes before time…"; and "create meaningless one-child levels". No span is quoted that I did not locate.

## Files considered and rejected

The row is as much these as it is its fixtures.

- **`Conflict Search Result - Vance v Northgate Retail.pdf`** — kept in the JSON as a fixture *for the boundary*, not as evidence. Searched names, hit/no-hit, clearing practitioner, clearance decision: no requested-work slot, no identity rows. It is `law_practice.conflicts-check`'s on that row's own evidence.
- **`Client Care and Retainer Letter - Vance - executed.pdf`** — rejected twice over. It carries a bound party pair and an execution block, so it fires `legal`'s executed-instrument signal, and `legal` is a safety domain whose protection runs first; and its content is the retainer, which is `law_practice.engagement-terms`'.
- **`Employee Onboarding - Right to Work Check - J Okafor.pdf`** — the structural twin, rejected on one slot. Identical per-document verification grammar and certifier attestation. It names a job title, a start date and a hiring manager; the person will do work *for* the holder. `hr.onboarding-offboarding`'s.
- **`New Client Onboarding Questionnaire - Northgate Retail.pdf`** — rejected because "client intake" is a phrase whole industries use. Scope of services, deliverables, milestones, prepared-for/prepared-by blocks: `career.consulting-client-engagement`'s.
- **A bare `Passport scan.jpg` with no surrounding pack** — rejected as activation evidence and kept only as a never-alone case. A scan says what the document is, never whose corpus it belongs in. It routes to Protected Records unclaimed.
- **A bare account statement** — rejected. Finance owns statement structure on its own evidence; only the practice's own covering label makes it intake evidence, and even then no finance fact is copied here.
- **A practice-management or CRM database file, and a live intake mailbox** — rejected as source systems rather than file nodes, following the landed neighbour's reasoning. A bounded export with a readable manifest is represented instead.
- **A blank firm intake template** — accepted as a fixture but deliberately *not* as protected material, and routed to Independent Records. It has the full labelled structure and nobody in it. This mirrors the schema's precedent-bank inverse-recognition logic and guards against the row learning that intake-shaped layout is what makes a file sensitive.
- **Client-name gazetteers, practice-area lists, AML regime taxonomies, jurisdiction rules, retention periods** — rejected wholesale. R4 owns gazetteer contents, R2 owns detector regexes, and J-IND defers industry depth. The node states no threshold, no period and no regulatory conclusion.

## Collision fixture, stated as required

The single file that most looks like this row's evidence and is not: **`Employee Onboarding - Right to Work Check - J Okafor.pdf`**. It has the certified-copy attestation, the expiry column, the date-seen column and the attached ID scans — the exact grammar of a client due-diligence pack. What discriminates it is the **direction of the work**: HR's form asks what the person will do *for* the holder organisation and carries a job title and a start date; this row's form asks what the person wants done *for them*. Where neither directional slot is present, neither row activates: the pack is protected once and left for Review Later, which is the cheap error.

## Reciprocal boundaries

Each is stated in both directions in the JSON, naming the same fixture on both sides. Summarised:

| Neighbour | Shared fixture | This row fires when | Neighbour fires when |
|---|---|---|---|
| `law_practice.conflicts-check` | combined intake-and-conflicts form | prospective-party + requested-work + disposition, or per-document identity attestation | searched-names list + hit/no-hit + clearance decision |
| `law_practice.engagement-terms` | client care / retainer letter | costs and funding info given *before* acceptance; decline letter | retainer, scope, funding basis after a decision to act (also `legal`, on execution) |
| `legal.practice-matter-file` | client-and-matter intake or assessment doc | enquiry with a disposition and no matter reference | an accepted representation is separately evidenced |
| `career.consulting-client-engagement` | new-client onboarding questionnaire | legal practitioner/client role split + identity rows | services scope, deliverables, milestones, prepared-for/by |
| `business_operations.customer-account-management` | portfolio table of parties | rows are enquiries with a disposition column | rows are accounts with stage/value columns |
| `hr.onboarding-offboarding` | ID verification checklist + scans | requested-work slot present | job title / start date / hiring manager present |
| `finance.personal-records` | source-of-funds bank statement | practice's covering evidence labels it as supplied by an enquirer | statement stands alone; finance keeps its own slots either way |

`identity.core-documents` is the one `also_holds_with`: a certified passport copy in an intake pack is genuinely both, in `00`'s abstract-that-is-also-an-application sense, and identity's holder-agnostic reading must keep firing because it is a safety domain.

## Neighbours considered that did not get an edge

- **`identity.immigration-visa`** — an immigration practice's intake pack is full of visa documents, but the confusion is already carried by `identity.core-documents` as coactivation; adding a second identity edge would be practice-area taxonomy, which J-IND defers.
- **`legal.personal-legal-matters`** — the holder-as-party seam is real but is the *schema's* collision, already argued at the anchor, and this row's material has no bound party pair to confuse.
- **`law_practice.matter-correspondence`** — the unsolicited enquiry email tempts here, but correspondence's anchor is a matter, and an enquiry from a stranger has none. If a sibling later claims pre-opening correspondence, R1c should decide; I did not author a speculative mutex.
- **`medical.*`** — a personal-injury intake carries medical evidence, and neither schema should erase the other; this is a coactivation case for the *matter file*, not for intake, and no edge is authored.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `role_split: []`. `law_practice` declares no fields under PR-6 and D1's deferral stands, so a template on it may declare none. Candidates deliberately **not** minted: `client` and `our_firm` (canonical engagement-role keys, but the schema does not reference them, and the whole point of this row is that neither role is settled yet); `matter_id`, `enquiry_ref`, `disposition`, `party_role`, `verification_status`, `source_of_funds` (none canonical; minting any of them here would pre-empt R1c and would also serialize exactly the disclosive labels this row argues against). `proposed_context_terms` carries nine intake-specific phrases as *proposals only* — the design floor terms in `00` are academic and I have not pretended otherwise.

## Grouping and the residual rule that is this row's own

Groups are bounded by an intake identifier allocated by the practice, or by the same prospective party **and** the same requested-work description across the episode's artefacts; the name alone never bounds a group, because `00`'s stop rules refuse a group "when one high-frequency entity acts as the only bridge". Membership copies no facts.

The rule no sibling has: **when the disposition is declined, no group into a matter may ever form**, because no anchor exists and none ever will — `00`: "It should not form a supported group when there is no valid anchor." Declined intake material stays isolated in Protected Records, and the temptation to attach it to a later matter for the same person by name recurrence must be refused. This is also why the row's residual profile differs from the schema's: Protected Records is not a fallback of last resort here, it is the *expected permanent home* of a real and recurring class of this row's material.

## NEEDS-JOSEPH

**NJ-1 — merge or keep `client-intake` and `conflicts-check`?** In many practices these are one form, and the schema's own deterministic signal names them together as "AN INTAKE-AND-CONFLICTS structure". Alternatives: (a) keep both rows with the seam as authored — requested-work-and-identity-attestation versus searched-names-and-clearance — accepting that a combined form activates both and is protected once; (b) merge into a single intake-and-conflicts row and move the enquiry register and non-engagement letter into it. I did not decide, and did not touch `law_practice.conflicts-check`. This is the only cross-row change I would recommend, and it is R1c's.

**NJ-2 — retention of declined-intake material.** The product must not infer any retention duty, but the corpus fact remains that a refused person's identity documents sit on disk with no engagement behind them. Options: (a) recognise, protect, and say nothing further; (b) allow a surfaced review prompt ("material about a party you did not act for") with no automated action. This node implements (a).

**NJ-3 — whether an intake episode may ever have a visible branch label.** The row proposes no person level at any depth, but even an episode-numbered branch can be reversed to a name by anyone with the register. P7 and explicit user policy should own this; the node states the constraint as prose, not as a serialized dimension.

**NJ-4 — combined-structure files generally.** One PDF carrying an intake structure *and* a conflicts structure *and* an executed retainer is common. CONNECTION allows coactivation, but the family needs a settled rule on whether such a file is protected once under the strictest activated posture (my assumption) or listed under each.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches the `law_practice` anchor's, including `proposed_context_terms`. Every `source_type` used is in `SOURCE_TYPES`. Every edge id — `law_practice.conflicts-check`, `law_practice.engagement-terms`, `legal.practice-matter-file`, `career.consulting-client-engagement`, `business_operations.customer-account-management`, `hr.onboarding-offboarding`, `finance.personal-records`, `identity.core-documents` — was confirmed present in `planning/domains/roster.json`, as were the `also_schema` references. Every `falls_through_to` name is one of `00`'s nine residual homes. No `00` quotation was written that was not first located verbatim. No threshold, count, score or handling class appears. `fields` and `proposed_fields` are empty. I wrote only the two assigned files and edited nothing else.
