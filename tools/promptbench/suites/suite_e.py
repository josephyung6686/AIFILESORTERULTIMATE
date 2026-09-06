# tools/promptbench/suites/suite_e.py
"""Site E stress cases: an accepted group that fits no template asks for one.

`00`:97 governs. The model receives the group's representative excerpts, the
validated facts, the approved label, the schema it sits in and the structural
constraints, and proposes a strict-JSON template: dimensions with a declared
scope and a citation each, levels with a retrieval justification, example label
chains. It may reference a published fragment; it may not publish one.

`allowed_vocabulary` is P10's closure for the schema (`allowed_vocabulary_for`),
which `field_glossary` then explains. Branch context that the live builder has
no channel for (the parent dimension, the schema id, the sensitivity policy
reference, the depth limit) arrives as `branch_context` items (packet §7, G10).
"""
from __future__ import annotations

from llm_harness.vocabulary import E_TEMPLATE
from production import load_shipped_catalogue, read_packaged_library_file
from tree_design.template_schema import allowed_vocabulary_for

from tools.promptbench.cases import Case, Item, evidence

PLAN = "plan-bench-1"
_CATALOGUE = load_shipped_catalogue(read_packaged_library_file)


def closure(uses_schema: str) -> tuple[str, ...]:
    return allowed_vocabulary_for(_CATALOGUE, uses_schema=uses_schema)


def _context(*lines: str) -> tuple[Item, ...]:
    return tuple(Item(evidence_ref=f"context-{i}", kind="branch_context", location=line)
                 for i, line in enumerate(lines, 1))


def _excerpt(group: str, file_id: str, address: str, value: str, zone: str):
    return evidence(subject_ref=group, address=f"{file_id}:{address}", value=value,
                    zone=zone, location=f"{zone} of {file_id}")


def _case(case_id, title, persona, traces, group, schema, context, excerpts, expect,
          *, should_abstain, notes="") -> Case:
    vocabulary = closure(schema)
    for name in expect.get("must_include", ()):
        assert name in vocabulary or expect.get("template_local_ok"), (case_id, name, vocabulary)
    return Case(
        case_id=case_id, site=E_TEMPLATE, title=title, persona=persona,
        traces=tuple(traces), subject_ref=group, allowed_vocabulary=vocabulary,
        evidence=tuple(excerpts),
        items=_context(f"uses_schema={schema}",
                       "sensitivity_policy_ref=policy.personal-default",
                       "maximum depth below this branch: 4 levels",
                       *context),
        plan_version=PLAN, expect=expect, should_abstain=should_abstain, notes=notes)


CASES = (
    _case(
        "E01", "a trip's photos: time first, then the occasion", "multi-life",
        ("00:95", "00:70"), "group:e01", "photos",
        ("accepted group label: Kyoto trip, July 2025", "parent branch: Photos (no dimension above)"),
        [_excerpt("group:e01", "f-p1", "metadata:DateTimeOriginal", "2025:07:17 09:12:03", "metadata"),
         _excerpt("group:e01", "f-p2", "metadata:DateTimeOriginal", "2025:07:18 16:40:11", "metadata"),
         _excerpt("group:e01", "f-p3", "metadata:GPS", "35.0116 N, 135.7681 E (Kyoto)", "metadata"),
         _excerpt("group:e01", "f-p4", "ocr:1", "Fushimi Inari Taisha", "ocr")],
        {"must_include": ["capture_year", "event"], "first": "capture_year",
         "must_exclude": ["people", "camera_information"]},
        should_abstain=False,
        notes="Photos are the exception where time belongs first."),
    _case(
        "E02", "a research group whose parent already is the project", "multi-life",
        ("00:97", "00:99"), "group:e02", "research",
        ("accepted group label: PVA/RDP manuscripts and figures",
         "parent branch: Research > PVA-RDP; the parent level already expresses project=PVA-RDP"),
        [_excerpt("group:e02", "f-ms", "heading:1", "PVA/RDP vascular grafts - manuscript draft 3", "heading"),
         _excerpt("group:e02", "f-fig", "heading:1", "Figure 3 - graft compliance versus time", "heading"),
         _excerpt("group:e02", "f-data", "title", "cohort-B-compliance.csv", "title"),
         _excerpt("group:e02", "f-ms", "body:1", "Submitted to the Journal of Biomedical Materials Research.", "body")],
        {"must_include": ["artifact_type"], "must_exclude": ["project", "authored_by", "lab"]},
        should_abstain=False,
        notes="Repeating the parent dimension is the first thing 00:97 forbids."),
    _case(
        "E03", "consulting deliverables all prepared by the same person", "Mara",
        ("00:44", "00:97"), "group:e03", "professional_services",
        ("accepted group label: GRC website engagement", "parent branch: Work"),
        [_excerpt("group:e03", "f-scope", "heading:1", "Statement of work - GRC website redesign", "heading"),
         _excerpt("group:e03", "f-scope", "body:1", "Prepared by Jane Doe for GRC.", "body"),
         _excerpt("group:e03", "f-survey", "heading:1", "Stakeholder survey results - GRC", "heading"),
         _excerpt("group:e03", "f-compare", "heading:1", "Vendor comparison - GRC website", "heading"),
         _excerpt("group:e03", "f-compare", "body:1", "Prepared by Jane Doe.", "body")],
        {"must_exclude": ["authored_by", "our_firm", "subject_of_record"], "template_local_ok": True},
        should_abstain=False,
        notes="Authorship is never a collector; the client or the engagement is."),
    _case(
        "E04", "a course where every file shares one term", "Priya",
        ("00:97", "00:99"), "group:e04", "academic",
        ("accepted group label: PHYS1401 course materials", "parent branch: Coursework",
         "every member states term=Spring 2026; no member states any other term"),
        [_excerpt("group:e04", "f-syl", "heading:1", "PHYS 1401 Syllabus - Spring 2026", "heading"),
         _excerpt("group:e04", "f-hw", "heading:1", "PHYS 1401 Homework 3 - Spring 2026", "heading"),
         _excerpt("group:e04", "f-exam", "heading:1", "PHYS 1401 Midterm - Spring 2026", "heading")],
        {"must_include": ["work_type"], "must_exclude": ["term", "instructor", "subject"]},
        should_abstain=False,
        notes="A level that produces one child is a meaningless level. Label corrected "
              "after the first cloud run: every member is PHYS 1401, so `subject` is a "
              "one-child level too and the model was right to leave it out."),
    _case(
        "E05", "a domain the library has no schema for", "Tom",
        ("00:97", "43:9"), "group:e05", "tabletop_games",
        ("accepted group label: Thursday D&D campaign", "parent branch: Personal Projects",
         "no shipped schema declares fields for this group; template-local dimensions are allowed"),
        [_excerpt("group:e05", "f-1", "heading:1", "Curse of Strahd - Session 12 notes", "heading"),
         _excerpt("group:e05", "f-2", "heading:1", "Curse of Strahd - Session 13 notes", "heading"),
         _excerpt("group:e05", "f-3", "title", "Barovia map v2", "title"),
         _excerpt("group:e05", "f-4", "heading:1", "Waterdeep campaign - Session 1 notes", "heading")],
        {"min_template_local": 1, "must_exclude": ["project", "event", "subject"],
         "template_local_ok": True, "max_dimensions": 4},
        should_abstain=False,
        notes="Template-local names, never another schema's field key relabelled as local."),
    _case(
        "E06", "a recurring pattern that tempts publication", "multi-life",
        ("00:97", "43:9"), "group:e06", "code",
        ("accepted group label: matcher repository", "parent branch: Code",
         "note from the engine: the same shape recurs in three other code branches"),
        [_excerpt("group:e06", "f-readme", "heading:1", "matcher - README", "heading"),
         _excerpt("group:e06", "f-manifest", "manifest:1", "package.json: name matcher, version 0.4.1", "manifest"),
         _excerpt("group:e06", "f-test", "title", "test_matcher.py", "title"),
         _excerpt("group:e06", "f-doc", "title", "docs/architecture.md", "title")],
        {"must_include": ["artifact_type"],
         "must_exclude": ["programming_language", "authored_by", "repository", "project"]},
        should_abstain=False,
        notes="A proposal may reference published fragments and may not publish one. Label "
              "corrected after the first cloud run: one repository and one project make "
              "one-child levels; only the kind of artifact splits these files."),
    _case(
        "E07", "financial records where a person would be the collector", "Tom",
        ("00:97", "00:185"), "group:e07", "finance",
        ("accepted group label: household statements 2025", "parent branch: Finance (protected area)"),
        [_excerpt("group:e07", "f-1", "heading:1", "Chase - checking statement, January 2025", "heading"),
         _excerpt("group:e07", "f-2", "heading:1", "Chase - checking statement, February 2025", "heading"),
         _excerpt("group:e07", "f-3", "heading:1", "Fidelity - brokerage statement, Q1 2025", "heading"),
         _excerpt("group:e07", "f-4", "heading:1", "Form 1099-INT, tax year 2024", "heading")],
        {"must_include": ["institution"], "must_exclude": ["account_holder", "subject_of_record", "people"]},
        should_abstain=False),
    _case(
        "E08", "evidence that supports more levels than a tree should have", "multi-life",
        ("00:97", "00:99"), "group:e08", "research",
        ("accepted group label: COVID19-Stroke study", "parent branch: Research"),
        [_excerpt("group:e08", "f-1", "heading:1", "COVID19-Stroke - analysis notebook, cohort A, 2024, draft 2, R", "heading"),
         _excerpt("group:e08", "f-2", "heading:1", "COVID19-Stroke - manuscript, submitted to Stroke journal, 2025", "heading"),
         _excerpt("group:e08", "f-3", "heading:1", "COVID19-Stroke - figure 2, cohort B", "heading"),
         _excerpt("group:e08", "f-4", "heading:1", "COVID19-Stroke - dataset, cohort A, de-identified", "heading")],
        {"must_include": ["artifact_type"], "max_dimensions": 4, "must_exclude": ["authored_by"]},
        should_abstain=False),
    _case(
        "E09", "a dimension no file has a value for", "multi-life",
        ("00:97",), "group:e09", "research",
        ("accepted group label: iPSC differentiation reading", "parent branch: Research"),
        [_excerpt("group:e09", "f-1", "title", "iPSC differentiation protocols - lab notebook, March", "title"),
         _excerpt("group:e09", "f-2", "title", "iPSC differentiation - protocol v3", "title"),
         _excerpt("group:e09", "f-3", "title", "iPSC differentiation - journal article (saved)", "title")],
        {"must_include": ["artifact_type"], "must_exclude": ["venue", "lab", "authored_by"]},
        should_abstain=False,
        notes="No file names a venue or a lab; a level over them would be empty."),
    _case(
        "E10", "a group with no recoverable facts", "Tom", ("00:97", "00:63"), "group:e10",
        "academic",
        ("accepted group label: misc", "parent branch: Documents"),
        [_excerpt("group:e10", "f-1", "body:1", "see attached", "body"),
         _excerpt("group:e10", "f-2", "body:1", "final final v2", "body")],
        {"abstain": True},
        should_abstain=True),
    _case(
        "E11", "recruiting documents: the employer before the cycle", "multi-life",
        ("00:95", "00:70"), "group:e11", "career",
        ("accepted group label: 2026 internship applications", "parent branch: Career"),
        [_excerpt("group:e11", "f-1", "heading:1", "EY - summer internship application, 2026 cycle", "heading"),
         _excerpt("group:e11", "f-2", "heading:1", "EY - cover letter", "heading"),
         _excerpt("group:e11", "f-3", "heading:1", "Deloitte - summer internship application, 2026 cycle", "heading"),
         _excerpt("group:e11", "f-4", "title", "Resume - 2026", "title")],
        {"must_include": ["target_employer"], "first": "target_employer",
         "must_exclude": ["authored_by", "employer"]},
        should_abstain=False,
        notes="For document domains the subject comes before time."),
    _case(
        "E12", "a code project: repository, not language", "multi-life",
        ("00:30", "00:97"), "group:e12", "code",
        ("accepted group label: ThirdEye", "parent branch: Code"),
        [_excerpt("group:e12", "f-1", "manifest:1", "pyproject.toml: name thirdeye", "manifest"),
         _excerpt("group:e12", "f-2", "title", "thirdeye/detector.py", "title"),
         _excerpt("group:e12", "f-3", "title", "docs/README.md", "title"),
         _excerpt("group:e12", "f-4", "title", "config/settings.yaml", "title")],
        {"must_include": ["artifact_type"],
         "must_exclude": ["programming_language", "authored_by", "repository", "project"]},
        should_abstain=False,
        notes="Label corrected after the first cloud run for the same reason as E06: one "
              "repository is a one-child level."),
)
