# 80 — The role-matcher ruling

Date: 2026-08-31
Status: **RULING. The gate on `66` §16 is lifted, on the terms below and no others.**
Supersedes the open item at `62` §D and `69` §4.3, and ungates `75` §5.

**Provenance.** `78` was written as an internal decision brief and `79` as a briefing for
somebody outside the project. Joseph took `79` to a professional adviser, received the advice
quoted below, and adopted it. **The ruling is Joseph's; the reasoning is the adviser's and is
recorded because the reasoning is what a later reader will need.** Where this document states a
requirement, it is now binding on implementation in the same way a SPEC section is.

---

## 1. The ruling on the mechanism

**Option 2 — a LOCAL model proposes a shortlist; the person confirms — with Option 5 running
underneath it continuously, and Option 1 as the fallback whenever no local model is present.**

**Options 3 and 4 are CLOSED.** Not deprioritised: closed. They fail for different structural
reasons and the difference matters.

### 1.1 Why 3 is closed

> *"Option 3 isn't a worse version of Option 2 — it's a different kind of commitment. …
> revocation cannot retract what has already left the device. That means Option 3 isn't 'send it
> to the cloud unless the user objects' — it's 'send it to the cloud, permanently, the first
> time', before you've learned anything about whether this feature is even good. You don't have
> enough information yet to spend an irreversible action on a feature you haven't shipped."*

A future version may revisit cloud-assisted onboarding. That is a **separate decision, made with
a working local version already in hand for comparison**, and it does not reopen by default.

### 1.2 Why 4 is closed, and it is the important one

Option 4 was the most faithful reading of the owner's original sentence, and it is the one whose
consequences were hardest to see. The adviser's argument, which is now the recorded reason:

> *"It takes the one part of the design that is unconditionally categorical — absent means
> refuse, never guess — and builds the entire onboarding mechanism as a standing exception to
> it. … it lets a permanent, unstructured, unretractable piece of context quietly shade every
> ambiguous judgment from then on, with no on-screen line connecting a specific misfile to the
> sentence that caused it.*
>
> *This is the same failure mode as Priya's whole disk filed as coursework, except worse, because
> right now that failure is at least a legible bug — one word, one command-line flag, traceable
> and fixable. Option 4 turns that failure mode into an architectural feature: a permanent
> unlabeled bias with no debug path."*

And the reconciliation with the owner's original objection:

> *"The owner's instinct that 'this cannot be rule-based' is correct. But the fix for 'don't
> discard the sentence' is not 'let the sentence become ambient, untraceable gravity.' It's 'let
> something read the sentence and propose, transparently, per-decision, so every effect is
> attributable.'"*

### 1.3 Why Option 2 is not a compromise

It is the version of *let it be judged* that keeps the judgement inside a boundary that can be
inspected. The model reads the whole sentence; it may propose only from the closed list; the
person makes the decision. **Nothing discards the sentence, and nothing lets an ungoverned
judgement silently colour the rest of the system.** It is the only option under which both
original objections stop applying at once.

### 1.4 Option 5 runs regardless

Option 5 is not an alternative. It is the design's own general mechanism — ask a narrow question
exactly when a specific decision is blocked — applied consistently, and it catches what Option 2
structurally cannot:

> *"Priya is a teacher and a student — knowing both roles doesn't tell the system which one a
> specific ambiguous PDF belongs to; the in-context question does."*

---

## 2. The ruling on the always-local question — settled, not open

`78` §3.6 and `79` §3.6 recorded this as the single most consequential unresolved point, and
framed it as unresolvable from inside the project. **That framing is rejected and the question is
now answered.**

> *"You don't need an outside authority to rule on this, you need to notice that the answer is
> implied by the rest of your own design. … A typed self-description is not hypothetically
> similar to that risk class — it's the same risk class by construction: free text, typed by the
> person, about themselves, with no schema constraining what's in it. It could contain a name, a
> diagnosis, a legal status, an employer under NDA, anything. The fact that it wasn't anticipated
> when the nine always-local categories were written is not evidence that it falls outside them —
> it's evidence the list needs a housekeeping update."*

**RULING: a person's typed self-description IS a user edit under `00`:186. It is always local,
by default, with no exception, and consent does not unlock it.**

> *"Consent is the wrong tool for content whose sensitivity the person can't preview or bound in
> advance."*

This is a RESTRICTION, not a permission — it closes a path rather than opening one, which is why
it can be recorded here rather than requiring a fresh ratification round. **It must be recorded
at the member itself** (`src/privacy/vocabulary.py`), per the standing rule that a closed
vocabulary's membership carries its own approval.

Consequences, which follow mechanically and are not separate decisions:

- §3.7 Q2 ("may the sentence leave the device") is answered: **no, never, by default.**
- Option 3 is closed **by the design as written**, not by a fresh judgement call.
- Any future proposal to send a self-description off-device is a change to `00`:186 and is
  refused until `00`:186 changes.

---

## 3. The ruling on WHEN the question appears — this is a design change

The brief assumed onboarding. **It is not onboarding.**

> *"A brand-new user doesn't yet trust the product enough to answer an identity question about
> themselves. Seamless would mean: let the person run the tool once, see it do something correct
> and small first, and ask the self-description question only once there's evidence the product
> needs it — i.e. precisely when it hits its first genuinely ambiguous file. … From the user's
> side, this reads as 'the tool asked me something because it actually needed it', not 'the tool
> interrogated me before I'd even seen it work.'"*

**REQUIREMENT R1.** The self-description question is **triggered by the first genuinely ambiguous
file**, not by first run. Option 5's existing mechanism — `src/questions/triggers.py`, which
raises a question only when a specific decision is blocked, from a finished run and never up
front — is the **trigger** for introducing the Option 2 flow, not a separate fallback bolted on
beside it.

This is already how every other question in this product works, and it is why `66` §12 forbids
asking except when a decision is blocked. The ruling brings §16 into line with §12 rather than
adding anything new.

---

## 4. The seamlessness requirements — binding

These came from asking what the moment actually feels like to the person typing. Each is a
requirement, not a preference.

**R2 — the friction budget is spent ONCE.** Confirmation happens at the moment the roles are
established. It does **not** recur per file.

> *"If the design implies confirming every time the context gets used later … that becomes death
> by a thousand tiny interruptions, and a user will start clicking through without reading, which
> defeats the entire safety rationale."*

A confirmation a person has learned to click through is not a safety mechanism. This is the
sharpest argument in the advice and it constrains the implementation more than anything else
here: **a confirmed role operates silently afterwards.**

**R3 — one box, not a form.** No dropdowns and no "select all that apply" from a visible list of
23 up front.

> *"that's the exact discarding-the-sentence problem the owner objected to, just moved into the
> UI instead of the matcher."*

**R4 — the shortlist must read as having heard the whole sentence.**

> *"If the person mentions three things and the shortlist only reflects one, that's the moment
> trust breaks, even if the one it picked is technically correct."*

**R5 — "none of these" is a normal outcome, not an error.** Same visual weight, same tone, no
apology shape. There is no wrong answer to *what do you do*; there is only *we don't have a
category ready for that yet*. The raw sentence stays recorded and visible rather than discarded.

*(This is a content requirement. The wording itself is prompt-adjacent and remains the owner's to
approve manually — see §6.)*

**R6 — the roles are editable, not a gate.** A person whose situation changes — finishes teaching
a course, takes on a new one — makes a small localised edit. They do not re-run an onboarding
flow.

> *"The confirmed roles should feel like a light, editable settings panel the person can glance at
> and adjust anytime, not a one-time gate they went through and now can't see again."*

`75` D1 already requires several roles live at once, each with a scope and a period, and its
negative twin already forbids using supersession to hold a second simultaneous role. R6 is the
surface half of the same requirement.

---

## 5. The second risk the brief underweighted — binding

`78` §3.5 named the central risk as a plausible wrong shortlist item being read as the product's
endorsement. A second, quieter one is now recorded beside it:

> *"Shortlist ORDER itself is information the person will use whether or not you intend it to be.
> Even 'unordered' presentation isn't neutral if the UI renders a list top-to-bottom — position
> seven versus position one still reads as ranked to a human, regardless of your intent."*

**R7 — the mitigation must be stronger than "do not sort by confidence."** Removing ranking from
the data and then reintroducing it through the geometry of the presentation is not a mitigation.
Acceptable approaches named: randomising visual order per render, or a layout with no implied
first item. The presentation must not encode an order the data deliberately does not carry.

This applies to P13, which owns every surface, and it is the kind of requirement that is easy to
satisfy in the data and lose in the rendering.

---

## 6. What is STILL the owner's, and is not ruled here

- **Prompt text.** The adviser explicitly declined to draft any, for the reason this project
  already holds: prompt wording is a separately governed, near-permanent artifact — its bytes are
  fingerprinted into every audit record and cache key it produces — and it requires the owner's
  manual approval. **No agent may author or approve it.** R5's "no-match" wording is a content
  requirement here, not a string.
- **Which local model, and how it is obtained.** Not addressed by the ruling.
- **`74` §8 Q2**, the four rival `review_action` vocabularies, is untouched by this and stays open.

---

## 7. What this ruling unblocks, and what it now forbids

**Unblocked** — `75` §5 in full, no longer only its ungated half:

| | task | note |
|---|---|---|
| D1 | the role declaration record | already specified; several roles live at once |
| D2 | the four outcomes, closed | §16:553 |
| D3 | a confirmed role activates through the one activation surface | confirmation is the gate |
| **NEW** | the local proposal step | Option 2; local only; proposes, never activates |
| **NEW** | the ambiguity trigger (R1) | reuses `questions/triggers.py` |
| **NEW** | the editable role surface (R6) | P13 |

**Newly forbidden**, and these are the tests that must exist:

1. No path sends a self-description off-device. It is an always-local kind, enforced where the
   other nine are enforced, and a test must fail if a transport can name it.
2. No model output activates anything. Activation requires the person's confirmation, as a hard
   invariant rather than a default.
3. No per-file re-confirmation of an established role (R2).
4. No presentation that reintroduces ranking the data does not carry (R7).
