# Phase 4: Security, Secrets, And Connection Validation - Research

**Researched:** 2026-03-08
**Domain:** Auth hardening, server-managed secrets, and evidence-based connection reporting
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Secrets must be server-managed in `AI-Enterprise`; no browser-side secret persistence pattern is allowed to survive into the clean target.
- `DASHBOARD_ADMIN_KEY` must not be accepted when it is left at a placeholder/default value unless an explicit local-development override says otherwise.
- Sensitive settings and integration-status surfaces must follow a consistent auth contract.
- `AI-Enterprise/.env.example` must contain names only, no live values and no unsafe default admin secret.
- `AI-Enterprise/SECRETS-MANIFEST.md` should be created now as the clean target's canonical secrets inventory.
- Connection reporting must distinguish `live`, `partial`, `missing`, and `planned` with evidence.
- Datastore validation should reuse the duplicated registry/data-store foundation from Phase 2.

### Claude's Discretion
- Exact module boundaries for secret inventory, connection checks, and route handlers
- Whether to expose both generic and control-ui-shaped routes now or only the normalized secrets routes
- Exact test split between auth coverage and connection-status coverage

### Deferred Ideas (OUT OF SCOPE)
- Full orchestration/control-plane normalization beyond secrets/settings
- Frontend rebuild
- Full cutover/live routing validation

</user_constraints>

<research_summary>
## Summary

Phase 4 should not bolt security onto the side of the clean target; it should define the security contract that later phases must respect. The source system proved the operational need for `X-Admin-Key`, autonomy-header writes, Claude OAuth inspection, and datastore verification, but it also proved the risk: keys were persisted in browser `localStorage`, placeholder admin configuration could be mistaken for a real secret, and settings/integration surfaces were readable or writable under inconsistent rules.

The clean target is still small, which is an advantage. The right approach is to harden configuration and auth first, then add a secrets/connection service layer with explicit redaction guarantees. That service layer should read from a checked-in secret inventory plus the registry/data-store tables already duplicated in Phase 2. Routes should then expose only redacted status and opt-in tests. This keeps the future `/secrets` frontend route thin and keeps the backend contract auditable.

**Primary recommendation:** implement Phase 4 in two plans. First, harden config/auth, create the secrets manifest, and add admin-only settings routes. Second, add a redacted secret inventory + connection-status service with `/api/control-ui/secrets/status`, `/api/control-ui/secrets/test/{key_name}`, and a secured `/api/datastores/verify`, all backed by pytest coverage that proves no secret values leak.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | source current | route auth and sensitive endpoint handling | already in the clean target |
| sqlite3 | stdlib | persistent registry and settings state | already the clean target source of truth |
| python-dotenv | source current | local secret/env loading | already the target config pattern |
| pytest | source current | auth and redaction verification | already the project test stack |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| subprocess | stdlib | targeted CLI auth/SSH validation | for evidence-based connection tests only |
| pathlib | stdlib | SSH key and local datastore path checks | for deterministic non-network validation |
| Markdown manifests | n/a | durable secrets policy and inventory | create in this phase |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| server-side redacted status endpoints | frontend-managed key entry | repeats the source security flaw |
| config-level default-key rejection | documentation only | too easy to misconfigure and silently stay weak |
| registry-backed connection reporting | ad hoc env scans in routes | duplicates logic and becomes inconsistent fast |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Reject Insecure Defaults at the Auth Boundary
**What:** treat placeholder/default admin keys as effectively unset unless an explicit override is enabled.
**When to use:** for all privileged key checks in the clean target.
**Why:** prevents the easiest accidental insecure deployment path.

### Pattern 2: Secret Inventory as Data, Not Scattered Conditionals
**What:** define a catalog of required secrets with provider, priority, scope, and validation target metadata.
**When to use:** for `.env.example`, manifest generation, status payloads, and future frontend `/secrets` wiring.
**Why:** one catalog lets later phases reason about presence, priority, and validation consistently.

### Pattern 3: Redacted Status Routes with Explicit Evidence
**What:** routes return presence, priority, scope, and validation evidence without returning the underlying values.
**When to use:** for secret status, connection tests, and datastore verification.
**Why:** operators need visibility, but visibility must not become disclosure.

### Pattern 4: Admin-Only Settings Surface
**What:** settings listing and updates both require an admin key in the clean target.
**When to use:** for `/api/settings*` routes.
**Why:** the source mixed read openness with write protection; the clean build should not.

### Anti-Patterns to Avoid
- **Placeholder secrets that behave like real secrets**
- **Status endpoints returning token suffixes or masked values**
- **Auth bypass via autonomy headers on settings mutation**
- **Connection validation implemented only in docs, not in routes/tests**

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| distributed secret checks in every route | repeated `os.getenv` logic | shared secret/connection service | keeps policy centralized |
| custom auth behavior per route | ad hoc header checks | `admin_auth.py` guard helpers | avoids drift and inconsistent semantics |
| “safe enough” secret redaction | manual string masking in responses | never include values at all | simpler and safer |
| manual connection spot checks | only shell notes in docs | route + pytest contract | later phases need machine-readable state |

**Key insight:** the highest-value outcome in Phase 4 is not “more security code.” It is making the clean target incapable of repeating the source system's weakest operational patterns.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Treating `.env.example` defaults as harmless
**What goes wrong:** a placeholder admin key becomes a valid runtime credential.
**Why it happens:** code accepts any non-empty configured key.
**How to avoid:** explicitly reject known placeholder/default keys unless a local override is enabled.
**Warning signs:** tests can authenticate with `change-me-admin-key`.

### Pitfall 2: Returning “masked” secret values in status payloads
**What goes wrong:** payloads still leak enough entropy to aid compromise.
**Why it happens:** UI convenience takes priority over security.
**How to avoid:** return presence and validation evidence only; never echo or derive secret content.
**Warning signs:** API payloads contain token prefixes/suffixes or value lengths.

### Pitfall 3: Leaving source settings behavior intact
**What goes wrong:** sensitive model/config settings remain broadly readable or partially writable.
**Why it happens:** copying source `settings.py` too literally.
**How to avoid:** admin-only settings route contract in the clean target.
**Warning signs:** unauthenticated clients can list settings or Claude auth metadata.

### Pitfall 4: Reporting “configured” as if it were “live”
**What goes wrong:** operators believe a connection is valid when only env presence was checked.
**Why it happens:** status model lacks evidence semantics.
**How to avoid:** include a validation class/evidence field and reserve `live` for tested connectivity.
**Warning signs:** all integrations show green with no recorded last test or evidence note.

</common_pitfalls>

<open_questions>
## Open Questions

1. **Should `/api/control-ui/secrets/status` arrive in Phase 4 or wait for Phase 5?**
   - What we know: the master plan names it explicitly and the future `/secrets` UI depends on it.
   - Recommendation: add it now because it directly satisfies `SEC-03`; broader API normalization can still continue in Phase 5.

2. **Should autonomy credentials read secret status?**
   - What we know: autonomy is useful for controlled operational writes, but settings are more sensitive.
   - Recommendation: allow write-authorization on secret-status reads, but keep settings reads/writes admin-only.

3. **How much live network validation belongs in this phase?**
   - What we know: some integrations cannot be fully tested without real credentials and should not fail the whole phase.
   - Recommendation: implement both passive status and opt-in targeted tests; use `partial` when configuration exists but live auth is unproven.

## Validation Architecture

Phase 4 validation should prove:

- placeholder/default admin credentials are rejected by default
- admin-only settings routes require a real admin key
- autonomy credentials can access only the intended status surfaces
- `.env.example` and `SECRETS-MANIFEST.md` align with the clean secret inventory
- `/api/control-ui/secrets/status` and `/api/control-ui/secrets/test/{key_name}` return no secret values
- `/api/datastores/verify` returns evidence-based statuses sourced from the duplicated registry
- the clean target contains no `localStorage`-based auth handling code

<sources>
## Sources

### Primary (HIGH confidence)
- `/Users/IAn/Downloads/PLAN.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/INTEGRATIONS.md`
- `AI-Enterprise/api/config.py`
- `AI-Enterprise/api/security/admin_auth.py`
- `AI-Enterprise/api/system/program_registry.py`
- source `backend/routes/settings.py`
- source `backend/routes/datastores.py`

### Secondary (MEDIUM confidence)
- `.planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md`
- `.planning/phases/02-backend-and-registry-duplication/02-RESEARCH.md`

### Tertiary (LOW confidence - needs validation)
- live external auth/network behavior for Claude CLI and cPanel SSH on the clean target host

</sources>

<metadata>
## Metadata

**Research scope:**
- auth hardening
- secret inventory/manifest design
- redacted connection status
- datastore and integration validation surfaces

**Confidence breakdown:**
- auth boundary design: HIGH
- route split and payload design: HIGH
- live validation semantics: MEDIUM
- provider-specific network checks: MEDIUM

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 04-security-secrets-and-connection-validation*
*Research completed: 2026-03-08*
*Ready for planning: yes*
