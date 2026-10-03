# File companion onboarding

This is the onboarding UI. The screens are built from `source/`.

```bash
python3 src/onboarding/ui/build.py
python3 -m onboarding.ui_app --write ./answers.json
```

Open the printed address. The page asks for folders, a profile, work areas, and categories. When the choices are finished and folder access was granted, Save choices & scan writes `answers.json` in the shape `filesorter` already reads. The write is atomic and happens before any engine scan. This page does not start that scan and does not move files.

A scan of a real folder is the existing command, after the file exists:

```bash
database-agent FOLDER --database ./plan.sqlite --answers ./answers.json
```

Name and school are collected on the Student profile because the answers file already requires them. They are not filled in ahead of time. Sensitive finance, identity, medical, and legal material is held and is not written as a life. Only confirmed categories that match a known life are used. Refused and pending categories are not. Counts on the briefing stay empty until a real scan reports them.

The timer on the local-scan screen is still a preview. macOS folder permission prompts are still a preview. The workspace after the handoff is not built here.

`Review.html` jumps to a screen or an edge state. Those controls sit outside the product window.

```bash
node --test src/onboarding/ui/tests/model.test.js
python3 -m pytest tests/onboarding/test_snapshot_answers.py
```
