# 93 — Protected filenames: summarised by default, `--show-protected` expands

Date: **2026-09-02**. Status: **RULED BY THE OWNER. Implemented.**
Supersedes the disclosure half of the decision recorded at
`tests/test_cli.py::test_a_protected_group_is_never_the_one_summarised_away`
(now `..._is_counted_and_reachable_rather_than_listed`).

**Read this before changing `PROTECTED_SUMMARY` in `src/cli.py`.** The code there
deliberately contradicts one half of `00`, and without this note the next person
to notice will "fix" it back.

---

## 1. What was decided

**Protected filenames are summarised by default. `--show-protected` prints every
one of them.** The count and the command are on the screen every time.

## 2. What it was decided over

The owner had already ruled on this once, and ruled the other way: protected
groups are **listed in full, and sorted last**. That decision is not being
overturned as a mistake — it was right for the evidence in front of him. The
evidence changed.

Two of his own rules point in opposite directions here, and both are load-bearing:

- **The standing rule** (`84` §1): protected material is *marked and counted,
  never opened, never silently omitted*.
- **`00`:201**: *"a summary such as '11 protected identity records' may be safe to
  show, while a visible list of passport filenames on a shared screen may not
  be."*

While the longest such list anyone had seen was **four names in a demo folder**,
the two rules did not conflict in practice, and completeness won.

## 3. The numbers he was shown

Measured on a generated corpus with the realistic mess of a person's disk —
coursework, payslips, a lease, medical notes, a passport, memes, screenshots,
game saves, junk downloads, one `.app` bundle.

| files | protected group | share of the report |
|---|---|---|
| 1,000 | 173 lines of a 250-line file section: 144 filenames + 19 set names | **69 % of the file section** |
| 5,000 | 810 lines of 1,113: 710 filenames + 89 set names | **73 % of the whole report** |

The two ordinary groups at 5,000 files were 37 and 38 lines. After the earlier
collapse (`d99f501`) the protected list was **the only part of the report still
growing linearly with the person's disk**.

So what a person's screen mostly showed, on a real corpus, was their own
payslips, bank statements, medical notes and passport scans **by name**.

## 4. What "never silently omitted" means now

The word carrying the weight is **silently**. The default view keeps both halves,
and dropping either is what would break the rule rather than reinterpret it:

1. **The count, always.** `"144 protected files, marked and counted, and none of
   them opened."` A person never has to ask whether something was set aside.
2. **The command, always.** `--show-protected`, printed right there. A summary a
   person cannot get out of is concealment; a summary with the way out beside it
   is the person choosing when the names are safe to show.

And the expansion is **complete** — every one, never the first N. A truncated
expansion would be the omission the rule forbids, wearing the fix's clothes.

## 5. What did NOT change

- The **protected containers** block (`Numbers.app` and friends) is a different
  thing, is still first, and is still whole. It was never part of this question.
- Protected groups still sort **last** (`00`:201's other half).
- Protected **review sets** are still named and counted in both views — a set
  label is a summary already and leaks nothing about the files.
- `--send-set` is still offered on **no** protected set: P11 refuses it before
  reading any decision, so printing it would be an instruction that always fails.
- Nothing about a protected file is read, indexed, classified or moved in either
  view. `--show-protected` changes what is on the screen and nothing else.

## 6. How it is held

| guard | what it holds |
|---|---|
| `test_a_protected_group_is_counted_and_reachable_rather_than_listed` | names absent by default; count and command present |
| `test_show_protected_lists_every_one` | the expansion is all forty, not the first ten |
| `test_the_show_protected_command_the_report_prints_actually_shows_them` | the command is taken from the report verbatim, tokenised as a shell would, and passed back in |
| `test_the_flag_is_named_only_on_the_line_that_is_the_command` | the flag is never mentioned in prose, where a person would copy something unpasteable |
| `test_the_protected_list_no_longer_decides_how_long_the_report_is` | ten times the protected material does not lengthen the report |
| `test_a_protected_files_own_words_are_never_printed_back_to_the_person` | in BOTH views, a protected file's contents never appear |

Five sabotages were run against the implementation and each turned at least one
of these red: dropping the command, dropping the count, truncating the expansion
to ten, making the flag a general verbosity switch, and naming the flag in prose.

## 7. Measured effect

Both columns against the same `src/cli.py`.

| files | before | after |
|---|---|---|
| 10 | 141 | 144 |
| 100 | 317 | 310 |
| 1,000 | 479 | **342** |

**At ten files the report is three lines longer, and that is expected.** With one
protected file, a two-line summary plus a command costs more than printing one
name. It was not special-cased: a second rule for small corpora would be a second
thing to keep true, and a person with exactly one passport is not obviously the
person who wants it on screen.

## 8. Provenance

Ruled by the owner on 2026-09-02, relayed through the team lead, who recorded the
gesture `--show-protected` as carrying his sign-off under `84` §1 (a new mechanism
needs manual owner approval). The measurement that prompted the question was made
by the report agent and is in
`scratchpad/report/` — `HANDOFF.md` and `CLI-PATCH.txt`.
