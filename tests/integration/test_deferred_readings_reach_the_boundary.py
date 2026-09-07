# tests/integration/test_deferred_readings_reach_the_boundary.py
"""R-08: the authored readings are collected and counted, and they stop at a wall.

`102` §3 found the shipped library's `recognition.needs_llm` rows -- prose saying, per
situation, exactly what a model must decide and when it must abstain -- loaded by
`recognition.rules` into `SchemaRules.deferred_readings` and appearing *"nowhere
outside `src/recognition/`"*. `104` R-08 is that finding; `104` §7 Phase 1 step 5 asks
for the situation's readings to be sent *"under a key the ratified template names, or
route to D2"*.

**There is no such key, and the template says so about itself.** The shipped A_fact
revision tells the model the dossier *"has these keys and no others"* and lists
fifteen. `llm_harness.dossier._body` writes exactly those fifteen. A sixteenth would
make the model's own instructions false about the bytes beside them, and prompt text
is the owner's to ratify, never an agent's. So the plumbing runs to the wall and
stops there: the readings reach `FactCallAuthorities`, where the A_fact request is
built from, and are not written into the dossier.

**The numbers the packet needs, measured here rather than asserted.**

  * 314 `needs_llm` ROWS across 23 schemas, carrying 1,984 individual readings. (The
    "314 rows" in `102` is rows; the reading count is six times larger.)
  * `SchemaRules.deferred_readings` is the SCHEMA's, not the situation's:
    `recognition.rules._schema` flattens every row's `readings` and discards the
    `row` key that says which situation authored them. So a coursework run holds
    `academic`'s 69 readings, 14,491 characters -- **3.6x the whole 4,000 dossier
    ceiling on their own**, and `law_practice` holds 67,167 characters.
  * The situation's own share is small: `academic.coursework`'s row plus the
    schema-wide `academic` row is 11 readings and 2,015 characters.

Which is the finding the packet turns on. Sending a schema's readings per call is not
affordable and never will be; sending a situation's is, and needs `row` preserved
through `recognition.rules`. Both numbers are pinned below so the packet argues from
measurement.
"""
from __future__ import annotations

import inspect
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from llm_harness.dossier import _body  # noqa: E402
from llm_harness.prompt_library import (  # noqa: E402
    a_fact_template_folder_levels_bytes,
)
from model_facts import dossier_tokens, measure_released_tokens  # noqa: E402
from recognition.rules import load_rules  # noqa: E402

SITUATION = "academic.coursework"
SCHEMA = "academic"


def _manifest() -> dict:
    return json.loads(cli._RECOGNITION_MANIFEST.read_text(encoding="utf-8"))


def _rules():
    return load_rules(cli._RECOGNITION_MANIFEST.read_text)


def _authorities(conn, **overrides):
    """The shape `cli.run` builds, with the same library reads it makes."""
    from production import (
        folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    )
    from readers.model_routing import FAST, LOGIC, REASONING, deepseek_routing

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    routing = deepseek_routing(
        api_key="not-a-key", base_url="https://example.invalid",
        model_id_of_tier={REASONING: "r", LOGIC: "l", FAST: "f"},
        tier_of_call_site=cli.TIER_OF_CALL_SITE,
        max_response_tokens=cli.MAX_RESPONSE_TOKENS, timeout_seconds=1.0)
    values = dict(
        routing=routing, scan_run_id="scan", corpus_file_count=1,
        policy_version="policy", wire_handle_key=bytes(32), schema=SCHEMA,
        folder_levels=folder_levels_for(catalogue, SITUATION), user_id="t",
        now=lambda: "2026-09-05T00:00:00+00:00")
    values.update(overrides)
    return cli.fact_call_authorities(conn, **values)


# --- collected ------------------------------------------------------------------


def test_the_readings_the_run_holds_are_the_librarys_own_verbatim():
    """Not a count of them and not a summary: the strings, in order.

    Compared against the manifest parsed here, so a compiler change that dropped or
    reworded a reading fails this rather than passing quietly.
    """
    authored = tuple(
        reading
        for entry in _manifest()["schemas"][SCHEMA]["needs_llm"]
        for reading in entry["readings"]
    )
    assert _rules().schemas[SCHEMA].deferred_readings == authored
    assert len(authored) == 69


def test_every_schema_a_situation_can_name_carries_readings():
    """1,984 readings over 314 rows, and no schema a person can reach is empty.

    An empty one would mean a run whose model is steered by nothing while another
    run in the same product is steered by prose -- a difference nobody chose.
    """
    manifest = _manifest()["schemas"]
    rows = sum(len(schema.get("needs_llm", ())) for schema in manifest.values())
    readings = sum(len(entry["readings"])
                   for schema in manifest.values()
                   for entry in schema.get("needs_llm", ()))
    assert (rows, readings) == (314, 1984)

    rules = _rules()
    for schema_id in sorted(rules.schemas):
        assert rules.schemas[schema_id].deferred_readings, schema_id


def test_the_authorities_carry_them_and_default_to_none_of_them(conn):
    """The slot the A_fact request is built from. Defaulted, because a deployment
    with no compiled release is a real state and an empty tuple is what it has --
    unlike `folder_levels`, whose absence is a wiring failure and refuses."""
    readings = _rules().schemas[SCHEMA].deferred_readings
    assert _authorities(conn, deferred_readings=readings).deferred_readings == \
        readings
    assert _authorities(conn).deferred_readings == ()


def test_the_run_is_what_supplies_them_and_it_reads_the_compiled_release():
    """The composition root joins the two, and the join is checked at the source.

    `_model_fact_pass` is only reachable with a credential and `--enable-cloud`, so
    no test may execute it; what can be checked is that the line exists and reads
    the release `run` already loaded rather than a second copy of the library.
    """
    source = inspect.getsource(cli.run)
    assert "deferred_readings=rules.schemas[schema].deferred_readings" in source
    assert source.count("load_rules(") == 1


# --- counted --------------------------------------------------------------------


def test_the_cost_of_the_readings_is_measured_and_it_does_not_fit(conn):
    """The number the packet argues from, in the units the ceiling is kept in.

    `academic`'s 69 readings are 14,491 characters against a 4,000 dossier ceiling.
    Per SCHEMA they can never be sent; the situation's own share is 2,015. The
    measurement is `dossier_tokens`, the same upper bound the gate uses, so the two
    numbers are comparable.
    """
    readings = _rules().schemas[SCHEMA].deferred_readings
    assert dossier_tokens(readings) == 14491
    assert dossier_tokens(readings) > cli.GROUPING_LIMITS.max_dossier_tokens * 3

    rows = _manifest()["schemas"][SCHEMA]["needs_llm"]
    situation = tuple(
        reading
        for entry in rows
        if entry["row"] in (SITUATION, SCHEMA)
        for reading in entry["readings"]
    )
    assert len(situation) == 11
    assert dossier_tokens(situation) == 2015

    # And the attribution that would let a run take the second number is thrown
    # away: `SchemaRules` keeps the readings and not the `row` they came from.
    assert not hasattr(_rules().schemas[SCHEMA], "row")


def test_the_gate_ceiling_still_measures_only_what_is_released(conn):
    """The readings are NOT added to `measure_released_tokens`, deliberately.

    That function answers "how many characters would the provider receive", and the
    readings reach no provider. Counting them there would refuse calls for bytes
    nobody sends -- a coverage regression wearing a budget fix's name -- and
    `dossier_tokens`' own docstring already excludes the situation-constant material
    (template, levels, vocabulary) for exactly this reason. When the packet adds the
    key, the readings join that same prefix, not this ceiling.
    """
    class _Item:
        def __init__(self, value: str) -> None:
            self.value = value

    readings = _rules().schemas[SCHEMA].deferred_readings
    assert measure_released_tokens(None, [_Item("abcd")]) == 4
    assert measure_released_tokens(None, []) == 0
    assert dossier_tokens(readings) not in (0, 4)


# --- and there they stop --------------------------------------------------------


def _template_key_list() -> tuple[str, ...]:
    text = a_fact_template_folder_levels_bytes().decode("utf-8")
    marker = "The dossier has these keys and no others: "
    start = text.index(marker) + len(marker)
    return tuple(key.strip()
                 for key in text[start:text.index(".", start)].split(","))


def test_the_template_names_no_key_for_a_reading():
    """The wall, in the model's own instructions. Parsed from the shipped bytes."""
    keys = _template_key_list()
    assert len(keys) == 15
    assert not [key for key in keys
                if "reading" in key or "needs_llm" in key or "defer" in key]


def test_the_dossier_body_is_exactly_the_keys_the_template_names():
    """So a sixteenth cannot arrive without the sentence above being edited first.

    `_body` is the only function in the product that writes model-visible bytes,
    and this compares its output against the prose that describes it rather than
    against a list re-typed here.
    """
    body = json.loads(_body(
        call_site=cli.A_FACT, subject_ref="file-1",
        eligibility_reason="remains_ambiguous", plan_version=None,
        policy_version="policy-1", max_dossier_tokens=4000,
        reduction_rung="none", allowed_vocabulary=("subject",),
        folder_levels=(), evidence_items=(), conflicts=(), released_evidence=(),
        prompt=cli.a_fact_prompt(), handle_key=bytes(32)).decode("utf-8"))
    assert tuple(sorted(body)) == tuple(sorted(_template_key_list()))


def test_no_reading_reaches_the_bytes_the_model_is_shown():
    """The assertion R-08 stays open under. It fails the day the key is added, and
    that failure is the signal to close the register entry."""
    raw = _body(
        call_site=cli.A_FACT, subject_ref="file-1",
        eligibility_reason="remains_ambiguous", plan_version=None,
        policy_version="policy-1", max_dossier_tokens=4000,
        reduction_rung="none", allowed_vocabulary=("subject",),
        folder_levels=(), evidence_items=(), conflicts=(), released_evidence=(),
        prompt=cli.a_fact_prompt(), handle_key=bytes(32))
    for reading in _rules().schemas[SCHEMA].deferred_readings:
        assert reading.encode("utf-8") not in raw
