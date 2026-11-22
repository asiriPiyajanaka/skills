#!/usr/bin/env python3
"""Create, validate and summarize the Product Assurance discovery workspace.

`init` and `status` use only the Python standard library.
`validate` requires jsonschema>=4.21 for complete schema validation.
No command executes the product's code or calls an external service.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "workspace.template.json"
SCHEMA = SKILL_ROOT / "assets" / "workspace.schema.json"
WORKSPACE_RELATIVE_PATH = Path(".product-assurance") / "workspace.json"


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read {path}: {exc}") from exc


def workspace_path(args: argparse.Namespace) -> Path:
    if getattr(args, "workspace", None):
        return Path(args.workspace).resolve()
    return Path(args.project_root).resolve() / WORKSPACE_RELATIVE_PATH


def init(args: argparse.Namespace) -> int:
    target = workspace_path(args)
    if target.exists():
        print(f"Workspace already exists: {target}. Refusing to overwrite.", file=sys.stderr)
        return 2
    data = read_json(TEMPLATE)
    if args.name:
        data["project"]["name"] = args.name
    if args.summary:
        data["project"]["summary"] = args.summary
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
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
    groups = ["actors", "features", "data_categories", "data_flows", "third_parties", "jurisdictions", "claims", "unknowns", "risk_signals"]
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
        required_domains = {
            "product_and_business", "actors_and_age", "markets_and_distribution", "features_and_content",
            "data_inventory_and_flows", "device_permissions_and_tracking", "ai_and_third_parties",
            "security_and_access", "payments_and_marketing", "regulated_activities_and_ip",
            "retention_rights_and_operations", "accessibility_and_user_harm",
        }
        if set(names) != required_domains:
            errors.append("discovery_complete requires all 12 coverage domains")
        if any(c.get("status") not in ("sufficient", "not_applicable") for c in coverage):
            errors.append("discovery_complete requires each domain to be sufficient or justified not_applicable")
        if any(c.get("status") == "not_applicable" and not c.get("reason", "").strip() for c in coverage):
            errors.append("discovery_complete requires a reason for each not_applicable domain")
    return errors


def validate(args: argparse.Namespace) -> int:
    target = workspace_path(args)
    try:
        data = read_json(target)
        import jsonschema
        schema = read_json(SCHEMA)
        validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
        errors = [f"{'.'.join(str(p) for p in e.absolute_path) or '$'}: {e.message}" for e in validator.iter_errors(data)]
        if not errors:
            errors.extend(cross_reference_errors(data))
    except ImportError:
        print("Complete validation requires jsonschema. Install with: python3 -m pip install 'jsonschema>=4.21,<5'", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if errors:
        print(f"INVALID {target} ({len(errors)} issue(s))", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(f"VALID {target} (schema 1.0.0; cross-references checked)")
    return 0


def status(args: argparse.Namespace) -> int:
    try:
        data = read_json(workspace_path(args))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    interview = data.get("interview", {})
    coverage = interview.get("coverage", [])
    unknowns = [item for item in data.get("unknowns", []) if item.get("status") in ("open", "research_needed")]
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    unknowns.sort(key=lambda x: (priority_order.get(x.get("priority"), 4), x.get("id", "")))
    print(f"# Discovery status: {data.get('project', {}).get('name', 'Unknown')}")
    print(f"Interview: {interview.get('status', 'unknown')}")
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
    for command in ("init", "validate", "status"):
        cmd = subparsers.add_parser(command)
        cmd.add_argument("--project-root", default=".", help="Product repository root (default: current directory)")
        cmd.add_argument("--workspace", help="Use this workspace JSON path (for tests or alternate layouts)")
        if command == "init":
            cmd.add_argument("--name", help="Project name")
            cmd.add_argument("--summary", help="One-sentence product description")
    args = parser.parse_args()
    return {"init": init, "validate": validate, "status": status}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
