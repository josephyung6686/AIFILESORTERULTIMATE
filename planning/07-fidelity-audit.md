# Fidelity audit — specs against the author's design

Date: 2026-08-19
Auditor: independent pass over all thirteen `parts/*/SPEC.md` (8,600 lines) against
[`00-database-agent-product-design.md`](00-database-agent-product-design.md) (source of truth),
[`01-product-design-structured.md`](01-product-design-structured.md), [`02-segmentation-map.md`](02-segmentation-map.md),
[`04-resolutions.md`](04-resolutions.md), [`05-minor-resolutions.md`](05-minor-resolutions.md).
Method: both design documents read in full; all thirteen specs read in full; every enumerated list in the
design counted against its spec; every `must` / `never` / `always` clause in the source of truth traced to an
owner; the whole spec set grepped for numeric thresholds and for stale cross-spec field names.
**No file was edited.**

---

## Verdict

**No spec contradicts the design.** The set is faithful on all five deviation tests: I found **zero invented
mechanisms without design warrant, zero hard-coded thresholds, and zero deferred content authored**. Three
real defects remain — one design `must` that survives only as an open question, one design clause owned by
nobody, and one seam where a resolution's field rename did not propagate — plus the structure contract
(`02`) is stale enough to now contradict the specs it governs.

---

## DEVIATIONS — spec departs from the design

**None.** Every behaviour, field and rule I checked traces to design text. The near-misses that most deserved
suspicion, and why each cleared:

| Part | § | Design says (quote) | Spec says | Verdict |
|---|---|---|---|---|
| P6 | §3.11 | "a small shared set of universal file facts, **such as** file type, creation date, language, duplicate family, version family, and sensitivity status" | adds one universal field, `download_session` | **Faithful.** §3.13 literally defines `Possible` as "A useful but insufficient clue, such as **membership in a short download session**" — so a fact for it must exist. §3.11's list is introduced with "such as". P6 pins it `destination_eligible = FALSE`, never above `possible`, excluded from the proposal-eligible read. It is the only field the spec set adds; the *name* deserves the author's ratification. |
| P7 | §8.4 | "Paths, complete extracted text, OCR output … should remain local" | permits `filename` as a releasable dossier item for non-protected files | **Faithful.** §7.7 is explicit that the residual dossier "includes the filename"; §7.3's Protected-Records carve-out ("must not cause filenames or content to be exposed in model prompts") is vacuous under any other reading. §8.4's list governs wholesale export — it also lists "OCR output" while §8.4 itself permits "selected excerpts". P7 flags the reading in OQ2 rather than burying it. Ratify, don't rewrite. |
| P4 | §2.8 | gives location *examples*, not a scheme | invents a closed 15-value `zone` vocabulary, 15 segment kinds, a canonical locator grammar | **Faithful.** §2.8's whole purpose is that "downstream logic … do not need separate logic for PDFs, DOCX files, images, archives, or OCR", which is unachievable without one scheme. Every zone and kind cites the § that names that place. P4 declares all of it under "Design decisions made here, and alternatives rejected". |
| P4/P6/P11/P13 | §2.8, §8.7 | design names no citation handle | `observation_key` (content-addressed) replaces `observation_id` everywhere | **Faithful.** §8.7 requires a rejection "stored with the evidence that produced them" to keep working; a per-row id dies on extractor upgrade. M14. |
| P6 | §3.12 | "The core database model is therefore simple" — five tables | adds an `unresolved` abstention table | **Faithful.** §8.5 asks "Did it abstain when evidence was absent?"; an absence cannot answer it. §0 already contemplates more tables ("movement plans, user corrections, and undo history"). B7. |
| P12 | §8.3 | never mentions directory creation | creates intermediate directories and conditionally removes them on undo | **Faithful.** §5.1/§5.12 leave frozen nodes as designed structure, not folders, so something must create them; §8.3 makes *every* filesystem mutation require "a reversible journal entry". Removal is conditional on empty + unreferenced + created-by-this-entry, and §7.11's no-delete rule is untouched (an empty directory contains no file). |
| P13 | — | design never names a "part" for review | a fourteenth part exists | **Faithful** — see *The five decisions*. |

---

## WEAKENED OBLIGATIONS

### W1 — §8.4's local-first default became an open question (severity: **MEDIUM**)

> **Design (§8.4):** "The default posture **must** therefore be local-first and data-minimizing."

P7 does not carry this as a binding rule. It appears only as **P7 Open question 11**: *"§8.4 requires the
default posture be 'local-first and data-minimizing' but does not say which of the four modes ships as the
install default, or what the default redaction settings are."* There is no entry in P7's *Design slice
owned*, no Done-means test, and no stated constraint on what may ship.

The design genuinely does not name a mode, so deferring *which* mode is correct. What was lost is the
constraint the `must` imposes on whatever is chosen: nothing in the spec set forbids shipping
`cloud_assisted` as the install default, which would satisfy every other P7 rule and violate §8.4's sentence.
This is the only place I found where a design `must` survives as a question with no test.

**Nearest faithful fix (not applied):** state in P7's Contract out that the shipped default must be `offline`
or `local_model` and that default redaction must be the more redacting option where the design is silent;
add a Done-means. Leave the exact choice deferred.

### W2 — nothing else weakened

The seven clauses the brief named as worth checking hard were all checked, and all hold:

| Clause | Where it is honoured |
|---|---|
| §6.12 "No system component may invent a new destination after freeze" | P10 freeze guarantee (legal set = `{node_id : plan_version = frozen, accepts_placement = true}`); P11 Done-means 2 tests **both** node-absence and `accepts_placement = false`; P12 refuses `node_not_in_frozen_tree`; P12 refuses `node_path_collision` rather than silently merging two frozen nodes into one destination. User-created folders post-freeze route to P10 as a tree edit producing a new plan version — and §7.10 and §7.6 explicitly give the *user* that action, so this is design-sanctioned, not a loophole. |
| §8.4 "enforced **before** content reaches any model" | P7 is a structural gate, not a policy P8 consults: P8 holds only references, `Released` is minted solely inside P7, the transport accepts nothing else, and the audit record is appended *before* `Released` returns. P7 precedes P8 in wave order for this reason. |
| §8.3 "never silently overwrite" | P12 Contract out §4, exactly the four §8.3 behaviours; Done-means 6: "No path exists through the code that overwrites an existing file." |
| §3.6 "must return `unknown`" | P8: `unknown` → `abstain` at all five sites, never `reject`, excluded from every failure count. P6: `unresolved` row, reason `model_returned_unknown`. |
| §4.2 "embeddings never establish the group by themselves" | P9 Contract out 9 states it as six numbered rules; SR2 fires when the graph is connected only by embeddings; Done-means 5 requires embeddings-off equivalence (any group not also reachable from a direct anchor is a defect); P2 carries `run_settings.embeddings_enabled` so it is testable. §6.5's downstream restatement is carried by P11. |
| §6.10 "correct abstention is a successful outcome" | P11 Done-means 11; P2's `abstained_correctly` is a passing verdict (Done-means 5); P8 reports abstention separately from rejection and never counts it as failure. |
| §8.6 "cost exhaustion must never turn into lower-quality automatic classification" | Stated and operationalised in all of P1, P3, P4, P5, P6, P8, P9, P10, P11, P12, P13 — each with a *distinct budget-deferral value* separable from abstention (B7), which is what makes the rule testable rather than aspirational. |

---

## DROPPED — required by the design, owned by no part

### D1 — §8.6's per-scan resource observability (severity: **MEDIUM**)

> **Design (§8.6):** "Every scan should have an observable budget for **elapsed time, memory, CPU or
> accelerator usage, storage, network use, and LLM cost**. The user should be able to see what is running,
> what has been deferred, and why."

Owners exist for two of the six resources and part of a third:

| Resource | Owner |
|---|---|
| storage | P1 ("P1 reports the database's and the log's storage as an observable budget line") |
| LLM cost | P8 (single egress point, O9) |
| elapsed time | **none** — P5 owns OCR time per file/scan only |
| memory | **none** |
| CPU / accelerator usage | **none** |
| network use | **none** |

P3 quotes the sentence and then disclaims it: *"the scan is P3's operation. §8.6's list of configurable
ceilings names none for traversal or hashing … P3 therefore operates under the general scan envelope with no
ceiling of its own named by the design."* That is correct about *ceilings* and does not discharge
*observability*. P13's `progress_line` (G14) carries file counts, not resource usage — its `entries[]` are
`label / count / state / source / cause`, with no resource dimension.

The second sentence ("what is running, what has been deferred, and why") **is** owned, by P13's
`progress_line`. It is the first sentence that has no home.

### D2 — named-and-unresolved, correctly surfaced (not spec faults)

These are design obligations the design itself does not answer. Every one is flagged in the owning spec
rather than invented, which is the behaviour the brief asked for:

| Obligation | Status |
|---|---|
| §8.3: "The product needs defined behavior for locked files, files currently open in another application, … aliases, shortcuts" | §8.3 supplies defaults for symlinks, package bundles and unavailable source/destination only. P12 carries those three plus permission-loss and cloud-sync; **locked, open-in-another-app, aliases, shortcuts remain undefined** (P12 OQ3). Correctly flagged, not guessed. |
| §8.4: "review and **delete** local derived data" vs §8.2's append-only log | A genuine contradiction inside the design. `Gate.delete_derived(scope)` exists in P7 marked *"see Open questions (conflicts with §8.2)"*; P5 OQ6 and P13 OQ11 raise the same conflict. Nobody resolved it unilaterally. Correct. |
| §4.9: "Rare but sensitive files … may be surfaced as protected records even when they do not meet a normal group-size threshold" | Stated as a P9 group-level constraint; *where it lands* (P9 group / P7 surface / P11 residual destination) is P9 OQ9, unresolved across four parts. |
| §3.4's "analysis tier" and §8.2's "extraction status by extractor tier" | Never enumerated by the design. Flagged consistently in P3 OQ4, P4 OQ1, P5 OQ3, P6 OQ1. |
| §3.9 "Purpose must be a first-class facet" vs §3.11 placing `purpose` only under College applications | Design-internal tension; P6 OQ3. |

### D3 — the fourteen earlier gaps: all closed, none reopened

Verified against the actual spec text, not against `04`'s claims:

G1 → P4 `text_units` (Record 3) · G2 → P9 computes / P1 `put_embedding` · G3 → P1 Contract out §7 ·
G4 → P1 Contract out §8 (all 15 keys) · G5 → P6 duplicate/version family · G6 → P6 `download_session` ·
G7 → P6 Photos `event` · G8 → P12 `cross_folder_not_permitted` + Done-means 19 · G9 → P3 R6
`curation_signal` · G10/G13/G14 → P13 · G11 → deferred to the author · G12 → closed by S1.

I checked the two structural moves for new cycles: M10 (residual library → P10) leaves P10's Contract in
from P11 reading *"nothing at tree-design time"*, so the cycle is genuinely gone; B3 (path resolution → P12)
introduces no upstream path dependency, since P11 and P13 both show ancestor `display_label` chains and never
a path string.

---

## HARD-CODED VALUES the design leaves open

**None found.** I grepped the whole spec set for digits adjacent to threshold/limit/margin/depth/window/size
vocabulary. Every hit was one of two things:

1. **Quotations of §8.6's own example line** — *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs
   deferred after the OCR limit; 34 files require model review; 18 files remain unreadable"* — reproduced by
   P3, P4, P5, P2 and P13 as the acceptance case for the legibility requirement. Not values.
2. **P4's illustrative `"config": { "dpi": 200, … }`** inside a JSON *example* of an `extraction_runs` row.
   §2.7 itself says "a practical rendering resolution **such as** 200 DPI", and P5 lists it under Deferred
   with the "such as" preserved. Not a fixed value.

Every threshold the design leaves open is explicitly deferred, by name, with the § that fails to supply it:

| Deferred threshold | Deferred by |
|---|---|
| §3.7 minimum score and minimum margin | P6 |
| §3.7 positional weight per zone; §2.6 signal-tier weights | P6 |
| §3.9 bounded-session window; §4.2 photo-event time/GPS/camera parameters | P6 |
| §2.2/§2.7 `no_usable_facts` threshold | P6 (surface) / P5 (caller) |
| §1.1 curated-vs-incidental threshold and the "software material" extension list | P3 — and every value is `undetermined` until authored (Done-means 15) |
| §4.x neighbour cap, neighbourhood size, cluster size, generic-hub frequency, minimum anchor count, "normal group-size threshold" | P9 OQ1 |
| §5.7 practical depth limit; §5.9 "large number of tiny folders" / "excessive" depth / "materially improve retrieval" | P10 OQ1–2 |
| §6.10 minimum support threshold and meaningful margin; the support *scale* | P11 OQ1–2, P8 OQ2 |
| §8.6 all twelve ceiling values | P1 ("P1 stores whatever is set and proposes no default") |
| §8.5 pass thresholds / regression tolerance | P2 OQ2 |
| §7.11 lifecycle windows ("older than 30 days" is read as a user-defined example, not a default) | P11, P13 |
| §8.3 deterministic suffix format | P12 OQ1 |
| hash algorithm; `normalized filename` rules | P1 OQ10; P3 OQ1 |

**Non-numeric picks that are declared rather than silent** — each stated as a spec decision with alternatives
rejected, and each within vocabulary the design already names: P4's Unicode NFC for mechanical normalization,
0-based half-open code-point offsets, 1-based container indices, and SHA-256 for `observation_key`.

**One scope narrowing to flag (severity: LOW).** S1 makes v1 **macOS-only** because §2.7 names Apple Vision
and no other OCR provider. The design never says the product is macOS-only, and §8.3 discusses
case-sensitive *versus* case-insensitive filesystems and platform-specific path limits as live concerns.
Narrowing OCR to the one provider §2.7 names is defensible; narrowing the *product* is a scope decision made
by `04`, not by the design. P12 nonetheless still implements both filesystem cases, so nothing is lost.

---

## DEFERRED CONTENT that was invented anyway

**None.** Checked item by item:

| Deferred body | Result |
|---|---|
| §5.7's 200–300 template library | **Zero templates authored.** P10 publishes the JSON *schema* they must conform to and the six §5.7 validation checks, and says outright: *"This spec defines the schema those templates must conform to; it authors none of them."* P2, P4, P5, P6, P8, P9, P11, P12 and P13 each carry it as a Deferred row. |
| §3.11 domain fact fields | P6 reproduces the six-row table **verbatim** and adds no domain field. The "several additional fields used only for search, privacy protection, explanation, or later review" that §3.11 asserts exist are deferred, not filled. |
| Career/recruiting schema (§3.15 names it a launch domain; §3.11 gives it no row) | **Explicitly refused.** P6: *"A launch domain with no stated fields. §5.4's Career *template* (company → role/cycle → document type) is a folder dimension list, not a fact schema, and is not copied here."* That distinction is exactly right and is the trap I expected a spec to fall into. Identity/medical/legal likewise refused. |
| §3.7 gazetteer contents | Deferred by P3, P4, P6, P7, P8, P9, P10, P11, P12, P13. Nobody lists a university, course-code format, company or venue. |
| §7.3 residual library | P10 lists **exactly the nine names**, reproduces the **four** default parent locations §7.3 states, and leaves the other five blank with *"the remaining five have none stated and none is invented here."* The eight §7.2 attribute slots are published as slots; their values are deferred. The user-defined areas §7.3 lists (Things to Read, Ideas, Memes…) are marked *"illustrations of user freedom; the product ships none of them as templates."* |
| §5.1's nine candidate top-level branch names | Correctly read as illustrative: *"they are illustrative and must not be shipped as a fixed set"* (§5.1: "a typical initial canvas **might** include"). |
| §7.5's eight residual review sets | Correctly read as illustrative by both P11 and P13 (§7.5: "It **may** show"). P13 adds *"must not assume eight sets or these eight names."* |
| §5.4's five template dimension rows | Reproduced literally, no sixth invented; P10 notes Code and Finance have fact schemas but no design-stated dimensions and defers them (S3). |

Invented **vocabulary over design-stated behaviour** — P4's zones/kinds/`source_type`, P5's three text-layer
states, P6's `unresolved` reason codes, P8's outcome and reason-code registry, P9's `support_kind`,
P10's `node_role` / `accepts_placement` / `disposition`, P11's `outcome` and `abstention_reason`, P12's
refusal classes, P13's `review_action` — is encoding, not authorship. Each value cites the § that states the
behaviour it names, and I traced the design's enumerations to confirm nothing was added or lost:

19 event types · 11 event-record fields · 13 file-record items · 4 verification points · 6 reliability states
· 6 universal fields · 6 domain field rows · 5 core tables · 4 seed kinds · 6 retrieval channels · 6 stop
rules · 4 LLM group tasks · 6 §5.7 validation checks · 5 node types · 8 residual attribute slots · 9 residual
templates · 8 residual actions · 3 dispositions · 13 plan fields · 5 staleness triggers · 4 collision
behaviours · 5 handling classes · 4 operation modes · 4 consent options · 6 audit fields · 5 redaction facets
· 10 attribution stages · 10 measured dimensions · 12 adversarial cases · 12 ceilings · 11 plan-version items
· 11 §1.1 exclusion names · 9 always-local items — **all present, all matching, none padded.**

The four validator check-sets are individually complete: §3.6's four → P8 site A; §4.8's six → site B;
§6.10's five → site C; §7.9's four → site D. No check was lost in the merge.

---

## THE FIVE DECISIONS — verdict on each

### 1. P13 added as a fourteenth part — **JUSTIFIED**

The design names a user-facing surface eight times, in the author's own words:

- §6.11 — *"The user should see these distinctions in **the review interface**"*
- §7.5 — *"a visible residual surfacing screen, not an automatic cleanup operation"*
- §7.6 — a set-level decision *"before the LLM analyzes individual files"*
- §7.10 — *"The residual review interface should make each recommendation editable"*
- §8.3 — *"show it to the user where policy requires review"*
- §8.4 — *"configurable redaction in **the canvas and review screens**"*
- §8.5 — the replay system serves *"the engineering team **and the user**"*
- §8.6 — *"**The user interface** should show the difference between completed work and deferred work"*

plus §5.2/§5.9/§5.11, which say "The interface should…" three times. And S4's structural argument holds on
inspection: §8.3's `Required review policy` field had no consumer, and P11's clause that P12 consumes only
records *"whose `review_policy` has been satisfied"* named an event that did not exist. P13's
`review_approval` is that event.

P13 is scoped correctly: it *"presents and collects; it never decides"*, writes four record types and nothing
else, emits no `stage_output` (correctly refusing to become an eleventh §8.5 attribution stage), and carries
a negative Done-means (#22) asserting it contains no scoring, classification, validation, path-resolution or
mutation code. All visual design is deferred — *"It fixes no pixel."*

**Caveat (minor):** P13's `Owns:` header claims §6.11, §7.5–§7.6 and §7.10 without the qualifier its body
applies, while P11's header claims the same sections. Both bodies state the split cleanly (P11 computes and
decides; P13 renders and collects — P13's *Explicitly not owned* table is precise, including §7.6's gating
rule). The headers, read alone, contradict `02`'s "no two implementers write the same file" discipline.

### 2. Embeddings kept in v1, owned by P9, stored by P1 as §0's compact local arrays — **JUSTIFIED**

Dropping them would have been the deviation. §4.2's own worked case is the reason: *"Embeddings are useful at
this stage because they can find files such as `HW 3.pdf` that lack the course code but resemble lecture
notes and earlier problem sets."* §6.3 requires *"Full-text and OCR embeddings should retrieve semantically
compatible node profiles."* §0 anticipates them and fixes only the storage form: *"store vectors separately as
compact local arrays if embeddings are used, because a vector database would add complexity without material
value at the initial scale."*

Consistency check passes on all four sections: P1 stores an opaque array, exposes `put_embedding` /
`get_embedding` and **no similarity function, no index, no nearest-neighbour query**, and keeps vectors out of
`files` and `events` (§0). P9 computes and keys on `content_hash` so a content change invalidates the vector
with the rest of that version's evidence (§8.2). §4.2's establishment ban and §6.5's *"a semantic embedding
alone is insufficient"* survive as six numbered rules with only two legal positions for a vector
(`mutual-semantic-retrieval` as a `support_kind` or as an `edge_type`) and an explicit *"No path exists by
which a semantic neighbour becomes an anchor."* Excluded from the walking skeleton, which is deterministic by
design.

### 3. Residual-library definitions moved P11 → P10 — **JUSTIFIED**

§7.4 is literal: *"Once the user approves the desired residual branches, those branches become **legal nodes
in the frozen destination tree**."* P10 freezes the tree, so P10 cannot freeze a complete one without the
library that produces those nodes. §7.4 also places the enablement moment inside tree design — *"**During
destination-tree design**, the product should show the residual library as an optional set of controlled
branches"* — and tree design is §5, which is P10's. The design puts it there itself.

The split is clean: P10 owns §7.2–§7.4 (nine names, eight slots, enable/disable/rename/relocate/merge/
replace, three dispositions); P11 retains §7.5–§7.11 (surfacing, set decisions, eight-action review, the §7.9
loop, bulk decisions, lifecycle). The enforcement §7.4 describes — *"The LLM may choose among them later, but
it may not create additional generic destinations"* — becomes structural: a template the user did not enable
has no node, so no model can name it, and P11 needs no residual-specific legality path.

**Caveat (cosmetic):** three specs still attribute residual-library contents to P11 in their Deferred tables
— P1 (*"§7.2, §7.3 (P11)"*), P4 (*"§7.3 | P11."*), P6 (*"P11's surface"*). P9, P12 and P13 were updated.

### 4. P12 resolves node → filesystem path — **JUSTIFIED**

Verified against the source of truth. §8.3's plan record carries these as two consecutive, separate lines:

```text
Requested destination node
Resolved destination path
```

So the resolution step exists in the design and was unassigned. §8.3 also puts the rules any resolution must
obey on the mutation layer — *"Long paths, invalid filename characters, reserved names, prohibited characters
on particular filesystems, and platform-specific path-length limits must all be normalized **before an action
is planned**"* — which is P12's transaction. And a plan-versioned tree holding platform-specific strings
would resolve differently on a case-sensitive and a case-insensitive volume, while §8.8 requires the same
frozen tree to survive across versions.

P12's resolution rules are conservative in the right direction: an `existing` ancestor short-circuits and its
`existing_path` is used verbatim (§5.10), every composed segment keeps its intended label beside its
filesystem-safe form (§8.3's explainability rule applied at every level, not just the last), and two sibling
labels that normalize to one name are **refused, never merged** — because merging would silently create a
destination the user never approved, which §6.12 forbids. P10 Done-means 11 makes it testable by grep: no
published node carries a separator-composed path other than `existing_path`.

### 5. The two-condition rule at one candidate — **DOES NOT WEAKEN §6.10**

§6.10 requires the best legal destination to *"reach a minimum support threshold **and** … exceed the
next-best destination by a meaningful margin."* At N=1 there is no next-best. The decisive sentence is two
lines later in the same section:

> **"A direct match to a unique node may be sufficiently strong to enter a suggested or automatic move plan."**

The design therefore contemplates a unique node clearing the rule. The alternative reading — that an
unmeasurable margin fails, so a unique node can never be accepted — contradicts that sentence outright.
P11's rule is the design's own: margin satisfied vacuously, **minimum support remains binding and is the sole
gate**, and *"A file that clears no support threshold **abstains even when only one destination exists** …
The scarcity of destinations is not evidence about the file, and a tree with one branch must not become a
funnel that everything falls into."*

It is also information-preserving rather than merely permissive: `margin_over_next` is null,
`margin_threshold` is still recorded, and `meets_margin` is `true_vacuous` — a *third* value, distinguishable
from a measured `true`, so a reviewer and a P2 replay can tell an unopposed candidate from a genuine margin.
P11 Done-means 10b asserts **both halves**, and notes that only the second (abstention despite the single
destination) proves the threshold stayed binding. B8(b) additionally gives the walking skeleton a second
frozen node so the margin path is exercised rather than bypassed.

---

## CONSISTENCY DEFECTS (not design deviations, but they break the contract set)

### C1 — `02-segmentation-map.md` is stale and now contradicts the specs it governs (severity: **MEDIUM**)

`02` calls itself the **structure contract**. It was not updated after `04`, which assigned the update to the
lead (*"— | 02-segmentation-map | Updated by the lead: two-node skeleton, P13, M10 back-edges"*). Four
contradictions with the current specs:

| `02` says | Specs say |
|---|---|
| "the twelve parts" (title, and twice in *Build shape*) | thirteen exist |
| no P13 row in *The parts* table | P13 exists and consumes §8.3's `Required review policy` |
| `P10 \| Tree design and freeze \| §5` | P10 owns §5, **§6.1, §7.2–§7.4** (B4, M10) |
| `P11 \| Placement and residual \| §6, §7` | P11 owns §6 **except §6.1**, §7 **except §7.2–§7.4** |
| skeleton: "`P10` a hand-authored **single-node** tree; freeze it" | B8(b) requires **two** nodes; P10 Done-means 2(a) and P11 Done-means 10b both assume two |

Also unaddressed: P13 has no position in `02`'s five-wave order, yet P7 and P8 both depend on it
(`NeedsConsent` "surfaces the four §8.4 options through P13").

### C2 — MINOR 6's `destination.kind` removal did not propagate to P2 and P13 (severity: **LOW-MEDIUM**)

MINOR 6 deleted `destination.kind` from P11's record in favour of P10's `node_role`. P11 documents the
removal (*"Why there is no `destination.kind`"*). Two consumers still reference the deleted field:

- **P2**, `bundle_expectation` (line 218): `` `place` + `destination.kind` ∈ approved_residual | approved_parent ``.
  Worse than a rename — `approved_parent` was never a `node_role` value. Under MINOR 6 the broad-parent case
  is `node_role = ordinary` with a non-empty `decision_depth.unsupported_levels[]`, so P2's residual
  expectation for §7.7 action 4 **cannot be expressed** against P11's current record without translation.
- **P13**, Contract in from P11 (line 83): `` `destination {node_id, kind}` ``. P13 uses `node_role`
  correctly everywhere else, so this is a single stale field name.

### C3 — §3.15 appears in no `Owns:` header (severity: **LOW**)

P6's body claims the fact-schema half and assigns the folder-template half to P10 (*"Split ownership"*), but
P6's header reads `§3.1–3.14` and P10's reads `§5, §6.1, §7.2–§7.4`. The section is covered in prose and
unowned in the headers.

---

## FAITHFUL — verified sound

Beyond the five decisions, the following were checked against the source of truth and hold. These are the
places where a blind agent had the clearest opportunity to drift and did not:

- **§2.4's three-way distinction survives intact.** *"An empty extraction result is different from an
  extractor that does not yet exist."* P4's `completeness` keeps `complete`-with-zero, `unsupported` and
  `metadata_only` as three distinguishable states, with a negative Done-means asserting it. B1 correctly
  killed P5's parallel status vocabulary — a per-file status structurally cannot say "EXIF read
  successfully, OCR capped," which is why the record is per-(file × extractor).
- **§2.6's absence rule is enforced structurally, not by convention.** *"the system must not mistake the
  absence of EXIF for proof that an image is a screenshot."* P4 forbids any observation recording an absence
  (conformance rule 12); "no EXIF" lives on the run record; P5's `whatsapp-stripped-exif.jpg` fixture asserts
  **zero** observations about the absence. An absence written as evidence would be a value P6 could rank.
- **§2.6's conflicting signals produce abstention through §3.7's margin**, not a new mechanism: two
  observations at `signal_tier` 1 and 3, no conflict row, no resolution at the extractor, and P6 emitting
  `unresolved` with reason `below_margin`.
- **§3.5's five academic context terms are literal** — "syllabus," "lecture," "credits," "instructor,"
  "semester" — and B8(a)'s fixture fix (`context_before: "Syllabus — "`) makes the walking skeleton satisfy
  the rule rather than route around it. The skeleton would otherwise have needed P6 to break §3.5 to pass.
- **§2.2/§2.3's producer-metadata discount is owned and two-tiered** (M4): `python-docx` produces *no fact in
  any field*; other author metadata may populate an authorship role and nothing else, and §3.8 already makes
  every authorship field `destination_eligible = FALSE`. The rule fires before facet ranking, so a discounted
  value never contests a margin it should not have entered.
- **§8.4's four consent options cannot silently collapse.** B2's `NeedsConsent` branch has *no reason code
  and no outcome value* in P8 — P8 states the absence explicitly so it does not read as an omission — and
  P8 Done-means 13 is falsifiable two ways (grep the vocabulary; replay the fixture). This was the one seam
  where a mismatch is a privacy failure rather than a bug, and the fix is structural.
- **§8.6's reduction ladder actually runs** (M9). P8 measures pre-release and runs summarize → preserve
  anchors → split → defer; P7's `dossier_over_budget` is a backstop that *"should never fire"*. A gate-only
  check would have run after the last point the dossier could be reduced, turning every over-budget dossier
  into a denial — strictly less capable and, by §8.6's own preference for deferral over silent loss, less
  accurate.
- **§7.9's hand-back loop is expressible end to end**: P11's `return_to_placement` + `returned_from`, P8's
  `reject`+`STRONGER_RELATIONSHIP_OVERLOOKED` → `return_to_placement` disposition, and M6's fix to P2's
  residual expectation so §7.8's Columbia-submission screenshot has a representable expected outcome. Both
  records persist; the residual finding is not discarded because placement later succeeded.
- **§8.8's shared-evidence boundary holds everywhere.** P1, P3, P4, P5, P6 and P9 all place their records in
  the shared database; M15's `group_acceptance` is the only plan-versioned P9 record, which lets one candidate
  group be accepted in v2 and rejected in v3 over a single shared dossier, response and verdict set. P6
  correctly places only display labels and aliases in the version (§8.8: "User labels and aliases").
- **§8.2's supersede-never-overwrite is uniform**, with `preferred` correctly living on P6's `file_facts`
  alone (M1) — §8.2 says *"the resolver may mark"* and §3.2 places the resolver after extraction, so the
  observation layer records what was read and what superseded it, and nothing about which one wins.
- **§8.5's ban on a single accuracy number is a negative acceptance test** in both P2 (Done-means 3) and P13
  (Done-means 19), not a style note.
- **P12 grants itself no capability the design withholds**: no delete of user files (§7.11), no semantic
  renaming (the design grants file renaming nowhere — "rename" in §5.10/§8.7/§8.8 refers to tree branches),
  and the only source removal is the verified cross-volume case (§8.2).

---

## Recommended actions, in order

1. **W1** — bind §8.4's local-first `must` in P7: constrain the shippable install default and add a
   Done-means. One paragraph.
2. **C1** — update `02-segmentation-map.md`: thirteen parts, P13 row and wave position, P10/P11 ownership
   columns, two-node skeleton. It is the structure contract and it currently contradicts the specs.
3. **D1** — assign §8.6's elapsed-time / memory / CPU / network observability. P3 owns the scan envelope and
   is the natural home; P13 renders.
4. **C2** — replace `destination.kind` with `node_role` in P2 line 218 and P13 line 83, and re-express P2's
   `approved_parent` expectation as `node_role = ordinary` + non-empty `unsupported_levels[]`.
5. **C3, and the stale P11 residual attributions in P1/P4/P6** — one-line edits.
6. **Author ratification, not repair:** P6's `download_session` field name; P7's `filename` reading of
   §8.4's always-local list; S1's macOS-only v1 scope.
