# Codebase Concerns

**Analysis Date:** 2026-03-08

## Highest-Severity Concerns

### 1. Shared header keys remain the full control-plane auth boundary

- Risk: any actor with `X-Admin-Key` or `X-Autonomy-Key` can access broad operational surfaces, and there is no user identity, session server, or RBAC layer
- Evidence:
  - `api/security/admin_auth.py`
  - `api/routes/control_ui.py`
  - `api/routes/autonomy.py`
  - `api/routes/settings.py`
- Current mitigation:
  - placeholder admin keys are rejected
  - frontend holds keys in memory only
  - tests explicitly forbid browser persistence
- Residual concern: the security model is improved over the brownfield source, but still coarse-grained

### 2. Startup performs live state mutation on every boot

- Risk: application start is not a passive read-only operation; every boot can modify registry, application, specialist, and autonomy state
- Evidence:
  - `api/app.py`
  - `api/bootstrap.py`
  - `api/system/program_registry.py`
  - `api/system/application_registry.py`
  - `api/system/autonomy_service.py`
- Current mitigation:
  - boot logic is intentionally centralized
  - runtime foundation tests cover the basic bootstrap contract
- Residual concern: a bad seed/sync change can become a boot-time regression rather than an isolated admin task failure

### 3. The clean repo still has hidden fallback coupling to the archived source project

- Risk: some operational scripts will read `../IAn/.env*` if repo-local env files are absent, which means the clean target is not fully self-contained
- Evidence:
  - `scripts/_cpanel_common.sh`
  - `scripts/_git_governance_common.sh`
- Current mitigation:
  - repo-local `.env.local` works and should be preferred
- Residual concern: this can mask missing configuration and reintroduce brownfield dependence during operations or validation

### 4. Catalog metadata still contains brownfield-era path drift

- Risk: the runtime layout is now `api/` + `src/` + `dist/`, but some catalog metadata still points at `backend/*` and `backend/static/*`
- Evidence:
  - `api/config/application_catalog.json`
- Current mitigation:
  - the live runtime itself does not rely on those stale path strings for core serving
  - tests verify the clean target excludes the old `frontend/` and `backend/static/ui` paths
- Residual concern: dashboards, reports, or future tooling can misread the codebase if they trust the catalog blindly

### 5. Autonomous repo provisioning is implemented but not fully operational by default

- Risk: the system can plan and execute governed repo provisioning, but real autonomy still depends on executor-host rollout and `GITHUB_AUTONOMY_TOKEN`
- Evidence:
  - `api/system/autonomy_service.py`
  - `docs/autonomy-executor-host.md`
  - `ops/systemd/ai-enterprise-autonomy.service`
  - `ops/repository-topology.json`
- Current mitigation:
  - explicit rollout stages
  - dry-run and policy gates
  - validation scripts
- Residual concern: code completeness can be mistaken for live operational autonomy

### 6. Validation is strong, but mostly script-driven rather than CI-enforced

- Risk: `scripts/validate_ai_enterprise.sh` is comprehensive, but there is no repo-local CI workflow guaranteeing it runs on every change
- Evidence:
  - `scripts/validate_ai_enterprise.sh`
  - absence of a repo-local `.github/workflows/` contract in the canonical root
- Current mitigation:
  - local validation scripts are in place
  - API and phase regression tests exist
- Residual concern: discipline currently substitutes for automated enforcement

## Medium-Severity Structural Concerns

### Generated and runtime artifacts live beside source

- `dist/` and SQLite files are present at repo root during local operation
- They are ignored by Git, which is good
- The concern is operational clarity, not version-control pollution

### Portfolio payload heterogeneity is still high

- `programs/` mixes archive context, placeholders, embedded references, and active payloads
- This is intentional, but it means the registry layer is the real normalizer and the filesystem alone is not enough to infer runtime truth

## Concerns That No Longer Apply From Older Maps

- Browser `localStorage` auth storage is no longer a live concern in the main control-plane app
- Supabase is no longer part of the live control-plane secret catalog or active datastore contract
- The planning-root split has already been cleaned up; `.planning/` now lives inside `AI-Enterprise`
