# creative.performing-practice — J-DEPTH research memo

## Verdict

**REFUSE the node.** The archive described by the roster is real; the proposed template is not. A musician, dancer or actor genuinely accumulates programmes, scripts or parts, rehearsal notes, call sheets, set lists, session files, recordings, reviews, publicity, contracts and audition material. But the candidate distinction is an occupation/author label plus work-type and event values. The creative schema's default already says it covers work that is “performed”, recognizes script grammar, production paperwork, timeline-and-media project files, revisions and recordings, and groups “one shoot day, session or performance date and everything recorded on it.” There is no evidence class left for this row to own.

This is the exact failure the node test is meant to catch: a medium is not an organizational situation, a work type is a value, a date-shaped token is not an event fact, and the corpus owner's name must not become a collector. The legacy coverage for `perf.performing-artist` and `pers.music-practice` survives through the creative schema, narrower creative project/event templates when their positive evidence fires, the career/photos schemas where the same file legitimately carries their facts, and the residual library when no reliable association lands.

## Sources and authority stack

I used the binding stack named by the dispatch brief:

- `planning/00-database-agent-product-design.md`, the only design source quoted as authority.
- `planning/01-product-design-structured.md`, checked as a derived rendering only; no claim here depends on it over `00`.
- `planning/prompts/ALIGNMENT.md`, especially the separation of schema, template, grouping and residual, and its rule that work types are values rather than nodes.
- `planning/domains/_CONTRACT.md`, including the placeholder/no-field rule, snake_case, the closed edge vocabulary and the prohibition on a template copying schema fields.
- `planning/domains/CONNECTION.md` and `CONNECTION-EXAMPLES.md`, especially the three-leg node test, activation/grouping firewall, reciprocal-boundary requirement and browse-only `parent_id`.
- `planning/domains/canonical_fields.json`, confirming the six universal keys and that no creative performance/event key is licensed. No key was minted.
- `planning/domains/roster.json` and `ROSTER.md`, confirming this id, `schema_id: creative`, the `career`, `code`, `photos` neighbours, residuals, and absorbed legacy rows.
- `src/evidence_shape/vocabulary.py`, used to check every `source_type`.
- `planning/overnight/council/DECISION-BRIEF.md`: D1/PR-6 keeps this placeholder fieldless, D6 keeps keys snake_case, D4 forbids jurisdiction dimensions, and J-IND requires coverage without inventing a schema. J-DEPTH in the standing brief supersedes J-IND's retired gist label.

Calibration and nearest neighbours read: `creative.json` and its memo as the schema anchor; `creative.self-initiated-work` as the closest refused creative-practice row; `creative.creative-brief` and `creative.raw-photo-catalogue` for positive creative situation boundaries; `photos.camera-events`, `career.portfolio-work-samples`, and `code.software-project`; and `finance.crypto-assets.research.md` as the full launch-depth memo standard. `business_operations.organisational-records` supplied the exemplary refusal idiom, not the depth target.

## Node test — all three legs

### 1. Detection signals do not differ from the creative default

The strongest candidate fixtures were tested bottom-up:

- A programme labels production, venue, date, cast and credits. That can anchor an accepted performance group, but it does not prove that the corpus owner performed, and its structure is ordinary creative/publication evidence.
- A script or set of sides has strict scene/character/dialogue grammar. The creative schema already names this as a deterministic script structure.
- A call sheet labels production, call time, cast, crew and location. The creative schema already names production paperwork with exactly this shape.
- A DAW, editing or multitrack session refers to media by path and arranges tracks/takes on a timeline. The creative schema already names timeline-and-media and linked-asset structures.
- Same-stem takes, edits and exports form an intentional revision/version family. The creative schema already owns that structure.
- A recording, review, poster or press pack is an artifact of one named work/event. The creative schema already groups one work and one performance date with its recorded material.

After subtracting these defaults, the remaining tokens are performer/ensemble name, instrument, role, repertoire title, genre, venue, date, and words such as programme, part, rehearsal, recording or review. Every one is never-alone. They occur in citations, downloaded reference material, audience photographs, ticketing records, lessons, auditions, news coverage and other people's productions. The words are work types or topic values. They cannot activate a node.

The deletion test makes the refusal easy to audit: delete names, medium labels, date tokens and file extensions. The actual positive structures that remain are script, production-paperwork, linked-media, timeline, version-family and project/event-group structures. All are already the creative default. Nothing unique survives.

### 2. Recommended dimensions do not differ

The legal order is empty today. `creative` is a placeholder schema with `fields: []`, and the contract forbids a template branching on undeclared fields. `creation_date` is universal but not destination-eligible; it also names the file timestamp, not rehearsal/performance/publication date. Setting `time_first: true` would therefore be both unlawful and semantically wrong.

Conditionally, if R1c adopts the creative schema's existing proposals (`project`, `stage`, `artifact_type`, `client`), this row still does not become distinct. One production/performance is a project/event value; programme, part, recording and review are artifact/work-type values; rehearsal, performed, edited and published are stage values. The order would be creative's default: named work/event before stage or artifact. `00` gives the practical rule verbatim: “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.” Year/date first would split a single production across audition, rehearsal, performance, release and review dates.

The tempting extra level is performer. It is forbidden in substance even if a key existed. `00`: “It should avoid using authorship or creator identity as a destination dimension. A folder should not become a collection point for everything produced by the same person or organization. Authorship is usually metadata; the document’s purpose, project, subject, or target is more informative for placement.” On a performer's own disk, that level has one child and adds no retrieval value.

### 3. Privacy rules do not differ

The archive ranges from public programmes and reviews to private self-tapes, cast contact sheets, contracts, location schedules and unreleased recordings. That mixed posture is real but already belongs to creative's schema-wide policy. Public evidence does not propagate a public classification to neighbouring bytes. A call sheet can expose phone numbers and precise locations; a private rehearsal recording exposes likeness and voice; a contract exposes commercial terms. The refusal retains `sensitivity: potentially_sensitive` so it cannot be misread as a relaxation, but no unique handling rule distinguishes this template.

The photos and career co-activations reinforce the point. A performance recording may carry photo/media facts, and an audition self-tape may be a career work sample. That is set-valued schema activation, not a new privacy regime and not a reason to mint a performing-practice node.

## The concrete file corpus

The JSON carries twelve fixtures. The first eight deliberately cover the required depth before the tail cases:

1. `Hamlet - Riverside Theatre - 2026-03-14 programme.pdf` — labelled happy case, but a cast list does not identify the owner.
2. `Ophelia sides - Act 3.pdf` — sparse file; it may join a production group without receiving copied event facts.
3. `Riverside Hamlet call sheet 2026-03-14.pdf` — structured production paperwork and the sensitive-contact case.
4. `Hamlet rehearsal notes 2026-03-08.docx` — free prose plus unreliable author metadata.
5. `Hamlet_20260314_multicam_v4.prproj` — linked-media/timeline structure and version evidence, already creative default.
6. `Hamlet curtain call take 04.mov` — recording that may also activate photos; no performer slot.
7. `Review - Hamlet at Riverside - City Arts Weekly.pdf` — the publication/citation-role collision fixture.
8. `Hamlet press pack.zip` — archive packet with mixed members; facts are not copied across the manifest.
9. `Blue Note set list 2026-05-09.jpg` — OCR and EXIF; venue/date readings remain ambiguous.
10. `piano-practice-2026-05-09.m4a` — the absorbed `pers.music-practice` fixture; "practice" is a topic/work-type value, not a situation.
11. `Dance showcase poster final.png` — flat promotion that proves neither authorship nor participation.
12. `Hamlet audition self-tape.mp4` — career work-sample collision; audition for a role is not evidence of having performed it.

Every fixture lists all six universal keys as the only legal facts: `file_type`, `creation_date`, `language`, `duplicate_family`, `version_family`, `sensitivity_status`. This is deliberate. The creative schema declares no fields, so writing project, event, venue, performer, role, stage or artifact facts would violate the allow-list. Some observations may remain possible clues or group evidence; they are not licensed facts in this row.

Three sparse cases set `group_without_copying_facts: true`: the sides, the curtain-call recording, and the photographed set list. This follows `00`'s firewall: graph/neighbourhood membership may support a reviewable group but cannot silently propagate a programme's date, venue or cast onto bytes that do not carry them.

## Files considered and rejected

These tempting files were considered and excluded as evidence for this row:

- A concert ticket or booking confirmation. It is a transactional document for an attendee unless other evidence establishes the holder's production role; otherwise `Receipts and Confirmations`, not a practice archive.
- A downloaded cast recording or soundtrack. Performer names and album tags describe its content and rights metadata, not the corpus owner's work.
- A phone video from the audience. Camera event/home video evidence belongs to photos; visible performers do not establish the filmer's creative role.
- A music lesson handout, scale sheet or annotated score. It may be academic/instructional or reference material. Instrument and repertoire words do not establish an event or project.
- A streaming playlist export. It records listening, not making or performing.
- A venue calendar `.ics`. Calendar is a `SOURCE_TYPE`; event title/date/location do not establish participation, and format is never a domain.
- A ticketing email or “doors at 7” confirmation. Transactional evidence belongs to `Receipts and Confirmations` unless it is production paperwork with a labelled role.
- A publicity portrait. Photos schema facts may be true, but a portrait does not prove performance practice or one production.
- `package.json` for a show-control, audio-plugin or portfolio site repository. The theme is performance; the structure is code. Code wins on repository markers.
- A union membership card or professional credential. Career/identity or protected-record evidence, not a performance event.
- An invoice from a venue or promoter. Finance/business evidence may help a project group, but the invoice's role is transactional and the creative schema must not copy its counterparty onto the performance files.
- A review mentioning the same production only in comparison. This is the collision fixture inside fixture 7: mention is not membership.

## Reciprocal boundaries

Because the node is refused, it authors no `collides_with` edges: a nonexistent template cannot be a mutex endpoint. The boundaries still matter and are stated reciprocally for R1c.

### Creative schema/default

Same bytes: the programme, call sheet, rehearsal notes, multitrack/edit session, recording and review. From this row toward creative: all positive structures are creative default evidence; nothing remains to discriminate. From creative toward this row: medium/occupation words cannot narrow the schema into a new template, and one performance is a project/event group value. This is the boundary that refuses the node.

### `creative.self-initiated-work`

Same bytes: `piano-practice-2026-05-09.m4a`, a home rehearsal recording, and an uncommissioned showcase poster. From performing-practice toward self-initiated-work: absence of a client does not prove personal purpose. From self-initiated-work toward performing-practice: performance vocabulary does not prove a distinct personal-practice situation. That neighbour is already refused for the same negated-evidence and author-as-collector reasons, so no edge is appropriate.

### Creative project/event neighbours

The narrower production, shoot-day, post-production, exhibition/showcase, commissioned-work and deliverable templates keep files only on their own positive structures: a brief/client role, one bounded production/day, a persistent editing workflow, a public presentation package, or a handoff set. This refused row keeps nothing in the reverse direction. Missing client/event evidence means schema-default evaluation then residual, never “performer's practice”. Fixture shared on the seam: `Hamlet_20260314_multicam_v4.prproj`; a timeline proves post-production structure, not who performed.

### `career` / `career.portfolio-work-samples`

Same bytes: `Hamlet audition self-tape.mp4`, a showreel, biography and review clipping. From the refused row toward career: an audition tape or selected excerpt is a career work sample when its purpose is applying/showcasing, not evidence of a dated performed event. From career toward this row: a programme or review can document experience, but employment/portfolio use does not make the work itself a separate performing-practice template. The self-tape may legitimately carry both creative and career schemas; that is `also_schema` on the file, not a mutex.

### `photos` / `photos.camera-events`

Same bytes: `Hamlet curtain call take 04.mov`, `Blue Note set list 2026-05-09.jpg`, poster scans and publicity photographs. From the refused row toward photos: EXIF/capture facts and media type remain photos facts; performance content must not overwrite them. From photos toward this row: a camera event can record a performance without the photographer or corpus owner being the performer, and visible faces/name OCR do not establish authorship or participation. Co-activation is legal; collision is not.

### `code` / `code.software-project`

Same topical vocabulary but not the same evidence: show-control repositories, audio plugins, generative performance code and a portfolio site may name productions, performers and venues. From the refused row toward code: repository markers, manifests and source structure are code evidence and cannot be stolen by subject matter. From code toward this row: a `.prproj`/DAW session is a creative timeline/linked-media project, not a software repository merely because it is structured or proprietary. No shared discriminating bytes warrant an edge; the boundary is clean.

### Residuals

`Independent Records` keeps durable standalone programmes, certificates and notices with no broader group. `Review Later` keeps sparse sides, rehearsal notes, recordings and mixed packs whose meaning is partly understood but association is unresolved. In the reverse direction, residual membership is never evidence for creative activation. These are fallthrough destinations, not schemas or nodes.

## Proposed fields and work types

`proposed_fields` is empty. This row neither declares nor adopts fields. The tempting keys were rejected:

- `performer`, `ensemble`, `instrument`, `role` — identity/role/search values; performer would be authorship as a destination collector.
- `performance_date` — the design licenses `creation_date` and photos' capture fields, neither of which means event date. Reusing either would corrupt semantics; minting a date key here would pre-decide a cross-schema vocabulary question.
- `venue` — canonical today in the research schema as a publication venue. A theatre or music venue is a different role/value universe, and overloading it from a single placeholder row would be silent schema expansion.
- `event` — canonical only as a photos field in the current catalogue. Whether creative should share it is NJ-CPP-1, not this row's decision.
- `project`, `stage`, `artifact_type` — already proposed by the creative schema; this row adds no reason or reliability rule beyond the schema default.

`work_types` is empty because the node is refused. Programme, part, script, score, set list, rehearsal note, call sheet, recording, take, review, press pack, self-tape and showreel remain possible values for a future creative `artifact_type`/`work_type` decision; listing them on a refused node would make the node look like their owner.

## Neighbours considered that did not get an edge

- `career`: considered and represented as per-file co-activation, not a template collision.
- `code`: considered; repository structure and creative timeline structure are cleanly separable.
- `photos`: considered and represented as per-file co-activation; capture facts coexist with creative evidence.
- `creative.self-initiated-work`: no edge because it is also refused and absence of client is not positive evidence.
- `creative.raw-photo-catalogue`: no edge; catalogue/sidecar/index structure is distinct from performance content.
- `creative.creative-brief`: no edge; a brief's labelled deliverables/purpose structure is positive and this row has no competing structure.
- `academic` music/theatre coursework: considered but no edge. A score or rehearsal note in a labelled course context belongs to academic facts; performance words alone are not a conflict.
- `travel` and event tickets: no edge; attendance/booking evidence is transactional or travel context, not participation.
- `finance`/business operations: invoices, contracts and settlements may support a creative group but retain their own schema evidence. No copied client/venue fact is licensed here.

## Exact quotation audit

All quotation marks in the JSON and this memo refer to exact spans checked in `00` or to exact prose in the landed creative schema explicitly attributed as that sibling's claim. The key `00` spans are:

- “A model that cannot cite sufficient evidence must return unknown.”
- “A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact.”
- “It should avoid using authorship or creator identity as a destination dimension.”
- “For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders.”
- “Independent Records may live under Personal/Independent Records and hold standalone certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader group.”
- “Review Later may hold files whose meaning is partly understood but whose final location requires a future decision.”

No threshold, score, statistic, handling class or detector regex is asserted.

## NEEDS-JOSEPH

### NJ-CPP-1 — what represents a performance occurrence?

The hint says the performance is the unit and the date is its name, but no current creative field can represent that fact. Alternatives:

- Keep the occurrence entirely as a P9 accepted group anchored by labelled programme/call-sheet evidence; members retain only their own facts.
- Reuse `project` after R1c adopts it for creative, treating one production/performance occurrence as a project value.
- Propose a cross-schema `event` fact shared with photos, with a separate event-date question.

The choice affects creative generally, not this refused row. None makes performing-practice a distinct situation; each describes the creative default's event/project material.

### NJ-CPP-2 — template/schema co-activation expression

An audition self-tape and showreel may legitimately activate both creative and career; a performance video/photo may activate creative and photos. The contract permits `also_holds_with` only between schemas, while this is a template row and is refused. The JSON uses per-file `also_schema` and authors no edge. R1c should confirm that this is the intended expression and should not invent same-kind collision edges merely to force reciprocity.

## Self-verification and claims

- JSON parses with `python3 -m json.tool`.
- The top-level key set matches the landed creative template shape exactly.
- `fields: []`; `proposed_fields: []`; no canonical or private field was minted.
- Twelve specific file examples are present; the first eight cover labelled document, sparse prose, sensitive form, free prose, creative project, audio/video, collision publication and mixed archive.
- Every fixture separates observations from facts and lists only the six universal keys as legal facts.
- Every `source_type` is in `SOURCE_TYPES`; extensions are never treated as sufficient.
- Sparse fixtures use `group_without_copying_facts` and write no inherited event/project facts.
- `collides_with`, `also_holds_with`, and `role_split` are empty because the node is refused and no legal edge should target it.
- Both residual targets are exact names from `00`.
- The refusal argues detection, dimensions and privacy separately, names rejected files, states reciprocal boundaries and includes a collision fixture.
- No thresholds, scores, statistics, field rows, handling classes, fabricated quotes or folder paths as facts.
- Only `creative.performing-practice.json` and `creative.performing-practice.research.md` were written.

**Final claim:** `creative.performing-practice` should remain a refused placeholder id for audit/legacy coverage. Its material is covered; its node is not justified.
