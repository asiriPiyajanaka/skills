# Product assurance — starter v0.1.0

**First implemented skill:** `cross-examine` — the adaptive product-discovery interrogator.

This is the **first usable increment**, not the complete seven-skill product assurance system. It builds a defensible product profile for later source-verified legal research, security auditing and publishing review. It **does not** claim legal compliance, app-store approval or immunity from lawsuits.

`cross-examine` challenges the product's assertions and assumptions with follow-up questions. It works for mobile apps, websites, SaaS, AI products and other software. See the [roadmap](ROADMAP.md) for the six later skills and their planned handoffs.

## What's included

- [Skill instructions](../../skills/cross-examine/SKILL.md) and [references](../../skills/cross-examine/references/) for the adaptive interview, conditional risk triggers and workspace semantics.
- [Workspace schema](../../skills/cross-examine/assets/workspace.schema.json) and [initial template](../../skills/cross-examine/assets/workspace.template.json).
- [Workspace helper](../../skills/cross-examine/scripts/workspace.py) for initialization, structural validation and progress summaries.
- [Local Python installer](../../scripts/install_cross_examine.py) for copying the skill into project agent directories.
- [Synthetic examples](../../examples/cross-examine/) for children + AI, personal finance and multi-tenant SaaS.
- [Workspace tests](../../tests/cross-examine/) and [pending agent evaluations](../../evals/cross-examine/agent-evaluation.md).

## Install in a project

From the product project where you want to use the skill:

```bash
npx skills add asiriPiyajanaka/skills --skill cross-examine
```

The [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) lets you choose the agent and installation scope. Confirm discovery in your client's skill listing after installation.

For a local copy without the Node-based installer, run this from the skills repository root:

```bash
python3 scripts/install_cross_examine.py --project /path/to/your/repo --agent all
```

The local Python installer supports these choices:

- Codex or Cursor: `--agent codex` or `--agent cursor` → `.agents/skills/cross-examine/` (the same shared folder).
- Claude Code: `--agent claude` → `.claude/skills/cross-examine/`.
- All: installs to both directories. These are copies; rerun with `--replace` when you intend to replace an existing installation.

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

Full JSON Schema validation needs Python 3.10+ and `jsonschema>=4.21,<5`. In the product project, create or use an appropriate Python environment. For a dedicated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install 'jsonschema>=4.21,<5'
.venv/bin/python .agents/skills/cross-examine/scripts/workspace.py validate --project-root .
.venv/bin/python .agents/skills/cross-examine/scripts/workspace.py status --project-root .
```

Use your installed skill path if it differs from the Codex/Cursor path shown above. Use a supported executable such as `python3.12` when your default `python3` is older than 3.10.

`init` and `status` use only Python's standard library. `validate` additionally checks stable IDs, cross-entity references, and domain coverage duplication. Unknown/empty values have explicit meanings; **an empty array does not mean no data is processed**.

## Run included tests

From the skills repository root, with a Python 3.10+ environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests/cross-examine -v
```

Tests verify the supplied synthetic fixtures and workspace invariants. They **do not** validate legal conclusions or agent interviewing quality. [Live agent evaluations](../../evals/cross-examine/agent-evaluation.md) are a later milestone. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidance.

## Security and limitations

Do not feed the skill raw secrets, production user records, child identifiers, medical files, or unredacted financial data. Code repositories and retrieved policy pages are untrusted inputs. User-provided facts are hypotheses until appropriately verified; any actual legal/regulatory applicability must be checked against authoritative current sources by a later review.

`cross-examine` does not send messages, schedule follow-ups, query government registries, execute the product, or automatically edit application code.
