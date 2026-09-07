# tools/promptbench/suites/suite_c.py
"""Site C stress cases: one file, a shortlist of legal nodes, a hierarchical judge.

`00`:104-116 governs. The file's evidence is released; the candidates are legal
nodes of one frozen plan, each carried as a `candidate` evidence item whose
`location` is the node's label chain and what it expects -- the profile `00`:105
asks for and the live builder cannot yet carry (packet §7, G3). Accepted-group
context arrives as an `accepted_group` item. The file's OWN folder, when it is a
candidate, says so in its profile, which is what `104` §13.8's refinement-versus-
removal split turns on.

Node ids are opaque, as the product mints them. Expectations name the node the
case author would file to, `"none"` where `00` says abstain or ask.
"""
from __future__ import annotations

import hashlib

from llm_harness.vocabulary import C_PLACEMENT

from tools.promptbench.cases import Case, Item, evidence

PLAN = "plan-bench-1"

# The frozen tree the cases draw from. One plan, opaque ids, readable profiles.
NODES = {
    "n-01": "Coursework > PHYS1401 | expects subject=PHYS 1401 | holds every kind of work for the course",
    "n-02": "Coursework > PHYS1401 > syllabus | expects subject=PHYS 1401; work_type=syllabus",
    "n-03": "Coursework > PHYS1401 > homework | expects subject=PHYS 1401; work_type=homework | holds problem sets and worksheets",
    "n-04": "Coursework > PHYS1401 > exam | expects subject=PHYS 1401; work_type=exam",
    "n-05": "Coursework > PHYS1401 > General | scoped fallback for PHYS 1401 files with no recoverable kind of work",
    "n-06": "Coursework > PHYS1403 > syllabus | expects subject=PHYS 1403; work_type=syllabus",
    "n-07": "Coursework > PHYS2801 > homework | expects subject=PHYS 2801; work_type=homework",
    "n-08": "Coursework > 2026-Spring > PHYS1401 > homework | expects term=Spring 2026; subject=PHYS 1401; work_type=homework",
    "n-09": "Applications > Columbia > 2026 > supporting materials | expects target_university=Columbia; application_cycle=2026",
    "n-10": "Applications > Duke > 2026 > supporting materials | expects target_university=Duke; application_cycle=2026",
    "n-11": "Applications > Shared Application Materials | shared-material branch for documents that serve more than one application",
    "n-12": "Applications > Columbia > 2026 > essays | expects target_university=Columbia; application_document_type=essay",
    "n-13": "Applications > Duke > 2026 > essays | expects target_university=Duke; application_document_type=essay",
    "n-14": "Coursework > Python 1006 | the person's own existing folder; the file sits in this folder now",
    "n-15": "Coursework > Python 1006 > lecture | a child of the folder the file sits in now | expects work_type=lecture",
    "n-16": "Household > Ada > report cards | the person's own existing folder; the file sits in this folder now",
    "n-17": "Coursework > SPRING2026 > report card | expects term=Spring 2026; work_type=report card",
    "n-18": "Applications > Columbia > 2026 > portal records | expects target_university=Columbia; application_document_type=portal record",
    "n-19": "Applications > Duke > 2026 > portal records | expects target_university=Duke; application_document_type=portal record",
    "n-20": "Applications > MIT > 2026 > essays | expects target_university=MIT; application_document_type=essay",
    "n-21": "Applications > UChicago > 2026 > essays | expects target_university=UChicago; application_document_type=essay",
    "n-22": "Coursework > Georgetown Prep > essay | expects school=Georgetown Prep; work_type=essay",
    "n-23": "Coursework > University Writing > essay | expects subject=University Writing; work_type=essay",
}


def _candidates(*ids: str) -> tuple[Item, ...]:
    return tuple(Item(evidence_ref=node, kind="candidate", location=NODES[node])
                 for node in ids)


def _group(group_id: str, text: str) -> Item:
    return Item(evidence_ref=group_id, kind="accepted_group", location=text,
                reliability_state="possible", basis="context-supported")


def _shuffled(case_id: str, ids) -> tuple[str, ...]:
    """Candidates in an order that carries no information about the answer.

    Zheng et al. 2023 and Pezeshkpour & Hruschka 2024 measure position bias in
    option lists; an author who lists the right node first would be measuring
    that bias and calling it the prompt's accuracy."""
    return tuple(sorted(ids, key=lambda n: hashlib.sha256(
        f"{case_id}:{n}".encode("utf-8")).hexdigest()))


def _case(case_id, title, persona, traces, subject, items, candidates, expect, *,
          should_abstain, extra_items=(), conflicts=(), notes="") -> Case:
    candidates = _shuffled(case_id, candidates)
    return Case(
        case_id=case_id, site=C_PLACEMENT, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject,
        allowed_vocabulary=tuple(candidates),
        evidence=tuple(evidence(subject_ref=subject, **item) for item in items),
        items=_candidates(*candidates) + tuple(extra_items),
        conflicts=tuple(conflicts), plan_version=PLAN,
        authorities={"frozen_nodes": tuple(NODES)},
        expect=expect, should_abstain=should_abstain, notes=notes)


CASES = (
    _case(
        "C01", "a syllabus that uniquely matches one node", "Priya",
        ("00:110", "104:13.5"), "file:c01",
        [dict(address="heading:1", value="PHYS 1401 Syllabus, Spring 2026", zone="heading"),
         dict(address="body:1", value="Course description, grading policy and schedule.", zone="body")],
        ("n-02", "n-01", "n-06"),
        {"destination": "n-02"}, should_abstain=False,
        notes="The unique direct match is the top-ranked candidate, not a bypass."),
    _case(
        "C02", "a sparse homework file placed through its accepted group", "Priya",
        ("00:108", "00:111"), "file:c02",
        [dict(address="heading:1", value="Homework 3", zone="heading"),
         dict(address="body:1", value="Problem 1. A block slides down a frictionless incline.", zone="body")],
        ("n-03", "n-05", "n-07"),
        {"destination": "n-03"}, should_abstain=False,
        extra_items=(_group("group-phys1401", "accepted group: PHYS1401 course materials; this file is a context-supported member, retrieved with the course's lecture and midterm"),),
        notes="HW 3.pdf: homework by name and structure, course by group context."),
    _case(
        "C03", "a term the deeper node carries and the file contradicts", "Priya",
        ("00:111", "00:107"), "file:c03",
        [dict(address="heading:1", value="PHYS 1401 Problem Set 2", zone="heading"),
         dict(address="body:1", value="Spring 2025. Due Friday.", zone="body")],
        ("n-08", "n-03", "n-01"),
        {"destination": "n-03"}, should_abstain=False,
        notes="Spring 2025 is not Spring 2026: the approved shallower path, never a filled slot."),
    _case(
        "C04", "a transcript with two supported homes and no shared branch", "multi-life",
        ("00:113", "00:239"), "file:c04",
        [dict(address="title", value="Official Transcript", zone="title"),
         dict(address="body:1", value="Cumulative GPA 3.9. Courses and grades follow.", zone="body")],
        ("n-09", "n-10"),
        {"destination": "none"}, should_abstain=True,
        extra_items=(_group("group-columbia", "accepted group: Columbia application packet; this file is a member"),
                     _group("group-duke", "accepted group: Duke application packet; this file is a member")),
        notes="No shared branch exists: the system must not arbitrarily choose one university."),
    _case(
        "C05", "the same transcript when a shared branch exists", "multi-life",
        ("00:113",), "file:c05",
        [dict(address="title", value="Official Transcript", zone="title"),
         dict(address="body:1", value="Cumulative GPA 3.9. Courses and grades follow.", zone="body")],
        ("n-11", "n-09", "n-10"),
        {"destination": "n-11"}, should_abstain=False,
        extra_items=(_group("group-columbia", "accepted group: Columbia application packet; this file is a member"),
                     _group("group-duke", "accepted group: Duke application packet; this file is a member"))),
    _case(
        "C06", "a Duke essay retrieved by a Columbia packet, with the conflict recorded", "multi-life",
        ("00:107", "00:112", "00:114"), "file:c06",
        [dict(address="heading:1", value="Why Duke?", zone="heading"),
         dict(address="body:1", value="Duke University's Pratt School is where I want to build.", zone="body")],
        ("n-13", "n-12"),
        {"destination": "n-13"}, should_abstain=False,
        conflicts=(("conflict-target-duke", "target_university"),),
        extra_items=(_group("group-columbia", "accepted group: Columbia application packet; this file was retrieved as a candidate member"),),
        notes="Measures G1: a correct answer that echoes the shown conflict id is rejected CONFLICT_IGNORED."),
    _case(
        "C07", "refinement: a lecture sitting in its own course folder", "multi-life",
        ("104:13.8", "00:22"), "file:c07",
        [dict(address="title", value="Lecture 1: Introduction to Python", zone="title"),
         dict(address="heading:1", value="Python 1006", zone="heading"),
         dict(address="body:1", value="What is a program? Variables, types and the REPL.", zone="body")],
        ("n-14", "n-15", "n-01"),
        {"destination": "n-15", "refinement": "deeper_in_own_folder"}, should_abstain=False,
        notes="Moving deeper inside the branch the file already sits in is the model's call."),
    _case(
        "C08", "removal: a report card in the folder its parent keeps it in", "Tom",
        ("104:13.8", "00:22", "68:F5"), "file:c08",
        [dict(address="title", value="Report Card - Spring 2026", zone="title"),
         dict(address="body:1", value="Grade 4. Reading: A. Mathematics: A-.", zone="body")],
        ("n-16", "n-17"),
        {"destination": "n-17", "refinement": "out_of_own_folder"}, should_abstain=False,
        notes="Out of the person's arrangement is a constraint the product surfaces; the model names it."),
    _case(
        "C09", "a file linked only by a generic hub", "multi-life",
        ("00:63", "00:109"), "file:c09",
        [dict(address="body:1", value="Sent from my phone. columbia.edu", zone="body"),
         dict(address="body:2", value="See you Thursday.", zone="body")],
        ("n-12", "n-18"),
        {"destination": "none"}, should_abstain=True,
        notes="A university domain bridges everything and supports nothing."),
    _case(
        "C10", "MIT inside submit", "Priya",
        ("00:43", "00:239"), "file:c10",
        [dict(address="heading:1", value="PHYS 1401 Problem Set 2", zone="heading"),
         dict(address="body:1", value="Please submit by Friday at noon.", zone="body")],
        ("n-03", "n-20"),
        {"destination": "n-03"}, should_abstain=False),
    _case(
        "C11", "a number that is an invoice, not a course", "Tom",
        ("00:239", "00:46"), "file:c11",
        [dict(address="heading:1", value="Invoice 1401 - Order confirmation", zone="heading"),
         dict(address="body:1", value="Thank you for your purchase. Total: $42.10.", zone="body")],
        ("n-05", "n-01"),
        {"destination": "none"}, should_abstain=True,
        notes="Course-code patterns that are ZIP codes, invoices or device models."),
    _case(
        "C12", "a course file with no recoverable kind of work", "Priya",
        ("00:99", "00:111"), "file:c12",
        [dict(address="heading:1", value="PHYS 1401 - Office hours and contact sheet", zone="heading"),
         dict(address="body:1", value="Office hours Monday 2-4. TA: Priya.", zone="body")],
        ("n-03", "n-04", "n-05"),
        {"destination": "n-05"}, should_abstain=False,
        notes="The scoped General under the meaningful parent, never a filled slot."),
    _case(
        "C13", "a packet member placed inside its confirmed packet", "multi-life",
        ("00:112",), "file:c13",
        [dict(address="title", value="Certificate of Achievement", zone="title"),
         dict(address="body:1", value="Awarded to the applicant for first place, regional science fair.", zone="body")],
        ("n-09", "n-12"),
        {"destination": "n-09"}, should_abstain=False,
        extra_items=(_group("group-columbia", "accepted group: Columbia application packet; this file is an accepted supporting-material member"),)),
    _case(
        "C14", "an essay naming the author's school and the target university", "multi-life",
        ("00:44", "104:11.1"), "file:c14",
        [dict(address="heading:1", value="Why UChicago?", zone="heading"),
         dict(address="body:1", value="At Georgetown Prep I learned to argue on paper.", zone="body"),
         dict(address="body:2", value="The University of Chicago's core is where that argument belongs.", zone="body")],
        ("n-21", "n-22"),
        {"destination": "n-21"}, should_abstain=False,
        notes="The regression's mechanism at the placement site: the mentioned school is metadata."),
    _case(
        "C15", "a screenshot whose OCR is noise", "multi-life",
        ("00:110", "00:125"), "file:c15",
        [dict(address="ocr:1", value="l0g1n p0rtal ... 2O26 ... c0ntinue", zone="ocr"),
         dict(address="metadata:1", value="PNG 1170x2532", zone="metadata")],
        ("n-18", "n-19"),
        {"destination": "none"}, should_abstain=True),
    _case(
        "C16", "a university course essay whose own course node exists", "multi-life",
        ("104:11.1", "00:44"), "file:c16",
        [dict(address="heading:1", value="University Writing - Essay 2", zone="heading"),
         dict(address="body:1", value="At Georgetown Prep I learned to argue on paper.", zone="body")],
        ("n-23", "n-22"),
        {"destination": "n-23"}, should_abstain=False,
        notes="The five essays: University Writing/essay, not Coursework/Georgetown Prep/essay."),
)
