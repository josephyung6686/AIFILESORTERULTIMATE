# 101 — Why nothing is placed, traced end to end

**For the owner. Every number below was measured on your own 199 files.** This
document exists because three separate explanations for "0% exact placement" were
offered before this one, and all three were wrong. The chain is now traced from the
regex that starts it to the abstention that ends it, and each link is a query you can
re-run.

Nothing here is a fix. It is the diagnosis the fixes have to satisfy.

## The short version

A regular expression matches ZIP codes and calls them course codes. Those wrong values
become *conflicting evidence*. Conflicting evidence **deletes the correct destination
folder from consideration** — 56 times for one folder. With the right answer deleted,
the remaining candidates tie, and §6.10 correctly abstains.

**Placement is not broken. It is being handed poison and behaving correctly.**

## The chain, link by link

| # | Link | Measured |
|---|---|---|
| 1 | `subject` is filled from a SHAPE with no vocabulary — letters then digits | 110 values across 199 files, the most-produced fact in the product |
| 2 | The shape matches things that are not courses | `NY11794`, `MD20852`, `MA01003`, `IN46256`, `NY10172` are ZIP codes. `VHX7000` is a microscope, `UARF470911` a booking reference, `U238` an isotope |
| 3 | A file's `subject` becomes evidence that rules out folders expecting a different `subject` | 258 node suppressions across the corpus |
| 4 | So the wrong values delete the **right** folder | proposed `E1006` suppressed **56** times; `Spring2023` 16; `Fall2024` 16. ZIP codes alone cause 52 suppressions |
| 5 | What survives is the person's existing folders, which tie | every abstaining file scores `0.2857` against **seven** candidates, all `0.2857` |
| 6 | §6.10 needs support ≥ 0.50 **and** margin ≥ 0.20. Margin is 0.00 | `"verdict": "weak"`, `"abstention_reason": "low_margin"` |
| 7 | The file is not placed | 85.4% not placed, **0.0% exact** |

Link 3 is the one worth staring at. **Suppression is correct behaviour.** A file that
is genuinely `E1006` *should* rule out a folder expecting `PHYS1401`. `E1006` itself
suppresses 10 nodes and is right to. The defect is not the mechanism; it is that the
values fed into it are mostly not course codes.

Re-run link 4 yourself against any run database:

```python
import sqlite3, json, collections
c = sqlite3.connect("file:RUN.sqlite?mode=ro", uri=True); c.row_factory = sqlite3.Row
nodes = {r["node_id"]: dict(r) for r in c.execute("select * from tree_nodes")}
total, proposed = 0, collections.Counter()
for (p,) in c.execute("select payload from placement_decisions"):
    for cf in json.loads(p).get("conflicts_considered") or []:
        total += cf.get("suppressed_node_count", 0)
        for nid in cf.get("suppressed_node_ids") or []:
            n = nodes.get(nid)
            if n and n["node_type"] == "proposed":
                proposed[n["display_label"]] += 1
print(total, proposed.most_common())
```

## Three explanations that were wrong, and why they are recorded

Recorded so nobody spends another night on them.

**"The tree hardcodes four levels."** It does not. The scorecard's `built` column is
`max(depth) - 1` over *every* node including the mirrored copies of your existing
folders, so it reads 4 for every situation regardless. A measurement artefact, not a
product behaviour.

**"The model was never wired up."** It is wired and it works. With `--enable-cloud`:
78 dossiers, 78 responses, 631 verdicts, **zero call failures, zero refusals**. It
moved exact placement from 0.0% to 0.0%, because the model is asked for fields that
cannot become folders — `file_type` (59 values), `authored_by` (34), `creation_date`
(19) — while `work_type`, a REQUIRED level, was filled **once in 199 files**. The
library itself forbids two of those from ever becoming a level: *"instructor,
authored_by and programming_language may never become a level."*

**"`active_schema_for` is hardcoded to three fields, and that is the bug."** Half
right, and the half matters. It *is* hardcoded to `subject`, `term`, `media_type`, and
a field outside that tuple is one P9 will not group on — so it is **necessary**. It is
not **sufficient**: adding `school` and `work_type` to it did create new folder
expectations (`school = "Georgetown Preparatory School"` appeared), and exact placement
stayed at 0.0%, because the values arriving were themselves wrong —
`work_type = "CONSTITUTION OF THE [ Georgetown Preparatory School Red Cross Club]"` is
a document's title, not a kind of work.

## The measurement error that hid all of this

**Every accuracy number produced before this document was measured with the model
switched off.** `tools/groundtruth/_one_run.py:32` sets `GRAPH_AGENT_NO_DOTENV=1`
unless the word `cloud` is passed, which makes the key unreadable *by design* — the
runs are meant to cost nothing unless somebody types `--enable-cloud`. That is correct
behaviour and it is stated at the top of every report. It was simply never noticed:

> No model was consulted: DEEPSEEK_API_KEY is not set, so this run used only what it
> could read and decide on this device.

Any future claim about accuracy has to say which of the two it is measuring.

## The scale nobody had measured: 2 of 169

The chain above is one situation. The library ships **208 situations**; 169 template
rows carry at least one REQUIRED level. Of those:

**2 rows (1.2%) have every required field producible today. 167 (98.8%) do not.**

| blocking field | template rows it blocks | producer |
|---|---|---|
| `project` | 67 | none |
| `record_type` | 45 | none |
| `work_type` | 30 | none |
| `institution` | 13 | none |
| `event` | 13 | none |
| `site` | 12 | none |
| `subject` | 7 | exists, and is the subject of this document |

The whole product has **one** `DirectSlot` (`subject`) plus `term` from `_rule_stage`.
Three producers — `project`, `record_type`, `work_type` — would unblock 142 of the 167.

**This is why "95% accurate" cannot mean one number.** 95% on `academic.coursework`
would leave 165 of 169 template rows with no producer at all.

## What this does not excuse

Two ceilings stand regardless of the chain above, and both are already owner
questions:

* **16 of 128 scorable files are set aside before being read** — the software-project
  rule, which never consults the situation, so it fires even under
  `code.notebooks-experiments`, whose purpose is organising code. That caps exact
  placement at **87.5%** on this corpus. Whether the rule or the ground-truth label is
  wrong is `96` §5, still unanswered. *Changing the product here would raise the score
  and might make the product worse; a person with a repo on their Desktop probably does
  not want it shredded into `matcher/source file`.*
* **`subject` is written `direct`**, the highest confidence the product has,
  outranking any model answer. A shape with no vocabulary should not hold that rank.
  `99` proposes the vocabulary; this document supplies the cost of not having it.
