"""A corpus profile: declared lives and the fields that are not schemas.

Stage 2 of docs/context-onboarding-plan.md. The record is stored and readable.
Nothing here is handed to the recogniser.
"""
from __future__ import annotations

import sqlite3

import pytest

from questions.profile import apply_profile, withdraw_profile
from questions.registry import QUESTION_KINDS
from questions.schema import create_questions_schema
from questions.store import (
    activated_schemas, declared_lives, left_alone, named_courses,
    named_projects, profile_wording, refused_lives,
)

T0 = "2026-09-30T12:00:00+00:00"
T1 = "2026-09-30T12:05:00+00:00"

# The founder's filing lives, as schema ids. Coursework, recruiting,
# applications, and projects. Leave-alone is not a schema.
LIVES = (
    "coursework=academic",
    "recruiting=career",
    "applications=college_applications",
    "projects=code",
)
REFUSED = (
    "business=business_operations",
    "construction=construction_property",
    "clinical=clinical_practice",
    "law=law_practice",
)


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    return connection


def _record(conn, **kwargs):
    apply_profile(
        conn, user_id="founder", recorded_at=T0,
        lives=kwargs.get("lives", ()),
        refused=kwargs.get("refused", ()),
        projects=kwargs.get("projects", ()),
        leave_alone=kwargs.get("leave_alone", ()),
        courses=kwargs.get("courses", ()),
        wording=kwargs.get("wording", ()),
    )


def test_confirmed_lives_are_returned_and_do_not_activate_schemas(qconn):
    _record(qconn, lives=LIVES, refused=REFUSED)
    assert declared_lives(qconn) == frozenset({
        "academic", "career", "college_applications", "code"})
    assert refused_lives(qconn) == frozenset({
        "business_operations", "construction_property",
        "clinical_practice", "law_practice"})
    assert activated_schemas(qconn) == frozenset()
    claimed = {kind.consequence_field for kind in QUESTION_KINDS}
    assert "declares_life" in claimed
    assert "activates_schema" != "declares_life"


def test_skip_revoke_and_not_about_me_leave_the_set_empty(qconn):
    _record(qconn, lives=("coursework=academic",))
    withdraw_profile(qconn, "life:coursework", state="skipped",
                     user_id="founder", recorded_at=T1)
    assert declared_lives(qconn) == frozenset()

    _record(qconn, lives=("recruiting=career",))
    withdraw_profile(qconn, "life:recruiting", state="revoked",
                     user_id="founder", recorded_at=T1)
    assert "career" not in declared_lives(qconn)

    _record(qconn, lives=("applications=college_applications",))
    withdraw_profile(qconn, "life:applications", state="not_applicable",
                     user_id="founder", recorded_at=T1)
    assert "college_applications" not in declared_lives(qconn)


def test_a_refusal_removes_a_life_that_was_also_declared(qconn):
    _record(qconn, lives=("business=business_operations",),
            refused=("business=business_operations",))
    assert "business_operations" not in declared_lives(qconn)
    assert "business_operations" in refused_lives(qconn)


def test_projects_courses_leave_alone_and_wording_round_trip(qconn):
    sentence = "Columbia ChemE junior, recruiting this term"
    _record(
        qconn,
        projects=("hackathon=hackathon-repo",),
        leave_alone=("dashboards=Power BI files", "export=LinkedIn export"),
        courses=("transport=CHEN 3120",),
        wording=(f"me={sentence}",),
    )
    assert named_projects(qconn) == ("hackathon-repo",)
    assert left_alone(qconn) == ("Power BI files", "LinkedIn export")
    assert named_courses(qconn) == ("CHEN 3120",)
    assert profile_wording(qconn) == (sentence,)
    assert declared_lives(qconn) == frozenset()


def test_a_choice_does_not_require_raw_wording(qconn):
    _record(qconn, lives=("coursework=academic",))
    assert declared_lives(qconn) == frozenset({"academic"})
    assert profile_wording(qconn) == ()
