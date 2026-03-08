---
phase: 10
slug: autonomy-infrastructure-and-repo-provisioning
created: 2026-03-08
status: researched
---

# Phase 10 Research

**Researched:** 2026-03-08
**Domain:** Always-on autonomy execution, governed Git repo provisioning, service credentials, and rollback-safe validation
**Confidence:** HIGH

<user_constraints>
## User Constraints

### Locked Decisions
- Use a Tailscale-hosted, always-on executor instead of a laptop-bound runtime.
- Keep Git as the canonical source of truth.
- Keep cPanel and other SSH hosts as deploy targets only.
- Allow AI-Enterprise to provision missing governed Git remotes without a human creating them first.
- Use a non-human control identity for autonomous provisioning and writes.
- Keep destructive actions guarded and auditable.
- Extend the existing topology manifest and validation scripts instead of rewriting the platform.

### Verified Baseline
- Phase 9 already established `ops/repository-topology.json` as the machine-readable repo topology contract.
- `scripts/bootstrap_primary_remote.sh` already handles idempotent local repo bootstrap against a chosen remote.
- `scripts/validate_git_governance.sh` and `scripts/validate_ai_enterprise.sh` already form the canonical validation path.
- The clean runtime already uses explicit bootstrap wiring in `api/bootstrap.py`, not import-time mutations.
- The clean backend already distinguishes admin writes from autonomy writes through `DASHBOARD_ADMIN_KEY` and `IAN_AUTONOMY_KEY`.
- The clean schema already has a `settings` table that can hold autonomy policy flags without introducing a second config system.

### Deferred Or Guarded
- Broad CI/CD platform replacement.
- Browser-bound or laptop-bound credentials for routine autonomous writes.
- Automatic destructive actions such as repo deletion, DNS ownership changes, billing changes, or root-secret rotation.

</user_constraints>

<research_summary>
## Summary

The cleanest Phase 10 implementation is not a new autonomy platform. It is an extension of the Phase 9 contracts:

1. run AI-Enterprise on one always-on Linux executor host inside the tailnet
2. keep `ops/repository-topology.json` as the canonical desired-state manifest
3. add a small provisioning/reconciliation layer that wraps the existing Git bootstrap and validation scripts
4. use service credentials that live only on the executor host
5. gate all autonomous writes behind explicit settings, durable audit records, and rollback-safe failure handling

**Primary recommendation:** keep GitHub as the current primary remote strategy if that is the fastest path to operational autonomy, but host the executor itself on Tailscale and treat self-hosted bare Git as an optional secondary remote or later fallback. That matches the current topology manifest, avoids a Phase 10 rewrite of the remote model, and still satisfies the requirement for always-on autonomy.

**Provisioning model:** add a repo-reconcile workflow that reads the topology manifest, checks whether a governed remote exists, creates it through a provider adapter if it does not, bootstraps the local repo with the existing script, records audit/provenance, and then re-runs the existing governance validation.

**Credential model:** use a non-human executor identity everywhere possible. For GitHub, that means a GitHub App or other server-to-server credential. If the `Kim-Like` personal namespace remains the primary namespace in Phase 10, a fine-grained PAT stored only on the executor host is an acceptable transitional implementation, but it should be treated as weaker than an org-backed GitHub App installation token.

**Safety model:** implement both a soft kill switch in the database and a hard kill switch at the host/service level. Autonomous provisioning should default to additive and reversible actions. Failed repo creation should quarantine or archive the new remote rather than silently deleting or continuing.

</research_summary>

<standard_stack>
## Standard Stack

| Layer | Recommended Standard | Why |
|-------|----------------------|-----|
| Executor host | One always-on Linux host on the tailnet | satisfies AUT-02 without depending on an interactive laptop |
| Tailnet identity | Tagged Tailscale node authenticated with a tagged auth key | creates a non-human host identity and avoids personal login state |
| AI runtime | Existing FastAPI app plus a small autonomy worker/timer | extends current runtime instead of replacing it |
| Source of truth | Git history plus `ops/repository-topology.json` | keeps repo governance and desired state in one model |
| Primary remote provisioning | GitHub provider adapter first | matches current Phase 9 policy and repo naming |
| Optional mirror | Tailscale-reachable bare Git mirror | gives private redundancy later without changing the main workflow |
| Secret loading | Server-side env or secret store on the executor host | satisfies AUT-03 and existing security rules |
| Audit store | Existing SQLite database extended with autonomy tables | simplest durable trail that fits the current platform |
| Validation entrypoint | `scripts/validate_ai_enterprise.sh` extended with autonomy validation | preserves the canonical validation path |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Manifest Reconciliation, Not Ad Hoc Provisioning

Treat `ops/repository-topology.json` as the desired-state declaration for governed repos. Phase 10 should add autonomy metadata to that manifest instead of creating a second provisioning inventory.

Recommended extension shape per repository:

```json
{
  "id": "ai-enterprise",
  "classification": "main",
  "local_path": "/Users/IAn/Agent/AI-Enterprise",
  "primary_remote_env": "AI_ENTERPRISE_PRIMARY_GIT_REMOTE",
  "mirror_remote_env": "AI_ENTERPRISE_GIT_MIRROR_REMOTE",
  "primary_remote": {
    "provider": "github",
    "namespace": "Kim-Like",
    "repo_name": "AI-Enterprise",
    "protocol": "ssh",
    "create_if_missing": true,
    "credential_ref": "GITHUB_AUTONOMY"
  }
}
```

This keeps the current env-based runtime contract intact while giving autonomy enough information to derive or create the remote.

### Pattern 2: Thin Provisioning Wrapper Over Existing Git Primitives

Do not replace `scripts/bootstrap_primary_remote.sh`. Phase 10 should add a higher-level script such as `scripts/provision_governed_remote.sh` or `scripts/reconcile_governed_repos.sh` that:

1. reads the topology manifest
2. checks kill-switch and policy settings
3. verifies the provider credential exists
4. checks whether the remote already exists
5. creates the remote if missing
6. calls `bootstrap_primary_remote.sh`
7. pushes the intended default branch if the remote is empty
8. records audit and provenance
9. re-runs `validate_git_governance.sh`

That preserves the Phase 9 contract and keeps provisioning idempotent.

### Pattern 3: Explicit Runtime Wiring

The current clean runtime already isolates startup through `api/bootstrap.py` and FastAPI lifespan wiring in `api/app.py`. Phase 10 should follow the same shape:

- add an autonomy service module
- wire it through explicit startup functions
- keep scheduler startup or recurring worker startup behind a config flag
- avoid import-time provisioning side effects

### Pattern 4: Additive Autonomy With Guarded Escalation

Routine safe actions can be autonomous:

- create a missing governed repo
- configure or verify the expected remote URL
- push a bootstrap branch
- update topology/provenance records
- run validation

Guarded actions should remain admin-only:

- deleting a repo
- force-pushing protected branches
- changing repo ownership or billing owner
- rotating root credentials
- changing DNS authority

</architecture_patterns>

## Tailscale Executor Host

Phase 10 should define one concrete executor host, not a vague future runtime. The recommended shape is:

- one Linux host dedicated to AI-Enterprise autonomy
- enrolled in Tailscale with a tagged auth key
- assigned a stable tag such as `tag:ai-autonomy`
- reachable through Tailscale SSH for maintenance
- running AI-Enterprise services under `systemd`

Recommended services:

- `ai-enterprise-api.service`: runs the existing FastAPI control plane
- `ai-enterprise-autonomy.service`: runs a long-lived worker or a queue poller
- `ai-enterprise-autonomy.timer`: optional simpler alternative that runs a reconcile loop on a schedule

Recommended directories:

- `/srv/ai-enterprise` for the checked-out control-plane repo
- `/srv/ai-enterprise/state` for host-local working state
- `/srv/git` only if a self-hosted mirror or bare remote is later enabled
- `/var/log/ai-enterprise` for host-level operational logs

Why Tailscale fits this phase:

- tagged device identity supports non-human host enrollment
- the host can stay private without public inbound exposure
- Tailscale SSH reduces ad hoc key sprawl for operator access
- the same host can later support private mirrors or remote execution without changing the control-plane model

The executor host should not depend on a browser session, a forwarded agent from an operator laptop, or a one-off shell export. It should boot and run autonomously from server-managed configuration alone.

## Repo Provisioning Model

The provisioning workflow should be topology-driven and provider-aware.

### Recommended Flow

1. Operator or scheduler triggers a reconcile run for one repo or all governed repos.
2. AI-Enterprise loads the topology manifest and filters to `main` and `independent` repositories with `create_if_missing=true`.
3. The provider adapter checks whether the expected remote already exists.
4. If the remote is missing, the adapter creates it with the configured visibility and namespace.
5. The wrapper script calls `bootstrap_primary_remote.sh` to ensure the local repo points at the expected remote.
6. If the remote is empty, the wrapper pushes the intended branch and records the resulting commit SHA.
7. AI-Enterprise records the provisioning result in the audit tables and deployment-provenance trail.
8. The canonical validation path re-runs and marks the run as passed, failed, or quarantined.

### Recommended Provider Adapters

**Primary adapter for Phase 10:** GitHub remote creation.

Why:

- Phase 9 already models GitHub as the current primary strategy in the topology manifest and docs.
- It closes the immediate gap that `validate_git_governance.sh` still reports: remotes are not configured yet.
- It avoids changing the repo boundary model while adding autonomy.

**Optional secondary adapter:** self-hosted bare Git over Tailscale.

Why:

- `bootstrap_primary_remote.sh` already supports `--create-bare` over SSH.
- it is a natural later extension for a private mirror or fallback remote
- it does not need to block initial autonomy delivery

### Recommended New Script Surface

Phase 10 should prefer adding one wrapper script and one validation script:

- `scripts/provision_governed_remote.sh`
- `scripts/validate_autonomy.sh`

The wrapper script should call the existing scripts, not replace them. The validation script should be invoked from `scripts/validate_ai_enterprise.sh`, not from a separate out-of-band workflow.

## Service Credentials Vs User Credentials

The clean split is:

| Capability | Use Human Credential? | Use Service Credential? | Recommendation |
|------------|------------------------|-------------------------|----------------|
| Tailnet host enrollment | no | yes | tagged auth key |
| Tailnet API automation | no | yes | OAuth client only if needed |
| AI-Enterprise autonomous write calls | no | yes | `IAN_AUTONOMY_KEY` or a successor with the same contract |
| Break-glass settings/admin writes | yes | no | `DASHBOARD_ADMIN_KEY` |
| GitHub repo creation and bootstrap push | no | yes | GitHub App preferred; fine-grained PAT only as a transition |
| cPanel deploy SSH | no | yes | dedicated executor-host SSH key |

### GitHub Credential Recommendation

**Best long-term option:** move governed repos under an organization or namespace where a GitHub App installation token can create and manage repos server-to-server.

Why:

- GitHub Apps are the cleanest non-human control identity
- installation tokens are short-lived and scoped
- the credential is not tied to a person logging in interactively

**Acceptable transitional option:** if `Kim-Like` remains a personal namespace in Phase 10, use a fine-grained PAT or GitHub App user token stored only on the executor host.

Tradeoff:

- it still removes laptop/browser dependency
- but it remains more coupled to a human-owned namespace
- rotation and governance are weaker than an org-backed installation token

### AI-Enterprise Internal Auth Recommendation

Keep the current admin/autonomy split and extend it, rather than collapsing everything into one secret:

- `DASHBOARD_ADMIN_KEY` remains break-glass and settings/admin scope
- `IAN_AUTONOMY_KEY` remains the service credential for routine write-capable automation
- autonomy routes should still check explicit policy flags before performing a write

That aligns with the current `api/security/admin_auth.py` behavior and keeps AUT-03 compatible with the Phase 4 security model.

## Safety Rails, Kill Switch, Audit, And Rollback

Autonomy should be explicitly bounded. The minimum safe model is:

### Kill Switch

Implement both:

- a **soft kill switch** in the database `settings` table
- a **hard kill switch** by stopping the executor worker service

Recommended settings:

- `AUTONOMY_ENABLED`
- `AUTONOMY_MODE`
- `AUTONOMY_REPO_PROVISIONING_ENABLED`
- `AUTONOMY_ALLOWED_REPOSITORY_IDS`
- `AUTONOMY_REQUIRE_STRICT_VALIDATION`
- `AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS`

Suggested semantics:

- `AUTONOMY_MODE=off` blocks all autonomous writes
- `AUTONOMY_MODE=dry_run` allows planning and audit only
- `AUTONOMY_MODE=provision` allows non-destructive repo bootstrap work
- destructive operations remain blocked unless explicitly enabled and admin-authorized

### Audit Trail

Do not rely on stdout logs alone. Add durable DB tables that mirror the existing pattern used for execution history and task transitions.

Recommended additions:

- `autonomy_runs`
- `autonomy_actions`

Minimum fields to capture:

- run id
- trigger source
- actor identity
- repo id
- requested action
- planned action
- credential class used
- result status
- validation status
- commit SHA or branch pushed
- rollback anchor
- timestamps

### Rollback-Safe Failure Handling

Autonomy should default to quarantine, not destruction.

Recommended failure behavior:

- if remote creation succeeds but bootstrap fails, mark the remote as `provisioning_failed` and quarantine it in audit state
- if topology or provenance changes were prepared locally but validation fails, do not promote or push those metadata changes
- if a deploy-related step fails after a known commit SHA is recorded, use the existing deployment provenance contract as the rollback anchor
- only archive or delete a newly created remote automatically if explicit destructive policy is enabled

This keeps failure handling safe even when the provider operation itself is not perfectly reversible.

## Validation Architecture

Phase 10 validation should extend the current validation chain rather than fork it.

### 1. Static Contract Validation

Validate that the topology manifest includes the new autonomy/provisioning fields and that they are internally consistent:

- provider is known
- namespace and repo name are present
- only `main` and `independent` repos are eligible for autonomous creation
- credential references are declared
- `primary_remote_env` values still map to the runtime config contract

This belongs in a new autonomy validation script plus Python contract tests.

### 2. Credential Presence Validation

Validate that the executor has the required non-human credentials without exposing them:

- `IAN_AUTONOMY_KEY`
- Git provider credential
- any required SSH key for deploy/bootstrap
- any optional Tailscale API credential if tailnet API calls are used

This should reuse the existing secret-status philosophy: prove presence and status, never echo values.

### 3. Executor Host Validation

Validate the always-on host itself:

- Tailscale is connected
- the host tag or identity matches the expected autonomy role
- required `systemd` units are active
- the AI-Enterprise working tree is present
- the runtime can reach the configured provider endpoints

This should be part of `scripts/validate_autonomy.sh`, not a separate platform.

### 4. Dry-Run Provisioning Validation

Every reconcile path should support `dry_run` and prove:

- which repo would be created
- which remote URL would be written
- which branch would be pushed
- which validation steps would execute
- which rollback anchor would exist

Dry-run mode should be mandatory in tests and available in production before enabling live writes.

### 5. Live Provisioning Integration Validation

Add an integration path that proves end-to-end remote creation and bootstrap for a safe test target:

- create a disposable governed repo or sandbox target
- bootstrap the local working tree to it
- push the initial branch
- re-run `validate_git_governance.sh`
- confirm audit rows and provenance output were written

This is the core proof for AUT-01, AUT-03, AUT-05, and VAL-06.

### 6. Failure-Path Validation

Deliberately test failure cases:

- missing provider credential
- remote already exists
- provider create succeeds but push fails
- validation fails after bootstrap
- kill switch turns on mid-run

A passing result means the system leaves an audit trail, returns a clear status, and does not continue into uncontrolled writes.

### 7. Canonical Validation Wiring

The top-level validation path should remain:

```bash
bash scripts/validate_ai_enterprise.sh
```

Phase 10 should extend it so that it also invokes:

- `scripts/validate_autonomy.sh`
- new Python tests for autonomy contracts and auth

Recommended test additions:

- extend `tests/test_phase9_contracts.py` into a broader infrastructure contract suite or add `tests/test_phase10_contracts.py`
- add API tests covering autonomy policy and kill-switch enforcement
- add script-level tests for dry-run and bootstrap behavior using temporary repos

If Phase 10 ships without this wiring, autonomy will exist operationally but not canonically.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| executor identity | personal laptop login flow | tagged Tailscale node identity | stable non-human host |
| repo provisioning state | second inventory file | extend `ops/repository-topology.json` | keeps desired state unified |
| bootstrap logic | new Git bootstrap implementation | existing `bootstrap_primary_remote.sh` | preserves tested Phase 9 primitive |
| validation entrypoint | separate autonomy checker tree | extend `validate_ai_enterprise.sh` | keeps one canonical gate |
| write authorization | one super-secret for everything | existing admin/autonomy split plus settings policy | clearer blast-radius control |
| rollback model | implicit cleanup assumptions | explicit audit plus quarantine/archive rules | safer failure handling |

## Common Pitfalls

### Pitfall 1: Treating The Executor Host As A Personal Machine

If the host still depends on an operator shell session, forwarded SSH agent, or browser login, AUT-02 and AUT-03 are not actually solved.

### Pitfall 2: Building A Second Provisioning Truth

If autonomy uses a separate YAML or DB inventory that can drift from `ops/repository-topology.json`, Phase 10 breaks the Phase 9 governance model instead of extending it.

### Pitfall 3: Using Admin Keys For Routine Autonomous Writes

If the autonomy worker uses the admin key for all actions, the safety boundary between break-glass admin and routine automation disappears.

### Pitfall 4: Treating Repo Creation As Fully Reversible

Provider-side creation often cannot be cleanly undone without a destructive action. Safe default behavior is quarantine and audit, not silent deletion.

### Pitfall 5: Rewriting Startup Around Background Autonomy

The clean runtime already fixed the earlier startup-side-effect problem. Phase 10 should keep explicit bootstrap wiring and avoid reintroducing hidden startup mutations.

## Implementation Notes For AI-Enterprise

The existing codebase already contains the extension points needed for this phase:

- `api/bootstrap.py` and `api/app.py` already provide explicit startup hooks
- `api/security/admin_auth.py` already distinguishes autonomy writes from admin-only actions
- `api/routes/settings.py` already provides an admin-only control surface for kill-switch settings
- `api/db/schema.sql` already contains a `settings` table and other audit-style tables that new autonomy tables can mirror
- `scripts/bootstrap_primary_remote.sh` already handles idempotent remote wiring
- `scripts/validate_git_governance.sh` already verifies topology and remote reachability
- `scripts/validate_ai_enterprise.sh` is already the canonical end-to-end validation entrypoint

That means Phase 10 should mostly add:

- one provider adapter layer
- one reconcile/provision script
- one autonomy validation script
- a small number of DB tables and API/service modules for policy and audit
- executor-host bootstrap docs and service units

## Recommended Sequence

1. Extend `ops/repository-topology.json` with optional autonomy/provisioning metadata while preserving the current env-based remote contract.
2. Add DB settings and audit tables for autonomy mode, repo scope, run records, and action records.
3. Add a provider adapter plus `scripts/provision_governed_remote.sh` that wraps `bootstrap_primary_remote.sh`.
4. Add executor-host bootstrap docs and `systemd` units for the Tailscale-hosted always-on runner.
5. Add `scripts/validate_autonomy.sh` and wire it into `scripts/validate_ai_enterprise.sh`.
6. Add contract, auth, dry-run, and failure-path tests.
7. Only then enable live provisioning for the governed repo set.

<sources>
## Sources

### Primary (HIGH confidence)
- `/Users/IAn/Agent/AI-Enterprise/.planning/phases/10-autonomy-infrastructure-and-repo-provisioning/10-CONTEXT.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/REQUIREMENTS.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/STATE.md`
- `/Users/IAn/Agent/IAn/CLAUDE.md` (`/Users/IAn/Agent/CLAUDE.md` was not present)
- `/Users/IAn/Agent/AI-Enterprise/ops/repository-topology.json`
- `/Users/IAn/Agent/AI-Enterprise/scripts/_git_governance_common.sh`
- `/Users/IAn/Agent/AI-Enterprise/scripts/bootstrap_primary_remote.sh`
- `/Users/IAn/Agent/AI-Enterprise/scripts/validate_git_governance.sh`
- `/Users/IAn/Agent/AI-Enterprise/scripts/validate_ai_enterprise.sh`
- `/Users/IAn/Agent/AI-Enterprise/docs/infrastructure-topology.md`
- `/Users/IAn/Agent/AI-Enterprise/docs/repository-governance.md`
- `/Users/IAn/Agent/AI-Enterprise/docs/deployment-provenance.md`
- `/Users/IAn/Agent/AI-Enterprise/docs/security-model.md`
- `/Users/IAn/Agent/AI-Enterprise/api/app.py`
- `/Users/IAn/Agent/AI-Enterprise/api/bootstrap.py`
- `/Users/IAn/Agent/AI-Enterprise/api/config.py`
- `/Users/IAn/Agent/AI-Enterprise/api/security/admin_auth.py`
- `/Users/IAn/Agent/AI-Enterprise/api/routes/settings.py`
- `/Users/IAn/Agent/AI-Enterprise/api/routes/datastores.py`
- `/Users/IAn/Agent/AI-Enterprise/api/db/schema.sql`
- `/Users/IAn/Agent/AI-Enterprise/tests/test_phase9_contracts.py`
- `/Users/IAn/Agent/AI-Enterprise/tests/api/test_runtime_foundation.py`
- `/Users/IAn/Agent/AI-Enterprise/tests/api/test_security_auth.py`

### External (HIGH confidence)
- Tailscale auth keys: https://tailscale.com/kb/1085/auth-keys
- Tailscale tags: https://tailscale.com/kb/1068/tags
- Tailscale OAuth clients: https://tailscale.com/kb/1215/oauth-clients
- Tailscale systemd install guidance: https://tailscale.com/kb/1097/install-systemd
- GitHub App best practices: https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app
- GitHub REST repo creation for organizations: https://docs.github.com/en/rest/repos/repos#create-an-organization-repository
- GitHub REST repo creation for the authenticated user: https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user
- GitHub personal access token guidance: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

</sources>
