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
deliberately opens a door, the scan that catches *undeclared* doors lands BEFORE the
release path.

### §4 CORRECTED, 2026-09-02. This paragraph was stronger than the instrument.

The sentence above originally read that the scan is *"what makes doing so safe"*, and
that the path lands into a repo where an undeclared `invoke` *"is already impossible"*.
**Both were overstated, and the two agents who built and audited the scan said so
independently.** It is corrected here rather than quietly softened, because the owner is
being asked to ratify prompt text partly on this paragraph.

What the scan is: **an allowlist of NAMED exits**, and it is a good one. Five bypasses
were found and closed — an aliased `.invoke`, `getattr(c, 'invoke')`, an
attribute-qualified construction, the type spelled as a string, and a part importing
`readers.model_*` directly, which is CR-02's shape in four ordinary lines with no exotic
syntax in it. Eleven sabotages, each red.

What it cannot see, in the module's own words: `os.system` / `os.popen` / `os.exec*`
(`os` is imported across the tree for `os.path`, so that family stays open and
`subprocess` closes only the common spelling); `ctypes` reaching libc; `pty`;
`asyncio.open_connection`; a program assembled at runtime and handed to `eval`; and
anything outside `src/**.py` — not tests, not a root script, not `sitecustomize`, not a
`.pth`, not a C extension. And any exit shape nobody has named, **which is the class all
five closed bypasses came from.**

It also keeps one hole deliberately: `partial(SelfDescription)` is syntactically
identical to `isinstance(x, SelfDescription)`, which must stay legal or the door cannot
be wired at all.

**So the honest sentence is: this file raises the cost of a second door. It does not
make one impossible.** That is worth having, and it is not the same claim. A ruling that
rests on the stronger sentence rests on something that is not true.

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

### §5 RESOLVED, 2026-09-02, later the same day

It did specify a local model, twice. The role matcher's author produced the citations:

- **`80` §1** rules for Option 2 with **"a LOCAL model proposes a shortlist"** — the
  mechanism.
- **`80` §1.1** closes the cloud option **because "revocation cannot retract what has
  already left the device"** — the reason.
- **`80` §2** rules the self-description always-local and says **"consent does not
  unlock it"**.
- **`80` §8** suspends §2's ENFORCEMENT. It never replaced §1's MECHANISM, and `80` §6
  leaves *"which local model, and how it is obtained"* open rather than substituting a
  cloud one.

And the alternative was on the shelf: `src/readers/model_ollama.py` exists, claims
`locality="local"`, and hardcodes `127.0.0.1:11434` with no host parameter precisely so
the claim is checkable. It needed **no change to P7's policy at all** — only a ruling on
whether `privacy/items.py::_refuse_always_local_name` refuses an always-local item
because of the ITEM or because of the DESTINATION, since a local target keeps it local.

**All of that was put in front of the owner unsoftened, including that choosing cloud
overturns two of his own rulings and that `80` §8.2 already records the cost as
unrecoverable. He reaffirmed the cloud path.**

So this is a decision taken TWICE, the second time knowing exactly what it reverses. It
is not an oversight and it is not to be re-litigated. **`80` §1 and §1.1 are overturned
deliberately**, and that sentence exists here because without it the next person finds
§1, sees the cloud path, and assumes a mistake.

## 7. What §2's seal turned out to require: nothing

Recorded because it inverts §2's expectation. `privacy/items.py` has **one frozen
dataclass per releasable kind** — `Excerpt`, `RedactedIdentifier`, `CandidateLabel`,
`MetadataField`, `EvidenceReference`, `Filename` — and `kind_of()` maps type to name,
raising on a foreign type. **It takes no kind parameter.** The eight remaining
always-local kinds have no type at all, so §2's feared shape — *"a path that takes an
item kind as a parameter and happens to be called with `user_edits` today"* — was
already impossible. There is nothing to pass. The narrow door is a seventh dataclass and
nothing else moves.

Two seals were added on top, and one honest gap named rather than papered over:

- `SelfDescription` carries a **reference, never the sentence** (§6's "references only"),
  and its `__post_init__` refuses an id that is not `role:<name>`, so the type cannot
  address any other row in the questions store.
- `allow_self_description` is its own tier with **no default**, rather than reusing
  `gate.py`'s hardcoded `allow_unratified`, which would have admitted a self-description
  everywhere a filename is admitted — the "happens to be called with" failure, avoided.
- **A type can seal WHICH KIND and WHICH ROW. It cannot seal WHO CONSTRUCTS.** That one
  is an AST scan pinning a single construction site, and the module says so plainly
  instead of pretending it is a type.

**Owner approval, 2026-09-02: a seventh `ITEM_KINDS` member**, for the self-description
REFERENCE and nothing else. `ALWAYS_LOCAL` stays at NINE and is untouched; `80` §2's "no
tenth member is added" is unaffected and remains true.

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
