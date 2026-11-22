# Workspace runtime

Use Python 3.10 or later. `init` and `status` need only the standard library. `validate` and `migrate` also need the dependencies in the installed skill's [requirements.txt](../requirements.txt).

The bundled RFC 3339 checker makes timestamp validation explicit; installing `jsonschema` alone can leave date-time checks unavailable.

Prefer an existing project Python environment that already has those dependencies. Otherwise, within the user's existing authorization, create a local environment. Run from the product repository and substitute the actual installed skill path:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r .agents/skills/cross-examine/requirements.txt
.venv/bin/python .agents/skills/cross-examine/scripts/workspace.py validate --project-root .
.venv/bin/python .agents/skills/cross-examine/scripts/workspace.py status --project-root .
```

If `python3` is older than 3.10, select a supported executable such as `python3.12` when creating the environment. Do not change the system Python or install globally as part of this workflow. Ask only when an installation actually requires additional authorization. If setup is unavailable, continue discovery, preserve the workspace if possible, and state that schema validation is pending.

`status` does not perform schema validation. It labels the interview status as recorded, reports priority unknowns, and never establishes completeness or readiness. Run `validate` to check the contract and cross-entity references. Validation checks evidence references and review notes for presence, not the truth or contents of the referenced evidence.

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | Command succeeded. For migration, the separate candidate is valid. |
| 1 | Workspace validation failed. Migration may have written a candidate requiring repair. |
| 2 | Invalid input, unreadable file, unsupported Python or refused overwrite. |
| 3 | Required Python validation dependency is unavailable; no validation was completed. |

For old workspaces, follow [the migration procedure](workspace-contract.md#migrating-v1-workspaces). Never overwrite an existing workspace merely to get a valid initial template.
