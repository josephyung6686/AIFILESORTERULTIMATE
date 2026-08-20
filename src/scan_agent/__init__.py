# src/scan_agent/__init__.py
"""P3 — scan and corpus selection. The only part that walks the filesystem."""
from scan_agent.scan import scan

__all__ = ["scan"]
