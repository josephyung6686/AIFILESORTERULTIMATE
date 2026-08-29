# Research memo — `law_practice.settlement`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.settlement.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Absorbed legacy: `law.adr`

## Result

**REFUSED.** `refuse_node: true`. The row fails all three legs of CONNECTION.md §2's template test against
its own schema's default. The schema anchor had already named this id in NJ-LP-3 as a document-kind fold
against `orders-and-judgments`; that neighbour refused; this row completes the pair.

No coverage is lost. An executed settlement, release or Tomlin/consent order is `legal`'s on `legal`'s own
evidence and is protected there first; without-prejudice offer traffic and settlement-authority instructions
are the `law_practice` default template's; a blank settlement form is `law_practice.precedent-bank`'s; family
mediation whose privacy differs is `law_practice.family-law`'s; transaction completion is
`law_practice.closing-binder`'s; a settlement remittance is `finance`'s; an employer-side compromise is `hr`'s;
the holder-as-party settlement is `legal.personal-legal-matters'`. Every home is named in `collides_with`,
`falls_through_to` or a file example.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/law_practice.json` — default template, work_types, never_alone, NJ-LP-3, legal concession.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration only (~13KB target).
- `planning/domains/nodes/law_practice.orders-and-judgments.json` + `.research.md` — sibling refusal on the paired
  document-kind charge; idiom and edge shape.
- `planning/domains/nodes/law_practice.matter-correspondence.json` — dead deferral of WP traffic to this id.
- Light grep across `law_practice.closing-binder`, `law_practice.family-law`, `legal.leases-agreements`,
  `finance.insurance-corporate` for reciprocal mentions.
- `planning/00-database-agent-product-design.md` — reached only by `grep -c -F` on each quoted span. Every
  quotation below returned exactly one match before it was written.

## THE CHARGE — strongest case that this row should not exist

Stated at full strength before any defence.

1. **It is a `work_type` value.** `law_practice.work_types` contains, verbatim,
   `"settlement, mediation and negotiated-outcome record"`. The roster name is that enum entry. The schema
   proposed `work_type` so that settlement (with pleading, motion, order, opinion) would stay a value, and so
   that "a template row justified only by holding a different legal document kind is the schema's default
   template with a narrower filename filter."
2. **It is a document type.** Settlement agreement, deed of release, mutual release, compromise agreement,
   Tomlin order, consent order, Calderbank letter, Part 36 offer, mediation agreement, mediation position
   paper. Apply the anchor's deletion test — delete every entity name and every document-type word — and what
   survives is either `legal`'s party-pair-plus-execution / caption-plus-operative surface, or the schema's
   email-plus-matter-reference default.
3. **It is defined by absence.** The roster hint's own words: *"The offers, the exchanges and the agreement
   that ends a dispute without a decision."* An absence of a tribunal decision is not an observation.
   `law_practice.orders-and-judgments` refused the mirror definition (being what three neighbours are not).
4. **It is a lifecycle stage.** Offer → exchange → accepted offer → engrossment → execution → payment →
   discharge. Draft-versus-executed is the same kill vector that defeated the consent-order rescue on the
   orders refusal.
5. **The schema already flagged the fold.** NJ-LP-3: the same charge is owed *"against `settlement` versus
   `orders-and-judgments`"* . Inventing a node to save the id after that note would be the 574's mistake.
6. **Legacy `law.adr` is a procedure-mode label**, not a structure. A mode word (mediation, arbitration, ADR)
   is exactly as never-alone as a practice-area word the anchor already struck.

## The node test, argued in full

### The schema's default template, stated exactly

`law_practice` requires **both** legs: (i) an exact matter, file or engagement reference repeated across two
or more artefacts, **and** (ii) at least one artefact whose own labelled slots separate a
**practitioner-or-firm role** from a **client role**. Recommendation held as prose: client only on explicit
approval, then matter, then **document function**, then period; `time_first: false`. Privacy is stricter than
`legal`'s because it protects a **third party** who never chose this filesystem. Executed instruments and
proceeding records inside a matter are deliberately **not** held here — they stay `legal`'s.

### Leg 1 — detection signals. FAIL.

Every candidate artefact collapses into an existing home:

| Candidate | Why it is not a new signal |
|---|---|
| Executed settlement / release | Bound party pair + execution = `legal`'s instrument signal; schema one_line cedes it |
| Tomlin / consent order | Caption + operative paragraphs = `legal`'s proceeding signal; orders row already refused this surface |
| WP / Calderbank / Part 36 email | Schema deterministic email signal + without-prejudice legend already never-alone |
| Settlement-authority instruction | Schema needs_llm: strategy / client-instruction prose by name |
| Mediation position paper | Matter-keyed practitioner work product = schema default; family privacy → `family-law` |
| Blank release / settlement form | Schema inverse-recognition → `precedent-bank` |
| Completion funds direction | `closing-binder`'s transaction-completion situation |
| Settlement remittance invoice | `finance`'s issuer-and-billed-to structure |

A template cannot own signals its schema conceded to `legal`, already carries as default, or already handed to
a sibling. 00: *"A model that cannot cite sufficient evidence must return unknown"* and *"Correct abstention
is a successful outcome because the product’s goal is reliable organization, not maximum file movement."*

### Leg 2 — dimension order. FAIL: a value at the function level, not a difference from it.

PR-6 leaves `dimension_order: []` on the default and here. If fields ever lift, "Settlement" is one label at
the schema's DOCUMENT FUNCTION level. Branching it in a single-matter corpus is what 00 forbids — the engine
must not *"create meaningless one-child levels"*. 00 also: *"A work type such as Homework 3 is meaningful only
after the course is known"*; an offer or release schedule is unintelligible without the matter. Surviving
siblings earned keep by arguing the function level away (`court-filing-record`) or finding a second structure
(`appeals`, `opinions-advice`). This row is the function level's value.

### Leg 3 — privacy rules. FAIL, and the tempting stricter rule is forbidden.

Without-prejudice, privileged, confidential and subject-to-contract legends look like a stricter posture.
The product must preserve them as literal observations and decide **no** legal status, waiver, admissibility
or costs consequence — the schema already strikes those legends as never-alone. The third-party posture that
distinguishes `law_practice` from `legal` applies to the whole matter apparatus, not to a document-kind drawer.
00: *"Finance, identity, medical, and legal material should be implemented first as safety domains, meaning
the system detects and protects them before any cloud or automated placement decision is allowed."* An
executed settlement **is** that material and receives the safety posture from `legal` whether or not this row
exists. Being looser on a public Tomlin schedule is not a licence either; public availability is never-alone.

## Defence attempts, each tried and each defeated

1. **"Without-prejudice offer exchange is a distinct apparatus."** Sharpest rescue. Defeated: the structural
   half is the schema's email-plus-matter-reference signal; the discriminating half is a legend the schema
   strikes. `matter-correspondence` deferred this traffic here hoping for a structural anchor; research found
   none. Redirect is back to the schema default.
2. **"Mediation is a three-role structure (mediator / party / counsel)."** Defeated twice. An executed
   mediation agreement is `legal`'s instrument. A position paper is matter-keyed work product. Where privacy
   actually differs (children, family), `law_practice.family-law` already holds mediation as part of its
   privacy argument — not as an ADR document-type node.
3. **"Ending without a decision is the opposite of an order, so the pair needs two rows."** Defeated: that is
   definition by absence, and a Tomlin order is a decision instrument *with* a settlement schedule — the
   supposed opposite collapses into the refused orders surface.
4. **"Legacy `law.adr` requires a home."** Defeated: absorbing a procedure label into a work_type enum value
   is exactly what the schema's `work_type` proposal exists to do. Saving an id for a mode is the 574 failure.

## Files considered and rejected

- `Settlement Agreement and Mutual Release - Hartley v Nash - executed.pdf` — central; rejected to `legal`.
- `Tomlin Order - Hartley v Nash - sealed.pdf` — rejected to `legal` (orders surface).
- `WITHOUT PREJUDICE - Calderbank offer - 41127-0006.eml` — rejected to schema default.
- `RE … your instructions on the without prejudice offer.eml` — rejected to schema default (also used by
  `legal.practice-matter-file` from the neighbouring side).
- `Mediation position paper - Hartley - WITHOUT PREJUDICE.pdf` — rejected to schema default / `family-law`.
- `PRECEDENT - Deed of Release (firm standard) v4.docx` — rejected to `precedent-bank`.
- `Completion statement and settlement funds direction.xlsx` — rejected to `closing-binder`.
- `Settlement payment remittance - invoice 8841.pdf` — rejected to `finance`.
- `Commercial Mutual Release - Acme Ltd and SupplyCo - no dispute file.pdf` — rejected to
  `legal.leases-agreements` (agreement without dispute apparatus).
- `Offers and ADR - Jul 2026 download.zip` — rejected: download session. 00: *"A session should never be
  treated as proof of topic"*; *"It should not form a supported group when there is no valid anchor"*.
- `Screenshot … mediation portal booking.png` — rejected: OCR'd ADR word; Temporary Screenshots.

## The collision fixture

**`Mutual Settlement and Release - my employment claim - signed.pdf`.** Settlement, release, execution,
payment, confidentiality — precisely the surface this row would have claimed — and the holder is the
**party**, not the practitioner. Discriminator: which signature slot the holder occupies, and whether any
practitioner-side apparatus exists in the corpus. Here neither does, so `legal.personal-legal-matters` owns
it under `legal`'s safety protection. From the employer's corpus without outside counsel, the same bytes are
`hr`'s internal compromise. Caption-free commercial language decides nothing about `law_practice`.

A second, over-firing collision: `Settlement Agreement and Mutual Release - Hartley v Nash - executed.pdf`
inside a genuine practitioner corpus. Even there the item counts for `legal` first, because `legal` is a
safety domain and its protection runs before any placement decision.

## Reciprocal boundaries

| Neighbour | Same fixture | This row would own | Neighbour owns | Discriminated by |
|---|---|---|---|---|
| `legal` | executed settlement / Tomlin | nothing on the face | party-pair+execution / caption+operative | those structures themselves |
| `legal.personal-legal-matters` | employment claim release (holder signed) | nothing | holder-as-party record | which slot the holder occupies |
| `law_practice.closing-binder` | completion funds direction | nothing | deal completion / funds-flow | completion structure vs dispute-offer/release |
| `finance` | settlement remittance invoice | nothing | issuer-and-billed-to | finance structure; "settlement" in narrative is never-alone |
| `hr` | same release from employer corpus | nothing | internal personnel compromise | whose process it is |
| `law_practice.precedent-bank` | blank deed of release | nothing | empty party/execution slots by design | placeholders + no matter/client |
| `legal.leases-agreements` | commercial release, no dispute file | nothing | agreement without dispute apparatus | presence/absence of claim/matter apparatus |

This row's side of every boundary is empty or negative — the reason it is refused rather than bounded.

## Edges deliberately not authored

- **`also_holds_with` is empty.** CONNECTION §5 restricts it to schema ↔ schema; this row is a template.
  Substantive co-activation (`legal` on the instrument face; `law_practice` on disjoint matter-and-role
  artefacts elsewhere) is recorded here for R1c. Same divergence `orders-and-judgments` already flagged
  against siblings that authored template-level `also_holds_with`.
- `career` (must_consider) — no edge. A consulting SOW has fees and two organisations but no
  without-prejudice offer machinery and no release-of-claim structure; the schema's consulting seam already
  covers the engagement-letter false friend. Dropped on evidence.
- `law_practice.family-law` — no mutex edge. Mediation papers in a family matter are co-membership /
  privacy-rule territory that family-law already argued; not same-evidence theft of a settlement drawer.
- `law_practice.orders-and-judgments` — no edge to a refused twin; both route to `legal`. Recorded in
  NEEDS-JOSEPH instead.
- `role_split` empty: schema declares no field keys.

## Fields

`fields: []` and `proposed_fields: []`. Placeholder launch; schema declares none under PR-6; schema already
carries the six proposals R1c must adjudicate. A refused row proposes nothing — in particular not
`settlement_type`, `adr_mode`, `offer_type` or `release_type`, all respellings of `work_type`.

## NEEDS-JOSEPH

**NJ-SET-1 — Dead deferral from `matter-correspondence`.** That refused sibling wrote that genuine
without-prejudice offer traffic belongs to this row's structural anchor. Research found no such anchor.
**Alternatives:** (a) redirect to the `law_practice` default — recommended; (b) reopen matter-correspondence;
(c) mint a narrower without-prejudice-offer row (outside one-node scope).

**NJ-SET-2 — Schema NJ-LP-3 pair.** Anchor asked whether settlement versus orders-and-judgments fold as
document-kind values. Both refused. **Alternatives:** (a) record the pair closed on one argument —
recommended; (b) reopen either on new evidence; (c) mint a single `negotiated-outcome-documents` row that must
still defeat the `legal` concession — this row judges that undefeatable.

**NJ-SET-3 — `closing-binder` reciprocal.** That landed memo already said settlement's execution mechanics
should merge into completion rather than pad this id. This refusal agrees and authors `collides_with`.
**Alternatives:** (a) R1c cleans any live pointer on that neighbour — recommended; (b) leave dangling text
until P8 surfaces it.

**NJ-SET-4 — Legacy `law.adr`.** **Alternatives:** (a) leave absorbed in the schema work_type enum —
recommended; (b) reopen only where privacy differs (`family-law` already owns family mediation); (c) mint
ADR-administration for mediator-appointment apparatus alone — thin without a matter, and outside scope.

## Self-verification

- Both assigned files exist; `python3 -m json.tool` parses the JSON; memo carries `Depth: J-DEPTH`.
- Every 00 span quoted was `grep -c -F` verified (exactly one match) before writing.
- Twelve file examples; every `source_type` in SOURCE_TYPES; no folder path written as a fact.
- Every `collides_with` entry is `{domain, signal, provenance}` with `SAME FIXTURE BOTH SIDES`; 
  `also_holds_with` empty per CONNECTION §5.
- Every neighbour id verified on `roster.json`; every `falls_through_to` name is one of 00's residual homes.
- No thresholds, no handling classes, `fields: []`, `proposed_fields: []`.
- Files written: exactly the two assigned. No roster, neighbour, contract or shared file modified.
