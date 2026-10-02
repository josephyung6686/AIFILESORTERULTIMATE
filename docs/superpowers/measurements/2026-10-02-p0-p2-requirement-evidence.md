# P0–P2 + Addendum A — requirement evidence

**Gate command:** `bash tools/run_assistant_gates.sh`  
**Date:** 2026-10-02  

| Requirement | Evidence | Status |
|---|---|---|
| Injection fixtures | `tests/fixtures/injection/*`, `test_injection_fixtures.py`, `test_injection_files.py`, `test_addendum_a.py` | PASS |
| Eval harness in CI | `tools/run_assistant_gates.sh` (exit 0) | PASS |
| Hybrid find readiness | `src/items/hot_index.py` FTS+vec+RRF+CJK+chunks; scale tests | PASS |
| Recall beats FTS-only (CJK) | `test_find_scale_and_recall.py`: naive MATCH `"作業"` empty; `find_files` hits `作業講義.pdf` | PASS |
| Find p95 @ 2k / 50k / 250k | `measurements/2026-10-02-find-latency-2k-50k-250k.json` (0.6ms / 12ms / **62ms**) | PASS |
| Untrusted cards (A1) | `tools.py` `UNTRUSTED_LABEL`; `test_addendum_a.py` | PASS |
| Held withhold | `test_held_egress.py`, `test_tools_readonly.py` | PASS |
| Held never in egress body | `test_held_egress.py::test_egress_ledger_never_stores_held_body` | PASS |
| Egress ledger | `egress.py` + chat persist; `test_plans_journal.py` | PASS |
| Write-tool refuse | `WRITE_SHAPED` hard refuse; injection tests | PASS |
| pass^3 trajectories ≥0.7 | `test_trajectories.py` 3/3; gate pass^3 loop | PASS |
| 0 injection write calls | injection suite + pass^3 | PASS |
| CLI ask/search wired | `cli.py` + `ask_main` / `search_main` | PASS |
| Per-provider trust (A4) | `trust.py`, `--show-trust`, `test_provider_trust.py` | PASS |
| DiffEvent provenance (A6) | `memory_l0.py`, `test_memory_l0_provenance.py` | PASS |
| INJ-07..09 (A7) | `test_addendum_a.py` | PASS |
| Local-only option (P2) | `--local-only` refuses until FM wired | PASS |
| No silent moves | all tools/payloads `moved: false` unless gated apply env | PASS |
