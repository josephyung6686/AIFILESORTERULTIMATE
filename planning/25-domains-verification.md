# Domain catalogue — coverage verification

Date: 2026-08-21
Status: **count is real; the thing you asked for is not.** 574 entries, gate green, not a connected domain/subdomain library.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)
Contract: [`domains/_CONTRACT.md`](domains/_CONTRACT.md)
Gate: `python3 planning/domains/check.py` → **14 files, 574 entries, 0 problems** (re-run this pass).

You asked for 500+ **domains and subdomains connected to each other**, because a real corpus spans that many industries and file kinds. What landed is fourteen parallel slices of ~40 sibling labels, joined only by a collision list.

---

## Verdict

| What you expected | What is on disk |
|---|---|
| 500+ domains **and subdomains** | **574 flat domains.** Every id is exactly two parts (`acad.course-enrollment`). Zero `parent` / `children` / `subdomain` / `broader` / `narrower` fields. |
| Connected to each other | Connected **only** by `collides_with` (disambiguation, not hierarchy). 1 weakly-connected component of 574 — because every entry was required to name 1–7 neighbours, not because a taxonomy was researched. |
| Shared vocabulary across neighbours | **80% of field names appear in one domain only** (1,831 / 2,295). **88% of work types are unique to one domain** (3,276 / 3,722). **1,452 of 1,463 grouping reasons are singletons.** Neighbours do not share a language. |
| File types mapped into domains | P5 publishes 14 `source_type`s. Catalogue entries do not route `.pdf` / `.ics` / `.vcf` / mail / photos. The `.json` hit-rate of 574/574 is the file format of the catalogue itself. |
| Comprehensive industry + file research | Slice sizes `[40, 43, 40, 37, 38, 43, 43, 40, 45, 46, 45, 44, 56, 14]` — mean 41. That is a **quota per author**, not a coverage function of the world. Slice 14 exists because the first 560 had **no calendar domain** while `.ics` already routes to `calendar`. |
| Honest design vs proposal | **76% `proposal`** (436), 21% `inference`, **3% `design`** (19). The 19 design rows are the right seed. The other 555 were overnight invention under a shape contract. |

The gate is doing its job: required fields, no fabricated `00` quotes, no dangling collision ids, no held numeric thresholds. **A green gate means the JSON is well-formed. It does not mean the library is complete, hierarchical, or researched.**

---

## What is actually good

Do not throw the 19 design rows away. They are the seed.

- Shape per entry is the right product object: schema + recognition + work types + grouping reasons + template + collisions + sensitivity. That matches `00`: a domain is a fact schema **and** a folder template.
- Provenance is honest. `proposal` rows do not pretend to be in `00`.
- Collision **ids** all resolve (slice 14 closed the calendar dangling refs). Reciprocity is only 44% (874 / 1,977 directed edges), so the graph is one-way more often than not, but it is not fiction.
- Open questions (171) are real product questions (child's name as a folder level, teaching vs coursework, etc.). Keep them.
- `check.py` is the right kind of gate. Extend it; do not replace reviewer attention with it and stop.

---

## Why this is not the library

**No subdomain tree.** `acad.course-enrollment` and `acad.k12-schooling` are siblings. There is no `acad` node, no `acad.course`, no `acad.course.work-type.syllabus`. Fourteen `supercategory` strings are the only broader term, and they are file-level, not a graph.

**Collisions are not connections.** A connection in this product is: this domain **activates** when that evidence is present; this domain is a **child** of that one; this **file kind** plausibly belongs here; these two domains **share fields** so a file can hold both (`00`: an abstract can be research *and* an application). `collides_with` only says "do not confuse these two." 1,103 of 1,977 collision edges are one-way.

**Fields do not form one catalogue.** 2,295 distinct names for 3,706 occurrences. 130 pairs are the same concept spelled spaced and snake_case (`account type` / `account_type`). Council D6 is still open; the catalogue already froze both.

**Coverage is the 14 authors' imaginations, capped at ~40.** Missing from id/name/one_line this pass, among probes: cryptocurrency, religion, YouTube/social exports, divorce, HOA, startup cap tables as such, 3D print, drone, scrapbook, tabletop, concert tickets, Obsidian/Notion, iMessage/WhatsApp, password managers, Time Machine backups, homeschool, MOOCs, SolidWorks/BIM as named, IEP. Present: immigration, passport, military, veterinary, patents, CAD, lab notebooks, pharmacy. So it is not empty — it is **uneven**, which is what quota-writing produces.

**Launch vs library is a separate decision (D1).** `00` says fully support six launch domains, treat finance/identity/medical/legal as safety domains first, and leave others as **placeholders**. A placeholder library still has to be the real taxonomy, or P10 has nothing to propose and §3.6 has nothing to allow. Today's 574 are neither a tight launch set nor a researched placeholder tree.

---

## Other decisions that need the same kind of research

These are **catalogues of the world**. A planning agent cannot invent them in a night. Coin-flips (subject vs course, I6, install default) are not on this list.

| # | What | Why research, not a decision | Blocks |
|---|---|---|---|
| **R0** | **Connection architecture** | Write down `00`'s join (fields, schema set, file-neighborhood graph, folder dimensions). Not an industry DAG. | R1–R6, P6, P10 |
| **R1** | **Few schemas, then one agent per template** | R1a = canonical fields + small schema list + ~200–300 template roster. R1b = stamp on every row: real files, observations vs facts. R1c = merge. "500+ subdomains" = templates + folder depth, not 500 schemas (`00`: do not prematurely hand-author hundreds of specialized schemas). | P6, P8, P10 |
| **R2** | **Sensitivity detector + identifier classes + redaction transforms** | No part claims the detector. After P7, every file is `Denied(unclassified)`. | P7 as a product, P9/P10/P11 |
| **R3** | **Residual library (nine §7.3 templates, eight slots)** | Domain templates are ~200–300 (R1/P10). Residual is the complement: no reliable domain. Slots are empty. | P10, P11 |
| **R4** | **Gazetteers the rules actually fire** | §3.7. Catalogues 01–07 are screens/cameras/producer strings — not universities. | P6 validated facts |
| **R5** | **One jurisdiction's value lists** (D4) | Fields stay generic; tax-form *names* do not. Never a destination dimension. | Finance/legal/gov recognition |
| **R6** | **Academic / capture pattern catalogues** | Three term patterns and one course-code rule in `00`. No fuzzy dates. | P6 Tasks 8–12 |

Do **not** send a research agent at: D6 spelling, D2 *which record is authoritative*, I6 deletion-vs-append, `offline` vs `local_model`, "what is a corpus area", W1 ratification. Those are yours to write in one sentence.

**Dispatch R0 first** (with [`prompts/ALIGNMENT.md`](prompts/ALIGNMENT.md)), then **R1a**. Then fire **R1b once per roster row** (templates = the hundred-agent research; schemas = a handful, first). **R1c** after the swarm. R2 can run beside R1a. R3–R6 after R0.

How to stamp R1b: [`prompts/01-DISPATCH.md`](prompts/01-DISPATCH.md).
