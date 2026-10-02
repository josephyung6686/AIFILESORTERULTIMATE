# Demo run

A copy of Downloads, not the real Downloads folder. The plan database sits
outside that copy. Nothing here moves a file.

The order is: profile, provider, scan (rules, then understanding), the
outline, then an optional second pass over whatever understanding left open.

## 1. Profile

`filesorter onboard` asks the questions and stores them. `--answers FILE`
reads a JSON file that is already filled in. `confirmed` must be true, and
a field that still says TODO is refused. The database must sit outside the
folder.

```bash
filesorter onboard \
  --folder ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite
```

## 2. Provider

`filesorter providers` stores the lane. A DeepSeek key can also come from
`DEEPSEEK_API_KEY` and `DEEPSEEK_MODEL_FAST`. No provider means the scan
stops before it reads a file. Nothing is sent.

## 3. Scan, understanding, outline

The scan reads the copy, sorts with the rules, then asks the model about
files the rules did not place. `--structure-out` writes the proposed
folders. Finder copies, `_export` titles, and same-course peers are folded
before that file is written.

```bash
database-agent ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite \
  --answers ~/star-sorter-test/answers.json \
  --structure-out ~/star-sorter-test/proposed-structure.txt
```

A later scan of the same folder can omit `--answers`. The stored profile
is the one the model sees.

## 4. Understanding budget

The pass stops when the next call would pass either ceiling. The defaults
are 4000 calls and 4,000,000 estimated input tokens. The estimate is
`len(dossier_json) / 4`. Cache hits do not spend a call. A file past the
ceiling is needs-review with reason `budget stop` and is not cached.

Those defaults cover a Downloads copy of about 1800 files even when each
file is its own call. Raise them for a larger folder:

```bash
database-agent ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite \
  --understand-max-calls 8000 \
  --understand-max-input-tokens 8000000
```

A lower `--understand-max-calls` is how a short demo stops early on purpose.
The screen prints how many calls were used out of the ceiling.

## 5. Second pass

`--understand-residuals` does not scan again and does not rewrite the
outline. It spends calls only on files that are still unplaced and have no
settled answer: a budget stop, a rejected call, or a file the first pass
never reached. A file that already has a life area is not sent again. A
file the model already marked needs-review stays there and is not sent
again.

Use the same database as the scan. The stored profile is the one this pass
uses. The budget flags apply to this run on their own, so a first pass that
stopped at a low cap can be finished without raising that cap for the whole
corpus.

```bash
database-agent ~/star-sorter-test/dl \
  --database ~/star-sorter-test/dl-plan.sqlite \
  --understand-residuals \
  --understand-max-calls 4000
```

The line `Understanding residuals:` says how many files are still to ask,
how many are already settled, and how many still need review from an
earlier answer.
