# Shoot-day media — research memo

**Depth: J-DEPTH.** Mechanical depth marker; the placeholder boundary and substantive findings are preserved.

## Verdict

**Keep as a placeholder template; do not refuse.** This is a real organizational situation, but it is not a new schema. The distinctive unit is a capture-day production packet: call sheet and schedule, camera/sound capture, production report, rushes or dailies, metadata and selects, then a handoff manifest. The same-day chain is materially different from the Photos schema's ordinary event evidence and from a later post-production project file. Because the roster's `creative` schema is explicitly a placeholder with no inherited field keys, this node writes no fields and no folder dimensions.

## Sources used

- `planning/00-database-agent-product-design.md`: evidence is stored before domain placement; image EXIF, capture time and GPS can support photo-event proposals; audio/video extraction yields container and codec metadata; archives yield manifests; a file is a record with many facts; templates recommend dimensions but do not freeze a path.
- `planning/prompts/ALIGNMENT.md`: templates are organizational situations, grouping is separate from domain activation, and sparse files must not receive facts copied from their neighborhood.
- `planning/domains/_CONTRACT.md`: closed JSON shape, placeholder-schema boundary, residual names, `SOURCE_TYPES`, and no invented thresholds or handling classes.
- `planning/domains/roster.json` and the stamped `make_prompt.py` assignment: `creative.shoot-day-media` is a `template` on `creative`, launch `placeholder`, with no inherited fields.
- `src/evidence_shape/vocabulary.py`: source-type vocabulary used for the examples.

## Capture chain tested

The examples cover a call sheet, card manifest, camera original, sound roll, production report, archive of dailies, metadata sidecar, selects and handoff manifest. They also include the hard boundary fixture `IMG_4821.JPG`: camera EXIF and a set-like image can support ordinary Photos facts but do not establish production-day media without a call sheet, slate, production report or equivalent anchor. A calendar or email can supply planned context, but cannot make unrelated media part of a shoot.

The recommended operational sequence is therefore:

`call sheet / schedule → card and sound capture → rushes / dailies → metadata and selection → checksum-backed handoff`

That sequence is a grouping rationale, not a claim that facts may be copied from one file to another. A sparse clip may join a reviewed group through card, reel, slate or manifest relationships while its own unsupported project or event facts remain unknown.

## Fields and dimensions

`fields` and `proposed_fields` are intentionally empty. Existing canonical keys such as `project`, `stage`, `artifact_type`, `event`, `capture_year` and `media_type` may be relevant in a future creative schema, but this placeholder is not authorized to promote them into the creative schema or to invent a private production-day vocabulary. Accordingly `dimension_order` is empty and `time_first` records the proposed capture-day orientation without creating a folder level.

## Neighbours considered

- `photos`: considered for the ordinary event-photo boundary. The node does not author an edge because the template row cannot use `also_holds_with` to a schema, and the decisive distinction is a production anchor rather than a mutex over the image itself. The example marks the image as `also_schema: photos`.
- `creative.commissioned-shoot`: considered as a client/job-level sibling. A commissioned shoot may contain this capture-day packet, but this node is about the media-day evidence chain and can also cover personal or documentary production. No edge is authored because reciprocal same-kind collision evidence is not established here.
- `creative.raw-photo-catalogue`: considered as the long-term camera-original archive. That template organizes an archive/catalogue over many events; this node handles one capture-day packet and its handoff. No edge is authored.
- `creative.film-production`: considered as the production-wide container. This node is a narrower day-level slice inside or alongside that production and must not imply a full script/schedule/cut structure. No edge is authored.
- `creative.post-production`: considered for selects and dailies. Post-production owns the assembly/editing process; this node owns the source-day handoff. No edge is authored.
- `career`: considered for client/engagement records. Client, contract, rate and rights facts are not written here; a handoff filename mentioning a client is not enough to activate career.
- `code`: considered because media may include sidecars, manifests or checksum files. File format or machine-generated metadata is not a code project signal.

## Files considered and rejected as activation anchors

- An isolated `IMG_*.JPG` with EXIF: valid Photos evidence, not shoot-day media.
- A bare `Day 1` folder: a naming hint only; it lacks a production anchor.
- A standalone calendar invite: planned context, not proof that media was captured.
- A single `.mov`, `.wav` or `.zip` extension: format routing only; extensions never establish meaning.
- A final branded export with no card/roll or production-report link: may be a deliverable, but does not establish this capture-day packet.

## NEEDS-JOSEPH

1. Decide whether personal/documentary production days should remain eligible for this template, or whether activation must require a client/production anchor. The current conservative rule accepts a production anchor without assuming a paying client.
2. Decide which future creative fields, if any, are allowed to become destination dimensions. Until the creative placeholder schema is resolved, this node must remain fieldless and dimensionless.
3. Decide whether handoff manifests should later also activate a rights/licensing or career template when they mention recipients, clients or usage restrictions; this node intentionally does not infer those facts.

## Contract notes

`planning/domains/CONNECTION.md` reinforces that activation is independent of grouping and that template rows point to exactly one schema. The prompt's `file_kinds` output shape is used as stamped; no non-contract edge or handling-class vocabulary was added.
