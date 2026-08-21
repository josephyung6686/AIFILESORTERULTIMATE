# Dispatch prompt — R3 · residual template library

Copy everything below the line into a new agent. The agent should not need this chat.

Give it read access to the repo. It writes under `planning/deferred-catalogues/09-residual-library/`. It does **not** edit P10/P11 SPECs or `src/`. Domain templates (the 200–300) are **not** this job — that is R1's schema + P10's later template half. This job is the **residual** library only.

---

You are authoring the **residual template library** for a local-first file-organization agent.

## Why you are here

`00` splits two libraries and the overnight work collapsed them:

- **Domain templates** (~200–300): deep meaningful hierarchies for recurring life areas (`Academics/School/Term/Course/Work Type`). R1 + P10.
- **Residual templates**: safe, broad destinations for files with **no reliable deeper association**. P10 owns definitions (M10); P11 owns the workflow.

P7's plan only hard-codes one literal name, `Protected Records`. P10's SPEC lists the nine **names** and defers every slot value. Without slot values, P11 cannot surface "17 receipts, tickets, and confirmations" as a review set, and the LLM has nothing constraining it from inventing `Random PDF Things`.

`00` §7.2 says the library exists to **prevent** the LLM creating arbitrary folders (`Random PDF Things`, `Important Screenshot`, `Miscellaneous Documents`, `Travel/Gate B12`).

## Product constraint (quote only from `00`)

Read:

- `planning/00-database-agent-product-design.md`
- `planning/01-product-design-structured.md` §7.2–§7.11, §5.7
- `planning/parts/P10-tree-design-freeze/SPEC.md` section "The residual template library"
- `planning/parts/P11-placement-residual/SPEC.md` if present — workflow only
- `planning/domains/CONNECTION.md` if present (R0) — `falls_through_to`
- `planning/25-domains-verification.md`

**Nine shipped template names, fixed** (`00` / P10 SPEC). You fill **slots**, you do not rename:

| Template | Default parent in `00` | Holds (verbatim job) |
|---|---|---|
| Temporary Screenshots | `Photos/Temporary Screenshots` | Screenshots that appear time-sensitive or remind the user of something but have no accepted project, trip, application, or event relationship |
| One-Off Images | `Photos/One-Off Images` | Images with no event, project, reference collection, or photo-family association |
| Reference Clips | `Personal/Reference Clips` | Saved visual inspiration, product references, quotes, recipes, short article captures, code snippets — useful for later retrieval but not part of a current project |
| Independent Records | `Personal/Independent Records` | Standalone certificates, notices, confirmations, forms, and PDFs with a durable purpose but no broader group |
| Receipts and Confirmations | *(none stated)* | Isolated invoices, delivery confirmations, booking records, boarding passes, purchase receipts, event tickets, and similar transactional documents |
| Reading Inbox | *(none stated)* | Papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association |
| Review Later | *(none stated)* | Files whose meaning is partly understood but whose final location requires a future decision |
| Unsupported or Encrypted | *(none stated)* | Password-protected archives, unreadable documents, damaged files, and unknown formats — or, more safely, represented without moving |
| Protected Records | *(none stated)* | Sensitive isolated material such as passport scans, medical documents, account statements, visas, legal forms, or credentials. Normally local-only; must not cause filenames or content to be exposed in model prompts |

**Eight slots every template defines** (`00` §7.2, P10 SPEC literal):

`display_name` · `default_parent_location` · `accepted_evidence_patterns[]` · `expected_file_types[]` · `sensitivity_restrictions` · `optional_shallow_subfolders[]` · `max_permitted_depth` · `treatment` (reviewed | retained | merely kept searchable)

**Opt-in** (`00` §7.4): not auto-created. User may enable/disable/rename/relocate/merge/replace-with-existing. Three dispositions: physical destination, review-only (never auto-move), leave-in-place. Once approved, they become legal nodes in the frozen tree. The LLM may choose among them and **must not** create additional generic destinations.

**User-defined areas** (`00`): Things to Read, Ideas, Shopping Research, Memes, Travel, Receipts to Process, Clips, Stuff to Sort — illustrations of freedom. **Ship none of them as templates.** Specify the *shape* a user-defined residual must fill (same eight slots) so P13 can collect one.

P7: Protected Records forbids filenames **and** content in prompts. `max_permitted_depth` and shallow subfolders must not become a second filing system (`00` §7.2: residual is intentionally broad).

## The join you must get right (this is the under-thought part)

Residual is the **complement** of domain association, not a parallel taxonomy.

For each of the nine, state `falls_through_from` / "do not steal from":

- Receipts and Confirmations vs finance domain vs travel domain vs `Independent Records`
- Reading Inbox vs research domain vs coursework readings
- Temporary Screenshots vs photo-event domain (EXIF/GPS/time cluster) vs Protected Records (screenshot of a passport)
- Protected Records vs safety-domain activation (R2): isolated *and* sensitive vs grouped *and* sensitive (a medical packet that **did** group still is not "residual")
- Unsupported or Encrypted vs P5 `unreadable` / `dataless` / protected container (11 §4b produces **nothing** — residual cannot claim a file that was never a `files` row)

If CONNECTION.md exists, use `falls_through_to`. If not, define it here so R0/R1 can adopt it.

`00` §7.5 review sets (screenshots with no event, standalone PDFs, unclear spreadsheets, receipts, protected records, encrypted, multiple plausible destinations, no extractable text) must be **projectable** from your evidence patterns + file types. If a review set cannot be produced from the slots, the slots are incomplete.

## What to research

- Real leftover piles on a personal Mac: Desktop, Downloads, Screenshots folder, `To Sort`, email attachments never filed, Apple Photos "hidden", AirDropped images, browser PDF pile.
- Boundary cases: a boarding pass that *is* part of a trip group (travel domain, not residual); a boarding pass alone (Receipts and Confirmations); a passport scan alone (Protected Records); a passport scan in an application packet (applications domain + safety, not residual).
- Depth: `00` wants residual **shallow**. Propose `max_permitted_depth` as a **slot with injected integer**, not a number you pick — unless `00` states one (it does not). You may recommend a number in RESEARCH.md as `proposal`.
- Default parents for the five `00` left blank: **propose**, mark `proposal`, do not pretend `00` named them.

## What you must not do

- Do not grow nine into 200. The "200–300" number in `00` is **domain** templates.
- Do not ship user-defined examples as built-ins.
- Do not invent `Random PDF Things` as a template — that is the failure mode.
- Do not assign handling classes beyond Protected Records' stated constraint.
- Do not auto-enable any branch.
- Do not edit `src/`.

## Output

```text
planning/deferred-catalogues/09-residual-library/
  README.md                 P10 injects definitions; P11 reads them; user-defined uses same schema
  01-nine-templates.json    nine objects, eight slots filled or explicitly `null` + why
  02-user-defined-shape.json  the eight slots a custom residual must supply
  03-falls-through.json     residual ↔ domain boundaries, with 00 worked cases
  RESEARCH.md
  check.py                  exactly nine shipped names, no extra; every slot key present;
                            Protected Records carries the no-filename-no-content constraint;
                            no fabricated 00 quotes; expected_file_types ⊆ SOURCE_TYPES ∪ extension examples
```

## Done when

- All nine have all eight keys (value or explicit null with reason).
- Complement rule is written: when a domain association is reliable, residual **must not** claim the file.
- Protected Records cannot leak filenames into a model prompt by construction of its slots.
- §7.5's eight review-set bullets can be named as queries over your patterns + file types.
- User-defined shape exists; zero user-defined templates shipped.
