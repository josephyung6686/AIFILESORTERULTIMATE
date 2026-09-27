# Investor product overview

## What it is

This is a local-first tool for a person's own files. The filesystem is the system of record. Files stay ordinary files in ordinary folders that Finder, Spotlight, backups, and other programs can open. The product does not own the namespace or keep files in a private format.

A local SQLite database is the working memory: file identity, extracted content, facts, groups, the approved structure, movement plans, corrections, and undo history. If that database is lost, the tool can be rebuilt from the filesystem.

A cloud language model is used only where a ratified prompt and a privacy gate allow it. Reading, evidence, and rules stay local. The model may not invent a destination the person has not approved.

Launch domains are academic coursework, college applications, research, career, photos, and code. Finance, identity, medical, and legal material are safety holds: detected and protected before any cloud call or automated placement, and not used as filing domains at launch.

## Why the usual file-sorter fails

A usual sorter reads a filename or a short preview and picks one category. Real files break that. Names are vague. Homework can be a photograph of a page. A screenshot can be a receipt, a portal, a conversation, or a figure. One file can be a syllabus, part of a course, part of an application, and sensitive at once. One category drops the rest.

Sorting by likeness fails too. An application packet holds pieces that do not look alike, and a person keeps them together because they share a purpose. A shared string such as a university name does the opposite: it merges the school someone attends, the school they apply to, and a school named once in a citation.

## How a run works

A run is a fixed loop: pick, extract once, record facts, group, propose a structure the person edits, freeze, classify, residual, then apply.

The person picks the folders to analyze and the places that may later be roots. Roots are context for the proposal, not permission to move files.

Each file is read once per content version. Unchanged size and modification time reuse that extraction. The record keeps path, type, text or OCR where the format allows, and where each observation appeared. Extraction does not choose a folder.

Facts are claims tied to evidence. A model fact must cite stored evidence, use an allowed field, and clear stronger rules. Thin support stays unknown.

Groups are suggestions built from those facts and a few related files.

The person edits the proposal as a text outline, `proposed-structure.txt`, read back with `--structure`. There is no canvas yet. Freeze locks the legal destinations. Classification may then choose one approved folder, a shallower parent, or nowhere. An unplaced file is a correct result when the match is weak.

Nothing moves until the person freezes and then applies.

## What is built

What works is the proposal. A folder the person already made keeps its name. When two or more files in that folder have already recorded a kind of work, that kind becomes a child. The kind comes from the catalogue, a closed vocabulary such as work type, media type, or artifact type, not from a hardcoded list of courses or paths. A second folder spelled the way a document spells a course is left out when those files already sit in the person's folder. Files are not moved.

## What the measurement says

Sorting does not work yet. On the owner's pinned folder, the latest placement run scored 8 of 41 known coursework files in the exact folder. Two went to a wrong folder, two to the right parent with the wrong leaf, and twenty-nine were not placed. All 29 files that should have been left for the person were left unplaced. Nothing was moved. The run took under two minutes.

Only 8 of those 41 were placed on a path that matches the labelled course and the labelled kind of work. Ten labels have such a path on the proposal. The other files need a leaf the file does not name, or a folder name spelled differently from the one the person already made. The product does not invent that leaf and does not rename one spelling into the other.

The release bar is 30 of 41 exact, 0 wrong, and all 29 left unplaced. The 29 were left unplaced. Exact is 8 and wrong is 2.

The first reading of this folder took about half a minute. The whole job stays under ten minutes.

## What has to happen before this is a product someone pays for

A paid product has to move a file only into the right folder and leave the rest alone. This run names a wrong folder for two files. It moves nothing.

Before a paid release, the pinned folder has to reach 30 of 41 exact and none wrong, with a full run including the first reading under ten minutes. That needs course facts that match the words in the files, and a classifier that stops at the right depth. The text outline has to be enough to review and freeze, or the canvas has to exist. Undo has to remain available after apply.

Until that bar is met, this is a local tool that can propose a structure. It is not ready to move someone's files.
