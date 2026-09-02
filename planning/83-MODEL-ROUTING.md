# 83 — Which model answers which question

Date: 2026-08-31
Status: **Deployment policy, set by the owner.** Not a design change: `00` names no model and
no provider, so every word here is a composition-root choice and belongs in `src/cli.py` and
`.env`, never inside a part package.

---

## 1. The owner's instruction

> *"Best for Heavy Reasoning & Coding: DeepSeek-V4-Pro (and its Max mode) … Best for Hard Logic
> on a Budget: DeepSeek-R1 excels at deep, step-by-step math and logic problems … Best for Speed
> and Efficiency: DeepSeek-V4-Flash provides rapid, cost-effective inference for lighter everyday
> tasks. Try a combination of each model to maximise efficiency, cost and also time."*

So: **one model per kind of judgement, not one model for everything.**

**A caveat that must not be lost.** These names were supplied by the owner and are not verified
against the provider's catalogue by anyone in this project. If a name is wrong the provider
rejects the call and says so — which is the intended failure. A wrong name must **never** fall
back to another tier: a cheap model answering a question the expensive one was chosen for is a
wrong answer that looks exactly like a right one, and the whole point of tiering is defeated the
first time it happens silently.

## 2. The three tiers, and what decides which

The routing question is **not** "how hard is this task". It is **what does being wrong cost the
person**, which is the north star applied to spend. The user is one multi-role human — a student
AND an employee AND a litigant AND a householder — and the costs are not evenly distributed.

| tier | env name | what it answers | why |
|---|---|---|---|
| **Reasoning** | `DEEPSEEK_MODEL_REASONING` | judgements where being wrong is expensive and hard to notice | a wrong answer here becomes a folder, and a person finds out months later |
| **Logic** | `DEEPSEEK_MODEL_LOGIC` | bounded, checkable, verification-shaped work | the answer can be checked against something, so a cheaper reasoner is not a risk |
| **Fast** | `DEEPSEEK_MODEL_FAST` | high volume, low stakes, individually cheap to get wrong | a screenshot mislabelled costs a person nothing they cannot undo in one gesture |

## 3. The routing, by call site

Written against the call sites that exist. A site that is not built yet is marked so, and
inherits nothing by default — an unrouted site refuses rather than picking a tier.

| call site | tier | reasoning |
|---|---|---|
| **A_fact** — proposing facts from a compact dossier (`llm_harness/fact_validation.py`) | **Reasoning** | This is the one that becomes folder structure. `00` §3.6 already demands the model return `unknown` rather than guess, and the model most able to decline is the one worth paying for. It is also the site the whole product is currently blocked on. |
| **Group coherence** (`llm_harness/group_validation.py`) | **Logic** | A bounded yes/no against evidence already extracted, checkable against the group's own anchor facts. |
| **Placement validation** (`llm_harness/placement_validation.py`) | **Logic** | Same shape: does this destination follow from these facts. The verdict is checked by the validator either way. |
| **Template validation** (`llm_harness/template_validation.py`) | **Logic** | Structural, bounded, and its answer is re-checked. |
| **Role shortlist** (`questions/`, being built) | **Reasoning** | It reads a person's own sentence about their life, and `80` §4's R4 requires the shortlist to read as having heard the WHOLE sentence. This is exactly the judgement a cheap model flattens to one keyword, which is the failure `62` §D objected to in the first place. |
| **Residual per-file review** (§7.7, `placement/`) | **Fast** | High volume by construction — these are the files nothing else could place — and §7.6 already makes the person authorise the spend per set before any of it happens. |
| Anything not listed | **refuses** | absent means refuse, never guess. A new call site names its tier or does not run. |

## 4. What this policy may not do

- **No silent downgrade.** A tier that is unavailable, rate-limited or misnamed produces a
  refusal that names it. It does not quietly answer from another tier.
- **No tier changes what may be SENT.** Routing decides which model; `privacy.vocabulary`'s
  `ALWAYS_LOCAL` and `ITEM_KINDS` decide what reaches any of them, and those are untouched by
  this document. A faster model does not get looser data.
- **No tier is a default.** `DEEPSEEK_MODEL` as a single catch-all name is deliberately NOT read
  any more; three names replace it so that no call site can inherit a tier it never chose.
- **Max mode**, which the owner mentioned, is not wired. It is not in the env template because
  nothing in the code knows what it is yet. If it becomes a per-call option rather than a model
  name, it is a fourth env name and a row in §3, not a flag buried in a part package.

## 5. Cost, honestly

The owner asked to maximise efficiency, cost and time together. The three do not always point the
same way, and where they conflict this policy spends money to protect the person:

- **A_fact is the expensive tier and it is also the highest-volume site**, because every file that
  needs a model needs this call. That is the one place where the cheap choice would be tempting
  and wrong: it is the call whose errors become folders.
- The cheapest real saving is not a smaller model, it is **not making the call**. P6's direct and
  rule stages, P4's evidence locations and P7's gate already resolve most files without any
  model, and every fact settled locally is a call not made. `72` and `76` both make this point;
  it is repeated here because a tiering document invites the opposite instinct.
- Budgets are enforced independently of routing (`llm_harness/budgets.py`, ceilings in
  `src/cli.py`). A tier is not a spending limit and must not be used as one.

---

## 6. 2026-09-02 — the model names in this document were wrong, measured against the API

The three names §3 recorded were never checked against DeepSeek. A live probe of all three tiers
(synthetic content only, no user file and no dossier) returned HTTP 400 from every one:

> The supported API model names are `deepseek-v4-pro`, `deepseek-v4-flash`, and
> `deepseek-v4-flash-vision-exp`, but you passed `DeepSeek-V4-Pro`.

Two were case errors. **The third, `DeepSeek-R1`, does not exist on this API at all.** The
transport itself was never at fault: a bad key returns 401 and this was 401-free, so the client,
the routing and the credential were all correct and only the names were not.

After correcting `.env`, all three tiers return the probe's expected word. **The model path is
proven live for the first time.**

### The finding this exposes, which is a decision and not a typo

**Three tiers map onto two general-purpose models.** `logic` has no model of its own. The options:

- `logic` -> `deepseek-v4-pro`. **Taken, and it is what `.env` now says.** §4's "no silent
  downgrade" rules out the alternative: sending B_group, C_placement and E_template to `flash`
  would be exactly the silent downgrade that rule exists to forbid, and it would be a downgrade of
  the calls that decide grouping and placement.
- `logic` -> `deepseek-v4-flash`. Cheaper, and refused on the above.
- Collapse the vocabulary to two tiers. **Not taken**, and deliberately: the tier names are a
  statement about the KIND of judgement a call site makes, and that statement stays true whether or
  not two of them currently resolve to the same model. Collapsing them would throw away the
  distinction and make it expensive to re-introduce when a third model exists.

So `reasoning` and `logic` are the same model today. That is a fact about DeepSeek's catalogue on
2026-09-02, not about this design, and the routing table is unchanged.

`deepseek-v4-flash-vision-exp` exists and is unused. P5 extracts images and runs OCR; whether a
vision model belongs in that path is a question this document does not answer and did not ask
before. Named here so it is not discovered a third time.

**How to re-check rather than trust this section:** the probe is six lines and sends nothing of the
person's. Any claim here that a tier reaches its model should be re-measured rather than read.
