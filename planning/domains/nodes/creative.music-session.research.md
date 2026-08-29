# Research memo — `creative.music-session`

**Depth: J-DEPTH.** This is a non-refused placeholder template under the fieldless `creative` schema.

## Verdict

Keep the row. The node test passes on detection and organizational situation: this is not merely “audio files” or a mix file extension. A music-production neighbourhood has a distinctive lifecycle—session/tracking → take families and edits → stems → mix recalls → master → rights/metadata → delivery—and its working sessions commonly reference audio that is not embedded. The creative schema currently declares no field rows, so `fields`, proposed fields, and `dimension_order` remain empty. Universal facts such as file type, creation date, language, version family and sensitivity status remain legal; they are not music fields.

## Sources used

- `planning/00-database-agent-product-design.md` for universal facts, observation-versus-fact discipline, extensions as routing signals, local privacy, and the distinction between facts, groups, templates and residuals.
- `planning/prompts/ALIGNMENT.md` for creative's fieldless J-IND placeholder, work types as values, and the rule that grouping must not copy a course/project fact from a neighbour.
- `planning/domains/_CONTRACT.md` for the template node test, closed edge vocabulary, canonical-field restriction, residual names and field deferral.
- `planning/domains/CONNECTION.md` for activation as per-file evidence, collision versus also-holds, and browse-only parent semantics.
- `planning/domains/dispatch/make_prompt.py creative.music-session` for the stamped assignment and neighbour set.

## Files considered (bottom-up)

The JSON records eleven concrete fixtures. Together they cover a DAW session (`North Star_Song_04_Tracking.logicx`), take audio (`North Star_S04_Take_07_Vocal.wav`), comp/edit session (`S04_Vocal_Comp_R2.ptx`), mixed archive (`North Star_S04_Stems_2026-07-18.zip`), recall notes (`North Star_S04_Mix_Recall_03.pdf`), approved mix (`North Star_S04_Mix_04_Approved.wav`), master (`North Star_S04_Master_24bit_44k1.wav`), metadata and splits (`North Star_S04_Metadata_and_Splits.xlsx`), delivery QC mail (`North Star_S04_Delivery_QC.eml`), an unlabelled voice memo (`Voice Memo 2026-07-18.m4a`), and a picture sound-mix collision (`Harbour Film_Sound_Mix_05.aaf`).

The labelled files support only universal facts in this pass. A session title, track number, performer role, mix number or catalogue identifier is an observation and may support grouping; it does not become `project`, `stage`, `artifact_type`, rights, ownership or approval because the creative schema declares none. A sparse take can join the accepted song group without receiving the song fact from its neighbours. The archive timestamp is not the recording date, and `Approved`, `Master` and `FINAL` are not proof of commercial release or rights clearance.

The ugly cases are intentional. `Voice Memo 2026-07-18.m4a` demonstrates that an audio extension, date-like token and duration cannot activate a music session. `Harbour Film_Sound_Mix_05.aaf` demonstrates the reverse collision: an interchange session with tracks, stems and a mix can belong to picture sound, not a song. The spreadsheet and email demonstrate rights/operations material that may co-hold with the creative group while retaining their own legal or business interpretation.

## Node test, leg by leg

**Detection signals.** The row has a signal that the creative default does not express at this granularity: recording-specific structure. Take folders, playlists, overdubs, performer/track roles, song or release identifiers, stems, recall notes, and platform-specific masters form a bundle. A single WAV or DAW extension is never enough; activation needs recoverable links across the lifecycle or a clearly labelled music session plus corroborating neighbourhood evidence.

**Recommended dimensions.** No dimension can be authored. The lifecycle is documented as a recommendation for later template compilation, not a folder path: session/tracking, takes/edits, stems, mix/recall, master, rights/metadata, delivery. Recording date, mix date and release date are distinct clocks, so `time_first` is false. This differs from generic post-production by the kind of production evidence, not by a `.logicx` versus `.prproj` distinction.

**Privacy.** Unreleased songs, raw performances, private vocals, contributor identities, split sheets and delivery metadata can expose both the work and third parties. That posture is materially relevant even though it does not authorize a new field or handling class. The row therefore remains potentially sensitive and local-first.

## Boundaries and collision fixtures

The primary boundary is `creative.post-production`. `North Star_S04_Stems_2026-07-18.zip` and `North Star_S04_Mix_Recall_03.pdf` could activate generic post-production, but take/performer/song/release evidence makes the music reading specific. In the reverse direction, `Harbour Film_Sound_Mix_05.aaf` has tracks, stems and a mix but scene/timecode/picture evidence, so it must not become a music session.

`creative.sound-design` competes for the same audio vocabulary. Music uses song/release, takes, overdubs, instrumental/acapella and music delivery variants; sound design uses picture/game/installation cues, foley, effects and scene/timecode. `creative.podcast-episode` competes for recording/edit/mix/delivery, but episode/show cadence, transcript or publish evidence distinguishes it. `photos` is a boundary for phone/field recordings: capture metadata alone does not create a session. `career` may hold the same finished master as a portfolio or reel, but the purpose is self-presentation rather than making. `code` must own repository/build evidence even when generated audio is present.

Rights instruments and operational packets are `also_holds_with` legal or business_operations when the same file genuinely carries both roles. A signed split sheet remains a legal instrument; a label production packet can also be an operational record. This is not permission to copy legal or business facts into the fieldless creative row.

## Files considered and rejected as activation proof

- `Voice Memo 2026-07-18.m4a`: rejected as a session from extension, duration and date; it falls through to One-Off Images unless context recovers a recording group.
- `Harbour Film_Sound_Mix_05.aaf`: rejected as music because picture/scene/timecode structure points to sound design or post-production.
- A lone `Final Mix.wav`: rejected as approval, master or release evidence; the suffix is universal version-family noise without a linked lifecycle.
- A downloaded reference beat or sample: rejected as a current project without a session, take or delivery relationship; it falls through to Reference Clips.
- A split spreadsheet with unsigned percentages: rejected as agreed rights; it may group with the recording while remaining unresolved or legal/business evidence.

## Proposed fields

None. `project`, `stage`, and `artifact_type` are already discussed as creative candidates in the schema's proposal, but this row cannot ratify them. `work_type` and terms such as take, stem and master are values, not new fields or child nodes. A rights/usage field is a genuine open design issue, not a license to mint a synonym here.

## NEEDS-JOSEPH

1. Decide whether creative later adopts existing `project`, `stage` and `artifact_type` keys, or remains fieldless with lifecycle applicability assembled by graph/template passes. Recommendation: retain the placeholder until that schema decision is made.
2. Decide whether rights/usage should be a shared canonical facet or remain in legal/business records. Recommendation: do not mint a music-only key; preserve `also_holds_with` legal for signed instruments.
3. Decide how podcast, spoken-word release and music-session overlaps should be represented when one recording has both episode cadence and song delivery variants. Recommendation: allow overlap only with disjoint evidence or user confirmation.

## Ending claims

- This row recognizes a recording-and-production lifecycle, not audio extensions, artist names, or `FINAL` tokens.
- It remains a fieldless creative placeholder and writes no project, stage, work-type, rights or folder facts.
- It preserves the distinction between music recording, picture sound, podcast, photo capture, career presentation and code-generated audio.
- Unattached or ambiguous files fall through safely to Reference Clips, Review Later, Independent Records, One-Off Images, Protected Records or Unsupported or Encrypted.

## What changed in this pass

Authored the row from the stamped assignment, made the session→takes→mix/master→rights/delivery lifecycle explicit, added concrete labelled and unlabelled fixtures, and documented reciprocal boundaries with post-production, sound design, podcast, photos, career and code. No neighbouring file or shared catalogue was edited.
