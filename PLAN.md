# AI-Enterprise v1.0 Clean-Slate Plan

## Summary
- Audit root is `/Users/IAn/Agent` per operator choice.
- First-party migration scope is `/Users/IAn/Agent/IAn`; workspace-only runtimes like `.venv`, `.python39`, `.openssl`, caches, generated bundles, and vendor trees are excluded from first-party inventory.
- Vendor/generated/duplicate trees are tracked as dependency noise, not as Programs, Applications, or Agents. Key exclusions: `backend/static/ui/assets`, `frontend/node_modules`, WordPress `wp-content` vendor/plugin trees, program-local `venv`, and `programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility/AI-Visibility copy`.
- Baseline discovered on 2026-03-08: 10 canonical programs, 24 canonical applications, 44 agent directories, 9 datastores, 6 unique GitHub repos, 2 first-party deploy workflows, 1 working cPanel SSH target, 1 live Claude CLI OAuth session.
- Clean-slate objective: preserve live orchestration and registry truth, normalize APIs, rebuild the frontend from scratch, centralize secrets server-side, and remove client-side key leakage.

## Output Files To Produce
- `PLAN.md`: readable master plan with discovery summary, program/application map, agent audit, connection validation plan, secrets plan, frontend design system, IAn architecture, and execution checklist.
- `AUDIT.json`: machine-readable inventory using the exact top-level shape requested, with each object carrying `classification`, `evidence`, `lastActiveAt`, `source`, and `notes`.
- `SECRETS-MANIFEST.md`: grouped P0/P1/P2 secret inventory, no values, plus storage policy and frontend exposure rules.
- `ARCHITECTURE.md`: clean-build system map covering hierarchy, runtime components, APIs, state stores, orchestration flows, security boundaries, and escalation paths.

## AUDIT.json Baseline
- Use `program_registry`, `application_registry`, `data_store_registry`, filesystem discovery, and `father.db` activity as primary truth.
- Use `LIVE` only when runtime, build, or connectivity evidence exists; downgrade registry `active` entries to `PARTIAL` if local implementation, auth, or build evidence is missing.
- Use `source: "registry"` for canonical items and `source: "filesystem_orphan"` for incubators and unregistered assets.

```json
"summary": {
  "totalPrograms": 10,
  "totalAgents": 44,
  "realAgents": 42,
  "partialAgents": 2,
  "dummyAgents": 0,
  "liveConnections": 3,
  "brokenConnections": 6,
  "missingSecrets": [
    "GITHUB_SSH_KEY",
    "GITHUB_PAT",
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "SHOPIFY_STORE_DOMAIN",
    "SHOPIFY_ADMIN_TOKEN"
  ]
}
```

## Program And Application Map
- `ian-control-plane` | `/Users/IAn/Agent/IAn` | master `father` | apps `ian-mission-control (LIVE)` | `LIVE` | FastAPI + React + SQLite; frontend build passed and control-ui tests passed on 2026-03-08.
- `artisan-reporting` | `/Users/IAn/Agent/IAn/programs/artisan/reporting.theartisan.dk` | master `artisan-master` | apps `artisan-reporting-app (LIVE)` | `LIVE` | Billy + cPanel MySQL configured; program build/syntax passed.
- `artisan-wordpress` | `/Users/IAn/Agent/IAn/programs/artisan/the-artisan-wp` | master `artisan-master` | apps `artisan-wordpress-site (LIVE)`, `artisan-b2b-dashboard-orders (PENDING)` | `LIVE` | live URL present, cPanel SSH validated, WordPress/B2B task traffic exists.
- `artisan-email-marketing` | `/Users/IAn/Agent/IAn/programs/artisan/e-mail-marketing` | master `artisan-master` | apps `artisan-email-marketing (PENDING)` | `PENDING` | directory exists, no working implementation.
- `lavprishjemmeside-cms` | SSH-first repo at `cp10.nordicway.dk` | master `lavprishjemmeside-master` | apps `lavprishjemmeside-ai-cms (PARTIAL)`, `lavprishjemmeside-seo-dashboard (PENDING)`, `lavprishjemmeside-ads-dashboard (PENDING)`, `lavprishjemmeside-client-subscription-overview (PENDING)` | `PARTIAL` | registry active, SSH target exists, DB env missing locally.
- `samlino-seo-agent-playground` | `/Users/IAn/Agent/IAn/programs/ian-agency/contexts/samlino/seo-agent-playground` | master `samlino-master` | apps `samlino-seo-agent-playground-app (PARTIAL)`, `samlino-seo-schema-runtime (PARTIAL)`, `samlino-seo-audit-runtime (PARTIAL)`, `samlino-prototyper-runtime (PARTIAL)` | `PARTIAL` | code exists, private repo auth missing, build blocked by missing local Vite.
- `baltzer-tcg-index` | `/Users/IAn/Agent/IAn/programs/baltzer/TCG-index` | master `baltzer-master` | apps `baltzer-tcg-index-app (PARTIAL)` | `PARTIAL` | duplicated payload is now demoted to a migration-hold contract pending local datastore replacement.
- `baltzer-reporting` | `/Users/IAn/Agent/IAn/programs/baltzer/reporting.baltzergames.dk` | master `baltzer-master` | apps `baltzer-reporting-app (PARTIAL)` | `PARTIAL` | syntax passed and local state verified, but repo remote is mispointed and no confirmed live URL.
- `baltzer-shopify` | `/Users/IAn/Agent/IAn/programs/baltzer/shopify` | master `baltzer-master` | apps `baltzer-shopify-core (PARTIAL)`, `baltzer-social-media-management (PENDING)`, `baltzer-event-management-platform (PENDING)`, `baltzer-employee-schedule-salary-api (PENDING)` | `PARTIAL` | registry active, local core directory empty, Shopify secrets missing.
- `personal-assistant-suite` | `/Users/IAn/Agent/IAn/programs/personal-assistant` | master `personal-assistant-master` | apps `personal-assistant-calendar-management (PENDING)`, `personal-assistant-email-management (PENDING)`, `personal-assistant-fitness-dashboard (PENDING)`, `personal-assistant-social-media-management (PENDING)`, `personal-assistant-task-manager (PENDING)` | `PENDING` | placeholder portfolio only.

## Orphan And Duplicate Application Candidates
- `programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility` -> `PARTIAL` incubator app with frontend-runnable code and unsafe browser-side key handling.
- `programs/ian-agency/contexts/samlino/seo-agent-playground/samlino-mind-map` -> `PARTIAL` incubator app with legacy client-side datastore wiring.
- `programs/ian-agency/contexts/samlino/seo-agent-playground/seo-auditor/audit-server` -> `PARTIAL` runtime service, not in canonical app registry.
- `programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility/AI-Visibility copy` -> `DEAD` duplicate copy; keep only as audit evidence, never migrate as active first-party code.

## Connectivity Matrix
Legend: `✓ LIVE`, `⚠ PARTIAL`, `○ PENDING`, `✗ DEAD`

| Program | GitHub | SSH | OAuth | API-key | Webhook | DB | Tailwind | Other |
|---|---|---|---|---|---|---|---|---|
| ian-control-plane | ✗ | ✗ | ✓ | ✓ | ○ | ✓ | ✓ | SQLite/WAL |
| artisan-reporting | ⚠ | ⚠ | ✗ | ✓ | ○ | ✓ | ✗ | Node/Express |
| artisan-wordpress | ✓ | ✓ | ✗ | ⚠ | ○ | ✓ | ✗ | WordPress/Woo |
| artisan-email-marketing | ✗ | ○ | ✗ | ○ | ○ | ○ | ✗ | Brevo planned |
| lavprishjemmeside-cms | ✗ | ✓ | ✗ | ⚠ | ○ | ⚠ | ○ | SSH-first Astro |
| samlino-seo-agent-playground | ⚠ | ✗ | ✗ | ⚠ | ○ | ⚠ | ⚠ | Runtime subapps |
| baltzer-tcg-index | ⚠ | ✗ | ✗ | ⚠ | ○ | ○ | ⚠ | Migration hold |
| baltzer-reporting | ⚠ | ⚠ | ✗ | ○ | ○ | ✓ | ✗ | Node/Express |
| baltzer-shopify | ✗ | ○ | ✗ | ⚠ | ○ | ⚠ | ○ | Local core missing |
| personal-assistant-suite | ✗ | ✗ | ✗ | ○ | ○ | ○ | ○ | Placeholders |

## Agent Audit
- Agent directory summary for `AUDIT.json`: 44 total, 42 `REAL`, 2 `PARTIAL`, 0 `DUMMY`.
- Role summary: `FATHER 1`, `LEAD 1`, `MASTER 7`, `SPECIALIST 34`, `UNKNOWN 1`.
- Canonical health trend: most common missing file is `heartbeat.md`, second is `ARCHITECTURE.md`.
- `father` is `FATHER/REAL` with all 8 canonical files present.
- `engineer` is `LEAD/REAL` with all 8 canonical files present.
- Program masters `artisan-master`, `baltzer-master`, `samlino-master`, `lavprishjemmeside-master`, `personal-assistant-master`, and `ian-master` are `MASTER/REAL`.
- `masters/Orchestration` is `MASTER/PARTIAL` and should be archived as historical structure, not used as the clean-build reference master.
- 34 task specialists exist and are mostly healthy but standardized only to `soul.md`, `user.md`, `agents.md`, `skills.md`, `tools.md`, `memory.md`; the clean build should add `heartbeat.md` and `ARCHITECTURE.md` to every active specialist.
- `programs/ian-agency/contexts/samlino/seo-agent-playground/ian` is `UNKNOWN/PARTIAL` and should be treated as a legacy local agent, not part of the core hierarchy.

## Connection Validation Plan
- GitHub repos to validate: `git@github.com:kimjeppesen01/reporting.theartisan.dk.git`, `https://github.com/kimjeppesen01/the-artisan.git`, `https://github.com/kimjeppesen01/card-pulse.git`, `https://github.com/SamlinoDK/seo-agent-playground.git`, `https://github.com/SamlinoDK/ai-clarity.git`, `https://github.com/SamlinoDK/samlino-mind-map.git`.
- GitHub auth baseline: HTTPS read succeeds for `the-artisan`; SSH auth to `github.com` fails; other private repos fail without PAT or matching SSH key.
- SSH hosts to validate: `theartis@cp10.nordicway.dk:33` with `/Users/IAn/.ssh/cpanel_theartisan` is working; `github.com` SSH auth is missing.
- OAuth baseline: Claude CLI OAuth session is live; no first-party `client_id`/`client_secret` app configs were found for AI providers, so the new build should not depend on browser OAuth for model access.
- API-key baseline: `ANTHROPIC_API_KEY`, `BILLY_API_TOKEN`, `SHOPIFY_ADMIN_TOKEN`, `CPANEL_API_TOKEN`, `DASHBOARD_ADMIN_KEY`, and `IAN_AUTONOMY_KEY` are current patterns; browser-side `VITE_*_API_KEY` usage in Samlino incubators is an explicit security defect to eliminate.
- Tailwind/CSS baseline: root frontend has `tailwind.config.js` and `postcss.config.js` and builds clean; Baltzer TCG and Samlino have Tailwind configs but local builds fail because Vite is unavailable.
- Datastore baseline: `father-db` verified, `artisan-reporting-local-state` configured, `artisan-wordpress-cpanel-mysql` configured, `lavprishjemmeside-cpanel-mysql` missing env, `samlino-module-storage` missing path, `baltzer-tcg-migration-hold` planned, `baltzer-reporting-local-state` verified, `baltzer-shopify-cloud` missing env, `personal-assistant-local` planned.
- Webhook baseline: no first-party inbound or outbound webhook endpoints are confirmed live; webhook support should be planned as greenfield, with explicit signing and replay protection.

## SECRETS-MANIFEST.md Contents
- `P0`: `DASHBOARD_ADMIN_KEY`, `IAN_AUTONOMY_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CPANEL_API_TOKEN`, `CPANEL_SSH_HOST`, `CPANEL_SSH_USER`, `CPANEL_SSH_PORT`, `SSH_KEY_DEPLOY_CPANEL`, `ARTISAN_REPORTING_DB_HOST`, `ARTISAN_REPORTING_DB_PORT`, `ARTISAN_REPORTING_DB_NAME`, `ARTISAN_REPORTING_DB_USER`, `ARTISAN_REPORTING_DB_PASSWORD`, `ARTISAN_WP_DB_HOST`, `ARTISAN_WP_DB_NAME`, `ARTISAN_WP_DB_USER`, `ARTISAN_WP_DB_PASSWORD`.
- `P1`: `BILLY_API_TOKEN`, `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ADMIN_TOKEN`, `BRIGHTDATA_API_TOKEN`, `BRIGHTDATA_UNLOCKER_ZONE`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- `P2`: optional OAuth client IDs for future operator sign-in, webhook signing secrets, staging-only provider keys, and any non-production analytics keys.
- Secret storage policy: local development uses `.env.local`; shared environments use a secrets manager; `.env.example` contains names only; frontend receives only non-secret client config like OAuth client IDs.
- Frontend security policy: no raw provider API keys in bundle, no API-key persistence in `localStorage`, and the new `/secrets` route operates through backend status/test endpoints only.

## Frontend Design System And Route Plan
- Preserve the supplied visual direction exactly: warm dark terminal, amber phosphor emphasis, IBM Plex Mono for display/data, DM Sans for body, scanlines/noise/glass panels, 200-400ms ease-out motion, no purple SaaS styling.
- `tokens.css` must define the exact palette supplied in the request and keep all numeric fields in monospace.
- Route priorities: `/`, `/programs`, `/orchestration`, `/agents/configs`, `/secrets` are `P0`; `/report` and `/settings` are `P1`.
- `/` needs agent roster, health, active runs, and quick actions; primary drawer is `AgentDetailPanel`.
- `/programs` needs program/app registry, connections, and hierarchy; primary drawer is `Program/Application detail`.
- `/orchestration` needs queue, timelines, run detail, and manual trigger; primary drawers are `RunDetail` and `StepContractEditor`.
- `/agents/configs` needs canonical file coverage, staleness, token estimates, and missing-file detection; primary drawer is `CanonicalFilePanel`.
- `/report` needs lost/pending/live drift, stale agents, stale apps, and missing secret coverage; primary drawer is `Evidence detail`.
- `/secrets` needs secret presence status, connection health, per-provider tests, and OAuth metadata; primary drawers are `ConnectionTester` and `OAuthManager`.
- `/settings` needs provider defaults, motion/theme controls, alert thresholds, and environment policy.

## Component And API Architecture
- Component tree is fixed: `AppShell`, `TopHUD`, `NavRail`, `ContentArea`, `TheFloor`, `ProgramsMap`, `OrchestrationCenter`, `AgentConfigExplorer`, `StateReport`, `SecretsPanel`, and shared `SlideDrawer`, `StatusDot`, `HealthBar`, `ReliabilityPips`, `ScanlineOverlay`.
- Public API normalization: replace current `/api/control-ui/floor` with `/api/control-ui/agents`; merge current queue/overview surfaces into `/api/control-ui/orchestration/overview` and `/api/control-ui/orchestration/runs`; replace `/api/control-ui/report/state` with `/api/control-ui/reporting/loss-pending`; add `/api/control-ui/secrets/status` and `/api/control-ui/secrets/test/{key_name}`.
- DTOs to lock now: `AgentSummary {id,name,role,programId,status,canonicalHealth,lastActiveAt,activeRunId?}`, `CanonicalFileAudit {agentId,files[],totalTokenEstimate,issues[]}`, `OrchestrationOverview {activeRuns,blockedRuns,queueDepth,lastRunAt}`, `RunRecord {id,status,owner,programId,applicationId,startedAt,endedAt,steps[]}`, `ProgramOverview {programs[],applications[],connections[]}`, `SecretStatus {name,present,scope,lastValidatedAt,status}`, `ConnectionTestResult {target,status,checkedAt,latencyMs,detail}`.
- IAn hierarchy is fixed for the clean build: `IAn` at top, `Engineer` for technical execution, then program masters `ian-master`, `artisan-master`, `lavprishjemmeside-master`, `samlino-master`, `baltzer-master`, `personal-assistant-master`; `masters/Orchestration` is not part of the target hierarchy.
- IAn canonical file contents are fixed now: `soul.md` identity and limits; `user.md` operator model and permissions; `agents.md` full hierarchy and routing ownership; `skills.md` routing/synthesis/escalation capabilities; `tools.md` read/write/security boundaries; `heartbeat.md` health checks and escalation paths; `ARCHITECTURE.md` living system map; `memory.md` durable decisions and live operational context.

## Duplicate And Validate Checklist
- Phase 1 Duplicate: copy only first-party program directories, active agent directories, backend API modules required for the new surface, and env var names into the new `.env.example`; never copy frontend implementation, build artifacts, `node_modules`, `dist`, `build`, vendor trees, nested `.git`, or duplicate incubators.
- Phase 2 Validate Connections: run `git ls-remote` for each repo, `ssh -T -o ConnectTimeout=5` for each host, minimal authenticated provider checks for Anthropic/OpenAI/Billy/Shopify, DB pings for each datastore, and signed test payloads once webhook endpoints exist.
- Phase 3 Secrets Setup: create `.env.local`, populate all `P0` secrets before any build, expose only secret status to the frontend, and fail the build if any secret appears in client bundle output.
- Phase 4 IAn Foundation: create `IAn` and `Engineer` with all 8 canonical files, create one reference Program Master plus one reference Specialist, then verify `IAn -> Program Master -> Specialist -> Engineer` routing.
- Phase 5 Frontend Build: scaffold shell, tokens, all P0 routes with mock data first, wire to real APIs second, and remove mocks only after all P0 connection tests pass.

## Test Cases And Acceptance Criteria
- Discovery acceptance: regenerated audit must still show 10 canonical programs, 24 canonical applications, and 44 first-party agent directories unless intentional scope changes are documented.
- Security acceptance: `rg` against the production frontend bundle must show no raw provider secrets, no `VITE_*_API_KEY`, and no admin/autonomy keys.
- API acceptance: contract tests for every target `/api/control-ui/*` endpoint, including no-value guarantees on secrets endpoints.
- Frontend acceptance: all seven planned routes render on desktop and mobile, use the design tokens exactly, and animate within the 200-400ms rule.
- Orchestration acceptance: one end-to-end manual run from IAn to Program Master to Specialist to Engineer succeeds, and one blocked run escalates back to IAn with traceable status.
- Connection acceptance: all P0 connections pass before live mode, and every partial/broken connection remains visible in `/report` and `/secrets`.
- Migration acceptance: new `AI-Enterprise` excludes duplicate incubators and vendor trees while preserving all live first-party programs, agents, API contracts, and env names.

## Assumptions And Defaults
- Workspace root remains `/Users/IAn/Agent`, but only `/Users/IAn/Agent/IAn` is duplicated into `AI-Enterprise`.
- Generated assets and vendor code are excluded from the first-party audit and migration.
- Registry `active` does not automatically mean `LIVE`; runtime/build/connectivity evidence is required.
- Browser-side provider keys are forbidden in the target build, even if legacy apps currently use them.
- Claude CLI OAuth is treated as current-state evidence only; target AI provider access should be server-managed and secrets-backed.

## GSD Execution Alignment
- Treat this file as the master PRD for the clean build, but use `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/TESTING.md`, and `.planning/codebase/CONCERNS.md` as the brownfield source baseline generated by `gsd-map-codebase`.
- Treat `.planning/phases/01-planning-and-contract-freeze/01-CONTEXT.md`, `.planning/phases/01-planning-and-contract-freeze/01-SOURCE-TRACEABILITY.md`, `.planning/phases/01-planning-and-contract-freeze/01-RESEARCH.md`, `.planning/phases/01-planning-and-contract-freeze/01-VALIDATION.md`, `.planning/phases/01-planning-and-contract-freeze/01-01-PLAN.md`, and `.planning/phases/01-planning-and-contract-freeze/01-02-PLAN.md` as the execution-grade Phase 1 handoff created to satisfy `gsd-plan-phase`.
- The source system being duplicated is locked to `/Users/IAn/Agent/IAn`.
- The duplication target root is locked to `/Users/IAn/Agent/AI-Enterprise`.
- Overnight workflow rule: no new discovery unless Phase 1 artifacts are proven wrong by implementation evidence. Execution should begin from the frozen source traceability matrix and roadmap, not from ad hoc repo browsing.
