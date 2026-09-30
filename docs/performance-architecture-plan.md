# Performance and architecture

Date: 2026-09-30. Status: measurement, plus stages 1 and 2 from the order below.

Branch: `app`. `main` is untouched. Nothing here is merged.

The product is a virtual library. Files stay at their real paths. The index records those paths. Gmail and Calendar are later items on the same graph. This note is about the sorter engine that scan still runs, and about the line between that engine and the app layer. It does not start Gmail, Calendar, or a view.

## What this run was

A plain scan of a synthetic corpus built on this machine.

- Host: Linux, 4 vCPU. No Apple Vision, no Cocoa document reader, no FSEvents, no Finder.
- Command: `database-agent` on the corpus with `--situation academic.coursework`, `--label Library`, `--user bench`, and a database outside the corpus. No `--semantic-model`. No cloud key. `GRAPH_AGENT_LOCAL_MODEL` and `OLLAMA_BASE_URL` unset. `GRAPH_AGENT_NO_DOTENV=1`.
- Corpus: 2,000 files, 9,925,605 bytes, four folders (`School`, `Money`, `Code`, `Loose`). Mix by `i % 100`: 600 one-page PDFs, 400 `.txt`, 240 `.md`, 240 `.docx`, 240 1×1 PNGs, 120 `.csv`, 80 `.json`, 40 `.html`, 40 `.zip`. Text is a short unique paragraph, repeated 2, 12, or 60 times. The database was deleted before the run, so this is a first scan.
- Result: exit 0, 2,000 files indexed, 0 unreadable, 0 model calls, 210 files held on device. Wall clock **120.51 s**, **16.60 files/s**. Building the corpus took 3.16 s and is not part of the 120.51 s.

cProfile covered the main thread only: 263,304,347 calls, 115.208 s internal time. Worker processes that read PDFs, docx, and zips do not appear in exclusive time. The main thread spent **42.71 s** inside `extraction_pool.close` / `_shutdown`, blocked until those workers finished. That wait sits inside `run_production_p1_p7` (45.26 s).

`hash_file` did not show up as its own phase. Hashing is inside `scan`, which took **0.83 s**.

## Where the time went

These numbers overlap. `Detector.explain` is part of the 120.51 s, and part of it sits inside the two production stages. They are not slices of a pie.

| What | Measured |
| --- | --- |
| Wall clock, `cli.main` | 120.51 s |
| `run_production_p1_p7` | 45.26 s, of which 42.71 s is joining the extraction pool |
| `downstream` | 38.17 s, of which `run_production_p8_p11` is 36.11 s |
| Rest of `run()`, outside those two | about 36.7 s, not split further |
| `Detector.explain` | 12,149 calls (6.07 per file), 22.84 s cumulative |
| `scan` (walk, stat, hash, rows) | 0.83 s |
| `sqlite3.Connection.execute` | 22.107 s exclusive, 662,829 calls |
| `detector._tokens` | 10.743 s exclusive, 564,476 calls |
| `detector._matches` | 2.909 s exclusive, 32.763 s cumulative, 20,989 calls |
| `detector._terms_in` | 1.999 s exclusive, 14.682 s cumulative, 1,063,052 calls |
| `observations_for_file` | 25,110 calls (12.6 per file), 1.019 s exclusive, 12.999 s cumulative |
| `observation_from_mapping` | 1.418 s exclusive, 12.372 s cumulative, 286,296 calls |

Main-thread exclusive time by area: recognition 19.62 s, evidence_shape 20.23 s, grouping 5.90 s, facts 1.30 s, placement 0.74 s (cumulative 51.80 s, because it calls into other code). `items` was 0.02 s. Readers on the main thread were 0.07 s, because the read happens in the pool.

The recogniser builds one term index in `Detector.__init__` from all **23** schemas in `facts.domains.SCHEMA_IDS`. It does not run 23 scorers. Every file's text is tokenised and matched against that combined vocabulary. Tokenising (`_tokens`) is the expensive part of a match. Scoring every schema is real work, and it is smaller than doing that work six times per file.

A 40-file smoke of an earlier mix took 5.69 s (7.0 files/s). 2,000 files took 21× longer, not 50×. The small run was dominated by pool startup. That ratio is not a claim that a real Downloads folder is linear.

## What this measurement could not reproduce

- The owner's Mac run: 1,833 files from a copy of Downloads, about 17 minutes, 1,821 files read. This run was 2,000 synthetic files, 9.9 MB, many one-page PDFs and a 1×1 PNG, 120.51 s.
- Apple Vision OCR. `readers/ocr_vision.py` returns without reading when the platform is not Darwin.
- pdfium / Cocoa document readers, FSEvents, Finder renames.
- `--semantic-model`. No weights were on this machine. The term detector ran alone.
- A split of the 42.71 s worker wait into pdfminer, docx, and zip. Those seconds are joined on the main thread and were not profiled inside the workers.
- Which statements make up the 662,829 executes. The total is measured. The text of each statement is not.

`planning/58-SCALE-STRESS.md` describes an older in-suite fixture (100 files) and problems that later commits fixed (unindexed `current_path` and `events`). Its timings are not this run.

## Targets, as proposals

The only wall-clock number this note treats as measured is **120.51 s** for the corpus above, on this Linux VM, first scan, fresh database.

Proposal: after the repeated main-thread reads in stages 1 and 2, rerun that same command and record the new wall clock in this file before anyone names a goal in seconds. The extraction join (42.71 s) and the p8–p11 pass (36.11 s) remain until a later stage measures them on their own. A goal such as "under two minutes on the owner's Mac" is not a proposal here. That machine was not measured.

Proposal for the suite: it stays at the path-index baseline of **19 failed, 11,277 passed, 44 skipped, 34 xfailed** (1,148 s). A new failure is a regression. Those 19 names were already the failure set before this pass.

## What to keep

- `observe_path`, content hashes, and the path index (`items`, `item_versions`, `project_after_scan`). A rename keeps one item id. An edit mints a new file id and keeps the item. A missing path stays a row with presence `missing`. Two live copies stay two items.
- The extraction pool, the safety holds (`finance`, `identity`, `medical`, `legal`), and the declared-life gate. An empty profile leaves the catalogue as it is. A declined winner is cited as `outside_declared_lives` and does not become the label.
- Frozen `Recognition` and `Abstention` values. Abstaining stays a result.
- The rule that this index does not call `mutation/execute.py`. The sorter's apply path still moves files when someone asks it to. The virtual library does not.

## What to rewrite

- `Detector.explain` runs about six times per file on a plain scan (classification, partition, gist, precaution, situation). The return value is frozen. Stage 1 remembers it until the inputs that can change it change.
- `observations_for_file` decodes every evidence row for the file about thirteen times per file. The rows are frozen. Stage 2 remembers the decoded tuple until a row is inserted or superseded, or an `observation_key` at either extreme of the file's keys changes.
- Later, and only after a statement histogram: the execute calls that remain once those two repeats are gone.
- Later, and only after a worker profile: whichever reader owns the pool wait. `EXTRACTION_WORKERS` is 7 and this machine has 4 CPUs. That mismatch was not measured, so it is not a change in this pass.

## What to drop, and what not to drop

`planning/` holds 21 Python modules (domain checks, deferred-catalogue checks, `parts/assemble.py`, `parts/build.py`) and the design notes. `src/` does not import that package. `src/tree_design/catalogue.py` says so. Deleting `planning/` would not shorten a scan. This pass leaves it in the tree. It is source for the catalogues, not a runtime cost.

The combined term index stays. Restricting it to declared lives would skip work, and it would also skip the citation of a winner the person did not declare. That citation is the gate's contract (`tests/recognition/test_declared_lives_gate.py`). A later stage can narrow the index only with that citation still true. It is not one of the two changes below.

Semantic recognition stays off unless a model directory is passed. This pass does not turn it on and does not delete it.

## Engine and app

**Engine.** Scan, read, extract, facts, recognition, grouping, tree design, placement, privacy holds, and the production orchestrator that runs them. Packages: `scan_agent`, `readers`, `extractors`, `extraction_pool`, `evidence_shape`, `facts`, `recognition`, `grouping`, `tree_design`, `placement`, `privacy`, `orchestrator`, `production`, and the database tables those packages own. The engine may propose a folder. It moves a file only through the existing apply path, after a freeze.

**App.** The path index in `items`: one item id, a real `open_target`, presence `live` or `missing`. Future Gmail and Calendar connectors, and any view that opens `open_target`. The app reads engine tables. It does not call `mutation/execute.py` to rearrange the disk. A click opens the path the index stored.

`cli.py` is the composition root both sides currently share. New app behavior enters through that root the way `create_items_schema` and `project_after_scan` already do. It does not grow a second copy of recognition inside the view.

## Order of changes

Each stage reruns the same 2,000-file first scan (fresh database, same flags) and the suite. The suite's job is to stay on the baseline failure set.

1. **Remember `Detector.explain`.** Keyed on the detector, the file version, the path, the extension, whether the path is a protected container, the live evidence stamp (count, max `rowid`, supersede count, min and max `observation_key`), the routing stamp, and the current declared, settled, and corroborating answers. A change to any of those misses. The cached value is the frozen return. Before: explain 22.84 s cumulative, 12,149 calls, inside 120.51 s. After: recorded below once this change reruns the corpus.
2. **Remember `observations_for_file`.** Same evidence stamp, per connection. A hit returns a new list of the same frozen observations, so a caller can append to the list it received. Before: 12.999 s cumulative, 25,110 calls. After: recorded below with stage 1.
3. **Count the execute statements** on a few hundred files, then change the statement that dominates. No code for this until that count exists.
4. **Time the workers by reader** on this corpus. Change a reader only if its share of the 42.71 s is the largest remaining cost, and only with the suite still on the baseline.
5. **Revisit the term index and declared lives** with the citation test still passing. Not before stages 1 and 2 have numbers.
6. **Leave `planning/` imported by nothing.** Not a performance stage.

Stages 1 and 2 are the ones this change implements. They are the largest main-thread costs that can be removed without changing a recognition rule, a reader, or a move.

## After stages 1 and 2

One rerun, after both stages, on the same corpus and the same command. A fresh database. Same machine. The two stages were not timed as separate wall clocks.

| | Before | After |
| --- | --- | --- |
| Wall clock | 120.51 s | 101.80 s |
| Files per second | 16.60 | 19.65 |
| Exit, indexed, unreadable, held | 0, 2000, 0, 210 | 0, 2000, 0, 210 |
| `Detector.explain` (phase timer) | 22.90 s, 12,149 calls | 9.05 s, 12,149 calls |
| `_tokens` exclusive | 10.743 s, 564,476 calls | 6.076 s, 309,162 calls |
| `_matches` | 20,989 calls, 32.763 s cumulative | 11,308 calls, 18.317 s cumulative |
| `evidence_shape` exclusive | 20.23 s | 14.08 s |
| `recognition` exclusive | 19.62 s | 11.12 s |
| `sqlite3.Connection.execute` | 22.107 s, 662,829 calls | 23.110 s, 701,451 calls |
| Pool join inside p1–p7 | 42.71 s | 40.05 s |
| `run_production_p8_p11` | 36.11 s | 38.26 s |
| Main-thread calls | 263,304,347 | 180,882,790 |

The explain phase is the stage 1 check: the same 12,149 calls, 13.85 s less. `_matches` was called about half as often. Stage 2 is the evidence_shape exclusive drop (20.23 s to 14.08 s). `observations_for_file` was in the before top exclusive list at 1.019 s / 12.999 s cumulative and 25,110 calls. It was not in the after top 35 exclusive functions.

The stamp queries are why `execute` went up by 38,622 calls and about one second. The wall clock still fell by 18.71 s.

The remembered values sit on the connection `open_database` returns. A base `sqlite3.Connection` cannot carry attributes, and a cache kept beside the connection would hold it open after `cli.main` dropped its reference. The 101.80 s figure is from the run before that move. The scan holds one connection for the whole run, so the hit path is the same.

The pool join and the p8–p11 pass moved by about two seconds in opposite directions on this single pair of runs. Those stages were not rewritten. Treat that pair as run-to-run movement, and the 18.71 s wall-clock drop as the measurement of stages 1 and 2.

Full suite on this change: **21 failed, 11,287 passed, 44 skipped, 34 xfailed** in 1,167 s. The baseline on the path-index commit was **19 failed, 11,277 passed, 44 skipped, 34 xfailed** in 1,148 s. Twelve new tests passed. The two additional failures are `test_the_sort_writes_groups_a_tree_and_a_plan` and `test_the_held_file_is_not_placed_and_the_released_one_is`. Those two failed in the earlier 11,267-passed run and passed in the 11,277-passed run. They also fail, with `placement_decisions` at 66 rather than 44, when run alone against the commit from before this change. The life-mate pair still fails, as it did in the 11,277 run, and passes alone. This run has both pairs failed at once.

## OCR, from the owner's Mac profile

The profile that follows is the owner's machine, a copy of Downloads at `~/star-sorter-test/dl`, 1,821 files, macOS, SQLite 3.50.4, `--scan-profile`. Wall clock 717 s, and the process then crashed in the targeted OCR pass (`_pool_result` was missing the file row). This Linux VM has no Vision, so none of the times below were reproduced here.

Extraction worker time, summed, was 1,155 s. Vision OCR was 1,031 s of that, over 600 files (p50 0.58 s, p95 5.8 s, max 33.8 s). pdfium's text layer was 100.6 s over 1,080 files. The parent blocked in `pool.result` for 282 s. Database execute was 19.3 s (475,000 executes, 4,394 commits, 416,000 of the executes in extraction). Recognition was 2.0 s, hashing 2.2 s, the walk 0.1 s. The slowest files were all OCR: an 11 MB PDF at 65 s, a 1.8 MB PNG at 63 s, then scanned PDFs at 12–29 s. OCR is about 89% of extraction work (1,031 / 1,155). The next cost is OCR.

SQLite on that report is 3.50.4. SQLite on this VM is 3.45.1. The WAL-reset fix is 3.51.3. Neither copy was upgraded.

### What the first scan does

`cli.FIRST_SCAN_OCR_PAGES` is 2. The ground-truth corpus measured 2026-09-06, pdfium, no OCR and no model, was 68 readable PDFs with a median of 2 pages. A cap of 2 reads that median document whole. The synthetic corpus in this note is one-page PDFs, so the cap does not shorten them. The Mac run already had the earlier 20-page OCR bound and a 120-second per-file bound, and Vision still took 1,031 s, because each file stayed inside those bounds. `OCR_PAGE_CEILING` stays 20 as that earlier bound. `PDF_PAGE_CEILING` stays 50; that measurement is the text-layer reader, and cutting it to 20 pages lost 3 classifications.

`OCR_SECONDS_PER_FILE` stays 120. The Mac Vision samples maxed at 33.8 s. There is no classification-versus-time measurement that would set a lower cap. The page cap is what bounds a long PDF. A single image cannot be interrupted mid-call; an overrun is recorded as capped.

OCR runs when the text layer, or an image's metadata, is under `OCR_SPARSE_PAGE_WORDS` (20). A page or a caption that already meets that floor is enough to classify. The engine is not called, and the file is still an OCR run: `completeness` is `capped`, `extractor_name` is `ocr.not_called`, and `config` carries `not_called` plus `pages_not_read`. A camera tag such as `Canon` stays under the floor and still goes to the engine.

`VISION_CONFIG["recognition_level"]` is `fast` for this classification pass. The engine still accepts `accurate`. Label agreement between the two levels is not measured on this machine.

`OCR_IMAGE_LONG_EDGE_PX` is 2,200. That is the long side of a US Letter page at the 200 DPI already in `VISION_CONFIG`, which is the size `_render_pdf_page` already produces. A loose image is not submitted larger than that page. The Mac report's 1.8 MB PNG does not include a pixel size, so this edge is not fitted to that file.

A successful OCR run, including a capped classification read, is reused by content hash. A second path with the same bytes does not call the engine. A run the scan budget marked `deferred` does not count, so the next scan retries it. Changing the page cap, the recognition level, or the long-edge setting changes the config fingerprint, so the next Mac scan reads each file once under the new settings and then caches.

### Deferred OCR, designed and not built

A first pass that classifies from cheap evidence and leaves OCR-dependent files as "pending OCR", with the screen up before Vision finishes, does not fit this pipeline cheaply. Classification and the screen both happen inside one `run_p1_p7`, and the CLI prints when that call returns. A background tier would need a process that keeps running after the CLI returns, a status the review screen already understands, and a second classification once the text exists. `deferred` already records a budget stop and is excluded from "already extracted", so the next scan retries that file. A later full-OCR pass reads `pages_not_read` on the capped runs. That pass is not this change.

Anything that can reach a cloud model is unchanged.
