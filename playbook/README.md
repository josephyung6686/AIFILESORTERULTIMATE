# Playbook rollups (L2 / L3)

Human-readable Markdown generated from memory rules + atoms.

```bash
PYTHONPATH=src python3 -c "
from pathlib import Path
from database_agent.db import open_database
from assistant.playbook_rollups import write_rollups
conn = open_database(Path('/tmp/ga-500.sqlite'), scan_roots=[])
print(write_rollups(conn))
"
```

- `clusters/` — L2 by kind  
- `profiles/` — L3 summary  

Never auto-files. Atoms stay dark for steering until the precision gate passes.
