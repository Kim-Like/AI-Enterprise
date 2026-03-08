# AI-Enterprise Security Model

## Principles

- Secrets are server-managed only.
- No client-side `localStorage` pattern is allowed in the clean target.
- Placeholder admin secrets are rejected by default.
- Settings reads and writes are admin-only.
- Secret and connection status routes return metadata and evidence, never values.

## Auth Matrix

| Route | Access |
|-------|--------|
| `GET /api/settings` | admin key only |
| `PUT /api/settings/{key}` | admin key only |
| `GET /api/datastores/verify` | admin key or autonomy key |
| `GET /api/control-ui/secrets/status` | admin key or autonomy key |
| `POST /api/control-ui/secrets/test/{key_name}` | admin key only |

## Admin-Key Policy

- `DASHBOARD_ADMIN_KEY` must be explicitly configured.
- `change-me-admin-key` and equivalent placeholders are treated as insecure defaults.
- `ALLOW_DEFAULT_ADMIN_KEY=1` exists only for local-development escape hatches and should remain disabled in normal operation.

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
