# htpasswd-cli

A small, dependency-free command-line tool that generates Apache-style
`htpasswd` entries (`username:hash` lines) for HTTP Basic Auth, and can
add or update those entries directly in an existing htpasswd file.

## Why

The standard `htpasswd` binary isn't always installed, and Python's
standard library has no bcrypt (the `crypt` module is Unix-only and was
removed in Python 3.13). This tool covers the common case — generating a
crypt-format entry and dropping it into a file — using only `hashlib`.

**Security note:** entries use the `{SHA256}` crypt-format prefix with an
*unsalted* SHA-256 digest, not bcrypt. This is weaker than a proper bcrypt
or salted-SHA512 hash: it has no per-entry salt, so identical passwords
produce identical hashes, and SHA-256 is fast to brute-force compared to
bcrypt. It's fine for low-stakes internal tooling (a staging server, a
personal dashboard) but not a substitute for `htpasswd -B` (bcrypt) on
anything public-facing or sensitive. Also verify your web server actually
recognizes `{SHA256}` — Apache's own `htpasswd -s` produces `{SHA}` (SHA-1)
instead, and support varies by server and module.

## Install

```bash
pip install .
```

This installs an `htpasswd-cli` command on your PATH.

## Usage

Print an entry to stdout (prompts for the password, with confirmation):

```bash
htpasswd-cli alice
```

```
Password:
Confirm password:
alice:{SHA256}47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=
```

Pass the password non-interactively (visible in shell history — only for
scripting in trusted environments):

```bash
htpasswd-cli alice --password hunter2
```

Add or update an entry directly in a file:

```bash
htpasswd-cli alice --password hunter2 --append /etc/nginx/.htpasswd
```

```
htpasswd-cli: added entry for 'alice' in /etc/nginx/.htpasswd
```

Running it again for the same user updates the existing line in place
instead of duplicating it.

### Options

| Flag           | Description                                                        |
|----------------|----------------------------------------------------------------------|
| `--password`   | Password to hash (insecure: visible in shell history/process list; omit to be prompted) |
| `--append FILE`| Add or update this user's entry in an existing htpasswd-style file  |

### Exit codes

- `0` — entry generated or file updated successfully
- `2` — invalid username/password, or a file I/O error

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
