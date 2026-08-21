# Residual library — research notes (R3)

Grounding for the slot values in `01-nine-templates.json` and the boundaries in
`03-falls-through.json`. Everything in this file is research context or `proposal`-grade
recommendation — the JSONs are the deliverable, this file is why they say what they say.
Curly double quotes are reserved for verbatim `00` quotations (verified by `check.py`); every
other source is paraphrased and named. Unlike the JSONs, this file may hold recommended
integers: the dispatch explicitly allows recommending a number here as `proposal`, for slots
whose runtime values are injected.

## 1. Method and sourcing honesty

- The primary source is `00` itself: the residual sections define the nine names, the eight
  slots, the opt-in model, the review sets, the worked examples, and the lifecycle policies.
  Every slot value that could be read off a `00` sentence was, and is cited with a verbatim
  quotation.
- Where `00` is silent (five default parents, all depth values, most treatments), the value is
  marked `inference` when one `00` sentence makes the answer nearly forced, and `proposal`
  when it is a genuine recommendation. Forks worth Joseph's attention are in the README's
  NEEDS-JOSEPH section.
- macOS behavioral facts below (screenshot naming and default location, AirDrop's landing
  folder, the Photos library being a package) are **recalled, not retrieved** — no web pages
  were opened for this catalogue. They are used only to ground evidence-pattern choices, never
  as slot values, and the sibling catalogues they point at (02 screen resolutions, 04 filename
  patterns) carry their own per-row verification tags.
- Sibling-catalogue claims were checked against the shipped JSONs on disk: catalogue 04 does
  carry macOS Screenshot / Screen Shot legacy / screen-recording rows, an Android screenshot
  row, Windows screenshot and snipping rows, and CleanShot — and **no iOS screenshot row**,
  because iOS screenshots use the camera-roll `IMG_` convention (that catalogue deliberately
  labels naming conventions, never media types). Catalogue 06 carries DOI / arXiv / ISBN
  rows; catalogue 01 carries browser and export-tool producer strings.

## 2. The leftover piles on a real personal Mac

`00` names the residual reality directly: “a screenshot of a boarding gate, a saved product
image, a one-off receipt, an unconnected PDF form, a spreadsheet with unclear purpose, an
article saved to read later, a private document with no project association, an encrypted
archive, or a file whose contents simply cannot be read”. The piles below are where that
material actually accumulates on a personal Mac, and what each implies for the evidence
patterns.

| Pile | What accumulates | Where it lands in this library |
|---|---|---|
| **Desktop** | screenshots (the macOS default screenshot location is the Desktop, `Screenshot ….png` / legacy `Screen Shot ….png`), drag-outs, one-off exports | Temporary Screenshots via the screenshot-hypothesis pattern; One-Off Images; Review Later for the partly-understood exports |
| **Downloads** | the deepest pile: browser PDFs, installers, AirDropped files (AirDrop lands here), emailed attachments the user saved out, receipts, tickets | Reading Inbox (browser-pdf-pile pattern), Receipts and Confirmations, Independent Records, Unsupported or Encrypted (`.dmg`, installers), One-Off Images |
| **A user Screenshots folder** | users who redirect screenshot capture keep a dedicated folder | same as Desktop's screenshot slice; an existing curated folder the enablement model can map Temporary Screenshots onto rather than inventing a new branch |
| **`To Sort` / `Stuff` folders** | deliberate deferral piles | exactly Review Later's material — and `00` prefers mapping the template onto the existing folder: “Another may already have an existing To Sort folder, and the system should map the Review Later template onto that folder rather than inventing a new one.” |
| **Email attachments never filed** | mail stores live under `~/Library/Mail`, which is inside a P3 exclusion root (`Library`) — the pile the product sees is only what the user saved out, usually into Downloads | Receipts and Confirmations (emailed confirmations, `.eml` exports), Independent Records, Reading Inbox |
| **Apple Photos "hidden"** | the Photos library is a macOS package — a protected container under `planning/11-ops-runtime.md` §4b: P3 never descends, nothing inside becomes a `files` row | out of scope by construction; only exported images reach the corpus, entering as One-Off Images / Temporary Screenshots material |
| **AirDropped images** | photos and screenshots received from other devices, frequently with stripped or partial metadata | One-Off Images via the stripped-metadata-photo pattern — absence of EXIF is never screenshot proof |
| **Browser PDF pile** | papers, articles, statements, tickets, forms — saved once and never filed | Reading Inbox (papers, articles — catalogue 06 identifier hits; catalogue 01 browser producer strings), Receipts and Confirmations (tickets, confirmations), Independent Records (forms), Protected Records when P7 protects (statements) |

Note "hidden" in the Photos row (straight quotes deliberately) is this file's label for the
album, not a `00` quotation — `00` never discusses Photos-app albums; the row's substance is
the §4b protected-container rule.

Two structural observations from this inventory, both already encoded in the JSONs:

1. **Piles are mixed; homes are not.** Every pile above spreads across several residual homes
   plus material that is not residual at all (a receipt that belongs to an accepted trip, a
   paper that belongs to a course). That is why the evidence patterns are per-template content
   classes rather than per-location rules — location is where the pile is, never what a file
   is.
2. **Leave-in-place is a first-class outcome for every pile.** “A user may decide that all
   isolated screenshots should remain where they are and should never be moved.” The library
   constrains what may be *proposed*; it never implies movement.

## 3. Boundary cases

The eleven boundaries and fourteen worked cases live in `03-falls-through.json`; the four the
dispatch called out resolve as:

- **Boarding pass in a trip group** → travel-domain material via the group; residual never
  offered (complement rule). **Boarding pass alone** → Receipts and Confirmations.
- **Passport scan alone** → Protected Records (the `identity → Protected Records` edge,
  fixture 4 of CONNECTION-EXAMPLES.md). **Passport scan in an application packet** → the
  packet claims it, protection intact — grouped-and-sensitive is not residual.
- **Screenshot of a passport** → Protected Records, never Temporary Screenshots: content class
  outranks capture mechanism.
- **Unreadable vs never-read** — Unsupported or Encrypted claims only files whose extraction
  *ran* and ended unreadable/unsupported. iCloud-dataless files were never opened
  (`planning/11-ops-runtime.md` §5), protected-container contents were never scanned (§4b),
  and budget-deferred files are waiting, not damaged. None of the three is claimable.

## 4. `max_permitted_depth` — semantics and recommended values (`proposal`)

**Semantics** (proposal, needed for the slot to be checkable): the number of folder levels
permitted *beneath the enabled residual node itself*. `0` means the home is flat — files sit
directly in it; `1` permits exactly the optional shallow subfolder level and nothing below.

**Recommendation: `0` for eight of the nine; `1` for Reference Clips only if its optional
clip-kind subfolders ship** (NEEDS-JOSEPH NJ-R3-2; if they are dropped, `0` there too).

Why the floor everywhere: `00` makes residual homes “safe, intentionally broad destinations”,
and “An isolated file should normally remain high in the tree because there is no evidence
that it deserves a deep project-specific path.” Any depth inside a residual home is structure
built without evidence — the second filing system the dispatch warns against. Deeper wants are
handled by the design's own channels: a real recurring area belongs to a domain template; a
personal taxonomy belongs to user-defined areas or the custom-template flow. Protected Records
additionally treats flatness as an exposure bound: no content-derived subfolder names can leak
into paths, screens, or P12's composed labels.

The runtime values stay injected (`residual_max_depth.<template id>`); these integers are
recommendations for the injection site, nothing more.

## 5. The five blank default parents (`proposal`)

`00` states four: `Photos/Temporary Screenshots`, `Photos/One-Off Images`,
`Personal/Reference Clips`, `Personal/Independent Records` — images under `Photos/`,
documents under `Personal/`. The five blanks are all document-kind homes, so the proposal
extends the stated pattern: `Personal/Receipts and Confirmations`, `Personal/Reading Inbox`,
`Personal/Review Later`, `Personal/Unsupported or Encrypted`, `Personal/Protected Records`.

Held against alternatives `00` itself names as user freedom, not defaults: “Another may
prefer Desktop/Inbox for unclear downloads, Personal/Clips for visual references, and
Travel/Confirmations for tickets and reservation records.” The enablement model (rename /
relocate / merge / replace-with-existing) already delivers every one of those; a default only
has to be safe and unsurprising. Two homes carry extra reasoning:

- **Review Later**: the stronger `00` preference is mapping onto an existing `To Sort` folder;
  the proposed parent applies only when no such folder exists.
- **Unsupported or Encrypted**: `00` leans away from moving at all — its holds sentence says
  this home may hold “or, more safely, represent without moving” the material — so the parent
  matters only if the user chooses a physical-destination disposition.
- **Protected Records**: the label deliberately reveals nothing about contents; wherever it
  lives, the branch renders as a protected area with configurable redaction (§8.4).

All five are NEEDS-JOSEPH NJ-R3-1.

## 6. Treatment assignments

`00` fixes the vocabulary — “whether the file should be reviewed, retained, or merely kept
searchable” — and assigns none explicitly. The assignments and their strength:

| Template | Treatment | Strength |
|---|---|---|
| Temporary Screenshots | reviewed | `inference` — `00`'s lifecycle example is a review policy for exactly this home: “show temporary screenshots older than 30 days” |
| One-Off Images | merely kept searchable | `proposal` — no reminder function, no record duty; retrieval is the remaining value |
| Reference Clips | merely kept searchable | `inference` — “useful for later retrieval” is the stated purpose |
| Independent Records | retained | `inference` — “a durable purpose but no broader group” |
| Receipts and Confirmations | reviewed | `inference`, fork NJ-R3-3 — “surface travel confirmations after their date has passed” vs durable purchase records |
| Reading Inbox | reviewed | `inference` — “review Reading Inbox every two weeks” |
| Review Later | reviewed | `inference` — definitionally the deferred-decision home |
| Unsupported or Encrypted | retained | `proposal`, fork NJ-R3-4 — nothing is readable to review or search; the duty is keeping the record |
| Protected Records | retained | `inference` — “keep protected records indefinitely”; any review is user-manual, never model review |

The lifecycle around every treatment is non-destructive: creation date, last access, and
duplicate status may surface review suggestions, but the product never deletes, never
auto-expires, and never moves material out of a protected area without explicit user action
(§7.11, paraphrased; the quoted policies above are `00`'s own examples).

## 7. What was verified vs what is proposed

- **Verified mechanically**: every curly-quoted span in all five text-bearing files of this
  catalogue exists verbatim in `00` (`check.py`, run green); the nine names and eight slot
  keys match `00` and P10's SPEC table exactly; `expected_file_types` values are P5
  `SOURCE_TYPES` members or literal extensions; `falls_through_to` targets are the nine names
  and no residual is ever a source; the eight §7.5 review-set bullets project from the slots;
  the user-defined shape carries exactly the eight keys and ships zero templates; `check.py`
  itself was mutation-tested against ten failure classes (fabricated quote, renamed template,
  numeric value, bad file type, stripped Protected Records constraint, residual-as-source,
  non-nine target, shipped illustration, dropped review set, missing slot) and caught all ten.
- **Verified by reading**: the adopted join matches CONNECTION.md §5/§7 and fixture 4 of
  CONNECTION-EXAMPLES.md; the P7 paraphrases match P7's SPEC (the `unreadable_unclassified`
  handling class; the Protected Records denial P11 consumes); the P11 shapes named
  (`residual_set.evidence_availability`, `residual_candidates`) match P11's SPEC; `11 §4b`
  and `§5` say what `03`'s b9 claims.
- **Proposal, awaiting Joseph**: the five default parents; the depth semantics and values in
  §4; Reference Clips' six subfolder names; the two treatment forks; the browser-pdf-pile
  evidence pattern; who authors the shadow edge for user-defined homes.
