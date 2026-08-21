# Domain swarm dispatch

R1a writes `../roster.json` here (path: `planning/domains/roster.json`).
R1b agents write `../nodes/<id>.json` — one file per domain, no shared writes.
R1c reads `../nodes/` and extends `../check.py`.

Stamp prompts:

```text
python3 planning/domains/dispatch/make_prompt.py --list
python3 planning/domains/dispatch/make_prompt.py acad.coursework.enrollment
python3 planning/domains/dispatch/make_prompt.py --all --out-dir /tmp/r1b-prompts
```
