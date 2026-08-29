# src/recognition/__init__.py
"""The compiled recognition rule set, and the detector it produces.

P7's SPEC *Deferred* names exactly this part and leaves it empty: *"The design
states **what** is protected and never **how it is recognised**. The detector rule
set, its signals, and its thresholds are hand-authored. P7 publishes the vocabulary
the detectors write into."* `src/privacy/` therefore holds no regex, no gazetteer
and no keyword list, and `src/production.py` raises `MissingClassificationAuthority`
because nothing supplied one. This package is the supplier.

Three modules, in the order the data moves:

* `compile` -- BUILD TIME. The one module in `src/` allowed to read a
  `planning/domains/nodes/*.json` row. It emits a versioned manifest.
* `rules` -- RUNTIME. Parses one manifest through an INJECTED reader. It touches no
  filesystem and imports no planning code, exactly as `tree_design.catalogue` does:
  *"A later deterministic compiler consumes ratified records and emits a versioned
  manifest; this module reads that manifest and nothing else."*
* `detector` -- RUNTIME. Applies the compiled rules to one file version's own P4
  observations and returns a `ClassificationRecord` or, far more often, `None`.

**Abstention is a result.** `00` requires abstention where two readings are both
supported, and a confident wrong classification files a file where nobody will look
for it. `Detector.explain` returns an `Abstention` carrying the reason, and
`Detector.__call__` -- the `ClassificationProducer` the orchestrator binds -- turns
it into `None`. Every abstaining path is tested directly.
"""
