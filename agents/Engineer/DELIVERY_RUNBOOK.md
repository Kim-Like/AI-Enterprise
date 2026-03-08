# Delivery Runbook

## Scope

Standard execution flow for all Engineer-led changes in the IAn control plane.

## Pre-Work Checklist

1. Confirm objective and owning `master_id` + `program_id`.
2. Confirm working directory is `/Users/IAn/Agent/IAn`.
3. Read latest `engineer/MEMORY.md` and `father/MEMORY.md`.

## Implementation Flow

1. Apply code/doc changes.
2. Run tests:
   - `pytest -q`
3. Run core endpoint checks:
   - `/health`
   - `/api/system-map`
   - `/api/datastores/verify`
4. Validate queue contract for any new tasks.
5. Update memory/context docs when behavior changes.

## Runtime Verification

```bash
lsof -nP -iTCP:8001 -sTCP:LISTEN
curl -s http://127.0.0.1:8001/health
sqlite3 /Users/IAn/Agent/IAn/father.db "PRAGMA journal_mode;"
```

Expected journal mode: `wal`

## Rollback

1. Revert code/docs in git where possible.
2. Restart service and recheck endpoints.
3. Confirm DB integrity and queue readability.

## Definition of Done

- tests passing
- endpoints healthy
- routing/ownership intact
- docs/memory updated
- no unmanaged changes outside canonical root
