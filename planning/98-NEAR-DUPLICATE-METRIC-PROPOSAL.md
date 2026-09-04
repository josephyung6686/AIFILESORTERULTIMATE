# 98 — The near-duplicate distance metric: one number nobody has ruled

**Status: OWED TO THE OWNER. Nothing is authored here and nothing is bound.**
Written 2026-09-04 by the fields agent. Companion to `97` and `99`.

---

## 1. What the design says, and where it stops

`00` §2.6:

> "Exact hashes and perceptual hashes can identify duplicates and near-duplicates."

It names the perceptual hash and **states no distance metric and no threshold.** §8.3
separates the two claims by strength — a content-hash match supports deduplication
review — and §3.13 puts anything weaker than byte identity below `direct`.

## 2. What is built and waiting

`facts.families.duplicate_family` has two halves and only one of them needs a number:

| half | evidence | state | needs a number? |
|---|---|---|---|
| byte identity | identical `content_hash` | `direct` | **no** |
| near-duplicate | perceptual hashes within some distance | `possible` | **yes — this proposal** |

```python
def duplicate_family(conn, *, file_ids, perceptual_hash_label, near_match)
```

`near_match(left_raw, right_raw) -> bool` is required with no default. P5 already emits
the input: `extractors/image.py` writes a `perceptual hash` observation whenever the
image reader supplies one.

**As of tonight it is bound to a refusal** (`lambda left, right: False`). The exact half
is unconditional and unaffected.

## 3. The decision the owner has to make

**Two things, and the second is the one that matters.**

1. **Which metric.** Perceptual hashes are compared by Hamming distance in practice, but
   `00` names no algorithm, and the distance is only meaningful against the hash the
   reader actually produces. Whatever ships must be stated together with the hash it
   assumes.

2. **Which threshold.** This is a judgement about the owner's tolerance, not a technical
   constant. It trades two errors that are not symmetric:
   - too loose → two different photographs are called near-duplicates, and the review
     screen invites the owner to delete one of them;
   - too tight → a resized or re-exported copy of one photo is treated as two files.

   The product's standing instruction is that a wrong confident answer is worse than a
   question, which argues for the tight end — but the number is the owner's.

**Equality is not a way out.** `near_match = (a == b)` looks like it avoids choosing a
number; it is a threshold of zero, and zero is a number nobody ruled. It is also nearly
useless: two identical perceptual hashes over different bytes is a rare case that the
exact-hash half mostly already covers.

## 4. What it costs to leave it open

Measured on a 42-file corpus of the owner's real files including 16 real photographs:
**7 duplicate families over 15 files, all from byte identity, all `direct`.** Not one of
them needed this number. The owner's disk is full of true byte-identical copies —
`file (1).pdf` beside `file.pdf` — because that is what a browser download does.

So the cost of leaving this open is low today and rises with the photo library: resized
exports, screenshots of screenshots, and messaging-app re-encodes are exactly the
material §2.6 names and exactly what byte identity cannot catch.

## 5. Why this was not decided by an agent

`84` §1: absent means refuse, never guess. A threshold invented in an implementation is
a policy with no reviewer, and this one is directly visible to the owner as a deletion
suggestion about their own photographs.
