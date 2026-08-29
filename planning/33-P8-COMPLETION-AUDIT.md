# P8 completion audit

Date: 2026-08-26
Status: **P8 is complete for the scope it owns.** Every release blocker in
`docs/superpowers/plans/2026-08-26-p8-live-composition-repair.md` is closed. The
seams listed in §3 are external and named, not bypasses inside P8.

Suite at the time of writing: **3252 passed, 0 failed.**

This is the document R6 asks for and that nothing in the repo had yet created.

---

## 1. Release blockers — all closed

The repair plan listed five. Each is closed with a test that was watched failing
against the previous code.

| # | Blocker | Closed by | Evidence |
|---|---|---|---|
| 1 | `run_call` sent newline-joined released values and discarded P7 addresses plus builder metadata | `1dd29ba` | `src/llm_harness/dossier.py`; `tests/p8/test_p8_dossier.py` |
| 2 | a caller-supplied `site_validator` could bypass Site A–E validators | `7ccec8f` | `src/llm_harness/sites.py`; `tests/p8/test_p8_sites.py` |
| 3 | citation span matching was not bound to the released material | `195da8c` | `validation.py::_check_citation`; `tests/p8/test_p8_release_binding.py` |
| 4 | dossier identity used the single-use `release_id` | `1dd29ba` | `dossier.build_dossier`; address test in `test_p8_dossier.py` |
| 5 | public surface, P2 tuple binding, event provenance, walking skeleton and determinism proof incomplete | `7049b2b`, `4746b7a`, `911a3db` | `tests/integration/test_p8_walking_skeleton.py`; `tests/p8/test_p8_determinism.py` |

### What each blocker actually cost

Recording these because each shipped green, and the shape recurs.

- **Blocker 1 was two bugs.** The model saw values with no address, zone, context
  or truncation flag — and separately, `_evidence_items` synthesised
  `kind="excerpt"`, `location="body"`, `reliability_state="direct"`,
  `basis=direct-anchor` for every reference. The SPEC says `basis` is *"supplied
  by the dossier builder, never inferred by P8"*. The consequence nobody had
  noticed: Site B's `_dossier_members` reads `kind == "member"`, `run_call` never
  produced one, so **every member P9 proposed would have been rejected as
  invented**. The tests passed because the Site-B tests construct their own
  `Dossier` and never went through `run_call`.
- **Blocker 3 was symmetric.** With redaction on, matching against the store
  accepts a quotation the model could not have read and rejects the only one it
  could.
- **Blocker 4 broke replay in production**, and R5 is where that surfaced.
  `transport.issue` wrote `record_response(dossier_id=payload.release_id)`; once
  `dossier_id` became a content address the response no longer joined to its
  dossier, so `replay_recorded_response` could never find one. The P2 replay test
  passed only because it wrote the response row by hand.

### Defects the repair surfaced that were not on the list

- `fact_validation._verdict` set `dossier_id=request.file_id` — a P6 file id in a
  P8 dossier address field — and `verdict_id = f"{file_id}:{field_key}"`, which is
  a PRIMARY KEY, so a second dossier over the same file and field collided on
  insert. Both now take the dossier's content address (`7ccec8f`).
- The P6 consequence and the P8 verdict about it were two separate transactions.
  A failure between them left P6 holding an `llm_supported` fact whose judgement
  no verdict recorded. Only reachable once R3 connected Site A — before that
  `run_call` never reached P6 at all (`8ac6f42`).
- Integration fixtures cited `obs-key-1`, which is not a P4 observation key (M14
  requires the `sha256:` prefix). Nothing noticed because no test reached P6.

---

## 2. Invariants re-verified

1. **Single egress.** `model_client.invoke` appears at exactly one site in all of
   `src/`: `llm_harness/transport.py:166`. Re-scanned product-wide including
   nested modules and aliases; enforced by a test added in `8edf835`.
2. **Frozen public surface.** `src/llm_harness/__init__.py` exports exactly the
   eight names `planning/30-p8-p9-connection-contract.md` lists.
3. **Reference-only before release.** `DossierRequest` carries no value-bearing
   field; `EvidenceItem` has six fields and none of them is a value.
4. **D14.** `privacy/gate.py:510` writes `release_id=None` on the audit row.
5. **`NeedsConsent` is returned unchanged** and is neither an outcome, a reason
   code, nor a refusal.
6. **No-invention sweep is derived, not listed** (`001a34a`). Both registries are
   computed from the package, so a new public callable or authority bundle cannot
   escape it — the old hand-written lists had already gone stale on four
   callables and two bundles.
7. **Determinism.** The probe replays stored bytes through the dispatcher, emits
   and reads back a real P2 row, and is byte-identical across two independent
   interpreters.

---

## 3. Remaining seams — external, and honest

These are things P8 does not do. Each is somebody else's, and none is a bypass
inside P8: reaching one produces `ValidationUnavailable` or a refusal, never a
pass.

| Seam | Owner | State today |
|---|---|---|
| **Authored prompt text, response schema, shaping policy** | prompt authoring, not yet started | `PromptDefinition` has no defaults for any of the three; a missing one is a construction error. P8 authors none of them. |
| **Deployment transport** | ops | `ModelClient.invoke` is an injected `Callable[[bytes], bytes]`. Every test supplies a recorder. No HTTP client, no credential handling, no retry — Q8 leaves retry disabled at one attempt. |
| **C-5 normalize / contradiction authorities** | domain work | `FactValidationDependencies` requires both; neither P8 nor P6 invents them, and omitting either is `ValidationUnavailable`, not a pass. |
| **Site B–E producers** | P9, P10, P11 | The dossier builders do not exist. `llm_harness/fixtures.py` publishes content-free recorded pairs as contract witnesses. The producer swap happens at the named dossier-builder seam and nowhere else. |
| **P13 consent hand-off** | P13 | `run_call` returns the exact `NeedsConsent` object to its caller and writes nothing. The caller owns the hand-off; P13 has no producer yet. |
| **Site D two-condition rule** | ratification | P8 Q3's rule is ratified for Site C only. Site D requires an injected/ratified rule and otherwise returns `ValidationUnavailable`. |
| **Redaction reverse mapping** | P7 (SPEC open question 4) | R4 made the released value the span source, which removes P8's need for the reverse map in the common case. Whether anything needs to map a redacted span back to raw evidence is still P7's open question. |

### Newly named: Site E's fragment boundary is not enforced

`planning/domains/TEMPLATE-BUILDING-HANDOFF.md` says a Site E prompt *"may
reference published fragments by exact ID/version"* but *"cannot publish or
propose a new canonical fragment"*, and that repeated local dimensions become
fragment candidates only in a later human-reviewed synthesis pass.

**Nothing in `src/llm_harness/` enforces that.** The word `fragment` appears zero
times in the package. `TemplateDependencies` carries only `schema_validator`, and
`_template_site` checks the response schema, that every dimension name is in the
dossier's allowed vocabulary, that every dimension cites evidence, and that each
level carries a retrieval justification. A response declaring a new canonical
fragment, or referencing a fragment id that was never published, passes all four.

This is legitimately deferred — P10 does not exist, and the published-fragment
registry that a check would consult is P10's to publish. It was not written down
as deferred anywhere, which is the only thing wrong with it. When P10 ships,
`TemplateDependencies` gains a published-fragment authority and a missing one is
`ValidationUnavailable` like every other.

---

## 4. What P8 may now be called

Complete for its own scope: the only model invocation in the product, the only
deterministic validator for sites A–E, the canonical post-release dossier and its
content address, the release-bound citation check, and one connected consequence
path from `Gate.release` to a P6 fact and a P2 row.

Not complete as a *deployed* stage, and no test claims otherwise. Every seam in
§3 is a real absence with a named owner, and each one fails closed.

---

## 5. Process notes worth carrying forward

1. **A test that constructs its own record does not exercise the code that builds
   it.** Site B's validator tests were green for weeks while the only production
   path that could feed them produced a dossier they would have rejected. When a
   record has one production builder, at least one test must go through it.
2. **The connected path is where the defects are.** R3 and R5 together found four
   bugs that R1, R2 and R4 could not have, because until Site A was wired to P6
   there was nothing to be wrong between them.
3. **Derived registries beat listed ones.** The no-invention sweep had silently
   fallen behind by four callables and two bundles. The same pattern is still
   open elsewhere: the public surface is asserted as a literal list in nine
   places, which is how the eight-vs-six contradiction survived (see
   `32-HANDOFF.md` §4.1).
4. **A capability is not an identity.** `release_id` was used as a dossier id and
   again as a response key. Both were type-correct and both were wrong.
