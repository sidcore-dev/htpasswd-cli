"""Core hashing and file-merge logic for htpasswd-cli."""
from __future__ import annotations

import base64
import hashlib

SHA256_PREFIX = "{SHA256}"


def hash_password(password: str) -> str:
    """Return an Apache/nginx-style crypt-format hash for `password`.

    This produces an unsalted SHA-256 digest, base64-encoded, prefixed with
    `{SHA256}` in the style crypt-format password fields use. It is NOT
    bcrypt and NOT salted -- see the README for the security tradeoffs
    before using this for anything beyond low-stakes internal tooling.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return SHA256_PREFIX + base64.b64encode(digest).decode("ascii")


def validate_username(username: str) -> None:
    """Raise ValueError if `username` is not usable in a htpasswd line."""
    if not username:
        raise ValueError("username must not be empty")
    if ":" in username:
        raise ValueError("username must not contain ':'")
    if "\n" in username or "\r" in username:
        raise ValueError("username must not contain newlines")


def format_entry(username: str, password: str) -> str:
    """Return a full 'username:hash' htpasswd line (no trailing newline)."""
    validate_username(username)
    return f"{username}:{hash_password(password)}"


def merge_entry(existing: str, username: str, password: str) -> tuple[str, str]:
    """Insert or replace `username`'s entry within existing htpasswd content.

    Comment lines (starting with '#') and blank lines are preserved as-is.
    Returns (new_content, action) where action is "added" or "updated".
    """
    validate_username(username)
    new_entry = format_entry(username, password)

    out_lines: list[str] = []
    replaced = False
    for line in existing.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue
        name = stripped.split(":", 1)[0]
        if name == username:
            out_lines.append(new_entry)
            replaced = True
        else:
            out_lines.append(line)

    if not replaced:
        out_lines.append(new_entry)

    action = "updated" if replaced else "added"
    new_content = "\n".join(out_lines) + "\n"
    return new_content, action
