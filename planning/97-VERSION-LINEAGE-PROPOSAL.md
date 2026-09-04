# 97 — Version-family lineage: what is missing, and what a person has to decide

**Status: OWED TO THE OWNER. Nothing is authored here and nothing is bound.**
Written 2026-09-04 by the fields agent. Companion to `98` (near-duplicate metric)
and `99` (the subject identifier vocabulary).

---

## 1. What the design says, and where it stops

`00` §2.9 lists *"duplicate and version-family signals"* among what basic extraction
produces. **It names them and defines none of them.** There is no sentence anywhere in
`00` that says what makes two files two versions of one document.

`00` §8.3 says the one thing that is settled, and it is a prohibition:

> "A content-hash match supports deduplication review; a filename match alone does
> not."

So the design rules out the rule everyone reaches for first — `Report.pdf` and
`Report (1).pdf`, or `draft_v1` and `draft_v2` — and puts nothing in its place.

## 2. What is built and waiting

`facts.families.version_family` is complete, tested, and takes its rule as an injected
parameter with no default:

```python
def version_family(conn, *, file_ids, lineage_rule) -> tuple[str, ...]
```

`lineage_rule(conn, left_file_id, right_file_id)` returns a `Lineage` or `None`:

```python
@dataclass(frozen=True)
class Lineage:
    family_value: str
    reliability_state: str        # `validated` or `possible` -- NEVER `direct`
    evidence_refs: tuple[str, ...]
```

The half the design *does* state is already enforced: Done-means 24 makes a version
family never `direct`, because no explicit slot states a version relation, and
`Lineage.__post_init__` refuses any other state. Identical content hashes are excluded
before the rule is asked — those are a duplicate family, not a version family.

**As of tonight it is bound to a refusal** (`lambda conn, left, right: None`), the same
shape this deployment already uses for the model stage it does not ship. It therefore
writes no fact, and — correctly — no `unresolved` row either: the module's own rule is
that a relation nobody proposed was never attempted.

## 3. The decision the owner has to make

**What evidence makes two files two versions of one document?** The answer has to be
something a rule can check and cite, because `Lineage.evidence_refs` must name real
observations — a family with nothing to cite is not written.

Candidate signals, none of them ruled, in rough order of how much this project's own
constraints favour them:

| signal | what it would need | what §8.3 says about it |
|---|---|---|
| a shared document title in `title`/`heading`, plus different content hashes | nothing new — both are already extracted | not forbidden; it is content, not a filename |
| a shared `authored_by` plus a near-identical body prose | prose is now extracted from PDFs and docx (2026-09-04) | not forbidden |
| an explicit revision marker in the document (`Rev. B`, `v3`, `Draft 2`) | a marker vocabulary, which does not exist | not forbidden, but it is a vocabulary to author |
| filename stems differing only by a version suffix | nothing | **forbidden as the sole basis** by §8.3 |

**A second decision rides on the first:** `Lineage.family_value` is chosen by the rule
and it is the name the family is stored under. It carries the same constraint the
duplicate family was just fixed for — **it must not be a file hash.** `content_hash` is
`file_hashes` in `privacy.vocabulary.ALWAYS_LOCAL`, and a fact's value is releasable by
design: it becomes a `grouping.seeds.Seed`, then a group display label, then site-B
dossier content. Whatever names a version family must be safe to show and to send.

## 4. Why this was not decided by an agent

`84` §1: absent means refuse, never guess. §2.9 naming a signal without defining it is
exactly that case. Authoring a version rule from a reading of the word "version" would
be an implementation answering a deferred design question, and the one rule that is
obvious — the filename — is the one §8.3 names and rejects.

## 5. What it costs to leave it open

Measured on a 42-file corpus of the owner's real files: **`version_family` fills nothing,
`duplicate_family` fills 15 files in 7 families.** The duplicate half needs no ruling and
is unaffected. What is lost is the case where the owner has two genuinely different
drafts of one document — common on this disk, and currently invisible to the product.
