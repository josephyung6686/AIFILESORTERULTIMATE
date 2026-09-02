# 88 — The self-description may leave, and nothing else may follow it

Date: 2026-09-02
Status: **Owner ruling. Binding.** Supersedes nothing; it CLOSES the route question
`80` §6 left open by name (*"Which local model, and how it is obtained. Not addressed
by the ruling."*).

---

## 1. What was asked, and what was answered

The role matcher's narrowing step — `80`'s Option 2, *a model proposes a shortlist, the
person confirms* — needs to put the person's typed self-description in front of a model.
It had no legal way to do that, and `build-role-matcher` stopped rather than inventing
one. The wall, in its own words:

- P8's Done-means 1, quoted at `src/privacy/transport_guard.py:7-11`: **"Exactly one
  function in the codebase constructs a model request, and its only parameter type is
  P7's `Released`."** `tests/p7/test_p7_real_transport_egress.py:47` and `:51` hold it.
- A self-description is a `user_edits` item. `user_edits` is one of `ALWAYS_LOCAL`'s
  nine. **P7 refuses to release it**, so there is no `Released` to hand to `issue`.
- `80` §2 + §8 suspended the ENFORCEMENT of that classification for development. It did
  not build a MECHANISM. A suspension with no path is not a path.

Three routes were put to the owner on 2026-09-02 with the tradeoffs stated:

1. a genuinely local in-process model — no egress, P7 untouched;
2. **a narrow P7 release path for the self-description alone**;
3. neither yet — ship `80` §1's named fallback, the unnarrowed closed list.

**The owner chose 2**, and said in his own words that **the scoping IS the hard part.**
That sentence is part of the ruling and is why §2 exists.

## 2. The ruling is not "loosen P7"

It is **open exactly one door, and make the other eight unreachable by construction.**

The eight remaining always-local kinds — `paths`, `complete_extracted_text`,
`ocr_output`, `file_hashes`, `image_exif`, `gps`, `group_memberships`,
`raw_sensitive_values` — must be sealed by a mechanism that makes reaching them
**impossible, not merely untested**.

**A release path that takes an item kind as a parameter and happens to be called with
`user_edits` today is NOT what was approved.** The next caller passes `ocr_output` and
nothing stops them; the seal would be a convention, and a convention is what the whole
of P7 exists to replace. Prefer a path the other eight **cannot express**: a distinct
type only a self-description can inhabit, constructed at the single place a
self-description is collected, with no code path from any other kind into it.

If the seal turns out to be a check rather than a type, that is a finding to surface
with the reason the type was not possible — not a thing to quietly add a check for.

## 3. What this ruling does NOT do

- **It does not touch the other eight.** Their classification, their enforcement and
  their tests are unchanged. A release path that reaches any of them is a defect under
  this ruling, not an extension of it.
- **It does not modify `80` §8's three conditions, which still bind.** Local stays the
  DEFAULT. A run that sends **says so on screen BEFORE sending** — not after, not in a
  log. It reverts before anyone who is not Joseph uses this.
- **It does not approve prompt text.** The route being decided makes a draft
  *possible*; ratification is still the owner's, an agent may not adopt its own draft,
  and nothing installs one. `82` is the model for how a draft is written.
- **It does not widen the `call_site` vocabulary beyond one member.** The approval
  recorded at that member covers **the self-description, for the role shortlist, and
  nothing else.**

## 4. The compensating control, which lands FIRST

`build-role-matcher` found this while blocked, and it is the most important thing in
its report:

> nothing scans for a module that calls a client's `invoke` WITHOUT setting
> `IS_MODEL_TRANSPORT`. The flag scan (`tests/p7/test_p7_skeleton_step.py:294`) only
> finds modules that declare themselves.

**A guard that only catches the honest is not a guard.** Because this ruling
deliberately opens a door, the scan that catches *undeclared* doors is what makes doing
so safe, and it lands BEFORE the release path — so the path lands into a repo where an
undeclared `invoke` is already impossible.

Repo-wide AST over `src/`: any `.invoke(` or provider-client construction in a module
not declaring `IS_MODEL_TRANSPORT`, with `src/readers/model_*.py` the only permitted
declarers. Proven by sabotage, per house rule.

## 5. The thing the owner was not told before he ruled

Recorded here because a ruling made without it should be revisitable.

Route 1 was argued as *"a genuinely local in-process model, which is what `80` §1
actually specifies."* If that reading is right, the owner has chosen the cloud path over
an earlier ruling of his own without that being pointed out at the moment of choosing.
`build-role-matcher` has been asked for a plain statement of what `80` §1 says and what
a local model would have to be for the narrowing step to be legal without touching P7
at all.

**This ruling stands and work proceeds under it.** But if §1 does specify a local model,
that goes in front of the owner, and §5 is where the next session looks to see whether
it did.

## 6. Order of work

1. the repo-wide undeclared-egress scan (§4);
2. the `cli.main` wiring — `questions.roles`, `questions.proposal` and
   `role_declaration_is_due` are imported by no run today, so **R2's friction budget is
   currently enforced in a function nothing calls**, which is a live defect independent
   of this ruling;
3. the narrow release path (§2);
4. the prompt draft, inert, for ratification.

`80` R2 also governs the on-screen send notice: a notice a person learns to click
through is not a safety mechanism, so it is not a per-run confirmation dialog. What the
person is consenting to, and how often they are asked, is reasoned about rather than
picked.
