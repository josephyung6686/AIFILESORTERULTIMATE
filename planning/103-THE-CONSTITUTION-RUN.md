# 103 — Four changes, four measurements

**For the owner.** Every number below is from a run of the shipped command over your
199 files with the model in the loop (`--enable-cloud`). Nothing here is reasoned from
the code; `102` §1 is what happens when it is.

The product constitution of 2026-09-05 is the standard each change is measured
against. Items 2 (coverage), 3 (valid options only) and 5 (the number) are the ones
these four commits act on.

## The scoreboard

| | `e31c70f` | `9351788` | `3ac0c0b` | `3e4a64d` |
|---|---|---|---|---|
| | filename | +coverage, +valid options | +embeddings | +closed vocabulary |
| **exact** | 0 | 0 | 0 | **0** |
| right parent, wrong leaf | 6 | 6 | 6 | **6** |
| top folder only | 3 | 3 | 0 | **0** |
| **wrong** | 3 | 3 | 0 | **0** |
| not placed | 29 | 29 | 35 | 35 |
| **"ask the person" — abstained** | 29/29 | 29/29 | **25/29** | **29/29** |
| files blocked from the model | 114 | **19** | 19 | 19 |
| model answers that can never be a folder | **56** | **0** | 0 | 0 |
| vectors stored | 0 | 0 | **95** | 95 |
| files classified | 104 | 104 | **119** | 119 |
| fields filled correctly | 15 | 15 | 15 | 15 |

## What each one was

**`e31c70f` — the model is shown the filename.** `filename` and `path` are the only
two zones present on all 199 files and the model saw neither. §7.7 makes the filename
the flagged sixth releasable kind, `items.Filename` is built, and
`gate._precheck_items` passes `allow_unratified=True` expressly to admit it — but the
only construction of one in `src/` was a fixture. For `homework0.py` the model was
shown two metadata rows while the word `homework` sat in a field it never received.

**`9351788` — coverage, and valid options.** `model_route_permitted` refused every
unclassified file on the written premise "an unclassified file is one nothing has read
successfully". Measured false: 95 of 199 had no classification and **every one had
evidence**. 114 files → 19, and the 19 are the protected ones, which stay out.

In the same commit, `open_question` stopped offering fields that can never become a
folder. It had offered everything pending and merely SORTED the levels first, which
does not stop a model answering what it was shown: 28 `file_type`, 16 `authored_by`,
9 `creation_date`, and **zero `subject`**. After: every answer is a folder level.

**`3ac0c0b` — §4.4's semantic channel, on a measured threshold.** The comment this
replaced said the channel "needs a threshold, channel weights and a compatibility
predicate that nothing has measured". So they were measured — every pair of labelled
files, encoded by the weights the deployment names, split by whether one course:

```
SAME course   n=73   p10=0.212  p50=0.417  p90=0.603
DIFFERENT     n=362  p10=-0.045 p50=0.057  p90=0.165
```

The 90th percentile of DIFFERENT sits below the 10th of SAME. F1 peaks at **0.30** —
90.7% precision, 67.1% recall. It removed the 3 wrong and 3 flat placements.

**And it broke the north star, which the scorecard caught.** The 29 files whose right
answer is *ask the person* went from 29 of 29 abstained to 25. `00`:56 warns of exactly
this: "Retrieval systems can introduce irrelevant context and increase unsupported
conclusions when their context is too broad."

**`3e4a64d` — a work type the library never authored is not a work type.** The 4 bad
placements were `Coursework/Daniel Lacker/IEOR3658/.pdf`. The rule producer wrote
`lecture`, `homework`, `exam` — all members of the library's 942 terms. The model wrote
`.pdf`, `Proposed Scope`, `GRC Proposed Scope V2.1`, `Abstract` — none of them members,
and `.pdf` became a folder. `normalize_for_model` already promised that a model value is
canonicalised by the same rule the deterministic path uses; `work_type`'s rule is
membership and it had no branch. **29 of 29 abstentions restored, 0 wrong, 0 flat.**

## What `subject = 0 of 43` actually measures

Every value the producer wrote is **the right course under a different spelling**:

| file | produced | the label says |
|---|---|---|
| `Desktop/Python 1006/lecture01_introduction.ipynb` | `E1006` | `PYTHON1006` |
| `Downloads/Essay 2 Final Draft.pdf` | `ELTU3017` | `University Writing` |

`ELTU3017` **is** University Writing. `E1006` **is** the course in the folder you named
`Python 1006`. The label follows the folder, which is you saying the folder you made is
the naming authority. The model also found `IEOR3658` on four probability lecture PDFs
the labels leave blank — a course code nothing had read before retrieval was on.

**So string equality against one spelling is not the product's scoreboard.** The official
scorer says so in its own words — *"folder-name spelling is normalised away, because
which spelling the product mints is a normalisation decision and not a sorting one"* —
and placement is the row that matters.

Reconciling `E1006` with `Python 1006` is a model decision under constitution 1, and the
model cannot make it: the folder name lives in the `path` zone, which is one of the nine
always-local kinds. At placement (`00`:105) a node profile carries the user-selected
label by design; at the fact call there is no folder label at all.

## The last mile

**Six files sit at `right parent, wrong leaf` and have through all four commits.** They
land in `Desktop/Python 1006` and should land in `PYTHON1006/lecture`. `work_type =
lecture` is written for five of them, `validated`, from the library's vocabulary. The
level exists, the fact exists, and the file stops one level short.

That is the whole distance between 0 exact and 6 exact, and it is the next thing to run.
