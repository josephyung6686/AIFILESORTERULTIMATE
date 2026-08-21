# 08 — Software, technology and digital work

_Domain catalogue slice. Conforms to [`_CONTRACT.md`](_CONTRACT.md)._

- **supercategory**: `software-technology`
- **version**: 1.0
- **authored**: 2026-08-21
- **entries**: 40 — 2 `design`, 11 `inference`, 27 `proposal`
- **source of truth**: [`00-database-agent-product-design.md`](../00-database-agent-product-design.md). Every quotation in this file was checked verbatim against it.
- **consumer**: P6 owns the fact-schema half of every entry (P6 SPEC: "P6 owns the fact schema half; P10 owns the folder template half"); the P6/P8 validator enforces the schema as an allow-list under §4.8 "each fact or label belongs to an allowed domain schema"; P10 draws branch proposals from the `template` half under §5.3 "proposes one or more domain templates based on the groups and facts that already belong inside it"

## What this file is

A slice of the domain catalogue covering software, technology and digital work. Per the contract, a domain here is a SCHEMA (which fact fields are legal) plus a TEMPLATE (how its branch is shaped). It is the allow-list the validator enforces, not a listing exercise.

Read the provenance column before reading anything else. §3.11 "Code files may use project, repository, programming language, and artifact type." is the ONLY sentence in the design that gives this whole supercategory a fact schema, and §3.15 "The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects." is the only one that makes it a launch domain. Everything past those two sentences is marked `inference` or `proposal` and is a request for a decision, not an assertion.

## Standing rules

1. **No field here exists yet.** §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." and P6 SPEC restates it: "Fields: authored schema changes and user-approved schema changes only - never runtime, never the LLM." Every field below beyond §3.11's four literal Code fields is therefore a PROPOSED authored schema change for Joseph to accept or reject. The catalogue proposes; it does not create.

2. **Recognition is pattern PLUS corroborating context, never bare.** The model is the design's own: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context", and §3.13 "A validated fact was found by a deterministic rule and passed contextual checks". Every `recognition.deterministic` row in this file names both halves. A row that named only a pattern would be claiming `validated` for something a rule cannot confirm, which contract rule 4 forbids.

3. **The repository-marker list is not re-derived here.** It is authored, in `planning/deferred-catalogues/05-repository-markers.json`, as `p3_exclusion_roots` (four rows) and `p5_evidence_markers` (many rows across four kinds). Every entry in this file that needs a marker CITES a row id from that file. No filename, extension or directory name is introduced here. A second copy of that list is the defect this rule exists to prevent.

4. **No numbers.** No thresholds, no severity scales, no confidence scores, no counts. Where a co-occurrence is required it is written as "together with", which is the design's own phrasing.

5. **No handling classes.** `sensitivity` carries §2.9's phrase `potentially_sensitive` and stops. §8.4 "The system should classify data into handling classes before LLM escalation" -- those classes, the escalation gate, and the redaction policy are P7's under §8.4 and are never set here. The entries whose CONTENT is credentials (`soft.configuration-and-secrets`, `soft.security-finding-report`, `soft.monitoring-log-export`) are exactly the cases where that gate matters most, which is a reason to mark and stop, not a reason to decide.

## The root signal — the one deterministic pattern this slice is built on

> a catalogue-05 `p5_evidence_markers` row matching at a directory root (kind `package manifest` or `repository marker`) TOGETHER WITH a sibling or descendant file whose extension routes to the structured-text extractor

The single deterministic signal this slice is built on, stated once and referenced by name from every entry that uses it. It is pattern PLUS corroborating context in the design's own shape - §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" -- and neither half is decisive alone: a marker without a source sibling is a stray config file, and a source sibling without a marker is exactly what §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." refuses to reason from. The marker rows come from `planning/deferred-catalogues/05-repository-markers.json`; none is restated here.

## `never_alone` — universal to every entry

These four apply to EVERY entry in this slice and are abbreviated inside each entry's `recognition.never_alone` as `[universal] ...`. The full reasoning lives here so it is stated once and cannot drift between entries.

| signal | why it is never enough alone |
|---|---|
| a bare file extension | `.js`, `.py`, `.json`, `.yml`, `.sql`, `.tf` name a FORMAT, not a domain. §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning" -- a routing signal is not a conclusion, and §2.1 "filenames alone are too weak for real personal corpora" |
| a bare camelCase or snake_case identifier token in running text | §3.7 "It should use word-boundary matching rather than substring matching." An identifier-shaped token is the substring hazard that rule exists for: the design's own examples are MIT inside 'submit' and UNC inside 'uncertainty', and a code identifier is worse, because it is DESIGNED to be a concatenation of ordinary words. |
| a bare version-shaped or number-shaped string | §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." -- the design names version numbers and build numbers literally as the tokens that must not be trusted, and this supercategory is where they are densest. |
| a lock file on its own | Catalogue 05 `unc-lockfiles-as-exclusion` records that a lock file is "machine-generated and never hand-authored". That makes it strong evidence about a ROOT and no evidence at all about authored content - the authored/generated split in one row, already on the record in this repo. |

## Authored vs. generated — the policy for this whole slice

Code corpora are mostly not authored. A template that files generated, vendored and dependency output by project is worse than no template: it produces branches that look populated and are not the user's work. Every entry in this file therefore carries an `authored_vs_generated` block naming, for that domain, what a person wrote and what a machine emitted.

| Layer | Mechanism | What it covers | What it does NOT cover |
|---|---|---|---|
| **1. Scan-time directory exclusion (P3)** | §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees." | The bulk of dependency and build output, WHERE it sits under one of those literal names. Those files never become file records at all, so no domain can file them. | Generated files that sit beside authored ones rather than in a directory of their own: notebook stored outputs, database schema snapshots, infrastructure state files, game-engine per-asset import metadata, generated API reference markdown, vendored manufacturer SDKs. |
| **2. Scan-time project-root exclusion (P3)** | §1.1 "It should also reject descendants of software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or go.mod. This prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal destination." | Everything below a root marked by one of those four names. | Every other ecosystem. Catalogue 05 deliberately refused to extend the list - `unc-pyproject-as-exclusion` ("the default answer this file ships with is no"), `unc-lockfiles-as-exclusion`, `unc-other-ecosystems-as-exclusion`. **This is the asymmetry that shapes the whole slice:** a Node, pip, Cargo or Go project enters the corpus as a thin shell of root-level documents, while a pyproject-only Python project, a Gradle or Maven project, or a Ruby, PHP, Elixir or Dart project enters WHOLE. Two projects of the same kind can therefore be visible to completely different degrees, and no template can assume either case. |
| **3. Root-anchored recognition (this catalogue)** | §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." | A file does not activate a software domain on its own extension. It inherits membership from a marker-bearing root above it. A stray generated file with no marker root in its ancestry activates nothing, which is the correct outcome. This is why every `never_alone` list in this file begins with bare extensions. | Generated files INSIDE an admitted project tree, which do have a marker root above them and therefore do inherit membership. |
| **4. Project-scale dimensions (this catalogue)** | Every template here uses project-scale dimensions - `project` then `artifact_type` - and never a per-file or per-run dimension. Branch count therefore tracks the number of PROJECTS, not the number of files. A generated file inside an admitted tree lands as a member under its project's branch, which is right, rather than creating a branch of its own, which would not be. The fields that would fragment a tree - `run`, `release_version`, `interface_version`, `environment` - are held as metadata, which §5.4 "It defines the dimensions that are meaningful for one type of material, their recommended order, which dimensions are optional, which ones are metadata only, and what safety or usability constraints apply." explicitly provides for. | The layer-2 gap. It is the only layer that works on a fully admitted tree. | It bounds the number of branches, not the number of files inside one. A project branch can still contain an enormous generated subtree; it just does not shatter the tree. |
| **5. Template-time and canvas-time validation (P10)** | §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." and, before the user commits, §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." with §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." | The user sees what a split would cost before choosing it, and after freeze §5.11's tree health shows where files are unresolved. | It is a review surface, not a filter. It makes a bad template visible; it does not make a good one. |
| **6. Anchor discipline (P9)** | §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." -- a generated file may join a group but must never be the anchor that creates one. Stated per entry wherever a domain has a high-volume generated class (ML run records, eval scored outputs, performance result sets, pipeline run logs, automated dependency alerts, notification messages). | Prevents a branch existing BECAUSE of generated bulk. | Nothing about where those files then go. |

### The gap, and one proposal

Layers 1 and 2 are scan-time and uneven. Layers 3 to 6 bound the DAMAGE without identifying the files. Nothing in the design identifies a generated file that sits beside an authored one inside an admitted tree - and by the entries in this file, that is the common case: generated API reference markdown, notebook stored outputs, schema snapshots, infrastructure state, engine import metadata, generated clients.

**Proposal, for Joseph, not adopted here.** The design already has the shape of the answer for a different problem: §2.2 "a value such as python-docx, Mozilla/5.0, or a browser-generated producer string should not be mistaken for meaningful content.". A tool-emitted string is not content. Generated source files carry the same class of marker - a do-not-edit / generated-by banner written by the generator into the head of the file. A small authored catalogue of those banner shapes would give the product one deterministic, content-position-based signal for authored-versus-generated, and it would sit naturally beside catalogue 01 (tool producer strings), which already exists for the metadata equivalent. It is NOT authored here: it would be a new deferred catalogue with its own owner, and whether P5 emits it as an observation or P6 derives it as a universal fact is a boundary question this file has no standing to settle. See the supercategory open questions.

### What this catalogue refuses to do

- It does not add any name to `p3_exclusion_roots`. That array is destructive - catalogue 05: "A wrong entry in `p3_exclusion_roots` makes real user files invisible to the entire product" - and §1.1's four are the only ones the design settles.
- It does not add any name to `p5_evidence_markers` either. Where an entry needs a marker class catalogue 05 lacks (game-engine project files, embedded linker scripts, diagram-tool formats), it says so and stops, and the addition is recorded as an open question against catalogue 05.
- It does not define a vulnerability-name or credential-name pattern. Catalogue 06 refuses the equivalent for government and payment identifiers because such a list "creates the exposure it would then have to protect"; the same reasoning holds here.

## Cross-slice note

Several entries name domains owned by other slices in `collides_with` - `res.*` (research), `acad.*` (academic), `fin.*` (finance), `law.*` (legal), `career.*`, `design.*`, `pm.*`. Those ids are written in the expected form so the collisions are reviewable; this slice does not own them and does not assert their schemas. §3.11 "One file may hold facts from more than one domain without losing information." -- so a file carrying both is the designed outcome, not a conflict to resolve. What must be resolved is which domain's TEMPLATE gets to place the file, and that is P11's under §6.

## Supercategory open questions

Copy these into `NEEDS-JOSEPH.md` unresolved.

1. §5.4 gives folder templates for Academic, Applications, Research, Career and Photos and gives NO Code row - yet §3.11 "Code files may use project, repository, programming language, and artifact type." gives Code a fact schema and §3.15 "The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects." makes code projects a launch domain. What are the Code template's folder dimensions and their order? Every template in this file proposes `project -> artifact type` and asserts none of it.
2. P3 SPEC Open Question 9, carried in catalogue 05 as `unc-p3-oq9`: "Does the project-root rule exclude the root directory itself, or only its descendants?" The answer decides whether a Node or Cargo project appears in `soft.source-project` as a thin shell of root-level documents or does not appear at all. This slice's most consequential unresolved dependency.
3. Should there be an authored catalogue of generated-file banner shapes, so the product can distinguish a generated source file from an authored one inside an admitted tree? §2.2 "a value such as python-docx, Mozilla/5.0, or a browser-generated producer string should not be mistaken for meaningful content." establishes the principle for metadata; nothing establishes it for file content. If yes, who owns it - P5 as an observation, or P6 as a universal fact alongside §2.9's duplicate and version-family signals?
4. Is `severity` a field this product should have? The brief proposes it for incidents, and it is conventional for security findings too. NO design sentence supplies a severity vocabulary, scale or set of levels anywhere, and §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically.". It is omitted from `soft.incident-postmortem` and `soft.security-finding-report` rather than invented. If Joseph wants one, a single authored vocabulary should serve both.
5. Game-engine import-cache directories, dotfile plugin directories and vendored manufacturer SDKs are generated or third-party bulk that §1.1's eleven literal directory names do not cover and §1.1's four project-root markers do not reach. Should the exclusion mechanism be extended to them? That is P3's and Joseph's; any addition would live in catalogue 05, which already refuses to extend `p3_exclusion_roots` on its own authority.
6. Should `soft.configuration-and-secrets` record even the SHAPE observation that a file appears to hold credential material? §8.4 "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local." -- and a domain whose content is secrets is exactly where §8.4's gate matters. The gate is P7's; whether the observation may be made at all is prior to it.
7. Three cross-slice ownership questions this file records and does not resolve: analysis code and notebooks that are also research artifacts (research slice); notebooks that are also coursework (academic slice); compliance evidence, IT asset inventories and helpdesk tickets that may belong under an administrative, legal or career branch rather than a software one. §5.1 "a typical initial canvas might include Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material."
8. Are `soft.design-doc-rfc` and `soft.technical-specification` one domain? They share every field and differ only in the document's intent, which is prose. Same question for `soft.security-finding-report` and `soft.vulnerability-disclosure`, which differ only in whose system the weakness is in - a role distinction §3.8 "The system must separate roles that happen to contain the same entity type." supports, but a thin one.
9. Is `soft.sdk-integration` a domain at all, or a VALUE of `artifact_type` inside `soft.source-project`? Its discriminating field, `integration_direction`, has an `llm_supported` ceiling, which means the domain has almost no deterministic existence.
10. Should a personal dotfiles directory be organised by this product at all? §1.1 "The system should also know that existing folder structures should mainly be preserved. For example, if a folder called AIKonic Project has a lot of files such as JSON and other software material, those are probably not supposed to be touched." and §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." both point toward recognising it and leaving it untouched. That is a decision about someone's real working setup.

---

## Entries at a glance

| # | id | name | provenance | sensitivity | template | open question? |
|---|---|---|---|---|---|---|
| 1 | `soft.source-project` | Application source project | `design` | `none` | `project` → `artifact_type` | yes |
| 2 | `soft.library-package` | Library or package intended for distribution | `inference` | `none` | `project` → `artifact_type` | — |
| 3 | `soft.infrastructure-as-code` | Infrastructure as code | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 4 | `soft.configuration-and-secrets` | Configuration and secrets management | `inference` | `potentially_sensitive` | `project` → `artifact_type` | yes |
| 5 | `soft.ci-cd-definition` | Continuous integration and delivery definitions | `inference` | `none` | `project` → `artifact_type` | — |
| 6 | `soft.container-deployment` | Container and deployment artifacts | `inference` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 7 | `soft.database-schema-migration` | Database schemas and migrations | `inference` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 8 | `soft.api-specification` | API specifications and interface contracts | `proposal` | `none` | `project` → `artifact_type` | — |
| 9 | `soft.sdk-integration` | SDK and third-party integration work | `proposal` | `none` | `project` → `artifact_type` | yes |
| 10 | `soft.data-pipeline` | Data pipelines and scheduled jobs | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 11 | `soft.notebook-analysis` | Computational notebooks and exploratory analysis | `design` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 12 | `soft.ml-experiment` | Machine-learning experiments and runs | `proposal` | `potentially_sensitive` | `project` → `experiment` | yes |
| 13 | `soft.dataset-artifact` | Datasets held as files | `inference` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 14 | `soft.model-artifact` | Trained model files and checkpoints | `proposal` | `none` | `project` → `artifact_type` | yes |
| 15 | `soft.prompt-eval-asset` | Prompt and evaluation assets | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 16 | `soft.design-doc-rfc` | Design documents and RFCs | `proposal` | `none` | `project` → `artifact_type` | yes |
| 17 | `soft.architecture-decision-record` | Architecture decision records | `proposal` | `none` | `project` → `artifact_type` | — |
| 18 | `soft.technical-specification` | Technical specifications | `proposal` | `none` | `project` → `artifact_type` | — |
| 19 | `soft.issue-ticket-export` | Issue and ticket exports | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 20 | `soft.code-review-artifact` | Code review artifacts | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 21 | `soft.release-notes-changelog` | Release notes and changelogs | `inference` | `none` | `project` → `artifact_type` | — |
| 22 | `soft.incident-postmortem` | Incident and postmortem records | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | yes |
| 23 | `soft.runbook-operational-doc` | Runbooks and operational documentation | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 24 | `soft.monitoring-log-export` | Monitoring and log exports | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 25 | `soft.performance-load-test` | Performance and load testing | `proposal` | `none` | `project` → `artifact_type` | — |
| 26 | `soft.security-finding-report` | Security findings and penetration test reports | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | yes |
| 27 | `soft.vulnerability-disclosure` | Vulnerability disclosures and advisories | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 28 | `soft.tech-compliance-evidence` | Compliance evidence for technical controls | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 29 | `soft.licence-oss-compliance` | Licences and open-source compliance | `inference` | `none` | `project` → `artifact_type` | — |
| 30 | `soft.dev-environment-setup` | Developer environment setup | `inference` | `none` | `project` → `artifact_type` | — |
| 31 | `soft.personal-dotfiles` | Personal dotfiles and shell configuration | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | yes |
| 32 | `soft.scratch-prototype` | Scratch and prototype work | `proposal` | `none` | `project` → `artifact_type` | — |
| 33 | `soft.game-development-asset` | Game development projects and assets | `proposal` | `none` | `project` → `artifact_type` | yes |
| 34 | `soft.embedded-firmware` | Embedded and firmware projects | `proposal` | `none` | `project` → `artifact_type` | — |
| 35 | `soft.hardware-design-file` | Hardware design files | `inference` | `none` | `project` → `artifact_type` | — |
| 36 | `soft.network-diagram` | Network and system diagrams | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 37 | `soft.it-asset-inventory` | IT asset and inventory records | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 38 | `soft.helpdesk-ticket` | Helpdesk and support tickets | `proposal` | `potentially_sensitive` | `project` → `artifact_type` | — |
| 39 | `soft.user-documentation` | User-facing documentation | `inference` | `none` | `project` → `artifact_type` | — |
| 40 | `soft.training-material` | Technical training and teaching material | `proposal` | `none` | `project` → `artifact_type` | — |

---

## Entries in full

### 1. `soft.source-project` — Application source project

A directory a person authored as one piece of running software, marked as a project root and holding their own source files.

- **provenance**: `design`
- **design cite**: §3.11 "Code files may use project, repository, programming language, and artifact type." | §3.15 "The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects." names code projects a launch domain. | §2.5 "A source-code archive may reveal a README.md, package.json, src directory, or Python package layout and can be recognized as a code project." | §5.1 "a typical initial canvas might include Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material." names Code and Projects as a top-level branch.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to source text as such. A project root that also holds credential material is `soft.configuration-and-secrets`, a separate entry, so this one stays `none` rather than inheriting a neighbour's exposure.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `repository` | string | AIFILESORTERULTIMATE | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `repository` is literal. Populated from the directory name that carries the version-control marker (catalogue 05 `p5r-git`, `p5r-hg`, `p5r-svn`), not from any string inside a source file. |
| `programming_language` | string | Python | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `artifact_type` | string | application | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |
| `component` | string | extractors | `possible` | NO design sentence names a `component` field. It is a PROPOSED authored schema addition; §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." -- so it can only ever arrive as an authored or user-approved schema change, never at runtime. Ceiling `possible` and not higher for a reason specific to this slice: a component lives in a SUBDIRECTORY, and §1.1 "It should also reject descendants of software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or go.mod. This prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal destination." means that for a project marked by one of those four names the subdirectories are never scanned, so the field is unpopulated exactly where the domain is strongest. See `open_question`. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 `p5_evidence_markers` row matching at a directory root (kind `package manifest` or `repository marker`) TOGETHER WITH a sibling or descendant file whose extension routes to the structured-text extractor -- this is the cleanest deterministic signal in the whole catalogue, and it is clean because neither half is decisive alone: the marker without a source sibling is a stray config file, and the source sibling without the marker is §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text."<br><br>• an archive member listing that satisfies the same pairing without unpacking: §2.5 "A source-code archive may reveal a README.md, package.json, src directory, or Python package layout and can be recognized as a code project." -- and §2.5 "the normal scan should never extract archive contents to the filesystem"<br><br>• a version-control marker directory (catalogue 05 `p5r-git`) at the same root as a package manifest row, which pairs two independent marker CLASSES rather than one repeated one |
| **needs LLM** | • whether a directory of loose scripts with no manifest and no version-control marker is one project or several unrelated files - there is no structural signal, only prose in the files<br><br>• which of several sibling directories is the project and which are its siblings' support material, where the user's own folder naming is the only evidence |
| **never alone** | • a `src` directory name alone (catalogue 05 `p5r-src`) - the bare word is ordinary English and catalogue 05 already carries it as evidence, not as proof<br><br>• a README alone; a README marks a directory a person wrote ABOUT, which is many things besides software<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `source file`, `package manifest`, `README`, `build script`, `test suite`, `configuration file`, `changelog`, `licence`

**Grouping reasons**: one project across its files; one project across its versions and forks; a project and the archive that contains a snapshot of it

**Template**: `project` → `artifact_type` — time first: `false`

> §5.5 "a parent dimension should provide the context required to understand the child" -- an artifact type such as a test suite is meaningless until the project is known. §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." so no year level. The order is a PROPOSAL, not a design statement: §5.4 lists Academic, Applications, Research, Career and Photos templates and gives no Code row, so the Code template's dimensions are unauthored. See the supercategory open question.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • source files the person typed<br>• the README they wrote<br>• the manifest they hand-edited (dependency names and version constraints are a human choice)<br>• build scripts<br>• tests<br>• the changelog |
| **generated / not authored** | • everything under §1.1's eleven literal directory names - §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees."<br>• lock files, which catalogue 05 itself calls machine-generated and never hand-authored<br>• compiled output, minified bundles, generated API clients, generated migrations and snapshot fixtures that happen to sit OUTSIDE a directory §1.1 names<br>• vendored third-party source copied into the tree under a name §1.1 does not list |
| **template guard** | Three layers, in order. (a) §1.1 "It should also reject descendants of software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or go.mod. This prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal destination." removes the dependency bulk before scanning, but ONLY for those four marker names - catalogue 05's `unc-pyproject-as-exclusion`, `unc-lockfiles-as-exclusion` and `unc-other-ecosystems-as-exclusion` deliberately refused to extend the list, so a pyproject-only Python project, a Gradle project or a Ruby project enters WHOLE. (b) For those, the guard is that this template's dimensions are `project` and `artifact_type` only - both project-scale - so the branch count tracks the number of projects, not the number of files. A generated file inside an admitted tree lands under its project's branch as a member, which is correct, rather than creating a branch of its own, which would not be. (c) §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." - the user sees what the split would cost before committing to it. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.library-package` | both carry a package manifest; only a library declares itself publishable and names a distribution registry, and only an application declares an entry point or a deployment target | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.scratch-prototype` | both are authored code; a prototype has no licence, no changelog, no CI definition and usually no version-control marker | §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |
| `res.analysis-code` | analysis code written for a paper is a research artifact first; the research slice owns it when a manuscript, dataset or lab fact is present at the same root. Ownership is a genuine cross-slice question, recorded not resolved | §3.11 "One file may hold facts from more than one domain without losing information." |

**Open question** — Joseph's, unresolved.

> §5.4 gives templates for Academic, Applications, Research, Career and Photos and gives NO Code row, yet §3.11 gives Code a fact schema and §3.15 names code projects a launch domain. What are the Code template's folder dimensions and their order? This catalogue proposes `project -> artifact type` and does not assert it. Related and also Joseph's: P3 SPEC Open Question 9 (carried in catalogue 05 as `unc-p3-oq9`) asks whether the marker-bearing directory itself is excluded or only its descendants. The answer decides whether a Node or Cargo project appears in this domain as a thin shell of root documents or does not appear at all.

---

### 2. `soft.library-package` — Library or package intended for distribution

Code authored to be consumed by other code, declaring itself publishable to a package registry.

- **provenance**: `inference`
- **design cite**: Extends §3.11 "Code files may use project, repository, programming language, and artifact type." -- a library is a value of the literal `artifact_type` field, not a new domain's worth of fields. No design sentence distinguishes a library from an application; the split is proposed here because their templates differ (a library has a version series a user may want as a level, an application does not).
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | plasmole-sdk | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `repository` | string | AIFILESORTERULTIMATE | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `repository` is literal. Populated from the directory name that carries the version-control marker (catalogue 05 `p5r-git`, `p5r-hg`, `p5r-svn`), not from any string inside a source file. |
| `programming_language` | string | Python | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `artifact_type` | string | library | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |
| `distribution_name` | string | plasmole-sdk | `validated` | NO design sentence names this field. Proposed. Validated is claimable because the value is read from a named key in a manifest catalogue 05 already recognises - a labelled field in a structured file, which is §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." territory; it is kept at `validated` rather than `direct` because the RULE that the manifest is a manifest is what licenses it. |
| `release_version` | string | v2.1.0 | `possible` | NO design sentence names this field, and §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." is the reason its ceiling is `possible`: a version-shaped string is the exact class of token that rule refuses to trust alone. Metadata only - see the template note. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 `p5_evidence_markers` row matching at a directory root (kind `package manifest` or `repository marker`) TOGETHER WITH a sibling or descendant file whose extension routes to the structured-text extractor, TOGETHER WITH a publish-oriented key present in the manifest (a distribution name and a version declared in the same manifest object)<br><br>• a manifest whose own filename is a distribution manifest rather than an application one - catalogue 05's `p5m-package-swift`, `p5m-pyproject-toml`, `p5m-cargo-toml` rows are the recognisers; this catalogue adds no filenames of its own |
| **needs LLM** | • whether a repository containing both an application and its extracted library is one project or two, when only prose in the README says so |
| **never alone** | • a distribution name that is also an ordinary English word, with no manifest around it<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `package manifest`, `public API surface`, `changelog`, `licence`, `release notes`, `usage documentation`

**Grouping reasons**: one library across its released versions; a library and the applications that vendor it

**Template**: `project` → `artifact_type` — time first: `false`

> Same order and same reasoning as `soft.source-project`. `release_version` is deliberately NOT a dimension: a version level is the textbook case of §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." -- it produces a large number of tiny folders. It stays metadata, which §5.4 "It defines the dimensions that are meaningful for one type of material, their recommended order, which dimensions are optional, which ones are metadata only, and what safety or usability constraints apply." explicitly provides for. PROPOSED, not design.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the public API the author designed<br>• the usage documentation<br>• the changelog<br>• the version constraints in the manifest |
| **generated / not authored** | • built wheels, tarballs, jars and bundles under `build`, `dist` or `target` - all three are §1.1 literal names<br>• generated API reference pages produced from docstrings<br>• lock files |
| **template guard** | Identical to `soft.source-project`, plus one specific to distribution: a downloaded THIRD-PARTY package sitting in the user's corpus is not their library. The discriminator is the version-control marker and authorship of the README, not the manifest, because a downloaded package has a manifest too. Where that cannot be settled structurally the entry must not fire - §3.6 "A model that cannot cite sufficient evidence must return unknown." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.source-project` | the publishable declaration is the discriminator; without it the project is an application | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.sdk-integration` | a library you PUBLISH versus a vendor SDK you CONSUME - the same manifest keys read in opposite directions, which is exactly the role confusion §3.8 "The system must separate roles that happen to contain the same entity type." | §3.8 "The system must separate roles that happen to contain the same entity type." |

---

### 3. `soft.infrastructure-as-code` — Infrastructure as code

Declarative files that describe cloud or server infrastructure so it can be created from the file rather than by hand.

- **provenance**: `proposal`
- **design cite**: NO design sentence names infrastructure as code. Proposed. The nearest design anchor is §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." which routes YAML, JSON and structured data to an extractor - that is a format statement, not a domain statement, and it is not cited here as one.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally, not by default: an infrastructure file that inlines an endpoint, account identifier or key is credential-bearing material, and §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. names credentials in the corpus this product processes. This catalogue marks and stops. The handling class and the escalation gate are P7's under §8.4 and are NOT set here.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | prod-platform | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `environment` | string | staging | `possible` | NO design sentence names this field. Proposed. `possible` because an environment name is a bare ordinary word (`prod`, `staging`, `dev`) and §3.7 "It should use word-boundary matching rather than substring matching." is precisely the hazard: `dev` is a substring of a great many things. |
| `provider` | string | AWS | `possible` | NO design sentence names this field. Proposed. A provider name is an ORGANISATION name, and §3.8 "It should avoid using authorship or creator identity as a destination dimension." - it is metadata here and never a folder level. |
| `artifact_type` | string | infrastructure module | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- reusing the literal Code field rather than minting a parallel one. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 `p5_evidence_markers` row matching at a directory root (kind `package manifest` or `repository marker`) TOGETHER WITH a sibling or descendant file whose extension routes to the structured-text extractor where the sibling files are declarative rather than executable, TOGETHER WITH a state or lock artifact of the same tool at the same root<br><br>• a repository marker root TOGETHER WITH a container or orchestration definition catalogue 05 already recognises (`p5r-dockerfile`, `p5r-docker-compose-yml`, `p5m-chart-yaml`) |
| **needs LLM** | • whether a directory of YAML is infrastructure, a CI definition, or application configuration - all three are YAML at a repository root and the discriminator is what the keys MEAN<br><br>• whether an environment name in a filename refers to a deployment environment or to a person's own naming habit |
| **never alone** | • a provider's name appearing in prose<br><br>• an environment word with no infrastructure file around it<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `infrastructure module`, `environment definition`, `policy document`, `state file`, `provisioning script`

**Grouping reasons**: one platform across its environments; one migration of infrastructure across its files

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. `environment` is deliberately not a dimension: environment names are few and repeat across every project, so leading with them is the §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." failure mode of using a shared label as a collector. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the declarations a person wrote<br>• the module structure they chose<br>• the policy documents |
| **generated / not authored** | • state files, which are tool-written snapshots of reality and are regenerated, not authored<br>• generated provider lock files<br>• rendered manifests produced from a template at deploy time |
| **template guard** | State files are the specific hazard here: they are large, machine-written, sit beside the authored declarations, and are NOT covered by any §1.1 literal name. The guard is the same project-scale dimension rule - they land under their project as members and never create a branch - plus §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." before commit. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.configuration-and-secrets` | infrastructure code DESCRIBES resources; a secrets file HOLDS a credential. When one file does both, the sensitive entry wins the handling question and P7 decides it | §8.4 "A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately." |
| `soft.ci-cd-definition` | a CI definition runs ON a commit; infrastructure code declares a resource. Both are YAML at a repository root and this is the weakest boundary in the entry | §3.3 "have multiple plausible domains" |

---

### 4. `soft.configuration-and-secrets` — Configuration and secrets management

Files whose job is to hold settings or credentials for software - recognised by SHAPE only, never by reading the values.

- **provenance**: `inference`
- **design cite**: Extends §2.4 "Text-bearing files such as Markdown, plain text, JSON, CSV, source code, notebooks, and configuration files should be handled through a lighter structured-text extractor." which names configuration files as an extractor class, and §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." which names JSON, YAML, TOML and XML. Neither sentence makes configuration a DOMAIN; the domain is the inference. The sensitivity half is anchored: §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies to this domain more directly than to any other in the slice. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. names credentials among what this product processes, and §8.4 "A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately." This catalogue marks and stops. A domain whose CONTENT is secrets is exactly the case where §8.4's escalation gate matters - §8.4 "Protected material should not be included in cloud-model prompts by default" -- and that gate, the handling class, and the redaction policy are P7's, not this catalogue's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `config_scope` | string | application settings | `possible` | NO design sentence names this field. Proposed. `possible` and no higher: distinguishing application settings from tool settings from machine settings requires reading keys, and this entry's whole discipline is that it recognises shape and stops. |
| `format` | string | TOML | `direct` | §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." names the formats literally. `direct` because the format is read from the file signature or extension route, which §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |
| `holds_credential_material` | boolean | true | `possible` | NO design sentence names this field, and it is the only one in the catalogue that must NEVER record what it found. It records THAT credential-shaped material is present, never the value. §8.4 "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local." Ceiling `possible` deliberately: a stronger state would license the product to act on a claim it can only make by reading the secret. See `open_question`. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a configuration filename catalogue 05 already recognises at a repository-marker root - the entry adds no filename list of its own and MUST NOT, because a filename list for secrets is a map of where to look<br><br>• a structured-text file at a project root whose top-level keys are settings-shaped, TOGETHER WITH the root signal - pattern plus corroborating context per §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" |
| **needs LLM** | • whether a `.env`-shaped file is a project's configuration or a person's own shell environment - the discriminator is where it sits and who wrote it, not what it contains<br><br>• whether a settings file belongs to the project it sits in or was copied there from elsewhere |
| **never alone** | • a key-shaped string on its own - matching one would mean extracting the secret, which §8.4 "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local." forbids as a starting posture<br><br>• a filename containing the word `config`, which is ordinary English<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `application configuration`, `environment file`, `credential store reference`, `key material`, `certificate`, `tool settings`

**Grouping reasons**: one project's configuration across its environments; configuration that travels with a project rather than with a machine

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. Configuration is a leaf under its project, never a top-level area, because a configuration branch collects files that share a FORM rather than a purpose - §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." §3.9 "Purpose must be a first-class facet."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the settings a person chose<br>• the schema and key names they defined<br>• the example or template file they committed for other people to copy |
| **generated / not authored** | • generated configuration rendered from a template at build or deploy time<br>• credential caches and token files written by a tool, not typed by a person<br>• editor and IDE settings written automatically |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. One addition specific to this entry: a generated config carries no authored intent, so it should reach at most §3.13 "A possible fact is a useful but insufficient clue, such as membership in a short download session or a low-confidence semantic match." and must never anchor a group - §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.personal-dotfiles` | a config file that is also a personal dotfile is the brief's named collision. The discriminator is location and ownership: inside a project root it configures the project; in the home directory it configures the person. §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." | §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." |
| `soft.infrastructure-as-code` | declaring a resource versus configuring a running program | §3.3 "have multiple plausible domains" |

**Open question** — Joseph's, unresolved.

> This entry deliberately records SHAPE and never content. Two things follow that are not this catalogue's to decide. First: may an extractor record that a file appears to hold credential material at all, given §8.4 "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive values should remain local." ? Second: §8.4's handling classes are named but not assigned by this catalogue - which class a configuration file holding a live key receives, and whether the file is eligible for any model call, is P7's under §8.4.

---

### 5. `soft.ci-cd-definition` — Continuous integration and delivery definitions

Files that tell an automation service what to run when a repository changes.

- **provenance**: `inference`
- **design cite**: Extends catalogue 05, which already carries the CI recognisers as `repository marker` rows (`p5r-github`, `p5r-gitlab-ci-yml`, `p5r-travis-yml`, `p5r-azure-pipelines-yml`, `p5r-jenkinsfile`, `p5r-circleci`) under §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" -- so the recognisers are cited, not re-derived. Making them a DOMAIN is the inference.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to the definition itself. A pipeline file that inlines a credential is `soft.configuration-and-secrets` material and is marked there.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `repository` | string | AIFILESORTERULTIMATE | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `repository` is literal. Populated from the directory name that carries the version-control marker (catalogue 05 `p5r-git`, `p5r-hg`, `p5r-svn`), not from any string inside a source file. |
| `automation_service` | string | GitHub Actions | `validated` | NO design sentence names this field. Proposed. `validated` is claimable because the value follows deterministically from WHICH catalogue-05 marker matched - the marker names the service - which is a rule passing a contextual check, §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" |
| `artifact_type` | string | pipeline definition | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 CI `repository marker` row at a directory root TOGETHER WITH the root signal - the CI file alone would match a copied snippet, and the pairing is what §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" |
| **needs LLM** | • whether a pipeline definition is the project's own or a template someone saved for reference |
| **never alone** | • a YAML file with job-shaped keys and no repository marker anywhere above it<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `pipeline definition`, `workflow file`, `build script`, `release workflow`, `reusable action`

**Grouping reasons**: one project's pipelines across its services

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. CI definitions are leaves under their project. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the pipeline steps a person wrote<br>• the reusable actions they authored |
| **generated / not authored** | • build logs and run artifacts the service produces<br>• generated matrices and expanded workflows<br>• caches under names §1.1 already ignores |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.infrastructure-as-code` | a pipeline that provisions infrastructure sits in both; the discriminator is whether the file is triggered by a repository event or declares a resource | §3.3 "have multiple plausible domains" |

---

### 6. `soft.container-deployment` — Container and deployment artifacts

Files that describe how software is packaged into an image and placed onto a running system.

- **provenance**: `inference`
- **design cite**: Extends catalogue 05's container rows (`p5r-dockerfile`, `p5r-docker-compose-yml`, `p5r-docker-compose-yaml`, `p5r-dockerignore`, `p5m-chart-yaml`) held under §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" Making them a domain is the inference.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: deployment manifests routinely carry registry credentials and secret references. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped; the handling class is P7's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `deployment_target` | string | Kubernetes | `validated` | NO design sentence names this field. Proposed. `validated` because it follows from which catalogue-05 marker matched, §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" |
| `image_name` | string | graphify-api | `possible` | NO design sentence names this field. Proposed. `possible`: an image name is a bare identifier token and §3.7 "It should use word-boundary matching rather than substring matching." |
| `artifact_type` | string | container definition | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 container marker at a directory root TOGETHER WITH the root signal<br><br>• an orchestration chart manifest (`p5m-chart-yaml`) at a root TOGETHER WITH a sibling template directory of the same tool |
| **needs LLM** | • whether a compose file describes the user's own deployment or a third-party stack they ran once |
| **never alone** | • the word `docker` in a filename<br><br>• a bare image-name-shaped token<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `container definition`, `compose file`, `chart`, `deployment manifest`, `ignore file`

**Grouping reasons**: one service across its deployment artifacts; one stack across its component services

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the image definition a person wrote<br>• the compose or chart they hand-authored |
| **generated / not authored** | • rendered manifests produced from a chart<br>• image layers and build caches<br>• generated ignore files |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.infrastructure-as-code` | packaging and placement versus resource declaration; a chart of templated resources sits genuinely in both | §3.3 "have multiple plausible domains" |

---

### 7. `soft.database-schema-migration` — Database schemas and migrations

Files that define a database's structure and the ordered steps that changed it.

- **provenance**: `inference`
- **design cite**: Extends §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." which names SQL literally as a routed format. Making SQL a domain rather than a format is the inference.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: a schema file is structure and carries no personal data, but a seed or dump file can carry rows of it. The two share an extension. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `database_system` | string | PostgreSQL | `possible` | NO design sentence names this field. Proposed. `possible`: dialect is inferred from syntax, which is semantic analysis of code text - the thing §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." |
| `schema_object` | string | file_facts | `possible` | NO design sentence names this field. Proposed. `possible`: a table name is a bare identifier and §3.7 "It should use word-boundary matching rather than substring matching." |
| `artifact_type` | string | migration | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a migrations directory whose members share one ordered naming series, TOGETHER WITH the root signal - the SERIES is the corroborating context, and a single SQL file has none<br><br>• a schema-definition file at a project root TOGETHER WITH a manifest that declares a database dependency |
| **needs LLM** | • whether a `.sql` file is a schema definition, a one-off query someone saved, or an export<br><br>• whether a migration series belongs to this project or was copied from another |
| **never alone** | • a single `.sql` file with no series and no project root<br><br>• an ordered numeric prefix on its own; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `schema definition`, `migration`, `seed data`, `stored procedure`, `query`

**Grouping reasons**: one migration series in order; one schema across its versions

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. Migrations are ordered but the order is INSIDE the branch, not a folder level: a level per migration is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." 'a large number of tiny folders' exactly.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the DDL a person wrote<br>• the migration steps they ordered<br>• the seed fixtures they chose |
| **generated / not authored** | • schema snapshots regenerated by a tool after every migration<br>• dumps produced by an export command<br>• generated ORM model files |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. The schema-snapshot file is the specific hazard: it is rewritten on every migration, so it looks recently authored while being entirely machine-written. It is a member, never an anchor - §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.dataset-artifact` | a `.sql` dump of ROWS is data; a `.sql` file of DDL is schema. Both have the same extension and this is a real ambiguity | §3.3 "have multiple plausible domains" |

---

### 8. `soft.api-specification` — API specifications and interface contracts

A machine-readable description of an interface that other software is expected to call.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." which routes JSON, YAML and XML and names 'schema keys' as extractable structure - a format statement, cited as a format statement only.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `interface_name` | string | Placement API | `possible` | NO design sentence names this field. Proposed. `possible`. |
| `specification_format` | string | OpenAPI | `validated` | NO design sentence names this field. Proposed. `validated` is claimable because a specification declares its own format in a named top-level key, and a rule reading a declared key with the surrounding document present is §3.13 "A validated fact was found by a deterministic rule and passed contextual checks" |
| `interface_version` | string | v3 | `possible` | NO design sentence names this field. Proposed. §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `artifact_type` | string | interface specification | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a structured file declaring a specification format in a named top-level key, TOGETHER WITH the root signal or a sibling implementation file - §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." names schema keys as extractable structure, and the declared key plus the project context is the pattern-plus-context shape §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" |
| **needs LLM** | • whether a JSON schema file describes an API, a configuration format, or a data file<br><br>• whether the specification is the user's own interface or a vendor's, saved for reference |
| **never alone** | • a `.json` or `.yaml` extension<br><br>• the word `api` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `interface specification`, `schema definition`, `generated client`, `interface documentation`, `example request collection`

**Grouping reasons**: one interface across its versions; a specification and the implementation that serves it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child" `interface_version` stays metadata for the same reason `release_version` does in `soft.library-package`.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the interface a person designed<br>• the descriptions and examples they wrote |
| **generated / not authored** | • generated client and server stubs, which are the largest generated file class in this domain<br>• specifications emitted from code annotations at build time<br>• generated documentation sites |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Generated clients are the specific hazard and they are usually LARGE: one specification can emit many stub files in many languages. They must not each carry a `programming_language` fact that fragments the project - the language field is metadata here, never a dimension, which §5.4 "It defines the dimensions that are meaningful for one type of material, their recommended order, which dimensions are optional, which ones are metadata only, and what safety or usability constraints apply." provides for. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.sdk-integration` | a specification you PUBLISH versus one you CONSUME. Same file shape, opposite role - the collision §3.8 "The system must separate roles that happen to contain the same entity type." exists for. | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.technical-specification` | a machine-readable interface contract versus a prose specification a person reads | §3.3 "have multiple plausible domains" |

---

### 9. `soft.sdk-integration` — SDK and third-party integration work

Code and notes produced while wiring someone else's service into the user's own software.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. It is included because the brief's range names it and because it is the clearest worked case of §3.8 "The system must separate roles that happen to contain the same entity type."
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to integration code as such; the credential half sits in `soft.configuration-and-secrets`.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `integrated_service` | string | Snowflake | `possible` | NO design sentence names this field, and the value is an ORGANISATION name, so two design rules bear on it: §3.8 "It should avoid using authorship or creator identity as a destination dimension." keeps it out of the dimension order, and §3.7 "It should use word-boundary matching rather than substring matching." keeps a vendor name from being found inside ordinary words. |
| `integration_direction` | string | consuming | `llm_supported` | NO design sentence names this field. Proposed, and it is the field that MAKES this domain: whether the user publishes or consumes the interface. Structure cannot settle it - the same manifest keys appear either way - so the ceiling is `llm_supported`, which per §3.6 "The validator checks that the proposed field exists in the relevant domain schema" still requires validation and per §3.6 "A model that cannot cite sufficient evidence must return unknown." |
| `artifact_type` | string | integration | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a manifest declaring a named third-party client dependency TOGETHER WITH the root signal and a sibling source file - dependency declaration alone is not enough, because every project has dependencies |
| **needs LLM** | • the integration direction, as above<br><br>• whether a vendor name in a file means the user integrated with that vendor or merely mentioned it - the exact ambiguity §4.9 "members carry irreconcilable course, institution, project, term, or purpose facts" guards against for institutions |
| **never alone** | • a vendor or product name appearing anywhere in a file<br><br>• a dependency entry in a manifest with no code that calls it<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `integration code`, `credential configuration`, `vendor documentation`, `example script`, `integration test`

**Grouping reasons**: one integration across its code and notes

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and deliberately NOT `service -> project`: leading with the vendor is §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." using an organisation merely as a collector, which the template validator refuses. §3.8 "It should avoid using authorship or creator identity as a destination dimension."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the glue code a person wrote<br>• their notes on the vendor's behaviour<br>• their integration tests |
| **generated / not authored** | • vendored SDK source copied into the tree<br>• generated clients from the vendor's specification<br>• sample projects downloaded from the vendor |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Vendored SDK source is the specific hazard: it is another organisation's authored code sitting inside the user's tree, and unless it is under a §1.1 name such as `vendor` it is scanned. It must never anchor - §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.library-package` | publishing versus consuming, again | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.configuration-and-secrets` | integration work reliably produces credential files; those belong to the secrets entry and are marked there, not here | §8.4 "A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately." |

**Open question** — Joseph's, unresolved.

> This is the weakest entry in the slice and is recorded as such. Its discriminating field, `integration_direction`, has an `llm_supported` ceiling, which means the domain barely exists deterministically. Should it be a domain at all, or a VALUE of `artifact_type` inside `soft.source-project`? Joseph's call.

---

### 10. `soft.data-pipeline` — Data pipelines and scheduled jobs

Code that moves and reshapes data on a schedule rather than serving a user request.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." for the formats involved - cited as a format statement only.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: a pipeline's connection settings and sample rows can carry credential and personal material. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | etl-nightly | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `programming_language` | string | Python | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `pipeline_name` | string | nightly-facts-load | `possible` | NO design sentence names this field. Proposed. `possible`: a pipeline name is a bare identifier token, §3.7 "It should use word-boundary matching rather than substring matching." |
| `data_source` | string | Snowflake | `possible` | NO design sentence names this field. Proposed. An organisation or system name, so §3.8 "It should avoid using authorship or creator identity as a destination dimension." keeps it out of the dimension order. |
| `artifact_type` | string | pipeline | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a scheduler or orchestrator manifest at a directory root TOGETHER WITH the root signal and sibling task-shaped source files |
| **needs LLM** | • whether a script that reads and writes files is a pipeline, a one-off migration, or analysis code - the discriminator is whether it is SCHEDULED, which is usually stated only in prose |
| **never alone** | • a filename containing `etl`, `pipeline` or `job`<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `pipeline definition`, `task script`, `schedule definition`, `transformation`, `data contract`

**Grouping reasons**: one pipeline across its tasks; one data platform across its pipelines

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the transformations a person wrote<br>• the schedule they chose<br>• the data contracts they defined |
| **generated / not authored** | • run logs and task instance records<br>• materialised intermediate outputs<br>• generated DAG files produced from a template |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Run logs are the specific hazard: one pipeline produces a run record per execution, so they are the highest-count generated class in the slice after build output. They belong to `soft.monitoring-log-export` if anywhere, and they must never anchor - §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.notebook-analysis` | a notebook promoted into a scheduled job is both; a notebook that stayed exploratory is only the analysis entry | §3.11 "One file may hold facts from more than one domain without losing information." |
| `soft.infrastructure-as-code` | the scheduler's own deployment is infrastructure; the tasks it runs are the pipeline | §3.3 "have multiple plausible domains" |

---

### 11. `soft.notebook-analysis` — Computational notebooks and exploratory analysis

A notebook whose cells are the record of someone working a problem out, not a program someone shipped.

- **provenance**: `design`
- **design cite**: §2.4 "Text-bearing files such as Markdown, plain text, JSON, CSV, source code, notebooks, and configuration files should be handled through a lighter structured-text extractor." names notebooks as an extractor class; §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" names notebook metadata as a structural indicator class; §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." names Jupyter notebooks and notebook cell types literally. Catalogue 05 carries the five notebook-metadata keys as `p5n-nbformat`, `p5n-nbformat-minor`, `p5n-kernelspec`, `p5n-language-info` and `p5n-cells` -- cited, not re-derived. Honest qualification on the `design` mark: the DOMAIN is named by the design; applying §3.11 "Code files may use project, repository, programming language, and artifact type." to a notebook extends a row whose own words are "Code files". §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." supports the extension by treating source code, notebooks, configuration files and structured data as one routed class - but the field reuse is inference sitting inside a design-named domain.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally and for a reason peculiar to notebooks: STORED OUTPUTS embed whatever the code printed, which can include rows of personal data and connection strings that appear nowhere in the source. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped; the handling class is P7's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | PVA/RDP | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `programming_language` | string | Python | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `analysis_question` | string | does marker density predict retention | `llm_supported` | NO design sentence names this field. Proposed. A notebook's subject lives in its markdown cells as prose, which is exactly what §3.3 "have multiple plausible domains" sends to the model, and §3.6 "A model that cannot cite sufficient evidence must return unknown." |
| `notebook_state` | string | has stored outputs | `direct` | NO design sentence names this field, but the VALUE is read from the notebook's own top-level keys, which catalogue 05 already recognises, so §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." It exists to serve the authored-versus-generated split: stored outputs are machine-written, the cells are not. |
| `artifact_type` | string | notebook | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • the notebook top-level metadata keys catalogue 05 carries (`p5n-nbformat` with `p5n-cells`) present in the same JSON object - two INDEPENDENT keys of the format, which is pattern plus corroborating context per §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context", and which is why a JSON file that merely has a `cells` key does not match; catalogue 05 records that collision itself as `unc-notebook-key-collision`<br><br>• notebook metadata TOGETHER WITH the root signal, which additionally attaches the notebook to a project |
| **needs LLM** | • what the notebook is ABOUT - its markdown prose is the only evidence and it is prose<br><br>• whether an untitled notebook is exploratory work, coursework, or a research artifact |
| **never alone** | • a `.ipynb` extension alone - the extension names a format and §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning"<br><br>• a kernel name alone, which says which language ran, not what the work was<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `exploratory notebook`, `analysis notebook`, `tutorial notebook`, `report notebook`, `scratch notebook`

**Grouping reasons**: one analysis across its notebook versions; a notebook and the dataset it reads; a notebook and the figures it produced

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." -- so no year level even though notebooks carry strong dates. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the code cells a person wrote<br>• the markdown narrative they wrote around them<br>• the order they arranged the cells in |
| **generated / not authored** | • stored cell outputs, including embedded images and printed tables<br>• execution counts and kernel state<br>• checkpoint copies written automatically beside the notebook - and note that auto-save folders are named in §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees." |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Notebooks are the one place in this slice where authored and generated content sit INSIDE the same file rather than in different files. The `notebook_state` field exists so that split is recorded rather than assumed, and so an output-heavy notebook is not mistaken for a richly authored one on size alone. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `res.computational-notebook` | a notebook that produced a figure in a manuscript is a research artifact and the research slice has a claim on it. Cross-slice ownership, recorded not resolved | §3.11 "One file may hold facts from more than one domain without losing information." |
| `acad.course-enrollment` | the brief's named collision - a notebook that is also coursework. The discriminator is an academic fact at the same root, and §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" supplies the rule shape for that. | §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" |
| `soft.ml-experiment` | a notebook that trains a model and records a run is both; the experiment entry owns it once run and metric artifacts are present | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 12. `soft.ml-experiment` — Machine-learning experiments and runs

The record of training a model - what was tried, on what data, and what came out.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. The field names below are the brief's proposed vocabulary and are marked as proposals throughout. Nearest design anchor is §3.11 "It should then activate domain-specific schemas only when the evidence indicates that a domain is plausible." -- which licenses domain-specific schemas in principle without naming this one.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: training data and evaluation dumps can hold personal records. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `experiment` | string | retention-baseline | `possible` | NO design sentence names this field. Proposed. `possible`: an experiment name is a bare identifier and §3.7 "It should use word-boundary matching rather than substring matching." |
| `dataset` | string | corpus-v3 | `possible` | NO design sentence names this field. Proposed. Note the deliberate reuse of the WORD across this entry and `soft.dataset-artifact`: the same value names a thing in one domain and a reference in the other, which is §3.8 "The system must separate roles that happen to contain the same entity type." |
| `model` | string | gbm-depth-six | `possible` | NO design sentence names this field. Proposed. |
| `run` | string | a run identifier | `possible` | NO design sentence names this field. Proposed, and it is the field that must NEVER become a folder level: a run per training attempt is §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." 'a large number of tiny folders' by construction. |
| `artifact_type` | string | experiment | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • an experiment-tracking directory whose members share one run-naming series, TOGETHER WITH the root signal - the SERIES is the corroborating context<br><br>• a configuration file naming a model and a dataset in the same object, TOGETHER WITH a sibling training script |
| **needs LLM** | • whether a script is training a model or merely loading one<br><br>• what an experiment was FOR, which lives in a README or notebook prose |
| **never alone** | • a metric-shaped number<br><br>• a model architecture name appearing in text<br><br>• a run identifier on its own<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `training script`, `experiment configuration`, `run record`, `metric log`, `evaluation report`, `checkpoint`

**Grouping reasons**: one experiment across its runs; one model across its training attempts; an experiment and the dataset it consumed

**Template**: `project` → `experiment` — time first: `false`

> PROPOSED, and the one entry in the slice whose second dimension is not `artifact_type`, because an experiment IS the organising unit here. `run` is metadata only - §5.4 "It defines the dimensions that are meaningful for one type of material, their recommended order, which dimensions are optional, which ones are metadata only, and what safety or usability constraints apply." provides for metadata-only dimensions and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the training script<br>• the experiment configuration the person chose<br>• the notes and evaluation write-up |
| **generated / not authored** | • run records, metric logs and checkpoint files - all machine-written, all numerous<br>• tracking-server databases<br>• generated plots |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. This domain has the worst authored-to-generated ratio in the slice: a single authored training script produces run records without limit. The guard is structural rather than advisory - `run` is barred from the dimension order, so runs are members inside an experiment branch and never branches themselves. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.notebook-analysis` | training done inside a notebook sits in both; this entry owns it once run records exist | §3.11 "One file may hold facts from more than one domain without losing information." |
| `res.research-project` | an ML experiment run for a paper is a research artifact and the research slice has a claim. Cross-slice, recorded not resolved | §3.11 "One file may hold facts from more than one domain without losing information." |

**Open question** — Joseph's, unresolved.

> The brief proposes `experiment`, `dataset`, `model` and `run` as this domain's fields. NONE is named anywhere in the design, and §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." -- so all four are proposed authored schema additions for Joseph to accept or reject, not fields this catalogue can assert.

---

### 13. `soft.dataset-artifact` — Datasets held as files

A file whose content is rows of data the user keeps as data, rather than as a document to read.

- **provenance**: `inference`
- **design cite**: Extends §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." which names CSV as a routed structured-data format, and §2.4 "Text-bearing files such as Markdown, plain text, JSON, CSV, source code, notebooks, and configuration files should be handled through a lighter structured-text extractor." which names CSV again. Making a data FILE a domain is the inference. Note the design's own treatment of tabular files elsewhere: §2.4 "The system should never silently treat an unsupported format as an empty document"
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies and this entry is the slice's clearest case: a tabular file of rows is the shape personal data arrives in. §2.9 requires contact formats to be 'normally privacy-protected rather than used to create folder proposals', and a CSV of contacts is the same content in a different container. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped; the class and the gate are P7's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `dataset` | string | corpus-v3 | `possible` | NO design sentence names this field. Proposed. `possible`. |
| `format` | string | CSV | `direct` | §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." names CSV literally; the value is read from the routing decision, §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning" |
| `column_labels` | string list | file_id, extractor, zone | `direct` | NO design sentence names this field for a DATASET, but the design names the equivalent for spreadsheets - 'sheet names, visible cell text' in §2.4 - and a header row is a labelled field, so §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." This is the field that makes the domain useful: column labels are what a person can actually search a forgotten dataset by. |
| `artifact_type` | string | dataset | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a tabular file whose first row is a header, TOGETHER WITH a sibling file that references it by name - the reference is the corroborating context per §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context"<br><br>• a tabular file inside a directory named as data at a project root, TOGETHER WITH the root signal |
| **needs LLM** | • whether a CSV is a dataset the user keeps, a one-off export they forgot, or someone's contact list - and the third possibility is why this entry is marked sensitive |
| **never alone** | • a `.csv` or `.parquet` extension<br><br>• a large file size<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `dataset`, `data export`, `reference table`, `fixture`, `sample data`

**Grouping reasons**: one dataset across its versions; a dataset and the code that reads it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. A dataset is a leaf under the project that uses it; a top-level data branch collects files that share a FORM, which §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the dataset a person assembled or collected<br>• the schema and column names they chose<br>• any data dictionary they wrote |
| **generated / not authored** | • exports produced by a query, which regenerate on demand<br>• cached intermediate files written by a pipeline<br>• sample and fixture files generated for tests |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Data files are large but usually FEW, so the bulk hazard here is size rather than count - which the tree does not care about. The real hazard is the opposite one: a single enormous authored dataset looks trivial to the tree and may be under-weighted. That is a P9 grouping question and is not settled here. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.database-schema-migration` | a `.sql` file of rows versus a `.sql` file of structure | §3.3 "have multiple plausible domains" |
| `fin.financial-records` | a CSV of transactions is a finance record before it is a dataset, and finance is a SAFETY domain: §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" | §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" |

---

### 14. `soft.model-artifact` — Trained model files and checkpoints

The binary output of training - a file that is the model rather than the code that made it.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. The design's nearest statement is about how such files are HANDLED, not what domain they are: §2.9 "disk images, executables, databases, encrypted containers, damaged files, and unknown binary formats should default to safe metadata-only indexing unless a dedicated extractor has been explicitly approved."
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to weights as such. A model trained on personal data is a genuine question this catalogue does not have standing to answer, and it is recorded as an open question rather than resolved.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `model` | string | gbm-depth-six | `possible` | NO design sentence names this field. Proposed. |
| `experiment` | string | retention-baseline | `possible` | NO design sentence names this field. Proposed; shared vocabulary with `soft.ml-experiment` on purpose. |
| `format` | string | safetensors | `direct` | Read from the file signature, which §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning" and §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `artifact_type` | string | model artifact | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a model-format file signature TOGETHER WITH a sibling training script or experiment configuration at the same root - the sibling is what distinguishes the user's own model from a downloaded one |
| **needs LLM** | • whether a model file is the user's own training output or a third-party model they downloaded - structure rarely says, and getting this wrong files someone else's artifact as the user's work |
| **never alone** | • a model file extension<br><br>• a checkpoint-shaped filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `trained model`, `checkpoint`, `quantised model`, `tokenizer or vocabulary file`, `model card`

**Grouping reasons**: one model across its checkpoints; a model and the experiment that produced it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the model card or notes a person wrote<br>• the decision of which checkpoint to keep |
| **generated / not authored** | • every checkpoint file - written by the training loop, not by a person<br>• quantised and converted copies<br>• downloaded third-party weights |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Checkpoints are the hazard: a training run writes them repeatedly and they are large. They are members under their model, never branches. And because they are binary, §2.9 "disk images, executables, databases, encrypted containers, damaged files, and unknown binary formats should default to safe metadata-only indexing unless a dedicated extractor has been explicitly approved." -- the product indexes them and does not open them, which is the right posture and also means this domain will always be thin on evidence. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.ml-experiment` | the experiment is the process, the model artifact is its output; they are separated because a downloaded model has no experiment and must still be filable | §3.8 "The system must separate roles that happen to contain the same entity type." |

**Open question** — Joseph's, unresolved.

> Does a model trained on the user's personal corpus inherit the sensitivity of its training data? The design does not address derived artifacts. §8.4's handling classes are P7's; this is a prior question about what §2.9's phrase even attaches to, and it is Joseph's.

---

### 15. `soft.prompt-eval-asset` — Prompt and evaluation assets

The prompts, fixtures and scored outputs that make a language-model feature testable.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. There is however a strong internal anchor: the design already treats a prompt as a first-class identified object elsewhere - §3.4 makes 'prompt fingerprint' part of the cache key and §8.4 requires the audit record to show 'the prompt fingerprint'. That establishes prompts as objects the product reasons about; it does NOT establish a prompt-asset domain, which is the proposal.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: an eval fixture built from the user's real corpus contains their real content by construction. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `prompt_name` | string | grouping-dossier | `possible` | NO design sentence names this field. Proposed. |
| `eval_set` | string | ambiguous-notebooks | `possible` | NO design sentence names this field. Proposed. |
| `model_identifier` | string | a model name string | `direct` | The design names this exact value in §3.4's cache key and in §8.4's audit record. Here it is read from a labelled key in an eval configuration, so §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." -- but it is the design's own vocabulary being reused, not a new coinage. |
| `artifact_type` | string | prompt asset | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a directory of prompt-shaped text or template files TOGETHER WITH a sibling eval configuration or scored-output file at the same root |
| **needs LLM** | • whether a markdown file is a prompt, documentation, or a draft of something else - a prompt is prose and looks like prose<br><br>• whether scored outputs are an evaluation or ordinary logs |
| **never alone** | • a `.md` or `.txt` file containing instruction-shaped language<br><br>• the word `prompt` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `prompt template`, `eval_set`, `scored output`, `rubric`, `golden fixture`, `eval report`

**Grouping reasons**: one prompt across its versions; a prompt and the eval set that scores it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the prompts a person wrote<br>• the rubric and the eval set they chose<br>• their analysis of results |
| **generated / not authored** | • scored output files, regenerated on every eval run<br>• cached model responses<br>• generated comparison reports |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Scored outputs regenerate per run, like ML run records; same guard, same reason. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.technical-specification` | a prompt written as a specification of desired behaviour is genuinely both | §3.3 "have multiple plausible domains" |
| `soft.dataset-artifact` | an eval set is a dataset with a purpose; the purpose is what separates them, and §3.9 "Purpose must be a first-class facet." | §3.9 "Purpose must be a first-class facet." |

---

### 16. `soft.design-doc-rfc` — Design documents and RFCs

A prose document written to propose a change and get agreement on it before the work starts.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. §5.7 "covering common organizational situations such as academic programs, university applications, recruiting processes, client engagements, research workflows, financial records, travel, legal matters, creative projects, software repositories, personal administration, and photo collections." names software repositories among the library's situations but names no document kind inside them.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `proposal_title` | string | Deterministic validation of LLM facts | `direct` | The value is the document's own title, and §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." The FIELD is a proposal; the reliability of the value is not. |
| `decision_state` | string | accepted | `possible` | NO design sentence names this field or any state vocabulary for it. Proposed, and marked `possible` because a state word in a document header is an unlabelled convention, not a labelled form field. See `open_question`. |
| `artifact_type` | string | design document | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a prose document at a repository-marker root or in a documentation directory beneath one, TOGETHER WITH the root signal - the root is what makes it a TECHNICAL document rather than a document, and §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." -- and TOGETHER WITH a header block whose labelled keys name a status or a decision, which is the corroborating context §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" requires |
| **needs LLM** | • whether a document proposes a change or records one already made - the difference between this entry and `soft.architecture-decision-record`, and it is a difference in TENSE, which is prose<br><br>• whether a design document is the user's own or one they saved from elsewhere |
| **never alone** | • the letters `rfc` in a filename<br><br>• a numbered filename; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `design document`, `request for comments`, `proposal`, `review comments`, `superseded draft`

**Grouping reasons**: one proposal across its drafts; a proposal and the review comments on it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child" §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the whole document - this domain is almost purely authored, which is why it matters |
| **generated / not authored** | • generated tables of contents and index pages<br>• rendered HTML or PDF copies of the same document |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. This cluster inverts the slice's usual problem. There is almost no generated bulk; the hazard is the opposite one - a rendered copy of an authored document creating a duplicate that looks like a second work. The design already handles that outside this catalogue: duplicate and version-family signals are universal facts in §2.9 and are P6's. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.technical-specification` | a proposal argues for a change; a specification states what a thing does. Documents routinely do both and this is the weakest boundary in the document cluster | §3.3 "have multiple plausible domains" |
| `ops.product-requirements` | the brief's named collision - a spec that is also a product-management document. The discriminator is whether the document sits at a repository root; a product document usually does not | §3.3 "routing obvious files into plausible domains" |

**Open question** — Joseph's, unresolved.

> This entry and `soft.technical-specification` may be one domain, not two. They share every field and differ only in the document's intent, which is prose. Joseph's call. A second, narrower question rides on it: `decision_state` implies a state VOCABULARY (proposed, accepted, superseded) that no design sentence supplies, and §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." -- so the vocabulary is an authored schema decision, not a runtime one.

---

### 17. `soft.architecture-decision-record` — Architecture decision records

A short numbered document recording one decision, its context, and its consequences.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `decision_title` | string | Store facts separately from paths | `direct` | The document's own title; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `decision_state` | string | superseded | `possible` | Same field and same caveat as `soft.design-doc-rfc`. NO design vocabulary exists for it. |
| `supersedes` | string | a prior record's title | `possible` | NO design sentence names this field HERE - but note the design uses the word for facts: §8.2's supersede-rather-than-overwrite rule, which P6 carries as `supersedes` / `superseded_by`. Reusing the product's own word for a document relationship is deliberate; it is still a proposal. |
| `artifact_type` | string | decision record | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a directory whose members share one ordered numbered naming series AND a common header shape, TOGETHER WITH the root signal - the SERIES plus the header is the corroborating context; either alone is not |
| **needs LLM** | • whether a numbered document is a decision record or a chapter of something else |
| **never alone** | • a numbered filename<br><br>• the letters `adr` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `decision record`, `superseded record`, `decision index`

**Grouping reasons**: one decision series in order; a decision and the record that superseded it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the whole record |
| **generated / not authored** | • generated index pages listing the records |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.design-doc-rfc` | a record states a settled decision; a proposal argues for one. The ordered series is the only structural discriminator | §3.3 "have multiple plausible domains" |

---

### 18. `soft.technical-specification` — Technical specifications

A document that states precisely what a component does, for someone who has to build or verify it.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. The design does use the word for its own artifacts, but about ITSELF rather than about a user's corpus, so it is not cited as authority here.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `specified_component` | string | the evidence extractor | `possible` | NO design sentence names this field. Proposed. `possible`: a component name is a bare identifier, §3.7 "It should use word-boundary matching rather than substring matching." |
| `specification_title` | string | Evidence shape | `direct` | The document's own title; §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `artifact_type` | string | specification | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a prose document at a repository-marker root or in a documentation directory beneath one, TOGETHER WITH the root signal - the root is what makes it a TECHNICAL document rather than a document, and §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." -- TOGETHER WITH a structural shape a specification has and a design proposal does not: numbered requirement clauses or a labelled acceptance section |
| **needs LLM** | • whether a document specifies or proposes - see `soft.design-doc-rfc`<br><br>• whether the specification is the user's or a vendor's, saved for reference |
| **never alone** | • the word `spec` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `specification`, `requirements document`, `acceptance criteria`, `interface contract`

**Grouping reasons**: one component across its specification versions; a specification and the implementation it governs

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the whole document |
| **generated / not authored** | • generated requirement traceability tables |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.design-doc-rfc` | as above; a merge candidate | §3.3 "have multiple plausible domains" |
| `soft.api-specification` | prose a person reads versus a machine-readable contract a program parses | §3.3 "have multiple plausible domains" |

---

### 19. `soft.issue-ticket-export` — Issue and ticket exports

A file dumped out of an issue tracker - many tickets in one file, or one ticket saved as one file.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is the format one: §2.9 "Source code, notebooks, configuration files, and structured data formats such as Python, JavaScript, SQL, Jupyter notebooks, JSON, YAML, TOML, XML, and CSV should yield readable text plus format-specific structure such as language, imports, notebook cell types, package manifests, schema keys, repository markers, and project-root signals." routes JSON and CSV, and these arrive as JSON or CSV. Cited as a format statement only.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: ticket exports carry reporter names, email addresses and message bodies, and §2.9 requires exactly those to be treated as potentially sensitive - §2.9 "treating addresses and message content as potentially sensitive" Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `tracker` | string | GitHub Issues | `possible` | NO design sentence names this field. Proposed. An organisation or product name, so §3.8 "It should avoid using authorship or creator identity as a destination dimension." keeps it out of the dimension order. |
| `ticket_identifier` | string | an issue key | `validated` | NO design sentence names this field. Proposed. `validated` is claimable because a tracker key has a distinctive labelled shape AND appears inside a document whose structure is a ticket export - pattern plus corroborating context, §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context". Bare, it is a version string, which §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `artifact_type` | string | ticket export | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a structured file whose repeated objects carry ticket-shaped labelled keys, TOGETHER WITH the root signal or a tracker name in the same document |
| **needs LLM** | • whether an export is the user's own project's or one they received<br><br>• which project a mixed export belongs to when it spans several |
| **never alone** | • a ticket-key-shaped token in running text - it is the exact shape §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• a `.json` or `.csv` extension<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `issue export`, `single ticket`, `backlog snapshot`, `sprint report`

**Grouping reasons**: one project's tickets; one export across its parts

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the ticket text people wrote |
| **generated / not authored** | • the export container itself - the file is machine-produced even though its contents are authored<br>• generated report and burndown files |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. This entry inverts the usual split: the FILE is generated, the CONTENT is authored. That is why it stays a domain rather than being dismissed as build output - and why the guard here is about volume of PEOPLE named rather than volume of files. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.helpdesk-ticket` | an engineering issue versus a support request. Same file shape, different organisation; the discriminator is whether the tracker is a development tracker | §3.3 "have multiple plausible domains" |

---

### 20. `soft.code-review-artifact` — Code review artifacts

The record of one change being reviewed - the diff, the comments on it, and the decision.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: review exports carry named colleagues and their comments - §2.9 "treating addresses and message content as potentially sensitive" Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `repository` | string | AIFILESORTERULTIMATE | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `repository` is literal. Populated from the directory name that carries the version-control marker (catalogue 05 `p5r-git`, `p5r-hg`, `p5r-svn`), not from any string inside a source file. |
| `change_identifier` | string | a pull-request number or a commit reference | `validated` | NO design sentence names this field. Proposed. `validated` only with its label present (`PR`, `commit`) inside a review-shaped document; bare it is a number and §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `review_outcome` | string | approved | `llm_supported` | NO design sentence names this field or any outcome vocabulary. Proposed. An outcome stated in prose needs interpretation, so §3.6 "A model that cannot cite sufficient evidence must return unknown." |
| `artifact_type` | string | review record | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a diff-formatted file TOGETHER WITH the root signal - a diff has a machine-recognisable header shape, and the root attaches it to a project<br><br>• a review export whose repeated objects carry comment-shaped labelled keys, together with a change identifier in the same document |
| **needs LLM** | • the outcome, as above<br><br>• whether saved review comments are the user's own or a colleague's |
| **never alone** | • a `.diff` or `.patch` extension<br><br>• a commit-hash-shaped token<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `diff`, `patch`, `review comments`, `review summary`, `merge record`

**Grouping reasons**: one change across its review artifacts; one project's reviews

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the review comments people wrote<br>• the summary the reviewer wrote |
| **generated / not authored** | • the diff itself, which is computed from two versions and not typed<br>• generated review reports and statistics |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.issue-ticket-export` | a review thread exported from the same tracker looks identical; the change identifier and the diff are what separate them | §3.3 "have multiple plausible domains" |

---

### 21. `soft.release-notes-changelog` — Release notes and changelogs

The running record of what changed in a piece of software between one release and the next.

- **provenance**: `inference`
- **design cite**: Extends catalogue 05, which already carries `p5r-changelog-md` as a `repository marker` under §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" -- the recogniser is cited, not re-derived. Making it a domain is the inference.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `release_version` | string | v2.1.0 | `possible` | NO design sentence names this field. Proposed. §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." -- and a changelog is the densest concentration of version-shaped strings in any corpus, so this ceiling is doing real work. |
| `release_date` | date | a dated heading | `validated` | NO design sentence names this field, but the design DOES govern how it may be found: §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." A dated changelog heading is an explicit labelled position, so a narrow rule can validate it; a date anywhere else in the file cannot. |
| `artifact_type` | string | changelog | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • catalogue 05's `p5r-changelog-md` at a directory root TOGETHER WITH the root signal<br><br>• a document whose headings form a descending version series - the SERIES is the corroborating context and a single version heading is not |
| **needs LLM** | • whether release notes written as prose for users are a changelog or user documentation |
| **never alone** | • a version-shaped string; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• the word `changelog` inside a document body<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `changelog`, `release notes`, `migration guide`, `upgrade notes`

**Grouping reasons**: one project's releases in order

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and `release_version` is barred from the dimension order for the same reason as in `soft.library-package`: §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the entries a person wrote describing what changed |
| **generated / not authored** | • changelogs assembled automatically from commit messages - increasingly the norm, and indistinguishable from an authored one by file shape alone |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. The generated changelog is the honest limit of this entry: there is no structural signal separating a hand-written changelog from a generated one. That is not a reason to drop the entry - both are the project's release record and both file identically - but it IS a reason the entry claims nothing about authorship. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.user-documentation` | release notes written for end users are both; the discriminator is whether the document is organised by version | §3.3 "have multiple plausible domains" |

---

### 22. `soft.incident-postmortem` — Incident and postmortem records

The record of something breaking in production and what was learned from it.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: postmortems name individuals and quote internal correspondence - §2.9 "treating addresses and message content as potentially sensitive" Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `incident` | string | an incident identifier or title | `validated` | NO design sentence names this field. Proposed. `validated` only with an incident label present inside a postmortem-shaped document - pattern plus corroborating context, §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" |
| `service` | string | the placement service | `possible` | NO design sentence names this field. Proposed. `possible`: a service name is a bare identifier, §3.7 "It should use word-boundary matching rather than substring matching." |
| `occurred_at` | datetime | a labelled timestamp in the timeline section | `validated` | NO design sentence names this field, but the design governs how a date may be found: §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." A postmortem timeline is a labelled position, so a narrow rule can validate a timestamp there and nowhere else in the document. |
| `artifact_type` | string | postmortem | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a document containing a labelled timeline section AND a labelled impact or resolution section, TOGETHER WITH the root signal or an operations directory - the PAIR of labelled sections is the corroborating context and either alone is not |
| **needs LLM** | • whether a document describing a failure is a postmortem, a bug report, or a support ticket<br><br>• the narrative of what happened, which is the whole substance and is prose |
| **never alone** | • the word `incident` or `outage` in a filename<br><br>• a timestamp; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `postmortem`, `incident timeline`, `status update`, `action item list`, `review notes`

**Grouping reasons**: one incident across its documents; a family of incidents on one service

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." -- so no year level, even though incidents are strongly dated. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the timeline, analysis and action items people wrote |
| **generated / not authored** | • log excerpts pasted in<br>• generated status-page histories<br>• automated alert records |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.monitoring-log-export` | the log excerpt attached to a postmortem is evidence FOR it; the postmortem is the authored document. They travel together and must not be merged | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.security-finding-report` | a security incident is both, and the security entry's sensitivity should govern | §3.11 "One file may hold facts from more than one domain without losing information." |

**Open question** — Joseph's, unresolved.

> The brief proposes `severity` as a field of this domain. NO design sentence supplies a severity vocabulary, scale or set of levels, anywhere. §3.12 "The system may create new values when it sees a new course, project, company, university, or event, but it should not invent new fields automatically." -- so a severity scale would be an authored schema addition AND an authored VALUE vocabulary, and this catalogue is barred from minting either. It is therefore omitted from the schema above rather than invented with a plausible set of levels. Does Joseph want a severity field, and if so whose scale?

---

### 23. `soft.runbook-operational-doc` — Runbooks and operational documentation

Instructions for operating a running system - what to do when, and in what order.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: runbooks routinely carry access instructions and endpoint details. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `service` | string | the placement service | `possible` | NO design sentence names this field. Proposed. `possible`, §3.7 "It should use word-boundary matching rather than substring matching." |
| `procedure` | string | restore from backup | `possible` | NO design sentence names this field. Proposed. |
| `artifact_type` | string | runbook | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a prose document at a repository-marker root or in a documentation directory beneath one, TOGETHER WITH the root signal - the root is what makes it a TECHNICAL document rather than a document, and §2.4 "Code-related files should rely heavily on local structural evidence, including repository roots and package files, rather than forcing semantic analysis to infer a project from arbitrary code text." -- TOGETHER WITH an ordered instruction structure (numbered steps with imperative headings), which is a document SHAPE a rule can check |
| **needs LLM** | • whether an ordered document is a runbook, a setup guide, or a tutorial - all three are numbered steps and the difference is who the reader is |
| **never alone** | • the word `runbook` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `runbook`, `operational procedure`, `escalation guide`, `on-call handbook`, `checklist`

**Grouping reasons**: one service's operational documents

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the procedures people wrote |
| **generated / not authored** | • generated diagrams embedded in the document |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.dev-environment-setup` | operating a running system versus preparing a machine to develop on. Both are numbered steps | §3.3 "have multiple plausible domains" |
| `soft.user-documentation` | the reader is the discriminator - an operator versus an end user - and the reader is rarely stated | §3.3 "have multiple plausible domains" |

---

### 24. `soft.monitoring-log-export` — Monitoring and log exports

A file of machine-emitted operational records, saved out of a monitoring system.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is a HANDLING one: §2.9 "disk images, executables, databases, encrypted containers, damaged files, and unknown binary formats should default to safe metadata-only indexing unless a dedicated extractor has been explicitly approved."
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: logs contain user identifiers, addresses, request contents and tokens. §2.9 "treating addresses and message content as potentially sensitive" and §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped - and this is one of the cases where §8.4's escalation gate matters most, because a log is exactly the kind of file whose content should not be sent anywhere. That gate is P7's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `service` | string | the placement service | `possible` | NO design sentence names this field. Proposed. |
| `capture_window` | string | a labelled from-to range in the export header | `validated` | NO design sentence names this field. Proposed. `validated` ONLY from a labelled export header; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." forbids reading a range out of the log lines themselves. |
| `artifact_type` | string | log export | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a file whose lines share one repeated timestamped record shape, TOGETHER WITH an export header or a monitoring directory at a project root |
| **needs LLM** | • what an unlabelled log is FOR - why it was saved, which is the only thing that makes it worth keeping and is never in the file |
| **never alone** | • a `.log` extension<br><br>• a timestamp; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `log export`, `metric export`, `trace export`, `alert history`, `dashboard definition`

**Grouping reasons**: one export across its parts; logs attached to one incident

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and this entry is a strong candidate for a RESIDUAL destination rather than a domain branch: §7.3 "the library must support user-defined residual areas" and §7.3's Unsupported or Encrypted template is the nearest existing home for machine files with no durable purpose. Not decided here - §7 is P11's and the residual library is already authored.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the decision to save this export, and any note saying why - usually nothing else |
| **generated / not authored** | • the entire file. This domain is the slice's one fully generated domain and it is included deliberately so, because a template that does not know these files exist will file them somewhere worse. |
| **template guard** | The guard here is the domain's PURPOSE. It exists to give machine-emitted operational files a named, shallow, low-status destination instead of letting them be absorbed into an authored project branch by proximity. §3.9 "Purpose must be a first-class facet." §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." -- so a log export may never be the anchor that creates a branch; it can only join one. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.incident-postmortem` | logs attached to a postmortem belong WITH it as evidence, not merged into it | §3.8 "The system must separate roles that happen to contain the same entity type." |

---

### 25. `soft.performance-load-test` — Performance and load testing

The scripts that generate load and the measurements that came back.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `scenario` | string | sustained write load | `possible` | NO design sentence names this field. Proposed. |
| `system_under_test` | string | the placement service | `possible` | NO design sentence names this field. Proposed. §3.8 "The system must separate roles that happen to contain the same entity type." -- the system tested is a different role from the system that ran the test, and conflating them is the error that rule exists to prevent. |
| `artifact_type` | string | performance test | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a load-scenario definition file at a project root TOGETHER WITH a sibling result file of the same tool |
| **needs LLM** | • whether a result file is a performance measurement or ordinary monitoring output<br><br>• whether a run was a real benchmark or an accident |
| **never alone** | • a filename containing `bench`, `perf` or `load`<br><br>• a measurement-shaped number - and NO number of any kind may enter a fact here<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `load scenario`, `benchmark script`, `result set`, `performance report`, `baseline`

**Grouping reasons**: one scenario across its runs; one system across its benchmarks

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the scenario a person designed<br>• their analysis of the results |
| **generated / not authored** | • result files, one per run<br>• generated comparison charts |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Result files regenerate per run, like ML run records and eval outputs; the same member-not-anchor rule applies. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.monitoring-log-export` | a result set is a measurement export; the scenario script is what makes this a distinct domain | §3.8 "The system must separate roles that happen to contain the same entity type." |

---

### 26. `soft.security-finding-report` — Security findings and penetration test reports

A report describing weaknesses found in the user's own systems.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. The design's relevant sentence is about protection, not classification: §8.4 "A scanned passport, tax statement, medical document, authentication key, or account record should enter a protected state immediately."
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies, and this is among the strongest cases in the slice: a findings report is a description of how to compromise the user's own systems. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. names credentials among what the product handles and §8.4 "Protected material should not be included in cloud-model prompts by default" -- but the handling class, the redaction policy and the model-escalation gate are P7's under §8.4 and are NOT set here. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `engagement` | string | an engagement or assessment name | `possible` | NO design sentence names this field. Proposed. |
| `assessed_system` | string | the placement service | `possible` | NO design sentence names this field. Proposed. §3.8 "The system must separate roles that happen to contain the same entity type." |
| `assessing_party` | string | an organisation name | `possible` | NO design sentence names this field. Proposed, and it is metadata ONLY: §3.8 "It should avoid using authorship or creator identity as a destination dimension." -- filing security reports by the firm that wrote them is precisely the collector anti-pattern §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group." refuses. |
| `artifact_type` | string | security report | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a report document at a project root TOGETHER WITH a labelled findings section - and note this entry deliberately defines NO vulnerability-name pattern of its own, because a catalogue of attack strings is exposure surface, which is the same refusal catalogue 06 makes about government identifier patterns |
| **needs LLM** | • whether a security document is a finding about the user's system, an advisory about a dependency, or a policy statement<br><br>• how serious a finding is - which is a severity question and is refused; see `open_question` |
| **never alone** | • a vulnerability identifier appearing anywhere<br><br>• the word `security` in a filename - catalogue 05's `p5r-security-md` is a repository POLICY file, an entirely different thing, and conflating them would file every open-source project's boilerplate as a penetration test<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `assessment report`, `finding`, `remediation plan`, `retest report`, `scope document`

**Grouping reasons**: one engagement across its documents; findings on one system

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. Deliberately NOT `assessing party -> ...`: §3.8 "It should avoid using authorship or creator identity as a destination dimension."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the findings and remediation advice the assessor wrote |
| **generated / not authored** | • scanner output appended as an appendix<br>• generated evidence screenshots |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.vulnerability-disclosure` | a finding about the user's OWN system versus a published advisory about someone else's code that the user depends on. §3.8 "The system must separate roles that happen to contain the same entity type." | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.tech-compliance-evidence` | a report submitted as compliance evidence is both | §3.11 "One file may hold facts from more than one domain without losing information." |

**Open question** — Joseph's, unresolved.

> Findings are conventionally ranked, and the brief flags exactly this: a severity vocabulary is one this catalogue must not invent. No design sentence supplies one. It is omitted rather than guessed. Joseph's call, and the same call as `soft.incident-postmortem`'s - if a severity field is wanted, one authored vocabulary should serve both.

---

### 27. `soft.vulnerability-disclosure` — Vulnerability disclosures and advisories

A published notice that a named piece of software has a named weakness.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: a PUBLISHED advisory is public by definition, but coordinated-disclosure correspondence before publication is not. The two arrive as the same document type. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `advisory_identifier` | string | a labelled advisory reference | `validated` | NO design sentence names this field. Proposed. `validated` requires the label present with the reference - the same discipline catalogue 06 applies to `cid-pmid`, where 'a bare number is never an identifier'. Cited from catalogue 06, not re-derived. |
| `affected_package` | string | a package name | `possible` | NO design sentence names this field. Proposed. `possible`: a package name is a bare identifier, §3.7 "It should use word-boundary matching rather than substring matching." |
| `affected_version_range` | string | a labelled range | `possible` | NO design sentence names this field. Proposed. §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `artifact_type` | string | advisory | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a labelled advisory reference TOGETHER WITH a labelled affected-package section in the same document |
| **needs LLM** | • whether the user is the reporter, the maintainer, or merely an affected consumer - three different roles in one document, which §3.8 "The system must separate roles that happen to contain the same entity type." |
| **never alone** | • an advisory-identifier-shaped token with no label<br><br>• a package name in a dependency list<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `advisory`, `disclosure notice`, `dependency alert`, `patch notice`, `coordinated disclosure correspondence`

**Grouping reasons**: one advisory across its correspondence; advisories affecting one project

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the user's own report or correspondence, where they are the reporter |
| **generated / not authored** | • automated dependency alerts, which arrive continuously and in volume |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Automated dependency alerts are the hazard: a tool can emit one per dependency per release. They are members, never anchors - §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.security-finding-report` | someone else's published weakness versus a finding about the user's own system | §3.8 "The system must separate roles that happen to contain the same entity type." |

---

### 28. `soft.tech-compliance-evidence` — Compliance evidence for technical controls

Documents and exports collected to show an auditor that a technical control is actually in place.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Note what the design DOES say about the adjacent material: §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" -- legal material is a safety domain, and audit evidence sits beside it without being it.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: compliance evidence bundles account records, access lists and personnel data. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `control` | string | a control reference | `possible` | NO design sentence names this field. Proposed. |
| `audit_period` | string | a labelled period in the report header | `validated` | NO design sentence names this field. Proposed. `validated` only from a labelled header; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `framework` | string | a named control framework | `possible` | NO design sentence names this field. Proposed. A framework name is an organisation-adjacent label; §3.8 "It should avoid using authorship or creator identity as a destination dimension." keeps it out of the dimension order. |
| `artifact_type` | string | compliance evidence | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a document containing a labelled control reference AND a labelled evidence or period section, TOGETHER WITH an audit or compliance directory |
| **needs LLM** | • whether a document is evidence, a policy, or a report ABOUT the audit<br><br>• which control a screenshot or export was collected for, when the file itself does not say |
| **never alone** | • a control-reference-shaped token<br><br>• a framework name in running text<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `policy document`, `control evidence`, `audit report`, `questionnaire response`, `attestation letter`

**Grouping reasons**: one audit period's evidence; evidence for one control across periods

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and a genuinely uncertain one: compliance evidence may belong under a legal or administrative branch rather than a software one. §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" Not decided here - cross-slice, and §5.1 "a typical initial canvas might include Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material." lists both Code and Projects and Personal Records as candidate top-level areas.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the policies and narratives a person wrote<br>• the decision of what evidences what |
| **generated / not authored** | • exported access lists and configuration snapshots collected as evidence<br>• automated evidence-collection output |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `law.compliance-programme` | cross-slice; the legal slice may own the whole of this. Recorded, not resolved | §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" |
| `soft.security-finding-report` | a penetration test submitted as evidence is both | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 29. `soft.licence-oss-compliance` — Licences and open-source compliance

The licence a project is released under and the record of what it depends on and under what terms.

- **provenance**: `inference`
- **design cite**: Extends catalogue 05, which already carries `p5r-license`, `p5r-license-md`, `p5r-license-txt` and `p5r-copying` as `repository marker` rows under §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" -- and records that `LICENSE` and `COPYING` are case-SENSITIVE there 'so that a document named licence or description cannot match'. Cited, not re-derived. Making them a domain is the inference.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to a public licence text.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `licence_identifier` | string | a licence short name | `validated` | NO design sentence names this field. Proposed. `validated` because the value is read from a licence header inside a file catalogue 05 already recognises by name - marker plus content position, which is §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context". A licence name in ordinary prose is not. |
| `artifact_type` | string | licence | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 licence marker row (`p5r-license`, `p5r-copying`) at a directory root TOGETHER WITH the root signal<br><br>• a dependency-inventory document listing package names with licence identifiers in the same rows |
| **needs LLM** | • whether a licence file governs the user's own work or a dependency they vendored<br><br>• whether a compliance note is a decision or a draft |
| **never alone** | • a licence short name in running text<br><br>• the lowercase word `licence` or `license` as a filename - catalogue 05 makes this row case-sensitive for exactly that reason<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `licence`, `notice file`, `dependency inventory`, `attribution list`, `compliance note`

**Grouping reasons**: one project's licence and its attributions

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the choice of licence<br>• the attribution and notice text a person assembled |
| **generated / not authored** | • generated dependency inventories and bills of materials<br>• licence texts copied verbatim from upstream - authored by someone, but not by this user |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Note the specific inversion: a licence file is one of the most-duplicated files in any corpus, because every project and every vendored dependency carries one. §2.9's duplicate and version-family signals are universal facts and are P6's; this entry relies on them rather than restating them. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `legal.contracts` | a negotiated commercial licence is a legal document; an open-source licence file is a repository artifact. Cross-slice | §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" |

---

### 30. `soft.dev-environment-setup` — Developer environment setup

The files and instructions that get a machine ready to work on a project.

- **provenance**: `inference`
- **design cite**: Extends catalogue 05's tooling rows (`p5r-editorconfig`, `p5r-pre-commit-config-yaml`, `p5m-flake-nix`, `p5m-shell-nix`, `p5m-environment-yml`) held under §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files"
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies to setup files as such; an environment file holding a real key is `soft.configuration-and-secrets` and is marked there.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `toolchain` | string | a named toolchain or runtime | `possible` | NO design sentence names this field. Proposed. |
| `artifact_type` | string | environment setup | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 environment or tooling marker at a directory root TOGETHER WITH the root signal<br><br>• a setup document at a project root TOGETHER WITH an ordered install-step structure |
| **needs LLM** | • whether a setup document is for this project, for a machine generally, or is a personal note |
| **never alone** | • the word `setup` in a filename - catalogue 05's `p5m-setup-py` is a PACKAGE MANIFEST, an entirely different thing<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `environment definition`, `setup guide`, `bootstrap script`, `editor configuration`, `tool version pin`

**Grouping reasons**: one project's environment files

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the setup steps a person wrote<br>• the tool versions they pinned |
| **generated / not authored** | • generated lock files for the environment<br>• installed toolchain directories |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.personal-dotfiles` | project-scoped versus person-scoped. Location decides it and §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." | §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." |
| `soft.runbook-operational-doc` | preparing to develop versus operating what is running | §3.3 "have multiple plausible domains" |

---

### 31. `soft.personal-dotfiles` — Personal dotfiles and shell configuration

The configuration a person carries between machines because it is how THEY like to work.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. But the design speaks directly to how such a folder must be treated: §1.1 "The system should also know that existing folder structures should mainly be preserved. For example, if a folder called AIKonic Project has a lot of files such as JSON and other software material, those are probably not supposed to be touched." -- a curated personal configuration folder is the same kind of thing, and §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent."
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: shell history, credential helpers and host aliases live among dotfiles. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `tool` | string | a named tool | `possible` | NO design sentence names this field. Proposed. |
| `machine_scope` | string | personal | `possible` | NO design sentence names this field. Proposed, and it is the field that separates this domain from `soft.configuration-and-secrets` - which makes it the whole entry and also its weakest point, since it is inferred from LOCATION rather than content. |
| `artifact_type` | string | dotfile | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a dot-prefixed configuration file in the user's home directory rather than inside a project root - the ABSENCE of a project root above it is the corroborating context here, which is the inverse of every other entry in this slice and is stated deliberately<br><br>• a dot-prefixed configuration file inside a directory that is itself version-controlled AND whose members are predominantly dot-prefixed |
| **needs LLM** | • whether a dotfile is the person's own preference or a project's requirement copied home |
| **never alone** | • a leading dot in a filename - which describes hiddenness, not purpose<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `shell configuration`, `editor configuration`, `prompt configuration`, `keybinding file`, `install script`

**Grouping reasons**: one person's configuration across their tools

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and flagged: a dotfiles collection is very often ALREADY a curated folder the user maintains, and §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." together with §1.1 "The system should also know that existing folder structures should mainly be preserved. For example, if a folder called AIKonic Project has a lot of files such as JSON and other software material, those are probably not supposed to be touched." point the same way - the right default may be to leave it alone entirely rather than to propose a structure for it. See `open_question`.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • every configuration choice in them - this is one of the most purely authored domains in the slice, file for file |
| **generated / not authored** | • plugin directories installed by a tool manager<br>• generated completion scripts<br>• shell history files |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. The generated half here is usually a plugin directory, which is a dependency tree under a name §1.1 does NOT list - so §1.1's exclusion often does not fire on a dotfiles repository. That makes this one of the entries where the project-scale dimension rule is doing all the work on its own. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.configuration-and-secrets` | the brief's named collision - a config file that is also a personal dotfile. Location decides: inside a project it configures the project, in the home directory it configures the person. Where a dotfiles repository is BOTH version-controlled and personal, both domains legitimately activate, which §3.11 "One file may hold facts from more than one domain without losing information." | §3.11 "One file may hold facts from more than one domain without losing information." |

**Open question** — Joseph's, unresolved.

> Should a personal dotfiles directory be organised by this product at all? §1.1 "The system should also know that existing folder structures should mainly be preserved. For example, if a folder called AIKonic Project has a lot of files such as JSON and other software material, those are probably not supposed to be touched." and §5.10 "A carefully curated existing folder should be treated as a strong expression of user intent." both suggest the answer may be to recognise it and leave it untouched. That is a decision about someone's real working setup and it is Joseph's, not this catalogue's.

---

### 32. `soft.scratch-prototype` — Scratch and prototype work

Code someone wrote to find something out, with no intention of keeping it.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. The design's relevant provision is a destination one: §5.9 "It should also support a scoped General or Other branch within a meaningful parent."
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `programming_language` | string | Python | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `prototype_subject` | string | what was being tried | `llm_supported` | NO design sentence names this field. Proposed, and it can only ever be `llm_supported`: scratch code by definition carries no structural evidence of its purpose, which is the case §3.3 "have multiple plausible domains" describes. §3.6 "A model that cannot cite sufficient evidence must return unknown." |
| `artifact_type` | string | prototype | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • THERE IS NO STRONG DETERMINISTIC SIGNAL FOR THIS DOMAIN, and saying so is the entry's main contribution. The nearest is negative: a source file with NO project root above it, NO version-control marker, and NO manifest anywhere in its ancestry - which is the absence of every signal the rest of this slice depends on. An absence is not a pattern, so this is recorded as a routing hint, not as a validated-fact rule |
| **needs LLM** | • everything of substance - what the scratch file was for is prose or nothing at all |
| **never alone** | • a filename containing `test`, `tmp`, `scratch`, `old` or `untitled` - these are the most over-loaded words in any corpus and §3.7 "It should use word-boundary matching rather than substring matching."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `scratch script`, `spike`, `throwaway prototype`, `snippet`, `experiment file`

**Grouping reasons**: files written in one bounded working session - and note the ceiling: §3.13 "A possible fact is a useful but insufficient clue, such as membership in a short download session or a low-confidence semantic match."

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and the recommendation is the shallow one. §5.9 "It should also support a scoped General or Other branch within a meaningful parent." -- scratch work belongs in a scoped General folder under a meaningful parent, not in a deep structure of its own, and §7.2 "The library prevents the LLM from creating arbitrary folders" is the general warning against inventing plausible-sounding homes for material that has none.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • all of it - this domain is entirely authored, which is exactly why it deserves an entry despite having no reliable signal |
| **generated / not authored** | • nothing generated is characteristic of it |
| **template guard** | The guard runs the other way here. The risk is not that this domain files generated bulk; it is that generated stray files with no project above them look EXACTLY like scratch work and get filed as someone's thinking. The mitigation is the `llm_supported` ceiling on the only substantive field plus §3.6 "A model that cannot cite sufficient evidence must return unknown." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.source-project` | a prototype that acquired a manifest, a licence and version control has become a project; the markers are the transition | §2.5 "A source-code archive may reveal a README.md, package.json, src directory, or Python package layout and can be recognized as a code project." |
| `soft.notebook-analysis` | a scratch notebook is both; the notebook metadata gives the notebook entry the stronger claim because it has an actual deterministic signal | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 33. `soft.game-development-asset` — Game development projects and assets

A game project, where the authored work is as much art, audio and level data as it is code.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is a FORMAT one covering the asset half: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty."
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | orbit-runner | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `engine` | string | a named engine | `validated` | NO design sentence names this field. Proposed. `validated` because a game engine writes a distinctive project file at the root, and matching it TOGETHER WITH the engine's own asset directory layout is pattern plus corroborating context, §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context". This catalogue names no engine file - that would be a marker list, and marker lists live in catalogue 05. |
| `asset_class` | string | level data | `possible` | NO design sentence names this field. Proposed. |
| `artifact_type` | string | game project | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • an engine project file at a directory root TOGETHER WITH the engine's asset directory layout - the specific names belong in catalogue 05 if Joseph wants them, NOT here |
| **needs LLM** | • whether a directory of art assets belongs to a game, to a design project, or to neither<br><br>• which of several prototypes is the real project |
| **never alone** | • a 3D or image file extension<br><br>• the word `game` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `engine project`, `scene or level`, `art asset`, `audio asset`, `gameplay script`, `build configuration`

**Grouping reasons**: one game across its assets and code; one game across its builds

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child" -- and note that `asset_class` is a strong candidate for a THIRD level here, which most entries in this slice do not warrant. Not asserted: §5.7 "The engine validates that the proposed template does not repeat a parent dimension, create meaningless one-child levels, exceed practical depth limits, use an author or organization merely as a collector, expose protected information, or produce empty branches when tested against the accepted group."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • scripts, scene and level data, and the art and audio the person made or licensed |
| **generated / not authored** | • imported asset caches and reimport metadata - a game engine writes one per source asset, making this the highest generated-file ratio of any entry here<br>• compiled shaders and baked lighting data<br>• packaged builds |
| **template guard** | This entry is where the slice's guard is most load-bearing, because game engines generate a companion metadata file for EVERY imported asset, and those companion files sit directly beside the authored asset rather than in a separate directory. §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees." does not name any of them, and §1.1 "It should also reject descendants of software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or go.mod. This prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal destination." does not fire because a game project carries none of §1.1's four markers. So neither scan-time layer helps. What is left is the project-scale dimension rule and §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps.". If Joseph wants engine cache directories excluded, that is an addition to catalogue 05's or §1.1's lists - not something this catalogue may do. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.source-project` | a game IS a source project; it is separated only because its authored work is predominantly non-code, which changes the template | §3.11 "One file may hold facts from more than one domain without losing information." |
| `studio.stock-asset-library` | art assets belong to the creative slice when they exist independently of a game project. Cross-slice | §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." |

**Open question** — Joseph's, unresolved.

> Game engine cache and import-metadata directories are generated bulk that §1.1's eleven literal names do not cover and §1.1's four project-root markers do not reach. Should they be added to the exclusion mechanism? That is P3's and Joseph's, and catalogue 05 is where any addition would live.

---

### 34. `soft.embedded-firmware` — Embedded and firmware projects

Software written to run on a specific piece of hardware rather than on a general computer.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `programming_language` | string | C | `direct` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `programming_language` is literal. `direct` ONLY where the value is read from a labelled metadata field - a notebook's `language_info` / `kernelspec` (catalogue 05 `p5n-language-info`, `p5n-kernelspec`), or a manifest's own language declaration. §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." Inferred from an extension it is `possible`, never `direct`. |
| `target_hardware` | string | a named board or microcontroller | `possible` | NO design sentence names this field. Proposed. `possible`: a part number is exactly the class of token §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." warns about - it looks like a version and is not. |
| `artifact_type` | string | firmware | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a build manifest catalogue 05 already carries (`p5m-cmakelists-txt`, `p5m-makefile`) at a directory root TOGETHER WITH a hardware-specific configuration or linker file as a sibling - the hardware-specific sibling is what separates firmware from ordinary C++, and neither half is decisive alone |
| **needs LLM** | • whether a C project targets hardware or a desktop<br><br>• which board a project targets, when it is stated only in a comment |
| **never alone** | • a `.c`, `.h` or `.hex` extension<br><br>• a part-number-shaped token; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values."<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `firmware source`, `board configuration`, `linker script`, `flashing script`, `datasheet`

**Grouping reasons**: one device across its firmware versions; firmware and the hardware design it runs on

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the firmware source<br>• the board configuration a person wrote |
| **generated / not authored** | • compiled binaries and hex images<br>• generated register-definition headers from a vendor tool<br>• vendor SDK trees copied into the project |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. The vendor SDK tree is the specific hazard: embedded projects routinely vendor an entire manufacturer SDK into the repository, and it is large, authored by someone else, and NOT under any name §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees." lists - `vendor` is on that list, but manufacturer SDKs are rarely put in a directory called `vendor`. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.hardware-design-file` | firmware and the board it runs on are one project to their author and two file families on disk; a user may well want them under one branch | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 35. `soft.hardware-design-file` — Hardware design files

Schematics, board layouts and mechanical models - the drawings a physical thing is built from.

- **provenance**: `inference`
- **design cite**: Extends §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." which names CAD files and 3D files literally and prescribes what to do when the format cannot be read. Making them a domain is the inference.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `design_name` | string | a board or part name | `possible` | NO design sentence names this field. Proposed. |
| `design_revision` | string | a labelled revision | `possible` | NO design sentence names this field. Proposed. §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `format` | string | a CAD format | `direct` | §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." -- the design requires format to be yielded at minimum even where the content cannot be read, and §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `artifact_type` | string | hardware design | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a CAD or board-layout file signature TOGETHER WITH a sibling of a paired format from the same toolchain (a schematic beside a layout) at the same root - the PAIR is the corroborating context |
| **needs LLM** | • what a design is FOR, when the format is proprietary and unreadable - and the design already anticipates this: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." |
| **never alone** | • a CAD file extension<br><br>• a revision-shaped token<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `schematic`, `board layout`, `mechanical model`, `fabrication output`, `bill of materials`, `datasheet`

**Grouping reasons**: one board across its revisions; a board and the firmware that runs on it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the schematic and layout a person drew<br>• the bill of materials they compiled |
| **generated / not authored** | • fabrication outputs generated from the layout<br>• generated 3D renders and preview images<br>• autosave and backup copies the CAD tool writes - and §1.1 "The engine should ignore node_modules, .git, venv, build, dist, target, vendor, Pods, site-packages, Library, __pycache__, build artifacts, caches, auto-save folders, previews, and generated dependency trees." names auto-save folders, so this one IS covered where the tool uses a folder rather than a sibling file. |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Fabrication output is generated from the layout on demand and is numerous; it is a member under the design, never a branch. Where the format cannot be read at all, §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." governs - indexed-but-unreadable, not empty, which is also §2.4 "The system should never silently treat an unsupported format as an empty document" |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.embedded-firmware` | as above - one project, two file families | §3.11 "One file may hold facts from more than one domain without losing information." |
| `cg.3d-asset` | 3D files span mechanical design and creative work; §2.9 names them once and does not separate the two uses. Cross-slice | §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." |

---

### 36. `soft.network-diagram` — Network and system diagrams

A drawing of how systems connect, kept as the reference for how the estate is laid out.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Nearest anchor is the format one: §2.9 "Design and creative formats such as PSD, AI, SVG, Figma exports, CAD files, and 3D files should at minimum yield filename, format, dimensions or canvas properties, embedded metadata, layers or artboards where accessible, linked asset names, and preview text; unsupported proprietary formats should be recorded as indexed-but-unreadable rather than silently treated as empty." names SVG and design formats; a diagram file is one of those, which is a format statement and not a domain one.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies conditionally: a network diagram is a map of an organisation's internal topology, including addresses and access paths. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `estate` | string | a network or environment name | `possible` | NO design sentence names this field. Proposed. |
| `diagram_format` | string | a diagram format | `direct` | Read from the file signature; §2.9 "The engine should treat the file extension as a routing signal rather than an assumption about meaning" and §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." |
| `artifact_type` | string | diagram | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a diagram-tool source file TOGETHER WITH a network or architecture directory, or together with the root signal where the diagram sits in a project's documentation |
| **needs LLM** | • what a diagram DEPICTS - the labels inside it are the only evidence, they are often images rather than text, and §2.1 "filenames alone are too weak for real personal corpora" |
| **never alone** | • a `.svg` or `.drawio` extension<br><br>• the word `diagram` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `network diagram`, `architecture diagram`, `topology map`, `rack layout`, `data-flow diagram`

**Grouping reasons**: one estate across its diagrams; a diagram and the document that embeds it

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and shallow: diagrams are few and belong beside the documents they illustrate. §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders."

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the diagram a person drew |
| **generated / not authored** | • diagrams generated from infrastructure code or discovery scans<br>• exported raster copies of the same authored diagram |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Exported raster copies are the practical hazard: they duplicate the authored source and, being images, carry weaker evidence than the source did. §2.9's duplicate and version-family signals are universal facts and P6's; this entry relies on them. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.technical-specification` | a diagram embedded in a specification travels with it; a standalone diagram does not | §3.11 "One file may hold facts from more than one domain without losing information." |
| `soft.it-asset-inventory` | a diagram of the estate and a list of the estate are two views of one thing | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 37. `soft.it-asset-inventory` — IT asset and inventory records

The list of what hardware and software exists, who has it, and what it is licensed for.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies: asset registers name people and their assigned equipment, and licence inventories carry licence keys. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `asset_class` | string | laptop | `possible` | NO design sentence names this field. Proposed. |
| `inventory_scope` | string | an organisation or site name | `possible` | NO design sentence names this field. Proposed. §3.8 "It should avoid using authorship or creator identity as a destination dimension." keeps an organisation name out of the dimension order. |
| `as_of_date` | date | a labelled date in the export header | `validated` | NO design sentence names this field. Proposed. `validated` only from a labelled header; §3.10 "The product must not use fuzzy date parsing because file names and documents frequently contain numbers that look like years but are course identifiers, version numbers, build numbers, ZIP codes, or other unrelated values." |
| `artifact_type` | string | inventory | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a tabular file whose header row carries asset-shaped labelled columns, TOGETHER WITH an inventory or asset directory - the header labels are the corroborating context and the table shape alone is not |
| **needs LLM** | • whether an inventory is the user's own, their employer's, or a vendor quote<br><br>• whether a spreadsheet of equipment is an inventory or a purchase record |
| **never alone** | • a `.csv` or `.xlsx` extension<br><br>• a serial-number-shaped token<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `asset register`, `licence inventory`, `assignment record`, `disposal record`, `audit export`

**Grouping reasons**: one inventory across its exports; one site's assets

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and uncertain: an asset inventory may belong under an administrative or work branch rather than a software one. §5.1 "a typical initial canvas might include Academics, Applications, Research, Career, Personal Records, Finance and Administration, Photos and Captures, Code and Projects, and Media or Miscellaneous Personal Material." lists Personal Records alongside Code and Projects and this entry could sit under either.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the inventory a person compiled and maintains |
| **generated / not authored** | • exports produced by a discovery or management tool - the ordinary case, and one that regenerates |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `career.onboarding-paperwork` | equipment assigned to a person by an employer is an employment record too. Cross-slice | §3.11 "One file may hold facts from more than one domain without losing information." |
| `fin.receipts-expenses` | an asset list and a purchase record overlap where the list carries prices; finance is a safety domain and §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" | §3.15 "Finance, identity, medical, and legal material should be implemented first as safety domains" |

---

### 38. `soft.helpdesk-ticket` — Helpdesk and support tickets

The record of someone asking for help and someone answering.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed.
- **sensitivity**: `potentially_sensitive` — §2.9's phrase applies directly and by the design's own words for this exact material: §2.9 "treating addresses and message content as potentially sensitive" A support ticket IS addresses and message content. §8.4 "identity documents, account statements, tax records, medical information, legal records, credentials, private correspondence, GPS metadata, employment materials, and educational records" names that material among what this product processes. Marked and stopped; the handling class and the gate are P7's.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `support_queue` | string | a queue or desk name | `possible` | NO design sentence names this field. Proposed. |
| `ticket_identifier` | string | a labelled ticket reference | `validated` | NO design sentence names this field. Proposed. `validated` requires the label with the reference, per catalogue 06's rule that 'a bare number is never an identifier'. |
| `artifact_type` | string | support ticket | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a structured export whose repeated objects carry support-shaped labelled keys (requester, queue, resolution) TOGETHER WITH a labelled ticket reference in the same document<br><br>• a mail export whose messages share one ticket reference in the subject - and note this makes it an EMAIL file first, which §2.9 governs: §2.9 "treating addresses and message content as potentially sensitive" |
| **needs LLM** | • whether a ticket is the user's own request or one they answered - two different roles, §3.8 "The system must separate roles that happen to contain the same entity type."<br><br>• whether a support thread is technical support, customer service, or an internal request |
| **never alone** | • a ticket-reference-shaped token with no label<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `ticket export`, `support thread`, `resolution note`, `knowledge-base draft`, `satisfaction survey`

**Grouping reasons**: one ticket across its messages; one queue's tickets

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED, and uncertain in the same way as `soft.it-asset-inventory`: support tickets may belong under a work or career branch rather than a software one.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • what the requester and the responder wrote |
| **generated / not authored** | • the export container<br>• automated acknowledgement and notification messages<br>• generated survey records |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Automated notification messages are the volume hazard here: a single ticket can generate many, and they carry the same ticket reference as the authored messages, so they group WITH the real thread rather than separately. That is arguably correct behaviour - the guard is that they must not anchor a group on their own, §4.9 "Sparse groups with no anchor should be shown only as tentative discovery candidates, if at all." |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.issue-ticket-export` | the brief's boundary: an engineering issue versus a support request. The tracker identity is the only reliable discriminator and it is often absent | §3.3 "have multiple plausible domains" |
| `career.correspondence` | support threads at work are also work correspondence. Cross-slice | §3.11 "One file may hold facts from more than one domain without losing information." |

---

### 39. `soft.user-documentation` — User-facing documentation

Documentation written for the people who use the software, not the people who build it.

- **provenance**: `inference`
- **design cite**: Extends §2.4 "structural indicators such as repository markers, package manifests, notebook metadata, and README files" which names README files as a structural indicator class, and catalogue 05's six README rows (`p5d-readme-md` and siblings, kind `README file`). §2.5 "A source-code archive may reveal a README.md, package.json, src directory, or Python package layout and can be recognized as a code project." also names README.md as a code-project signal. Making documentation a DOMAIN rather than a marker is the inference.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `project` | string | graphify | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `project` is literal. Validated because the rule is the root signal: §3.5 "becomes a course fact only when the engine finds a course-code pattern together with academic context" is the model - pattern plus corroborating context, and the corroborating context here is the marker-bearing root, not the file's own extension. |
| `documented_product` | string | a product name | `possible` | NO design sentence names this field. Proposed. |
| `document_title` | string | the document's own title | `direct` | The document's own title, which §3.13 "A direct fact was read from a reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled form field." names as a direct source. |
| `artifact_type` | string | user documentation | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a catalogue-05 README row at a directory root TOGETHER WITH the root signal - which is exactly the pairing §2.5 "A source-code archive may reveal a README.md, package.json, src directory, or Python package layout and can be recognized as a code project." describes for archives, applied to a directory.<br><br>• a documentation directory beneath a repository-marker root, TOGETHER WITH a documentation-site configuration file at that root |
| **needs LLM** | • whether a document is for users or for developers - the same file often serves both and the reader is rarely stated<br><br>• whether documentation describes the user's own product or a third-party one they saved |
| **never alone** | • a README alone. A README marks a directory someone wrote ABOUT - catalogue 05 carries it as EVIDENCE and refuses it as an exclusion root in `ref-readme-as-exclusion`, and the same restraint applies here<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `README`, `user guide`, `tutorial`, `reference page`, `FAQ`, `installation guide`

**Grouping reasons**: one product's documentation set; one document across its versions

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "a parent dimension should provide the context required to understand the child"

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the documentation people wrote |
| **generated / not authored** | • generated API reference pages built from source comments - typically the LARGEST file count in any documentation tree, and indistinguishable from authored pages by extension<br>• rendered site output under `build` or `dist`, both §1.1 literal names<br>• generated search indexes and navigation files |
| **template guard** | The generated API reference is this entry's defining hazard and the clearest case in the slice of generated material that looks authored: it is prose, it is markdown or HTML, it sits in the documentation directory beside hand-written guides, and it can outnumber them heavily. §1.1 catches only the RENDERED output, because that lands in `build` or `dist`; the generated markdown SOURCE usually does not. Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. This is the strongest single argument for the generated-file banner catalogue proposed at `authored_vs_generated_policy` - a generated reference page almost always carries a do-not-edit banner, and nothing else separates it from an authored one. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `soft.training-material` | documentation to consult versus material to teach FROM; a tutorial is genuinely both | §3.3 "have multiple plausible domains" |
| `soft.runbook-operational-doc` | the reader again - an end user versus an operator | §3.3 "have multiple plausible domains" |

---

### 40. `soft.training-material` — Technical training and teaching material

Material prepared to teach a technical subject to other people.

- **provenance**: `proposal`
- **design cite**: NO design sentence names this domain. Proposed. Adjacent design provision, which is why the collision below matters: §3.15 "The initial release should fully support only the domains required to validate the product on real heterogeneous corpora: academic coursework, college applications, research and lab work, career and recruiting, photos and captures, and code projects." makes academic coursework a launch domain, and teaching material produced BY the user is a different role from coursework produced FOR a course.
- **sensitivity**: `none` — No §2.9 sensitivity phrase applies.

**Schema** — the fields this domain and only this domain legitimises.

| field | type | example | reliability ceiling | why |
|---|---|---|---|---|
| `subject_taught` | string | a technical subject | `llm_supported` | NO design sentence names this field. Proposed. A subject stated in prose needs interpretation; §3.6 "A model that cannot cite sufficient evidence must return unknown." |
| `audience` | string | new engineers | `llm_supported` | NO design sentence names this field. Proposed, and it is the field that separates teaching material from documentation. It is prose-only, which is why this entry is weak. |
| `artifact_type` | string | training material | `validated` | §3.11 "Code files may use project, repository, programming language, and artifact type." -- `artifact_type` is literal, and it is the field that carries this whole supercategory. It is a SMALL controlled vocabulary at project scale, not a per-file type: it answers what kind of thing the project is, so the branch count is bounded by project count and not by file count. |

**Recognition**

| | |
|---|---|
| **deterministic** (pattern **plus** corroborating context) | • a slide deck or exercise set TOGETHER WITH a companion exercise or solution file of the same series - the PAIR is the corroborating context, and a lone deck is not enough |
| **needs LLM** | • the audience and the intent, both of which are prose<br><br>• whether a deck is training material the user delivered or a course they attended |
| **never alone** | • a `.pptx` or `.md` extension<br><br>• the word `training` in a filename<br><br>• [universal] a bare file extension - see `never_alone_universal` at the top of this file<br><br>• [universal] a bare camelCase or snake_case identifier token<br><br>• [universal] a bare version-shaped or number-shaped string<br><br>• [universal] a lock file on its own |

**Work types**: `slide deck`, `exercise set`, `solution set`, `workshop guide`, `recorded session notes`, `assessment`

**Grouping reasons**: one course across its sessions; one session across its materials

**Template**: `project` → `artifact_type` — time first: `false`

> PROPOSED. §5.5 "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders." -- so subject before any delivery date.

**Authored vs. generated**

| | |
|---|---|
| **authored** (this domain's material) | • the slides, exercises and notes a person wrote |
| **generated / not authored** | • rendered handout copies of the same deck<br>• generated certificates and attendance exports |
| **template guard** | Standard supercategory guard, stated in full at `authored_vs_generated_policy` and not repeated per entry: §1.1 removes the named directories and the four marker-rooted subtrees before scanning; this template's dimensions are project-scale so branch count tracks projects and not files; §5.9 "Before the user chooses a split, the system should show the resulting number of child branches, the number of files under each child, example members, unresolved files, and any evidence gaps." and §5.9 "It should warn when a level produces only one child, repeats a concept already expressed in the parent, creates excessive depth, or creates a large number of tiny folders." show the cost of a split before the user commits. Little generated bulk; the hazard is the rendered duplicate, which §2.9's duplicate and version-family signals handle and which is P6's. |

**Collides with**

| domain | signal | design cite |
|---|---|---|
| `acad.course-enrollment` | material the user TAUGHT versus material they were TAUGHT - the clearest instance of §3.8 "The system must separate roles that happen to contain the same entity type." in this slice, and the academic slice owns the receiving side. | §3.8 "The system must separate roles that happen to contain the same entity type." |
| `soft.user-documentation` | a tutorial serves both; the discriminator is whether there is an exercise or assessment component | §3.3 "have multiple plausible domains" |
| `hr.training-lnd` | training delivered as part of a job is a career artifact too. Cross-slice | §3.11 "One file may hold facts from more than one domain without losing information." |

---

