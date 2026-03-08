# AI-Enterprise Security Model

## Principles

- Secrets are server-managed only.
- No client-side `localStorage` pattern is allowed in the clean target.
- Placeholder admin secrets are rejected by default.
- Settings reads and writes are admin-only.
- Secret and connection status routes return metadata and evidence, never values.
- Autonomous provisioning stays behind explicit policy flags, executor scoping, audit readiness, and host kill-switch controls.

## Auth Matrix

| Route | Access |
|-------|--------|
| `GET /api/settings` | admin key only |
| `PUT /api/settings/{key}` | admin key only |
| `GET /api/autonomy/policy` | admin key or autonomy key |
| `POST /api/autonomy/provisioning/preflight` | admin key or autonomy key plus autonomy policy |
| `GET /api/autonomy/executor` | admin key or autonomy key |
| `POST /api/autonomy/executor/run` | admin key or autonomy key plus executor and autonomy policy |
| `GET /api/autonomy/audit/runs` | admin key or autonomy key |
| `GET /api/autonomy/sync/repositories` | admin key or autonomy key |
| `GET /api/datastores/verify` | admin key or autonomy key |
| `GET /api/control-ui/secrets/status` | admin key or autonomy key |
| `POST /api/control-ui/secrets/test/{key_name}` | admin key only |

## Admin-Key Policy

- `DASHBOARD_ADMIN_KEY` must be explicitly configured.
- `change-me-admin-key` and equivalent placeholders are treated as insecure defaults.
- `ALLOW_DEFAULT_ADMIN_KEY=1` exists only for local-development escape hatches and should remain disabled in normal operation.

## Autonomy Provisioning Policy

- `IAN_AUTONOMY_KEY` remains the routine service credential for automation.
- Admin access can manage the policy, but it does not bypass the autonomy kill switch or allowed repository scope on the provisioning preflight route.
- `AUTONOMY_ENABLED`, `AUTONOMY_MODE`, `AUTONOMY_REPO_PROVISIONING_ENABLED`, `AUTONOMY_ALLOWED_REPOSITORY_IDS`, `AUTONOMY_EXECUTOR_ENABLED`, and `AUTONOMY_EXECUTOR_ALLOWED_AGENTS` must all permit the request before a live executor run is returned.
- The executor host also enforces `AUTONOMY_HARD_DISABLE` or the kill-switch file configured by `AUTONOMY_HOST_KILL_SWITCH_FILE`.
- Live provisioning requires `AUTONOMY_MODE=provision` and `AUTONOMY_AUDIT_READY=1`; failures quarantine and roll back the local remote contract instead of continuing.

## Secret Inventory

- Canonical inventory lives in `SECRETS-MANIFEST.md`.
- `.env.example` contains names only.
- `.env.local` is the local-development override file supported by the clean target config loader.

## Connection Status Semantics

| Status | Meaning |
|--------|---------|
| `live` | a direct validation succeeded or a local resource was verified |
| `partial` | configuration exists but live auth/connectivity is not fully proven |
| `missing` | required env/path/auth material is missing |
| `planned` | integration is intentionally not implemented yet |

## Redaction Rule

- API responses may include `name`, `provider`, `priority`, `scope`, `status`, `evidence`, and `checked_at`.
- API responses must not include raw secret values, masked fragments, token lengths, or derived hashes.
