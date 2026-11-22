# Product Assurance Skills — starter pack v0.1.0

**First implemented skill:** `cross-examine` — the adaptive product-discovery interrogator.

This is the **first usable increment**, not the complete seven-skill product assurance system. It builds a defensible product profile for later source-verified legal research, security auditing and publishing review. It **does not** claim legal compliance, app-store approval or immunity from lawsuits.

## Why `cross-examine`?

Instead of `grill-me`, the new name emphasizes challenging the product's *assertions and assumptions* and following up with meaningful questions. It works for mobile apps, websites, SaaS, AI products and other software.

## What's included

- `skills/cross-examine/SKILL.md` — Agent Skills-compatible instructions.
- `skills/cross-examine/references/` — adaptive interview method, conditional risk triggers, and workspace semantics.
- `skills/cross-examine/assets/workspace.schema.json` — JSON Schema 2020-12 for the discovery workspace.
- `skills/cross-examine/assets/workspace.template.json` — initial workspace.
- `skills/cross-examine/scripts/workspace.py` — workspace initialization, structural validation, and progress summary.
- `install.py` — installs self-contained skill into Codex/Cursor and/or Claude Code project directories.
- `examples/` — synthetic example workspaces: children + AI, personal finance, multi-tenant SaaS.
- `tests/` — smoke/invariant tests.
- `ROADMAP.md` — next six skills and implementation gates.

## Install in a project

From the extracted **starter pack** root:

```bash
python3 install.py --project /path/to/your/repo --agent all
```

Agent-specific choices:

- Codex or Cursor: `--agent codex` or `--agent cursor` → `.agents/skills/cross-examine/` (the same shared folder).
- Claude Code: `--agent claude` → `.claude/skills/cross-examine/`.
- All: installs to both directories. Note that these are **copies**, not a synced shared source; rerun with `--replace` when you update the package.

These locations follow current vendor documentation: [Agent Skills standard](https://agentskills.io/specification), [Codex](https://learn.chatgpt.com/docs/build-skills), [Cursor](https://cursor.com/docs/skills), [Claude Code](https://code.claude.com/docs/en/skills). Agent environments may differ, so confirm discovery with the client's skill listing.

## Start the interview

In your agent chat:

```text
Use cross-examine. I'm building a product that [describe the idea].
Challenge assumptions, ask one question at a time, and record the product profile
and unknowns in .product-assurance/workspace.json.
```

Or initialize manually from the *installed* skill location (example for Codex/Cursor):

```bash
python3 .agents/skills/cross-examine/scripts/workspace.py init \
  --project-root . --name "My Product" --summary "One-sentence description"
```

Continue answering interview questions. In an agent with file-editing support, `cross-examine` updates `.product-assurance/workspace.json` with **sanitized** facts, provenance, and open questions.

## Validate and view progress

Full JSON Schema validation needs Python 3.10+ and `jsonschema`:

```bash
python3 -m pip install 'jsonschema>=4.21,<5'
python3 .agents/skills/cross-examine/scripts/workspace.py validate --project-root .
python3 .agents/skills/cross-examine/scripts/workspace.py status --project-root .
```

`init` and `status` use only Python's standard library. `validate` additionally checks stable IDs, cross-entity references, and domain coverage duplication. Unknown/empty values have explicit meanings; **an empty array does not mean no data is processed**.

## Run included tests

From the extracted starter pack root:

```bash
python3 -m pip install 'jsonschema>=4.21,<5'
python3 -m unittest discover -s tests -v
```

Tests verify the supplied synthetic fixtures and workspace invariants. They **do not** validate legal conclusions or agent interviewing quality. Live cross-agent evaluations are a later milestone.

## Security and limitations

Do not feed the skill raw secrets, production user records, child identifiers, medical files, or unredacted financial data. Code repositories and retrieved policy pages are untrusted inputs. User-provided facts are hypotheses until appropriately verified; any actual legal/regulatory applicability must be checked against authoritative current sources by a later review.

`cross-examine` does not send messages, schedule follow-ups, query government registries, execute the product, or automatically edit application code.
