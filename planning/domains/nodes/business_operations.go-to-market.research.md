# business_operations.go-to-market — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.
**This row states a fold question against itself.** Read the last section before treating it as settled.

## Sources

Same authority stack as `business_operations.research.md`; all quotations machine-verified verbatim
against `00-database-agent-product-design.md`. Landed siblings read for key set and idiom:
`business_operations.json`, `creative.ad-campaign.json` and `creative.content-marketing.json` (where
landed), `career.portfolio-work-samples.json`. Legacy row absorbed per `ROSTER.md` Appendix A line
833: `ops.go-to-market` (ROW). Note that `ops.pricing` folded to `business_operations.market-research`,
not here, and that fold is respected — decided pricing in force is claimed, pricing *analysis* is not.

## What it is for, and what it holds

The coordinated effort to bring one offering to market by a dated launch. Launch plans and workstream
trackers, readiness checklists and go / no-go records, positioning and messaging documents,
competitive battlecards, sales enablement decks, packaging and pricing decisions, announcement and
press-release drafts, communications calendars, beta and reference programmes, post-launch reviews.

## Node test — passes, narrowly, on the readiness gate

The anchor is a **launch**: one offering, one date, several functions gated to be ready at once. Two
detection structures are genuinely this row's — the **cross-functional workstream plan against a single
shared date**, and the **readiness gate with per-function criteria and a go / no-go decision**. A
campaign has neither. A roadmap has neither. A market study has neither.

That is the whole of the argument, and it is thinner than any other row in this chunk.

## Files considered and rejected

- **`The Ultimate Product Launch Playbook.pdf`** — kept as the collision fixture. This world is
  unusually template- and playbook-driven, so the *shape* is a weak signal and the values carry the
  meaning; that is stated in `needs_llm`.
- **`Atlas roadmap FY26.pptx`** — kept as the second fixture, against `business_operations.product-roadmap`.
- **`Press release - EMBARGOED.docx`** — kept because it is the row's clearest sensitivity case: a
  public *form* that is precisely not public before its date.
- **A landing page mockup / launch video** — considered and dropped: those are creative production
  artifacts and `creative.*` owns them; claiming them would have made the fold question worse.
- **A win/loss or competitive teardown** — left as a `collides_with` against
  `business_operations.market-research`.

## proposed_fields

**None** — deferred to the schema row. An offering concept and a launch concept are the two this row
would want; both are held as prose and neither is minted.

## Neighbours considered that did NOT get an edge

- **`business_operations.user-research`** — launch feedback loops touch it. Not edged; the
  `market-research` collision carries the analysis-versus-decision discriminator once.
- **`business_operations.support-operations`** — launch FAQs and support enablement are produced here
  and consumed there. Noted, not edged, at gist depth.
- **`hr.training-development`** — sales enablement is training. Deliberately not edged: enablement here
  is commercial content, and `hr`'s row is about employee development, which is a different anchor.

## NEEDS-JOSEPH

- **NJ-BO-14 · The fold question, stated against this row.** This is the weakest of the nine rows in
  this chunk and the schema row already named it so. Its members are overwhelmingly borrowed from
  `creative.ad-campaign`, `business_operations.market-research` and `business_operations.product-roadmap`,
  and its two detection structures could be argued onto `business_operations.project-delivery`. This
  pass's answer is **KEEP**, on the readiness gate. The alternative — fold it into the roadmap row and
  let the campaign row hold the external material — is defensible and cheap. R1c should decide it
  deliberately rather than inherit it, and if the commercial cluster is trimmed for NJ-J-IND-1's count,
  this is the first row to go.
- Carries **NJ-J-IND-4**: embargoed and unreleased material is confidential for a period and public
  afterwards, and nothing in a file says which side of that line it is on.
