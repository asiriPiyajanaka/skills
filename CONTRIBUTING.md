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
.venv/bin/python -m unittest discover -s tests/cross-examine -v
```

These tests check the discovery schema, fixtures and workspace invariants. They do not evaluate legal conclusions or the quality of an agent's interview. The [agent evaluation cases](evals/cross-examine/agent-evaluation.md) describe that separate, pending work. Repository-wide validation and GitHub Actions are not configured yet.

## Adding or updating a skill

- Use a lowercase, hyphenated directory name that matches the `name` in `SKILL.md` frontmatter. Include a concise `description` explaining what the skill does and when to use it.
- Keep scripts, references, templates and other runtime files inside the skill directory. An installed skill must not depend on an uninstalled sibling or on repository-only files.
- Add supporting directories only when needed. Keep detailed conditional guidance in linked references rather than duplicating it in the entrypoint.
- Put collection and workflow documentation under `docs/`, synthetic examples under `examples/<skill-name>/`, tests under `tests/<skill-name>/`, and behavioral evaluation cases under `evals/<skill-name>/`.
- Preserve copyright notices and include the applicable license with files copied into an installed skill.
- For changes to the discovery schema, preserve its versioning contract and document migrations for breaking changes in the [product-assurance roadmap](docs/product-assurance/ROADMAP.md).

Run checks relevant to the change. For `cross-examine`, use the test command above. When installation paths or runtime resources change, check discovery from the repository root:

```bash
npx skills add . --list
```

Then install into a disposable project and exercise the installed tools. See the [product-assurance guide](docs/product-assurance/README.md) for the local Python installer and workspace commands.

## Pull requests

Describe the problem, the resulting behavior, and the checks you ran. Use synthetic or sanitized examples; do not include credentials, production records, or private evidence in this public repository. Document any evaluation that remains pending rather than claiming support that has not been tested.
