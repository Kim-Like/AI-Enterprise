# AI-Enterprise Autonomy Executor Host

## Purpose

The autonomy executor host is the always-on, non-human runtime for routine IAn and Engineer reconciliation work.

It removes laptop-bound state from governed repo provisioning, validation, and topology sync.

## Host Identity

Required host contract:

- Linux host on the tailnet
- Tailscale tag: `tag:ai-autonomy`
- Stable host id: `AUTONOMY_EXECUTOR_HOST_ID=ai-enterprise-autonomy`
- Maintenance access via Tailscale SSH, not forwarded laptop agents

## Required Directories

- `/srv/ai-enterprise` for the checked-out control plane repo
- `/srv/ai-enterprise/state` for executor runtime state and scratch files
- `/var/log/ai-enterprise` for host-local logs
- `/etc/ai-enterprise/autonomy.env` for server-managed environment configuration

## Environment Contract

Minimum env file keys:

- `DASHBOARD_ADMIN_KEY`
- `IAN_AUTONOMY_KEY`
- `IAN_AUTONOMY_HEADER`
- `GITHUB_AUTONOMY_TOKEN`
- `AUTONOMY_EXECUTOR_HOST_ID`
- `AUTONOMY_EXECUTOR_TAG`
- `AUTONOMY_STATE_ROOT`
- `AUTONOMY_API_URL`
- `AUTONOMY_HOST_KILL_SWITCH_FILE`
- `AUTONOMY_EXECUTOR_ACTOR`
- `AUTONOMY_EXECUTOR_MODE`

Recommended defaults:

- `AUTONOMY_API_URL=http://127.0.0.1:8001`
- `AUTONOMY_EXECUTOR_ACTOR=ian-master`
- `AUTONOMY_EXECUTOR_MODE=dry_run`
- `AUTONOMY_HOST_KILL_SWITCH_FILE=/etc/ai-enterprise/autonomy.disabled`

## Systemd Units

Wave 2 ships the host artifacts in `ops/systemd/`:

- `ai-enterprise-api.service`
- `ai-enterprise-autonomy.service`
- `ai-enterprise-autonomy.timer`

Install flow:

```bash
sudo cp ops/systemd/ai-enterprise-api.service /etc/systemd/system/
sudo cp ops/systemd/ai-enterprise-autonomy.service /etc/systemd/system/
sudo cp ops/systemd/ai-enterprise-autonomy.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ai-enterprise-api.service
sudo systemctl enable --now ai-enterprise-autonomy.timer
```

## Scheduled And Event-Driven Execution

Scheduled execution:

- `ai-enterprise-autonomy.timer` starts `ai-enterprise-autonomy.service`.
- The service runs `scripts/run_autonomy_executor.sh --all --trigger-source systemd_timer`.
- The runner authenticates to `POST /api/autonomy/executor/run` with `IAN_AUTONOMY_KEY`.

Event-driven execution:

```bash
bash scripts/run_autonomy_executor.sh --repo-id ai-enterprise --actor-agent-id engineer --mode dry_run --trigger-source manual_api
```

This is the authenticated IAn or Engineer execution path on the autonomy host contract.

## Safety Rails

Soft kill switch:

- `AUTONOMY_ENABLED=0` or `AUTONOMY_MODE=off` in the database blocks runtime work.

Hard kill switch:

- `AUTONOMY_HARD_DISABLE=1`, or
- create the file at `AUTONOMY_HOST_KILL_SWITCH_FILE`

When the hard kill switch is active, `scripts/run_autonomy_executor.sh` and `/api/autonomy/executor/run` refuse to proceed.

## Audit, Topology Sync, And Provenance

Every executor run writes durable audit rows and updates topology sync state.

- `autonomy_runs` stores run-level actor, trigger, validation, commit, rollback, and quarantine state.
- `autonomy_actions` stores per-repository action outcomes.
- `autonomy_repo_sync` is the topology sync table for the latest governed-repo state.
- `deployment_provenance` stores the latest provenance record tied to the autonomy run id.
- When a governed GitHub repo is missing, the executor creates it with `GITHUB_AUTONOMY_TOKEN` before local bootstrap and records whether the provider-side repo already existed or was created during the run.

Rollback-safe failure handling means bootstrap or validation failures restore the previous `origin` contract when possible and leave the repo quarantined instead of silently continuing.

## Validation

Host-local validation:

```bash
bash scripts/validate_autonomy.sh
```

Canonical validation:

```bash
bash scripts/validate_ai_enterprise.sh
```

`validate_ai_enterprise.sh` now calls `validate_autonomy.sh`, so autonomy remains part of the single validation path.
