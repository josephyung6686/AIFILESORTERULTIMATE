# business_operations.organisational-records — lab notes (REFUSED template row)

**Depth: J-DEPTH.** Deepened 2026-08-25 from the retired gist draft.

Row kind: **template**. Launch: **placeholder** (`fields: []`).
Verdict: **`refuse_node: true` — unchanged, and strengthened, not revisited.**

**Status of this file.** The gist-era draft was **verified-but-shallow, not untrusted**: its
quotations were machine-checked verbatim, its key set matched the landed siblings, and its argument
was sound. It has since been cited as the reference refusal by roughly a dozen rows across three
families (`business_operations`, `clinical_practice`, `construction_property`) and generalised by the
`business_operations` schema anchor into a rule binding on all 24 of its siblings. This pass does not
retest the verdict. **It hardens the argument to the load now placed on it**, and closes one escape
route that did not exist when the draft was written. What was preserved and what was added is
itemised under *What changed in this pass*.

**A note on length.** A refusal has less to describe than a launch row and more to *prove*. This memo
is long where the proof is load-bearing — the node test, the two-role closure, the tempting files —
and short where a description would be padding. There is no `recognition` section to write out,
because having none is the finding.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — the only design document quoted. Every quotation
  below was matched with `grep -F` against it before this file was written.
- `planning/domains/CONNECTION.md` — §2 (the node test and the empty-industry-label ban), §4 step 1
  and step 2 (activation, and the never-alone rule as an edge invariant), §5 (edge invariants), §9
  (failure modes).
- `planning/domains/_CONTRACT.md` — rules 6, 10, 11, 15.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/roster.json`;
  `planning/overnight/council/DECISION-BRIEF.md` (D1 as narrowed, PR-6, J-IND / J-DEPTH).
- `planning/domains/ROSTER.md` §4 + Appendix A — `ops.business-records` folds into this id.

### Read for this pass specifically

- **`planning/domains/nodes/business_operations.research.md` (46KB, the deepened schema anchor).**
  It states the family's default template explicitly and generalises this row's refusal into the
  family rule quoted under *Leg 1*. This row's node test is measured against that stated default,
  not against a vague sense of one.
- **`planning/domains/nodes/clinical_practice.patient-chart.research.md` (38KB).** Read in full, and
  the reason §*The two-role escape route, closed* exists. It draws a distinction that, left
  unanswered, is the most plausible route by which this row gets rebuilt.
- The `business_operations` siblings that cite this refusal and argue against it in their own terms:
  `board-governance`, `meeting-record`, `risk-register`, `it-asset-inventory`, `compliance-audit`,
  `customer-account-management`, `partnerships-bd`, `procurement-sourcing`, `strategy-plan`,
  `product-requirements`, `support-operations`, `market-research`, `project-delivery`,
  `contract-administration`, `go-to-market`, `policy-handbook`, `budget-forecast`.
- Cross-family: `clinical_practice.practice-administration` (which authors a `collides_with` **at**
  this row), `clinical_practice.case-conference`, `clinical_practice.research.md`,
  `construction_property.research.md` and its own two refusals.

No neighbour file was edited. Where this pass finds an obligation on a neighbour, it is recorded as a
recommendation to R1c.

---

## What the row claimed to be, and why that sentence is the whole problem

The roster hint:

> Material produced by or for an organisation that carries an organisation and a document type but no
> more specific operational sub-domain — the working-life branch itself.

Read the clause *"but no more specific operational sub-domain"* as what it is: a **subtraction
operator**. The row is not defined by what its files have. It is defined by what they are missing
after every sibling has taken what it recognises. A definition by residue is a definition of a
residual, and `00` already owns the residual library and states its purpose:

> Residual templates provide safe, intentionally broad destinations for files that have no reliable
> deeper association.

That is the row's job description, written years before the row, and owned by P10 and P11 rather than
by this namespace. `_CONTRACT` rule 6 and CONNECTION §2 keep residual homes out of the roster
entirely — they are the residual library's nine names, not roster entries — and CONNECTION §9's
failure mode 6 names precisely the artefact this row would be: a residual duplicating a template
without a fallthrough.

Everything below is the same finding, argued rather than asserted.

---

## The node test, argued leg by leg — for a failure

CONNECTION §2 states the test:

> A **template** row exists only if its detection signals, recommended dimensions, or privacy
> rules differ from its schema's default template.

The test is disjunctive: **one** leg passing is enough to make a node. So a refusal is not proved by
finding one weak leg. It has to fail **all three**, and each failure has to be argued in its own
terms. That is what this section does. Failure has legs too, and they fail differently.

### Leg 1 — detection signals: fails, and this is the leg that ends the row

The family's default template and its signal posture are stated in the schema anchor. The anchor's
rule for all 24 siblings, itself generalised **from this refusal**, is:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**. If a proposed row cannot name such a pair, it is not
> a node — it is the schema's default template, or a residual wearing a domain's clothes.

This row's entire candidate evidence is **an organisation name plus a document-type word**. Take the
two terms separately, because they fail for different reasons and a reader who conflates them will
mis-state the argument.

**The organisation name is constitutionally never-alone.** Not weakly, not usually — constitutionally,
because the ambiguity is in what an entity name *is*, not in how well it is extracted. `00` states it
about a university:

> A university name alone should not create a group because Columbia can appear as an authoring
> school, course provider, target institution, employer, research venue, or merely a cited
> organization.

The reasoning there is **role ambiguity**: one token, many possible roles, and nothing in the token
to choose between them. Read across — and this is marked as **inference**, since `00` says
*university* and not *company* — the identical ambiguity holds for any employer, supplier, client,
insurer, regulator or registry. "Acme Ltd" on a page may mean Acme wrote it, Acme received it, Acme
is discussed in it, Acme is the payer, Acme is the payee, or Acme is merely cited. The read-across is
safe because the sentence's own justification is generic: it gives six roles and says the name cannot
choose among them. Nothing in that turns on higher education. CONNECTION §4 step 2 then makes it
operative rather than advisory — it is an **edge invariant**, not a comment:

> **Apply the never-alone rule** (an edge invariant, not a comment — see section 5). Strike any
> schema whose entire support is never-alone evidence

**The document-type word is not evidence of a situation at all** — it is a *value*. "Report",
"record", "letter", "form", "register", "profile" name what the artefact **is**, and the anchor is
explicit that this class of word cannot earn a node: business functions and document functions are
*values of a function dimension*, and what earns a row its node is a distinct **structure**. A
document-type word is therefore not a weak signal that might combine with others into a strong one.
It is the wrong kind of object — a field value being asked to do a detection signal's work.

Now the consequence, and it is the sentence the citing rows quote:

> A row whose entire support is never-alone evidence can never clear activation, so it would be a row
> that never fires.

Note what this is **not**. It is not "this row's signals are weak" or "this row would misfire". It is
a claim about activation arithmetic: after step 2 strikes the never-alone support, the row's support
set is **empty**, and an empty support set cannot reach any threshold, whatever the injected
thresholds turn out to be. This is why the refusal does not depend on a number, and why it cannot be
rescued by tuning one. No `min_activation_score` exists at which zero clears a bar.

**The deletion test, which is the leg's operational form.** Several sibling authors independently
converged on the same diagnostic, and it is worth stating cleanly because it is what a future reader
should actually run:

> Delete every entity name and every document-type word from the row's candidate evidence. Is
> anything left that would still fire the row?

For `it-asset-inventory`, yes: `intune_device_export_20260301.csv` names no entity anywhere and fires
on its header structure. For `risk-register`, yes: a workbook headed `Risk ID | Description |
Inherent L | Inherent I | Controls | Residual L | Residual I | Owner | Next review` names no entity
and fires on structure alone. For `board-governance`, yes: strip "Acme Ltd" and the word "minutes"
and the numbered papers index with its decision/noting column is still there. **For this row,
nothing is left.** That asymmetry is the refusal in one operation, and `patient-chart` states it from
the other side in exactly these terms: *"`organisational-records` had nothing left after you deleted
its never-alone evidence. This row has the whole of its recognition left."*

**What would have had to be true for this leg to pass.** One nameable structure-plus-labelled-slot
pair — a layout, a header, a table shape, a labelled reference slot — that is true of this row's
files and false of the schema's default template. The search for one is not hypothetical: it is
§*The files that tempt someone to build this row* below, which takes seventeen real candidates and
finds that every structure any of them carries is already the defining structure of a sibling. That
is not a coincidence; it is what "no more specific operational sub-domain" **means**. The row is
defined as the complement of the siblings, so any structure it could claim has, by construction,
already been claimed.

Leg 1: **fails.**

### Leg 2 — recommended dimensions: fails twice over, and the second failure is the interesting one

**The contract failure, first, and it is not this row's fault.** `template.dimension_order` is `[]`
because a dimension may only branch on a field the same entry's schema declares, and
`business_operations` declares none (`_CONTRACT` rules 10 and 15; CONNECTION PR-6; D1's deferral as
narrowed; J-IND / PR-6). This is true of **every one of the 24 siblings**, so on its own it proves
nothing about this row: a leg that no sibling can pass cannot discriminate between them. Recording
that honestly matters, because a refusal that leans on a disqualification shared by every row it is
compared with is a refusal that has cheated.

**The substantive failure is the one that counts.** The family holds its recommendation as prose, and
the anchor states the paragraph every sibling must differ from:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

Ask what this row would recommend if fields existed. Its only available dimensions are the two things
it has: an **organisation** and a **document function**. Those are the anchor's level 1 and level 4 —
the same two levels, in the same order, with the middle of the tree missing. That is not a different
recommendation. It is the family default **with its discriminating levels deleted**, which is the
schema's default template under a second name, and ALIGNMENT rules exactly on that:

> ALIGNMENT: a template that would only repeat its schema's fields and dimension order **is not a
> node** — it is the schema's default template.

Worse, the one level it would lead on is the level the anchor **seeds ineligible**. `organization` is
conditional there, because in a single-entity corpus it names the user's own employer above
everything they have ever filed, hitting both of `00`'s validator failures at once — dimensions that
*"create meaningless one-child levels"* and that *"use an author or organization merely as a
collector"*. A row whose top dimension is the family's seeded-ineligible level, and whose only other
dimension is the family's bottom level, has not proposed a tree. It has proposed a two-level
`Employer / Document type` grid — which is, exactly, `00`'s forbidden shape:

> The library prevents the LLM from creating arbitrary folders such as Random PDF Things, Important
> Screenshot, Miscellaneous Documents, or Travel/Gate B12, which may sound plausible but would
> fragment the user's filesystem and create unmaintainable structure.

`Acme Ltd / Miscellaneous Documents` is that folder with a company name in front of it.

Leg 2: **fails.**

### Leg 3 — privacy rules: fails, and the failure is the *right* outcome, not a gap

The row's privacy posture is `potentially_sensitive`, which is the family's own posture, applied for
the family's own reason: unattached organisational documents routinely carry named individuals and
employment material, and `00` names that corpus — it *"can include identity documents, account
statements, tax records, medical information, legal records, credentials, private correspondence, GPS
metadata, employment materials, and educational records."* The operative limits are `00`'s:

> Protected material should not be included in cloud-model prompts by default, should not display raw
> content in general group summaries, and should not be moved automatically without a user policy
> that explicitly permits it.

Identical to the schema's. **Leg 3 fails.**

The important thing about this leg is what its failure does *not* cost, because a careless reader will
assume a refusal deletes protection. It does not, and the mechanism is worth stating: those limits
attach to the **file**, through P7 and through the schema, not through this row. A passport scan in a
work archive enters a protected state because `00` says *"A scanned passport, tax statement, medical
document, authentication key, or account record should enter a protected state immediately"* — a
statement about the document, with no template in it. Refusing the row removes a folder proposal.
It removes no protection. That is why the JSON still records `sensitivity: potentially_sensitive`
even though the row is refused, and why `Protected Records` is authored as a fallthrough: the
protective routing survives the refusal intact.

### Overall

**Refused on all three legs.** The disjunctive test is not merely unsatisfied — no leg comes close,
and the three fail for three unrelated reasons: leg 1 on activation arithmetic, leg 2 on tree shape,
leg 3 on inheritance. Independently, the row is a residual in a template namespace, which is a
category error the node test does not even need to reach. And the last defence — *keep it to preserve
`ops.business-records`* — is the 574's original mistake stated in one line: **inventing a node to save
an id.**

---

## The two-role escape route, closed

This is the section this pass exists to add, and the most valuable thing in the file.

`clinical_practice.patient-chart` (37KB) faced the charge that it was this refusal in clinical
clothes: *its only candidate signal is a person's name plus a clinical document-type word, and both
are never-alone.* It defeated the charge, correctly, and in doing so drew a distinction that is now
available to anyone who wants this row back:

> A row supported by a *relation between two labelled roles* is not a row supported by never-alone
> tokens, even though each of its tokens is never-alone on its own

**The resurrection argument writes itself.** *An organisational document also carries two labelled
roles filled by different entities — a letter on Acme letterhead addressed to Beta Ltd has an issuer
slot and a recipient slot, both labelled by the artefact, both filled by different organisations.
By `patient-chart`'s own reasoning, that relation escapes never-alone. Therefore
`organisational-records` clears activation after all and the refusal was wrong.*

It does not work, for four independent reasons. Any one of them is sufficient; taken together they
close the route rather than merely blocking this instance of it.

### 1. The relation must be the row's *definition*, not a property some of its files happen to have

`patient-chart`'s holder/subject relation is **co-extensive with the row**. Every chart has it; a file
without it is not a chart. The relation is not evidence the row collects — it is what the row *is*,
and the row's leg-1 signal is stated as a positive structure that a file either exhibits or does not.

This row has no definition to be co-extensive with. It is defined by subtraction: *carries an
organisation and a document type but **no more specific operational sub-domain***. A negative
definition cannot own a positive structure, because the moment you name a structure that its files
exhibit, you have named a *specific* thing about them — and by the row's own definition, a file with
something specific about it belongs to whichever sibling owns that specificity, not here.

The escape route requires a defining structure. This row's definition is the absence of one. Finding
a structure in some of its members does not rescue the row; it identifies a **different row**, and
§*What a legitimate replacement would look like* below says what would have to happen for that
different row to be built properly.

### 2. A document-type word is not a role. It is a value in a role's place

`patient-chart`'s two blocks are **both party-shaped and separately labelled**: an exported-by or
printed-by slot naming the holder, beside a patient banner naming the subject. Two parties, two
labelled slots, two different people. The second slot is what resolves the first slot's role
ambiguity — that is the entire mechanism, and it is why the escape works there.

This row's candidate pair is *an organisation name* **plus** *a document-type word*. The second term
is not a party. It cannot be named, it has no relation to the first party, and it resolves nothing
about the first party's role: "Acme Ltd" + "report" leaves Acme exactly as ambiguous as "Acme Ltd"
alone — author, subject, recipient, or merely cited. The anchor already classifies document function
as a **value of a function dimension**.

So the resurrection argument does not present a two-role structure. It presents a **one-role
structure with a field value standing where the second role should be**, and hopes the shape of the
sentence carries it. Substituting a value for a role is precisely the move the two-role test exists
to catch. The test is not "name two tokens"; it is "name two labelled parties whose relation the
artefact records."

### 3. The pincer: where a genuine second organisational role *does* exist, a sibling already owns it

Grant the escape its best case. Suppose the file really does carry two labelled organisational roles
filled by different entities. Run the procedure on any real file and it terminates in one of two
places, neither of which is this row:

**If the two roles are present**, the *pair* is already the whole node of a named sibling, and this
row firing would be theft:

| The role pair | The row that owns it, on that pair |
|---|---|
| buyer / supplier, at the moment of issue | `business_operations.procurement-sourcing` — which notes that at issue *there is no supplier yet*, and that this is what saves it from being a counterparty-name row |
| principal / counterparty in an executed instrument | `legal` for the instrument; `business_operations.contract-administration` for the post-signature register, notice calendar and obligation tracker |
| provider / customer, across an account's life | `business_operations.customer-account-management` |
| two organisations negotiating a joint arrangement | `business_operations.partnerships-bd` — which states outright that if the counterparty name were its evidence, it *"would be `organisational-records` with a sales vocabulary, and it would deserve the same refusal"* |
| regulator / regulated | `business_operations.corporate-regulatory-filings`; `business_operations.compliance-audit` for the request-list and finding-table structure |
| employer / employee | the `hr` family |
| main contractor / subcontractor | `construction_property.subcontract` |
| landlord / tenant | `construction_property.tenancy-management`, `commercial-lease` |
| clinician-holder / patient-subject | `clinical_practice.patient-chart` — the row that raised the distinction |

**If the two roles are absent**, the file is back to one entity name plus a document-type word, and
leg 1 strikes it at activation step 2.

There is no third branch. **The two-role test empties this row from both ends**: applied strictly, it
removes every file that satisfies it (to a sibling) and every file that does not (to never-alone).
Membership is empty under the escape route, and the escape route is therefore not a rescue — it is a
*stronger* refusal than the original argument, because it holds even if you grant the premise
entirely. That is the single most useful sentence for a future reader to carry away.

### 4. `patient-chart` does not rest on the two roles alone, and citing only that paragraph cites half its argument

`patient-chart`'s leg 1 is **longitudinal accumulation about a single named subject** — several dated
entries about the *same* person over months — and it is careful that this is *disjoint* from the
schema's batched signal, which requires the subject to change between items. The two-role structure
is what defeats the role-ambiguity objection; the **accumulation** is what makes it a node rather
than the schema's default. Both are required. A resurrector who quotes the two-role paragraph without
the accumulation signal is quoting the half that was never sufficient on its own.

Can this row supply an accumulation analogue? No, and the failure is instructive. Its accumulation
axis would be *"lots of documents from the same organisation"* — but (a) the axis is the organisation
name, the exact token that is struck, so the accumulation is an accumulation of struck evidence;
(b) the anchor seeds that level ineligible as a dimension for the collector reason; and (c) as the
JSON already says, a pile of assorted work documents from one employer is **a folder, not a group
with a reason**. `patient-chart`'s accumulation is about *one subject in a defined relation to the
holder*. This row's is about *one collector*, which is `00`'s named validator failure, not a signal.

### The closure, in one operation

The deletion test survives the escape route, and that is why the route cannot be reopened by
rephrasing. Delete every entity name and every document-type word. In `patient-chart`, the structures
remain: the banner layout, the dated-entry sequence, the ordering-clinician direction on a filed
result. In this row, the *proposed relation* is a relation **between two deleted tokens** — and a
relation whose only terms have been struck is itself struck. Nothing carries it. A relation is not a
third thing that survives the deletion of both its arguments.

**If you are reading this because you want to rebuild the row using the `patient-chart` argument:
name the two labelled parties and the structure that records their relation. If you can, you have
found a sibling's row or a new narrow row — build that instead. If you cannot, you have found this
refusal again.**

---

## The files that tempt someone to build this row — and where each actually belongs

This is the inverted *files considered and rejected* section, and for a refusal it is the most useful
thing in the memo: it is what a future reader will search for at the moment they are tempted to
re-add the row. Each of these is a real document type a person or small team actually keeps, each one
genuinely *feels* like it wants a general "company records" home, and each one already has a better
one. The rightmost column is the structure that survives the deletion test and takes the file to its
real owner.

| File | Why it tempts | Where it actually belongs | What discriminates it |
|---|---|---|---|
| `Certificate of incorporation.pdf` | the archetypal "company record" | `business_operations.corporate-regulatory-filings` | a registry issuing authority, a company number, a labelled registry reference and an incorporation date — none of which is an entity name or a document-type word |
| `Companies House confirmation statement CS01.pdf` | statutory, dull, org-shaped | `business_operations.corporate-regulatory-filings` | a statutory form identifier and a filing period in labelled slots |
| `Registered office change notice.pdf` | a notice about the company itself | `business_operations.corporate-regulatory-filings` | issuing authority plus a statutory notice structure |
| `Articles of association.pdf` | constitutional, belongs to "the company" | `business_operations.board-governance` (the constitution the body operates under); the seam with `legal` is real and named under *Open questions* | numbered operative clauses governing a body's proceedings |
| `Share register 2026.xlsx` | ownership, an org fact | `finance.cap-table-equity` | a holder-and-holding ledger with share classes and transfer dates |
| `Board minutes 2026-03-11.docx` | "Acme Ltd" + "minutes" is *literally* this row's pattern | `business_operations.board-governance` / `meeting-record` | the numbered papers index with its decision/noting column, and the cross-file series regularity — both survive deleting the name and the word |
| `Org chart 2026.pptx` | company structure, impersonal-looking | `hr.org-design-headcount` | named individuals in reporting relations; a diagram of people is not impersonal |
| `Employee handbook v4.pdf` | company-wide, no counterparty | `business_operations.policy-handbook` | a numbered policy contents page with an effective date, a version and an acknowledgement page |
| `Company letterhead template.docx` | pure org identity, zero content | `creative.brand-identity` | a blank document carrying only logo, address block and footer is a brand asset, not a record |
| `MSA - Acme Ltd - executed.pdf` | an org name and a document type in the filename | `legal` for the instrument; `contract-administration` for the register that runs it after signature | an executed instrument's operative clause structure — the anchor names this same fixture on both sides |
| `Insurance certificate - EL 2026.pdf` | certificate + company = "records" | `finance.insurance-corporate` | a policy number, an insurer, and a period of cover in labelled slots |
| `Risk register.xlsx` | internal, no counterparty, org-owned | `business_operations.risk-register` | likelihood/impact scoring columns; fires with no entity named anywhere |
| `intune_device_export_20260301.csv` | an internal admin export | `business_operations.it-asset-inventory` | an asset register with serials and lifecycle dates; **names no organisation at all**, which is exactly why it is a node and this is not |
| `Business card scan.jpg` | an organisation name, clearly readable | contact handling, privacy-side — **not** a folder proposal | contact data is treated as privacy-side rather than as a source of folder proposals |
| `Misc work stuff.zip` | *the* file people imagine this row is for | members are extracted as their own files, each finding its own situation or its own residual; `Unsupported or Encrypted` if unreadable | an archive of unrelated files is the residual case **by definition** — it is the argument for residuals, not against them |
| `Acme Ltd - company profile.pdf` | an org name, a document-type word, and genuinely nothing else | `Independent Records` | nothing discriminates it, and that is the point: no dates, no references, no counterparty, no structure beyond headings |
| `Scan_20260218.pdf` | a real business letter with no handle on it | `Review Later` | a scanner date token and two mentions of a name; the meaning is partly understood and the location needs a decision |

**What the distribution shows, and it is the finding rather than an illustration.** Fifteen of the
seventeen turned out to have a real home the moment they were looked at properly — across five
schemas and eleven templates. The two that did not are the two `00` sends to a residual home. There
is no residue in the middle. A branch-root row would not be *covering a gap*; it would be
**intercepting fifteen files that already have owners** and **giving two files a false home under a
collector folder**. Both halves of that are harms, and the second is the one people forget.

---

## The collision fixture, in both directions

**Direction A — a file that would wrongly fire this row.**
`Acme Ltd - Certificate of Employers Liability Insurance 2026.pdf`. It carries an organisation name in
the filename, on the letterhead and in the body; it carries a document-type word (*certificate*); it
is unmistakably a company record. Under a permissive branch-root row it fires immediately and lands
under `Acme Ltd / Certificates`. It belongs to `finance.insurance-corporate`, and the discriminator is
that a **policy number, a named insurer and a period of cover** sit in labelled slots and survive the
deletion of every entity name and every document-type word. The same bytes: `finance.insurance-corporate`
names them on its side as its own evidence; this row must name them as a **collision it does not take**,
which is what the JSON's `file_examples` do rather than authoring an edge (see *Edges*).

**Direction B — a file that must not be lost *to* this row.**
`Scan_20260218.pdf` — the genuinely unattached business letter, OCR-only, a scanner date token for a
filename, an organisation name appearing twice, no reference number, no subject line. This is the file
the branch root was invented for, and the direction of the harm is the one that gets overlooked: the
row does not merely *fail* to file it, it files it **wrongly and confidently**, under a company-name
collector, producing the shape `00` names outright — *Random PDF Things, Important Screenshot,
Miscellaneous Documents* — with a plausible company name in front. `Review Later` is the correct home
and the difference is not cosmetic: a residual home is reviewable, bounded, and honest about not
knowing. A false template placement is none of those, and P10 will have frozen it into a tree.

---

## `falls_through_to` — each destination argued, with the file that goes there

The refusal is only honest if the coverage is routed. Four residual homes are authored, each with its
verbatim `00` definition and each with the named file from the table above that lands there.

**1. `Independent Records` — the home this row was really describing.**

> Independent Records may live under Personal/Independent Records and hold standalone certificates,
> notices, confirmations, forms, and PDFs that have a durable purpose but no broader group.

Read that list against the roster hint. *Standalone*, *durable purpose*, *no broader group* — it is
this row's job description, already written, already owned, and already sized for exactly the case.
**Goes here:** `Acme Ltd - company profile.pdf`, and `Company letterhead template.docx` in the case
where `creative.brand-identity` does not activate. This is the destination that makes the refusal
cost nothing: the material the row would have held has a home that is *better* than the row, because
it is bounded and does not pretend to a situation.

**2. `Review Later` — the cautious outcome for a partly-resolved work document.**

> Review Later may hold files whose meaning is partly understood but whose final location requires a
> future decision.

The precise description of an OCR'd business letter that clearly *is* work material and clearly lacks
a handle. **Goes here:** `Scan_20260218.pdf`. Note the epistemic honesty this buys, which the row
could not: "partly understood, decision pending" is true; "Acme Ltd / Correspondence" is a guess
wearing a folder.

**3. `Protected Records` — when the unattached organisational document turns out to be personal.**

> Protected Records may represent sensitive isolated material such as passport scans, medical
> documents, account statements, visas, legal forms, or credentials; it should normally remain
> local-only and must not cause filenames or content to be exposed in model prompts.

This is why the refusal costs no protection. **Goes here:** `Org chart 2026.pptx` when
`hr.org-design-headcount` does not activate — a diagram of named people with reporting lines is
employment material about identifiable individuals — and any identity or account document that turns
up loose inside a work pile. The route is P7's and the schema's; it never needed this row.

**4. `Unsupported or Encrypted` — the safe outcome for the unreadable.**

> Unsupported or Encrypted may hold—or, more safely, represent without moving—password-protected
> archives, unreadable documents, damaged files, and unknown formats.

**Goes here:** `Misc work stuff.zip` when it cannot be opened, or when its members cannot be
extracted. The *"represent without moving"* clause matters: the safe outcome for an unreadable work
archive is to leave it where it is, which is something no template row can do.

**Nothing is dropped.** Add the two non-residual routes and the coverage is complete: the
`business_operations` **schema's own default template** takes anything that legitimately activates the
schema without a sibling firing — which is what a default template is *for*, and the reason a branch
root is redundant rather than merely weak — and the fifteen files in the table go to their named
owners. Between the default template, the siblings and the four residual homes, there is no file this
refusal orphans. That claim is falsifiable and I invite the check: name a file that this row would
have held and that none of those six routes takes.

---

## Reciprocal boundaries

### Edges: none authored, and the reason is a contract reason

`collides_with` joins same-kind pairs and asserts an evidence-item mutex (CONNECTION §5). **A row that
never activates cannot be one side of a mutex** — the invariant would be vacuous on this side and
would leave R1c reconciling reciprocity against something that does not exist. `also_holds_with` fails
for the same reason. Only `falls_through_to` is authored, because that is a statement about where
material goes, not a claim to be one side of a contest. This is preserved from the gist draft and I
endorse it.

That leaves the boundaries to be stated in prose, which this section does. They are real obligations
even though they are not edges.

### With the ~dozen rows that cite this refusal as their standard

Roughly a dozen rows across three families read this file before writing their own node test, and
several structure a whole section around *why this row is not `organisational-records`*. The boundary
runs in both directions and both halves matter:

**This row takes nothing from them.** It never activates, so it can never intercept a file on its way
to `risk-register`, `it-asset-inventory`, `compliance-audit`, `board-governance`, `meeting-record`,
`policy-handbook`, `strategy-plan`, `product-requirements`, `support-operations`, `market-research`,
`project-delivery`, `go-to-market` or `budget-forecast`. A refused row is not a weak competitor; it is
not a competitor. Those rows may treat their boundary with this one as closed.

**They take nothing from it**, because it holds nothing. What they *do* take from it is a standard,
and here is the one reciprocal obligation this refusal places on them, stated plainly: **citing this
refusal is not a licence to weaken your own signals.** The argument they are quoting is
*structure-plus-labelled-slot, verified by deletion*. A row that cites the refusal and then rests on a
business vocabulary word has used the citation as decoration. `meeting-record` and `go-to-market`
both record having audited themselves against exactly this and I endorse how they did it;
`project-delivery` records one member that cannot clear activation on its own evidence and surfaces it
as an open question rather than smoothing it, which is the right handling.

### With the three counterparty-name rows — the nearest neighbours to the escape route

`customer-account-management`, `partnerships-bd` and `procurement-sourcing` are the rows for which the
two-role escape is genuinely load-bearing, so the boundary needs stating precisely and in both
directions.

**Their side, as they state it and as I endorse it:** their node is the **pair and its structure** —
an account lifecycle, a negotiation arc, a tender-and-award sequence — never the counterparty's name.
`partnerships-bd` says so explicitly: if the counterparty name were its evidence it *"would be
`organisational-records` with a sales vocabulary, and it would deserve the same refusal."*
`procurement-sourcing` makes the sharper point that at the moment of issue **there is no supplier
yet**, which is a structural fact about the artefact and not a fact about a name.

**My side, and it is the reciprocal they are owed:** this row does not contest those pairs, and the
pincer in §3 above says why — a file carrying a genuine two-role structure is *theirs on that
structure*, and this row must not fire on it even if a permissive implementation would let it.
Conversely, if any of those three ever has its pair-structure removed or diluted in a later pass, it
collapses into this row and should be refused here rather than kept there. That is the reciprocal
they should hold me to.

### With `clinical_practice.patient-chart` and `case-conference`

Cross-family and cross-kind, so no edge is possible in either direction. The boundary is
argumentative and it is now symmetric: `patient-chart` states the difference from its side
(*"`organisational-records` had nothing left after you deleted its never-alone evidence. This row has
the whole of its recognition left."*) and this file states, from its side, why the distinction it
drew does not run backwards — §*The two-role escape route, closed*. **I have contradicted nothing in
`patient-chart` and reversed nothing.** I accept its distinction in full and show it does not reach
this row. `case-conference` defeated the same charge on cardinality (many subjects in one artefact),
which is a second positive structure and, on my reading, an independently sufficient one.

### With `clinical_practice.practice-administration` — an unreciprocated edge, for R1c

`clinical_practice.practice-administration` authors a `collides_with` **at this row**, correctly framed
as standing for the whole `business_operations` family and named at the nearest template because
`collides_with` joins same-kind rows only. Its own memo records that this row has landed and does not
name `clinical_practice` back.

**I have not authored the reciprocal, and I recommend against R1c adding one here.** A refused row
cannot hold a mutex, per the contract reason above. The right fix is on the other side: point that
edge at the `business_operations` **schema row** — which is what it is actually standing for — or
record it as a one-way family-level note. Either way, **R1c owes a decision, not a silent
reciprocity failure.** Recorded as **NJ-BO-6** below. I did not edit that file.

### With `construction_property`

That family's own two refusals (`compliance-certificate` and its sibling) follow this row's model, and
its schema anchor names this file as *"the refusal standard, and the model both of this family's own
refusals follow."* No boundary is contested. The only thing I would add for that family's readers is
the pincer: a certificate carrying an issuing body and a subject property **has** a two-role structure
and belongs to whichever row owns that pair — which is why those refusals turned on the same
subtraction this one did.

---

## What a legitimate replacement would look like — the resurrection gate

The refusal is not a claim that nothing in this neighbourhood deserves a row. It is a claim that
*this* row, defined this way, cannot be one. So that a future reader has something constructive to do
with the impulse, here are the three conditions any replacement must meet. They are just the node test
made concrete, and a proposal failing any one of them is this refusal again under a new name.

1. **Name a positive structure, not a residue.** The row must be defined by what its files *have*, and
   the definition must not contain the words *"no more specific"* or any equivalent subtraction. If
   the proposal's sentence needs to subtract the siblings to say what it holds, stop.
2. **Pass the deletion test.** Delete every entity name and every document-type word from the proposed
   evidence. Something must still fire the row — a header shape, a table structure, a labelled
   reference slot, a two-role relation whose *structure* (not merely whose tokens) survives.
3. **Differ from the family default template.** Not in business function — that is a value — but in
   detection signals, dimension recommendation, or privacy posture, measured against the anchor's
   stated paragraph rather than against an impression of it.

**The one candidate I think might pass** is named in the JSON's `open_question` and preserved from the
gist draft, because it was a good observation and this pass strengthens rather than replaces it: **the
corporate identity documents of an entity a person owns or administers** — incorporation certificate,
constitution, share register, registered-office notices, statutory registers. That is a real and
coherent pile, it is *not* defined by subtraction (it is defined by *"documents constituting this
legal entity"*), and it currently splits across `business_operations.corporate-regulatory-filings`,
`business_operations.board-governance` and `finance.cap-table-equity`.

Would it pass condition 2? **Genuinely unsettled, and I am not going to smooth it.** The candidate
structure is *a registry authority plus a company-number slot* — which does survive deletion of the
entity name, and which is exactly why `corporate-regulatory-filings` exists. So the honest risk is
that the pile is not a new row but a **dimension inside** that one, or a `role_split` question about
whose entity it is. Either way the fix is a **new narrow row named for that situation**, argued on its
own evidence — **never the reinstatement of a branch root**, which is what this file refuses. This
agent did not mint one: creating a replacement roster id is outside what a single node agent may do.

---

## Open questions — NEEDS-JOSEPH

- **NJ-BO-4 · Was something narrower meant?** *(preserved from the gist draft, deepened above.)* The
  corporate identity documents of an entity a person owns or administers. **Alternatives and their
  costs:** *(i)* a new narrow row — costs a roster id and a reciprocity pass, gains a real situation
  with a testable structure; *(ii)* a dimension inside `corporate-regulatory-filings` — costs nothing
  structurally but leaves the share register stranded in `finance`; *(iii)* leave the three-way split
  as it is — costs the user a coherent pile that lands in three places, gains simplicity. My reading
  is *(i)* or *(ii)*, and the deciding evidence is whether the pile's structure survives the deletion
  test independently of the registry-filing structure. **Not settleable from the design docs.**
- **NJ-BO-5 · Confirm the legacy fold.** `ops.business-records` is **retired here, not rebuilt**.
  ROSTER.md §4 counts it as a 1:1 row; that arithmetic changes if this refusal is accepted, and R1c
  should recount rather than let the table drift. Unchanged from the gist pass and still open.
- **NJ-BO-6 · The unreciprocated `clinical_practice.practice-administration` edge.** *(new this
  pass.)* That row authors `collides_with` at this refused row. A refused row cannot hold a mutex.
  **Alternatives:** *(i)* repoint the edge at the `business_operations` schema row, which is what it
  stands for — cheapest and, I think, correct; *(ii)* record it as a one-way family-level note and
  exempt it from the reciprocity check — honest but adds an exemption class; *(iii)* author the
  reciprocal here — rejected, it would be a vacuous invariant. **R1c's call; I edited neither file.**
- **NJ-BO-7 · Where does a company's constitution sit?** *(new this pass, surfaced by the tempting-
  files table.)* `Articles of association.pdf` is simultaneously a numbered operative instrument
  (`legal`) and the document a governance body proceeds under (`board-governance`). Both readings are
  defensible and the anchor's own seam table puts an executed instrument's operative-clause structure
  in `legal` while giving the register that runs it to `business_operations`. A constitution is
  governed-by rather than run-by, so I lean `board-governance` with a `legal` co-activation — but
  **both those rows are outside my assignment and I have not stated it on either side.** Recorded so
  R1c sees it rather than inheriting a silent guess.

---

## What changed in this pass

**Preserved unchanged** — the verdict and everything load-bearing about it:

- `refuse_node: true`, and the three-leg failure it rests on.
- The core sentences the citing rows quote: *an organisation name is constitutionally never-alone*;
  *a row whose entire support is never-alone evidence can never clear activation, so it would be a row
  that never fires*; *a residual wearing a domain's clothes*; *keeping it to preserve a legacy id would
  be the 574's mistake: inventing a node to save an id*. These are load-bearing **as quoted text** in
  a dozen neighbour files and were deliberately not rephrased.
- `launch: "placeholder"`, `fields: []`, `proposed_fields: []`, empty `template.dimension_order`, the
  `sensitivity: potentially_sensitive` posture and its reasoning, all four `falls_through_to` entries,
  the "no edges from a refused row" decision, the eight existing `file_examples`, NJ-BO-4 and NJ-BO-5.

**Added**:

- **§The two-role escape route, closed** — the whole section, answering `clinical_practice.patient-chart`
  in four independent ways and stating the **pincer** (two-role present → a sibling owns it; two-role
  absent → never-alone strikes it; membership empty either way) and the **deletion-test closure** (a
  relation between two struck tokens is itself struck). This is the pass's main deliverable. It is
  mirrored into the JSON as a second `recognition.never_alone` entry — *an organisation name paired
  with a document-type word, offered as a two-role relation* — and as clause **(4) THE TWO-ROLE
  ESCAPE ROUTE, CLOSED** in `refuse_reason`, carrying all four answers, the pincer with its sibling
  table collapsed to a list, the deletion test, and the closing instruction to a would-be
  resurrector. Both were written so that a downstream reader holding **only** the JSON cannot use the
  `patient-chart` argument to reopen the row; that is why the argument lives in the data and not only
  in this memo.
- **The node test argued leg by leg for a failure**, replacing a three-bullet verdict: leg 1 on
  activation arithmetic (with the deletion test stated as its operational form and the explicit note
  that no threshold value can rescue an empty support set); leg 2 distinguishing the *contract*
  emptiness that every sibling shares from the *substantive* failure that is this row's own, and
  identifying its would-be tree as `00`'s forbidden collector shape; leg 3 with the explicit
  demonstration that refusing costs no protection because the limits attach to the file, not the row.
  Each leg now also states **what would have had to be true for it to pass**.
- **§The files that tempt someone to build this row** — seventeen real named files, inverted as the
  brief required: each with what tempts, where it actually belongs, and the discriminating structure.
  Fifteen have named owners across five schemas and eleven templates; two are residual cases. Six of
  these are new to this pass (`Companies House CS01`, `Registered office change notice`, `Articles of
  association`, `Share register`, `Board minutes`, `MSA - Acme Ltd - executed`, `Insurance
  certificate`, `Risk register`, `intune_device_export`).
- **§The collision fixture, in both directions** — direction A (`Acme Ltd - Certificate of Employers
  Liability Insurance 2026.pdf`, and the same bytes named on `finance.insurance-corporate`'s side);
  direction B, arguing that the row's harm is not only failing to fire but **firing wrongly into a
  collector folder**, tied to `00`'s named forbidden shapes.
- **`falls_through_to` argued in full** — each of the four with its verbatim `00` definition *and*
  the named file from the table that lands there, plus the falsifiable completeness claim.
- **§Reciprocal boundaries** — previously a four-line *Edges* note. Now states the boundary in both
  directions with the dozen citing rows (including the one obligation they owe back), with the three
  counterparty-name rows nearest the escape route, with `patient-chart` and `case-conference`, and
  with `construction_property`.
- **§What a legitimate replacement would look like** — a three-condition resurrection gate, and an
  honest assessment that the one plausible candidate may be a dimension rather than a row.
- **NJ-BO-6** (the unreciprocated `practice-administration` edge) and **NJ-BO-7** (where a company's
  constitution sits) — both new, both surfaced rather than smoothed, both left for R1c.

**Reversed**: nothing. **Contradicted in a neighbour file**: nothing.

**Reconciliation pass (2026-08-25).** The agent that wrote this memo was killed by the usage limit
between writing it and writing the JSON, so for one pass this section's *Added* bullet claimed a
`recognition.never_alone` entry and a `refuse_reason` clause that were not in fact present in
`business_operations.organisational-records.json` — the file was still the gist draft. A follow-up
pass applied exactly those two edits and rewrote the bullet above to describe the landed state. No
argument was re-researched, no verdict revisited, and no other memo claim was found to imply absent
JSON content: `sensitivity: potentially_sensitive`, the eight `file_examples` standing in place of
authored edges, and the `open_question` naming the one plausible replacement were all already
present and were checked individually. The JSON diff is two lines — one `never_alone` entry added,
one `refuse_reason` string extended — with every other key, including `refuse_node: true`,
`launch: "placeholder"`, `fields: []` and `proposed_fields: []`, byte-identical.

**Self-verification.** JSON parses. Key set unchanged from the gist draft (no key added or removed).
`refuse_node` is `true`; `launch` is `"placeholder"`; `fields` and `proposed_fields` are `[]`; no
canonical field key minted. Every quotation in this memo and in the JSON was matched with `grep -F`
against its source — `00-database-agent-product-design.md`, `CONNECTION.md`,
`business_operations.research.md`, `clinical_practice.patient-chart.research.md` — before writing.
Every `file_examples.source_type` is in `SOURCE_TYPES`. Every row id named in the tempting-files table
and the pincer table was checked against `roster.json`. No threshold, statistic or file count was
invented. Two files written, both mine; no neighbour edited.
