# Research memo — `nonprofit.political-campaign`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/nonprofit.political-campaign.json`
Roster row: template on the fieldless `nonprofit` schema, `parent_id: null`, placeholder launch
Result: **`refuse_node: true`**

## Result in one paragraph

Refuse. The row is a real world and not a node. Everything an electoral campaign files splits cleanly into two piles, and neither pile belongs to a template on this schema. The first pile — party member rolls, campaign donations, canvasser rotas, the campaign plan, the executive minutes — activates the `nonprofit` schema on the schema's **own default structures**, verbatim, and is already owned by a landed sibling or by `business_operations`. The second pile — the nomination pack, the election-agent appointment, the return of election expenses, the imprinted election address, the canvass return — is what actually makes an election distinguishable from a charity appeal, and **none of it can activate the `nonprofit` schema at all**, because the schema's precondition is a non-exchange relation and those five artefacts evidence a statutory relation, an officer appointment, a regulator relation, a marketing relation, and no relation whatsoever. Subtract both piles and what is left is the assertion that the association is a political party rather than a charity. That is an organisation type, which is the same kind of thing as a tax status, which the schema names as a forbidden sole activator.

## The charge — the strongest case that this row should not exist

I made this case first, before writing anything, and it survived.

**It is an organisation type, i.e. a never-alone label.** The schema anchor states its own ban in terms that reach this row without amendment: *"a charitable registration number, a 501(c)(3) or CIC or union or diocese designation, a mission statement, a logo, or a nonprofit-sounding name is NEVER sufficient on its own, and neither is a document-type word beside one. Tax status is a field value, not a structure."* A political party is an association with a particular purpose and a particular regulator. "Party rather than charity" is a value on the same axis the schema already closed.

**It is already enumerated as a work-type value on its own schema.** `nonprofit.json`'s `work_types[]` contains *"campaign, advocacy and lobbying record where a registration or disclosure structure exists"*. Per the dispatch prompt, `work_types[]` is an enum of values for a field. This row is asking to be promoted from a value to a node.

**It is a lifecycle period.** A campaign is time-boxed to a regulated period. The schema's default already forms exactly this group: *"one APPEAL or campaign: the ask, the donations attributed to it, the thank-you letters and the result report."* The group exists whether or not this row does.

**Its own schema pre-registered it as weak.** `nonprofit.json`'s `open_question` item (4) says: *"campaigning-advocacy is WEAK because a campaign plan is go-to-market with different nouns and a lobbying registration is a regulator filing"* and *"If ten rows are required, the three weak ones should be refused rather than invented."*

I did **not** treat that last point as dispositive, because my row is not the advocacy row. Electoral campaigning has statutory machinery a charity's issue campaign does not: ballot access, a personally liable election agent, a regulated spending period, an imprint requirement, permissible-donor certification, and a voter file. So I steelmanned the node on that machinery and tested it against the schema. That test is what refuted it, below.

## Node test — all three legs, argued

The schema's **default template** is the paragraph in `nonprofit.json`'s `template.why`: the association only where the corpus spans more than one, then the non-exchange counterparty or fund (the grant, the restricted fund, the appeal, the membership class, the case, the register), then the period, then the document function — held as prose, serialised as an empty `dimension_order`, `time_first: false`, with a hard ban on a named person as a folder level. Its default **detection** is the non-exchange precondition plus six named structures (restricted grant, restricted fund, donation-with-declaration, membership register, beneficiary case, safeguarding). Its default **privacy** is `potentially_sensitive`, argued on third-party exposure and on affiliation being disclosed by the record's mere existence.

**Leg 1 — detection signals. Fails.** Each campaign artefact that can fire the precondition fires a schema default word for word:

| Campaign artefact | Schema default it is | Verdict |
|---|---|---|
| Party selection ballot, leadership proxy form | *"a members' meeting instrument carrying a notice period, a motion, a proxy or ballot form and a member-vote count"* | identical |
| Branch subscription roll | *"a roll or register with one row per named member carrying a membership number or class, a join or lapse date, and a subscription or dues status"* | identical |
| Contribution form with permissibility certification | donation structure: named donor slot + recipient association + a declaration | identical; only the declaration's *subject* differs, and a subject is a value |
| Canvasser / phone-bank rota | volunteer structure | identical |

And each artefact that is genuinely campaign-specific fails the precondition — *"Every accepted signal must evidence a NON-EXCHANGE relation between two labelled parties: money or labour given without a commensurate return, or service given to a named person who is not paying for it."*

- **Nomination pack.** Relation runs candidate → returning officer. Statutory. The assentors' signatures are tempting as "labour given without commensurate return", but a signature attesting to a statutory qualification is not labour and an assentor is not a volunteer of the campaign; many assentors are not even supporters.
- **Election-agent appointment.** An appointment to a statutory office carrying personal liability. Officer appointment, which is `business_operations` governance.
- **Return of election expenses.** Regulated-entity → regulator. The schema ceded this by name: *"the relation is regulated-entity to regulator, which is the whole of that landed row's node. This schema takes none of it."*
- **Election address / imprinted literature.** Publisher → public. Marketing collateral; the imprint is one line of statutorily required text, no more structural than a copyright notice.
- **Canvass return.** No relation at all — see the deciding fixture below.

**Leg 2 — recommended dimensions. Cannot differ.** The schema declares no field rows under PR-6, so both the default and any template on it serialise an empty `dimension_order`. An empty order cannot be shown to differ from an empty order. For the record, two orders were tested in prose and rejected anyway: campaign-first is period-first, which the default already places *after* the counterparty; candidate-first is a person's name, which the schema bans outright — *"a named BENEFICIARY, DONOR, MEMBER or SAFEGUARDED PERSON may NEVER be a folder level"*.

**Leg 3 — privacy rules. Do not differ.** The schema's sensitivity argument already names this row's central case inside its own list: membership and donation records *"reveal belief, affiliation or need from the fact of the record's existence, before any content is read"*, and its enumeration is *"a union roll, a congregation register, a political donation and a support-group membership"*. The posture this row would claim is the posture the schema already carries.

One privacy observation **is** new — the canvass register exposes someone with a weaker consent basis than any party the schema enumerated. But a privacy rule that applies only to a file the schema cannot activate on is not a schema privacy rule; it is a residual-routing rule, and Protected Records already carries it. It is recorded as NJ-PC-1, not used to save the node.

**Prior condition it also fails.** A template whose flagship evidence cannot activate its own schema is not a template on that schema. Refusing is the cheap error: *"Correct abstention is a successful outcome because the product's goal is reliable organization, not maximum file movement."*

## The deciding fixture — `Canvass returns - Ward 4 - 2026-04-18.csv`

One row per named elector, elector number, street address, a coded voting-intention column, canvasser initials, date of contact. No consent field, no membership number, no amount column.

This is the single most distinctive artefact of an electoral campaign, and it fails the schema's precondition more completely than any file the schema's own author had to test. The elector gives nothing and receives nothing. They are not a donor, not a member, not a volunteer, not a beneficiary, not a customer, not an employee. There is no non-exchange relation because **there is no relation**. The coded support value is not the elector's declared opinion; it is an inference recorded about them by a stranger who knocked on their door, which they never saw and cannot correct.

That is why the refusal is structural rather than tidy-minded, and why `Protected Records` is named first in `falls_through_to` rather than last. NJ-PC-1 asks R1c to decide the register's permanent home and warns against the tempting answer.

## The collision fixture — `Statement of persons nominated - Ward 4.pdf`

A file that looks exactly like campaign evidence and is not. Authority letterhead, returning officer's signature block, a table of every candidate with descriptions and assentors, a validity determination column, a receipt stamp with an office file reference. The candidate and party strings are byte-identical to those in the campaign's own nomination pack.

What discriminates it: `government.elections-administration`'s precondition — *"every signal below must show the corpus holder on the ADMINISTERING side of a poll"*. The receipt stamp, the office file reference, the validity determination and the officer signature are administering-side custody marks. The campaign's copy carries the candidate's consent block and the assentor rows instead, and no determination. A second discrimination matters too: this document is routinely published, so a downloaded copy is neither side's record and falls to Reading Inbox.

Runner-up collision fixture: `Constituency casework log - housing cases.xlsx`. An elected member's office is not the campaign that elected them — `government.constituent-casework` owns it, and the reciprocal rule that must be stated in both directions is that a canvass return may never merge into a casework log even though both are registers of named residents of one district. The constituent asked for help; the elector was approached. That is the difference between a service relation and no relation.

## Reciprocal boundaries

Eight `collides_with` entries, all object-shaped with a same-fixture-both-sides signal, all ids verified present on the roster. The four that carry the refusal:

1. **`nonprofit.member-association`** — `Members roll - Riverside branch - 2026.xlsx`. Discriminated by nothing, because there is nothing to discriminate; the only proposed difference is the organisation's politics. Reverse: the sibling loses nothing, since a selection ballot is a members' meeting instrument whatever the association is.
2. **`nonprofit.fundraising-donor`** — `Contribution form - permissibility declaration.pdf`. Reverse: the sibling must not treat a political recipient as out of scope; an appeal is an appeal.
3. **`business_operations.corporate-regulatory-filings`** — `Return of election expenses - candidate declaration.pdf`. Reverse: the neighbour also owns a party's periodic donation report to an electoral regulator, for the same reason it owns a charity annual return.
4. **`government.elections-administration`** — `Statement of persons nominated - Ward 4.pdf`.

That last one deserves its own note, because **a landed neighbour has already argued a boundary against me and I have to disagree with half of it.** `government.elections-administration.json` collides with my id and asserts, verbatim: *"A completed nomination pack, agent appointment, spending return, election address, or agent's count tally sheet is campaign material even though the form was issued by the authority."* That is **correct about the side and wrong about the host**. Campaign-side custody is real; it is not a `nonprofit` non-exchange relation. Recorded as NJ-PC-2: R1c must re-point that edge at `business_operations.corporate-regulatory-filings` plus `creative.ad-campaign`, or reopen this coverage on `business_operations` rather than on `nonprofit`. I did not touch the neighbour's file.

The remaining four (`nonprofit.volunteer-management`, `nonprofit.advocacy-campaign`, `government.constituent-casework`, `creative.ad-campaign`) are in the JSON with both directions stated.

`also_holds_with` is **empty**, and deliberately: CONNECTION §5 makes it schema ↔ schema only, and this is a template row. The co-activations I would otherwise have recorded, offered to R1c as intent rather than as edges: `hr` on a combined staff-and-volunteer rota; `finance` on the giver's copy of a contribution; `legal` on a party constitution as an executed instrument. All three already exist on `nonprofit.json`'s own `also_holds_with`, so nothing is lost by this row's refusal.

`role_split` is empty: the schema declares no fields, so there is no field pair to split.

## Files considered and rejected as this row's evidence

- **Manifesto, platform document, policy paper.** Reading material with political content. Topic is not purpose. → Reading Inbox.
- **Published results table, turnout statistics, boundary map.** Public information; `government.statistical-programme` or Reading Inbox depending on custody. A downloaded result table is nobody's record.
- **Opinion poll dataset, crosstabs.** A pollster's or researcher's artefact — `business_operations.market-research` or a research row. Superficially the closest thing to a canvass file in the whole corpus, and the discriminator is that a poll's respondents are anonymised and sampled while a canvass return names every elector on a street.
- **Voter's own polling card.** An individual's civic document. The cleanest single proof that electoral vocabulary is a never-alone token: every word on it is electoral and none of it is an association's record. → Independent Records.
- **Party brand guidelines, ad buy schedule, social creative.** `creative.brand-identity`, `creative.ad-campaign`, `business_operations.go-to-market`.
- **NEC or executive minutes, budgets, policies, procurement, IT assets.** The schema states this flatly for all associations: *"this schema does NOT hold them"*. → `business_operations.board-governance`, `.meeting-record`, `.budget-forecast`.
- **Lobbying registration.** A regulator filing, exactly as the schema's own open question says.
- **Election-worker payroll, staff contracts.** `hr` — paid work is an exchange relation.
- **Password-protected campaign database export.** Filename manufactures no side, no register and no sensitivity result. → Unsupported or Encrypted.

## `proposed_fields`

Empty, and correct for a refusal. No key was needed and none is minted. Three were considered and rejected: `organization` (already proposed by thirteen rows and adjudicated once by R1c; nothing here changes it), `fiscal_period` (a regulated election period is a content period, but it is the same shape as the grant and appeal periods already argued on the schema, so this row adds a use case rather than a key — and adds it to a refused row, which is worth nothing), and a mooted `electoral_district` (rejected as a gazetteer request rather than a field, and R4 owns gazetteer contents).

## Neighbours considered that got no edge

- **`nonprofit.governance`** — a party constitution and its officer records overlap, but the seam is already fully expressed against `business_operations.board-governance` at the schema level, and duplicating it here would add nothing a refused row can act on.
- **`nonprofit.trade-union`** — the affiliation and political-fund structures genuinely overlap in some jurisdictions, but the overlap is *membership*, which is already collided against `nonprofit.member-association`. Adding a second membership collision would be padding.
- **`business_operations.go-to-market`** — real overlap on the campaign plan, but `creative.ad-campaign` carries the same fixture with a sharper discriminator (print production structure), so one edge states it rather than two.
- **`finance.tax-filings`** — a donor's own charitable- or political-giving tax record is finance, but that is the *giver's* side and the schema already states the donor-side seam. Not this row's to restate.
- **`government.public-records-foi`, `government.legislative-record`** — adjacent vocabulary only. No shared fixture.

## Coverage routing after the refusal — nothing is orphaned except one thing

| Campaign artefact | Home after refusal |
|---|---|
| Party / branch member roll, selection ballots, subscriptions | `nonprofit.member-association` |
| Contributions, permissibility declarations, pledges, appeal results | `nonprofit.fundraising-donor` |
| Canvasser and phone-bank rotas, volunteer agreements, expenses | `nonprofit.volunteer-management` (+ `hr`) |
| Issue campaigning, lobbying, message grids | `nonprofit.advocacy-campaign`, `business_operations.go-to-market` |
| Constitution, executive minutes, budgets, policies | `nonprofit.governance`, `business_operations.board-governance` / `.meeting-record` |
| Nomination packs, agent appointments, spending returns, donation reports | `business_operations.corporate-regulatory-filings` |
| The authority's copies of the same forms | `government.elections-administration` |
| Literature, artwork, ad buys | `creative.ad-campaign`, `creative.print-production` |
| Elected office's constituent files | `government.constituent-casework` |
| **Canvass / voter-contact register** | **Protected Records — no owning row. NJ-PC-1.** |

## NEEDS-JOSEPH

**NJ-PC-1 — the orphan structure.** The canvass or voter-contact register is a real, coherent, highly sensitive artefact family with no owning row after this refusal, because it evidences no relation and therefore cannot activate `nonprofit`. Alternatives: **(a)** leave it permanently in Protected Records — safe, gives it no grouping axis; **(b)** host it on `business_operations` as an outreach-and-contact register beside `customer-account-management` — gains a grouping axis, loses the protective default; **(c)** treat "a register of named non-consenting third parties" as a cross-schema privacy primitive owned by P7 rather than a domain. I recommend **(a)** and flag **(b)** as the dangerous choice.

**NJ-PC-2 — the dangling edge.** `government.elections-administration` collides with this id and asserts campaign-side custody of nomination packs, agent appointments, spending returns, election addresses and count tallies. The assertion survives; its target does not. R1c must re-point it or reopen the coverage on `business_operations`. Not editable from here.

**NJ-PC-3 — sibling symmetry.** `nonprofit.json`'s open question marks `nonprofit.advocacy-campaign` weak on the ground that a campaign plan is go-to-market with different nouns. Whatever reason keeps that sibling will very likely apply here. R1c should decide both together rather than land an inconsistent pair.

**NJ-PC-4 — a privacy gap noticed here.** A party's donation report to an electoral regulator is structurally a regulated-entity-to-regulator filing, but unlike a company's filing it **discloses named individual donors**. If that matters, `business_operations.corporate-regulatory-filings` needs a privacy note it does not currently carry. This row is where the need surfaced; the fix is not this row's to make.

## Self-verification

- JSON parses (`python3 -m json.tool`). Key set matches the landed sibling `government.elections-administration.json` exactly.
- All eight `collides_with` ids verified present in `planning/domains/roster.json` by string check.
- All six `falls_through_to` names are among `00`'s nine residual homes.
- All seven `00` quotations grep-verified verbatim against `planning/00-database-agent-product-design.md`; every other quotation is attributed to `nonprofit.json` or `government.elections-administration.json` in text, not to `00`.
- `fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`, `role_split: []`. No thresholds, no handling classes, no `public_low`.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact.
- Wrote only the two assigned files. Did not edit the roster, `29-DOMAIN-OWNERSHIP.md`, canonical fields, `check.py`, `src/`, or any neighbour node.
