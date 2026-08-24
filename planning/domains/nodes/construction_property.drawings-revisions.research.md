# construction_property.drawings-revisions — gist research memo

Depth: GIST
Row: `construction_property.drawings-revisions` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `cons.drawings-revisions`.

## The warning I was given, answered directly

The dispatch asked whether this row is a version-family concern already handled by the landed
duplicate/version-family design rather than a domain of its own. **It is not — but only just, and
the distinction has to be drawn on the right leg.**

- **What the universal design already handles, and this row must not re-derive:** grouping bytes
  that belong together. `00` makes version family a universal fact, and the landed P6 work decides
  family membership by hash, not by filename — `00`'s own words are that a content-hash match
  supports deduplication review while a filename match alone does not. A row whose content was
  "construction files have versions" would be a duplicate of that machinery and should be refused.
- **What this row actually stands on:** the **title block**. A bordered zone carrying project,
  drawing number, sheet title, revision, scale, status, originator and date as co-occurring
  *labelled slots* is a detection structure that exists nowhere else on the roster, and it has
  nothing to do with version families. The **transmittal/issue register** is a second such
  structure, and the **status vocabulary** (issued for construction / superseded / as-built) is a
  third. That is a detection-signal difference from the schema's default template, which is
  precisely what CONNECTION §2's node test requires.
- **Its dimension recommendation also differs**, and differs in an unobvious direction: revision is
  explicitly **not** a folder level. That is the row's most useful single output.

So the row stands, and its `never_alone` list opens with the thing it is most likely to be misused
for: a revision-shaped token in a filename is not a revision.

## proposed_fields justification

One key, `revision`, proposed **with its own counter-argument first** and flagged as droppable. The
argument is narrow: `version_family` is an *identifier for the family* — it says these bytes belong
together — and says nothing about *which member this is*. In almost every domain that gap does not
matter. Here the entire purpose of the situation is preventing construction from a superseded sheet,
which is a question about position, not membership. `destination_eligible` is proposed **false**.

If R1c rules that position-within-family is universal machinery, drop the proposal; the row's
detection signals and dimension recommendation are unaffected.

## Files considered and rejected

- A structural calculation package and a specification: same job, same discipline, but their
  evidence is prose and tables, not a title block — they belong to `construction-project`.
- A point cloud / laser scan: genuinely this world, but the roster's `cons.site-survey` →
  `construction_property.site-survey` row owns survey capture and is not mine.
- A CAD block library and a title-block template file: real files in a practice's folder, but they
  are tooling, not controlled information about a building.

## Neighbours considered that did NOT get an edge

- `photos.drone-captures` — overlaps as-built recording, but the confusable artefact is a
  photograph, and the progress-photograph row (not mine) is the correct place to state it.
- `academic` / `research` — a student's studio drawings carry title blocks too. No edge, because
  the discriminating evidence is a course code plus academic context, which the academic schema
  already owns and which decides the case cleanly.
- `finance.household-property` — a householder keeps their extension drawings. Covered by the
  schema row's household collision; repeating it here would be duplicate authorship.

## NEEDS-JOSEPH (this node only)

- **NJ-CP-5** — position within a version family: domain field or universal machinery? This row
  proposes `revision` and states the case for dropping it.
- **Superseded**, recorded not solved: the single most valuable marker in this world, and this
  catalogue has no vocabulary for it. It may be a `work_type`/status value, a P7 concern, or out of
  scope. This pass invented no mechanism.
- Inherits **NJ-CP-1**, **NJ-CP-2**.
