"""Command line interface for branching automation."""
from __future__ import annotations

import argparse
import sys

from .branching import BranchAutomation, GitCommandError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate branch workflows for projects.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new feature branch")
    create_parser.add_argument("name", help="Name of the feature branch to create")
    create_parser.add_argument("--base", default="main", help="Base branch to create from")
    create_parser.add_argument(
        "--no-checkout",
        action="store_true",
        help="Do not remain on the created branch after creation",
    )

    list_parser = subparsers.add_parser("list", help="List branches")
    list_parser.add_argument("--remote", action="store_true", help="List remote branches")

    merge_parser = subparsers.add_parser("merge", help="Merge source branch into target")
    merge_parser.add_argument("source", help="Source branch")
    merge_parser.add_argument("target", help="Target branch")

    delete_parser = subparsers.add_parser("delete", help="Delete a branch")
    delete_parser.add_argument("name", help="Branch name")
    delete_parser.add_argument("--remote", action="store_true", help="Delete remote branch")
    delete_parser.add_argument("--remote-name", default="origin", help="Name of the remote")

    track_parser = subparsers.add_parser("track", help="Set upstream tracking branch")
    track_parser.add_argument("name", help="Local branch name")
    track_parser.add_argument("--remote", default="origin", help="Remote to track")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    automation = BranchAutomation()

    try:
        if args.command == "create":
            automation.create_feature_branch(args.name, base=args.base, checkout=not args.no_checkout)
        elif args.command == "list":
            branches = automation.list_branches(remote=args.remote)
            print("\n".join(branches))
        elif args.command == "merge":
            automation.merge_branch(args.source, args.target)
        elif args.command == "delete":
            automation.delete_branch(args.name, remote=args.remote, remote_name=args.remote_name)
        elif args.command == "track":
            automation.ensure_tracking_branch(args.name, remote=args.remote)
        else:
            parser.error("Unknown command")
    except GitCommandError as exc:  # pragma: no cover - exercised indirectly
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
