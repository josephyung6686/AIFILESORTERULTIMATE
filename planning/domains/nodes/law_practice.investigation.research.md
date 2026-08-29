# Research memo — `law_practice.investigation`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.investigation.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`
Team: OTHER-TEAM · sole id for this pass

## Result

**Accepted, narrowly.** The row does not stand on the word investigation, on a litigation stage, or on document-type names. It stands on a practitioner-side enquiry apparatus the schema default states only as a work_type value — terms of reference with a commissioning-client / investigator pair and an in-scope / out-of-scope partition; investigator-authored interview summaries; investigation-keyed evidence logs; source-cited chronologies; findings reports — plus one privacy rule the default does not operationalise: the subject of the enquiry is routinely not the client, and existence of the file is disclosive about that person. `fields: []`, `proposed_fields: []`, `dimension_order: []`. Ten `collides_with` entries with SAME-FIXTURE language; five schema↔schema `also_holds_with` entries; six residual homes.

Landed siblings already assumed this row's existence and wrote seams toward it (`law_practice.depositions-testimony`, `law_practice.criminal-defence`, `law_practice.discovery`). This memo supplies the reciprocal structures those seams require; it does not edit those files.

## Binding material read

Stamped dispatch from `make_prompt.py law_practice.investigation`; `planning/domains/dispatch/RESEARCH-BRIEF.md`; handoff §6–§7; schema anchor `law_practice.json` only (not its memo); calibration on `legal.practice-matter-file.research.md`; CONNECTION node test; roster neighbours `legal`, `career`, `finance` plus looked-up `hr.employee-relations`, `law_practice.discovery`, `law_practice.depositions-testimony`, `law_practice.criminal-defence`, `business_operations.compliance-audit`, `career.consulting-client-engagement`, `clinical_practice.malpractice-incident`, `government.professional-regulator`, `legal.personal-legal-matters`. Every `00` span below was grep-verified verbatim before use.

## THE CHARGE — strongest case that this row should not exist

I built each attack before writing the JSON.

**1. It is a `work_type` value, and the schema said so in its own vocabulary.** The anchor's work_types already include *"investigation and interview record conducted for a client"*. The dispatch is explicit that work types are values of a field, not child nodes. Keeping a row because it holds investigation records repeats the 574.

**2. It is a LIFECYCLE STAGE.** In many matters, "investigation" is simply the early phase — before disclosure, before pleadings, before hearing. A stage is not a node. `law_practice.trial-preparation` already had to defeat the same charge by narrowing to compilation structure; if this row cannot narrow, it fails.

**3. It is a document-type cluster.** Terms of reference, interview note, chronology, findings report, evidence log, hold notice — delete every entity name and every document-type word and, on many fixtures, only a firm letterhead survives. That is never-alone evidence wearing a professional coat.

**4. It duplicates the schema default.** Same matter-anchored two-role precondition, same empty dimensions, same `potentially_sensitive`, same Protected Records fallback. The schema's recognition already covers intake, work product, disclosure review and closure. An "investigation" filter on those signals is not a new template.

**5. It duplicates `hr.employee-relations`.** That landed row's constitutive signal is already terms of reference naming an investigating officer, interview notes, investigation packs and findings — under a written employment procedure. If the only difference is that a lawyer typed the same forms, the row is a role-name node, which the schema forbids.

**6. It duplicates `law_practice.discovery`.** Preservation notices, custodian collection logs and one-row-per-document review tables are discovery's D3/D7. The schema's own disclosure-review signal lives there. An "internal investigation" reading of the same tables is a label, not a structure.

**7. It duplicates `law_practice.depositions-testimony`.** Both hold one person's account of events. Without a structural discriminator, interview and deposition collapse into one file-kind node.

**8. The 36-row problem.** If investigation exists because it holds interview notes, then every work_type on the anchor becomes a template and the family explodes.

## Why the charge does not defeat the row

Charges 1, 2, 3 and 8 all attack distinctive *content*. I concede that claim entirely. The row is not kept for its content. Charges 5, 6 and 7 are real same-evidence mutexes and are authored as such. Charge 4 is the only one that can kill the row, and it is the one I defeat — on detection structure and on privacy, which are two of the three template legs in CONNECTION §2.

### Leg 1 — detection signals the default does not sharpen

The schema lists investigation as a work_type. It does **not** state the terms-of-reference grammar (commissioning client + investigator + in-scope/out-of-scope + reporting deadline), the investigator-authored third-person summary without attestation, the investigation-keyed evidence log that specifically lacks a production volume, or the findings-report section grammar addressed to the instructing party. Those are structures. Landed siblings already depend on them:

- Depositions draws the attestation seam and names this row as owner of the unsigned investigator summary.
- Criminal-defence draws the direction-of-questioning seam and names this row as owner when the practice is the questioner.
- Discovery places this row between discovery and compliance-audit for review logs under an internal-investigation mandate with no demand instrument.

If this row were refused, those seams would point at a ghost. The structures are real; the refusal would not delete the artefacts, only the place that distinguishes them.

Narrowing that defeats the stage reading: this row does **not** claim everything made during an investigative phase. A pleading drafted while an enquiry runs stays with pleadings/`legal`; a deposition taken for the same matter stays with depositions; a discovery demand stays with discovery. Only the enquiry apparatus itself is claimed.

### Leg 2 — dimensions

Empty, as required. No destination-eligible fields exist under PR-6. A subject-named or allegation-named branch would be a disclosure even if fields existed — worse than the schema's already-seeded client-level ban, because the named person often never retained the firm. Recommendation held as prose only: matter or enquiry reference first (user-approved), then document function; never the subject. `time_first: false` — "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

### Leg 3 — privacy rules the default does not operationalise

The schema's privacy claim is that it protects a third party who never chose this filesystem. This row is where that claim is most concrete: the **subject of investigation** is routinely not the client — an employee under suspicion, a complainant, a whistleblower, a witness. Existence of `INV-…` material about a named person can disclose that they are under enquiry before any page is read. Consequences this template states that the default does not:

- A subject name may never become a folder level.
- Cross-enquiry bridging by subject name is suppressed as a privacy barrier.
- Findings reports and interview notes are detected to protect, never to summarise into a remote prompt by default — "If a model needs text containing sensitive content, the user should see that requirement and choose whether to allow a local model, a cloud model, a redacted prompt, or no model use."
- Privilege/confidential legends stay literal observations; no legal status is decided.

## Bottom-up file set

Fifteen fixtures in the JSON. Core positive set: terms of reference, investigator interview note, evidence log, source-cited chronology, findings report, preservation notice under enquiry mandate, interview audio, enquiry-pack export. Collision / false-friend set: criminal-defence interview of the client by the state (`Interview transcript - 2026-03-04 - Rowan Pike.pdf`), employer HR grievance pack, discovery requests for production, certified deposition transcript, internal-audit prepared-by-client list, LPC sample interview note, password-protected pack. The set covers labelled forms, free text, spreadsheets, email-capable holds, audio, archives, OCR-adjacent screenshots via residual routing, public/training false friends, and unreadable material.

## Files considered and rejected

- A live practice-management or e-discovery database is a source system, not a file node; only a bounded export with a readable manifest is represented.
- Contact exports naming subjects or witnesses do not activate merely by containing names.
- Public news articles about an investigation are Reading Inbox unless an exact enquiry reference establishes membership.
- The client's own complaint letter instructing the firm is matter correspondence / engagement apparatus, not this row, unless it is itself structured as terms of reference.
- Police custody records and regulator case-administration produced by the authority are government / criminal-defence material; this row takes only practitioner-commissioned or practitioner-conducted enquiry apparatus.
- Due-diligence request lists remain `law_practice.due-diligence` / discovery's mutex; this row does not reclaim them by calling commercial diligence an "investigation."

## External artifact shapes (existence only)

Used only to confirm that the proposed structures occur in real practice; no legal rule is imported.

- ABA / SRA-style investigation and interview practice materials describe terms of reference, interview notes, evidence schedules and written findings as ordinary workplace and regulatory-enquiry artefacts.
- Civil disclosure / e-discovery materials distinguish litigation holds and production volumes from internal fact-finding mandates — supporting the discovery mutex.
- Employment-procedure guides describe employer-side investigation packs with representation rights and appeal routes — supporting the HR mutex.
- Deposition and transcript practice confirms oath, coordinates and errata as structures this row deliberately lacks.

These are artifact-existence notes. The node derives no retention period, privilege status, jurisdictional rule or professional-compliance outcome from them.

## Reciprocal boundaries

| Neighbour | This row owns | Neighbour owns | Shared fixture |
|---|---|---|---|
| `hr.employee-relations` | Instructed enquiry for a client | Employer's own procedural case | GRV investigation pack export |
| `law_practice.depositions-testimony` | Investigator summary, unsigned | Attested verbatim record | Okafor interview note |
| `law_practice.criminal-defence` | Practice as questioner | Client questioned by the state; practice as adviser | Rowan Pike interview transcript |
| `law_practice.discovery` | Enquiry mandate; no demand/volume apparatus | Demand pair or production volume | Preservation notice INV-2026-014 |
| `business_operations.compliance-audit` | Practitioner investigation mandate | Auditor/auditee engagement | FY2026 prepared-by-client list |
| `career.consulting-client-engagement` | Legal-services / counsel scope | Consulting prepared-for/by + milestones | Forensic engagement letter |
| `clinical_practice.malpractice-incident` | Legal matter enquiry pack | Clinician-side incident apparatus | Clinical adverse-event investigation report |
| `legal.personal-legal-matters` | Holder acts for a client | Holder is the subject | ToR where holder is named subject |
| `government.professional-regulator` | Practitioner copy for a client | Authority-produced case admin | Regulator investigation plan |
| `legal` | Enquiry apparatus without caption/execution | Instruments and proceedings inside the pack | Sworn statement collected as evidence |

`also_holds_with` is schema↔schema only (`legal`, `identity`, `medical`, `finance`, `hr`), per handoff §7. Template co-membership is recorded in fixtures via `also_schema` observations and left for R1c if a template-level edge is wanted.

## Neighbours considered that did not get an edge

- `law_practice.evidence-exhibits` — an investigation exhibit log is enquiry-keyed; a hearing bundle index is event-keyed. Distinct enough that a mutex would be forced; if R1c sees shared bytes in practice, add then.
- `law_practice.expert-materials` — expert instruction letters are not enquiry terms of reference; no same-fixture claim authored.
- `finance.small-business-bookkeeping` — covered by schema-level finance `also_holds_with` for collected ledgers.
- `research.reading-library` — specimen packs fall to Reading Inbox; not a mutex.
- `law_practice.due-diligence` — discovery already owns that mutex; this row does not reopen it.

## Collision fixture (looks like this row and is not)

Primary: `Grievance GRV-2026-014 investigation pack - employer HR export.zip` — terms of reference, interviews, findings, investigation vocabulary throughout. Discriminator: employer procedural triad and appeal route with no instructing-solicitor / commissioning-client pair. Secondary: `Interview transcript - 2026-03-04 - Rowan Pike.pdf` — interview vocabulary throughout; discriminator is direction of questioning plus caution block.

## Fields and proposals

`fields: []` and `proposed_fields: []` by assignment and PR-6. No minting. If R1c later adopts the schema's proposed `project` / `subject_of_record`, this template would be the strongest consumer of destination-**ineligible** `subject_of_record`, but that adjudication is not opened here.

## Residual routing

Protected Records first for isolated enquiry material about named third parties. Review Later for unresolved process ownership. Unsupported or Encrypted for locked packs. Reading Inbox for specimens. Independent Records for blank forms with no third party. Temporary Screenshots for portal captures without an enquiry anchor. Quotes are verbatim from `00` § residual library.

## NEEDS-JOSEPH

1. **NJ-INV-1** — Work-type charge. Keep on apparatus + subject-existence privacy, or refuse and route to schema default + HR + discovery + depositions + Protected Records?
2. **NJ-INV-2** — Employer-client instructs the practice: prefer this row, prefer HR, or allow schema-level co-activation (preferred here)?
3. **NJ-INV-3** — Regulator/police interviews of third parties collected into a defence pack: this row, government, or criminal-defence only?
4. **NJ-INV-4** — Safety-ordering residue for enquiry apparatus that does not fire `legal` (restates schema NJ-LP-6).

## Final recommendation

Keep `law_practice.investigation` as a placeholder template with no fields, no dimensions, and no time-first hierarchy. Activate only on the enquiry apparatus and the subject-existence privacy posture. Cede employer procedures, discovery demand/production apparatus, attested examinations, and state interviews of the client to their landed owners. Refuse rather than expand if R1c finds the apparatus indistinguishable from the schema default.
