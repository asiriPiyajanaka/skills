#!/usr/bin/env python3
"""Validate this skills collection and run its discovered unittest suites."""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_DIRS = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.product-assurance'}
NAME_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
ALLOWED_FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}


def repository_files(root: Path):
    for folder, directories, files in os.walk(root):
        directories[:] = sorted(d for d in directories if d not in SKIP_DIRS)
        for name in sorted(files):
            yield Path(folder) / name


def load_frontmatter(path: Path) -> dict:
    import yaml

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if not isinstance(key, str) or key in result:
                raise ValueError('frontmatter keys must be unique strings')
            result[key] = loader.construct_object(value_node)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    content = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', content, re.DOTALL)
    if not match:
        raise ValueError('missing YAML frontmatter')
    result = yaml.load(match.group(1), Loader=UniqueLoader)
    if not isinstance(result, dict):
        raise ValueError('frontmatter must be a mapping')
    return result


def markdown_prose(text: str) -> str:
    """Ignore fenced examples while checking actual documentation links."""
    output = []
    marker = None
    length = 0
    for line in text.splitlines():
        fence = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker is None:
                marker, length = fence[1][0], len(fence[1])
            elif fence[1][0] == marker and len(fence[1]) >= length and not fence[2].strip():
                marker = None
            continue
        if marker is None:
            output.append(line)
    return '\n'.join(output)


def validate_repository(root: Path) -> list[str]:
    import jsonschema
    import yaml

    errors = []
    skills_root = root / 'skills'
    skills = sorted(skills_root.rglob('SKILL.md')) if skills_root.exists() else []
    if not skills:
        errors.append('skills/: no SKILL.md files found')
    for directory in sorted(skills_root.iterdir()) if skills_root.exists() else []:
        if directory.is_dir() and not directory.name.startswith('.') and not (directory / 'SKILL.md').is_file():
            errors.append(f'{directory.relative_to(root)}: missing SKILL.md')

    for entrypoint in skills:
        label = str(entrypoint.relative_to(root))
        if entrypoint.parent.parent != skills_root:
            errors.append(f'{label}: skills must be direct children of skills/')
        try:
            metadata = load_frontmatter(entrypoint)
            unexpected = metadata.keys() - ALLOWED_FIELDS
            if unexpected:
                errors.append(f'{label}: unsupported frontmatter fields: {sorted(unexpected)}')
            name = metadata.get('name')
            if not isinstance(name, str) or len(name) > 64 or not NAME_PATTERN.fullmatch(name):
                errors.append(f'{label}: invalid skill name')
            elif name != entrypoint.parent.name:
                errors.append(f'{label}: name must match its directory')
            description = metadata.get('description')
            if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                errors.append(f'{label}: description must contain 1–1024 characters')
            for field in ('license', 'allowed-tools', 'compatibility'):
                if field in metadata and (not isinstance(metadata[field], str) or not metadata[field].strip()):
                    errors.append(f'{label}: {field} must be a nonempty string')
            if isinstance(metadata.get('compatibility'), str) and len(metadata['compatibility']) > 500:
                errors.append(f'{label}: compatibility exceeds 500 characters')
            if 'metadata' in metadata and (
                not isinstance(metadata['metadata'], dict)
                or any(not isinstance(v, str) for v in metadata['metadata'].values())
            ):
                errors.append(f'{label}: metadata values must be strings')
            if not (entrypoint.parent / 'LICENSE').is_file():
                errors.append(f'{label}: missing bundled LICENSE')
            for resource in re.findall(r'`((?:references|assets|scripts)/[^`\s]+|requirements\.txt)`', entrypoint.read_text(encoding='utf-8')):
                destination = (entrypoint.parent / resource).resolve()
                if not destination.is_relative_to(entrypoint.parent.resolve()):
                    errors.append(f'{label}: runtime resource escapes its skill: {resource}')
                elif not destination.is_file():
                    errors.append(f'{label}: missing runtime resource {resource}')
        except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f'{label}: {exc}')

    for path in repository_files(root):
        label = str(path.relative_to(root))
        try:
            if path.suffix == '.json':
                document = json.loads(path.read_text(encoding='utf-8'))
                if path.name.endswith('.schema.json'):
                    jsonschema.Draft202012Validator.check_schema(document)
                    def check_refs(node):
                        if isinstance(node, dict):
                            reference = node.get('$ref', '')
                            if isinstance(reference, str) and reference.startswith('#/'):
                                target = document
                                try:
                                    for part in unquote(reference[2:]).split('/'):
                                        part = part.replace('~1', '/').replace('~0', '~')
                                        target = target[int(part)] if isinstance(target, list) else target[part]
                                except (KeyError, IndexError, TypeError, ValueError):
                                    errors.append(f'{label}: unresolved schema reference {reference}')
                            for value in node.values():
                                check_refs(value)
                        elif isinstance(node, list):
                            for value in node:
                                check_refs(value)
                    check_refs(document)
            elif path.suffix == '.py':
                ast.parse(path.read_text(encoding='utf-8'), filename=label, feature_version=(3, 10))
            elif path.suffix == '.md':
                for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', markdown_prose(path.read_text(encoding='utf-8'))):
                    target = target.strip('<>')
                    url = urlsplit(target)
                    if url.scheme or url.netloc or not url.path:
                        continue
                    destination = (path.parent / unquote(url.path)).resolve()
                    boundary = next((entry.parent for entry in skills if path.is_relative_to(entry.parent)), root)
                    if not destination.is_relative_to(boundary):
                        errors.append(f'{label}: link escapes {boundary.relative_to(root) or "."}: {target}')
                    elif not destination.exists():
                        errors.append(f'{label}: broken local link: {target}')
        except (ValueError, OSError, UnicodeError, SyntaxError, jsonschema.SchemaError) as exc:
            errors.append(f'{label}: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--static-only', action='store_true', help='Skip unittest suites')
    args = parser.parse_args()
    root = args.root.resolve()
    if sys.version_info < (3, 10):
        print('Validation requires Python 3.10 or later.', file=sys.stderr)
        return 2
    try:
        errors = validate_repository(root)
    except ImportError:
        print('Install validation dependencies: python -m pip install -r requirements-dev.txt', file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f'ERROR {error}', file=sys.stderr)
        return 1
    print('Repository structure, skill metadata, local links, JSON schemas and Python syntax are valid.', flush=True)
    if not args.static_only:
        suites = sorted({p.parent for p in (root / 'tests').rglob('test_*.py')})
        if not suites:
            print('No test suites found.', file=sys.stderr)
            return 1
        for directory in suites:
            print(f'Running {directory.relative_to(root)}', flush=True)
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(directory), '-v'],
                cwd=root, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
            )
            if result.returncode:
                return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
