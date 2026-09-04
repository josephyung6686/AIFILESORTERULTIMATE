# 99 — `subject` is a shape with no vocabulary, and it is why the tree is wrong

**Status: OWED TO THE OWNER. Nothing is authored here.** This is the largest single
accuracy defect measured tonight, and unlike `97` and `98` it is already costing the
owner wrong folders on real files.
Written 2026-09-04 by the fields agent. Companion to `97` and `98`.

---

## 1. The measurement

199 of the owner's real files, run `academic.coursework`, no model
(`baseline/academic_coursework.sqlite`):

```
files                        199
text units extracted      20,819
observations               6,679
FACTS                        121      <- and they are only TWO fields
```

The 121 are `subject` (104 rows, 43 files) and `term` (17 rows, 17 files). **No other
field has a deterministic or rule producer at all**, so 54 of the 56 catalogue fields
cannot fill without a model.

## 2. Where the 6,679 go

`subject` is filled by one direct slot, `cli.text.identifier`. Its gates, measured:

| gate | surviving | of 6,679 |
|---|---|---|
| observations | 6,679 | 100 % |
| in a zone the slot reads (`body`, `heading`) | 1,438 | 21.5 % |
| ...carrying a text span | 1,422 | 21.3 % |
| ...matching `_STRUCTURED` | **107** | **1.6 %** |
| distinct values they produce | **61** | |

The loss is not a normalizer rejecting good candidates. It is that **one slot subscribes
to the evidence and 54 fields subscribe to nothing.**

## 3. The part that is worse than the loss

`_STRUCTURED = re.compile(r"\b[A-Z][A-Z0-9]*[ -]?[0-9]{3,}\b")` — capital letters
followed by three or more digits. That is a SHAPE. It carries no notion of what a course
code is, and it is applied to every span of every document.

The most common `subject` values on the owner's actual disk:

| value | files | what it really is |
|---|---|---|
| `NY11794` | 8 | a postal address — Stony Brook, NY 11794 |
| `MD20852` | 8 | a postal address — Rockville, MD 20852 |
| `E1006` | 5 | **a real course** |
| `VHX7000` | 4 | a microscope model number |
| `PROGRAM2024` | 4 | — |
| `I1403`, `ELTU3017` | 3 each | **real courses** |
| `UA872`, `UA2657`, `UA179`, `UA487`, `UA1986` | 2 each | airline flight numbers |
| `U238`, `U235` | 2 each | uranium isotopes, from a physics exam |
| `BOEING777`, `BOEING737` | 2 each | aircraft types |
| `TWD43506` | 2 | a currency amount |
| `USZC4-743` | 1 | a Library of Congress call number |
| `MA01923`, `IN46256`, `NY10022`, `MA01003` | 2 each | more postal addresses |

**The two most common "subjects" on this person's disk are ZIP codes.** A folder tree
built from these facts proposes `NY11794` and `MD20852` as course folders holding eight
files each. The ground-truth agent measured 17 of 18 field values wrong; this is the
mechanism behind that number.

Two aggravating properties:

- **The facts are written `direct`** — §3.5's slot applies no test to the reading's
  reliability, and `direct` is above everything a model can propose. So a ZIP code
  outranks a correct model answer about the same file.
- **The pattern already caused one recorded incident.** `cli.py`'s own comment records
  `_STRUCTURED` claiming `AY 2024` and filing essays under "a course called AY2024".
  That was fixed by adding term patterns, not by constraining the identifier.

## 4. The decision the owner has to make

**What distinguishes a course code from every other alphanumeric identifier in a
document?** A rule can only be written once that is answered. Options, none of them
ruled:

| option | what it needs from the owner | what it costs |
|---|---|---|
| **a department-prefix list** (`PHYS`, `COMS`, `BUSIB`, `ELTU`, …) | a list, per institution, that grows | rejects a course whose prefix is not listed |
| **a context requirement** — the identifier must sit near a word like *course*, *syllabus*, *lecture*, *section*, or near a `term` fact | a small context vocabulary | rejects a bare code in a filename |
| **a shape constraint** — 2–4 letters then 3–4 digits | one ruling, no list | **measured below: not sufficient on its own** |
| **demote from `direct`** — a shape match is `possible`, never `direct` | one ruling | the model and the person can then overrule it; no folder is built on a shape alone |

**The mechanism for the second option already exists and is dormant.**
`facts.rules.context_check` and `facts.evidence.context_pair` are written and tested;
their only caller is `facts.rules.apply_rules`, which ships no authored rule set
(`85-REACHABILITY-TRIAGE.md` §10). What is missing is the rule set, not the machinery.

### The shape constraint on its own was tested and it is not enough

Tightening `_STRUCTURED` to `[A-Z]{2,4}[ -]?[0-9]{3,4}` over the same 199 files takes the
distinct values from **61 to 26**. It does remove every postal code, every isotope and
every aircraft type. But measured rather than assumed, it fails in both directions:

- **it removes two real courses** — `E1006` and `I1403` have one-letter prefixes;
- **it keeps the flight numbers** — `UA179`, `UA487`, `UA872`, `UA1986`, `UA2657` all
  survive, as do `ISO8601`, `JAMA316` (a journal citation), `OCT2007`, and the Library
  of Congress call numbers `HG030`, `HG146`, `HG153`, `HG381`, `HG3918`.

Of the 26 survivors exactly one, `ELTU3017`, is unambiguously a course. **So a shape can
narrow this and cannot settle it** — which is the argument for the context requirement
and, independently, for the demotion. Demoting to `possible` is the one option that
needs no vocabulary at all and stops any of this reaching a folder unchallenged.

## 5. Why this was not decided by an agent

Choosing what counts as a course code is authoring the vocabulary §3.5 leaves to the
deployment, and it is the same class of decision as `97` and `98`. It is listed here
with the counts attached because the owner should decide it knowing that the status quo
files his physics homework under a uranium isotope and his applications under a ZIP code.
