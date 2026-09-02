"""The gesture that moves a person's real files.

P12 built seventeen modules and `src/cli.py` imported one name from them, so
every run ended *"Nothing was moved."* This package is the wiring: it turns the
proposal a run prints into frozen move plans, applies the ones the person names,
and takes them back. It holds no policy -- every number, every sentence about an
unruled question and every filesystem constant is a parameter, and `src/cli.py`
is where they are chosen.
"""
