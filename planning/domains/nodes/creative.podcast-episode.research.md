# Research memo — `creative.podcast-episode`

**Depth: J-DEPTH.** This is a non-refused placeholder template under the fieldless `creative` schema.

## Scope and sources

This is the R1b pass for the roster row `audio.podcast-episode`, absorbed as the template
`creative.podcast-episode`. I read `planning/00-database-agent-product-design.md`,
`planning/01-product-design-structured.md`, `planning/prompts/ALIGNMENT.md`,
`planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`,
`planning/domains/canonical_fields.json`, `planning/domains/ROSTER.md`, and the source-type list in
`src/evidence_shape/vocabulary.py`. I also compared the landed creative rows
`creative.client-engagement`, `creative.deliverable-handoff`, `creative.music-session`,
`creative.sound-design`, `creative.post-production`, and `creative.motion-graphics`.

The design gives the important media premise: audio/video extraction may yield “duration, container
and codec metadata, creation time, embedded tags, subtitles or captions where present, and—only under
an explicit privacy and compute policy—speech-to-text transcripts.” It also says that every extractor
must emit the same evidence shape and that an extension is a routing signal rather than meaning. Those
sentences support the file-level observations below; they do not license a podcast field. The design
also makes purpose and grouping first-class: a bounded, purpose-coherent packet can contain different
file types, but a session or co-occurrence is retrieval evidence rather than proof. Since `creative`
is a ratified field-less placeholder, this row writes `fields: []` and `proposed_fields: []`.

## Bottom-up file inventory

The following are concrete fixtures for this situation. “Facts legal” is intentionally empty: the
active schema has no legal field rows. Episode, season, host, guest, lifecycle stage, and release state
are work-type or contextual observations until R1c ratifies a field. A group may still use them as
evidence without copying them as facts.

| File | Type / extensions | What the extractor can observe | Facts legal / must remain unknown | Residual |
|---|---|---|---|---|
| `S03E04 - Rivers and Resilience - episode brief.docx` | `text_document`; `.docx` | Labelled episode title and guest; angle, questions, record date, ad-read, deliverables, and release-window sections; host/producer role slot | Legal: none. Unknown: recording happened, acceptance, release, rights, or a path from the proposed date | Review Later |
| `Rivers_Resilience_guest-release_signed.pdf` | `text_document`; `.pdf` | Episode/show/guest named in a release, permitted uses, and signature block; no audio | Legal: none. Unknown: recording, publication, ownership, exclusivity, and legal effect beyond text | Protected Records |
| `S03E04_remote-recording_multitrack.zip` | `archive`; `.zip` | Readable manifest lists host and guest WAV tracks, room tone, session file, and cue sheet; shared episode stem | Legal: none. Unknown: member semantics beyond manifest, editing, approval, and rights. Archive must be inspected without extraction, per design | Review Later |
| `S03E04_Rivers_Resilience_edit_v2.rpp` | `audio_video`; `.rpp` | DAW project has labelled voice tracks, edit regions, episode marker, and references to matching raw stems; `v2` is a version observation | Legal: none. Unknown: approval, release, licensing, and whether references resolve | Review Later |
| `S03E04_Rivers_Resilience_master.mp3` | `audio_video`; `.mp3` | Media metadata has title/show-like album values; speech contains host introduction and guest interview; hash differs from edit project | Legal: none. Unknown: public release, approval, rights, and canonical-master status | Independent Records |
| `S03E04_Rivers_Resilience_transcript.vtt` | `text_document`; `.vtt` | Time-coded host/guest speech; show and episode in header; cue timing aligns with master duration | Legal: none. Unknown: authoritative verbatim status, consent, publication, and whether alignment is accidental | Independent Records |
| `S03E04_show-notes-and-links.md` | `text_document`; `.md` | Episode/season front matter, summary, guest links, sponsor copy, chapter timestamps, and draft marker | Legal: none. Unknown: publication; links do not prove endorsement or guest relationship | Review Later |
| `podcast-feed-export-2026-08-24.xml` | `text_document`; `.xml` | RSS item has title, description, enclosure URL, GUID, explicit status/date; enclosure refers to master; neighboring items also occur | Legal: none. Unknown: local canonical copy, permanence, and whether all feed items belong to this packet | Independent Records |
| `Guest interview booking.ics` | `calendar`; `.ics` | Event title names guest/topic; organizer/attendees and proposed time are structured; no linked recording/release | Legal: none. Unknown: acceptance, attendance, recording, episode identity, and guest facts from title alone | Review Later |
| `Guest_Leah_Martin_media_kit.pdf` | `text_document`; `.pdf` | Biography, headshot, speaking topics, contact details; may mention podcast appearance generically | Legal: none. Unknown: that this episode exists or that the person consented | Independent Records |
| `S03E04_episode-artwork.png` | `image`; `.png` | Square title artwork and show logo; no camera EXIF required; may be a design export | Legal: none. Unknown: episode production, publication, and whether artwork is final | Independent Records |
| `S03E04_publish-checklist.xlsx` | `spreadsheet`; `.xlsx` | Rows for master, transcript, artwork, title, description, platform, and release state; checkboxes and owner column | Legal: none. Unknown: checked rows are not proof unless the sheet identifies evidence; platform status needs platform record | Review Later |

The ugly cases matter. A booking calendar is a plausible anchor for retrieval but not production. A
master can be a finished private test or a speech recording from a meeting. A transcript can be a court
or lecture transcript. The archive is mixed and must remain a manifest observation. A screenshot of a
player page would be `image` or `ocr` and could be episode evidence only when positive page identity and
episode linkage are visible; missing EXIF is never proof of screen origin. A contacts export for a guest
is privacy-sensitive and is not independently an episode anchor.

## Why this is a template, not a refusal

### Detection signals

The creative default can hold creative material, but this situation has a narrower, repeated program
lifecycle. A role-bearing episode brief or booking can open a candidate; multitrack/session evidence
can establish recording; a DAW project and rendered mix create version-family continuity; transcript and
show notes supply editorial derivatives; and a feed item, platform export, or release checklist tied to
the exact master supplies publication evidence. No one extension or token does this. This is a
purpose-coherent media packet whose members answer one another across stages. That is materially
different from a generic creative file and from the default’s open-ended making record.

The strongest deterministic rule is conjunctive: episode-specific identity or show/guest continuity,
speech-led production evidence, and at least one lifecycle link to edit, transcript/show notes, or feed
publication. The rule produces candidates, not asserted facts. It follows the design’s distinction
between observations and facts and keeps sparse files as group candidates. A release document can be
also-held by legal; its signature does not turn the episode node on without media or publication
evidence.

### Recommended dimensions

There are no dimensions at launch because the parent schema has no fields. The JSON therefore leaves
`dimension_order` empty and explains the deferred recommendation in prose. If R1c later licenses a
canonical episode/show identifier, the intelligible order would be show or series → episode identity →
work type/lifecycle value; a release state should remain a value, not a child schema. Recording date,
edit date, and publication date are distinct clocks, so `time_first` is false. This is a recommendation
for later template construction, not a filesystem path and not a claim that a user must organize this
way. The design explicitly says the template is a recommendation mechanism and warns against empty or
one-child levels.

### Privacy

This node differs from the default in privacy exposure as well as signals: unreleased interviews,
personal guest data, consent and rights documents, sponsor terms, private feeds, platform credentials,
and copyrighted music or clips can coexist in one packet. Public release of an episode does not make
raw takes, contact cards, or signed releases public. The catalogue only records `potentially_sensitive`;
P7 owns handling classes and gates. Pre-model processing should use the minimum excerpt and suppress
raw audio/transcript previews where not needed.

## Neighbour boundaries and collisions

### `creative.music-session`

Both rows may contain WAV stems, DAW sessions, cue sheets, mixes, and a studio name. The collision
fixture is `S03E04_remote-recording_multitrack.zip`: its bytes could be misread as a music session if
the detector sees only multitrack audio. Host/guest speech, spoken-program continuity, and matching
transcript/show-notes/feed evidence discriminate podcast production. Conversely, a music-session
archive with performer, instrument, song, take, and album-production markers belongs to music-session
even if it has a spoken count-in. This row must not steal a music recording; music-session must not
steal a podcast packet because of `.wav` or `.rpp`.

### `creative.sound-design`

Both can contain edited audio, stems, cue sheets, and rendered masters. `S03E04_Rivers_Resilience_edit_v2.rpp`
is the collision fixture: a DAW project without its speech/show context is ambiguous. Episode lifecycle,
host/guest continuity, transcript, show notes, and feed linkage support this node. Picture-lock cues,
effect names, Foley layers, library delivery, or client sound brief without a spoken program support
sound-design. Podcast must not infer sound-design from an ad marker; sound-design must not infer an
episode from a generic master.

### `creative.post-production` and `creative.motion-graphics`

An MP4 can be a video podcast, a post-production export, or a motion-graphics render. For this row,
`S03E04_Rivers_Resilience_master.mp3` plus its transcript and feed item is an episode fixture; a camera
original plus edit timeline and picture-lock notes is post-production. A waveform animation, title
sequence, keyframes, and render composition support motion-graphics. Neither neighbour should copy
episode identity from a filename, and the podcast node should not claim a video just because it has
spoken audio.

### `photos`

Podcast artwork or behind-the-scenes photographs may also carry photo evidence. `S03E04_episode-artwork.png`
can be an episode member while `photos` owns positive capture evidence when present. A screenshot of a
player page has to show screen chrome or other positive screen-origin evidence; absent EXIF is not a
podcast or screenshot signal. Photos must not take an exported cover image solely because it is `.png`,
and podcast must not convert camera metadata into episode facts.

### `career`

`Guest_Leah_Martin_media_kit.pdf` is a collision fixture: it may mention an appearance but is a
professional biography/media kit, not episode production. Career owns the person’s professional record;
this row owns the episode packet. A guest name, host title, or byline alone is never enough for either
side. A published episode may also be a career work sample, but portfolio selection requires separate
evidence and is not inferred here.

### `code`

Podcast sites and feed tooling can include XML, JSON, scripts, or repositories. `podcast-feed-export-
2026-08-24.xml` is episode evidence only because it contains a feed item and enclosure tied to a master;
a repository with package manifests, tests, and deployment configuration is code. Code must not steal
the feed because it is XML; podcast must not claim automation source files as media production.

### `creative.content-marketing` and `creative.client-engagement`

A branded podcast can also be a campaign deliverable, and a commissioned series can also be a client
engagement. The same master, show notes, or sponsor brief may legally carry both schemas. Content-marketing
owns campaign/distribution purpose; client-engagement owns commissioner–maker relationship and acceptance;
podcast owns the episode’s production lifecycle. A branded episode without an evidenced campaign remains
podcast; a marketing campaign without recording/transcript/feed evidence remains content-marketing.

### Legal and residual boundaries

`Rivers_Resilience_guest-release_signed.pdf` is also legal. Legal owns instrument, parties, and legal
status; the episode node only records its evidenced relationship to the packet and does not infer
ownership or enforceability. If no episode packet fires, a release or consent can fall through to
Protected Records. A standalone feed export, transcript, or master falls to Independent Records. A
booking, pitch, generic archive, or unresolved final-looking file goes to Review Later. An unreadable
encrypted DAW project or archive goes to Unsupported or Encrypted without semantic invention.

## Recognition discipline

The JSON’s `never_alone` list is deliberately broad. `Brief.pdf` is the primary collision fixture: its
tribunal caption, case identifier, argument headings, and counsel signature make it a legal document,
despite the shared word “brief.” `Podcast episode.mp3`, an RSS URL, or a guest contact card is equally
insufficient alone. The engine should preserve raw observations, normalized candidates, locations, and
reliability states; only a direct labelled slot or structured feed field can be direct evidence. Filename
tokens, free prose, OCR, and embedded tags remain possible until a rule or bounded model review confirms
the role. A nearby group can supply retrieval context, but it must not copy episode or guest facts onto
`S03E04_master.mp3` merely because it sits next to a brief.

## Proposed fields

None. `fields: []` is required by the assignment and by the ratified creative schema decision. The
tempting candidates—`episode`, `show`, `season`, `guest`, `release_status`, and `recording_date`—are
not minted as proposals because the roster’s placeholder contract explicitly defers creative fields.
R1c should decide whether one canonical identifier can cover show/series and episode without creating
parallel keys, and whether lifecycle and release are values of `work_type` or a future field. No field
is copied from career, code, photos, or legal.

## NEEDS-JOSEPH

* **NJ-POD-1:** Confirm that the lifecycle conjunction (booking/consent, recording, edit/master,
  editorial derivative, release evidence) is enough to distinguish this template from the field-less
  creative default. If not, choose refusal and route isolated audio to residuals.
* **NJ-POD-2:** Decide whether a future canonical `episode_id`, `series`, or equivalent single key is
  required, and whether episode number is an observed value rather than a folder dimension. The row
  must not mint synonyms.
* **NJ-POD-3:** Resolve reciprocally with `creative.music-session` and `creative.sound-design` how
  spoken-word recordings with commissioned music beds, sonic logos, or designed effects split or
  also-hold.
* **NJ-POD-4:** Resolve reciprocally with `creative.content-marketing` and `creative.client-engagement`
  how a branded or commissioned podcast shares the same bytes without copying campaign, client, or
  legal facts into the episode template.
* **NJ-POD-5:** Decide whether a remote enclosure or feed export may establish release membership when
  the local master is absent, and how replaced, scheduled, private, or taken-down episodes are recorded
  without treating platform state as permanent truth.
* **NJ-POD-6:** Confirm privacy treatment for guest contact cards, consent documents, raw interviews,
  and transcripts before any speech-to-text or connector retrieval occurs.

## Self-verification

The assignment helper was run with `python3 planning/domains/dispatch/make_prompt.py
creative.podcast-episode`. The JSON is a single node object with the required universal keys,
`kind: template`, `schema_id: creative`, `launch: placeholder`, empty fields, and only roster or
residual names in edges. Every example uses one of the exact vocabulary source types; no example writes
a folder path as a fact; every edge distinguishes observation from conclusion; and no threshold,
confidence score, handling class, or fabricated design quotation was added. The only intended writes are
`creative.podcast-episode.json` and this memo.
