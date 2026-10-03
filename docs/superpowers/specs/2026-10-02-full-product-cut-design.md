# Full Product Cut (no UI / no sorter polish / no live mail·cal)

**Date:** 2026-10-02  
**Status:** Approved for implementation  
**Out:** Mac UI · sorter polish · live Gmail/Calendar · Apple FM on macOS 15 (probe only)

## Intention

Laptop-resident BYOK assistant: find → understand → relate → nudge (file/profile only) → organize with approval. Disk is system of record; DB is working memory that must stay true after moves and Finder edits.

## Locked decisions

1. **Truth loop:** apply/undo update `items.open_target`, label, bookmarks, FTS with the disk move.  
2. **Freshness:** auto-refresh roots at start of `ask`/`search`; optional `watch` daemon.  
3. **Held bodies:** cloud path = metadata only; local gen (`ASSISTANT_LOCAL_BASE_URL` / `--local-only` with local URL) may read held bodies.  
4. **Grounded plans:** every plan `item_id` must be session-surfaced (find) or user-picked.  
5. **Nudge without mail:** `list_gaps` + richer `list_deadlines` from files/profiles.  
6. **Connectors:** `sync_mail` / `sync_calendar` explicitly disabled (not “use fixture”).  
7. **Correction:** reject_link captures L0 DiffEvent.

## Success

Gates green; apply then find by new path/label; ask after Finder rename stays correct when watcher/refresh runs; held cloud read still refuses body.
