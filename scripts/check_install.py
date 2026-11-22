#!/usr/bin/env python3
"""Test skill discovery, copies and detached runtime tools in temporary projects."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_VERSION = '1.9.0'
AGENT_FOLDERS = { 'codex-cursor': '.agents/skills', 'claude-code': '.claude/skills' }
SKIP_NAMES = {'__pycache__', '.DS_Store', 'metadata.json'}


def run(command: list[str], cwd: Path, env: dict[str, str], expected: int = 0) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    if result.returncode != expected:
        raise ValueError(f'Command failed ({result.returncode}): {command[0]}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def package_files(skill: Path):
    return {
        path.relative_to(skill): path
        for path in skill.rglob('*')
        if path.is_file() and not any(part in SKIP_NAMES for part in path.relative_to(skill).parts)
        and path.suffix != '.pyc'
    }


def check_runtime(skill: Path, project: Path, env: dict[str, str]) -> None:
    if skill.name != 'cross-examine':
        return
    project.mkdir(parents=True)
    script = skill / 'scripts/workspace.py'
    prefix = [sys.executable, '-B', str(script)]
    run(prefix + ['init', '--project-root', str(project), '--name', 'Installation smoke test',
                  '--summary', 'Synthetic project for checking the installed workspace tooling.'], project, env)
    workspace = project / '.product-assurance/workspace.json'
    original = workspace.read_bytes()
    run(prefix + ['validate', '--project-root', str(project)], project, env)
    run(prefix + ['status', '--project-root', str(project)], project, env)
    run(prefix + ['init', '--project-root', str(project)], project, env, expected=2)
    if workspace.read_bytes() != original:
        raise ValueError('Read-only commands or repeated initialization changed the workspace')


def check_install(source: str, cli: list[str]) -> None:
    skills = sorted(path.parent for path in (ROOT / 'skills').glob('*/SKILL.md'))
    if not skills:
        raise ValueError('No source skills found')
    with tempfile.TemporaryDirectory(prefix='skills-install-') as temporary:
        base = Path(temporary)
        project = base / 'project'
        project.mkdir()
        env = {**os.environ, 'DISABLE_TELEMETRY': '1', 'DO_NOT_TRACK': '1', 'CI': '1',
               'PYTHONDONTWRITEBYTECODE': '1', 'GIT_TERMINAL_PROMPT': '0',
               'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
               'GH_CONFIG_DIR': str(base / 'gh'), 'XDG_STATE_HOME': str(base / 'state'),
               'XDG_CONFIG_HOME': str(base / 'config'), 'XDG_DATA_HOME': str(base / 'data')}
        for name in ('GH_TOKEN', 'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN'):
            env.pop(name, None)
        listing = run(cli + ['add', source, '--list'], project, env)
        for skill in skills:
            if skill.name not in listing:
                raise ValueError(f'Installer did not discover {skill.name}')
        run(cli + ['add', source, '--skill', '*', '--agent', 'codex', 'cursor', 'claude-code',
                   '--yes', '--copy'], project, env)
        for agent, folder in AGENT_FOLDERS.items():
            for original in skills:
                installed = project / folder / original.name
                for relative, source_file in package_files(original).items():
                    target = installed / relative
                    if not target.is_file() or not target.resolve().is_relative_to(project.resolve()):
                        raise ValueError(f'Missing or externally linked installed file: {agent}/{original.name}/{relative}')
                    if target.read_bytes() != source_file.read_bytes():
                        raise ValueError(f'Installed contents differ from this checkout: {agent}/{original.name}/{relative}')
                detached = base / 'detached' / agent / original.name
                shutil.copytree(installed, detached)
                check_runtime(detached, base / 'products' / agent / original.name, env)
                print(f'PASS {agent}/{original.name}: copied resources and detached runtime', flush=True)
        # The retained Python installer must also work independently of its cwd.
        legacy = base / 'python-installer'
        legacy.mkdir()
        run([sys.executable, str(ROOT / 'scripts/install_cross_examine.py'), '--project', str(legacy), '--agent', 'all'], legacy, env)
        for folder in AGENT_FOLDERS.values():
            for relative, source_file in package_files(ROOT / 'skills/cross-examine').items():
                if (legacy / folder / 'cross-examine' / relative).read_bytes() != source_file.read_bytes():
                    raise ValueError(f'Python installer changed or omitted {relative}')
        print('PASS retained Python installer', flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=str(ROOT), help='Local checkout or public owner/repo@commit')
    parser.add_argument('--cli', type=Path, help='Existing skills CLI JavaScript file, for offline local verification')
    args = parser.parse_args()
    source = str(Path(args.source).resolve()) if Path(args.source).exists() else args.source
    cli = ['node', str(args.cli.resolve())] if args.cli else ['npx', '--yes', f'skills@{CLI_VERSION}']
    try:
        check_install(source, cli)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('Installation checks passed. Agent reasoning quality is a separate evaluation.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
