# Research memo — `law_practice.admission-cle`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.admission-cle.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, placeholder launch
Verdict: **REFUSED** (`refuse_node: true`)

## Result

Refused. The situation — a practitioner proving their own right to practise — is `career.credentials-licenses`' landed structure with a bar, law society or legal regulator standing in the issuer slot. An issuer is a **value** of a position that row already declares, not a structure. Measured against the `law_practice` default template, this pile does not *differ* from it; it falls *outside* it, because every member carries exactly one person and no matter reference, where the schema's defining signal is an exact matter anchor plus a second, differently-labelled party.

The refusal was predicted before it was researched. The schema anchor `law_practice.json` already carries the charge in its own recognition block: a practising certificate, an admission record, a CPD or CLE log and a professional-indemnity certificate are "the HOLDER'S OWN professional standing - no client, no matter, no third party", and the recommendation there is that this row "should be refused and folded to `career.credentials-licenses`, unless its author can name a structure that row does not already hold." I looked for that structure. I could not name one. This memo records what I looked for, so the search does not have to be repeated.

## The charge, stated at full strength before anything else

Argued against my own row first, as the brief requires:

- **It is a document type.** Admission certificate, practising certificate, good-standing letter, renewal notice, CLE transcript, course completion slip, indemnity certificate, annual return. That list *was* the row's content. The schema anchor already ruled, against its own siblings `pleadings` / `motions-and-briefs` / `orders-and-judgments`, that a legal document kind is a `work_type` **value** and not a node. The same ruling lands on me harder, because my values are not even `law_practice`'s — they are `career.credentials-licenses`' declared enum.
- **It is a lifecycle stage.** Admission → practice → renewal → CLE compliance → good standing is a validity lifecycle, and `career.credentials-licenses` states the validity window as "the structural signature of this template." A row whose content is the stages of a neighbour's declared window is a duplicate of that neighbour.
- **It is an organisation name.** Strip the letterhead off my strongest fixture and nothing distinguishes it from the neighbour's. My discriminator reduces to *which regulator appears in the issuer slot* — never-alone evidence doing the whole job.
- **It is a row defined by an absence.** The most accurate honest description of my pile is: the `law_practice` artefacts that have *no* matter and *no* client. A row defined by what its files lack cannot activate.
- **It is a duplicate of a neighbour.** Fixture for fixture, not thematically. See the reciprocal-boundary section.

Three of five charges land cleanly and two land partially. Nothing defeats them.

## Sources used (named)

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — standing brief, read in full.
- Stamped assignment via `planning/domains/dispatch/make_prompt.py law_practice.admission-cle`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibration row named by the brief.
- `planning/domains/nodes/law_practice.json` — my schema anchor: `one_line`, `recognition`, `template`, `proposed_fields`, `open_question` (NJ-LP-1 … NJ-LP-6). Read via key extraction, not streamed.
- `planning/domains/nodes/career.credentials-licenses.json` — `one_line`, `recognition`, `template`, `falls_through_to`, full fixture list.
- `planning/domains/nodes/clinical_practice.licensure-credentialing.json` — the structural twin, already refused; read for its refusal shape and its leg-by-leg reasoning.
- `planning/domains/roster.json` — id verification for every edge written (`career.credentials-licenses`, `law_practice.court-filing-record`, `legal.personal-legal-matters`, `academic.continuing-education`, `government.professional-regulator` all confirmed present; `finance.insurance-corporate` confirmed for an `also_schema` note).
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -n` only. Three spans quoted, each grep-verified verbatim before use: the university-name-alone stop rule (line 63), the parent-context rule (line 95), and the residual-library definitions including Protected Records, Independent Records, Review Later, Reading Inbox, Temporary Screenshots (line 120).

I did not read the anchor's `.research.md`, because the JSON settled the node test without ambiguity. I did not read other rows for context.

## The node test, all three legs

**Leg 1 — fields. Unsatisfiable, and an unsatisfiable leg is not a satisfied one.** `law_practice` declares no field rows under PR-6 and D1's deferral as narrowed by J-IND, so a template on it can declare none and cannot differ from the default on field set. This leg carries no weight in either direction. The row had to survive on legs 2 and 3, exactly as the clinical twin did.

**Leg 2 — detection signals. The decisive failure.** The anchor states the `law_practice` default template as a structure, not a vocabulary: a matter-anchored two-role structure, *"an exact matter or file reference repeated across artefacts, together with at least one artefact whose own labelled slots separate a practitioner or firm role from a client role."*

Run it against my own file list:

| Fixture | Matter anchor | Two-role split |
|---|---|---|
| `Practising Certificate 2026-27 - Law Society.pdf` | none | one person |
| `CLE Transcript 2025 - State Bar of California.pdf` | none | one person |
| `Certificate of Good Standing - State Bar of California.pdf` | none | one person |
| `Professional Indemnity - Certificate of Insurance 2026.pdf` | none | insurer + firm — two *organisations*, never-alone |
| `admission packet.zip` | none | referees attest *about* the holder |
| `Firm CPD returns 2025 - all fee earners.xlsx` | none | many staff, no client |

Zero for six on both halves. The pile does not differ from the default; it is outside it. That is precisely the failure the clinical twin named when it wrote that its files "do not differ from it but fall outside it: they carry one person, the holder, where this schema's defining signal is a second, differently-labelled subject."

Now run the comparison the other way, which is the comparison that actually kills the row. Every signal I could have written is a landed `career.credentials-licenses` signal with a legal regulator substituted into the issuer position:

1. A credential title in a high-weight zone plus a labelled identifier slot — bar number, roll number, SRA ID. That row's signal, verbatim, with a different number name.
2. The validity window — a labelled issue date paired with a labelled valid-through or renewal-due date. That row calls this pair its structural signature; a practising certificate *is* that pair.
3. An issuing-body gazetteer hit at a word boundary in the issuer position. That row's signal; R4 owns the gazetteer and neither of us writes the list.
4. A verification affordance — a registry lookup code or verify URL beside a holder name.
5. A renewal or expiration email from a licensing board or professional association.

Five for five. A row whose discriminator is which regulator occupies an already-declared slot is proposing a value as a node.

**Leg 3 — privacy. Fails, and fails in the direction that matters.** The anchor is explicit about why `law_practice`'s default is stricter than `legal`'s: it protects *"a THIRD PARTY's - a client, an adverse party, a witness, a deponent, an accused, a child - who never chose this filesystem and cannot consent."* My pile contains no third party. Its sensitivity is ordinary holder-identifier sensitivity — a bar number, sometimes a date of birth or home address on a renewal form — which is the posture `career.credentials-licenses` already carries and already routes under 00's own residual definition: *"Protected Records may represent sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials; it should normally remain local-only and must not cause filenames or content to be exposed in model prompts."*

Needing no protection this schema does not already give — and needing materially *less* than its characteristic material — is not a privacy difference that earns a row. Note the asymmetry with the anchor's NJ-LP-4 ruling for the practice-area siblings: `family-law`, `criminal-defence` and `immigration-casework` may survive on leg 3 because the file's existence is disclosive about a child, an accused or an immigration status. Mine is disclosive about a lawyer being a lawyer, which their own letterhead publishes.

## The strongest cases for keeping the row, and why each loses

I built each of these deliberately, as the best available defence, before refusing.

1. **The character-and-fitness admission application.** The most serious candidate, because it is purpose-coherent and content-incoherent — transcripts, employment history, financial disclosure, referee affidavits, criminal-history responses — and 00 makes purpose a first-class facet for exactly that shape (the application-packet case). It loses twice. The packet's *subject* is still the single holder, so it is an application **about a credential** and sits with the certificates-and-applications family the clinical twin already routed to `career.credentials-licenses`. And the referees attest *about* the holder rather than transacting *with* the practitioner: a one-subject structure wearing a two-name costume, not a practitioner/client split. Marked as **inference**, not design — 00 does not adjudicate this case.
2. **Pro hac vice admission.** Genuinely matter-anchored, with a tribunal caption and an exact case identifier — and that is exactly why it loses. Being matter-anchored makes it `law_practice.court-filing-record`'s under the schema default, so it was never this row's. It survives in my JSON as the collision fixture, which is the only place it belongs.
3. **Firm-level compliance.** A roll of admitted staff, firm CPD returns, the firm's PII schedule. This is the firm running itself, which the anchor explicitly cedes to `business_operations`, `hr` and `finance`. Many staff names are a personnel record, not a two-role matter structure.
4. **Trust/client-account compliance.** Considered because a practising certificate is often conditioned on it, and it is the one admission-adjacent artefact that genuinely touches a third party's money. It defeats itself: a client-account reconciliation names client matter balances, so it *is* matter-anchored and two-role, and therefore belongs to `law_practice.time-and-billing` and `finance` — not to a credentialing row. Its being good evidence for the schema is proof it is not evidence for me.

No candidate survives. Refusal.

## Files considered and rejected

Beyond the four defences above, these were the tempting false positives:

- `State Bar of California - Formal Opinion 1994-134.pdf` — a regulator name in the title and no holder anywhere. Public reading material; Reading Inbox unless an accepted research or matter reference claims it. This is the file that makes the regulator-name never-alone rule concrete.
- `Notice of Disciplinary Complaint - In re Jordan Lee.pdf` — concerns a licence, so it reads as credentialing; but the holder is the respondent, which makes it the holder's own legal position under `legal.personal-legal-matters`, and `legal` is a safety domain whose protection runs first. A credential record states that a standing holds; a complaint states that someone contests it.
- Law-school transcripts and the bar-exam score report — `academic.transcripts-credentials`. A transcript states that something happened; a licence states that a standing currently holds and will end. Same discriminator the credentials row already uses against diplomas.
- A CV or firm bio listing admissions and jurisdictions — `career`'s own material. A recital of a credential is not the credential.
- The practising-certificate fee invoice and the bar-dues receipt — `finance.receipts-expenses` on its own transactional evidence; a receipt for a credential is not a credential.
- Contacts and calendar exports containing CLE seminar entries — a seminar in a calendar is not a compliance record, and no row activates from an event title.
- Live regulator portals and registers — a source system, not a file node.

## Reciprocal boundaries

Each stated in both directions, naming the same fixture on both sides.

**`career.credentials-licenses` — the terminal collision, the one this row loses.** *Toward that row:* `Practising Certificate 2026-27 - Law Society.pdf` and `CLE Transcript 2025 - State Bar of California.pdf` carry an issuing body in the issuer position, a credential title, a labelled identifier and a validity window — its stated structure exactly. *Toward this row:* nothing. There is no evidence configuration on which this id should win, which is why it is refused rather than bounded. The duplication is fixture-level, not thematic: that row's landed `CE credits transcript 2025 - Board of Nursing.pdf` **is** my CLE transcript with a different regulator, and its landed `Certificate of Liability Insurance - 2026.pdf` **is** my professional-indemnity certificate under its American name. It needs no edit to absorb this pile.

**`law_practice.court-filing-record`.** *Toward that row:* `Motion for Admission Pro Hac Vice - Acme v Beta.pdf` carries a tribunal caption and an exact case identifier, so the matter anchor decides it. *Toward this row:* never — the word "Admission" is a document-type word and never-alone. The seam is the attached `Certificate of Good Standing`: as an exhibit inside an accepted matter packet it is that row's member; as a standalone file in the holder's own records it is `career.credentials-licenses`'. Neither copies the other's anchor onto it.

**`legal.personal-legal-matters`.** *Toward that row:* `Notice of Disciplinary Complaint - In re Jordan Lee.pdf`, holder as respondent, safety protection first. *Toward this row:* never; a proceeding about a licence is not a licence record.

**`academic.continuing-education`.** *Toward that row:* the dated course-title, provider and credit-hour rows of the CLE transcript, read as continuing education. *Toward this row:* never — the compliance-period framing is a regulator's label on the same rows, not a second structure. The two neighbours split the same bytes by which half is being read, not by contest, and the regulator-issued artefact-as-credential stays with `career.credentials-licenses`.

**`government.professional-regulator`** — recorded as both a collision and a `role_split`. *Toward that row:* the register, the issuing workflow, the authority's own file about an admittee. *Toward this row:* never; a practitioner's copy of their own certificate is a holder record. Written so the coverage does not migrate to the authority's side when this id retires.

Neighbours considered that got **no** edge: `business_operations` and `hr` (named in the refusal for the firm-level fixture, but that is a different pile, not the same bytes); `finance.insurance-corporate` (recorded as an `also_schema` on the indemnity certificate — coactivation, not contest); `photos.screenshot-captures` (coactivation on the portal screenshot); `identity.core-documents` (a bar card is a professional credential, not a core identity document, and the credentials row already holds the distinction).

## The collision fixture

`Motion for Admission Pro Hac Vice - Acme v Beta.pdf`. It contains the word "Admission" in its title, it is about the holder's right to appear, and it would be picked up by any keyword rule this row could have written. It is not this row's evidence: it carries an exact case caption and a movant/local-counsel role pair, which is the `law_practice` default template firing correctly. **The discriminator is the matter anchor, never the vocabulary.**

A second, subtler one: `Certificate of Good Standing - State Bar of California.pdf` — the same bytes legitimately sit in two homes, because such certificates are commonly obtained *in order to* attach to a pro hac vice motion. Standalone it is a credential record; as a referenced exhibit it is a matter member. Membership never copies the matter fact onto it.

## Fields, dimensions, work types

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`.

`proposed_fields` is empty **deliberately, and not conditionally**. A refused row must not leave a field claim standing for R1c to inherit. The keys this situation would have wanted — a credential title, an issuing body, a validity window — belong to `career.credentials-licenses` on the `career` schema, and that row has already argued them; restating them here would be the duplicate proposal the brief forbids.

The dimension order this row would have recommended — issuing authority, then credential, then document type — is the order `career.credentials-licenses` already recorded in prose, for 00's parent-context reason: *"A work type such as Homework 3 is meaningful only after the course is known."* A folder named "Renewal Notice" is unintelligible until the granting body and standing are known. That recommendation is satisfied on the career side and is not duplicated here.

`work_types: []`. The list is a document-type enumeration and enumerating it was the row's actual content.

## NEEDS-JOSEPH

**NJ-AC-1 — the retirement.** Retire `law_practice.admission-cle` from the roster. Successors: `career.credentials-licenses` (certificates, renewals, good-standing, membership, indemnity), `academic.continuing-education` (the CLE course-and-provider reading), `legal.personal-legal-matters` (a proceeding against the holder), `law_practice.court-filing-record` (pro hac vice), Protected Records / Review Later / Independent Records / Reading Inbox / Temporary Screenshots for the residue. `career.credentials-licenses` needs no edit to absorb it; if R1c wants the absorption visible, the one-line change is to that row's `one_line`, made by its own author, not here. *Alternative, kept for the record and rejected:* keep the id as a browse-only label with no activation — the contract does not provide for it, and it would reintroduce the 574's original mistake.

**NJ-AC-2 — the third refusal of the same shape.** This is now the third holder's-own-standing row to fail the same test: `clinical_practice.licensure-credentialing` refused, this row refused, and the `law_practice` schema row predicted both before either was written. Is that a per-row finding or a standing rule? *Alternative (a):* record it as a rule — a licensure or credentialing sibling under any professional schema is presumed to fold to `career.credentials-licenses` unless its author names a structure containing a second, differently-labelled subject. This spares the remaining professional schemas the same three memos. *Alternative (b):* keep adjudicating one row at a time, on the argument that some profession may yet produce a credentialing artefact with a third party inside it. I prefer (a) and cannot settle it.

**NJ-AC-3 — the safety-ordering residue.** `legal` carries the safety flag and co-activates across much of the `law_practice` family, but not on this pile, which has no instrument, no caption and no bound party pair. The disciplinary-complaint fixture reaches `legal` through `legal.personal-legal-matters`; the practising certificate and the CLE log reach nothing that triggers protect-before-model ordering except the residual routing above. This is the schema's own NJ-LP-6 restated on the one pile it explicitly named, and it is not settled here.

## Self-verification

- `python3 -m json.tool` parses `law_practice.admission-cle.json` clean.
- Every edge id verified present in `planning/domains/roster.json`: `career.credentials-licenses`, `law_practice.court-filing-record`, `legal.personal-legal-matters`, `academic.continuing-education`, `government.professional-regulator`.
- Every `falls_through_to` names one of 00's residual templates (Protected Records, Review Later, Independent Records, Reading Inbox, Temporary Screenshots).
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`text_document`, `email`, `image`, `spreadsheet`, `archive`).
- All three 00 quotations grep-verified verbatim before use (lines 63, 95, 120). Quotations attributed to `law_practice.json`, `career.credentials-licenses.json` and `clinical_practice.licensure-credentialing.json` were copied from those files' own text.
- No thresholds, no counts, no handling classes, no `public_low`.
- Two files written; nothing else touched. The ownership register, the roster, canonical fields and all neighbour nodes are unmodified — every cross-row change is a recommendation in NJ-AC-1/2.
