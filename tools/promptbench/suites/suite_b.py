# tools/promptbench/suites/suite_b.py
"""Site B stress cases: one candidate group, four constrained questions.

`00`:55-64 governs. A dossier separates anchor files from context-supported
candidates (`00`:58); the model judges coherence, per-member inclusion, outliers
and conflicts, and proposes a label and a category only if coherence holds
(`00`:59). Every member arrives as a `member` evidence item; each released
excerpt's item names the member it was read from, and the proposed basis
arrives as an item too -- three things the live seam does not yet carry
(packet §7, G9).

`allowed_vocabulary` is the category ids the label may be filed under; the live
product defines none (G4), so the bench defines the shipped situation ids.
"""
from __future__ import annotations

from llm_harness.vocabulary import B_GROUP

from tools.promptbench.cases import Case, Item, evidence

CATEGORIES = (
    "academic.coursework", "academic.teaching", "applications.undergraduate-packet",
    "applications.purpose-packet", "research.manuscript-publication",
    "career.recruiting", "photos.camera-events", "law_practice.discovery",
)


def _member(file_id: str, document_type: str, *, anchor: bool, why: str = "") -> Item:
    return Item(
        evidence_ref=file_id, kind="member",
        location=(f"{document_type}; direct anchor: states the group's basis itself"
                  if anchor else f"{document_type}; candidate retrieved by {why}"),
        reliability_state="direct" if anchor else "possible",
        basis="direct-anchor" if anchor else "context-supported")


def _basis(text: str) -> Item:
    return Item(evidence_ref="proposed-basis", kind="proposed_basis", location=text)


def _excerpt(group: str, file_id: str, address: str, value: str, zone: str,
             *, anchor: bool = True):
    return evidence(subject_ref=group, address=f"{file_id}:{address}", value=value,
                    zone=zone, location=f"{zone} of {file_id}",
                    reliability_state="direct" if anchor else "possible",
                    basis="direct-anchor" if anchor else "context-supported")


def _case(case_id, title, persona, traces, group, basis, members, excerpts, expect,
          *, should_abstain, conflicts=(), notes="") -> Case:
    return Case(
        case_id=case_id, site=B_GROUP, title=title, persona=persona,
        traces=tuple(traces), subject_ref=group, allowed_vocabulary=CATEGORIES,
        evidence=tuple(excerpts), items=(_basis(basis),) + tuple(members),
        conflicts=tuple(conflicts), plan_version=None,
        expect=expect, should_abstain=should_abstain, notes=notes)


CASES = (
    _case(
        "B01", "a course group with a direct syllabus anchor and a sparse homework candidate",
        "Priya", ("00:57", "00:60"), "group:b01", "PHYS1401 course materials",
        [_member("f-syl", "pdf", anchor=True), _member("f-lec", "pdf", anchor=True),
         _member("f-hw3", "pdf", anchor=False, why="mutual semantic retrieval with the syllabus and the lecture; homework-shaped filename")],
        [_excerpt("group:b01", "f-syl", "heading:1", "PHYS 1401 Syllabus - Spring 2026, Columbia University", "heading"),
         _excerpt("group:b01", "f-lec", "title", "PHYS 1401 Lecture 08: Rotational Dynamics", "title"),
         _excerpt("group:b01", "f-hw3", "heading:1", "Homework 3", "heading", anchor=False),
         _excerpt("group:b01", "f-hw3", "body:1", "Problem 1. A block slides down a frictionless incline.", "body", anchor=False)],
        {"coherent": "yes", "members": {"f-syl": "include", "f-lec": "include", "f-hw3": "uncertain|include"},
         "label_required": True, "category_in": ["academic.coursework"]},
        should_abstain=False,
        notes="HW 3 may be uncertain rather than automatically included (00:60)."),
    _case(
        "B02", "one course code, two terms", "Priya", ("00:63", "00:62"), "group:b02",
        "PHYS1401 course materials",
        [_member("f-syl25", "pdf", anchor=True), _member("f-syl26", "pdf", anchor=True),
         _member("f-hw", "pdf", anchor=False, why="shared validated fact: PHYS 1401")],
        [_excerpt("group:b02", "f-syl25", "heading:1", "PHYS 1401 Syllabus - Spring 2025", "heading"),
         _excerpt("group:b02", "f-syl26", "heading:1", "PHYS 1401 Syllabus - Spring 2026", "heading"),
         _excerpt("group:b02", "f-hw", "heading:1", "PHYS 1401 Problem Set 2", "heading", anchor=False)],
        {"coherent_in": ["no", "insufficient"]},
        should_abstain=True,
        notes="A course code alone should not merge different semesters."),
    _case(
        "B03", "a Duke essay inside a Columbia packet", "multi-life",
        ("00:58", "00:59", "00:62"), "group:b03", "Columbia application packet",
        [_member("f-essay-col", "docx", anchor=True), _member("f-checklist", "pdf", anchor=True),
         _member("f-transcript", "pdf", anchor=False, why="bounded download session with the checklist; compatible document type"),
         _member("f-essay-duke", "docx", anchor=False, why="mutual semantic retrieval with the Columbia essay")],
        [_excerpt("group:b03", "f-essay-col", "heading:1", "Why Columbia?", "heading"),
         _excerpt("group:b03", "f-checklist", "heading:1", "Columbia University application checklist", "heading"),
         _excerpt("group:b03", "f-transcript", "title", "Official Transcript", "title", anchor=False),
         _excerpt("group:b03", "f-essay-duke", "heading:1", "Why Duke?", "heading", anchor=False),
         _excerpt("group:b03", "f-essay-duke", "body:1", "Duke University's Pratt School is where I want to build.", "body", anchor=False)],
        {"coherent": "yes",
         "members": {"f-essay-col": "include", "f-checklist": "include",
                     "f-transcript": "include|uncertain", "f-essay-duke": "exclude"},
         "outliers": ["f-essay-duke"], "label_required": True,
         "category_in": ["applications.undergraduate-packet", "applications.purpose-packet"]},
        should_abstain=False,
        conflicts=(("conflict-target-b03", "target_institution"),)),
    _case(
        "B04", "files bridged only by a university email domain", "multi-life",
        ("00:63", "00:57"), "group:b04", "columbia.edu correspondence",
        [_member("f-1", "eml", anchor=True), _member("f-2", "eml", anchor=True),
         _member("f-3", "pdf", anchor=True)],
        [_excerpt("group:b04", "f-1", "body:1", "From: registrar@columbia.edu - Your enrollment", "body"),
         _excerpt("group:b04", "f-2", "body:1", "From: careers@columbia.edu - Fall recruiting fair", "body"),
         _excerpt("group:b04", "f-3", "body:1", "Contact: physics-help@columbia.edu", "body")],
        {"coherent_in": ["no", "insufficient"]},
        should_abstain=True,
        notes="One high-frequency entity as the only bridge."),
    _case(
        "B05", "a purpose-coherent application submission packet", "multi-life",
        ("00:45", "00:61"), "group:b05", "Columbia application submission",
        [_member("f-portal", "png", anchor=True), _member("f-checklist", "pdf", anchor=True),
         _member("f-transcript", "pdf", anchor=False, why="named on the checklist; bounded session"),
         _member("f-resume", "pdf", anchor=False, why="named on the checklist; bounded session"),
         _member("f-statement", "docx", anchor=False, why="named on the checklist")],
        [_excerpt("group:b05", "f-portal", "ocr:1", "Your Columbia University application has been submitted.", "ocr"),
         _excerpt("group:b05", "f-checklist", "heading:1", "Application checklist: transcript, resume, personal statement", "heading"),
         _excerpt("group:b05", "f-transcript", "title", "Official Transcript", "title", anchor=False),
         _excerpt("group:b05", "f-resume", "heading:1", "Resume", "heading", anchor=False),
         _excerpt("group:b05", "f-statement", "heading:1", "Personal Statement", "heading", anchor=False)],
        {"coherent": "yes",
         "members": {"f-portal": "include", "f-checklist": "include", "f-transcript": "include",
                     "f-resume": "include", "f-statement": "include"},
         "label_required": True,
         "category_in": ["applications.undergraduate-packet", "applications.purpose-packet"]},
        should_abstain=False,
        notes="Content-incoherent, purpose-coherent, with direct application evidence."),
    _case(
        "B06", "a tight download session with no purpose evidence", "Tom",
        ("00:61", "00:45"), "group:b06", "download session 2026-03-02 14:02-14:05",
        [_member("f-img", "png", anchor=True), _member("f-receipt", "pdf", anchor=True),
         _member("f-syl", "pdf", anchor=True)],
        [_excerpt("group:b06", "f-img", "metadata:1", "PNG 1170x2532", "metadata"),
         _excerpt("group:b06", "f-receipt", "body:1", "Order confirmation. Total $42.10.", "body"),
         _excerpt("group:b06", "f-syl", "heading:1", "AP World History - course outline", "heading")],
        {"coherent_in": ["no", "insufficient"]},
        should_abstain=True,
        notes="A session is a retrieval clue, never proof of shared purpose."),
    _case(
        "B07", "a research abstract that also supports an application", "multi-life",
        ("00:63", "00:48"), "group:b07", "UChicago application packet",
        [_member("f-checklist", "pdf", anchor=True), _member("f-portal", "png", anchor=True),
         _member("f-abstract", "pdf", anchor=False, why="named on the checklist as a research abstract")],
        [_excerpt("group:b07", "f-checklist", "heading:1", "UChicago application checklist: essay, transcript, research abstract", "heading"),
         _excerpt("group:b07", "f-portal", "ocr:1", "University of Chicago - application received", "ocr"),
         _excerpt("group:b07", "f-abstract", "title", "PVA/RDP vascular grafts: an abstract", "title", anchor=False)],
        {"coherent": "yes", "members": {"f-checklist": "include", "f-portal": "include", "f-abstract": "include"},
         "label_required": True, "category_in": ["applications.undergraduate-packet", "applications.purpose-packet"]},
        should_abstain=False,
        notes="A file may belong to more than one accepted group."),
    _case(
        "B08", "a university name that is a target, a provider and an employer", "multi-life",
        ("00:63",), "group:b08", "Columbia",
        [_member("f-essay", "docx", anchor=True), _member("f-syl", "pdf", anchor=True),
         _member("f-resume", "pdf", anchor=True)],
        [_excerpt("group:b08", "f-essay", "heading:1", "Why Columbia?", "heading"),
         _excerpt("group:b08", "f-syl", "body:1", "Columbia University, Department of Physics. PHYS 1401.", "body"),
         _excerpt("group:b08", "f-resume", "body:1", "Columbia University - research assistant, 2025", "body")],
        {"coherent_in": ["no", "insufficient"]},
        should_abstain=True),
    _case(
        "B09", "a coherent course group that needs a label", "Priya",
        ("00:59",), "group:b09", "PHYS1401 course materials, Spring 2026",
        [_member("f-syl", "pdf", anchor=True), _member("f-lec", "pdf", anchor=True),
         _member("f-mid", "pdf", anchor=True)],
        [_excerpt("group:b09", "f-syl", "heading:1", "PHYS 1401 Syllabus - Spring 2026", "heading"),
         _excerpt("group:b09", "f-lec", "title", "PHYS 1401 Lecture 08", "title"),
         _excerpt("group:b09", "f-mid", "heading:1", "PHYS 1401 Midterm Practice", "heading")],
        {"coherent": "yes", "members": {"f-syl": "include", "f-lec": "include", "f-mid": "include"},
         "label_required": True, "category_in": ["academic.coursework"]},
        should_abstain=False),
    _case(
        "B10", "a conflicting course code among the candidates", "Priya",
        ("00:59", "00:62"), "group:b10", "PHYS1401 course materials",
        [_member("f-syl", "pdf", anchor=True), _member("f-lec", "pdf", anchor=True),
         _member("f-ps2801", "pdf", anchor=False, why="mutual semantic retrieval with the lecture")],
        [_excerpt("group:b10", "f-syl", "heading:1", "PHYS 1401 Syllabus", "heading"),
         _excerpt("group:b10", "f-lec", "title", "PHYS 1401 Lecture 08", "title"),
         _excerpt("group:b10", "f-ps2801", "heading:1", "PHYS 2801 Problem Set 3", "heading", anchor=False)],
        {"coherent": "yes", "members": {"f-syl": "include", "f-lec": "include", "f-ps2801": "exclude"},
         "outliers": ["f-ps2801"], "label_required": True, "category_in": ["academic.coursework"]},
        should_abstain=False),
    _case(
        "B11", "a photo event with a screenshot in the same hour", "multi-life",
        ("00:56", "00:32"), "group:b11", "photo event 2025-07-17, Kyoto",
        [_member("f-p1", "heic", anchor=True), _member("f-p2", "heic", anchor=True),
         _member("f-p3", "heic", anchor=True),
         _member("f-shot", "png", anchor=False, why="capture time inside the event window")],
        [_excerpt("group:b11", "f-p1", "metadata:DateTimeOriginal", "2025:07:17 09:12:03", "metadata"),
         _excerpt("group:b11", "f-p2", "metadata:DateTimeOriginal", "2025:07:17 09:14:40", "metadata"),
         _excerpt("group:b11", "f-p3", "metadata:GPS", "35.0116 N, 135.7681 E", "metadata"),
         _excerpt("group:b11", "f-shot", "metadata:1", "PNG 1170x2532, no EXIF, software: iOS", "metadata", anchor=False)],
        {"coherent": "yes", "members": {"f-p1": "include", "f-p2": "include", "f-p3": "include",
                                         "f-shot": "exclude|uncertain"},
         "label_required": True, "category_in": ["photos.camera-events"]},
        should_abstain=False),
    _case(
        "B12", "a TA's solution set with the student's own problem set as a candidate", "Priya",
        ("68:F6", "00:59"), "group:b12", "PHYS2801 teaching materials",
        [_member("f-sol", "pdf", anchor=True), _member("f-rubric", "pdf", anchor=True),
         _member("f-ps1401", "pdf", anchor=False, why="compatible document type; same author")],
        [_excerpt("group:b12", "f-sol", "heading:1", "PHYS 2801 Problem Set 3 - Solutions (TA copy)", "heading"),
         _excerpt("group:b12", "f-rubric", "heading:1", "PHYS 2801 grading rubric", "heading"),
         _excerpt("group:b12", "f-ps1401", "heading:1", "PHYS 1401 Problem Set 2", "heading", anchor=False)],
        {"coherent": "yes", "members": {"f-sol": "include", "f-rubric": "include", "f-ps1401": "exclude"},
         "outliers": ["f-ps1401"], "label_required": True,
         "category_in": ["academic.teaching", "academic.coursework"]},
        should_abstain=False,
        notes="Which of her two roles a file belongs to; the solution set must not sit beside submissions."),
    _case(
        "B13", "versions of one essay", "multi-life", ("00:239", "00:56"), "group:b13",
        "version family: Essay 2",
        [_member("f-v1", "pdf", anchor=True), _member("f-v2", "pdf", anchor=True),
         _member("f-docx", "docx", anchor=False, why="version stem match")],
        [_excerpt("group:b13", "f-v1", "heading:1", "University Writing - Essay 2 - Final Draft", "heading"),
         _excerpt("group:b13", "f-v2", "heading:1", "University Writing - Essay 2 - Final Draft (1)", "heading"),
         _excerpt("group:b13", "f-docx", "heading:1", "University Writing - Essay 2", "heading", anchor=False)],
        {"coherent": "yes", "members": {"f-v1": "include", "f-v2": "include", "f-docx": "include"},
         "label_required": True, "category_in": ["academic.coursework"]},
        should_abstain=False),
    _case(
        "B14", "a litigator's matter with an e-filing receipt", "Mara",
        ("68:2", "00:59"), "group:b14", "matter CV20261234",
        [_member("f-motion", "docx", anchor=True), _member("f-depo", "pdf", anchor=True),
         _member("f-log", "xlsx", anchor=True),
         _member("f-receipt", "pdf", anchor=False, why="shared validated fact: CV20261234")],
        [_excerpt("group:b14", "f-motion", "heading:1", "Motion to compel - Case No. CV20261234", "heading"),
         _excerpt("group:b14", "f-depo", "heading:1", "Deposition transcript, CV20261234", "heading"),
         _excerpt("group:b14", "f-log", "table:1", "Privilege log - CV20261234", "table"),
         _excerpt("group:b14", "f-receipt", "body:1", "Receipt for e-filing fee, CV20261234", "body", anchor=False)],
        {"coherent": "yes", "members": {"f-motion": "include", "f-depo": "include", "f-log": "include",
                                         "f-receipt": "include|uncertain"},
         "label_required": True, "category_in": ["law_practice.discovery"]},
        should_abstain=False),
    _case(
        "B15", "duplicate suffixes on unrelated files", "Tom", ("00:239", "00:172"), "group:b15",
        "version family: Report",
        [_member("f-r1", "pdf", anchor=True), _member("f-r2", "pdf", anchor=True)],
        [_excerpt("group:b15", "f-r1", "heading:1", "Q3 sales report - Rivooo K12", "heading"),
         _excerpt("group:b15", "f-r2", "heading:1", "PHYS 1401 Lab Report 2", "heading")],
        {"coherent_in": ["no", "insufficient"]},
        should_abstain=True,
        notes="A filename match alone does not make a family."),
)
