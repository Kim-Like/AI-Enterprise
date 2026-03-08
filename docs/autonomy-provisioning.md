# AI-Enterprise Autonomy Provisioning

## Wave 2 Contract

Wave 2 upgrades autonomy from preflight-only planning to an audited executor runtime.

`ops/repository-topology.json` still defines the governed-repo contract, but routine work now flows through an always-on executor host, durable audit tables, topology sync, and deployment provenance sync.

## Single Source Of Truth

`ops/repository-topology.json` remains the only desired-state inventory for governed repositories.

Sync rule:

1. `primary_remote_env` stays the runtime override for an already-configured remote URL.
2. `primary_remote` describes the canonical provider-side repo identity when the env var is empty.
3. `autonomy` now declares Wave 2 execution support with `dry_run` and `provision`.
4. No second provisioning YAML, JSON, or database inventory is allowed.

## Repository Contract

Each governed repository entry carries:

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

Wave 2 uses `allowed_modes: ["dry_run", "provision"]`, `wave: 2`, and `preflight_only: false`.

`credential_ref` points at the server-side environment variable that holds the non-human provider credential. The current GitHub provider reference remains `GITHUB_AUTONOMY_TOKEN`.

## Policy Gates

Autonomy policy remains admin-managed through the existing `settings` table and `/api/settings/{key}` route.

Relevant keys:

- `AUTONOMY_ENABLED`
- `AUTONOMY_MODE`
- `AUTONOMY_REPO_PROVISIONING_ENABLED`
- `AUTONOMY_ALLOWED_REPOSITORY_IDS`
- `AUTONOMY_REQUIRE_STRICT_VALIDATION`
- `AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS`
- `AUTONOMY_AUDIT_READY`
- `AUTONOMY_EXECUTOR_ENABLED`
- `AUTONOMY_EXECUTOR_ALLOWED_AGENTS`

Wave 2 semantics:

- `AUTONOMY_MODE=off` blocks autonomy work.
- `AUTONOMY_MODE=dry_run` allows audited preflight and scheduled dry runs only.
- `AUTONOMY_MODE=provision` enables live bootstrap or reconcile work only when `AUTONOMY_AUDIT_READY=1`.
- `AUTONOMY_EXECUTOR_ENABLED=1` is required before the executor host may run IAn or Engineer tasks.
- `AUTONOMY_ALLOWED_REPOSITORY_IDS` and `AUTONOMY_EXECUTOR_ALLOWED_AGENTS` bound repo scope and actor scope separately.
- Destructive cleanup stays blocked unless `AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS=1`, and the Wave 2 runtime still defaults to quarantine instead of destruction.

## API Surface

Preflight planning remains available through:

- `GET /api/autonomy/policy`
- `POST /api/autonomy/provisioning/preflight`

Executor-host runtime and audit surfaces are:

- `GET /api/autonomy/executor`
- `POST /api/autonomy/executor/run`
- `GET /api/autonomy/audit/runs`
- `GET /api/autonomy/sync/repositories`

`/api/autonomy/provisioning/preflight` stays `dry_run` only. Live provision mode uses `/api/autonomy/executor/run`.

## Audit, Topology Sync, And Provenance

Wave 2 writes durable runtime state to:

- `autonomy_runs`
- `autonomy_actions`
- `autonomy_repo_sync`
- `deployment_provenance`

The topology sync row tracks the latest repo status, validation result, rollback anchor, quarantine state, and latest provenance record. This is the topology sync boundary for governed repos.

Each live executor run records:

- trigger source
- actor identity
- credential class
- requested mode
- commit anchor
- rollback anchor
- validation status
- quarantine outcome

## CLI Surface

Dry-run preflight:

```bash
bash scripts/provision_governed_remote.sh --repo-id ai-enterprise --mode dry_run --json
```

Authenticated executor run:

```bash
bash scripts/run_autonomy_executor.sh --repo-id ai-enterprise --actor-agent-id engineer --mode dry_run
```

Host validation:

```bash
bash scripts/validate_autonomy.sh
```

## Rollback And Quarantine

Wave 2 does not assume provider-side creation is fully reversible.

- If bootstrap fails, the run is quarantined and the previous local `origin` contract is restored when possible.
- If validation fails after bootstrap, the executor records a failed provenance row, restores the previous `origin`, and leaves the repo in quarantine state.
- The rollback anchor stores the pre-run commit and the pre-run `origin` value so a human can reason about what changed.

## Related Files

- `docs/autonomy-executor-host.md`
- `docs/deployment-provenance.md`
- `docs/security-model.md`
- `ops/repository-topology.json`
- `scripts/run_autonomy_executor.sh`
- `scripts/validate_autonomy.sh`
