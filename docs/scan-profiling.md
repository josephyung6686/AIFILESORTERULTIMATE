# Scan profiling

A plain scan does not time itself. Pass `--scan-profile` and the run writes two
files beside the plan database:

- `plan.scan-profile.json`
- `plan.scan-profile.csv`

The names follow the database file. A database at
`~/star-sorter-test/plan.sqlite` produces
`~/star-sorter-test/plan.scan-profile.json` and
`~/star-sorter-test/plan.scan-profile.csv`.

Those files name the slow files by path. They stay on the machine that ran the
scan. Do not commit them.

## What the owner runs

This reads a **copy** of Downloads at `~/star-sorter-test/dl`. It does not read
`~/Downloads`. It does not pass `--apply`, so it does not move or rename
anything. The plan database sits **next to** `dl`, not inside it.

```bash
database-agent ~/star-sorter-test/dl \
  --situation academic.coursework \
  --label Library \
  --database ~/star-sorter-test/plan.sqlite \
  --scan-profile
```

`--situation` is included so the run can finish without stopping to ask which
life the folder is. Another situation from `database-agent --list-situations`
can be substituted. `--label` is the name of the top folder in the proposal.

When the scan function returns, the terminal prints `Scan profile:` and the
path of the JSON file. Send that JSON (and the CSV if you want). The numbers
in it are from the machine that ran the command.

## What the report contains

- Wall time and share of that wall for walk/stat, hashing, extraction (main
  thread blocked on the pool, worker time summed, and the pool join),
  recognition, the p8–p11 pass, and database calls.
- Per extension and per reader: file count, total seconds, and p50 / p95 / max
  of each file's own time (hash + extraction work + recognition). Percentiles
  are nearest-rank.
- The 25 slowest files, with extension, size, and path.
- Time the main thread spent blocked in the extraction pool, time workers
  spent reading, and the part of the wait that was longer than that file's own
  read.
- SQLite statement counts and commits per phase. Statements are grouped by
  the head of the SQL (the text before `WHERE` / `VALUES` / `SET`), not by a
  Python stack, because a stack walk on every statement would dominate the
  measurement.
- Which PDF reader the production path wired (`read_pdf` from
  `extraction_context`), and which reader each extracted file actually called.
  PDF text-layer time and OCR time are split when both ran. On Linux, OCR and
  Cocoa are not wired; a Mac report is what shows those.

The SQLite version is in the report. If it is below 3.51.3, the report says
so. That release fixes a WAL-reset bug. This command does not upgrade SQLite.

If the scan raises after the profile is armed, the report is still written.
`partial` is true on that report. A scan that returns has `partial` false.

## Off by default

Without `--scan-profile` the scan does not install a statement counter, does
not keep per-file times, and does not write a report.
