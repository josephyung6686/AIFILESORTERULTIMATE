# Product one-pager (v2)

> Founder product write-up (Alana, Sep 30, 2026). Canonical consumer / context-graph direction for FileSorter.
> Older engine design (Joseph): [`planning/00-database-agent-product-design.md`](../planning/00-database-agent-product-design.md).

**Date:** Sep 30, 2026. **Supersedes:** `one-pager.md` (the go/no-go note, kept unchanged).
**Tags:** plain statements are **founder decisions** (Sep 30, 2026) or **verified facts** from the repo audit. Anything not decided by the founder is tagged **[Proposal]**. No usage, market, or revenue numbers exist yet, and none are invented here.

## What changed (founder decisions, Sep 30 2026)

The product is no longer "a virtual library of files for students." It is a **context graph** over everything a person already has. Files, folders, emails, calendar events, tasks, people and projects are all connected **items** with **relationships**, built automatically from evidence. Example: this PDF was attached to that email, which is about that event, which belongs to that project.

- **Not student-only.** Students are the first starting profile/template. Other profiles come later: job seeker, researcher, freelancer, founder.
- **The folder tree is one view, not the product.** Classic Folder view stays. New views: Graph, Timeline, Board, Table.
- **Files never move on disk.** Clicking an item opens the original. Gmail and Calendar are read-only.

## Why it is different

Notion makes you build structure by hand. This builds structure **automatically from what already exists** on the laptop and in Gmail/Calendar. The pitch is "sorting what exists," not "start a workspace and fill it in."

## The views (founder decision: these views exist; layouts are [Proposal])

| View | Shows | Notes |
|---|---|---|
| Graph | Relationships between items | Focus on one item and its neighbors; filter by project/time to avoid a hairball |
| Timeline | Items by date and deadline | |
| Board | Items by project and status | |
| Table | Notion-style, filterable list | |
| Folder | The classic tree | One view among several |

## The agent: one ladder, three capabilities (founder decision)

1. **The connector.** Notices that an email, a file and an event are about the same thing and keeps them linked.
2. **The nudge.** Watches deadlines and says what is missing before time runs out.
3. **The assistant.** Answers questions about your own stuff, e.g. "what did the recruiter send me and what do I still owe them?"

All three sit on the same ladder. The agent acts **only with user approval**. Nothing is silent. There is no cloud bypass of protected holds.

### Agent one-sentence pitch: PLACEHOLDER

> **[PLACEHOLDER: the founder said the agent's one-sentence pitch is still being fleshed out. Do not fill this in until the founder supplies it. Do not reuse old wording such as "virtual library" or "proactive sorter" as a stand-in.]**

## Kept from before (founder decisions)

- Onboarding where the user confirms or refuses categories.
- Correction memory (approve / reject / undo feed back).
- Local search, local-first privacy.
- AI mode: BYOK, local-only, or managed.
- First ~300 files free, then paid: premium search and the download watcher.

## Honest status (what is proven and what is not)

- **Sorter engine:** works on a 10-file test.
- **Real data, not good:** on a real 1,833-file Downloads copy it **mislabeled student files**: 736 as Business operations, 237 Construction, 170 Creative, 18 Clinical, 11 Law, 40 Academic.
- **Profile gate:** just built on PR #2. Proven **only on synthetic text**. **Not yet re-run on real files.**

### Repo audit

| Area | Finding |
|---|---|
| Correction memory | Only exact-match suppression of repeated rejects. **No learning.** |
| Template library | **None exists.** |
| Graphs | Two narrow ones exist: a file-version evidence graph and a node-local placement graph. |
| Index | A SQLite index exists. |
| Opening originals | Nothing opens originals from an in-app library. |
| Item / relationship model, views | **Do not exist yet.** |

So the reframe is a direction and a design, not a working product. Nothing above the sorter engine is built, and the engine has not yet passed a real-data check.

## Moat (honest)

The defensible combination is: **automatic structure from real data + learning correction memory + researched profile templates.** None is built today: correction memory does not learn, no templates exist, and the real-data run failed. Spotlight, Notion, Obsidian, Tidy and Apple are each close on parts (search, structure, linking, sorting, system integration). No claim here that any of them lacks a given feature beyond what earlier research verified.

## Risks [Proposal]

- **Real-data accuracy is the gate.** The real-file mislabeling above would destroy trust in a graph that claims to know how your stuff connects. Wrong links are more visible than wrong folders.
- **Link quality, not link count.** Every link needs visible evidence and approve/reject/undo. The graph view can become an unreadable hairball without focus and filter defaults.
- **Scope jump.** Going from "sort files" to "items + relationships + five views + agent" is a large step from a repo that has no item model yet.
- **Not student-only adds a generalization burden** on templates that do not exist yet.

## Suggested next steps [Proposal]

1. Re-run the profile gate on the real 1,833-file Downloads copy and report the same category counts.
2. Define the item and relationship model with evidence per link (the wireframe brief v2 assumes it).
3. Make correction memory actually learn, or stop calling it learning.
4. Build one view end to end (Graph in focus mode or Table) on real data before the others.
5. Research one non-student template to test that the model generalizes.
6. Get the founder's agent pitch to replace the placeholder above.

## Open questions for the founder

- What is the agent's one-sentence pitch? (placeholder above)
- Which profile comes after students?
- Does every link need user confirmation, or only low-confidence ones?
- What is the release order of views?
