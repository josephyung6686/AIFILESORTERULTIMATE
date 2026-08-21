# P7 — Privacy and consent gate — PLAN, Tasks 20–22

> This file is one section of P7's implementation plan. Tasks 1–19 are written by other authors
> against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything they publish is consumed here
> under the names the skeleton's `Interfaces:` blocks fix. Tasks 15 and 16 are in
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md) and this file follows its voice, its depth and its
> format. The format standard behind both is [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md).

**Verified against the live substrate, 2026-08-22.** Every signature quoted below was read with
`inspect.signature` against the shipped packages, and every design quotation was `grep`-ed against
[`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md) before it
was written down. Four fabricated quotations were found and removed from these plans this week; the
mechanism that produced them was quoting from memory, so nothing here is quoted from memory. The
facts that most change what these three tasks say:

- `orchestrator.run_wave2` takes **eighteen parameters** and none of them is a gate, a policy or a
  classifier. The signature, read live:

  ```text
  run_wave2(conn, selection_id, *, source, mime_type_for, scan_state, budget_exhausted,
            detect_format, policy, readers, sink, now, context_window, no_usable_facts,
            transcription_authorized, corpus_form, policy_settings, file_entry_body) -> Wave2
  ```

  `policy` there is P5's `SafetyPolicy` — `is_protected_container` and `is_dataless` — and **not**
  P7's `Policy`. Two different words one parameter apart, which is the defect class this project has
  paid for most. Task 22 names both in the same test so the two cannot be conflated later.
- `src/orchestrator.py:402` passes **literal `None`** for `bundle_file_entry.handling_class`, with
  the comment *"The honest value is None because the class is unknown, not because another column
  happened to be empty."* Task 22 asserts that literal stays, and says why below.
- `database_agent.files_table.record_file(..., materialized: bool, content_hash: str | None = None)`
  accepts an explicit content hash. That is what makes Task 20's replay possible at all: a fixture
  seeded at P4's own content hash reproduces P4's own `observation_key`, so the published fixtures
  and the replayed ones address the same evidence.
- `evidence_shape.fixtures.FIXTURES` holds **nineteen** worked examples; `Observation` carries
  `observation_key` as an attribute, already computed. Fixture 8 is an OCR region — a 43-character
  text unit with an observation spanning `0-24` — and fixture 18 carries `completeness =
  "unreadable"`. Those two are the substrate Task 20's excerpt and unreadable fixtures resolve
  against, so P7 invents no evidence of its own.

---

## Three rulings that bind this section, applied rather than restated

**D2 (ratified) inverts one of Task 21's guards, and this is the whole reason Task 21 is dangerous
to write from the skeleton alone.** The skeleton's §5 says *"Every open question stays open … Each is
held by a guard in Task 21 that names it and fails the moment someone answers it"* — and its §4 says
the opposite about one of them: **P6 OQ11 is CLOSED.** A guard asserting OQ11 is open fails the day
this plan is executed, which is the day D2 is applied. Task 21 asserts the **D2 shape** instead:
`ClassificationRecord` keyed `(file_id, content_hash)` is authoritative, `files.sensitivity_state` is
its projection written through P1's **`set_sensitivity_state`** (which now exists, and P7 takes no
writer protocol), `src/privacy/` issues **no `UPDATE files`** of its own, and `unclassified` never
reaches that column because it is a **gate outcome, not a file fact**.

**The detector is unwritten (D2), so `Denied(unclassified)` is the ordinary path on a real corpus.**
No task in any plan produces a rule set. Task 20's fixtures 2 and 15 are built for that, and Task
22's skeleton step says it in a named test rather than in a report nobody rereads: the walking
skeleton proves **the door**, not the classification. A P7 that is done and a product that classifies
files are different claims and only the first is deliverable here.

**P7 never reaches the bundle, and its own Open question 8 is why.** OQ8: *"May a replay bundle carry
audit records and excerpt spans? §8.5 allows 'a frozen corpus snapshot or a metadata-safe
representation of one' and lists 'policy settings'. Whether a bundle intended to leave the user's
machine may carry audit records — which name excerpts — is unstated."* So
`bundle_file_entry.handling_class` is the **Wave-2 caller's** field, not P7's, and the caller passes
literal `None` today. Task 22 asserts the `None` stays and asserts P7 wrote it nothing — the opposite
of what the skeleton's *"What P7 consumes from P2"* paragraph expects, and the reason is written out
in Task 22 rather than left as a disagreement between two documents.

---

## Three contradictions between skeleton blocks, resolved here and reported

Each is a place where two `Interfaces:` blocks name the same object and only one can own it. They are
resolved the way `PLAN-tasks-15-16.md` resolved the `facts_seam` → `classification_store` rename: pick
the one the File Structure supports, apply it, and say so.

1. **`NeedsConsent` is produced by both Task 11 and Task 14.** Task 11's `Produces` lists `Released`,
   `Denied`, `NeedsConsent`; Task 14's lists `NeedsConsent (consent_request_id, requirement,
   options)`. The File Structure gives `release.py` *"Gate.release — the request, the three branches,
   the ordering"* and gives `consent.py` *"NeedsConsent, the consent_request_id, the P13 seam"*. Two
   definitions of one branch type is exactly the duplication that makes a caller's `isinstance` check
   silently false. **The three branch dataclasses are defined in `release.py`; `consent.py` imports
   `NeedsConsent` and owns its lifecycle** (`open_consent_request`, `record_consent_choice`,
   `pending_consent`). Tasks 20 and 22 import all three branch types from `privacy.release`.
   Reported.
2. **Four of the six item kinds have no published field list.** SPEC §4 gives shapes for `excerpt`
   (`{ observation_key, span, reason }`) and `redacted_identifier`
   (`{ observation_key, span, identifier_class }`) and prose for the other four. Task 7 must publish
   them and Task 20 cannot be written without them, so they are pinned here:
   `CandidateLabel(label)`, `MetadataField(name)`, `EvidenceReference(observation_key)`,
   `Filename(file_id)`. The load-bearing one is `MetadataField(name)` and **not**
   `MetadataField(name, value)`: SPEC §6 says requests *"carry references, never materialised
   content"*, so a request naming a metadata field names it and the gate resolves it.
   `CandidateLabel` is the single exception and it is the SPEC's, not this plan's — §8.4's releasable
   list contains *"candidate labels"*, and a label is a name the local database already holds
   (§4.5, §5.4), not a span of a file. Reported.
3. **`ConsentRequirement` has no published shape.** SPEC §6 says only *"requirement — which items
   require sensitive text, and why"*. Pinned as `ConsentRequirement(items: tuple[str, ...],
   why: str)`, `items` holding P4 `observation_key` values (M14, never `observation_id`). Task 14
   must publish that. Reported.

---

## Tasks

### Task 20: The published fixtures (SPEC §11)

**Files:**
- Create: `src/privacy/fixtures.py`
- Test: `tests/p7/test_p7_fixtures.py`

**Interfaces:**
- Consumes: `privacy.release.ModelCallRequest`, `.ModelTarget`, `.Target`, `.Released`, `.Denied`,
  `.NeedsConsent`, `.Gate`; `privacy.items.Excerpt`, `.RedactedIdentifier`, `.CandidateLabel`,
  `.MetadataField`, `.EvidenceReference`, `.Filename`; `privacy.redaction.RedactionEntry`;
  `privacy.consent.ConsentRequirement`; `privacy.audit.AuditRecord`, `.AUDIT_FIELDS`;
  `privacy.policy.Policy`; `privacy.classification.ClassificationRecord`;
  `privacy.vocabulary.DENIAL_REASONS`, `.OPERATION_MODES`, `.CONSENT_OPTIONS`, `.HANDLING_CLASSES`;
  `privacy.denial.PROTECTED_RECORDS_TEMPLATE`; `evidence_shape.location.TextSpan`;
  `evidence_shape.fixtures.FIXTURES` (as `P4_FIXTURES`, for the substrate an excerpt resolves
  against).
- Produces (`fixtures.py`):
  - `GateFixture` — frozen, eleven fields: `number: int`, `spec_case: str`,
    `policy: Policy`, `classification: ClassificationRecord | None`,
    `area: str | None`, `request: ModelCallRequest`,
    `decision: Released | Denied | NeedsConsent`, `audit_record: AuditRecord`,
    `p4_fixture: int | None`, `downstream_obligation: str | None`, `revoked: bool`.
  - `FIXTURES: tuple[GateFixture, ...]` — sixteen.
  - `FIXTURE_CLOCK: str`, `FIXTURE_AREA: str`, `LOCAL_MODEL`, `CLOUD_MODEL`.
  - `SPEC_11_ITEMS: tuple[str, ...]` — SPEC §11's five *"plus"* items, in the SPEC's own words.
  - `FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]]` — thirteen keys: the eight `Denied.reason`
    values and the five `SPEC_11_ITEMS`.
  - `MODE_SWEEP: Mapping[str, int]` — operation mode → the fixture number that exercises a protected
    file under it.
  - `by_number(n) -> GateFixture`, `UnknownFixture`.

**Done-means:** 11 (first clause; the second clause is P8's test run and is named as such).

**One published surface this task pins for Task 11, because the fixtures cannot be replayed without
it.** `Gate` takes a **required keyword** `area_of: Callable[[str], str | None]` with **no default**.
SPEC Open question 3 — *"What is a 'corpus area'? … Consent grants cannot be scoped until this is
named"* — is unanswered, so a gate that resolved a file to an area would be answering it in code.
This is the identical discipline Task 15 applied to `files_in_scope` for the identical question, and
the skeleton's own negative-test table already anticipates it: *"Open question 3 leaves the area
undefined, so the test parameterises the scope."* Reported as a pin on Task 11.

**Five fields this task adds to the skeleton's `GateFixture`. Done-means 11 turns entirely on
replayability, and six fields cannot be replayed.** The skeleton's `Produces` lists `number`,
`spec_case`, `request`, `decision`, `audit_record`, `policy`.

1. **`classification`.** D2 makes `ClassificationRecord` P7's own authoritative record and the gate's
   second input. A fixture that carries a request and a policy but no classification cannot be
   replayed, because the gate would resolve every one of them to `Denied(unclassified)` and fifteen
   of the sixteen expected decisions would be wrong. `None` is a legitimate value and fixture 2 is
   the fixture where it is the point.
2. **`p4_fixture`.** The skeleton's own `Consumes` block already anticipates it —
   *"`evidence_shape.fixtures.FIXTURES` (for the P4 substrate a fixture excerpt resolves against)"* —
   and this is the field that names which of P4's nineteen. Naming the number rather than copying the
   observation is what keeps the two in lockstep: `observation_key` is derived from
   `(content_hash, extractor_name, locator, raw_value)`, so a P4 fixture that changes changes P7's
   key with it and the replay still resolves. A copied key would rot silently.
3. **`downstream_obligation`.** SPEC §11's last paragraph puts an obligation on P8 for exactly two of
   these fixtures. Carrying the sentence in the record rather than in a comment is what lets P8 read
   it; a comment in P7's source is not a contract P8 can consume.
4. **`area`.** Open question 3's parameter, carried as **data** rather than as a rule. `Gate` takes
   the resolver; the fixture supplies the answer. P7 still defines no area and Task 21 asserts it.
5. **`revoked`.** `policy_revoked` means a grant **existed and was withdrawn**. A fixture whose
   policy simply never carried the grant would be testing *never permitted*, which is a different
   denial with a different remedy. Task 5's `revoke_consent` is what the seeding step calls.

Reported as five additions.

**The sixteen fixtures are SPEC §11's list item for item, and two pairs look like duplicates until
you read what they differ on.** §11: *"Request → decision pairs, one per `Denied.reason`, plus: a
clean `Released` with redaction applied; a `NeedsConsent` returning all four options; a protected
file under each of the four modes; an `unreadable_unclassified` file; a `Protected Records` residual
request."* Eight plus five items, sixteen fixtures, because *"a protected file under each of the four
modes"* is four.

- **Fixture 2 (`unclassified`) and fixture 15 (an `unreadable_unclassified` file) are not the same
  fixture.** Fixture 2 has **no `ClassificationRecord` at all** — nothing has looked. Fixture 15 has
  one, and its `handling_class` **is** `unreadable_unclassified` — something looked and could not
  read it, which is §2.9's indexed-but-unreadable case and P4's fixture 18 (`completeness =
  "unreadable"`). Both deny with reason `unclassified`, and the distinction between them is D2's
  third clause: *"nothing has looked"* can never be read as *"this file carries nothing"*. A fixture
  set that collapsed them would delete the distinction D2 exists to protect.
- **Fixture 4 and fixture 16 are the two halves of one sentence.** §7.3: `Protected Records`
  *"must not cause filenames or content to be exposed in model prompts"*. Fixture 4 requests an
  `Excerpt` — the content half. Fixture 16 requests a `Filename` — the filename half, and the one
  §4's flagged reading of Open question 2 makes reachable at all.
- **Fixtures 1 and 13 differ on the item, not the mode.** Both are a protected file with a cloud
  target under `hybrid`. Fixture 1 asks for an `Excerpt`; fixture 13 asks for a `MetadataField`. That
  is the assertion that §8.4's protected rule is about **the prompt**, not about how innocuous the
  requested item is — *"Protected material should not be included in cloud-model prompts by
  default"* names no item kind.

**One precedence rule this task pins for Task 13, because the mode sweep cannot be written without
it.** A protected file with a cloud target under `offline` satisfies two denial reasons at once.
**Mode is evaluated first**, so fixtures 11 and 12 are `mode_forbids_target` and fixtures 13 and 14
are `protected_cloud_target`. The reason is §8.4's opening sentence — *"Privacy policy must be
enforced before content reaches any model or external connector"* — read with §8.4's mode table:
under `offline`, *"No content leaves the device"* for **any** file, so the mode answer is the more
general and the more truthful one. Telling a user their passport was blocked because it is a passport
when it would have been blocked anyway is a false explanation, and §8.6 requires the UI to show
*"what has been deferred, and why"*. Reported as a pin on Task 13.

**Every fixture is replayed through the real gate and compared field for field, and that is the
substance of the task.** SPEC §11's second sentence — *"Each fixture carries the audit record the
gate would have appended"* — is satisfiable two ways, and one of them is a trap: a hand-written audit
record is a second implementation of the gate that drifts from the first, and the drift is invisible
because both sides are P7's. So `tests/p7/test_p7_fixtures.py` seeds a real database from the
fixture, calls the real `Gate`, and compares. **`file_id` is the only substituted field**, because
`record_file` accepts an explicit `content_hash` and every `observation_key` is derived from the
content hash rather than the file id. The substituted and minted field names are published in the
test as two small frozen sets, so the ignore-list cannot quietly grow.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_fixtures.py
"""Done-means 11's first clause, and its second clause named as P8's rather than faked.

SPEC §11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean
`Released` with redaction applied; a `NeedsConsent` returning all four options; a
protected file under each of the four modes; an `unreadable_unclassified` file; a
`Protected Records` residual request. Each fixture carries the audit record the gate
would have appended."

The second sentence is what makes this worth doing and what makes it hard. A fixture
carrying a HAND-WRITTEN audit record is a second implementation of the gate, and it
drifts from the first invisibly because both sides belong to P7. So every fixture here
is replayed through the real gate against a real database and compared field for
field, and only the identity fields a replay cannot preserve are excused -- by name,
in a frozen set, so the excuse list cannot grow quietly.
"""
import dataclasses

import pytest

from database_agent.files_table import record_file

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.store import record_observation, record_run, record_text_unit

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.classification_store import ClassificationStore
from privacy.fixtures import (
    FIXTURE_CLOCK, FIXTURE_COVERAGE, FIXTURES, GateFixture, MODE_SWEEP, SPEC_11_ITEMS,
    UnknownFixture, by_number,
)
from privacy.gate import Gate
from privacy.policy import revoke_consent, set_policy
from privacy.release import Denied, NeedsConsent, Released, Target
from privacy.vocabulary import (
    CONSENT_OPTIONS, DENIAL_REASONS, HANDLING_CLASSES, OPERATION_MODES,
)

COMPONENT = "0.1.0"

#: The only field a replay cannot preserve. `record_file` mints the id; everything
#: else -- content hash, observation key, locator -- is content-addressed and survives.
SUBSTITUTED_FIELDS = frozenset({"file_id", "file_ids"})

#: Minted by the gate at call time, so a fixture can carry an example and never the
#: value. `audit_id` is P1's `lastrowid`; the other two are P7's own ids.
MINTED_FIELDS = frozenset({"audit_id", "release_id", "consent_request_id",
                           "appended_at"})


def p4(number: int):
    found = [f for f in P4_FIXTURES if f.number == number]
    assert found, f"P4 fixture {number} does not exist"
    return found[0]


def seed(conn, fixture, tmp_path) -> str:
    """A real `files` row, a real P4 substrate, a real policy, a real classification.

    Nothing here is synthesized past P1's own writer. `record_file` takes an explicit
    `content_hash` with `materialized=False`, which is what lets the row carry P4's
    fixture hash -- and therefore what makes the seeded `observation_key` identical to
    the published one. Without that, every excerpt in every fixture would address an
    observation the replay had not written.
    """
    source = p4(fixture.p4_fixture) if fixture.p4_fixture is not None else None
    content_hash = (source.run.content_hash if source is not None
                    else fixture.request.target.file_ids[0])
    corpus = tmp_path / f"corpus-{fixture.number}"
    corpus.mkdir(parents=True, exist_ok=True)
    document = corpus / "fixture-document.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size, observed_timestamps='{"mtime": 1.0}',
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=False,
        content_hash=content_hash)

    if source is not None:
        run = dataclasses.replace(source.run, file_id=file_id)
        record_run(conn, run)
        for unit in source.text_units:
            record_text_unit(conn, unit)
        for observation in source.observations:
            record_observation(conn, dataclasses.replace(observation, file_id=file_id))

    set_policy(conn, fixture.policy, author="P7", component_version=COMPONENT,
               user_id="joseph")
    if fixture.revoked:
        # Task 5's `revoke_consent` records the withdrawal and mints a new
        # `policy_version`; it appends no event (Task 15 owns that append). It is what
        # makes `policy_revoked` distinguishable from "never granted", which is the
        # whole content of that denial reason.
        revoke_consent(conn, fixture.policy, fixture.area, user_id="joseph",
                       component_version=COMPONENT, observed_at=FIXTURE_CLOCK)
    if fixture.classification is not None:
        ClassificationStore(conn).write(
            dataclasses.replace(fixture.classification, file_id=file_id,
                                content_hash=content_hash))
    return file_id


def replay(conn, fixture, tmp_path):
    """Run the fixture's own request through the real gate and return the decision."""
    file_id = seed(conn, fixture, tmp_path)
    request = dataclasses.replace(
        fixture.request,
        target=Target(file_ids=(file_id,), group_id=fixture.request.target.group_id))
    # `area_of` has no default. SPEC Open question 3 -- "What is a 'corpus area'? ...
    # Consent grants cannot be scoped until this is named" -- is unanswered, so the
    # resolver is the caller's and the fixture carries the answer as data.
    gate = Gate(conn, component_version=COMPONENT,
                area_of=lambda _file_id: fixture.area)
    return gate.release(request), file_id


# --- SPEC §11's list, item for item -----------------------------------------

def test_the_coverage_map_names_every_spec_11_item_and_nothing_else():
    # The test that fails if a list member has no fixture, which is the only thing
    # standing between "sixteen fixtures" and "the sixteen the SPEC asked for".
    assert set(FIXTURE_COVERAGE) == set(DENIAL_REASONS) | set(SPEC_11_ITEMS)
    for item, numbers in FIXTURE_COVERAGE.items():
        assert numbers, item
        for number in numbers:
            assert by_number(number)


def test_the_five_plus_items_carry_the_specs_own_words():
    # A paraphrase here is a failing test and not an editorial choice: SPEC_11_ITEMS is
    # the checklist, and a checklist rewritten in the author's words no longer checks
    # the document it came from.
    assert SPEC_11_ITEMS == (
        "a clean `Released` with redaction applied",
        "a `NeedsConsent` returning all four options",
        "a protected file under each of the four modes",
        "an `unreadable_unclassified` file",
        "a `Protected Records` residual request",
    )


def test_there_is_one_fixture_per_denial_reason():
    for reason in DENIAL_REASONS:
        reached = [f for f in FIXTURES
                   if isinstance(f.decision, Denied) and f.decision.reason == reason]
        assert reached, reason


def test_the_denial_reasons_are_all_eight_and_no_ninth():
    reasons = {f.decision.reason for f in FIXTURES if isinstance(f.decision, Denied)}
    assert reasons == set(DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8


def test_fixture_numbers_are_dense_unique_and_sixteen():
    numbers = [f.number for f in FIXTURES]
    assert numbers == list(range(1, 17))


def test_by_number_raises_on_a_number_nobody_published():
    assert by_number(1).number == 1
    with pytest.raises(UnknownFixture):
        by_number(99)


def test_the_gate_fixture_publishes_eleven_named_fields():
    # Six are the skeleton's. Five are added by this task and every one of them is
    # either a held-open question the fixture answers AS DATA (`area`) or a replay
    # precondition without which "each fixture carries the audit record the gate would
    # have appended" is unfalsifiable (`classification`, `p4_fixture`, `revoked`).
    # `downstream_obligation` carries SPEC §11's own two sentences to P8.
    assert [f.name for f in dataclasses.fields(GateFixture)] == [
        "number", "spec_case", "policy", "classification", "area", "request",
        "decision", "audit_record", "p4_fixture", "downstream_obligation", "revoked"]


def test_exactly_one_fixture_revokes_a_grant_before_the_call():
    # §8.4: the user may "revoke a policy for future runs". `policy_revoked` means a
    # grant EXISTED and was withdrawn; a fixture with no grant to begin with would be
    # testing "never permitted", which is a different denial.
    revoking = {f.number for f in FIXTURES if f.revoked}
    assert revoking == {3}
    fixture = by_number(3)
    assert fixture.decision.reason == "policy_revoked"
    assert fixture.area in dict(fixture.policy.consent_grants)


def test_the_corpus_area_is_carried_as_data_and_never_inferred():
    # Open question 3 stays open: P7 defines no area, so every fixture that needs one
    # states it and the gate takes a resolver with no default. Task 21 asserts
    # `src/privacy/` publishes no corpus-area definition of its own.
    scoped = {f.number: f.area for f in FIXTURES if f.area is not None}
    assert scoped
    assert all(isinstance(area, str) and area for area in scoped.values())
    for fixture in FIXTURES:
        for scope, _option in fixture.policy.consent_grants:
            assert isinstance(scope, str)


def test_no_fixture_invents_a_vocabulary_value():
    for fixture in FIXTURES:
        assert fixture.policy.operation_mode in OPERATION_MODES
        if fixture.classification is not None:
            assert fixture.classification.handling_class in HANDLING_CLASSES
        if isinstance(fixture.decision, Denied):
            assert fixture.decision.reason in DENIAL_REASONS
        if isinstance(fixture.decision, NeedsConsent):
            assert set(fixture.decision.options) == set(CONSENT_OPTIONS)


# --- the two pairs that look like duplicates and are not ---------------------

def test_the_unclassified_fixture_has_no_record_and_the_unreadable_one_does():
    # D2's third clause: `Unreadable or unclassified` is a GATE OUTCOME, not a file
    # fact, so "nothing has looked" and "something looked and could not read it" are
    # two different states that produce one verdict. Collapsing these two fixtures
    # would delete the distinction D2 exists to protect.
    nothing_looked = by_number(2)
    looked_and_failed = by_number(15)
    assert nothing_looked.classification is None
    assert looked_and_failed.classification is not None
    assert looked_and_failed.classification.handling_class == "unreadable_unclassified"
    assert nothing_looked.decision.reason == looked_and_failed.decision.reason == (
        "unclassified")


def test_the_unreadable_fixture_stands_on_p4s_own_unreadable_run():
    # §2.9's indexed-but-unreadable, which P4 fixture 18 carries as
    # `completeness = "unreadable"`. P7 invents no extraction outcome of its own.
    assert by_number(15).p4_fixture == 18
    assert p4(18).run.completeness == "unreadable"


def test_both_halves_of_7_3_are_covered_separately():
    # §7.3: Protected Records "must not cause filenames or content to be exposed in
    # model prompts". Two nouns, two fixtures.
    from privacy.items import Excerpt, Filename
    content_half = by_number(4)
    filename_half = by_number(16)
    assert all(isinstance(item, Excerpt)
               for item in content_half.request.requested_items)
    assert all(isinstance(item, Filename)
               for item in filename_half.request.requested_items)
    assert content_half.decision.reason == "protected_records_template"
    assert filename_half.decision.reason == "protected_records_template"


def test_the_protected_cloud_rule_does_not_depend_on_the_item_kind():
    # §8.4 names no item kind: "Protected material should not be included in
    # cloud-model prompts by default." Fixture 1 asks for an excerpt, fixture 13 for a
    # metadata field, and both are denied for the same reason under the same mode.
    from privacy.items import Excerpt, MetadataField
    assert by_number(1).policy.operation_mode == by_number(13).policy.operation_mode
    assert isinstance(by_number(1).request.requested_items[0], Excerpt)
    assert isinstance(by_number(13).request.requested_items[0], MetadataField)
    assert by_number(1).decision.reason == "protected_cloud_target"
    assert by_number(13).decision.reason == "protected_cloud_target"


# --- the mode sweep ---------------------------------------------------------

def test_a_protected_file_appears_under_each_of_the_four_modes():
    assert set(MODE_SWEEP) == set(OPERATION_MODES)
    for mode, number in MODE_SWEEP.items():
        fixture = by_number(number)
        assert fixture.policy.operation_mode == mode
        assert fixture.classification is not None
        assert fixture.classification.protected is True


def test_mode_is_evaluated_before_protection_so_the_reason_is_the_general_one():
    # The precedence this task pins for Task 13. Under `offline` and `local_model` a
    # cloud target is unreachable for ANY file, so naming the passport as the cause
    # would be a false explanation -- and §8.6 requires the UI to show "what has been
    # deferred, and why". Under `hybrid` and `cloud_assisted` the target IS reachable
    # and the protection is the real cause.
    assert by_number(MODE_SWEEP["offline"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["local_model"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["hybrid"]).decision.reason == "protected_cloud_target"
    assert by_number(
        MODE_SWEEP["cloud_assisted"]).decision.reason == "protected_cloud_target"


def test_the_mode_only_denial_uses_a_non_protected_file():
    # Fixture 8 isolates the mode axis: a `public_low`, unprotected file still cannot
    # reach a cloud target under `offline`. Without this, `mode_forbids_target` would
    # only ever be observed on protected files and the two rules would be untestable
    # apart.
    fixture = by_number(8)
    assert fixture.classification.handling_class == "public_low"
    assert fixture.classification.protected is False
    assert fixture.policy.operation_mode == "offline"
    assert fixture.decision.reason == "mode_forbids_target"


# --- the two non-denial branches --------------------------------------------

def test_the_released_fixture_applied_redaction_and_carries_a_manifest():
    # §11: "a clean `Released` with redaction applied".
    fixture = by_number(9)
    assert isinstance(fixture.decision, Released)
    assert fixture.audit_record.redaction_applied is True
    assert fixture.decision.redaction_manifest
    assert all(entry.identifier_class for entry in fixture.decision.redaction_manifest)


def test_the_needs_consent_fixture_offers_all_four_options_in_the_specs_order():
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use". Four, and a surface that offers three has
    # made the decision for them.
    fixture = by_number(10)
    assert isinstance(fixture.decision, NeedsConsent)
    assert fixture.decision.options == CONSENT_OPTIONS
    assert len(CONSENT_OPTIONS) == 4


def test_the_needs_consent_fixture_has_no_reason_field_to_be_read_as_a_denial():
    # B2: `NeedsConsent` "is never an outcome the caller may absorb". P7's obligation
    # is to make the absorption unrepresentable, and the type-level form of that is
    # the absence of a `reason` field a caller could map onto a denial.
    names = {f.name for f in dataclasses.fields(by_number(10).decision)}
    assert "reason" not in names
    assert names == {"consent_request_id", "requirement", "options"}


# --- the P8 obligations, carried as data rather than as a comment ------------

def test_exactly_two_fixtures_carry_an_obligation_on_p8():
    carriers = {f.number for f in FIXTURES if f.downstream_obligation is not None}
    assert carriers == {6, 10}


def test_the_budget_fixture_says_a_p8_test_that_reaches_it_is_a_p8_failure():
    # SPEC §11, verbatim: a M9 backstop, not a gate result.
    obligation = by_number(6).downstream_obligation
    assert obligation == (
        "so P8 can prove its ladder ran first -- a P8 test that reaches this denial "
        "through the normal path is a P8 failure, not a gate result")
    assert by_number(6).decision.reason == "dossier_over_budget"


def test_the_consent_fixture_says_p8_must_return_the_branch_intact():
    assert by_number(10).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


def test_done_means_11s_second_clause_is_p8s_test_run_and_not_assertable_here():
    # "and P8's harness passes its own tests against those fixtures with P7
    # unimplemented." P8 does not exist. This test exists so the limitation lives in
    # the suite rather than in a report nobody rereads -- the same posture Task 19
    # takes for Done-means 3.
    import importlib
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("llm_harness")
    assert all(f.decision is not None for f in FIXTURES), (
        "the P7 half -- published, replayable request/decision pairs -- is what this "
        "part can deliver; the P8 half is P8's test run")


# --- requests carry references, never content --------------------------------

def test_no_request_carries_materialised_content(p7_conn, tmp_path):
    # SPEC §6: requests "carry references, never materialised content". Asserted over
    # the item records rather than by eye, because a sixth item kind added later would
    # otherwise slip through.
    for fixture in FIXTURES:
        for item in fixture.request.requested_items:
            for field in dataclasses.fields(item):
                value = getattr(item, field.name)
                if isinstance(value, str):
                    assert "\n" not in value, (fixture.number, field.name)
                    assert len(value) < 200, (fixture.number, field.name)


def test_a_metadata_field_names_a_field_and_does_not_carry_its_value():
    from privacy.items import MetadataField
    names = {f.name for f in dataclasses.fields(MetadataField)}
    assert names == {"name"}


def test_excerpts_included_holds_key_and_span_pairs_and_not_the_text():
    # SPEC §7: "excerpts_included stores (observation_key, span) pairs plus the
    # redaction_manifest, not a second copy of the text". The always-local text
    # already exists once.
    unit_text = p4(8).text_units[0].text
    for fixture in FIXTURES:
        for key, span in fixture.audit_record.excerpts_included:
            assert key.startswith("sha256:")
            assert "-" in span
            assert unit_text not in key and unit_text not in span


# --- the fixtures stand on P4's fixtures, not on a private substrate ---------

def test_every_excerpt_addresses_an_observation_p4_published():
    # The reason `p4_fixture` names a NUMBER and does not copy the observation:
    # `observation_key` is derived from (content_hash, extractor_name, locator,
    # raw_value), so a P4 fixture that moves moves P7's key with it. A copied key
    # would rot silently and the replay would address nothing.
    from privacy.items import Excerpt, RedactedIdentifier
    for fixture in FIXTURES:
        addressed = [item for item in fixture.request.requested_items
                     if isinstance(item, (Excerpt, RedactedIdentifier))]
        if not addressed:
            continue
        assert fixture.p4_fixture is not None, fixture.number
        published = {o.observation_key for o in p4(fixture.p4_fixture).observations}
        for item in addressed:
            assert item.observation_key in published, (fixture.number, item)


# --- the replay: the fixture and the gate are one implementation -------------

@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_through_the_real_gate_reproduces_the_decision(
        p7_conn, tmp_path, number):
    fixture = by_number(number)
    decision, _ = replay(p7_conn, fixture, tmp_path)
    assert type(decision) is type(fixture.decision), fixture.spec_case
    if isinstance(fixture.decision, Denied):
        assert decision.reason == fixture.decision.reason
        assert decision.explanation
        assert decision.remedy_options
    if isinstance(fixture.decision, NeedsConsent):
        assert decision.options == fixture.decision.options
    if isinstance(fixture.decision, Released):
        assert decision.model_target == fixture.decision.model_target
        assert decision.policy_version == fixture.policy.policy_version


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_reproduces_its_audit_record_field_for_field(
        p7_conn, tmp_path, number):
    # SPEC §11: "Each fixture carries the audit record the gate would have appended."
    # `would have appended` is a claim about the implementation, so it is checked
    # against the implementation and not against a second hand-written copy of it.
    fixture = by_number(number)
    decision, file_id = replay(p7_conn, fixture, tmp_path)
    appended = audit_record(p7_conn, _audit_id_of(p7_conn, decision))
    for field in AUDIT_FIELDS:
        if field in MINTED_FIELDS or field in SUBSTITUTED_FIELDS:
            continue
        assert getattr(appended, field) == getattr(fixture.audit_record, field), (
            fixture.number, field)


def test_the_excused_field_list_is_small_and_named():
    # An ignore-list is the standard way a golden-record test stops testing anything.
    # Five names, each with a reason, and the set is asserted rather than extended.
    assert SUBSTITUTED_FIELDS == {"file_id", "file_ids"}
    assert MINTED_FIELDS == {"audit_id", "release_id", "consent_request_id",
                             "appended_at"}
    assert len(SUBSTITUTED_FIELDS | MINTED_FIELDS) < len(AUDIT_FIELDS) / 2


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_every_replay_leaves_exactly_one_audit_event(p7_conn, tmp_path, number):
    # §8.4: "Every model call should be recorded in a consent-aware audit record."
    # Every call, including the denied ones and the local ones -- §8.4 names no
    # exemption, and §8.2 covers "Every significant event affecting a file".
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    replay(p7_conn, by_number(number), tmp_path)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after > before


def _audit_id_of(conn, decision) -> int:
    """The audit id the gate returned, whichever branch it returned it on."""
    if isinstance(decision, Released):
        return int(decision.audit_id)
    row = conn.execute(
        "SELECT event_id FROM events WHERE subsystem = 'P7' "
        "ORDER BY event_id DESC LIMIT 1").fetchone()
    return int(row["event_id"])
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: FAIL — `ImportError: cannot import name 'FIXTURE_COVERAGE' from 'privacy.fixtures'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/fixtures.py`**

```python
# src/privacy/fixtures.py
"""SPEC §11's published fixtures: the door's behaviour as data, so P8 can be built
against P7 before P7 ships.

§11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean `Released`
with redaction applied; a `NeedsConsent` returning all four options; a protected file
under each of the four modes; an `unreadable_unclassified` file; a `Protected Records`
residual request. Each fixture carries the audit record the gate would have appended."

Three things are true of this module and none of them is a style choice:

- **It is a LEAF.** Nothing else under `src/privacy/` imports it. That is what keeps
  the numbers it holds -- one `max_dossier_tokens`, one span length -- out of the
  gate: a fixture records a value the way a recorded call records one, and Task 21
  asserts no other module holds a bare number at all.
- **Every excerpt stands on one of P4's nineteen published fixtures.** The keys are
  computed from `evidence_shape.fixtures` at import, never copied. `observation_key`
  is derived from `(content_hash, extractor_name, locator, raw_value)` (M14, MINOR 8),
  so a P4 fixture that moves moves P7's key with it and the replay keeps resolving.
- **The always-local set is enforced twice, and fixture 7 is why.** Task 7 makes the
  nine named kinds unconstructible, so a request holding "OCR output" cannot be built
  and cannot be a fixture. `Denied(always_local_item)` is therefore reached the other
  way: by a CONSTRUCTIBLE `Excerpt` that RESOLVES to always-local content -- P4's
  fixture 8 is an `ocr.apple_vision` run in zone `ocr`, and §8.4 puts "OCR output" in
  the always-local set. Construction refuses the name; release refuses the resolution.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.location import TextSpan

from privacy.audit import AUDIT_FIELDS, AuditRecord
from privacy.classification import ClassificationRecord
from privacy.consent import ConsentRequirement
from privacy.denial import PROTECTED_RECORDS_TEMPLATE
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, Filename, MetadataField,
    RedactedIdentifier,
)
from privacy.policy import Policy
from privacy.redaction import RedactionEntry
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent, \
    Released, Target
from privacy.vocabulary import CONSENT_OPTIONS

#: One clock for every fixture. A fixture whose timestamps drift is a fixture whose
#: golden audit record cannot be compared field for field.
FIXTURE_CLOCK: str = "2026-08-22T09:00:00+00:00"

#: The area name every scoped fixture uses. It is a STRING THE CALLER SUPPLIED and not
#: a definition: SPEC Open question 3 asks "What is a 'corpus area'?" and P7 answers
#: nothing. `Gate` takes an `area_of` resolver with no default for the same reason.
FIXTURE_AREA: str = "Academics"

LOCAL_MODEL = ModelTarget(locality="local", model_id="local-small", provider="local")
CLOUD_MODEL = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")

#: SPEC §11's five "plus" items, in the SPEC's own words. This is the checklist, so a
#: paraphrase here stops it checking the document it came from.
SPEC_11_ITEMS: tuple[str, ...] = (
    "a clean `Released` with redaction applied",
    "a `NeedsConsent` returning all four options",
    "a protected file under each of the four modes",
    "an `unreadable_unclassified` file",
    "a `Protected Records` residual request",
)


class UnknownFixture(KeyError):
    """A fixture number nobody published. Not a fallback, not the nearest neighbour."""


def _p4(number: int):
    for fixture in P4_FIXTURES:
        if fixture.number == number:
            return fixture
    raise UnknownFixture(f"P4 publishes no fixture {number}")


def _key(number: int) -> str:
    """P4 fixture `number`'s first observation key, computed by P4 and read here."""
    return _p4(number).observations[0].observation_key


def _hash(number: int) -> str:
    return _p4(number).run.content_hash


def _unit_length(number: int) -> int:
    return len(_p4(number).text_units[0].text)


def _policy(mode: str, *, grants: tuple[tuple[str, str], ...] = (),
            moves: Mapping[str, str] | None = None, version: str = "policy-1") -> Policy:
    """A policy at `mode`. Every redaction facet is at its more redacting value.

    W1's second half: "Where the design is silent on a redaction default, the more
    redacting option is the default." A fixture that shipped a `shown` facet would be
    publishing a posture §8.4's `must` forbids -- "The default posture must therefore
    be local-first and data-minimizing" -- and P8 would build against it.
    """
    return Policy(
        policy_version=version, operation_mode=mode, consent_grants=grants,
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions=dict(moves or {}), plan_version="plan-1",
        set_at=FIXTURE_CLOCK)


def _classified(p4_number: int, handling_class: str, *, protected: bool,
                basis: str = "detector",
                reliability_state: str = "validated") -> ClassificationRecord:
    """A classification over P4 fixture `p4_number`'s bytes.

    `protected` is a PARAMETER here, never derived from `handling_class`. SPEC §2:
    "Neighbouring parts should consume the `protected` flag, not infer it from the
    class", and Open question 1 -- whether `protected` is exactly the top two classes
    -- is unsettled. Fixture 10 is the fixture that depends on it staying unsettled.
    """
    return ClassificationRecord(
        file_id="fixture-file", content_hash=_hash(p4_number),
        handling_class=handling_class, protected=protected, basis=basis,
        evidence_refs=(_key(p4_number),) if basis == "detector" else (),
        reliability_state=reliability_state, observed_at=FIXTURE_CLOCK)


def _request(*, stage: str, model_target: ModelTarget, items: tuple,
             fingerprint: str, max_dossier_tokens: int,
             template: str = "tpl.resolve_subject") -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=("fixture-file",), group_id=None),
        model_target=model_target, requested_items=items,
        prompt_template_id=template, prompt_fingerprint=fingerprint,
        max_dossier_tokens=max_dossier_tokens)


#: Built from `AUDIT_FIELDS` rather than from a literal keyword list, the way Task 15
#: builds its own. Task 10 owns SPEC §7's names and asserts they match §7 name for
#: name; constructing from the published tuple means a field this module never varies
#: can be respelled without breaking sixteen fixtures, while a field it DOES vary
#: disappearing fails loudly at the seam that cares.
_AUDIT_DEFAULTS: Mapping[str, object] = MappingProxyType({
    "audit_id": None,
    "release_id": None,
    "policy_version": "policy-1",
    "plan_version": "plan-1",
    "stage": "grouping",
    "outcome": "denied",
    "operation_mode": "offline",
    "authorizing_policy": "policy-1",
    "file_sensitivity": "unreadable_unclassified",
    "excerpts_included": (),
    "redaction_applied": False,
    "redaction_manifest": (),
    "model": {"locality": "local", "model_id": "local-small", "provider": "local"},
    "content_hashes": (),
    "content_hash": None,
    "prompt_fingerprint": "fp-fixture",
    "file_id": "fixture-file",
    "file_ids": ("fixture-file",),
    "group_id": None,
    "consent_request_id": None,
    "user_id": None,
    "observed_at": FIXTURE_CLOCK,
    "appended_at": FIXTURE_CLOCK,
})


def _audit(**over: object) -> AuditRecord:
    missing = [name for name in AUDIT_FIELDS if name not in _AUDIT_DEFAULTS]
    if missing:
        raise KeyError(
            f"AUDIT_FIELDS names {missing} and this module has no value for them; "
            "SPEC §7 changed and the fixtures need a value, not a default")
    values = {name: _AUDIT_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update({name: value for name, value in over.items() if name in values})
    return AuditRecord(**values)


@dataclass(frozen=True)
class GateFixture:
    """One published request -> decision pair, replayable against the real gate.

    Six fields are the plan skeleton's. Five are added here: `classification`,
    `p4_fixture` and `revoked` because a fixture that cannot be seeded cannot be
    replayed, and Done-means 11 turns on replay; `area` because Open question 3 is
    open and the corpus area must therefore be data rather than a rule; and
    `downstream_obligation` because SPEC §11 puts an obligation on P8 for two of these
    and a comment in P7's source is not a contract P8 can read.
    """

    number: int
    spec_case: str
    policy: Policy
    classification: ClassificationRecord | None
    area: str | None
    request: ModelCallRequest
    decision: Released | Denied | NeedsConsent
    audit_record: AuditRecord
    p4_fixture: int | None
    downstream_obligation: str | None
    revoked: bool


def _denied(reason: str, explanation: str, *remedies: str,
            evidence_refs: tuple[str, ...] = ()) -> Denied:
    """Every denial carries an explanation and at least one legitimate alternative.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial whose
    remedy list is empty is a dead end the user cannot act on.
    """
    return Denied(reason=reason, explanation=explanation,
                  remedy_options=tuple(remedies), evidence_refs=evidence_refs)


FIXTURES: tuple[GateFixture, ...] = (
    GateFixture(
        number=1,
        spec_case="Denied.reason = protected_cloud_target (an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),),
                         fingerprint="fp-01", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: protected material is not included in cloud-model prompts by "
            "default, and this policy is `hybrid` -- 'Sensitive files remain local; "
            "non-sensitive bounded dossiers may use a cloud LLM.'",
            "run the same request against a local model",
            "ask the user for a consent grant covering this area",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="hybrid",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-01",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=2,
        spec_case="Denied.reason = unclassified (nothing has looked)",
        policy=_policy("local_model"),
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-02", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "§8.4 makes classification a precondition of escalation -- 'classify data "
            "into handling classes before LLM escalation' -- and no classification "
            "exists for this file. Absence resolves to `unreadable_unclassified`, "
            "never to `public_low`.",
            "classify the file and retry",
            "resolve the question from local deterministic facts"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            prompt_fingerprint="fp-02"),
        p4_fixture=None, downstream_obligation=None, revoked=False),
    GateFixture(
        number=3,
        spec_case="Denied.reason = policy_revoked",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-03", max_dossier_tokens=2000),
        decision=_denied(
            "policy_revoked",
            "the consent grant authorizing a cloud model for this area was revoked. "
            "§8.4: revocation applies to future runs, so this call is decided against "
            "the policy version in force now.",
            "grant consent for this area again",
            "run the same request against a local model"),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-03",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=True),
    GateFixture(
        number=4,
        spec_case="Denied.reason = protected_records_template (the content half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="identify the issuing body"),),
                         fingerprint="fp-04", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE} residual "
            "template, which 'must not cause filenames or content to be exposed in "
            "model prompts' (§7.3).",
            "resolve the placement from local deterministic facts",
            "ask the user to move the file out of the protected area explicitly",
            evidence_refs=(_key(3),)),
        audit_record=_audit(
            outcome="denied", operation_mode="cloud_assisted",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            prompt_fingerprint="fp-04",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=5,
        spec_case="Denied.reason = whole_document_requested",
        policy=_policy("local_model"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(0, _unit_length(3)),
                                        reason="read the page"),),
                         fingerprint="fp-05", max_dossier_tokens=20000),
        decision=_denied(
            "whole_document_requested",
            "the requested span covers the whole text unit. §8.4: the engine 'should "
            "not send full documents where a short heading or OCR excerpt is enough "
            "to resolve the question.'",
            "request the heading or the anchor excerpt instead",
            "split the task across bounded excerpts",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-05"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=6,
        spec_case="Denied.reason = dossier_over_budget (M9's backstop)",
        policy=_policy("local_model"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),),
                         fingerprint="fp-06", max_dossier_tokens=1),
        decision=_denied(
            "dossier_over_budget",
            "the resolved dossier exceeds the `max_dossier_tokens` the caller is "
            "operating under. This is a backstop: §8.6's ladder -- 'summarize "
            "deterministic facts, preserve anchor excerpts, split the task, or defer "
            "the decision' -- runs in P8 before the call (M9).",
            "run §8.6's reduction ladder and call again",
            "defer the decision",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-06"),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove its ladder ran first -- a P8 test that reaches this "
            "denial through the normal path is a P8 failure, not a gate result"),
        revoked=False),
    GateFixture(
        number=7,
        spec_case="Denied.reason = always_local_item (an excerpt resolving to OCR)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(8, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(8),
                                        span=TextSpan(0, 24),
                                        reason="read the status banner"),),
                         fingerprint="fp-07", max_dossier_tokens=2000),
        decision=_denied(
            "always_local_item",
            "the excerpt resolves to OCR output, which §8.4 places in the always-local "
            "set: 'Paths, complete extracted text, OCR output, file hashes, image "
            "EXIF, GPS, user edits, group memberships, and raw sensitive values should "
            "remain local.'",
            "use the deterministic facts derived from the OCR text",
            "ask the user to review the screenshot locally",
            evidence_refs=(_key(8),)),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="public_low", content_hash=_hash(8),
                            content_hashes=(_hash(8),), prompt_fingerprint="fp-07",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=8, downstream_obligation=None, revoked=False),
    GateFixture(
        number=8,
        spec_case="Denied.reason = mode_forbids_target (the mode axis, unprotected)",
        policy=_policy("offline"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-08", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The file is neither sensitive nor "
            "protected; the mode alone forbids the target.",
            "run the same request against a local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="offline",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-08",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=9,
        spec_case="a clean `Released` with redaction applied",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "personal_non_sensitive", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),
                                RedactedIdentifier(observation_key=_key(3),
                                                   span=TextSpan(12043, 12051),
                                                   identifier_class="institution"),
                                EvidenceReference(observation_key=_key(3))),
                         fingerprint="fp-09", max_dossier_tokens=2000),
        decision=Released(
            release_id="release-fixture-09", audit_id=None,
            policy_version="policy-1",
            materialised_items=("Columbia", "[institution]"),
            redaction_manifest=(
                RedactionEntry(observation_key=_key(3), span="12043-12051",
                               identifier_class="institution", redacted=True),),
            model_target=CLOUD_MODEL),
        audit_record=_audit(
            outcome="released", operation_mode="cloud_assisted",
            file_sensitivity="personal_non_sensitive", content_hash=_hash(3),
            content_hashes=(_hash(3),), prompt_fingerprint="fp-09",
            excerpts_included=((_key(3), "12043-12051"),),
            redaction_applied=True,
            redaction_manifest=((_key(3), "12043-12051", "institution", True),),
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=10,
        spec_case="a `NeedsConsent` returning all four options",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        # `sensitive_personal` and NOT protected. Open question 1 -- "Is `protected`
        # exactly the top two handling classes?" -- is unsettled, and SPEC §2 says
        # outright: "Neighbouring parts should consume the `protected` flag, not infer
        # it from the class." This fixture is where that stays true: a gate that
        # inferred `protected` from the class would deny here and §8.4's consent
        # branch would be unreachable.
        classification=_classified(3, "sensitive_personal", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="fact_resolution", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="the sensitive passage names the "
                                               "institution"),),
                         fingerprint="fp-10", max_dossier_tokens=2000),
        decision=NeedsConsent(
            consent_request_id=None,
            requirement=ConsentRequirement(
                items=(_key(3),),
                why="the requested excerpt is text from a file classified "
                    "`sensitive_personal`"),
            options=CONSENT_OPTIONS),
        audit_record=_audit(
            outcome="consent_requested", operation_mode="cloud_assisted",
            file_sensitivity="sensitive_personal", content_hash=_hash(3),
            content_hashes=(_hash(3),), prompt_fingerprint="fp-10",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove it returns the branch to its caller intact"),
        revoked=False),
    GateFixture(
        number=11,
        spec_case="a protected file under `offline`",
        policy=_policy("offline"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-11", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The mode is evaluated first, because "
            "under `offline` this target is unreachable for every file and naming the "
            "file's protection would be a narrower reason than the true one.",
            "run the same request against a local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="offline",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-11",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=12,
        spec_case="a protected file under `local_model`",
        policy=_policy("local_model"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-12", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's local-model mode: 'Local extraction plus a user-installed local "
            "LLM for eligible dossiers.' No cloud target is reachable under it.",
            "run the same request against the local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-12",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=13,
        spec_case="a protected file under `hybrid` (a metadata field, not an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-13", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: 'Protected material should not be included in cloud-model prompts "
            "by default.' The sentence names no item kind, so an innocuous metadata "
            "field is refused on the same ground as an excerpt.",
            "run the same request against a local model",
            "ask the user for a policy that explicitly permits it"),
        audit_record=_audit(outcome="denied", operation_mode="hybrid",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-13",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=14,
        spec_case="a protected file under `cloud_assisted`, with no grant for the area",
        policy=_policy("cloud_assisted"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-14", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4's cloud-assisted mode: 'User explicitly permits selected corpus "
            "areas to use a cloud model.' No grant covers this area, and the material "
            "is protected.",
            "ask the user for a consent grant covering this area",
            "run the same request against a local model"),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-14",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=15,
        spec_case="an `unreadable_unclassified` file (something looked and failed)",
        policy=_policy("local_model"),
        classification=_classified(18, "unreadable_unclassified", protected=False,
                                   basis="detector", reliability_state="direct"),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-15", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "the extraction is §2.9's indexed-but-unreadable case and the handling "
            "class is `unreadable_unclassified`. §8.4 makes classification a "
            "precondition of escalation, and §8.6 forbids the alternative: 'Cost "
            "exhaustion must never turn into lower-quality automatic classification.'",
            "show the file as unprocessed rather than unimportant",
            "ask the user to classify it"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="unreadable_unclassified",
                            content_hash=_hash(18), content_hashes=(_hash(18),),
                            prompt_fingerprint="fp-15"),
        p4_fixture=18, downstream_obligation=None, revoked=False),
    GateFixture(
        number=16,
        spec_case="a `Protected Records` residual request (the filename half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Filename(file_id="fixture-file"),),
                         fingerprint="fp-16", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE} residual "
            "template. §7.3 forbids both nouns: it 'must not cause filenames or "
            "content to be exposed in model prompts'.",
            "place the file from local deterministic facts",
            "surface the residual area to the user without naming the file"),
        audit_record=_audit(
            outcome="denied", operation_mode="cloud_assisted",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            prompt_fingerprint="fp-16",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
)


#: SPEC §11's list, mapped to the fixtures that satisfy it. Thirteen keys: the eight
#: `Denied.reason` values and the five `SPEC_11_ITEMS`. A key with an empty tuple is a
#: §11 item with no fixture, which is the failure this map exists to make visible.
FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]] = MappingProxyType({
    "protected_cloud_target": (1, 13, 14),
    "unclassified": (2, 15),
    "policy_revoked": (3,),
    "protected_records_template": (4, 16),
    "whole_document_requested": (5,),
    "dossier_over_budget": (6,),
    "always_local_item": (7,),
    "mode_forbids_target": (8, 11, 12),
    "a clean `Released` with redaction applied": (9,),
    "a `NeedsConsent` returning all four options": (10,),
    "a protected file under each of the four modes": (11, 12, 13, 14),
    "an `unreadable_unclassified` file": (15,),
    "a `Protected Records` residual request": (16,),
})

#: The four-mode sweep, mode -> fixture number. `offline` and `local_model` deny on the
#: mode; `hybrid` and `cloud_assisted` deny on the protection. That difference is the
#: precedence rule, published as data so Task 13 cannot quietly invert it.
MODE_SWEEP: Mapping[str, int] = MappingProxyType({
    "offline": 11,
    "local_model": 12,
    "hybrid": 13,
    "cloud_assisted": 14,
})

_BY_NUMBER: Mapping[int, GateFixture] = MappingProxyType(
    {fixture.number: fixture for fixture in FIXTURES})


def by_number(number: int) -> GateFixture:
    """The fixture with this number, or `UnknownFixture`. Never a nearest neighbour."""
    try:
        return _BY_NUMBER[number]
    except KeyError:
        raise UnknownFixture(
            f"P7 publishes no gate fixture {number}; the published numbers are "
            f"{tuple(sorted(_BY_NUMBER))}") from None
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: PASS — 68 passed (24 unparameterised tests plus three parameterisations over the
sixteen fixtures)

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–20 green, and the 1300 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/fixtures.py tests/p7/test_p7_fixtures.py
git commit -m "feat(P7): SPEC 11's sixteen published fixtures, each replayed through the real gate"
```

---
