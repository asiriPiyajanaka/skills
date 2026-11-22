# Contributing

Keep each skill independently installable and focused on a concrete task. Add new skills under `skills/<skill-name>/` and list implemented skills in the root README. Keep proposed skills in roadmap documentation until they work.

## Local setup

Clone the public repository and enter its root:

```bash
git clone https://github.com/asiriPiyajanaka/skills.git
cd skills
```

Use Python 3.10 or later for the existing workspace tooling. If `python3` points to an older interpreter, substitute a supported executable such as `python3.12` in the first command:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
```

The command discovers skills and checks their frontmatter, directory names, bundled licenses, local documentation/resource links, JSON schemas and Python 3.10 syntax. It then discovers and runs every directory containing `test_*.py` under `tests/`, including the workspace fixtures and recording invariants. Use `--static-only` to skip test execution.

These checks do not evaluate legal conclusions or the quality of an agent's interview. The [agent evaluation cases](evals/cross-examine/agent-evaluation.md) describe that separate, pending work.

## Installation checks and CI

With Node.js 22.20+ available, run:

```bash
.venv/bin/python scripts/check_install.py
```

This uses the pinned `skills@1.9.0` installer to list and copy the collection into a temporary project for Codex, Cursor and Claude Code. It compares installed runtime files with the checkout, exercises `cross-examine` from detached copies, and checks the retained Python installer. Temporary projects and installer state are removed afterward. This checks packaging and helper execution, not agent reasoning behavior.

To reuse an already available installer without downloading it:

```bash
.venv/bin/python scripts/check_install.py --cli /path/to/skills/bin/cli.mjs
```

The [validation workflow](.github/workflows/validate.yml) runs on pushes, pull requests and manual dispatch. Its matrix covers the minimum supported Python 3.10 and Python 3.14, with Node.js 24. It installs dependencies from `requirements-dev.txt`, then runs both commands above. Tests for uncommitted changes use the checkout; nothing is published by the workflow.

After a push to the default branch, a separate job fetches the exact public GitHub commit with persisted Git credentials disabled and GitHub token variables removed. You can repeat that check once your commit is publicly reachable:

```bash
.venv/bin/python scripts/check_install.py --source asiriPiyajanaka/skills@FULL_COMMIT_SHA
```

The public installation must match the checkout. It cannot validate unpushed changes. When updating the pinned installer version, rerun installation checks and confirm the agent paths still match the documented behavior. Official references: [skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md), [setup-python](https://github.com/actions/setup-python), [setup-node](https://github.com/actions/setup-node).

## Adding or updating a skill

- Use a lowercase, hyphenated directory name that matches the `name` in `SKILL.md` frontmatter. Include a concise `description` explaining what the skill does and when to use it.
- Keep scripts, references, templates and other runtime files inside the skill directory. An installed skill must not depend on an uninstalled sibling or on repository-only files.
- Declare runtime Python dependencies in the skill's own `requirements.txt`, and include that file from the repository's development requirements when its tests need them.
- Add supporting directories only when needed. Keep detailed conditional guidance in linked references rather than duplicating it in the entrypoint.
- Put collection and workflow documentation under `docs/`, synthetic examples under `examples/<skill-name>/`, tests under `tests/<skill-name>/`, and behavioral evaluation cases under `evals/<skill-name>/`.
- Preserve copyright notices and include the applicable license with files copied into an installed skill.
- For changes to the discovery schema, preserve its versioning contract and document migrations for breaking changes in the [product-assurance roadmap](docs/product-assurance/ROADMAP.md).

Run `scripts/validate.py` for changes to the collection. To run only the workspace tests:

```bash
.venv/bin/python -m unittest discover -s tests/cross-examine -v
```

When installation paths or runtime resources change, also run `scripts/check_install.py`. Add a runtime exercise there when a new skill includes executable helpers. See the [product-assurance guide](docs/product-assurance/README.md) for the local Python installer and workspace commands.

## Pull requests

Describe the problem, the resulting behavior, and the checks you ran. Use synthetic or sanitized examples; do not include credentials, production records, or private evidence in this public repository. Document any evaluation that remains pending rather than claiming support that has not been tested.
