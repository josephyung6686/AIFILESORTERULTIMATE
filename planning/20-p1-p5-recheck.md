# P1–P5 recheck — stress + original design join

Date: 2026-08-21 (~02:00)
Status: **The Wave-2 path now runs as the original design cut it.** Not a finished sorter. `python3 -m pytest tests -q` → **1231 passed** (fresh this pass).
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) · cut: [`02-segmentation-map.md`](02-segmentation-map.md)
Supersedes the execute-headline of [`19-p4-p5-stress.md`](19-p4-p5-stress.md). File 19 stays as the break list that this pass closed.
Orchestrator-specific verification: [`21-orchestrator-verification.md`](21-orchestrator-verification.md).

---

## Verdict

P1–P5 plus the Wave-2 caller now do what the segmentation map asked of Wave 1–2: hash and store on P1, scan on P3, freeze the observation on P4, extract on P5, measure on P2, in **one path**.

They do **not** yet organize a corpus. P6–P13 are unbuilt. A real PDF library is still injected, not chosen. Three join leftovers remain (sensitivity signals, routing rows, `handling_class` column). None of those crash a scan.

---

## Fresh evidence (this pass)

| Check | Result |
|---|---|
| Full suite | **1231 passed** in 12.87s |
| Prior join-break 1 (fingerprint) | Closed. P5 `fingerprint` == P4 `config_fingerprint`; `run_from_mapping` accepts a P5 run |
| Prior join-break 2 (`TierConflict` on `.dmg` / `.psd`) | Closed. Stopped run is `format.unrouted` / `native`. Status map is `{filesystem: complete, native: metadata_only\|unreadable}` |
| Prior join-break 2 leftover | Closed this pass. Unreadable observations had kept `extractor_name=filesystem.record` on a `format.unrouted` run. Both now match. `RunWriter` stores them |
| Prior join-break 3 (`failed`) | Closed. Reader exception → `failed` run, scan continues (`tests/wave2`) |
| Prior join-break 4 (D10 on DOCX) | Closed. Two `Columbia` hits → one row, `occurrence_count=2` (collapse on `ExtractionResult`) |
| Prior join-break 5 (two event writers) | Closed. `extractors.events.append` deleted. `RunWriter.write` ends with one `record_run_event` |
| Empty `raw_value` | Closed. P5 builder calls P4 `check_non_empty` |
| OCR name spelling | Closed. `apple-vision` / `Apple Vision` → `ocr.apple_vision` |
| GIF/WebP/TIFF/MP3/MP4/MOV | Routed (B6). MP3 is `audio_video` → `text.structured`, not `unsupported` |
| Walking skeleton join | `run_wave2`: P3 scan → filesystem + `extract()` → P4 `RunWriter` → P1 `set_extraction_status` → P2 bundle. Uses `current_path`. Protected container → nothing. Dataless-with-`file_id` → `dataless` run. Extractor upgrade bypasses P3 REUSE |

---

## Does it match the original design?

Yes, for the slice P1–P5 were supposed to own.

| Design sentence | Live |
|---|---|
| §0 one local SQLite database; each part owns tables | P1 `files`/`events`, P2 eval tables, P3 scan tables, P4 three evidence tables, P5 routing + sensitivity. Same `conn` |
| §2.1 read once per content version | P5 copies P1’s 64-hex hash. Does not re-hash. Stat-cache REUSE skips extract unless extractor version changed |
| §2.8 one observation shape, no per-format consumers | P4 records; P5 builders; `RunWriter` validates the twelve rules before insert |
| M8 acting part authors; P1 writes | Events `subsystem` ∈ `{P3, P5}`. Orchestrator never appears |
| §8.2 extraction / OCR reserved | P4 `record_run_event` is the one writer. One event per `extraction_runs` row |
| §8.5 stage envelope | P5 maps completeness → P2 `produced`/`deferred`/`abstained`/`error`. Bundle `source_scan_ref` is the scan run |
| §8.6 unfinished work stays visible | `failed`, `dataless`, `metadata_only`, `unsupported` are distinct. Ceilings live on P1; P5 reads, does not invent |
| §1.2 P3 fills `files`; P5 does not recompute it | O5 re-emits the row as `source_type: filesystem` |
| 11 §4b / §5 | Protected container: no run. Dataless: run only if a `files` row already exists |
| Walking skeleton: P1 hash → P3 scan → P4/P5 one observation → P2 replay | `tests/wave2/test_wave2_orchestrator.py` plus the per-part skeleton steps |

What the original design also said, and this wave still does not do: facts, folders, LLM, privacy gate, grouping, placement, apply/undo, review. That is P6–P13, not a P5 hole.

---

## Still not the way we want it (named, not blockers for “does Wave 2 run”)

1. **Sensitivity signals are computed and dropped.** `extract()` returns `Dispatched.sensitivity`. The orchestrator keeps only `.results`. `record_sensitivity_signals` is never called from `run_wave2`. §2.9’s “addresses and message content as potentially sensitive” does not reach the database on a real scan. P7 will have nothing to redact against.

2. **Routing decisions are not recorded on the Wave-2 path.** P5’s `extraction_routing` table exists. `run_wave2` calls `route()` and never `record_routing_decision`. The wave2 test fixture also never calls `create_extraction_schema`. Every file still *has* a decision; the durable record of it is missing.

3. **`handling_class=file_row["sensitivity_state"]`.** P2’s column is P7’s, still open (C2). P1’s `sensitivity_state` is a different field. On a live scan it is NULL, so the bundle stores NULL and tests pass. It is still the wrong name. Until P7 exists the design answer is `None`, not a different P1 column.

4. **First-sight iCloud still has no `files` row.** Unchanged OQ3. Counted only in P3 `dataless_detections`. A later eviction of a hashed file does get a `dataless` run.

5. **`.pages` / `.swift` stay `unsupported`.** Spec-faithful (not in §2.9’s list). A Mac corpus will index them by filename only.

6. **No production readers.** PDF/DOCX/HEIC/OCR are still injected. The skeleton proves the seam, not Apple Vision or `pypdf`.

---

## What I changed this pass

`src/extractors/filesystem.py`: unreadable metadata rows now carry `format.unrouted`, same as their run (A4 leftover). `tests/p5/test_p5_filesystem.py` asserts both.

---

## What to do next

Wave 2 is allowed to stand. Caller leftovers and the new bundle-scope findings are in [`21-orchestrator-verification.md`](21-orchestrator-verification.md). Then P6.

Do not reopen fingerprint, D10-at-the-result, `failed` catcher, stopped-run identity, or the one-event writer.
