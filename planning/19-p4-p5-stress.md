# P4 / P5 stress test — what actually breaks

Date: 2026-08-21
Status: **Not perfect.** Rechecked later the same night: break 1 (fingerprint) is **closed**. Breaks 2–5 and the corpus holes are **unchanged**. Live probes 2026-08-21 ~00:22.

Original pass: packages green in isolation and did not join. `pytest tests/p4 tests/p5 -q` → **623 passed**. Every break was executed against live `src/evidence_shape/` and `src/extractors/`, not inferred from PLAN prose.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md). Ratifications 2026-08-20 still stand; several of them are **not what the code does**.

This is not a re-read of [`15-p4-p5-plan-robustness.md`](15-p4-p5-plan-robustness.md) or [`18-p4-p5-prebuild.md`](18-p4-p5-prebuild.md). Those reviewed plans. This tried to break the running packages the way a messy Mac corpus would.

---

## Verdict

P4 and P5 each do what their unit tests ask. They are **not** a working join and **not** a perfect sorter.

**Recheck 2026-08-21 ~00:22.** Break 1 is closed: P5 `fingerprint` now calls P4 `sha256_of`, and `run_from_mapping` accepts a P5 run. Still open: `TierConflict` on `.dmg` / `.psd`, zero `except` in `src/extractors/`, D10 only on PDF and archives, P5 `append` still writes around P4, no `EvidenceSink.write`, no `dataless_result`, no `extract(...)` dispatcher. GIF/WebP/audio still `unsupported`.

Do not start the Wave-2 orchestrator until breaks 2–5 are closed. Coverage holes after that are product-scope, not join-blockers.

---

## Confirmed breaks (executed 2026-08-21)

### 1. P5’s `config_fingerprint` is not P4’s — every stored run is refused

P5 `extractors.shape.fingerprint` hashes `canonical_json(config)` as raw UTF-8.

P4 `evidence_shape.runs.config_fingerprint` hashes the same JSON through `sha256_of`, which **length-prefixes** the string first (`N:bytes`). Same config, two digests:

| | `{"dpi":200,"languages":["en","zh-Hans"]}` |
|---|---|
| P5 | `sha256:2e0a05c7…de21c8c` |
| P4 | `sha256:e79df100…bf65d9` |

`run_from_mapping` then raises `MalformedRun`: the fingerprint “is not the fingerprint of this config.” There is no `EvidenceSink` implementation in P4 (`store.py` is `record_run` / `record_observation` / `record_text_unit`, none of them a batch). The first orchestrator `sink.write(p5_result)` dies on the first file.

P5’s own comment in `events.py` claims the two fingerprints are the same identity. They are not.

**Close:** P5 must call `evidence_shape.canonical.sha256_of` / `evidence_shape.runs.config_fingerprint`. Delete `extractors.shape.fingerprint` as a second hash. Do not “fix” P4 to the weaker hash — length-prefixing is the injective property P4 Task 5 exists for.

### 2. `extraction_status_by_tier` raises on every unrouted file

`unrouted_result` reuses `filesystem.record` and `analysis_tier="filesystem"`. The filesystem run is `complete`. The unrouted run is `metadata_only` (`.dmg`) or `unreadable` (`.psd`). Same tier, two completeness values → `TierConflict`.

Executed:

- `archive.dmg`: `complete` + `metadata_only` → conflict.
- `design.psd` + `extract_filesystem` → conflict.

A4 (2026-08-20): a routed-but-stopped run carries **`analysis_tier: native`**. The stopping run is not a second filesystem extract. It is the native extractor that did not exist or refused to open. Using `filesystem.record` as `extractor_name` also makes §3.4’s cache key for “no extractor” look like “the filesystem extractor ran twice.”

`test_a_disk_image_stops_at_metadata_only_and_is_still_indexed` writes both runs and never calls `extraction_status_by_tier`. The orchestrator sketch does. The first `.dmg` in Downloads would abort the status write for that file.

**Close:** `unrouted_result` is its own extractor name (or `extractor_name is None` mapped to a dedicated stopped-run name P4 will accept), `analysis_tier="native"` per A4, zero observations for `unsupported` / `metadata_only` as now. Filesystem run stays the indexer.

### 3. No `failed` path exists in P5

`src/extractors/` contains **zero** `except`. A password-protected PDF, a corrupt ZIP, a reader that raises, a truncated DOCX — all propagate. The orchestrator sketch catches only `ProtectedContainerRefused` and `DatalessRefused`. §2.4’s `completeness=failed` is in the vocabulary and in P4 rule 9. Nothing produces it.

A real corpus has these files. Today they crash the scan, they do not become indexed-but-failed rows.

**Close:** one catcher around the injected reader (orchestrator or a single P5 `extract(...)`). Map unexpected reader errors to `failed` + `failure_reason`. Do not invent a threshold for “too corrupt.” The exception is the signal.

### 4. D10 is optional, and most extractors skip it

P4 publishes `collapse_key` and **enforces no uniqueness**. Deliberate in P4. P5 promised six extractors collapse the same way.

Live: `_collapse` exists in `pdf.py` and `archive.py` only. `docx.py`, `structured_text.py`, `long_tail.py`, `ocr.py`, `image.py`, `filesystem.py` emit one row per hit.

Executed against `extract_docx`: two body hits of `Columbia` → two observations, each `occurrence_count=1`. D10 wants one row, count 2, first location.

That is not a P4 bug. It is P5 shipping a sorter whose DOCX/CSV/OCR evidence will explode row counts and split P6 weights across clones of the same string. PDF happens to be the one family the product’s academic examples care about, which is why the tests look comprehensive.

**Close:** one `_collapse` (or P4’s `collapse_key` on mappings) used by every emitter. A sink-level check that rejects an uncollapsed batch is the only way this stays true after a sixth extractor is added.

### 5. Two event writers, P4 landed, P5 still writes around it

P4 `record_run_event` exists. P5 `extractors.events.append` still calls `database_agent.events.append_event` directly. The file header still says “WHEN P4 LANDS.” It has.

An orchestrator that follows both plans writes two `extraction` events per run, or one event whose `explanation` is P5’s payload and not P4’s `observation_keys` list. Done-means “exactly one event per run” cannot hold.

**Close:** `append` becomes `record_run_event(conn, run_id, author="P5")`. Keep `extraction_event` / `ocr_event` only if something still needs the dict; do not INSERT it.

---

## Confirmed smaller fractures

These will not crash the first file. They will make citations and routing lie.

| # | What I did | What happened | Why it matters |
|---|---|---|---|
| OCR name | `extractor_name_for("apple-vision")` | `ocr.apple-vision` | P4 fixtures and P2 examples use `ocr.apple_vision`. Two names, two cache keys, two replay sets for one engine. Pin the string the engine actually reports; do not have a second spelling in fixtures. |
| Empty `raw_value` | `Observation(raw_value="")` vs P5 `observation(raw_value="")` | P4 `MalformedObservation`; P5 accepts | Stub `validate_observation` rejects `""`. Production P5 builder does not. A span of empty text can leave the extractor and die at the store. |
| `NaN` in config | `canonical_json({"c": float("nan")})` | `'{"c":NaN}'`, which is not JSON | Python `json.loads` accepts it. A strict consumer, and `config_fingerprint` stability across languages, will not. Refuse non-finite floats at fingerprint time. |
| Hash prefix | `observation_key(content_hash=64hex)` vs `sha256:`+hex | Two different keys | Live P1 is 64 hex. P4/P5 fixtures still use `"sha256:abc"`. Tests pass. The walking skeleton must copy `get_file()["content_hash"]` unchanged. Mixing prefixes in one database splits one file into two evidence sets. |
| No batch writer | Inspected `store.py` | Three inserts, no `transaction()`, no `write(ExtractionResult)` | Crash after `record_run` leaves a run with zero observations. P1 already has `transaction(conn)`. The missing object is the sink P5’s Protocol describes. |
| Schema docstring | `evidence_shape/schema.py` | Still says OQ2 is **unsettled**, which is why there is no FK to `files` | OQ2 closed 2026-08-20 (hash owns the set). The missing FK is still reasonable (P4 must test without a `files` row). The comment is a landmine for the next reader. |
| `p4_stub.py` | Still imported by every P5 extractor test | It now re-exports `evidence_shape` | Better than the old reconstructed SPEC. It is still a second import path. `validate_run` requires `coverage` always; P4 allows `None`. Swap leftover is unfinished. |

---

## Not comprehensive enough yet (real corpus, not a missing gazetteer)

These are the holes a Downloads folder hits that 623 tests do not.

### Routing: images and media

`SOURCE_TYPE_BY_FORMAT` is only what §2.9 / §2.6 named, plus jpg. Executed: `gif`, `webp`, `tiff`, `bmp`, `avif`, `heif`, `mp3`, `mp4`, `mov`, `m4a`, `wav` all route as **`unsupported`**.

B6 said audio/video are **metadata-only** at launch, not “no extractor exists.” An `.mp3` is not an unknown format. It is a format the product chose not to transcribe. Today it is indistinguishable from `thing.qqq`.

Screenshots on this Mac are usually PNG (routed). iPhone photos are HEIC (routed). WhatsApp / browser saves are often WebP or GIF. Those files get a filesystem filename and nothing else — no dimensions, no EXIF, no OCR trigger via E5. OCR policy keys off an image/native result that never ran.

`.numbers` is in the table as spreadsheet. A real Numbers document is often a **package**. P3 Q7 (packages) is still open. Routing “numbers → text.structured” and then `admit()` refusing a package is a silent empty.

`.pages` / Keynote are unrouted. Common on a Mac corpus. Spec-faithful (not in §2.9’s list). Still a sorter hole: they become `unsupported`, not `unreadable` like PSD.

### Code and documents

§2.4 named Python, JavaScript, SQL, notebooks, JSON, YAML, TOML, XML, CSV. `swift`, `ts`, `go` are `unsupported`. That matches the list. It does not match “Code and Projects” as a top-level area of the product. A `.swift` homework file is indexed by filename only.

No encrypted-PDF fixture. No 0-byte file fixture. No file that changes between `stat` and open. No NFC vs NFD filename (macOS NFD). P3 already passes `normalized_filename=path.name` unchanged (Q1 open). P5 then emits that string as `direct` metadata named `normalized_filename`. P6 can treat it as actually normalized. It is not.

### Safety / incremental scan

Extractor upgrade does not appear in P3’s `VERDICT_REUSE` key (path + mtime + size). An orchestrator that skips `VERDICT_REUSE` files will never re-run `pdf.text 0.2.0` on an unchanged corpus. P5’s `cache_key` includes extractor version; P3’s verdict does not. Two caches, and the outer one wins. Named on the orchestrator page (OQ6). Still the way a shipped extractor bug stays in the database forever.

First-sight dataless still has no `files` row. `dataless_result()` still does not exist. Unchanged from [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md).

### What P4/P5 correctly refuse to be comprehensive about

Do not “complete” these inside these packages:

- Course codes, universities, `subject = BUSIB 4300` — P6 + catalogues.
- Screenshot vs photograph classification — P6, from E5’s `signal_tier` rows.
- `no_usable_facts` threshold — injected, no default (B7).
- Handling class / OQ4 — P7.
- Speech-to-text — out of v1.
- Inventing GIF/WebP tokens without a SPEC sentence — but **audio/video metadata-only is already a SPEC sentence (B6)** and the router does not implement it.

---

## What is actually solid (do not reopen)

- P4 vocabularies, locator escaping, RAW-1 on CJK/emoji fixtures, RAW-2 triggers, nine completeness values, five zero-observation states, rule 8 four-field replay key, `file_id` out of the compared set.
- P5 does not re-hash or re-stat. O5 re-emits P3’s row. Catalogues stay injected. Apple Vision is a provider string, not a hard-coded engine import. XLSX/PPTX are routed to `text.structured` (B6), not marked unsupported in the live router.
- Protected-container and dataless still raise at `admit()`. That gate is correct. The missing piece is the catcher for ordinary reader failure, not an override of §4b.
- Dual extractors on one image (E5 + E6) as two runs is the right shape. `TierConflict` is right **when two native outcomes disagree**. It is wrong when the second run is the unrouted stopper stuffed into the filesystem tier.

---

## What to do, in order

1. **Fingerprint.** P5 uses P4’s `config_fingerprint`. One executed test: `run_from_mapping(p5_run_dict | {run_id})` succeeds.
2. **Unrouted run identity.** Native tier, not a second `filesystem.record`. `extraction_status_by_tier([fs, unrouted])` returns two keys, no raise. Matches A4.
3. **One sink.** `EvidenceSink.write` in P4 (or a thin adapter) wraps `transaction()`, inserts run + units + observations, then `record_run_event`. P5 `append` dies.
4. **One collapse.** Every extractor, or the sink rejects an uncollapsed batch. Re-run the DOCX `Columbia` twice case.
5. **`failed` catcher.** One. Reader exceptions become a `failed` run, not a crashed scan.
6. **Pin OCR extractor_name** to one spelling and use it in P4 fixtures.
7. Then, and only then, orchestrator. Then walking skeleton with live hex hashes, not `sha256:abc`.

Optional product-scope (Joseph, not a silent P5 table): WebP/GIF/TIFF as images; audio/video tokens as `metadata_only` per B6; whether `.swift` is `code_structured` or stays unsupported.

---

## What I did not break, and why that is not comfort

I did not need a 10 GB PDF, a Unicode trick, or a gazetteer gap. The first real file the orchestrator stores hits break 1. The first `.dmg` hits break 2. The first locked PDF hits break 3.

623 tests passed because P5 never calls `run_from_mapping`, never calls `extraction_status_by_tier` on the two-run unrouted fixture, never raises from a reader, and never collapses DOCX. The suite is comprehensive about shape. It is not comprehensive about the join.
