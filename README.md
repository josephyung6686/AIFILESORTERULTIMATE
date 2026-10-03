# File Companion

File Companion reads the folders a person chooses and indexes them into one SQLite database. The files stay on disk at their original paths. She opens each file normally, from Finder, at that path.

Inside the app, the index is sorted into the categories she confirms. She can refuse a category. Anything that does not fit stays unplaced. Sensitive finance, identity, medical, and legal material is held and is not sent to a model.

There is no Gmail, calendar, inbox, or connections step.

The folder tree she reviews is the app's sort. It is not a rewrite of her computer. Moving or renaming the real files on disk is a paid action. It does not happen in the free product. Onboarding and a normal scan do not move or rename files. That paid path stays off unless it is explicitly on.

Product description → [`docs/product-one-pager.md`](docs/product-one-pager.md).

Python 3.12. The scan command is `database-agent` (also installed as `filesorter`). It runs on macOS and Linux. On Linux, Apple Vision OCR, `.doc` via AppKit, and ImageIO metadata are absent; text, PDF, and `.docx` still read.

## One database

One SQLite file is the working memory. There is not a second database.

The sorter owns the scan. It records files, exclusion verdicts, and classifications (sensitive, held, or ordinary), then groups and the in-app folder tree. A placement in that database is where the app sorts a file. It does not move the file.

The assistant searches and answers from those same files. Relationships are links she can approve, such as a duplicate or a note that one file belongs with another.

Graphify is a separate developer tool for searching this codebase. It is not part of File Companion.

## Open the window

On a Mac, this opens File Companion in its own window. It is not a browser page.

```bash
PYTHONPATH=src python3 -m companion
```

The same window is `apps/File Companion.app`. Double-click that on a Mac, or run the command above from the repository. Do not open `index.html`.

The six onboarding screens are that window: folder access, profile, work areas, categories, scan, and briefing. Nothing is preselected. Saving writes the answers file the scan already reads, and the write is atomic. A scan does not start when those answers are unfinished or folder access was not granted. After that, the workspace shows the in-app sort from the one database, files that need review, and empty folders. A folder is empty only when it has zero files on disk. It is listed, and it is removed only when she says yes.

Wired to the engine: the answers file, the refusal to scan, and one plan scan (`--accept-groups`) into `plan.sqlite`. That scan does not move or rename files. The workspace reads the outline and review rows that scan stored. Still preview: the macOS permission dialog is the in-app Allow step, and briefing counts stay empty when a scan does not finish. Moving or renaming files on disk is not wired. The paid path stays off.

## Quickstart

```bash
python3.12 -m pip install -e ".[dev,readers]"
database-agent /path/to/folder --user you --database ./plan.sqlite
```

That command reads the folder and writes `plan.sqlite`. It does not move or rename anything in the folder.

A scan uses a model provider for files the rules do not place. Set the profile with `filesorter onboard`, then `filesorter providers`, then run `database-agent FOLDER --database ./plan.sqlite`. When onboarding has written an answers file, pass it with `--answers FILE`. The scan runs understanding after the rules. Protected files stay on this computer and are not sent to a model. A folder with no provider stops and says to set one up. `--model-dry-run` prints what would be sent and does not open a network connection. Developers skip the understanding pass with `--no-understand` or `FILESORTER_SKIP_UNDERSTANDING=1`.

`--accept-groups` writes `proposed-structure.txt` next to the database. That file is the in-app outline. It does not change the folder on disk. `--stop-after tree` stops once that outline exists.

Score a labelled folder the same way, without changing the files:

```bash
python3 -m tools.groundtruth --corpus DIR --labels labels.json --out ./score --force
```

Tests:

```bash
python3 -m pytest tests/
```

`jsonschema` is in the `dev` extra because several tests validate model-response schemas.

## What a scan does

```text
1. CHOOSE      the folders she named; exclusions are recorded first
2. INDEX       one pass per file version, into the one SQLite database
3. CLASSIFY    sensitive, held, or ordinary; held material is not sent to a model
4. GROUP       files that belong together, from evidence in that database
5. SORT        an in-app folder tree, using only categories she confirmed
6. REVIEW      unplaced files and held files stay in the index, on their original paths
```

She reviews that sort in the app. Finder still shows the original paths.

## Standing constraints

- One SQLite database for the sorter and the assistant
- Files stay at their original paths during onboarding and a normal scan
- Only confirmed categories are used; a refused category is not
- A file that fits none of them stays unplaced
- Finance, identity, medical, and legal material is held and is not sent to a model
- Evidence is extracted once per content version and reused
- The model may only propose fields in the active schema, and must cite evidence or return `unknown`
- Correct abstention is a successful outcome
- Graphify is not part of the product
