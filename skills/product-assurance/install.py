#!/usr/bin/env python3
"""Install the self-contained cross-examine skill in an existing project."""
import argparse
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "skills" / "cross-examine"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, help="Path to repository where skill should be installed")
    p.add_argument("--agent", choices=["codex", "cursor", "claude", "all"], default="all")
    p.add_argument("--replace", action="store_true", help="Replace an existing installed copy")
    args = p.parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        p.error(f"Project directory does not exist: {root}")
    folders = [".agents/skills"] if args.agent in ("codex", "cursor") else [".claude/skills"]
    if args.agent == "all":
        folders = [".agents/skills", ".claude/skills"]
    destinations = [root / parent / "cross-examine" for parent in folders]
    occupied = [dest for dest in destinations if dest.exists()]
    if occupied and not args.replace:
        p.error("Destination(s) exist; refusing to overwrite: " + ", ".join(map(str, occupied)) + ". Use --replace if intentional.")
    for dest in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)
        shutil.copytree(SOURCE, dest)
        print(f"Installed: {dest}")
    print("Start a fresh agent conversation or reload skills, then invoke cross-examine with your product idea.")


if __name__ == "__main__":
    main()
