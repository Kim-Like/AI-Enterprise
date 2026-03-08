# External Integrations

**Analysis Date:** 2026-03-08

## APIs & External Services

**AI Provider Runtime:**
- Claude Code CLI - Agent execution and model-backed workflows from `backend/agent/claude_client.py`
  - Integration method: Local CLI process invocation rather than direct HTTPS client code
  - Auth: Local Claude OAuth session plus CLI binary selection through `CLAUDE_BINARY` and related settings
  - Status: Live in the current workstation environment; authenticated session was detected during audit

**Business Integrations:**
- Billy API - Accounting/reporting integration for `artisan-reporting`
  - Integration method: Registry- and env-driven, referenced by `backend/system/program_registry.py` and the managed app in `programs/artisan/reporting.theartisan.dk/`
  - Auth: `BILLY_API_TOKEN`
  - Status: Configured in the current environment, but not centrally validated by the control-plane backend

**Remote Operations:**
- cPanel / SSH operations - Remote WordPress and hosting management through `backend/system/artisan_wp_service.py` and `backend/routes/workspace.py`
  - Integration method: SSH commands and remote PHP/MySQL probes
  - Auth: `CPANEL_SSH_HOST`, `CPANEL_SSH_USER`, `CPANEL_SSH_PORT`, and an SSH key path env var
  - Status: SSH connectivity was confirmed during audit

**Registry-Declared External Services:**
- Supabase - Declared for Baltzer TCG and some Samlino incubators through `backend/db/schema.sql` and `backend/system/program_registry.py`
  - Auth: `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the control plane; some incubators also reference publishable/browser keys
  - Status: Not fully configured in the current root environment
- Shopify Admin - Declared for `baltzer-shopify` through `backend/db/schema.sql`
  - Auth: `SHOPIFY_STORE_DOMAIN` and `SHOPIFY_ADMIN_TOKEN`
  - Status: Missing in the current root environment
- Brevo / email marketing - Referenced as a managed-program concern for Artisan email marketing
  - Status: Planned/partial, not a live first-party control-plane integration

## Data Storage

**Databases:**
- SQLite - Primary control-plane database at `father.db`
  - Connection: `DB_PATH` via `backend/config.py`
  - Client: `backend/db/client.py`
  - Migrations/schema: `backend/db/schema.sql`
  - Status: Live and verified in current runtime
- cPanel MySQL - Artisan reporting and WordPress data stores
  - Connection: `ARTISAN_REPORTING_DB_*` and `ARTISAN_WP_DB_*`
  - Validation method: Remote checks initiated through service code
  - Status: Recorded as configured, not proven fully live-authenticated by a central integration suite
- cPanel MySQL - Lavprishjemmeside
  - Connection: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
  - Status: Missing env values in the current root environment
- SQLite - Samlino module storage
  - Connection: program-local file path tracked in registry data
  - Status: Registry reports missing path
- Supabase Postgres - Baltzer TCG
  - Connection: `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
  - Status: Registry reports missing env

**File Storage:**
- Local filesystem - Static UI assets in `backend/static/ui`, agent canonical files in `father/`, `engineer/`, and `masters/`, and runtime logs/backups beside source
- No dedicated first-party object storage integration was found in the control-plane code

**Caching:**
- No dedicated Redis or external cache layer was found
- The system relies on SQLite, filesystem state, and in-process request handling

## Authentication & Identity

**Control-Plane Write Auth:**
- Shared static header auth from `backend/security/admin_auth.py`
  - Implementation: `X-Admin-Key` plus configurable autonomy header
  - Token storage: Browser `localStorage` in `frontend/src/api/client.ts` and `frontend/src/components/ui/ControlAuthPanel.tsx`
  - Status: Live, but weak from a security perspective

**Model/Auth Provider:**
- Claude OAuth
  - Credentials: Managed by the local CLI runtime, not by repo-stored OAuth client config
  - Session handling: CLI session inspection via `backend/routes/settings.py`
  - Status: Live in the audited workstation

**OAuth Integrations:**
- No first-party browser or server OAuth app configuration was found for operator sign-in
- Some managed/incubator apps use browser auth libraries or publishable keys, but those are outside the control-plane auth model

## Monitoring & Observability

**Error Tracking:**
- Local error capture middleware stores runtime issues in the control-plane DB through `backend/middleware/error_capture.py`
- No Sentry, Datadog, or equivalent hosted error tracking was found

**Analytics:**
- No first-party analytics integration was found in the control-plane SPA

**Logs:**
- Python logging plus local log files under `logs/`
- Service manager integration through `deploy/systemd/` and `deploy/launchd/`

## CI/CD & Deployment

**Hosting:**
- Service-managed Python process using `scripts/run_prod.sh`
- Example Linux deployment through `deploy/systemd/ian-father-agent.service`
- Example macOS deployment through `deploy/launchd/com.ian.father-agent.plist.example`

**CI Pipeline:**
- The control plane itself has no root-level CI workflow
- Program-level GitHub Actions exist for some managed apps, including `programs/artisan/reporting.theartisan.dk/.github/workflows/deploy.yml` and `programs/baltzer/reporting.baltzergames.dk/.github/workflows/deploy.yml`
- GitHub SSH auth is not configured in the current workstation, so private SSH remotes cannot be validated through SSH today

## Environment Configuration

**Development:**
- Root env source is `.env`, with names documented in `.env.example`
- Critical local categories: DB path, write auth, model runtime, Billy token, cPanel SSH, and program datastore credentials
- Current live evidence:
  - Claude CLI auth works
  - cPanel SSH works
  - Root frontend build works
  - GitHub SSH auth is missing

**Staging:**
- No separate first-party staging environment contract was found in the control-plane repo

**Production:**
- Production expectations are implied through service-manager files and env loading in `backend/config.py`
- External datastore state is seeded and tracked in the registry, but many statuses represent config presence rather than true connectivity

## Webhooks & Callbacks

**Incoming:**
- No confirmed first-party webhook endpoints were identified as active control-plane integrations
- Webhook references are mostly planned or indirect in managed/incubator code

**Outgoing:**
- No centrally implemented outgoing webhook dispatcher was found in the control-plane backend
- Treat webhook support as planned unless a managed program owns it separately

## Validation Notes

- The current registry status model should be read carefully:
  - `verified` means a stronger local check exists
  - `configured` often means env/path presence only
  - `missing_env` and `missing_path` mean the integration cannot be treated as live
- Preserve this distinction in future mapping and rebuild work; do not collapse configured and authenticated into the same status.

---

*Integration audit: 2026-03-08*
*Update when adding or removing external services*
