# tests/integration/test_exif_stays_local.py
"""CR-05b, end to end: a GPS coordinate a real extractor produced cannot be released.

The finding, reproduced against the real gate before this file existed:

    metadata:field=GPSLatitude  -> Released "37 deg 46' 29.64\" N"

§8.4 puts `image_exif` and `gps` in the always-local nine. `extractors/image.py`
emits every EXIF tag into `zone="metadata"`, which is the TRUTHFUL zone for one -- so
P7's always-local ZONE rule (CR-01) cannot reach them, and `ZONES` has no `exif`
member to move them to. Adding one would need owner approval and a `SHAPE_VERSION`
bump, and refusing on a list of tag NAMES would make `privacy/items.py` own the
"gazetteer ... keyword list" its own module docstring forbids.

So the fix uses the channel the design already had and only E3 was using: P5 raises a
`SensitivitySignal`, P4 keys it to an `observation_key`, and `check_item` refuses an
`Excerpt` over a signalled key under §8.4's `raw_sensitive_values`. That is WR-07's
image half, closed.

**This test runs all four parts.** The real `extract_image`, the real `RunWriter`, the
real `record_sensitivity_signals`, and the real `Gate`. `tests/p5/
test_p5_image_sensitivity.py` proves the remap that connects the first two; this
proves the chain reaches the door. Neither is sufficient alone: a correct remap that
nothing records still releases the coordinate, and a recorded signal keyed to the
wrong row refuses the wrong value while the coordinate goes out.
"""
from __future__ import annotations

import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.locator import serialize_locator
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, observation_keys_for_run
from extractors.image import ExifValue, ImageRecord, extract_image
from extractors.long_tail import record_sensitivity_signals
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.gate import Gate
from privacy.items import Excerpt
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.schema import create_privacy_schema

OBSERVED_AT = "2026-09-02T09:00:00Z"
PLAN_VERSION = "plan-exif"
COMPONENT = "0.1.0"
CLOUD = ModelTarget(locality="cloud", model_id="a-model", provider="Acme")
MAX_DOSSIER_TOKENS = 4000
CONTENT_HASH = "c977b477a6329f00518d55e10bb5c469fc6b24e8528f3fc1a9bbbbe94a6feada"

#: A real photo's shape. `DateTime` and `DateTimeOriginal` agree, as they do on
#: almost every camera, so D10 collapses them and every row after shifts -- the case
#: an identity remap gets wrong.
GPS_LATITUDE = "38.6488N"
A_PHOTO = ImageRecord(
    image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
    perceptual_hash="phash:8f3a",
    exif=(ExifValue(name="DateTime", value="2026:07:17 14:03:22",
                    kind="capture time"),
          ExifValue(name="DateTimeOriginal", value="2026:07:17 14:03:22",
                    kind="capture time"),
          ExifValue(name="Make", value="Apple", kind="camera EXIF"),
          ExifValue(name="GPSLatitude", value=GPS_LATITUDE, kind="GPS")),
    color={"ColorSpace": "sRGB"}, software={"Software": "iOS 19.1"})


@pytest.fixture()
def exif_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    return conn


def _scanned_photo(conn) -> tuple[str, dict[str, str]]:
    """P1's row, P5's run, P4's rows, and P5's signals -- the live sequence.

    This is what `orchestrator.run_wave2` does for one image, with nothing stubbed
    between the extractor and the database.
    """
    corpus = Path(tempfile.mkdtemp()) / "corpus"
    corpus.mkdir()
    photo = corpus / "IMG_4821.heic"
    photo.write_bytes(b"\x00\x00\x00\x18ftypheic")
    file_id = record_file(
        conn, photo, filename=photo.name, normalized_filename=photo.name.lower(),
        extension=".heic", observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="image/heic",
        detected_format="heic", scan_state="scanned", materialized=True,
        content_hash=CONTENT_HASH)

    produced = extract_image(
        file_row={"file_id": file_id, "content_hash": CONTENT_HASH,
                  "filename": photo.name},
        path=photo,
        policy=SafetyPolicy(is_protected_container=lambda p: False,
                            is_dataless=lambda p: False),
        read_image=lambda target: A_PHOTO,
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        now=OBSERVED_AT, context_window=20)

    run_id = RunWriter(conn, author="extractors").write(produced.extraction)
    keys = observation_keys_for_run(conn, run_id)
    record_sensitivity_signals(
        conn, run_id=run_id, signals=produced.sensitivity,
        observation_keys=keys, now=OBSERVED_AT)

    by_value = {row["raw_value"]: keys[i]
                for i, row in enumerate(produced.extraction.observations)}

    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=CONTENT_HASH, handling_class="public_low",
        protected=False, basis="detector", evidence_refs=(keys[0],),
        reliability_state="direct", observed_at=OBSERVED_AT))
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(("area-1", "cloud_model"),),
        redaction_settings=dict(MORE_REDACTING), automatic_move_permissions={},
        plan_version=PLAN_VERSION, set_at=OBSERVED_AT)
    set_policy(conn, draft, component_version=COMPONENT, user_id="joseph",
               reason="exif end to end")
    return file_id, by_value


def _gate(conn) -> Gate:
    return Gate(
        conn, store=ClassificationStore(conn), plan_version=PLAN_VERSION,
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1",
        files_in_scope=lambda scope: (),
        component_version=COMPONENT, now=lambda: OBSERVED_AT, user_id="joseph")


def _ask(conn, file_id: str, key: str):
    return _gate(conn).release(ModelCallRequest(
        stage="fact_resolution", target=Target(file_ids=(file_id,)),
        model_target=CLOUD,
        requested_items=(Excerpt(observation_key=key, span=None, reason="metadata"),),
        prompt_template_id="template.under-ratification",
        prompt_fingerprint="fingerprint-exif-1",
        max_dossier_tokens=MAX_DOSSIER_TOKENS))


def test_a_gps_coordinate_from_a_real_photo_is_refused(exif_conn):
    """The finding, closed. Before this chain existed the gate returned `Released`
    with the coordinate as the item's value."""
    file_id, by_value = _scanned_photo(exif_conn)
    decision = _ask(exif_conn, file_id, by_value[GPS_LATITUDE])
    assert isinstance(decision, Denied), (
        f"a GPS coordinate was {type(decision).__name__}; §8.4 places 'gps' and "
        "'image_exif' in the always-local set")
    assert decision.reason == "always_local_item"
    assert GPS_LATITUDE not in decision.explanation


@pytest.mark.parametrize("value", ["Apple", "2026:07:17 14:03:22"])
def test_every_other_exif_tag_is_refused_too(exif_conn, value):
    """`image_exif` is a member of the nine in its own right, so the refusal is not
    the GPS tag's alone. `ExifValue.kind` ranks §2.6's signals and is NOT what the
    refusal keys on -- a camera make is `image_exif` even though §2.6 calls it
    tier-1 evidence, and an unranked tag with `kind=None` is one too."""
    file_id, by_value = _scanned_photo(exif_conn)
    decision = _ask(exif_conn, file_id, by_value[value])
    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"


@pytest.mark.parametrize("value", ["HEIC", "4032x3024", "sRGB", "iOS 19.1"])
def test_the_releasable_image_metadata_still_releases(exif_conn, value):
    """The control, and the reason the refusal keys on the reader's own EXIF list
    rather than on the zone.

    §2.6 wants the format, the pixel dimensions, the colour space and a screenshot's
    software metadata to stay usable evidence; none is `image_exif` and refusing them
    would trade the finding for a different kind of wrong. Without this test the
    fix is also satisfied by marking every image observation sensitive.
    """
    file_id, by_value = _scanned_photo(exif_conn)
    decision = _ask(exif_conn, file_id, by_value[value])
    assert isinstance(decision, Released), (
        f"{value!r} is not EXIF and §2.6 reads it as evidence")
    assert decision.materialised_items[0].value == value
