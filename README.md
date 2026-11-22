# Skills

My public collection of reusable skills for coding agents. Each skill lives in its own directory under `skills/` and can be installed independently.

## Available skills

| Skill | What it does | Status |
| --- | --- | --- |
| [cross-examine](skills/cross-examine/SKILL.md) | Uses adaptive questions to record product facts, assumptions, data flows, risks and unknowns. | Workspace v2 tooling and installation checks; live agent evaluations pending. |

`cross-examine` is the first skill in the [product-assurance workflow](docs/product-assurance/README.md). Related skills are described in its [roadmap](docs/product-assurance/ROADMAP.md); they are not yet implemented or installable.

## Install

Run these commands from the project where you want to use the skills. The [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) fetches this public GitHub repository; no npm package from this repository is required.

```bash
# Browse available skills without installing
npx skills add asiriPiyajanaka/skills --list

# Choose skills and agents interactively
npx skills add asiriPiyajanaka/skills

# Install cross-examine
npx skills add asiriPiyajanaka/skills --skill cross-examine
```

Installation is project-local by default. Add `--global` to install for your user account, or select an agent explicitly:

```bash
npx skills add asiriPiyajanaka/skills --skill cross-examine --agent codex
```

The current installer requires Node.js 22.20 or later. Each skill may also have its own runtime requirements: `cross-examine` uses Python 3.10+ and bundles a [requirements file](skills/cross-examine/requirements.txt) for workspace validation. See the [product-assurance guide](docs/product-assurance/README.md) for setup and the retained Python installer for local copies.

## Try cross-examine

After installation, ask your agent:

```text
Use cross-examine. I'm building a product that [describe the idea].
Challenge assumptions, ask one question at a time, and record the product profile
and unknowns in .product-assurance/workspace.json.
```

The skill captures discovery facts and risk hypotheses. It does not certify legal compliance or release readiness. Agent behavior evaluations have not yet been run; see the [evaluation scenarios](evals/cross-examine/agent-evaluation.md).

## Repository layout

```text
skills/
└── cross-examine/          # Installable skill and runtime resources
docs/
└── product-assurance/      # Workflow overview and roadmap
examples/
└── cross-examine/          # Synthetic workspace fixtures
tests/
└── cross-examine/          # Workspace tests
evals/
└── cross-examine/          # Agent behavior evaluation scenarios
scripts/
├── validate.py             # Static checks and discovered test suites
├── check_install.py        # Temporary-project installation checks
└── install_cross_examine.py
```

Skills use the [Agent Skills format](https://agentskills.io/specification): a `SKILL.md` entrypoint with optional scripts, references and assets. Runtime resources stay inside the skill directory so installations are self-contained apart from documented system dependencies.

## Contribute

Use Python 3.10+ to set up validation and run the collection's checks:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_install.py
```

The [GitHub Actions workflow](.github/workflows/validate.yml) runs validation, tests and checkout installation on Python 3.10 and 3.14. A push to the default branch also checks installation of that public commit without GitHub credentials. See [CONTRIBUTING.md](CONTRIBUTING.md) for details and how to add a skill.

Existing schema v1 product workspaces need an [explicit migration candidate](skills/cross-examine/references/workspace-contract.md#migrating-v1-workspaces). The migration command preserves the source and reports records requiring review under the stricter contract.

## License

[MIT](LICENSE). The original Product Assurance Skills copyright notice is preserved. The installable `cross-examine` directory also includes a copy of the license.
