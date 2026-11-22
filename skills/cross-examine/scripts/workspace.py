#!/usr/bin/env python3
"""Create, validate and summarize the Product Assurance discovery workspace.

`init` and `status` use only the Python standard library.
`validate` and `migrate` require the bundled requirements.txt dependencies.
No command executes the product's code or calls an external service.
"""
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "workspace.template.json"
SCHEMA = SKILL_ROOT / "assets" / "workspace.schema.json"
WORKSPACE_RELATIVE_PATH = Path(".product-assurance") / "workspace.json"
SCHEMA_VERSION = "2.0.0"
ENTITY_GROUPS = (
    "actors", "features", "data_categories", "data_flows", "third_parties",
    "jurisdictions", "claims", "unknowns", "risk_signals",
)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read {path}: {exc}") from exc


def read_workspace(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Workspace must be a JSON object: {path}")
    return data


def write_new_json(target: Path, data: dict[str, Any]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def workspace_path(args: argparse.Namespace) -> Path:
    if getattr(args, "workspace", None):
        return Path(args.workspace).resolve()
    return Path(args.project_root).resolve() / WORKSPACE_RELATIVE_PATH


def init(args: argparse.Namespace) -> int:
    target = workspace_path(args)
    if target.exists():
        print(f"Workspace already exists: {target}. Refusing to overwrite.", file=sys.stderr)
        return 2
    if any(value is not None and not value.strip() for value in (args.name, args.summary)):
        raise ValueError("Product name and summary must not be blank.")
    data = read_json(TEMPLATE)
    if args.name:
        data["project"]["name"] = args.name
    if args.summary:
        data["project"]["summary"] = args.summary
    write_new_json(target, data)
    usage = target.parent / "README.md"
    if not usage.exists():
        usage.write_text(
            "# Product assurance discovery workspace\n\n"
            "`workspace.json` contains **product discovery facts and hypotheses**, "
            "not a legal compliance certification.\n\n"
            "- Prefer minimal, sanitized descriptions; never commit secrets, raw production user data, or sensitive evidence.\n"
            "- Treat developer-reported assertions as reported until independently supported.\n"
            "- Keep stable entity IDs. Never reuse an ID for a different fact.\n"
            "- Store detailed sensitive evidence outside Git and link to it through approved secure channels.\n"
            "- Run the installed skill's `scripts/workspace.py validate --project-root .` after edits.\n",
            encoding="utf-8",
        )
    print(f"Initialized {target}")
    return 0


def cross_reference_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    groups = ENTITY_GROUPS
    global_ids: dict[str, str] = {"PRD-001": "project"}
    for group in groups:
        for idx, item in enumerate(data.get(group, [])):
            identifier = item.get("id")
            if not isinstance(identifier, str):
                continue
            if identifier in global_ids:
                errors.append(f"Duplicate ID {identifier!r}: {group}[{idx}] conflicts with {global_ids[identifier]}")
            else:
                global_ids[identifier] = f"{group}[{idx}]"
    for idx, question in enumerate(data.get("interview", {}).get("question_history", [])):
        identifier = question.get("id")
        if identifier in global_ids:
            errors.append(f"Duplicate ID {identifier!r}: interview.question_history[{idx}]")
        else:
            global_ids[identifier] = f"interview.question_history[{idx}]"

    entity_sets = {group: {o["id"] for o in data.get(group, []) if "id" in o} for group in groups}
    def references(items: list[dict[str, Any]], group: str, field: str, target: str) -> None:
        ids = entity_sets[target]
        for idx, item in enumerate(items):
            for ref in item.get(field, []):
                if ref not in ids:
                    errors.append(f"{group}[{idx}].{field} references missing {target} ID {ref!r}")
    references(data.get("features", []), "features", "actor_ids", "actors")
    references(data.get("data_categories", []), "data_categories", "subject_actor_ids", "actors")
    references(data.get("data_flows", []), "data_flows", "feature_ids", "features")
    references(data.get("data_flows", []), "data_flows", "data_category_ids", "data_categories")
    references(data.get("data_flows", []), "data_flows", "subject_actor_ids", "actors")
    references(data.get("third_parties", []), "third_parties", "data_category_ids", "data_categories")
    for idx, flow in enumerate(data.get("data_flows", [])):
        vendor_id = flow.get("third_party_id")
        if vendor_id is not None and vendor_id not in entity_sets["third_parties"]:
            errors.append(f"data_flows[{idx}].third_party_id references missing vendor {vendor_id!r}")
    for group in ["claims", "unknowns", "risk_signals"]:
        for idx, item in enumerate(data.get(group, [])):
            for ref in item.get("related_ids", []):
                if ref not in global_ids:
                    errors.append(f"{group}[{idx}].related_ids references missing ID {ref!r}")
    for idx, question in enumerate(data.get("interview", {}).get("question_history", [])):
        for ref in question.get("updated_ids", []):
            if ref not in global_ids:
                errors.append(f"interview.question_history[{idx}].updated_ids references missing ID {ref!r}")
    coverage = data.get("interview", {}).get("coverage", [])
    names = [c.get("domain") for c in coverage]
    if len(names) != len(set(names)):
        errors.append("interview.coverage repeats a domain")
    if data.get("interview", {}).get("status") == "discovery_complete":
        required_domains = set(read_json(SCHEMA)["$defs"]["interview"]["properties"]["coverage"]["items"]["properties"]["domain"]["enum"])
        if set(names) != required_domains:
            errors.append("discovery_complete requires all 12 coverage domains")
        if any(c.get("status") not in ("sufficient", "not_applicable") for c in coverage):
            errors.append("discovery_complete requires each domain to be sufficient or justified not_applicable")
        if any(not c.get("reason", "").strip() for c in coverage):
            errors.append("discovery_complete requires a reason for every coverage domain")
        project = data["project"]
        initial = read_json(TEMPLATE)["project"]
        for field in ("name", "summary"):
            if project[field] == initial[field]:
                errors.append(f"discovery_complete requires a substantive project.{field}")
        for field in ("product_types",):
            if not project[field]:
                errors.append(f"discovery_complete requires project.{field}")
        for field in ("actors", "features"):
            if not data[field]:
                errors.append(f"discovery_complete requires at least one {field} record")
        for field in ("platforms", "channels"):
            if not data["distribution"][field]:
                errors.append(f"discovery_complete requires distribution.{field}")
        if any(not feature["actor_ids"] for feature in data["features"]):
            errors.append("discovery_complete requires an actor link for every feature")
        if data["data_categories"] and not data["data_flows"]:
            errors.append("discovery_complete requires data flows for the recorded data inventory")
        for field in ("question_history", "last_updated"):
            if not data["interview"][field]:
                errors.append(f"discovery_complete requires interview.{field}")
    return errors


def validation_errors(data: dict[str, Any]) -> list[str]:
    import jsonschema
    import rfc3339_validator

    if data.get("schema_version") == "1.0.0":
        return ["schema_version 1.0.0 requires explicit migration: use migrate --output <new-file.json> and review the candidate"]
    schema = read_json(SCHEMA)
    format_checker = jsonschema.FormatChecker()

    @format_checker.checks("date-time")
    def valid_timestamp(value: Any) -> bool:
        return not isinstance(value, str) or rfc3339_validator.validate_rfc3339(value.upper())

    validator = jsonschema.Draft202012Validator(schema, format_checker=format_checker)
    errors = [f"{'.'.join(str(p) for p in e.absolute_path) or '$'}: {e.message}" for e in validator.iter_errors(data)]
    if not errors:
        errors.extend(cross_reference_errors(data))
    return errors


def report_errors(target: Path, errors: list[str]) -> None:
    print(f"INVALID {target} ({len(errors)} issue(s))", file=sys.stderr)
    for error in errors:
        print(f" - {error}", file=sys.stderr)


def validate(args: argparse.Namespace) -> int:
    target = workspace_path(args)
    errors = validation_errors(read_workspace(target))
    if errors:
        report_errors(target, errors)
        return 1
    print(f"VALID {target} (schema {SCHEMA_VERSION}; cross-references checked; evidence contents require review)")
    return 0


def migrate(args: argparse.Namespace) -> int:
    source = workspace_path(args)
    target = Path(args.output).resolve()
    if target.exists():
        raise ValueError(f"Migration output already exists: {target}. Refusing to overwrite.")
    data = read_workspace(source)
    if data.get("schema_version") != "1.0.0":
        raise ValueError("migrate accepts only schema 1.0.0; the source is never overwritten.")
    data["schema_version"] = SCHEMA_VERSION
    errors = validation_errors(data)
    write_new_json(target, data)
    print(f"Wrote migration candidate {target}; source unchanged: {source}")
    if errors:
        report_errors(target, errors)
        print("Repair the candidate without inventing evidence or erasing history, then validate and review its diff.", file=sys.stderr)
        return 1
    print("Candidate is valid. Review its diff before replacing the original workspace.")
    return 0


def status(args: argparse.Namespace) -> int:
    data = read_workspace(workspace_path(args))
    for field in ("project", "interview"):
        if not isinstance(data.get(field), dict):
            raise ValueError(f"Workspace {field} must be an object; run validate for details.")
    for field in ENTITY_GROUPS:
        if not isinstance(data.get(field), list) or any(not isinstance(item, dict) for item in data[field]):
            raise ValueError(f"Workspace {field} must be an array of objects; run validate for details.")
    interview = data.get("interview", {})
    coverage = interview.get("coverage", [])
    history = interview.get("question_history", [])
    if not isinstance(coverage, list) or any(not isinstance(item, dict) for item in coverage) or not isinstance(history, list):
        raise ValueError("Invalid interview coverage or question history; run validate for details.")
    for item in data["unknowns"]:
        if any(not isinstance(item.get(field), str) for field in ("id", "priority", "question", "status")):
            raise ValueError("Unknown records require string id, priority, question and status; run validate for details.")
    unknowns = [item for item in data.get("unknowns", []) if item.get("status") in ("open", "research_needed")]
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    unknowns.sort(key=lambda x: (priority_order.get(x.get("priority"), 4), x.get("id", "")))
    print(f"# Discovery status: {data.get('project', {}).get('name', 'Unknown')}")
    print(f"Recorded interview: {interview.get('status', 'unknown')}")
    print("Validation: not performed by status; run validate to check this snapshot.")
    print(f"Questions answered: {len(interview.get('question_history', []))}")
    print(f"Actors: {len(data.get('actors', []))} | Features: {len(data.get('features', []))} | Data flows: {len(data.get('data_flows', []))}")
    print(f"Covered domains: {sum(1 for c in coverage if c.get('status') in ('sufficient', 'not_applicable'))}/{len(coverage)}")
    print(f"Open unknowns: {len(unknowns)} | Risk hypotheses: {sum(1 for r in data.get('risk_signals', []) if r.get('status') in ('hypothesis', 'requires_research'))}")
    if unknowns:
        print("\nPriority follow-ups:")
        for item in unknowns[:7]:
            print(f"- [{item['priority']}] {item['id']}: {item['question']}")
    print("\nDiscovery status is NOT a legal compliance or launch-readiness verdict.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for command in ("init", "validate", "status", "migrate"):
        cmd = subparsers.add_parser(command)
        cmd.add_argument("--project-root", default=".", help="Product repository root (default: current directory)")
        cmd.add_argument("--workspace", help="Use this workspace JSON path (for tests or alternate layouts)")
        if command == "init":
            cmd.add_argument("--name", help="Project name")
            cmd.add_argument("--summary", help="One-sentence product description")
        if command == "migrate":
            cmd.add_argument("--output", required=True, help="New candidate file; never overwrite the source or an existing file")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        print("Workspace tooling requires Python 3.10 or later.", file=sys.stderr)
        return 2
    try:
        return {"init": init, "validate": validate, "status": status, "migrate": migrate}[args.action](args)
    except ImportError:
        requirements = shlex.quote(str(SKILL_ROOT / "requirements.txt"))
        print(f"Complete validation requires the bundled Python dependencies. Install in your Python environment with: python -m pip install -r {requirements}", file=sys.stderr)
        return 3
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
