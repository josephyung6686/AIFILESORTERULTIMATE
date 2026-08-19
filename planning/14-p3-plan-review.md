# P3 Plan Review — `planning/parts/P3-scan-corpus-selection/PLAN.md`

**(review in progress — findings are appended as they are confirmed)**

Reviewed against: P3 SPEC, `01-product-design-structured.md` (§1.1, §1.2, §8.2, §8.6),
the live P1 implementation in `src/database_agent/` (150 tests passing, verified
`python3 -m pytest -q` → `150 passed in 1.31s`), `11-ops-runtime.md`,
`10-i4-learning-ops.md`, and `13-p2-p3-plan-robustness.md`.

---

## Blocking findings — do not execute these as written

### B1 — `basic_record.py` uses `unicodedata`, `datetime` and `timezone` without importing them (Task 10)

**Where:** PLAN.md Task 10, Step 3, `src/scan_agent/basic_record.py`.

The module's import block is exactly:

```python
import json
import sqlite3
from collections.abc import Callable
from pathlib import Path, PurePath

from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path

from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM, event_defaults
```

and the body of `record_basic_record` then calls:

```python
        normalized_filename=unicodedata.normalize("NFC", path.name),
        ...
        observed_timestamps=json.dumps({
            "mtime": datetime.fromtimestamp(observed.mtime, timezone.utc).isoformat(),
        }),
```

`unicodedata`, `datetime` and `timezone` are all undefined names. The first non-excluded
file in any scan raises `NameError: name 'unicodedata' is not defined`.

**Why blocking:** this is the single function that produces R2. Every Done-means that
touches a `files` row (1, 10, 11, 17, 18) fails, and so do Tasks 11–18, which all scan.
`tests/p3/test_p3_basic_record.py` as written cannot go green.

**Fix:** add `import unicodedata` and `from datetime import datetime, timezone` to
`basic_record.py`'s import block.

### B2 — Task 17's `test_p3_defines_no_filename_normalization` fails against Task 10's own code

**Where:** PLAN.md Task 17, `tests/p3/test_p3_no_invention.py`, versus Task 10,
`src/scan_agent/basic_record.py`.

Task 17 asserts, over the concatenated text of every `src/scan_agent/*.py`:

```python
def test_p3_defines_no_filename_normalization():
    # SPEC Q1 is OPEN: Unicode form, case folding, whitespace and separator collapse,
    # extension retention and diacritic handling are all unstated.
    source = all_source()
    assert "unicodedata" not in source
    assert "casefold" not in source
    assert "NFC" not in source and "NFD" not in source
```

Task 10 writes, in `src/scan_agent/basic_record.py`:

```python
        normalized_filename=unicodedata.normalize("NFC", path.name),
```

`all_source()` is `"\n".join(path.read_text() for path in SOURCE_DIR.glob("*.py"))`,
so both `"unicodedata"` and `"NFC"` are present and the guard fails on its first two
assertions.

**Why blocking:** this is not a token false positive — it is the substantive
contradiction the guard exists to catch. Task 10 answers **P3 SPEC Q1** (*"`normalized
filename` is undefined … Unicode form, case folding, whitespace and separator collapse,
extension retention, and diacritic handling are all unstated"*) by choosing NFC in P3's
own code, which the SPEC says is open and Task 17's own prose says P3 must not do
(*"P3 does not ratify that choice and defines no normalization of its own; OQ1 stays
open"*). An executor hitting this will "fix" it by deleting or narrowing the guard —
Task 17 Step 3 explicitly tells them the fix is never in the guard — and Q1 gets
silently answered.

**Root cause:** the patch for P1's new `record_file` signature landed in Task 10 only.
Before the patch, P1 derived `normalized_filename` itself and P3 passed nothing; now
P3 must supply it, and the plan chose NFC without reconciling Task 17.

**Fix (a decision the plan must make explicitly, not a token edit):** make
`normalized_filename` a caller-supplied strategy exactly as `mime_type_for` and
`scan_state` already are — e.g. a required `normalize_filename` keyword on
`record_basic_record` / `scan`, with the test fixtures supplying
`unicodedata.normalize("NFC", ...)`. That keeps Q1 open in the same shape Q6 and Q4
are already held open in, keeps Task 17's guard green unchanged, and keeps P1's
required keyword satisfied. Deleting the guard's `unicodedata`/`NFC` assertions
instead would close Q1 by accident.


---

## Non-blocking findings

### N1 — Task 17's "Divergence recorded, not fixed here" block describes a P1 that no longer exists

**Where:** PLAN.md Task 17, the block-quoted paragraph above Step 1.

It says:

> P1's **plan** has `record_file` call `path.stat()` and `hash_file(path, ...)` itself,
> deriving filename, normalized filename, extension, size, timestamps and content hash
> from the path rather than storing what P3 observed. That is P1 re-deriving six of
> P3's ten. … Related: P1's `record_file` normalizes with
> `unicodedata.normalize("NFC", ...)`, which **answers P3 OQ1**.

The live P1 (`src/database_agent/files_table.py:65-118`) does none of that. Its
signature is

```python
def record_file(conn, path, *, filename, normalized_filename, extension,
                observed_size, observed_timestamps, parent_folder_context,
                mime_type, detected_format, scan_state, materialized,
                content_hash=None) -> str:
```

with the docstring `**P1 derives none of the R2 record.**`, and
`src/database_agent/files_table.py:29-31` carries an explicit
`NOTE: P1 deliberately has no timestamp/filename derivation helper.` The only thing
`record_file` still derives is the content hash (which P3's own SPEC assigns to P1)
and `volume_id_for(path)` (P1's field under §8.2).

The divergence this paragraph reports is **dead** — P1 fixed it. Leaving the text in
tells the executor P1 answers OQ1, which is exactly the mistaken premise that produced
B2. Delete the paragraph and replace it with the real current state: P1 requires the
five R2 fields as keywords with no default, so P3 is now the *only* possible author of
`normalized_filename`, and Q1 must therefore be held open at P3's own boundary (B2).


---

## Already sound — do not re-litigate

<!-- appended as confirmed -->

---

## Stale findings from `13-p2-p3-plan-robustness.md`

<!-- appended as confirmed -->

---

## Edit order

<!-- written last -->
