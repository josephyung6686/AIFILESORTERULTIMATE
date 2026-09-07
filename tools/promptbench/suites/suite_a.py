# tools/promptbench/suites/suite_a.py
"""Site A stress cases for the `school` and `subject` glossary entries.

Fix-chain step 1 (`104` §11.2): `school` for coursework's `holder_institution`
must mean the institution that offers this course and term, and a school merely
mentioned is `authored_by`-class metadata (`00`:44) and never a level; `subject`
must mean the course as the course names itself, and a study guide, textbook or
publisher is not one. The same folder-levels template is shown under both
glossaries; only the two meanings differ. The cases are the regression's own
mechanisms (`104` §11.1), the personas of `68`, and `00`:239's adversarial list.

Expectations are per field: a value means "propose exactly this spelling", `None`
means "decline". Fields not named are not judged. Every value is the minimal
identifying run of characters as the evidence spells it (ratified rule 4 and 5).
"""
from __future__ import annotations

from llm_harness.vocabulary import A_FACT

from tools.promptbench.cases import Case, evidence

SITUATION = "academic.coursework"
SCHEMA = "academic"


def _case(case_id: str, title: str, persona: str, traces, subject: str,
          items, expect_fields: dict, *, should_abstain: bool, notes: str = "") -> Case:
    return Case(
        case_id=case_id, site=A_FACT, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject, allowed_vocabulary=(),
        evidence=tuple(evidence(subject_ref=subject, **item) for item in items),
        expect={"fields": expect_fields}, should_abstain=should_abstain,
        schema_id=SCHEMA, situation=SITUATION, notes=notes)


CASES = (
    _case(
        "A01", "a university course essay that names the author's old school and a target university",
        "multi-life", ("104:11.1", "00:44"), "file:a01",
        [dict(address="title", value="Essay 2 Final Draft", zone="title"),
         dict(address="heading:1", value="University Writing - Essay 2", zone="heading"),
         dict(address="body:3", value="At Georgetown Prep I learned to argue on paper.", zone="body"),
         dict(address="body:9", value="This is why I want to study at the University of Chicago.", zone="body")],
        {"subject": "University Writing", "school": None, "work_type": "Essay"},
        should_abstain=False,
        notes="The regression: the ratified wording files this under Georgetown Prep."),
    _case(
        "A02", "a CliffsNotes study guide asked coursework's subject",
        "multi-life", ("104:11.1", "00:63"), "file:a02",
        [dict(address="title", value="CliffsNotes on The Great Gatsby", zone="title"),
         dict(address="body:1", value="Published by Houghton Mifflin Harcourt. All rights reserved.", zone="body"),
         dict(address="heading:2", value="Chapter summaries and analysis", zone="heading")],
        {"subject": None, "school": None, "work_type": None},
        should_abstain=True,
        notes="The publisher is not a course; a node was minted from it on the cloud run."),
    _case(
        "A03", "a syllabus that states the course, the institution and the term",
        "Priya", ("00:38", "00:41"), "file:a03",
        [dict(address="title", value="Syllabus", zone="title"),
         dict(address="heading:1", value="PHYS 1401 - General Physics I", zone="heading"),
         dict(address="body:1", value="Columbia University, Department of Physics. Spring 2026.", zone="body"),
         dict(address="body:2", value="Instructor: Dr. Lee. Lectures Tuesday and Thursday.", zone="body")],
        {"subject": "PHYS 1401", "school": "Columbia University", "term": "Spring 2026",
         "work_type": "Syllabus"},
        should_abstain=False),
    _case(
        "A04", "a resume that lists the schools attended",
        "multi-life", ("104:11.1", "00:44"), "file:a04",
        [dict(address="heading:1", value="Education", zone="heading"),
         dict(address="body:1", value="Georgetown Preparatory School, 2020-2024", zone="body"),
         dict(address="body:2", value="Columbia University, B.A. expected 2028", zone="body"),
         dict(address="heading:2", value="Experience", zone="heading")],
        {"school": None, "subject": None, "work_type": None},
        should_abstain=True,
        notes="Spillover control: resumes name schools attended and are not coursework."),
    _case(
        "A05", "a homework file with the course code and nothing else",
        "Priya", ("00:55", "00:57"), "file:a05",
        [dict(address="heading:1", value="PHYS 1401 Homework 3", zone="heading"),
         dict(address="body:1", value="1. A block slides down a frictionless incline of angle 30 degrees.", zone="body")],
        {"subject": "PHYS 1401", "work_type": "Homework", "school": None, "term": None},
        should_abstain=False),
    _case(
        "A06", "lecture slides whose footer names the university that teaches the course",
        "Priya", ("00:43", "104:11.2"), "file:a06",
        [dict(address="title", value="Lecture 08: Rotational Dynamics", zone="title"),
         dict(address="footer:1", value="Columbia University", zone="header_footer"),
         dict(address="body:4", value="Torque is the rate of change of angular momentum.", zone="body")],
        {"school": "Columbia University", "subject": None, "work_type": "Lecture"},
        should_abstain=False,
        notes="A footer on course material names the provider; there is no course name to propose."),
    _case(
        "A07", "a textbook chapter naming its publisher",
        "Priya", ("104:11.2",), "file:a07",
        [dict(address="title", value="Chapter 5: Thermodynamics", zone="title"),
         dict(address="body:1", value="Fundamentals of Physics, 10th edition. Wiley.", zone="body"),
         dict(address="body:2", value="The first law states that energy is conserved.", zone="body")],
        {"subject": None, "school": None},
        should_abstain=True,
        notes="A textbook or publisher is not a course."),
    _case(
        "A08", "a study guide that names the course it is for",
        "Tom", ("104:11.2",), "file:a08",
        [dict(address="title", value="AP World History Study Guide - Unit 3", zone="title"),
         dict(address="body:1", value="Barron's. Key terms: Silk Road, Mongol Empire.", zone="body")],
        {"subject": "AP World History", "school": None},
        should_abstain=False,
        notes="The course names itself in the title; the publisher is still not the course."),
    _case(
        "A09", "an application essay addressed to a target university",
        "multi-life", ("00:44", "00:47"), "file:a09",
        [dict(address="heading:1", value="Common App Personal Statement", zone="heading"),
         dict(address="body:2", value="Duke's engineering program is where I want to build this.", zone="body"),
         dict(address="body:5", value="Word count: 648", zone="body")],
        {"school": None, "subject": None},
        should_abstain=True,
        notes="Duke is the target, never the school that offers a course."),
    _case(
        "A10", "a course named by title, with a term the pattern list covers",
        "Priya", ("00:46", "00:38"), "file:a10",
        [dict(address="heading:1", value="Introduction to Organic Chemistry", zone="heading"),
         dict(address="body:1", value="Tutorial sheet 4, Michaelmas term", zone="body")],
        {"subject": "Introduction to Organic Chemistry", "term": "Michaelmas term",
         "work_type": "Tutorial sheet", "school": None},
        should_abstain=False),
    _case(
        "A11", "a lab report whose body mentions the author's high school in passing",
        "multi-life", ("00:44", "104:11.2"), "file:a11",
        [dict(address="heading:1", value="PHYS 1401 Lab Report 2", zone="heading"),
         dict(address="body:3", value="When I was at Georgetown Prep we never used a photogate.", zone="body")],
        {"subject": "PHYS 1401", "school": None, "work_type": "Lab Report"},
        should_abstain=False),
    _case(
        "A12", "an online course offered by a university through a platform",
        "multi-life", ("104:11.2",), "file:a12",
        [dict(address="title", value="Coursera - Machine Learning, Week 3 Quiz", zone="title"),
         dict(address="body:1", value="This course is offered by Stanford University.", zone="body")],
        {"school": "Stanford University", "subject": "Machine Learning", "work_type": "Quiz"},
        should_abstain=False,
        notes="The institution that OFFERS the course is the school, not the platform."),
    _case(
        "A13", "a transcript listing many courses at two institutions",
        "multi-life", ("00:113", "104:11.2"), "file:a13",
        [dict(address="title", value="Official Transcript", zone="title"),
         dict(address="body:1", value="Georgetown Preparatory School - Grades 9 to 12", zone="body"),
         dict(address="body:2", value="Columbia University - Fall 2024: PHYS 1401 A, MATH 1101 A-", zone="body")],
        {"subject": None, "school": None},
        should_abstain=True,
        notes="A transcript is not one course; two schools are named and neither offers this file."),
    _case(
        "A14", "an exam whose room number looks like a course number",
        "Priya", ("00:239",), "file:a14",
        [dict(address="heading:1", value="Final Exam - Room 1401", zone="heading"),
         dict(address="heading:2", value="PHYS 2801 Final", zone="heading"),
         dict(address="body:1", value="Answer all six questions. Time allowed: three hours.", zone="body")],
        {"subject": "PHYS 2801", "work_type": "Final Exam"},
        should_abstain=False),
)
