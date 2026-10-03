# Non-UI release checklist

Use with `bash tools/run_release_gates.sh` from a clean checkout.

## Before release

- [ ] Wheel builds; profiles + entry point present (`tests/test_packaging_install.py`)
- [ ] Provider matrix green (`tests/assistant/test_provider_resolution.py`)
- [ ] Assistant + items gates green (`tools/run_assistant_gates.sh`)
- [ ] Freshness / identity lifecycle green (T2)
- [ ] Index refresh recovery green (T3)
- [ ] Search quality gate green (T4) — zero deleted/stale citations
- [ ] Policy boundary + injection pass^3 green (T5)
- [ ] Relationship approval/projections green (T6)
- [ ] Crash-safe apply/undo green (T7)
- [ ] Memory release stays dark unless version-bound gate passes (T8)
- [ ] `db check|backup|restore|rebuild-index` green (T9)
- [ ] Privacy-at-rest docs + fixture atomicity (T10)
- [ ] Live connectors scratched assert (T11) — **do not enable OAuth**
- [ ] Daily-use pilot report written with cloud/memory/apply off

## Pilot thresholds (supervised)

- Zero stale/deleted search hits
- Zero protected egress
- Zero unapproved writes
- Zero unresolved journal states
- 100% installed profile load (`student`, `files_only`, `job_seeker`)

## Incident defaults

See [everyday-product-runbook.md](./everyday-product-runbook.md).
