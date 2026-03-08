# Codebase Concerns

**Analysis Date:** 2026-03-08

## Tech Debt

**Split source of truth across DB, Markdown, JSON, and generated assets:**
- Issue: Runtime state and product metadata are split across `father.db`, canonical Markdown files, `backend/config/*.json`, seeded SQL in `backend/db/schema.sql`, and built UI assets in `backend/static/ui/`
- Why: The system evolved as an operational control plane and portfolio registry at the same time
- Impact: Behavior is hard to reason about, startup must reconcile multiple sources, and rebuild/migration work is riskier
- Fix approach: Establish one authority per concern during the rebuild and reduce startup reconciliation work

**Platform and payload live in the same repo tree:**
- Issue: The control plane and managed portfolio apps share one workspace under `programs/`
- Why: The system manages local snapshots and active downstream apps directly
- Impact: It is easy to blur platform changes with payload changes, and mapping/migration scope is easy to misread
- Fix approach: Keep the control plane distinct from managed-program payload in future architecture and docs

## Known Bugs

**GET endpoints have operational side effects:**
- Symptoms: Some read-looking routes trigger verification work or mutate state
- Trigger: Calling routes such as those tied to datastore verification or workspace probes in `backend/routes/datastores.py`, `backend/routes/workspace.py`, and helpers in `backend/system/program_registry.py`
- Workaround: Treat these endpoints as operational actions, not cache-safe reads
- Root cause: Verification and read concerns are mixed in route/service design

**Potential stale UI bundle drift:**
- Symptoms: `frontend/` source and `backend/static/ui/` compiled output can diverge
- Trigger: Changing source without rebuilding, or inspecting backend-served assets as if they were canonical
- Workaround: Treat `frontend/` as the source of truth and rebuild before validating UI behavior
- Root cause: Generated assets are stored beside source in the same repo tree

## Security Considerations

**Weak write authorization model:**
- Risk: High-impact actions rely on shared static headers from `backend/security/admin_auth.py`, and some write-capable routes are insufficiently protected
- Current mitigation: `X-Admin-Key` and autonomy-header checks exist for some paths
- Recommendations: Move to explicit auth boundaries, consistent enforcement, and server-side secret handling

**Settings and internal topology exposure:**
- Risk: Settings, internal state, prompt/config previews, and error surfaces are too broadly readable through routes such as `backend/routes/settings.py`, `backend/routes/control_ui.py`, `backend/routes/chat.py`, and `backend/routes/errors.py`
- Current mitigation: Partial route-level protections only
- Recommendations: Harden read access, separate operator-only surfaces, and audit every route for data exposure

**Secrets stored in browser localStorage:**
- Risk: Admin and autonomy keys are stored client-side in `frontend/src/api/client.ts` and `frontend/src/components/ui/ControlAuthPanel.tsx`
- Current mitigation: None beyond same-origin request usage
- Recommendations: Remove browser-side secret storage and use a stronger server-mediated auth/session model

## Performance Bottlenecks

**Startup sync path:**
- Problem: Boot performs DB and filesystem mutation plus registry/specialist synchronization from `backend/main.py`
- Measurement: No formal startup timing instrumentation was found
- Cause: The app repairs and seeds runtime state on every boot
- Improvement path: Split migrations/sync into explicit jobs or idempotent admin commands

**Large aggregation services:**
- Problem: Large modules such as `backend/system/workspace_service.py` (2954 lines), `backend/system/chat_service.py` (2309 lines), and `backend/system/control_ui_service.py` (1620 lines) have wide regression radius
- Measurement: No endpoint-level performance instrumentation was found
- Cause: Many responsibilities are concentrated in a few files
- Improvement path: Decompose read models, extract adapters, and add targeted contract tests before refactors

## Fragile Areas

**App startup in `backend/main.py`:**
- Why fragile: Startup performs migrations, registry sync, specialist sync, attribution backfill, and boundary validation before serving traffic
- Common failures: Boot-time regressions, unexpected local mutations, environment-sensitive behavior
- Safe modification: Change one startup concern at a time and cover it with explicit tests
- Test coverage: Partial; startup behavior is exercised indirectly by many tests, not by a dedicated isolated boot suite

**Registry and control UI services:**
- Why fragile: `backend/system/program_registry.py` and `backend/system/control_ui_service.py` combine filesystem discovery, DB state, and runtime checks
- Common failures: Status drift, mismatched IDs, incomplete UI aggregates, configured-vs-live confusion
- Safe modification: Preserve current IDs and payload shapes until versioned replacements exist
- Test coverage: Present for some control UI/API paths, but not exhaustive for all portfolio states

**Managed program bridge for Samlino and workspace ops:**
- Why fragile: The backend directly depends on `programs/samlino/seo-agent-playground/runtime/*` and remote-operation code in `backend/routes/workspace.py`
- Common failures: Missing local dependencies, missing envs, SSH drift, runtime path changes
- Safe modification: Treat these as adapter boundaries and test with known fixture states before change
- Test coverage: Limited compared with the operational surface area

## Scaling Limits

**Single-process SQLite-centered runtime:**
- Current capacity: Not explicitly documented
- Limit: Writes, boot-time sync, and operational probes all funnel through one app/database model
- Symptoms at limit: Slow startup, request contention, and operational coupling
- Scaling path: Separate control-plane command jobs, isolate read-heavy endpoints, and consider dedicated service boundaries if load grows

## Dependencies at Risk

**Local Claude CLI session:**
- Risk: Agent execution depends on a local CLI install and local OAuth state from `backend/agent/claude_client.py`
- Impact: Runtime can degrade silently if the local CLI changes or auth expires
- Migration plan: Replace or wrap with explicit provider-health checks and better failure reporting

**Unpinned Python dependency set:**
- Risk: `requirements.txt` does not fully pin versions
- Impact: Reproducibility and regression control are weaker than they should be
- Migration plan: Pin or lock dependencies as part of the rebuild

**Remote infra encoded through env and registry metadata:**
- Risk: SSH, MySQL, Supabase, and Shopify assumptions are scattered through env names and registry seed data
- Impact: Drift is easy and auth state is easy to misclassify
- Migration plan: Centralize integration contracts and validation policy

## Missing Critical Features

**Unified CI and safe baseline:**
- Problem: There is no trustworthy committed baseline in the current repo state, and no control-plane CI pipeline was found
- Current workaround: Manual checks and local test execution
- Blocks: Reliable regression control and safe documentation-only commits
- Implementation complexity: Medium

**Hermetic test environment:**
- Problem: Root tests are coupled to real app startup and sometimes real repo paths
- Current workaround: Local cleanup within tests
- Blocks: Confident refactoring and reproducible test runs
- Implementation complexity: Medium

**Proper operator auth model:**
- Problem: Shared static headers stand in for authentication and authorization
- Current workaround: Browser-stored keys and partial route guards
- Blocks: Safe exposure of operational UI beyond a trusted local environment
- Implementation complexity: High

## Test Coverage Gaps

**Frontend behavior:**
- What's not tested: Component rendering, route flows, and UI auth handling in `frontend/`
- Risk: UI regressions can ship without detection
- Priority: High
- Difficulty to test: Moderate; no existing frontend test harness is in place

**Security boundary coverage:**
- What's not tested: Route-by-route auth enforcement and settings exposure hardening
- Risk: High-impact endpoints can remain open or regress silently
- Priority: High
- Difficulty to test: Moderate

**External integration validation:**
- What's not tested: True authenticated connectivity for every declared external system
- Risk: Registry state may claim configured integrations that are not actually usable
- Priority: High
- Difficulty to test: Moderate to high due to external dependencies

---

*Concerns audit: 2026-03-08*
*Update as issues are fixed or new ones are discovered*
