# 4. The privacy gate and the model harness

P7 and P8 are one story told in two halves. P7 decides whether anything about a file may
leave the machine and mints a single-use token that says so. P8 is the only thing in the
product that could spend one. Neither half is exercised on the run the product actually
ships, and the interesting part of this section is exactly *why* that is true and what it
costs.

Everything below was read out of `src/`. Where a SPEC promises something the code does not
do, the section says so and cites the line.

---

## 4.0 Two corrections to the map before we start

Two things a reader arriving from the SPECs or from a briefing will have wrong.

**The module names differ from the SPEC's prose.** `src/privacy/` holds twenty-two modules,
not the seven a summary would name: `gate.py`, `release.py`, `denial.py`, `consent.py`,
`policy.py`, `defaults.py`, `binding.py`, `items.py`, `redaction.py`, `resolve.py`,
`classification.py`, `classification_store.py`, `audit.py`, `moves.py`, `display.py`,
`revocation.py`, `learning_seam.py`, `transport_guard.py`, `schema.py`, `vocabulary.py`,
`authorship.py`, `fixtures.py`. The decomposition matters: several of the properties P7
claims are structural are structural *because* a rule lives in a module that cannot reach
the thing it must not touch.

**A detector does ship, and it is wired.** The claim that "no detector ships" is false as of
this commit. `src/recognition/detector.py` implements `orchestrator.ClassificationProducer`;
`src/cli.py:565` constructs one from a compiled 358-row rule library and hands it to the
production run at `src/cli.py:393`; `src/orchestrator.py:713` calls it once per file version
and `:722` writes the result. What is true — and what makes the "no detector" claim
*directionally* right — is that the detector is deliberately built so that it classifies
almost nothing. §4.1 works through why.

---

## 4.1 What a handling class is, and how a file gets one

### The closed set

§8.4 names five handling classes. `src/privacy/vocabulary.py:86-92` publishes them in the
design's order:

```
public_low · personal_non_sensitive · sensitive_personal ·
highly_sensitive_credential_bearing · unreadable_unclassified
```

Closed means a caller may not add a member. `check_handling_class` (`vocabulary.py:105`)
routes through `_check` (`vocabulary.py:58`), and `_check` does something unusual: it
refuses an outsider **without naming any member of the set**. The docstring gives the
reason — `check_handling_class("public")` answering with a suggestion of `public_low` is how
a misspelling becomes a silent downgrade, which is the failure §8.6 names by name
(`vocabulary.py:59-67`). The design's own vocabularies are carried beside the identifiers as
prose (`HANDLING_CLASS_LABELS`, `vocabulary.py:96`; `MODE_SEMANTICS`, `vocabulary.py:119`)
so that a paraphrase is a failing test rather than a drift.

### The record

`ClassificationRecord` (`classification.py:107`) is eight fields: `file_id`, `content_hash`,
`handling_class`, `protected`, `basis`, `evidence_refs`, `reliability_state`, `observed_at`.
Three of its construction-time checks are load-bearing:

- **It is keyed on bytes.** `content_hash` is required non-empty. A classification is about a
  file *version*; new bytes at a path inherit nothing (`classification.py:10-13`).
- **`basis = detector` must carry evidence.** `classification.py:155` raises
  `UnbackedClassification` for a detector classification with an empty `evidence_refs`,
  quoting §8.4's "evidence-backed". `user` and `safety_domain` are exempt — the user's act
  *is* the evidence, and a safety domain is a rule about a domain rather than a reading of a
  span (`classification.py:70-72`).
- **Every ref must be a P4 `observation_key`, never an `observation_id`.**
  `_is_observation_key` (`classification.py:92`) validates by *shape*, derived at import from
  one probe key (`classification.py:77-79`) so that a change in P4's hashing propagates
  rather than drifting. The reason is M14: a per-row id dies on extractor upgrade, so a
  negative example recorded today would silently stop resolving and the same false
  protection would return (`classification.py:163-167`).
- **`protected` is supplied, never derived.** `classification.py:142` requires a real bool
  and the docstring cites Open question 1 — whether `protected` is exactly the top two
  classes is unsettled, so nothing in the codebase infers one from the other.

### The store

`ClassificationStore` (`classification_store.py:117`) is concrete, not injected — D2 removed
the old `SensitivityFacts` seam. It never overwrites: the table has a `BEFORE UPDATE` trigger
over all eight published fields (`schema.py:63-67`) and a `BEFORE DELETE` trigger
(`schema.py:58`), so supersession is the only legal write to an existing row. The index is
deliberately **not** unique (`schema.py:52`) — an early detector and a later one may disagree
and both survive, which is §8.2's own OCR example.

`current` resolves several live rows through `strongest` (`classification_store.py:88`),
which ranks by §3.13's six reliability states in the design's listed order, derived from P4's
tuple with `rejected` removed in place (`classification_store.py:56`). A tie raises
`AmbiguousCurrentClassification` rather than picking.

### How a file actually gets one, today

`recognition/detector.py` is two steps with a contract between them. *Recognition* says which
domain schema a file version's own P4 observations make plausible. *Classification* says
which handling class it carries. The rule library carries no handling class at all —
`planning/domains/_CONTRACT.md` rule 5 forbids it: "A catalogue that assigns one is inventing
P7's vocabulary" (`detector.py:11-14`). So `handling_for` is an injected map with no default.

`Detector.explain` (`detector.py:296`) runs, in order:

1. **Protected container first, before any evidence is read.** `is_protected_container` is
   P3's own predicate, and a hit returns `Abstention("protected_container", ...)` whose
   sentence is *"marked, counted and never opened; it is unclassified because nothing
   looked, not because nothing was found"* (`detector.py:309-314`).
2. No authored term matched → `Abstention("no_evidence")`.
3. Fewer than two distinct matched terms for the leading schema → `Abstention`
   `"no_corroboration"`. All 358 rows set `file_kinds.never_alone: true`, read literally as
   "two" (`detector.py:24-32`, `:330-338`).
4. Leading schema implausible for this file kind → `"file_kind_implausible"`.
5. Two schemas tied → `"ambiguous"`. Nothing breaks the tie; a tie-breaker would be the
   invented threshold this package exists without (`detector.py:354-356`).
6. Schema recognised but the caller's `handling_for` states no class for it →
   `"unassigned_handling"`. "Recognition is not classification" (`detector.py:367-378`).

`cli.py:566` passes `handling_for=SAFETY_DOMAIN_HANDLING`, which covers exactly four schema
ids — `finance`, `identity`, `medical`, `legal` (`recognition/vocabulary.py:64`) — each
mapped to `sensitive_personal`, `protected=True`, `basis=safety_domain`
(`detector.py:117-121`). The class is the detector's own hand-authored choice and says so:
`00` names five classes and never says which one a safety domain carries
(`detector.py:106-116`).

**Consequence.** Every file that is not decisively one of four safety domains, on two or more
authored terms, on a plausible file kind, with no tie, resolves to `Abstention`.
`Detector.__call__` (`detector.py:392`) turns an `Abstention` into `None`, and
`resolve_class(None)` returns `unreadable_unclassified` (`classification.py:179-180`). On an
ordinary folder of coursework, invoices and screenshots, the overwhelming majority of files —
plausibly all of them — carry no classification record at all.

### Why absence never resolves downward

`resolve_class` is four lines and its docstring is the whole argument: a file that has not
been classified has not met §8.4's precondition for escalation, "so the gate denies it rather
than guessing at it downward" (`classification.py:170-186`). There is no
default-to-`public_low` code path anywhere under `src/privacy/`; the module docstring states
this as a property of the file (`classification.py:4-8`) and §8.6 supplies the reason: *"Cost
exhaustion must never turn into lower-quality automatic classification."* Defaulting an
unclassified file to public so the pipeline can continue is precisely the failure that
sentence forbids.

`src/cli.py:351-372` records the same argument being lost and then recovered. This deployment
used to classify every unrecognised file `highly_sensitive_credential_bearing,
protected=True` as a precaution, because P11 raised on an unclassified file and one such file
refused an entire corpus. The comment on the fix is the clearest statement of the principle
anywhere in the repo: *"'We deliberately did not look' and 'we could not tell' are different
answers, they ask the user for different things, and a product that says the first when it
means the second is lying in the direction that happens to feel safe."*

---

## 4.2 `unreadable_unclassified` is a gate outcome, not a file fact

This is D2, and it is enforced structurally in four places rather than by discipline.

- **The module that produces the value cannot reach a column.** `classification.py` contains
  no writer at all: no `set_`, `write_`, `record_`, `mirror_` or `update_`, and it does not
  import `database_agent.files_table`. The docstring states this as the mechanism: *"'Nothing
  has looked' and 'this file carries nothing' must never become the same value in the same
  column, and the durable way to hold them apart is for the string meaning the first to be
  produced by a decision function in a module that can reach no column"*
  (`classification.py:17-24`).
- **The store refuses it as a row.** `ClassificationStore.write` raises
  `GateOutcomeNotAFileFact` (`classification_store.py:129`).
- **The store refuses it as a projection.** `mirror_state` raises the same
  (`classification_store.py:197`), so it can never reach `files.sensitivity_state`.
- **A detector cannot assign it.** `Handling.__post_init__` raises
  (`recognition/detector.py:87-91`).

The distinction exists because absence of a record already carries the meaning. A stored row
saying `unreadable_unclassified` would claim, as a fact, exactly what the absence of a row
says — and the two could then disagree (`classification_store.py:23-26`).

`completeness_implies_unclassified` (`classification.py:228`) is the adjacent reader: it maps
each of P4's nine completeness markings to whether a run at that marking leaves nothing to
classify, with the deciding sentence carried per value in `COMPLETENESS_RULE`
(`classification.py:194-225`). Six of the nine imply unclassified. **It has no caller in
`src/`.** It is a published predicate nothing asks.

### The defect fixed on 2026-08-29

`planning/66-FIND-FILE-AND-ONBOARDING.md` §4 forbids five states from sharing one message:
*"'Protected by your privacy policy' means the product deliberately did not reveal more.
'Unreadable' means the product could not obtain usable content. 'Still indexing' … 'Unsupported
format' … 'No strong match' … These states should never share one vague message such as
'could not find.'"*

The user-facing sentence for a privacy-blocked, unclassified file used to end *"nothing has
been able to read enough of it"*. Commit `53c41d1` caught it on a live run: all four files
had a `direct` fact in `file_facts` and zero rows in `classifications`. Reading is the step
that **worked**, and it was the step the sentence blamed — two of §4's five states sharing
one message. The current sentence is at `src/placement/pipeline.py:585-590`:

> "This file has not been classified -- nothing has yet said what kind of material it is --
> so it was not shown to a model and nothing moved."

The comment above it states the discipline that produced it: P11 knows nothing classified the
file; whether it was *readable* is P4's `extraction_runs`, which P11 does not read and must
not guess at, "so the sentence names the step that stopped and claims nothing about the one
before it" (`placement/pipeline.py:570-584`).

The same conflation survives one layer down. See §4.12, finding 3.

---

## 4.3 The policy: modes, grants, redaction

### One version is the whole snapshot

`Policy` (`policy.py:122`) carries `operation_mode`, `consent_grants`, `redaction_settings`,
`automatic_move_permissions`, `plan_version`, `set_at` and its own `policy_version`. All of
it travels together, and a change to any of it mints a new version
(`policy.py:5-11`). The reason is a binding one: `policy_version` is a term of every release
binding, so a consent grant that did not mint a new version would leave a release minted
before the grant still spendable after it — "the least acceptable silent change in the
product".

The caller may not supply a version: `_persist` raises `CallerSuppliedPolicyVersion` unless
`policy_version == UNSET_POLICY_VERSION` (`policy.py:209`). The row and its event commit in
one transaction (`policy.py:260-266`) so a committed policy change cannot exist with no event
accounting for it. Supersession is enforced by trigger (`schema.py:94-98`).

`grant_consent` and `revoke_consent` derive a *complete* next snapshot from the one handed
in, so the supplied version is a concurrency token: `_require_in_force` raises
`StalePolicyVersion` inside the write transaction (`policy.py:185-203`). `set_policy` is
exempt — it replaces rather than derives.

### The four modes and what `offline` costs

`OPERATION_MODES` (`vocabulary.py:112`) is `offline · local_model · hybrid · cloud_assisted`,
with the design's four sentences carried verbatim (`vocabulary.py:119-129`).

The only predicate that reads the mode for egress is `mode_forbids`
(`denial.py:151`): it returns True when `locality == "cloud"` and the mode is one of
`("offline", "local_model")` (`denial.py:86`). It refuses the *target's locality*, never the
call — a local model is permitted under both, per §8.4's "only local rules and local models
may run".

**The shipped deployment chooses `offline`.** `src/cli.py:150`:

```python
OPERATION_MODE: str = "offline"
```

with the comment: *"`offline` is chosen, not defaulted: it is the only mode under which
nothing about any file can leave the device, and a first run on somebody's home directory is
not the moment to ask for less."* `cli.py:658-667` puts it in force with
`consent_grants=()`, `redaction_settings={}`, `automatic_move_permissions={}`.

### `local_only` versus `dossier_permitted` is P11's vocabulary, not P7's

This pair does not exist in `src/privacy/`. It is P11's `model_eligibility`
(`placement/vocabulary.py`), and `placement/privacy.py:14-16` says so plainly: *"`model_eligibility`
is DERIVED rather than read, because §8.4's three values have no producer in
`src/privacy/` at all."*

`privacy_state_for` (`placement/privacy.py:100`) derives it from three P7 authorities
(`placement/privacy.py:125-133`):

```python
unclassified = handling_class == UNREADABLE_UNCLASSIFIED and unclassified_denies(
    locality=CLOUD, local_calls_on_unclassified=False)
local_only = (unclassified
              or mode_forbids(policy.operation_mode, CLOUD)
              or protected)
```

Under `offline`, `mode_forbids(..., "cloud")` is True for every file, so **every file in
every shipped run is `local_only`** regardless of its classification. The classification only
changes *which sentence the person reads*, not the outcome.

### The model-release decision, and the two open questions the code refuses to close

`unclassified_denies` (`denial.py:177`) has no default for
`local_calls_on_unclassified` — Open question 5 ("does `unreadable_unclassified` permit a
*local* model call?") is unanswered, so the caller answers it and P7 names no winner. The
`Gate` constructor takes it as a required keyword (`gate.py:96`, constructor at `:95-102`), alongside two more
required, defaultless parameters for the same reason: `classifier`/`transform` (identifier
classes and the redaction transform are enumerated nowhere in the design) and `scope_for`
(Open question 3, "what is a corpus area?"). `gate.py:14-21` names all three.

`P11` answers OQ5 in one direction and says so at the call site: it passes
`local_calls_on_unclassified=False` but only ever asks about `cloud`, where the answer is
True before the flag is read (`placement/privacy.py:121-126`).

### W1's local-first floor is built and unreachable

`privacy/defaults.py` is the whole of §8.4's *"The default posture must therefore be
local-first and data-minimizing"*. `LOCAL_FIRST_MODES` is `(offline, local_model)`
(`defaults.py:52`); `MORE_REDACTING` maps all five display facets to `redacted`
(`defaults.py:55`); `_check_install_mode` raises `DefaultPostureViolation` for `hybrid` or
`cloud_assisted` (`defaults.py:67`); `resolve_default_policy` fills absent facets but leaves
a user-set one alone (`defaults.py:96`); `assert_local_first` raises on a cloud starting mode,
an unresolved facet, or any facet left shown (`defaults.py:108-129`). The module reads no
file, no environment variable and no build flag, deliberately: "a module that cannot reach
one cannot be handed a mode by one" (`defaults.py:31-34`).

**None of `effective_policy`, `resolve_default_policy` or `assert_local_first` has a caller
anywhere in `src/`.** `defaults.py:102` calls `effective_policy` "the one composition the gate
calls" — the gate does not call it. `Gate.release` calls `current_policy` directly and raises
`NoPolicyInForce` when nothing is stored (`gate.py:123-130`), explicitly deferring the floor
to a module nobody invokes. `display_policy` reaches the same floor by re-implementing the
fill against `MORE_REDACTING` (`display.py:110-115`) rather than composing
`resolve_default_policy`, and `moves.py:28-32` explains at length why it too declines to
compose it.

---

## 4.4 Release: the ledger, what may leave, and the audit record

### The request carries references only

`ModelCallRequest` (`release.py:113`) has exactly seven fields: `stage`, `target`,
`model_target`, `requested_items`, `prompt_template_id`, `prompt_fingerprint`,
`max_dossier_tokens`. No field accepts a document string, a path, or an `Observation`
(`release.py:116-120`). `call_site` is deliberately *not* a field — B2 puts it inside
`prompt_fingerprint` (`release.py:121-122`).

`release.py` also publishes two guards *as data* so a test asserts against a named constant
rather than a literal: `RELEASE_PARAMETERS = {"self", "request"}` (`release.py:270`) proves no
unpublished parameter exists on `Gate.release`, and `FORBIDDEN_PARAMETER_NAMES`
(`release.py:278`) is a fourteen-word blacklist compared token-wise so that a legitimate
`unclassified_permits_local` is not caught by substring matching.

### The six releasable kinds and the nine that are not

`ITEM_KINDS` (`vocabulary.py:157`) is `excerpt`, `redacted_identifier`, `candidate_label`,
`metadata_field`, `evidence_reference`, `filename`. §8.4 names five; `filename` is the sixth
and it is held unratified. `items.py` builds it, names it, and makes it **unadmittable**:
`check_item` raises `UnratifiedItemKind` unless the caller passes `allow_unratified=True`
(`items.py:281-290`), and the exception is deliberately not one of the eight denial reasons
because "this is a build defect, not a policy outcome, and it must reach the developer rather
than a user who might try to consent around it" (`items.py:69-75`).

`ALWAYS_LOCAL` (`vocabulary.py:142`) is §8.4's nine. Two of the refusals fire at
*construction*, not at the gate: `MetadataField.__post_init__` raises `AlwaysLocalRequested`
for a name that normalises to one of the nine (`items.py:165`), and `Filename.__post_init__`
raises for a `file_id` containing a path separator — "a path wearing an id's field name"
(`items.py:186-193`). A request naming one of the nine is therefore not constructible, so it
cannot be a fixture either.

`items.py` is candid about the limits of this. `_normalise` is `strip().lower().replace(" ",
"_")` and nothing wider (`items.py:85-92`); the consequence, stated in the module docstring,
is that `MetadataField(name="current_path")` is **not** caught, "and that gap is deliberate
and tested: a synonym list would be a detection rule P7 is forbidden to own"
(`items.py:26-30`).

The one per-value sensitivity signal in the product is P5's, read through
`sensitive_observation_keys` (`items.py:320`): an `Excerpt` whose key P5 marked
`POTENTIALLY_SENSITIVE` is refused as `always_local_item`, with the remedy that the same key
is releasable as a `RedactedIdentifier` (`items.py:302-309`). An empty set means *nothing was
signalled*, never *nothing is sensitive*.

### The decision order, published as data

`DECISION_ORDER` (`release.py:259`) is:

```
collect_request_denials · needs_consent · materialise ·
collect_content_denials · append_audit · mint_release
```

It is forced, not chosen: nothing materialises until every check that could deny has run,
because a gate that resolved first would hold the text in memory before deciding it was
allowed to (`release.py:255-258`). `denial.py` states the same principle as
`DECIDABLE_FROM_REQUEST` (`denial.py:76`) — six of the eight reasons need only the request,
the policy and a row lookup, and every one of them precedes the two that need resolved text.
`Gate.release` asserts the first element on entry (`gate.py:122`).

The gate decides no precedence itself: it collects *every* triggered reason into a dict of
builders and asks `first_reason` which wins (`gate.py:212`, `denial.py:136`), because
`DENIAL_ORDER` (`denial.py:63`) is `denial.py`'s and a second total order in the gate would be
a second home for it.

### The eight denial reasons

`DENIAL_REASONS` (`vocabulary.py:180`): `protected_cloud_target`, `unclassified`,
`policy_revoked`, `protected_records_template`, `whole_document_requested`,
`dossier_over_budget`, `always_local_item`, `mode_forbids_target`. There is deliberately no
bare `protected` — collapsing the two protected reasons would produce a denial that cannot
say which rule fired (`vocabulary.py:175-179`).

Every `Denied` requires a non-empty explanation *and* at least one remedy
(`release.py:231-240`, `denial.py:119-128`): "a denial with no legitimate alternative is a
dead end the user cannot act on (§8.6)". `denial.py` is explicit that `unclassified` is the
ordinary case and is written for it — "it carries the longest explanation and the most
remedies, because it is what the audit log will be full of" (`denial.py:3-8`).

### The ledger is what makes a `Released` a capability

`Released` (`release.py:181`) is an ordinary frozen dataclass; anyone may construct one and it
buys nothing. The authority is the ledger. `mint_release` (`binding.py:112`) inserts
`(release_id, model_target, prompt_fingerprint, policy_version, audit_id, minted_at,
spent_at=NULL)` with `release_id = "release-" + secrets.token_hex(16)`.

`consume_release` (`binding.py:132`) is ordered: **issued, then bound, then spent**.

1. Not in the ledger → `ReleaseNotIssued`. This is the refusal that makes the door real
   (`binding.py:70-76`).
2. Any of the three binding terms differs → `BindingMismatch`, before any spend. "A mis-wired
   caller must not be able to burn an authorization the user granted"
   (`binding.py:15-17`).
3. The `Released`'s own echoed `model_target` / `policy_version` must agree with the call.
4. `UPDATE ... WHERE spent_at IS NULL`; `rowcount != 1` → `ReleaseAlreadySpent`. The check and
   the mark are one statement so single use survives a concurrent second caller
   (`binding.py:179-185`).

`audit_id` is carried and never compared — B2's rule that two releases differing only in audit
record are the same authorization. It is `NOT NULL` in the DDL because `append_event` returns
`lastrowid`, so a mint with no audit id is a mint whose audit record was never written and
SQLite refuses it (`binding.py:18-22`, `binding.py:63`).

### The audit record, and what "egress" means

§8.4 requires six fields. `AuditRecord` (`audit.py:90`) carries nineteen plus three, and lands
them under three constraints that are jointly satisfiable exactly one way (`audit.py:9-14`):
P1's `append_event` accepts seventeen named columns and rejects an eighteenth; §8.2's list is
fixed at eleven forever; B5 settles that there is **one** log. So five fields land in columns
— `file_id`, `content_hash`, `prompt_fingerprint`, `observed_at`, `user_id`
(`audit.py:61-63`) — and the other sixteen become canonical JSON in `explanation`, which is
§8.2's own "structured explanation or evidence reference" slot. P7 adds no column to `events`.

Two properties are structural rather than procedural:

- **`audit_id` cannot exist before the record does.** It *is* the `event_id` a completed
  insert returns (`audit.py:139-150`), so §6's ordering guarantee — the audit record is
  appended before `Released` is returned — is not a discipline anyone can forget.
  `Gate.release` shows the sequence at `gate.py:272-287`: `append_audit`, then `mint_release`,
  then construct `Released`.
- **The record says what left without holding a copy of it.** `excerpts_included` is
  `(observation_key, span)` pairs; re-running `resolve.materialise` over them reproduces the
  payload exactly (`audit.py:20-25`). §8.4 puts raw sensitive values in the always-local set
  and the text already exists once.

**What may leave.** Only `Excerpt` and `RedactedIdentifier` are text-bearing
(`gate.py:78`); `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry
no local content and are never materialised and never echoed back. `_materialise`
(`gate.py:467`) is the only path from a reference to a string, through
`resolve.materialise` — "the one module under `src/privacy/` that binds a P4 text
materialiser". The redaction it applies replaces the *value* and not its context, and the
released type has no place to put the context: `ReleasedItem` (`release.py:159`) carries
`observation_key`, `span`, `value`, `zone`, `unit_length` and deliberately no
`context_before`/`context_after`, with the docstring recording the bug that made this
necessary — "for as long as this type was `Materialised`, an 8-character requested span
released every character of its 61-character unit, the value redacted and the account number
beside it not" (`release.py:166-171`).

**What never may.** Paths are never releasable in any form. §8.4's nine always-local names are
unconstructible as a request item, and the `filename` reading — that a directory path is not a
filename, which is the only reading under which §7.3's carve-out is not vacuous — is adopted,
flagged, and gated behind an explicit `allow_unratified` (`vocabulary.py:151-156`,
`items.py:281`).

### Consent events

`NeedsConsent` (`consent.py:155`) carries `consent_request_id`, a `ConsentRequirement`, and
`options`, which must be §8.4's four **in order** — fewer raises `IncompleteConsentOptions`,
quoting P13: "A surface that offers fewer has silently made the user's decision for them"
(`consent.py:172-176`). It carries **no `reason` field**, and that is load-bearing: it is not
a `Denied` in disguise and cannot be mapped onto a denial reason by accident
(`consent.py:13-15`).

There is no consent table. The log is the state (`consent.py:22-26`), which is what makes
Done-means 7 falsifiable: a `consent_requested` event and no `model_release` for that request
until a choice is recorded. `open_consent_request` (`consent.py:213`) writes one audit record
with `outcome="consent_requested"` and the requirement carried as `(observation_key, span)`
pairs — never the text, because "a consent prompt that embedded the value would have released
it in order to ask permission to release it" (`consent.py:143-146`).

`grant_authorizes` (`consent.py:98`) is the table that says which *target* an answer
authorizes: `local_model → {local}`, `cloud_model → {local, cloud}`, `redacted_prompt →
{local, cloud}`, `no_model_use → {}` (`consent.py:90-95`). The comment records the bug it
fixes: the gate used to keep only the scope and drop the option, "so answering `local_model` to
a local-model prompt authorized a CLOUD release of the same protected file". A table rather
than a chain of `if`s, "for the reason `CONSENT_AUTHORIZES` is one: the negated form is a
single edit away from silently granting."

### Revocation

`revoke` (`revocation.py:125`) is forward-only. It requires a non-empty `retraction_limit` —
§8.4 makes the statement mandatory and the SPEC defers its wording to P13, so presence is
enforced and no sentence lives in P7 (`revocation.py:139-145`). It calls `revoke_consent` to
mint the new version, reads the prior releases out of the one audit log, and appends one
`consent_revoked` event. `_prior_releases` (`revocation.py:167`) is deliberately **not**
filtered to the revoked policy version: §8.4's purpose is to tell the user what has already
been sent, and a list narrowed to one version answers a different question.

`delete_derived` (`revocation.py:190`) always raises, on both sides of D3's literal
enumeration: `ScopeNotDerived` outside it, `UnratifiedResolution` inside it. There is no third
branch, no tombstone column exists, and the function writes nothing. `Gate.delete_derived`
(`gate.py:368`) is `staticmethod` returning `NoReturn`, because "D3 built no tombstone column,
so there is nothing here that could read or write one".

---

## 4.5 Protected material

`protected` is a boolean on the record, supplied by whoever classified and never derived from
the handling class. Open question 1 leaves the relation between flag and class unsettled, and
every consumer in the codebase reads the flag:

- **Egress.** `protected_cloud_denies` (`denial.py:196`) returns False unless the file is
  protected *and* the target is cloud; the carve-out is `cloud_assisted` plus an explicit
  grant naming this scope. `scope` is an opaque string because Open question 3 is open.
- **Movement.** `may_move_automatically` (`moves.py:88`) checks **absence first**, then the
  flag, then the policy. The order is not interchangeable: checking the flag first would
  answer `not_protected` for every file in a corpus nothing has classified, which is §8.6's
  forbidden move reached from a different direction (`moves.py:93-98`). Four closed reasons:
  `unreadable_unclassified` (bound to `resolve_class(None)` rather than typed a second time,
  `moves.py:58`), `not_protected`, `policy_permits`, `protected_without_permitting_policy`.
  P11 asks it rather than re-deriving it (`placement/privacy.py:162`) and only for protected
  files, "not an optimisation, it is the only case the answer can change"
  (`placement/pipeline.py:295-303`).
- **Display.** `summarize_protected` (`display.py:124`) returns counts only, with
  `class_breakdown` over every file in scope by resolved class and `scope_total` separated
  from `count` "because they answer two questions, and one number cannot answer both without
  lying about one" (`display.py:135-140`).
- **Prompts.** `ProtectedItemRequested` (`items.py:78`) refuses a `filename` on a protected
  file **for any target**, because §7.3's sentence carries no locality qualifier
  (`items.py:292-300`).

### The standing rule: marked and counted, never opened

The rule holds at three layers and no layer trusts the one above it.

1. **P3** writes an exclusion verdict for a protected container and creates no `files` row for
   anything inside it, so a file inside one never acquires the `(file_id, content_hash)` pair
   the gate keys on.
2. **The detector** checks `is_protected_container` *first*, before it reads even a stored
   observation, and returns an abstention naming the file rather than an error or a silent
   skip. The comment says why the check is there at all given P3: "this should be unreachable
   through a live scan -- it is here because a detector must not be the part that makes it
   reachable" (`detector.py:304-314`).
3. **The report** prints the count and the labels and never the contents.
   `src/cli.py:881-887`: `"Protected containers: {n} marked, none opened"`, then per area a
   display label and a path, then *"Nothing inside these was read, indexed, classified or
   moved, and none of them is a place anything can be filed."*

`vocabulary.py:31-39` pins the distinction that makes this legible: five strings share the
stem "protected" and no two are the same word. P3's `untouched_protected` and
`protected_container` are about **reading**; P7's `protected` flag,
`protected_cloud_target` and `protected_records_template` are about **release**, which is a
policy the user can override through consent. `src/privacy/` imports neither of P3's
constants.

---

## 4.6 `sensitivity_policy_ref`: carried, required, read by nothing

Verified by exhaustive grep over `src/`. `sensitivity_policy_ref` appears in exactly four
files, all under `src/tree_design/`:

- `templates.py:301` — a required `str` field on `TemplateDefinition`.
- `templates.py:338` — `_require(self.sensitivity_policy_ref, ...)`, so an empty one is a load
  error.
- `template_schema.py:81, 216-218` — the JSON schema requires it as a non-empty string.
- `catalogue.py:94` — read out of the raw JSON into the dataclass.
- `fixtures.py:394` — one fixture value, `"policy.public"`.

Nothing reads `.sensitivity_policy_ref` off a `TemplateDefinition` anywhere. Nothing under
`src/privacy/` or `src/llm_harness/` mentions the name at all. It is an **inert field**: every
one of the shipped template definitions must carry one, and no code path consults it.

What it is eventually for: `66` §4 makes the *wording and visible level of detail* of a
protected result follow the user's protected-display policy — "On a shared screen, even
'Identity documents' may reveal more than the user wants; a generic protected count may be
safer." A template's `sensitivity_policy_ref` is the per-destination hook for that: the
policy a node's contents are displayed and searched under, so that a Finance branch can be
visible as a protected area without its filenames being visible (§5.2). P7's SPEC *Deferred*
places the templates' `privacy rules` / `sensitivity policy` fields outside its contract as
hand-authored per-template content; the field is the slot that content will land in. Today the
slot is empty of consequence.

---

## 4.7 P8: what a dossier is, and why a model never sees a file

A dossier is the model's entire world for one call. `Dossier` (`records.py:328`) carries
`dossier_id`, `call_site`, `subject_ref`, `eligibility_reason`, `plan_version`,
`policy_version`, `allowed_vocabulary`, `evidence_items`, `conflicts`, `released_evidence`,
`max_dossier_tokens`, `reduction_rung`, `release_id`. It refuses to exist without a
`policy_version` and a `release_id`: "Dossier is content-bearing only after P7 release"
(`records.py:354-358`).

The asymmetry that makes the gate unbypassable is that P8 holds two different shapes for the
same evidence:

- `EvidenceItem` (`records.py:218`) — the *builder's* reference metadata: `evidence_ref`,
  `kind`, `location`, `excerpt_span`, `reliability_state`, `basis`. No value. This is what
  goes into the `ModelCallRequest`.
- `ReleasedEvidence` (`records.py:241`) — one P7 `ReleasedItem` as the model saw it:
  `observation_key`, `address`, `value`, `zone`. This only exists after `Gate.release`
  returned, and `build_dossier` constructs it from `released.materialised_items`
  (`dossier.py:45-54`).

`ReleasedEvidence` also carries a fixed leak in its docstring: it used to hold
`context_before`/`context_after`/`context_truncated`, copied from P7 into the canonical
model-visible bytes, "and nothing in P8 ever read them" — so the three fields were removed
from the record rather than emptied in it (`records.py:246-253`, `dossier.py:67-79`).

`dossier_id` is the content address of the model-visible bytes, deliberately not the
`release_id`: a release id is a single-use spend capability, so using it as an identity meant
two calls over identical content had two identities and no call could be recognised as a
replay of another (`dossier.py:11-14`, and `CallPayload` refuses `dossier_id ==
release_id` at `records.py:135-140`).

Call eligibility is closed per site. `ELIGIBILITY_BY_SITE` (`vocabulary.py:150`) maps the five
sites to closed reason lists quoted from the design, and `assess_call` (`eligibility.py:60`)
returns `PreCallAbstention(NOT_ELIGIBLE_FOR_MODEL)` for a reason outside its site's list —
before anything is reserved or released.

---

## 4.8 The validation architecture

### Universal validation

`validate_response` (`validation.py:440`) parses the response bytes once, keeps them
untouched, and checks claims in input order. No model is consulted anywhere.

Per claim (`_validate_claim`, `validation.py:316`):

1. Not a mapping, or a non-mapping payload → `reject` / `SCHEMA_INVALID`.
2. `unknown` present → `abstain`, with no reasons and `may_propose=False`. `unknown` plus a
   non-empty `citations` list is `SCHEMA_INVALID` — the two are mutually exclusive.
3. No citations and no `unknown` → `reject` / `UNCITED_CLAIM`. This is the "cites nothing"
   case, and it is never softened into a low-confidence accept (`validation.py:365-374`).
4. Every citation checked. Any failure → `reject` carrying every failing code.
5. The injected `contradicts` oracle. **`None` is `ValidationUnavailable`, not a pass**
   (`validation.py:411-412`).
6. Acceptance split: if every cited evidence item's `basis` is `context-supported`, the
   outcome is `accept_context_supported`; otherwise `accept_direct`
   (`_acceptance_outcome`, `validation.py:306`). `basis` is supplied by the builder and never
   inferred by P8.
7. The site validator may replace the verdict.

### The citation check: two checks, two sources

`_check_citation` (`validation.py:130`) is the mechanism the whole grounding claim rests on:

- `CITATION_NOT_IN_DOSSIER` — the ref is not among the dossier's `evidence_items`, or it is
  but nothing about it was released.
- `CITATION_NOT_FOUND` — `evidence_resolver(ref)` returns `None`; this resolves against the
  store.
- `CITATION_SPAN_MISMATCH` — the quoted span is compared against **`released.value`**, what
  the model actually saw, and never against P4's stored raw text. The docstring gives the
  reason: with redaction on, matching against the store "would accept a quotation the model
  could not have read and reject the one it did" (`validation.py:137-142`).

Three fixed bugs are recorded in place, and each is worth reading as evidence of what this
check is exposed to:

- An empty `cited_span` used to reach the substring test, where `"" in anything` is True, "so
  neither check ever ran" (`validation.py:168-172`).
- Site A ran its own citation check against P6's `FactRequest` — every observation for the
  file version — and set `span_matched` to a copy of `resolved`. "A key P7 withheld, quoted
  with a span the model invented, was accepted and the fact was written"
  (`check_citations`, `validation.py:187-192`).
- `run_call` used to take a `site_validator` callable straight from the caller. `lambda *a,
  **k: None` was a valid value "and it disabled every site-specific check … while the
  universal citation checks still ran and the result still looked like a real verdict"
  (`sites.py:4-8`). The mapping from call site to validator is now fixed in `sites.dispatch`
  and callers may inject only *authorities*.

### The verdict

`P8Verdict` (`records.py:388`) enforces three invariants at construction:
`accept_context_supported` always sets `requires_review=True` (`records.py:418`); `weak`
forbids `may_propose=True` (`records.py:422`); and every `reason` must be in
`ALL_REASON_CODES` (`records.py:410`). `outcome`, `disposition` and `scope` are each checked
against their closed vocabulary.

`OUTCOMES` and `DISPOSITIONS` are two vocabularies, not one — the outcome is uniform across
sites and the disposition names what the owning part does with it (`vocabulary.py:40`,
`:388`).

A call that produced several verdicts returns exactly one, chosen by
`worst_outcome` (`harness.py:311`) against `OUTCOME_SEVERITY`
(`vocabulary.py:50`, worst first). The docstring records why this is one function and not two:
the shard reducer used severity and the claim reducer took the last verdict by position, "so a
two-claim response whose FIRST claim was rejected returned `accept_direct`. A caller told
`accept_direct` must be able to take it as true of the whole call."

### Per-site fact validation

`sites.dispatch` (`sites.py:255`) routes by `dossier.call_site` and requires a typed authority
bundle per site; a missing one is `ValidationUnavailable`, never a pass. `SiteDependencies`
(`sites.py:84`) rejects a bare callable outright: "P8 owns which validator runs at each site
and takes no acceptance callback" (`sites.py:102-105`).

Site A alone writes into another part's store — `apply_verdict` writes P6's fact or its
`unresolved` row — which is why `apply_consequence` has no default and separates a live call
from a replay (`sites.py:270-276`). `_fact_site` (`sites.py:176`) parses every claim, refuses
a response with two claims about one field because `claim_ref` is the field key and two
verdicts would be indistinguishable (`sites.py:208-213`), and hands both P6's bare-key
`Proposal` and P8's span-carrying `Citation` list down, "because a key alone cannot say
whether the model quoted what P7 released or invented the quotation" (`sites.py:140-143`).

`_addressed_to_the_response` (`sites.py:233`) appends a digest of the response bytes to every
`verdict_id`. The reason is a real crash: `verdict_id` was `dossier_id:claim_ref`, "which is
the identity of a question rather than of an answer", and `llm_verdict.verdict_id` is a
primary key — so a re-scan of an unchanged file collided on the insert "and crashed out of
`run_call` with the reservation already taken."

Sites C and D each call an injected `sensitivity_policy(dossier, payload) -> bool` and reject
on False, as `SENSITIVITY_POLICY_VIOLATION` (`placement_validation.py:237-238`) and
`SENSITIVITY_RESTRICTION_IGNORED` (`placement_validation.py:328-329`). P8 authors neither
predicate; `placement/p8_seam.py:83, 96` constructs the dependency objects that would carry
them.

---

## 4.9 Budgets, ceilings, and failing closed

### Refused before it is made

Three things can stop a call before `Gate.release` is even asked:

1. **Ineligibility.** `assess_call` returns `PreCallAbstention(NOT_ELIGIBLE_FOR_MODEL)` for a
   reason outside the site's closed list (`eligibility.py:69-74`).
2. **A standing user rejection.** `suppressed_by_learning` (`eligibility.py:37`) queries P1's
   `learning_records` for a matching `(proposal_class, basis_key)` with `polarity == reject`
   and returns `USER_REJECTED_EQUIVALENT`. Equivalence is that pair, not dossier bytes.
3. **The token ceiling.** `plan_reduction` (`budgets.py:297`) walks §8.6's ladder — unreduced,
   summarized, anchors, split — over *injected* fit flags. P8 measures nothing: "Fit flags are
   injected; this module does not measure." Nothing fits → rung `deferred` and a
   `PreCallAbstention`.

Then, per unit, `reserve_call` (`budgets.py:166`) takes a scan-scoped reservation in one
conditional SQL statement (`_RESERVE_COUNTER_SQL`, `budgets.py:31`) that inserts-or-increments
only while `calls_reserved + 1 <= allowed` and the cost ceiling holds. No row returned →
`BudgetExhausted` → `PreCallAbstention(BUDGET_EXHAUSTED)` and the loop breaks
(`harness.py:429-440`).

**`call_refused` is a real event and it is written on both refusal paths.** Every refusal
produces a *zero-count grounding report* — `report_for_pre_call_terminal`
(`validation.py:506`) builds one with all nine counts at zero, a one-entry histogram naming
the reason, `reduction_rung = deferred` for `BUDGET_EXHAUSTED` and `none` otherwise, and
`release_audit_id=None`. `record_refusal` (`store.py:320`) and `record_pre_call_abstention`
(`store.py:339`) each write a typed row, the report, and one `call_refused` event
(`_append_call_refused`, `store.py:303`) in a single transaction. So a gate `Denied`, an
ineligible call, a suppressed equivalent and an exhausted budget are each first-class recorded
outcomes with a code, never a silent skip — which is §8.6's requirement that the interface
distinguish completed from deferred work. `NeedsConsent` writes none of the three, and that is
the point.

### Fail closed

"Fail closed" here has a precise meaning and it is not "return a safe default". Every missing
capability is a distinct, non-outcome value:

- `ValidationUnavailable` (`records.py:556`) names the missing injected capabilities and is
  documented as "Never an abstain outcome". A missing `contradicts` oracle, a missing site
  bundle, a missing `evidence_resolver`, a missing `conn` — all become this, and none becomes
  a pass or a verdict.
- `CallResult` (`records.py:536`) refuses to wrap a `NeedsConsent` at all.
- `run_call` checks *every* field of `CallDependencies` before doing anything
  (`harness.py:111-152`), and checks the site's own request requirements before the spend —
  `_missing_request_inputs` (`harness.py:155`) exists because `record_cd_verdict` used to raise
  for a missing `evidence_snapshot_id` "only after the release was consumed, the model was
  called and the response was stored: a call paid for that produced no verdict and no report."
- The reservation is released on **any** exception between reserve and settle
  (`harness.py:470-477`), not just the gate's terminal branches — "a binding mismatch, an open
  transaction, a malformed record, an interrupt … removed a call and its estimated cost from
  the scan budget permanently, with nothing left holding the reservation id."

### The release-consuming transport: the gate is asked before assembly

The ordering in `run_call` is the whole of P8's egress claim, and it is visible in one
sequence (`harness.py:424-478`):

```
reserve_call → gate.release(unit.model_call_request) → build_dossier(request, released)
             → build_call_payload → record_dossier → issue(...)
```

`build_dossier` (`dossier.py`) takes `released` as a required argument and reads
`released.materialised_items` to construct the only content-bearing part of the dossier. There
is no path that assembles a dossier and then asks. `NeedsConsent` and `Denied` both release
the reservation and return before `build_dossier` is reached (`harness.py:448-456`), and
`NeedsConsent` is returned **unchanged** — no verdict, no abstention, no report, no event.

`transport.issue` (`transport.py:163`) is the only egress. It refuses an already-open
transaction so a rollback cannot unspend a release after bytes have left
(`transport.py:151-156`); recomputes the fingerprint and the model-visible bytes from
immutable sources and raises if they do not match (`_require_sources`, `transport.py:82`);
checks that `model_client.model_target == payload.model_target == released.model_target`
(`transport.py:95-104`); then, inside one transaction, consumes the release and appends
`model_call_issued`; and only then calls `model_client.invoke(payload.model_visible_bytes)`.
`ModelClient` (`transport.py:49`) is target-bound — its `model_target` is a field, so "callers
cannot supply a second destination to invoke".

`privacy/transport_guard.py` is the mechanised inspection behind P7 Done-means 3. It resolves
annotations with `inspect.signature(..., eval_str=True)` rather than scanning source text,
walks containers and unions, requires exactly one public entry point, bans `Path` /
`Observation` / `TextUnit` module-wide and `str` / `bytes` on the egress surface, and requires
the entry point to take a `Released` (`transport_guard.py:332-...`). `assert_single_call_site`
(`transport_guard.py:303`) is a second instrument over the module's AST, because a second
`model_client.invoke(...)` inside the one entry point changes no signature. Both are called
only from `tests/`; nothing in `src/` invokes them.

---

## 4.10 What actually happens on the shipped run

`src/cli.py` is the only composition root a person can run. Three lines decide everything in
this section.

```python
OPERATION_MODE: str = "offline"                                   # cli.py:150
model_route_permitted=lambda file_id: False                       # cli.py:327
embeddings=EmbeddingsOff(), p8_run_call=None, p8_authorities=None # cli.py:757
```

`production.CorpusAuthorities.__post_init__` enforces that `p8_run_call` and `p8_authorities`
are both present or both absent (`production.py:405-409`), and `None` for both "is a legal
deterministic run: `group_subject` returns a candidate with `no_model_call_configured` rather
than synthesising a verdict" (`production.py:369-371`).

The consequences, each verified by grep over `src/`:

- **No `Gate` is ever constructed.** `Gate(` appears in `src/` only inside
  `privacy/fixtures.py:288`'s docstring. `Gate.release` is therefore never called, no release
  is ever minted, `release_ledger` stays empty, and no `model_release`,
  `model_release_denied` or `consent_requested` event is ever appended. The audit log is empty
  by construction, which is exactly what P7's Done-means 13 walking-skeleton obligation
  asserts.
- **No model client, no prompt, no budget.** `ModelClient(`, `PromptDefinition(`,
  `ScanBudget(` and `CallDependencies(` have no constructor call anywhere in `src/` outside
  `llm_harness/fixtures.py`.
- **P8's tables are never created.** `create_llm_schema` (`schema.py:205`) and
  `create_budget_schema` (`budgets.py:141`) have no caller in `src/`. `production.py:238-246`
  creates P1's, P3's, P4's, P5's, P6's, P7's and P2's schemas and not P8's. If a model were
  wired tomorrow without also wiring these, `record_dossier` would fail on a missing table
  after the release was already minted and the audit record already written.
- **The deterministic engine's answer is what a person gets.** `FactResolver` ships with
  `stages={"direct": ..., "rule": None, "llm": None}` and `None` means "this stage does not
  exist" rather than "an empty one", "so a fact this run could not reach stays unresolved and
  visible instead of being recorded as absent" (`cli.py:318-327`).
- **Every file is `local_only` anyway.** Under `offline`,
  `mode_forbids(policy.operation_mode, "cloud")` is True unconditionally, so
  `privacy_state_for` returns `LOCAL_ONLY` for every file regardless of class or flag
  (`placement/privacy.py:127-133`).
- **Nothing moves.** `automatic_move_permissions={}` (`cli.py:663`), so
  `may_move_automatically` returns `protected_without_permitting_policy` for every protected
  file and `unreadable_unclassified` for every unclassified one. The only `allowed=True` branch
  a shipped run can reach is `not_protected`, for a file the detector classified into one of
  the four safety domains — which by construction it never does, since all four are
  `protected=True`.

So the product a person runs today is: a scanner, a reader, a deterministic fact engine, a
tree designer, and a placement engine that names a destination or explains why it cannot. The
privacy gate is a correctly-built door in a wall nobody walks up to. The harness is a
correctly-built validator with no model to validate.

That is the honest v1 posture and `denial.py:3-8` says so in as many words — "a correct locked
door when nobody has been given a key". The cost is that the property most of P7 and P8 exist
to guarantee has never been exercised end to end outside the test suite.

---

## What looks wrong here

Flagged, not resolved. Ordered by how much a real person would care.

**1. The consent loop does not close.** `record_consent_choice` (`consent.py:292`) links a
user's answer to the question by writing `consent_request_id` into a `consent_granted` event,
and `pending_consent` / `ConsentAlreadyRecorded` both look it up with
`json_extract(explanation, '$.consent_request_id')` (`consent.py:205-210`). But for the three
*authorizing* options the function delegates to `policy.grant_consent`
(`consent.py:325`), whose event explanation is built by `policy._explanation`
(`policy.py:230-245`) and contains `policy_version`, `plan_version`, `operation_mode`,
`consent_grants`, `redaction_settings`, `automatic_move_permissions`, `granted_scope`,
`granted_option` — and **no `consent_request_id`**. So: after a user answers `cloud_model`,
`pending_consent` still returns the open question forever, and `ConsentAlreadyRecorded` never
fires, so the same request can be answered again and again. Only `no_model_use` — the branch
that appends its own event at `consent.py:328-340` — is correctly linked. P7 Done-means 7's
falsifiable form ("the audit log holds a `consent_requested` event and no `model_release` for
that request until a choice is recorded") is not decidable from the log as written.

**2. W1's local-first floor is unreachable.** `defaults.py` is complete, tested-looking, and
has zero callers in `src/`. `effective_policy` describes itself as "the one composition the
gate calls" (`defaults.py:102`) and `Gate.release` does not call it — it calls
`current_policy` and raises `NoPolicyInForce` (`gate.py:123-130`). `display.py:110-115`
re-implements the facet fill rather than composing `resolve_default_policy`, so the floor now
has two implementations, one of which is dead. Done-means 12's negative half ("no code path,
build flag, packaged configuration file, or first-run flow produces a starting mode of
`hybrid` or `cloud_assisted`") is satisfied today only because `cli.py:150` happens to write
`"offline"` — not because anything enforces it.

**3. The gate's own `unclassified` explanation still commits `66` §4's error, and puts a JSON
blob in front of a person.** `Gate._completeness` (`gate.py:395`) reads P1's
`extraction_status_by_tier` column — a per-tier JSON map like `{"native": "complete"}` — and
returns `str(stored)`. `deny_unclassified` (`denial.py:306`) then renders it as *"its
extraction completeness is '{...}'"* (`denial.py:315-316`). Two problems. First, that value is
not one of P4's nine completeness markings, which is what `COMPLETENESS_RULE` and the
parameter name both promise; the sentence has the wrong shape of value in it. Second, and
worse, it re-attaches a *reading* claim to a *classification* refusal — the exact conflation
`53c41d1` removed one layer up at `placement/pipeline.py:585`. The fix landed in P11's user
sentence and did not reach P7's.

**4. `ProtectedItemRequested` is denied under the wrong reason.** `Gate._precheck_items`
catches `ProtectedItemRequested` — raised for a `filename` on a protected file
(`items.py:292`) — and maps it to `deny_protected_records_template` (`gate.py:176-179`). That
denial's explanation tells the user the file is *"held under the 'Protected Records' residual
template"* (`denial.py:349-351`), which is a different rule and is almost certainly false:
`template_for` is `None` in every `Gate` construction in the repo, so no file is ever under a
residual template. `vocabulary.py:175-179` argues at length that collapsing the two protected
reasons "would produce a denial that cannot say which rule fired" — and then the gate collapses
them anyway, in the one direction that produces a factually wrong sentence.

**5. `BUDGET_EXHAUSTED` names two different things.** `plan_reduction` returns a
`PreCallAbstention(reason=BUDGET_EXHAUSTED)` when no rung of the token ladder fits
(`budgets.py:351-355`), and `reserve_call` failure produces the same code
(`harness.py:430-434`). The first is a *dossier too large for one call*; the second is *the
scan has spent its call or cost ceiling*. P2's mapping table sends both to `deferred` /
`ceiling_reached`, so a reader of the metrics cannot tell a corpus that ran out of money from
a single unsplittable file. There is no second code and the reason registry has no room for
one.

**6. Supersession only covers one of the three things the SPEC says triggers it.** All five
declared P8 event types are written (`transport.py:182`, `store.py:172`, `store.py:228`,
`store.py:269`, `store.py:303`). But `verdict_superseded` has exactly one route to it:
`supersede_verdict` ← `revalidate_for_plan` (`placement_validation.py:632`) ←
`placement/versions.py:143`, with `reason="plan_or_snapshot_changed"` hard-coded. The SPEC's
*Provenance* section says "A re-run under a new model, prompt, **or validator version**
supersedes"; only the plan-or-snapshot case exists, it applies only at sites C and D, and
nothing in `run_call` supersedes anything. A second call at site A over the same dossier
produces a second independent verdict distinguished only by the response digest
(`sites.py:248`), with no link recording that one replaced the other.

**7. `sensitivity_policy_ref` is a required field with no reader.** Every
`TemplateDefinition` must carry a non-empty one (`templates.py:338`) and nothing consults it.
It is a schema obligation on hand-authored content that buys nothing today, and a field that
has never been read is a field whose values have never been checked against anything.

**8. `always_local` is name-matching, and says so.** `items._normalise` is
`strip().lower().replace(" ", "_")` (`items.py:92`), so `MetadataField(name="current_path")`,
`"filepath"`, `"full_text"` and `"exif_gps"` all pass. The module argues that a synonym list
would be a detection rule P7 may not own (`items.py:26-30`), which is a coherent position —
but the guarantee "nothing in §8.4's always-local set can be named as a releasable item kind"
is then true only of nine exact strings, and the SPEC states it without that qualifier.

**9. Several published surfaces have no caller in `src/`.** Beyond `defaults.py`:
`classification.completeness_implies_unclassified`, `classification.sensitivity_signal_keys`,
`policy.transcription_authorized_for`, `audit.audit_extra`, `consent.pending_consent`,
`consent.record_consent_choice`, `budgets.report_for_budget_exhausted`,
`stage_output.emit_stage_output`, `Gate.reclassify` / `display_policy` /
`summarize_protected` / `revoke` / `delete_derived` (the whole facade, since no `Gate` is
constructed), and both `transport_guard` assertions. Some are legitimately waiting on P13.
`transcription_authorized_for` is different: `extractors/long_tail.py:224` calls a
zero-argument `transcription_authorized()` declared at `:215`, and `TranscriptionAuthorization`
(`policy.py:331`) exists specifically to close over the scope that call site cannot pass — a
seam built for a caller that does not use it.

**10. The one number in `may_move_automatically` that a person can reach is the wrong-shaped
answer.** `moves.may_move_automatically` returns `allowed=True, reason=not_protected` for any
classified, unprotected file (`moves.py:102-104`). Combined with a detector that classifies
only four protected safety domains, the predicate has exactly two reachable answers on a real
corpus — `unreadable_unclassified` (refuse) and `protected_without_permitting_policy`
(refuse). `policy_permits` requires `automatic_move_permissions[file_id] is True`, keyed on
individual file ids; nothing in the product ever writes that map, and it is not obvious that a
per-file-id key is the right granularity for a user policy the design describes in terms of
areas.

**11. The detector's handling-class choice is a P7 vocabulary decision made in P-recognition.**
`SAFETY_DOMAIN_HANDLING` (`detector.py:117`) assigns `sensitive_personal` to all four safety
domains, and the comment admits `00` names no class for them and that this is "this
detector's own hand-authored choice". It is recorded honestly and it is still a policy
decision living in a detection module — the exact boundary
`planning/domains/_CONTRACT.md` rule 5 was written to hold.

**12. A wired model would hit a missing table.** `create_llm_schema` and
`create_budget_schema` have no caller in `src/`, while `run_call`'s success path calls
`record_dossier` *after* `gate.release` has already minted a release and written the audit
record (`harness.py:290`). A deployment that supplied `p8_run_call` and `p8_authorities`
without also calling both schema creators would spend a release, write an audit record saying
content was released, and then crash — leaving a log that says a release happened and no
record of what it carried.
