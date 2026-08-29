---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
# Technology Stack

**Analysis Date:** 2026-08-29

## Languages

**Primary:**
- Python 3.12 (pinned `requires-python = "==3.12.*"` in `pyproject.toml`) — all application and test code under `src/` and `tests/`

**Secondary:**
- JSON — packaged template library under `src/tree_design/library/` (`fragments.json`, `definitions.json`, `applicabilities.json`, wave2 library files) and recognition rule manifests under `src/recognition/library/`
- Markdown — product design and phase contracts under `planning/` (not runtime)

## Runtime

**Environment:**
- CPython 3.12 (project lock: `==3.12.*`; local `.venv` resolves via uv-managed `cpython-3.12`)
- macOS is the intended deployment OS for the wired OCR path (Apple Vision via PyObjC); core pipeline is stdlib SQLite and filesystem I/O

**Package Manager:**
- pip / setuptools editable install (`pip install -e '.[dev]'`, `pip install -e '.[readers]'`)
- Lockfile: Not detected (no `uv.lock`, `poetry.lock`, or `requirements*.txt` in repo)
- Build backend: `setuptools>=68` / `setuptools.build_meta` (`pyproject.toml`)

## Frameworks

**Core:**
- None — application is a library + CLI composed from stdlib packages; no web framework, no ORM, no async server

**Testing:**
- `pytest>=8` (optional extra `dev`) — configured in `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `pythonpath = ["src"]`
- `pytest-randomly>=3.15` (optional extra `dev`) — order independence; run with `python3 -m pytest tests/ -p randomly --randomly-dont-reset-seed`

**Build/Dev:**
- setuptools package discovery: `[tool.setuptools.packages.find] where = ["src"]`
- No TypeScript/Node toolchain; no Docker build in-repo

## Key Dependencies

**Critical (runtime core — declared empty on purpose):**
- `dependencies = []` in `pyproject.toml` — P5 contract: extractors add no third-party runtime dependency; format libraries are deployment-injected callables only

**Critical (deployment optional — `readers` extra):**
- `pdfminer.six>=20231228` — PDF text/layout reader in `src/readers/pdf_pdfminer.py`
- `pyobjc-framework-Vision>=10.0` (darwin only) — Apple Vision OCR in `src/readers/ocr_vision.py`
- `pyobjc-framework-Quartz>=10.0` (darwin only) — PDF/page rasterisation for OCR in `src/readers/ocr_vision.py`

**Infrastructure:**
- Python stdlib `sqlite3` — sole durable store (`src/database_agent/db.py`)
- Python stdlib `hashlib` (SHA-256) — content hashes, prompt fingerprints, library release ids
- Python stdlib `mimetypes` — CLI MIME guess in `src/cli.py`
- Python stdlib `zipfile` / archive inspection — only via injected readers; `src/extractors/archive.py` opens no archive itself
- Injected `ModelClient.invoke: Callable[[bytes], bytes]` — sole model egress shape in `src/llm_harness/transport.py` (no vendor SDK in-tree)

**Dev-only (installed in `.venv` at map time):**
- `pytest`, `pluggy`, `iniconfig`, `packaging`, `Pygments` — test runner stack

## Configuration

**Environment:**
- No `.env` / `.env.*` files in the repo
- `src/privacy/defaults.py` reads no environment variable, file, or build flag for install mode
- Deployment decisions live in `src/cli.py` (ceilings, offline operation mode, database path flags) and `src/readers/deployment.py` (`VISION_CONFIG`: languages, dpi, recognition_level)

**Key configs required at run:**
- Database path: CLI `--database` or default `./database-agent-plan.sqlite`; production path helper `default_database_path(bundle_id)` → `~/Library/Application Support/<bundle_id>/agent.sqlite` in `src/database_agent/db.py`
- Privacy `install_mode`: must be `offline` or `local_model` (`src/privacy/defaults.py`); CLI sets `OPERATION_MODE = "offline"`
- Situation / label CLI flags (`--situation`, `--label`) — user authorities, not env vars
- Injected authorities for production composition (`src/production.py`, `src/orchestrator.py`): readers, resolvers, catalogues, budgets, clocks

**Build:**
- `pyproject.toml` — project metadata, optional extras, pytest config, setuptools layout
- `.gitignore` — ignores `.venv/`, `*.sqlite`, `*.npy`, `graphify-out/`, egg-info

## Platform Requirements

**Development:**
- Python 3.12.x
- Editable install of `database-agent` with at least `[dev]` for tests
- Optional `[readers]` for real PDF/OCR adapters on macOS

**Production:**
- Local macOS-oriented desktop/agent deployment (Application Support SQLite path helper)
- Filesystem remains system of record; SQLite is working memory only
- Model providers are not bundled — caller injects a `ModelClient` behind P7 `Released` + P8 transport
- OCR provider when wired: Apple Vision (macOS); DOCX/image/long-tail readers currently return `unsupported` in `macos_readers` (`src/readers/deployment.py`)

---

*Stack analysis: 2026-08-29*
