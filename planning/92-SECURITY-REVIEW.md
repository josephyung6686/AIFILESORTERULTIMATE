---
phase: security-review
reviewed: 2026-09-02T18:40:00Z
depth: deep
files_reviewed: 30
files_reviewed_list:
  - src/privacy/vocabulary.py
  - src/privacy/items.py
  - src/privacy/release.py
  - src/privacy/gate.py
  - src/privacy/resolve.py
  - src/privacy/redaction.py
  - src/privacy/binding.py
  - src/privacy/denial.py
  - src/privacy/audit.py
  - src/privacy/defaults.py
  - src/privacy/transport_guard.py
  - src/privacy/fixtures.py
  - src/llm_harness/transport.py
  - src/llm_harness/records.py
  - src/llm_harness/dossier.py
  - src/llm_harness/harness.py
  - src/readers/model_anthropic.py
  - src/readers/model_deepseek.py
  - src/readers/model_routing.py
  - src/readers/archive_zipfile.py
  - src/extractors/filesystem.py
  - src/extractors/long_tail.py
  - src/extractors/safety.py
  - src/evidence_shape/observation.py
  - src/evidence_shape/locator.py
  - src/grouping/p8_seam.py
  - src/grouping/dossier.py
  - src/grouping/pipeline.py
  - src/scan_agent/traversal.py
  - src/scan_agent/exclusion.py
  - src/scan_agent/corpus_source.py
  - src/scan_agent/watch.py
  - src/database_agent/binding.py
  - src/cli.py
  - tests/integration/test_single_egress.py
findings:
  critical: 4
  warning: 7
  info: 0
  total: 11
status: issues_found
---

# GRAPH AGENT — Adversarial Security Review

**Reviewed:** 2026-09-02
**Depth:** deep (cross-file, with executable probes)
**Tree state:** `build/p6-p7-first-packages` at the time of the runs below. Eleven
agents share this index; `src/privacy/gate.py` moved by ~16 lines mid-review, so every
citation names a **symbol** as well as a line.
**Method:** every Critical and every Warning marked *reproduced* was **run** against
the real `Gate`, the real `resolve`, the real `dossier` builder and the real
`transport.issue`, driven off `tests/integration/test_live_path.py`'s live corpus
fixture. No real API call was made. No source file was modified: the probe module was
written under `tests/integration/`, run, and deleted. `.env` was never opened.

**Ranked by what a person actually loses.** CR-01 through CR-03 each put one of the
nine always-local kinds on the wire. CR-04 loses no data by itself — it is the guard
that would have caught the next CR-02, and it is last for that reason.

## Verdict on the five properties

| # | Property | Verdict |
|---|---|---|
| 1 | The nine `ALWAYS_LOCAL` kinds never leave the device | **BROKEN — reproduced.** `paths` reaches the model-visible bytes on the ordinary release path (CR-01). `complete_extracted_text`, `paths` and `file_hashes` all reach the wire through `transport.issue` on a valid live release (CR-02). A redacted value and a seed value are both recoverable in seconds from digests the wire carries (CR-03). |
| 2 | Protected material is marked and counted, never opened | **HOLDS — reproduced.** `pytest tests/integration/test_live_path.py -k protected` → `2 passed`, covering both the database and the session watch. The code supports it: `is_protected_container` is subtree-scoped, case-folded, checked first, and takes no argument that can switch it off; `extractors.safety.admit` runs it as the first statement of every extractor; `traversal.walk` prunes before descending; `corpus_source` never follows a symlink; `watch` prunes `dirnames` in place and re-checks in `notify`. One reservation: the `extra` extension point is unreachable from the live scan (WR-05). |
| 3 | Exactly one function constructs a model request, and its only parameter is a released, gated object | **BROKEN — reproduced.** `issue`'s second content parameter, `payload`, is never checked against the release (CR-02). The tree-wide guard that would catch a second door has four bypasses I ran through the guard itself (CR-04). On the owner's narrow `self_description` door specifically: it is **not** sealed only by convention — it is not connected at all, and the gate returns `Released` with the item silently dropped (WR-01, reproduced). |
| 4 | No credential reaches the screen, a log, an audit record or an exception message | **NOT FULLY VERIFIED.** I found no path that interpolates the key into any message: `_require_credential` in both provider modules names the *variable*, never the value; `model_route` prints only model ids; `deepseek_routing`'s refusals carry no secret. I probed the OpenAI SDK locally with a fake key and a bad base_url (no network): `str(exc)` was `"Connection error."`, and the fake key appeared in neither the message nor the traceback. I could **not** clear the class, because `transport.issue` writes `str(exc)` from an arbitrary third-party SDK into a durable row and into a user-visible `CallFailed` (WR-06). One shape checked; the channel is open. |
| 5 | Absent means refuse, never guess | **BROKEN in four places.** CR-01 is the worst instance (absent unit length → *unbounded*, not refused). WR-01 (absent resolver → silently drop, not refuse), WR-03 and WR-04 (absent tokenizer / absent template map → §8.6's ceiling and §7.3's carve-out both become unreachable) are the others. `resolve_class(None)`, `over_dossier_ceiling` with an unset ceiling, `Gate.release` on a missing policy, and both providers' missing-key/missing-endpoint refusals all behave correctly. |

---

## Critical

### CR-01 — `Gate.release` releases a whole absolute filesystem path, on the ordinary path, for every scanned file

**Files:** `src/privacy/resolve.py:197` (`materialise`), `src/privacy/items.py:350`
(`is_whole_document`), `src/privacy/items.py:355` (`check_item`),
`src/extractors/filesystem.py:87`, `src/privacy/gate.py:466` (`_postcheck_items`)

**What a person loses:** the folder structure of their private machine —
`/Users/<name>/Documents/Legal/Divorce`, `/Volumes/Work/ClientX` — sent verbatim to a
cloud model. §8.4's always-local list opens with the word "Paths".

**The chain, and why every comment beside it reads correct:**

1. `extractors/filesystem.py:83-89` writes one observation per scanned file with
   `zone="path"` and `raw_value = file_row["directory_position"]` — the parent
   directory. It carries **no `text_span`**, because the run's one text unit is the
   filename. Correct, and the comment says so.
2. `resolve.materialise:197` — for an observation with no `text_span` — returns
   `value = observation.raw_value` **whole**, `unit_length = None`. The docstring
   explains this is §2.3's cell and §2.8's EXIF field, "there is nothing to take a
   substring of". True, and also true of a path.
3. `items.is_whole_document:350` returns `False` when `unit_length is None`, with a
   correct justification: "Reading it as length zero would make every cell a whole
   document." The consequence is that a container-path-only observation has **no bound
   of any kind** — §8.4's "should not send full documents" cannot fire on it.
4. `check_item` never inspects `zone`. `_refuse_always_local_name` runs on
   `MetadataField.name` and `Filename.file_id` only; an `Excerpt` is never asked what
   zone it addresses. `evidence_shape.vocabulary.ZONES` contains `"path"` and
   `"filename"`.
5. `redaction.apply_redaction:161-165` returns the value **unredacted** when the
   injected classifier returns `None`, which is its ordinary answer for a path.

**Reproduced.** Against the real gate, on the live corpus:

```
('path', 'path', 'RELEASED',
 {'span': 'path',
  'value': '/private/var/folders/.../pytest-434/test_a_path_zone_observation_i0/corpus',
  'zone': 'path', 'unit_length': None})
```

and, carried through the real `build_dossier` → `canonical_dossier_bytes` →
`assemble`, into the exact bytes a model would be shown:

```json
"released_evidence":[{"address":"path","observation_key":"sha256:8ba45b…",
 "value":"/private/var/folders/…/corpus","zone":"path"}]
```

The same run confirms the check that *does* work: a `filename` observation **with** a
span is correctly `Denied whole_document_requested`. It is precisely the span-less
form that escapes.

**Exploitability, honestly:** a `path`-zone observation reaches a dossier only if a
deployment's fact slots cite it, and today's `cli.py` slots do not. But this is a
*gate* defect, and the gate's contract is that it refuses regardless of who asks. The
identical code path also covers `unrouted_result`'s span-less `zone="filename"`
observation (`filesystem.py:144`), which would release a whole filename as an
`Excerpt` — bypassing `Filename`'s `allow_unratified` opt-in and §7.3's
protected-records filename ban, neither of which `check_item` applies to an `Excerpt`.
I verified the mechanism on the `path` observation; the `filename` case is the same
three lines and is *inferred*, not separately run.

**Fix — lead with the zone check.**

```python
# privacy/vocabulary.py — a mapping onto the existing nine, NOT a tenth member
ALWAYS_LOCAL_ZONES: frozenset[str] = frozenset({"path", "filename"})

# privacy/items.py — inside check_item, taking the resolved zone as a new keyword,
# beside unit_length; gate._postcheck_items already holds it on ReleasedItem.zone
if zone in ALWAYS_LOCAL_ZONES:
    raise AlwaysLocalRequested(
        f"the observation addresses zone {zone!r}; §8.4 places 'paths' in the "
        "always-local set, and §7.7's filename is the flagged sixth kind, which "
        "must arrive as a `Filename` under `allow_unratified` — not as an "
        "unbounded excerpt that no check reads the zone of")
```

Do **not** simply flip `is_whole_document` to return `True` when `unit_length is None`:
`test_live_path.py:715-716` asserts that the span-less `title:field=Title` observation
**is** `Released`, and that assertion is correct — a metadata field is a bounded value,
not a document. If you want a second layer, add a distinct
`UnboundedAddressRequested` refusal for a container-path address whose `raw_value`
exceeds a configured length, so the cell case and the path case stop sharing an answer.

---

### CR-02 — `transport.issue` sends bytes the gate never released; the docstring that says otherwise is wrong

**Files:** `src/llm_harness/transport.py:82` (`_require_sources`),
`transport.py:95` (`_require_binding`), `transport.py:163` (`issue`),
`src/privacy/binding.py:46,132` (`BINDING_TERMS`, `consume_release`),
`src/privacy/transport_guard.py:53-58` (the false claim)

**What a person loses:** everything. The complete extracted text of every file, every
absolute path, every content hash — on the wire, on a valid live release, with an audit
record that says a single `[redacted]` excerpt was released.

**The claim under review.** `transport_guard.py:53-58` states its own limit and then
disposes of it:

> **Stated limit.** … Classes the transport imports — P8's `CallPayload`, which carries
> the model-visible bytes — are not walked … That a `CallPayload`'s bytes are the
> released dossier is proven at runtime by `build_call_payload`,
> `CallPayload.__post_init__` and `issue`'s own `_require_sources`, not here.

None of the three does what that sentence says:

- `records.build_call_payload` never receives the `Released`. It takes
  `canonical_dossier_bytes`, `model_target`, `policy_version`, `release_id` and
  `dossier_id` as bare values and assembles them.
- `CallPayload.__post_init__` checks `model_visible_bytes == assemble(prompt_definition,
  canonical_dossier_bytes)` — internal self-consistency only.
- `_require_sources` recomputes the fingerprint from `prompt_definition` and reassembles
  the same two fields. Also internal only.

`_require_binding` compares `model_target`, `release_id`, `policy_version`.
`consume_release` compares `BINDING_TERMS = (model_target, prompt_fingerprint,
policy_version)`. **`Released.materialised_items` appears in none of them.** The binding
covers *who* receives it and *under what policy*; nothing covers *what*.

**Reproduced.** Minted a real release through the real `Gate` (its one materialised item
was `"[redacted]"`), bound to the real prompt's fingerprint exactly as
`grouping/p8_seam.prompt_fingerprint_for` does, then handed `issue` a `CallPayload`
whose dossier bytes were a JSON dump of `evidence.raw_value`,
`evidence.context_before/after`, `files.current_path` and `files.content_hash`. `issue`
returned `ModelResponse`; the client received:

```
TEMPLATE
{"complete_extracted_text": [{"raw_value": "Lecture 08.pdf", …},
 {"raw_value": "/private/var/folders/…/corpus", …},
 {"raw_value": "BUSIB 4300",
  "context_before": "his syllabus covers the spring term for ",
  "context_after": ".\npage 1 of 1\n"}, …],
 "paths": [{"current_path": "/private/var/folders/…/Lecture 08.pdf"}, …],
 "file_hashes": [{"content_hash": "e317e437…"}, …]}
```

Note the third entry: the pre-redaction value **and** the surrounding context that
`dossier._released_body` and `records.ReleasedEvidence` both document as having been
deliberately removed. They were removed from the *release*. The egress does not require
the bytes to have come from one.

**Fix.** Bind the content into the ledger and check it at the door:

```python
# privacy/binding.py
BINDING_TERMS = ("model_target", "prompt_fingerprint", "policy_version",
                 "content_digest")

def mint_release(conn, *, policy, model_target, prompt_fingerprint, audit_id,
                 minted_at, content_digest: str) -> str: ...
```

with `content_digest = sha256_of(canonical_json([item.to_mapping() for item in
resolved]))` computed inside `Gate.release` (and stored on `Released` so a caller can
echo it), and `issue` recomputing it from `released.materialised_items` and requiring
that every `released_evidence` entry it can see in `payload.canonical_dossier_bytes`
is one of them. Until that lands, `build_dossier`'s three key-set checks
(`dossier.py:244-250`) are the only thing tying bytes to a release, and they live in
the *caller* — which is exactly what "exactly one door" exists to make impossible.
Also correct the two docstrings: a stated limit disposed of by a false sentence is
worse than an unstated one, because it stops the next reviewer looking.

---

### CR-03 — two un-keyed digests on the wire are reversible; both were reversed in under a second

**Files:** `src/evidence_shape/observation.py:110-119`,
`src/evidence_shape/canonical.py:56` (`sha256_of`),
`src/grouping/pipeline.py:257-262` (`_group_id`),
`src/llm_harness/dossier.py:101-137`, `src/grouping/p8_seam.py:142-156`

**What a person loses:** redaction, and the point of keeping `file_hashes` local.

#### (b) is the worse one: `subject_ref` needs nothing but the wire bytes

`grouping/pipeline.py:259-262`:

```python
digest = hashlib.sha256("\x1f".join((seed.field_key, seed.value)).encode()).hexdigest()
return f"group:{seed.field_key}:{digest}:{seed.seed_kind}"
```

That string becomes `DossierRequest.subject_ref` (`p8_seam.py:200`) and is printed
**verbatim in the model-visible bytes**. From my capture:

```json
"subject_ref":"group:subject:448eba491c13a2204bfd695bbafa81b544e05a0fb9a6a35d4f2c3dc68f3451c8:strongly-identified-file"
```

The docstring's reasoning is: *"The value is digested rather than spelled into the id
because a field value is arbitrary user text — a course code, a client name, a filename
with a colon in it."* Digesting it protects the id *parser*. It protects nothing on the
wire: `field_key` is printed in the clear immediately before the digest, the separator
is a fixed `\x1f`, and `sha256` is unkeyed and unsalted. The **only** unknown is
`value` — and "arbitrary user text" that identifies a group is exactly what a
dictionary attack is for: a client name, an employer, a course code, a case number.

**Reproduced from the wire bytes alone, no copy of any file:**

```
RECOVERED after 3301 hashes: field_key='subject' value='BUSIB 4300'
```

#### (a) `observation_key`, which needs the wire bytes plus a copy of the file

```python
observation_key = sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)
```

Four preimage components; three are free:

- `locator` is printed **in the clear in the same JSON object**, as
  `released_evidence[].address` (`"address":"heading:page=1/heading=1#0-10"`).
- `extractor_name` is a small closed set shipped in this repo (`"pdf.text"`,
  `"filesystem"`, …).
- `content_hash` is unsalted `sha256` of the file's bytes
  (`database_agent/identity.py:61-65`), so anyone holding a copy computes it.

That leaves `raw_value` — the value redaction removed. **Reproduced:** attacker holds
the wire bytes and a copy of the corpus, nothing else; 227,301 hashes, ~1 second on a
laptop:

```
wire value  : "[redacted]"
wire key    : sha256:3ac012e8030ea640be13509aab5bb386c12116e3bbb1f28017aaa8c540815f10
wire address: heading:page=1/heading=1#0-10
RECOVERED   : {"file": "Syllabus.pdf", "extractor": "pdf.text",
               "recovered_plaintext": "BUSIB 4300"}
```

Independently of un-redaction, this is a membership oracle over `file_hashes`: given a
candidate file, a yes/no answer to "was *this* file, byte for byte, in the scan?" — the
thing `file_hashes` is in the always-local set to prevent. The key is also stable across
every call about a file, so a provider can link sessions and build a per-file profile
without ever being told a path.

**Fix — both digests, and `observation_key` appears on the wire twice.**

`observation_key` is emitted at `dossier._released_evidence` (as
`released_evidence[].observation_key`) **and** at `p8_seam._excerpt_items:145` (as
`evidence_items[].evidence_ref`); both are in my captured bytes. Remapping one leaves
the oracle intact. Give the dossier a per-call opaque handle and keep the mapping local:

```python
# llm_harness/dossier.py — one map, applied to BOTH keys, built once per dossier
def _handles(released) -> dict[str, str]:
    return {item.observation_key: f"e{i}"
            for i, item in enumerate(released.materialised_items)}
```

`_released_evidence` uses it for `observation_key`; `_evidence_item_body` uses it for
`evidence_ref`; `build_dossier`'s three key-set checks (`dossier.py:244-250`) reconcile
through the same map rather than on raw keys; the map is stored on the local
`llm_dossier` row so `validation._check_citation` and the audit record still resolve. If
a stable cross-call handle is genuinely needed, derive it as
`HMAC(install_secret, observation_key)`.

For `_group_id`, do the same or use `HMAC(install_secret, field_key ‖ value)`. Note that
`address` alone still leaks structure and can leak an archive member path; see WR-02.

---

### CR-04 — the tree-wide egress guard has four bypasses; all four verified by running the guard itself

**File:** `tests/integration/test_single_egress.py:161-200` (`_calls_invoke`,
`findings`)

**Loses no data directly.** It is the instrument that would have caught the next CR-02,
which is why it is Critical and why it is ranked last of the four.

This file is the *only* instrument that asks "exactly one function constructs a model
request" of the whole codebase — its own docstring says the other two only prove "the
module which admits to being a transport is a good one." Its rule E is also the only
seal on who may construct a `SelfDescription`, which `privacy/items.py:250-257`
explicitly delegates to it: *"That seal is an AST scan over `src/` in
`tests/integration/test_single_egress.py`."*

I ran the real `findings()` over synthetic modules:

| module source | `findings()` |
|---|---|
| `from privacy import items` / `items.SelfDescription('role:me')` | `()` — **not caught** |
| `f = c.invoke` / `f(b)` | `()` — **not caught** |
| `getattr(c, 'invoke')(b)` | `()` — **not caught** |
| `import subprocess` / `subprocess.run(['curl','-d',b,url])` | `()` — **not caught** |
| `from privacy.items import SelfDescription` / `SelfDescription(...)` (control) | caught |
| `c.invoke(b)` (control) | caught |

Causes: rule E matches only `ast.Name` call targets, so any attribute-qualified
construction passes. `_calls_invoke` matches only a direct `ast.Attribute` call, so an
alias or `getattr` passes. `NETWORK_MODULES` omits `subprocess`, `ssl`, `ftplib`,
`smtplib`, `pycurl`. The file states rule C is a named list, but `subprocess` is not a
future-SDK gap — it is the oldest way out of a process.

**Fix:**

```python
def _constructs(tree, name):
    return any(
        isinstance(n, ast.Call) and (
            (isinstance(n.func, ast.Name) and n.func.id == name)
            or (isinstance(n.func, ast.Attribute) and n.func.attr == name))
        for n in ast.walk(tree))

def _calls_invoke(tree):
    """A call through .invoke, through an alias bound from it, or via getattr."""
    aliases = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
               for t in n.targets if isinstance(t, ast.Name)
               and isinstance(n.value, ast.Attribute) and n.value.attr == EGRESS_CALL}
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and f.attr == EGRESS_CALL:
            return True
        if isinstance(f, ast.Name) and f.id in aliases:
            return True
        if (isinstance(f, ast.Call) and isinstance(f.func, ast.Name)
                and f.func.id == "getattr" and len(f.args) == 2
                and isinstance(f.args[1], ast.Constant)
                and f.args[1].value == EGRESS_CALL):
            return True
    return False

NETWORK_MODULES = frozenset({..., "subprocess", "ssl", "ftplib", "smtplib",
                             "pycurl", "websockets"})
```

Add each bypass as a fixture under `tests/integration/egress_fixtures/`; the file's own
standard is that every rule is "proven in both directions", and these four rules are
currently proven in one.

---

## Warnings

### WR-01 — the narrow `self_description` door is not connected; the gate returns `Released` with the item silently dropped

**Files:** `src/privacy/items.py:228-278` (`SelfDescription`),
`src/privacy/gate.py:78` (`TEXT_BEARING`), `gate.py:282`, `gate.py:503`
(`_materialise`), `src/privacy/resolve.py` (whole file)

`SelfDescription`'s docstring states: *"This one carries the `question_id` of the role
declaration and **`resolve.py` looks the wording up** — so the words exist in exactly
one place, the gate is what reads them."* It does not. `resolve.py` contains no
reference to `question_id` and has exactly two resolvers, both keyed on
`observation_key`; `SelfDescription` has none. `TEXT_BEARING = (Excerpt,
RedactedIdentifier)`, and `_materialise` is called with `text_items` only.

**Reproduced.** Two items requested (`Excerpt` + `SelfDescription("role:me")`), against
the real gate on the live corpus:

- `suspension_permits_self_description=False` → `Denied always_local_item`. Correct.
- `suspension_permits_self_description=True` → **`Released`, `len(materialised_items) == 1`
  of 2 requested.** The self-description is neither released nor refused; it evaporates,
  and `AuditRecord.excerpts_included` — built from `resolved` — does not name it either.

This is the reverse of the failure the ruling was written against, and it is still a
property-5 failure: absent means *silently omit* where it must mean refuse. It also
means the owner's ruling of 2026-09-02 currently buys nothing — the role matcher cannot
be built on it — while the vocabulary member, the type, the two-tier flag system and the
AST seal are all written as though it were live.

**Fix:** either wire a third resolver in `resolve.py` keyed on `question_id` and add
`SelfDescription` to `TEXT_BEARING`, or make the gate refuse an item kind it cannot
materialise:

```python
# privacy/gate.py, in release(), after _precheck_items
unmaterialisable = tuple(
    item for item in request.requested_items
    if kind_of(item) in MATERIALISED_KINDS and not isinstance(item, TEXT_BEARING))
if unmaterialisable:
    raise MalformedRequest(
        "the gate has no materialiser for "
        f"{sorted({kind_of(i) for i in unmaterialisable})}; a release that omitted an "
        "item would be an audit record that does not describe the call")
```

### WR-02 — the locator is on the wire, and it can carry an archive member path

**Files:** `src/evidence_shape/locator.py:17-19,87-93`,
`src/evidence_shape/vocabulary.py:39` (`LABEL_SEGMENT_KINDS`),
`src/privacy/redaction.py:118` (`span_address`), `src/llm_harness/dossier.py:124-137`

`LABEL_SEGMENT_KINDS = ("field", "entry", "key")` are serialised into the locator **by
label**, and `locator.py`'s own docstring says so: *"Archive member paths contain `/`
and this [escaping] is not optional."* `span_address` returns
`serialize_locator(location)` unmodified, `ReleasedItem.span` carries it, and
`_released_body` puts it on the wire as `address`. So an observation inside a `.zip`
publishes its member path — e.g. `body:entry=Tax%2FReturn%202024.pdf#0-42` — to the
model. `ZONES` also contains `path` and `filename`, and `zone` is on the wire too.

I did not build an archive fixture; this is read from the code. That `address` reaches
the wire verbatim **is** reproduced (CR-01, CR-03).

**Fix:** the released form of an address should carry the addressing *shape*, not the
labels — strip or opaque-hash `LABEL_SEGMENT_KINDS` labels on the way out, and keep the
full locator in the local audit manifest, where it already lives.

### WR-03 / WR-04 — two `None` defaults on `Gate.__init__` make two refusals unreachable

**File:** `src/privacy/gate.py:101-102` (`measure_tokens`, `template_for`), with
`gate.py:293` and `gate.py:225`; `src/privacy/denial.py:214` (`over_dossier_ceiling`)

`measure_tokens: … | None = None` — unset, §8.6's `dossier_over_budget` check never
runs. `over_dossier_ceiling` *also* returns `False` when the stored ceiling is unset.
Two independent absences, either of which disables the ceiling, both defaulting to the
permissive side. `template_for: … | None = None` — unset, no file is ever under §7.3's
residual template, so `protected_records_template` cannot fire from that branch.

Both are documented as deliberate, and the reasoning ("with no measurement there is
nothing to compare") is sound in isolation. But `vocabulary.py` calls
`dossier_over_budget` "a backstop that should never fire", and a backstop that is off in
every deployment that forgets one keyword is not a backstop.

**Fix:** make both required keywords with no default, exactly as `classifier`,
`transform`, `scope_for` and `unclassified_permits_local` already are, and let a
deployment with no tokenizer pass an explicit sentinel it has to name.

### WR-05 — the `is_protected` extension point is unreachable from the live scan

**Files:** `src/scan_agent/traversal.py:55,73,118` (`walk`),
`src/scan_agent/exclusion.py:73-97,125-127`, `src/scan_agent/disappearance.py:109`

`exclusion_for` and `is_protected_container` both take an `extra` / `is_protected`
predicate whose stated purpose is that "a deployment supplies the rest" of §4b's "system
location" members, which P3 deliberately authors none of. `traversal.walk` — the only
walker `scan.scan()` uses — calls `exclusion_for` twice and passes it at neither site,
and `walk` has no parameter for it. `disappearance.py:109` likewise. Only
`watch.SessionWatch` threads it.

So the one open half of the protected-container rule cannot be closed by any deployment:
`.app` is enforced, everything else the SPEC names is unreachable — in a rule the design
says has no override.

**Fix:** add `is_protected=None` to `walk`'s keyword-only signature, pass it to both
`exclusion_for` calls, and thread it from `scan.scan()`.

### WR-06 — an arbitrary SDK exception string is written to the database and returned to the user

**File:** `src/llm_harness/transport.py:159-160` (`_client_exception_explanation`),
`transport.py:186-205`

```python
except Exception as exc:
    explanation = _client_exception_explanation(exc)   # str(exc) or the type name
    record_call_failure(conn, …, explanation=explanation, …)
    return _failed(released, payload, explanation=explanation)
```

The `try` spans the whole client call, `except Exception` is as wide as it gets, and the
message goes into a durable row and into a `CallFailed` that `records.py:513-514` says
`emit_stage_output` serialises "verbatim into P2's `error` row". Whatever a third-party
SDK puts in an exception message — a request echo, a URL with a query parameter, a
header dump — lands in the audit trail unfiltered. This is the one channel I could not
clear for property 4.

Probed: `openai.APIConnectionError` stringifies to `"Connection error."`, and a fake key
appeared in neither the message nor the traceback. One shape out of many, and the SDKs
are free to change it.

**Fix:** record the exception type and a bounded, allow-listed field, not free text:

```python
def _client_exception_explanation(exc: BaseException) -> str:
    return canonical_json({"type": type(exc).__qualname__,
                           "status": getattr(exc, "status_code", None)})
```

If the free text is needed for debugging, put it behind an explicit developer flag, not
in the record §8.4 requires to be consent-aware.

### WR-07 — the `raw_sensitive_values` refusal cannot fire for a PDF, a DOCX, an image or an OCR result

**Files:** `src/extractors/long_tail.py:40-63,239-318`, `src/privacy/items.py:413-420`
(`check_item`), `src/privacy/items.py:431-447` (`sensitive_observation_keys`)

`check_item`'s always-local refusal for `raw_sensitive_values` keys off
`sensitive_observation_keys`, which reads `sensitivity_signals_for`. **Every**
`SensitivitySignal` in the product is emitted from `extractors/long_tail.py` (two call
sites), and only for `source_type` in `("email", "contacts")` plus email-zone structured
strings. `LONG_TAIL_SOURCE_TYPES` is spreadsheet / presentation / email / calendar /
contacts / audio\_video; PDFs, DOCX, images and OCR go through other extractors and emit
**no signals at all**.

`sensitive_observation_keys`' docstring is careful — "An empty set means NOTHING WAS
SIGNALLED, not 'nothing is sensitive'" — and that is exactly the problem: for the formats
carrying most of a person's sensitive text, the set is always empty, so the refusal is
structurally unreachable rather than merely quiet.

**Fix:** this is a P5 gap, not a P7 one, and the honest short-term fix is to make the gap
visible rather than invent a detector P7 is forbidden to own — have
`sensitive_observation_keys` refuse when the file's `source_type` has no signal producer
at all, so a deployment must supply one or explicitly accept the risk.

---

## What I checked and found clean

- **SQL.** No string-built query takes user or file data. `cli._protected_among:1743`
  builds its `IN` list from `?` placeholders; `db.transaction`'s savepoint name is a
  uuid; `shadow.foreign_table_counts` interpolates table names read from `sqlite_master`.
- **Symlinks and `..`.** `FilesystemCorpusSource.entries` uses
  `stat(follow_symlinks=False)` throughout; a symlink becomes `KIND_OTHER`, is never
  descended and never hashed. `watch._walk`'s `os.walk` defaults to `followlinks=False`.
  `is_protected_container` walks `PurePath.parents`, which does not normalise `..`, so it
  errs toward over-exclusion — the safe direction, and the one its docstring requires.
- **Zip bombs.** `readers/archive_zipfile.py` reads the central directory only and never
  extracts, so decompression-ratio attacks have no target; `file_size` is documented as
  stated-not-verified and is not trusted. `max_members` is injected.
- **Protected containers, run.** `pytest tests/integration/test_live_path.py -k protected
  -p no:randomly` → `2 passed`. `extractors.safety.admit` runs the protected check as the
  first statement of every extractor and takes no override field.
- **Single-use release.** `consume_release` checks issuance, then binding, then spends
  with `UPDATE … WHERE spent_at IS NULL` and `rowcount != 1` — check and mark are one
  statement, so a second caller arriving between them loses.
- **Transaction discipline.** `issue` refuses an already-open transaction so a rollback
  cannot unspend a release after bytes have left; `harness` releases the budget
  reservation on `BaseException`.
- **`absent → refuse` where it works.** `resolve_class(None)` → `unreadable_unclassified`;
  `Gate.release` raises `NoPolicyInForce` rather than synthesising a policy;
  `deepseek_invoke` refuses a missing `base_url` rather than taking the SDK's OpenAI
  default; both providers refuse a missing key at construction, before the scan.
- **Locality is measured where it is a fact.** Both provider modules refuse a
  `ModelTarget` whose `locality` is not `cloud`, closing the one hole `Gate.release`
  structurally cannot see.
- **Provider modules hold no prompt and no credential.** Neither reads the environment;
  both name the variable and never the value in their refusals.
- **Whole suite green** before and after: `tests/p7` + `tests/integration/test_single_egress.py`
  → `1161 passed, 2 xfailed`. Every finding above is invisible to it.

## What I could not check, and why

- **Property 4 in full** (WR-06). There is no way to enumerate every exception string an
  SDK may produce. I verified one shape locally and no more.
- **Archive-member locators on the wire** (WR-02) — read from the code, not run; I did
  not build a `.zip` fixture.
- **The `unrouted_result` span-less filename case** in CR-01 — inferred from the same
  three lines I reproduced for `zone="path"`, not separately run.
- **Unbounded reads on a hostile document.** I found **no length cap** anywhere between a
  reader and `evidence_shape.text_units` — no `MAX_*` constant, no slice, no configured
  ceiling — so a single enormous PDF/DOCX text layer becomes one in-memory `TextUnit` and
  one DB row. I did not build a hostile file to measure it, so this is a gap I am
  reporting rather than a finding I proved. `extractors/long_tail` and
  `grouping/dossier._excerpts_for` do cap (`limit`), but those are downstream of storage.
- **TOCTOU between `identity.hash_file` and extraction.** A file rewritten between the
  hash and the read is stored with a hash that does not describe its bytes. I did not
  test it. The consequence is bounded in the safe direction for the gate — a changed file
  has no classification keyed to the new hash, so `resolve_class` returns
  `unreadable_unclassified` and a cloud call is denied — but the *evidence* rows would
  describe content the hash does not.
- **`subject_ref` and `EvidenceItem.location` as free strings.** Both reach the
  model-visible bytes with **no validation of any kind** (`records.py:186-215`,
  `records.py:226-237` check `evidence_ref` and `basis` only). Today's producers pass a
  group id, a zone, or a `document_type`, so this is not a leak now — but it is precisely
  "a field that carries more than it appears to", and `subject_ref` already turned out to
  carry a reversible digest (CR-03b). A builder that passed a path or a title into either
  would be caught by nothing.
- **`.env`** — never opened, per the brief.

---

_Reviewed: 2026-09-02_
_Reviewer: Claude (gsd-code-reviewer), adversarial pass_
_Depth: deep — four Critical and two Warning findings reproduced by execution_

---

## CR-06 — the one end-to-end proof of the model path proved it with a fabrication

Added 2026-09-02 by the lead, found by `value-evidence-check` while wiring
`VALUE_NOT_IN_CITED_TEXT`. **Not found by the review above**, and worth recording for
that reason as much as for the defect.

`tests/p8/test_p8_walking_skeleton::test_one_run_call_walks_p7_to_p8_to_p6_to_p2` is
the product's ONLY end-to-end P7 → P8 → P6 → P2 proof. It seeded a classified file,
the gate redacted it, the model was shown `"[redacted]"` — and the fixture then had the
model propose `subject = "Columbia University"`, **the very text the redaction removed**,
citing the span `[redacted]`.

That was `accept_direct`, and it became an **active `llm_supported` fact on the person's
file**. Nothing in the dossier carried those characters: the model either invented them
or knew them from elsewhere, and the product wrote a model's guess about redacted
content onto the person's record as a fact.

**Three things make this worse than an ordinary bad fixture.**

1. **It is the test that certifies the whole model path.** Every claim that "the LLM
   seam works end to end" rested on a walk whose accept step was a fabrication.
2. **It could not be fixed by changing the proposed value.** `apply_redaction` redacts
   whole values, so under that fixture's policy *every* released value is `[redacted]`
   and the only correct model behaviour over that world is `unknown`. The world was
   wrong, not the answer.
3. **The value-grounding check refuses it** — which is how it surfaced. A defect that
   sat in the certifying test until an unrelated guard was pointed at it.

The fixture now carries a second reading the gate releases in the clear, binds the
accepting claim to that, still proves R4 with the redacted reading beside it, and pins
the old claim as `test_the_walk_refuses_a_value_the_gate_removed` so it cannot drift
back. Both twins fail in opposite directions under sabotage.

**The transferable lesson, and it belongs beside `84` §5.3.** A guard that has never
failed is not a guard; **a proof whose premise is impossible is not a proof.** This one
passed for as long as it existed, and what it demonstrated was that the pipeline will
carry an invented value from a model to a person's file without objecting.

---

## CR-07 — a whole document passes the gate as one span-less excerpt

Found by `deepen-extraction` while writing `95` §5.4, and **reproduced independently by the lead
on 2026-09-03** rather than accepted on report:

```
is_whole_document(span=None, unit_length=None) -> False
'complete_extracted_text' in ALWAYS_LOCAL      -> True
check_item(...)  : PASSED -- the gate admits a span-less whole-document excerpt
```

`extractors/structured_text.py` emits a whole text document as one span-less `body` observation.
`privacy/resolve.py:197` resolves a span-less observation to its `raw_value`, which is the whole
document. And `privacy/items.py:369` reads `span is None or unit_length is None` as **not** a whole
document, so §8.4's *"should not send full documents where a short heading or OCR excerpt is
enough"* never fires on it. Reproduced on the live path by its finder: a 339-character `.txt`
through `run_wave2` releases as one `Excerpt` and `check_item` passes.

**`complete_extracted_text` is member 2 of `ALWAYS_LOCAL`.** This is the gate admitting, as an
"excerpt", exactly the kind the vocabulary says never leaves the device.

**Not live today and that is timing, not design.** `MODEL_CALL_SITES_WIRED` is `False`, no site
builds an A_fact dossier, and no prompt is installed — so nothing can send anything. **It must
close before the model path opens**, and the model path is the next thing anyone will want to
build. A hole that is unreachable only because the feature above it is unfinished is a hole.

**Why the obvious fix is wrong.** `items.py:369`'s reasoning is sound where it was written:
`unit_length is None` is the container-path form — §2.3's spreadsheet cell, §2.8's EXIF field —
where there is no unit for a span to cover, and reading it as length zero *"would make every cell a
whole document"*. A blanket refusal of span-less items breaks those legitimate cases. The shape of
the fix is **refuse a span-less item whose `raw_value` is the whole of a text unit at its own
container path** — narrower than "span-less", and it belongs in `src/privacy/`.

The finder did not build it, correctly: it is a `src/privacy/` decision and the module it lives in
already reasons carefully about the case it would break.
