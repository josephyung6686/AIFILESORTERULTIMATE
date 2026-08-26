# Research memo — `law_practice.family-law`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.family-law.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, narrowly, on leg three of the node test and only there.** The row does not survive because it holds
family-shaped documents. It survives because its file carries an **internal non-disclosure boundary between two
people who are both named inside it**, because its subject is routinely a **child who cannot consent at any age**,
and because a client-named branch here discloses a divorce, a protective application or a child-protection case
about a **named private individual rather than a company**. Two detection structures the schema's default template
cannot see are secondary support: a **mirror pair** of sworn means statements about two private individuals inside
one matter reference, and a **welfare report authored by an assessor who is neither side's practitioner**.

If R1c decides those privacy rules belong on the `law_practice` schema rather than on one of its 36 templates, the
correct outcome is refusal and the coverage routes to the schema default plus Protected Records. That alternative is
written into the node's `open_question` as NJ-FL-1 so it can be taken.

## The charge against this row, stated at full strength first

The strongest case that `law_practice.family-law` should not exist is not mine — **my own schema anchor wrote it**,
and it names me first:

> "A PRACTICE-AREA WORD ALONE - family, criminal, immigration, conveyancing, probate, employment, intellectual
> property, corporate. A practice area is a VALUE, not a structure, exactly as clinical_practice ruled a specialty
> to be, and a practice-area word beside a firm name is two struck tokens."
> — `law_practice.json`, `recognition.never_alone`

And in its open questions:

> "(4) NJ-LP-4, THE PRACTICE-AREA ROWS: `family-law`, `criminal-defence`, `immigration-casework`, `ip-prosecution`,
> `conveyancing` and `estates-administration` are practice AREAS, which are values exactly as clinical_practice ruled
> specialties to be. This row's ruling for their authors: a practice-area row survives ONLY if it changes the PRIVACY
> RULE, never because it changes the topic."
> — `law_practice.json`, `open_question`

The charge is therefore fully formed before I start, in five independent barrels:

1. **A value, not a node.** "Family" is a practice area; the schema struck practice-area words as never-alone. A row
   whose activation depends on a struck token can never activate.
2. **A duplicate of its own schema's default template.** The default already requires a repeated matter reference plus a
   two-role artefact, already holds correspondence, billing, diary, disclosure and closure, and already recommends an
   empty `dimension_order`. If all I add is which documents appear, I am the default with a narrower filename filter —
   the failure NJ-LP-3 raises against `pleadings`, `motions-and-briefs` and `orders-and-judgments`.
3. **A document-type list.** Financial statement, welfare report, parenting plan, consent order are `work_type` values;
   the schema declares `work_types` precisely so document kinds do not become rows.
4. **A person-name row.** Every token I might reach for — a firm, a court, two surnames, a child — is never-alone.
5. **The 36-row problem.** If family-law exists because it holds disclosure forms, criminal-defence exists because it
   holds a charge sheet and conveyancing because it holds a transfer. 36 rows, one default template.

### Why the charge does not defeat the row

I concede barrels 1, 3 and 4 **entirely** and encode them: the practice-area word, the two-name caption, the form
code, the statement-of-truth block, the child's name, the DOB slot and the emotive subject line are all in
`never_alone`, and `Divorce papers.pdf` is carried as a fixture that trips them and fires nothing.

Barrels 2 and 5 are answered on structure and on privacy.

**Structure.** Two signals in my `recognition.deterministic` are not narrower versions of the schema's — the schema
has no signal that would see them at all.

- *The mirror pair.* The schema's financial signal is a time-and-disbursement column set anchored by a matter-reference
  column. A sworn means statement has none of that: no timekeeper, no units, no rate, no matter column. It is one named
  private individual's whole financial life in labelled slots, closed by a declaration block. Read through 00's direct-fact
  path, which names "a labeled form field" as a reliable slot. The **pairing** is what makes it this row's rather than
  `finance`'s: two mirror-image forms about two different people, joined by one matter reference, is a household being
  divided. One alone is an individual's dossier and I do not claim it.
- *The three-role welfare report.* Two parties, a **child in a labelled subject slot**, and an author in an assessor or
  officer role belonging to neither side. No other sibling produces a document whose author is structurally a non-party.
  Delete the practice-area word and the child's name — the strike test `business_operations.organisational-records`
  established — and the subject-plus-non-party-assessor grammar still stands. That is a structure surviving the deletion.

**Privacy — the load-bearing leg.** Three rules the `law_practice` default does not state:

- *An internal non-disclosure boundary.* The schema's posture is "protect a third party from the outside world." Here the
  file protects **one named person from another named person who is inside the same file**: a withheld-contact-details
  form, a redacted-for-service copy with a redaction schedule naming from whom the material is withheld. No other
  `law_practice` sibling has an artefact whose labelled slot *is* a non-disclosure instruction aimed at a co-subject.
- *A subject who cannot consent at any age.* The schema argues its third parties never chose the filesystem. A child
  additionally cannot choose, cannot later object, and cannot be asked. The rule that follows is a naming rule: a child's
  name or initials never become a stored identifier, a group label, a preview line, or a folder level; an initial in the
  source is never expanded.
- *Existence-disclosure about a private individual.* Elsewhere a client branch says a company has lawyers. Here it says a
  named person is being divorced, is seeking protection from someone, or has a child in proceedings. 00's posture is
  "The default posture must therefore be local-first and data-minimizing."

That third rule is why my `dimension_order` differs from the schema's even though both serialize as `[]`. The schema's
prose recommendation seeds the client level **ineligible-but-unlockable by explicit user approval**. Mine makes it
**ineligible outright**, together with any matter level whose label embeds a party name.

## The node test, all three legs

**Leg 1 — detection signals.** DIFFER. The schema default fires on intake-and-conflicts, matter-opening, time-and-
disbursement, limitation diary, disclosure review, privilege log, precedent bank, internal work product, counsel
instruction, closure/retention, DMS export, and role-crossing mail. This row adds the mirror-pair means structure, the
three-role welfare structure, the non-disclosure-to-a-named-party structure, the household-dissolution exhibit bundle
(purpose-coherent per 00's "The documents are content-incoherent but purpose-coherent."), the unexecuted arrangements-
and-consent structure, and the protective-application structure. The schema's precondition is **inherited whole and
not restated as a difference** — that is stated in the first `deterministic` entry so no reviewer mistakes inheritance
for novelty.

**Leg 2 — recommended dimensions.** DIFFER, in the prose that the contract cannot serialize. Both are `[]` under PR-6.
The schema's default template is nevertheless a prose paragraph that "every one of the 36 templates must differ from,"
and the difference is stated above: no client level at all, no party-naming matter level, function under an opaque
matter token, period last, not time-first ("For document and record domains, project, function, or subject usually
comes before time because putting year first scatters related work across calendar folders.").

**Leg 3 — privacy rules.** DIFFER, and this is the leg the schema itself demanded be argued. The three rules above,
plus one operational consequence unique to this row: **a redacted service copy and its unredacted original are not a
duplicate pair.** Near-identical text is exactly what a redacted pair looks like to a duplicate detector; collapsing
them either destroys the served record or surfaces the withheld information. Every other sibling can safely treat
near-identical files as a version family; this one cannot.

Three legs differ. The row stands — narrowly, and reversibly.

## Files considered and rejected

Naming what I do **not** hold was the more useful half of the work.

- **`Client account reconciliation - July 2026.xlsx`** — the anchor's finance concession. An institution-and-account
  header is finance's discriminating structure; a per-matter ledger listing does not promote it.
- **`Time recording export - August 2026.csv`** — the schema default's own fixture. Family matters produce it
  identically to every other practice area, which is exactly why it is not evidence for *this* row.
- **`Pension sharing report - actuarial.pdf`** — tempting, because pension division reads as stereotypically family
  work. Its structure is instruction, qualifications, materials considered, opinion: that is
  `law_practice.expert-materials`. Taking it would have been barrel 3 of the charge landing.
- **Executed prenuptial, separation and cohabitation agreements; sealed orders and decrees** — a bound party pair plus
  an execution block, or a tribunal caption plus operative paragraphs, is `legal`'s own deterministic signal, and
  `legal` is a safety domain whose protection runs first. I hold only the *drafting* record (bracketed open points,
  revision markers, no execution block) — the same inverse-recognition seam the schema drew for its precedent bank,
  applied here to `Parenting plan - agreed - v3.docx`.
- **A contacts export containing both parties, the child's school and a refuge** — a contact record is not a matter
  member because it holds matter-adjacent names. Never-alone, and specifically dangerous here.
- **A folder of one person's bank statements beside matter papers** — a download session, not a disclosure exercise:
  "It should not form a supported group when there is no valid anchor". Carried as the finance collision, not evidence.
- **A live case-management system** — a source system, not a file node. Only a bounded export with a readable manifest
  is represented, read without unpacking.
- **Published family judgments, guidance leaflets, practice notes, blank court forms** — Reading Inbox, or
  `law_practice.precedent-bank` where a firm template marker is present. The profession publishes its own case law and
  its own templates, which makes these unusually convincing exemplars.

## Reciprocal boundaries — both directions, same fixture named on both sides

1. **`legal.personal-legal-matters`** — fixture on both sides: **`Ellis and Co - Client Care Letter - my divorce.pdf`**,
   taken verbatim from the schema anchor's file list. The anchor chose a *divorce* letter for the family's hardest case,
   which makes it my problem before any sibling's. *Toward the neighbour:* the holder is a party to their own
   relationship breakdown; every practitioner-looking token is present and the holder's signature is in the client block.
   *Toward me:* the holder's firm allocated the reference, produced the intake screen, drafted one of the two mirror
   statements, recorded time. Deciding evidence is **where the apparatus is** — never the firm name, the reference, the
   practice area, or the folder. Cost asymmetry recorded in the node: unresolved side → Review Later, not a guess.
2. **`law_practice.estates-administration`** — fixture on both sides: **`Estate inventory and account - Re late M
   Hartley.xlsx`** against my sworn financial statement. Both are complete asset-and-liability schedules about named
   private individuals on the same firm template, often about the same household. *Toward estates:* a **date of death**
   and a **personal representative** role, one subject, distributed. *Toward me:* two mirror-image schedules, two living
   subjects, divided. The seam is a slot pair plus a cardinality, not a topic word.
3. **`finance.personal-records`** — fixture on both sides: **`Exhibit bundle JS1 - statements payslips and school
   letters.zip`** and the loose statements. *Toward finance:* an institution-and-account structure is finance's own
   evidence wherever it sits, and finance is a safety domain whose protection runs first. *Toward me:* the same bytes
   become disclosure material only through an exhibit index or an exact matter reference, and even then I write **no**
   finance fact on them — membership and protection only. On my Form-E fixture I say this explicitly: `institution`,
   `account_type` and `record_type` stay unknown, because finance's records are the *holder's* and these accounts belong
   to someone who never chose this filesystem.
4. **`medical.dependant-child-health`** — fixture on both sides: a paediatric letter naming a child with a DOB. *Toward
   the neighbour:* the holder's own child. *Toward me:* the identical letter as an exhibit about somebody else's child.
   **The bytes do not differ at all.** Both sides must treat the child's name as never-alone and never as a folder level;
   unresolved → Protected Records, not a placement.
5. **`law_practice.immigration-casework`** — fixture on both sides: marriage certificate, cohabitation evidence, a
   child's birth certificate, a household financial bundle. *Toward immigration:* the same evidence proves a relationship
   **to an authority** — an application reference, an authority addressee, a required-documents checklist; the household
   is being shown intact. *Toward me:* the same evidence supports a **division between the two people themselves** — no
   external addressee, two mirror disclosures; the household is being unwound. Seam = presence of an external
   decision-maker as addressee. This matters because both proceed in one household at once.

## The collision fixtures

Three, because this row has three distinct ways to be wrong.

- **Over-firing — `Financial statement (blank) - downloaded from court website.pdf`.** Every labelled slot my strongest
  signal depends on is present, complete, and worthless: the slots are empty, there is no second form, and there is no
  matter reference. Discriminator: **filled slots plus a mirror counterpart plus a matter reference.** Routes to
  `law_practice.precedent-bank` with a firm template marker, Reading Inbox without. Uniquely among my fixtures it is not
  protected material — no party, no child, no third party is in it.
- **Under-firing — `Ellis and Co - Client Care Letter - my divorce.pdf`.** Covered above; the discriminator is the
  location of the practitioner apparatus.
- **Sibling — `Estate inventory and account - Re late M Hartley.xlsx`.** Covered above; the discriminator is a date of
  death plus a personal-representative role.

And the never-alone tripper, which is the charge in file form: **`Divorce papers.pdf`** in a folder named for a surname.
Practice-area word + document-type word + surname folder = three struck tokens. Nothing fires — not this row, not
`law_practice`, not `legal`. Review Later.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`, `role_split: []`, `also_holds_with: []`.

- **`fields`** — PR-6/D1: `law_practice` declares none, and a template may only reuse its schema's fields.
- **`proposed_fields`** — deliberately **empty**, which is a decision rather than an omission. The schema anchor already
  proposes `client`, `our_firm`, `project`, `work_type`, `subject_of_record` and `fiscal_period`, and every field concept
  this row needs is inside that set. Adding a sixth proposal here — `child`, `party`, `subject_child`, `withheld_from` —
  would be exactly the 36-way mint the anchor wrote its `project` entry to prevent. My one ask is carried in the memo and
  in NJ-FL-4: if `subject_of_record` is adopted, its destination-ineligibility should live on the **key**, and my subject
  is the strongest argument for that, because a child in proceedings is neither the holder, nor the holder's counterparty,
  nor a party, nor capable of consent.
- **`also_holds_with: []`** — following the landed `legal.practice-matter-file` precedent: a template cannot author
  schema-level co-activation, and both schemas here are fieldless. The genuine co-activations are recorded per fixture as
  `also_schema` (`finance` on the sworn means statement, `identity` on the exhibit bundle, `legal` on the personal-legal
  fixture) rather than asserted as an edge this row has no standing to write.
- **`role_split: []`** — the schema anchor already authored the `our_firm`/`client` and `client`/`subject_of_record`
  splits. Restating them here would be a second copy of the schema's own work.

## Neighbours considered that got no edge

- **`law_practice.criminal-defence`** — a plausible collision (breach of a protective order crosses into prosecution, and
  a protected witness address exists on both sides), but the discriminating slot on that side is a charge or prosecution
  reference and an accused role, which I do not hold. I raise it as NJ-FL-2 rather than authoring a mutex against a row
  whose author has not yet argued its own leg three. R1c can add it reciprocally.
- **`identity.core-documents`** — birth, marriage and change-of-name certificates are identity's own evidence and are
  carried as never-alone and as an `also_schema` on the exhibit bundle. A co-activation, not a mutex.
- **`law_practice.expert-materials`** — the pension actuary and the psychological assessor look like mine. The welfare
  report is distinguished by its author being a **non-party** officer rather than an instructed expert; a genuinely
  instructed expert report in a family matter is that sibling's, and I say so on the welfare fixture.
- **`law_practice.settlement`, `law_practice.deadlines-diary`, `law_practice.matter-correspondence`** — the schema's own
  situations, produced identically in family matters. Claiming them would be the duplicate-of-the-default failure.
- **`career.consulting-client-engagement`** — the schema's engagement collision. Family matters are between private
  individuals with no organisation on either side, so the consulting false friend does not reach this row.
- **`education`/school records** — a school letter is an exhibit here and education's evidence there; handled by the
  medical/child boundary and the exhibit-index rule rather than a separate edge.

## NEEDS-JOSEPH

- **NJ-FL-1 — the existence question.** Accepted narrowly on leg three. If R1c judges that the redaction and
  withheld-address rules belong on the `law_practice` **schema** rather than on one template — defensible, since criminal
  and investigation files can also carry a protected witness address — then this row should be **refused**, the rules move
  up, and coverage routes to the schema default plus Protected Records. Alternatives are spelled out in the node.
- **NJ-FL-2 — the three-allowed-rows seam.** NJ-LP-4 allowed `family-law`, `criminal-defence` and `immigration-casework`
  on one argument. I have since found a same-evidence collision with immigration and can see one with criminal defence.
  Are these three privacy rules or one? If one, the right structure may be a single protected-natural-persons template
  with the practice areas as `work_type` values. Raised; nothing edited.
- **NJ-FL-3 — the redacted-pair mechanic.** "A redacted service copy and its original are never de-duplicated" is stated
  here as a privacy rule but enforced by whatever computes `duplicate_family` and `version_family`, which is not this
  row's. (a) a universal never-collapse rule for pairs differing by a redaction layer; (b) a per-domain suppression flag;
  (c) leave it to user review — which I believe is unsafe, because the pair is invisible until one of them is surfaced.
- **NJ-FL-4 — the `subject_of_record` dependency.** My child-naming rule is a prohibition with no field behind it. If the
  key is adopted, put the ineligibility on the key, not on 36 templates.

## Cross-row recommendations for R1c (nothing edited)

1. Reciprocals owed **to** this row from `legal.personal-legal-matters`, `law_practice.estates-administration`,
   `finance.personal-records`, `medical.dependant-child-health` and `law_practice.immigration-casework`.
2. `law_practice.criminal-defence` should be asked to argue leg three explicitly, per NJ-LP-4, and to say whether a
   protected-witness-address slot is its rule or the schema's — the answer decides NJ-FL-1 and NJ-FL-2 together.
3. The redacted-pair rule (NJ-FL-3) is a product-wide behaviour, not a domain one, and should be routed to whoever owns
   duplicate detection.

## Self-verification

- `python3 -m json.tool` parses the node cleanly; key set is **identical** to the `law_practice` anchor's (no missing,
  no extra keys), checked by set difference.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `spreadsheet`, `archive`, `email`,
  `audio_video`, `opaque_binary`).
- Every edge id was confirmed present in `planning/domains/roster.json`: `legal.personal-legal-matters`,
  `law_practice.estates-administration`, `finance.personal-records`, `medical.dependant-child-health`,
  `law_practice.immigration-casework`. Every `falls_through_to` name is one of 00's nine residual homes.
- Every span quoted from `00` was grep-verified verbatim in `planning/00-database-agent-product-design.md` before use
  (the purpose-coherent sentence, the no-valid-anchor stop rule, the local-first posture, the time-last rule, the
  authorship-as-dimension prohibition, the protected-records-without-a-threshold licence, the personal-corpus
  enumeration, "labeled form field", "must return unknown", the topic-versus-purpose sentence, "raw sensitive values").
  Quotes attributed to `law_practice.json` were read from that file directly. No thresholds, no counts, no handling
  classes, no fabricated spans.
- `fields`, `proposed_fields`, `dimension_order`, `also_holds_with` and `role_split` are empty by argument, each recorded.
- Files written: **only** `planning/domains/nodes/law_practice.family-law.json` and this memo. No roster, canonical-field,
  neighbour-node, `check.py`, `src/` or SPEC file was touched.
