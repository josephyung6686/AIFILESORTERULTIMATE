# `unsupported_region_copy` — the one honesty string

Authored 2026-08-22 by R5. Status of the wording: **proposal**, until Joseph ratifies it.
Nothing is committed by the authoring agent.

## Why the slot exists

D4's risk seat, verbatim (`planning/overnight/council/seat-what-goes-wrong.md`):

> Give the residual surface one string that can say a domain is unmodelled for the user's
> region.

and its diagnosis of the gap:

> nothing distinguishes a file that fell to residual because its country is not modelled from
> one that fell there because it is genuinely a boarding-gate screenshot. The residual surface
> (§7.5) has no field that can say *"this domain is not modelled for your region."*

The DECISION-BRIEF's D4 section carries the same ask ("give the residual surface one string
that can say *this domain is not modelled for your region*"). Without it, a user outside the
shipped jurisdiction sees a big residual pile and concludes the product does not work, rather
than that it does not do their country. With it, residual review can tell the truth in one
sentence.

## The slot

- **Name:** `unsupported_region_copy`.
- **Where it lives:** every pack manifest (`_pack.json`), one string per pack — see
  `_SCHEMA.md`. It is pack data because it exists precisely because a pack is a partial map of
  the world; a deployment with no pack loaded has the same honesty problem and the same string
  serves it (the injection point may carry the slot with no pack — `PACKS.md`, "The unpacked
  deployment").
- **Type:** one factual string. **Not** a template with variables, not a per-domain matrix,
  not tone-adjustable UX copy — the risk seat sized it as "One row attribute, not a feature",
  and this catalogue does not invent UX voice beyond the factual slot.
- **Consumers:** P10/P11's residual machinery — `01` §7.5's residual surfacing screen is the
  natural surface, alongside (never replacing) the residual template the file actually landed
  in. The wiring is P10/P11's; the recorded seam is that P11's SPEC currently has no field for
  it (the risk seat's §7.5 observation above). This catalogue defines the slot and the string;
  it does not edit P11.
- **When it may show:** when a file's activation evidence touched a jurisdiction-dependent
  domain (finance / legal / government recognition) and the loaded pack — or the absence of
  one — could not supply that region's values. Deciding *that condition* is the consumer's
  logic, built on activation flags and pack metadata; this file deliberately specifies only
  what the string may say, not when, because thresholds and firing conditions are injected
  slots elsewhere and are not this catalogue's to write.
- **What it must never do:** name the file, echo content, or leak anything a residual card
  would not already show — it is a statement about the *product's coverage*, not about the
  file. It never gates anything: safety classification and Protected Records routing are
  upstream of it and independent of any pack (`README.md`, "Safety does not depend on the
  pack").

## The proposed string

```text
This domain is not modelled for your region.
```

Provenance: **proposal.** The wording is the brief's own phrase with sentence casing — chosen
so the string states a fact about coverage (the domain is unmodelled) rather than a judgement
about the file (unimportant, unrecognisable), which is exactly the distinction `00` §8.6 draws
for deferred work: the product must avoid "the false impression that an unprocessed file was
understood and found unimportant."

Carried in `00-example/_pack.json` as the live example of the slot; every future pack manifest
carries it (checked mechanically), and `check.py` holds its provenance at `proposal` until
Joseph ratifies the wording — at which point the same edit records the ratification in the
manifest's `origin` note and relaxes the check. (The provenance vocabulary stays the repo's
closed three; ratification is recorded as a fact, not minted as a fourth value.)
