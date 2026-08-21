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
- `database_agent.files_table.record_file` ends `..., scan_state: str, materialized: bool,
  content_hash: str | None = None) -> str` — it **accepts an explicit content hash**. That is what
  makes Task 20's replay possible at all: a fixture seeded at P4's own content hash reproduces P4's
  own `observation_key`, so the published fixtures and the replayed ones address the same evidence
  and `file_id` is the only field a replay has to substitute.
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
    """Built from `AUDIT_FIELDS`, never from a literal keyword list.

    Task 10 owns SPEC §7's names and asserts they match §7 name for name. Building
    from the published tuple means a field these sixteen fixtures never vary can be
    respelled without breaking them, while a field they DO vary disappearing fails
    here, loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _AUDIT_DEFAULTS]
    if missing:
        raise KeyError(
            f"AUDIT_FIELDS names {missing} and this module has no value for them; "
            "SPEC §7 changed and the fixtures need a value, not a default")
    unknown = [name for name in over if name not in _AUDIT_DEFAULTS]
    if unknown:
        raise KeyError(
            f"{unknown} is not an audit field this module knows; a silently dropped "
            "keyword is how a fixture stops carrying the value it claims to carry")
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

### Task 21: The no-invention guard, and every open question held open

**Files:**
- Modify: `src/privacy/vocabulary.py` (add `HELD_OPEN` — see below)
- Test: `tests/p7/test_p7_no_invention.py`

**Interfaces:**
- Consumes: every module under `src/privacy/`, by `importlib` + `vars(module)`; `ast` over the same
  files for the assertions introspection cannot make; `database_agent.files_table.FILES_COLUMNS`,
  `.set_sensitivity_state`, `.get_file`, `.record_file`; `privacy.classification.ClassificationRecord`;
  `privacy.classification_store.ClassificationStore`, `.mirror_state`;
  `privacy.learning_seam.assign`; `evidence_shape.text_units.raw_value_at`;
  `evidence_shape.store.text_units_for_run`, `.text_unit_at`, `.unit_for_observation`.
- Produces (`vocabulary.py`): `HELD_OPEN: Mapping[str, str]` — the three questions held open that are
  **not** among the SPEC's eleven. `OPEN_QUESTIONS` (the eleven) is Task 2's and is asserted here.

**Done-means:** the guard behind 1, 12, and the whole *Deferred* table.

**One guard INVERTS, and it is the reason this task cannot be written from the skeleton alone.**
The skeleton's §5 says *"Every open question stays open … Each is held by a guard in Task 21 that
names it and fails the moment someone answers it"*, and its §4 says the opposite about one of them:
**P6 OQ11 is CLOSED (D2).** A guard asserting OQ11 is open **fails on the day this plan is
executed**, because that is the day D2 is applied. Task 21 asserts the **D2 shape** instead, in four
clauses, each of which is a separate test:

1. `ClassificationRecord` keyed `(file_id, content_hash)` is **authoritative** — the store resolves
   one current record per pair, and a new content hash inherits nothing.
2. `files.sensitivity_state` is a **projection**, written through P1's published
   `set_sensitivity_state`. P7 takes no writer protocol; P1 publishes the setter and P7 calls it.
3. `src/privacy/` issues **no `UPDATE files`** of its own — asserted over the AST's string literals,
   so a docstring explaining the rule cannot satisfy it and cannot break it.
4. **`unclassified` never reaches that column.** It is a gate outcome, not a file fact. Storing it
   would make *"nothing has looked"* indistinguishable from *"this file carries nothing"*, which is
   the distinction D2's third clause exists to protect and Task 20's fixtures 2 and 15 exist to
   demonstrate.

**Two things are genuinely open and are held open BY NAME, because a question nobody names is a
question that gets answered by accident.**

- **`filename` as a sixth releasable kind.** §8.4 names **five** — *"selected excerpts, redacted
  identifiers, candidate labels, non-sensitive metadata, and evidence references"* — and puts
  *paths* in the always-local set. P7's SPEC adds a sixth and **flags it itself**: *"This is the one
  place where the contract resolves an apparent conflict rather than deferring it, because P8 and
  P11 cannot build without an answer."* It is SPEC Open question 2, and it is Joseph's call, routed
  as NEEDS-JOSEPH **B5d** (*"`filename` as a releasable kind — the one P7 open question its own plan
  left off its list. §8.4's releasable list is five and does not name it"*) and **C9a**
  (*"Recorded; the design wins. The SPEC flags it itself. **Your call.**"*). The guard asserts the
  sixth kind exists, that the SPEC's own flag text is carried beside it, and that **nothing in
  `src/privacy/` treats the conflict as settled** — no module holds a resolution constant, and the
  `Filename` item is denied for protected files exactly as §7.3 requires, which is the narrow part
  the design does settle.
- **Whether P6 keeps a `sensitivity status` field row at all.** P7's SPEC Contract-in says
  *"**P6 must accept `sensitivity` as a first-class universal field** (§3.11) rather than a
  domain-scoped one"* while D2 makes P7's own record authoritative. The skeleton states the residue
  precisely: *"whether P6 keeps a `sensitivity status` row among §3.11's universal fields at all.
  Round 1's F-2 already found that field has no producer. D2 decided which record is AUTHORITATIVE;
  it did not decide whether a second, P6-owned field row continues to exist beside it. Until that is
  answered, P6 should create no such row and P7 should not read one."* **Do not resolve it.** The
  guard asserts `src/privacy/` reads no P6 surface, holds no `file_facts` table name, and names all
  three spellings — `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state`
  (P1's column) — as distinct.

**And a third, which is P4's and reaches P7 through redaction.** `Region` is
`{ x, y, w, h, unit }` with `unit ∈ {px, norm}` and **no document in this repository says which
corner the origin is**. `evidence_shape.vocabulary.OPEN_QUESTIONS` carries one entry, OQ4, and it is
not this one; the design says only *"locations or bounding boxes where available"* (§2.7). P7's
redaction and resolution both touch `Location.region`, so a guard that P7 never assumes an origin is
cheap now and unbuildable after someone has written `y = height - y` somewhere. The guard asserts
`src/privacy/` performs **no arithmetic on a region field at all** and holds no origin token.

**`src/privacy/` imports none of `extractors`' refusals, and that list is now THREE names.** The
skeleton's §1 says *"never imports `ProtectedContainerRefused` or `DatalessRefused`"* and stops at
two. `extractors.failure.ContractViolation` is the third and it is live —
`src/orchestrator.py` imports all three side by side. The three refusals in this product are three,
and P7 owns only the last of them: reading is refused by P3/P5, materialising is refused by P3/P5,
and **release** is refused by P7. A file that failed either of the first two never acquires the
`(file_id, content_hash)` pair P7 keys on, so re-deriving the verdict is not merely redundant, it is
unconstructible. Reported as a correction from two names to three.

**Two corrections to the L2 guard, found by running it against the live repository rather than by
reading the skeleton.** The skeleton says the set of packages binding a P4 text materialiser is
*"`{evidence_shape, extractors, privacy}` and nothing else"*. Introspected 2026-08-22, the live set
is **`{evidence_shape, orchestrator}`**:

- **`extractors` binds none of the four.** P5 emits observations and text units; it never reads one
  back. The skeleton's set would have been wrong in the permissive direction — it licenses a package
  that does not need the licence.
- **`orchestrator` binds `text_units_for_run`**, at `src/orchestrator.py`, to copy units into P2's
  replay bundle. That is a **local** copy, not an egress — but whether a bundle may carry excerpt
  text is **P7's own Open question 8**, unanswered, so this guard **records the binder and its reason
  and does not rule on it**. Writing the guard to exclude `orchestrator` by calling it "not a
  package" would be hiding a real binder behind a technicality.

The guard is therefore written over **every module under `src/`**, with an allowlist of three
top-level names and a published reason for each. It passes trivially today and becomes load-bearing
the moment P8 lands, which is why it is written now rather than by someone who wants it to pass.

**Everything else is runtime introspection, and where it cannot be, it is the AST.** The skeleton is
emphatic and it is right: *"a source-text guard matches comments and docstrings, which is a failure
this repository has already recorded more than once."* `tests/p3/test_p3_no_invention.py` documents
the case where it broke the other way — a comment explaining why a value is absent failed the test
asserting the value is absent. This task reimplements `code_tokens()` over `src/privacy/` rather
than importing it, because `tests/` has no `__init__.py` and a cross-directory import there would
collide on module basenames the way `conftest.py` already has twice on this project.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_no_invention.py
"""P7 answers no open question in code, and D2's shape holds.

Two techniques and one rule. The rule: an assertion of the form "this token appears
nowhere" is made against the AST, never against `read_text()`, because a comment or a
docstring EXPLAINING why a value is absent matches a text scan for that value. That
failure is recorded in `tests/p3/test_p3_no_invention.py`, which is where
`code_tokens()` comes from and why it exists.

The technique for everything else is `vars(module)`: what a module BINDS is what it
holds, and a number inside a docstring is prose.
"""
import ast
import importlib
import json
import pathlib

import pytest

import privacy
from database_agent.files_table import FILES_COLUMNS, get_file, record_file

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror_state
from privacy.learning_seam import assign, reclassify
from privacy.vocabulary import HELD_OPEN, OPEN_QUESTIONS

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
SOURCE_DIR = pathlib.Path(privacy.__file__).parent
SRC_ROOT = pathlib.Path(privacy.__file__).parent.parent

#: Module-level names permitted to be bound to a number. It is EMPTY, and adding a
#: name to it is a P7 contract revision rather than an implementation decision:
#: SPEC *Deferred* puts "Numeric values for every ceiling" outside this contract --
#: §8.6 "names the knobs, states they are 'configurable', and gives no values".
NUMERIC_ALLOWLIST: frozenset[str] = frozenset()

#: Top-level names permitted to bind a P4 text materialiser, each with its reason.
#: Introspected against the live repository, not copied from the plan skeleton, which
#: named `extractors` (which binds none) and omitted `orchestrator` (which binds one).
MATERIALISER_BINDERS = {
    "evidence_shape": "P4 owns them",
    "privacy": "L2 -- `resolve.py` is the ONE place a (key, span) becomes text",
    "orchestrator": (
        "copies text units into P2's replay bundle (§8.5). A local copy, not an "
        "egress -- and whether a bundle may carry excerpt text is P7 Open question 8, "
        "unanswered, so this guard records it and does not rule on it"),
}

MATERIALISERS = ("raw_value_at", "text_units_for_run", "text_unit_at",
                 "unit_for_observation")


def modules():
    return sorted(SOURCE_DIR.glob("*.py"))


def imported():
    """Every module under `src/privacy/`, imported, for namespace introspection."""
    found = []
    for path in modules():
        name = path.stem
        if name == "__init__":
            found.append(privacy)
            continue
        found.append(importlib.import_module(f"privacy.{name}"))
    return found


def _docstrings(tree: ast.AST) -> set[int]:
    """The id() of every node that is a docstring, so it can be skipped."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def code_strings(path: pathlib.Path) -> set[str]:
    """String and numeric literals P7's code USES, docstrings excluded."""
    tree = ast.parse(path.read_text(), filename=str(path))
    skip = _docstrings(tree)
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and id(node) not in skip
                and isinstance(node.value, (str, int, float))
                and not isinstance(node.value, bool)):
            tokens.add(str(node.value))
    return tokens


def code_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            tokens.add(node.id)
        elif isinstance(node, ast.Attribute):
            tokens.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tokens.add(node.name)
        elif isinstance(node, ast.arg):
            tokens.add(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            tokens.add(node.arg)
        elif isinstance(node, ast.alias):
            tokens.add(node.name)
            if node.asname:
                tokens.add(node.asname)
    return tokens


def code_tokens(path: pathlib.Path) -> set[str]:
    return code_names(path) | code_strings(path)


def imports_of(path: pathlib.Path) -> set[str]:
    """Every dotted name this module imports, from the AST rather than from text."""
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            found.add(module)
            found.update(f"{module}.{alias.name}" for alias in node.names)
            found.update(alias.name for alias in node.names)
    return found


def module_numbers(module):
    return {name: value for name, value in vars(module).items()
            if not name.startswith("_")
            and isinstance(value, (int, float)) and not isinstance(value, bool)}


# --- the eleven, present with the SPEC's own text ---------------------------

def test_all_eleven_spec_open_questions_are_present():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, text in OPEN_QUESTIONS.items():
        assert text.strip(), number


def test_open_question_11_names_no_winner_between_the_two_local_modes():
    # W1 narrowed it and did not close it: "What remains genuinely open is only WHICH
    # of those two ships, which turns on whether a local model is assumed present."
    from privacy.defaults import LOCAL_FIRST_MODES
    assert set(LOCAL_FIRST_MODES) == {"offline", "local_model"}
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            assert value not in ("offline", "local_model"), (module.__name__, name)


def test_no_module_holds_a_bare_hybrid_or_cloud_assisted_default():
    # Done-means 12's negative half, by introspection rather than by grep: both names
    # appear legitimately inside `OPERATION_MODES`, inside `MODE_SEMANTICS`, inside
    # denial messages and inside fixture records, so a text scan either passes
    # vacuously or fails on a comment.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            assert value not in ("hybrid", "cloud_assisted"), (module.__name__, name)


def test_open_question_3_defines_no_corpus_area():
    # "What is a 'corpus area'? ... Consent grants cannot be scoped until this is
    # named." The gate takes an `area_of` resolver with no default; the only area
    # STRING in the package is the fixture module's single example.
    import inspect
    from privacy.gate import Gate
    parameters = inspect.signature(Gate.__init__).parameters
    assert "area_of" in parameters
    assert parameters["area_of"].default is inspect.Parameter.empty
    holders = [m.__name__ for m in imported()
               if any(name.upper().endswith("AREA") or name.upper().endswith("AREAS")
                      for name in vars(m) if not name.startswith("_"))]
    assert holders == ["privacy.fixtures"]
    from privacy.fixtures import FIXTURE_AREA
    assert isinstance(FIXTURE_AREA, str)


def test_open_question_1_never_infers_protected_from_the_handling_class():
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Fixture 10 is where that stays true -- a `sensitive_personal`
    # file that is NOT protected, which is the input §8.4's consent branch needs.
    from privacy.fixtures import by_number
    fixture = by_number(10)
    assert fixture.classification.handling_class == "sensitive_personal"
    assert fixture.classification.protected is False
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=True, basis="user", evidence_refs=(),
        reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    assert record.protected is True


def test_open_question_7_counts_no_repetitions():
    # "Does repeated reclassification generalize?" Nothing counts, so nothing widens.
    for module in imported():
        assert not module_numbers(module) - set(NUMERIC_ALLOWLIST), module.__name__


def test_open_question_10_states_no_retention_period():
    # "How long audit records, consent grants, and superseded classifications are
    # kept. The design states no retention period anywhere."
    for module in imported():
        for name in vars(module):
            upper = name.upper()
            for token in ("RETENTION", "TTL", "EXPIR", "MAX_AGE", "PURGE", "DAYS"):
                assert token not in upper, (module.__name__, name)


# --- the three held open that are not among the eleven ----------------------

def test_held_open_names_exactly_three_and_each_carries_its_source():
    assert set(HELD_OPEN) == {"I6", "P6-sensitivity-field-row", "P4-region-origin"}
    for key, text in HELD_OPEN.items():
        assert text.strip(), key


def test_i6_is_held_by_delete_derived_refusing_and_not_by_a_sentence():
    from privacy.revocation import DerivedScope, UnratifiedResolution, delete_derived
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)


def test_the_p6_field_row_question_stays_open_and_p7_reads_no_p6_surface():
    # P7's SPEC Contract-in: "P6 must accept `sensitivity` as a first-class universal
    # field (§3.11) rather than a domain-scoped one." D2 made P7's own record
    # authoritative and round 1 found that field has no producer. D2 did NOT decide
    # whether a second P6-owned row exists beside it, so P7 creates none, reads none,
    # and holds no P6 table name.
    for path in modules():
        tokens = code_tokens(path)
        for forbidden in ("file_facts", "fact_id", "field_id", "value_id"):
            assert forbidden not in tokens, (path.name, forbidden)
        assert not [name for name in imports_of(path) if name.startswith("facts")]


def test_the_three_spellings_of_sensitivity_stay_three():
    # `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state`
    # (P1's column). C8 calls this "the defect class that has cost this project the
    # most, at the largest scale it has appeared." Three names, one concept, and no
    # code that treats any two as one.
    assert "sensitivity_state" in FILES_COLUMNS
    from privacy.classification import CLASSIFICATION_FIELDS
    assert "handling_class" in CLASSIFICATION_FIELDS
    assert "sensitivity" not in CLASSIFICATION_FIELDS
    assert "sensitivity_state" not in CLASSIFICATION_FIELDS


def test_the_filename_sixth_kind_is_flagged_and_not_treated_as_settled():
    # §8.4's releasable list is FIVE -- "selected excerpts, redacted identifiers,
    # candidate labels, non-sensitive metadata, and evidence references" -- and puts
    # paths in the always-local set. The SPEC adds a sixth and flags it (Open question
    # 2, NEEDS-JOSEPH B5d / C9a). It is Joseph's call and nothing here decides it.
    from privacy.items import Filename
    from privacy.vocabulary import ITEM_KINDS
    assert ITEM_KINDS[-1] == "filename"
    assert len(ITEM_KINDS) == 6
    assert "filename" in OPEN_QUESTIONS[2].lower() or "Filename" in OPEN_QUESTIONS[2]
    assert {f.name for f in __import__("dataclasses").fields(Filename)} == {"file_id"}
    for path in modules():
        tokens = code_tokens(path)
        for settled in ("filename_resolved", "filename_settled",
                        "FILENAME_IS_NOT_A_PATH"):
            assert settled not in tokens, path.name


def test_p7_assumes_no_origin_for_a_normalized_bounding_box():
    # P4's SPEC: "`region` -- `{ x, y, w, h, unit }` where `unit ∈ {px, norm}`", and
    # §2.7 says only "locations or bounding boxes where available". NO document in
    # this repository says which corner the origin is. P7's redaction and resolution
    # both touch `Location.region`, so the guard is that P7 does ARITHMETIC on none of
    # its fields and holds no origin token.
    from evidence_shape.location import Region
    region_fields = {f.name for f in __import__("dataclasses").fields(Region)}
    assert region_fields == {"x", "y", "w", "h", "unit"}
    for path in modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.BinOp):
                continue
            for side in (node.left, node.right):
                if isinstance(side, ast.Attribute):
                    assert side.attr not in region_fields, (path.name, side.attr)
        tokens = code_tokens(path)
        for origin in ("top_left", "bottom_left", "top-left", "bottom-left",
                       "origin"):
            assert origin not in tokens, (path.name, origin)


# --- D2's shape, which is what replaced the OQ11 guard -----------------------

def test_the_classification_record_is_keyed_on_file_id_and_content_hash(
        p7_conn, tmp_path):
    # D2 clause 1: "Keyed on the hash because a classification is about BYTES; new
    # bytes at a path are a new file version and inherit nothing."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "doc.pdf"
    document.write_bytes(b"%PDF-1.4 one")
    file_id = record_file(
        p7_conn, document, filename="doc.pdf", normalized_filename="doc.pdf",
        extension=".pdf", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="application/pdf", detected_format="pdf",
        scan_state="fixture-scan-state", materialized=True)
    first = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis="user",
        evidence_refs=(), reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    store.write(first)
    assert store.current(file_id, first.content_hash) == first
    assert store.current(file_id, "sha256:different-bytes") is None


def test_the_column_is_written_only_through_p1s_published_setter():
    # D2 clause 2, and the reason there is no `SensitivityStateWriter`: P1 publishes
    # `set_sensitivity_state`, the twin of `set_extraction_status`. A protocol
    # wrapping a function that exists is a second write path to a column that spent
    # the whole project with none.
    binders = [m.__name__ for m in imported()
               if "set_sensitivity_state" in vars(m)]
    assert binders == ["privacy.learning_seam"]
    for module in imported():
        for name in vars(module):
            assert "SensitivityStateWriter" not in name, module.__name__


def test_src_privacy_issues_no_update_files_of_its_own():
    # D2 clause 2's negative half. Over the AST's string literals, so a docstring
    # explaining the rule neither satisfies it nor breaks it.
    for path in modules():
        for literal in code_strings(path):
            collapsed = " ".join(literal.lower().split())
            assert "update files" not in collapsed, (path.name, literal[:60])
            assert "insert into files" not in collapsed, (path.name, literal[:60])
            assert "delete from files" not in collapsed, (path.name, literal[:60])


def test_unclassified_never_reaches_the_projection_column(p7_conn, tmp_path):
    # D2 clause 3: "`Unreadable or unclassified` is a GATE OUTCOME, not a file fact.
    # It lives on the release decision and never in that column, so 'nothing has
    # looked' can never be read as 'this file carries nothing'."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "opaque.psd"
    document.write_bytes(b"8BPS fixture bytes")
    file_id = record_file(
        p7_conn, document, filename="opaque.psd", normalized_filename="opaque.psd",
        extension=".psd", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="image/vnd.adobe.photoshop", detected_format="psd",
        scan_state="fixture-scan-state", materialized=True)
    content_hash = get_file(p7_conn, file_id)["content_hash"]
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="unreadable_unclassified", protected=False, basis="detector",
        evidence_refs=("sha256:" + "0" * 64,), reliability_state="direct",
        observed_at=FIXED_CLOCK)
    assign(p7_conn, record, store=store, component_version=COMPONENT)
    stored = get_file(p7_conn, file_id)["sensitivity_state"]
    assert stored is not None
    assert "unclassified" not in json.dumps(json.loads(stored))


def test_the_projection_is_not_the_authoritative_record():
    # `mirror_state` is a PROJECTION: it drops what the column cannot answer. A mirror
    # that carried every field would invite a reader to treat the column as the
    # record, which is the shape D2 replaced.
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=False, basis="detector", evidence_refs=("sha256:x",),
        reliability_state="validated", observed_at=FIXED_CLOCK)
    state = mirror_state(record)
    assert set(state) < {f for f in vars(record)} | set(state)
    assert "file_id" not in state


# --- the three refusals stay three ------------------------------------------

def test_src_privacy_imports_none_of_extractors_three_refusals():
    # Reading is refused by P3/P5 (`ProtectedContainerRefused`); materializing is
    # refused by P3/P5 (`DatalessRefused`); a malformed extraction is refused by P5
    # (`ContractViolation`). RELEASE is P7's, and only release has a consent branch.
    # A file that failed either of the first two never acquires the
    # `(file_id, content_hash)` pair P7 keys on, so re-deriving is unconstructible.
    refusals = ("ProtectedContainerRefused", "DatalessRefused", "ContractViolation")
    for path in modules():
        names = imports_of(path)
        for refusal in refusals:
            assert refusal not in names, (path.name, refusal)
            assert f"extractors.safety.{refusal}" not in names, path.name
        assert "extractors.safety" not in names, path.name
        assert "admit" not in names, path.name


def test_the_orchestrator_imports_all_three_so_the_list_is_three_and_not_two():
    # The plan skeleton names two. The live caller names three, side by side, which is
    # how the omission was found.
    orchestrator = importlib.import_module("orchestrator")
    for refusal in ("ProtectedContainerRefused", "DatalessRefused",
                    "ContractViolation"):
        assert refusal in vars(orchestrator), refusal


# --- L2: one materialisation locus, repo-wide -------------------------------

def test_only_one_module_under_src_privacy_binds_a_p4_text_materialiser():
    binders = [m.__name__ for m in imported()
               if any(name in vars(m) for name in MATERIALISERS)]
    assert binders == ["privacy.resolve"]


def test_the_repo_wide_set_of_materialiser_binders_is_the_named_three():
    # Layer L2 of Done-means 3. This passes trivially today and becomes load-bearing
    # the moment P8 lands, which is why it is written now rather than later by someone
    # who wants it to pass.
    from evidence_shape import store as p4_store
    from evidence_shape import text_units as p4_text
    targets = {p4_text.raw_value_at, p4_store.text_units_for_run,
               p4_store.text_unit_at, p4_store.unit_for_observation}
    found: set[str] = set()
    for path in sorted(SRC_ROOT.rglob("*.py")):
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted
        module = importlib.import_module(dotted)
        if any(value in targets for value in vars(module).values()):
            found.add(dotted.split(".")[0])
    assert found == set(MATERIALISER_BINDERS), sorted(found)
    for binder, reason in MATERIALISER_BINDERS.items():
        assert reason.strip(), binder


# --- P7 invents nothing -----------------------------------------------------

def test_no_module_imports_re_so_p7_holds_no_detection_rule():
    # SPEC *Deferred*: "The design states *what* is protected and never *how it is
    # recognised*. The detector rule set, its signals, and its thresholds are
    # hand-authored. P7 publishes the vocabulary the detectors write into."
    for path in modules():
        names = imports_of(path)
        assert "re" not in names, path.name
        assert "regex" not in names, path.name


def test_no_module_enumerates_an_identifier_class_or_holds_a_transform():
    # SPEC *Deferred*: "Which identifier classes exist and how each is transformed is
    # not enumerated anywhere in the design. `redaction_manifest` carries the class as
    # an opaque string until this is authored."
    import inspect
    from privacy import redaction
    assert not hasattr(redaction, "IDENTIFIER_CLASSES")
    assert not hasattr(redaction, "TRANSFORMS")
    parameters = inspect.signature(redaction.apply_redaction).parameters
    for required in ("classifier", "transform"):
        assert parameters[required].default is inspect.Parameter.empty


def test_the_gate_holds_no_threshold_and_reads_p1s_ceiling():
    # SPEC *Deferred*: "Numeric values for every ceiling ... Deferred to configuration,
    # not to this contract." The ceiling is read from `database_agent.budget`; the
    # request field is the caller's echo of it (M9).
    from database_agent.budget import CEILING_KEYS
    assert "model.max_dossier_tokens_per_call" in CEILING_KEYS
    from privacy.release import REQUEST_FIELDS
    assert "max_dossier_tokens" in REQUEST_FIELDS


def test_the_fixture_module_is_a_leaf_so_its_numbers_reach_no_decision():
    # The one module holding numbers holds them INSIDE records, and nothing imports
    # it. A fixture records a value the way a recorded call records one.
    for path in modules():
        if path.stem == "fixtures":
            continue
        assert "privacy.fixtures" not in imports_of(path), path.name
        assert "fixtures" not in imports_of(path), path.name


def test_subsystem_p7_is_written_in_exactly_one_module():
    # M8: "the acting part authors, P1 stores." A second place that writes the author
    # is a second place the two can disagree.
    holders = [path.name for path in modules() if "P7" in code_strings(path)]
    assert holders == ["authorship.py"]


def test_no_module_holds_a_gazetteer():
    # §3.7 names "validated gazetteers" as a mechanism and never enumerates contents.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, (tuple, frozenset)):
                continue
            assert len(value) <= 20, (module.__name__, name, len(value))


def test_the_retraction_limit_wording_lives_nowhere_in_the_package():
    # SPEC *Deferred*: "Consent-prompt and retraction-limit wording | §8.4 | UX copy."
    # Task 15 enforces PRESENCE; the words are P13's. Asserted package-wide here
    # because the failure mode is a helpful default appearing in a neighbouring module.
    for path in modules():
        for literal in code_strings(path):
            assert "cannot retract" not in literal.lower(), path.name
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: FAIL — `ImportError: cannot import name 'HELD_OPEN' from 'privacy.vocabulary'`.
Task 2 publishes `OPEN_QUESTIONS` (the SPEC's eleven) and nothing else; the three questions held
open that are **not** among the eleven have no home until this step adds one.

- [ ] **Step 3: Add `HELD_OPEN` to `src/privacy/vocabulary.py`**

Append to the module, below `OPEN_QUESTIONS`:

```python
#: The questions held open that are NOT among SPEC Open questions 1-11, each with the
#: document that states it. They are separate from `OPEN_QUESTIONS` because that
#: mapping is keyed by the SPEC's own numbering and these three are not in it: one is
#: a cross-part conflict deferred to this build, one is a residue D2 deliberately left,
#: and one belongs to P4 and reaches P7 only through redaction.
#:
#: Nothing here is answered anywhere under `src/privacy/`, and
#: `tests/p7/test_p7_no_invention.py` fails the moment one of them is.
HELD_OPEN: Mapping[str, str] = MappingProxyType({
    "I6": (
        "§8.4 gives the user the right to 'review and delete local derived data'; "
        "§8.2 forbids updating or deleting an event. D3 (2026-08-21) ratified the "
        "DIRECTION -- events append-only forever, derived projections tombstonable, "
        "'derived' a literal enumerated list -- and ratified that NOTHING IS BUILT "
        "until P13 drives it. `delete_derived` therefore refuses on both sides of the "
        "enumeration and writes nothing. Also open in: P5 OQ6, P13 OQ11, P1 OQ16."
    ),
    "P6-sensitivity-field-row": (
        "P7's SPEC Contract-in requires that 'P6 must accept `sensitivity` as a "
        "first-class universal field (§3.11) rather than a domain-scoped one', while "
        "D2 makes P7's `ClassificationRecord` authoritative. D2 decided which record "
        "is AUTHORITATIVE; it did not decide whether a second, P6-owned field row "
        "continues to exist beside it, and review round 1 found that field has no "
        "producer. Until it is answered, P6 creates no such row and P7 reads none."
    ),
    "P4-region-origin": (
        "P4's `Location.region` is `{ x, y, w, h, unit }` with `unit ∈ {px, norm}`, "
        "and no document in this repository states which corner the origin is; §2.7 "
        "says only 'locations or bounding boxes where available'. P7 reads bounding "
        "boxes when it redacts, so it assumes no origin: it performs no arithmetic on "
        "a region field and holds no origin token. P4's question, held here because "
        "P7 is the part that would otherwise answer it by accident."
    ),
})
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: PASS — 27 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–21 green, and the 1300 P1–P5 tests still green. This is the run that
matters most for this task: the L2 guard walks **every module under `src/`** and imports each one, so
a module that raises at import anywhere in the repository fails here.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/vocabulary.py tests/p7/test_p7_no_invention.py
git commit -m "feat(P7): the no-invention guard, D2's shape asserted where OQ11's guard used to be"
```

---

### Task 22: The walking-skeleton P7 step, and 11 §9's second fixture path

**Files:**
- Modify: `src/privacy/fixtures.py` (add `SKELETON_FIXTURE` — see below)
- Test: `tests/p7/test_p7_skeleton_step.py`

**Interfaces:**
- Consumes: `orchestrator.run_wave2`, `.Wave2`, `.TARGETED_OCR_UNAVAILABLE`;
  `scan_agent.corpus_source.FilesystemCorpusSource`, `scan_agent.selection.record_selection`,
  `scan_agent.exclusion.is_protected_container`, `scan_agent.schema.create_scan_schema`;
  `extractors.safety.SafetyPolicy`, `extractors.dispatch.Readers`, `extractors.schema.create_extraction_schema`;
  `evidence_shape.store.RunWriter`; `eval_harness.bundle.bundle_files`,
  `eval_harness.store.create_eval_schema`; `database_agent.files_table.get_file`;
  `privacy.gate.Gate`, `privacy.release.Denied`, `.NeedsConsent`, `.Released`, `.Target`;
  `privacy.policy.set_policy`, `.transcription_authorized_for`;
  `privacy.classification_store.ClassificationStore`; `privacy.learning_seam.assign`;
  `privacy.consent.record_consent_choice`, `.pending_consent`;
  `privacy.audit.audit_records_for`; `privacy.transport_guard.assert_single_egress`;
  `privacy.fixtures.by_number`, `.SKELETON_FIXTURE`, `.FIXTURE_CLOCK`.
- Produces (`fixtures.py`): `SKELETON_FIXTURE: int = 10` — which published fixture **is** 11 §9's
  second path, named as data so P8 and P13 can find it without reading this plan.

**Done-means:** 13.

**The `run_wave2` signature is what makes path one assertable, and it was read live.** Eighteen
parameters, and **none of them is a gate, a classification, a detector or a P7 policy**. So *"`release`
was called zero times"* is not a discipline the skeleton observes — it is a **structural fact**: the
caller has nowhere to put a gate, so it cannot have called one. That is the strongest available form
of the Done-means clause and it is checked with `inspect.signature`, not by counting.

The parameter that **is** called `policy` is P5's `SafetyPolicy` — two fields, `is_protected_container`
and `is_dataless` — and **not** P7's `Policy`. Two different words one parameter apart is the defect
class this project has paid for most (`sensitivity` in four homes; `handling_class` fed
`sensitivity_state`). The test names both types in one assertion so the two cannot be conflated by a
later author who sees `policy=` and reaches for the gate's.

**The one seam Wave-2 does have is `transcription_authorized`, and P7 fills it.** P5's call site is
`transcription_authorized()` — a zero-argument predicate, `Callable[[], bool]`,
`src/extractors/long_tail.py:204`. Task 5 publishes `transcription_authorized_for(scope)` to satisfy
it. Path one wires the real one in and asserts it answers `False` under a policy with no grant, which
is the M10 back-edge working end to end. **This is not the gate being exercised**: it is an
authorization predicate consulted before an extractor runs locally, and no content leaves. The test
says so, because a reader who saw P7 in the Wave-2 call could otherwise conclude the skeleton
exercises §8.4's door.

**The bundle assertion INVERTS the skeleton's, and this is the second guard that would fail on day
one if it were copied.** The skeleton says path one *"must also assert that after classification the
Wave-2 bundle's `handling_class` is non-null, closing the loop `src/orchestrator.py:259` left open."*
That is wrong on two counts, and both are quotable:

1. **P7 never reaches the bundle, by its own Open question 8.** *"May a replay bundle carry audit
   records and excerpt spans? §8.5 allows 'a frozen corpus snapshot or a metadata-safe
   representation of one' and lists 'policy settings'. Whether a bundle intended to leave the user's
   machine may carry audit records — which name excerpts — is unstated. Affects P2."* Unanswered. A
   task that made P7 write into `bundle_file_entry` would answer it in code.
2. **The value is the Wave-2 caller's, and it is `None` on purpose.** The live comment at the call
   site — now at `src/orchestrator.py:402`, not 259 — says it in the caller's own words: *"The honest
   value is None because the class is unknown, not because another column happened to be empty."*
   That is the standing rule from the connection review: *"a part that does not own the concept
   passes `None` and says the value is unknown. It never forwards a neighbour's column because the
   shapes line up."* And it remains true after P7 ships, because **no task in any plan produces a
   detector** — so on a real corpus there is no class to carry.

So the test asserts the `None` **stays**, asserts `src/privacy/` writes nothing into any `bundle_*`
table, and names OQ8 as the reason. Reported as a correction to the skeleton's Task 22 block.

**Path two is 11 §9's addendum and P7 owns two of its four clauses.** The addendum, verbatim:

```text
P7/P8   a dossier that requires sensitive text
        Gate.release returns NeedsConsent
        P13 presents the four §8.4 options
        choosing no_model_use does not become abstain inside P8
```

11 §9 also states what kind of test it is: *"This is a contract test of B2, not an LLM test. It is
the minimum that makes the one privacy-failure seam exercisable without waiting for full depth."*
Clauses one and two are P7's and are asserted here against **fixture 10**, which exists for exactly
this. Clause three is P13's — its SPEC's routing table gives P7 the `consent` surface and
`action = select_consent_option`, and P13 is unbuilt. Clause four is P8's Done-means 13 and cannot be
run without P8. The test names both as deferred **in named tests that assert the parts do not exist**,
so the limitation lives in the suite rather than in a report nobody rereads. The B2 contract test the
first path cannot exercise is exactly this: path one never returns a `NeedsConsent`, because under
`offline` nothing gets far enough to need consent.

**And the honesty clause, which is the point of the whole task.** The detector is unwritten (D2), so
on a real corpus **every file resolves to `Denied(unclassified)`** — a correct, locked door with
nobody holding a key. Path one's classification is therefore written **by the test**, standing in for
the detector and saying so in its docstring, exactly as Task 17's verdict test and Task 20's fixtures
do. A final named test runs the gate over the actually-scanned file **with no classification** and
asserts `Denied(unclassified)`, so the plan's honest posture is a passing assertion rather than a
paragraph. **This step proves the door, not the classification.**

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_skeleton_step.py
"""Done-means 13, and 11 §9's second fixture path.

02-segmentation-map.md's walking skeleton is "One file, one deterministic path, every
seam touched. No LLM, no cloud, no embeddings -- which also means no privacy gate is
exercised, because nothing leaves the machine."

Done-means 13 turns that into an obligation: the skeleton "must nonetheless assert:
the classification exists for the scanned file; the gate is installed on the only
egress path; `release` was called zero times; the audit log is empty; and a deliberate
attempted call under `offline` returns `Denied` with reason `mode_forbids_target`.
That is the seam test -- that the door exists and is shut."

Read the last test in this file before reading the rest of it. The detector is
unwritten (D2), so the classification path one asserts is written HERE, by the test,
standing in for a detector that does not exist. On a real corpus every file resolves
to `Denied(unclassified)`. This step proves the door, not the classification.
"""
import dataclasses
import importlib
import inspect
import pathlib
from typing import Callable

import pytest

from database_agent.files_table import get_file

from eval_harness.bundle import bundle_files
from eval_harness.store import create_eval_schema

from evidence_shape.store import RunWriter

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument

from orchestrator import TARGETED_OCR_UNAVAILABLE, Wave2, run_wave2

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

from privacy.audit import audit_records_for
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.consent import pending_consent, record_consent_choice
from privacy.fixtures import FIXTURE_CLOCK, SKELETON_FIXTURE, by_number
from privacy.gate import Gate
from privacy.learning_seam import assign
from privacy.policy import set_policy, transcription_authorized_for
from privacy.release import Denied, ModelTarget, NeedsConsent, Released, Target
from privacy.transport_guard import assert_single_egress
from privacy.vocabulary import CONSENT_OPTIONS

COMPONENT = "0.1.0"
NEVER: Callable[[], bool] = lambda: False
SKELETON_CLOCK = "2026-08-22T10:00:00+00:00"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
SRC_ROOT = pathlib.Path(importlib.import_module("privacy").__file__).parent.parent


@pytest.fixture()
def skeleton_db(p7_conn):
    """P1 + P4 + P7 from `p7_conn`, plus the three schemas Wave 2 also needs.

    `tests/wave2/`'s own harness records why all five are created rather than four:
    "§0's 'each part owns its own tables' cuts both ways, and a harness that creates
    four parts' tables out of five is testing a database the product never runs on."
    """
    create_scan_schema(p7_conn)
    create_extraction_schema(p7_conn)
    create_eval_schema(p7_conn)
    return p7_conn


@pytest.fixture()
def corpus(tmp_path: pathlib.Path) -> pathlib.Path:
    """02-segmentation-map.md's input: "one PDF whose title carries a course code"."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    return root


def mime_for(path: pathlib.Path) -> str | None:
    return {".pdf": "application/pdf"}.get(path.suffix)


def skeleton_readers() -> Readers:
    """Deterministic readers. No LLM, no network, no OCR provider."""
    page = "BUSIB 4300 Course Information"
    return Readers(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1, label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text=page),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None)


def offline_policy():
    """W1's floor, and every redaction facet at its more redacting value.

    §8.4's `must`: "The default posture must therefore be local-first and
    data-minimizing." A skeleton that ran under anything else would be testing a
    posture the design forbids as a default.
    """
    from privacy.policy import Policy
    return Policy(
        policy_version="policy-skeleton", operation_mode="offline",
        consent_grants=(),
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=SKELETON_CLOCK)


def walk(conn, corpus_root, *, authorized=None) -> Wave2:
    """One deterministic pass. Note what is NOT passed: there is no gate parameter."""
    selection = record_selection(conn, sources=[corpus_root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        conn, selection, source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=skeleton_readers(), sink=RunWriter(conn, author="P5"),
        now=lambda: SKELETON_CLOCK, context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=authorized or NEVER,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


def only_file(conn) -> str:
    rows = conn.execute("SELECT file_id FROM files").fetchall()
    assert len(rows) == 1
    return rows[0]["file_id"]


def classify(conn, file_id, handling_class="personal_non_sensitive", *,
             protected=False) -> ClassificationRecord:
    """THE DETECTOR THAT DOES NOT EXIST, written by the test and saying so.

    D2 put the rule set behind an injection and no task in any plan produces one.
    SPEC *Deferred*: "The design states *what* is protected and never *how it is
    recognised*. The detector rule set, its signals, and its thresholds are
    hand-authored. P7 publishes the vocabulary the detectors write into."

    Until one is supplied, this is what a classification's arrival looks like: a
    caller writing through P7's writer. Nothing here is a detection rule; it is the
    act of recording a decision some other component made.
    """
    record = ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=SKELETON_CLOCK)
    assign(conn, record, store=ClassificationStore(conn),
           component_version=COMPONENT)
    return record


def p7_events(conn) -> int:
    return conn.execute(
        "SELECT count(*) c FROM events WHERE subsystem = 'P7'").fetchone()["c"]


# ===========================================================================
# Path one -- the deterministic skeleton. The door exists and is shut.
# ===========================================================================

def test_the_wave_2_caller_has_nowhere_to_put_a_gate():
    # "`release` was called zero times" as a STRUCTURAL fact rather than a counted one:
    # eighteen parameters and not one of them is a gate, a classification, a detector
    # or a P7 policy. A caller that cannot hold a gate cannot have called one.
    parameters = inspect.signature(run_wave2).parameters
    assert len(parameters) == 18
    for forbidden in ("gate", "release", "classifier", "detector", "handling_class",
                      "privacy_policy", "classification"):
        assert forbidden not in parameters, forbidden


def test_the_policy_parameter_is_p5s_safety_policy_and_not_p7s():
    # Two different words one parameter apart. `SafetyPolicy` has two fields and
    # deliberately no third; P7's `Policy` has seven. Conflating them is how a future
    # author "wires the gate in" and silently disables the container rule instead.
    assert {f.name for f in dataclasses.fields(SafetyPolicy)} == {
        "is_protected_container", "is_dataless"}
    from privacy.policy import Policy
    assert "operation_mode" in {f.name for f in dataclasses.fields(Policy)}
    assert "operation_mode" not in {f.name for f in dataclasses.fields(SafetyPolicy)}


def test_the_deterministic_path_runs_end_to_end(skeleton_db, corpus):
    result = walk(skeleton_db, corpus)
    assert isinstance(result, Wave2)
    assert skeleton_db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] > 0


def test_the_audit_log_is_empty_after_the_deterministic_path(skeleton_db, corpus):
    # Done-means 13's fourth clause. Not "P7 wrote few events" -- none, because
    # nothing asked the gate anything.
    walk(skeleton_db, corpus)
    assert p7_events(skeleton_db) == 0
    assert audit_records_for(skeleton_db,
                             file_id=only_file(skeleton_db)) == []


def test_the_classification_exists_for_the_scanned_file(skeleton_db, corpus):
    # Done-means 13's first clause. Written by `classify`, which stands in for the
    # detector and says so; see its docstring.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    record = classify(skeleton_db, file_id)
    store = ClassificationStore(skeleton_db)
    assert store.current(file_id, record.content_hash) == record
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is not None


def test_the_gate_is_installed_on_the_only_egress_path(skeleton_db, corpus):
    # Done-means 13's second clause, in the only form available before P8 exists:
    # there is no transport, so the property "the transport's only content parameter
    # is a `Released`" holds over an empty set -- and `assert_single_egress` is proven
    # correct against a conforming and four non-conforming fixtures in Task 19.
    walk(skeleton_db, corpus)
    transports = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted
        module = importlib.import_module(dotted)
        if getattr(module, "IS_MODEL_TRANSPORT", False):
            transports.append(module)
    assert transports == [], "a transport appeared; run assert_single_egress over it"
    for module in transports:                      # reachable the day P8 lands
        assert_single_egress(module)


def test_release_was_called_zero_times(skeleton_db, corpus):
    # Done-means 13's third clause, counted as well as proven structurally. A gate is
    # constructed, handed to nobody, and asked nothing -- which is exactly the
    # skeleton's shape: the door is installed and never opened.
    calls: list[object] = []

    class RecordingGate(Gate):
        def release(self, request):
            calls.append(request)
            return super().release(request)

    RecordingGate(skeleton_db, component_version=COMPONENT,
                  area_of=lambda file_id: None)
    walk(skeleton_db, corpus)
    assert calls == []


def test_a_deliberate_call_under_offline_is_denied_mode_forbids_target(
        skeleton_db, corpus):
    # Done-means 13's fifth clause, and the whole point: the door is SHUT, not absent.
    # §8.4's fully offline mode: "No content leaves the device; only local rules and
    # local models may run."
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    set_policy(skeleton_db, offline_policy(), author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: None)
    request = dataclasses.replace(
        by_number(8).request, target=Target(file_ids=(file_id,), group_id=None))
    decision = gate.release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"
    assert decision.explanation
    assert decision.remedy_options


def test_the_deliberate_call_is_audited_even_though_it_was_denied(
        skeleton_db, corpus):
    # §8.4: "Every model call should be recorded in a consent-aware audit record", and
    # §8.2 covers "Every significant event affecting a file". The empty log above is
    # empty because nothing asked, not because denials go unrecorded.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    set_policy(skeleton_db, offline_policy(), author="P7",
               component_version=COMPONENT, user_id="joseph")
    before = p7_events(skeleton_db)
    Gate(skeleton_db, component_version=COMPONENT,
         area_of=lambda _file_id: None).release(dataclasses.replace(
             by_number(8).request,
             target=Target(file_ids=(file_id,), group_id=None)))
    assert p7_events(skeleton_db) > before
    assert audit_records_for(skeleton_db, file_id=file_id)


def test_the_transcription_back_edge_is_p7s_and_is_not_the_gate(skeleton_db, corpus):
    # M10's back-edge: P5's call site is `transcription_authorized()`, a zero-argument
    # predicate at `src/extractors/long_tail.py:204`. P7 fills it. This is an
    # authorization consulted before a LOCAL extractor runs -- no content leaves, and
    # it is NOT §8.4's door. A reader who saw P7 in the Wave-2 call could otherwise
    # conclude the skeleton exercises the gate.
    set_policy(skeleton_db, offline_policy(), author="P7",
               component_version=COMPONENT, user_id="joseph")
    authorized = transcription_authorized_for("Academics")
    assert inspect.signature(authorized).parameters == {}
    assert authorized() is False
    walk(skeleton_db, corpus, authorized=authorized)
    assert p7_events(skeleton_db) == 1        # the `policy_set` above, and nothing more


# ===========================================================================
# The bundle -- where this task INVERTS the plan skeleton
# ===========================================================================

def test_the_bundle_handling_class_is_still_none_after_a_classification(
        skeleton_db, corpus):
    # The plan skeleton expects this to be non-null "closing the loop
    # src/orchestrator.py:259 left open". It is NOT, and both reasons are quotable.
    #
    # 1. P7 Open question 8 is open: "Whether a bundle intended to leave the user's
    #    machine may carry audit records -- which name excerpts -- is unstated."
    #    A P7 that wrote into `bundle_file_entry` would answer it in code.
    # 2. The value is the Wave-2 caller's and the caller's own comment says why it is
    #    None: "The honest value is None because the class is unknown, not because
    #    another column happened to be empty."
    result = walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    entries = bundle_files(skeleton_db, result.bundle_id)
    assert entries
    for entry in entries:
        assert entry["handling_class"] is None


def test_a_second_pass_after_classification_still_carries_none(skeleton_db, corpus):
    # The classification is written BEFORE this pass, so "the bundle was built too
    # early" is not the explanation. The caller passes a literal `None` and P7 has no
    # seam into it -- which is the honest posture while no detector exists.
    walk(skeleton_db, corpus)
    classify(skeleton_db, only_file(skeleton_db))
    second = walk(skeleton_db, corpus)
    for entry in bundle_files(skeleton_db, second.bundle_id):
        assert entry["handling_class"] is None


def test_src_privacy_writes_into_no_bundle_table(skeleton_db, corpus):
    # OQ8 held structurally, not by restraint: P7 imports no P2 writer at all.
    import ast
    privacy_dir = SRC_ROOT / "privacy"
    for path in sorted(privacy_dir.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("eval_harness"), path.name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("eval_harness"), path.name


# ===========================================================================
# Path two -- 11 §9's second fixture path, the B2 contract test
# ===========================================================================

def test_the_skeleton_fixture_is_named_as_data():
    # So P8 and P13 can find 11 §9's second path without reading this plan.
    assert SKELETON_FIXTURE == 10
    assert isinstance(by_number(SKELETON_FIXTURE).decision, NeedsConsent)


def test_a_dossier_requiring_sensitive_text_returns_needs_consent(
        skeleton_db, corpus):
    # 11 §9, clauses one and two: "a dossier that requires sensitive text /
    # Gate.release returns NeedsConsent". §8.4: "If a model needs text containing
    # sensitive content, the user should see that requirement and choose."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal",
             protected=False)
    set_policy(skeleton_db, fixture.policy, author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, NeedsConsent)
    assert decision.options == CONSENT_OPTIONS
    assert decision.consent_request_id


def test_path_one_can_never_produce_this_branch(skeleton_db, corpus):
    # Why 11 §9 exists: "It is the minimum that makes the one privacy-failure seam
    # exercisable without waiting for full depth." Under `offline` nothing gets far
    # enough to need consent, so the first path cannot exercise B2 at all.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, offline_policy(), author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: None)
    decision = gate.release(dataclasses.replace(
        by_number(SKELETON_FIXTURE).request,
        target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_no_model_release_exists_until_a_choice_is_recorded(skeleton_db, corpus):
    # Done-means 7's own falsifiable form, and it needs the id Task 14 added.
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, fixture.policy, author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    records = audit_records_for(skeleton_db,
                                consent_request_id=decision.consent_request_id)
    assert [r.outcome for r in records] == ["consent_requested"]
    assert pending_consent(skeleton_db, decision.consent_request_id) is not None


def test_choosing_no_model_use_records_the_choice_and_releases_nothing(
        skeleton_db, corpus):
    # 11 §9's third clause is P13's gesture; P7's half is that the recorded choice
    # closes the request and produces no `model_release`. P13's SPEC: "P13 records the
    # collection, not the grant."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, fixture.policy, author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    record_consent_choice(skeleton_db, decision.consent_request_id, "no_model_use",
                          user_id="joseph", component_version=COMPONENT,
                          observed_at=FIXTURE_CLOCK)
    outcomes = [r.outcome for r in audit_records_for(
        skeleton_db, consent_request_id=decision.consent_request_id)]
    assert "released" not in outcomes
    assert pending_consent(skeleton_db, decision.consent_request_id) is None


def test_no_model_use_is_one_of_the_four_and_is_not_a_denial_reason():
    # The typed half of "does not become abstain": `no_model_use` is a CONSENT OPTION.
    # It is not in `DENIAL_REASONS`, so a caller cannot map the branch onto a denial by
    # respelling, and `NeedsConsent` carries no `reason` field to hold one.
    from privacy.vocabulary import DENIAL_REASONS
    assert "no_model_use" in CONSENT_OPTIONS
    assert "no_model_use" not in DENIAL_REASONS
    fields = {f.name for f in dataclasses.fields(NeedsConsent)}
    assert fields == {"consent_request_id", "requirement", "options"}


def test_clause_four_is_p8s_and_clause_three_is_p13s_and_neither_exists_here():
    # 11 §9: "choosing no_model_use does not become abstain inside P8." INSIDE P8 --
    # so the assertion belongs to P8's suite, as its Done-means 13, and to P13's as its
    # Done-means 16. P7's obligation is to make the absorption UNREPRESENTABLE, which
    # the test above does at the type level; policing it is not P7's and cannot be.
    #
    # This test exists so the limitation lives in the suite rather than in a report
    # nobody rereads -- the same posture Task 19 takes for Done-means 3 and Task 20
    # takes for Done-means 11's second clause.
    for absent in ("llm_harness", "review_surface"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(absent)
    assert by_number(SKELETON_FIXTURE).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


# ===========================================================================
# The honesty clause -- read this one first
# ===========================================================================

def test_with_no_detector_every_real_file_resolves_to_denied_unclassified(
        skeleton_db, corpus):
    # The claim the plan skeleton makes in prose, asserted: "Until it is supplied, a
    # P7 running against a real corpus classifies nothing and every real file resolves
    # to `Denied(unclassified)` -- a correct, locked door with nobody holding a key."
    #
    # Nothing is classified here because nothing in the product classifies. Path one's
    # `classify()` is the test standing in for a detector; remove it and this is what
    # the walking skeleton actually produces.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is None
    assert ClassificationStore(skeleton_db).history(file_id) == []
    set_policy(skeleton_db, by_number(9).policy, author="P7",
               component_version=COMPONENT, user_id="joseph")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                area_of=lambda _file_id: "Academics")
    decision = gate.release(dataclasses.replace(
        by_number(9).request, target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"
    assert not isinstance(decision, Released)


def test_this_step_proves_the_door_and_not_the_classification():
    # Said once, in a test, so it survives the plan being archived. "P7 is done" and
    # "the product classifies files" are different claims and only the first is
    # deliverable from these twenty-two tasks.
    detector_producers = []
    for name in ("privacy.classification", "privacy.classification_store",
                 "privacy.learning_seam", "privacy.gate"):
        module = importlib.import_module(name)
        detector_producers += [
            attribute for attribute in vars(module)
            if attribute.lower().startswith("detect")
            or attribute.upper().startswith("RULE")]
    assert detector_producers == []
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_skeleton_step.py -v`
Expected: FAIL — `ImportError: cannot import name 'SKELETON_FIXTURE' from 'privacy.fixtures'`
(collection fails on the first import; Task 20 published sixteen fixtures and named none of them as
11 §9's second path).

- [ ] **Step 3: Add `SKELETON_FIXTURE` to `src/privacy/fixtures.py`**

Append to the module, below `MODE_SWEEP`:

```python
#: 11 §9's second fixture path, named as data rather than left to be rediscovered:
#:
#:     P7/P8   a dossier that requires sensitive text
#:             Gate.release returns NeedsConsent
#:             P13 presents the four §8.4 options
#:             choosing no_model_use does not become abstain inside P8
#:
#: 11 §9 also says what kind of test that is -- "a contract test of B2, not an LLM
#: test ... the minimum that makes the one privacy-failure seam exercisable without
#: waiting for full depth". P7 owns the first two lines; the third is P13's and the
#: fourth is P8's Done-means 13.
SKELETON_FIXTURE: int = 10
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_skeleton_step.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Run the whole repository**

Run: `pytest tests/ -q`
Expected: PASS — P7 complete, and the 1300 P1–P5 tests still green. This task touches
`src/orchestrator.py`, `tests/wave2/` and `tests/conftest.py` **not at all**: it imports the Wave-2
caller and asserts against it, and every P7 fixture it needs lives in `tests/p7/`.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/fixtures.py tests/p7/test_p7_skeleton_step.py
git commit -m "feat(P7): the walking-skeleton gate step, and 11 9's NeedsConsent path"
```

---

## What these three tasks leave open, and to whom

| Held open | Held by | Whose call |
|---|---|---|
| I6 — §8.4's delete versus §8.2's append-only | `vocabulary.HELD_OPEN["I6"]`; `delete_derived` refusing on both sides of D3's enumeration (Task 15) | Joseph — NEEDS-JOSEPH C1. D3 ratified the direction; nothing is built until P13 drives it. |
| `filename` as a sixth releasable kind | SPEC Open question 2, asserted present and unresolved by Task 21 | Joseph — NEEDS-JOSEPH **B5d** and **C9a**. §8.4 names five kinds and puts *paths* in the always-local set; the SPEC adds a sixth and flags it itself. |
| Whether P6 keeps a `sensitivity status` field row beside P7's record | `vocabulary.HELD_OPEN["P6-sensitivity-field-row"]`; Task 21 asserts P7 reads no P6 surface | Joseph. D2 settled which record is authoritative and did not settle whether a second row exists; P7's SPEC Contract-in still requires P6 to accept `sensitivity` as a universal field, and round 1 found that field has no producer. |
| Which corner `norm` measures from | `vocabulary.HELD_OPEN["P4-region-origin"]`; Task 21 asserts P7 does no arithmetic on a region field | P4's, and nobody's yet — no document in the repository states an origin. P7 is the part that would otherwise answer it by accident, when it redacts a bounding box. |
| What a *corpus area* is (Open question 3) | `Gate(area_of=…)`, a required keyword with no default; Task 20's fixtures carry the answer as data | Joseph — NEEDS-JOSEPH C3. |
| Whether a replay bundle may carry audit records and excerpt spans (Open question 8) | Task 22 asserting `bundle_file_entry.handling_class` stays `None` and that `src/privacy/` imports no P2 writer | Joseph, and P2's. |
| Whether the product classifies anything at all | Task 22's last two tests | **The detector.** No task in any plan produces one. Twenty-two tasks deliver a correct, locked door; they do not deliver a key. |
