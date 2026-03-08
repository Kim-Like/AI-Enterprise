# External Integrations

**Analysis Date:** 2026-03-08

## Status Reading

- `LIVE`: code path exists and current validation or runtime evidence proves it is active
- `PARTIAL`: env/config exists, but the control plane does not fully prove live auth on every run
- `PLANNED`: secret or registry contract exists without a live first-party implementation

## Git And Repository Governance

**Primary Git remote**
- Provider: GitHub over SSH
- Namespace: `Kim-Like`
- Source of truth contract: `ops/repository-topology.json`
- Governance validation: `scripts/validate_git_governance.sh`
- Live repo provisioning path: `api/system/autonomy_service.py`
- Status: `LIVE` for the main `AI-Enterprise` repo, `PARTIAL` for governed independent repos until they are fully materialized

**Autonomous repo creation**
- Provider-side create path uses GitHub REST calls from `api/system/autonomy_service.py`
- Required credential: `GITHUB_AUTONOMY_TOKEN`
- Status: `PARTIAL`
- Notes: implemented in code, but still depends on a real executor host env and non-human credential

## Remote Hosting And cPanel

**cPanel / SSH**
- Shared shell helpers: `scripts/_cpanel_common.sh`
- Runtime contract checks: `scripts/check_remote_config_contract.sh`
- Live health checks: `scripts/verify_remote_portfolio.sh`
- Policy doc: `docs/cpanel-runtime-contract.md`
- Status: `LIVE`

Verified remote surfaces are modeled as deploy targets, not code source:
- `https://lavprishjemmeside.dk`
- `https://api.lavprishjemmeside.dk`
- `https://ljdesignstudio.dk`
- `https://api.ljdesignstudio.dk`
- `https://theartisan.dk`
- `https://reporting.theartisan.dk`

## Databases And Storage

**Primary control-plane datastore**
- SQLite database at `ai_enterprise.db`
- Client: `api/db/client.py`
- Schema: `api/db/schema.sql`
- Startup seeding: `api/bootstrap.py`
- Status: `LIVE`

**Registry-declared external or adjacent datastores**
- Artisan Reporting MySQL: env-backed cPanel database, status `PARTIAL`
- Artisan WordPress MySQL: env-backed cPanel database, status `PARTIAL`
- Lavprishjemmeside MySQL: env-backed cPanel database, status `PARTIAL`
- Samlino local SQLite path: registry-tracked local payload store, status depends on payload path presence
- Baltzer Shopify cloud surface: env-backed external platform, status `PARTIAL`
- Baltzer TCG migration hold: explicit planned/non-live replacement contract

Datastore status is derived by:
- `api/system/program_registry.py`
- `api/system/connection_status.py`

## Secrets And Connection Health

**Canonical secret inventory**
- `api/system/secret_catalog.py`
- `.env.example`
- `SECRETS-MANIFEST.md`

**Secrets/status API**
- `GET /api/control-ui/secrets/status`
- `POST /api/control-ui/secrets/test/{key_name}`
- Implementation: `api/routes/secrets.py` and `api/system/connection_status.py`

Important distinction:
- Many external connections are only proven as `env present`
- Only a subset perform live checks during validation, such as Claude CLI auth and cPanel SSH

## AI Provider And API Integrations

**Claude CLI**
- Used for local auth/status verification through `claude auth status`
- Implementation: `api/system/connection_status.py`
- Status: `LIVE` when the executor/workstation is logged in

**Anthropic / OpenAI**
- Present in the secret contract
- No first-party SDK-based control-plane client is currently mapped in the repo
- Status: `PLANNED` from the control-plane perspective

**Billy**
- Present in env/secret definitions and portfolio registry
- Used as a program-level dependency for reporting payloads
- Status: `PARTIAL`

**Shopify**
- Present in the secret contract and program registry
- No first-party control-plane API client beyond connection inventory
- Status: `PARTIAL`

## Frontend/Auth Boundary

- Operator keys are assembled in-memory only in `src/lib/control-session.tsx`
- Requests use same-origin fetch wrappers in `src/lib/api/client.ts`
- `localStorage` and `sessionStorage` are forbidden in the clean target
- Status: `LIVE`

This is a real improvement over the brownfield source project and should be treated as current truth.

## Tailscale And Always-On Host

- Host contract: `docs/autonomy-executor-host.md`
- Services: `ops/systemd/ai-enterprise-api.service`, `ops/systemd/ai-enterprise-autonomy.service`
- Requirement: `tailscaled.service` on the executor host
- Status: `PARTIAL`

The code and service units exist, but full autonomous execution depends on host rollout and environment provisioning.

## Retired Or Non-Live Integrations

- Supabase is no longer part of the live control-plane secret catalog or datastore contract
- If Supabase references appear, they are legacy payload material or archive context, not active AI-Enterprise infrastructure
