---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
# External Integrations

**Analysis Date:** 2026-08-29

## APIs & External Services

**LLM / model providers:**
- No vendor SDK is imported (guards in `tests/p6/test_p6_llm_seam.py` ban `http`, `openai`, `anthropic`, `urllib`, `socket`, `api_key` in facts LLM seam)
- Sole egress: `src/llm_harness/transport.py` (`IS_MODEL_TRANSPORT = True`) — `issue` consumes a P7 `Released`, reassembles model-visible bytes, then calls injected `ModelClient.invoke(bytes) -> bytes`
- Target identity: `privacy.release.ModelTarget` with `locality` ∈ `{local, cloud}`, plus `model_id` and `provider` (`src/privacy/release.py`)
- Cloud vs local is a privacy-policy decision (`offline` / `local_model` / `hybrid` / `cloud_assisted` in `src/privacy/vocabulary.py`), not a hard-coded vendor URL
- Auth: Not applicable to in-repo code — credentials would belong to a deployment-supplied client, never to package code

**OCR:**
- Apple Vision + Quartz (macOS) via PyObjC — `src/readers/ocr_vision.py`, wired by `src/readers/deployment.py` (`PROVIDER = "Apple Vision"`)
  - SDK/Client: `Vision`, `Quartz`, `Foundation.NSURL`
  - Auth: OS frameworks only; no API key

**PDF reading:**
- pdfminer.six — `src/readers/pdf_pdfminer.py` (`extract_pages`, `PDFParser` / `PDFDocument`)
  - Auth: Not applicable (local file I/O)

**Embeddings:**
- Computation is caller-injected (`Encoder` callable in `src/grouping/embeddings.py`); P1 only stores opaque bytes in SQLite (`vector_embeddings` / `vector_arrays` in `src/database_agent/db.py`)
- No embedding vendor client in-tree; CLI production path uses `EmbeddingsOff()` (`src/cli.py`)

**Filesystem / OS:**
- Local filesystem corpus via `scan_agent.corpus_source.FilesystemCorpusSource` and path observation in `src/database_agent/` / `src/scan_agent/`
- Session watch: `src/scan_agent/watch.py` exposes `notify` / `poll`; FSEvents / DispatchSource adapter is not built (stdlib-only P3)

## Data Storage

**Databases:**
- SQLite (stdlib `sqlite3`) — single local file database
  - Connection: path argument to `open_database` (`src/database_agent/db.py`); CLI default `./database-agent-plan.sqlite`; helper `default_database_path(bundle_id)` under Application Support
  - Client: raw `sqlite3.Connection` with `Row` factory, WAL, `synchronous=FULL`, foreign keys, recursive triggers, authorizer protecting append-only `events`
  - Schema owners: P1 substrate in `src/database_agent/db.py`; additional DDLs in package `schema.py` modules (`evidence_shape`, `extractors`, `facts`, `privacy`, `llm_harness`, `grouping`, `tree_design`, `placement`, `scan_agent`, `eval_harness`)

**File Storage:**
- Local filesystem only — corpus roots selected by the user; archives inspected without unpack-to-disk in `src/extractors/archive.py` (manifest reader injected)
- Packaged read-only assets: `src/tree_design/library/*.json`, `src/recognition/library/`

**Caching:**
- In-database caches only (e.g. extraction/fact cache keys, `scan_agent.stat_cache`) — no Redis/Memcached

## Authentication & Identity

**Auth Provider:**
- Custom local privacy/consent gate — not an identity SaaS
  - Implementation: `src/privacy/` (`gate.py`, `consent.py`, `policy.py`, `binding.py`, `release.py`, `defaults.py`)
  - File content reaches a model only after P7 issues `Released`; transport refuses unbound calls
  - Install floor: local-first modes only (`offline`, `local_model`); no env/build-flag default cloud mode

**User identity fields:**
- Optional `user_id` on events / CLI `--user` (defaults to `getpass.getuser()` in `src/cli.py`) — local attribution, not OAuth

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry/Datadog/OpenTelemetry clients)

**Logs:**
- Append-only SQLite `events` table (`src/database_agent/events.py`) with subsystem authorship helpers per package
- Model call audit: `model_call_issued` / `model_response_received` (`src/llm_harness/authorship.py`, `src/llm_harness/transport.py`, `src/llm_harness/store.py`)
- Privacy audit: model release / denial / consent events (`src/privacy/audit.py`, `src/privacy/authorship.py`)
- Scan resource usage counters in `scan_resource_usage` (`src/database_agent/scan_usage.py`); LLM cost column reserved for P8

## CI/CD & Deployment

**Hosting:**
- Not detected — local agent / CLI (`src/cli.py` entry); no cloud host config in-repo

**CI Pipeline:**
- None (no `.github/workflows` or other CI config detected)

**Packaging:**
- setuptools wheel/editable package `database-agent` 0.1.0
- Deployment readers extra: `pip install -e '.[readers]'`
- Composition entry: `src/production.py` (P1–P11) and `src/orchestrator.py` (P1–P7)

## Environment Configuration

**Required env vars:**
- None required by application code — configuration is CLI flags, injected callables, and SQLite-stored policy/budget rows

**Secrets location:**
- Not applicable in-repo — no `.env`, credential files, or secret directories tracked
- Model API secrets (if any) would live only in a deployment-supplied `ModelClient`, outside this package

**Notable non-secret config surfaces:**
- `VISION_CONFIG` in `src/readers/deployment.py`
- Budget ceilings via `database_agent.budget.set_ceiling` / `budget_ceilings` table
- Privacy policy rows (`src/privacy/policy.py`) and CLI `OPERATION_MODE`

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None as HTTP webhooks
- Outgoing model traffic only through injected `ModelClient.invoke` after privacy release (`src/llm_harness/transport.py`); privacy transport guard (`src/privacy/transport_guard.py`) asserts single egress surface

---

*Integration audit: 2026-08-29*
