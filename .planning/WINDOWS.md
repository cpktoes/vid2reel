---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-10-18T05:38:27.870Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 03 | stub | v2r/look/measure.py |  | shot_changes and sound are placeholders (null and []) until plan 03-04 measures them | open |  | 2026-10-18T05:38:27.870Z |  |

````json
[
  {
    "id": 1,
    "kind": "stub",
    "phase": "03",
    "file": "v2r/look/measure.py",
    "line": null,
    "description": "shot_changes and sound are placeholders (null and []) until plan 03-04 measures them",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-10-18T05:38:27.870Z",
    "resolved_at": null
  }
]
````
