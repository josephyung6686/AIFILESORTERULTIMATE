# File Companion

**Date:** Oct 3, 2026. This is the product description.

File Companion reads the folders a person chooses and indexes them into one SQLite database. The files stay on disk at their original paths. She opens each file normally, from Finder, at that path.

Inside the app, the index is sorted into the categories she confirms. She can refuse a category. Anything that does not fit stays unplaced. Sensitive finance, identity, medical, and legal material is held and is not sent to a model.

There is no Gmail step, no calendar step, no inbox, and no connections step.

The folder tree she reviews is the app's sort. It is not a rewrite of her computer. Moving or renaming the real files on disk is a paid action. It does not happen in the free product. Onboarding does not move or rename files. A normal scan does not move or rename files. That paid path stays off unless it is explicitly on.

## One database

There is one SQLite database.

The sorter owns the scan, the classifications, the groups, and the in-app folder tree. A scan records each file (its id, path, and hash), exclusion verdicts for folders that are not indexed, and a classification of sensitive, held, or ordinary. Groups and the folder tree are rows in that same database. A placement says where the app sorts a file. It does not change the file's path.

The assistant searches and answers from those same files. It does not keep a second database.

Relationships are links in that database. A link can say that two files are duplicates, or that one file belongs with another. She can approve a proposed link.

Graphify is a separate developer tool for searching this codebase. It is not part of File Companion, and the app does not build it in.

## Categories

Onboarding asks her to confirm or refuse categories. Only a confirmed category is used. A refused category is left out. A file that matches nothing stays unplaced. The app does not guess a place for it.

Finance, identity, medical, and legal material is held. Held material is not sent to a model.

## What stays on disk

The original path remains the path. Finder opens the file there. The free product does not move it and does not rename it.

A local change, meaning an actual move or rename on disk, is a paid action. It runs only when that paid path is explicitly on. The free product leaves it off.

## What this repository stores

Checked against the code, Oct 3, 2026:

- `open_database` is the one SQLite file. Items and relationships are tables in that file, not a second database.
- The sorter's tables in that file include `files`, `exclusion_verdicts`, `classifications`, `groups`, `group_edges`, `tree_nodes`, and `placement_decisions`.
- `relationships` is the link table. A proposed link is not an approved link.
- A normal `database-agent` scan reads a folder and writes that database. It does not move or rename the files.
- Graphify is not a product module. `graphify-out/` is a developer artifact and is gitignored.
