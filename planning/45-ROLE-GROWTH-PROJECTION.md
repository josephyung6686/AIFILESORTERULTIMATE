# How many organization roles, really — and does the answer matter to the architecture

Date: 2026-08-27 · **Everything below computed at 2026-08-27T13:00:17Z** against `planning/domains/nodes/`
(being written live by another session; read-only in this pass, and the census at the top and the last
quotation check at the end returned identical numbers).
Second opinion on [`43-ROLE-VOCABULARY-AND-RECUT.md`](43-ROLE-VOCABULARY-AND-RECUT.md), commissioned
because 43's growth projection rested on two data points. It revises none of 43's recipe work.
`00-database-agent-product-design.md` wins on conflict.

**Nothing here was taken from 43.** The 270 kept template rows were re-read in full (444,078 bytes of
`template.why`) and re-assigned roles from scratch, deliberately without starting from 43's list of 24.
§7 says where the two readings differ. All 25 quotations below were checked by exact substring match
against the row's own `template.why`: **misses 0 of 25.**

---

## 0. The answer, before the evidence

| | |
|---|---|
| **Independently derived role count** | **36 named**, **32 adopted** at 43's own ≥2-domain bar — *not* 24. My 12 extras project cleanly onto 43's 24 with no orphans, so the gap is a **granularity choice**, not a factual dispute. |
| **Is the growth curve sub-linear?** | **Yes, but the published evidence for it was invalid.** The launch six is a **1.8th-percentile** sample for k=6 — the least role-diverse 6-subset available. The 15→24 pair measured *sample bias*, not saturation. The real curve is a species-accumulation curve and it does flatten. |
| **Is it flat at 23?** | **Depends entirely on granularity, and on nothing else.** At 43's granularity the last **9 consecutive domains added 0 new roles**. At a granularity that keeps single-domain concepts distinct, 3 of the last 9 still added one each and the curve had **not** stopped. |
| **Defensible ceiling** | **32–41** for domains resembling these 23. For *unresearched* domains: **UNKNOWN**, and not estimable from this corpus — 23 domains one person enumerated is not a random sample of the domain universe, so every richness estimator's key assumption fails. |
| **Does an incomplete role vocabulary break the architecture?** | **No.** A role is a semantic label; P10's `TemplateDefinition` already admits "template-local roles" (`P10 SPEC:353`). Role count is a **research** question. |
| **Does anything else break?** | **YES, and this is the finding.** The ceiling that binds is the **P6 field allow-list**, not the role list — and `allowed_vocabulary_for` is planned to be **the union of one schema's allowed FIELDS**, with a test named `test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider`. For a schema with no fields it returns `()`, and Site E then rejects **every** proposed dimension. §5.7's custom-template path is closed for any domain without declared fields. |
| **The 17 zero-field schemas** | **Do not declare fields for them before shipping**, and note the harder fact: the shipped product does not know those 17 domains exist. Fix the **one** Site-E decision instead (§6). |
| **Where 43 §9 is wrong** | §9 requires `allowed_vocabulary` to carry "the canonical roles plus template-local dimension names". P10 Task 8's own docstring forbids exactly that widening. §9 also cites one gate; there are **four**, carrying three different kinds of content (§5.2). |

**The single sentence.** The owner is right that the product must not be limited to what is on his
computer — but he is right about **fields**, not roles, and the code agrees with him: `src/facts/domains.py`
recognises **ten** schema ids and carries **37 fields** total, and it says in terms that it reads
`planning/domains/` **never**.

---

## 1. Method, and what is actually on disk

### 1.1 Census, recomputed

```
roster rows                                            358
complete rows (.json AND .research.md present)         333
kept template rows (kind==template, refuse_node falsy) 270  across 23 schemas
  ├─ bound   (template.dimension_order non-empty)       54  in 6 schemas
  └─ prose   (dimension_order == [])                   216  in 17 schemas
schema rows                                             23
schemas declaring fields                                 6   academic 5, college_applications 5,
                                                             research 6, photos 6, code 4, finance 5
```

Identical to 43 §1.1. Bound rows by schema: finance 18, academic 11, photos 9, research 8,
college_applications 5, code 3.

### 1.2 How I derived roles

For each of the 270 rows I read the level sequence the row actually recommends — the bound
`dimension_order` tokens where they exist, and the level named in `template.why` prose where they do not
(*"the recommendation held as prose is X, then Y, then Z"*). I named each level from the row's own words
and merged two levels only when a row's own argument made them one thing. I did **not** start from 43's
24, and where the corpus draws a distinction I kept it rather than collapsing it to fit an existing role.

**Two conventions, stated so they can be disagreed with.**

1. **A level a row argues for but cannot fill counts.** `manufacturing.field-service-report` names
   `client` and cannot use it; `research.grants-funding` names the sponsor and has no key for it. Both
   are roles the corpus needs. I count them where the row puts them in a recommended order, and *not*
   where the row only laments their absence (so grants-funding's sponsor is excluded).
2. **A level a row affirmatively forbids does not count.** Every `law_practice` row's banned party level,
   `government.international-development`'s geography, `retail_hospitality`'s SKU. These are the corpus
   saying "not this", and counting them would inflate the vocabulary with refusals.

### 1.3 The unit of the curve is the domain, not the row

43 counted rows-and-domains per role. For a growth question the row count is a nuisance variable —
`law_practice` has 23 rows and 8 roles; `code` has 3 rows and 3 roles. What matters is: **when you add a
new domain, how many roles does it bring that you did not already have.** So §3 samples domains.

---

## 2. Task A — the 36 roles this pass derives

### 2.1 The 24 that agree with 43

`artifact_kind`, `subject_anchor`, `matter_anchor`, `scope_period`, `cycle_period`, `lifecycle_stage`,
`site_anchor`, `asset_instance`, `component_anchor`, `occasion_anchor`, `holder_institution`,
`issuing_org`, `addressed_org`, `counterparty_org`, `org_unit`, `capture_time`, `capture_kind`, `place`,
`account_kind`, `repository_instance`, `purpose_anchor`, `series_instalment`, `standard_ref`,
`variant_axis`.

I reached all 24 independently and would retire none. I would merge none either — including the pair I
expected to merge, `occasion_anchor` / `cycle_period`, which several rows write as one disjunctive level
(`business_operations.board-governance`: *"then the meeting occurrence or cycle"*). The field evidence
settles it: `event` (photos) and `term` (academic) are both canonical, both destination-eligible, and
plainly different. Keep them apart.

### 2.2 The 8 roles 43 lacks that clear its own ≥2-domain bar

| Role this pass adds | Definition | Dom | Verbatim evidence (checked) |
|---|---|---:|---|
| **`entitlement_anchor`** | a granted, renewable standing — right, permit, licence, credential, approval, consent — that **outlives every proceeding beneath it** | **6** | `law_practice.ip-prosecution`: *"THE RIGHT COMES BEFORE THE MATTER"*; `engineering.aerospace-airworthiness`: *"drops or demotes project because the approval outlives it"*; `government.permit-licensing`: *"the organizing level for this row is the PERMISSION"*; `career.credentials-licenses`: *"the ISSUING AUTHORITY first, then the CREDENTIAL"*; `manufacturing.environmental-compliance`: *"authorisation, then emission point, then reporting period"*; `resource_operations.forestry-records`: *"operating_authority inserted only where several licences, tenures or obligations divide the same estate"* |
| **`product_line`** | a standing offering, range, menu, season, part or output stream that persists across every occasion and is not a project | **5** | `retail_hospitality.menu-recipe-costing`: *"a STANDING PRODUCT-LINE level - the menu, range or season"*; `business_operations.product-requirements`: *"then the PRODUCT, then the feature or initiative"*; `manufacturing.spare-parts`: *"SITE (as the stocking location) then PART then record type"*; `resource_operations.farm-records`: *"crop, livestock group or output stream"* |
| **`function_area`** | a standing service, duty, policy or discipline area **above** both the subject and the document function | **4** | `government.social-services-casework`: *"service or duty area, then the CASE TOKEN"*; `business_operations.policy-handbook`: *"then the policy AREA or function"*; `construction_property.drawings-revisions`: *"then the DISCIPLINE or package, then the SHEET"*; `engineering.simulation-analysis`: *"project -> design_item -> study_type"* |
| **`provenance_side`** | which side of an exchange the artefact came from — obtained/authored/published, sent/received, issued/received/decided | **3** | `creative.journalism-reporting`: *"a split on the PROVENANCE of the material (obtained / authored / published)"*; `clinical_practice.referral-correspondence`: *"the correspondence direction (sent versus received) and then the document function"*; `government.public-procurement`: *"then the issued-versus-received-versus-decided function"* |
| **`recurring_series`** | the standing named series that *generates* occurrences — not the occurrence, not the cycle instance | 2 | `business_operations.meeting-record`: *"then the meeting SERIES, then the occurrence date"*; `nonprofit.religious-institution`: *"then the REGISTER SERIES, then the VOLUME"* |
| **`position_anchor`** | a post, role held, requisition or grade | 2 | `career.employment-records`: *"EMPLOYER first, then ROLE HELD, then DOCUMENT TYPE"*; `hr.compensation-planning`'s job grade |
| **`holding_collection`** | a curated holding of reusable material with its own taxonomy — a fonds, a library, an asset collection | 2 | `government.archives-recordkeeping`: *"The custody unit - collection, fonds, or accession - would come first"*; `creative.sound-design`: *"its parent dimension is the sound's own category"* |
| **`disclosure_tier`** | the access/aggregation tier a version belongs to | 2 | `government.public-health-administration`: *"aggregation state — identifiable source, working list, published output — is a stronger candidate separator than period"*; `business_operations.product-roadmap`: *"an audience level is arguably load-bearing here"* |

**Named and NOT adopted (1 domain each): 4.** `channel_locus` (retail_hospitality — agreeing with 43 §9
O6), `option_route` (a competing creative direction, distinct from `variant_axis`; `creative.ad-campaign`
puts them at two different depths: *"then CONCEPT ROUTE, then the VARIANT AXIS - market or placement"*),
`lot_instance` (manufacturing batch/lot/heat/serial), `fund_anchor` (nonprofit restricted fund).

### 2.3 The disagreement that is not cosmetic — `entitlement_anchor`, and 43's own O5

43 folds every one of my six `entitlement_anchor` rows into `matter_anchor` (*"a bounded proceeding, case,
claim, application, transaction, engagement, tenancy, requisition or job that opens, runs and closes"*).
But those rows put the entitlement **above** a matter, explicitly and with argument. Under one role that
becomes `matter_anchor > matter_anchor`.

**That is exactly 43 §9 O5**, which asks *"May `matter_anchor` nest inside itself? … 00's no-repeat rule
appears to forbid it at role level and permit it at field level."* O5 is not an open question about the
no-repeat rule. It is the symptom of a missing role. Splitting `entitlement_anchor` out dissolves it, and
the split is supported by 6 domains — above the 4-domain bar 43 itself used to **freeze** recipes.

`function_area` is the second substantive disagreement: 43 §7.3 names it and declines to adopt it as
single-domain (government). It is 4 domains.

### 2.4 Where 43's and my vocabularies stand relative to each other

Projecting my 36 onto 43's granularity (12 extras → nearest published role) yields **exactly 24, with no
orphans**. So neither reading contains a role the other cannot express. The whole 24-vs-32 gap is one
decision: *how coarsely may a role be defined before it stops being useful?* The corpus does not answer
that, and neither does 00.

---

## 3. Task B — the actual curve, not two points

### 3.1 The first published data point is invalid

43 (and the session lead) inferred sub-linear growth from **15 roles at 6 domains → 24 roles at 23
domains**. The six were the launch six: academic, college_applications, research, photos, finance, code.

Over all C(23,6) = 100,947 six-domain subsets:

| | launch six | random six, mean | sd | percentile of the launch six |
|---|---:|---:|---:|---:|
| this pass's granularity | **16** | 23.63 | 3.40 | **1.8 %** |
| 43's granularity | **16** | 18.04 | 2.05 | **11.0 %** |

(My 16 at 43's granularity corroborates 43's stated 15 to within one role.)

The launch six is the **least role-diverse** realistic 6-subset in the corpus — six personal-document
domains that share one shape (an institution, a period, a named work, a document function). Fitting a
growth trend through it and through k=23 does not measure saturation; it measures the distance between an
unrepresentative sample and the whole. **The projection "roles land in the 30s–40s" happens to bracket my
independent 32–41, but it was arrived at by a method that could not have known that.**

### 3.2 The real accumulation curve

Mean distinct roles over random k-domain subsets (exhaustive to k=5 and k≥19; 4,000 samples otherwise,
`random.seed(7+k)`):

| k | this pass (36 roles) | Δ | 43's granularity (24 roles) | Δ |
|---:|---:|---:|---:|---:|
| 1 | 8.04 | — | 7.00 | — |
| 2 | 13.19 | +5.15 | 11.07 | +4.07 |
| 4 | 19.67 | +2.80 | 15.62 | +1.88 |
| 6 | 23.63 | +1.80 | 18.03 | +1.07 |
| 8 | 26.42 | +1.22 | 19.59 | +0.68 |
| 12 | 30.21 | +0.79 | 21.48 | +0.40 |
| 16 | 32.87 | +0.49 | 22.71 | +0.22 |
| 20 | 34.87 | +0.46 | 23.56 | +0.20 |
| 23 | 36.00 | +0.35 | 24.00 | +0.13 |

**The shape, stated without a reassuring adjective:** it is a species-accumulation curve. It is concave
from k=2 onward, the marginal gain falls by roughly an order of magnitude between k=2 and k=23, and it is
still strictly increasing at 23. It does **not** plateau in either reading; the increment shrinks but never
reaches zero, and the final increment is exactly `f1/23` (the singleton count over the domain count), which
is an identity, not a measurement.

**And the curve cannot answer the question it looks like it answers.** Its ceiling is the vocabulary
observed in these 23 domains. It is flat at k=23 *by construction* — the 23rd domain can only contribute
roles already in the total. A rarefaction curve tells you about resampling the corpus you have; it tells
you nothing about a domain outside it.

### 3.3 The honest test: the corpus in the order it was actually researched

`git log --diff-filter=A` gives the real landing order of the 23 schemas. Cumulative distinct roles:

| # | schema landed | 43's granularity | this pass |
|---:|---|---:|---:|
| 1–7 | academic … photos (the launch six + career) | 18 | 20 |
| 8–11 | identity, legal, medical, clinical_practice | 18 (+0) | 21 (+1 `provenance_side`) |
| 12 | **business_operations** | **22 (+4)** | **29 (+8)** |
| 13 | construction_property | 23 (+1) | 30 (+1) |
| 14 | **creative** | **24 (+1)** | 33 (+3) |
| 15–19 | engineering, government, hr, law_practice, logistics | 24 (**+0 each**) | 33 (+0 each) |
| 20 | manufacturing | 24 (+0) | 34 (+1 `lot_instance`) |
| 21 | nonprofit | 24 (+0) | 35 (+1 `fund_anchor`) |
| 22 | retail_hospitality | 24 (+0) | 36 (+1 `channel_locus`) |
| 23 | resource_operations | 24 (+0) | 36 (+0) |

**This is the strongest evidence in either direction, and it points both ways at once.**

At 43's granularity the vocabulary was complete at domain **14**, and nine consecutive new domains from
six unrelated industries added **nothing**. That is a genuine saturation signal and it is not circular:
it says the last nine domains contain no role *concept* the first fourteen had not already produced.

At a granularity that preserves single-domain concepts, three of the last four domains each added one,
and the corpus stopped while still climbing at ~0.35 roles/domain.

**Both statements are true of the same corpus.** The difference is entirely the lumping threshold — and
that threshold was chosen by an analyst who had already seen all 23 domains. A flat tail produced by a
post-hoc coarsening is weaker evidence than it looks.

---

## 4. Task C — the ceiling, with the uncertainty stated

### 4.1 What can be estimated

Incidence-based richness estimators (Chao2), applied to domain-incidence:

| | roles observed | singletons f1 | doubletons f2 | Chao2 (bias-corrected) | classic |
|---|---:|---:|---:|---:|---:|
| this pass | 36 | 8 | 7 | **39.5** | 40.6 |
| 43's granularity | 24 | 3 | 4 | **24.6** | 25.1 |

Same corpus, same method, **two answers 15 roles apart**, because the estimator inherits the analyst's
lumping decision through `f1`. That alone should stop anyone quoting a single number.

### 4.2 The defensible range

**For domains that resemble these 23: 32–41 roles.** Lower bound = observed at the ≥2-domain bar; upper
bound = Chao2 at the finer granularity. If you prefer 43's coarser cut, the same interval reads **24–26**.
Pick a granularity first; the range follows from it, not the other way round.

### 4.3 For 100 domains, or for "not the ones on my computer": **UNKNOWN**

Not "probably fine". **Unknown, and not estimable from this corpus.** Three reasons, each sufficient:

1. **The sample is not random.** Chao2's load-bearing assumption is that the 23 domains are a random draw
   from the domain universe. They are one person's enumeration of the domains he could think of, heavily
   weighted to professional office work. Under a non-random sample Chao2 is a lower bound on a quantity
   whose definition has already been violated.
2. **The estimate moves more with granularity than with data.** §4.1: 24.6 vs 39.5, same corpus. Adding
   domains 24–100 would move the number less than a single lumping decision does.
3. **The tail is where the answer lives, and the tail is what a biased sample loses first.** Eight of my
   36 roles appear in exactly one domain. Every one of them arrived from a domain unlike the launch six —
   `channel_locus` from the 22nd domain landed, `fund_anchor` from the 21st, `lot_instance` from the 20th.
   The three most recently-researched domains each contributed a singleton. That is the signature of a
   sample that stopped, not one that finished.

**The one directional claim the evidence does support**, stated as weakly as it deserves: roles are
*relational* (a thing, a place, a bounded process, a period, a function, an org in one of four postures)
while fields are *lexical*. A genuinely new domain reliably brings new field vocabulary and only sometimes
brings a new relation. Nine consecutive domains adding zero roles at 43's granularity is real support for
that. It supports **"roles grow much more slowly than fields."** It does **not** support any specific
ceiling, and it must not be used as one.

---

## 5. Task D — does the architecture depend on the role count being bounded?

### 5.1 The direct answer: **no, not on roles**

`planning/parts/P10-tree-design-freeze/SPEC.md:353` already says `TemplateDefinition` composes fragment
versions *"plus any template-local roles and constraints"*, and `:355` says `TemplateApplicability`
*"maps those roles to live P6 fields for exactly one `uses_schema` domain … without weakening P6's
allow-list."*

So a role is a **semantic label that costs nothing to add**, and it becomes *fillable* only when an
applicability row maps it to a live P6 field. Naming is open; filling is gated. **The role count is a
research question, and the owner should be told that plainly.**

### 5.2 Correction: `allowed_vocabulary` is not one gate, and does not hold one kind of thing

43 §9 cites `template_validation.py:102-103` as though it were the gate. There are **four**, and the field
carries **three different kinds of content** depending on `call_site`:

| Site | Code | What `allowed_vocabulary` members ARE |
|---|---|---|
| **B** group | `src/llm_harness/group_validation.py:132,145-149` | fact **values** — `payload["date"]`, `["project"]`, `["purpose"]` must be in it |
| **C** placement | `src/llm_harness/placement_validation.py:207,220` + `_invented_dimension(:185-197)` | destination **node ids**, then `node_exists(destination, plan_version)` against the frozen tree; dimension **values** |
| **D** residual | `src/llm_harness/placement_validation.py:324` | target **node ids** |
| **E** template | `src/llm_harness/template_validation.py:101-103` | dimension **names** — the roles question |

§9's requirement is therefore only meaningful **per site**. Read globally it is incoherent: putting role
names into Site C's vocabulary would offer them as destinations, and putting node ids into Site E's would
break custom templates. Any test written from §9 as drafted would test the wrong site.

There is also a second Site-E gate §9 does not mention: `:113` rejects any dimension whose
`evidence_ref` is not in the response's own citations, and citations are validated against the dossier's
evidence. **A template-local dimension must be backed by evidence already in the dossier**, and dossier
evidence comes from validated facts.

### 5.3 The finding: the binding ceiling is the FIELD allow-list, and §9 asks for a widening the plan forbids

43 §9 requires: *"`allowed_vocabulary` MUST NOT be the 24 canonical roles alone … It MUST carry the
canonical roles **plus** template-local dimension names."*

P10 Task 8 — the very task §9 addresses — plans the opposite. `planning/parts/P10-tree-design-freeze/PLAN.md:5548-5559`:

```python
def allowed_vocabulary_for(catalogue: TemplateCatalogue, *,
                           uses_schema: str) -> tuple[str, ...]:
    """The closure P8's Site E checks every proposed dimension name against.

    It is the union of the allowed fields of the rows for ONE schema. Unioning
    across schemas here would widen a P6 allow-list at the dossier boundary,
    which is the one thing the one-row-one-schema rule exists to prevent.
    """
```

and its test, `PLAN.md:5118-5123`, is named
**`test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider`**:

```python
assert allowed_vocabulary_for(CATALOGUE, uses_schema="photos") == ("capture_year", "event")
assert allowed_vocabulary_for(CATALOGUE, uses_schema="academic") == ()
```

Three consequences, in order of severity.

1. **Site E's vocabulary is planned to hold P6 field keys, not role names.** §9's premise is wrong about
   what goes in the field.
2. **A schema whose rows declare no fields yields `()`**, and `template_validation.py:102-103` then
   rejects **every** dimension in any proposal (`any(name not in set())` is true for a non-empty list).
   §5.7's custom-template path is not merely narrow for such a domain — it is closed.
3. **§9's fix is the one widening the plan's own docstring forbids**, because it would widen a P6
   allow-list at the dossier boundary. §9 cannot be implemented as written without reversing a decision
   P10 made deliberately.

*(Caveat, stated: the `academic == ()` assertion is a fixture artifact — that CATALOGUE has no academic
rows. The **mechanism** is what matters: empty closure → total rejection, and a schema with no declared
fields produces an empty closure.)*

### 5.4 The harder fact: the product does not know the other 17 domains exist

`src/facts/domains.py:52-55` — shipped code, not a plan:

```python
SCHEMA_IDS: tuple[str, ...] = (
    "academic", "college_applications", "research", "career", "photos", "code",
    "finance", "identity", "medical", "legal")
```

and `:36-38` of the same module:

> *"**This module reads `planning/domains/` never.** That directory is a research artifact of 574
> proposed entries with its own gate; the catalogue this activates is `facts.fields`, and Task 25 asserts
> the import does not exist."*

The shipped field catalogue is 37 rows over 7 scopes, 24 destination-eligible:

| scope | n | keys |
|---|---:|---|
| universal | 10 | file_type, creation_date, language, duplicate_family, version_family, download_session, authored_by, target_school, our_firm, client |
| academic | 5 | school, term, subject, instructor, work_type |
| college_applications | 4 | target_university, application_cycle, application_document_type, purpose |
| research | 5 | project, stage, artifact_type, lab, venue |
| finance | 4 | institution, account_type, tax_year, record_type |
| photos | 7 | capture_year, event, location, people, camera_information, media_type, capture_date |
| code | 2 | repository, programming_language |

`FieldNotInCatalogue` exists so that *"'it should not invent new fields automatically' is enforced by
there being no code that could"* (`src/facts/fields.py:55-60`), and Site A enforces it independently of
`allowed_vocabulary` at `src/llm_harness/fact_validation.py:204` (`if proposal.field_key not in allowlist`).

So there are **two independent ceilings**, and 43 §9 addresses only the second:

- **the field allow-list** (Site A, `facts.fields`, 37 keys, closed by construction) — decides what the
  product can *know*;
- **the dimension vocabulary** (Site E) — decides what it can *branch on*, and is planned to be derived
  *from* the first.

**The owner's instinct is correct and better-targeted than the answer he was given.** *"There's too much
field stuff we need to encapsulate. we cannot be limited to the ones in my computer"* names the real
constraint. The role count does not.

### 5.5 One further thing that breaks, worth naming

Even a perfectly validated custom template is inert until its node is in a frozen plan version:
`placement_validation.py:220-221` requires `node_exists(destination, plan_version)`, and P10 SPEC:360
says *"Neither a fragment nor a valid template creates nodes."* So the §5.7 path is
**propose → user approval → freeze → only then placement**. That is correct by design, but it means the
custom-template path has a *third* dependency beyond vocabulary and fields: P11 must actually turn an
approved custom template into nodes in the next plan version. That wiring is unbuilt.

---

## 6. Task E — the 17 zero-field schemas

### 6.1 The case FOR declaring fields before shipping

- It is the only thing that makes those domains organizable at all. Every one of the 216 prose rows says
  the same sentence in its own words — *"a dimension naming an undeclared field opens a tree level no fact
  could ever fill."* The research is done; the fields are argued in 444 KB of prose that will decay.
- It is what unlocks §5.7 for them. Per §5.3, a fieldless schema's Site-E closure is empty and every
  custom-template proposal is rejected. Declaring fields is the *only* currently-planned mechanism that
  makes the closure non-empty.
- 43's own conclusion depends on it: **8 of its 11 freezable recipes are prose-only**, including the
  largest. Until fields land, none of them can bind (43 §9 O3).

### 6.2 The case AGAINST

- **It contradicts the design's explicit launch scope.** §3.15 (`planning/01-product-design-structured.md:558-568`):
  *"The initial release should fully support only the domains required to validate the product on real
  heterogeneous corpora: academic coursework, college applications, research and lab work, career and
  recruiting, photos and captures, and code projects. … Other domains remain placeholders until user
  demand and corpus evidence justify detailed templates."* The 17 are placeholders **by decision**.
- **It is not 17 edits; it is 17 new schemas.** The shipped product recognises ten schema ids (§5.4).
  Thirteen of the 17 are not among them. Adding one means: a `SCHEMA_IDS` entry, a `facts.fields` scope,
  every field row with `destination_eligible` and reliability ceiling, an `ActivationSignals` rule (P6
  authors none — *"The signals arrive as an injected `ActivationSignals` with no default"*), extractors
  that can produce the facts, P7 sensitivity classes, and P10 applicability rows. Multiply by 17.
- **It does not generalize.** Declaring fields for these 17 makes the product good at *these* 23 domains
  and no better at the 24th. It is the exact thing the owner said he does not want.
- **He is behind schedule.** This is the largest available scope increase and it buys the least
  architectural leverage of the three options.

### 6.3 Recommendation

**Do not declare fields for the 17 before shipping. Do fix one thing, and it is small.**

The custom-template path is the design's own answer to "not limited to the ones on my computer", and it is
currently closed for exactly the domains it exists to serve — not because the role list is short, but
because `allowed_vocabulary_for` returns `()` for a schema with no fields (§5.3). **That is one decision in
one unbuilt function**, and it is the highest-leverage thing available:

1. **Decide, explicitly, what `allowed_vocabulary_for` returns for a group that fits no existing template.**
   This is the sharp version of 43 §9's question, and 43 does not ask it. Site E fires on
   `ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE` (`src/llm_harness/vocabulary.py:137-140`) — *no existing
   template*. So what `uses_schema` is passed? Today the function's contract has no answer for "none", and
   passing the nearest schema hands a novel domain the wrong closure. **Decide it before P10 Task 8 is
   built; it is a one-line contract change then and a rewrite afterwards.**
2. **Add a test for both halves of the asymmetry** — 43 §9's one genuinely good instruction, kept: an
   evidence-backed novel dimension is accepted at template-local scope; nothing promotes it to canonical
   without human review.
3. **Do not adopt 43 §9's requirement as drafted.** It names one gate of four (§5.2), misidentifies what
   the field holds, and asks for a widening P10 Task 8's docstring forbids.
4. **Ship the launch six.** Their fields exist, their 54 bound rows are the only recipes that can bind
   (43 §6.1: zero bound rows use any new role — my read agrees), and nothing in this analysis changes
   what they do.
5. **Keep `planning/domains/` as the research artifact it is.** If a 17-domain field pass ever happens, do
   it after launch, evidence-first, one domain at a time — which is precisely what §3.15 already says:
   *"until user demand and corpus evidence justify detailed templates."*

**Cost of the recommendation: one decision. Cost of the alternative: 17 schemas, before a launch that is
already late.**

---

## 7. Where this pass disagrees with 43

| | 43 says | This pass says | Consequence |
|---|---|---|---|
| **D1** | 24 roles adopted | 36 named, 32 at the same bar | Granularity, not fact. Both project onto each other with no orphans. |
| **D2** | `matter_anchor` covers rights, permits, licences and credentials | `entitlement_anchor` is a 6-domain role that sits **above** matter | **Dissolves 43 §9 O5.** O5 is a missing role, not an open rule question. |
| **D3** | §7.3 `function_area` is single-domain, not adopted | 4 domains | Adopt it. |
| **D4** | Roles grow sub-linearly (15@6 → 24@23) | The 15@6 point is a **1.8th-percentile** sample; the conclusion survives, the evidence does not | Do not cite the two-point trend again. |
| **D5** | §9 O7: is `operating_authority` `holder_institution` or `counterparty_org`? | Neither — the four `resource_operations` rows read it as the **licence/tenure/consent**, not an organization (*"several licences, tenures or obligations divide the same estate"*) | O7 is asking an org question about a non-org. It resolves to `entitlement_anchor`. |
| **D6** | §9: `allowed_vocabulary` must carry roles + template-local names | It is planned to hold **fields**, per-schema, deliberately narrow | §9 is not implementable as written (§5.3). |
| **D7** | §9 cites one gate | Four gates, three content kinds | Any §9-derived test would target the wrong site. |
| **D8** | (silent) | The product recognises **10** schemas and **37** fields, and reads `planning/domains/` never | Reframes Task E entirely. |

Where 43 is right and I confirm it independently: the org-role split survives (I find the same four
postures, and a fifth strain — *the organization a record is ABOUT*, in `law_practice.corporate-secretarial`'s
ENTITY and `government.school-district-administration`'s INSTITUTION — which I record rather than adopt);
`variant_axis` is genuinely thin; the launch six's bound orders are unaffected by any of this.

---

## 8. OPEN

| | Question | What would settle it |
|---|---|---|
| **N1** | **What `uses_schema` does Site E receive for a group that fits no existing template?** | A P10 contract decision, before Task 8 is built. This is the load-bearing one. |
| **N2** | May a Site-E dimension be backed by evidence that is not a stored P6 fact? §5.7 says a custom template *"cannot invent unsupported facts"*; if the answer is no, the field allow-list is the permanent ceiling and §5.7 is only usable inside the 6 field-declaring schemas. | A design ruling. |
| **N3** | Is there a fifth org role — *the organization the record is about*, distinct from holder / issuer / addressee / counterparty? 2 domains (`law_practice`, `government`). | A third domain, or a decision to read it as `counterparty_org`. |
| **N4** | Does the granularity question have an answer at all? Two careful readers of one corpus produced 24 and 32. | A stated rule for when two levels are one role. 00 gives none. |
| **N5** | Who turns an approved custom template into nodes in the next plan version? (§5.5) | A P11 task. Currently unassigned. |

---

## Appendix — reproduction

```bash
cd "/Users/jy/GRAPH AGENT"

# §1.1 census
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
kept=[d for d in rows if d['kind']=='template' and not d.get('refuse_node')]
bound=[d for d in kept if d['template'].get('dimension_order')]
print('complete',len(rows),'kept',len(kept),'bound',len(bound),'prose',len(kept)-len(bound))
sch=[d for d in rows if d['kind']=='schema']
print('schemas',len(sch),'with fields',[(d['id'],len(d['fields'])) for d in sch if d.get('fields')])"

# the 444,078-byte prose corpus this pass read in full
python3 -c "
import json,os,collections
r=json.load(open('planning/domains/roster.json')); N='planning/domains/nodes/'; f=set(os.listdir(N))
rows=[json.load(open(N+n['domain_id']+'.json')) for n in r['nodes']
      if n['domain_id']+'.json' in f and n['domain_id']+'.research.md' in f]
by=collections.defaultdict(list)
for d in rows:
    if d['kind']=='template' and not d.get('refuse_node'):
        by[d['schema_id']].append((d['id'], d['template'].get('dimension_order'), d['template']['why']))
tot=0
for s in sorted(by):
    print('#'*8, s, len(by[s]))
    for i,o,w in sorted(by[s]): print('###',i,'| ORDER:',o); print(w); print(); tot+=len(w)
print('TOTAL BYTES', tot)"

# §3 the curve, §4 Chao2 — the per-domain role assignment is this pass's reading and lives in
# this session's scratchpad as roles.py; the assignment is reproduced in full in §2 and the
# per-domain sets are recoverable from the corpus dump above.

# §5.2 the four allowed_vocabulary gates
grep -rn "allowed_vocabulary" src/llm_harness/*.py

# §5.3 what P10 Task 8 plans to put in it
sed -n '5118,5123p;5548,5559p' planning/parts/P10-tree-design-freeze/PLAN.md

# §5.4 what the product actually recognises
sed -n '36,38p;52,55p' src/facts/domains.py
python3 -c "
import sys; sys.path.insert(0,'src')
from facts.fields import FIELD_ROWS
from facts.vocabulary import FIELD_SCOPES
import collections
c=collections.Counter(r.scope for r in FIELD_ROWS)
print(len(FIELD_ROWS),'fields |',sum(1 for r in FIELD_ROWS if r.destination_eligible),'destination-eligible')
for s in FIELD_SCOPES: print(' ',s,c[s],[r.field_key for r in FIELD_ROWS if r.scope==s])"

# §3.3 the real landing order
for s in academic college_applications research photos finance code career business_operations \
         construction_property creative engineering government hr law_practice legal logistics \
         clinical_practice manufacturing nonprofit resource_operations retail_hospitality identity medical; do
  echo "$(git log --diff-filter=A --format=%ct -- "planning/domains/nodes/${s}.*.json" | tail -1) $s"
done | sort -n
```

Every quotation in §2 was verified by exact substring match against its row's `template.why` before
publication: **misses 0 of 25.**
