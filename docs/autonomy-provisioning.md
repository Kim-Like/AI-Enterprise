# AI-Enterprise Autonomy Provisioning

## Wave 1 Contract

Wave 1 adds topology-driven governed remote provisioning in `dry_run` and `preflight` mode only.

Live provider writes stay blocked until durable audit plumbing lands in Phase 10 Plan 10-02.

## Single Source Of Truth

`ops/repository-topology.json` remains the only desired-state inventory for governed repositories.

Sync rule:

1. `primary_remote_env` remains the runtime override for an already-configured remote URL.
2. `primary_remote` describes the canonical provider-side repo identity if the env var is empty.
3. `autonomy` declares Wave 1 scope and keeps provisioning preflight-only.
4. No second provisioning YAML, JSON, or database inventory is allowed.

## Repository Contract

Each governed repository entry now carries:

- `primary_remote.provider`
- `primary_remote.namespace`
- `primary_remote.repo_name`
- `primary_remote.protocol`
- `primary_remote.create_if_missing`
- `primary_remote.credential_ref`
- `autonomy.scope`
- `autonomy.allowed_modes`
- `autonomy.wave`
- `autonomy.preflight_only`

`credential_ref` points at the server-side environment variable that holds the non-human provider credential. Wave 1 uses `GITHUB_AUTONOMY_TOKEN` as the GitHub provisioning reference.

## Policy Gates

Autonomy policy stays admin-managed through the existing `settings` table and `/api/settings/{key}` route.

Relevant keys:

- `AUTONOMY_ENABLED`
- `AUTONOMY_MODE`
- `AUTONOMY_REPO_PROVISIONING_ENABLED`
- `AUTONOMY_ALLOWED_REPOSITORY_IDS`
- `AUTONOMY_REQUIRE_STRICT_VALIDATION`
- `AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS`
- `AUTONOMY_AUDIT_READY`

Wave 1 semantics:

- `AUTONOMY_MODE=off` blocks all autonomy provisioning work.
- `AUTONOMY_MODE=dry_run` allows preflight planning only.
- `AUTONOMY_MODE=provision` is still blocked for live writes because `AUTONOMY_AUDIT_READY=0` and Wave 1 is preflight-only.
- `AUTONOMY_ALLOWED_REPOSITORY_IDS` must explicitly scope which repos may be reconciled.

## Script Surface

Preflight governed provisioning through:

```bash
bash scripts/provision_governed_remote.sh --repo-id ai-enterprise --mode dry_run
```

The wrapper does not reimplement Git bootstrap logic. It reads the topology manifest, derives the expected remote, validates `credential_ref`, and emits the exact `bootstrap_primary_remote.sh` command that would be used once live execution is allowed.

Use `--json` for machine-readable output:

```bash
bash scripts/provision_governed_remote.sh --repo-id ai-enterprise --mode dry_run --json
```

## API Surface

Provisioning policy and preflight are available through:

- `GET /api/autonomy/policy`
- `POST /api/autonomy/provisioning/preflight`

Both routes require write authorization, but the provisioning route still enforces the autonomy policy gates before returning a preflight plan. Admin access does not bypass the soft kill switch or repository scope rules.
