# AI-Enterprise Deployment Provenance

## Principle

Every live rollout must be explainable in terms of Git history.

The minimum acceptable provenance record is:

- repo ID
- branch or tag
- commit SHA
- deploy target
- deploy timestamp
- validation result
- autonomy run id when the action came from the executor host
- rollback anchor when validation or bootstrap can be reversed locally

If a live surface cannot be tied back to a commit, it is out of governance.

## Rollout Sequence

1. Validate the repo topology and remote contract:

```bash
cd /Users/IAn/Agent/AI-Enterprise
bash scripts/validate_git_governance.sh
```

2. Validate the application and remote runtime surfaces:

```bash
cd /Users/IAn/Agent/AI-Enterprise
bash scripts/validate_ai_enterprise.sh
```

3. Record the Git commit used for release:

```bash
git rev-parse HEAD
```

4. Deploy the intended revision to the target host.

5. Re-run the post-deploy health checks.

For autonomy-managed repo reconciliation, the same evidence is written to SQLite in `deployment_provenance`, and the latest topology sync row in `autonomy_repo_sync` points at the latest provenance record.

For create-if-missing governed repos, provenance is recorded after the GitHub provider-side repo existence check or creation step, so the latest row can show whether the remote already existed or was created by the autonomy run.

## Rollback Rule

Rollback is performed by returning a deploy boundary to a known-good commit or tag.

For Git-backed cPanel surfaces:

- use the existing release preflight and rollback workflow where available
- treat the Git SHA as the rollback anchor
- never treat "whatever is currently on the server" as the rollback reference

## Suggested Provenance Record

```json
{
  "repo_id": "lavprishjemmeside.dk",
  "autonomy_run_id": "f2f598f1-3d23-4b66-b85f-77f48f9b4a4f",
  "ref": "main",
  "commit": "abc123def456",
  "deploy_target": "cpanel:api.lavprishjemmeside.dk",
  "deployed_at": "2026-03-08T22:30:00Z",
  "validated": true,
  "rollback_anchor": {
    "origin": "git@github.com:Kim-Like/lavprishjemmeside.dk.git",
    "commit": "abc123def456"
  }
}
```

## cPanel Contract

cPanel remains a deploy target. It is validated after rollout with:

- `scripts/check_remote_config_contract.sh`
- `scripts/verify_remote_portfolio.sh`

These checks prove that runtime config is still hardened and that the live health surfaces still answer.

## Related Files

- `docs/infrastructure-topology.md`
- `docs/repository-governance.md`
- `docs/autonomy-provisioning.md`
- `ops/repository-topology.json`
- `scripts/bootstrap_primary_remote.sh`
- `scripts/validate_git_governance.sh`
