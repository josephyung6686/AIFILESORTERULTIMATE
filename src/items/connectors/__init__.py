"""External connectors — live Gmail/Calendar are scratched for this product cut.

Fixture sync via `filesorter sync --fixture` remains. Live OAuth is not shipped.
"""

CONNECTORS_DISABLED_REASON = (
    "live Gmail/Calendar scratched — no OAuth; use --fixture for local imports"
)
