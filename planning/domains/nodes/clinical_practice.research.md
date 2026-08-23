# clinical_practice — lab notes (schema row)

**Depth: GIST.** This is the J-IND gist pass, not the deep per-industry research the 83 launch rows
received: an honest map of what this filing world is for, what files it really holds, what signals
recognise it, and what folder dimensions would make sense. It is deliberately not padded to imitate
depth it does not have. Full depth is a much later pass.

## Sources used

- `planning/00-database-agent-product-design.md` — the only source quoted. Every quotation in the
  JSON was verified verbatim against this file mechanically (a script held the quote bank and
  refused to emit if any string was not present). No section numbers are attributed to `00`.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md`, `planning/domains/canonical_fields.json`
- `planning/overnight/council/DECISION-BRIEF.md` — J-IND, D1, D6 read as ratified and not re-argued.
- `planning/domains/ROSTER.md` §4 line 80, §5, Appendix A lines 589–604 (the legacy folds).
- Landed siblings read before writing: `medical.json`, `medical.personal-health-records.json`,
  `legal.practice-matter-file.json`, `career.credentials-licenses.json`. Key set and house idiom
  are matched to `medical.json` exactly (same 27 keys, same order).
- `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

## What this world is FOR

`medical` is the safety domain for *the holder's own* health material. This row is its role-reverse:
the holder is the **author and custodian** of material **about other people**. That single reversal
is the whole licence for the row, and it is why refusing it would have been wrong — a clinician's
corpus is not a large `medical` corpus, it is a different object with a different privacy owner.
The exposed party here never chose this filesystem, cannot review what the product does, and cannot
correct it. That argues for the strictest posture available, not a lesser one, and it is stated in
the JSON as inference rather than as a `00` claim.

## Node test

The prompt's schema test says refuse if you cannot name a distinct 3–6 field set. **I did not refuse,
and I want to be explicit about why rather than let it pass silently.** This row writes no field rows
at all — D1 as narrowed, `_CONTRACT` rules 10 and 15, `CONNECTION` PR-6, and the J-IND ratification
that placeholder professional schemas describe a domain without minting fields. So the row cannot be
justified by a distinct field list; it is justified by the ratified J-IND expansion plus the role
reversal above, and the one field the world genuinely needs is filed as a `proposed_fields` entry for
R1c rather than minted here. If R1c reads the schema node test literally, this row fails it and every
other J-IND placeholder schema fails it identically — that is a roster-wide question, not this row's
to answer.

## proposed_fields — one, argued

**`subject_of_record`** (string, not destination-eligible, ceiling `possible`, adjudicate: R1c).
It is the one fact that separates this schema from every neighbour, and no canonical key holds it:
`authored_by` is the opposite role and is the role the holder occupies; `client` is a commercial
engagement counterparty whose `role_split` partner is `our_firm`, and a patient is not the client of
the person writing about them (the letter is usually addressed to a third clinician); `people` is the
photos-side co-occurrence facet; `institution` is the facility, not the person. Proposed as **never**
destination-eligible on two independent grounds — `00`'s rule against creator identity as a
destination dimension, and the stronger point that the label would name a third party.

The five templates propose **nothing**, deliberately. Duplicating this question five times would be
five rows answering a decision that is not theirs; `career.credentials-licenses` sets the same
discipline and I followed it.

## Files considered and rejected

- **A blank practice letter template / SOAP template.** Full clinical structure, no subject. Kept as
  a *collision fixture* in two rows rather than as evidence — it is the tempting false file.
- **A guideline PDF, a drug leaflet, a journal article.** Dense clinical vocabulary, no subject, no
  author-role structure. These belong to the sibling `clinical_practice.protocol-guideline` and to
  `Reading Inbox`, and they are why `never_alone` leads with "clinical vocabulary alone".
- **`.dcm` imaging files.** Already carried honestly on `medical.json` as `opaque_binary`; I did not
  re-litigate them, and used a dictation `.m4a` instead as this family's unreadable-but-dangerous case.
- **A de-identified teaching case.** Rejected as this schema's evidence; it is the sibling
  `clinical_practice.teaching-material`'s, and it is a collision fixture here.

## Neighbours considered that did NOT get an edge

- **`photos`** — appears as `also_schema` on file examples (a phone photo of a chart page carries
  real EXIF facts) but gets no `also_holds_with` row: the co-activation is already carried on the
  photos side by its own EXIF evidence, and asserting it here would add nothing but a maintenance
  burden.
- **`identity`** — the identity/coverage-card confusion is already stated on `medical.json`'s
  `collides_with`. This schema's version of it (a professional registration card versus an issued
  identity document) lives on the `licensure-credentialing` template where the files actually are,
  not duplicated up here.
- **`hr` and `law_practice`** — both are on the roster and both are adjacent (staff occupational
  health; medico-legal instruction). I left them unedged at gist depth rather than guess: an
  unasserted pair means unasserted, not false (CONNECTION §8).

## NEEDS-JOSEPH (this node)

- **NJ-CP-SAFETY (restates ROSTER NJ-J-IND-4 with this row's evidence).** `is_safety_domain: true`
  marks `00`'s four named domains and this row does not carry it. But the material is
  patient-identifying by default and the case is arguably *stronger* here than for some of the four,
  because the exposed party is not the user. If the flag is withheld, **the substitute mechanism must
  be named**: CONNECTION §4 step 5's protect-before-model ordering is keyed to the flag and nothing
  else currently forces P7 ahead of a model path for this schema. This is the item I would put first.
- **NJ-CP-FIELD.** May `subject_of_record` exist as a stored key at all? This is not `medical.json`'s
  holder-versus-subject question repeated — it is the sharper version, because here the subject is
  definitionally *not* the holder.
- **NJ-CP-EVIDENCE (NJ-2 for this domain).** May matched clinical text about a third party be stored
  in the local evidence table like any other observation, or should detection store only a protected
  marker plus a location? A stored third-party narrative is a much larger local surface than a flag,
  and every later dossier builder reads that table.
- **NJ-CP-SHAPE.** Is ten templates on a field-less schema the right shape? My answer for the five I
  can see: `patient-chart`, `case-conference`, `malpractice-incident` and `referral-correspondence`
  each pass the node test on detection signals and privacy rules; `licensure-credentialing` is the
  weakest and carries its own fold question (NJ-CP-2, in that row's memo).

## Reciprocity owed to R1c

Every edge here is authored **one-way**. No landed node mentions `clinical_practice` (verified by
grep across `nodes/`). R1c owes the reciprocals on `medical.json`, `legal.json`, `career.json`,
`finance` and `research` for the `also_holds_with` pairs, and on `medical.json`, `career`, `legal`,
`academic`, `research` for the `collides_with` pairs.
