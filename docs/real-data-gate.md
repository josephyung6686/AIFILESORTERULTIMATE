# Real-data profile-gate measurement

Date: 2026-10-02.

## What the one-pager reported

On a copy of Downloads (~1,833 files), without a declared-lives gate, the gist
showed roughly: Business 736, Construction 237, Creative 170, Clinical 18,
Law 11, Academic 40.

## What this repo can do now

`tools/measure_profile_gate.py` scores every file that already has observation
rows in a plan database, with optional `--declared` lives, and prints the same
kind of category counts. It does not move files.

```bash
python3 tools/measure_profile_gate.py \
  --database /path/to/plan.sqlite \
  --declared academic,career,college_applications,code
```

## Gap

There is **no checked-in database** of the founder’s Downloads scan in this
checkout. The local `database-agent-plan.sqlite` is a tiny fixture corpus (9
files), not the 1,833-file run. Until a Downloads scan database is available
(or re-created), the exact one-pager counts cannot be reproduced here.

Synthetic proof that the gate changes winners remains in
`tests/recognition/test_declared_lives_gate.py` (coursework+business → academic
when declared; business-only → `outside_declared_lives`).

## Editorial

Do not invent a new Downloads score. Report only numbers from a real scan
database or from the synthetic tests. Agent pitch and view release order stay
open on the one-pager.
