# Dispatch prompt — R1c · merge and fact-check the swarm

Copy everything below the line into a **single** new agent **after** R1b has landed (or after a declared cutoff). This agent does not research a new domain. It fact-checks the forest the swarm produced.

Give it read access. It may extend `planning/domains/check.py` and `_CONTRACT.md`, write `planning/domains/FOREST-REPORT.md`, and **only** patch node files to (a) add missing reciprocal edges, (b) replace synonym fields with canonical keys, (c) mark refuse_node that R1a should have dropped. It does **not** invent schemas. It does **not** edit `src/`.

> ### ⚙️ AMENDMENT 2026-08-27 — edit authority widened, or this gate cannot close
>
> The catalogue closed at **358/358 rows** on 2026-08-27. Running the edge gate over the finished
> corpus (`python3 planning/domains/check_edges.py`) returns **1,892 findings**, and under the
> authority as originally written **364 of them are unrepairable** — the agent would be dispatched
> to close a gate it is forbidden to close. Specifically:
>
> - **215 `also_holds_with` edges authored on `kind: template` rows** (81 rows; 31 of them
>   template→template). `also_holds_with` is schema↔schema only (CONNECTION §5, `_CONTRACT` rule 14).
>   The only sound repairs are **lift the edge to the schema pair** or **delete it** — and (a)/(b)/(c)
>   authorize neither. Reciprocating them would *propagate* the violation; and "Do not collapse
>   `also_holds_with` into `collides_with`" below correctly forbids the third option.
> - **149 cross-kind `collides_with` edges** (81 rows). `collides_with` is same-kind only. Repair is
>   to lift to the schema pair or push down to the template pair.
>
> **Therefore this agent MAY additionally:**
> **(d)** lift a template-borne `also_holds_with` to its schema pair, or delete it, recording which
> and why per row; **(e)** resolve a cross-kind `collides_with` by lifting to the schema pair or
> pushing to the template pair; **(f)** normalise a bare-string edge into `{domain, signal}` — but
> **only where the row's own memo already supplies the argument**. Where it does not, record it as
> `NEEDS-R1b-REFIRE`, do not invent a signal.
>
> **Lifting is not collapsing.** The prohibition below stands: never convert an `also_holds_with`
> into a `collides_with`. They mean opposite things — co-holding vs mutual exclusion — and guessing
> destroys the distinction CONNECTION §5 exists to protect.
>
> **Also fold in `check_edges.py`.** It postdates this prompt pack, is referenced by no prompt and no
> contract, and its 1,892 findings currently block nothing. The done-when below ("green on the live
> node set") cannot be met while the edge gate runs outside the gate. Merge its checks into
> `check.py` and delete the standalone, or state why not.
>
> **The `one_way_reason` escape hatch is unusable as written.** §5 below says reciprocate "unless
> `one_way_reason` exists", and the done-when sets the bar at ≥90%. Measured on the closed corpus:
> `collides_with` is 47.9% reciprocated (1,252 one-way), `also_holds_with` 12.5% (267 one-way) —
> and **zero node files carry the `one_way_reason` key at all.** Meanwhile ~71 rows *do* argue their
> one-wayness, in prose buried inside the `signal` string, where no gate can read it. So 1,519
> deliberate one-way edges are currently indistinguishable from 1,519 oversights. Before mass
> back-filling reciprocals, **lift those existing prose arguments into a real `one_way_reason` key** —
> otherwise this gate will manufacture reciprocal edges for seams a row already argued should not
> have them.
>
> **`nodes/_refused/` does not exist.** §3 below requires refusals to move there; all **44** argued
> refusals currently sit in the live set and are counted in every metric. Decide whether to move them
> or to amend §3 — but note the count is 44, while `planning/26-research-dispatch-state.md`:73-81
> still records 6, so the state file is 38 behind disk.
>
> **Note its one misleading label:** `check_edges.py` buckets `resource_operations`'s four
> bare-string `also_holds_with` entries under `KEY_DRIFT_target`, whose message reads "uses <key> not
> 'domain'". They are not key drift — they are bare strings carrying no argument at all. Fix the
> label before trusting the bucket.

---

You are the **merge gate** for a swarm of per-domain research agents.

## Why you are here

Hundreds of agents wrote `planning/domains/nodes/<id>.json`. Each was isolated on purpose. Isolation causes systematic holes:

- A collides with B; B never mentions A (overnight reciprocity was 44%)
- Two nodes proposed `course_name` and `course` for the same facet
- Calendar still has no owner
- Roster id with no node file and no refuse
- `also_holds_with` used as a synonym of `collides_with`
- File examples whose `source_type` is not in shipped `SOURCE_TYPES`
- Inherited fields restated with different spellings
- Placeholder nodes padded so the count looks like 500

Your job is to **measure and repair the join**, not to rewrite the library.

## Read

- `planning/00-database-agent-product-design.md`
- `planning/domains/CONNECTION.md` if present
- `planning/domains/roster.json`
- `planning/domains/canonical_fields.json`
- `planning/domains/_CONTRACT.md`
- `planning/domains/check.py`
- `planning/25-domains-verification.md` (what “connected” was supposed to mean)
- every `planning/domains/nodes/*.json`

Do not treat the old `planning/domains/0*.json` slices as source of truth. They are the 574 dump. Harvest only if a swarm node is missing a design cite you can verify.

## Fact-check (all of these)

1. **Coverage vs roster.** Every roster id has a node file or you write `MISSING` in the report. Every node id is on the roster (strays are errors).
2. **Kinds.** Every node has `kind: schema | template`. Every template has `schema_id` that exists. Schema count stays small; template count is not padded to 500. `parent_id` if present is unused by activation checks.
3. **Node test.** `refuse_node` files go to `nodes/_refused/`. Live **schemas** have a distinct 3–6 field set. Live **templates** differ in detection signals, dimensions, or privacy from the schema default. Work types and extensions are not nodes.
4. **Fields.** Templates reuse schema keys. Cluster `proposed_fields`: merge synonyms into canonical_fields. Kill spaced vs snake pairs. **Do not** target “≤30% singleton fields” by inventing shared fake fields — `00` wants small per-schema sets, so some fields *should* live on one schema (`target university` is Applications-only). Fail if two schemas use different keys for the same role without `role_split`.
5. **Edges.** Closed vocabulary only. Reciprocate `collides_with` and `also_holds_with` unless `one_way_reason` exists. Same pair must not be both collide and also-hold unless CONNECTION allows it. Dangling ids fail. Residual names in `falls_through_to` must be one of the nine `00` §7.3 names.
6. **File kinds.** Union of `file_kinds.source_types` covers all 14 `SOURCE_TYPES`. Each file_example maps to a legal source_type. Format-only activation (`never_alone: false` on extensions) fails unless CONNECTION carved an exception.
7. **Quotes.** Re-run the fabricated-quote check against `00` (existing `check.py` `cited_quotes`).
8. **Numbers.** No threshold numbers in node JSON.
9. **Sensitivity.** Only `none` | `potentially_sensitive`.
10. **Activation ≠ grouping.** Spot-check nodes that mention `HW 3` / packets / sessions; they must not treat grouping as schema activation.
11. **Worked `00` files** still make sense if those ids exist: BUSIB syllabus, Wash U application, abstract-that-is-also-application, passport → safety + Protected Records, `.ics`, `.vcf`, HEIC with EXIF.

## What you may change

- `check.py` to scan `nodes/*.json` (one object per file **or** `entries` arrays — support the R1b shape).
- `_CONTRACT.md` required keys to match R1b's object.
- Reciprocal edge patches (minimal JSON edits).
- Canonical field additions from clustered `proposed_fields`; then rewrite nodes to use the chosen key.
- Move `refuse_node` out of the live set.

Commit-style discipline: one concern per edit if you touch many node files; do not “improve” prose.

## What you must not do

- Do not fill missing schemas yourself. List `MISSING` / `THIN` for a re-fire of R1b.
- Do not add roster ids.
- Do not pad to 500.
- Do not collapse `also_holds_with` into `collides_with`.
- Do not assign handling classes.

## Output

`planning/domains/FOREST-REPORT.md`:

- counts (schemas vs templates, landed, refused, missing, thin)
- fields: synonym merges; which keys are correctly schema-private (`target university`)
- collision reciprocity before/after
- `SOURCE_TYPES` coverage table
- list of nodes to **re-fire** (id + why)
- `NEEDS-JOSEPH`

`python3 planning/domains/check.py` green on the live node set, or a printed problem list that is the work remaining.

## Done when

The gate is honest: green means schemas few, templates reuse fields, edges reciprocal, file-kinds covered. Missing nodes are listed as re-fire. Reciprocity ≥ 90% or `one_way_reason`. Every `SOURCE_TYPES` member has ≥1 owner. You did not invent a schema to cover a hole. You did not treat median-depth-of-ids as a quality metric (`00` folder depth is `dimension_order`).
