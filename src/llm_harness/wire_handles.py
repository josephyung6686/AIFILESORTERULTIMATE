# src/llm_harness/wire_handles.py
"""What an identifier may look like once it has left the device.

Two un-keyed digests used to go on the wire and both were reversed. `subject_ref`
carried `sha256(field_key \x1f value)` with `field_key` printed in the clear
beside it, and the seed value came back in a few thousand hashes from the wire
bytes alone. `observation_key` carried
`sha256(content_hash ‖ extractor ‖ locator ‖ raw_value)` with the locator printed
in the clear as `address`, and a value the dossier had printed as `"[redacted]"`
came back in about a second from the wire plus a copy of the file. Both are
dictionary attacks, and both work because a digest anyone can recompute is a
digest anyone can guess against.

**The identity does not move.** `evidence_shape.observation.observation_key` is
M14's version-independent citation handle: the same observation keys the same way
across runs and across extractor versions, and `resolve`, the audit record, the
`llm_dossier` row and §8.5's replay all address it. Nothing here changes it. What
changes is only what may be **spoken aloud**: the model is shown a keyed digest of
the identifier instead of the identifier, and the key never leaves the device, so
the recipient cannot compute a single candidate -- not slowly, not at all.

A handle is `HMAC-SHA256(key, identifier)`, which buys three properties at once:

* **Uninvertible without the key.** The only attack left is guessing the key.
* **Deterministic given the key.** Two calls over identical content produce
  identical bytes, so `llm_harness.store.record_dossier` still recognises the
  second as the first -- `dossier_id` is the address of these bytes, and that
  address IS the replay identity.
* **Injective in practice.** Two subjects never collapse onto one address. A
  per-call opaque handle (`e0`, `e1`) would be more private still, and it fails
  here: two different subjects with the same shape would produce the same bytes,
  the same `dossier_id`, and `record_dossier` refuses a second payload under an
  address it already holds.

**What this does not fix.** The handle is stable for as long as the key is, so a
provider still sees that two calls named the same observation. Closing that needs
a key that changes every run, and a key that changes every run throws away the
cross-run dossier identity above. The key's lifetime is a deployment fact and is
chosen at the composition root, which is where that trade can be made.

The key is a credential: it is never returned, never formatted into a message,
never logged, and the refusal below names the missing thing and not its value.
"""
from __future__ import annotations

import hmac
from collections.abc import Iterable, Mapping
from hashlib import sha256

from evidence_shape.observation import is_observation_key

#: The one name for the injected key. `dossier.build_dossier` and
#: `validation.validate_response` both report it absent, and a second spelling of
#: it is a refusal a composition root cannot answer.
WIRE_HANDLE_KEY: str = "wire_handle_key"

#: The algorithm prefix a handle carries, deliberately not `sha256`: a reader and
#: `is_observation_key` must both be able to tell a handle from a P4 key.
HANDLE_PREFIX: str = "handle"


class WireHandleKeyRequired(RuntimeError):
    """No key was injected, and there is no unkeyed fallback.

    Falling back to a bare digest is the defect this module exists to remove, and
    it would restore it silently: the bytes would still be well-formed.
    """


def _checked(key: object) -> bytes:
    if not isinstance(key, (bytes, bytearray)) or not key:
        raise WireHandleKeyRequired(
            "a wire handle key is required; this package ships no default and "
            "will not fall back to an unkeyed digest a recipient can reverse")
    return bytes(key)


def wire_handle(value: str, *, key: bytes) -> str:
    """One identifier as the model may see it, and never as it is stored."""
    return f"{HANDLE_PREFIX}:" + hmac.new(
        _checked(key), value.encode("utf-8"), sha256).hexdigest()


def wire_ref(ref: str, *, key: bytes) -> str:
    """One evidence reference, keyed if it is a digest of the person's content.

    A P4 `observation_key` is a digest of the file's bytes, of the locator and of
    the raw value, so it goes out keyed. A `file_id` is `uuid.uuid4()`
    (`database_agent.files_table`): derived from nothing, inverting to nothing,
    and the reference the model's own `members` list is read against. Keying it
    would buy no privacy and cost that reading.
    """
    return wire_handle(ref, key=key) if is_observation_key(ref) else ref


def issued_handles(refs: Iterable[str], *, key: bytes) -> dict[str, str]:
    """What the model was shown -> what it names here. One dossier's whole map."""
    return {wire_ref(ref, key=key): ref for ref in refs}


def local_ref(cited: str, *, handles: Mapping[str, str]) -> str:
    """The local identifier a model's reference names.

    A reference this dossier never issued comes back unchanged, so citation
    checking reports it absent from the dossier rather than resolving it. That is
    the same answer the model would have got for a reference it invented.
    """
    return handles.get(cited, cited)
