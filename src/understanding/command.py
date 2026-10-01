# src/understanding/command.py
"""Name-only dry-run. It does not open files and it does not call a model.

The count is an upper bound: the deterministic tier has not run, so every
ordinary file is a candidate. Protected paths and private areas are not.
"""
from __future__ import annotations

import os
from pathlib import Path

from understanding.dossier import (
    FIELDS_THAT_LEAVE,
    WORD_CAP,
    FileView,
    NotSendable,
    build_dossier,
    path_is_protected,
    in_private_area,
)
from understanding.onboarding import questions_from_names
from understanding.run import cost_formula, dry_run_estimate
from understanding.store import STATEMENT


def _views(root: Path, private_areas: set[str]) -> tuple[list[dict], int]:
    dossiers = []
    excluded = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames
                       if name not in {".git", "node_modules"}
                       and not path_is_protected(str(Path(dirpath) / name))]
        for name in filenames:
            path = str(Path(dirpath) / name)
            view = FileView(
                file_id=path, path=path, filename=name,
                protected=path_is_protected(path) or in_private_area(path, private_areas))
            try:
                dossiers.append(build_dossier(view, private_areas=private_areas))
            except NotSendable:
                excluded += 1
    return dossiers, excluded


def dry_run_folder(root: Path, *, out, private_areas: set[str] | None = None,
                   offline: bool = True, consent: bool = False,
                   model_id: str = "") -> int:
    private = private_areas or set()
    dossiers, excluded = _views(root, private)
    estimate = dry_run_estimate(dossiers)
    print("Model dry-run. Nothing was sent. No network call was made.", file=out)
    print("The deterministic tier has not run, so this count is an upper "
          "bound: every ordinary file is a candidate.", file=out)
    print(f"Candidates: {estimate['files']}.", file=out)
    print(f"Excluded as protected or private: {excluded}.", file=out)
    print("Fields that would leave the device:", file=out)
    for field in FIELDS_THAT_LEAVE:
        print(f"    {field}", file=out)
    print(f"text_excerpt is the first {WORD_CAP} words.", file=out)
    print(f"Estimated input tokens: {estimate['estimated_input_tokens']} "
          f"(len(dossier_json) / 4).", file=out)
    print(f"Estimated output tokens: {estimate['estimated_output_tokens']} "
          f"(files * 512).", file=out)
    print(cost_formula(), file=out)
    print(f"Mode: {'offline' if offline else 'cloud allowed'}. "
          f"Consent recorded: {'yes' if consent else 'no'}.", file=out)
    if model_id:
        print(f"FAST model id configured: {model_id}.", file=out)
    else:
        print("No FAST model id is configured.", file=out)
    if offline:
        print("offline sends nothing, including after this dry-run.", file=out)
    return 0


def _names(root: Path) -> list[str]:
    names = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames
                       if name not in {".git", "node_modules"}
                       and not path_is_protected(str(Path(dirpath) / name))]
        for name in filenames:
            path = Path(dirpath) / name
            if path_is_protected(str(path)):
                continue
            names.append(name)
    return names


def onboarding_questions_folder(root: Path, *, out, consent: bool,
                                offline: bool, provider=None,
                                model_id: str = "",
                                declared_areas: set[str] | None = None) -> int:
    """Names only. No file is opened. Cloud calls need consent and a model.

    The role is reasoning. FAST is not used here.
    """
    names = _names(root)
    print(f"Names seen: {len(names)}. File contents were not read.", file=out)
    if offline:
        print("offline: the onboarding questions sent nothing.", file=out)
        return 0
    if not consent:
        print(STATEMENT, file=out)
        print("Pass --accept-cloud-understanding once for this folder. "
              "Nothing was sent.", file=out)
        return 0
    if provider is None or not model_id:
        print("Onboarding questions did not run: no reasoning model is "
              "configured. Nothing was sent.", file=out)
        return 0
    result = questions_from_names(
        names, declared_areas=declared_areas or set(), provider=provider,
        model_id=model_id, consent=True)
    print(result["summary"], file=out)
    for question in result["questions"]:
        print(f"- {question}", file=out)
    return 0
