# Restore 00 Fidelity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the live product path (`src/cli.py` → `production.run_production_corpus`) actually perform the hybrid loop `planning/00-database-agent-product-design.md` describes — extract usable evidence, produce validated facts, group and place with optional gated LLM help, then apply moves with undo — instead of a deterministic PDF/text slice that prints “Nothing was moved.”

**Architecture:** Packages P1–P11 already encode most of `00`. The drift is in **deployment wiring and missing mutation/review parts**. This program (1) tells the truth in docs, (2) wires readers/rules/P8/oracles/residual/catalogue gates into the CLI chooser, (3) executes the already-authored P12 and P13 plans, (4) connects CLI to apply/review, (5) re-audits against `00`. Do not invent second homes for vocabulary inside `production.py` / `orchestrator.py` — inject authorities from `cli.py` or a new `src/deployment/` profile module.

**Tech Stack:** Python 3.12, stdlib SQLite core, optional `readers` extra (pdfminer.six, pyobjc Vision), pytest with `-p no:randomly` when thinc/spaCy is importable, existing `llm_harness` / `privacy.Gate` / `facts` seams.

**Spec:** `planning/00-database-agent-product-design.md` (canonical). Part SPECs under `planning/parts/`. Evidence: `.planning/codebase/CONCERNS.md`, wiring audit of `cli.py`, design-fidelity audit 2026-08-29.

## Global Constraints

- **`00` wins.** Grep-verify every quotation from `00` before writing it. Never fabricate.
- **`python3`, not `python`.** Full-suite: `python3 -m pytest tests/ -p no:randomly` (or `-p randomly --randomly-dont-reset-seed` per `pyproject.toml`).
- **Explicit pathspec commits only.** Never `git add -A` / wildcards over `planning/domains/nodes/`.
- **Composition invents no domain defaults.** Thresholds, catalogues, readers, `normalize`/`contradicts`, consent scopes: injected from CLI/deployment profiles.
- **P7 before any model content.** `NeedsConsent` is returned unchanged — never coerced to abstain/deny.
- **C-5:** `facts` must not publish `normalize(` / `contradicts(`. Deployment supplies them into P8 `validation_dependencies`.
- **After freeze:** no invented destinations. P11 places or abstains; only P12 mutates the filesystem.
- **Protected material:** marked and counted, never opened.
- **Launch-domain default:** academic, applications, research, career, photos, code — plus safety detect/protect for finance/identity/medical/legal. Other schemas/templates stay loadable only behind an explicit flag.
- **Do not re-open ratified decisions** (D1–D6, J-IND, J-DEPTH). Do not close open NEEDS-JOSEPH items.
- **Sibling plans (do not rewrite):** `docs/superpowers/plans/2026-08-29-p12-apply-undo.md`, `docs/superpowers/plans/2026-08-29-p13-review-approval-surface.md`.

## Program waves (ship independently)

| Wave | Outcome | Depends on |
|------|---------|------------|
| **0** | Docs/audits match HEAD | — |
| **1** | Extraction fidelity on CLI | 0 |
| **2** | Hybrid facts + P8 on CLI (offline-safe) | 1 |
| **3** | Launch-domain catalogue gate | 1 |
| **4** | Minimal residual library enabled | 3 |
| **5** | P12 apply/undo green | 0 (parallel after 0) |
| **6** | P13 review surface green | 5 partial OK; prefer after 5 Task that publishes move plans |
| **7** | CLI prints plan then applies with journal | 2, 4, 5, 6 |
| **8** | Fresh `00` conformance audit | 7 |

---

## File structure (new / primary touch)

| Path | Responsibility |
|------|----------------|
| `src/deployment/__init__.py` | Package marker for chooser profiles |
| `src/deployment/launch_profile.py` | Launch-domain allowlists, OCR language list, residual stubs |
| `src/deployment/academic_rules.py` | Injected §3.5 `Rule` set (pattern + academic context terms + `subject`) |
| `src/deployment/validation_oracles.py` | Injected `normalize` / `contradicts` for P8 Site A (C-5) |
| `src/deployment/usable.py` | Real `usable_threshold` for targeted OCR |
| `src/readers/docx_stdlib.py` (or zip+xml) | DOCX reader returning P5 `TextDocument` / structured shape |
| `src/readers/image_exif.py` | Image metadata reader (no OCR); OCR stays Vision |
| `src/readers/archive_manifest.py` | Archive listing without unpack-to-disk |
| `src/readers/deployment.py` | Wire real readers; configurable `VISION_CONFIG["languages"]` |
| `src/cli.py` | Choose profile; wire resolvers, P8, residual, later P12/P13 |
| `README.md`, `.planning/.continue-here.md`, `planning/28-p1-p7-design-conformance-audit.md` | Truth |
| `src/mutation/` | Created by Wave 5 (existing P12 plan) |
| `src/review_surface/` | Created by Wave 6 (existing P13 plan) |
| `tests/deployment/` | Profile + wiring tests |
| `tests/integration/test_cli_00_fidelity.py` | End-to-end “does the product path honor 00” |

---

### Task 0.1: Refresh project truth documents

**Files:**
- Modify: `README.md`
- Modify: `.planning/.continue-here.md`
- Modify: `.planning/HANDOFF.json`
- Modify: `planning/28-p1-p7-design-conformance-audit.md` (add a 2026-08-29 superseding banner at top; do not delete history)
- Test: none (docs only) — verify with `rg`

**Interfaces:**
- Consumes: live `src/` package list; HEAD sha
- Produces: README status that lists P1–P11 present, P12/P13 planned, CLI path incomplete until Wave 7

- [ ] **Step 1: Write the README status block**

Replace the false “No application code in this repo yet.” paragraph with:

```markdown
**Status (2026-08-29):** Runtime packages **P1–P11** live under `src/` on
`build/p6-p7-first-packages`. The design authority remains
[`planning/00-database-agent-product-design.md`](planning/00-database-agent-product-design.md).
P12 (apply/undo) and P13 (review surface) have SPECs/PLANs but are not yet in `src/`.
The shipped CLI (`src/cli.py`) currently runs a **deterministic** slice (direct facts,
no P8, PDF/text readers) and does not move files — see
`docs/superpowers/plans/2026-08-29-restore-00-fidelity.md`.
```

- [ ] **Step 2: Replace `.planning/.continue-here.md` with a short current handoff**

```markdown
---
context: default
phase: restore-00-fidelity
status: in_progress
last_updated: 2026-08-29
branch: build/p6-p7-first-packages
plan: docs/superpowers/plans/2026-08-29-restore-00-fidelity.md
---

# Continue here

1. Read `planning/00-database-agent-product-design.md` (authority).
2. Read `.planning/codebase/CONCERNS.md` and the restore plan above.
3. Execute the next unchecked task in that plan.
4. Never `git add -A`. Ignore unrelated `src/` churn from other workstreams only if
   ownership docs say so; this program owns `src/cli.py`, `src/deployment/`,
   `src/readers/`, and later `src/mutation/`, `src/review_surface/`.
```

- [ ] **Step 3: Banner on audit 28**

Prepend:

```markdown
> **SUPERSEDED IN PART (2026-08-29):** Claims that “P8/P9 remain plans only” are
> false on current HEAD. P8–P11 packages exist; the live CLI still under-wires them.
> See `docs/superpowers/plans/2026-08-29-restore-00-fidelity.md` Wave 8 for the
> replacement conformance audit. Historical verification numbers below are retained.
```

- [ ] **Step 4: Verify the lie is gone**

Run: `rg -n "No application code in this repo yet" README.md; rg -n "P8/P9 remain plans only" planning/28-p1-p7-design-conformance-audit.md | head`

Expected: README has **no** match; audit 28 match only inside/near the SUPERSEDED banner context (old prose may remain below).

- [ ] **Step 5: Commit**

```bash
git add README.md .planning/.continue-here.md .planning/HANDOFF.json \
  planning/28-p1-p7-design-conformance-audit.md
git commit -m "$(cat <<'EOF'
docs: tell the truth — P1–P11 exist; CLI under-wires 00 loop

EOF
)"
```

---

### Task 1.1: Configurable Vision languages + fail-loud missing readers flag

**Files:**
- Modify: `src/readers/deployment.py`
- Create: `tests/readers/test_deployment_languages.py`
- Modify: `src/deployment/launch_profile.py` (create package + profile)

**Interfaces:**
- Consumes: `VISION_CONFIG` shape `{"languages": list[str], "dpi": int, "recognition_level": str}`
- Produces: `macos_readers(..., languages: Sequence[str] | None = None) -> Readers`; `LAUNCH_OCR_LANGUAGES: tuple[str, ...] = ("en-US", "zh-Hans", "zh-Hant", "ja-JP", "ko-KR")`

- [ ] **Step 1: Write the failing test**

```python
# tests/readers/test_deployment_languages.py
from readers.deployment import VISION_CONFIG, macos_readers

def test_default_vision_languages_include_cjk_for_launch_profile():
    from deployment.launch_profile import LAUNCH_OCR_LANGUAGES
    assert "en-US" in LAUNCH_OCR_LANGUAGES
    assert "zh-Hans" in LAUNCH_OCR_LANGUAGES

def test_macos_readers_folds_languages_into_ocr_config():
    readers = macos_readers(
        find_structured_strings=lambda text: (),
        languages=("en-US", "zh-Hans"),
    )
    assert readers["ocr_config"]["languages"] == ["en-US", "zh-Hans"]
    assert readers["ocr_config"]["dpi"] == VISION_CONFIG["dpi"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m pytest tests/readers/test_deployment_languages.py -p no:randomly -v`

Expected: FAIL (`deployment` import missing and/or languages still `["en-US"]` only).

- [ ] **Step 3: Implement profile + `macos_readers` languages kwarg**

```python
# src/deployment/__init__.py
"""Deployment chooser profiles — authorities the CLI injects. Not a numbered part."""

# src/deployment/launch_profile.py
"""Launch release gates and OCR language list (00 §2.7 CJK)."""
from __future__ import annotations

LAUNCH_OCR_LANGUAGES: tuple[str, ...] = (
    "en-US", "zh-Hans", "zh-Hant", "ja-JP", "ko-KR",
)

LAUNCH_SCHEMA_IDS: frozenset[str] = frozenset({
    "academic", "applications", "research", "career", "photos", "code",
    # safety detect/protect — not destination trees until Wave 3 says so
    "finance", "identity", "medical", "legal",
})

LAUNCH_DESTINATION_SCHEMA_IDS: frozenset[str] = frozenset({
    "academic", "applications", "research", "career", "photos", "code",
})
```

In `src/readers/deployment.py`, change `macos_readers` to accept `languages: Sequence[str] | None = None` and set `ocr_config = {**VISION_CONFIG, "languages": list(languages or VISION_CONFIG["languages"])}`. Keep `_no_reader` for formats not yet implemented in Task 1.2–1.4.

- [ ] **Step 4: Run tests — expect PASS**

Run: `PYTHONPATH=src python3 -m pytest tests/readers/test_deployment_languages.py -p no:randomly -v`

- [ ] **Step 5: Commit**

```bash
git add src/deployment/__init__.py src/deployment/launch_profile.py \
  src/readers/deployment.py tests/readers/test_deployment_languages.py
git commit -m "$(cat <<'EOF'
feat(readers): launch OCR languages include CJK; deployment profile package

EOF
)"
```

---

### Task 1.2: Ship a real DOCX reader (unsupported → actual text)

**Files:**
- Create: `src/readers/docx_zipxml.py`
- Modify: `src/readers/deployment.py` (bind `read_docx`)
- Create: `tests/readers/test_docx_zipxml.py`

**Interfaces:**
- Consumes: `extractors.structured_text.TextDocument`
- Produces: `read_docx(path: Path) -> TextDocument | None` (None only if not a zip/docx)

- [ ] **Step 1: Write failing test with a minimal docx zip fixture**

```python
# tests/readers/test_docx_zipxml.py
import zipfile
from pathlib import Path
from readers.docx_zipxml import read_docx

def _write_minimal_docx(path: Path, paragraph: str) -> None:
    # Minimal Office Open XML: [Content_Types] + word/document.xml
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body><w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p></w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document.main+xml"/>'
            '</Types>',
        )
        zf.writestr("word/document.xml", document_xml)

def test_read_docx_returns_paragraph_text(tmp_path: Path):
    path = tmp_path / "syllabus.docx"
    _write_minimal_docx(path, "Syllabus BUSIB 4300 Spring 2026")
    doc = read_docx(path)
    assert doc is not None
    assert "BUSIB 4300" in doc.text
```

- [ ] **Step 2: Run — expect FAIL (module missing)**

Run: `PYTHONPATH=src python3 -m pytest tests/readers/test_docx_zipxml.py -p no:randomly -v`

- [ ] **Step 3: Implement stdlib zip+xml reader**

Implement `read_docx` using only `zipfile` + `xml.etree.ElementTree`, concatenate `w:t` text nodes in document order, return `TextDocument(text=..., encoding="utf-8")` matching whatever constructor `extractors.structured_text.TextDocument` requires (inspect live signature before coding). On `BadZipFile`, return `None` (→ P5 `unsupported`), never raise into “failed” unless parse after open fails — then re-raise so P5 records `failed`.

Wire in `macos_readers`: `"read_docx": read_docx`.

- [ ] **Step 4: Extend CLI `_detect_format` for `.docx` → `"docx"`**

Modify `src/cli.py` `_detect_format` map to include `".docx": "docx"`.

- [ ] **Step 5: Tests PASS + commit**

```bash
git add src/readers/docx_zipxml.py src/readers/deployment.py src/cli.py \
  tests/readers/test_docx_zipxml.py
git commit -m "$(cat <<'EOF'
feat(readers): stdlib DOCX reader wired into macos deployment

EOF
)"
```

---

### Task 1.3: Image metadata reader + archive manifest reader

**Files:**
- Create: `src/readers/image_exif.py`
- Create: `src/readers/archive_manifest.py`
- Modify: `src/readers/deployment.py`
- Modify: `src/cli.py` (`_detect_format` for common image + archive suffixes)
- Create: `tests/readers/test_image_and_archive_readers.py`

**Interfaces:**
- Produces: `read_image(path) -> Mapping | None` matching P5 image reader contract (inspect `extractors.dispatch.Readers` / image extractor expected keys — EXIF datetime, dimensions; no pixel OCR here)
- Produces: `read_manifest(path) -> Mapping | None` listing member names/sizes without extracting payloads to disk

- [ ] **Step 1: Inspect live reader contracts**

Run:

```bash
PYTHONPATH=src python3 -c "import inspect; from extractors.dispatch import Readers; print(Readers)"
rg -n "read_image|read_manifest|ImageEvidence|Archive" src/extractors -g '*.py' | head -40
```

Write tests against the **live** return shape, not a guessed one.

- [ ] **Step 2: Implement + wire + detect formats**

Include at least: `.jpg`/`.jpeg`/`.png`/`.heic` (HEIC may return metadata-only or None if platform cannot parse — never pretend empty text success), `.zip` for manifest.

- [ ] **Step 3: Commit**

```bash
git add src/readers/image_exif.py src/readers/archive_manifest.py \
  src/readers/deployment.py src/cli.py tests/readers/test_image_and_archive_readers.py
git commit -m "$(cat <<'EOF'
feat(readers): image metadata and archive manifest on macos deployment

EOF
)"
```

---

### Task 1.4: Real `usable_threshold` so targeted OCR can fire

**Files:**
- Create: `src/deployment/usable.py`
- Modify: `src/cli.py` (replace `lambda facts, unresolved: True`)
- Create: `tests/deployment/test_usable_threshold.py`

**Interfaces:**
- Consumes: P6 facts iterable + unresolved iterable (same objects CLI already passes)
- Produces: `usable_threshold(facts, unresolved) -> bool` — **True** means “usable enough; skip targeted OCR”; **False** means “trigger targeted OCR path”

- [ ] **Step 1: Failing tests**

```python
# tests/deployment/test_usable_threshold.py
from deployment.usable import usable_threshold

def test_no_facts_and_unresolved_means_not_usable():
    assert usable_threshold(facts=(), unresolved=("x",)) is False

def test_any_direct_or_validated_fact_is_usable():
    fact = {"reliability_state": "direct", "field_key": "subject"}
    assert usable_threshold(facts=(fact,), unresolved=()) is True
```

Adjust field access to match real fact row/mapping shape from `facts.read_surface` / resolver output (inspect before locking the test).

- [ ] **Step 2: Implement** — treat “no facts and any unresolved” or “only possible-tier clues” as not usable; never invent numeric OCR confidence thresholds beyond presence/absence of usable fact states.

- [ ] **Step 3: Wire CLI**

```python
from deployment.usable import usable_threshold as launch_usable_threshold
# in authorities construction:
usable_threshold=launch_usable_threshold,
```

- [ ] **Step 4: Commit**

```bash
git add src/deployment/usable.py src/cli.py tests/deployment/test_usable_threshold.py
git commit -m "$(cat <<'EOF'
fix(cli): usable_threshold can trigger targeted OCR

EOF
)"
```

---

### Task 2.1: Academic §3.5 rules injected on the CLI resolver

**Files:**
- Create: `src/deployment/academic_rules.py`
- Modify: `src/cli.py` (`_resolver` stages)
- Create: `tests/deployment/test_academic_rules.py`
- Create: `tests/integration/test_cli_rule_facts.py`

**Interfaces:**
- Consumes: `facts.rules.Rule`, `facts.rules.ACADEMIC_CONTEXT_TERMS`, field key `subject` (D6)
- Produces: `ACADEMIC_SUBJECT_RULES: tuple[Rule, ...]` and a `rule` stage callable for `FactResolver`

- [ ] **Step 1: Inspect `rules` stage entrypoint**

```bash
PYTHONPATH=src python3 -c "import inspect; from facts import rules; print([n for n in dir(rules) if not n.startswith('_')])"
rg -n "def run_rules|def rule_facts|stages" src/facts/rules.py src/facts/resolver.py | head
```

- [ ] **Step 2: Author one course-code rule** using `ACADEMIC_CONTEXT_TERMS` and `field_key="subject"`. Pattern must be caller-supplied on `Rule` (module may ship the regex for the launch academic deployment — that is the chooser’s job, not `facts.rules` inventing a sixth context term).

- [ ] **Step 3: Wire**

```python
stages={"direct": _direct_stage, "rule": _rule_stage, "llm": None},
```

Keep `llm=None` until Task 2.3. Keep `model_route_permitted` False until Task 2.3.

- [ ] **Step 4: Integration test** — tiny `.txt` “Syllabus BUSIB 4300 …” through `cli.main` or `run_production_corpus` with test authorities; assert a `subject` fact at `validated`.

- [ ] **Step 5: Commit**

```bash
git add src/deployment/academic_rules.py src/cli.py \
  tests/deployment/test_academic_rules.py tests/integration/test_cli_rule_facts.py
git commit -m "$(cat <<'EOF'
feat(cli): inject academic §3.5 rules into FactResolver

EOF
)"
```

---

### Task 2.2: Close C-5 at deployment — inject `normalize` and `contradicts`

**Files:**
- Create: `src/deployment/validation_oracles.py`
- Create: `tests/deployment/test_validation_oracles.py`
- Modify: none under `src/facts/` (guard must keep failing if someone publishes normalize there)

**Interfaces:**
- Produces:

```python
def normalize(field_key: str, raw_value: str) -> str | object:  # value or not_normalizable sentinel
def contradicts(claim: Mapping, existing_fact: Mapping) -> bool
```

Match exact sentinel / types expected by `llm_harness.fact_validation` (inspect `ValidationDependencies` / Site A).

- [ ] **Step 1: Read live P8 dependency type**

```bash
rg -n "normalize|contradicts|ValidationDependencies|FactValidation" \
  src/llm_harness/fact_validation.py src/llm_harness/harness.py | head -40
```

- [ ] **Step 2: Implement minimal launch oracles**

- `normalize`: strip; for known date fields reuse `facts.dates` parsers; otherwise identity; refuse empty → not_normalizable
- `contradicts`: True only when same `field_key` and canonical values differ and existing reliability is stronger/equal per `facts.states.is_stronger`

- [ ] **Step 3: Guard test** — `facts` package still has no `normalize` attribute:

```python
import facts
def test_facts_does_not_publish_normalize():
    assert not hasattr(facts, "normalize")
```

- [ ] **Step 4: Commit**

```bash
git add src/deployment/validation_oracles.py tests/deployment/test_validation_oracles.py
git commit -m "$(cat <<'EOF'
feat(deployment): inject P8 normalize/contradicts oracles (C-5)

EOF
)"
```

---

### Task 2.3: Wire offline-safe P8 `run_call` into grouping + placement authorities

**Files:**
- Modify: `src/cli.py` (build `Gate`, `ModelClient` local/offline stub or real local client, `p8_run_call`, `p8_authorities`)
- Create: `src/deployment/p8_bindings.py`
- Create: `tests/integration/test_cli_p8_offline.py`
- Reference pattern: `tests/integration/test_live_path.py` (`_WiredRunCall`)

**Interfaces:**
- Consumes: `privacy.gate.Gate`, `llm_harness.harness.run_call`, deployment oracles
- Produces: `p8_run_call` matching `production.CorpusAuthorities` / grouping signature; `OPERATION_MODE` remains `"offline"` unless user opts in

- [ ] **Step 1: Copy the live-path wiring pattern into `deployment/p8_bindings.py`**

A function:

```python
def build_p8_run_call(*, gate: Gate, model_client, prompt, validation_dependencies, observed_at):
    def p8_run_call(conn, request, **authorities):
        return run_call(conn, request, gate=gate, model_client=model_client,
                        prompt=prompt, validation_dependencies=validation_dependencies,
                        observed_at=observed_at)
    return p8_run_call
```

Adjust kwargs to **exact** `run_call` signature (already verified: `conn, request, *, gate, model_client, prompt, validation_dependencies, observed_at`).

- [ ] **Step 2: Offline model client** — returns structured `unknown` for every call (so Site B/C abstain cleanly) OR uses a recorded fixture client. Must not open network sockets. Test that no DNS/TCP occurs (monkeypatch socket).

- [ ] **Step 3: Wire CLI** — replace `p8_run_call=None, p8_authorities=None` with real bindings; set `model_route_permitted` only for files Gate would release under offline/local policy.

- [ ] **Step 4: Integration test** — grouping receives a real `run_call` result type (`P8Verdict | NeedsConsent | …`), never `not_implemented_reason=no_model_call_configured`.

- [ ] **Step 5: Commit**

```bash
git add src/deployment/p8_bindings.py src/cli.py \
  tests/integration/test_cli_p8_offline.py
git commit -m "$(cat <<'EOF'
feat(cli): wire offline P8 run_call into corpus authorities

EOF
)"
```

---

### Task 2.4: Enable LLM fact stage behind Gate (optional path)

**Files:**
- Modify: `src/cli.py` / `src/deployment/` fact stage binder
- Create: `tests/integration/test_cli_llm_facts_unknown.py`

**Interfaces:**
- Consumes: `facts.llm_seam` proposal/apply APIs + P8 Site A
- Produces: `stages["llm"]` callable that abstains to `unknown` safely when client returns unknown

- [ ] **Step 1: Wire `llm` stage** using existing `facts.llm_seam` + P8 Site A validators with injected oracles from Task 2.2.

- [ ] **Step 2: Test** — ambiguous file yields unresolved/`unknown`, **no** invented field keys, **no** active fact without PASSING verdict.

- [ ] **Step 3: Commit**

```bash
git add src/cli.py src/deployment/*.py tests/integration/test_cli_llm_facts_unknown.py
git commit -m "$(cat <<'EOF'
feat(cli): LLM fact stage through Gate + Site A validator

EOF
)"
```

---

### Task 3.1: Gate non-launch destination schemas/templates by default

**Files:**
- Modify: `src/deployment/launch_profile.py`
- Modify: `src/cli.py` / catalogue load path
- Modify: `src/production.py` only if a pure filter hook is required (prefer filter in CLI before `design_tree`)
- Create: `tests/deployment/test_launch_catalogue_gate.py`

**Interfaces:**
- Produces: `filter_catalogue_for_launch(catalogue) -> catalogue` keeping only templates whose schema_id ∈ `LAUNCH_DESTINATION_SCHEMA_IDS`
- Finance/identity/medical/legal: remain in **recognition safety** handling map; **strip destination eligibility** from freeze catalogue unless `--all-schemas` flag

- [ ] **Step 1: Failing test** — default catalogue used by CLI contains no `law_practice` / `manufacturing` template applicability for freeze.

- [ ] **Step 2: Implement filter + CLI flag `--all-schemas` for escape hatch (explicit).**

- [ ] **Step 3: Commit**

```bash
git add src/deployment/launch_profile.py src/cli.py \
  tests/deployment/test_launch_catalogue_gate.py
git commit -m "$(cat <<'EOF'
feat(cli): default freeze catalogue to 00 launch destination domains

EOF
)"
```

---

### Task 4.1: Minimal residual library (Review Later + Independent Records)

**Files:**
- Create: `src/deployment/residual_library.py`
- Modify: `src/cli.py` (`RESIDUAL_LIBRARY = {}` → load launch residual)
- Create: `tests/deployment/test_residual_library.py`

**Interfaces:**
- Produces: non-empty mapping accepted by `tree_design.pipeline.design_tree(..., residual_library=...)`

- [ ] **Step 1: Inspect required residual library shape**

```bash
rg -n "residual_library" src/tree_design -g '*.py' | head -40
```

- [ ] **Step 2: Author the smallest library** that unblocks residual node projection for “Review Later” and one Independent Records style node — labels and policies from `00` residual language; no new thresholds.

- [ ] **Step 3: CLI wires `residual_library=LAUNCH_RESIDUAL_LIBRARY` and allows `residual_choices` from decisions when present.

- [ ] **Step 4: Commit**

```bash
git add src/deployment/residual_library.py src/cli.py \
  tests/deployment/test_residual_library.py
git commit -m "$(cat <<'EOF'
feat(cli): enable minimal residual library for tree projection

EOF
)"
```

---

### Task 5.1: Execute P12 plan (apply/undo)

**Files:** as listed in `docs/superpowers/plans/2026-08-29-p12-apply-undo.md` (`src/mutation/`, `tests/p12/`, …)

**Interfaces:** exactly those ratified in the P12 plan (A1–A9).

- [ ] **Step 1:** Open `docs/superpowers/plans/2026-08-29-p12-apply-undo.md`.
- [ ] **Step 2:** Execute **Task 1 through Done** of that plan with subagent-driven-development (or inline executing-plans). Do not edit P1–P11 sources (P12 A5).
- [ ] **Step 3:** Stop when P12’s own suite is green: `PYTHONPATH=src python3 -m pytest tests/p12/ -p no:randomly`
- [ ] **Step 4:** Record completion in `planning/27-dispatch-run-log.md` with HEAD sha (explicit path commit).

---

### Task 6.1: Execute P13 plan (review surface)

**Files:** as listed in `docs/superpowers/plans/2026-08-29-p13-review-approval-surface.md` (`src/review_surface/`, …)

- [ ] **Step 1:** Execute that plan task-by-task.
- [ ] **Step 2:** Green: `PYTHONPATH=src python3 -m pytest tests/p13/ -p no:randomly` (or path the P13 plan names).
- [ ] **Step 3:** Log completion.

---

### Task 7.1: CLI apply path — plan then mutate

**Files:**
- Modify: `src/cli.py` (replace terminal “Nothing was moved.” with optional `--apply` that calls P12)
- Create: `tests/integration/test_cli_apply_undo.py`

**Interfaces:**
- Consumes: P11 placement decisions + P10 `frozen_tree` + P12 apply transaction API (live names from P12 plan)
- Produces: journaled moves; default remains preview-only

- [ ] **Step 1: Default behavior unchanged** — without `--apply`, still prints preview and does not move.

- [ ] **Step 2: With `--apply`** — build P12 plans from accepted placements; run precondition checks; apply; print journal ids; refuse overwrite.

- [ ] **Step 3: `--undo <journal_id>`** — conditional undo per P12.

- [ ] **Step 4: Commit**

```bash
git add src/cli.py tests/integration/test_cli_apply_undo.py
git commit -m "$(cat <<'EOF'
feat(cli): optional --apply/--undo through P12 journal

EOF
)"
```

---

### Task 7.2: End-to-end 00 fidelity acceptance test

**Files:**
- Create: `tests/integration/test_cli_00_fidelity.py`

**Done-means (all must pass on a tiny fixture corpus):**
1. DOCX or PDF text yields stored P4 observations reused on second run (REUSE).
2. Academic syllabus text yields rule-validated `subject` **or** explicit unresolved — never silent empty success.
3. Freeze legal set ⊆ launch destination schemas (unless `--all-schemas`).
4. Placement abstains rather than inventing a node id.
5. Without `--apply`, zero filesystem moves; with `--apply`, journal exists and source/dest hashes verify.

- [ ] **Step 1: Write the test module** exercising `cli.main` against `tmp_path` corpus.
- [ ] **Step 2: Run until green.**
- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_cli_00_fidelity.py
git commit -m "$(cat <<'EOF'
test: end-to-end 00 fidelity acceptance for launch CLI path

EOF
)"
```

---

### Task 8.1: Write replacement conformance audit

**Files:**
- Create: `planning/43-00-fidelity-conformance-audit.md`

- [ ] **Step 1: Re-run focused suites** and record counts:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_cli_00_fidelity.py \
  tests/deployment tests/readers/test_docx_zipxml.py tests/p12 tests/p13 \
  -p no:randomly --tb=no -q
```

- [ ] **Step 2: For each Wave 1–7 Done-means**, cite `00` grep-verified quote + code path + pass/fail.
- [ ] **Step 3: Explicit remaining gaps** (embeddings still off by default is OK if documented; long-tail formats; catalogue R1c; NEEDS-JOSEPH).
- [ ] **Step 4: Commit**

```bash
git add planning/43-00-fidelity-conformance-audit.md
git commit -m "$(cat <<'EOF'
docs: 00 fidelity conformance audit after restore program

EOF
)"
```

---

## Self-review (author)

| Drift from audits | Task coverage |
|-------------------|---------------|
| Stale README / audit 28 / continue-here | 0.1 |
| OCR languages en-US only | 1.1 |
| DOCX/image/archive unwired | 1.2, 1.3 |
| `usable_threshold` always True | 1.4 |
| `rule`/`llm` None on CLI | 2.1, 2.4 |
| C-5 ValidationUnavailable | 2.2 |
| P8 unwired (`no_model_call_configured`) | 2.3 |
| 23 schemas vs six launch domains | 3.1 |
| Empty residual library | 4.1 |
| No APPLY / P12 | 5.1, 7.1 |
| No P13 review surface | 6.1 |
| End-to-end proof | 7.2, 8.1 |
| Finance safety vs destination | 3.1 (destination stripped; safety retained) |
| Invented CLI evidence spans | addressed indirectly by using real P4 locators in P8 bindings — if still present after 2.3, file a follow-up task in Wave 8 gaps rather than silently leaving `cli.py` `evidence_for` inventing `location="heading"` |

**Out of scope (do not smuggle in):** domain catalogue R1c edge reciprocity; nonprofit anchor politics; closing NEEDS-JOSEPH; Graphify dangling-endpoint cleanup; rewriting P6/P7 SPECs.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-29-restore-00-fidelity.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute in this session with checkpoints  

**Which approach?**
