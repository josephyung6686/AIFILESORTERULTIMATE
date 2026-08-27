# 55 — Ambiguity and Overlap

**The question:** *"If I were a user, a human being, what would I want to do? If I'm a lawyer or a
student or a researcher, or I am multiple. How would I want my files sorted and how would I want the
experience to be? Does the current system honour that? What if there are nuances — like a research
paper that's part of a school homework? Or legal stuff for an application or for a deal?"*

Every persona pass so far assumed one person living one life. Real disks are not like that. This
document is about the cases where two domains legitimately claim the same file, or one person is
several people at once.

**Method.** Half 1 grounds every case in the 358-row corpus (`planning/domains/nodes/*.json`) and
cites `domain_id`. Half 2 answers, against the built code, whether each case works — read and RUN,
not read and judged. Where a case could be executed it is, in
`tests/integration/test_ambiguity_cases.py` (17 tests). Full suite at the time of writing: **4270 passed, 1 xfailed**. Several of those tests pass by
asserting the product does the wrong thing; the assertion is the evidence, and the day one starts
failing is the day that case got fixed.

**Verified against** `3605aa1` plus the uncommitted working tree, 2026-08-27T16:22Z. The tree moved
under this audit twice — `src/tree_design/freeze.py` and `src/placement/groups.py` both landed
mid-pass and both closed findings this document had already written down. Every verdict below is the
state at that timestamp and two of them are marked as having changed during the audit.

---

## 0. The corpus already mapped the overlap

Counts re-derived by script over `planning/domains/nodes/*.json` (and pinned in
`test_thirteen_of_the_corpus_twenty_three_schemas_have_no_runtime_identity`):

| | count |
|---|---|
| template/schema rows | **358** across **23** schemas |
| `collides_with` edges | **2409**, of which **1339 cross schemas** |
| `also_holds_with` edges | **309**, of which **277 cross schemas** |
| launch state | 17 `full`, 16 `safety`, 325 `placeholder` |

The two edge kinds are the corpus telling us two different things, and the distinction is the whole
subject of this document:

* **`collides_with`** = *two situations, one of them is right.* The row states the discriminating
  evidence. Example, `academic.teaching` → `academic.coursework`: "a syllabus, lecture deck, problem
  set or solution set can sit in a student's corpus and an instructor's corpus as **byte-identical
  files** … The discriminating evidence is instructor-side authorship and cohort custody."
* **`also_holds_with`** = *two situations, both are right.* Example, `research` →
  `college_applications`: "An academic abstract submitted as part of a university application can
  retain project = PVA/RDP and document type = abstract **while also** carrying purpose = university
  application and target university = UChicago."

The corpus's answer to ambiguity, stated in nearly identical words on dozens of rows, is
**co-activation on disjoint evidence, with the protective ordering running first**:

> "both schemas may remain active on disjoint evidence and the identity safety gate runs before any
> academic placement" — `identity.immigration-visa`
>
> "protection remains first whichever group holds it" — `identity.core-documents`
>
> "One file may hold facts from more than one domain without losing information." — quoted by
> `construction_property.snagging-defects` from §3.11

**The single most important finding of this audit is that the built system implements co-activation
at exactly one layer and then destroys it at the next.** §5 below.

---

## HALF 1 — The case set

Twenty-one cases in six classes. Each states the file, the claimants, what a real person wants, and
why it is hard.

### A. One file, two domains (`also_holds_with`)

**A1 — The CAD drawing that is also a contract exhibit.**
`engineering.cad-model` ∩ `construction_property.variation-claim` ∩ `legal.practice-matter-file`.
The corpus carries the chain: `engineering.invention-disclosure` `also_holds_with`
`legal.practice-matter-file` and `research.manuscript-publication`;
`construction_property.variation-claim` `also_holds_with` `legal`, `finance` and
`business_operations`. *Wants:* one folder for the dispute, with the drawing appearing under both the
design set and the exhibit bundle. *Hard because:* the drawing's engineering facts (part number,
revision) and its legal facts (matter reference, exhibit number) are genuinely disjoint, so neither
side is wrong, and a revision that changes the design does not change the exhibit.

**A2 — The photo that is a family memory and insurance-claim evidence.**
`photos.family-archive` ∩ `finance.insurance-personal` (see `legal.personal-legal-matters` →
`finance.insurance-personal`: "A household liability claim and a personal legal matter share the
people, loss event, claim reference and money figure"). *Wants:* it stays in the family album and
appears in the claim bundle. *Hard because:* the claim bundle is time-bounded and the album is
permanent, so the "same" file has two lifetimes.

**A3 — The spreadsheet that is household budgeting and sole-trader bookkeeping.**
`business_operations.budget-forecast` `also_holds_with` `finance.small-business-bookkeeping`;
`logistics.fleet-vehicle` `also_holds_with` `finance.small-business-bookkeeping`. *Wants:* one file,
two views — "what I spend" and "what I can claim". *Hard because:* the split is per-ROW inside the
file, not per-file, and no file-level fact can express it.

**A4 — The conference paper that is also submitted coursework.**
`research.conference-presentation` `collides_with` `academic.coursework`: "a class project deck has
slide titles, speaker notes and result figures and often names an institution … The failure this
prevents is a coursework deck being shelved as a conference talk because a university name appeared
on its title slide." Plus `academic` `also_holds_with` `research`: "a course-numbered thesis, senior
project or lab report carries subject and work_type from its course evidence and project, lab or
artifact_type from its own research evidence." *Wants:* under the course while the course runs, under
the research project forever after. *Hard because:* both readings are simultaneously true and the
user's own answer changes at the end of term.

**A5 — 00's own example: the PVA/RDP abstract.** `research` ∩ `college_applications`, quoted verbatim
above. This is the design's canonical multi-domain file and the one every worked example returns to.

### B. Same file type, opposite side of the table (`collides_with`, role inversion)

**B1 — The résumé that is mine vs a candidate's.** `career.recruiting` ∩
`career.employer-side-hiring`. The corpus is blunt: *"Two resumes are indistinguishable as documents;
the roles are opposite … This edge is not cosmetic: the wrong side of it puts another person's data
into the holder's job-search branch, which is what this row's privacy rules exist to prevent."*
*Wants:* absolute separation. *Hard because:* the only discriminator is the one-to-many inversion —
one person across many employers vs many people under one opening — which is a property of the
neighbourhood, not the file.

**B2 — The NDA signed as an employee vs issued to a contractor.**
`career.employment-records` ∩ `hr.onboarding-offboarding` ∩ `law_practice.contract-negotiation`
(`hr.onboarding-offboarding` `also_holds_with` `legal` and `identity`). *Wants:* "agreements binding
me" apart from "agreements I impose". *Hard because:* the executed PDF is the same shape both ways
and the signature block names both parties.

**B3 — The invoice sent vs the invoice received.** `finance.receipts-expenses` ∩
`finance.small-business-bookkeeping` ∩ `business_operations.customer-account-management`. *Wants:*
receivables apart from payables — the single most consequential folder split a sole trader makes.

**B4 — The lease as tenant vs as landlord.** `construction_property.tenancy-management`
`collides_with` `legal.leases-agreements`: *"A tenancy agreement is that row's executed instrument and
this row's managed item, and one signed PDF is both."*

**B5 — The clinical note: author vs subject.** `clinical_practice.patient-chart` `collides_with`
`medical.personal-health-records`: *"The discriminating evidence is the holder's ROLE — an author
sign-off … beside a differently named subject, supports this row; the holder named in the patient
slot … supports medical.personal-health-records … where the role is unevidenced the correct outcome
is neither."*

### C. One person, several lives

**C1 — The PhD student who TAs a course they also take.** `academic.coursework` ∩
`academic.teaching`, quoted above: byte-identical files, discriminated only by custody evidence.

**C2 — The freelancer with two clients and a day job.** `creative.client-engagement`
`also_holds_with` `career`: *"A delivered client work may later be selected as the maker's portfolio
sample. The commissioned production record and the authored career evidence coexist; portfolio
selection is not inferred from delivery."* Plus `creative.client-engagement` `collides_with`
`career.consulting-client-engagement`: *"The same multidisciplinary engagement may contain members of
both."*

**C3 — The doctor who is also a patient.** B5 with both roles held by one person, so even the
name-matching discriminator inverts.

**C4 — The parent filing for two children.** `medical.dependant-child-health` `collides_with`
`academic.k12-schooling`: *"School-required immunization, medication, sports-physical, and action-plan
files carry a school name and child name while containing clinical structure … A school name or
required-for-school line discriminates nothing, and protection runs first."* *Hard because:* the two
children's records are structurally identical and only the child's name separates them — and
`people` is destination-ineligible (§4 below).

**C5 — The lawyer whose matter file contains their client's medical records.**
`law_practice.discovery` `also_holds_with` `medical.personal-health-records`: *"Production membership
must not strip the clinical protection, and the clinical protection must not hide the fact that the
file is part of a bounded disclosed set."* Two protections that pull in opposite directions.

### D. The same file changing domain over time

**D1 — Job application → employment record on the day of hire.** `career.recruiting` `collides_with`
`career.employment-records`: *"candidacy language about a process still open, with no executed
commencement, is recruiting; an executed signature or countersignature block together with a labelled
effective-or-start-date slot … is the employment record. Fixtures: Offer letter - Deloitte.pdf,
awaiting countersignature, here; Offer letter - countersigned.pdf there. The two copies are one
version_family without either fact crossing."*

**D2 — Draft → preprint → published → someone else's citation.**
`research.manuscript-publication` `collides_with` `research.reading-library`: *"the holder's own
manuscript carries a manuscript-id token, a submission packet, an editorial thread or an author-query
proof; a collected paper carries a DOI and an author list without the holder and no lifecycle
evidence at all."*

**D3 — House purchase → property records → estate planning.** `law_practice.conveyancing`
`also_holds_with` `finance` — *"THE MONEY SEAM, and it runs through one folder in both directions …
THE SAME FIXTURE ON BOTH SIDES: a redemption statement from an existing lender"* — then
`legal.estate-planning` `collides_with` `finance.investment-brokerage`. One deed, three decades,
three domains.

**D4 — Performance review → capability process.** `hr.performance-cycle` `also_holds_with`
`hr.employee-relations`: *"An improvement plan is simultaneously the last routine step of a review
cycle and the first formal step of a capability process. Both readings are real and the stricter case
posture governs."*

### E. Protected material needed for an unprotected workflow — THE SHARPEST CLASS

**E1 — Passport scan required for a visa application.** `identity.core-documents` ∩
`identity.immigration-visa` ∩ `applications.purpose-packet`. The corpus states the intended behaviour
exactly: *"An identity copy is a common member of an application packet … Packet purpose must not be
copied onto the ID, and **protection remains first whichever group holds it**."* And
`applications.purpose-packet` → `identity.core-documents`: *"Whichever side holds it, protection runs
first and its filename and content stay out of model prompts."*

**E2 — Medical letter required for exam accommodations.** `medical` ∩
`academic.iep-accommodation-plans` ∩ `academic.standardized-testing`.
`academic.iep-accommodation-plans` `collides_with` `medical.dependant-child-health`: *"a school
issuer, an evaluator-ROLE slot, and a stated purpose of educational eligibility is this node; the
same assessment issued under a clinic's patient-identification block … is the dependant's health
record."*

**E3 — Divorce decree required for a mortgage application.** `legal.personal-legal-matters` ∩
`finance.loans-mortgage` ∩ `law_practice.family-law`. Both schemas are `safety` launch. The user
needs the decree *inside* the mortgage bundle and needs it *not* to make the mortgage bundle
sensitive.

**E4 — School-required immunisation record.** C4, restated as a protection question: the file must
sit in the child's school folder and stay a medical record.

**E5 — Identity documents inside a legal production volume.** `law_practice.discovery`
`also_holds_with` `identity.core-documents`.

### F. The ambiguity that resolves to nothing

**F1 — Clearly part of `Academics/Columbia/2026-Spring`, no recoverable work type.** §5.9's own
example, and the design's own answer is a scoped `General` branch rather than a global Unsorted
folder. This is the commonest ambiguity on any real disk.

**F2 — A group the categoriser could not label.** Exactly the multi-domain situations above are the
ones least likely to resolve to one category.

---

## HALF 2 — Verdicts against the built system

### 1. §6.9 shared material — **PARTIAL, and the missing half is decisive**

This is the design's own answer to one-file-two-homes, so it gets the fullest treatment. Nine links
are needed end to end. Six exist.

| # | link | state | evidence |
|---|---|---|---|
| 1 | user records a policy | ✅ | `src/tree_design/store.py:248` `set_shared_material_policy` |
| 2 | freeze resolves it to a VALUE | ✅ | `src/tree_design/freeze.py:265-274`, `:334` |
| 3 | P11 refuses a tree without one | ✅ | `src/placement/index.py:143-148` |
| 4 | something branches on WHICH policy | ✅ **(landed mid-audit)** | `src/placement/groups.py:64-66` `_BRANCH_BEARING`, `:261` |
| 5 | never returns a competing institution | ✅ **(landed mid-audit)** | `src/placement/groups.py:232-272` `resolve_multi_home` |
| 6 | **a `shared-material` node can be created** | ❌ | no assignment of `node_role=SHARED_MATERIAL` anywhere in `src/` |
| 7 | **something calls `resolve_multi_home`** | ❌ | zero callers in `src/` |
| 8 | `shared-material decision` is emitted | ❌ | `src/placement/vocabulary.py:148`, referenced by no other module |
| 9 | a `PlacementDecision` / `Ask` is written | ❌ | `PlacementDecision(` appears once in `src/`, at `store.py:75`, which REHYDRATES; `Ask(` has no constructor |

**Link 6 is the one that matters and it is not a plumbing detail.** `_BRANCH_BEARING` —
`shared-branch`, `primary-home`, `reference-or-alias` — only places when a `shared_branch_node_id` is
supplied. Nothing in the tree designer can mint one: `materialise.py:383` writes `ORDINARY`,
`candidates.py:179` writes `ORDINARY`, `residuals.py:243,274` write `RESIDUAL`, and there is no
fourth writer. `BRANCH_ACTIONS` contains `add-scoped-general` and `set-shared-material-policy` but no
`add-shared-branch`.

> **Consequence for a real person:** a user who reads the four options and chooses "shared branch"
> gets `mandatory-review`. Three of the four settings collapse onto the fourth, silently.

`node_role=SCOPED_GENERAL` has **no producer either** — so §5.9's scoped `General` branch (case F1,
the commonest ambiguity on any disk) also cannot be created, and the "global catch-all folder should
not become the product's default answer to ambiguity" line has nothing enforcing it.

Two further defects found by running the real code:

* **The §6.9 gate sits one stage too late.** `validate_for_freeze` (`freeze.py:114`) checks four
  things and the shared-material policy is not one of them; `_shared_material` returns `None` rather
  than refusing. So the tree freezes cleanly and `build_destination_index` refuses at the next stage
  with a contract error about a policy the user was never asked to choose.
  Test: `test_a_tree_freezes_with_no_shared_material_policy_and_placement_then_refuses`.
* **`node_role` reaches the index and no scorer reads it.** `IndexEntry.node_role` is populated at
  `index.py:109`; `scoring.py`'s `_CHANNEL_WEIGHT` scores channels and `shared-material` is not a
  channel. So a shared branch reached through `accepted_group` (weight 2) ranks **below** the two
  institution branches reached through `direct_fact` (weight 3) — the one node §6.9 names is ranked
  below the two nodes §6.9 forbids choosing between.
  Test: `test_two_packets_claim_one_transcript_and_the_shared_branch_ranks_last`.

**Case A5/§6.9's own transcript, run end to end** (`test_the_transcript_abstains_but_names_the_wrong_reason_and_asks_nothing`):
the outcome is correct — `meets_margin == false`, `requires_review == true`, nothing moves. The
account of it is wrong: `abstention_reason == "low_margin"`, not `no_shared_branch`;
`confidence_class == "abstain: no supported destination"`, not `shared-material decision`. The user
is told "the two best destinations were too close together" — a scoring complaint — instead of "this
file belongs to two of your packets; which is its home?"

### 2. Protected ∩ workflow (cases E1–E5) — **BROKEN, and this is the worst finding**

**V5 refuses a whole branch because one file under it is protected.**

`materialise_branch` fills `handling_classes_by_value` with the union of the handling classes of
**every member contributing that value** (`materialise.py:157-166`). V5 (`validation.py:168-201`)
then refuses any folder level whose value carries a protected class. So a passport inside the
UChicago packet gives the VALUE `"UChicago"` — an institution name, not sensitive at all — the
passport's `highly_sensitive_credential_bearing`, and the level is refused. `run_checks` collects the
failure and `project_branch_nodes` raises `MaterialisationRefused`.

Run in `test_one_passport_in_a_visa_packet_refuses_the_whole_branch`, with a second institution
present so V2 cannot be the cause:

* `level.values == ("Rice", "UChicago")`
* `handling_classes_by_value["UChicago"]` carries the protected class; `["Rice"]` does not
* failures == `["V5"]`, affected == `("UChicago",)`
* `project_branch_nodes` raises — **and Rice is gone too.** V5 is a per-value finding with a
  per-branch consequence.

The control (`test_removing_the_passport_restores_the_branch_which_is_the_whole_problem`) builds the
identical branch from the identical files minus the passport and gets `["Rice", "UChicago"]`.

> **Consequence for a real person:** "I need my passport for this application" is answered with "then
> you may not have this application folder." Every case in class E hits this. The two workarounds are
> both losses — mark the level metadata-only and get no institution folders at all (§5.4), or keep
> the passport out of the packet and lose the packet's completeness.

The corpus says the opposite in terms: *"both schemas may remain active on disjoint evidence and the
identity safety gate runs before any academic placement"*, *"protection remains first whichever group
holds it"*. Protection running FIRST means the passport is isolated and the branch is built.
Protection running INSTEAD means the branch is refused. The product does the second.

**What does work.** The standing rule about protected containers is honoured where it is wired.
`protected_area_nodes` (`candidates.py:124`) produces a `node_type=protected` node with
`accepts_placement=False`, an explanation naming what was not done, and no
`protected_movement_permitted` parameter at all. **This changed during the audit:** the producer had
no caller when this pass began — a marked area was pruned by the scan and then absent from the tree,
which is silent omission. `freeze.represent_protected_areas` is now that caller and
`validate_for_freeze` refuses a version in which a marked area has no node. Verified in
`test_a_protected_area_is_marked_and_counted_and_the_producer_is_wired` (that test's assertion was
inverted mid-audit to match).

### 3. One file, two domains (cases A1–A5) — **BROKEN at the tree, PARTIAL at placement**

**C6 refuses any branch spanning two schemas.** `routing.py:292-305` compares each accepted group's
single `domain` against the schemas of the rows being evaluated and refuses on any dropped member.
C6 is in `NON_OVERRIDABLE_GATES`, so no user gesture clears it. Two single-schema recipes are
evaluated independently, so each drops the other's files and both refuse: the branch produces **no
composition at all** and the user gets the no-split option.
Test: `test_a_branch_holding_two_domains_is_refused_by_every_single_schema_recipe`.

**The escape exists and is unreachable.** One `TemplateDefinition` with a `TemplateApplicability` row
in each schema covers both and clears C6 — verified in
`test_the_cross_domain_escape_exists_and_needs_a_catalogue_that_does_not`. But `load_catalogue`
(`catalogue.py:117`) reads a compiled manifest, **no such manifest exists in this repository, and
`load_catalogue` has no caller in `src/`**. Zero of the 358 corpus rows reach runtime. Every
cross-domain recipe the 277 cross-schema `also_holds_with` edges would justify is a recipe nobody has
compiled.

**A group the categoriser could not label is refused too** (case F2). `AcceptedGroup.domain` is
`str | None` and C6 tests `if group.domain in schemas`; `None` is in no schema set, so an accepted,
coherent, labelled group whose category never resolved drops all its files and refuses every recipe.
P9's schema permits exactly this (`grouping/schema.py:56-59` forces the NULL only when the group is
NOT coherent). Test: `test_a_group_the_engine_could_not_categorise_is_refused_by_c6`.

### 4. Opposite side of the table (cases B1–B5) — **BROKEN**

**No destination-eligible field expresses which side of the table you are on.** §3.8's role
separation is real in the catalogue — `authored_by`, `our_firm`, `target_school`, `client` — but D9
makes the two authorship-side roles `destination_eligible = False` (`facts/fields.py:27-32`). What
survives as a folder dimension is the COUNTERPARTY, which is the same value on both sides.

The 24 destination-eligible fields, enumerated in
`test_no_destination_field_expresses_which_side_of_the_table_you_are_on`, contain no `direction`, no
`party_role`, no `counterparty_role`, no `issued_or_received`.

So the user's only way to build both folders is to give them the same expected value — and then
retrieval matches both on `direct_fact`, the scores are identical, the margin is zero, and **every
such file abstains**. Verified end to end in
`test_two_opposite_side_folders_tie_and_every_such_file_abstains`: `support_score` equal,
`margin_over_next == 0.0`, `abstention_reason == low_margin`.

> **Consequence for a real person:** the sole trader who builds `Invoices/Sent` and
> `Invoices/Received` has made the product **worse** at deciding than a single `Invoices` folder
> would have been. B1's privacy consequence is sharper: nothing structural stops a candidate's résumé
> landing in the holder's own job-search branch, which is what
> `career.employer-side-hiring`'s privacy rules exist to prevent.

`people` and `instructor` are also destination-ineligible, which is why case C4 (two children,
structurally identical records) has no dimension to split on either.

### 5. The multi-valued file (cases A4, A5, D1–D3) — **BROKEN, and it is where co-activation dies**

P6 gets this exactly right. `facts/domains.py:20`: *"**Activation adds; it never chooses.**
`active_domains` returns a set, not a winner. No domain suppresses another, no field is dropped, and
nothing here ranks."* §3.11's worked example is preserved at the fact layer.

Then it is thrown away, twice:

* **At the group boundary.** `AcceptedGroup.domain` is one `str | None` — P9's `group_category`,
  which resolution M12 made a single field. One group, one domain. (A file may still be in several
  groups; `memberships` has no unique index.)
* **At the fact-value boundary.** `preferred_fact` (`facts/supersede.py:180-209`) returns `None` when
  a file holds two simultaneous live values for one field. That is correct — OQ6 is open and a reader
  that picked one would close it — but `preferred_value_for` carries the `None` through and
  `materialise_branch` therefore gives the file **no branch at all**.

**And the screen does not say so.** `vertical_options` computes the unresolved list the user reads
from `candidate.covered_file_ids` (`candidates.py:392-395`) — C6's group-coverage set — and never
reads `evidence.unresolved_by_field`. Since C6 already refused any candidate that dropped a member,
that list is empty for every surviving option.

Verified in `test_a_file_pulled_two_ways_gets_no_branch_and_appears_in_no_unresolved_line`: the
engine records the file in `unresolved_by_field`, the file is in no value's member set, and
`option.unresolved_file_ids == ()`.

> **Consequence for a real person:** the file two branches both wanted gets no folder AND is reported
> as nothing. §5.5's promise — "the resulting number of child branches, the number of files under
> each child, example members, **unresolved files**, and any evidence gaps" — is not kept for the
> unresolved half.

Two further hard-wired blanks at the same call site (`candidates.py:350-351`):
`evidence_gaps_by_node={}` and `sensitive_node_ids=frozenset()`. So `BranchCounts.evidence_gap_file_ids`
is always empty and `BranchCounts.sensitive_isolated` is always `False` — §5.11's "where sensitive
material has been isolated" reports nothing, ever.

### 6. Breadth across the 23 schemas — **BROKEN for 13 of them**

P6 recognises **10** schema ids (`facts/domains.py:51-53`); the corpus carries **23**. The thirteen
with no runtime identity at all are the professional half:

`business_operations`, `clinical_practice`, `construction_property`, `creative`, `engineering`,
`government`, `hr`, `law_practice`, `logistics`, `manufacturing`, `nonprofit`, `resource_operations`,
`retail_hospitality`.

A group categorised as any of those has no applicability row, so **C3 refuses before C6 is even
reached**. `law_practice` alone holds 37 rows and 45 cross-schema `also_holds_with` edges — every
case in classes C5 and D3 is in this set.

Four of the ten that ARE recognised carry no fields at all (`career`, `identity`, `medical`,
`legal`), so they can be activated and still build nothing. **Two of those four are exactly the
schemas class E needs**: identity and medical are `FIELD_LESS_SCHEMA_IDS`, so an identity document
activates a schema that can express nothing about it.

> **Consequence for a real person:** a lawyer, an engineer, a nurse, a builder or a shopkeeper cannot
> be grouped at all. The product currently addresses a student, a researcher, a job-seeker, a
> photographer and a developer.

### 7. Where the design is right and the code follows it

Recorded honestly, because not everything is broken:

* **§6.3's suppression is real and recorded.** A direct `target_university = Duke` suppresses the
  Columbia node and the suppression reaches `conflicts_considered` (`retrieval.py:100-113`) — the
  review surface can show what was ruled out and why.
* **§6.10's two conditions genuinely abstain.** Every ambiguity case above ends in abstention rather
  than a guess. "Correct abstention is a successful outcome" is honoured.
* **§6.6's deterministic path keys uniqueness on the FACTS, not the candidate count**
  (`scoring.py:159-171`), so two direct matches are never a unique match.
* **§6.9's prohibition is implemented structurally, not asserted.** `resolve_multi_home` has no code
  path that returns a member of `candidate_node_ids`, and it refuses a `shared_branch_node_id` that
  is one of the competing homes. That is the right way to build this rule.
* **The protected-area rule is now honoured end to end** (§2 above).
* **Multi-valued facts survive into P11's retrieval.** `retrieve` keys on `(field, value)` pairs, so
  a file carrying two institutions retrieves both nodes rather than neither. P11 is more faithful to
  §3.11 than P10 is.

---

## Ranked: what breaks for a real person

Ordered by *how badly it hurts × how many people hit it*.

**1. A protected file destroys the branch that needs it.** (§2, class E)
Passport in a visa packet, medical letter in an accommodations file, divorce decree in a mortgage
bundle: V5 refuses the whole composition. This is the sharpest class in the case set and the product
fails it in the most damaging possible direction — the user loses the organisation, not the
protection. `validation.py:168-201` + `materialise.py:157-166`.
*Fix shape:* V5 should refuse a level whose **value string** is protected material, not one whose
members include a protected file. A file's class belongs to the file, and §5.11's "where sensitive
material has been isolated" is the mechanism for the file — isolate it and build the branch.

**2. Thirteen of twenty-three schemas do not exist at runtime.** (§6)
Every professional persona is unserved, and they hold most of the cross-schema overlap. No amount of
fixing the ambiguity machinery helps a lawyer whose groups cannot be categorised.
`facts/domains.py:51-53`.

**3. The shared branch three of the four §6.9 policies need cannot be created.** (§1, link 6)
`shared-branch`, `primary-home` and `reference-or-alias` all silently degrade to `mandatory-review`.
`scoped-general` is in the same state, so §5.9's answer to the commonest ambiguity of all is
unavailable too. No `node_role=SHARED_MATERIAL` or `SCOPED_GENERAL` writer in `src/`.

**4. A file two branches both want vanishes with no trace on screen.** (§5)
It gets no folder, and the unresolved list the user reads is computed from a different set that
cannot contain it. `candidates.py:392-395` should read `evidence.unresolved_by_field`.
Same call site: `evidence_gaps_by_node` and `sensitive_node_ids` are hard-wired empty
(`candidates.py:350-351`).

**5. Opposite sides of the table are indistinguishable, and building both folders makes it worse.**
(§4) Every invoice, every NDA, every lease, every résumé abstains. The privacy consequence in B1 —
another person's data in the holder's own branch — is the one the corpus flags as "not cosmetic".
Needs a destination-eligible role/direction field; §3.8 already argues for the separation and D9
closed the only door to it.

**6. A branch that spans two domains produces no composition at all.** (§3)
C6 is non-overridable, the cross-domain escape requires a compiled catalogue that does not exist, and
`load_catalogue` has no caller in `src/`.

**7. The transcript abstains for the wrong reason and asks nothing.** (§1)
Right outcome, wrong account. `low_margin` instead of `no_shared_branch`; no `Ask`; no
`shared-material decision`. `resolve_multi_home` has no caller and no `PlacementDecision` is ever
constructed, so nothing can carry the answer even once it is computed.

**8. Freeze succeeds without the §6.9 policy and placement refuses afterwards.** (§1)
The user is never asked the question, and finds out at the wrong stage.
`validate_for_freeze` should require it.

**9. An accepted group with no domain is refused by every recipe.** (§3)
And the multi-domain groups are precisely the ones a categoriser fails on, so this compounds every
case above.

---

## Where this document is wrong about the design

Two places where the design, not the code, looks wrong to me:

**§6.9 assumes the shared material is factually neutral.** Its worked example is a transcript that
"contains **no institution-specific fact**". The commoner and harder shape is the file that carries
*both* institutions — an accepted membership in each packet wrote an addressee each. §6.9 has no
answer for that file: it is not neutral shared material, it is doubly-claimed material, and
"abstain or ask" is the only outcome the section permits. A `reference-or-alias` convention would
serve it, but §6.9 never says which policy applies when.

**D9 closed the door §3.8 opened.** §3.8 says "The system must separate roles that happen to contain
the same entity type" and the corpus builds 79 `role_split` rows on that sentence. D9 then made both
authorship-side roles destination-ineligible on the strength of a *different* §3.8 sentence ("avoid
using authorship or creator identity as a destination dimension"). Those are not the same rule. "Do
not build a folder per author" is right; "you may never express whose side of a contract this is" is
its casualty, and class B is the whole cost.

---

## Executable companion

`tests/integration/test_ambiguity_cases.py` — 17 tests, all passing at the timestamp above; the whole suite was green with them in it (`4270 passed, 1 xfailed`).

**Line numbers in this document drift.** `src/tree_design/` and `src/placement/` were being edited throughout this audit; every citation was re-verified at the timestamp above, and the tests are the durable evidence because they bind to symbols rather than to lines.

Several assert the presence of a defect (no producer, no caller, empty list). Those are written to
fail loudly the day someone fixes the thing they describe — that failure is the signal, and the test
should be deleted or inverted deliberately at that point, as
`test_a_protected_area_is_marked_and_counted_and_the_producer_is_wired` already was during this
audit.

Cases **not** executed, and why:

* **A1–A3, B2, B4, C2–C5, D2–D4, E2–E5** — the mechanisms they would exercise (a cross-domain
  compiled catalogue, a `shared-material` node, a role/direction field, thirteen schema ids) do not
  exist. There is nothing to drive. Stubbing one would test the stub.
* **The full §6.9 flow** — `resolve_multi_home` is exercised by `tests/p11/test_p11_groups.py`
  against hand-supplied arguments; there is no caller to drive it from a file, so no integration test
  can reach it.
