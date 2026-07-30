"""Command-line entry point for htpasswd-cli."""
from __future__ import annotations

import argparse
import getpass
import sys

from .core import format_entry, merge_entry, validate_username


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="htpasswd-cli",
        description="Generate Apache-style htpasswd entries (username:hash) for HTTP Basic Auth.",
    )
    parser.add_argument("username", help="Username to generate an entry for")
    parser.add_argument(
        "--password",
        help="Password to hash (insecure: visible in shell history/process list; omit to be prompted)",
    )
    parser.add_argument(
        "--append", metavar="FILE", help="Add or update this user's entry in an existing htpasswd-style file"
    )
    return parser


def _prompt_password() -> str:
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise ValueError("passwords do not match")
    return password


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        validate_username(args.username)
    except ValueError as exc:
        print(f"htpasswd-cli: error: {exc}", file=sys.stderr)
        return 2

    if args.password is not None:
        password = args.password
    else:
        try:
            password = _prompt_password()
        except ValueError as exc:
            print(f"htpasswd-cli: error: {exc}", file=sys.stderr)
            return 2
        except (EOFError, KeyboardInterrupt):
            print("htpasswd-cli: aborted", file=sys.stderr)
            return 2

    if not args.append:
        print(format_entry(args.username, password))
        return 0

    try:
        with open(args.append, "r", encoding="utf-8") as fh:
            existing = fh.read()
    except FileNotFoundError:
        existing = ""
    except OSError as exc:
        print(f"htpasswd-cli: error: {exc}", file=sys.stderr)
        return 2

    new_content, action = merge_entry(existing, args.username, password)

    try:
        with open(args.append, "w", encoding="utf-8") as fh:
            fh.write(new_content)
    except OSError as exc:
        print(f"htpasswd-cli: error: {exc}", file=sys.stderr)
        return 2

    print(f"htpasswd-cli: {action} entry for '{args.username}' in {args.append}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
