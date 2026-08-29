# Research memo — `creative.film-production`

## Verdict

Keep this as a non-refused placeholder template on the fieldless `creative` schema. Film production is a real organizational situation because its evidence is a purpose-coherent, cross-format lifecycle: screenplay, preproduction records, shoot media, edit timeline, cuts, delivery package, and rights records. It is not a new schema and does not justify film-specific fields. The node's distinguishing contribution is the lifecycle signal and its collisions, while `dimension_order` remains empty under the creative-schema contract.

**Depth: J-DEPTH (first eight fixtures are the primary evidence set).** The ninth fixture is an additional collision check.

## Sources used

- `planning/00-database-agent-product-design.md`: files carry many facts; extensions are routing signals; audio/video and creative extractors expose metadata and structure; unsupported proprietary formats are indexed-but-unreadable; purpose is a first-class facet; groups are assembled from evidence and may overlap; residual destinations handle unsupported or ambiguous records; creative is a placeholder outside the launch domains.
- `planning/prompts/ALIGNMENT.md`: template versus schema distinction, work types as values, activation versus grouping, observation/fact separation, no path facts, residual behavior, and the no-invented-field rule.
- `planning/domains/_CONTRACT.md`: closed node shape, canonical-key discipline, fieldless creative placeholder rule, edge vocabulary, and sensitivity vocabulary.
- `planning/domains/roster.json`: assignment metadata and required neighbours `career`, `code`, and `photos`.
- `planning/domains/nodes/creative.json`: the creative default template is fieldless; its prose names project/stage/artifact type only as deferred candidates and emphasizes linked assets, revisions, briefs, delivery, production paperwork, scripts, timelines and rights structures.
- `src/evidence_shape/vocabulary.py`: source-type vocabulary used by the node.

## Files considered

The JSON contains nine concrete fixtures: screenplay, call-sheet spreadsheet, calendar schedule, camera-original MXF, edit project, picture-lock export, delivery archive, model release, and a director portfolio reel. Together they cover the whole proposed lifecycle and the ugly cases: labelled versus sparse files, calendar/contact-bearing records, mixed archive handoff, proprietary editing format, rights-sensitive paperwork, an overlapping photos case, and a career collision.

The key observation/fact boundary is deliberate. A title, extension, codec, `FINAL`, `PICTURE_LOCK`, camera date, or archive name is evidence only. Universal facts such as `file_type`, `creation_date`, `version_family`, `language`, `duplicate_family`, and `sensitivity_status` remain legal. Production identity, stage, artifact type, rights scope, approval, attendance, and publication are not written as domain facts because the creative schema declares no fields.

## J-DEPTH: first eight fixtures, bottom up

1. **`Harbour Lights - screenplay v5.fdx`** — labelled screenplay grammar is a strong development anchor; `v5` remains universal version evidence and does not prove financing, approval, or a shoot.
2. **`Harbour Lights - call sheet 2026-09-14.xlsx`** — labelled call time, scenes, location and crew roles establish preproduction paperwork; a schedule does not prove attendance or completion.
3. **`Harbour Lights - shoot schedule.ics`** — calendar structure can link planned calls and locations; an event record does not prove that the shoot happened.
4. **`A003_CamA_014.MXF`** — codec, timecode and slate frame make a camera-original candidate; the take is not thereby good, selected, or even part of a production without its neighbours. It may also carry photos/capture context.
5. **`Harbour Lights_Edit_v12.prproj`** — timeline bins and linked media are a distinctive edit-stage structure; sequence names do not establish approval or a creative field fact.
6. **`Harbour Lights_PictureLock_2026-10-03.mov`** — a named cut plus caption sidecar and review context supports an edit/review member; `PictureLock` does not prove public release.
7. **`Harbour Lights - delivery manifest and masters.zip`** — a manifest with masters, captions, poster and checksums supports a handoff set; packaging does not prove recipient acceptance or universal rights.
8. **`Model release - Mara Chen - Harbour Lights.pdf`** — a signed, role-labelled release makes the rights stage concrete; its terms apply only to named media, uses, territories and terms.

The ninth **`Selected Works 2025 - director reel.mp4`** is deliberately outside the first-eight lifecycle set: its curated multi-work framing activates the career collision rather than a film production.

## Lifecycle finding

The strongest production recognition is not one file but a recoverable chain:

`script → preproduction → shoot → edit → release/rights`

Each stage has characteristic evidence, but the chain is a grouping/retrieval reason rather than permission to copy the production name or stage onto every member. A call sheet may prove a scheduled event without proving attendance; a camera file may show a slate without proving a selected take; a picture-lock filename does not prove approval; and a signed release grants only the labelled scope. The node therefore records the lifecycle in deterministic signals, work-type values, grouping reasons, and the open question about a future typed graph view.

## Proposed fields

None. `proposed_fields` is empty because `creative` explicitly declares no field rows and the assignment is a placeholder. `project`, `stage`, and `artifact_type` are already canonical candidates in the creative default's prose, but adopting them is a schema decision owned upstream. Film-specific spellings such as `production`, `shoot_day`, `cut_type`, `rights_scope`, `cast`, or `location` would either mint synonyms or turn work types/roles into fields without authorization. The template consequently has no folder dimensions. If the schema is later ratified, the honest candidate order is `project → stage → artifact_type`; lifecycle names and media forms remain values.

## Neighbours and edges

- `career`: collision authored. A director reel or selected-works export can look like a delivery master, but its portfolio framing and multiple unrelated works make it career material.
- `code`: collision authored. Editing projects and media manifests can be structured, but repository markers and source files—not a timeline referencing media—activate code.
- `photos`: collision authored. Camera-origin video/stills share capture evidence; a film production needs script, production paperwork, timeline, or rights anchors, while a photo event can activate from capture/event evidence.

No `also_holds_with` edge was authored. The camera-original fixture records `also_schema: photos` as a concrete possible overlap, but the roster's reciprocal schema/template edge should be added only if the other node independently accepts the same evidence under its own rule. No edge was added to shoot-day, post-production, or rights rows because those are separate lifecycle views in the roster and are not required by this node's three assigned neighbours; duplicating them as edges would imply ownership or activation semantics the contract forbids.

## Residuals

Unanchored scripts, cuts, releases, or media fall to `Independent Records`; unresolved production membership or approval goes to `Review Later`; downloaded trailers/stock/reference footage goes to `Reference Clips`; rights documents with personal or contractual exposure go to `Protected Records`. These are residual destinations, not extra film nodes.

## Final claim

The production lifecycle is sufficient to keep the template. The row should remain a placeholder, fieldless, potentially sensitive, and cross-format. The product should eventually expose the lifecycle as reviewable graph structure, but should not create film-specific schema fields or a stage-first folder tree in this pass.

## Self-verification and claims

- The paired JSON parses and uses the stamped id, `schema_id`, closed node keys, `fields: []`, `proposed_fields: []`, empty dimensions, and `potentially_sensitive` posture.
- All eight primary fixtures separate observations from legal facts and use only universal keys; no production, stage, rights, cast, location, or media-specific field is asserted.
- The JSON includes the required lifecycle signals, work-type values, `career`/`code`/`photos` collisions, and residual fallthroughs. No invented edge or folder path is used.
- The final recommendation is intentionally bounded: retain the template as a placeholder and defer any creative-field ratification or typed lifecycle view to Joseph/R1c.
