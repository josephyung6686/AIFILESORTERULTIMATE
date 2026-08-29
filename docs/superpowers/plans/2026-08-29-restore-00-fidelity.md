# Restore 00 Fidelity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the live product path (`src/cli.py` → `production.run_production_corpus`) actually perform the hybrid loop `planning/00-database-agent-product-design.md` describes — extract usable evidence, produce validated facts, group and place with optional gated LLM help, then apply moves with undo — instead of a deterministic PDF/text slice that prints “Nothing was moved.”

**Architecture:** Packages P1–P11 already encode most of `00`. The drift is in **deployment wiring and missing mutation/review parts**. This program (1) tells the truth in docs, (2) wires readers/rules/P8/oracles/residual/catalogue gates into the CLI chooser, (3) executes the already-authored P12 and P13 plans, (4) connects CLI to apply/review, (5) re-audits against `00`. Do not invent second homes for vocabulary inside `production.py` / `orchestrator.py` — inject authorities from `cli.py` or a new `src/deployment/` profile module.

**Tech Stack:** Python 3.12, stdlib SQLite core, optional `readers` extra (pdfminer.six, pyobjc Vision), pytest with `-p no:randomly` when thinc/spaCy is importable, existing `llm_harness` / `privacy.Gate` / `facts` seams.

**Spec (authority order — every task reads these before coding):**

1. `planning/00-database-agent-product-design.md` — product truth; quote only after `grep -F`
2. Part **SPEC.md** for the wave (table below) — Contract in/out + **Done means** are the acceptance tests
3. Part PLAN.md / sibling restore plans — how to build; SPEC wins on conflict
4. Live `src/` signatures — win over stale plan line numbers
5. Audits / `.planning/codebase/*` — evidence of drift only; not authority to invent behaviour

| Wave | Primary SPEC(s) an implementer must open |
|------|------------------------------------------|
| 1 | `planning/parts/P5-extractors/SPEC.md` (esp. Done means 1, 5–10; Contract out on readers / OCR / routing) |
| 2 | `planning/parts/P6-facts-facets/SPEC.md` (Done means 4, 8, 11, 17) · `planning/parts/P7-privacy-consent-gate/SPEC.md` (Done means 3, 7, 12, 13) · `planning/parts/P8-llm-harness-validator/SPEC.md` (Done means 1, 5, 10, 13) · `planning/parts/P9-grouping/SPEC.md` (Contract out on P8 seam; Done means that require harness fixtures) |
| 3 | `planning/parts/P6-facts-facets/SPEC.md` (§3.11 / Deferred launch set) · `planning/parts/P10-tree-design-freeze/SPEC.md` (Contract out §3 template schema; Deferred: dimensions beyond five §5.4 names; Done means on freeze closed set) |
| 4 | `planning/parts/P10-tree-design-freeze/SPEC.md` (Contract out §6 residual nine names; Deferred residual slot *contents*) · `planning/parts/P11-placement-residual/SPEC.md` (residual workflow ownership) |
| 5 | `planning/parts/P12-apply-undo/SPEC.md` + plan `docs/superpowers/plans/2026-08-29-p12-apply-undo.md` |
| 6 | `planning/parts/P13-review-approval-surface/SPEC.md` + plan `docs/superpowers/plans/2026-08-29-p13-review-approval-surface.md` |
| 7–8 | P11 + P12 + P13 SPECs together; re-audit cites SPEC Done means numbers, not package presence |

**Rule:** A task is not done because CLI behaviour “looks better.” It is done when the cited SPEC **Done means** (or an explicitly scoped subset for a deployment profile) are green *on the live CLI path*, or the task documents which Done means remain package-only and why (with SPEC open-question id).

## Global Constraints

- **`00` wins; SPECs operationalize `00`.** Grep-verify every `00` quotation. Do not invent SPEC behaviour that is listed under **Deferred** or **Open questions** — inject or leave open.
- **`python3`, not `python`.** Full-suite: `python3 -m pytest tests/ -p no:randomly` (or `-p randomly --randomly-dont-reset-seed` per `pyproject.toml`).
- **Explicit pathspec commits only.** Never `git add -A` / wildcards over `planning/domains/nodes/`.
- **Composition invents no domain defaults.** Thresholds, catalogues, readers, `normalize`/`contradicts`, consent scopes: injected from CLI/deployment profiles (P5/P6/P7/P8 SPECs: Deferred / no defaults).
- **P7 before any model content.** P7 Done means 7 / P8 Done means 13: `NeedsConsent` unchanged — never coerced to abstain/deny.
- **C-5:** P6 SPEC / `facts.llm_seam` — `facts` must not publish `normalize(` / `contradicts(`. P8 SPEC Deferred table files domain oracles to injection. Deployment supplies them into P8 `validation_dependencies`.
- **After freeze:** P10/P11 SPECs — no invented destinations. P11 places or abstains; only P12 mutates the filesystem (P12 SPEC Purpose / Contract out).
- **Protected material:** P7 Done means 9–10; P12/P13 SPECs — marked and counted, never opened.
- **Launch-domain default:** P6 SPEC §3.11 / Deferred and P10 Deferred (five §5.4 template dimensions): academic, applications, research, career, photos, code as destination; finance/identity/medical/legal as **safety** first (P7), not freeze destinations until explicitly enabled.
- **Do not re-open ratified decisions** (D1–D6, J-IND, J-DEPTH; P6 D6 `subject`). Do not close open NEEDS-JOSEPH / SPEC Open questions.
- **Sibling plans (do not rewrite):** `docs/superpowers/plans/2026-08-29-p12-apply-undo.md`, `docs/superpowers/plans/2026-08-29-p13-review-approval-surface.md` — those plans already bind to P12/P13 SPECs.

## Program waves (ship independently)

| Wave | Outcome | SPEC acceptance focus | Depends on |
|------|---------|----------------------|------------|
| **0** | Docs/audits match HEAD | — | — |
| **1** | Extraction fidelity on CLI | P5 Done means 1, 5–10 on deployed readers | 0 |
| **2** | Hybrid facts + P8 on CLI (offline-safe) | P6 DM 4/8/11/17 · P7 DM 3/7/12/13 · P8 DM 1/5/10/13 | 1 |
| **3** | Launch-domain catalogue gate | P6 §3.11 launch set · P10 freeze closed set | 1 |
| **4** | Minimal residual library enabled | P10 Contract out §6 names; slot *contents* stay Deferred | 3 |
| **5** | P12 apply/undo green | Entire P12 SPEC Done means via sibling plan | 0 |
| **6** | P13 review surface green | Entire P13 SPEC Done means via sibling plan | 5 preferred |
| **7** | CLI apply path | P11 + P12 + P7 `may_move_automatically` | 2, 4, 5, 6 |
| **8** | Fresh conformance audit | Trace each claim to SPEC Done means # | 7 |

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
`build/p6-p7-first-packages`. Authority order:
[`planning/00-database-agent-product-design.md`](planning/00-database-agent-product-design.md)
→ part SPECs under [`planning/parts/`](planning/parts/) → plans → live `src/`.
P12/P13 have SPECs + plans but are not yet in `src/`. The shipped CLI currently
under-wires SPEC Done means (deterministic slice; no apply) — see
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

**SPEC:** `planning/parts/P5-extractors/SPEC.md` — Design slice OCR / §2.7; Done means **9** (OCR persists §2.7 fields; languages are configuration folded into cache key). Do **not** invent DPI/recognition defaults beyond what SPEC + `00` already name; languages list is deployment configuration (SPEC Deferred / Open questions on exact language packs — CJK required by `00` §2.7 when corpus needs it).

**Files:**
- Modify: `src/readers/deployment.py`
- Create: `tests/readers/test_deployment_languages.py`
- Modify: `src/deployment/launch_profile.py` (create package + profile)

**Interfaces:**
- Consumes: `VISION_CONFIG` shape `{"languages": list[str], "dpi": int, "recognition_level": str}`
- Produces: `macos_readers(..., languages: Sequence[str] | None = None) -> Readers`; `LAUNCH_OCR_LANGUAGES: tuple[str, ...] = ("en-US", "zh-Hans", "zh-Hant", "ja-JP", "ko-KR")`

**Done-means (this task):**
- Changing `languages` changes `ocr_config` on the `Readers` object and is the value stored/used for OCR cache identity (P5 DM 9 / §2.7 cache-key intent).
- Launch profile languages include CJK codes; en-US alone is insufficient for the launch chooser.

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

**SPEC:** `planning/parts/P5-extractors/SPEC.md` — Done means **1** (`unsupported` ≠ empty complete), **2** (P4 shape, no per-format consumer branch), **6** (DOCX table cells and heading zones distinguishable from body). Contract out: deployment may omit a library → `unsupported`; once a reader ships, outcomes must be real observations, not silent empty docs (`00` / SPEC §2.4).

**Files:**
- Create: `src/readers/docx_zipxml.py`
- Modify: `src/readers/deployment.py` (bind `read_docx`)
- Create: `tests/readers/test_docx_zipxml.py`

**Interfaces:**
- Consumes: `extractors.structured_text.TextDocument` (live signature)
- Produces: `read_docx(path: Path) -> TextDocument | None` (None only if not a zip/docx → P5 `unsupported`)

**Done-means (this task):**
- Minimal docx fixture yields observations readable through P4 shape (P5 DM 2).
- Heading vs body distinguishable when XML carries both (P5 DM 6) — if minimal fixture cannot express tables yet, add a second fixture before claiming DM 6 complete; otherwise mark DM 6 partial in the commit message and finish in a follow-up step of this same task.

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

**SPEC:** `planning/parts/P5-extractors/SPEC.md` — Done means **7** (no archive byte written outside process; bomb/protected/nested terminate marked), **8** (HEIC extracts; §2.6 traps abstain — no invented photo/screenshot conclusion in E5), **10** (routing signature over extension on disagree fixture; each family has handler or explicit `unsupported`).

**Files:**
- Create: `src/readers/image_exif.py`
- Create: `src/readers/archive_manifest.py`
- Modify: `src/readers/deployment.py`
- Modify: `src/cli.py` (`_detect_format` for common image + archive suffixes)
- Create: `tests/readers/test_image_and_archive_readers.py`

**Interfaces:**
- Produces: `read_image(path) -> Mapping | None` matching P5 image reader contract (inspect live extractor)
- Produces: `read_manifest(path) -> Mapping | None` listing member names/sizes without extracting payloads to disk

**Done-means (this task):**
- Archive fixture: zero files written under `tmp_path` outside the input archive (P5 DM 7).
- HEIC: either real extract or explicit `unsupported`/`unreadable` — never empty-as-success (P5 DM 1, 8).
- CLI format map expanded so router can select families; disagree fixture still prefers signature when P5 path is used (P5 DM 10) — do not weaken `extractors.router`.

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

**SPEC:** `planning/parts/P5-extractors/SPEC.md` — Done means **5** (two text-layer states behave differently; no global language-quality check). Targeted OCR after failed usable facts is `00` §2.7 / P5 Contract sequencing with P6 — orchestrator already sequences; CLI must not hard-wire “always usable.” Do **not** invent a numeric language-quality score (SPEC forbids global language-quality check).

**Files:**
- Create: `src/deployment/usable.py`
- Modify: `src/cli.py` (replace `lambda facts, unresolved: True`)
- Create: `tests/deployment/test_usable_threshold.py`

**Interfaces:**
- Consumes: P6 facts iterable + unresolved iterable (same objects CLI already passes into `P1P7Authorities.usable_threshold`)
- Produces: `usable_threshold(facts, unresolved) -> bool` — **True** = skip targeted OCR; **False** = allow targeted OCR path

**Done-means (this task):**
- Broken-text fixture with unresolved / no direct|validated facts returns False (P5 DM 5 path can fire).
- File with direct/validated fact returns True.
- No module under `src/deployment/` or `src/cli.py` introduces a “language quality” score API.

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

**SPEC:** `planning/parts/P6-facts-facets/SPEC.md` — Done means **4** (syllabus fixture → `subject`/term/work type with evidence), **8** (no academic context → no `subject`; capital-S Syllabus → yes), **17** (items 4–10 work with P8 absent). Contract: context terms for academic are exactly the five in `facts.rules.ACADEMIC_CONTEXT_TERMS`; field key is **`subject`** (D6). Pattern regex is **injected** (Deferred catalogue) — deployment may author the launch regex; `facts.rules` must not grow a sixth context term.

**Files:**
- Create: `src/deployment/academic_rules.py`
- Modify: `src/cli.py` (`_resolver` stages)
- Create: `tests/deployment/test_academic_rules.py`
- Create: `tests/integration/test_cli_rule_facts.py`

**Interfaces:**
- Consumes: `facts.rules.Rule`, `facts.rules.ACADEMIC_CONTEXT_TERMS`, field key `subject` (D6)
- Produces: `ACADEMIC_SUBJECT_RULES: tuple[Rule, ...]` and a `rule` stage callable for `FactResolver`

**Done-means (this task):**
- P6 DM 8 positive + negative cases pass through CLI/`FactResolver` with `llm=None` (supports DM 17).
- Stored key is `subject`, never `course`.

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

**SPEC:** `planning/parts/P6-facts-facets/SPEC.md` Done means **11** (LLM proposal absent citation / out-of-schema / contradicted by stronger fact → no fact). `planning/parts/P8-llm-harness-validator/SPEC.md` Contract out Site A four checks; **Deferred** table: domain `normalize` / `contradicts` are **not** authored by P8 — injected. `src/facts/llm_seam.py` documents C-5: P6 publishes **neither** function.

**Files:**
- Create: `src/deployment/validation_oracles.py`
- Create: `tests/deployment/test_validation_oracles.py`
- Modify: none under `src/facts/` (guard must keep failing if someone publishes normalize there)

**Interfaces:**
- Produces: `normalize` / `contradicts` matching exact types expected by `llm_harness.fact_validation` / `ValidationDependencies` (inspect live)

**Done-means (this task):**
- P8 Site A can run with injected oracles without `ValidationUnavailable` solely due to missing callbacks.
- `import facts; hasattr(facts, "normalize")` is False (C-5 / llm_seam guard).
- Fixture: altered citation / missing field / contradicting direct fact → reject or no active fact (P6 DM 11 / P8 DM 3–4).

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

**SPEC:** `planning/parts/P7-privacy-consent-gate/SPEC.md` Done means **3** (one egress; only `Released`), **7** (`NeedsConsent` not converted), **12** (local-first default offline|local_model), **13** (gate installed; offline deliberate call Denied). `planning/parts/P8-llm-harness-validator/SPEC.md` Done means **1**, **5** (`unknown`→abstain), **10** (refusals are abstentions, NeedsConsent not in that list), **13**. `planning/parts/P9-grouping/SPEC.md` Contract in: P8 seam for model coherence — `p8_run_call` must match live signature (see `tests/integration/test_live_path.py`).

**Files:**
- Modify: `src/cli.py` (build `Gate`, offline `ModelClient`, `p8_run_call`, `p8_authorities`)
- Create: `src/deployment/p8_bindings.py`
- Create: `tests/integration/test_cli_p8_offline.py`
- Reference pattern: `tests/integration/test_live_path.py` (`_WiredRunCall`)

**Interfaces:**
- Consumes: `privacy.gate.Gate`, `llm_harness.harness.run_call`, deployment oracles (Task 2.2)
- Produces: `p8_run_call` / `p8_authorities` pair required by `production` (both None or both set)

**Done-means (this task):**
- Static/runtime: model transport still single-egress with `Released` only (P7 DM 3 / P8 DM 1).
- `NeedsConsent` fixture returns consent branch, no abstain metric (P7 DM 7 / P8 DM 13).
- Shipped CLI default mode is `offline` or `local_model` (P7 DM 12) — already `OPERATION_MODE="offline"`; do not regress.
- Grouping no longer records `not_implemented_reason=no_model_call_configured` when profile enables P8.

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

**SPEC:** `planning/parts/P6-facts-facets/SPEC.md` Done means **3** (no runtime field mint), **11**, **12** (`possible` not proposal-eligible). `planning/parts/P8-llm-harness-validator/SPEC.md` Done means **5–6** (`unknown`→abstain; `may_propose: false` holds).

**Files:**
- Modify: `src/cli.py` / `src/deployment/` fact stage binder
- Create: `tests/integration/test_cli_llm_facts_unknown.py`

**Interfaces:**
- Consumes: `facts.llm_seam` + P8 Site A + Task 2.2 oracles
- Produces: `stages["llm"]` callable

**Done-means (this task):**
- Ambiguous file: `unknown` or unresolved — **no** invented schema field (P6 DM 3, 11).
- No `may_propose: false` verdict appears in proposal-eligible reads (P8 DM 6 / P6 DM 12).

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

**SPEC:** `planning/parts/P6-facts-facets/SPEC.md` — §3.11 / Deferred: launch domains and safety domains; do not treat the full professional schema roster as the freeze catalogue by default. `planning/parts/P10-tree-design-freeze/SPEC.md` — Contract out §3 (template schema); Deferred: dimensions beyond five §5.4 names (Academic/Applications/Research/Career/Photos); Code + Finance have fact schemas but **no design-stated dimensions** until Open questions close. `planning/parts/P7-privacy-consent-gate/SPEC.md` — finance/identity/medical/legal as **safety** handling before automated placement.

**Files:**
- Modify: `src/deployment/launch_profile.py`
- Modify: `src/cli.py` / catalogue load path
- Modify: `src/production.py` only if a pure filter hook is required (prefer filter in CLI before `design_tree`)
- Create: `tests/deployment/test_launch_catalogue_gate.py`

**Interfaces:**
- Produces: `filter_catalogue_for_launch(catalogue) -> catalogue` keeping templates whose schema_id ∈ `LAUNCH_DESTINATION_SCHEMA_IDS`
- Finance/identity/medical/legal: stay in recognition **safety** map; **absent** from default freeze destination catalogue unless `--all-schemas`

**Done-means (this task):**
- Default freeze legal set ⊆ launch destination schemas (P10 freeze closed-set intent).
- Safety domains still classifiable via P7 path (P7 DM 2) without becoming destination templates by default.

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

**SPEC:** `planning/parts/P10-tree-design-freeze/SPEC.md` — Contract out §6: **nine** residual template **names** are fixed; **slot contents** (evidence patterns, types, sensitivity, depth, default parents) are **Deferred** — do not invent full §7.2 attribute packs. Ship the smallest enablement that unblocks projection (names + enablement model already in SPEC). `planning/parts/P11-placement-residual/SPEC.md` owns residual workflow after freeze.

**Files:**
- Create: `src/deployment/residual_library.py`
- Modify: `src/cli.py` (`RESIDUAL_LIBRARY = {}` → load launch residual)
- Create: `tests/deployment/test_residual_library.py`

**Interfaces:**
- Produces: non-empty mapping accepted by `tree_design.pipeline.design_tree(..., residual_library=...)`

**Done-means (this task):**
- With library present, `design_tree` no longer early-returns solely because residual library is empty (P10 residual projection path).
- No invented residual names outside SPEC’s nine (grep library keys ⊆ Contract out §6 names).
- Slot fields left empty/Deferred-safe rather than fabricated patterns.

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

**SPEC:** `planning/parts/P12-apply-undo/SPEC.md` (entire Done means list). **Plan:** `docs/superpowers/plans/2026-08-29-p12-apply-undo.md` (already binds A1–A9 to that SPEC — do not fork).

**Files:** as listed in the P12 plan (`src/mutation/`, `tests/p12/`, …)

**Interfaces:** exactly those ratified in the P12 plan / P12 SPEC Contract out.

- [ ] **Step 1:** Open SPEC + plan; confirm Done means numbering still matches plan tasks.
- [ ] **Step 2:** Execute **Task 1 through Done** of the P12 plan with subagent-driven-development (or inline executing-plans). Do not edit P1–P11 sources (P12 plan A5 / SPEC ownership).
- [ ] **Step 3:** Stop when P12’s suite is green: `PYTHONPATH=src python3 -m pytest tests/p12/ -p no:randomly`
- [ ] **Step 4:** Record completion in `planning/27-dispatch-run-log.md` with HEAD sha + which SPEC Done means were asserted (explicit path commit).

---

### Task 6.1: Execute P13 plan (review surface)

**SPEC:** `planning/parts/P13-review-approval-surface/SPEC.md` (entire Done means list). **Plan:** `docs/superpowers/plans/2026-08-29-p13-review-approval-surface.md` (binds B2/B3/M8/M14 to SPEC — do not fork).

**Files:** as listed in the P13 plan (`src/review_surface/`, …)

- [ ] **Step 1:** Execute that plan task-by-task against the SPEC Done means.
- [ ] **Step 2:** Green: path named in the P13 plan (`tests/p13/` or equivalent).
- [ ] **Step 3:** Log completion with SPEC Done means coverage notes.

---

### Task 7.1: CLI apply path — plan then mutate

**SPEC:** `planning/parts/P11-placement-residual/SPEC.md` — placement decides; **moves nothing**. `planning/parts/P12-apply-undo/SPEC.md` — sole mutator; Contract out move plan + refusal classes. `planning/parts/P7-privacy-consent-gate/SPEC.md` Done means **9** (`may_move_automatically` consumed, not re-derived).

**Files:**
- Modify: `src/cli.py` (replace terminal “Nothing was moved.” with optional `--apply` that calls P12)
- Create: `tests/integration/test_cli_apply_undo.py`

**Interfaces:**
- Consumes: P11 placement decisions + P10 `frozen_tree` + P12 apply API (live names from P12)
- Produces: journaled moves; default remains preview-only

**Done-means (this task):**
- Without `--apply`: zero filesystem mutations (P11 “moves nothing”).
- With `--apply`: P12 preconditions + journal; never silent overwrite (P12 SPEC / `00` §8.3).
- Protected files: `may_move_automatically` false ⇒ refuse (P7 DM 9).

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

### Task 7.2: End-to-end 00 + SPEC fidelity acceptance test

**SPEC cross-check (must cite numbers in test docstrings):**
- P5 DM 1, 11 (outcome + REUSE determinism)
- P6 DM 4 or 8 (academic subject path)
- P10 freeze closed set / P11 abstain-not-invent
- P12 journal when `--apply` (or skip apply assertions if Wave 5 incomplete — fail clearly)

**Files:**
- Create: `tests/integration/test_cli_00_fidelity.py`

**Done-means (all must pass on a tiny fixture corpus):**
1. DOCX or PDF text yields stored P4 observations reused on second run (P5 DM 11).
2. Academic syllabus text yields rule-validated `subject` **or** explicit unresolved — never silent empty success (P6 DM 4/8).
3. Freeze legal set ⊆ launch destination schemas (unless `--all-schemas`) (P10 + Task 3.1).
4. Placement abstains rather than inventing a node id (P11 SPEC).
5. Without `--apply`, zero filesystem moves; with `--apply`, journal exists and hashes verify (P11/P12).

- [ ] **Step 1: Write the test module** exercising `cli.main` against `tmp_path` corpus; each test names SPEC Done means in its docstring.
- [ ] **Step 2: Run until green.**
- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_cli_00_fidelity.py
git commit -m "$(cat <<'EOF'
test: end-to-end 00/SPEC fidelity acceptance for launch CLI path

EOF
)"
```

---

### Task 8.1: Write replacement conformance audit

**SPEC:** Re-audit format must map **every** Wave 1–7 claim to a SPEC Done means id (or Deferred/Open question id). Do not claim “P8 exists” as conformance — claim P8 DM 1/5/13 on the CLI path.

**Files:**
- Create: `planning/43-00-fidelity-conformance-audit.md`

- [ ] **Step 1: Re-run focused suites** and record counts:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_cli_00_fidelity.py \
  tests/deployment tests/readers/test_docx_zipxml.py tests/p12 tests/p13 \
  -p no:randomly --tb=no -q
```

- [ ] **Step 2: For each Wave 1–7 Done-means**, cite `00` grep-verified quote **and** SPEC Done means # + code path + pass/fail.
- [ ] **Step 3: Explicit remaining gaps** (embeddings off; long-tail formats; catalogue R1c; SPEC Open questions; Deferred residual slots).
- [ ] **Step 4: Commit**

```bash
git add planning/43-00-fidelity-conformance-audit.md
git commit -m "$(cat <<'EOF'
docs: 00/SPEC fidelity conformance audit after restore program

EOF
)"
```

---

## Self-review (author)

| Drift from audits | Task coverage | SPEC Done means |
|-------------------|---------------|-----------------|
| Stale README / audit 28 / continue-here | 0.1 | docs |
| OCR languages en-US only | 1.1 | P5 DM 9 |
| DOCX/image/archive unwired | 1.2, 1.3 | P5 DM 1,6,7,8,10 |
| `usable_threshold` always True | 1.4 | P5 DM 5 |
| `rule`/`llm` None on CLI | 2.1, 2.4 | P6 DM 4,8,11,17 |
| C-5 ValidationUnavailable | 2.2 | P6 DM 11 · P8 Site A Deferred |
| P8 unwired | 2.3 | P7 DM 3,7,12,13 · P8 DM 1,5,10,13 |
| 23 schemas vs six launch domains | 3.1 | P6 §3.11 · P10 Deferred §5.4 |
| Empty residual library | 4.1 | P10 Contract out §6 |
| No APPLY / P12 | 5.1, 7.1 | P12 SPEC · P11 moves nothing |
| No P13 review surface | 6.1 | P13 SPEC |
| End-to-end proof | 7.2, 8.1 | cross-SPEC |
| Finance safety vs destination | 3.1 | P7 safety · P10 no Finance dimensions |

**Out of scope (do not smuggle in):** domain catalogue R1c; nonprofit anchor politics; closing SPEC Open questions / NEEDS-JOSEPH; inventing Deferred residual slot contents; rewriting P6/P7 SPECs.

**Placeholder scan:** none intentional — P12/P13 point at complete sibling plans that already contain full TDD steps bound to SPECs.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-29-restore-00-fidelity.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute in this session with checkpoints  

**Which approach?**
