# Toolchain Requirements

## Required Local Binaries

- `python3` (Python 3.9-compatible runtime)
- `uvicorn`
- `pytest`
- `sqlite3`
- `git`
- `node` and `npm` (program repos)
- `claude` (Claude Pro OAuth CLI)

## Recommended Utilities

- `rg`
- `jq`
- `curl`
- `lsof`
- `mysql` client (for cPanel DB diagnostics)

## Environment Expectations

- local MacBook is host server
- Tailnet access via Tailscale
- `.env` must contain API + integration credentials as needed

## Python Rule

Use typing syntax compatible with Python 3.9:

- `Optional[T]` instead of `T | None`
