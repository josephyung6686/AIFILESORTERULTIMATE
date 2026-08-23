# business_operations.retrospective-postmortem — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `business_operations.project-delivery.research.md`; all quotations
machine-verified verbatim against `00-database-agent-product-design.md`. Landed siblings read for key
set and idiom: `business_operations.json`, `business_operations.it-asset-inventory.json`,
`clinical_practice.case-conference.json` (read specifically for the morbidity-and-mortality edge, and
its posture respected rather than overridden). Legacy rows absorbed per `ROSTER.md` Appendix A lines
679 and 815: `ops.retrospective-postmortem` (ROW), `soft.incident-postmortem` (FOLD).

## What it is for, and what it holds

Something has already happened — a project finished, a launch failed, a service went down, a near miss
was caught — and the organisation writes down what occurred, why, and what it will change. The row
holds retrospectives and lessons-learned write-ups, incident and outage post-mortems, timeline
reconstructions, root-cause and contributing-factor analyses, remediation trackers, accumulated lessons
registers, retro-board captures, debrief recordings, and the metrics and log exports attached as
evidence.

## Node test — passes, and the brief was right to make me check

The dispatch brief flagged that this row might be a `work_type` value of `project-delivery`. That is the
strongest objection to it and it does not hold, on three independent grounds:

1. **A large share of the material has no project at all.** An outage post-mortem, a near-miss review and
   a failed-launch debrief are anchored on an *event*, not an effort. Under a project-first row they would
   be homeless.
2. **The detection shape is genuinely different**, not a vocabulary variant: a timeline of timestamped
   past-tense events plus a causal section, sitting *above* the actions table. Every other row in this
   family has the actions table and none has what sits above it — which is why "an actions-with-owners
   table alone" is this row's first `never_alone`.
3. **The privacy posture differs**, which is why this row carries `potentially_sensitive` and
   `project-delivery` does not.

Three differences, so it is a node under CONNECTION §2, not a value.

## Files considered and rejected

- **`Grievance investigation report`** — kept as the collision fixture against `hr.employee-relations`.
  This is the one misfile in the row with a real human cost, so it earned the slot.
- **`Phoenix closure report.docx`** — kept as the both-anchors fixture: a project artifact that *contains*
  a retrospective. It is not a defect; P10 chooses from an accepted group.
- **An architecture decision record** — considered and left as a `code.software-project` collision signal
  rather than an example; ADRs are past-tense rationale but the situation is design, not review.
- **A regulatory incident notification** — real, but its anchor is the authority it is sent to; it belongs
  with the compliance or filings rows and earns a collision signal only.

## proposed_fields

**None.** Nothing this row wants is unheld in a way that only this row can argue: the review's own occasion
would use `creation_date` plus (if licensed) the schema row's proposed `fiscal_period`, and the effort under
review would reuse the existing canonical `project`. The genuinely unheld concept — *the event being reviewed*,
where that event is an incident rather than a project — is real but is precisely the thing this row cannot mint
alone, because it would also be wanted by `risk-register` and `support-operations`. Recorded here for R1c
rather than minted.

## Neighbours considered that did NOT get an edge

- **`business_operations.support-operations`** — got an edge (major-incident reviews come out of the queue).
- **`business_operations.meeting-record`** — a retro *is* a meeting, and its minutes are a meeting record.
  Left unedged deliberately: the confusion is already carried by the meeting row's own scope, and the
  distinguishing content (a causal section) is stated here.
- **`academic`** — a reflective essay and an after-action review share the voice. Rejected as too thin to
  edge at gist depth.

## NEEDS-JOSEPH

- **NJ-BO-RP-1 · Retrospective as node or as `work_type`.** This pass says node, with the three grounds
  above stated in `open_question`. If R1c disagrees, the incident half needs a home — folding it into
  `project-delivery` would file an outage under a project that does not exist.
- **NJ-BO-RP-2 · The person-versus-effort discriminator** (stated reciprocally against
  `hr.employee-relations`). A grievance investigation and a blameless post-mortem are the same document
  shape. Guessing wrong files someone's disciplinary record in a working branch. R1c should confirm the
  discriminator this row authored, or replace it.
- **NJ-BO-RP-3 · Branch naming as disclosure.** A folder named after a failure is itself a statement.
  This row recommends no dimensions (it cannot), but if fields are ever licensed the branch label needs to
  be user-approved rather than auto-derived. That is a P10 policy question, flagged here because this row
  is where it first bites.
