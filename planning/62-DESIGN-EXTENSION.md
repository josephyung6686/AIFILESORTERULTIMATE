# 62 — Extension to the product design: what the user is asked, what they can find, and what moves by itself

This document extends `00-database-agent-product-design.md`. It is written to be read in
`00`'s voice and to sit inside its argument rather than beside it. `00` remains canonical:
where this document and `00` conflict on anything not explicitly amended here, `00` wins.
Three additions are made, approved by the owner: a corpus role declaration before tree design,
a retrieval surface, and automatic filing. The first is an engine input and is argued first
because the other two depend on it. The second and third are **not part of the engine** and are
scheduled after it; they are designed here so that the engine is built against a known shape
rather than retrofitted to one.

## A. The corpus role declaration

The design derives everything from files. Its stop rules are correct to abstain wherever a role
is unevidenced, and its instruction that a folder label should reflect the user's own vocabulary
rather than a universal corporate taxonomy is correct for the same reason. But a class of
question exists that no quantity of file evidence can settle, because the answer is a fact about
the person and not about the file. Is this course one the user takes or one they teach? Is this
lease the user's own or their client's? Is this résumé the user's or a candidate's? Which of the
user's two children is this report card about? Each of these inverts a role that the extraction
vocabulary deliberately collapses — the stored key is `school` whether the user attends or
teaches there — and each is answerable by a single question that takes a person two seconds. The
product currently has nowhere to ask and nowhere to store the answer, and so it abstains on the
professional and multi-life half of a real disk: correctly, by its own rules, and uselessly. The
design should therefore include a short role declaration, presented as an onboarding guide,
which produces user-confirmed facts about the corpus that schema activation and dimension
eligibility may read.

The declaration should sit between grouping and destination-tree design, not at install and not
before the scan. The questions are cheaper to answer and far easier to trust once the user has
already been shown what was found, and asking them first would make the product feel like a form
to fill in before it has demonstrated anything. It runs once per corpus and remains re-openable,
because a person's life changes and because a user who skipped a question should be able to
answer it later without rebuilding anything.

Every answer is either structural or contextual, and the distinction must be carried by the
design rather than by convention. A structural answer may gate a decision, because it resolves a
role inversion or an eligibility question that no evidence could settle; it is stored as a
user-confirmed corpus fact and outranks an inferred fact of any reliability, exactly as a user
correction already outranks an extraction. A contextual answer may only inform interpretation:
it may act as a prior on what to surface first, and it may be carried as context in a model
prompt, but it may never decide whether a folder level exists. If an optional question about age
range ever determines the shape of a tree, that is a defect and not a feature, because the user
was never told it would and cannot see it happening. The harm this separation prevents is
precise: a person answers a friendly onboarding question, and three screens later a folder they
expected is missing, with no explanation reachable. That is the same harm as a protected area
silently dropped from a tree, arriving through a nicer door.

Four questions are enough. The first asks what the user does, accepts several answers because
being more than one thing is the normal case rather than an edge case, and is structural: it
activates schemas and resolves the take-or-teach, own-firm-or-client, own-résumé-or-candidate's
inversions. The second asks whether anyone else appears in the user's files — children,
dependants, clients — with names optional, and is structural: it is what makes a person-shaped
folder level safe or unsafe, and it supplies the values. The third asks what the user is here to
do, offering find things again, tidy up, archive, and not sure; it is structural for depth,
because a user who answers *find things again* should never be required to move a single file.
The fourth asks for an age range, is optional, and is contextual only; it may steer which
schemas are offered first and nothing else. Every question is skippable, and the product must
work correctly with all four skipped, because that is the behaviour it has today. The
declaration may only ever add resolving power; it may never be a precondition.

The second question is the most sensitive input the product ever takes, because it collects the
names of other people and often of children, and it takes them from the user rather than
extracting them from a file. It must be stored under the same protections as extracted personal
data and must not be included in cloud-model prompts by default. The rule that governs its use
is that a dependant's name may become a folder level and a third party's name may not, and the
discriminator is the answer to the first question — which is precisely why the two questions are
one mechanism and not two. A folder named for the user's child is a kindness; a folder named for
their client, their patient, or their employee discloses that a named person has a matter, a
record, or a case, and the product must never create it. Where the user skips the question, the
product returns to abstaining on which-person, which is the correct fallback.

The declaration is bounded and the bounds are absolute. It may not invent a schema: the schema
vocabulary is closed, and an answer either selects from it or is recorded honestly as unmatched.
It may not invent a dimension or a field key: the second question supplies values, never a new
column. It may not lower a privacy floor: it can make a level eligible, and it can never make
protected material placeable. It may not act unconfirmed, and the user must be able to see what
each answer changed. The interesting engineering problem is the first question's matcher, which
takes free text and must map it onto the closed schema vocabulary; it must record an unmatched
answer as unmatched rather than snapping it to the nearest neighbour, because "I'm a sound
engineer" is not the engineering schema, and silently deciding that it is would be the same
invention the model is forbidden to make about a file.

## B. Retrieval

The product already scores every file against every candidate destination, suppresses
destinations contradicted by the file's own facts, computes a margin between the leading
candidates, and reaches a two-condition verdict about whether the leader is good enough. All of
that exists so that files can be moved, and none of it is exposed to the person who owns the
files. For several kinds of user the thing that would change their week is not a reorganized
disk but the ability to find one document again, and the product should therefore expose a
read-only retrieval surface over the index it already builds. This surface should ship before
any automatic movement is offered, because it is useful without a single file being touched and
because it lets a user judge whether the product understands their corpus before trusting it to
rearrange it.

Retrieval must be read-only in the strongest sense: it moves nothing, renames nothing, writes no
tree, and freezes no plan. It must present every home a file has rather than the best one,
because a file with two correct homes is the ordinary case and not a failure — a paper written
for a course and submitted to a lab genuinely belongs in both places, and telling the user the
product is uncertain about it is the wrong sentence. Where the product declined to place a file
on purpose, that refusal is itself a result and must be shown as one: a passport is not a
low-confidence extraction, it is material the product protected deliberately, and the two must
never be reported in the same words. Protected areas must appear in results as present,
counted, and unopened, with a reachable explanation, and must never be filtered silently out of
a result set — a search that quietly omits protected material is telling the user their file
does not exist. Retrieval must reuse the existing scoring rather than introduce a second
ranking, because two rankings in one product are two products, and the day they disagree the
user has no way to tell which one is lying.

## C. Automatic filing

Automatic filing is the most dangerous capability in the product and should be designed as such.
Everything above is recoverable by ignoring it; a file moved without the user's understanding is
a file they may never find again, and the product's own residual design already recognizes that
a plausible-sounding wrong destination is worse than an honest unsorted one. Automatic filing
should therefore never be a mode the product enters on its own, never apply to material the
product protected, and never run without a complete and reversible record of what it did.

The design should be a policy the user sets rather than a confidence threshold the product
chooses. A user who has reviewed a branch and agrees with it should be able to say that files
matching that branch may be filed without further review, and that statement should be scoped to
the branch they actually looked at rather than generalized to the whole tree. Where the engine's
verdict is anything other than a clear leader — where the margin is small, where two homes are
genuinely tied, where evidence is thin, or where the file is protected — automatic filing must
decline and route the file to review, and it must decline in the words that describe what
actually happened rather than the words for low confidence. Every automatic action should be
presented afterwards as a reviewable list rather than as a completed fact, and every action
should be individually reversible for as long as the user might plausibly notice it. A dry run
that shows exactly what would move, without moving it, should always be available and should be
the default the first time a user enables the capability.

Two prohibitions govern it absolutely. Automatic filing may never touch protected material, may
never touch applications or system files, and may never open a protected container in order to
decide: such a container is marked and counted, never opened, and automatic filing does not
create an exception to that rule. And automatic filing may never create a destination. It
chooses among branches the user has already approved in the frozen tree, exactly as the residual
process does, and a file for which no approved destination fits stays where it is and is
surfaced — because the correct response to a file the product does not understand is to say so,
not to put it somewhere that sounds reasonable.
