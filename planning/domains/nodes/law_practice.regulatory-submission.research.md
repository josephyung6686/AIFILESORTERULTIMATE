# Research memo — `law_practice.regulatory-submission`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.regulatory-submission.json`
Roster row: template on fieldless `law_practice`, absorbs legacy `law.compliance-programme`, placeholder launch
Team: OTHER-TEAM

## Result

Accept. `refuse_node: false`. The id survives as the practitioner-side **submission cycle** to a non-court public authority conducted for a client — outbound packet, acknowledgement, RFI/deficiency exchange, determination — joined by an authority-allocated submission reference paired with a practitioner matter/engagement reference and an authorised-agent slot. It is not the schema default with a “filings” filename filter, not court transmission, not the entity’s own compelled returns, and not IP-office prosecution of a transferable registered right.

## The charge (argued first)

Six kill vectors, pressed in the strongest available form before any rescue.

1. **It is a work_type value.** The parent schema’s own `work_types` list contains, verbatim, “regulatory or registry submission made on a client’s behalf”. The dispatch rule is explicit: work types are enum values, not child nodes. Pleadings was refused on this vector; the same sentence sits on this id.

2. **It is a document-type / genre node.** Notification, return, clearance, licence application, acknowledgement, RFI, decision — document-type words. Delete every entity name and every document-type word (the schema’s deletion test) and ask what structure survives.

3. **It is court-filing-record with “regulator” swapped for “court”.** That sibling already owns transmission receipts: machine acknowledgements, stamp overlays, rejection notices, fee receipts bound to a proceeding. Its never-alone list even warns about regulatory correspondence. If the only discriminator is the recipient organisation’s class, that is an organisation name — constitutionally never-alone.

4. **It is business_operations.corporate-regulatory-filings on the practitioner side.** That landed row’s one-line already covers “an entity (or a person acting for one)” and it already authors a collision into this id. Side-of-holder alone may be a field value, not a template.

5. **It duplicates law_practice.ip-prosecution.** An application to an IP office is a registry submission on a client’s behalf. That sibling raised NJ-IPP-1 naming this row as the merge target. Keeping both without a structural split repeats the 574.

6. **It is a lifecycle stage** (draft → filed → RFI → decision) or **defined by an absence** (no caption, no adverse party). Both are named failure modes in the handoff.

A seventh, weaker charge: the legacy absorption of `law.compliance-programme` smuggles the firm’s own AML/CPD programme into a client-submission template. That charge is conceded in part below; it does not kill the submission-cycle claim.

## The defeat

Charges 2, 3, 4 and 6 fall to one positive structure; charge 1 falls the same way court-filing-record’s did; charge 5 does **not** fully fall and is NJ-REG-1.

**Positive structure.** Take a portal acknowledgement and ask what identifies it as this world. Not the authority name and not the word “filing”. What identifies it is a **dual-reference pairing in labelled slots**: an authority-allocated submission/application/notification/case reference beside a practitioner matter or engagement reference (and usually an authorised-agent / filing-agent slot naming the holder’s firm). Neither half fires alone — the authority reference sits on every public register download; a matter reference is the schema’s already-struck identifier. The pairing says a firm is acting of record on a client submission. Read through 00’s “a labeled form field”.

That pairing is why the schema **default under-fires** on this corpus. The default’s second leg needs labelled practitioner/client slots. A regulator’s acknowledgement, RFI and determination routinely carry applicant / regulated-entity / agent slots and **no client slot** — the exchange runs between agent and authority. The same under-firing is why `law_practice.court-filing-record` and `law_practice.ip-prosecution` were allowed to stand; this row is the non-court, non-IP instance of that pattern.

**Against charge 3 (court-filing-record).** That sibling’s subject is that a document *moved* in a court/tribunal proceeding — caption, docket/entry number, often a recipient partition into parties who must be served — and it **excludes** the filed document’s body. This row’s subject is a **submission cycle** to a non-court authority: it **includes** the outbound packet (forms, schedules, annexes), the RFI/deficiency examination exchange joined by request numbers, and the clearance/licence/refusal determination. Fixture used on both sides: `Notice of Electronic Filing - Motion to Compel.eml` — every filing-receipt token present, still not this row’s.

**Against charge 4 (corporate-regulatory-filings).** Byte-identical CS01 receipts appear in both corpora. Discriminator, already authored by that neighbour and reciprocated here: matter/engagement apparatus, filed-by-agent authorisation held as the agent’s record, or matter-keyed time recording → this row; same return in the entity’s own statutory book with no practitioner apparatus → that row. Fixture: `CS01 confirmation statement - ACME 12345678 - filed receipt.pdf`.

**Against charge 1 (work_type).** Being named in the parent’s work_types list is a strong charge, not an automatic kill. Court-filing-record is also named there (“court or tribunal filing record and electronic-filing notice”) and stood because its detection structure, dimension prose and privacy rule differ from the default. This row makes the same three-leg showing below. The work_type phrase remains the enum value for *members* of the cycle; the node is the cycle situation.

**Against charge 2.** The file set spans labelled forms, machine receipts, numbered RFI sets, responses, decision letters, agent authorisations, calendars, archives and emails — not one genre.

**Against charge 6.** Draft→filed→RFI→decision is the **grouping** axis inside one submission reference, not the boundary of the node. The absence of a caption is true but not the activation evidence; the dual-reference pairing is.

**Charge 5 stands as an open seam.** IP-office examination shares the dual-reference shape. Discriminator this row can cite: absence of claim-amendment / transferable-right apparatus, presence of authorisation-notification-clearance-compelled-return shape. That is NJ-REG-1, reciprocal with NJ-IPP-1 — not smoothed.

## Node test — three legs

**Leg 1 — detection signals differ.** Yes. Substitute second leg (dual-reference pairing); outbound packet with agent checklist; authority acknowledgement without client slot and without tribunal service partition; numbered RFI/deficiency set joined by request numbers; determination/clearance structure; client-obligations filing monitor; filed-by-agent authorisation. None of these is the schema default’s intake / time-export / privilege-log / blank-precedent apparatus, and the acknowledgement is invisible to the default’s client-slot requirement.

**Leg 2 — recommended dimensions differ.** `dimension_order` stays `[]` (PR-6; safety co-activation with `legal`). Prose recommendation differs from the schema’s client → matter → function → period: inside this situation the varying axis is the **submission reference**, so matter (user-approved) → submission reference → shallow outbound/inbound only if wanted. Function-first inside one cycle would “create meaningless one-child levels”. Client, regulated-entity and submission-reference levels are seeded **more strongly ineligible** than the default because pre-announcement existence is the secret. Not time-first: one cycle carries five different moments; “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”

**Leg 3 — privacy rules differ.** Posture is still `potentially_sensitive`, but the guarded exposure is sharper than the schema’s generic third-party claim: **existence disclosure** of an unannounced deal or activity; commercial annexes in RFI responses; identity packs as schedules. Public availability of a later decision never downgrades the local pre-decision packet. “The default posture must therefore be local-first and data-minimizing.”

Three legs, three differences. Accept.

## Files considered and rejected

- **Court NEF / conformed pleading / affidavit of service** — rejected to `law_practice.court-filing-record` / `legal`; primary collision fixture named above.
- **IP office action with attorney docket** — rejected to `law_practice.ip-prosecution`; second collision fixture.
- **Public register decision download** — dual-reference pairing absent → Reading Inbox. “A session should never be treated as proof of topic” covers a folder of forty of them.
- **Firm AML policy / CPD / PI questionnaire** — firm running itself; **not** absorbed under legacy `law.compliance-programme`. Routes to business_operations / career / finance. Only client-obligation monitors are absorbed.
- **Holder’s own tax e-file acknowledgement** — `finance.tax-filings` / personal safety paths; holder is taxpayer, not agent.
- **Entity’s own CS01 in the minute book** — `business_operations.corporate-regulatory-filings`.
- **Blank statutory form / firm precedent with bracketed entity slots** — `law_practice.precedent-bank`.
- **Opinion letter merely addressed to a regulator** — `law_practice.opinions-advice`; address block is not a submission packet.
- **Government caseworker’s own licensing file** — `government` / `government.permit-licensing`.
- **Password-protected portal dump with no readable manifest** — Unsupported or Encrypted; “Unreadable, encrypted, corrupted, or unsupported files should retain basic metadata…”.
- **Live regulatory-portal account or practice DMS** — source system, not a file node; bounded export with readable manifest only.

## Reciprocal boundaries (same fixture both sides)

| Neighbour | Fixture | This row owns | Neighbour owns |
|---|---|---|---|
| `law_practice.court-filing-record` | `Notice of Electronic Filing - Motion to Compel.eml` | non-court submission cycle | court/tribunal transmission; service partition |
| `business_operations.corporate-regulatory-filings` | `CS01 confirmation statement - ACME 12345678 - filed receipt.pdf` | agent/matter apparatus | entity’s own corpus of the same return |
| `law_practice.ip-prosecution` | `Office Action - Application 18-742-113 - our ref P4412-US.pdf` | clearance/notification/compelled-return cycles | transferable-right prosecution; claim amendments |
| `law_practice.corporate-secretarial` | registry change packet with register extract + filed form | submission act and what comes back | continuous constitutional record; stops at submission |
| `government` | `Clearance decision - Project Cedar - Phase 1.pdf` | practitioner copy inside a matter | authority-side decision custody |
| `finance.tax-filings` | `Self assessment tax return acknowledgement - my UTR.pdf` | agent-filed client returns with matter apparatus | holder-as-taxpayer returns |
| `legal.personal-legal-matters` | personal planning/licence acknowledgement | agent for a distinct client | holder as applicant in their own life |
| `law_practice.opinions-advice` | regulator-addressed firm letter | submission packet seeking a decision | opinion separating questions from conclusions |
| `law_practice.transactional-deal` | merger notification inside a deal room | nested regulatory cycle | deal spine to completion |

`also_holds_with` is **schema ↔ schema only** (`legal`, `finance`, `government`, `business_operations`, `identity`). Template-to-template co-activation deliberately omitted.

**Neighbours considered, no edge:** `law_practice.discovery` (regulator second-request shape is close but primary ownership stays here; discovery’s production apparatus is different); `law_practice.deadlines-diary` (refused); `law_practice.pleadings` / `orders-and-judgments` (refused); `career.consulting-client-engagement` (engagement paper without submission apparatus → Review Later, already covered by schema consulting seam); `nonprofit.governance` (charity returns — owner-type seam already on corporate-regulatory-filings).

## Fields

`fields: []`, `proposed_fields: []`, deliberate. Schema declares none under PR-6. Candidates refused here rather than minted:

- `submission_reference` / `case_number` / `licence_number` — never-alone identifiers; stay observations for linkage only (same preference `ip-prosecution` recorded for right identifiers).
- `regulator` / `authority` — organisation names; struck.
- `filing_date` / `decision_date` — content dates; asserting one as operative is a legal conclusion.
- Reuse of schema proposals (`client`, `our_firm`, `project`, `work_type`, `subject_of_record`, `fiscal_period`) — not re-proposed; templates do not duplicate the schema’s pending list.

## Legacy `law.compliance-programme`

Absorbed **narrowly**: practitioner monitors of **client** regulatory obligations (filing calendars keyed to client entities and matters). Explicitly **not** absorbed: the firm’s own AML policies, training logs, practising-certificate renewals, professional-indemnity proposals, or regulator questionnaires about the practice — those are the firm-as-business concession the schema already gave to business_operations / hr / career / finance. If R1c wanted the legacy id to mean firm-own compliance, refuse that absorption (NJ-REG-3) rather than widen this node.

## NEEDS-JOSEPH

1. **NJ-REG-1 / NJ-IPP-1** — IP seam; alternatives (a) keep both with transferable-right discriminator, (b) merge IP into this row, (c) merge this row into IP. Preference: (a).
2. **NJ-REG-2** — regulator-housed tribunals with captions; preference: caption-plus-service → court-filing-record.
3. **NJ-REG-3** — legacy compliance-programme scope; preference: client monitors only.
4. **NJ-REG-4** — reciprocals on schema-level `also_holds_with` targets.

## Sources used

- Stamped dispatch via `make_prompt.py law_practice.regulatory-submission`
- `planning/domains/dispatch/RESEARCH-BRIEF.md`; handoff §6–§7
- `planning/domains/nodes/law_practice.json` (anchor only)
- Calibration: `legal.practice-matter-file.research.md`
- Landed seams: `law_practice.court-filing-record`, `law_practice.ip-prosecution`, `law_practice.corporate-secretarial`, `business_operations.corporate-regulatory-filings`
- `00-database-agent-product-design.md` — every quoted span grep-verified before write
- CONNECTION.md node test (template exists only if detection, dimensions, or privacy differ)

## Self-verification

- Wrote only the two assigned files; no shared-file edits; no commit
- JSON parses; `fields: []`; `refuse_node: false`
- Edges are objects with `SAME FIXTURE BOTH SIDES`; `also_holds_with` schema↔schema only
- Memo carries `Depth: J-DEPTH`; charge-first; three-leg node test; rejected files; collision fixtures; NJ items
