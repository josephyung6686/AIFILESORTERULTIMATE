"""Done-means 8 — P1's code contains no fact-field name, domain name, template name,
sensitivity class, or tier name (§3.11, §5.7, §7.3, §8.4 belong elsewhere).

The §8.6 ceiling keys and the nineteen reserved event names are NOT exceptions:
both are §0/§8.2/§8.6 vocabulary the design states literally, and neither names a
fact, a domain, or a class.
"""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "database_agent"

FORBIDDEN = [
    # §3.11 domain fact fields
    "course", "syllabus", "instructor", "semester", "target_university",
    "application_cycle", "artifact_type", "tax_year", "capture_year",
    # §7.3 residual template names
    "reference clips", "reading inbox", "review later", "protected records",
    # §8.4 sensitivity classes
    "sensitive personal", "credential-bearing", "public or low",
    # §5.4 template dimension names used as P1 vocabulary
    "work type", "admissions",
]


def test_p1_source_contains_no_other_parts_vocabulary():
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN:
            if term in text:
                offenders.append(f"{path.name}: {term!r}")
    assert not offenders, "P1 leaked interpretation: " + "; ".join(offenders)


def test_p1_stores_sensitivity_as_an_opaque_value():
    # P1 carries sensitivity_state as a column but defines none of P7's classes.
    text = (SRC / "files_table.py").read_text(encoding="utf-8")
    assert "sensitivity_state" in text
    for cls in ("sensitive personal", "credential", "unclassified"):
        assert cls not in text.lower()
