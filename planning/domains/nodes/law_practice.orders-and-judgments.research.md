# Research memo — `law_practice.orders-and-judgments`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/law_practice.orders-and-judgments.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch

## Result

**REFUSED.** `refuse_node: true`. The row fails all three legs of CONNECTION.md §2's template test against its own schema's
default, and it fails the first leg against a concession its own schema anchor had already written down, on this row's
own central artefact, before the row was dispatched.

No coverage is lost. The decision instrument is `legal`'s on `legal`'s own evidence and is protected there first; its
membership of a practitioner's matter is the `law_practice` default template's; the receipt that it moved is
`law_practice.court-filing-record`'s; the challenge to it is `law_practice.appeals`'; the blank form of it is
`law_practice.precedent-bank`'s; the dates it sets are the schema's own limitation-and-diary signal; a published
judgment kept to read is reading material. Every one of those homes is named in `collides_with`, `falls_through_to` or a
file example.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/law_practice.json` — the schema anchor. Read for the default template, the two-leg
  precondition, `work_types`, `never_alone`, `template.why`, and the file examples. **This file decided the row.**
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read for depth calibration.
- `planning/domains/nodes/business_operations.organisational-records.json` — read for refusal idiom and key set only.
- Landed siblings that had already argued a boundary against this id, found with one grep
  (`grep -rl "law_practice.orders-and-judgments" planning/domains/nodes/`): `law_practice.pleadings.json` (refused),
  `law_practice.appeals.json` (accepted), `law_practice.court-filing-record.json` (accepted),
  `law_practice.opinions-advice.json` (accepted), plus the refusal status of all 26 `law_practice.*` rows.
- `planning/00-database-agent-product-design.md` — reached only by `grep -c -F` on each span quoted, never streamed.
  Every quotation in the JSON and in this memo returned exactly one match.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before any defence was attempted, because the brief is right that inventing a filing world to
save an id is the recorded failure mode here.

1. **It is a `work_type` value, and a proper subset of one.** `law_practice.work_types` contains, verbatim,
   `"order, judgment, award and appeal record"`. The row is that string minus its last three words — and the last three
   words were already taken by an accepted sibling, `law_practice.appeals`. The dispatch is explicit that work types are
   values of a field, not child nodes; the schema anchor proposed `work_type` precisely so that "Pleading, motion,
   order, affidavit, exhibit, opinion, undertaking" would stay values.
2. **It is a document type.** Order, judgment, decree, decision, ruling, determination, award, direction, minute of
   order, disposition. Apply the anchor's own deletion test — delete every entity name and every document-type word —
   and what survives is a caption and a party pair, which is `legal`'s signal, not this schema's.
3. **It is a lifecycle stage, on the one reading that would rescue it.** "Draft order = practitioner-side, sealed order
   = `legal`'s" distinguishes draft from agreed from consented from lodged from sealed from entered.
4. **It is defined by absence, and three landed siblings define it that way in writing.** `law_practice.appeals`:
   *"one proceeding identifier, no on-appeal-from line and no slot directing another court means the NEIGHBOUR's"*.
   `law_practice.court-filing-record` distinguishes its own artefacts by a *"destination set"* the decision document
   lacks. `law_practice.opinions-advice` separates itself by an addressee block and a reliance clause, saying the
   tribunal instrument has *"no addressee block and no clause restricting reliance"*. All three characterisations are
   negative.
5. **It duplicates its own schema's default template**, since its only affirmative evidence is the schema's own
   precondition plus a filename filter.
6. **It duplicates a neighbour twice over** — `legal` on the instrument, `law_practice.precedent-bank` on the one
   structurally distinct residue (the blank draft order).

## The node test, argued in full

### The schema's default template, stated exactly

`law_practice`'s default requires **both** legs: (i) an exact matter, file or engagement reference repeated across two
or more artefacts, **and** (ii) at least one artefact whose own labelled slots separate a **practitioner-or-firm role**
from a **client role**. Its recommendation held as prose is: the client only where the corpus genuinely spans more than
one *and* the user has explicitly approved a client-named branch, then the matter, then the **document function**, then
the period last; `time_first: false`. Its privacy default is stricter than `legal`'s in one specific way — it protects a
**third party** who never chose this filesystem.

### Leg 1 — detection signals. FAIL, and the anchor conceded it in advance.

A sealed order carries neither leg on its face. It carries a tribunal caption, a party pair, a case identifier,
numbered operative paragraphs, a judicial signature and a seal. That is `legal`'s proceeding structure.

The decisive evidence is not my inference. `law_practice.json` spends the file `Order - Hartley v Nash - sealed.pdf` as
**its own over-firing collision fixture**, and its `must_not_conclude` reads verbatim:

> "THIS IS THE OVER-FIRING COLLISION FIXTURE AND THE ROW CONCEDES IT: the caption plus the operative paragraphs are
> `legal`'s own deterministic signal, `legal` is a safety domain, and its protection runs first. This schema
> co-activates through the counsel block and the matter reference, and takes nothing away."

A template cannot own detection signals its own schema has conceded to a neighbour. The row being proposed here is
exactly the row that would take something away. The schema's `one_line` says the same thing in the abstract: it
"deliberately does NOT hold the executed instruments and proceeding records inside a matter file".

The counsel block does not rescue leg 1. The anchor strikes a firm or practitioner name as never-alone, and 00 forbids
the neighbouring use directly: *"It should avoid using authorship or creator identity as a destination dimension"*.
A counsel block is a role name, not a labelled party pair.

### Leg 2 — dimension order. FAIL: it is a value **at** the schema's function level, not a difference **from** it.

The schema places DOCUMENT FUNCTION third. "Order" and "judgment" are labels at that level. Branching one in a
single-proceeding corpus is what 00 forbids the engine to validate — it must not *"create meaningless one-child levels"*.

The contrast with the two siblings that survived is decisive, and it is the most useful thing this refusal can record
for R1c. `law_practice.court-filing-record` earned its keep by **arguing the function level away** (a receipt is a leaf
beside the document it attests, never a branch). `law_practice.appeals` earned its keep by finding a **second
proceeding whose subject is a first** — a two-tier structure the function level cannot express. This row does neither:
it *is* the function level's value. And the schema's own ordering argument applies to it as a member, not as a rival —
00: *"A work type such as Homework 3 is meaningful only after the course is known"*; an order amending a directions
timetable is unintelligible without the proceeding it amends, in exactly that way.

### Leg 3 — privacy rules. FAIL, and on the row's most characteristic artefact they are **looser**.

00: *"Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system
detects and protects them before any cloud or automated placement decision is allowed."* A decision instrument **is**
that material and receives the safety posture from `legal` whether or not this row exists.

`law_practice`'s claim to a posture stricter than `legal`'s rests on the third party who never chose this filesystem —
true of a privilege log, an attendance note, a deponent's proof. The persons named in an order are the proceeding's own
parties, already inside the safety perimeter. And an approved judgment is frequently the single most **public**
document in the matter, handed down for citation. Being looser than a safety default is not a licence to create a node
— and the row cannot claim the looser posture either, because the anchor strikes public availability as never-alone.

There is one honest complication, recorded rather than smoothed: in family and criminal proceedings an order's
operative paragraphs name **children and complainants**, who are subjects rather than parties and are exactly the
anchor's `subject_of_record` case. That is a real stricter-privacy argument — but it belongs to
`law_practice.family-law` and `law_practice.criminal-defence`, both of which landed and both of which hold it on
evidence about the *matter*, not about the *document type*. It does not distinguish an order from a witness statement
in the same file.

## Defence attempts, each tried and each defeated

Three rescues were attempted seriously before refusing.

1. **"The tribunal authored it, so it is a different artefact class."** Defeated, and it makes things worse: it means
   the document has neither a practitioner slot nor a client slot on its face — one fewer of the schema's two legs than
   a pleading has. Authorship direction moves the row further from `law_practice`, not closer.
2. **"An order is operative — it resets the matter's posture and triggers obligations."** Defeated twice. The
   diarising of those obligations is the schema's own limitation-and-diary deterministic signal, and
   `law_practice.deadlines-diary` was itself refused into that default, so there is no third home to invent. And the
   product is forbidden from acting on operativeness at all: the anchor's order fixture already says the product must
   not conclude "that any order, finding or remedy is current, complied with, appealed, or true."
3. **"A draft consent order carries a two-firm consent block — that is a two-role structure."** The sharpest rescue,
   and the most instructive failure. It separates **practitioner from practitioner**, our side from the other side. The
   schema's second leg demands practitioner separated from **client**. Two struck role names are not the two labelled
   parties the schema rests on — the same point `business_operations.organisational-records` closed against a
   document-type word beside an organisation name. It is also a lifecycle stage, and the tracked draft carries the
   identical caption and party pair as the sealed instrument.

A fourth surface was checked because it is genuinely different: the **arbitral award**, which has no court caption at
all but a tribunal-constitution section, a seat, arbitrator signature blocks and a dispositive section. It still fails:
what it carries is a bound party pair plus an execution block, which is `legal`'s instrument structure stated in
`legal`'s *other* form. A different surface for the neighbour's evidence is still the neighbour's evidence.

## Files considered and rejected

The tempting false positives, and why none is this row's evidence.

- `Approved Judgment … hand-down.pdf` — the practitioner's copy and a copy pulled off a judgments website are
  indistinguishable on the face. Rejected: the discrimination cannot live in a document-type template.
- `Directions Order - CMC.pdf` — the timetable is the operational hook. Rejected: the instrument is `legal`'s and the
  diarising is the schema's own signal.
- `NEF - Order entered.eml` + attachment — rejected: `law_practice.court-filing-record` owns the covering notice, the
  attachment is `legal`'s, and the entry number is linkage.
- `Appellant's Appendix Vol 2 - decision under appeal.pdf` — rejected: `law_practice.appeals` already ruled that
  appendix membership "lives on the COMPILATION'S INDEX, never on the member".
- `Final Award - ICC 27331.pdf` — rejected as above.
- `DRAFT ORDER (blank) - firm standard v3.docx` — the one structurally distinct residue. Rejected: it is the schema's
  inverse-recognition signal and `law_practice.precedent-bank` landed on it.
- `Judgments to read - Supreme Court - Jul 2026.zip` — rejected: a download session. 00: *"A session should never be
  treated as proof of topic"*; and *"It should not form a supported group when there is no valid anchor"*.
- `Screenshot … order entry on the court portal.png` — rejected: a truncated OCR document-type word is the weakest
  instance of the row's only proposed evidence.
- `Decree Absolute - my divorce.pdf` — see below.

## The collision fixture

**`Decree Absolute - my divorce - certified copy.pdf`.** A court caption, a case number, a short operative
pronouncement and a registry seal — precisely the surface this row would have claimed, and the holder is the **party**,
not the practitioner. The discriminator is which slot the holder occupies and whether any practitioner-side apparatus
exists anywhere in the corpus; here neither does, so `legal.personal-legal-matters` owns it under `legal`'s safety
protection. Caption, seal and operative pronouncement decide nothing.

A second, over-firing collision runs the other way: `Order - Hartley v Nash - sealed.pdf`, where a genuine practitioner
corpus surrounds the file. Even there the item counts for `legal` first, because `legal` is a safety domain and its
protection runs before any placement decision.

## Reciprocal boundaries

Five, each naming the same fixture on both sides. All are authored as objects in `collides_with` with a
`SAME FIXTURE BOTH SIDES` signal; the repaired edge-shape defect is not recreated here.

| Neighbour | Same fixture | This row would own | Neighbour owns | Discriminated by |
|---|---|---|---|---|
| `legal` | `Order - Hartley v Nash - sealed.pdf` | nothing on the face | caption + party pair + operative paragraphs | the caption-and-operative structure itself — it is wholly the neighbour's |
| `legal.personal-legal-matters` | `Decree Absolute - my divorce.pdf` | nothing | the holder-as-party record | which slot the holder occupies; presence of any practitioner apparatus |
| `law_practice.appeals` | `Appellant's Appendix Vol 2 - decision under appeal.pdf` | the first-instance instrument (by absence only) | the two-tier pair + a direction to a lower tribunal | the on-appeal-from line and the lower-tribunal slot |
| `law_practice.court-filing-record` | `NEF - Order entered.eml` + attachment | the attached order | the covering notice | a destination set vs. numbered operative paragraphs |
| `research.reading-library` | `Approved Judgment … hand-down.pdf` | the matter copy | the reading copy | an exact accepted matter or research reference elsewhere in the corpus |

The first two are the reason the row is refused rather than bounded: this row's side of the boundary is empty in one
and negative in the other.

## Edges deliberately not authored

- **`also_holds_with` is empty.** CONNECTION §5 restricts it to schema ↔ schema, and this row is a template. The
  substantive co-activation intent is recorded here for R1c instead: on a sealed order inside a genuine practitioner
  corpus, `legal` is held by the document's own face while the `law_practice` side is held by items that are not on
  that face at all — the exact matter reference recurring across artefacts and a separate artefact separating
  practitioner from client. Because the two sides read **disjoint** items, both may count. Noted because
  `law_practice.pleadings` placed `legal` in `also_holds_with` from a template row; this row follows the contract
  instead and flags the divergence rather than copying it.
- `law_practice.precedent-bank`, `law_practice.evidence-exhibits`, `law_practice.hearing-transcripts` — no edge. The
  blank-draft-order residue is conceded to `precedent-bank` outright in a file example rather than contested; the other
  two never compete for a decision instrument.
- `finance` and `career`, named in `must_consider_neighbors` — no edge. An order for costs is a decision instrument,
  not an issuer-and-billed-to structure; the anchor already places the finance seam on the institution-and-account
  header and on the matter-reference column, neither of which appears on an order. Career does not compete: a consulting
  statement of work has no tribunal caption. Recorded so R1c can see they were considered and dropped on evidence.
- `role_split` is empty: `law_practice` declares no field keys, so there is nothing to split a role across.

## Fields

`fields: []` and `proposed_fields: []`. The schema anchor owns the fields, declares none under PR-6, and already
carries the six proposals R1c must adjudicate (`client`, `our_firm`, `project`, `work_type`, `subject_of_record`,
`fiscal_period`). A refused row proposes nothing; in particular it does **not** propose `document_kind`,
`instrument_type`, `order_type` or `disposition`, all of which would be respellings of `work_type` and all of which the
anchor pre-emptively refuses.

## NEEDS-JOSEPH

**NJ-OJ-1 — Refuse the pair on one argument, or reopen both.** `law_practice.pleadings` refused first and predicted
this outcome in writing: this row rests on *"the same caption-plus-party-pair structure separated only by a
document-type word, so the argument that refuses this row appears to reach them too"*, and it asked whether the two
should be refused together, folded into one proceeding-documents row that must still defeat the `legal` concession, or
retained on evidence it did not see. **Alternatives:** (a) record both as refused on one argument — this row's
recommendation, since it looked for the missing evidence and found none; (b) mint a single `proceeding-documents` row
and require it to defeat the anchor's own concession, which this row judges undefeatable; (c) reopen both on new
evidence. Not settleable by one node agent.

**NJ-OJ-2 — Two dead deferrals to redirect.** `law_practice.court-filing-record` and `law_practice.appeals` both defer
the decision document to this row **by name** in `collides_with`. Those pointers now aim at a refused row.
**Alternatives:** (a) rewrite both targets to `legal`, with matter membership going to the `law_practice` default —
recommended, and it needs no reopening of either landed row, only a target rewrite; (b) leave them and accept dangling
edges, which P8's validator will surface anyway. This row may not edit a neighbour, so it can only report it.

**NJ-OJ-3 — A narrower row this refusal may have thrown away.** The **order-compliance apparatus** a practice builds
around an unless order or an undertaking — a checklist pairing an operative paragraph with a step taken, a date and a
verifier — is practitioner-authored, has a genuine two-role structure, and is currently split between the schema's
limitation-and-diary signal and `law_practice.closing-binder`'s conditions-precedent shape. **Alternatives:** (a) leave
it split, which is defensible; (b) mint a new row named for that situation. Minting a replacement id is outside what a
single node agent may do, so this row does not create one.

**NJ-OJ-4 — The template-level `also_holds_with` divergence.** This row follows CONNECTION §5 and leaves it empty;
`law_practice.pleadings` did not. R1c should decide one way for the family so P8's validator sees a consistent rule.

## Self-verification

- `python3 -m json.tool` parses the node file; key set matches `law_practice.pleadings.json` exactly (27 keys, same
  order).
- Every 00 span quoted returns exactly one `grep -c -F` match against
  `planning/00-database-agent-product-design.md`. Every quotation attributed to a sibling node was copied from that
  node's own text in this session.
- Eleven file examples; every `source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact.
- Every `collides_with` entry is an object with `domain` / `signal` / `provenance`, and every signal names one real
  file present on both sides plus the item that discriminates. `also_holds_with` is empty per CONNECTION §5.
- Every neighbour id verified present in `planning/domains/roster.json`; every `falls_through_to` name is one of 00's
  nine residual homes.
- No thresholds, no handling classes, no `design_cite`, `fields: []`, `proposed_fields: []`.
- Files written: exactly the two assigned. No neighbour node, roster, contract or shared file was modified.
