# `creative.game-art-asset` — lab notes

Row: template on `creative` · `launch: placeholder` · `refuse_node: false`  
Absorbs: legacy `soft.game-development-asset` (ROSTER.md fold)  
Depth: full R1b — **J-DEPTH** (first eight fixtures are the primary evidence set)

## Sources and operating constraints

I ran `python3 planning/domains/dispatch/make_prompt.py creative.game-art-asset` and used its
stamped assignment. The row is a template, not a schema: the creative schema currently declares
no legal field rows, so `fields: []`, `proposed_fields: []`, and an empty `dimension_order` are
intentional. I read and applied:

- `planning/00-database-agent-product-design.md` as the design authority;
- `planning/01-product-design-structured.md` for the numbered rendering;
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md`, and `planning/prompts/ALIGNMENT.md`;
- `planning/domains/roster.json` and `ROSTER.md`, including the creative schema and the game-art,
  3D, motion, post-production, code, photos, stock, illustration, and shoot-day neighbours;
- `planning/domains/canonical_fields.json` (no field is needed or invented here); and
- `src/evidence_shape/vocabulary.py` (all source types in the node are members of `SOURCE_TYPES`).

The design span used in the node is the `00` guidance that design/creative formats should expose
format, dimensions or canvas properties, embedded metadata, layers/artboards, linked asset names,
and preview text, while unsupported proprietary formats remain indexed-but-unreadable. That is a
recognition and safe-indexing rule, not a licence to infer a game, project, owner, or engine from a
file suffix. CONNECTION's distinction between activation, grouping, and browse-only context also
controls this memo: a source and imported copy can be structurally grouped without copying a fact
from one onto the other.

## Why this is a real template (and where refusal would be correct)

The tempting refusal is correct for most isolated art. A single PNG, FBX, WAV, PSD, Blender file,
or stylised screenshot is already owned by a more general creative situation, a photo situation,
or a residual. “Game art” in a filename is not a domain fact. A folder called `GameAssets`, an
engine cache, and a downloaded Unity package are equally weak. If this node merely collected files
with game-like names or extensions, it would duplicate `creative.3d-asset`, `creative.motion-
graphics`, `creative.graphic-design-project`, `creative.stock-asset-library`, and `photos`.

The surviving distinction is a production relationship that crosses two evidence classes:

1. an authored or deliberately assembled asset source (layers, vectors, mesh, rig, material,
   animation, VFX, or authored sound);
2. a review or change artifact that names the asset or variant; and
3. an export/import/integration trace to an engine-side asset, prefab, scene, UI reference, build,
   or manifest.

That chain makes the situation engine-facing even when the engine file is proprietary and cannot
be opened. It also explains why the row is a template rather than a new schema: the creative schema
has deferred destination fields, while the recognition and grouping problem is already distinct.
The row would be a refusal if its evidence list stopped at “source art used by a game”; it survives
because it names a reproducible source → review → export → import → integration/version lifecycle.

## J-DEPTH fixtures, bottom up

### 1. `hero_idle_layers.psd` — labelled source, not yet game proof

This is a design-creative file with separated body, costume, shadow, and effects layer groups. A
nearby atlas manifest names trim, scale, and pivot policy. Those are observations available from a
creative extractor. No legal field is emitted: this template inherits no fields. The packet is
plausible only when the manifest, export, or consuming reference connects it to the game-art
workflow. A PSD by itself belongs to a graphic-design or illustration situation and falls through
to One-Off Images if no relationship appears. It is `also_holds_with` graphic design when the same
source is a design deliverable and an engine-bound sprite source. The filename does not establish a
hero character, game, artist, client, date, or folder path.

### 2. `hero_atlas_2x.png` — generated image and collision with photos

The packed image has trimmed sprites and transparent padding; a sidecar maps regions and pivots.
That is stronger than a generic illustration but still does not prove engine import. “2x” is an
observation in the name, not a current version fact. It must not activate from PNG, transparency,
pixel dimensions, or a visual impression of sprites. If its sidecar and source link are absent, it
is an isolated image. If linked to the PSD and an import record, it becomes a grouped generated
member, not a separate asset fact. A screenshot or atlas preview may also be photos only when
camera/capture evidence supports that route; depicted game content is not photo provenance.

### 3. `hero_atlas_import.json` — structured integration evidence, but not automatically code

The JSON maps atlas regions to animation names and import settings and references a prefab ID. Its
source type is `code_structured`, because the evidence is structured machine-readable data, not
because every JSON file is source code. The explicit reference is a strong deterministic signal
when the referenced files exist. It does not prove import success, authorship, or that the consuming
prefab is local. The same repository may also activate `code`; the role split leaves scripts,
tests, build tooling, and runtime logic there while this row groups the visual asset handoff.

### 4. `Knight_Run.fbx` — model source that must not swallow generic 3D

The container exposes a mesh, skeleton, and named animation takes, and an import record maps it to a
rig. Model, skeleton, and animation are observations; “Knight” and “Run” are not legal facts in a
field-less template. An FBX extension alone is never enough. Without the import record, consuming
scene, review proof, or another lifecycle edge this is `creative.3d-asset`, whose generic modelling,
texturing, and rendering situation owns it. With the engine-facing edge it is a member of this
template and may also hold with the 3D source situation. License and authorship remain unknown.

### 5. `Knight_Run_ImportSettings.uasset` — opaque imported copy

This proprietary binary pairs with the source model and records skeleton/material/import properties
in safe metadata; a prefab consumes the animation. The body is not silently treated as readable.
This fixture is important because the row's discriminator often lives in the relationship rather
than in decoded bytes. `uasset` alone could be an unrelated engine project, sample, cache, or
marketplace package. Import metadata plus a source and a consuming reference makes the packet
plausible. An unreadable binary with no surrounding packet falls through to Unsupported or
Encrypted, retaining only safe metadata and awaiting user attachment or an approved extractor.

### 6. `enemy_vfx_review_R2.mp4` — review proof, not camera media

The screen capture shows an effect running in an engine scene, carries an issue marker, and is
linked by notes to a timing change and export revision. It is `audio_video`, but the extension and
the video itself do not determine the domain. The explicit review linkage does. This may also hold
with motion graphics when the same effect is a designed motion deliverable; the collision rule
asks which lifecycle evidence is primary. A camera-original gameplay clip with capture metadata
and no source/import packet belongs to shoot-day media, even if it depicts the finished game.

### 7. `enemy_vfx_R2_notes.pdf` — review record and revision boundary

The annotated proof lists colour, timing, overdraw, and integration issues and names a retest build.
This is a text-document review artifact, also eligible for the revision-round situation. It does
not prove that issues were fixed, that a client approved them, or that the person named in notes is
the author. A review note may group with the asset family, but facts do not flow from the note to
every export. If detached, it is an Independent Record.

### 8. `gameplay_build_asset_manifest.csv` — version/integration ledger

Rows map asset IDs to imported paths, hashes, package version, and build status. The manifest does
not contain the assets, and listed paths are not facts about the current filesystem. It is useful
because it provides the version-family and integration edge: source and generated copies can be
joined by an explicit ID or hash, and a build result can be retained as evidence. A standalone
manifest remains an Independent Record. A status cell is not legal acceptance or proof that a build
was shipped.

## Additional collision fixtures

`summer_asset_pack.unitypackage` has prefabs, textures, materials, and vendor-like names but no
local source, review packet, or consuming project. It co-holds with the stock-asset-library only
for rights/provenance, and falls through to Review Later rather than being promoted to internal
game production. The archive manifest should be read without unsafe extraction; archive paths do
not become project facts.

`CharacterConcept_03.png` is a lone illustration with a signature and date-shaped suffix. Visual
content, a signature, and a date token cannot establish game production, artist identity, or a
character role. It belongs to illustration or One-Off Images unless later evidence connects it to
the production chain.

`Assets/Characters/Hero.uasset` is an engine binary in a repository that also contains source art,
import metadata, a prefab reference, scripts, tests, and build configuration. The repository
structure activates code for its own role and game-art for the visual asset handoff; the path is
not a fact and every repository member is not creative content. This is the clearest role-split
fixture.

`phone_capture_gameplay_0042.MOV` has camera-original metadata and capture naming, but no source,
import record, or review annotation. A game shown inside a recording does not turn camera media
into an engine asset. It falls through to Reference Clips or shoot-day media.

## Lifecycle and version logic

The recommended grouping spine is not a folder path. It is a graph of production evidence:

`source` → `review proof / change list` → `export package` → `engine import` → `prefab or scene`
→ `build verification` → `version/migration note`.

The arrows are evidence relationships. They may be made by an explicit asset ID or GUID, basename
and dependency record, a manifest, a hash, or a readable reference in a project file. An export
with a changed filename may still be the same version family when the manifest or content hash says
so; a file called `final` may be stale, copied, or rejected. Conversely, exact hashes identify
duplicate content but do not prove which copy is intended for integration. Generated atlases,
compressed textures, animation bundles, and imported binaries can be grouped as derivatives without
asserting that they are interchangeable.

Review is a stage of evidence, not approval. `R2`, a review date, a retest build, or a cell marked
approved can be recorded as an observation in a review packet, but the template writes no lifecycle
field and no legal status. The same discipline applies to integration: an import setting records
an intended configuration; only a build report or another explicit artifact can show that a build
actually consumed the member, and even that does not establish a release or legal acceptance.

Moves deserve caution. Engine projects often store path- or GUID-sensitive references. The local
organizer may group source and imported copies for retrieval, but should not relocate either merely
because they share a semantic name. A third-party package, generated cache, or build output may be
reproducible but still should not be deleted or rewritten from a weak duplicate inference.

## Recognition versus extraction

Deterministic signals in the JSON establish plausibility: a source plus import record plus consuming
reference; atlas metadata and pivot policy; model plus rig and import edge; annotated review proof;
manifest/build evidence; and explicit version lineage. They do not mint fields. The creative schema
has no fields, so even a perfect asset ID is a grouping signal only.

LLM-supported questions are deliberately limited to interpretation: authored versus reference,
consumer project versus sample, same asset across generated naming, review proof versus portfolio
clip, internal versus licensed, and game asset versus music session. They are not a substitute for
an absent edge. When context conflicts, the safe result is abstention or a residual, not a guessed
game project.

The never-alone list protects against the most common false positives: extensions; genre words;
engine directories; detached screenshots; version/date/GUID tokens; vendor metadata; download
sessions; and content-level properties such as alpha, bones, UVs, or dimensions. This also prevents
the activation/grouping error where a file joins a nearby project group but contributes no fact to
the game-art template.

## Neighbour decisions

- `creative.3d-asset` is a collision because the model/rig/texture bytes are identical evidence;
  engine consumption is the discriminator. Generic 3D is not swallowed.
- `creative.motion-graphics` is a collision for animation and VFX. Storyboard/composition/render
  delivery points there; asset IDs, prefabs, import settings, and integration point here.
- `creative.post-production` is a collision for video proofs and compositing. Recorded source and
  editorial timelines point there; a linked engine capture can be this row.
- `code` is both a collision and a role split. Scripts, tests, packages, repositories, and build
  tooling remain code; visual/audio asset production and handoff remain here.
- `photos` is a collision for PNG/JPG/screens and camera recordings. EXIF and capture events win;
  generated atlases and review images need production linkage.
- `creative.graphic-design-project` is `also_holds_with` for layered UI, sprites, icons, and visual
  development where both design and engine delivery are real.
- `creative.stock-asset-library` is `also_holds_with` for licensed assets. Rights/provenance must
  remain separate from integration.
- `creative.illustration`, `creative.shoot-day-media`, and `creative.revision-round` were considered
  as fixture owners or co-holders, but no reciprocal edge is needed in this file beyond the explicit
  fixture annotations: their role is clear and the node must not rewrite neighbours.
- `career` was considered from the roster hint. A portfolio or résumé may mention game art, but it
  is not a production packet and therefore has no edge here.

## Fields, dimensions, privacy, and open questions

No canonical field is licensed by this template. I did not mint `project`, `asset_type`,
`lifecycle_stage`, `engine_target`, `version`, `character`, or `platform`; those are useful future
proposals but are not currently legal destination facts. The empty dimension order is therefore
binding, not an omission. If a later field pass licenses them, production context should precede
lifecycle stage and asset type; engine target should be used only when directly evidenced. Time is
not first because a review date or export timestamp scatters one asset family and is not its stable
identity.

The node is potentially sensitive. Unreleased characters, levels, mechanics, source assets,
proprietary engine binaries, licensed packages, build manifests, and review captures may disclose
confidential development or third-party rights. Sensitivity follows the packet and rights context,
not the extension. The two `NEEDS-JOSEPH` questions are whether to license the future project /
lifecycle / asset / engine facets and how strictly to split packets containing substantial source
footage or soundtrack material.

## What changed / claims

1. The game-art row is retained as a narrowed, field-less creative template because its defining
   evidence is an engine-facing production lifecycle, not a file extension or visual style.
2. The node covers source, review, export, import, integration, build, and version relationships
   while keeping facts empty until the creative schema licenses fields.
3. Twelve concrete fixtures separate authored packets from generic 3D, motion, post-production,
   code, photos, stock downloads, illustration, and residual records.
4. Every source type is from the repository vocabulary; unsupported proprietary members remain
   metadata-only and may fall through to human review.
5. The node and this memo contain no filesystem path as a fact, no numeric threshold, no invented
   field, and no claim that `final`, `approved`, a version token, or an extension proves status.
6. The memo ends with the unresolved Joseph decisions rather than silently deciding future schema
   fields or rights policy.
