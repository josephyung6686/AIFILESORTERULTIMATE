# engineering.embedded-firmware — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.embedded-firmware.json`](engineering.embedded-firmware.json).
Salvage: none. No prior draft of either file existed; both are written fresh.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from
  `make_prompt.py engineering.embedded-firmware`.
- `planning/domains/nodes/engineering.json` — my schema anchor, read in full (JSON only; the
  `.research.md` was not needed). Supplied the default template I am measured against, the four
  proposed keys, the ten default deterministic signals, and the one sentence that licenses this
  row's dimension departure.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration, read once.
- `planning/domains/nodes/code.software-project.json` — my most dangerous neighbour, read for
  `one_line`, `recognition`, `file_examples`. It turned out to be **REFUSED**, which changed two
  things below.
- `planning/domains/_CONTRACT.md` 168–186 — rule 14: `also_holds_with` **joins schemas only**,
  `collides_with` **joins same-kind pairs**, any unrecognized entry key is a gate finding.
- `planning/00-database-agent-product-design.md` — grepped, never streamed. Four spans matched
  verbatim (audit below).
- `planning/domains/roster.json` — every edge endpoint checked against `domain_id`.
- `SOURCE_TYPES` — the fourteen members as listed verbatim in the stamped prompt.
- `grep -rl "engineering.embedded-firmware" planning/domains/nodes/` → **zero hits**. No landed row
  has argued a boundary against this id, so every boundary below is stated first here and is a
  RECOMMENDATION to R1c for the reciprocal side.

**External reality checks** (no field, gazetteer, regex or threshold created). *Software
Configuration Index* — the named DO-178C deliverable binding a delivered image to a controlled part
number and build environment; it is why `SW-PN-40012-003_Software-Configuration-Index.pdf` is in
the list, being the one firmware artifact that is unambiguously an *engineering document*. *Intel
HEX / S-record* — ASCII record lines with a type byte, address and checksum, terminated by an EOF
record; this is why the `.hex` fixture's observations say "ASCII record lines beginning with a
colon" rather than "unreadable binary" — a text extractor *can* read it and finds no natural
language, which is a different and more useful fact. *GNU ld linker scripts and link maps* — a
`MEMORY` block with per-region `ORIGIN`/`LENGTH`, and an emitted map reporting section sizes
against those regions plus a symbol table; the one structure in this corpus no neighbour produces.
*A/B slot layouts and signed OTA manifests* — two application slots, a config region, a key region,
and a manifest carrying from-version, to-version and an eligibility condition.

## THE CHARGE — the case that this row should not exist

**C1 — it is a medium / target platform, which is a property, not a filing world.** The roster hint
reads "Software written to run on a specific piece of hardware rather than on a general computer."
That defines the row by *where the code executes* — a property of the program in the way a page
count or a file format is a property of a document. A row defined by target platform is the same
error as a row defined by `.dwg`, and the hint's own phrasing is the strongest evidence against
this id.

**C2 — it duplicates the code schema, and duplicates a row already refused.** Every firmware
project is a repository with a build system, a manifest and a source tree; code's whole activation
apparatus fires on it. The only stated difference is a value — the target. And
`code.software-project` was **already refused** as "the Code schema's own activation rule and its
own dimension order... the schema's default situation wearing a template id". A firmware row risks
being that identical refusal with a hardware sticker on it.

**C3 — it duplicates its own schema's default template.** A released image with a part number, a
revision and an approval record is simply `engineering_artifact_type = released technical data
package` on `project → design_item → lifecycle_stage → engineering_artifact_type`. The anchor
already lists "released technical data package" among its work types, and ALIGNMENT is explicit
that work types are values, never nodes.

**C4 — its evidence is never-alone all the way down.** `.hex`, `.bin`, `.elf`, `.dfu` are
extensions. "Firmware" is a document-type word. STM32, ESP32, Nordic are product and organisation
names — the class 00 rules insufficient for a university name.

### Why the charge is defeated

**C1.** The row is defined not by the target but by the *relation the target creates*. "Where it
runs" is a property; *an image bound by a labelled compatibility statement to a named hardware
revision* is a filing relation, and it is the one that governs retrieval. The question this corpus
answers is "which image may I put on this board" — not code's "what language is it in", not the
engineering default's "what stage is the design at". The activating evidence is a co-occurrence of
labelled slots, which is why the platform word sits in `never_alone` and the manifest triple sits
in `deterministic`.

**C2.** The boundary is **source versus release**, and it is sharp. This row does not fire on a
repository — `never_alone` says "a repository whose target is a microcontroller is still a
repository". Its corpus is the released side, which frequently does not live in the repository at
all: a release directory, a PLM record, a manufacturing hand-off, or a supplier's firmware drop
whose sources the holder never possessed. The refusal of `code.software-project` helps here: that
row was refused for restating its schema's activation rule, and this row restates nobody's — none
of code's markers appear in my deterministic list, and none of mine appear in code's.

**C3.** The default cannot express the compatibility triple (its ten signals are all labelled
*document* structures; the primary artifact here is not a document); it keeps a level this corpus
cannot fill (`lifecycle_stage`); it forbids the level this corpus needs (`revision_or_baseline`).
And its privacy rule does not contain this row's refusal at all.

**C4.** Conceded in full and encoded rather than argued away: eleven `never_alone` rules, including
all four of C4's items by name, plus the download-session rule and "absence of readable text is not
proof of an executable image".

**Verdict: the node survives.** `refuse_node: false`. Had only C1's defence held, I would have
refused.

## The node test, all three legs

**Leg 1 — signals.** The schema's ten deterministic signals are labelled *document* structures:
title blocks, requirement rows with verification-method columns, TDP manifests, engineering-change
structures, BOM parent/child tables, analysis input/result packages, verification matrices,
prototype-build records, archive manifests over those, parent-folder context. **Not one can fire on
a `.hex`, a `.map`, a linker script or a signed OTA package**, which carry no document structure at
all. My four discriminators — the target-binding triple, memory-region structure, the
image+digest+signature triple, and the software part number / configuration index — appear in no
sibling I checked. This is the strongest leg.

**Leg 2 — dimensions.** Default: `project → design_item → lifecycle_stage →
engineering_artifact_type`. This row drops `lifecycle_stage` — firmware does not traverse design
gates once, it re-releases continuously against the same item, and the gate vocabulary the schema
validates against does not appear in this corpus; an unfillable level opens an empty branch. It
*promotes* `revision_or_baseline`, which the schema proposes `destination_eligible: false`. The
inversion is evidential, not aesthetic: the release version is the scope of the compatibility
statement, the digest, the signature and the notes, so a release level groups artifacts already
delivered as a unit rather than fragmenting a definition — the harm the schema's `false` guards
against. The anchor licenses the exception verbatim: "A specific released-baseline template may
later justify a different order, but the schema default does not." That sentence is from
`engineering.json`, not from `00`, and is attributed as such. Under PR-6 `dimension_order` stays
`[]`; the order lives in `template.why`.

**Leg 3 — privacy.** The schema's rationale is proprietary / export-controlled / IP. This row's
differs in kind: a release directory routinely holds **live secrets** — a code-signing private key,
a per-device provisioning table of serials, MAC addresses and device keys, debug unlock tokens —
and a `.map` or unstripped `.elf` publishes a full symbol table and memory layout. The rule this
row adds is a **refusal**: credential material beside a release is not an engineering artifact to
be filed by item and revision. It routes to Protected Records; identity has the claim.

## Reciprocal boundaries — both directions, same fixture on both sides

| Neighbour | This row holds | The neighbour holds | Shared fixture |
|---|---|---|---|
| `code.software-project` | the release: image, manifest, compatibility statement, map, signature, update package | the repository: roots, package manifests, source tree, build config | `stm32f411_flash.ld` — code's on repository evidence, `also_schema: "code"` here; `firmware-release-manifest_SN100_v1.4.2.json` is mine, and code cannot fire on it (no repo root, no ecosystem manifest) |
| `manufacturing.production-record` | the released image and what it may run on | what was written to which serials, in which lot, at which station | `LOT-24-113_Programming-Log.csv` — manufacturing's, though every row cites `v1.4.2`; `SN100_FW_Release-Notes_v1.4.2.pdf` is mine, though the lot record quotes it |
| `engineering.pcb-layout` | the image bound to the board | the board: layers, fabrication and assembly packages | `SN100-PCB_RevC_Gerber-Package.zip` — pcb-layout's; `SN100-APP_v1.4.2_HW-RevC.hex` is mine. They share the `RevC` token and nothing else |
| `engineering.change-order` | a release note reporting what a build contains | the instrument authorising a change to a released definition, with disposition | `SN100_FW_Release-Notes_v1.4.2.pdf` — mine; a defect list is not a disposition. A change record whose affected-item slot names the software part number is change-order's, firmware or not |
| `engineering.verification-validation` | a test result that is one member of a release manifest | a file organised as a requirement→method→result matrix | `SN100_HIL-Verification_v1.4.2.pdf` — V&V's, image version as configuration-under-test metadata; the same version inside the OTA manifest is mine |
| `engineering.product-certification` | the released image a certificate points at | the certificate and its application file | `SW-PN-40012-003_Software-Configuration-Index.pdf` — mine, though certification programmes produce that document type; the granted certificate citing it is certification's |
| `identity.credentials-passwords` | **nothing** — this is a refusal | signing keys, per-device secrets, unlock tokens | `secure_boot_signing_key.pem`, `provisioning_keys_batch07.csv` — named on my side *so that my answer on them is a refusal*, both `group_without_copying_facts: true` so the release's version and target never flow onto them |

## The collision fixture

`DIR-865L_REVA_FIRMWARE_1.08.B01.bin` — a router firmware update the holder downloaded for a device
they own. It carries the **exact triple shape** my manifest signal looks for: product model,
hardware-revision token, version token, all in one filename. It is the sharpest false positive on
the node because the tempting evidence is stable, structured and true — it really is firmware, and
it really is targeted at hardware.

Discriminator: **there is no authored release structure anywhere near it.** No manifest, notes,
map, signature, configuration index or approval — only a filename in a downloads directory beside a
support-page capture and an unrelated installer. Two rules kill it: the triple must appear in
**labelled slots** of a release record, not in a filename; and 00's "A session should never be
treated as proof of topic" removes the downloads neighbourhood that would otherwise assemble it
into a firmware project. Routes to Review Later (NJ-FW-4).

A quieter second collision: a device **settings backup** exported from a router or synthesizer,
named `config.bin` — same extension, same device, same "backup" framing, but no version, no target
statement, no image structure. It sits in `needs_llm`, not `deterministic`.

## Files considered and rejected

- **A silicon-vendor datasheet** (`STM32F411xC-E_Datasheet.pdf`). Names the exact part every other
  file names. Rejected: a received reference document controlling nothing the holder owns —
  `engineering.standards-library` or a reading residual. Kept only as the false file the "silicon
  or vendor name alone" `never_alone` rule exists to remove.
- **IDE workspaces, `platformio.ini`, `Makefile`, `.uvprojx`.** Build and environment
  configuration; code's, and `code.dotfiles-environment`'s for the editor half. Including them
  would have made this row a second code schema — C2's charge, conceded.
- **Serial-terminal logs, logic-analyzer captures.** Debug telemetry produced *while* working, with
  no version binding; a residual, not a controlled release artifact.
- **A schematic or netlist.** `engineering.electrical-schematic`'s. Considered because firmware and
  schematics share folders; rejected because sharing a folder is not sharing evidence.
- **A mobile companion app build (`.apk`, `.ipa`) shipped with device firmware.** Genuinely hard:
  versioned, signed, paired with a device. Rejected because it runs on a general computer — the one
  place the roster hint's platform distinction does real work — and its filing world is app
  distribution, not hardware effectivity.
- **A firmware requirements document.** `engineering.requirements-specification`'s; requirement
  rows are that row's signal and appear nowhere in mine.
- **Devkit / bench-setup photos.** Photos schema. No release structure.

## Sparse-file discipline

`blink.bin` is this node's `HW 3.pdf`: a few hundred bytes, no strings, beside two other tiny
images and a sketch file. `group_without_copying_facts: true`, `facts_legal` is universals only,
and `must_not_conclude` covers both halves — no target or version inherited from neighbours, and
absence of readable text is not proof of an executable image. The two credential fixtures carry the
same flag for the opposite reason: there the point is that the *release's* facts must not flow onto
a secret.

## `proposed_fields` — empty, deliberately

The string this material is saturated with is the **hardware target**. No key is proposed. The
schema's `design_item` proposal already names the configuration item a file controls, and a
firmware image's target *is* a design item under that definition; a second key would ship two
spellings of one role — the duplication the schema row asks R1c to avoid for `stage` and
`artifact_type`. A build identifier, an image digest and a signing-key identifier are evidence with
no destination: a directory named for a digest is unnavigable, and one named for a key identifier
publishes a credential reference onto the filesystem. Parked in `open_question`.

`proposed_context_terms` (26) are R6 candidates, marked PROPOSED, not design; 00 states the
pattern-plus-context shape for course codes only and does not list these.

## Neighbours considered that did **not** get an edge

- **`engineering.bill-of-materials`** — firmware really does appear on a BOM as a software part
  line. No edge: the BOM's activating structure is a parent/child quantity table, and one software
  line does not make the BOM firmware evidence, nor the release a BOM. Recorded rather than edged,
  to avoid giving one evidence item three claimants.
- **`engineering.aerospace-airworthiness`** — the Configuration Index fixture comes from that
  world. No edge: airworthiness owns approval of an aircraft or modification; the index itself is a
  software release record. If R1c disagrees, the edge belongs on that row's side.
- **`engineering.prototype-build`** — a bring-up image on a prototype board is real, but that row's
  evidence is the *physical* build record and its deviations; nothing discriminating is shared.
- **`code.scratch-prototypes`** — `blink.bin`'s neighbourhood. No edge: the honest answer there is
  a residual on both sides, not a contested claim.
- **`research.*`** — firmware for a lab instrument is either a release (mine) or an experiment
  (research's); they do not compete on the same bytes.
- **`also_holds_with` is empty by contract** (rule 14: schemas only; this is a template). The one
  true co-activation — a CI-produced tagged release that is both a repository artifact and a
  controlled product component — is carried as `also_schema: "code"` on `stm32f411_flash.ld`, and
  is licensed by the engineering schema row's own `also_holds_with` entry for code.
- **`role_split` is empty**, and this is the interesting refusal. The split this material most
  wants is *authored and released by the holder* against *received and installed by the holder* —
  the SN100 release against the DIR-865L download, the sharpest discrimination on the node. There
  is no canonical field pair to split against, and minting a producer-side key to solve one
  template's problem is the move that produced thousands of private field names overnight. It
  lives in `needs_llm` and in the collision fixture instead.

## Audits run

- `python3 -m json.tool` — parses.
- Key set compared mechanically against `finance.crypto-assets.json` and
  `code.scratch-prototypes.json`. My draft carried a structured `node_test` object copied from the
  *schema* anchor; landed **template** rows use a `node_test_note` string, so it was renamed and
  flattened. `code.scratch-prototypes.json`'s key set is a strict subset of mine. Remaining
  additions over crypto's set: `proposed_context_terms` (authorised by the stamped prompt),
  `proposed_context_terms_note`, `proposed_fields_note` (the `<key>_note` convention already on
  landed rows). **If the gate rejects `_note` keys beyond the landed set, R1c should fold those two
  into this memo — the argument is reproduced above and nothing is lost.**
- Four `00` spans matched verbatim under whitespace normalisation (project-before-time;
  parent-provides-context; extension routing-signal; download-session). All four
  `falls_through_to.design_cite` strings matched `00` line 120 verbatim. The one non-`00`
  quotation was grep-verified against `engineering.json` and attributed to that file. **No `00`
  quotation here is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (14/14); every
  `falls_through_if_inactive` is a §7.3 name.
- Every `collides_with.domain` resolves to a roster `domain_id` (7/7); every
  `falls_through_to.residual_template` is a §7.3 name (4/4); the single `also_schema` (`code`) is a
  roster schema id.
- `fields`, `proposed_fields`, `also_holds_with`, `role_split`, `dimension_order` all empty, each
  with a note saying why.
- No threshold, score, count or handling class. `sensitivity` is `potentially_sensitive`.
- Only the two assigned files were written. Roster, `canonical_fields.json`, `check.py`,
  `engineering.json` and all neighbour nodes untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-FW-1 — the hardware target has no canonical key, and I refused to mint one.** (a) The target
  is a `design_item` **value** — what this row recommends and what its dimension order assumes;
  coherent, but it means one design item can be a board and another a mechanical assembly, widening
  the key. (b) A separate target/platform key is minted — ships two spellings of one role and
  contradicts the schema row's own request to R1c. (c) The target stays evidence only and is never
  a fact — which makes "which images may run on Rev C" answerable by grouping alone, never by
  filing. **Recorded, not resolved. No field proposed.**
- **NJ-FW-2 — this row recommends `revision_or_baseline` as a dimension while the schema proposes
  it `destination_eligible: false`.** The schema licenses a released-baseline template to differ,
  in the sentence quoted above. R1c must decide whether that licence is per-template (this row and
  `engineering.drawing-package` would both invoke it) or whether the schema-level flag becomes
  conditional. Until then, leg 2 rests on a licence rather than a settled rule — stated plainly
  rather than smoothed.
- **NJ-FW-3 — the reciprocal edge target for code is ambiguous, because `code.software-project` is
  a REFUSED row** and the surviving activation is the code schema's default. Rule 14 forces a
  template to name a template id, which is what I did. R1c should decide whether a refused template
  may carry a reciprocal edge, or whether this collision must be re-pointed at the `code` schema
  row from `engineering.json`'s side. **Recommendation only; I touched neither file.**
- **NJ-FW-4 — which residual owns a downloaded vendor firmware update.** This row routes
  `DIR-865L_REVA_FIRMWARE_1.08.B01.bin` to **Review Later**, because whether it is a retained
  device asset or download detritus cannot be settled from its own evidence. The alternative is
  **Independent Records**, if a kept update for a device the holder owns counts as "a durable
  purpose but no broader group". Confirm, or invert.
