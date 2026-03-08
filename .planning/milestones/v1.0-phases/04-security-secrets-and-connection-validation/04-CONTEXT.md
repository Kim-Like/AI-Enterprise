# Phase 4: Security, Secrets, And Connection Validation - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning
**Source:** Master PRD + codebase map + completed AI-Enterprise Phase 2/3 baseline

<domain>
## Phase Boundary

Harden the clean AI-Enterprise target so it no longer carries the source system's weakest security patterns. This phase establishes a server-managed secrets model, removes any acceptance of placeholder admin credentials, applies a consistent authorization policy to settings and integration-status surfaces, and adds verifiable connection-status/test endpoints that later control-plane and frontend phases can consume.

</domain>

<decisions>
## Implementation Decisions

### Security model
- Secrets must be server-managed in `AI-Enterprise`; no browser-side secret persistence pattern is allowed to survive into the clean target.
- `DASHBOARD_ADMIN_KEY` must not be accepted when it is left at a placeholder/default value unless an explicit local-development override says otherwise.
- Mutating settings and other sensitive operational endpoints must follow a consistent auth contract instead of the source system's mixed read/write behavior.

### Route and API scope
- Phase 4 may introduce the clean secrets/connection routes early if they directly satisfy `SEC-03` and `VAL-01`.
- Phase 4 should preserve source-compatible helper routes like `/api/datastores/verify` only if they are hardened and useful for evidence-based validation.
- Broader control-plane API normalization still belongs to Phase 5; this phase should only add the security/secret surfaces needed now.

### Secrets and manifest scope
- `AI-Enterprise/.env.example` must contain names only, no live values and no unsafe default admin secret.
- `AI-Enterprise/SECRETS-MANIFEST.md` should be created now as the clean target's canonical secrets inventory.
- Secret status payloads must never include raw secret values, token substrings, or reversible metadata.

### Connection validation scope
- Connection reporting must distinguish `live`, `partial`, `missing`, and `planned` states with evidence.
- Datastore validation should reuse the duplicated registry/data-store foundation from Phase 2 rather than inventing a second source of truth.
- Networked live checks may be targeted and optional per route/test target, but the status model must exist even when credentials are missing.

### Claude's Discretion
- Exact module boundaries for secret inventory, connection checks, and route handlers
- Whether to expose both generic and future control-ui-shaped routes now or only the normalized secrets routes
- Exact test split between auth coverage and connection-status coverage

</decisions>

<specifics>
## Specific Ideas

- Add an explicit `ALLOW_DEFAULT_ADMIN_KEY` guard in the target config and reject the placeholder key by default.
- Add a root `SECRETS-MANIFEST.md` and align `.env.example` with it, including `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.
- Add `api/routes/settings.py` in the clean target with admin-only access for sensitive settings reads/writes.
- Add `api/routes/datastores.py` and a secrets/connection status route that surface evidence without exposing secret values.
- Add tests for auth hardening, secret-status redaction, and connection-status payloads.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AI-Enterprise/api/config.py` already owns env loading and should become the single place for auth-related defaults.
- `AI-Enterprise/api/security/admin_auth.py` already centralizes key checks and is the right hardening point.
- `AI-Enterprise/api/system/program_registry.py` already knows about canonical datastore rows and current verification semantics.
- Source references `backend/routes/settings.py` and `backend/routes/datastores.py` show which source capabilities need a secure clean-build equivalent.

### Established Patterns
- The clean target currently exposes only minimal health/meta routes.
- Registry sync already persists data-store status into SQLite during startup.
- The source system's weakest contract is not missing auth entirely; it is inconsistent auth and client-side key handling.

### Integration Points
- Phase 5 control-plane API normalization will consume whatever secrets/connection DTOs Phase 4 defines now.
- Phase 6 `/secrets` and `/settings` frontend routes depend on these Phase 4 route contracts.
- Phase 7 live cutover validation depends on Phase 4 status evidence for all P0 connections.

</code_context>

<deferred>
## Deferred Ideas

- Full orchestration endpoint normalization belongs to Phase 5.
- The mission-control frontend rebuild belongs to Phase 6.
- End-to-end operator routing validation belongs to Phase 7.

</deferred>

---

*Phase: 04-security-secrets-and-connection-validation*
*Context gathered: 2026-03-08*
